import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Claude Market API", version="3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

FMP_KEY = os.environ.get("FMP_API_KEY", "")
FMP_BASE = "https://financialmodelingprep.com/stable"

# Watchlist lives in GitHub Gist — fetched dynamically at runtime
# Claude updates the Gist directly; no code changes needed for watchlist edits
GIST_ID = "4c5cd13043497addfbbe3eaaf0ae67a8"
GIST_URL = f"https://gist.githubusercontent.com/gsaf5/{GIST_ID}/raw/watchlist.json"

RED_FLAG_KEYWORDS = [
    "class action", "sec investigation", "going concern", "shelf registration",
    "atm offering", "restatement", "subpoena", "dilution", "default", "delisted",
    "fraud", "bankruptcy", "nasdaq notice", "nyse notice"
]

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

def scan_news(articles):
    flags = []
    for a in (articles or [])[:15]:
        text = (a.get("title", "") + " " + a.get("text", "")).lower()
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
    """Fetch live watchlist JSON from GitHub Gist."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(GIST_URL, timeout=8)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": str(e), "tickers": {}}


# ── PING — fixes Claude.ai mobile sandbox domain whitelisting ─────────────────
@app.get("/ping")
async def ping():
    return JSONResponse(
        content={"status": "ok", "service": "Claude Market API v3.2", "ts": datetime.utcnow().isoformat()},
        headers={"Cache-Control": "no-store", "Access-Control-Allow-Origin": "*"}
    )


@app.get("/")
async def root():
    return {
        "service": "Claude Market API v3.2",
        "endpoints": ["/ping", "/quote", "/conviction", "/vet", "/scan", "/watchlist"],
        "fmp_plan": "Starter",
        "watchlist_source": f"GitHub Gist {GIST_ID} — updated dynamically by Claude",
        "mobile_note": "Fetch /ping first on Claude.ai mobile to whitelist domain"
    }


@app.get("/quote")
async def quote(symbols: str = Query(...)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[fmp(client, "/quote", {"symbol": t}) for t in tickers])
    output = {}
    for i, t in enumerate(tickers):
        d = first(results[i])
        output[t] = {
            "price": d.get("price"),
            "change": d.get("change"),
            "changesPercentage": d.get("changePercentage"),
            "dayLow": d.get("dayLow"),
            "dayHigh": d.get("dayHigh"),
            "yearLow": d.get("yearLow"),
            "yearHigh": d.get("yearHigh"),
            "volume": d.get("volume"),
            "avgVolume": d.get("averageVolume"),
            "marketCap": d.get("marketCap"),
            "priceAvg50": d.get("priceAvg50"),
            "priceAvg200": d.get("priceAvg200"),
        }
    return output


@app.get("/conviction")
async def conviction(symbol: str = Query(...)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        (quote_r, profile_r, income_r, earnings_r, grades_r,
         pt_r, insider_r, score_r, news_r, rsi_r, metrics_r) = await asyncio.gather(
            fmp(client, "/quote", {"symbol": sym}),
            fmp(client, "/profile", {"symbol": sym}),
            fmp(client, "/income-statement", {"symbol": sym, "limit": 5}),
            fmp(client, "/earnings-surprises", {"symbol": sym, "limit": 8}),
            fmp(client, "/grades", {"symbol": sym, "limit": 20}),
            fmp(client, "/price-target-summary", {"symbol": sym}),
            fmp(client, "/insider-trading/statistics", {"symbol": sym}),
            fmp(client, "/financial-scores", {"symbol": sym}),
            fmp(client, "/news/stock", {"tickers": sym, "limit": 20}),
            fmp(client, "/technical-indicators/rsi", {"symbol": sym, "periodLength": 14, "timeframe": "1day", "limit": 10}),
            fmp(client, "/key-metrics", {"symbol": sym, "limit": 2}),
            return_exceptions=True
        )

    q = first(quote_r)
    p = first(profile_r)
    current_price = q.get("price", 0) or 0

    rsi_history = [{"date": str(r.get("date", ""))[:10], "rsi": round(float(r.get("rsi", 0)), 2)}
                   for r in (rsi_r if isinstance(rsi_r, list) else [])[:10]]
    rsi_current = rsi_history[0]["rsi"] if rsi_history else None
    rsi_dir = ("RISING" if len(rsi_history) >= 3 and rsi_history[0]["rsi"] > rsi_history[2]["rsi"]
               else "FALLING" if len(rsi_history) >= 3 and rsi_history[0]["rsi"] < rsi_history[2]["rsi"]
               else "FLAT")
    rsi_sig = ("OVERSOLD" if rsi_current and rsi_current < 30
               else "OVERBOUGHT" if rsi_current and rsi_current > 70 else "NEUTRAL" if rsi_current else "N/A")

    eps_history = []
    if isinstance(earnings_r, list):
        for e in earnings_r[:4]:
            actual, est = e.get("actualEarningResult"), e.get("estimatedEarning")
            beat = actual >= est if actual is not None and est is not None else None
            pct = round(((actual - est) / abs(est)) * 100, 1) if beat is not None and est != 0 else None
            eps_history.append({"date": str(e.get("date", ""))[:10], "estimated": est,
                                 "actual": actual, "beat": beat, "surprise_pct": pct})
    beat_count = sum(1 for e in eps_history if e.get("beat"))

    revenue_trend = [{"date": str(s.get("date", ""))[:10], "revenue": s.get("revenue"),
                      "grossProfit": s.get("grossProfit"), "operatingIncome": s.get("operatingIncome"),
                      "netIncome": s.get("netIncome"), "eps": s.get("eps")}
                     for s in (income_r if isinstance(income_r, list) else [])[:4]]

    grade_summary = {}
    if isinstance(grades_r, list) and grades_r:
        recent5 = grades_r[:5]
        grade_summary = {
            "analyst_count": len(set(g.get("gradingCompany", "") for g in grades_r)),
            "recent_grades": [{"company": g.get("gradingCompany"), "grade": g.get("newGrade"),
                               "action": g.get("action"), "date": str(g.get("date", ""))[:10]}
                              for g in recent5],
            "upgrades_last5": sum(1 for g in recent5 if g.get("action") == "upgraded"),
            "downgrades_last5": sum(1 for g in recent5 if g.get("action") == "downgraded")
        }

    pt_summary = {}
    pt = first(pt_r)
    if pt and "lastMonthAvgPriceTarget" in pt:
        avg_pt = pt.get("lastMonthAvgPriceTarget") or pt.get("lastQuarterAvgPriceTarget")
        upside = round(((avg_pt - current_price) / current_price) * 100, 1) if avg_pt and current_price else None
        pt_summary = {
            "last_month_avg": pt.get("lastMonthAvgPriceTarget"),
            "last_month_count": pt.get("lastMonthCount"),
            "last_quarter_avg": pt.get("lastQuarterAvgPriceTarget"),
            "last_year_avg": pt.get("lastYearAvgPriceTarget"),
            "implied_upside_pct": upside,
            "current_price": current_price,
            "above_target": current_price >= avg_pt if avg_pt else None
        }

    insider_summary = agg_insider(insider_r if isinstance(insider_r, list) else [])

    score_summary = {}
    sc = first(score_r)
    if sc and "altmanZScore" in sc:
        z, f = sc.get("altmanZScore"), sc.get("piotroskiScore")
        score_summary = {
            "altman_z": z, "piotroski_f": f,
            "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE" if z else "N/A",
            "kill_flag": bool(z and z < 1.8 and f is not None and f <= 2)
        }

    news_articles = [a for a in (news_r if isinstance(news_r, list) else [])
                     if a.get("symbol", "").upper() == sym]
    if not news_articles and isinstance(news_r, list):
        news_articles = news_r
    news_scan = scan_news(news_articles)

    km = first(metrics_r)

    c1 = not insider_summary.get("kill_flag", False)
    c2 = not score_summary.get("kill_flag", False)
    c3 = grade_summary.get("analyst_count", 0) <= 8 and grade_summary.get("downgrades_last5", 0) < 2
    c4 = not pt_summary.get("above_target", False)
    c5 = news_scan.get("pass", True)
    fails = sum(1 for x in [c1, c2, c3, c4, c5] if not x)

    return {
        "symbol": sym,
        "timestamp": datetime.utcnow().isoformat(),
        "quote": {"price": current_price, "change": q.get("change"),
                  "changesPercentage": q.get("changePercentage"),
                  "dayLow": q.get("dayLow"), "dayHigh": q.get("dayHigh"),
                  "yearLow": q.get("yearLow"), "yearHigh": q.get("yearHigh"),
                  "volume": q.get("volume"), "avgVolume": q.get("averageVolume"),
                  "marketCap": q.get("marketCap"),
                  "priceAvg50": q.get("priceAvg50"), "priceAvg200": q.get("priceAvg200")},
        "profile": {"name": p.get("companyName"), "sector": p.get("sector"),
                    "industry": p.get("industry"), "exchange": p.get("exchangeFullName"),
                    "description": str(p.get("description", ""))[:300],
                    "ceo": p.get("ceo"), "employees": p.get("fullTimeEmployees"),
                    "beta": p.get("beta"), "ipoDate": p.get("ipoDate")},
        "technicals": {"rsi_current": rsi_current, "rsi_direction": rsi_dir,
                       "rsi_signal": rsi_sig, "rsi_history": rsi_history},
        "fundamentals": {"pe_forward": km.get("peRatio"), "peg": km.get("pegRatio"),
                         "price_to_sales": km.get("priceToSalesRatio"),
                         "price_to_book": km.get("pbRatio"),
                         "debt_to_equity": km.get("debtToEquity"),
                         "current_ratio": km.get("currentRatio"),
                         "roe": km.get("roe"),
                         "revenue_trend": revenue_trend,
                         "beat_count": beat_count, "beat_rate": f"{beat_count}/4",
                         "eps_history": eps_history},
        "analyst": {"grades": grade_summary, "price_targets": pt_summary},
        "insider": insider_summary,
        "financial_scores": score_summary,
        "news_scan": news_scan,
        "phase0_gate": {
            "gates_passed": 5 - fails, "gates_failed": fails,
            "overall": "PASS" if fails == 0 else f"FAIL ({fails} gates failed)",
            "results": {
                "check1_insider": {"pass": c1, "detail": insider_summary},
                "check2_balance_sheet": {"pass": c2, "detail": score_summary},
                "check3_analyst_coverage": {"pass": c3,
                    "analyst_count": grade_summary.get("analyst_count"),
                    "downgrades_last5": grade_summary.get("downgrades_last5")},
                "check4_price_target": {"pass": c4, "detail": pt_summary},
                "check5_news": {"pass": c5, "detail": news_scan}
            }
        }
    }


@app.get("/vet")
async def vet(symbol: str = Query(...)):
    sym = symbol.upper()
    async with httpx.AsyncClient() as client:
        insider_r, score_r, grades_r, pt_r, news_r, quote_r = await asyncio.gather(
            fmp(client, "/insider-trading/statistics", {"symbol": sym}),
            fmp(client, "/financial-scores", {"symbol": sym}),
            fmp(client, "/grades", {"symbol": sym, "limit": 20}),
            fmp(client, "/price-target-summary", {"symbol": sym}),
            fmp(client, "/news/stock", {"tickers": sym, "limit": 20}),
            fmp(client, "/quote", {"symbol": sym}),
        )

    q = first(quote_r)
    current_price = q.get("price", 0) or 0

    insider_summary = agg_insider(insider_r if isinstance(insider_r, list) else [])
    check1_pass = not insider_summary.get("kill_flag", False)

    sc = first(score_r)
    score_detail = {}
    check2_pass = True
    if sc and "altmanZScore" in sc:
        z, f = sc.get("altmanZScore"), sc.get("piotroskiScore")
        check2_pass = not (z and z < 1.8 and f is not None and f <= 2)
        score_detail = {"altman_z": z, "piotroski_f": f,
                        "z_zone": "DISTRESS" if z and z < 1.8 else "GREY" if z and z < 3 else "SAFE"}

    grade_detail = {}
    check3_pass = True
    if isinstance(grades_r, list) and grades_r:
        count = len(set(g.get("gradingCompany", "") for g in grades_r))
        recent5 = grades_r[:5]
        downs = sum(1 for g in recent5 if g.get("action") == "downgraded")
        check3_pass = count <= 8 and downs < 2
        grade_detail = {"analyst_count": count, "downgrades_last5": downs,
                        "recent": [{"company": g.get("gradingCompany"), "grade": g.get("newGrade"),
                                    "action": g.get("action")} for g in recent5[:3]]}

    pt_detail = {}
    check4_pass = True
    pt = first(pt_r)
    if pt and "lastMonthAvgPriceTarget" in pt:
        avg_pt = pt.get("lastMonthAvgPriceTarget") or pt.get("lastQuarterAvgPriceTarget")
        check4_pass = not (avg_pt and current_price >= avg_pt)
        upside = round(((avg_pt - current_price) / current_price) * 100, 1) if avg_pt and current_price else None
        pt_detail = {"avg_pt": avg_pt, "current_price": current_price,
                     "implied_upside_pct": upside, "above_target": not check4_pass}

    news_articles = [a for a in (news_r if isinstance(news_r, list) else [])
                     if a.get("symbol", "").upper() == sym]
    if not news_articles and isinstance(news_r, list):
        news_articles = news_r
    news_scan = scan_news(news_articles)

    kills = []
    if not check1_pass: kills.append(f"check1_insider: Net sellers {insider_summary.get('sell_pct')}%")
    if not check2_pass: kills.append("check2_balance_sheet: Z<1.8 AND F≤2")
    if not check3_pass: kills.append(f"check3_analyst: {grade_detail.get('analyst_count')} analysts or 2+ downgrades")
    if not check4_pass: kills.append("check4_price_target: Price at or above PT")
    if not news_scan["pass"]:
        kills.append(f"check5_news: '{news_scan['flags'][0]['keyword']}' — {news_scan['flags'][0]['headline'][:60]}")

    return {
        "symbol": sym, "timestamp": datetime.utcnow().isoformat(),
        "price": current_price,
        "overall": "PASS" if not kills else f"KILL — {kills[0]}",
        "kills": kills,
        "checks": {
            "check1_insider": {"pass": check1_pass, "detail": insider_summary},
            "check2_balance_sheet": {"pass": check2_pass, "detail": score_detail},
            "check3_analyst_coverage": {"pass": check3_pass, "detail": grade_detail},
            "check4_price_target": {"pass": check4_pass, "detail": pt_detail},
            "check5_news": {"pass": news_scan["pass"], "flags": news_scan.get("flags", [])},
            "check6_spec_gap": {"pass": None, "note": "Manual — Claude handles via web search"}
        }
    }


@app.get("/scan")
async def scan(symbols: str = Query(...)):
    tickers = [s.strip().upper() for s in symbols.split(",")]
    async with httpx.AsyncClient() as client:
        q_tasks = [fmp(client, "/quote", {"symbol": t}) for t in tickers]
        r_tasks = [fmp(client, "/technical-indicators/rsi",
                       {"symbol": t, "periodLength": 14, "timeframe": "1day", "limit": 3})
                   for t in tickers]
        all_r = await asyncio.gather(*q_tasks, *r_tasks, return_exceptions=True)

    q_results, rsi_results = all_r[:len(tickers)], all_r[len(tickers):]
    output = {}
    for i, t in enumerate(tickers):
        q = first(q_results[i])
        rsi_d = rsi_results[i]
        rsi = round(float(rsi_d[0].get("rsi", 0)), 1) if isinstance(rsi_d, list) and rsi_d else None
        vol = q.get("volume", 0) or 0
        avg_vol = q.get("averageVolume", 0) or 0
        vol_ratio = round(vol / avg_vol, 2) if avg_vol > 0 else None
        output[t] = {
            "price": q.get("price"), "change_pct": q.get("changePercentage"),
            "day_range": f"{q.get('dayLow')}–{q.get('dayHigh')}",
            "year_range": f"{q.get('yearLow')}–{q.get('yearHigh')}",
            "volume": vol, "avg_volume": avg_vol, "volume_ratio": vol_ratio,
            "volume_signal": ("HIGH" if vol_ratio and vol_ratio > 1.5
                              else "LOW" if vol_ratio and vol_ratio < 0.5 else "NORMAL"),
            "market_cap": q.get("marketCap"), "rsi": rsi,
            "rsi_signal": ("OVERSOLD" if rsi and rsi < 30 else "OVERBOUGHT" if rsi and rsi > 70
                           else "NEUTRAL" if rsi else "N/A")
        }
    return {"timestamp": datetime.utcnow().isoformat(), "count": len(tickers), "data": output}


@app.get("/watchlist")
async def watchlist():
    """Live watchlist — zones and metadata fetched from GitHub Gist, prices from FMP."""
    wl_data = await fetch_watchlist_data()

    if "error" in wl_data:
        return {"error": f"Could not fetch watchlist from Gist: {wl_data['error']}"}

    tickers_meta = wl_data.get("tickers", {})
    tickers = [t for t in tickers_meta.keys() if tickers_meta[t].get("z1") or tickers_meta[t].get("notes") != "TBD-AV"]

    if not tickers:
        return {"error": "No tickers found in Gist", "raw": wl_data}

    async with httpx.AsyncClient() as client:
        q_tasks = [fmp(client, "/quote", {"symbol": t}) for t in tickers]
        r_tasks = [fmp(client, "/technical-indicators/rsi",
                       {"symbol": t, "periodLength": 14, "timeframe": "1day", "limit": 3})
                   for t in tickers]
        all_r = await asyncio.gather(*q_tasks, *r_tasks, return_exceptions=True)

    q_results, rsi_results = all_r[:len(tickers)], all_r[len(tickers):]
    output = {}

    for i, t in enumerate(tickers):
        q = first(q_results[i])
        price = q.get("price")
        rsi_d = rsi_results[i]
        rsi = round(float(rsi_d[0].get("rsi", 0)), 1) if isinstance(rsi_d, list) and rsi_d else None

        meta = tickers_meta.get(t, {})
        z1 = meta.get("z1")
        z2 = meta.get("z2")
        stop = meta.get("stop")
        t1 = meta.get("t1")
        t2 = meta.get("t2")

        in_z1 = bool(z1 and price and z1[0] <= price <= z1[1])
        below_z1 = bool(z1 and price and price < z1[0])
        at_z2 = bool(z2 and price and price >= z2)

        if in_z1:
            status = "🟢 Z1 IN ZONE — full size entry"
        elif at_z2:
            status = "🔵 Z2 BREAKOUT — half size, confirm volume"
        elif below_z1:
            status = "⬇️ BELOW Z1 — wait"
        elif z1 and price and price > z1[1]:
            status = "⬆️ ABOVE Z1 — watch for Z2 coil"
        else:
            status = "TBD — AV pending"

        output[t] = {
            "price": price,
            "change_pct": q.get("changePercentage"),
            "rsi": rsi,
            "rsi_signal": ("OVERSOLD" if rsi and rsi < 30 else "OVERBOUGHT" if rsi and rsi > 70
                           else "NEUTRAL" if rsi else "N/A"),
            "z1_entry": f"${z1[0]}–${z1[1]}" if z1 else "TBD-AV",
            "z2_trigger": f"${z2}+" if z2 else "none",
            "stop": f"${stop}" if stop else "TBD",
            "t1": f"${t1}" if t1 else "TBD",
            "t2": f"${t2}" if t2 else "TBD",
            "tier": meta.get("tier", "TBD"),
            "notes": meta.get("notes", ""),
            "in_z1": in_z1,
            "at_z2": at_z2,
            "status": status
        }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "gist_updated": wl_data.get("updated", "unknown"),
        "z1_in_zone": sum(1 for v in output.values() if v.get("in_z1")),
        "z2_breakout": sum(1 for v in output.values() if v.get("at_z2")),
        "watchlist": output
    }
