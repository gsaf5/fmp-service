import os
import asyncio
import math
from datetime import datetime
from fastapi import FastAPI, Query, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import httpx

app = FastAPI(title="Claude Market API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── Auth ──────────────────────────────────────────────────────────────────────
API_SECRET = os.environ.get("API_SECRET", "")

async def verify_key(x_api_key: str = Header(default=None)):
    if API_SECRET and x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

FMP_KEY = os.environ.get("FMP_API_KEY", "")
FMP_BASE = "https://financialmodelingprep.com/api/v3"   # ← v3, confirmed Starter

GIST_ID = "4c5cd13043497addfbbe3eaaf0ae67a8"
GIST_URL = f"https://gist.githubusercontent.com/gsaf5/{GIST_ID}/raw/watchlist.json"

RED_FLAG_KEYWORDS = [
    "class action", "sec investigation", "going concern", "shelf registration",
    "atm offering", "restatement", "subpoena", "dilution", "default", "delisted",
    "fraud", "bankruptcy", "nasdaq notice", "nyse notice"
]

# ── Helpers ───────────────────────────────────────────────────────────────────
async def fmp(client, path, params=None):
    p = params or {}
    p["apikey"] = FMP_KEY
    try:
        r = await client.get(f"{FMP_BASE}{path}", params=p, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def first(data):
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    return {}

def no_cache(data):
    return JSONResponse(content=data, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Vary": "*"
    })

def calc_rsi(prices, period=14):
    """Calculate RSI from list of closing prices (newest first)."""
    if len(prices) < period + 1:
        return None
    closes = list(reversed(prices))  # oldest first for calculation
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i-1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def scan_news(articles):
    flags = []
    for a in (articles or [])[:15]:
        text = (a.get("title", "") + " " + a.get("text", "") + " " + a.get("summary", "")).lower()
        for kw in RED_FLAG_KEYWORDS:
            if kw in text:
                flags.append({"keyword": kw, "headline": a.get("title", "")[:120],
                               "date": str(a.get("publishedDate", ""))[:10]})
                break
    return {"pass": len(flags) == 0, "flags": flags, "articles_scanned": min(len(articles or []), 15)}

def agg_insider(data):
    if not isinstance(data, list) or not data:
        return {}
    recent = data[:4]
    total_acq = sum(q.get("acquiredTransactions", 0) or 0 for q in recent)
    total_disp = sum(q.get("disposedTransactions", 0) or 0 for q in recent)
    total = total_acq + total_disp
    sell_pct = round((total_disp / total) * 100, 1) if total > 0 else 0
    return {
        "total_buy_transactions": total_acq,
        "total_sell_transactions": total_disp,
        "net_direction": "NET BUYER" if total_acq > total_disp else "NET SELLER" if total_disp > total_acq else "NEUTRAL",
        "sell_pct": sell_pct,
        "buy_pct": round((total_acq / total) * 100, 1) if total > 0 else 0,
        "kill_flag": sell_pct > 60,
        "quarters_analyzed": len(recent)
    }

async def fetch_watchlist_data():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(GIST_URL, timeout=8)
            return r.json()
    except Exception:
        return {}

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "Claude Market API v4.0", "ts": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    html = """<!DOCTYPE html>
<html>
<head>
<title>mktpxdata72.com - Claude Market API</title>
<meta name="description" content="mktpxdata72.com Claude Market API - FMP proxy for conviction scoring and portfolio scans">
</head>
<body>
<h1>mktpxdata72.com - Claude Market API v4.0</h1>
<p>Primary: <a href="https://mktpxdata72.com">https://mktpxdata72.com</a></p>
<p>Backup: <a href="https://web-production-7e4e6.up.railway.app">https://web-production-7e4e6.up.railway.app</a></p>
<ul>
<li><a href="https://mktpxdata72.com/ping">https://mktpxdata72.com/ping</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/conviction?symbol=RKLB">https://web-production-7e4e6.up.railway.app/conviction?symbol=RKLB</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/quote?symbols=RKLB,ASTS">https://web-production-7e4e6.up.railway.app/quote?symbols=RKLB,ASTS</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/scan?symbols=RKLB,ASTS">https://web-production-7e4e6.up.railway.app/scan?symbols=RKLB,ASTS</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/vet?symbol=RKLB">https://web-production-7e4e6.up.railway.app/vet?symbol=RKLB</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/financials?symbol=RKLB">https://web-production-7e4e6.up.railway.app/financials?symbol=RKLB</a></li>
<li><a href="https://web-production-7e4e6.up.railway.app/watchlist">https://web-production-7e4e6.up.railway.app/watchlist</a></li>
</ul>
</body>
</html>"""
    return HTMLResponse(content=html)

@app.get("/quote")
async def quote(symbols: str = Query(...), _key=Depends(verify_key)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[fmp(client, f"/quote/{t}") for t in tickers])
    output = []
    for t, r in zip(tickers, results):
        d = first(r)
        output.append({
            "symbol": t,
            "price": d.get("price", 0),
            "change": d.get("change"),
            "changesPercentage": d.get("changesPercentage"),
            "dayLow": d.get("dayLow"),
            "dayHigh": d.get("dayHigh"),
            "yearLow": d.get("yearLow"),
            "yearHigh": d.get("yearHigh"),
            "volume": d.get("volume"),
            "avgVolume": d.get("avgVolume"),
            "marketCap": d.get("marketCap"),
            "priceAvg50": d.get("priceAvg50"),
            "priceAvg200": d.get("priceAvg200"),
        })
    return no_cache({"timestamp": datetime.utcnow().isoformat(), "count": len(tickers), "data": output})

@app.get("/conviction")
async def conviction(symbol: str = Query(...), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        (quote_r, profile_r, income_r, earnings_r, grades_r,
         pt_r, insider_r, score_r, news_r, hist_r, metrics_r) = await asyncio.gather(
            fmp(client, f"/quote/{sym}"),
            fmp(client, f"/profile/{sym}"),
            fmp(client, "/income-statement", {"symbol": sym, "limit": 5}),
            fmp(client, "/earnings-surprises", {"symbol": sym, "limit": 8}),
            fmp(client, "/grade", {"symbol": sym, "limit": 20}),
            fmp(client, "/price-target-summary", {"symbol": sym}),
            fmp(client, "/insider-trading/statistics", {"symbol": sym}),
            fmp(client, "/score", {"symbol": sym}),
            fmp(client, "/stock_news", {"tickers": sym, "limit": 20}),
            fmp(client, f"/historical-price-full/{sym}", {"timeseries": 30}),
            fmp(client, "/key-metrics", {"symbol": sym, "period": "annual", "limit": 2}),
            return_exceptions=True
        )

    # ── Quote & Profile ───────────────────────────────────────────────────────
    q = first(quote_r)
    p = first(profile_r) if isinstance(profile_r, list) else (profile_r if isinstance(profile_r, dict) else {})
    current_price = q.get("price", 0) or 0

    # ── RSI — calculated locally from historical prices ───────────────────────
    hist_prices = []
    if isinstance(hist_r, dict) and "historical" in hist_r:
        hist_prices = [h["close"] for h in hist_r["historical"][:30] if "close" in h]
    elif isinstance(hist_r, list):
        hist_prices = [h["close"] for h in hist_r[:30] if "close" in h]

    rsi_history = []
    if isinstance(hist_r, dict) and "historical" in hist_r:
        for h in hist_r["historical"][:10]:
            rsi_history.append({"date": str(h.get("date", ""))[:10], "close": h.get("close")})

    rsi_current = calc_rsi(hist_prices) if len(hist_prices) >= 15 else None
    rsi_dir = "N/A"
    if rsi_current and len(hist_prices) >= 17:
        rsi_prev = calc_rsi(hist_prices[2:]) if len(hist_prices) >= 17 else None
        if rsi_prev:
            rsi_dir = "RISING" if rsi_current > rsi_prev else "FALLING" if rsi_current < rsi_prev else "FLAT"
    rsi_sig = ("OVERSOLD" if rsi_current and rsi_current < 30
               else "OVERBOUGHT" if rsi_current and rsi_current > 70
               else "NEUTRAL" if rsi_current else "N/A")

    # ── EPS History ───────────────────────────────────────────────────────────
    eps_history = []
    if isinstance(earnings_r, list):
        for e in earnings_r[:4]:
            actual, est = e.get("actualEarningResult"), e.get("estimatedEarning")
            beat = actual >= est if actual is not None and est is not None else None
            pct = round(((actual - est) / abs(est)) * 100, 1) if beat is not None and est != 0 else None
            eps_history.append({"date": str(e.get("date", ""))[:10], "estimated": est,
                                 "actual": actual, "beat": beat, "surprise_pct": pct})
    beat_count = sum(1 for e in eps_history if e.get("beat"))

    # ── Revenue Trend ─────────────────────────────────────────────────────────
    revenue_trend = [{"date": str(s.get("date", ""))[:10], "revenue": s.get("revenue"),
                      "grossProfit": s.get("grossProfit"), "operatingIncome": s.get("operatingIncome"),
                      "netIncome": s.get("netIncome"), "eps": s.get("eps")}
                     for s in (income_r if isinstance(income_r, list) else [])[:4]]

    # ── Analyst Grades ────────────────────────────────────────────────────────
    grade_summary = {}
    if isinstance(grades_r, list) and grades_r:
        recent5 = grades_r[:5]
        upgrades = sum(1 for g in recent5 if g.get("action", "").lower() in ["upgrade", "initiated", "reiterated"])
        downgrades = sum(1 for g in recent5 if g.get("action", "").lower() == "downgrade")
        grade_summary = {
            "analyst_count": len(set(g.get("gradingCompany", "") for g in grades_r)),
            "recent_grades": [{"company": g.get("gradingCompany"), "grade": g.get("newGrade"),
                               "action": g.get("action"), "date": str(g.get("date", ""))[:10]}
                              for g in recent5],
            "upgrades_last5": upgrades,
            "downgrades_last5": downgrades
        }

    # ── Price Targets ─────────────────────────────────────────────────────────
    pt_summary = {}
    pt = first(pt_r)
    if pt and isinstance(pt, dict) and pt.get("lastMonthAvgPriceTarget"):
        pt_summary = {
            "last_month_avg": pt.get("lastMonthAvgPriceTarget"),
            "last_month_count": pt.get("lastMonthAvgPriceTargetCount"),
            "last_quarter_avg": pt.get("lastQuarterAvgPriceTarget"),
            "last_year_avg": pt.get("lastYearAvgPriceTarget"),
            "implied_upside_pct": round(((pt.get("lastMonthAvgPriceTarget", 0) - current_price) / current_price) * 100, 1) if current_price else None,
            "current_price": current_price,
            "above_target": current_price > (pt.get("lastMonthAvgPriceTarget") or 0)
        }

    # ── Key Metrics (annual) ──────────────────────────────────────────────────
    km = first(metrics_r)
    key_metrics = {}
    if km and isinstance(km, dict):
        key_metrics = {
            "pe": km.get("peRatio"),
            "peg": km.get("pegRatio"),
            "pb": km.get("pbRatio"),
            "ps": km.get("priceToSalesRatio"),
            "ev_ebitda": km.get("evToEbitda"),
            "debt_to_equity": km.get("debtToEquity"),
            "current_ratio": km.get("currentRatio"),
            "roe": km.get("roe"),
            "revenue_per_share": km.get("revenuePerShare"),
            "period": km.get("period"),
            "date": str(km.get("date", ""))[:10]
        }

    # ── Financial Scores ──────────────────────────────────────────────────────
    sc = first(score_r)
    financial_scores = {}
    if sc and isinstance(sc, dict) and "altmanZScore" in sc:
        z = sc.get("altmanZScore")
        f = sc.get("piotroskiScore")
        financial_scores = {
            "altman_z": z,
            "piotroski_f": f,
            "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE" if z else "N/A",
            "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)
        }

    # ── Insider ───────────────────────────────────────────────────────────────
    insider = agg_insider(insider_r)

    # ── News Scan ─────────────────────────────────────────────────────────────
    news_result = scan_news(news_r if isinstance(news_r, list) else [])

    # ── Phase 0 Gates ─────────────────────────────────────────────────────────
    analyst_count = grade_summary.get("analyst_count")
    downgrades = grade_summary.get("downgrades_last5", 0)
    pt_upside = pt_summary.get("implied_upside_pct")

    gate_insider = not insider.get("kill_flag", False)
    gate_balance = not financial_scores.get("kill_flag", False)
    gate_analyst = analyst_count is None or (analyst_count <= 14 and downgrades == 0)
    gate_pt = pt_upside is None or pt_upside > 0
    gate_news = news_result["pass"]

    gates_passed = sum([gate_insider, gate_balance, gate_analyst, gate_pt, gate_news])

    return no_cache({
        "symbol": sym,
        "timestamp": datetime.utcnow().isoformat(),
        "quote": {
            "price": current_price,
            "change": q.get("change"),
            "changesPercentage": q.get("changesPercentage"),
            "dayLow": q.get("dayLow"),
            "dayHigh": q.get("dayHigh"),
            "yearLow": q.get("yearLow"),
            "yearHigh": q.get("yearHigh"),
            "volume": q.get("volume"),
            "avgVolume": q.get("avgVolume"),
            "marketCap": q.get("marketCap"),
            "priceAvg50": q.get("priceAvg50"),
            "priceAvg200": q.get("priceAvg200"),
        },
        "profile": {
            "name": p.get("companyName"),
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "exchange": p.get("exchangeShortName"),
            "description": (p.get("description") or "")[:300],
            "ceo": p.get("ceo"),
            "employees": p.get("fullTimeEmployees"),
            "beta": p.get("beta"),
            "ipoDate": p.get("ipoDate"),
        },
        "technicals": {
            "rsi_current": rsi_current,
            "rsi_direction": rsi_dir,
            "rsi_signal": rsi_sig,
            "rsi_calculated_from": f"{len(hist_prices)} days of price history",
            "price_history": rsi_history[:10]
        },
        "fundamentals": {
            "key_metrics": key_metrics,
            "revenue_trend": revenue_trend,
            "beat_count": beat_count,
            "beat_rate": f"{beat_count}/4",
            "eps_history": eps_history
        },
        "analyst": {
            "grades": grade_summary,
            "price_targets": pt_summary
        },
        "insider": insider,
        "financial_scores": financial_scores,
        "news_scan": news_result,
        "phase0_gate": {
            "gates_passed": gates_passed,
            "gates_failed": 5 - gates_passed,
            "overall": "PASS" if gates_passed >= 4 else f"FAIL ({5-gates_passed} gates failed)",
            "results": {
                "check1_insider": {"pass": gate_insider, "detail": insider},
                "check2_balance_sheet": {"pass": gate_balance, "detail": financial_scores},
                "check3_analyst_coverage": {"pass": gate_analyst, "analyst_count": analyst_count, "downgrades_last5": downgrades},
                "check4_price_target": {"pass": gate_pt, "detail": pt_summary},
                "check5_news": {"pass": gate_news, "detail": news_result}
            }
        }
    })

@app.get("/scan")
async def scan(symbols: str = Query(...), _key=Depends(verify_key)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        quotes = await asyncio.gather(*[fmp(client, f"/quote/{t}") for t in tickers])
        hists = await asyncio.gather(*[fmp(client, f"/historical-price-full/{t}", {"timeseries": 20}) for t in tickers])

    output = []
    for t, q_r, h_r in zip(tickers, quotes, hists):
        q = first(q_r)
        hist_prices = []
        if isinstance(h_r, dict) and "historical" in h_r:
            hist_prices = [h["close"] for h in h_r["historical"][:20] if "close" in h]
        rsi = calc_rsi(hist_prices) if len(hist_prices) >= 15 else None
        avg_vol = q.get("avgVolume") or 1
        vol = q.get("volume") or 0
        output.append({
            "symbol": t,
            "price": q.get("price", 0),
            "change_pct": q.get("changesPercentage"),
            "volume": vol,
            "avg_volume": avg_vol,
            "volume_ratio": round(vol / avg_vol, 2) if avg_vol else None,
            "rsi": rsi,
            "rsi_signal": ("OVERSOLD" if rsi and rsi < 30 else "OVERBOUGHT" if rsi and rsi > 70 else "NEUTRAL" if rsi else "N/A"),
            "year_low": q.get("yearLow"),
            "year_high": q.get("yearHigh"),
            "market_cap": q.get("marketCap"),
        })
    return no_cache({"timestamp": datetime.utcnow().isoformat(), "count": len(tickers), "data": output})

@app.get("/vet")
async def vet(symbol: str = Query(...), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        insider_r, score_r, grades_r, pt_r, news_r, quote_r = await asyncio.gather(
            fmp(client, "/insider-trading/statistics", {"symbol": sym}),
            fmp(client, "/score", {"symbol": sym}),
            fmp(client, "/grade", {"symbol": sym, "limit": 20}),
            fmp(client, "/price-target-summary", {"symbol": sym}),
            fmp(client, "/stock_news", {"tickers": sym, "limit": 20}),
            fmp(client, f"/quote/{sym}"),
            return_exceptions=True
        )

    insider = agg_insider(insider_r)
    sc = first(score_r)
    scores = {}
    if sc and isinstance(sc, dict) and "altmanZScore" in sc:
        z, f = sc.get("altmanZScore"), sc.get("piotroskiScore")
        scores = {"altman_z": z, "piotroski_f": f,
                  "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE",
                  "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)}

    analyst_count = None
    downgrades = 0
    if isinstance(grades_r, list) and grades_r:
        analyst_count = len(set(g.get("gradingCompany", "") for g in grades_r))
        downgrades = sum(1 for g in grades_r[:5] if g.get("action", "").lower() == "downgrade")

    pt = first(pt_r)
    q = first(quote_r)
    current_price = q.get("price", 0) or 0
    pt_upside = None
    if pt and pt.get("lastMonthAvgPriceTarget") and current_price:
        pt_upside = round(((pt["lastMonthAvgPriceTarget"] - current_price) / current_price) * 100, 1)

    news_result = scan_news(news_r if isinstance(news_r, list) else [])

    gate1 = not insider.get("kill_flag", False)
    gate2 = not scores.get("kill_flag", False)
    gate3 = analyst_count is None or (analyst_count <= 14 and downgrades == 0)
    gate4 = pt_upside is None or pt_upside > 0
    gate5 = news_result["pass"]
    passed = sum([gate1, gate2, gate3, gate4, gate5])

    return no_cache({
        "symbol": sym,
        "timestamp": datetime.utcnow().isoformat(),
        "price": current_price,
        "phase0_gate": {
            "overall": "PASS" if passed >= 4 else f"FAIL ({5-passed} gates failed)",
            "gates_passed": passed,
            "check1_insider": {"pass": gate1, "detail": insider},
            "check2_balance_sheet": {"pass": gate2, "detail": scores},
            "check3_analyst": {"pass": gate3, "analyst_count": analyst_count, "downgrades": downgrades},
            "check4_price_target": {"pass": gate4, "implied_upside_pct": pt_upside,
                                    "avg_pt": pt.get("lastMonthAvgPriceTarget") if pt else None},
            "check5_news": {"pass": gate5, "detail": news_result}
        }
    })

@app.get("/financials")
async def financials(symbol: str = Query(...), period: str = Query(default="annual"),
                     limit: int = Query(default=4), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        income_r, balance_r, cashflow_r, scores_r, earnings_r, metrics_r = await asyncio.gather(
            fmp(client, "/income-statement", {"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "/balance-sheet-statement", {"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "/cash-flow-statement", {"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "/score", {"symbol": sym}),
            fmp(client, "/earnings-surprises", {"symbol": sym, "limit": 8}),
            fmp(client, "/key-metrics", {"symbol": sym, "period": "annual", "limit": limit}),
        )

    eps_history = []
    if isinstance(earnings_r, list):
        for e in earnings_r[:4]:
            actual, est = e.get("actualEarningResult"), e.get("estimatedEarning")
            beat = actual >= est if actual is not None and est is not None else None
            pct = round(((actual - est) / abs(est)) * 100, 1) if beat is not None and est != 0 else None
            eps_history.append({"date": str(e.get("date", ""))[:10], "estimated": est,
                                 "actual": actual, "beat": beat, "surprise_pct": pct})

    sc = first(scores_r)
    score_summary = {}
    if sc and isinstance(sc, dict) and "altmanZScore" in sc:
        z, f = sc.get("altmanZScore"), sc.get("piotroskiScore")
        score_summary = {"altman_z": z, "piotroski_f": f,
                         "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE",
                         "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)}

    return no_cache({
        "symbol": sym, "period": period,
        "timestamp": datetime.utcnow().isoformat(),
        "income_statement": income_r if isinstance(income_r, list) else [],
        "balance_sheet": balance_r if isinstance(balance_r, list) else [],
        "cash_flow": cashflow_r if isinstance(cashflow_r, list) else [],
        "key_metrics": metrics_r if isinstance(metrics_r, list) else [],
        "financial_scores": score_summary,
        "eps_history": eps_history,
        "beat_rate": f"{sum(1 for e in eps_history if e.get('beat'))}/4"
    })

@app.get("/watchlist")
async def watchlist(_key=Depends(verify_key)):
    wl = await fetch_watchlist_data()
    if not wl or "tickers" not in wl:
        return no_cache({"error": "Watchlist unavailable", "timestamp": datetime.utcnow().isoformat()})

    tickers_data = wl.get("tickers", {})
    symbols = list(tickers_data.keys())

    async with httpx.AsyncClient() as client:
        quotes = await asyncio.gather(*[fmp(client, f"/quote/{s}") for s in symbols])

    output = []
    for sym, q_r in zip(symbols, quotes):
        q = first(q_r)
        price = q.get("price", 0) or 0
        entry = tickers_data.get(sym, {})
        z1 = entry.get("z1", [None, None])
        z2 = entry.get("z2")
        stop = entry.get("stop")
        t1 = entry.get("t1")
        t2 = entry.get("t2")

        in_z1 = z1 and len(z1) == 2 and z1[0] <= price <= z1[1]
        in_z2 = z2 and isinstance(z2, list) and len(z2) == 2 and z2[0] <= price <= z2[1]
        below_stop = stop and price < stop
        zone = "Z1 ✅" if in_z1 else "Z2 ✅" if in_z2 else "BELOW STOP ⚠️" if below_stop else "WATCHING"

        upside_t1 = round(((t1 - price) / price) * 100, 1) if t1 and price else None
        upside_t2 = round(((t2 - price) / price) * 100, 1) if t2 and price else None

        output.append({
            "symbol": sym, "price": price,
            "change_pct": q.get("changesPercentage"),
            "zone": zone,
            "z1_range": z1, "z2_trigger": z2,
            "stop": stop, "t1": t1, "t2": t2,
            "upside_t1_pct": upside_t1, "upside_t2_pct": upside_t2,
            "tier": entry.get("tier"), "notes": entry.get("notes", ""),
        })

    return no_cache({
        "timestamp": datetime.utcnow().isoformat(),
        "updated": wl.get("updated"),
        "count": len(output),
        "watchlist": output
    })
