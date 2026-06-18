---
name: pre-earnings-radar
description: >
  Execute this skill every Sunday (or when the user says "run pre-earnings radar",
  "earnings radar", "what earnings setups are coming", "show me upcoming earnings plays",
  or any variation asking about stocks to position in BEFORE earnings). This skill finds
  stocks with earnings 15-45 days out that have a strong pre-earnings setup — the goal
  is to get IN before the move, not on earnings day. The CEG problem: surfacing a stock
  on earnings day instead of 3-6 weeks earlier when the setup was obvious and entry was
  clean. This skill exists to prevent that from ever happening again.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from the Railway FMP service.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This fetches directly via web_fetch — no prior search required. Returns live price, change, day range, 52-week range, volume. Do NOT use prices from search snippets, memory, or earlier in the conversation — those go stale within minutes.

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---



# Pre-Earnings Radar Skill

## Why This Skill Exists

On May 11, 2026, Constellation Energy (CEG) reported a massive earnings beat. The setup
was completely predictable 3-4 weeks earlier: 20/21 analysts bullish, stock down 13%
from highs, Calpine integration "show me" moment approaching, AI data center catalyst,
EPS estimates revised up. It was surfaced on earnings day — too late for a clean entry.

This skill exists to find the NEXT CEG before earnings day, not on it.

The goal is simple: identify stocks where the market has set up a pre-earnings entry
with asymmetric upside, get positioned 3-6 weeks out, and let earnings be the catalyst.

---

## When to Run

**Primary:** Every Sunday before market open — produces the week's Pre-Earnings Radar.
**Secondary:** Any time the user asks "what earnings setups are coming" or similar.
**Trigger phrases:** "pre-earnings radar", "earnings radar", "upcoming earnings plays",
"what should I be buying before earnings", "run the radar"

---

## The 7-Point Pre-Earnings Setup Screen

Every candidate must be scored against these 7 signals. A score of 5/7 or higher
qualifies for the radar. Below 5/7 is watchlist only.

### Signal 1 — EARNINGS DATE WINDOW ✅/❌
Earnings must be 15-45 days out. Not sooner (too close, already priced),
not later (too far, capital tied up waiting).
- Use FMP:calendar endpoint "earnings-calendar" to pull next 45 days
- Flag exact date and days-until
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 2 — THE DIP ✅/❌
Stock must be down 8-25% from its 52-week high. This is the entry gift.
- Too little (<8%): already priced in, no margin of safety
- Too much (>25%): may signal something broken, not just a dip
- The CEG example: down 13% from $412 high when the setup was clear
- Pull via FMP:quote endpoint "quote" — compare price vs 52wk high
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 3 — ANALYST CONVICTION ✅/❌
75%+ of covering analysts must rate it Buy or Strong Buy.
AND average price target must imply 15%+ upside from current price.
- Pull via FMP:analyst endpoint "analyst-estimates" or web search
- Both conditions must be true — high buy % with a low target doesn't count
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 4 — ESTIMATE REVISION MOMENTUM ✅/❌
EPS estimates must have been revised UP by 2+ analysts in the last 30 days.
This is the single most predictive signal for an earnings beat.
- "Earnings estimate revisions [TICKER]" search on stockanalysis.com
- Look for: "X analysts raised estimates", "consensus moved up $X"
- Bearish revision trend (estimates going DOWN) is an automatic disqualifier
  regardless of other signals — flag as WARNING, do not recommend
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 5 — OPTIONS IMPLIED MOVE ✅/❌
Options market must be pricing a 5%+ implied move for the earnings event.
This tells you the market KNOWS something big is coming. Combined with
a bullish setup, high implied move = high reward potential.
- Search "[TICKER] earnings implied move options" or check via web
- Also note: if IV is already spiked 30%+ heading in, premium is expensive
  for options buyers — flag this for the verdict
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 6 — THE "SHOW ME" CATALYST ✅/❌
There must be a specific, identifiable thing that will be confirmed or
denied on the earnings call — not just "will they beat estimates."
This is what separates a great pre-earnings setup from a coin flip.

Examples of strong "show me" catalysts:
- First full quarter integrating a major acquisition (Calpine for CEG)
- New contract or partnership expected to be confirmed
- Regulatory decision or approval expected before/on call
- Guidance raise signaled but not yet delivered
- Product launch or expansion results — first data point
- Management said "watch for X in Q1" and Q1 is now reporting
- Hyperscaler/enterprise deal commentary (data center names)

No "show me" catalyst = lower conviction, cap score at 5/7 max.
- Research via web search: "[TICKER] Q[X] earnings preview what to watch"
- **Score: Pass (1pt) or Fail (0pt)**

### Signal 7 — SECTOR TAILWIND ✅/❌
The sector must currently be receiving institutional inflows OR be
aligned with a macro trend that is accelerating.

Current strong sectors (update as macro evolves):
- AI infrastructure (power, data centers, chips, networking)
- Defense (government spending, geopolitical tension)
- Nuclear/clean energy (AI power demand)
- Semiconductors (AI supercycle, supply chain normalization)
- Financial technology (rate environment, credit normalization)

Sectors with headwinds to flag:
- Consumer discretionary (high-income pressure)
- Traditional retail (structural decline)
- Office REITs (remote work secular trend)

- **Score: Pass (1pt) or Fail (0pt)**

---

## Conviction Score → Action Matrix

| Score | Classification | Action |
|-------|---------------|--------|
| 7/7 | MAXIMUM CONVICTION | Strong pre-earnings position. Size up. |
| 6/7 | HIGH CONVICTION | Solid pre-earnings position. Normal size. |
| 5/7 | MODERATE CONVICTION | Starter position or watchlist with alert at 30 days out. |
| 4/7 | WATCHLIST ONLY | Track but do not commit capital yet. Re-evaluate at 30 days. |
| 3/7 or below | SKIP | Not enough signal. Move on. |

---

## Which Tier Does the Pre-Earnings Play Go In?

The tier assignment is based on the STOCK's profile, not just the setup:

**Tier 1 (Roth):**
- Under $50/share preferred (Roth account sizing)
- High implied move (10%+)
- Binary-ish catalyst (FDA, contract, first-quarter integration)
- Boom-or-bust acceptable

**Tier 2 (Taxable):**
- Quality company with proven track record
- Pre-earnings dip on a long-term compounder
- You'd own it anyway — earnings is just the catalyst to buy the dip
- CEG is the archetype: quality nuclear/energy compounder, down from highs,
  earnings as the re-rating moment

**Tier 3 (IRA/Simple):**
- Rarely appropriate for pre-earnings plays
- Exception: a steady dividend grower with estimate revision momentum
  where the earnings confirm the thesis — low implied move, low risk

---

## Execution Steps — Run Every Sunday

### STEP 0 — MANDATORY SECTOR ROTATION CHECK (Do this FIRST, every single run)

**The Gary Rule:** On May 11, 2026, the radar kept surfacing defense stocks because
prior conversation context anchored on defense. Gary's portfolio already has defense
exposure. The radar must scan the ENTIRE market every time — not just sectors from
prior conversations or recent news flow. Anchoring to one sector is a failure state.

Before pulling a single ticker, explicitly confirm you are scanning ALL 11 sectors:

| # | Sector | Example names to consider |
|---|--------|--------------------------|
| 1 | Energy | XOM, COP, DVN, OXY, SLB, HAL, CRK |
| 2 | Materials | NEM, FCX, NUE, CF, MOS, LIN, APD |
| 3 | Industrials | GE, CAT, DE, ETN, EMR, ROK, HEICO, BA |
| 4 | Consumer Discretionary | HD, MCD, NKE, LOW, TSLA, GM, F |
| 5 | Consumer Staples | PG, KO, PEP, COST, WMT, MO, PM |
| 6 | Healthcare | UNH, LLY, JNJ, ABT, MDT, BSX, ISRG |
| 7 | Financials | JPM, BAC, GS, MS, BLK, AXP, V, MA |
| 8 | Information Technology | AAPL, MSFT, NVDA, AMD, AMAT, KLAC, TXN |
| 9 | Communication Services | GOOGL, META, NFLX, DIS, T, VZ |
| 10 | Utilities | NEE, DUK, SO, AEP, CEG, PCG |
| 11 | Real Estate | AMT, PLD, EQIX, SPG, O, VICI |

**Software exclusion — NARROWED:** Exclude pre-revenue or money-losing software/SaaS only.
A profitable software company with positive TTM net income, FCF margin >20%, and PEG <2.0
passes and should be evaluated like any other quality compounder. The exclusion targets
narrative-driven multiple-compression risk — that risk lives in unprofitable software,
not in proven cash-generating businesses. Do NOT auto-reject profitable software names.

**The self-check before proceeding:** Can you name at least one candidate from at
least 6 different sectors that you evaluated this run? If not, you anchored — go back
and expand the scan before outputting results.

### STEP 1 — Pull the Earnings Calendar
Use FMP:calendar endpoint "earnings-calendar" for the next 45 days.
Filter to stocks with earnings 15-45 days out.
From that list, evaluate candidates across ALL 11 sectors (see Step 0).
Minimum criteria:
- Market cap $2B+ (enough analyst coverage to have a consensus)
- At least 5 analysts covering (need consensus to be meaningful)
- Stock price under $300 (Gary's actionability filter)

Eliminate immediately:
- Pure software/SaaS companies (see software exclusion above)
- Anything already up 20%+ YTD with no dip (nothing to buy)
- Any company with a recent scandal, SEC investigation, or management crisis
- Any company on the restricted entities list (check EVERY name)

### STEP 2 — Score Each Candidate
For each candidate surviving the filter, run all 7 signals.
Aim to evaluate 8-12 names per week. Surface the top 3-5 that score 5+/7.

Use FMP tools for live data first:
- FMP:quote for price vs 52wk high (Signal 2)
- FMP:analyst for consensus and targets (Signal 3)
- FMP:calendar for exact earnings date (Signal 1)

Use web search for:
- Estimate revision data (Signal 4)
- Implied move (Signal 5)
- "Show me" catalyst research (Signal 6)
- Sector flow data (Signal 7)

### STEP 3 — Assign Tier and Build the Output
For each name scoring 5+/7, produce the full output block (see format below).
For names scoring 4/7, add to the WATCHLIST section with a brief note.
Do NOT manufacture setups — if nothing scores 5+/7 this week, say so clearly.

### STEP 4 — Cross-Check Restricted List
Before outputting ANY name, verify it is not on the restricted entities list.
If a strong setup involves a restricted name: skip entirely, note "⛔ RESTRICTED — skipping."

### STEP 5 — Portfolio Overlap Check
For any Tier 1 recommendation, check if the portfolio already has exposure
to that sector or name. Flag redundancy.

---

## Output Format

```
═══════════════════════════════════════════════════════
PRE-EARNINGS RADAR — WEEKLY SETUP REPORT
[Day, Date] | Earnings window: [X] days out to [Y] days out
═══════════════════════════════════════════════════════

THE POINT OF THIS SCAN
We get in 3-6 weeks before earnings, not on earnings day.
Today's radar covers earnings from [date range].

═══════════════════════════════════════════════════════
🔴 TIER 1 PRE-EARNINGS SETUPS (Roth IRA)
═══════════════════════════════════════════════════════

[If setup found:]
NAME: [TICKER — Company Name]
EARNINGS DATE: [Date] — [X] days away
SCORE: [X]/7 — [HIGH/MODERATE] CONVICTION

SIGNAL SCORECARD:
  ✅ Earnings window: [X] days out
  ✅/❌ The Dip: [X]% below 52wk high (was $[X], now $[X])
  ✅/❌ Analyst conviction: [X]% Buy | Avg target $[X] ([X]% upside)
  ✅/❌ Estimate revisions: [Up/Down/Flat] — [specific detail]
  ✅/❌ Implied move: [X]% priced in by options
  ✅/❌ Show-me catalyst: [Exactly what will be confirmed/denied on the call]
  ✅/❌ Sector tailwind: [Which tailwind and why it's accelerating]

ENTRY: $[X] | STOP: $[X] (below [support level]) | TARGET: $[X] pre-earnings, $[X] post-earnings
RISK: [One sentence — what breaks the setup]
VERDICT: [One sentence. Would you be an idiot not to at least have a starter here?]

[If no Tier 1 setup: "No Tier 1 pre-earnings setup scores 5+/7 this week. Wait for the right pitch."]

═══════════════════════════════════════════════════════
🟡 TIER 2 PRE-EARNINGS SETUPS (Taxable)
═══════════════════════════════════════════════════════

[Same format as Tier 1]

VALUATION GATE: PEG [X] — [CHEAP/FAIR/PREMIUM] | FCF Yield [X]%
HOME: [Which basket this belongs in]

[If no Tier 2 setup: "No Tier 2 pre-earnings setup scores 5+/7 this week."]

═══════════════════════════════════════════════════════
📋 WATCHLIST — SCORED 4/7 (Check Again in 2 Weeks)
═══════════════════════════════════════════════════════
[Name | Score | What's missing | Earnings date | When to re-evaluate]

═══════════════════════════════════════════════════════
⚠️ EARNINGS WARNINGS — BEARISH REVISION TRENDS
═══════════════════════════════════════════════════════
[Any holding in the portfolio with earnings 15-45 days out AND
 estimates being revised DOWN — flag as "consider reducing before earnings"]
[If none: "No bearish revision trends detected for current holdings."]

═══════════════════════════════════════════════════════
BOTTOM LINE
═══════════════════════════════════════════════════════
[Max 3 sentences. What to buy now, what to watch, what to ignore.]
[Always include: "Next check-in on these setups: [date]"]
═══════════════════════════════════════════════════════
```

---

## The CEG Rule

Named after the May 2026 Constellation Energy situation where a textbook
pre-earnings setup was surfaced on earnings day instead of 3-4 weeks earlier.

**The CEG Rule:** If a stock has 5+/7 signals firing and earnings are
15-45 days away, it MUST appear in this week's Pre-Earnings Radar.
No exceptions. The whole point of this skill is to find these before
the crowd. Showing up on earnings day is a failure state.

When running any scan, if a name surfaces that has earnings within 45 days
AND scores 5+/7, flag it immediately in the Pre-Earnings Radar section
even if it wasn't in the earnings calendar pull. The CEG rule supersedes
everything else.

---

## Integration With Daily Morning Scan

The morning scan includes a "PRE-EARNINGS RADAR" section that surfaces
the current week's top setup from this skill as a daily reminder.

As earnings approach and the setup evolves, the daily scan should update
conviction scores and flag when the entry window is closing
(7 days out = last clean entry before IV spikes).

When earnings are 7 days out: flag "ENTRY WINDOW CLOSING — last clean entry
before implied volatility makes options expensive."

When earnings are 3 days out: flag "HOLD if already in / AVOID new entry —
IV too high for clean risk/reward."

---

## Critical Rules

1. **Never surface a stock on earnings day as if it's a new idea** — if
   it had 5+/7 signals weeks ago, it should have been in the radar already.
   Surfacing on earnings day is the failure this skill prevents.

2. **Always cite the exact earnings date and days-until** — vagueness
   about timing kills the pre-earnings setup thesis.

3. **The "show me" catalyst must be SPECIFIC** — "they might beat estimates"
   is not a show-me catalyst. "First full quarter with Calpine revenues
   after a $3.9B acquisition" is a show-me catalyst.

4. **Never recommend a pre-earnings play in a stock with bearish estimate
   revisions** — that's a trap, not a setup.

5. **Always check restricted entities list before outputting any name.**

6. **Cap the radar at 5 names per week** — more than 5 dilutes focus.
   Surface only the best. Quality over quantity.

7. **Watchlist entries must have a specific "re-evaluate date"** — not
   "check later" but "re-check on [specific date] when earnings are 30 days out."

8. **Always note whether the play is for pre-earnings drift OR the
   earnings event itself** — some plays are about the stock rising
   into earnings as anticipation builds (pre-earnings drift); others
   are about holding through the print (more risk). Be explicit.

9. **VIX Circuit Breaker applies to pre-earnings entries** — if the Macro
   Volatility Circuit Breaker is active (VIX sustained >25 OR S&P >5% below
   200 DMA), do NOT recommend new pre-earnings positions. Surface the setups
   for awareness only and flag: "Circuit breaker active — monitor only, no entry
   until regime clears." Pre-earnings setups that score 5+/7 during a circuit
   breaker regime should be re-evaluated when the circuit breaker clears.

10. **The Expedia Rule on Signal 7 (Sector Tailwind)** — when evaluating whether
    a sector has a tailwind, use ONLY Level 1 (category-wide) signals. A competitor
    losing share to the company you're evaluating is NOT a sector tailwind — it is
    intra-industry reshuffling. A true sector tailwind is evidence that the total
    category is expanding: total industry revenue rising, new legislation opening
    the market, macro forces benefiting all players. Apply this distinction before
    awarding Signal 7 a passing score.
