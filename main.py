import os
import asyncio
import math
from datetime import datetime
from fastapi import FastAPI, Query, Depends, Header, HTTPException
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
    return {"status": "ok", "service": "Claude Market API v5.1",
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

    # ── STAGE 1: UNIVERSE ────────────────────────────────────────────────────
    async with httpx.AsyncClient(timeout=30) as client:
        screener_params = {
            "marketCapMoreThan": marketCapMin,
            "marketCapLowerThan": marketCapMax,
            "isEtf": "false",
            "isActivelyTrading": "true",
            "country": "US",
            "netIncomeMoreThan": 0,
            "limit": 1000,
        }
        if sector:
            screener_params["sector"] = sector
        universe_raw = await fmp(client, "company-screener", screener_params)

    if not isinstance(universe_raw, list) or len(universe_raw) == 0:
        return no_cache({"error": "Universe pull failed or empty", "timestamp": start_ts.isoformat()})

    # Sort by market cap ascending (smaller = more undiscovered)
    universe_raw.sort(key=lambda x: x.get("marketCap") or 0)

    # Cap at maxNames — take smallest caps first (best discovery targets)
    universe = universe_raw[:maxNames]
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
        if sscore >= 3 and cluster:
            tier = "BOTH"
        elif sscore >= 3 and iscore < 3:
            tier = "Tier1-Roth"
        elif iscore >= 3:
            tier = "Tier2-Taxable"
        else:
            tier = "Watch"

        # Filter: only include if spring score also meets bar
        if sscore < minSpring and not cluster and iscore < 3:
            continue

        price_val = sp.get("price") or uni.get("price") or 0
        beta_val  = uni.get("beta") or 0
        rev_pcts  = f.get("revenue_pcts", [])

        # ── HARD KILLS ──────────────────────────────────────────────────────
        # 1. Penny stock: price < $1.00
        if price_val > 0 and price_val < 1.00:
            continue
        # 2. Absurd beta: |beta| > 10 (data artifact)
        if abs(beta_val) > 10:
            continue
        # 3. Revenue QoQ data artifact: any single quarter > 10,000% (base effect distortion)
        if rev_pcts and any(abs(r) > 10000 for r in rev_pcts):
            continue
        # 4. Market cap too thin: under $50M (screener sometimes returns stale data)
        mktcap_val = uni.get("marketCap") or 0
        if mktcap_val < 50_000_000:
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
        })

    # Sort by composite score descending
    flagged.sort(key=lambda x: x["composite_score"], reverse=True)

    elapsed = round((datetime.utcnow() - start_ts).total_seconds(), 1)

    return no_cache({
        "timestamp":       start_ts.isoformat(),
        "elapsed_seconds": elapsed,
        "pipeline_summary": {
            "universe_total":    len(universe_raw),
            "universe_scanned":  len(symbols),
            "survivors_stage2":  len(survivors),
            "flagged_output":    len(flagged),
        },
        "filters": {
            "marketCap":       f"${marketCapMin/1e6:.0f}M–${marketCapMax/1e6:.0f}M",
            "sector":          sector or "ALL",
            "minInflection":   minInflection,
            "minSpring":       minSpring,
        },
        "flagged": flagged,
    })

