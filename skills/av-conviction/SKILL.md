---
name: av-conviction
description: >
  ALWAYS use this skill when the user wants a conviction score on a stock, says "run AV on X",
  "score this ticker", "give me conviction on X", "what does AV say about X", "check Alpha Vantage",
  or asks for a 1-10 rating on any individual stock. This skill fetches live data from Alpha Vantage
  (RSI, fundamentals, EPS history) and returns a 1-10 conviction score with entry, stop, targets,
  tier placement, and the single biggest risk. Never skip this skill and rely on memory for conviction
  scoring — always fetch live AV data first.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from the Railway FMP service.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This fetches directly via web_fetch — no prior search required. Returns live price, change, day range, 52-week range, volume. Do NOT use prices from search snippets, memory, or earlier in the conversation — those go stale within minutes.

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---

## ⛔ MANDATORY FIRST ACTION — NO EXCEPTIONS ⛔

Before ANY other tool call, before ANY web search, before reading ANY other data:

**STEP 0: web_fetch → https://robinhood.com/us/en/stocks/TICKER**

This is Tool Call #1. Always. Not Tool Call #3. Not after the searches come back.
Search snippets contain stale prices. Railway FMP service is live. Use it.

If you have already run a search query before fetching the Railway service, you have already made the mistake. Stop. Fetch Railway now. Correct the price before proceeding.

**DO NOT TYPE A DOLLAR AMOUNT NEXT TO ANY TICKER UNTIL THIS FETCH IS COMPLETE.**

---

# AV Conviction Skill

Fetches live data and produces a 1–10 conviction score using the user's investment framework.

**DATA SOURCES — run in parallel:**
1. **Alpha Vantage** (primary for fundamentals and RSI)
2. **FMP MCP** (primary for live price, analyst targets, insider trades — always faster and more current)

## API Key (Alpha Vantage)
`171JCI69FB5GFTCL`

## Step 1 — Fetch data from BOTH sources simultaneously

**From FMP MCP (pull first — faster):**
- `FMP:quote` endpoint `quote` → current price, 52wk range, volume, market cap
- `FMP:analyst` endpoint `analyst-estimates` → analyst price targets and consensus rating
- `FMP:insiderTrades` endpoint `insider-trades` → filter for last 7 days, buys only
- `FMP:calendar` endpoint `earnings-calendar` → next earnings date

**From Alpha Vantage via web_fetch (run in parallel):**

**Overview:**
`https://www.alphavantage.co/query?function=OVERVIEW&symbol={TICKER}&apikey=171JCI69FB5GFTCL`

**RSI (14-day daily):**
`https://www.alphavantage.co/query?function=RSI&symbol={TICKER}&interval=daily&time_period=14&series_type=close&apikey=171JCI69FB5GFTCL`

**Earnings history:**
`https://www.alphavantage.co/query?function=EARNINGS&symbol={TICKER}&apikey=171JCI69FB5GFTCL`

**Volume history (web search — mandatory):**
Web search: `[TICKER] volume history average volume recent sessions [current month] [year]`
Pull last 10 sessions of volume vs average. Note direction — rising or falling.

## Step 2 — Pre-Score Pressure Test (MANDATORY — run before scoring)

**This checklist exists because of a specific failure: ZBIO was scored 8/10 and presented
as an "enter now" with a 3:1 R/R. Every one of these questions would have caught that error
before it reached Gary. Run ALL of them. Do not skip any. Do not rationalize past a red flag.**

Answer every question explicitly before assigning a conviction score:

### 2A — Volume Gate
- What has volume been over the last 10 sessions vs average daily volume?
- Is volume RISING (accumulation) or FALLING (distribution/disinterest)?
- On the most recent significant news day, was volume above or below average?
- **RED FLAG:** If volume is consistently below average AND a catalyst is supposedly imminent,
  institutions are not positioning. This directly contradicts the catalyst thesis. Score cannot
  exceed 6 until volume confirms.

### 2B — Offering Price Gate (if applicable)
- Has the company done a secondary offering in the last 6 months?
- What was the offering price?
- Is the stock currently trading ABOVE or BELOW that offering price?
- **RED FLAG:** Stock trading below its most recent secondary offering means institutional
  buyers from that offering are underwater and are potential sellers, not a support floor.
  Never use the CEO's personal purchase price as a downside floor. Use the 52-week low.

### 2C — Going Concern Gate
- Has the company received a going concern warning from auditors in the last 12 months?
- If yes — has it been formally resolved (new financing closed, auditors removed the warning)?
- **RED FLAG:** An unresolved going concern warning is a hard cap on conviction — maximum
  score of 5 regardless of clinical or fundamental merits until formally cleared.
- **IMPORTANT:** A company raising cash after a going concern warning does not automatically
  clear it. The auditors must remove it in a subsequent filing. Verify explicitly.

### 2D — Catalyst Reality Check
- What is the stated upcoming catalyst?
- Is this GENUINELY NEW INFORMATION (new trial readout, new contract, first revenue)
  OR is it a PRESENTATION of already-published data (conference talk, investor day recap)?
- **RED FLAG:** A conference presentation of already-known Phase 3 results is NOT a binary
  catalyst. The market already knows the data. Do not frame it as a re-rating event unless
  there is confirmed new data being presented for the first time.
- **Test:** If you removed the "catalyst," would the investment thesis still stand on its own?
  If no — the thesis is entirely event-dependent and the score should reflect that risk.

**The Expedia Rule — apply to every catalyst assessment:**
Classify the catalyst as Level 1 (category) or Level 2 (competitive) before weighting it.

- **Level 1 catalyst** (category-wide impact): A new government defense budget increasing
  spending across all contractors. A regulatory change that opens a new market for the whole
  sector. A macro shift (energy prices, interest rates, consumer spending) that lifts or
  sinks the entire category. These are high-weight catalysts — they move the whole pie.
- **Level 2 catalyst** (competitive reshuffling within category): Company A winning a
  contract that Company B previously held. Market share shift between two peers in a
  stable category. These matter for the specific company but do NOT validate the category
  thesis and should be weighted accordingly.

**Why this matters for conviction scoring:**
A Level 1 catalyst on a company in a growing category = multiply conviction.
A Level 2 catalyst (peer losing share to this company) in a SHRINKING category = trap.
Always identify which level the catalyst operates at before assigning conviction weight.

### 2E — True Downside Anchor
- What is the actual 52-week low?
- What is the actual cash per share (for pre-revenue/clinical stage names)?
- What is the post-dilution share count after all recent offerings?
- **RULE:** The downside floor is the 52-week low or cash per share — whichever is higher.
  NEVER use a CEO's personal purchase price or an offering price as a floor.
  Both are data points, not floors. Floors are where the stock has actually found support.

### 2F — Insider Buying Quality Check
- Are insider purchases by CEO/CFO/Director in open market (P code, direct ownership)?
- Are purchases part of a 10b5-1 automatic plan? If yes — weight significantly less.
- Has the insider sold any shares in the last 6 months? Net buyer or net seller?
- What % of their total position does the purchase represent?
- **RED FLAG:** A CEO buying $100K when they already own $50M in stock is a rounding error,
  not a conviction signal. Size the purchase relative to their total position.
- **GREEN SIGNAL:** CEO buying represents 5%+ increase in their position AND they have
  not sold in 6+ months AND purchase is direct open market (not 10b5-1).

**CEO Historical Buy Track Record — mandatory additional check:**
Web search: `"{CEO NAME} {TICKER} Form 4 purchases history"` and
`"site:openinsider.com {TICKER}"` to pull prior purchase history.

Ask: In the last 2–3 years, how many times has this specific insider bought stock?
What happened to the stock price in the 6 months after each prior purchase?

- **STRONG GREEN:** CEO has bought 2+ times previously AND stock was up 20%+ within
  6 months after each prior purchase. This insider has demonstrated market-timing alpha
  on their own equity. Weight the current purchase heavily.
- **NEUTRAL:** CEO is buying for the first time OR prior purchases showed mixed outcomes.
  Weight normally — it's a signal, not a guarantee.
- **RED FLAG (Value Trap Signal):** CEO has bought stock 2+ times in the last 2 years
  AND the stock dropped significantly after each prior purchase. This pattern indicates
  either persistent optimism bias, board mandate buying, or window-dressing before a
  capital raise. Reduce the insider signal weight by 50%. Cap maximum contribution from
  this gate at +0.5 conviction points regardless of purchase size.
  State explicitly: "CEO has bought previously with poor subsequent performance — treat
  as weak signal only."

**The ZBIO Rule (unchanged):** Insider buying is a signal, not a thesis. Build the thesis
on fundamentals, volume, and catalyst quality first. Layer insider buying on top as
confirmation, not foundation. Even a perfect insider signal never scores above 5/10 alone.

### 2G — Confirmation Bias Check (most important gate)
- State the BEAR CASE for this stock in 2 sentences before writing the bull case.
- What would have to be TRUE for this stock to go to zero or down 50%?
- Is there any evidence in the data that supports the bear case?
- **RULE:** If you cannot articulate a credible bear case, you have not done enough research.
  Go back and find it. Every stock has one.

---

## Step 3 — Pre-Score Checklist Output (show this before the score)

Before presenting the conviction score, output this section:

```
PRE-SCORE PRESSURE TEST: [TICKER]
──────────────────────────────────
Volume Gate: [PASS/FLAG] — [one sentence: volume trend vs average]
Offering Gate: [PASS/FLAG/N/A] — [one sentence: last offering price vs current]
Going Concern: [PASS/FLAG/N/A] — [one sentence: status]
Catalyst Reality: [PASS/FLAG] — [one sentence: genuine new info or re-presentation]
Downside Anchor: $[X] (52-week low) | $[X] (cash/share if applicable)
Insider Quality: [PASS/FLAG] — [one sentence: % position increase, 10b5-1 or not]
Bear Case: [Two sentences stating the bear case explicitly]
──────────────────────────────────
FLAGS: [X] of 6 gates flagged
Score ceiling from flags: [None / Max 6 / Max 5 / Max 4]
```

**Score ceiling rules from flags:**
- Volume below average AND catalyst supposedly imminent → max score 6
- Stock below recent offering price → max score 7
- Unresolved going concern → max score 5
- Catalyst is re-presentation of known data → max score 6
- Multiple flags → take the LOWEST ceiling, not the average

---

## Step 4 — Score using this framework

**Conviction score 1–10:**
- 9–10 = Must buy now
- 7–8 = Strong buy
- 5–6 = Watch/hold
- 3–4 = Wait for better entry
- 1–2 = Avoid

**RSI signals:**
- RSI below 30 = oversold, strong entry signal
- RSI 30–50 rising = bullish setup
- RSI 50–70 = neutral
- RSI above 70 = overbought, caution

**EPS beat signals:**
- 4/4 beats = exceptional management credibility, +1 conviction
- 3/4 beats = strong, positive signal
- 2/4 = mixed, neutral
- 1/4 or 0/4 = red flag, -1 conviction
- For clinical-stage/pre-revenue: EPS beats are irrelevant — do not add/subtract

**PEG / Tier placement:**
- PEG under 1.0 = cheap for growth → Tier 2 Taxable acceptable
- PEG 1.0–2.0 = fair value → Tier 2 Taxable acceptable
- PEG 2.0–3.0 = premium → cautious Tier 2
- PEG 3.0–5.0 = priced for perfection → Tier 1 Roth only
- PEG above 5.0 = Tier 1 Roth only or avoid

**Analyst consensus:**
- Majority strong buy + high target upside = positive signal
- Majority hold or sell = negative signal

---

## Step 5 — Output format

Present in this exact format:

---
**AV CONVICTION: {TICKER}**

**Data pulled:** [date]

| Metric | Value |
|--------|-------|
| Forward P/E | Xx |
| PEG Ratio | X.XX |
| Analyst Target | $XXX (X% upside) |
| Analyst Ratings | X strong buy / X buy / X hold / X sell |
| RSI (14) | XX.X — [rising/falling/flat] |
| 52wk Range | $XX – $XXX (currently X% from high) |
| Volume (10-day) | [X avg vs X recent — rising/falling] |
| Rev Growth YoY | X% |
| Mkt Cap | $XB |

**RSI history (last 5 days):** [date: XX.X, date: XX.X ...]

**EPS last 4 quarters:**
- [Q date]: Est $X.XX → Actual $X.XX → [Beat/Miss] (+X.X%)
- [repeat x4]
- Beat rate: X/4

**PRE-SCORE PRESSURE TEST:**
[Insert full checklist output from Step 3]

**CONVICTION SCORE: X/10**

**Verdict:** [2–3 direct sentences. No hedging. State clearly whether this is a buy,
wait, or skip and why. If any gates flagged, explain how they affected the score.]

**Bear case:** [Two sentences. What would have to be true for this to go down 50%.]

**Tier placement:** [Tier 1 Roth / Tier 2 Taxable / Tier 3 IRA / Skip]

**Entry:** $XX–XX
**Stop:** $XX (based on 52-week low or key support — NOT offering price or CEO purchase)
**Target 1:** $XX
**Target 2:** $XX

**Biggest risk:** [One sentence. The single most important thing that could make this trade wrong.]

---

## Rules
- Never skip the data fetch. Always pull live AV data before scoring.
- Never skip the Pre-Score Pressure Test. All 6 gates must be answered before scoring.
- The bear case must be written before the bull case internally. Never start with the bull.
- Be direct. No both-sides hedging. Give a clear verdict.
- Score ceilings from flags are hard limits — do not override them with qualitative reasoning.
- If AV returns a rate limit message or empty data, say so explicitly and tell the user to
  try again in a few minutes (25 calls/day free tier limit).
- Cross-reference the restricted-entities skill before scoring — if the ticker is restricted,
  flag it immediately and do not score.
- If the ticker is also being evaluated for the taxable account, apply the Tier 2 Valuation
  Gate from the investment-research skill using the PEG from AV data.
- Volume is mandatory data. A conviction score without volume history is incomplete.
- The ZBIO rule: insider buying is a signal, not a thesis. Build the thesis on fundamentals,
  volume, and catalyst quality first. Layer insider buying on top as confirmation, not foundation.
