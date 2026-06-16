import os
import asyncio
import math
from datetime import datetime
from fastapi import FastAPI, Query, Depends, Header, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import httpx

app = FastAPI(title="Claude Market API", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

API_SECRET = os.environ.get("API_SECRET", "")
async def verify_key(x_api_key: str = Header(default=None), apikey: str = Query(default=None)):
    key = x_api_key or apikey
    if API_SECRET and key != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

FMP_KEY  = os.environ.get("FMP_API_KEY", "")
FMP_BASE = "https://financialmodelingprep.com/stable"

GIST_ID  = "4c5cd13043497addfbbe3eaaf0ae67a8"
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
        r = await client.get(f"{FMP_BASE}/{path}", params=p, timeout=12)
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
        "Pragma": "no-cache", "Vary": "*"
    })

def momentum_to_rsi_proxy(change_data):
    """
    Since FMP stable has no per-stock historical price endpoint,
    we derive a momentum signal from price-change percentages.
    1M > 10% AND 3M > 20% = bullish (RSI proxy > 60)
    1M < -10% AND 3M < -10% = oversold (RSI proxy < 40)
    """
    if not change_data or not isinstance(change_data, dict):
        return None, "N/A", "N/A"
    m1  = change_data.get("1M", 0) or 0
    m3  = change_data.get("3M", 0) or 0
    m6  = change_data.get("6M", 0) or 0
    ytd = change_data.get("ytd", 0) or 0

    score = 50  # neutral baseline
    score += min(m1 * 1.5, 15)
    score += min(m3 * 0.5, 10)
    score = max(10, min(90, score))
    rsi_proxy = round(score, 1)

    if rsi_proxy < 35:
        signal = "OVERSOLD"
    elif rsi_proxy > 65:
        signal = "OVERBOUGHT"
    else:
        signal = "NEUTRAL"

    if m1 > 5:
        direction = "RISING"
    elif m1 < -5:
        direction = "FALLING"
    else:
        direction = "FLAT"

    return rsi_proxy, direction, signal

def scan_news(articles):
    flags = []
    for a in (articles or [])[:15]:
        text = (a.get("title","") + " " + a.get("text","") + " " + a.get("summary","")).lower()
        for kw in RED_FLAG_KEYWORDS:
            if kw in text:
                flags.append({"keyword": kw, "headline": a.get("title","")[:120],
                               "date": str(a.get("publishedDate",""))[:10]})
                break
    return {"pass": len(flags)==0, "flags": flags, "articles_scanned": min(len(articles or []),15)}

def agg_insider(data):
    if not isinstance(data, list) or not data:
        return {}
    recent = data[:4]
    total_acq  = sum(q.get("acquiredTransactions",0) or 0 for q in recent)
    total_disp = sum(q.get("disposedTransactions",0) or 0 for q in recent)
    total = total_acq + total_disp
    sell_pct = round((total_disp/total)*100,1) if total > 0 else 0
    return {
        "total_buy_transactions": total_acq,
        "total_sell_transactions": total_disp,
        "net_direction": "NET BUYER" if total_acq > total_disp else "NET SELLER" if total_disp > total_acq else "NEUTRAL",
        "sell_pct": sell_pct,
        "buy_pct": round((total_acq/total)*100,1) if total > 0 else 0,
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
    return {"status": "ok", "service": "Claude Market API v5.5",
            "ts": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    html = """<!DOCTYPE html>
<html><head>
<title>mktpxdata72.com - Claude Market API</title>
<meta name="description" content="mktpxdata72.com Claude Market API - FMP data proxy for conviction scoring and portfolio scans">
<meta name="google-site-verification" content="IAO9n3Y0Xd0IyEv1tUzXDgWyL72GVLoBHM2nZkC_s_g" />
</head><body>
<h1>mktpxdata72.com - Claude Market API v5.0</h1>
<p>Primary: <a href="https://mktpxdata72.com">https://mktpxdata72.com</a></p>
<p>Backup: <a href="https://web-production-7e4e6.up.railway.app">https://web-production-7e4e6.up.railway.app</a></p>
<ul>
<li><a href="https://mktpxdata72.com/ping">https://mktpxdata72.com/ping</a></li>
<li><a href="https://mktpxdata72.com/conviction?symbol=RKLB">https://mktpxdata72.com/conviction?symbol=RKLB</a></li>
<li><a href="https://mktpxdata72.com/conviction?symbol=ASTS">https://mktpxdata72.com/conviction?symbol=ASTS</a></li>
<li><a href="https://mktpxdata72.com/quote?symbols=RKLB,ASTS,KTOS,NVDA,MSFT">https://mktpxdata72.com/quote?symbols=RKLB,ASTS,KTOS,NVDA,MSFT</a></li>
<li><a href="https://mktpxdata72.com/scan?symbols=RKLB,ASTS,KTOS">https://mktpxdata72.com/scan?symbols=RKLB,ASTS,KTOS</a></li>
<li><a href="https://mktpxdata72.com/vet?symbol=RKLB">https://mktpxdata72.com/vet?symbol=RKLB</a></li>
<li><a href="https://mktpxdata72.com/financials?symbol=RKLB">https://mktpxdata72.com/financials?symbol=RKLB</a></li>
<li><a href="https://mktpxdata72.com/watchlist">https://mktpxdata72.com/watchlist</a></li>
</ul>
</body></html>"""
    return HTMLResponse(content=html)

@app.get("/quote")
async def quote(symbols: str = Query(...), _key=Depends(verify_key)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[fmp(client, "quote", {"symbol": t}) for t in tickers])
    output = []
    for t, r in zip(tickers, results):
        d = first(r)
        output.append({
            "symbol": t,
            "price": d.get("price", 0),
            "change": d.get("change"),
            "changesPercentage": d.get("changePercentage"),
            "dayLow": d.get("dayLow"),
            "dayHigh": d.get("dayHigh"),
            "yearLow": d.get("yearLow") or (d.get("range","").split("-")[0] if d.get("range") else None),
            "yearHigh": d.get("yearHigh") or (d.get("range","").split("-")[-1] if d.get("range") else None),
            "volume": d.get("volume"),
            "avgVolume": d.get("avgVolume"),
            "marketCap": d.get("marketCap"),
            "priceAvg50": d.get("priceAvg50"),
            "priceAvg200": d.get("priceAvg200"),
        })
    return no_cache({"timestamp": datetime.utcnow().isoformat(),
                     "count": len(tickers), "data": output})

@app.get("/conviction")
async def conviction(symbol: str = Query(...), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        (quote_r, profile_r, income_r, earnings_r, grades_r, grades_consensus_r,
         pt_r, insider_r, score_r, news_r, metrics_r, change_r) = await asyncio.gather(
            fmp(client, "quote",                        {"symbol": sym}),
            fmp(client, "profile",                      {"symbol": sym}),
            fmp(client, "income-statement",             {"symbol": sym, "limit": 5}),
            fmp(client, "earnings",                     {"symbol": sym, "limit": 8}),
            fmp(client, "grades",                       {"symbol": sym, "limit": 20}),
            fmp(client, "grades-consensus",             {"symbol": sym}),
            fmp(client, "price-target-summary",         {"symbol": sym}),
            fmp(client, "insider-trading/statistics",   {"symbol": sym}),
            fmp(client, "financial-scores",             {"symbol": sym}),
            fmp(client, "news/stock",                   {"symbol": sym, "limit": 20}),
            fmp(client, "key-metrics",                  {"symbol": sym, "period": "annual", "limit": 2}),
            fmp(client, "stock-price-change",           {"symbol": sym}),
            return_exceptions=True
        )

    # ── Quote & Profile ───────────────────────────────────────────────────────
    q = first(quote_r)
    p = first(profile_r)
    current_price = q.get("price", 0) or 0

    # Parse year range from profile if not in quote
    year_range = p.get("range", "") or ""
    year_low  = q.get("yearLow")  or (year_range.split("-")[0] if "-" in year_range else None)
    year_high = q.get("yearHigh") or (year_range.split("-")[-1] if "-" in year_range else None)

    # ── Momentum / RSI Proxy ──────────────────────────────────────────────────
    change_d = first(change_r)
    rsi_proxy, rsi_dir, rsi_sig = momentum_to_rsi_proxy(change_d)
    momentum = {
        "1D":  change_d.get("1D")  if change_d else None,
        "5D":  change_d.get("5D")  if change_d else None,
        "1M":  change_d.get("1M")  if change_d else None,
        "3M":  change_d.get("3M")  if change_d else None,
        "6M":  change_d.get("6M")  if change_d else None,
        "ytd": change_d.get("ytd") if change_d else None,
        "1Y":  change_d.get("1Y")  if change_d else None,
    }

    # ── EPS History ───────────────────────────────────────────────────────────
    eps_history = []
    if isinstance(earnings_r, list):
        for e in earnings_r[:4]:
            actual = e.get("epsActual")
            est    = e.get("epsEstimated")
            beat   = actual >= est if actual is not None and est is not None else None
            pct    = round(((actual-est)/abs(est))*100,1) if beat is not None and est != 0 else None
            eps_history.append({"date": str(e.get("date",""))[:10],
                                 "estimated": est, "actual": actual,
                                 "beat": beat, "surprise_pct": pct})
    beat_count = sum(1 for e in eps_history if e.get("beat"))

    # ── Revenue Trend ─────────────────────────────────────────────────────────
    revenue_trend = [{"date": str(s.get("date",""))[:10],
                      "revenue": s.get("revenue"),
                      "grossProfit": s.get("grossProfit"),
                      "operatingIncome": s.get("operatingIncome"),
                      "netIncome": s.get("netIncome"),
                      "eps": s.get("eps")}
                     for s in (income_r if isinstance(income_r, list) else [])[:4]]

    # ── Analyst Grades ────────────────────────────────────────────────────────
    consensus = first(grades_consensus_r)
    grade_summary = {}
    if isinstance(grades_r, list) and grades_r:
        recent5   = grades_r[:5]
        upgrades  = sum(1 for g in recent5 if g.get("action","").lower() in ["upgrade","initiated","reiterated"])
        downgrades= sum(1 for g in recent5 if g.get("action","").lower() == "downgrade")
        grade_summary = {
            "analyst_count": len(set(g.get("gradingCompany","") for g in grades_r)),
            "consensus": consensus.get("consensus") if consensus else None,
            "strong_buy": consensus.get("strongBuy") if consensus else None,
            "buy": consensus.get("buy") if consensus else None,
            "hold": consensus.get("hold") if consensus else None,
            "sell": consensus.get("sell") if consensus else None,
            "recent_grades": [{"company": g.get("gradingCompany"),
                                "grade": g.get("newGrade"),
                                "action": g.get("action"),
                                "date": str(g.get("date",""))[:10]} for g in recent5],
            "upgrades_last5": upgrades,
            "downgrades_last5": downgrades
        }

    # ── Price Targets ─────────────────────────────────────────────────────────
    pt = first(pt_r)
    pt_summary = {}
    if pt and isinstance(pt, dict) and pt.get("lastMonthAvgPriceTarget"):
        last_avg = pt["lastMonthAvgPriceTarget"]
        pt_summary = {
            "last_month_avg": last_avg,
            "last_month_count": pt.get("lastMonthCount"),
            "last_quarter_avg": pt.get("lastQuarterAvgPriceTarget"),
            "last_year_avg": pt.get("lastYearAvgPriceTarget"),
            "implied_upside_pct": round(((last_avg - current_price)/current_price)*100,1) if current_price else None,
            "current_price": current_price,
            "above_target": current_price > last_avg
        }

    # ── Key Metrics ───────────────────────────────────────────────────────────
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
            "period": km.get("period"),
            "date": str(km.get("date",""))[:10]
        }

    # ── Financial Scores ──────────────────────────────────────────────────────
    sc = first(score_r)
    financial_scores = {}
    if sc and isinstance(sc, dict) and "altmanZScore" in sc:
        z = sc.get("altmanZScore")
        f = sc.get("piotroskiScore")
        financial_scores = {
            "altman_z": z, "piotroski_f": f,
            "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE" if z else "N/A",
            "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)
        }

    # ── Insider ───────────────────────────────────────────────────────────────
    insider = agg_insider(insider_r)

    # ── News ──────────────────────────────────────────────────────────────────
    news_list = news_r if isinstance(news_r, list) else []
    news_result = scan_news(news_list)

    # ── Phase 0 Gates ─────────────────────────────────────────────────────────
    analyst_count = grade_summary.get("analyst_count")
    downgrades    = grade_summary.get("downgrades_last5", 0)
    pt_upside     = pt_summary.get("implied_upside_pct")

    gate_insider  = not insider.get("kill_flag", False)
    gate_balance  = not financial_scores.get("kill_flag", False)
    gate_analyst  = analyst_count is None or (analyst_count <= 14 and downgrades == 0)
    gate_pt       = pt_upside is None or pt_upside > 0
    gate_news     = news_result["pass"]
    gates_passed  = sum([gate_insider, gate_balance, gate_analyst, gate_pt, gate_news])

    return no_cache({
        "symbol": sym,
        "timestamp": datetime.utcnow().isoformat(),
        "quote": {
            "price": current_price,
            "change": q.get("change"),
            "changesPercentage": q.get("changePercentage"),
            "dayLow": q.get("dayLow"), "dayHigh": q.get("dayHigh"),
            "yearLow": year_low, "yearHigh": year_high,
            "volume": q.get("volume"), "avgVolume": q.get("avgVolume"),
            "marketCap": q.get("marketCap"),
            "priceAvg50": q.get("priceAvg50"), "priceAvg200": q.get("priceAvg200"),
        },
        "profile": {
            "name": p.get("companyName"), "sector": p.get("sector"),
            "industry": p.get("industry"), "exchange": p.get("exchangeShortName"),
            "description": (p.get("description") or "")[:300],
            "ceo": p.get("ceo"), "employees": p.get("fullTimeEmployees"),
            "beta": p.get("beta"), "ipoDate": p.get("ipoDate"),
        },
        "technicals": {
            "rsi_proxy": rsi_proxy,
            "rsi_direction": rsi_dir,
            "rsi_signal": rsi_sig,
            "note": "RSI proxy derived from momentum data (FMP stable has no per-stock historical price endpoint)",
            "momentum": momentum
        },
        "fundamentals": {
            "key_metrics": key_metrics,
            "revenue_trend": revenue_trend,
            "beat_count": beat_count,
            "beat_rate": f"{beat_count}/{len(eps_history)}",
            "eps_history": eps_history
        },
        "analyst": {"grades": grade_summary, "price_targets": pt_summary},
        "insider": insider,
        "financial_scores": financial_scores,
        "news_scan": news_result,
        "phase0_gate": {
            "gates_passed": gates_passed,
            "gates_failed": 5 - gates_passed,
            "overall": "PASS" if gates_passed >= 4 else f"FAIL ({5-gates_passed} gates failed)",
            "results": {
                "check1_insider":          {"pass": gate_insider,  "detail": insider},
                "check2_balance_sheet":    {"pass": gate_balance,  "detail": financial_scores},
                "check3_analyst_coverage": {"pass": gate_analyst,  "analyst_count": analyst_count, "downgrades_last5": downgrades},
                "check4_price_target":     {"pass": gate_pt,       "detail": pt_summary},
                "check5_news":             {"pass": gate_news,     "detail": news_result}
            }
        }
    })

@app.get("/scan")
async def scan(symbols: str = Query(...), _key=Depends(verify_key)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        quotes   = await asyncio.gather(*[fmp(client, "quote", {"symbol": t}) for t in tickers])
        changes  = await asyncio.gather(*[fmp(client, "stock-price-change", {"symbol": t}) for t in tickers])
    output = []
    for t, q_r, c_r in zip(tickers, quotes, changes):
        q = first(q_r)
        c = first(c_r)
        rsi_proxy, rsi_dir, rsi_sig = momentum_to_rsi_proxy(c)
        avg_vol = q.get("avgVolume") or 1
        vol     = q.get("volume") or 0
        output.append({
            "symbol": t,
            "price": q.get("price", 0),
            "change_pct": q.get("changePercentage"),
            "volume": vol,
            "avg_volume": avg_vol,
            "volume_ratio": round(vol/avg_vol, 2) if avg_vol else None,
            "rsi_proxy": rsi_proxy,
            "rsi_signal": rsi_sig,
            "momentum_1M": c.get("1M") if c else None,
            "momentum_3M": c.get("3M") if c else None,
            "year_low":  q.get("yearLow"),
            "year_high": q.get("yearHigh"),
            "market_cap": q.get("marketCap"),
        })
    return no_cache({"timestamp": datetime.utcnow().isoformat(),
                     "count": len(tickers), "data": output})

@app.get("/vet")
async def vet(symbol: str = Query(...), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        insider_r, score_r, grades_r, pt_r, news_r, quote_r = await asyncio.gather(
            fmp(client, "insider-trading/statistics", {"symbol": sym}),
            fmp(client, "financial-scores",           {"symbol": sym}),
            fmp(client, "grades",                     {"symbol": sym, "limit": 20}),
            fmp(client, "price-target-summary",       {"symbol": sym}),
            fmp(client, "news/stock",                 {"symbol": sym, "limit": 20}),
            fmp(client, "quote",                      {"symbol": sym}),
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
    analyst_count, downgrades = None, 0
    if isinstance(grades_r, list) and grades_r:
        analyst_count = len(set(g.get("gradingCompany","") for g in grades_r))
        downgrades    = sum(1 for g in grades_r[:5] if g.get("action","").lower() == "downgrade")
    pt = first(pt_r)
    q  = first(quote_r)
    current_price = q.get("price", 0) or 0
    pt_upside = None
    if pt and pt.get("lastMonthAvgPriceTarget") and current_price:
        pt_upside = round(((pt["lastMonthAvgPriceTarget"] - current_price)/current_price)*100, 1)
    news_result = scan_news(news_r if isinstance(news_r, list) else [])
    gate1 = not insider.get("kill_flag", False)
    gate2 = not scores.get("kill_flag", False)
    gate3 = analyst_count is None or (analyst_count <= 14 and downgrades == 0)
    gate4 = pt_upside is None or pt_upside > 0
    gate5 = news_result["pass"]
    passed = sum([gate1, gate2, gate3, gate4, gate5])
    return no_cache({
        "symbol": sym, "timestamp": datetime.utcnow().isoformat(), "price": current_price,
        "phase0_gate": {
            "overall": "PASS" if passed >= 4 else f"FAIL ({5-passed} gates failed)",
            "gates_passed": passed,
            "check1_insider":      {"pass": gate1, "detail": insider},
            "check2_balance_sheet":{"pass": gate2, "detail": scores},
            "check3_analyst":      {"pass": gate3, "analyst_count": analyst_count, "downgrades": downgrades},
            "check4_price_target": {"pass": gate4, "implied_upside_pct": pt_upside,
                                    "avg_pt": pt.get("lastMonthAvgPriceTarget") if pt else None},
            "check5_news":         {"pass": gate5, "detail": news_result}
        }
    })

@app.get("/financials")
async def financials(symbol: str = Query(...), period: str = Query(default="annual"),
                     limit: int = Query(default=4), _key=Depends(verify_key)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        income_r, balance_r, cashflow_r, scores_r, earnings_r, metrics_r = await asyncio.gather(
            fmp(client, "income-statement",       {"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "balance-sheet-statement",{"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "cash-flow-statement",    {"symbol": sym, "period": period, "limit": limit}),
            fmp(client, "financial-scores",       {"symbol": sym}),
            fmp(client, "earnings",               {"symbol": sym, "limit": 8}),
            fmp(client, "key-metrics",            {"symbol": sym, "period": "annual", "limit": limit}),
        )
    eps_history = []
    if isinstance(earnings_r, list):
        for e in earnings_r[:4]:
            actual, est = e.get("epsActual"), e.get("epsEstimated")
            beat = actual >= est if actual is not None and est is not None else None
            pct  = round(((actual-est)/abs(est))*100,1) if beat is not None and est != 0 else None
            eps_history.append({"date": str(e.get("date",""))[:10], "estimated": est,
                                 "actual": actual, "beat": beat, "surprise_pct": pct})
    sc = first(scores_r)
    score_summary = {}
    if sc and isinstance(sc, dict) and "altmanZScore" in sc:
        z, f = sc.get("altmanZScore"), sc.get("piotroskiScore")
        score_summary = {"altman_z": z, "piotroski_f": f,
                         "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE",
                         "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)}
    return no_cache({
        "symbol": sym, "period": period, "timestamp": datetime.utcnow().isoformat(),
        "income_statement": income_r if isinstance(income_r, list) else [],
        "balance_sheet":    balance_r if isinstance(balance_r, list) else [],
        "cash_flow":        cashflow_r if isinstance(cashflow_r, list) else [],
        "key_metrics":      metrics_r if isinstance(metrics_r, list) else [],
        "financial_scores": score_summary,
        "eps_history": eps_history,
        "beat_rate": f"{sum(1 for e in eps_history if e.get('beat'))}/{len(eps_history)}"
    })


# ── NEW DISCOVERY ROUTES ──────────────────────────────────────────────────────

@app.get("/discovery/screener-test")
async def discovery_screener_test(_key=Depends(verify_key)):
    """
    Diagnostic: Tests which FMP stable screener endpoint path is active.
    Returns first working path and a 3-name sample. Run this if /discovery/universe returns 404.
    """
    test_params = {
        "marketCapMoreThan": 500000000,
        "marketCapLowerThan": 1000000000,
        "isEtf": "false",
        "isActivelyTrading": "true",
        "country": "US",
    }
    results = {}
    async with httpx.AsyncClient() as client:
        for path in ["company-screener", "stock-screener", "screener"]:
            r = await fmp(client, path, test_params)
            if isinstance(r, list) and len(r) > 0:
                results[path] = {"status": "WORKING", "sample_count": len(r),
                                 "sample": [{k: v for k, v in s.items()
                                             if k in ["symbol","companyName","marketCap","price"]}
                                            for s in r[:3]]}
            elif isinstance(r, dict) and "error" not in r:
                results[path] = {"status": "WORKING_DICT", "keys": list(r.keys())[:5]}
            else:
                err = r.get("error", "empty") if isinstance(r, dict) else str(r)[:80]
                results[path] = {"status": f"FAILED: {err}"}
    working = [p for p, v in results.items() if "WORKING" in v.get("status","")]
    return no_cache({
        "timestamp": datetime.utcnow().isoformat(),
        "working_path": working[0] if working else None,
        "recommendation": f"Use: {working[0]}" if working else "No screener path working",
        "all_paths": results
    })


@app.get("/discovery/universe")
async def discovery_universe(
    marketCapMin: int = Query(default=50000000),
    marketCapMax: int = Query(default=2000000000),
    profitableOnly: bool = Query(default=True),
    sector: str = Query(default=None),
    exchange: str = Query(default=None),
    betaMax: float = Query(default=None),
    betaMin: float = Query(default=None),
    limit: int = Query(default=1000),
    _key=Depends(verify_key)
):
    """
    Universe Gate: Returns micro/small cap US stocks ($50M–$2B) filtered by profitability.
    This is the foundational pool for all discovery engines.
    """
    async with httpx.AsyncClient() as client:
        params = {
            "marketCapMoreThan": marketCapMin,
            "marketCapLowerThan": marketCapMax,
            "isEtf": "false",
            "isActivelyTrading": "true",
            "country": "US",
        }
        if profitableOnly:
            params["netIncomeMoreThan"] = 0
        if sector:
            params["sector"] = sector
        if exchange:
            params["exchange"] = exchange
        if limit:
            params["limit"] = limit
        # Confirmed working path: company-screener (validated 2026-06-16)
        r = await fmp(client, "company-screener", params)

    if isinstance(r, dict) and "error" in r:
        return no_cache({"error": r["error"], "timestamp": datetime.utcnow().isoformat()})

    results = r if isinstance(r, list) else []
    # Sort by market cap ascending (smallest first — better discovery targets)
    results.sort(key=lambda x: x.get("marketCap") or 0)

    simplified = []
    for s in results:
        beta = s.get("beta")
        # Post-filter by beta range if specified
        if betaMin is not None and (beta is None or beta < betaMin):
            continue
        if betaMax is not None and (beta is None or beta > betaMax):
            continue
        simplified.append({
            "symbol":    s.get("symbol"),
            "name":      s.get("companyName"),
            "sector":    s.get("sector"),
            "industry":  s.get("industry"),
            "marketCap": s.get("marketCap"),
            "price":     s.get("price"),
            "beta":      beta,
            "exchange":  s.get("exchangeShortName"),
        })

    return no_cache({
        "timestamp":      datetime.utcnow().isoformat(),
        "total_in_pool":  len(simplified),
        "filters_applied": {
            "marketCap":     f"${marketCapMin/1e6:.0f}M–${marketCapMax/1e6:.0f}M",
            "profitableOnly": profitableOnly,
            "sector":        sector or "ALL",
            "exchange":      exchange or "ALL",
            "betaRange":     f"{betaMin or 'any'}–{betaMax or 'any'}",
            "country":       "US",
            "etf":           False
        },
        "universe": simplified
    })


@app.get("/discovery/fundamentals")
async def discovery_fundamentals(symbol: str = Query(...), _key=Depends(verify_key)):
    """
    Fundamental Inflection Engine: Checks for revenue acceleration, margin expansion,
    and FCF inflection across last 4 quarters. Used to identify Tier 2 diamonds.
    """
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        income_r, cashflow_r, growth_r = await asyncio.gather(
            fmp(client, "income-statement",    {"symbol": sym, "period": "quarter", "limit": 6}),
            fmp(client, "cash-flow-statement", {"symbol": sym, "period": "quarter", "limit": 6}),
            fmp(client, "financial-growth",    {"symbol": sym, "period": "quarter", "limit": 4}),
            return_exceptions=True
        )

    # Revenue acceleration: QoQ growth rate increasing
    revenue_accel = False
    margin_expansion = False
    fcf_positive = False
    fcf_first_positive = False
    revenue_pcts = []
    gross_margins = []

    if isinstance(income_r, list) and len(income_r) >= 3:
        quarters = income_r[:5]
        for i in range(len(quarters) - 1):
            curr_rev = quarters[i].get("revenue") or 0
            prev_rev = quarters[i+1].get("revenue") or 1
            if prev_rev != 0:
                pct = ((curr_rev - prev_rev) / abs(prev_rev)) * 100
                revenue_pcts.append(round(pct, 1))
            gm = quarters[i].get("grossProfitRatio") or 0
            gross_margins.append(round(gm * 100, 2))

        # Revenue acceleration: latest QoQ > prior QoQ by 5%+
        if len(revenue_pcts) >= 2:
            revenue_accel = revenue_pcts[0] > revenue_pcts[1] + 5

        # Margin expansion: gross margin higher in each of last 2 quarters
        if len(gross_margins) >= 3:
            margin_expansion = (
                gross_margins[0] > gross_margins[1] + 0.5 and
                gross_margins[1] > gross_margins[2] + 0.5
            )

    # FCF analysis
    prev_fcf_values = []
    if isinstance(cashflow_r, list) and cashflow_r:
        for i, q in enumerate(cashflow_r[:6]):
            fcf = q.get("freeCashFlow") or 0
            if i == 0:
                fcf_positive = fcf > 0
            else:
                prev_fcf_values.append(fcf)
        # First time positive: current positive, all prior negative
        if fcf_positive and prev_fcf_values:
            fcf_first_positive = all(v <= 0 for v in prev_fcf_values[:3])

    # Growth data from FMP financial-growth endpoint
    growth_data = []
    if isinstance(growth_r, list):
        for g in growth_r[:4]:
            growth_data.append({
                "date":              str(g.get("date",""))[:10],
                "revenue_growth":    round((g.get("revenueGrowth") or 0) * 100, 2),
                "gross_profit_growth": round((g.get("grossProfitGrowth") or 0) * 100, 2),
                "ebitda_growth":     round((g.get("ebitdaGrowth") or 0) * 100, 2),
                "eps_growth":        round((g.get("epsgrowth") or 0) * 100, 2),
            })

    # Inflection score (0–5)
    inflection_score = sum([
        revenue_accel,
        margin_expansion,
        fcf_positive,
        fcf_first_positive,
        len(revenue_pcts) > 0 and revenue_pcts[0] >= 15  # ≥15% QoQ
    ])

    return no_cache({
        "symbol":    sym,
        "timestamp": datetime.utcnow().isoformat(),
        "inflection_signals": {
            "revenue_accelerating":  revenue_accel,
            "margin_expanding_2q":   margin_expansion,
            "fcf_positive":          fcf_positive,
            "fcf_first_positive":    fcf_first_positive,
            "revenue_qoq_ge15pct":   len(revenue_pcts) > 0 and revenue_pcts[0] >= 15,
        },
        "inflection_score": f"{inflection_score}/5",
        "flag_tier2": inflection_score >= 3,
        "raw": {
            "revenue_qoq_pcts":  revenue_pcts,
            "gross_margins_pct": gross_margins,
            "growth_data":       growth_data,
        }
    })


@app.get("/discovery/insider-cluster")
async def discovery_insider_cluster(
    symbol: str = Query(...),
    days: int = Query(default=14),
    min_total_usd: int = Query(default=50000),
    _key=Depends(verify_key)
):
    """
    Cluster Insider Buy Detector: Flags when 3+ distinct insiders buy within a
    rolling window (default 14 days). Cluster buying is a high-conviction signal.
    Old logic: single buyer, 48hr. New logic: 3+ distinct buyers, 14-day window.
    """
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        r = await fmp(client, "insider-trading", {"symbol": sym, "limit": 50})

    if not isinstance(r, list):
        return no_cache({"symbol": sym, "error": "No insider data", "cluster_detected": False,
                         "timestamp": datetime.utcnow().isoformat()})

    from datetime import datetime as dt, timedelta
    cutoff = dt.utcnow() - timedelta(days=days)

    purchases = []
    for trade in r:
        ttype = (trade.get("transactionType") or "").upper()
        # Only open-market purchases (P = purchase, not 10b5-1 plan)
        if "PURCHASE" not in ttype and ttype != "P":
            continue
        trade_date_str = str(trade.get("transactionDate") or trade.get("filingDate") or "")[:10]
        try:
            trade_date = dt.strptime(trade_date_str, "%Y-%m-%d")
        except Exception:
            continue
        if trade_date < cutoff:
            continue
        shares = trade.get("securitiesTransacted") or 0
        price  = trade.get("price") or 0
        value  = shares * price
        if value < 1000:  # skip tiny/zero-value entries
            continue
        purchases.append({
            "name":      trade.get("reportingName") or trade.get("reporterName") or "Unknown",
            "title":     trade.get("typeOfOwner") or "",
            "date":      trade_date_str,
            "shares":    shares,
            "price":     price,
            "value_usd": round(value, 0),
        })

    distinct_buyers = list({p["name"] for p in purchases})
    total_usd = sum(p["value_usd"] for p in purchases)
    cluster_detected = len(distinct_buyers) >= 3 and total_usd >= min_total_usd

    return no_cache({
        "symbol":           sym,
        "timestamp":        datetime.utcnow().isoformat(),
        "window_days":      days,
        "cluster_detected": cluster_detected,
        "distinct_buyers":  len(distinct_buyers),
        "buyer_names":      distinct_buyers,
        "total_value_usd":  total_usd,
        "min_threshold_usd": min_total_usd,
        "purchases":        sorted(purchases, key=lambda x: x["date"], reverse=True),
        "signal": "🔴 CLUSTER BUY — HIGH CONVICTION" if cluster_detected else
                  "🟡 SINGLE/DUAL BUYER" if len(distinct_buyers) in [1,2] and total_usd >= min_total_usd else
                  "⬜ NO SIGNIFICANT INSIDER BUYING"
    })


@app.get("/discovery/institutional")
async def discovery_institutional(symbol: str = Query(...), _key=Depends(verify_key)):
    """
    Institutional Footprint: Detects smart money accumulation in micro/small caps.
    Flags when institutional ownership increased 10%+ in most recent filing cycle.
    """
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        r = await fmp(client, "institutional-ownership/institutional-holders", {"symbol": sym})

    if not isinstance(r, list) or len(r) < 2:
        return no_cache({
            "symbol": sym, "timestamp": datetime.utcnow().isoformat(),
            "institutional_acceleration": False,
            "note": "Insufficient filing data (need 2+ periods)"
        })

    # Most recent vs prior period
    recent = r[0]
    prior  = r[1]

    recent_pct = recent.get("ownershipPercent") or recent.get("institutionalOwnershipPercentage") or 0
    prior_pct  = prior.get("ownershipPercent")  or prior.get("institutionalOwnershipPercentage")  or 0
    change_pct = round(recent_pct - prior_pct, 2)

    recent_holders = recent.get("numberOfInstitutionalHolders") or recent.get("investorsHolding") or 0
    prior_holders  = prior.get("numberOfInstitutionalHolders")  or prior.get("investorsHolding")  or 0
    holder_change  = recent_holders - prior_holders

    acceleration = change_pct >= 5.0  # 5%+ ownership increase = whale footprint

    return no_cache({
        "symbol":    sym,
        "timestamp": datetime.utcnow().isoformat(),
        "institutional_acceleration": acceleration,
        "ownership_pct_recent": recent_pct,
        "ownership_pct_prior":  prior_pct,
        "ownership_change_pct": change_pct,
        "holders_recent":       recent_holders,
        "holders_prior":        prior_holders,
        "holder_change":        holder_change,
        "filing_period_recent": str(recent.get("date",""))[:10],
        "filing_period_prior":  str(prior.get("date",""))[:10],
        "signal": "🐋 WHALE FOOTPRINT — institutional accumulation detected" if acceleration else
                  "📊 STABLE" if change_pct >= 0 else "📉 INSTITUTIONAL DISTRIBUTION"
    })


@app.get("/discovery/coiled-spring")
async def discovery_coiled_spring(symbol: str = Query(...), _key=Depends(verify_key)):
    """
    Coiled Spring Technical Check: Uses FMP price-change data to approximate
    consolidation tightness and momentum posture for Tier 1 Roth candidates.
    Complements Twelve Data time_series calls on survivors.
    Note: For precise BB width and ADX, supplement with Twelve Data /time_series.
    """
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        quote_r, change_r = await asyncio.gather(
            fmp(client, "quote", {"symbol": sym}),
            fmp(client, "stock-price-change", {"symbol": sym}),
            return_exceptions=True
        )

    q = first(quote_r)
    c = first(change_r) if not isinstance(change_r, Exception) else {}

    price     = q.get("price") or 0
    year_low  = q.get("yearLow")  or 0
    year_high = q.get("yearHigh") or 1
    day_low   = q.get("dayLow")   or price
    day_high  = q.get("dayHigh")  or price
    avg_vol   = q.get("avgVolume") or 1
    vol       = q.get("volume")    or 0

    # Proxy for consolidation: distance from 52wk high
    pct_from_high = round(((year_high - price) / year_high) * 100, 1) if year_high else None

    # Momentum check — coiled spring has flat/low recent momentum but not falling
    m1  = c.get("1M")  or 0
    m3  = c.get("3M")  or 0
    m5d = c.get("5D")  or 0

    # RSI proxy
    rsi_proxy, rsi_dir, rsi_sig = momentum_to_rsi_proxy(c)

    # Spring criteria
    flat_recent     = abs(m1) < 8           # <8% move in 1M = consolidating
    rsi_zone        = 45 <= (rsi_proxy or 0) <= 65  # not overbought, not dead
    near_high       = pct_from_high is not None and pct_from_high < 15  # within 15% of 52wk high
    vol_compression = vol < avg_vol * 0.85   # volume drying up = accumulation
    positive_base   = m3 > 0                 # still positive over 3M = base building

    spring_score = sum([flat_recent, rsi_zone, near_high, vol_compression, positive_base])

    return no_cache({
        "symbol":    sym,
        "timestamp": datetime.utcnow().isoformat(),
        "price":     price,
        "spring_signals": {
            "flat_recent_1M":       flat_recent,
            "rsi_in_zone_45_65":    rsi_zone,
            "near_52wk_high":       near_high,
            "volume_compressing":   vol_compression,
            "positive_3M_base":     positive_base,
        },
        "spring_score": f"{spring_score}/5",
        "flag_tier1":   spring_score >= 3,
        "raw": {
            "pct_from_52wk_high": pct_from_high,
            "momentum_5D":  m5d,
            "momentum_1M":  m1,
            "momentum_3M":  m3,
            "rsi_proxy":    rsi_proxy,
            "rsi_signal":   rsi_sig,
            "volume_ratio": round(vol / avg_vol, 2) if avg_vol else None,
        },
        "twelve_data_next": f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1day&outputsize=20&apikey=7873bf2e1b58407fbf87e642db913484"
    })




@app.get("/discovery/debug-universe")
async def discovery_debug_universe(
    marketCapMin: int = Query(default=50000000),
    marketCapMax: int = Query(default=2000000000),
    maxMomentum3M: float = Query(default=40.0),
    minIpoMonths: int = Query(default=12),
    _key=Depends(verify_key)
):
    """
    Debug endpoint: shows exactly what survives each wall layer and
    the cap distribution at each stage. Diagnoses sampling bias.
    """
    # Multi-bucket pull (same logic as /discovery/scan)
    CAP_BUCKETS_DBG = [
        (50_000_000,   150_000_000),
        (150_000_000,  400_000_000),
        (400_000_000,  900_000_000),
        (900_000_000,  2_000_000_000),
    ]
    active_dbg = [
        (max(lo, marketCapMin), min(hi, marketCapMax))
        for lo, hi in CAP_BUCKETS_DBG
        if lo < marketCapMax and hi > marketCapMin
    ]
    async with httpx.AsyncClient(timeout=30) as client:
        dbg_buckets = await asyncio.gather(*[
            fmp(client, "company-screener", {
                "marketCapMoreThan": lo, "marketCapLowerThan": hi,
                "isEtf": "false", "isActivelyTrading": "true",
                "country": "US", "netIncomeMoreThan": 0, "limit": 250,
            }) for lo, hi in active_dbg
        ])
    seen_d = set()
    universe_raw = []
    for bucket in dbg_buckets:
        for s in (bucket if isinstance(bucket, list) else []):
            sym = s.get("symbol")
            if sym and sym not in seen_d:
                seen_d.add(sym)
                universe_raw.append(s)

    if not universe_raw:
        return no_cache({"error": "Screener failed", "timestamp": datetime.utcnow().isoformat()})

    def cap_band(s):
        mc = (s.get("marketCap") or 0) / 1e6
        if mc < 100:   return "A_under100M"
        if mc < 300:   return "B_100-300M"
        if mc < 500:   return "C_300-500M"
        if mc < 750:   return "D_500-750M"
        if mc < 1000:  return "E_750M-1B"
        if mc < 1500:  return "F_1B-1.5B"
        return             "G_1.5B-2B"

    def dist(lst):
        from collections import Counter
        c = Counter(cap_band(s) for s in lst)
        return dict(sorted(c.items()))

    # Stage 0: raw screener
    raw_dist = dist(universe_raw)

    # Stage 1: CEF/BDC kill
    EXCLUDE_INDUSTRIES = {
        "closed-end fund", "asset management", "exchange traded fund",
        "diversified financials", "mortgage real estate investment trust",
        "real estate investment trust", "business development company",
        "investment trusts/mutual funds", "credit services", "capital markets",
    }
    wall1 = []
    for s in universe_raw:
        industry = (s.get("industry") or "").lower()
        name     = (s.get("companyName") or s.get("name") or "").lower()
        if any(excl in industry for excl in EXCLUDE_INDUSTRIES):
            continue
        if any(kw in name for kw in ["closed-end", "closed end", "interval fund",
                                      "nuveen", "calamos", "pimco dynamic",
                                      "blackrock tcp", "ares capital"]):
            continue
        wall1.append(s)
    wall1_dist = dist(wall1)

    # Stage 2: IPO age kill
    wall2 = []
    for s in wall1:
        ipo_date = s.get("ipoDate") or ""
        if ipo_date:
            try:
                from datetime import datetime as dt2
                ipo_dt = dt2.strptime(ipo_date[:10], "%Y-%m-%d")
                months_public = (datetime.utcnow() - ipo_dt).days / 30
                if months_public < minIpoMonths:
                    continue
            except Exception:
                pass
        wall2.append(s)
    wall2_dist = dist(wall2)

    # Stage 3: Momentum + proximity kill
    # Check how many have null momentum fields (the core diagnostic)
    null_m3  = sum(1 for s in wall2 if not s.get("threeMonthReturn") and not s.get("priceChange3Month"))
    null_m1  = sum(1 for s in wall2 if not s.get("oneMonthReturn") and not s.get("priceChange1Month"))
    null_yh  = sum(1 for s in wall2 if not s.get("yearHigh") and not s.get("highestPrice"))

    wall3_ran = wall3_spike = wall3_pass = 0
    wall3 = []
    for s in wall2:
        m3 = s.get("threeMonthReturn") or s.get("priceChange3Month") or None
        m1 = s.get("oneMonthReturn")   or s.get("priceChange1Month") or None
        price = s.get("price") or 0
        yh    = s.get("yearHigh") or s.get("highestPrice") or 0

        if m3 is not None and m3 > maxMomentum3M:
            wall3_ran += 1
            continue
        if price > 0 and yh > 0:
            proximity = price / yh
            if proximity >= 0.90 and m1 is not None and m1 >= 15:
                wall3_spike += 1
                continue
        wall3_pass += 1
        wall3.append(s)
    wall3_dist = dist(wall3)

    # Quartile sampling simulation
    wall3_sorted = sorted(wall3, key=lambda x: x.get("marketCap") or 0)
    total = len(wall3_sorted)
    maxNames = 200
    if total <= maxNames:
        sampled = wall3_sorted
    else:
        q = total // 4
        q1 = wall3_sorted[:q]
        q2 = wall3_sorted[q:q*2]
        q3 = wall3_sorted[q*2:q*3]
        q4 = wall3_sorted[q*3:]
        per_q = maxNames // 4
        import random
        random.seed(42)
        sampled = (
            q1[:per_q] +
            random.sample(q2, min(per_q, len(q2))) +
            random.sample(q3, min(per_q, len(q3))) +
            random.sample(q4, min(per_q, len(q4)))
        )
    sampled_dist = dist(sampled)

    return no_cache({
        "timestamp": datetime.utcnow().isoformat(),
        "diagnosis": {
            "momentum_fields_null": {
                "3M_null": null_m3,
                "1M_null": null_m1,
                "yearHigh_null": null_yh,
                "total_post_wall2": len(wall2),
                "pct_with_no_3M_data": f"{null_m3/len(wall2)*100:.1f}%" if wall2 else "n/a",
                "conclusion": "If 3M_null is high, Wall3A is NOT firing — momentum kill is blind" if null_m3 > len(wall2)*0.5 else "Momentum data present — Wall3A is active"
            },
            "wall3_kills": {
                "already_ran_3M": wall3_ran,
                "vertical_spike": wall3_spike,
                "passed": wall3_pass,
            }
        },
        "cap_distribution_by_stage": {
            "0_raw_screener":    {"count": len(universe_raw), "bands": raw_dist},
            "1_after_cef_kill":  {"count": len(wall1),        "bands": wall1_dist},
            "2_after_ipo_kill":  {"count": len(wall2),        "bands": wall2_dist},
            "3_after_momentum":  {"count": len(wall3),        "bands": wall3_dist},
            "4_sampled_200":     {"count": len(sampled),      "bands": sampled_dist},
        },
        "sample_fields_present": {
            "fields_in_first_record": list((universe_raw[0] if universe_raw else {}).keys()),
        }
    })


@app.get("/watchlist")
async def watchlist(_key=Depends(verify_key)):
    wl = await fetch_watchlist_data()
    if not wl or "tickers" not in wl:
        return no_cache({"error": "Watchlist unavailable", "timestamp": datetime.utcnow().isoformat()})
    tickers_data = wl.get("tickers", {})
    symbols = list(tickers_data.keys())
    async with httpx.AsyncClient() as client:
        quotes = await asyncio.gather(*[fmp(client, "quote", {"symbol": s}) for s in symbols])
    output = []
    for sym, q_r in zip(symbols, quotes):
        q     = first(q_r)
        price = q.get("price", 0) or 0
        entry = tickers_data.get(sym, {})
        z1    = entry.get("z1", [None, None])
        z2    = entry.get("z2")
        stop  = entry.get("stop")
        t1    = entry.get("t1")
        t2    = entry.get("t2")
        in_z1 = z1 and len(z1)==2 and z1[0] <= price <= z1[1]
        in_z2 = z2 and isinstance(z2, list) and len(z2)==2 and z2[0] <= price <= z2[1]
        below_stop = stop and price < stop
        zone = "Z1 ✅" if in_z1 else "Z2 ✅" if in_z2 else "BELOW STOP ⚠️" if below_stop else "WATCHING"
        output.append({
            "symbol": sym, "price": price,
            "change_pct": q.get("changePercentage"),
            "zone": zone, "z1_range": z1, "z2_trigger": z2,
            "stop": stop, "t1": t1, "t2": t2,
            "upside_t1_pct": round(((t1-price)/price)*100,1) if t1 and price else None,
            "upside_t2_pct": round(((t2-price)/price)*100,1) if t2 and price else None,
            "tier": entry.get("tier"), "notes": entry.get("notes",""),
        })
    return no_cache({"timestamp": datetime.utcnow().isoformat(),
                     "updated": wl.get("updated"), "count": len(output), "watchlist": output})


# ── DISCOVERY SCAN — FULL PIPELINE ENDPOINT ───────────────────────────────────

@app.get("/discovery/scan")
async def discovery_scan(
    marketCapMin: int = Query(default=50000000),
    marketCapMax: int = Query(default=2000000000),
    sector: str = Query(default=None),
    minInflection: int = Query(default=2),   # min inflection score to survive cut
    minSpring: int = Query(default=2),        # min spring score to appear in output
    maxNames: int = Query(default=200),       # cap universe before detailed scan
    maxMomentum3M: float = Query(default=40.0),  # kill if already ran (3M% > this)
    maxRsi: float = Query(default=65.0),         # kill if overbought (RSI proxy > this)
    minIpoMonths: int = Query(default=12),        # kill if IPO < N months ago
    _key=Depends(verify_key)
):
    """
    Full Discovery Pipeline — one call, ranked output.
    Stage 1: Pull universe (profitable US $50M–$2B)
    Stage 2: Run fundamentals + insider-cluster in parallel batches
    Stage 3: Run coiled-spring on survivors
    Stage 4: Score, rank, return flagged names only
    """
    start_ts = datetime.utcnow()

    # ── STAGE 1: UNIVERSE — multi-bucket pull to fix FMP cap bias ────────────
    # FMP company-screener ignores marketCapLowerThan below ~$750M and returns
    # mostly $1B-$2B names. Fix: pull 4 explicit cap buckets and merge.
    # Each bucket gets limit=250 → up to 1000 total before dedup.
    CAP_BUCKETS = [
        (50_000_000,   150_000_000),   # micro: $50M–$150M
        (150_000_000,  400_000_000),   # small-low: $150M–$400M
        (400_000_000,  900_000_000),   # small-high: $400M–$900M
        (900_000_000,  2_000_000_000), # mid: $900M–$2B
    ]
    # If caller specified a tighter range, filter buckets to overlap
    active_buckets = [
        (lo, hi) for lo, hi in CAP_BUCKETS
        if lo < marketCapMax and hi > marketCapMin
    ]
    # Clamp bucket edges to caller's range
    active_buckets = [
        (max(lo, marketCapMin), min(hi, marketCapMax))
        for lo, hi in active_buckets
    ]

    async def fetch_bucket(lo, hi, client):
        params = {
            "marketCapMoreThan": lo,
            "marketCapLowerThan": hi,
            "isEtf": "false",
            "isActivelyTrading": "true",
            "country": "US",
            "netIncomeMoreThan": 0,
            "limit": 250,
        }
        if sector:
            params["sector"] = sector
        result = await fmp(client, "company-screener", params)
        if isinstance(result, list):
            return result
        # Fallback: try stock-screener path
        result2 = await fmp(client, "stock-screener", params)
        return result2 if isinstance(result2, list) else []

    async with httpx.AsyncClient(timeout=30) as client:
        bucket_results = await asyncio.gather(
            *[fetch_bucket(lo, hi, client) for lo, hi in active_buckets]
        )

    # Merge + deduplicate by symbol
    seen_syms = set()
    universe_raw = []
    for bucket in bucket_results:
        for s in (bucket if isinstance(bucket, list) else []):
            sym = s.get("symbol")
            if sym and sym not in seen_syms:
                seen_syms.add(sym)
                universe_raw.append(s)

    if not universe_raw:
        return no_cache({"error": "Universe pull failed — all buckets empty", "timestamp": start_ts.isoformat()})

    # ── STAGE 1B: ENRICH WITH MOMENTUM DATA (batch price-change calls) ───────
    # company-screener returns no momentum fields — fetch them now before walls
    # Batch in groups of 20 using /quote which returns volume + price vs MAs
    MOMENTUM_BATCH = 20
    momentum_map = {}

    async def fetch_momentum_batch(syms, client):
        # Use /quote for price vs 50/200 MA + volume ratio (fast, cheap)
        symbols_str = ",".join(syms)
        r = await fmp(client, "quote", {"symbol": symbols_str})
        if isinstance(r, list):
            return {q["symbol"]: q for q in r if q.get("symbol")}
        return {}

    async with httpx.AsyncClient(timeout=25) as client:
        all_syms = [s["symbol"] for s in universe_raw if s.get("symbol")]
        batch_tasks = [
            fetch_momentum_batch(all_syms[i:i+MOMENTUM_BATCH], client)
            for i in range(0, len(all_syms), MOMENTUM_BATCH)
        ]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

    for br in batch_results:
        if isinstance(br, dict):
            momentum_map.update(br)

    # Attach momentum fields to each universe entry
    for s in universe_raw:
        sym = s.get("symbol", "")
        q   = momentum_map.get(sym, {})
        if q:
            # Compute approximate 1M/3M momentum from price vs moving averages
            price   = q.get("price") or 0
            ma50    = q.get("priceAvg50") or 0
            ma200   = q.get("priceAvg200") or 0
            yh      = q.get("yearHigh") or 0
            yl      = q.get("yearLow")  or 0
            avg_vol = q.get("avgVolume") or 1
            vol     = q.get("volume") or 0

            # Approximate 3M momentum: price vs 50d MA (50d ≈ 2.5 months)
            m3_proxy = round(((price - ma50) / ma50) * 100, 1) if ma50 > 0 else None
            # Approximate 1M momentum: price vs (midpoint of 50d and current)
            # Better: use stock-price-change endpoint but that's per-ticker
            # For now use the change% from quote as a 1D proxy, flag for upgrade
            m1_proxy = round(((price - ma50) / ma50) * 50, 1) if ma50 > 0 else None

            # yearHigh from quote is more reliable than screener
            s["yearHigh"]        = yh or s.get("yearHigh")
            s["yearLow"]         = yl or s.get("yearLow")
            s["threeMonthReturn"] = m3_proxy
            s["oneMonthReturn"]   = m1_proxy
            s["vol_ratio_live"]   = round(vol / avg_vol, 2) if avg_vol > 0 else None
            s["price_live"]       = price or s.get("price")

    # ══════════════════════════════════════════════════════════════════════
    # STRUCTURAL WALL — applied to screener data in memory, zero extra calls
    # ══════════════════════════════════════════════════════════════════════

    # ── WALL 1: CEF / BDC / REIT / ETF industry kill ─────────────────────
    EXCLUDE_INDUSTRIES = {
        "closed-end fund", "asset management", "exchange traded fund",
        "diversified financials", "mortgage real estate investment trust",
        "real estate investment trust", "business development company",
        "investment trusts/mutual funds", "credit services", "capital markets",
        # Additional REIT structures
        "reit", "real estate investment trust (reit)",
        "residential real estate investment trust",
        "commercial real estate investment trust",
        "diversified real estate investment trust",
        "office real estate investment trust",
        "retail real estate investment trust",
        "industrial real estate investment trust",
        "specialty real estate investment trust",
        "mortgage investment trust",
    }
    EXCLUDE_SECTORS = {
        # Kill entire real estate sector — too many income artifacts
        "real estate",
    }
    EXCLUDE_NAME_KEYWORDS = [
        "closed-end", "closed end", "interval fund",
        "nuveen", "calamos", "pimco dynamic", "blackrock tcp", "ares capital",
        # REIT name patterns
        "realty trust", "realty corp", "reit", "mortgage trust",
        "property trust", "property income", "income reit",
    ]
    wall1_passed = []
    for s in universe_raw:
        industry = (s.get("industry") or "").lower()
        sector   = (s.get("sector")   or "").lower()
        name     = (s.get("companyName") or s.get("name") or "").lower()
        if any(excl in industry for excl in EXCLUDE_INDUSTRIES):
            continue
        if sector in EXCLUDE_SECTORS:
            continue
        if any(kw in name for kw in EXCLUDE_NAME_KEYWORDS):
            continue
        wall1_passed.append(s)

    # ── WALL 2: IPO age kill — < 12 months public ────────────────────────
    wall2_passed = []
    for s in wall1_passed:
        ipo_date = s.get("ipoDate") or ""
        if ipo_date:
            try:
                from datetime import datetime as dt2
                ipo_dt = dt2.strptime(ipo_date[:10], "%Y-%m-%d")
                months_public = (datetime.utcnow() - ipo_dt).days / 30
                if months_public < minIpoMonths:
                    continue
            except Exception:
                pass
        wall2_passed.append(s)

    # ── WALL 3: PROXIMITY + MOMENTUM PRE-FILTER (zero extra API calls) ───
    # Uses price + yearHigh already in screener payload
    # Proximity ratio = price / 52wk_high
    # Rule A: proximity < 0.90 (more than 10% below high) → PASS directly
    # Rule B: proximity >= 0.90 (within 10% of high) → conditional fork:
    #   - 1M momentum < 5%  → PASS (flat consolidation at high = coiled spring)
    #   - 1M momentum >= 15% → KILL (vertical spike to high = chasing)
    #   - 5% <= 1M < 15%    → PASS (borderline — let fundamentals decide)
    # Rule C: 3M momentum > maxMomentum3M → KILL (already ran regardless of proximity)
    wall3_passed = []
    wall_kills   = {"cef_bdc": len(universe_raw) - len(wall1_passed),
                    "ipo_age": len(wall1_passed) - len(wall2_passed),
                    "already_ran_3M": 0,
                    "vertical_spike_to_high": 0,
                    "passed": 0}

    for s in wall2_passed:
        price    = s.get("price") or 0
        yh       = s.get("yearHigh") or s.get("highestPrice") or 0
        # 3M momentum from screener (field varies by FMP version)
        m3       = s.get("threeMonthReturn") or s.get("priceChange3Month") or 0
        m1       = s.get("oneMonthReturn")   or s.get("priceChange1Month") or 0

        # Rule C: 3M already ran
        if m3 and m3 > maxMomentum3M:
            wall_kills["already_ran_3M"] += 1
            continue

        # Rule A/B: Proximity to 52wk high
        if price > 0 and yh > 0:
            proximity = price / yh
            if proximity >= 0.90:
                # Within 10% of high — apply consolidation exception
                if m1 and m1 >= 15:
                    # Vertical spike to high — kill
                    wall_kills["vertical_spike_to_high"] += 1
                    continue
                # else: flat base at high or no 1M data — pass (spring candidate)

        wall_kills["passed"] += 1
        wall3_passed.append(s)

    filtered_raw = wall3_passed  # filtered_raw used in pipeline_summary

    # ── QUARTILE-BALANCED SAMPLING across full cap range ──────────────────
    filtered_raw.sort(key=lambda x: x.get("marketCap") or 0)
    total = len(filtered_raw)
    if total <= maxNames:
        universe = filtered_raw
    else:
        q = total // 4
        q1 = filtered_raw[:q]
        q2 = filtered_raw[q:q*2]
        q3 = filtered_raw[q*2:q*3]
        q4 = filtered_raw[q*3:]
        per_q = maxNames // 4
        import random
        random.seed(42)
        universe = (
            q1[:per_q] +
            random.sample(q2, min(per_q, len(q2))) +
            random.sample(q3, min(per_q, len(q3))) +
            random.sample(q4, min(per_q, len(q4)))
        )
        universe.sort(key=lambda x: x.get("marketCap") or 0)

    symbols = [s["symbol"] for s in universe if s.get("symbol")]

    # ── STAGE 2A: FUNDAMENTALS — batch async, 20 at a time ──────────────────
    async def get_fundamentals(sym, client):
        income_r, cashflow_r = await asyncio.gather(
            fmp(client, "income-statement",    {"symbol": sym, "period": "quarter", "limit": 6}),
            fmp(client, "cash-flow-statement", {"symbol": sym, "period": "quarter", "limit": 6}),
            return_exceptions=True
        )
        revenue_accel = False
        margin_expansion = False
        fcf_positive = False
        fcf_first_positive = False
        rev_qoq_ge15 = False
        revenue_pcts = []
        gross_margins = []

        if isinstance(income_r, list) and len(income_r) >= 3:
            quarters = income_r[:5]
            for i in range(len(quarters) - 1):
                curr = quarters[i].get("revenue") or 0
                prev = quarters[i+1].get("revenue") or 1
                if prev != 0:
                    revenue_pcts.append(round(((curr - prev) / abs(prev)) * 100, 1))
                # Try ratio first, fall back to computing from raw numbers
            gm_ratio = quarters[i].get("grossProfitRatio")
            if gm_ratio is not None:
                gross_margins.append(round(gm_ratio * 100, 2))
            else:
                rev_q = quarters[i].get("revenue") or 0
                gp_q  = quarters[i].get("grossProfit") or 0
                if rev_q > 0:
                    gross_margins.append(round((gp_q / rev_q) * 100, 2))
                else:
                    gross_margins.append(0.0)
            if len(revenue_pcts) >= 2:
                revenue_accel = revenue_pcts[0] > revenue_pcts[1] + 5
            if len(gross_margins) >= 3:
                margin_expansion = (gross_margins[0] > gross_margins[1] + 0.5 and
                                    gross_margins[1] > gross_margins[2] + 0.5)
            if revenue_pcts:
                rev_qoq_ge15 = revenue_pcts[0] >= 15

        prev_fcf = []
        if isinstance(cashflow_r, list) and cashflow_r:
            for i, q in enumerate(cashflow_r[:6]):
                fcf = q.get("freeCashFlow") or 0
                if i == 0:
                    fcf_positive = fcf > 0
                else:
                    prev_fcf.append(fcf)
            if fcf_positive and prev_fcf:
                fcf_first_positive = all(v <= 0 for v in prev_fcf[:3])

        score = sum([revenue_accel, margin_expansion, fcf_positive, fcf_first_positive, rev_qoq_ge15])
        return {
            "symbol": sym,
            "inflection_score": score,
            "signals": {
                "revenue_accel":       revenue_accel,
                "margin_expansion_2q": margin_expansion,
                "fcf_positive":        fcf_positive,
                "fcf_first_positive":  fcf_first_positive,
                "rev_qoq_ge15":        rev_qoq_ge15,
            },
            "revenue_pcts":   revenue_pcts[:3],
            "gross_margins":  gross_margins[:3],
        }

    # ── STAGE 2B: INSIDER CLUSTER — batch async ──────────────────────────────
    async def get_insider_cluster(sym, client):
        r = await fmp(client, "insider-trading", {"symbol": sym, "limit": 50})
        if not isinstance(r, list):
            return {"symbol": sym, "cluster_detected": False, "distinct_buyers": 0, "total_usd": 0}
        from datetime import datetime as dt, timedelta
        cutoff = dt.utcnow() - timedelta(days=14)
        purchases = []
        for trade in r:
            ttype = (trade.get("transactionType") or "").upper()
            if "PURCHASE" not in ttype and ttype != "P":
                continue
            ds = str(trade.get("transactionDate") or trade.get("filingDate") or "")[:10]
            try:
                td = dt.strptime(ds, "%Y-%m-%d")
            except Exception:
                continue
            if td < cutoff:
                continue
            shares = trade.get("securitiesTransacted") or 0
            price  = trade.get("price") or 0
            value  = shares * price
            if value < 1000:
                continue
            purchases.append({"name": trade.get("reportingName") or "Unknown", "value": value})
        distinct = list({p["name"] for p in purchases})
        total = sum(p["value"] for p in purchases)
        return {
            "symbol":           sym,
            "cluster_detected": len(distinct) >= 3 and total >= 50000,
            "distinct_buyers":  len(distinct),
            "total_usd":        round(total, 0),
            "buyers":           distinct[:5],
        }

    # ── STAGE 3: COILED SPRING ───────────────────────────────────────────────
    async def get_spring(sym, client):
        quote_r, change_r, metrics_r = await asyncio.gather(
            fmp(client, "quote",              {"symbol": sym}),
            fmp(client, "stock-price-change", {"symbol": sym}),
            fmp(client, "key-metrics",        {"symbol": sym, "period": "annual", "limit": 1}),
            return_exceptions=True
        )
        km = first(metrics_r) if not isinstance(metrics_r, Exception) else {}
        q = first(quote_r) if not isinstance(quote_r, Exception) else {}
        c = first(change_r) if not isinstance(change_r, Exception) else {}
        price   = q.get("price") or 0
        yh      = q.get("yearHigh") or 1
        avg_vol = q.get("avgVolume") or 1
        vol     = q.get("volume") or 0
        m1      = c.get("1M") or 0
        m3      = c.get("3M") or 0
        rsi_proxy, _, rsi_sig = momentum_to_rsi_proxy(c)
        pct_from_high = round(((yh - price) / yh) * 100, 1) if yh else None

        flat_recent   = abs(m1) < 8
        rsi_zone      = 45 <= (rsi_proxy or 0) <= 65
        near_high     = pct_from_high is not None and pct_from_high < 15
        vol_compress  = vol < avg_vol * 0.85
        positive_base = m3 > 0

        score = sum([flat_recent, rsi_zone, near_high, vol_compress, positive_base])
        return {
            "symbol":       sym,
            "spring_score": score,
            "signals": {
                "flat_1M":       flat_recent,
                "rsi_45_65":     rsi_zone,
                "near_52wk_hi":  near_high,
                "vol_compress":  vol_compress,
                "positive_3M":   positive_base,
            },
            "price":          price,
            "year_high":      yh,
            "year_low":       q.get("yearLow"),
            "pct_from_high":  pct_from_high,
            "rsi_proxy":      rsi_proxy,
            "rsi_signal":     rsi_sig,
            "momentum_1M":    m1,
            "momentum_3M":    m3,
            "vol_ratio":      round(vol / avg_vol, 2) if avg_vol else None,
            "avg_volume":     avg_vol,
            "pe":             km.get("peRatio") if km else None,
            "pb":             km.get("pbRatio") if km else None,
            "ev_ebitda":      km.get("evToEbitda") if km else None,
        }

    # ── RUN STAGES 2A + 2B IN PARALLEL BATCHES OF 20 ────────────────────────
    BATCH = 20
    fund_results  = []
    insider_results = []

    async with httpx.AsyncClient(timeout=20) as client:
        for i in range(0, len(symbols), BATCH):
            batch = symbols[i:i+BATCH]
            f_batch, ins_batch = await asyncio.gather(
                asyncio.gather(*[get_fundamentals(s, client) for s in batch]),
                asyncio.gather(*[get_insider_cluster(s, client) for s in batch]),
                return_exceptions=True
            )
            if isinstance(f_batch, list):
                fund_results.extend(f_batch)
            if isinstance(ins_batch, list):
                insider_results.extend(ins_batch)

    # Index results
    fund_map    = {r["symbol"]: r for r in fund_results if isinstance(r, dict)}
    insider_map = {r["symbol"]: r for r in insider_results if isinstance(r, dict)}

    # Filter survivors: inflection_score >= minInflection OR cluster_detected
    survivors = []
    for sym in symbols:
        f  = fund_map.get(sym, {})
        ins = insider_map.get(sym, {})
        iscore = f.get("inflection_score", 0)
        cluster = ins.get("cluster_detected", False)
        if iscore >= minInflection or cluster:
            survivors.append(sym)

    # ── RUN STAGE 3 ON SURVIVORS ONLY ────────────────────────────────────────
    spring_results = []
    async with httpx.AsyncClient(timeout=20) as client:
        for i in range(0, len(survivors), BATCH):
            batch = survivors[i:i+BATCH]
            s_batch = await asyncio.gather(
                *[get_spring(s, client) for s in batch],
                return_exceptions=True
            )
            spring_results.extend([r for r in s_batch if isinstance(r, dict)])

    spring_map = {r["symbol"]: r for r in spring_results}

    # ── SCORE + RANK ─────────────────────────────────────────────────────────
    # Universe metadata for sector/mktcap lookup
    uni_map = {s["symbol"]: s for s in universe}

    flagged = []
    for sym in survivors:
        f   = fund_map.get(sym, {})
        ins = insider_map.get(sym, {})
        sp  = spring_map.get(sym, {})
        uni = uni_map.get(sym, {})

        iscore  = f.get("inflection_score", 0)
        sscore  = sp.get("spring_score", 0)
        cluster = ins.get("cluster_detected", False)

        # Composite score (max 14)
        composite = 0
        composite += iscore * 2                    # up to 10 (5 signals × 2)
        composite += sscore                        # up to 5
        composite += (3 if cluster else 0)         # cluster buy = +3

        # Tier assignment
        uni_sector = (uni.get("sector") or "").lower()
        if sscore >= 3 and cluster:
            tier = "BOTH"
        elif sscore >= 3 and iscore >= 3:
            tier = "BOTH"
        elif sscore >= 3 and iscore < 3:
            tier = "Tier1-Roth"
        elif iscore >= 3 and uni_sector in ("financial services", "real estate"):
            tier = "Tier2-Taxable-Review"   # flag financials for manual review
        elif iscore >= 3:
            tier = "Tier2-Taxable"
        else:
            tier = "Watch"

        # Filter: composite score floor — score 7 goes to watch only if explicitly requested
        # Default: only output score 8+ to avoid noise (score 7 = watch, not actionable)
        if composite < 8 and not cluster:
            continue
        # Also filter: spring score meets bar
        if sscore < minSpring and not cluster and iscore < 3:
            continue

        price_val  = sp.get("price") or uni.get("price") or 0
        beta_val   = uni.get("beta") or 0
        rev_pcts   = f.get("revenue_pcts", [])
        mktcap_val = uni.get("marketCap") or 0
        m3_val     = sp.get("momentum_3M") or 0
        rsi_val    = sp.get("rsi_proxy") or 50
        ipo_date   = uni.get("ipoDate") or ""

        # ── HARD KILLS — applied before scoring ─────────────────────────────
        kill_reason = None

        # Pull live volume from momentum_map (batch-fetched from /quote)
        quote_data  = momentum_map.get(sym, {})
        avg_vol_live = quote_data.get("avgVolume") or uni.get("avgVolume") or 0
        vol_live     = quote_data.get("volume") or uni.get("volume") or 0
        exchange_live = (quote_data.get("exchange") or uni.get("exchangeShortName") or "").upper()

        # 1. Penny stock
        if price_val > 0 and price_val < 1.00:
            kill_reason = "penny_stock"
        # 2. Absurd beta (data artifact)
        elif abs(beta_val) > 10:
            kill_reason = "absurd_beta"
        # 3. Revenue QoQ data artifact (base-effect distortion)
        elif rev_pcts and any(abs(r) > 10000 for r in rev_pcts):
            kill_reason = "rev_artifact"
        # 4. Market cap below floor
        elif mktcap_val < 50_000_000:
            kill_reason = "mktcap_too_small"
        # 4b. Negative gross margin — burning at the gross level, not investable
        elif f.get("gross_margins") and len(f["gross_margins"]) > 0:
            latest_gm = f["gross_margins"][0]
            if latest_gm < 0:
                kill_reason = f"negative_gross_margin_{latest_gm:.1f}pct"
        # 5. DEAD TICKER — avg volume < 10,000 (private, delisted, or zombie)
        #    This kills OTC names that went private but still exist in FMP database
        elif avg_vol_live > 0 and avg_vol_live < 10000:
            kill_reason = f"dead_ticker_avgvol_{avg_vol_live:.0f}"
        # 6. UNTRADEABLE EXCHANGE — Pink Sheets / Expert Market / Grey Market
        elif exchange_live and any(x in exchange_live for x in ["PINK", "EXPERT", "GREY", "OTC"]):
            kill_reason = f"untradeable_exchange_{exchange_live}"
        # 7. ALREADY RAN — 3M momentum > threshold (discovery too late)
        elif m3_val > maxMomentum3M:
            kill_reason = f"already_ran_3M+{m3_val:.1f}pct"
        # 8. OVERBOUGHT — RSI proxy > threshold
        elif rsi_val > maxRsi:
            kill_reason = f"overbought_rsi{rsi_val:.0f}"
        # 9. IPO < N months old (base-effect revenue distortion)
        elif ipo_date:
            try:
                from datetime import datetime as dt2
                ipo_dt = dt2.strptime(ipo_date[:10], "%Y-%m-%d")
                months_public = (datetime.utcnow() - ipo_dt).days / 30
                if months_public < minIpoMonths:
                    kill_reason = f"ipo_too_recent_{months_public:.0f}mo"
            except Exception:
                pass

        if kill_reason:
            continue

        flagged.append({
            "symbol":           sym,
            "name":             uni.get("name") or uni.get("companyName", ""),
            "sector":           uni.get("sector", ""),
            "industry":         uni.get("industry", ""),
            "marketCap_M":      round(mktcap_val / 1e6, 1),
            "beta":             beta_val,
            "price":            price_val,
            "composite_score":  composite,
            "inflection_score": iscore,
            "spring_score":     sscore,
            "cluster_buy":      cluster,
            "tier":             tier,
            "fund_signals":     f.get("signals", {}),
            "spring_signals":   sp.get("signals", {}),
            "revenue_qoq":      rev_pcts,
            "gross_margins":    f.get("gross_margins", []),
            "insider_buyers":   ins.get("distinct_buyers", 0),
            "insider_usd":      ins.get("total_usd", 0),
            "pct_from_52hi":    sp.get("pct_from_high"),
            "rsi_proxy":        sp.get("rsi_proxy"),
            "rsi_signal":       sp.get("rsi_signal"),
            "momentum_1M":      sp.get("momentum_1M"),
            "momentum_3M":      sp.get("momentum_3M"),
            "vol_ratio":        sp.get("vol_ratio"),
            "avg_volume":       avg_vol_live,
            "exchange":         exchange_live,
        })

    # Sort by composite score descending
    flagged.sort(key=lambda x: x["composite_score"], reverse=True)

    elapsed = round((datetime.utcnow() - start_ts).total_seconds(), 1)

    return no_cache({
        "timestamp":       start_ts.isoformat(),
        "elapsed_seconds": elapsed,
        "pipeline_summary": {
            "universe_total":              len(universe_raw),
            "universe_build": {
                "buckets_pulled":          len(active_buckets),
                "total_after_dedup":       len(universe_raw),
                "momentum_enriched":       len(momentum_map),
            },
            "structural_wall_kills": {
                "cef_bdc_reit":            wall_kills["cef_bdc"],
                "ipo_too_recent":          wall_kills["ipo_age"],
                "already_ran_3M":          wall_kills["already_ran_3M"],
                "vertical_spike_to_high":  wall_kills["vertical_spike_to_high"],
                "passed_all_walls":        wall_kills["passed"],
            },
            "universe_scanned":            len(symbols),
            "survivors_stage2":            len(survivors),
            "flagged_output":              len(flagged),
            "cap_range_scanned":           f"${(universe[0].get('marketCap') or 0)/1e6:.0f}M – ${(universe[-1].get('marketCap') or 0)/1e6:.0f}M" if universe else "n/a",
        },
        "hard_kill_rules": {
            "WALL1_cef_bdc_reit":    "industry/name pattern kill — no API cost",
            "WALL2_ipo_age":         f"IPO < {minIpoMonths} months ago — no API cost",
            "WALL3A_already_ran":    f"3M momentum > {maxMomentum3M}% — no API cost",
            "WALL3B_spike_to_high":  "within 10% of 52wk high AND 1M > 15% — no API cost",
            "OUTPUT_penny":          "price < $1.00",
            "OUTPUT_beta":           "|beta| > 10",
            "OUTPUT_rev_artifact":   "any QoQ > 10,000%",
            "OUTPUT_dead_ticker":       "avgVolume < 10,000 — private/delisted/zombie",
            "OUTPUT_bad_exchange":      "PINK/EXPERT/GREY/OTC exchange — untradeable",
            "OUTPUT_negative_margin":   "gross margin < 0% — burning at gross level",
            "OUTPUT_score_floor":       "composite < 8 (score 7 = watch only, not flagged)",
            "OUTPUT_overbought":        f"RSI proxy > {maxRsi}",
        },
        "filters": {
            "marketCap":       f"${marketCapMin/1e6:.0f}M–${marketCapMax/1e6:.0f}M",
            "sector":          sector or "ALL",
            "minInflection":   minInflection,
            "minSpring":       minSpring,
            "cef_bdc_excluded": True,
            "sampling":        "quartile-balanced across full cap range",
        },
        "flagged": flagged,
    })

# ── HISTORY ENDPOINT ────────────────────────────────────────────────────────────
# NEW /history ENDPOINT — add before the /gcc route at bottom of main.py

@app.get("/history")
async def history(
    symbol: str = Query(...),
    months: int = Query(default=18),
    _key=Depends(verify_key)
):
    """
    Returns daily OHLC price history for a symbol.
    Used by Range Trader scan Gate 1 to count confirmed floor/ceiling touches.
    Default: 18 months of daily closes.
    """
    sym = symbol.upper()
    # FMP historical-price-full returns daily OHLC
    # We calculate the from-date based on months requested
    from datetime import datetime as dt, timedelta
    from_date = (dt.utcnow() - timedelta(days=int(months * 30.44))).strftime("%Y-%m-%d")
    to_date   = dt.utcnow().strftime("%Y-%m-%d")

    async with httpx.AsyncClient() as client:
        r = await fmp(client, "historical-price-eod/full", {
            "symbol": sym,
            "from": from_date,
            "to": to_date,
        })

    # FMP returns { "symbol": "X", "historical": [...] }
    if isinstance(r, dict) and "historical" in r:
        raw = r["historical"]
    elif isinstance(r, list):
        raw = r
    else:
        return no_cache({
            "symbol": sym,
            "error": "No historical data returned",
            "raw": str(r)[:200],
            "timestamp": dt.utcnow().isoformat()
        })

    # Build clean OHLC list sorted oldest → newest
    ohlc = []
    for bar in raw:
        ohlc.append({
            "date":   str(bar.get("date", ""))[:10],
            "open":   bar.get("open"),
            "high":   bar.get("high"),
            "low":    bar.get("low"),
            "close":  bar.get("close") or bar.get("adjClose"),
            "volume": bar.get("volume"),
        })
    # Sort ascending (oldest first)
    ohlc.sort(key=lambda x: x["date"])

    # Basic stats for Gate 1 convenience
    if ohlc:
        closes     = [b["close"] for b in ohlc if b["close"]]
        highs      = [b["high"]  for b in ohlc if b["high"]]
        lows       = [b["low"]   for b in ohlc if b["low"]]
        period_high = round(max(highs), 2) if highs else None
        period_low  = round(min(lows), 2)  if lows  else None
    else:
        period_high = period_low = None

    return no_cache({
        "symbol":        sym,
        "timestamp":     dt.utcnow().isoformat(),
        "months":        months,
        "from_date":     from_date,
        "to_date":       to_date,
        "bars_returned": len(ohlc),
        "period_high":   period_high,
        "period_low":    period_low,
        "ohlc":          ohlc,
    })


# ── HISTORY ANALYZE ENDPOINT ─────────────────────────────────────────────────────

@app.get("/history/analyze")
async def history_analyze(
    symbol: str = Query(...),
    months: int = Query(default=18),
    tolerance: float = Query(default=0.03),
    _key=Depends(verify_key)
):
    """
    Gate 1 automation for Range Trader scan.
    Pulls 18-month OHLC, identifies the stock's INTERNAL trading box
    (not just 52wk high/low), counts floor and ceiling touches,
    confirms round trips, and returns Gate 1 pass/fail with full detail.
    
    tolerance: how close to floor/ceiling counts as a touch (default 3%)
    """
    sym = symbol.upper()
    from datetime import datetime as dt, timedelta

    from_date = (dt.utcnow() - timedelta(days=int(months * 30.44))).strftime("%Y-%m-%d")
    to_date   = dt.utcnow().strftime("%Y-%m-%d")

    async with httpx.AsyncClient() as client:
        r = await fmp(client, "historical-price-eod/full", {
            "symbol": sym,
            "from": from_date,
            "to": to_date,
        })

    if isinstance(r, dict) and "historical" in r:
        raw = r["historical"]
    elif isinstance(r, list):
        raw = r
    else:
        return no_cache({
            "symbol": sym, "gate1_pass": False,
            "error": "No historical data", "timestamp": dt.utcnow().isoformat()
        })

    # Sort ascending
    ohlc = sorted([
        {
            "date":   str(b.get("date", ""))[:10],
            "open":   b.get("open"),
            "high":   b.get("high"),
            "low":    b.get("low"),
            "close":  b.get("close") or b.get("adjClose"),
            "volume": b.get("volume"),
        }
        for b in raw if b.get("close") or b.get("adjClose")
    ], key=lambda x: x["date"])

    if len(ohlc) < 60:
        return no_cache({
            "symbol": sym, "gate1_pass": False,
            "error": f"Insufficient data: only {len(ohlc)} bars",
            "timestamp": dt.utcnow().isoformat()
        })

    closes = [b["close"] for b in ohlc if b["close"]]
    lows   = [b["low"]   for b in ohlc if b["low"]]
    highs  = [b["high"]  for b in ohlc if b["high"]]

    period_low  = min(lows)
    period_high = max(highs)
    raw_box_width = (period_high - period_low) / period_low * 100

    # ── INTERNAL BOX DETECTION ────────────────────────────────────────────────
    # The 52wk high/low may be a single spike. We want the REPEATED trading range.
    # Method: trim the top 5% and bottom 5% of daily closes to find the
    # "body" range the stock actually oscillates within.
    sorted_closes = sorted(closes)
    trim = max(1, int(len(sorted_closes) * 0.05))
    body_low  = sorted_closes[trim]
    body_high = sorted_closes[-trim]
    body_width = (body_high - body_low) / body_low * 100

    # Gate 2 check: internal box width 18-35% is ideal
    # We use body range for gate scoring but report both
    floor_level   = body_low  * (1 + tolerance)
    ceiling_level = body_high * (1 - tolerance)

    # ── TOUCH COUNTING ────────────────────────────────────────────────────────
    # Minimum 10 trading days between touches to count as distinct
    floor_touches   = []
    ceiling_touches = []
    last_floor_idx   = -999
    last_ceiling_idx = -999

    for i, bar in enumerate(ohlc):
        low  = bar.get("low")  or 0
        high = bar.get("high") or 0

        if low and low <= floor_level and (i - last_floor_idx) >= 10:
            floor_touches.append({
                "date": bar["date"],
                "low": round(low, 2),
                "pct_from_body_low": round(((low - body_low) / body_low) * 100, 1)
            })
            last_floor_idx = i

        if high and high >= ceiling_level and (i - last_ceiling_idx) >= 10:
            ceiling_touches.append({
                "date": bar["date"],
                "high": round(high, 2),
                "pct_from_body_high": round(((high - body_high) / body_high) * 100, 1)
            })
            last_ceiling_idx = i

    # ── ROUND TRIP COUNTING ───────────────────────────────────────────────────
    # A round trip = floor touch followed by ceiling touch (or vice versa)
    # Merge all touches with type, sort by date, count direction changes
    all_touches = (
        [{"date": t["date"], "type": "floor"}   for t in floor_touches] +
        [{"date": t["date"], "type": "ceiling"} for t in ceiling_touches]
    )
    all_touches.sort(key=lambda x: x["date"])

    # Count round trips: each time direction changes floor→ceiling or ceiling→floor
    # counts as half a round trip. Two direction changes = one full round trip.
    # This correctly handles clustered touches (e.g. 4 floors then 10 ceilings = 1 RT)
    # as well as interleaved touches (floor ceiling floor ceiling = 2 RTs)
    direction_changes = 0
    last_type = None
    for touch in all_touches:
        if last_type is not None and touch["type"] != last_type:
            direction_changes += 1
        last_type = touch["type"]
    round_trips = direction_changes // 2  # 2 direction changes = 1 full round trip

    # ── GATE 1 SCORING ────────────────────────────────────────────────────────
    floor_count   = len(floor_touches)
    ceiling_count = len(ceiling_touches)

    gate1_pass = (
        floor_count   >= 3 and
        ceiling_count >= 3 and
        round_trips   >= 2 and
        box_width_pass            # box must be 20-40% wide
    )

    # ── BOX WIDTH GATE ────────────────────────────────────────────────────────
    box_width_pass = 20 <= body_width <= 40  # Tightened Jun15'26 — true oscillators only

    # ── CURRENT PRICE LOCATION ────────────────────────────────────────────────
    current_price = closes[-1] if closes else 0
    if body_high > body_low:
        price_pct_of_box = round(((current_price - body_low) / (body_high - body_low)) * 100, 1)
    else:
        price_pct_of_box = None

    # Zone determination
    bottom_15 = body_low + (body_high - body_low) * 0.15
    bottom_30 = body_low + (body_high - body_low) * 0.30
    if current_price <= bottom_15:
        zone = "TIER2_BUY"
    elif current_price <= bottom_30:
        zone = "TIER1_BUY"
    elif current_price >= body_high * (1 - tolerance):
        zone = "NEAR_CEILING"
    else:
        zone = "MID_RANGE"

    return no_cache({
        "symbol":      sym,
        "timestamp":   dt.utcnow().isoformat(),
        "months":      months,
        "bars":        len(ohlc),
        "gate1": {
            "pass":            gate1_pass,
            "floor_touches":   floor_count,
            "ceiling_touches": ceiling_count,
            "round_trips":     round_trips,
            "requirement":     "3+ floor, 3+ ceiling, 2+ round trips",
            "verdict":         "✅ PASS — confirmed range trader" if gate1_pass else "❌ FAIL — not a confirmed oscillator",
        },
        "box": {
            "body_low":        round(body_low, 2),
            "body_high":       round(body_high, 2),
            "body_width_pct":  round(body_width, 1),
            "period_low":      round(period_low, 2),
            "period_high":     round(period_high, 2),
            "raw_width_pct":   round(raw_box_width, 1),
            "width_gate_pass": box_width_pass,
            "floor_level":     round(floor_level, 2),
            "ceiling_level":   round(ceiling_level, 2),
            "tolerance_pct":   tolerance * 100,
        },
        "current_price": round(current_price, 2),
        "price_location": {
            "pct_of_box":  price_pct_of_box,
            "zone":        zone,
            "tier2_buy_under": round(bottom_15, 2),
            "tier1_buy_under": round(bottom_30, 2),
        },
        "floor_touch_dates":   [t["date"] for t in floor_touches],
        "ceiling_touch_dates": [t["date"] for t in ceiling_touches],
    })


# ── RANGE SCREEN ENDPOINT ───────────────────────────────────────────────────────

# ── RANGE SCREEN ENDPOINT ─────────────────────────────────────────────────────
# Master candidate pool of known sideways oscillators by sector.
# Runs Gate 1 on all candidates, returns only certified setups.

RANGE_CANDIDATES = [
    # Specialty Equipment / Rental
    "URI", "HRI", "MGRC", "WLFC", "KFRC", "HURN",
    # Water / Utilities / Infrastructure
    "AWR", "AWK", "WTS", "SJW", "MSEX", "YORW", "ARTNA",
    # Industrial Services / Defense Base
    "SAIC", "CACI", "LDOS", "ICFI", "KBR", "MANT",
    # Consumer Staples / Household
    "CHD", "PBH", "CENT", "CENTA", "IPAR", "AMSF",
    # Specialty Chemicals / Materials
    "HWKN", "IOSP", "ASIX", "LIQT", "GOED",
    # Food Distribution / Packaging
    "CORE", "JBSS", "SENEA", "SENEB", "LNDC",
    # Security / Safety
    "NSSC", "NAPCO", "SCSC", "DGLY",
    # Financial Services / Insurance
    "MBIN", "NBTB", "CZWI", "CHMG", "ESSA",
    # Boring Industrials
    "EPAC", "BCPC", "NNBR", "NN", "SMID", "DXPE",
    # Healthcare Services (low binary risk)
    "MMSI", "ADUS", "AFAM", "AMED",
]

@app.get("/range-screen")
async def range_screen(
    months: int = Query(default=18),
    _key=Depends(verify_key)
):
    """
    Runs Gate 1 (box width + touch count + round trips) across the full
    Range Trader candidate pool. Returns certified setups only.
    Sectors: equipment rental, utilities, consumer staples, industrial services,
    specialty chemicals, food distribution, security, boring industrials.
    """
    from datetime import datetime as dt, timedelta

    from_date = (dt.utcnow() - timedelta(days=int(months * 30.44))).strftime("%Y-%m-%d")
    to_date   = dt.utcnow().strftime("%Y-%m-%d")

    results   = []
    certified = []
    wide_box  = []
    failures  = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for sym in RANGE_CANDIDATES:
            try:
                r = await fmp(client, "historical-price-eod/full", {
                    "symbol": sym,
                    "from": from_date,
                    "to": to_date,
                })

                if isinstance(r, dict) and "historical" in r:
                    raw = r["historical"]
                elif isinstance(r, list):
                    raw = r
                else:
                    failures.append({"symbol": sym, "reason": "no data"})
                    continue

                ohlc = sorted([
                    {
                        "date":   str(b.get("date",""))[:10],
                        "high":   b.get("high"),
                        "low":    b.get("low"),
                        "close":  b.get("close") or b.get("adjClose"),
                        "volume": b.get("volume"),
                    }
                    for b in raw if b.get("close") or b.get("adjClose")
                ], key=lambda x: x["date"])

                if len(ohlc) < 60:
                    failures.append({"symbol": sym, "reason": f"only {len(ohlc)} bars"})
                    continue

                closes = [b["close"] for b in ohlc if b["close"]]
                lows   = [b["low"]   for b in ohlc if b["low"]]
                highs  = [b["high"]  for b in ohlc if b["high"]]

                # Internal body range (trim 5% extremes)
                sorted_closes = sorted(closes)
                trim      = max(1, int(len(sorted_closes) * 0.05))
                body_low  = sorted_closes[trim]
                body_high = sorted_closes[-trim]
                body_width = (body_high - body_low) / body_low * 100

                tolerance     = 0.03
                floor_level   = body_low  * (1 + tolerance)
                ceiling_level = body_high * (1 - tolerance)

                # Touch counting
                floor_touches   = []
                ceiling_touches = []
                last_fi = last_ci = -999

                for i, bar in enumerate(ohlc):
                    lo = bar.get("low")  or 0
                    hi = bar.get("high") or 0
                    if lo and lo <= floor_level   and (i - last_fi) >= 10:
                        floor_touches.append(bar["date"]); last_fi = i
                    if hi and hi >= ceiling_level and (i - last_ci) >= 10:
                        ceiling_touches.append(bar["date"]); last_ci = i

                # Round trips
                all_t = sorted(
                    [{"date": d, "type": "floor"}   for d in floor_touches] +
                    [{"date": d, "type": "ceiling"} for d in ceiling_touches],
                    key=lambda x: x["date"]
                )
                direction_changes = 0
                last_type = None
                for t in all_t:
                    if last_type is not None and t["type"] != last_type:
                        direction_changes += 1
                    last_type = t["type"]
                round_trips = direction_changes // 2

                current_price = closes[-1]
                box_width_ok  = 20 <= body_width <= 40

                # Zone
                bottom_15 = body_low + (body_high - body_low) * 0.15
                bottom_30 = body_low + (body_high - body_low) * 0.30
                if current_price <= bottom_15:
                    zone = "TIER2_BUY"
                elif current_price <= bottom_30:
                    zone = "TIER1_BUY"
                elif current_price >= ceiling_level:
                    zone = "NEAR_CEILING"
                else:
                    zone = "MID_RANGE"

                entry = {
                    "symbol":          sym,
                    "current_price":   round(current_price, 2),
                    "body_low":        round(body_low, 2),
                    "body_high":       round(body_high, 2),
                    "body_width_pct":  round(body_width, 1),
                    "floor_touches":   len(floor_touches),
                    "ceiling_touches": len(ceiling_touches),
                    "round_trips":     round_trips,
                    "zone":            zone,
                    "tier2_buy_under": round(bottom_15, 2),
                    "tier1_buy_under": round(bottom_30, 2),
                }

                gate1_pass = (
                    len(floor_touches)   >= 3 and
                    len(ceiling_touches) >= 3 and
                    round_trips          >= 2 and
                    box_width_ok
                )

                if gate1_pass:
                    certified.append(entry)
                elif body_width > 40 and len(floor_touches) >= 3 and len(ceiling_touches) >= 3 and round_trips >= 2:
                    # Valid oscillator but wide box — flag separately
                    entry["flag"] = "WIDE_BOX"
                    wide_box.append(entry)
                else:
                    entry["fail_reason"] = (
                        "box_width" if not box_width_ok else
                        "touches"   if (len(floor_touches) < 3 or len(ceiling_touches) < 3) else
                        "round_trips"
                    )
                    failures.append(entry)

            except Exception as e:
                failures.append({"symbol": sym, "reason": str(e)[:80]})

    return no_cache({
        "timestamp":        dt.utcnow().isoformat(),
        "months":           months,
        "candidates_run":   len(RANGE_CANDIDATES),
        "certified_count":  len(certified),
        "wide_box_count":   len(wide_box),
        "certified":        certified,
        "wide_box_flags":   wide_box,
        "failure_count":    len(failures),
        "failures":         failures,
    })

# ── Gary Command Center ───────────────────────────────────────────────────────
from pathlib import Path

@app.get("/gcc", response_class=HTMLResponse, include_in_schema=False)
async def command_center():
    html_path = Path(__file__).parent / "gcc.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)
# ── Watchlist price cache (populated by cron) ─────────────────────────────────
import json, time
_price_cache: dict = {}
_cache_ts: float   = 0.0

WATCHLIST_SYMBOLS = [
    "DVN","CVX","XOM","NOC","LMT","CDRE","MPTI",
    "NOVT","CVU","ROBO","RBCAA","MU","VOYG","MRVI","FLTCF"
]

async def _refresh_prices(client: httpx.AsyncClient) -> dict:
    """Fetch batch quotes for all watchlist symbols and cache them."""
    global _price_cache, _cache_ts
    syms = ",".join(WATCHLIST_SYMBOLS)
    try:
        r = await client.get(
            f"{FMP_BASE}/quote",
            params={"symbol": syms, "apikey": FMP_KEY},
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        arr  = data if isinstance(data, list) else []
        cache = {}
        for q in arr:
            sym = (q.get("symbol") or "").upper()
            if sym:
                cache[sym] = {
                    "price":  q.get("price") or q.get("previousClose") or 0,
                    "change": q.get("changesPercentage") or 0,
                    "ts":     time.time(),
                }
        _price_cache = cache
        _cache_ts    = time.time()
        return {"status": "ok", "symbols": list(cache.keys()), "ts": _cache_ts}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Cron endpoint (Railway calls this on schedule) ────────────────────────────
@app.get("/cron/refresh", dependencies=[Depends(verify_key)])
async def cron_refresh():
    """
    Railway cron hits this endpoint at:
      7:00 AM, 9:45 AM, 12:00 PM, 3:00 PM, 4:15 PM ET
    Schedule strings (UTC — ET is UTC-4 in summer):
      0 11 * * 1-5      →  7:00 AM ET
      45 13 * * 1-5     →  9:45 AM ET
      0 16 * * 1-5      → 12:00 PM ET
      0 19 * * 1-5      →  3:00 PM ET
      15 20 * * 1-5     →  4:15 PM ET
    """
    async with httpx.AsyncClient() as client:
        result = await _refresh_prices(client)
    return no_cache(result)


# ── Cached prices endpoint (GCC dashboard polls this) ─────────────────────────
@app.get("/prices", dependencies=[Depends(verify_key)])
async def get_prices(symbols: str = Query(default="")):
    """
    Returns cached prices for all watchlist symbols.
    Falls back to live fetch if cache is empty or stale (> 10 min).
    Dashboard calls: GET /prices?symbols=DVN,CVX,XOM,...
    """
    global _price_cache, _cache_ts
    requested = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    cache_age = time.time() - _cache_ts

    # If cache is fresh (< 10 min), serve it
    if _price_cache and cache_age < 600:
        result = {s: _price_cache[s] for s in requested if s in _price_cache}
        return no_cache({"source": "cache", "age_seconds": int(cache_age), "data": result})

    # Cache stale or empty — do a live fetch
    async with httpx.AsyncClient() as client:
        await _refresh_prices(client)
    result = {s: _price_cache[s] for s in requested if s in _price_cache}
    return no_cache({"source": "live", "age_seconds": 0, "data": result})


# ── GCC Dashboard ─────────────────────────────────────────────────────────────
from pathlib import Path

@app.get("/gcc", response_class=HTMLResponse, include_in_schema=False)
async def command_center():
    html_path = Path(__file__).parent / "gcc.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)
# ── Anthropic Claude Proxy ────────────────────────────────────────────────────
# Add this to the bottom of main.py
# Requires: ANTHROPIC_API_KEY environment variable set in Railway

# ── Anthropic Claude Proxy v2 (with web search) ───────────────────────────────
# REPLACE the existing claude_proxy and claude_test functions in main.py with these.
# Web search lets Claude fetch live prices, YTD data, insider filings, etc.

# ── Anthropic Claude Proxy v3 (async job queue) ───────────────────────────────
# REPLACE the existing ANTHROPIC_API_KEY, claude_proxy, and claude_test 
# blocks at the bottom of main.py with this entire block.

import uuid

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# In-memory job store: { job_id: { "status": "pending"|"done"|"error", "text": "..." } }
_jobs: dict = {}

async def _run_claude_job(job_id: str, system: str, message: str, max_tokens: int):
    """Runs in background. Stores result in _jobs when complete."""
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": max_tokens,
                    "system": system,
                    "tools": [{"type": "web_search_20250305", "name": "web_search"}],
                    "messages": [{"role": "user", "content": message}],
                }
            )
            r.raise_for_status()
            data = r.json()
            text = "".join(
                block.get("text", "")
                for block in data.get("content", [])
                if block.get("type") == "text"
            )
            _jobs[job_id] = {"status": "done", "text": text}
    except Exception as e:
        _jobs[job_id] = {"status": "error", "text": str(e)}


@app.post("/claude", dependencies=[Depends(verify_key)])
async def claude_proxy(request: Request, background_tasks: BackgroundTasks):
    """
    Starts a Claude job in the background. Returns job_id immediately.
    Client polls /claude/result/{job_id} for completion.
    Body: { "system": "...", "message": "...", "max_tokens": 4000 }
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    body       = await request.json()
    system     = body.get("system", "")
    message    = body.get("message", "")
    max_tokens = min(int(body.get("max_tokens", 4000)), 4000)
    job_id     = str(uuid.uuid4())

    _jobs[job_id] = {"status": "pending", "text": ""}
    background_tasks.add_task(_run_claude_job, job_id, system, message, max_tokens)

    return no_cache({"job_id": job_id})


@app.get("/claude/result/{job_id}", dependencies=[Depends(verify_key)])
async def claude_result(job_id: str):
    """Poll this endpoint every 3 seconds until status is 'done' or 'error'."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return no_cache(job)


@app.get("/claude/test", dependencies=[Depends(verify_key)])
async def claude_test():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    return {"key_loaded": bool(key), "key_prefix": key[:12] + "..." if key else "MISSING"}

# ── Stock Lookup Endpoint v6 ─────────────────────────────────────────────────
# REPLACE the existing /lookup endpoint in main.py with this.
# Field paths confirmed from /conviction response structure.

@app.get("/lookup", dependencies=[Depends(verify_key)])
async def stock_lookup(symbol: str = Query(...)):
    sym = symbol.upper().strip()
    async with httpx.AsyncClient() as client:
        quote_task   = fmp(client, "quote",                  {"symbol": sym})
        profile_task = fmp(client, "profile",                {"symbol": sym})
        rsi_task     = fmp(client, "technical-indicators/rsi", {"symbol": sym, "periodLength": 14, "timeframe": "1day"})
        change_task  = fmp(client, "stock-price-change",      {"symbol": sym})
        income_task  = fmp(client, "income-statement",        {"symbol": sym, "limit": 1})
        grades_task  = fmp(client, "analyst-stock-ratings",   {"symbol": sym, "limit": 5})
        target_task  = fmp(client, "price-target-consensus",  {"symbol": sym})

        quote_raw, profile_raw, rsi_raw, change_raw, income_raw, grades_raw, target_raw = await asyncio.gather(
            quote_task, profile_task, rsi_task, change_task, income_task, grades_task, target_task
        )

    q   = first(quote_raw)
    pro = first(profile_raw)
    inc = first(income_raw)
    tgt = first(target_raw)

    # Price
    price      = float(q.get("price") or 0)
    change     = float(q.get("change") or 0)
    change_pct = float(q.get("changesPercentage") or 0)

    # RSI
    rsi_val = None
    if isinstance(rsi_raw, list) and rsi_raw:
        rsi_val = rsi_raw[0].get("rsi")

    # YTD from stock-price-change
    chg = first(change_raw) if isinstance(change_raw, list) else (change_raw or {})
    ytd = float(chg.get("ytd") or chg.get("YTD") or chg.get("ytdChange") or 0) or None

    # EPS from income statement
    eps = float(inc.get("eps") or inc.get("epsdiluted") or 0) or None

    # Analyst target
    apt = float(tgt.get("targetConsensus") or tgt.get("targetMedian") or 0) or None

    # Recent grades
    recent = []
    grades_list = grades_raw if isinstance(grades_raw, list) else []
    for g in grades_list[:5]:
        recent.append({
            "company": g.get("gradingCompany") or g.get("company") or "",
            "grade":   g.get("newGrade") or g.get("grade") or "",
            "action":  g.get("action") or "",
            "date":    g.get("date") or "",
            "prevGrade": g.get("previousGrade") or "",
        })

    return no_cache({
        "symbol":        q.get("symbol", sym),
        "name":          q.get("name") or pro.get("companyName") or "",
        "price":         price,
        "change":        change,
        "changePct":     change_pct,
        "yearHigh":      float(q.get("yearHigh") or 0),
        "yearLow":       float(q.get("yearLow") or 0),
        "volume":        int(q.get("volume") or 0),
        "marketCap":     float(q.get("marketCap") or 0),
        "beta":          float(pro.get("beta") or q.get("beta") or 0) or None,
        "rsi":           float(rsi_val) if rsi_val is not None else None,
        "ytdPct":        ytd,
        "eps":           eps,
        "analystTarget": apt,
        "recentGrades":  recent,
    })
