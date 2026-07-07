# RothQuant Universe Endpoint — `/universe`
**Created:** June 20, 2026
**Purpose:** Solve the core RothQuant limitation — Claude defaulting to familiar names
instead of screening a proper candidate universe. This endpoint gives RothQuant a real
starting pool of 300–500 pre-filtered candidates every month.

---

## The Problem It Solves

Without this endpoint, RothQuant recycles ~10 known names from memory instead of
systematically screening the market. A real quant engine needs a starting universe
before scoring begins. Seeking Alpha screens 6,000 stocks daily. We need at least
500 quality candidates monthly.

---

## Data Source

FMP `sp-500` constituent list — 503 names with sector, subsector, market cap, and
headquarters data. Already confirmed available on Gary's FMP plan tier (tested June 20 2026).
Returns ticker, name, sector, subSector — enough for universe construction and sector
concentration tracking.

---

## Endpoint: `GET /universe`

### Query Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `exclude_sectors` | `Utilities,Real Estate` | Comma-separated sectors to exclude (low-growth) |
| `exclude_restricted` | `true` | Auto-filter restricted entities from Jen's list |
| `min_price` | `10` | Minimum stock price |
| `format` | `tickers` | `tickers` = array of symbols only; `full` = array with name+sector |

### What it does internally

1. Fetches S&P 500 constituent list from FMP `sp-500` endpoint
2. Applies sector exclusions (Utilities, Real Estate by default — low-growth, dividend-focused)
3. Applies restricted entities filter (hardcoded list from Jen's compliance list)
4. Returns clean candidate list ready for `/technicals/batch` scoring

### What it does NOT do

- Does NOT check price (FMP batch quote blocked on current plan)
- Does NOT check earnings proximity (call `/calendar` separately if needed)
- Does NOT score factors — that's Claude's job

---

## Python Implementation for Railway `main.py`

```python
# Restricted entities from Jen's compliance list (tickers only)
RESTRICTED_TICKERS = {
    "AFRM","AFL","AIG","AMC","DOX","NLY","APPN","AVPT","AVDX","AXTA",
    "BW","BANC","BANF","BLKB","BNT","BFST","CCBG","CSL","KMX","CVNA",
    "CCCS","CNC","CI","CIVI","CME","CNO","CSGP","CRBG","CRSS","DLX",
    "DENN","DB","RDY","DFH","ELAN","ET","ENLC","ESCA","EXEL","INBK",
    "FRME","FMBH","FSFG","FLS","FL","FBRT","FLL","GEN","GBCI","GPN",
    "GMED","GOGO","LOPE","GRNT","GECC","GSBC","HRB","HASI","HBI","HAYW",
    "HCI","HBIA","HQI","HOMB","HTBI","HBNC","HLI","HUM","ICAD","IROQ",
    "IBKR","IBOC","ITIC","JBHT","JRVR","JAI","JMIA","KCLI","KBH","KFFB",
    "KEQU","KEX","KKR","LEGH","LEG","LIN","LOB","LYFT","MMP","MBIN",
    "MRCY","MESA","MAA","MODV","MUR","NBHC","NRC","NWLI","NAVI","NIC",
    "NODK","NSC","OCFC","OLN","ONB","OSBC","OGS","OKE","KAR","KIDS",
    "OBK","PEBK","PEBO","PGTI","PDLB","PRAA","FRST","PTC","PVH","RBA",
    "REXR","RMBI","RLJ","ROK","ROP","RMBL","RUSHA","RYAN","SBR","SEB",
    "SNLC","SFBS","BSRR","SFNC","SKX","SWKS","SLDE","SMBK","SAH","SPFI",
    "SMBC","SR","SSNC","SCBFY","STWD","SPLP","SF","SYBT","STRM","SLF",
    "SPWR","SNV","TAK","TDS","TS","TX","TCS","SO","TOWN","TSCO","UDR",
    "ULTA","UNP","UTI","UPL","UWHR","VRA","MDRX","VERX","VSEC","WSBF",
    "WEAV","WELL","WEST","WHG","WRLD","ZIM"
}

# Sectors to exclude by default (low-growth, dividend-focused)
DEFAULT_EXCLUDE_SECTORS = {"Utilities", "Real Estate"}

@app.get("/universe")
def get_universe(
    exclude_sectors: str = "Utilities,Real Estate",
    exclude_restricted: bool = True,
    format: str = "tickers"
):
    """
    Returns pre-filtered S&P 500 candidates for RothQuant monthly screening.
    Excludes low-growth sectors and compliance-restricted tickers by default.
    """
    try:
        # Fetch S&P 500 constituents from FMP
        url = "https://financialmodelingprep.com/api/v3/sp500_constituent"
        params = {"apikey": FMP_KEY}
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        constituents = r.json()

        # Parse excluded sectors
        excluded = {s.strip() for s in exclude_sectors.split(",")} if exclude_sectors else set()

        # Filter
        filtered = []
        killed_restricted = []
        killed_sector = []

        for stock in constituents:
            symbol = stock.get("symbol", "").upper()
            sector = stock.get("sector", "")

            # Sector filter
            if sector in excluded:
                killed_sector.append(symbol)
                continue

            # Restricted entities filter
            if exclude_restricted and symbol in RESTRICTED_TICKERS:
                killed_restricted.append(symbol)
                continue

            filtered.append(stock)

        # Build response
        if format == "tickers":
            result = [s["symbol"] for s in filtered]
        else:
            result = [
                {
                    "symbol": s["symbol"],
                    "name": s["name"],
                    "sector": s.get("sector", ""),
                    "subSector": s.get("subSector", "")
                }
                for s in filtered
            ]

        return {
            "universe_size": len(result),
            "excluded_sectors": list(excluded),
            "restricted_killed": len(killed_restricted),
            "sector_killed": len(killed_sector),
            "as_of": "S&P 500 constituents",
            "tickers": result if format == "tickers" else None,
            "stocks": result if format == "full" else None
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/universe/sector-breakdown")
def get_universe_sector_breakdown():
    """
    Returns sector distribution of the filtered RothQuant universe.
    Use before scoring to understand what sectors are represented.
    """
    try:
        data = get_universe(format="full")
        stocks = data.get("stocks", [])

        from collections import Counter
        sector_counts = Counter(s["sector"] for s in stocks)

        return {
            "universe_size": data["universe_size"],
            "sector_distribution": dict(sector_counts.most_common()),
            "restricted_killed": data["restricted_killed"],
            "sector_killed": data["sector_killed"]
        }
    except Exception as e:
        return {"error": str(e)}
```

---

## How RothQuant Uses This Endpoint

**Monthly RothQuant workflow with `/universe`:**

```
STEP 1: GET /universe?format=full
→ Returns ~380-400 filtered candidates with sector labels
→ Claude uses sector distribution to plan scoring batches

STEP 2: Group by sector, identify highest-momentum sectors first
→ Focus scoring on Technology, Industrials, Healthcare, Financials
→ Skip Consumer Defensive, Utilities, Real Estate (low-growth default)

STEP 3: GET /technicals/batch?symbols=TICKER1,TICKER2,...
→ Run in batches of 10 (FMP rate limit)
→ Pre-score Factor 4 (Momentum) for all candidates

STEP 4: Sort by momentum_score descending, take top 30-50
→ These are the momentum leaders in the universe

STEP 5: Apply Factor 1-3 and Factor 5 scoring to top 30-50
→ Web search for revenue/EPS/revisions data per name
→ Compile full 35-point scores

STEP 6: Apply hard-kill gates, rank, output Top 10
```

---

## FMP API Endpoint Reference

The S&P 500 constituent list is at:
```
GET https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={KEY}
```
Returns: symbol, name, sector, subSector, headQuarter, dateFirstAdded, cik, founded

**Confirmed available on Gary's FMP Starter plan tier (tested June 20, 2026).**

---

## V2 Universe Expansion (Future)

When ready to go beyond S&P 500:
- Add Russell 1000 endpoint: `GET /api/v3/russell1000_constituent`
- Combined universe = ~1,200 names after deduplication
- Still manageable for monthly batch technicals scoring

---

## Implementation Checklist

- [ ] Add RESTRICTED_TICKERS set to Railway `main.py`
- [ ] Add `get_universe()` endpoint
- [ ] Add `get_universe/sector-breakdown` endpoint
- [ ] Test: `curl -H "x-api-key: ..." https://mktpxdata72.com/universe`
- [ ] Test with format=full to verify sector labels
- [ ] Verify GCC Railway MCP connector can reach `/universe`
- [ ] Update `rothquant/SKILL.md` Step 1 to call `/universe` first
- [ ] Push updated `main.py` to `gsaf5/fmp-service`
- [ ] Push this doc to `gsaf5/fmp-service/skills/rothquant/`

---

## SKILL.md Update Required

In `STEP 0 — PLATFORM DETECTION`, add:

> **Before sourcing candidates:**
> Desktop: Call Railway `/universe?format=full` via GCC MCP connector.
> Returns ~380 pre-filtered S&P 500 names excluding Utilities, Real Estate,
> and all restricted entities. Use this as the starting candidate pool.
> Group by sector, batch through `/technicals/batch` for momentum pre-scoring,
> then apply full 5-factor scoring to top 30-50 momentum leaders.
> Mobile: Same via GCC Railway MCP connector.

---

*Push to: `gsaf5/fmp-service/skills/rothquant/ROTHQUANT_UNIVERSE_ENDPOINT.md`*
*Created from June 20, 2026 RothQuant session — universe gap identified during Run 2*
