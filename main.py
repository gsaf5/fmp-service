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
    return {"status": "ok", "service": "Claude Market API v5.0",
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
