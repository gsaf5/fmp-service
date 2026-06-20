# RothQuant V2 — Backend Infrastructure Upgrade
**Created:** June 20, 2026  
**Triggered by:** June 2026 live run — FMP plan wall blocked income statements, key metrics,
analyst estimates, and batch quotes. RSI and 200-DMA had to be estimated from 52wk range
context rather than computed from live data. Momentum scores for FICO and MEDP carry ±1
point uncertainty as a result.  
**Target:** July 2026 run — all momentum factors computed precisely from Railway container.

---

## Root Cause

The June run exposed a two-layer data problem:

**Layer 1 — FMP plan wall (hard)**  
The following endpoints are blocked on Gary's current FMP tier:
- `statements` → income statement, key metrics, financial ratios, Piotroski
- `analyst` → grades, estimates, price targets, revision direction
- `quote` → batch quotes (single `profile-symbol` still works)
- `insiderTrades` → insider transaction history

Only confirmed working: `profile-symbol`, `calendar` (earnings-calendar only), `company` basic data.

**Layer 2 — Railway container egress (structural)**  
`/conviction?symbol=` and `/vet?symbol=` are inaccessible from Claude's container
(host not in allowlist). These always require Gary to curl locally and paste results,
OR the backend computes the data itself and exposes it via an endpoint Claude CAN reach
through the GCC Railway MCP connector.

**Result:** Momentum factor (double-weighted, 10 pts) and Profitability Piotroski component
had no live data source. June scores are directionally correct but not fully precise.

---

## The Fix: Self-Computed Technicals on Railway

### Core Principle
FMP's `historical-price-eod-light` endpoint returns daily closing prices and IS available
on Gary's plan tier. Pull 200+ days of closes per ticker → compute 50-DMA, 200-DMA, and
RSI(14) in the Railway container → expose via a new `/technicals?symbol=` endpoint.
Claude can then call this through the GCC Railway MCP connector without any egress issue.

### New Endpoint: `/technicals?symbol=TICKER`

**What it computes (all from free FMP daily price history):**

| Output Field | Computation |
|---|---|
| `price` | Latest close |
| `sma_50` | Simple 50-day moving average of closes |
| `sma_200` | Simple 200-day moving average of closes |
| `pct_above_200` | `(price - sma_200) / sma_200 * 100` |
| `price_vs_200` | "above" or "below" |
| `rsi_14` | Wilder's RSI over 14 periods |
| `rsi_weekly` | RSI computed on weekly closes (hard kill gate >85) |
| `high_52wk` | Max close over trailing 252 trading days |
| `low_52wk` | Min close over trailing 252 trading days |
| `pct_from_52wk_high` | `(price - high_52wk) / high_52wk * 100` |
| `near_52wk_high` | True if within 10% of 52wk high |
| `momentum_score` | Pre-computed RothQuant Factor 4 score (1–10) |

**Python implementation for Railway `main.py`:**

```python
import pandas as pd
import numpy as np
import requests

FMP_KEY = "TiUMLS7qhCpwLRIPcJKodOAKn4Bm82RC"

def get_daily_closes(symbol: str, days: int = 260) -> pd.Series:
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"
    params = {"apikey": FMP_KEY, "serietype": "line"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("historical", [])
    closes = pd.Series(
        {pd.to_datetime(d["date"]): d["close"] for d in data}
    ).sort_index()
    return closes.tail(days)

def compute_rsi(closes: pd.Series, period: int = 14) -> float:
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)

def compute_weekly_rsi(closes: pd.Series, period: int = 14) -> float:
    weekly = closes.resample("W").last().dropna()
    return compute_rsi(weekly, period)

def compute_momentum_score(price, sma_50, sma_200, rsi, high_52wk) -> int:
    near_high = price >= (high_52wk * 0.90)
    above_50 = price > sma_50
    above_200 = price > sma_200
    if above_50 and above_200 and 55 <= rsi <= 70 and near_high:
        return 10
    elif above_50 and above_200 and 50 <= rsi <= 70:
        return 9 if near_high else 8
    elif above_200 and 45 <= rsi <= 65:
        return 7 if above_50 else 6
    elif abs(price - sma_200) / sma_200 <= 0.05 and 40 <= rsi <= 55:
        return 5 if above_50 else 4
    elif not above_50 and above_200 and rsi < 50:
        return 3 if rsi >= 40 else 2
    else:
        return 1

@app.get("/technicals")
def get_technicals(symbol: str):
    try:
        closes = get_daily_closes(symbol.upper(), days=260)
        if len(closes) < 200:
            return {"error": f"Insufficient history for {symbol} ({len(closes)} days)"}
        price = float(closes.iloc[-1])
        sma_50 = float(closes.tail(50).mean())
        sma_200 = float(closes.tail(200).mean())
        rsi_14 = compute_rsi(closes)
        rsi_w = compute_weekly_rsi(closes)
        high_52 = float(closes.tail(252).max())
        low_52 = float(closes.tail(252).min())
        mom_score = compute_momentum_score(price, sma_50, sma_200, rsi_14, high_52)
        return {
            "symbol": symbol.upper(),
            "price": round(price, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2),
            "pct_above_200": round((price - sma_200) / sma_200 * 100, 1),
            "price_vs_200": "above" if price > sma_200 else "below",
            "rsi_14": rsi_14,
            "rsi_weekly": rsi_w,
            "rsi_weekly_kill": rsi_w > 85,
            "high_52wk": round(high_52, 2),
            "low_52wk": round(low_52, 2),
            "pct_from_52wk_high": round((price - high_52) / high_52 * 100, 1),
            "near_52wk_high": price >= (high_52 * 0.90),
            "momentum_score": mom_score
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@app.get("/technicals/batch")
def get_technicals_batch(symbols: str):
    tickers = [s.strip().upper() for s in symbols.split(",")][:10]
    results = []
    for t in tickers:
        results.append(get_technicals(t))
    return results
```

---

## Updated Data Sources Table (V2)

| Data Need | V1 Source | V2 Source | Status |
|-----------|-----------|-----------|--------|
| Price, market cap, sector | FMP profile-symbol | FMP profile-symbol | Working |
| 50-DMA, 200-DMA | FMP blocked / estimated | Railway /technicals | Fix |
| RSI-14 (daily) | Railway /conviction curl only | Railway /technicals MCP | Fix |
| RSI weekly (hard kill) | Not computed | Railway /technicals new | New |
| Momentum score | Manual scoring | Railway /technicals pre-scored | New |
| Revenue/EPS (4 quarters) | FMP statements blocked | Web search earnings releases | Manual |
| Gross margin, FCF | FMP statements blocked | Web search / 10-Q summary | Manual |
| Piotroski score | Railway /vet curl only | Railway /vet + add to /technicals | Fix |
| Analyst estimates/revisions | FMP analyst blocked | Web search consensus data | Manual |
| Insider transactions | FMP insiderTrades blocked | FMP insiderTrades retest | Retest |
| Earnings date/proximity | FMP calendar working | FMP calendar | Working |
| Restricted entities | Skill file | Skill file | Working |

---

## Implementation Checklist (Before July 1)

- [ ] Add get_daily_closes() to Railway main.py
- [ ] Add compute_rsi() and compute_weekly_rsi()
- [ ] Add compute_momentum_score()
- [ ] Add /technicals endpoint
- [ ] Add /technicals/batch endpoint
- [ ] Test: curl -H "x-api-key: ..." https://mktpxdata72.com/technicals?symbol=FICO
- [ ] Verify GCC Railway MCP connector can reach /technicals
- [ ] Update rothquant/SKILL.md data sources table
- [ ] Push updated main.py to gsaf5/fmp-service
- [ ] Update memory edit for RothQuant to reference V2 endpoint
- [ ] Run July RothQuant with full live Momentum scoring

---

## V3 Roadmap

OpenBB SDK (openbb-fmp + openbb-sec only) for institutional ownership + SEC filing sentiment.
Do NOT pip install openbb[all] on Railway. Target: September 2026.

*Push to: gsaf5/fmp-service/skills/rothquant/ROTHQUANT_V2_INFRASTRUCTURE.md*
