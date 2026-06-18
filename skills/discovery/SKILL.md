---
name: discovery
description: >
  AUTHORITATIVE unified discovery skill as of June 18, 2026. Supersedes and replaces
  space-opportunity-scan/SKILL.md, cross-sector-scan/SKILL.md, and
  supply-chain-discovery/SKILL.md. Execute when user says "run discovery", "run the
  scan", "run space scan", "find me something new", "any new names", "cross-sector scan",
  "supply chain discovery", "picks and shovels", "who supplies X", or any request for
  proactive opportunity hunting beyond existing holdings.

  FIVE engines, ONE report:
  ENGINE 1 (Space Discovery): Government contracts, SpaceX manifest, insider buys,
  launch news, SpaceX IPO supply chain.
  ENGINE 2 (Cross-Sector Quality Compounders): Profitable micro/small caps at or near
  ATH/52wk highs with accelerating fundamentals.
  ENGINE 3 (Tier 1 Speculative): Insider buying, oversold with catalyst, binary events,
  conference plays, strategic pivot plays.
  ENGINE 4 (Unusual Options + IEHC Early Warning): Large call sweeps under $2B mkt cap
  with fundamental confirmation + defense/aerospace micro-cap 8-K contract filings,
  OTCQX uplisting, CEO/CFO Form 4 buys in defense SIC codes.
  ENGINE 5 (Supply Chain Discovery + Stealth Catalyst): Layer 2/3 supply chain names
  before they run + 8-K contract filings where price hasn't moved + insider buys on
  flat price names.

  RSI RISING MOMENTUM runs as PRIMARY SCREENER before any engine's fundamentals check.
  MACRO REGIME CHECK runs before RSI screener via GET /macro-regime Railway endpoint.
  Never run individual engines separately. Always one unified report.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

Before stating any stock price, fetch it live:
URL: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`
Do NOT use prices from search snippets, memory, or earlier in the conversation.
If you are about to type a dollar amount next to a ticker, you must have fetched
that price in THIS response first.

---

## STEP 0 — MACRO REGIME CHECK (runs first, gates everything)

```
GET https://web-production-fa80.up.railway.app/macro-regime
```

Returns: `{ "regime": "UPTREND" | "CORRECTION" | "BEAR", "spy_vs_200sma": X%, "qqq_vs_200sma": X% }`

**UPTREND:** Proceed normally. No flags on output.

**CORRECTION:** Flag ALL output with ⚠️ REGIME RISK. Still surface names but note
elevated risk. Range Trader minimum window extends to 7 weeks. No new Tier 1 speculative
entries unless RSI divergence confirmed.

**BEAR:** Flag ALL output with 🚨 BEAR MARKET. Require RSI divergence on every name
before flagging. Favor defensive sectors only (utilities, defense, healthcare staples).
Range Trader minimum 4+ touches, 8 week minimum, must be above own 200 SMA.
Downgrade all 🔴 immediate flags to 🟡 WATCH — no new entries in bear market.

State regime at the top of every scan output. Never skip this step.

---

## STEP 1 — RSI RISING MOMENTUM SCREENER (primary screener, runs before fundamentals)

This runs on every candidate name from every engine BEFORE fundamentals checks.
Data source: FMP `/stock-price-change` and `/quote` endpoints exclusively.
**Never use Alpha Vantage. Never use alphavantage.co. FMP only.**

### [CRITICAL GATEKEEPER: THE COILED SPRING RULE]
To find names BEFORE they run, we require strict divergence: the sector must have
macro momentum, but the individual ticker must be a compressed, coiled spring.
We are NOT looking for names that have already broken out. We are looking for names
that are about to.

**SCREEN OUT — Hard Kill (log and drop immediately):**
- Ticker trailing RSI is above 58 — if RSI > 58, it has already broken out. REJECT IMMEDIATELY.
- RSI flat or falling over last 3 sessions.
- RSI rising on below-average volume all 3 sessions (low-conviction bounce, not accumulation).

**SCREEN IN (proceed to vetting and fundamentals):**
- Ticker trailing RSI is between 40 and 58 AND RSI has been rising for 3 consecutive
  sessions with volume above 20-day average on at least 2 of those 3 days.
- Ticker is above its 200-day SMA OR shows a clear bullish RSI divergence
  (higher RSI low + lower price low simultaneously).

**Priority Tiers (for ranked output):**
- HIGHEST PRIORITY: RSI between 40–50 (maximum runway, completely undiscovered)
- STANDARD PRIORITY: RSI between 51–58 (building immediate breakout strength)

**Note:** RSI below 40 is NOT automatically highest priority — it may indicate
fundamental deterioration rather than a coiled spring. Require volume confirmation
and trend gate pass before elevating. RSI above 58 is a hard kill regardless of
any other signal. No exceptions.

### RSI Screener Output per Name
```
RSI: [PASS/FAIL] | [X] | [Rising/Flat/Falling] [X]sess | Vol:[Y/N] | [HIGHEST/STANDARD/KILL] | Gate:[200SMA/DIV/FAIL] | Spring:[Y/N]
```

---

## PHASE 0 — VETTING GATE (runs after RSI screen passes, before output)

Every candidate runs Checks 1 through 5 via FMP API endpoints immediately.
First KILL stops the sequence. Log every KILL with a specific reason.
Only PASS names proceed to engine scoring.

**CRITICAL EXCEPTION — Checks 6 and 7 are DEFERRED:**
Do NOT run Check 6 or Check 7 on raw candidates. Running web searches on every
candidate simultaneously causes context-window brownout, hallucinated data, and
skipped checks. These two web-search-dependent checks run ONLY on final surviving
names that achieve an Immediate Flag score threshold:
- Engine 1: 8+/14 | Engine 2: 8+/12 | Engine 3: 9+/14 | Engine 4B: 8+/10 | Engine 5: 4+/6
Run Check 6 and Check 7 on those names only, right before generating the final output report.

**FMP Base URL:** `https://financialmodelingprep.com`
**API Key:** stored in Railway environment as FMP_API_KEY — use via backend proxy.

### CHECK 1 — Insider Selling Pattern
```
GET /api/v4/insider-trading-statistics?symbol={TICKER}&apikey={KEY}
```
KILL if: Net sellers > 60% of transactions over trailing 90 days.
PASS if: Net buyers ≥ net sellers, OR mixed with no dominant sell pattern.

### CHECK 2 — Balance Sheet Health
```
GET /api/v4/score?symbol={TICKER}&apikey={KEY}
```
KILL if: Altman Z-Score < 1.8 AND Piotroski F-Score ≤ 2 (both together).
PASS if: Z-Score > 1.8 OR F-Score ≥ 4.

### CHECK 3 — Analyst Coverage & Grade Direction
```
GET /api/v3/grade/{TICKER}?limit=10&apikey={KEY}
```
KILL if: More than 8 analysts covering (no discovery edge).
KILL if: 2 or more downgrades in last 5 grade changes.
PASS if: ≤ 8 analysts AND grade direction flat or improving.

### CHECK 4 — Price Target vs Current Price
```
GET /api/v4/price-target-summary?symbol={TICKER}&apikey={KEY}
```
KILL if: Current price equals or exceeds consensus price target.
FLAG (not kill) if: PT spread > 50% between low and high (note uncertainty).
PASS if: Current price meaningfully below consensus PT.

### CHECK 5 — Legal, Dilution & Structural Overhang
```
GET /api/v3/stock_news?tickers={TICKER}&limit=15&apikey={KEY}
```
KILL if ANY keyword found in last 15 headlines:
"class action" | "SEC investigation" | "going concern" | "shelf registration" |
"ATM offering" | "restatement" | "subpoena" | "dilution" | "default" | "delisted"
Surface the specific headline. Do not just say "news issue found."

### CHECK 6 — Competitive Spec Gap (web search)
Search: `"{COMPANY NAME} vs {INCUMBENT} technology differentiation advantage"`
KILL if: No clear, specific technical differentiation. Vague "next gen" or "AI-powered"
with no concrete spec = commodity risk.
PASS if: Specific defensible moat exists — patented process, sole-source contract,
proprietary material, certified-only supplier status.

### CHECK 7 — Customer Concentration Gate (web search)
Search: `"{COMPANY NAME} 10-K customer concentration revenue"`

Sector-specific thresholds:
- Consumer / Retail / Technology: KILL if any single customer > 30% TTM revenue
  without a signed multi-year contract.
- Aerospace / Defense / Government: KILL if any single customer > 60% TTM revenue
  without a sole-source contract.

Tier reclassification (not a kill): If concentration is within threshold but a
multi-year contract exists, allow passage BUT reclassify to Tier 1 Roth only.
Flag explicitly in output with contract expiry date.

---

## ENGINE 1 — SPACE DISCOVERY

### What to hunt
Names with government contract traction, SpaceX mission exposure, or insider buying —
before the move. Finds MNTS-type names.

### Source 1A — Government Contract Awards
Web search daily:
- `NASA contract award small business space satellite [current month] 2026`
- `DARPA contract award space [current month] 2026`
- `Space Development Agency contract award [current month] 2026`
- `SpaceWERX STRATFI TACFI award [current month] 2026`
- `Space Force contract award publicly traded [current month] 2026`
- `Missile Defense Agency SHIELD task order award 2026`

Flag: Any award to a publicly traded company not already held or on watchlist.
Check restricted-entities skill before flagging.

### Source 1B — SpaceX Manifest / Rideshare Customers
- `SpaceX Transporter rideshare manifest payload customer 2026`
- `SpaceX Transporter [next mission number] payload 2026`

Flag: Publicly traded payload customer, market cap under $500M, not up 50%+ in 30 days.

### Source 1C — SEC Form 4 Insider Buying (Space/Aerospace SIC codes)
Fetch: https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=2&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=50&vh=&ocl=&och=&sic1=3812&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc=&sortcol=0&cnt=20&page=1

Also check SIC 3760, 3769, 4812, 4813 for aerospace/satellite names.
Filter: CEO, CFO, Director only. Open market purchases ("P" code). Min $50K. Last 48hr.
Not automatic 10b5-1 plans.

### Source 1D — Space Industry Newswire
- `site:businesswire.com space satellite contract OR launch OR revenue 2026`
- `site:spacenews.com [current date]`
- `in-orbit services contract NASA DoD 2026`
- `commercial space company first revenue OR first customer 2026`

### Source 1E — SpaceX IPO Supply Chain Watch
- `SpaceX IPO [current date] update`
- `SpaceX supplier OR vendor publicly traded 2026`
- Check FLTCF price vs entry ($5.00–5.50) and flag any move toward T1 ($7.50)

### Space Scoring — The MNTS Test (14 points max)
| Signal | Points |
|--------|--------|
| Government contract with $ amount (NASA/DoD/DARPA/SDA/Space Force) | 3 |
| Cash > 50% of market cap | 2 |
| Director/officer open market purchase last 7 days | 2 |
| Successful mission/launch completed | 2 |
| Quantified backlog or pipeline (not just "interest") | 1 |
| Debt-free or debt being retired | 1 |
| Market cap under $200M | 1 |
| SpaceX rideshare customer (confirmed payload) | 1 |
| Revenue growing or first revenue imminent | 1 |

Thresholds: 8+ = Immediate flag + run AV | 5–7 = Watch list | Below 5 = Skip

Hard disqualifiers: Restricted list | Already held | Already on watchlist |
Up 50%+ in last 30 days | Zero revenue with no government contract traction

**The Expedia Rule — Engine 1 theme validation:**
Level 1 signal (confirms space theme): New Space Force contract CATEGORY opening for
commercial operators, total NASA budget expanding, new government space program launch.
Level 2 signal (company-specific only): RKLB winning a contract LUNR previously held.
Only Level 1 signals confirm or invalidate the space theme. Level 2 only affects the
specific company.

---

## ENGINE 2 — CROSS-SECTOR QUALITY COMPOUNDERS (Tier 2 Taxable)

### What to hunt
Profitable micro/small caps ($50M–$2B market cap) with accelerating fundamentals at
or approaching 52-week or all-time highs. Any sector. Profitability is a HARD REQUIREMENT.
Finds MPTI-type names.

### The MPTI Rule — When ATH Breakouts Are Safe to Buy
All five conditions must be present:
1. Fundamentals accelerating INTO the breakout — EPS beats, backlog growth, margin
   expansion, revenue acceleration. Hope-driven = skip.
2. RSI under 65 at the breakout (Rising Momentum screener already confirmed direction)
3. Low float preferred — under 15M shares means institutional buying moves price fast
4. Visible catalyst — earnings, Investor Day, contract win. Not "vibes."
5. Weekly chart not overbought — the move has legs beyond one session

ATH with all five = entry signal, not a warning. Flag it.

### The CDRE Pattern — Quality at a Discount
Profitable compounder at or near 52-week LOW with:
- Unanimous or near-unanimous analyst Buy ratings
- Record backlog or revenue acceleration despite stock weakness
- RSI recovering from oversold (was under 30, now rising — confirmed by RSI screener)
- Weakness explained by specific, potentially temporary overhang
- Overhang clearing = stock snaps back to analyst targets

### Source 2A — ATH/52wk High Breakout Screen
- `small cap micro cap new 52 week high breakout volume [current month] 2026`
Filter: Market cap $50M–$2B | Volume 1.5x+ 30-day avg | Fundamental catalyst present

### Source 2B — Record Backlog / Revenue Acceleration
- `"record backlog" small cap [current month] 2026`
- `"record revenue" OR "record quarter" small cap [current month] 2026`
- `"raised guidance" "beat estimates" small cap [current month] 2026`

### Source 2C — Investor Day / Analyst Day Calendar
- `"investor day" OR "analyst day" small cap [current month] [next month] 2026`
Finding names 2–3 weeks before Investor Day = the systematic MPTI play.

### Source 2D — Oversold Quality Screen (CDRE Pattern)
- `small cap "52 week low" "buy rating" OR "strong buy" [current month] 2026`
- `small cap RSI oversold "record backlog" OR "beat estimates" 2026`

### Source 2E — Estimate Revision Velocity
Signal: EPS estimates for upcoming quarter AND full year revised UP 5%+ by 3+ analysts
in last 14 days while stock price stayed flat or declined.
- `earnings estimate revision upward small cap [current month] 2026`
- `EPS estimate raised 3 analysts small cap [current month] 2026`

### Cross-Sector Scoring — The MPTI Test (12 points max)
| Signal | Points |
|--------|--------|
| EPS beat last quarter | 2 |
| Revenue beat AND raised guidance | 2 |
| Backlog growing 20%+ YoY | 2 |
| Breaking to 52wk or ATH on volume | 2 |
| RSI under 65 at breakout | 1 |
| Float under 15M shares | 1 |
| Upcoming catalyst within 30 days | 1 |
| Profitable (positive EPS TTM) | 1 |

Thresholds: 8+ = Immediate flag + run AV | 5–7 = Watch list | Below 5 = Skip

Hard disqualifiers: Restricted list | Already held | Already on watchlist |
RSI above 65 (caught by RSI screener) | Stock up 40%+ in last 30 days with no new catalyst

**SaaS/software inclusion rule:** Engine 2 may include profitable software IF:
positive TTM net income AND FCF margin >20% AND PEG <2.0. Pre-revenue or money-losing
software excluded. Pre-profit names: use EV/Forward Revenue instead of PEG.

---

## ENGINE 3 — TIER 1 SPECULATIVE (Roth)

### What to hunt
Asymmetric setups: insider buying on oversold names, binary catalyst events (PDUFA,
contract decisions, trial readouts), conference plays, strategic pivot plays.
The MX fix: strategic pivot + any insider buy + dated catalyst + cash floor = flag
regardless of profitability.

### Source 3A — Insider Buying on Oversold Names
Fetch: https://openinsider.com/screener (CEO/CFO/Director, open market, min $50K, last 48hr)
Cross-reference: RSI screener must confirm rising from oversold.
Flag: Any name where insider buy + RSI rising from below 35 + volume confirmation.

### Source 3B — Binary Catalyst Calendar
- `PDUFA date [current month] [next month] 2026 small cap biotech`
- `FDA decision [current month] 2026 small cap`
- `Phase 3 readout [current month] 2026`
- `DoD contract decision [current month] 2026 small cap`

Flag: Names 15–45 days from binary catalyst, not already up 100%+ from 52wk low.

### Source 3C — Conference Calendar Plays
- `biotech conference [current month] 2026 presentation small cap`
- `defense conference [current month] 2026 small cap presenting`
- `investor conference catalyst [current month] 2026`

### Source 3D — Strategic Pivot Screen
- `company pivoting to [AI / defense / space / energy] small cap [current month] 2026`
- Look for: board-level buying + product showcase date + cash floor + pivot to tailwind

### Tier 1 Speculative Scoring (14 points max)
| Signal | Points |
|--------|--------|
| Insider buy: CEO/CFO open market, last 7 days | 3 |
| Insider buy: Director, last 14 days | 2 |
| Binary catalyst with specific date (PDUFA, contract, trial) | 3 |
| Cash > 12 months runway at burn rate | 2 |
| RSI rising from below 35 with volume (RSI screener confirmed) | 2 |
| Asymmetry R/R > 3:1 calculable | 1 |
| Strategic pivot with board-level buy | 1 |

Thresholds: 9+ = Immediate flag + run AV | 6–8 = Watch list | Below 6 = Skip

Hard disqualifiers: Restricted list | Already held | Already on watchlist |
No dated catalyst (a cheap stock with insider buying and no catalyst is a value trap)
| Already up 100%+ from 52wk low (asymmetry gone)

---

## ENGINE 4 — UNUSUAL OPTIONS + IEHC EARLY WARNING

### Part A — Unusual Options Activity
Large call sweeps under $2B market cap with fundamental confirmation.
Options flow alone = noise. Options flow + Engine 2 or 3 scoring = actionable.

Sources:
- Unusual call sweep screens (unusualwhales.com, Barchart unusual options)
- Dark pool / block trade cross-reference

### Options Scoring (8 points max)
| Signal | Points |
|--------|--------|
| Call sweep > 10x normal volume | 3 |
| OTM calls expiring 30–90 days out | 2 |
| Multiple sweeps same strike same day | 2 |
| Dark pool block same day as sweep | 1 |

Options flag only produced when: Options Score 6+/8 AND Engine 2 score 5+/12 OR
Engine 3 score 6+/14. Pure flow with no fundamental confirmation = logged but not output.

### Part B — IEHC Early Warning (Defense Micro-Cap)
Finds the next IEHC at $8, not $20. The IEHC signal was visible 3 months before
the move: OTCQX uplisting (Feb 2026), record backlog (Mar 4), $5.1M Patriot contract
(Mar 24). Engine 4B fires on FILINGS, not price movement.

Source 4B-1: 8-K contract award monitor (defense manufacturer SIC codes 3812, 3760, 3769)
- Daily search: `8-K contract award defense aerospace micro cap [current date] 2026`
- SEC EDGAR full-text search: defense SIC codes, sub-$75M market cap, last 48hr

Source 4B-2: OTCQX/OTCQB uplisting feed
- `OTCQX uplisting defense aerospace [current month] 2026`

Source 4B-3: CEO/CFO Form 4 defense SIC screen
- Same openinsider.com screener filtered to SIC 3812, 3760, 3769

Source 4B-4: Backlog acceleration newswire (run every Monday)
- `"record backlog" defense aerospace micro cap manufacturer [current month] 2026`

Engine 4B includes OTC stocks. Liquidity risk noted in output but does not
automatically disqualify — adjusts position sizing only.

### IEHC Scoring (10 points max)
| Signal | Points |
|--------|--------|
| Named defense program contract (PATRIOT/AMRAAM/THAAD/etc) with $ amount | 3 |
| CEO/CFO open market buy, last 14 days | 3 |
| OTCQX or exchange uplisting event | 2 |
| Backlog acceleration announced | 1 |
| Market cap under $75M | 1 |

Thresholds: 8+ = Immediate flag + run AV | 5–7 = Watch list | Below 5 = Skip

---

## ENGINE 5 — SUPPLY CHAIN DISCOVERY + STEALTH CATALYST

### Part A — Supply Chain Discovery
Layer 2/3 suppliers of confirmed momentum themes. Finds the next FORM at $8 before
it runs 354%. Hard filter: under 40% YTD, under 8 analysts, under $3B cap,
lagging headline theme by 25%+ YTD.

### [CRITICAL SYSTEM CONSTRAINT: NO NARRATIVE SELECTION]
The model is strictly banned from choosing a theme based on personal bias, previous
chat history, or the pre-mapped examples below. The pre-mapped theme examples exist
ONLY as Layer 2/3 search term references AFTER the market has mathematically selected
the theme. They are NOT a menu. They are NOT a starting point. The market picks the
theme. The model executes the drill-down.

**Phase 1 — Mathematical Theme Selection (runs before any drill-down):**

Step 1: Query FMP sector and industry performance data for rolling 5-day AND 1-month
returns across all 11 GICS sectors:
- `https://financialmodelingprep.com/api/v3/sector-performance?apikey={KEY}`
- Web search: `best performing sector ETF 5 day 1 month [current date] 2026`

Step 2: Mathematically isolate the TOP 2 sectors/industry groups leading on the
COMBINED 5-day + 1-month rolling trend. Both timeframes must confirm — a sector
that spiked yesterday but is flat on the month does NOT qualify. This captures
institutional accumulation, not single-session noise.

Step 3: Time window enforcement — ALL data used must be from the last 5 trading
days. Any performance data older than 5 trading days is stale and banned from
theme selection. State the exact date range used at the top of Engine 5 output.

Step 4: Cross-reference the top 2 sectors with volume. Search for sub-$500M tickers
inside those sectors. If those tickers are NOT seeing combined average volume of
1.5x+ their 20-day average, DROP the sector and move to the next ranked sector.
Volume must confirm institutional interest, not just price movement.

Step 5: Lock the 2 market-selected sectors as the EXCLUSIVE allowed inputs for the
Layer 2/3 drill-down below. Any theme not backed by this rolling data pass is
BANNED from this session — including Nuclear, Space, Quantum, and any other
pre-mapped theme if the market data does not confirm them today.

Output from Phase 1 (required before any drill-down):
```
ENGINE 5 THEME SELECTION — [DATE RANGE: MM/DD to MM/DD]
SECTOR RANK 1: [Sector] | 5-day: +[X]% | 1-month: +[X]% | Volume confirm: [YES/NO]
SECTOR RANK 2: [Sector] | 5-day: +[X]% | 1-month: +[X]% | Volume confirm: [YES/NO]
LOCKED THEMES FOR THIS SESSION: [Theme 1] | [Theme 2]
BANNED FROM THIS SESSION (market did not confirm): [Any pre-mapped themes that didn't make the cut]
```

**Phase 2 — Drill Layer 2 and Layer 3 (only on market-confirmed themes):**
For each locked theme, ask: "What do the Layer 0 names have to BUY before they
can ship their product?" → That's Layer 2.
Then ask: "What does THAT supplier have to buy?" → That's Layer 3.

**Pre-mapped theme search terms (reference only — use ONLY if market selects that theme):**

NUCLEAR ENERGY — Layer 0 (skip): CCJ, UEC, NLR, SMR names
Layer 2: zircaloy/zirconium alloy suppliers, nuclear-grade valve manufacturers,
specialty alloy for fuel rod cladding, nuclear instrumentation suppliers
Search: "nuclear grade valve manufacturer small cap", "zircaloy supplier micro cap"

POWER INFRASTRUCTURE / AI DATA CENTERS — Layer 0 (skip): CEG, VST, GEV, PWR, ETN, VRT
Layer 2: transformer core manufacturers, high voltage switchgear components, silicon
carbide power modules, grid capacitor manufacturers, liquid cooling components
Search: "transformer core manufacturer small cap", "SiC power module supplier micro cap"

QUANTUM COMPUTING — Layer 0 (skip): IONQ, RGTI, QUBT, IBM quantum
Layer 2: cryogenic microwave cable suppliers, superconducting wire manufacturers,
RF electronics for quantum control, dilution refrigerator components
Search: "cryogenic microwave cable supplier quantum", "superconducting wire manufacturer small cap"

SPACE SUPPLY CHAIN — Layer 0 (skip — Gary holds): RKLB, ASTS, LUNR, RDW, PL
Layer 2: radiation-hardened electronics, satellite propulsion thrusters, reaction
wheels, star trackers, space-grade solar cells
Search: "radiation hardened electronics manufacturer small cap", "satellite thruster supplier micro cap"

MEMORY / SEMICONDUCTOR EQUIPMENT — Layer 0 (skip): MU, NVDA, AMD, TSM, AMAT, KLAC
Layer 2: CMP slurry suppliers, ALD precursor suppliers, specialty semiconductor gases,
advanced packaging substrate manufacturers, quartz components
Search: "CMP slurry chemical supplier semiconductor small cap", "ALD precursor supplier micro cap"

Discovery Filter — Hard Gates (all must pass):
| Filter | Threshold |
|--------|-----------|
| YTD return | Under 40% |
| Analyst coverage | Under 8 analysts |
| Market cap | Under $3B preferred |
| Divergence gap | Lagging theme headline 25%+ YTD |
| Theme momentum | Headline theme confirmed by Phase 1 mathematical selection |

### Part B — Stealth Catalyst Screen
Fixes the "already ran" problem by finding names BEFORE price reacts.

This is Day 1 discovery, not Day 30.

Source 5B-1: 8-K contract filings where price stayed flat
```
GET https://web-production-fa80.up.railway.app/stealth-catalyst
```
Returns names where: 8-K contract filed in last 10 days AND price moved less than 8%.
These are stealth catalysts — institutional positioning has not begun yet.

**HARD RECENCY GATE:** Verify the 8-K document timestamp on SEC EDGAR before
proceeding. If the filing date is older than 5 business days from today's live date,
it is a HARD KILL for Engine 5B — regardless of flat price action. A flat price on
a 3-week-old filing is not stealth; it is a missed opportunity or a value trap.
Log the filing date explicitly in every Engine 5B flag output.

Source 5B-2: Insider Form 4 open-market buys where price is still flat
Same endpoint cross-references Form 4 buys against price movement.

**Triple signal = highest priority regardless of RSI:**
8-K contract filing + insider open-market buy + price flat/down = surface immediately.
This overrides RSI screener priority ranking (but RSI screener still runs for context).

Stealth Catalyst Scoring (6 points max):
| Signal | Points |
|--------|--------|
| 8-K contract filing, price moved < 8% in 10 days | 3 |
| Insider open-market buy within 5 days of 8-K | 2 |
| Price flat or down since filing (institutional not in yet) | 1 |

Threshold: 4+ = Surface immediately | Below 4 = add to watch

---

## EXECUTION ORDER (every run)

1. **STEP 0:** GET /macro-regime → state regime at top of output
2. **RSI SCREENER:** Run on all candidate names from all engines
3. **PHASE 0 VETTING:** Run on all RSI-passing names
4. **ENGINES 1–5:** Run simultaneously (parallel searches)
5. **DEDUP:** Remove any name appearing in multiple engines — list once, note all engines that caught it
6. **PHASE 0 GATE:** Apply vetting checks to all surviving names
7. **OUTPUT:** Ranked by priority tier (HIGHEST RSI priority first within each engine)

All qualifying names surfaced — no artificial cap on output count.
All 11 GICS sectors covered on every run — no sector anchoring.
Check restricted-entities skill before flagging any name. No exceptions.

---

## CONVICTION PRE-SCORE (shown on every surfaced name)

🔵 Likely 7+ = RSI rising from below 35 + volume confirm + strong engine score + catalyst
🟡 Likely 5–6 = RSI rising 35–50 + moderate engine score + catalyst present
⚪ Filtered out = failed RSI screen or Phase 0 vetting gate

---

## OUTPUT FORMAT

```
═══════════════════════════════════════════════════════
DISCOVERY SCAN 🔭 [DATE] [TIME ET]
MACRO REGIME: [UPTREND ✅ / CORRECTION ⚠️ / BEAR 🚨]
SPY vs 200 SMA: [X]% | QQQ vs 200 SMA: [X]%
═══════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ENGINE 1 — SPACE DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ Government contract awards (NASA/DARPA/SDA/SpaceWERX/Space Force)
✅ SpaceX manifest/rideshare customers
✅ SEC Form 4 insider filings (last 48hr, space SIC codes)
✅ Space industry newswire
✅ SpaceX IPO supply chain watch

🔴 SPACE IMMEDIATE FLAG [Score 8+/14]:
TICKER: [TICKER — Company Name]
MNTS SCORE: [X]/14
RSI: PASS | [X] | Rising [X]sess | Vol✅ | [HIGHEST/STANDARD]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
PRICE: $[X] | Mkt Cap: $[X]M | Cash: $[X]M
SIGNALS:
  ✅ [Signal — specific detail and source]
  ✅ [Signal — specific detail and source]
  ❌ [Signal not met]
SOURCE: [Exact source — SAM.gov link, Form 4 filing date, press release URL]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

[If nothing:] "No space names score 8+/14 today."

🟡 SPACE WATCH LIST [Score 5–7]:
[TICKER] | [X]/14 | RSI [X] [Rising/Flat] | $[X] | [One line: what fired and source]

📡 SPACEX IPO WATCH:
FLTCF: $[X] vs entry $[X] | [Action note]
New supply chain names: [TICKER or "None"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ENGINE 2 — CROSS-SECTOR QUALITY COMPOUNDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ ATH/52wk high breakout screen
✅ Record backlog/revenue acceleration newswire
✅ Investor Day / Analyst Day calendar
✅ Oversold quality screen (CDRE pattern)
✅ Estimate revision velocity

🔴 CROSS-SECTOR IMMEDIATE FLAG [Score 8+/12]:
TICKER: [TICKER — Company Name] | SECTOR: [X]
MPTI SCORE: [X]/12
RSI: PASS | [X] | Rising [X]sess | Vol✅ | [HIGHEST/STANDARD]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
PRICE: $[X] | vs 52wk High: $[X] ([AT HIGH / BREAKING OUT / X% from high])
THE MPTI RULE: [List which of 5 ATH-safe conditions are met]
CATALYST: [Specific upcoming event]
TIER: Tier 2 Taxable
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X]
→ Run AV conviction on [TICKER]

[If nothing:] "No cross-sector names score 8+/12 today."

🟡 CROSS-SECTOR WATCH LIST [Score 5–7]:
[TICKER] | [X]/12 | RSI [X] [Rising/Flat] | $[X] | [One line: what fired, sector, catalyst]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ ENGINE 3 — TIER 1 SPECULATIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 TIER 1 SPECULATIVE IMMEDIATE FLAG [Score 9+/14]:
TICKER: [TICKER — Company Name]
TIER 1 SCORE: [X]/14
RSI: PASS | [X] | Rising [X]sess | Vol✅ | [HIGHEST/STANDARD]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
PRICE: $[X] | Cash runway: [X] months
CATALYST: [Specific dated event — PDUFA date, contract window, trial readout]
SIGNALS:
  ✅ [Signal — specific detail and source]
  ❌ [Signal not met]
ASYMMETRY: If catalyst hits: $[X]–[X] | If miss: $[X] floor | R/R: [X]:1
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

[If nothing:] "No Tier 1 speculative names score 9+/14 today."

🟡 TIER 1 WATCH LIST [Score 6–8]:
[TICKER] | [X]/14 | RSI [X] [Rising/Flat] | $[X] | [One line: catalyst, cash, what triggered]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ENGINE 4 — UNUSUAL OPTIONS + IEHC EARLY WARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 OPTIONS FLAG [Score 6+/8 with fundamental confirmation]:
TICKER: [TICKER] | SECTOR: [X]
OPTIONS SCORE: [X]/8 | FUNDAMENTAL CONFIRM: Engine [2/3] score [X]
RSI: PASS | [X] | [HIGHEST/STANDARD]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
FLOW: [Strike $[X] calls, [X] contracts, [X]x normal volume, exp [date]]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X]
→ Run AV conviction on [TICKER]

🔴 ENGINE 4B IEHC FLAG [Score 8+/10]:
TICKER: [TICKER — Company Name] | SECTOR: Defense [sub-sector]
IEHC SCORE: [X]/10
RSI: [PASS/FAIL — triple signal names flag regardless of RSI]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
PRICE: $[X] | Mkt Cap: $[X]M
PROGRAMS: [Named defense programs this company supplies]
TRIGGER: [Specific filing or event that fired this flag today]
SIGNALS:
  ✅ [Contract or backlog data with dollar amount]
  ✅ [Insider buy details if present]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

[If nothing:] "Engine 4 clean today — no options flags or defense micro-cap filings."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔩 ENGINE 5 — SUPPLY CHAIN DISCOVERY + STEALTH CATALYST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THEMES WITH MOMENTUM TODAY:
[2–4 confirmed themes, one line each with headline % and signal count]

🚨 STEALTH CATALYST [Triple Signal]:
TICKER: [TICKER — Company Name]
STEALTH SCORE: [X]/6
SIGNAL: 8-K filed [date] + Insider buy [who, $amount, date] + Price [flat/down X%]
RSI: [X] | [Rising/Flat — context only, not a gate for triple signal names]
CONVICTION PRE-SCORE: 🔵 (triple signal auto-elevates)
PRICE: $[X] | Mkt Cap: $[X]M
8-K FILING: [Contract description and dollar amount]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X]
→ Run AV conviction on [TICKER]

🔩 SUPPLY CHAIN DISCOVERY HIT:
THEME: [Theme name] | SUPPLY LAYER: Layer [2/3] — [plain English description]
TICKER: [TICKER — Company Name]
RSI: PASS | [X] | Rising [X]sess | [HIGHEST/STANDARD]
CONVICTION PRE-SCORE: [🔵/🟡/⚪]
WHAT THEY MAKE: [One specific sentence]
WHY UNDISCOVERED: [X] analysts | $[X]M cap | +[X]% YTD vs headline +[X]%
DIVERGENCE GAP: [X]% — window estimated [X] days before closes
DISCOVERY FILTER: ✅ YTD [X]% ✅ Analysts [X] ✅ Cap $[X]B ✅ Gap [X]%
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | TIER: [Tier 1 Roth / Tier 2 Taxable]
→ Run AV conviction on [TICKER]

[If nothing:] "Engine 5 clean today — no stealth catalysts and no supply chain names passing all filters."

═══════════════════════════════════════════════════════
BOTTOM LINE
═══════════════════════════════════════════════════════
[2–3 sentences. The single most actionable name today across all five engines.
Which engine caught it. Whether AV was flagged. Any circuit breaker or regime note.]
═══════════════════════════════════════════════════════
```

---

## UNIVERSAL RULES (apply to all engines)

1. **All five engines run every time.** Never output only some engines.
2. **Check restricted-entities skill before flagging any name.** No exceptions.
3. **RSI Rising Momentum screener runs before fundamentals on every name.** No exceptions.
   Exception: Engine 5B triple-signal names still get RSI context but RSI is not a gate.
4. **Macro Regime Check runs first.** State regime at top. Gate output accordingly.
5. **Never flag a name already up 50%+ in 30 days** unless a new catalyst just dropped.
6. **Always cite the exact source** — SAM.gov link, Form 4 filing date and dollar amount,
   press release URL. Vague sourcing = not actionable.
7. **No duplication across engines.** If a name appears in multiple engines, list it once
   under the highest-conviction engine and note "Also caught by Engine [X]."
8. **Tier placement:**
   - Engine 1 finds → Tier 1 Roth (space/speculative)
   - Engine 2 finds → Tier 2 Taxable (profitable compounders)
   - Engine 3 finds → Tier 1 Roth (speculative, binary)
   - Engine 4A options with Engine 2 confirm → Tier 2 Taxable
   - Engine 4A options with Engine 3 confirm → Tier 1 Roth
   - Engine 4B IEHC → Tier 1 Roth
   - Engine 5A supply chain → Tier 1 or 2 based on profitability
   - Engine 5B stealth catalyst → Tier depends on fundamentals
9. **All qualifying names surfaced — no artificial cap.**
10. **All 11 GICS sectors covered on every run — no sector anchoring.**
11. **Engine 4B fires on filings, not price movement.** Price moving is a disqualifier
    only if stock is already up 100%+ from 52wk low.
12. **If all engines clean, say so in one sentence.** That is a valid and valuable output.
13. **Alpha Vantage is permanently removed.** Never use Alpha Vantage or alphavantage.co
    for any data. FMP only via /stock-price-change and /quote endpoints.
14. **The Expedia Rule — theme validation:** Level 1 signals (category-wide) confirm
    themes. Level 2 signals (competitive reshuffling) only affect the specific company.
    Apply before marking any theme as confirmed.

---

## LESSON LOG (names already discovered — ask "who supplies THEM?")

| Name | Theme | Approx Run | Layer | Next Search |
|------|-------|-----------|-------|-------------|
| FORM (FormFactor) | Quantum | +354% | Layer 1 | Who makes components inside FORM's probe stations? |
| AMAT (Applied Materials) | Memory/semis | +166% | Layer 1 | ENTG, ACMR — check YTD; then ALD precursor suppliers |
| RKLB, ASTS, LUNR | Space | Significant | Layer 1 | Reaction wheel, star tracker, radiation-hardened suppliers |
| CCJ, UEC | Nuclear | Significant | Layer 1 | Zircaloy, specialty alloy, nuclear valve suppliers |
| IEHC | Defense connectors | Found at $20, should have been $8 | Layer 2 | Who supplies IEHC's hyperboloid connector materials? |
| MPTI | Defense components | Found at $85, should have been $72 | Layer 1 | Investor Day was the catalyst — find next Investor Day setup |
| MNTS | Space pre-revenue | Found after 137% run | Pre-Layer 1 | Engine 1 now finds these before the move |

