---
name: investment-research
description: >
  ALWAYS use this skill before recommending, analyzing, or discussing any stock, ETF, 
  country fund, sector, or investment position. Triggers on any investment recommendation 
  request, portfolio review, basket construction, position sizing, buy/sell/hold decision, 
  or "what do you think about X" investment question. Do NOT skip this skill and rely on 
  memory or prior knowledge — always run the full pre-recommendation checklist first. 
  This skill exists because incomplete research leads to bad recommendations and wasted time.
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



# Investment Research Skill

## Core Philosophy
Never recommend anything without completing all seven checks first. Present findings BEFORE giving a recommendation. The user should never have to correct research gaps after the fact.

---

## Primary Data Source: FMP MCP

**Always use FMP MCP tools before falling back to web search for any price or fundamental data.** FMP is connected and live — it is faster, more accurate, and avoids stale search results.

Key FMP tools for investment research:
| Need | FMP Tool | Endpoint |
|------|----------|----------|
| Live price, 52wk range, volume | `FMP:quote` | `quote` |
| Analyst targets & consensus | `FMP:analyst` | `analyst-estimates`, `price-target` |
| Insider trades (last 7 days) | `FMP:insiderTrades` | `insider-trades` |
| Earnings date & estimates | `FMP:calendar` | `earnings-calendar` |
| Income statement, FCF | `FMP:statements` | `income-statement`, `cash-flow-statement` |
| ETF holdings & flows | `FMP:etfAndMutualFunds` | `etf-holder`, `etf-info` |
| News on a ticker | `FMP:news` | `stock-news` |
| Technical indicators (RSI, MACD) | `FMP:technicalIndicators` | `rsi`, `macd` |

Use web_search only for: narrative context, FDA events, government contracts, options flow, estimate revision trends (Zacks/stockanalysis).

---

## The Seven Mandatory Checks

Before recommending ANY stock, ETF, or position, run ALL of the following. Do not skip steps. Do not present a recommendation until all seven are complete.

### Check 1 — Current Price & Range

**Pull from FMP first — do not web search for price data:**
- `FMP:quote` endpoint `quote` → current price, 52wk high/low, change%, volume
- This is the authoritative live price. Never use a stale web search result when FMP is available.
- Where is it in the 52-week range? Near highs = caution. Near lows = potential opportunity.

### Check 2 — YTD Performance vs S&P 500
- YTD return of the position
- S&P 500 YTD return for comparison
- Is it beating or lagging? By how much?
- If it's lagging the S&P significantly, explain why before recommending

### Check 3 — 30-Day Price Forecast & Momentum
- Check short-term price forecast (stockscan.io, analyst forecasts, options implied move)
- Is momentum positive or negative right now?
- Has it already had a big run? If so, flag the risk of buying at the top
- Never recommend something that has already run 25%+ without flagging this explicitly

### Check 3B — MACD Momentum Confirmation (use as confirmation, never as primary trigger)
MACD is a lagging indicator — it confirms what is already happening, not what is about
to happen. Never use it as a reason to buy something on its own. Use it specifically in
two situations:

**Situation 1 — Before adding to an existing winner:**
When considering adding to a position that has already run, check MACD to confirm
momentum is still building vs fading.
- MACD line above signal line AND histogram widening = momentum building, ADD is supported
- MACD line above signal line BUT histogram narrowing = momentum fading, WAIT for pullback
- MACD line below signal line = momentum broken, do NOT add until crossover

**Situation 2 — MACD Divergence Warning (most valuable signal):**
When price makes a new high but MACD does NOT confirm with a new high — this is
bearish divergence. It means the move is running out of steam before price reverses.
Flag this explicitly as a caution sign.
Conversely when price makes a new low but MACD does not confirm — bullish divergence.
Potential reversal higher. Worth flagging as an entry opportunity.

**Situation 3 — Sell signal confirmation:**
When a position triggers a sell signal (down 20%, thesis breaking, etc.), check MACD.
If MACD also shows bearish crossover — conviction to sell increases significantly.
Two signals together are far more reliable than either alone.

**How to check MACD:**
Search "[TICKER] MACD chart" or check TradingView/Finviz technical section.
Look for: crossover direction, histogram trend (widening or narrowing), divergence.

**MACD Output Format:**
MACD Status: [BULLISH CROSSOVER / BEARISH CROSSOVER / NEUTRAL]
Histogram: [WIDENING — momentum building / NARROWING — momentum fading]
Divergence: [NONE / BULLISH DIVERGENCE — potential reversal up / BEARISH DIVERGENCE — exhaustion warning]
Conviction impact: [+1 if confirming buy / -1 if diverging against buy / 0 if neutral]

### Check 4 — Performance History (The Scoop)
Run the full scoop before recommending:
- YTD, 1 year, 3 year, 5 year, 10 year returns
- Compare to S&P 500 AND relevant category benchmark
- Expense ratio (for ETFs)
- AUM (flag anything under $500M as a liquidity concern)
- Dividend yield if relevant

### Check 5 — Analyst Consensus & Price Target

**Pull from FMP first:**
- `FMP:analyst` endpoint `analyst-estimates` → median price target, buy/hold/sell breakdown
- `FMP:analyst` endpoint `price-target` → most recent price target changes
- Implied upside or downside from current FMP quote price
- Flag any 0 Buy ratings situations

### Check 5B — Earnings Estimate Revision Trend (CRITICAL for pre-earnings positions)
This is one of the most reliable leading indicators available. Always run this check
for any stock with earnings in the next 30 days, and include it for all individual stocks.

**What to look for:**
- How many analysts revised EPS estimates UP in the last 30 days?
- How many analysts revised EPS estimates DOWN in the last 30 days?
- How many analysts revised REVENUE estimates UP in the last 30 days?
- How many analysts revised REVENUE estimates DOWN in the last 30 days?
- Net direction — more ups than downs or more downs than ups?

**Why this matters:**
Analysts talk to management. When analysts raise estimates even by a penny they are
quietly signaling that channel checks and management conversations are trending positive.
When 12 of 30 analysts raise estimates before earnings that is smart money telling you
something. Stocks almost always beat when revisions trend up. Stocks almost always
miss when revisions trend down. FLY was a perfect example — bullish revisions ahead
of its 8/10 print. We should have caught that and added before the beat.

**How to interpret:**
- 60%+ of revisions going UP = strong buy signal ahead of earnings
- Mixed revisions = neutral, binary risk, wait until after
- 60%+ of revisions going DOWN = warning signal, wait until after earnings

**Where to search:**
Search "[TICKER] earnings estimate revisions 30 days" or Zacks Earnings ESP.

**Output format:**
Estimate Revision Trend: [BULLISH / NEUTRAL / BEARISH]
Revisions UP: [X] analysts | Revisions DOWN: [X] analysts
Net signal: [what this means for the upcoming print]

**Proactive flag rules:**
- Revisions BULLISH before earnings → flag as buy before the print with conviction score
- Revisions BEARISH before earnings → flag as warning, wait until after print
- Missed bullish revisions before a beat → note explicitly so we catch it next time

### Check 6 — Fund Flows (for ETFs)
- 1 month, 3 month, 1 year flows — money coming IN or going OUT?
- Outflows are a red flag even if performance looks good
- Never recommend an ETF with significant sustained outflows without flagging it

### Check 6B — Tier 2 Valuation Gate (TAXABLE ACCOUNT ONLY — individual stocks)
This check is MANDATORY for any individual stock being considered for the taxable account.
Skip for Roth Tier 1 positions where valuation is less relevant to the boom or bust thesis.
Skip for ETFs — use fund flows instead.

**The core question:** Is there still VALUE built into this stock at the current price?
Meaning — can the company grow earnings fast enough to justify or grow INTO its current
multiple without requiring everything to go perfectly?

**The PEG Ratio is the primary metric:**
PEG = Forward P/E divided by Expected EPS Growth Rate

| PEG Ratio | Interpretation | Tier 2 Verdict |
|-----------|---------------|----------------|
| Under 0.5 | Extremely cheap for growth rate | Strong Tier 2 buy |
| 0.5 - 1.0 | Getting growth at a discount | Good Tier 2 buy |
| 1.0 - 2.0 | Fair value — room to grow | Acceptable Tier 2 hold |
| 2.0 - 3.0 | Premium valuation — needs execution | Cautious Tier 2 |
| 3.0 - 5.0 | Priced for perfection | Tier 1 Roth only |
| Above 5.0 | Completely overvalued for Tier 2 | Tier 1 Roth only or avoid |

**Supporting valuation metrics to always include:**
- Forward P/E vs sector average — is it cheaper or more expensive than peers?
- Price/Sales ratio — useful for pre-profit growth companies
- EV/EBITDA — enterprise value relative to earnings power
- Free Cash Flow Yield — FCF divided by market cap. Above 3% = value. Below 1% = expensive.
- Revenue growth rate — faster growth justifies higher multiples

**The Palantir test — always ask this:**
"If I buy this today in my taxable account and hold it for 3-5 years, can the company
grow its earnings fast enough that the stock price is justified — or am I buying hope?"
PLTR at 180x forward earnings with 25% growth = PEG of 7.2 = buying hope = Tier 1 only.
AMZN at 35x forward earnings with 20%+ growth = PEG of 1.7 = fair value = Tier 2 acceptable.
TSM at 20x forward earnings with 25%+ growth = PEG of 0.8 = getting growth cheap = strong Tier 2.

**The valuation gate rule:**
- PEG above 3.0 → FLAG as Tier 1 Roth candidate only, not Tier 2 taxable
- PEG above 5.0 → Never recommend for taxable account regardless of thesis
- PEG under 1.0 → Flag as potential value opportunity in taxable
- Always note when a stock has "grown into" its valuation vs when valuation has "run away"

**Output format for Tier 2 valuation gate:**
Forward P/E: [X]x vs sector average [X]x
Expected Growth Rate: [X]%
PEG Ratio: [X] — [CHEAP / FAIR / PREMIUM / OVERVALUED / TIER 1 ONLY]
FCF Yield: [X]%
Tier 2 Verdict: [STRONG BUY / ACCEPTABLE / CAUTIOUS / NOT FOR TAXABLE]
One sentence: [Is there still value built into this stock at current price?]

### Check 7 — Macro & Sector Headwinds
- Is the sector under political, regulatory, or tariff attack right now?
- Are there specific news events that create near-term risk?
- What is the current macro environment doing to this position?
- For single country ETFs: political risk, currency risk, trade deal status

---

## The Scoop Format

When presenting research, always use this format for comparisons:

| Metric | [Position A] | [Position B] | Benchmark |
|--------|-------------|-------------|-----------|
| YTD | | | S&P: |
| 1 Year | | | |
| 3 Year | | | |
| 5 Year | | | |
| 10 Year | | | |
| ER | | | |
| AUM | | | |
| Flows | | | |
| Yield | | | |
| Verdict | | | |

Always include an honest verdict row — don't just present data, draw a conclusion.

---

## Top 10 Holdings Comparison

When comparing two ETFs, always pull and compare top 10 holdings side by side. This often reveals:
- Redundancy (high overlap = no diversification benefit)
- Hidden risks (one ETF holding a struggling company at high weight)
- Thesis validation (does it actually own what it claims to?)

---

## Pre-Recommendation Checklist Output

Before giving any recommendation, explicitly state:

**Pre-Recommendation Check: [TICKER]**
- ✅ or ❌ Price & Range: [finding]
- ✅ or ❌ YTD vs S&P: [finding]
- ✅ or ❌ 30-Day Forecast: [finding]
- ✅ or ❌ MACD Momentum: [BULLISH/BEARISH/NEUTRAL — histogram widening/narrowing — divergence if present] | Conviction impact: [+1/0/-1]
- ✅ or ❌ Historical Performance: [finding]
- ✅ or ❌ Analyst Consensus: [finding]
- ✅ or ❌ Estimate Revision Trend: [BULLISH/NEUTRAL/BEARISH — X up, X down in 30 days]
- ✅ or ❌ Fund Flows: [finding — ETFs only]
- ✅ or ❌ Tier 2 Valuation Gate: [PEG X — CHEAP/FAIR/PREMIUM/TIER 1 ONLY — individual stocks in taxable only]
- ✅ or ❌ Macro Headwinds: [finding]

**Recommendation:** [Buy / Hold / Skip / Wait for pullback]
**Account placement:** [Tier 1 Roth / Tier 2 Taxable / Tier 3 IRA — based on valuation gate]
**Honest concern:** [One sentence on the biggest risk]

---

## Proactive Flagging Rules

These situations require proactive flagging WITHOUT being asked:

1. **Sector under political attack** — drug pricing, managed care, tariffs, DOGE cuts. Flag immediately when relevant news breaks.
2. **Position up 25%+ YTD** — flag before recommending, not after
3. **ETF with sustained outflows** — flag even if performance looks good
4. **AUM under $200M** — liquidity risk, flag always
5. **Earnings within 2 weeks** — flag binary risk, suggest half position
6. **Analyst estimate revisions trending UP before earnings** — flag as pre-earnings buy opportunity with conviction score. Check how many of X analysts raised estimates in last 30 days. 60%+ going up = strong signal.
7. **Analyst estimate revisions trending DOWN before earnings** — flag as warning. Wait until after the print.
8. **30-day forecast negative** — flag before recommending, suggest waiting for pullback
9. **High overlap between two positions** — flag before recommending both
10. **Wash sale risk** — flag before any tax loss harvest recommendation
11. **Leveraged ETF** — flag the daily reset risk always

---

## Basket Construction Rules

When building or reviewing a basket:
1. Every position needs a specific role — no placeholders
2. Check overlap between positions before finalizing weights
3. Auto invest target weights must reflect actual conviction, not safe middle ground
4. Highest conviction names get highest weights — don't default to equal weight
5. Flag any position where the thesis has changed since it was added
6. Check tax implications before recommending any sale for rebalancing

---

## Things To Never Do

- Never recommend something that sounds good on thesis without running all seven checks
- Never present weights without checking current values first
- Never suggest selling without checking wash sale rules
- Never recommend a leveraged ETF without flagging the daily reset risk
- Never recommend a single country ETF without checking YTD vs S&P first
- Never let a basket sit with a broken thesis without proactively flagging it
- Never present "captain obvious" disclaimers — only flag risks that are specific and data-backed
- Never recommend an ETF replacement without checking overlap with existing positions first
- Never assume a gain on VCX or any other position — always verify before discussing tax implications

---

## The User's Standard

This user expects:
- Research done BEFORE recommendations, not after being challenged
- Proactive flagging of headwinds, not reactive acknowledgment
- Honest verdicts, not hedged both-sides analysis
- Weights that reflect real conviction, not safe defaults
- No wasted tokens on things that should have been caught earlier

When in doubt — search first, recommend second.
