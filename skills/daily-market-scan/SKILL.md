---
name: daily-market-scan
description: >
  Execute this skill every morning when the user asks for a daily scan, morning report, 
  market update, or says "run morning scan", "what should I look at today", "any opportunities today", 
  or anything suggesting they want a proactive daily market intelligence briefing. Also triggers 
  when the user asks if any existing positions should be moved between tiers or if a holding 
  belongs somewhere else. This skill combines portfolio monitoring with active opportunity hunting 
  across three investment tiers — Tier 1 (Roth/aggressive), Tier 2 (Taxable/long term), 
  Tier 3 (IRA/Simple/steady 8-15%). ALWAYS run this skill proactively and completely — 
  never give a partial scan. The user's goal is to wake up to actionable intelligence, 
  not a summary of what they already know.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from FMP REST API first.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This is your Railway-hosted FMP service — always available on Desktop and Mobile, no API key needed in the URL. Do NOT use Robinhood, search snippets, memory, or earlier conversation prices — those go stale within minutes.

**Fallback order if FMP returns no data:**
1. FMP REST API (primary — always use first)
2. Robinhood `https://robinhood.com/us/en/stocks/TICKER` (fallback only)
3. Web search (last resort only)

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---



# Daily Market Scan Skill

## Core Philosophy
This scan exists for one reason — to find things the user should act on today before the market moves. Every output must be actionable. No filler. No generic market commentary. If there's nothing worth flagging in a tier, say so in one sentence and move on. The highest value this skill delivers is the thing the user didn't know to look for.

The user has explicitly said: "I want to wake up to you telling me I'm an idiot if I don't invest in something." That is the standard. Meet it.

---

## ⚠️ MACRO VOLATILITY CIRCUIT BREAKER — CHECK FIRST EVERY MORNING

**Before running any part of this scan, check these two conditions:**

**Condition 1 — VIX Level:**
Fetch VIX via `FMP:quote` batch-quote-short on `^VIX`.

**Condition 2 — S&P 500 vs 200-Day Moving Average:**
Fetch SPY price and 200 DMA via `FMP:technicalIndicators` endpoint `sma` with period=200.

**CIRCUIT BREAKER TRIGGERS (either condition alone activates it):**
- VIX above 25 AND sustained (not a single intraday spike — check if it closed above 25 yesterday)
- S&P 500 more than 5% below its 200-day moving average

**WHEN CIRCUIT BREAKER IS ACTIVE:**
🔴 CAPITAL PRESERVATION MODE — display this prominently at the top of the scan output.
- Suspend ALL automated Tier 1 and Tier 2 buying triggers
- Suspend afternoon options chasing
- Suspend the Simple IRA "down 1% deployment" trigger
- Suspend all insider buying signals as entry triggers
- ONLY action allowed: trimming positions that hit stop-losses
- ONLY exception: a position already in the portfolio that has a hard stop — honor the stop
- Cash is an active position in this regime, not a drag

**When circuit breaker clears** (VIX sustains below 22 for 3 consecutive days AND S&P back
above 200 DMA): resume normal scan protocols. Note the resumption explicitly.

**Why this exists:** In a macro shock, correlation-to-1 environment, or liquidity cascade,
fundamentals do not matter. Quality Tier 2 compounders get sold at the same velocity as
speculative Tier 1 names because multi-strat funds meet margin calls by selling everything.
The "down 1% buy" rule will bleed the Simple IRA cash dry catching falling knives if this
circuit breaker doesn't exist. In March 2020 and August 2024, this rule would have saved
significant capital. Cash at the bottom of a macro crash is the most valuable asset you own.

---

## Primary Data Source: FMP MCP

**FMP is the first call for any price, quote, earnings, analyst, or insider data.** Do not web search for data FMP can provide.

Key FMP tools for the morning scan:
| Need | FMP Tool | Endpoint |
|------|----------|----------|
| Live prices (batch) | `FMP:quote` | `batch-quote-short` |
| Index levels | `FMP:indexes` | `index-quote` |
| Commodities (gold, oil, silver) | `FMP:commodity` | `commodities-quote` |
| Bitcoin | `FMP:crypto` | `cryptocurrency-quote` |
| Earnings this week | `FMP:calendar` | `earnings-calendar` |
| Analyst upgrades/downgrades | `FMP:analyst` | `price-target-analyst-company` |
| Insider buys (last 48hr) | `FMP:insiderTrades` | `insider-trades` |
| RSI, MACD on holdings | `FMP:technicalIndicators` | `rsi`, `macd` |
| News on specific ticker | `FMP:news` | `stock-news` |

Web search handles: options flow (unusualwhales, barchart), FDA dates, macro narrative, government contracts.

---

## The Three Tier System

**TIER 1 — Roth IRA — Aggressive/Boom or Bust**
Short to medium term. Binary events. High conviction momentum plays. Tax free gains forever.
- Deploy from: Roth SPAXX (~$8,800 available)
- Holding period: Days to months
- Risk tolerance: Can go to zero
- Examples: FDA decisions, earnings catalysts, unusual options activity, short squeezes, government contract wins, technical breakouts, emerging themes

**TIER 2 — Taxable Account — Long Term Growth**
Quality compounders. ETFs with strong thesis. Sector rotation plays. 2-5 year horizon.
- Deploy from: Taxable SPAXX or proceeds from sales
- Holding period: Years
- Risk tolerance: Volatility acceptable, permanent loss is not
- Examples: Quality individual stocks on dip, thematic ETFs with strong flows, sector rotation opportunities, international plays

**TIER 3 — Traditional IRA & Simple IRA — Steady 8-15% Annual Growth**
Boring is beautiful. Consistent compounding. No lottery tickets.
- Deploy from: IRA/Simple cash positions
- Holding period: Long term, retirement horizon
- Risk tolerance: Low — consistent returns only
- Examples: Dividend growers, low volatility quality ETFs, income generators, proven long term compounders

---

## Morning Scan Execution Order

Run ALL of the following steps every time. Do not skip steps. Do not abbreviate.

**TIMING DISCIPLINE — TWO PHASES:**

**Phase A — Operational (9:45 AM):** Steps 1–3 + Step 7. Risk management,
stops, earnings reactions, existing position alerts. Time-sensitive — act now
if needed. The first 30–45 minutes of the cash session are dominated by retail
order imbalances and overnight algorithms. New entry opportunities identified
at 9:45 AM frequently gap up and fade by noon. Do NOT present new entries as
"act right now" unless conviction is 9+/10 and the pre-market setup already
confirmed the move.

**Phase B — Opportunity Vetting (11:30 AM or 3:15 PM):** Steps 4–6. New entry
opportunities for Tier 1, Tier 2, and Tier 3. Present with timing note:
"Entry: Wait for 10:30 AM open confirmation" (Tier 1) or "Entry: 11:30 AM or
later — let morning noise clear" (Tier 2). Tier 3 IRA/Simple has no timing
constraint.

**Exception:** A pre-market confirmed move (stock already up/down 5%+ before
open with a real catalyst and 9+/10 conviction) can be flagged as immediate
at 9:45 AM. State explicitly: "Pre-market confirmed — entry timing is now."

---

### STEP 1 — Pre-Market Context (run first, frames everything else)

**PRIMARY: Use FMP MCP tools to pull live market data first — before any web search.**

Pull these via FMP in a single batch:
- `FMP:indexes` endpoint `index-quote` for SPY, QQQ, DIA (futures direction proxy)
- `FMP:commodity` endpoint `commodities-quote` for GCUSD (gold), SIUSD (silver), CLUSD (crude oil)
- `FMP:crypto` endpoint `cryptocurrency-quote` for BTCUSD
- `FMP:quote` endpoint `batch-quote-short` for TLT (10yr Treasury proxy), UUP (dollar index proxy)

Then supplement with web search for:
- Overnight news that moves markets (Fed, geopolitical, earnings)
- Any context that FMP data alone doesn't explain (why oil is moving, Fed commentary, etc.)

### STEP 1B — Live Technical & Flow Data (fetch these sources directly every morning)

**Full Market MACD Crossovers — fetch these URLs:**

Primary: https://stockanalysis.com/screener/stocks/?p=annual&column=macd&order=desc
This surfaces stocks with bullish MACD momentum sorted by signal strength across the full market.

Secondary: https://www.stockmonitor.com/stock-screener/macd-cross-and-rsi-above-55/
Stocks with MACD bullish cross AND RSI above 55 — double confirmation filter.

**Golden Cross — 50 DMA crossing above 200 DMA:**
https://www.stockmonitor.com/stock-screener/golden-cross-50ma-cross-up-200ma/
Full market scan for golden crosses. Check top 20 results for anything with earnings catalyst or unusual options activity layered on top.

**52-Week Highs on Volume:**
https://stockanalysis.com/stocks/screener/?p=quarterly&column=change&order=desc&f=price-over-52w-high
Stocks breaking to new highs today. Cross-reference with volume surge.

**Unusual Options Activity — fetch this URL every morning:**
https://unusualwhales.com/flow
Also fetch: https://barchart.com/options/unusual-activity/most-active

From these feeds, extract the TOP 3 most interesting names based on:
- Call volume 3x+ average in last 24 hours
- Large single block trades (sweeps) — smart money, not retail
- Out-of-the-money calls with near-term expiry — directional bet, not hedging
- Sector alignment with current macro (defense, AI, energy = higher priority)

For each of the top 3, present in the scan output:
TICKER | What the flow looks like | Why it's interesting | "Run AV on [TICKER] to score"

This is the single highest-value daily intelligence feed. Treat it as the lead item in Tier 1 opportunity hunting. A name with unusual call flow that ALSO has a technical setup or catalyst is an immediate Tier 1 candidate. Flag it prominently and explicitly prompt the user to run AV conviction on any name worth pursuing.

**Insider Buying Filed Last 48 Hours:**
https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=2&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=500&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc=&sortcol=0&cnt=20&page=1
Purchases over $500K filed in last 48 hours only.

**StockAnalysis Earnings Revisions:**
Search "[TICKER] earnings estimate revisions" on stockanalysis.com for any holdings with earnings in next 7 days.

**IMPORTANT — These fetches cover the FULL MARKET:**
StockMonitor and StockAnalysis screeners scan all US-listed securities, not just names already in the news. This is the difference between finding something before it moves vs after analysts are already writing about it. Always fetch these URLs first before doing any keyword searches.

### STEP 1C — Pre-Earnings Radar (run every morning — this is how we avoid the CEG problem)

**The CEG Rule:** On May 11, 2026, Constellation Energy reported a massive earnings beat.
The setup was completely knowable 3-4 weeks earlier (20/21 analysts bullish, stock down 13%
from highs, Calpine integration "show me" moment, EPS estimates revised up). It was surfaced
on earnings day — too late. This section exists so that never happens again.

Every morning, check the earnings calendar for stocks with earnings 15-45 days out that
score 5+/7 on the Pre-Earnings Setup Screen. Surface the top 1-2 names in the output.

**The 7-Point Pre-Earnings Setup Screen (score each signal 1=pass, 0=fail):**

| Signal | Check |
|--------|-------|
| 1. Earnings 15-45 days out | Exact date required |
| 2. Stock down 8-25% from 52wk high | The dip entry |
| 3. 75%+ analysts Buy + 15%+ avg upside | Analyst conviction |
| 4. EPS estimates revised UP by 2+ analysts in last 30 days | Momentum |
| 5. Options implying 5%+ move on earnings | Market knows something |
| 6. Specific "show me" catalyst on the call | Not just "might beat" |
| 7. Sector getting institutional inflows / macro tailwind | Wind at back |

**Score threshold:**
- 7/7 or 6/7 → Flag immediately as pre-earnings buy in the output
- 5/7 → Flag as watchlist with entry price
- Below 5/7 → Skip

**THE GARY RULE — MANDATORY SECTOR ROTATION:**
Added May 11, 2026 after the radar repeatedly anchored on defense stocks due to
prior conversation context. Every pre-earnings scan MUST rotate through all 11 sectors
before surfacing candidates. Anchoring to one or two sectors because they were discussed
recently is a failure state — Gary's question was "why is everything defense?" and the
answer was bias, not analysis.

Before outputting any name, confirm candidates were evaluated across:
Energy | Materials | Industrials | Consumer Discretionary | Consumer Staples |
Healthcare | Financials | Info Technology | Communication Services | Utilities | Real Estate

**Software/SaaS exclusion — NARROWED:** Exclude pre-revenue or money-losing software/SaaS only.
A profitable software company with positive TTM net income, FCF margin >20%, and PEG <2.0
is NOT excluded — it is a quality compounder that deserves evaluation. The original ban
targeted narrative-driven, multiple-compression risk; that risk lives in unprofitable software,
not in proven cash-generating software businesses. Physical products, chips, devices,
infrastructure, and hard assets remain the primary hunting ground, but do not auto-reject
a profitable software name that passes the valuation gate.

Self-check: Did you look at names from at least 6 different sectors this run?
If not, expand the scan before outputting anything.

**How to execute daily:**
- Use FMP:calendar "earnings-calendar" for next 45 days, filter to 15-45 day window
- Evaluate candidates across ALL 11 sectors (see Gary Rule above)
- Price filter: under $300 (Gary's actionability threshold)
- Cross-reference any name scoring 5+/7 against the restricted entities list
- Check if portfolio already has exposure (flag redundancy)
- Present in the PRE-EARNINGS RADAR section of output (see format below)
- If the Sunday Pre-Earnings Radar has already identified active setups, carry them
  forward in the morning scan daily until the entry window closes (7 days before earnings)

**Entry window language:**
- 15-45 days out: "OPEN — clean entry window"
- 8-14 days out: "NARROWING — IV starting to rise"
- 7 days out: "⚠️ ENTRY WINDOW CLOSING — last clean entry before IV gets expensive"
- Under 7 days: "CLOSED — hold if in, avoid new entry"

### STEP 2 — Portfolio Watch (existing positions)

**Use FMP first for live price data:**
- `FMP:quote` endpoint `batch-quote` with all current holdings — pull price, change%, volume in one call
- Flag any position with change% of ±5% or more immediately
- Use `FMP:quote` endpoint `quote` for deeper single-stock detail when flagging a specific name

Then for each position flagged by FMP data, follow up with web search for:
- Any position with overnight news (earnings, FDA, contract, upgrade/downgrade)
- Any position down 5%+ pre-market — explain why
- Any position up 5%+ pre-market — is it a sell opportunity or let it run?
- Any position that has crossed its 50 DMA or 200 DMA overnight
- Any position approaching a stop-loss level (down 20%+ from entry)
- Any position whose TIER classification should change based on new information

**Tier Misalignment Check:**
Ask this question for every holding: "Does this position still belong in this tier, or has something changed that warrants moving it?" Flag any misalignment explicitly.

### STEP 3 — Earnings & Catalyst Calendar

**Use FMP first:**
- `FMP:calendar` endpoint `earnings-calendar` to pull the next 7 days of earnings — filter for any holdings
- `FMP:calendar` endpoint `economic-calendar` for key macro events (CPI, jobs, Fed)

Then supplement with web search for FDA PDUFA dates and government contract announcements.

### STEP 4 — Tier 1 Opportunity Scan (most important)
Search aggressively for Tier 1 opportunities using these triggers in priority order:

**Primary Triggers (flag if any one of these fires):**
1. Unusual options call activity — volume 3x+ average in last 24 hours
2. Insider buying filed via Form 4 in last 48 hours — $500K+ only, cite exact filing date
3. Stock crossing above 50 DMA or 200 DMA on above-average volume
4. FDA PDUFA decision within 14 days on a small/mid cap biotech
5. Earnings in next 7 days with BULLISH estimate revision trend — 60%+ of analysts raised estimates in last 30 days. This is the FLY signal. Search "[TICKER] earnings estimate revisions" for every holding with earnings in next 7 days EVERY MORNING. Flag any with bullish revision trend as pre-earnings buy opportunity.
6. Short interest above 15% with a positive catalyst emerging
7. Government contract win announced in defense, aerospace, tech
8. Clinical trial Phase 3 data announcement or top-line results
9. Takeover/acquisition rumor or activist investor disclosed
10. Stock gapping up on volume after extended consolidation
11. Earnings in next 7 days with BEARISH estimate revision trend — flag as warning, do not add before the print

**Confirmation Signals (use to validate primary trigger):**
- RSI below 50 (room to run) or breaking out from oversold
- MACD crossover happening now AND histogram widening — momentum building confirms entry
- MACD bearish divergence present — reduces conviction score by 1 even if primary trigger fires
- Volume 2x+ average on the breakout day
- Analyst upgrade in last 48 hours
- Positive estimate revision in last 30 days

**For each Tier 1 opportunity found, pull live data from FMP before presenting:**
- `FMP:quote` endpoint `quote` — current price, 52wk high/low, volume
- `FMP:analyst` endpoint `analyst-estimates` — consensus target and rating
- `FMP:insiderTrades` endpoint `insider-trades` — check for recent insider buys (last 7 days only)
- Then provide:
- What triggered the flag
- Current price and 52-week range
- Catalyst and timeline
- Analyst consensus and price target
- Options market implied move if applicable
- Insider filing date if applicable (NEVER flag insider buying older than 1 week)
- Honest risk — what kills this trade
- Conviction score (1-10) using the scale below
- Verdict: One sentence. Make it count.

**CONVICTION SCORING SCALE:**

Score 9-10 — MAXIMUM CONVICTION
Multiple primary triggers firing simultaneously. Unusual options activity AND insider buying AND earnings/FDA catalyst AND technical breakout all converging. This combination is rare. When it happens, it's the "you'd be an idiot not to act" moment. Meaningful Roth position warranted.

Score 7-8 — HIGH CONVICTION  
Two or more primary triggers confirmed by supporting signals. Clear catalyst with defined timeline. High confidence setup where the risk/reward is clearly skewed in your favor. Solid Roth position warranted.

Score 5-6 — MODERATE CONVICTION
One strong primary trigger with some confirmation signals. Good setup but missing a piece — maybe the catalyst is unclear or the timing is uncertain. Worth a smaller position. Watch closely for additional confirmation.

Score 3-4 — LOW CONVICTION
Interesting thesis but only one weak signal or timing is too uncertain. Watchlist candidate only. Set an alert and wait for more confirmation before deploying capital.

Score 1-2 — MONITOR ONLY
Early stage idea with minimal signal strength. Too speculative even for Roth at this stage. Keep watching but do not act yet.

**SCORING RULES:**
- Never give a 9-10 unless at least 3 primary triggers are firing simultaneously
- Never give a 7-8 without at least 2 confirmed primary triggers
- Always show which triggers contributed to the score
- A high conviction score on a stock that has already run 25%+ gets automatically capped at 6 — chasing momentum is not high conviction
- Insider buying alone is never above a 5 — it needs confirmation
- Unusual options activity alone is never above a 6 — it needs a catalyst to confirm

### STEP 5 — Tier 2 Opportunity Scan
Search for long term additions to taxable account:
- Sector rotation signals — which sectors are getting institutional inflows this week
- Quality stocks trading below 5-year average P/E with analyst upgrades
- ETFs with 3+ year track record beating S&P with positive flows last 30 days
- International markets showing sustained outperformance with positive macro tailwind
- Thematic ETFs aligned with portfolio mega-trends showing momentum

**MANDATORY TIER 2 VALUATION GATE:**
Every individual stock flagged for Tier 2 taxable MUST pass the valuation gate before
being recommended. Calculate PEG ratio and FCF yield. If PEG is above 3.0, redirect
to Tier 1 Roth instead. Never recommend an overvalued stock for the taxable account
regardless of how compelling the thesis sounds. The taxable account is for VALUE with
growth — not hope with growth.

The Palantir rule: If a stock has a PEG above 5.0, it is Tier 1 Roth only or avoid.
Always ask: "Is there still value built into this stock at the current price?"

**For each Tier 2 opportunity found, provide:**
- Long term thesis in 2 sentences
- YTD vs S&P performance
- 3 and 5 year track record
- Fund flows — money coming in or going out
- Suggested basket home or standalone
- Verdict: Worth building a position now or wait?

### STEP 6 — Tier 3 Opportunity Scan
Search for steady compounders for IRA/Simple:
- ETFs with consistent 8-15% annualized returns over 10 years
- Dividend growth stocks with 10+ year track record and recent dip
- Low volatility quality factor ETFs with strong long term flows
- Income generators with sustainable yield above 3%

**For each Tier 3 opportunity found, provide:**
- 10-year annualized return
- Dividend yield and growth rate
- Expense ratio
- Max drawdown — how bad does it get in a crash
- Verdict: Does it fit the 8-15% mandate or not?

### STEP 7 — Sell Signal Review (Roth positions only)
Every morning check ALL existing Roth Tier 1 positions against the sell framework below. This runs every day without exception — gains evaporate fast in boom or bust names.

**SELL SIGNAL FRAMEWORK:**

**Take Profits:**
- Position up 30%+ AND conviction score has dropped since entry → Sell half
- Position up 50%+ regardless of conviction → Flag for review, raise stop loss
- Original catalyst has fully played out with no new catalyst emerging → Sell all
- Options implied volatility collapsing after a big move — smart money exiting → Sell half
- Analyst consensus price target reached or exceeded → Flag, reassess thesis
- Insider selling Form 4 filed after you bought → Immediate review, likely sell

**Cut Losses:**
- Position down 20% from entry → Automatic review — is thesis intact or broken?
- Position down 30% from entry → Sell unless there is a specific identifiable reason the thesis is intact and a defined catalyst to recover
- Original catalyst failed, was delayed significantly, or was wrong → Sell all
- Earnings miss that directly contradicts the thesis → Sell all
- FDA rejection or clinical trial failure → Sell all immediately

**Thesis Breaks — Sell Immediately:**
- Company loses key government contract or major partnership
- Competitor announces superior product that makes the thesis obsolete
- Regulatory action or investigation against the company
- Management guidance cut dramatically with no explanation
- The specific reason you bought it no longer exists

**CONVICTION-BASED SELL SCALE:**

| Conviction Change | Action |
|------------------|--------|
| Was 7-8, now 4-5 | Sell half — thesis weakening, protect gains |
| Was 9-10, now 5-6 | Sell half — something changed, de-risk |
| Any score drops to 3 or below | Sell all — thesis broken |
| Score unchanged, up 50%+ | Raise stop loss to 30% below current price |
| Score unchanged, down 20% | Review and decide — document why you're holding |

**SELL OUTPUT FORMAT — add to Portfolio Watch section:**

SELL SIGNAL — [Ticker]
POSITION: Up/Down [X]% from entry
TRIGGER: [Exactly what fired — profit target / loss threshold / thesis break]
CONVICTION NOW: [X/10] vs entry [X/10]
ACTION: [Sell all / Sell half / Raise stop / Hold with reason]
VERDICT: [One sentence — why now]

### STEP 8 — Tax & Portfolio Housekeeping
Flag any of the following:

**STANDING REMINDER — until explicitly told it's complete:**
SIMPLE IRA — ~$83,362 sitting in cash (SPAXX) waiting for deployment.

**DEPLOYMENT TRIGGER — REPLACED:** The old "down 1% today" rule is retired. It was too blunt
and would systematically catch falling knives during a multi-week market downdraft.

**NEW DEPLOYMENT TRIGGER — use this instead (check every morning):**

Pull S&P 500 RSI (14-day) via `FMP:technicalIndicators` endpoint `rsi` on SPY.
Pull S&P 500 price vs 200 DMA via `FMP:technicalIndicators` endpoint `sma` on SPY period=200.

**DEPLOY** when ONE OR MORE of these conditions is met:
- S&P 500 RSI (14-day) crosses below 35 → market is genuinely washed out
- S&P 500 is more than 8% below its 200-day moving average → meaningful dislocation
- VIX spikes above 30 intraday then CLOSES below 25 → fear peak, reversal signal

**DO NOT DEPLOY** on a single down day of 1–3% regardless of how tempting it feels.
A 1% down day in a healthy bull market is noise. A 1% down day in a waterfall is
just the beginning. The RSI and 200 DMA triggers ensure deployment happens when the
market is genuinely oversold, not just having a bad Tuesday.

**CIRCUIT BREAKER OVERRIDE:** If the Macro Volatility Circuit Breaker is active (VIX >25
sustained OR S&P >5% below 200 DMA), ALL deployment is suspended regardless of RSI.
Wait for the circuit breaker to clear before deploying any Simple IRA cash.

- Positions at a loss that could be harvested against known gains
- Wash sale risks if considering a replacement buy
- Basket drift above 5% from target weight
- Auto invest amounts that may need adjustment
- Positions that have grown large enough to consider trimming for concentration risk

---

## Output Format

Use this exact format every morning. No deviation.

```
═══════════════════════════════════════════
GOOD MORNING — DAILY MARKET SCAN
[Day, Date] | Markets open in [X] minutes
═══════════════════════════════════════════

MACRO CONTEXT
[3 bullet points max — only what moves the needle today]
• Futures: [direction and magnitude]
• Key overnight: [one sentence on most important news]
• Watch: [one specific thing that affects this portfolio today]

═══════════════════════════════════════════
PORTFOLIO WATCH ⚠️
═══════════════════════════════════════════
[List only positions with something worth flagging]
[If nothing to flag: "All positions quiet overnight — no action needed."]

SELL SIGNALS:
[Any Roth position triggering a sell signal — use sell output format]
[If none: "No sell signals today."]

TIER MISALIGNMENT FLAG:
[Any position that should move tiers — or "None identified today"]

═══════════════════════════════════════════
EARNINGS & CATALYSTS THIS WEEK 📅
═══════════════════════════════════════════
[List any holdings reporting with date, consensus EPS, implied move]
[If none: "No earnings for holdings this week."]

═══════════════════════════════════════════
UNUSUAL OPTIONS FLOW 🎯
═══════════════════════════════════════════
[Top 3 names from unusualwhales.com/flow and barchart unusual activity]

1. [TICKER] — [What the flow looks like in plain English] | [Why it's interesting — catalyst, sector, size] | → Run AV on [TICKER] to score
2. [TICKER] — [same format]
3. [TICKER] — [same format]

[If flow is all noise/hedging with no clear directional conviction: "Options flow today is mixed — no high-conviction directional bets worth surfacing."]

═══════════════════════════════════════════
TIER 1 — ROTH OPPORTUNITY 🔴
═══════════════════════════════════════════
[If opportunity found:]
NAME: [Ticker — Company Name]
TRIGGER: [Exactly what fired — be specific, list each signal]
PRICE: $[X] | 52-week range: $[low]-$[high]
CATALYST: [What happens and when]
ANALYST TARGET: $[X] ([X]% upside) | Consensus: [Buy/Hold/Sell]
OPTIONS SIGNAL: [If applicable]
INSIDER: [Filing date + amount — ONLY if within 7 days]
RISK: [One sentence — what kills this]
CONVICTION: [X/10] — [One sentence explaining the score and which triggers fired]
VERDICT: [One sentence. Make it count. This is the "you'd be an idiot" moment.]

[If no opportunity: "No Tier 1 setup meets the standard today. Wait for the right pitch."]

═══════════════════════════════════════════
TIER 2 — TAXABLE OPPORTUNITY 🟡
═══════════════════════════════════════════
[If opportunity found:]
NAME: [Ticker — Name]
THESIS: [2 sentences max]
YTD: [X]% vs S&P [X]%
TRACK RECORD: 3yr [X]% | 5yr [X]%
FLOWS: [Inflows or outflows — amount]
VALUATION GATE: PEG [X] — [CHEAP/FAIR/PREMIUM/TIER 1 ONLY] | FCF Yield [X]%
VALUE BUILT IN: [Yes — room to grow / No — priced for perfection]
HOME: [Which basket or standalone]
VERDICT: [Build now or wait — one sentence]

[If PEG above 3.0]: ⚠️ VALUATION WARNING — Redirect to Tier 1 Roth only.
Too expensive for taxable account long term hold.

[If no opportunity: "No Tier 2 additions warranted today."]

═══════════════════════════════════════════
TIER 3 — IRA/SIMPLE OPPORTUNITY 🟢
═══════════════════════════════════════════
[If opportunity found:]
NAME: [Ticker — Name]
10-YEAR RETURN: [X]% annualized
YIELD: [X]% | Growth rate: [X]% annually
EXPENSE RATIO: [X]%
MAX DRAWDOWN: [X]%
VERDICT: [Fits 8-15% mandate or doesn't — one sentence]

[If no opportunity: "No Tier 3 additions warranted today."]

═══════════════════════════════════════════
PRE-EARNINGS RADAR 📡
═══════════════════════════════════════════
[The CEG Rule in action — setups 15-45 days before earnings, not on earnings day]

[If active setup found:]
NAME: [TICKER — Company Name]
EARNINGS: [Date] — [X] days away | Entry window: [OPEN/NARROWING/CLOSING]
SCORE: [X]/7
SIGNALS: ✅/❌ Dip ([X]% off high) | ✅/❌ Analysts ([X]% Buy, $[X] target) | ✅/❌ Revisions ([up/down]) | ✅/❌ Implied move ([X]%) | ✅/❌ Show-me catalyst ([one phrase]) | ✅/❌ Sector tailwind
TIER: [1/2/3] | ENTRY: $[X] | STOP: $[X] | TARGET: $[X]
VERDICT: [One sentence — why now, not on earnings day]

[If no active setups scoring 5+/7:]
"No pre-earnings setups score 5+/7 today. Clean slate — check Sunday's radar for the week's candidates."

[If existing setup from Sunday radar is still active, carry it forward with updated days-until count]

═══════════════════════════════════════════
HOUSEKEEPING 🔧
═══════════════════════════════════════════
💰 SIMPLE IRA CASH — ~$83,362 AWAITING DEPLOYMENT
DEPLOYMENT CHECK: S&P RSI [X] | SPY vs 200 DMA: [X]% [above/below]
[If RSI <35 OR SPY >8% below 200 DMA AND circuit breaker NOT active]:
🚨 DEPLOYMENT SIGNAL ACTIVE — [specific condition met].
Consider deploying $[X] into [specific positions] in the Simple IRA.
[If conditions not met]: Holding. RSI [X] (need <35) | [X]% from 200 DMA (need >8% below).
Wait for genuine washout, not just a bad day.
[If circuit breaker active]: 🔴 CIRCUIT BREAKER ACTIVE — no deployment until VIX clears.

[All other housekeeping items below]

═══════════════════════════════════════════
BOTTOM LINE
═══════════════════════════════════════════
[3 sentences max. What matters most today. What to act on. What to ignore.]
═══════════════════════════════════════════
```

---

## Critical Rules

1. **Never flag insider buying older than 7 days** — always cite the exact Form 4 filing date
2. **Never recommend a Tier 1 play without checking the 30-day price forecast first** — don't send someone into a stock that's already run 30%+ with no catalyst remaining
3. **Never flag a Tier 2 ETF with sustained outflows** — money leaving is a red flag always
4. **Never use generic risk disclaimers** — only flag risks that are specific and data-backed to this position today
5. **Always compare any opportunity to S&P 500 YTD** — if it's underperforming the S&P with no clear catalyst for change, don't flag it
6. **Always check if a Tier 1 opportunity overlaps with an existing Roth position** — flag redundancy before recommending
7. **The bottom line must contain at least one specific action** — not "watch the market" but "buy X at open" or "wait for Y to pull back to Z before entering"
8. **If there is genuinely nothing worth acting on today, say so clearly** — "No actionable setups today" is a valid and valuable output. Do not manufacture opportunities.
9. **The Expedia Rule — apply to all news filtering in this scan:** Before treating any news item as a signal for a position or opportunity, classify it as Level 1 (category-wide impact) or Level 2 (competitive reshuffling within the category). Level 1 news — macro shifts, regulatory changes, total industry data — validates or invalidates the category thesis and is HIGH WEIGHT. Level 2 news — one competitor gaining share from another within a stable category — is LOW WEIGHT for evaluating the category but HIGH WEIGHT for evaluating that specific competitor directly. Do not let Level 2 noise contaminate Level 1 thesis assessment. Example: "Hotel room rates rising across the industry" is Level 1 signal for any hotel-adjacent name. "Marriott gaining share from Hilton" is Level 2 noise for Expedia but Level 1 signal if you're evaluating Marriott specifically.
10. **Check the Macro Volatility Circuit Breaker FIRST** — before any other step. If VIX >25 sustained or S&P >5% below 200 DMA: capital preservation mode, all buying suspended.

---

## Portfolio Reference

Current portfolio structure for context:

**Taxable Baskets:** Technology, Small/Mid Cap ETF, Crypto, Growth Blend, Defense, Healthcare, Critical Materials, AI Power Infrastructure (PowerInfra), Dividends, Bonds, ARK (closing), Financials, Speculative

**Taxable Standalones:** NVDL, QQQ, QQQM, VFMO, AMT, DCOM, FMSDX, CRK, XLE, PSQ, QID, AGNC 200sh, ACHR 200sh, SOUN 200sh, PONY 150sh, RR 100sh, ALAB 57sh, AMD 86sh, AMZN 126sh, ANET 52sh, CRWD 10sh, GOOG 148sh, META 10sh, MSFT 73sh, NOW 12sh, NVDA 228sh, ORCL 20sh, TSM 54sh, OPEN 65sh + warrants, NFLX Jun 18 $90 LONG call (1)

**Roth IRA:** Space basket (RKLB 18.1sh, ASTS 11.1sh, PL 22.2sh, LUNR 31.8sh, RDW 121.6sh). Standalones: NFLX 125sh @$90.38 avg + short Aug21 $110 call (1 contract), MU 4sh, RONB 150sh, CORT 35sh, LWLG 45sh, NSSC 150sh, ARXS 40sh, CIFR 50sh, FLTCF 150sh. SPAXX ~$730.

**Jen's Roth IRA:** VTI 35%, QQQM 25%, VXF 20%, SOXQ 12%, DFAS 8%. Pure growth, 20+ year horizon. Do not touch.

**Traditional IRA (~$456K):** FELC 3,950sh, TRBCX 291.8sh, QQQM 100sh, FMDE 1,000sh, FESM 630sh, FEMR 809.7sh, FENI 675sh, FAGIX 2,862sh, CTHRX 79.2sh, CDDRX 490.6sh. SPAXX ~$11,292. $40K rollover incoming from Principal.

**Simple IRA (~$335K):** FELC 1,613sh, FXAIX 151.9sh, TRBCX 247.5sh, FAGIX 1,256sh, FEMR 192sh, FENI 191.8sh, FESM 347sh, FMDE 586.2sh, QQQM 79.2sh. SPAXX ~$83,362 (~25% cash — deploy on down days).

**Watch for tier misalignment:** Any boom-or-bust name sitting in taxable that belongs in Roth. Any steady compounder sitting in Roth that belongs in IRA.

---

## Scheduling Note

This scan is designed to run at 9:45 AM ET — 15 minutes after market open. This timing captures:
- Pre-market moves and gap ups/downs
- Opening volume confirmation on any breakouts
- First 15 minutes of institutional order flow
- Any last-minute news before full market participation

If running manually, user triggers with: "run morning scan" or "good morning" or "what's the market doing"
