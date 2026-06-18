---
name: earnings-analyzer
description: >
  Execute this skill whenever the user asks about earnings results, earnings reports,
  or how a company did on earnings. Triggers on phrases like "what did they report",
  "how were earnings", "did they beat", "earnings results", "rate the earnings",
  "what happened after close", or any request to evaluate a quarterly report.
  Also triggers proactively in the morning scan and afternoon scan when holdings
  have reported earnings overnight or after close. ALWAYS run the full analysis —
  never give a partial read. The goal is a clear 1-10 rating with conviction
  impact so the user knows immediately whether to buy more, hold, or trim.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from the Railway FMP service.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This fetches directly via web_fetch — no prior search required. Returns live price, change, day range, 52-week range, volume. Do NOT use prices from search snippets, memory, or earlier in the conversation — those go stale within minutes.

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---



# Earnings Analyzer Skill

## Core Philosophy
Every earnings report tells a story. The job is to read that story accurately and
translate it into one number (1-10) and one action (buy more / hold / trim / sell).
Never hedge. Never give a "wait and see" answer unless the data genuinely requires it.
The user needs to know what to do with the position BEFORE the market opens.

The most important question is not "did they beat?" — it's "does this change the thesis?"
A company can beat estimates and still have a broken thesis. A company can miss and
still have a stronger thesis than before. Always answer the thesis question.

---

## The 10-Point Rating Scale

**9-10 — OUTSTANDING**
Beat on both EPS and revenue meaningfully (5%+). Guidance raised significantly.
New catalysts announced (new product, new contract, new market). Management tone
is confident and specific. Stock reaction confirms the read. Thesis strengthened.
Action: Add to position aggressively.

**7-8 — STRONG**
Beat on both lines. Guidance raised or at least maintained with positive tone.
No major negative surprises. Thesis intact and progressing. Stock reacts positively.
Action: Hold with conviction, consider adding on any dip.

**6 — SOLID BUT NOT EXCITING**
Mixed results — beat one line, miss the other. Guidance reiterated but not raised.
Thesis intact but no acceleration. Market reaction muted.
Action: Hold. Wait for next quarter to confirm direction.

**4-5 — CONCERNING**
Miss on one or both lines. Guidance lowered or given cautiously. Management tone
hedging. One specific element of the thesis is not tracking as expected.
Action: Hold but reduce conviction. Watch closely next quarter.

**2-3 — WEAK**
Miss on both lines. Guidance cut. Management struggling to explain shortfalls.
Thesis showing real cracks. Stock sells off hard.
Action: Trim position. Reassess thesis from scratch.

**1 — DISASTER**
Massive miss. Guidance cut dramatically or withdrawn. Thesis broken.
Something fundamental changed — losing key customers, regulatory failure,
management credibility destroyed, competitive threat confirmed.
Action: Sell. Do not average down.

---

## The Seven Scoring Factors

Score each factor and weight them to arrive at the final 1-10 rating.

### Factor 1 — EPS Surprise (Weight: 15%)
- Beat by 10%+ = +2 points
- Beat by 5-10% = +1.5 points
- Beat by 0-5% = +1 point
- In-line (within 1%) = +0.5 points
- Miss by 0-5% = -0.5 points
- Miss by 5-10% = -1 point
- Miss by 10%+ = -2 points

Note: For pre-revenue or early stage companies (FLY, SOUN, etc.)
EPS matters less — focus on revenue and cash burn rate instead.

### Factor 2 — Revenue Surprise (Weight: 20%)
- Beat by 5%+ = +2 points
- Beat by 2-5% = +1.5 points
- Beat by 0-2% = +1 point
- In-line = +0.5 points
- Miss by 0-2% = -0.5 points
- Miss by 2-5% = -1 point
- Miss by 5%+ = -2 points

Revenue is weighted higher than EPS because revenue is harder to manipulate
and better reflects the actual business trajectory.

### Factor 3 — Guidance (Weight: 25% — most important factor)
- Raised significantly (5%+) = +3 points
- Raised modestly (1-5%) = +2 points
- Reiterated with positive tone = +1 point
- Reiterated with neutral tone = 0 points
- Lowered modestly = -1.5 points
- Lowered significantly = -3 points
- Withdrawn entirely = -4 points

Guidance is the most important factor because it tells you where the
company is going, not just where it's been.

### Factor 4 — Thesis Advancement (Weight: 20%)
Ask: Did this quarter move the investment thesis forward, backward, or sideways?

- Major new catalyst announced (new drug approval, new contract, new market) = +2
- Thesis progressing as expected = +1
- Thesis neutral — neither confirmed nor challenged = 0
- Thesis showing early signs of weakness = -1
- Thesis clearly broken or challenged = -3

### Factor 5 — Management Quality (Weight: 10%)
Assess the tone and content of the earnings call:
- Specific, confident, new information provided = +1
- Standard corporate language, nothing new = 0
- Defensive, vague, avoiding questions = -1
- Major management surprise (CEO departure, accounting concern) = -3

### Factor 6 — Quality of Beat/Miss (Weight: 5%)
- Organic growth driving the beat = +0.5
- Beat driven by cost cuts only, not revenue growth = -0.5
- Miss due to timing (one-time item) with clear recovery path = -0.25
- Miss due to structural issue = -1

### Factor 7 — Market Reaction (Weight: 5%)
The market is usually right on earnings day:
- Stock up 5%+ after hours = +0.5
- Stock up 0-5% = +0.25
- Stock flat = 0
- Stock down 0-5% = -0.25
- Stock down 5%+ = -0.5

### Factor 8 — MACD Momentum Confirmation (Qualitative — use as conviction modifier)
After earnings, check MACD to assess whether post-earnings momentum is building or fading.
This is not a scored factor but modifies the final conviction score:

- MACD bullish crossover forming post-earnings AND histogram widening = +1 to conviction
- MACD neutral/no change = 0 to conviction  
- MACD bearish divergence forming (stock up but MACD not confirming) = -1 to conviction
- MACD bearish crossover post-earnings = reduce conviction by 1, consider waiting to add

**Why this matters for earnings specifically:**
A stock can beat earnings and pop 10% but if MACD shows bearish divergence the pop
may be a sell-the-news event not a sustained move. Checking MACD after earnings tells
you whether institutional money is actually buying the beat or just covering shorts.
FLY beat earnings and went up 10%+ — if MACD confirmed with widening histogram,
that's a sustained move. If MACD had diverged, that would signal a fading bounce.

---

## The Thesis Change Assessment

After scoring, always explicitly answer:

**Did this earnings report change the investment thesis?**
- STRENGTHENED — New evidence supports the original investment case even more
- INTACT — Nothing changed, thesis progressing as expected
- NEUTRAL — Mixed signals, need more data
- WEAKENED — One or more thesis assumptions now in question
- BROKEN — The original reason to own this is no longer valid

This is the most important output. A 6/10 earnings with INTACT thesis
means hold. A 6/10 earnings with WEAKENED thesis means trim.

---

## Conviction Score Impact

After every earnings analysis, update the conviction score:

| Earnings Rating | Conviction Change |
|----------------|-------------------|
| 9-10 | +2 points |
| 7-8 | +1 point |
| 6 | No change |
| 4-5 | -1 point |
| 2-3 | -2 points |
| 1 | Sell signal, conviction irrelevant |

Always state: "Pre-earnings conviction: X/10. Post-earnings conviction: Y/10."

---

## What To Research Before Scoring

Always fetch/search for the following before scoring:

1. Actual EPS vs estimate (from Benzinga, Yahoo Finance, or SEC 8-K)
2. Actual revenue vs estimate
3. Full year guidance — raised, lowered, or reiterated
4. Key product/segment performance (what's driving or dragging)
5. Any new catalysts announced on the call
6. Management commentary on the call (tone and specifics)
7. After-hours stock reaction
8. At least 2 analyst reactions post-earnings

---

## Output Format

```
═══════════════════════════════════════════
EARNINGS ANALYSIS — [TICKER]
[Company Name] | Q[X] [Year] Results
Reported: [Date] after/before close
═══════════════════════════════════════════

THE NUMBERS
EPS: $[actual] vs $[estimate] — [Beat/Miss] by [X]%
Revenue: $[actual] vs $[estimate] — [Beat/Miss] by [X]%
Guidance: [Raised/Lowered/Reiterated] — [details]
Stock reaction: [+/-X%] after hours

SCORING BREAKDOWN
Factor 1 — EPS Surprise: [score] | [beat/miss by X%]
Factor 2 — Revenue Surprise: [score] | [beat/miss by X%]
Factor 3 — Guidance: [score] | [raised/lowered/reiterated]
Factor 4 — Thesis Advancement: [score] | [what happened]
Factor 5 — Management Quality: [score] | [tone assessment]
Factor 6 — Quality of Beat/Miss: [score] | [organic/one-time]
Factor 7 — Market Reaction: [score] | [stock move]

EARNINGS RATING: [X]/10 — [OUTSTANDING/STRONG/SOLID/CONCERNING/WEAK/DISASTER]

THESIS ASSESSMENT
Pre-earnings thesis: [one sentence summary of why you owned it]
Thesis status: [STRENGTHENED / INTACT / NEUTRAL / WEAKENED / BROKEN]
Key evidence: [specific data point that most affects the thesis]

CONVICTION UPDATE
Pre-earnings conviction: [X]/10
Post-earnings conviction: [Y]/10
Change: [+/- X points] — [reason]

ACTION
[BUY MORE / HOLD / TRIM / SELL]
[One sentence explaining exactly what to do and why]

WHAT TO WATCH NEXT QUARTER
[The one metric that will tell you if the thesis is on track or not]
═══════════════════════════════════════════
```

---

## Special Cases

### Pre-Revenue Companies (FLY, SOUN, ADUR, etc.)
Weight revenue growth rate and cash burn differently:
- Revenue growth rate YoY is the primary metric (not absolute revenue)
- Cash runway — how many quarters of cash remain at current burn rate
- Backlog/bookings growth — future revenue visibility
- Key milestones achieved vs promised
EPS is nearly irrelevant for pre-revenue growth companies.

### Mutual Funds and ETFs
ETFs don't report quarterly earnings. Skip this skill for ETF performance questions
and use the investment research skill instead.

### Biotech Binary Events (FDA decisions, trial data)
These are not earnings reports but use the same framework:
- Replace EPS/Revenue with trial outcome (met/missed primary endpoint)
- Replace guidance with FDA timeline and next steps
- Weight Thesis Advancement at 50% for binary biotech events

---

## Portfolio Context

Always note which account and basket the position is in:
- Roth (boom or bust — higher tolerance for weak earnings if thesis intact)
- Taxable (tax consequences of selling matter)
- IRA/Simple (steady compounder — lower tolerance for thesis breaks)

A 5/10 earnings in a Roth boom or bust position may still be hold.
A 5/10 earnings in a Traditional IRA steady compounder is likely trim or sell.
