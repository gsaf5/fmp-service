---
name: afternoon-scan
description: >
  Execute this skill when the user asks for an afternoon update, afternoon scan, 
  end of day update, "what happened today", "anything new this afternoon", "3:15 scan",
  "afternoon review", or any request for a mid-to-late day market update. This skill
  runs at 3:15 PM ET — 45 minutes before market close and before the 4 PM mutual fund
  NAV cutoff — giving the user time to act on anything urgent before the bell. It 
  references the morning scan's findings, identifies what developed during the day,
  flags new opportunities from afternoon options activity and news, and builds an
  overnight research queue with priority levels. ALWAYS run this skill completely —
  never give a partial scan. The goal is to give the user 45 minutes of actionable
  intelligence before the market closes.
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



# Afternoon Scan Skill — 3:15 PM ET

## Core Philosophy
The afternoon scan exists for one reason — to catch what the morning scan missed and give the user 45 minutes to act before close. Every output must be actionable. The user is reading this with limited time. Lead with what needs action NOW, follow with what needs research TONIGHT, and close with what carries forward to tomorrow morning.

Key difference from morning scan:
- Morning scan = proactive opportunity hunting before the day starts
- Afternoon scan = reactive intelligence on what developed during the day + new opportunities that emerged

---

## Critical Timing Rules

**4:00 PM ET** — Mutual fund NAV cutoff at Fidelity. Any mutual fund purchase must be placed before 4 PM to receive today's closing price. Flag any mutual fund opportunities with "⏰ BEFORE 4 PM" warning.

**4:00 PM ET** — Market close. Any stock, ETF, or options trade must execute before this.

**3:15 PM** — This scan runs here. User has 45 minutes to act.

Non-Fidelity mutual funds may have different cutoff times. Always note if the fund is non-Fidelity and flag to check the prospectus.

---

## Execution Order

Run ALL steps every time. Do not skip.

### STEP 1 — Morning Scan Recap (30 seconds)
Briefly reference what was flagged in the morning scan:
- What Tier 1, 2, 3 opportunities were flagged this morning
- What conviction scores were assigned
- What actions were recommended
- Which of those played out today (up, down, or sideways)
- Which morning recommendations still stand vs need to be revised

This creates continuity between the two scans so the user sees the full picture.

### STEP 2 — Intraday Market Overview

**Pull live from FMP first — one batch call covers most of this:**
- `FMP:indexes` endpoint `index-quote` for SPX, NDX, DJI — current levels and % change
- `FMP:quote` endpoint `batch-quote-short` for VIX (^VIX), TLT, UUP, BTCUSD, GCUSD, CLUSD
- Use FMP data as the authoritative price source — supplement with web search only for narrative (why it moved)

### STEP 3 — Portfolio Positions Update

**Use FMP batch quote to pull all holdings at once — identify movers before doing any web search:**
- `FMP:quote` endpoint `batch-quote` with current holdings — flag anything ±2%
- For earnings reporters: `FMP:calendar` endpoint `earnings-confirmed` to confirm today's reports
- For earnings details: `FMP:statements` for beat/miss data, then supplement with web search for guidance commentary

For each position that had meaningful intraday movement (2%+ in either direction), flag:
- Current price vs morning open
- Why it moved — earnings, news, sector rotation, macro
- Does the thesis still hold or did something change today
- Any position that triggered a sell signal (see sell signal framework below)

**Earnings Results Review:**
For any holdings that reported TODAY, provide:
- Actual EPS vs estimate (beat/miss/in-line)
- Actual revenue vs estimate
- Guidance raised/lowered/maintained
- Stock reaction and what it means
- Hold/add/trim recommendation with conviction score
- Note: Was the estimate revision trend BULLISH before this print? If yes and they beat, flag that we should have added before. If no and they missed, flag that the revision trend was warning us.

**Earnings Revision Check for Upcoming Prints:**
For any holdings reporting in the next 7 days, run the estimate revision check:
- Search "[TICKER] earnings estimate revisions 30 days" for each upcoming earnings
- Flag any with 60%+ of analysts raising estimates as a pre-earnings buy opportunity
- Flag any with 60%+ of analysts lowering estimates as a warning — do not add before print
- This runs EVERY AFTERNOON for the upcoming week's earnings calendar

### STEP 4 — New Afternoon Options Activity
This is the most time-sensitive section. Search for unusual options activity that developed DURING TODAY'S SESSION that was not present at the morning scan.

Fetch: https://www.schwab.com/learn/story/todays-options-market-update
Search: "unusual options activity today [date]" for any afternoon developments

Look specifically for:
- New call volume spikes 3x+ average that weren't there at open
- Large block trades in names you own or are watching
- Earnings-related positioning in names reporting this week
- Any activity in your specific holdings

For each new options signal found:
- Name the ticker and what fired
- Call or put activity
- Size of the unusual activity (relative volume)
- What it might signal
- Conviction score 1-10 on whether to act before close

### STEP 5 — Analyst Actions During Market Hours
Search for analyst upgrades, downgrades, or price target changes that occurred TODAY:
- Any upgrades or downgrades on positions you own
- New coverage initiations on names you're watching
- Price target raises or cuts on your holdings
- Focus on major firms — Goldman, Morgan Stanley, JPMorgan, BofA, Citi, Barclays, Wells

For each analyst action:
- Who upgraded/downgraded
- New target vs old target
- What it means for the position
- Does it change your conviction score

### STEP 6 — Intraday Technical Developments
Search for:
- Any of your holdings crossing their 50 DMA or 200 DMA TODAY
- Golden cross or death cross formations developing
- Any significant support or resistance levels breached
- RSI moving into overbought (>70) or oversold (<30) territory on holdings
- MACD divergence developing on any holdings — especially on positions you are considering adding to

**MACD Divergence Check — run specifically for:**
1. Any position you are considering adding to — confirm momentum is building not fading
2. Any position that triggered a sell signal — MACD bearish crossover confirms sell
3. Any position up 30%+ where you want to know if the move has more legs

MACD bearish divergence (price new high, MACD lower high) on a position you own = reduce conviction, consider trimming
MACD bullish divergence (price new low, MACD higher low) on a watchlist name = potential entry signal building

For each technical development:
- What crossed or broke
- Direction — bullish or bearish
- Confirmation from volume — above or below average
- Does it support buying more, holding, or trimming

### STEP 7 — Mutual Fund Opportunity Check (⏰ BEFORE 4 PM)
Review IRA/Simple IRA mutual fund positions:
- Any opportunity to add to FELC, FESM, FMDE, FEMR, FENI, FAGIX, CDDRX, CTHRX, TRBCX on a down day
- If market is down 1%+ today, flag Simple IRA deployment opportunity prominently
- Note: Must execute before 4 PM for today's NAV price

**Simple IRA Standing Reminder:**
~$83,362 cash (SPAXX) waiting for deployment on down days. Check today's market movement:
- Down 1%+ = FLAG as deployment opportunity, suggest specific positions and amounts
- Down 0.5-1% = Note as modest opportunity, user's discretion
- Flat or up = Hold, wait for better entry

### STEP 8 — New Tier 1 Opportunities (Afternoon Discovery)
Any Tier 1 opportunity that emerged DURING THE DAY that was NOT in the morning scan:

Primary triggers to scan for afternoon:
1. Unusual call activity that spiked in the last 2-3 hours of trading
2. Positive catalyst announced during market hours (FDA approval, contract win, earnings beat)
3. Stock breaking above 52-week high on afternoon volume surge
4. Short squeeze developing — stock up 10%+ with no obvious news
5. Insider buy Form 4 filed today (within last 6 hours)

For each new afternoon Tier 1 opportunity:
- Ticker and trigger
- Current price and move today
- Catalyst
- Options signal if applicable
- Conviction 1-10
- Can you act before close or is this an overnight research item?

### STEP 9 — Overnight Research Queue
Items that need more digging TONIGHT before tomorrow's morning scan.

**Priority Levels:**
🔴 P1 — MUST research tonight. High conviction opportunity or risk that directly affects a position. Tomorrow's morning scan depends on this.
🟡 P2 — Should research tonight. Important but not urgent. Will improve tomorrow's scan quality.
🟢 P3 — Research when time allows. Background intelligence that builds over time.

For each research item:
- What to research
- Why it matters
- Priority level
- Specific questions to answer
- Where to look (SEC filings, earnings transcript, analyst reports, news)

### STEP 10 — Open Action Items (Rolling Forward)
Permanent rolling list that stays until explicitly marked complete by the user.

**Format:**
⬜ [Action item] — [Why it matters] — [Deadline if any]
✅ [Completed item] — [When completed]

Current standing open items to always include until resolved:
- Simple IRA ~$83,362 cash (SPAXX) — deploy when S&P RSI <35 OR >8% below 200 DMA (NOT on simple 1% down days)
- Traditional IRA — $40K rollover incoming from Principal; deploy on arrival
- CTHRX — exit when new rollover cash provides flexibility (redundant tech exposure)
- FAGIX — misaligned in both IRAs; exit plan TBD

Update this list based on what the user confirms has been completed during the session.

---

## Output Format

```
═══════════════════════════════════════════
AFTERNOON SCAN — 3:15 PM ET
[Day, Date] | [X] minutes to close | [X] minutes to mutual fund cutoff
═══════════════════════════════════════════

MORNING SCAN RECAP 📋
[What was flagged this morning and how it played out]
• Tier 1 [ticker] — Conviction [X]/10 — Today: [up/down X%] — [Still valid / Revised]
• Actions recommended: [list] — Completed: [Y/N]

═══════════════════════════════════════════
MARKET SNAPSHOT 📊
═══════════════════════════════════════════
S&P: [X] ([X]%) | Nasdaq: [X] ([X]%) | VIX: [X]
Oil: [X] | Gold: [X] | Bitcoin: [X] | 10yr: [X]%
[One sentence on what's driving the market today]

═══════════════════════════════════════════
PORTFOLIO MOVERS ⚡
═══════════════════════════════════════════
[Only positions that moved 2%+ or had news]

[TICKER] — [+/-X%] today
WHY: [reason]
THESIS: [intact / changed / broken]
ACTION: [hold / add / trim / sell] — Conviction [X]/10

EARNINGS RESULTS TODAY:
[TICKER] — Beat/Miss/In-line
EPS: $[actual] vs $[estimate] ([+/-X]%)
Revenue: $[actual] vs $[estimate]
Guidance: [raised/lowered/maintained]
Reaction: [+/-X%]
Action: [hold/add/trim] — Conviction [X]/10

SELL SIGNALS:
[Any position triggering sell criteria]
[If none: "No sell signals today."]

═══════════════════════════════════════════
NEW AFTERNOON OPTIONS ACTIVITY 🎯
═══════════════════════════════════════════
[New unusual activity not present at morning scan]

[TICKER] — [X]x average call/put volume
SIGNAL: [what the flow suggests]
CATALYST: [known or unknown]
CONVICTION: [X]/10
ACTION: [act before close / overnight research / monitor]

[If nothing new: "No new unusual options activity since morning scan."]

═══════════════════════════════════════════
ANALYST ACTIONS TODAY 📈
═══════════════════════════════════════════
[Upgrades, downgrades, target changes during market hours]

[FIRM] [upgraded/downgraded] [TICKER]
New target: $[X] (was $[X]) | [X]% upside from here
Impact: [what this means for your position]

[If none: "No analyst actions on holdings today."]

═══════════════════════════════════════════
TECHNICAL DEVELOPMENTS 📉
═══════════════════════════════════════════
[DMA crossovers, support/resistance breaks, RSI extremes]

[TICKER] — [crossed 50/200 DMA / broke support / RSI overbought]
Direction: [bullish/bearish]
Volume confirmation: [above/below average]
Action: [buy more / hold / trim]

[If none: "No significant technical developments today."]

═══════════════════════════════════════════
⏰ MUTUAL FUND WINDOW — ACT BEFORE 4 PM
═══════════════════════════════════════════
💰 SIMPLE IRA — ~$83,362 CASH
CIRCUIT BREAKER: [ACTIVE 🔴 — no deployment / CLEAR 🟢]
DEPLOYMENT CHECK: S&P RSI [X] | SPY vs 200 DMA: [X]% [above/below]
[If RSI <35 OR SPY >8% below 200 DMA AND circuit breaker CLEAR]:
🚨 DEPLOYMENT SIGNAL — [condition met]. Deploy $[X] into [positions] before 4 PM.
[If conditions not met]: Holding. RSI [X], [X]% from 200 DMA. Not washed out yet.
[If circuit breaker active]: 🔴 SUSPENDED — circuit breaker in effect.

[Any other mutual fund opportunities in IRA positions]

═══════════════════════════════════════════
NEW TIER 1 AFTERNOON OPPORTUNITY 🔴
═══════════════════════════════════════════
[Only if something new emerged this afternoon]

NAME: [Ticker]
TRIGGER: [What fired this afternoon]
PRICE: $[X] | Move today: [+/-X%]
CATALYST: [What happened]
OPTIONS: [If applicable]
CONVICTION: [X]/10 — [explanation]
ACT BEFORE CLOSE OR OVERNIGHT: [which]
VERDICT: [One sentence]

[If nothing new: "No new Tier 1 setups emerged this afternoon. 
Morning scan opportunities still stand."]

═══════════════════════════════════════════
OVERNIGHT RESEARCH QUEUE 🔬
═══════════════════════════════════════════
🔴 P1 — MUST RESEARCH TONIGHT
• [Item] — [Why it matters] — [Specific questions]

🟡 P2 — SHOULD RESEARCH TONIGHT  
• [Item] — [Why it matters]

🟢 P3 — RESEARCH WHEN TIME ALLOWS
• [Item] — [Background intelligence]

[If nothing urgent: "No P1 research items tonight. 
Morning scan ready to run at 9:45 AM."]

═══════════════════════════════════════════
OPEN ACTION ITEMS 📋
═══════════════════════════════════════════
⬜ Simple IRA ~$83,362 — Deploy on down days
⬜ Traditional IRA — $40K rollover incoming from Principal
⬜ CTHRX — exit when new rollover cash provides flexibility
⬜ FAGIX — misaligned in both IRAs; exit plan TBD
⬜ [Any unresolved morning actions]
⬜ [Any new actions from this scan]
✅ [Items completed today — with timestamp]

═══════════════════════════════════════════
BOTTOM LINE — NEXT 45 MINUTES
═══════════════════════════════════════════
[3 sentences max. What to do RIGHT NOW before close.
What to research tonight. What tomorrow morning looks like.]
═══════════════════════════════════════════
```

---

## Sell Signal Framework (same as morning scan)

**Take Profits — flag if:**
- Position up 30%+ AND conviction score dropped since entry → Sell half
- Position up 50%+ regardless → Flag, raise stop
- Original catalyst played out with no new catalyst → Sell all
- Options IV collapsing after big move → Sell half
- Analyst target reached → Reassess

**Cut Losses — flag if:**
- Down 20% from entry → Review thesis
- Down 30% from entry → Sell unless specific catalyst to recover
- Original catalyst failed → Sell all
- Earnings miss contradicting thesis → Sell all

**Thesis Break — sell immediately:**
- Key contract or partnership lost
- Competitor announces superior product
- Regulatory action
- Management guidance cut dramatically

**Conviction-Based Sell Scale:**
| Change | Action |
|--------|--------|
| Was 7-8, now 4-5 | Sell half |
| Was 9-10, now 5-6 | Sell half |
| Any score drops to 3 or below | Sell all |
| Score unchanged, up 50%+ | Raise stop to 30% below current |
| Score unchanged, down 20% | Review and decide |

---

## Critical Rules

1. **Check the Macro Volatility Circuit Breaker FIRST** — Before running STEP 4 (afternoon options), STEP 8 (Tier 1 opportunities), or any mutual fund deployment: check VIX (sustained >25) and S&P vs 200 DMA (>5% below). If circuit breaker is active: skip options chasing, skip new Tier 1 entries, suspend Simple IRA deployment, flag 🔴 CAPITAL PRESERVATION MODE at top of output.
2. **Always reference morning scan first** — user needs continuity between the two scans
3. **Lead with time-sensitive items** — mutual fund window, positions reporting today, options activity
4. **Never flag insider buying older than 7 days** — cite exact Form 4 filing date
5. **Never manufacture opportunities** — if nothing new emerged this afternoon, say so clearly
6. **Priority levels on research queue are non-negotiable** — P1 items must be researched before tomorrow's morning scan
7. **Open action items roll forward every scan** until user confirms completion
8. **Mutual fund window gets its own prominent section** — 4 PM cutoff is a hard deadline
9. **Simple IRA deployment uses RSI/200 DMA trigger, NOT "down 1% today"** — deploy only when S&P RSI <35 OR S&P >8% below 200 DMA AND circuit breaker is NOT active
10. **The Expedia Rule on afternoon news** — classify all news as Level 1 (category-wide) or Level 2 (competitive reshuffling) before treating it as a signal. Level 2 intra-industry jockeying does not validate or invalidate the category thesis.

---

## Portfolio Reference

**Taxable Baskets:** Technology, Small/Mid Cap, Crypto, Growth Blend, Defense, Healthcare, Critical Materials, AI Power Infrastructure, Dividends, Bonds, Financials, Speculative

**Taxable Standalones:** NVDL, QQQ, QQQM, VFMO, AMT, DCOM, FMSDX, CRK, XLE, PSQ, QID, AGNC 200sh, ACHR 200sh, SOUN 200sh, PONY 150sh, RR 100sh, ALAB 57sh, AMD 86sh, AMZN 126sh, ANET 52sh, CRWD 10sh, GOOG 148sh, META 10sh, MSFT 73sh, NOW 12sh, NVDA 228sh, ORCL 20sh, TSM 54sh, OPEN 65sh + warrants, NFLX Jun 18 $90 LONG call (1)

**Roth IRA:** Space basket (RKLB 18.1sh, ASTS 11.1sh, PL 22.2sh, LUNR 31.8sh, RDW 121.6sh). Standalones: NFLX 125sh @$90.38 avg + short Aug21 $110 call (1 contract), MU 4sh, RONB 150sh, CORT 35sh, LWLG 45sh, NSSC 150sh, ARXS 40sh, CIFR 50sh, FLTCF 150sh. SPAXX ~$730.

**Jen's Roth IRA:** VTI 35%, QQQM 25%, VXF 20%, SOXQ 12%, DFAS 8%. Do not touch.

**Traditional IRA (~$456K):** FELC 3,950sh, TRBCX 291.8sh, QQQM 100sh, FMDE 1,000sh, FESM 630sh, FEMR 809.7sh, FENI 675sh, FAGIX 2,862sh, CTHRX 79.2sh, CDDRX 490.6sh. SPAXX ~$11,292. $40K rollover incoming from Principal.

**Simple IRA (~$335K):** FELC 1,613sh, FXAIX 151.9sh, TRBCX 247.5sh, FAGIX 1,256sh, FEMR 192sh, FENI 191.8sh, FESM 347sh, FMDE 586.2sh, QQQM 79.2sh. SPAXX ~$83,362 — deploy on down days.

**Key Watchlist:** DVN, MU, NOC, LMT, LITE, COHR, GLW, FLTCF, FIGR, CDRE, MPTI, VOYG, QNT (post-IPO), VST
