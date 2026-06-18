---
name: cross-sector-scan
description: >
  Execute EVERY MORNING alongside the space-opportunity-scan. Triggers on "run
  cross-sector scan", "find me something new", "any new names outside space",
  "run discovery", "tier 1 ideas", "tier 2 ideas", or any request for proactive
  opportunity hunting beyond existing holdings in non-space sectors.
  FOUR engines, ONE report: ENGINE 1 (Tier 2 Quality): Profitable micro/small caps
  at or near ATH/52wk highs with accelerating fundamentals. ENGINE 2 (Tier 1
  Speculative): Insider buying, oversold with catalyst, binary events, conference
  plays, and strategic pivot plays (the MX fix). ENGINE 3 (Unusual Options): Large
  call sweeps under $2B mkt cap with fundamental confirmation. ENGINE 4 (IEHC Early
  Warning): Daily monitor of defense/aerospace micro-cap 8-K contract filings,
  OTCQX uplisting announcements, and CEO/CFO Form 4 buys in defense SIC codes —
  finds the next IEHC at $8 not $20. Run daily. Never weekly. Integrates with
  space-opportunity-scan — never duplicate findings between the two scans.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from the Railway FMP service.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This fetches directly via web_fetch — no prior search required. Returns live price, change, day range, 52-week range, volume. Do NOT use prices from search snippets, memory, or earlier in the conversation — those go stale within minutes.

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---



# Cross-Sector Opportunity Scan

## Core Philosophy

Every sector has its version of the MNTS and MPTI trades. The signals are the same —
government contracts, insider buying, record backlogs, oversold quality names — they
just show up in healthcare, industrials, energy, cybersecurity, and specialty finance
instead of space. This skill hunts them systematically every day.

**The five failure modes this scan eliminates:**
- **MPTI failure (Tier 2):** Profitable compounder with record backlog and upcoming
  Investor Day catalyst sitting 10% below ATH — found at $85 instead of $72.
- **MNTS failure (Tier 1):** Pre-revenue name with government contract traction, cash
  floor, and insider buying — found after it already 2x'd.
- **Institutional positioning failure:** Large unusual call sweep on a micro-cap 3
  weeks before a catalyst — ignored because it wasn't in existing holdings.
- **MX failure (Tier 1 Pivot):** Early-revenue turnaround company pivoting toward a
  secular tailwind (AI server power chips) with board-level buying and a dated product
  showcase — missed because it wasn't profitable (Engine 1 disqualifier) and had no
  CEO/CFO buy (Engine 2 gap). Strategic pivot + any insider buy + dated catalyst +
  cash floor = Engine 2 flag regardless of profitability or who specifically bought.
- **IEHC failure (Engine 4):** Defense/aerospace niche component manufacturer —
  hyperboloid connectors for PATRIOT/AMRAAM/THAAD — found at $20 ATH instead of $8
  when the stock was still at early price discovery. The signal was visible 3 months
  earlier: OTCQX uplisting (Feb 2026), record backlog announcement (Mar 4), $5.1M
  Patriot contract (Mar 24). None of those triggered a flag because there was no
  dedicated monitor for sub-$50M defense manufacturer SEC filings. Engine 4 fixes this.

---

## ENGINE 1 — TIER 2 QUALITY COMPOUNDER HUNT

### What to hunt
Profitable micro/small caps ($50M–$2B market cap) with accelerating fundamentals
at or approaching 52-week or all-time highs. Any sector. Profitability is a HARD
REQUIREMENT — no pre-revenue names here.

### The MPTI Rule — When ATH Breakouts Are Safe to Buy
All five conditions must be present to flag as immediate:
1. Fundamentals accelerating INTO the breakout — EPS beats, backlog growth, margin
   expansion, revenue acceleration. Stock running on hope = skip.
2. RSI under 70 at the breakout — room to run, not exhausted
3. Low float preferred — under 15M shares means institutional buying moves price fast
4. Visible catalyst — earnings, Investor Day, contract win, product launch, not "vibes"
5. Weekly chart not overbought — the move has legs beyond one session

ATH with all five = entry signal, not a warning. Flag it immediately.

### The CDRE Pattern — Quality at a Discount
The inverse: profitable compounder at or near 52-week LOW with:
- Unanimous or near-unanimous analyst Buy ratings
- Record backlog or revenue acceleration despite stock weakness
- RSI recovering from oversold (was under 30, now rising)
- Weakness explained by a specific, potentially temporary overhang
  (shelf filing, acquisition dilution, sector rotation, macro fear)
- Overhang clearing = stock snaps back to analyst targets

Both patterns flagged daily. MPTI is the breakout version. CDRE is the discount version.

### Source 1A — ATH/52wk High Breakout Screen
Fetch daily via web search:
- `site:stockanalysis.com screener 52 week high small cap [current date]`
- Web search: `small cap micro cap new 52 week high breakout volume defense industrial
  healthcare technology [current month] 2026`

Filter results for:
- Market cap $50M–$2B
- Volume 1.5x+ 30-day average on breakout day
- Has a fundamental catalyst (not a pure technical breakout on no news)
- Not already held, on watch list, or restricted

### Source 1B — Record Backlog / Revenue Acceleration Newswire
Web search daily:
- `"record backlog" small cap [current month] 2026`
- `"record revenue" OR "record quarter" small cap [current month] 2026`
- `"raised guidance" "beat estimates" small cap [current month] 2026`
- `"book-to-bill" small cap defense industrial [current month] 2026`

Flag: Any micro/small cap with accelerating backlog AND revenue beat, profitable,
not already in portfolio or watch list.

### Source 1C — Investor Day / Analyst Day Calendar
Web search every morning:
- `"investor day" OR "analyst day" small cap [current month] [next month] 2026`
- `"capital markets day" small cap 2026`

Flag: Any profitable micro/small cap with upcoming Investor Day not yet in price.
MPTI's May 12 Investor Day was the re-rating event. Finding it May 1 was the edge.
Finding names 2–3 weeks before their Investor Day = the systematic MPTI play.

### Source 1D — Oversold Quality Screen (CDRE Pattern)
Web search daily:
- `small cap "52 week low" OR "near 52 week low" defense industrial healthcare
  "buy rating" OR "strong buy" [current month] 2026`
- `small cap RSI oversold "record backlog" OR "beat estimates" 2026`

Flag: Profitable names near 52wk low with analyst Buy consensus and a specific
temporary overhang. RSI recovering from sub-30 is the entry setup.

### Source 1E — Estimate Revision Velocity Screen ⚡ (STANDALONE DAILY)

**Why this is a standalone source and not just a pre-earnings check:**
Earnings revisions are the single most reliable predictor of medium-term stock
outperformance. A name where analysts are scrambling to raise numbers WHILE THE
STOCK STAYS FLAT is the setup before it moves — not after. This is the valuation
compression loop: earnings power increasing, price not yet reflecting it. This
screen runs daily across the full Engine 1 universe, not just names with upcoming
earnings.

**The signal:** EPS estimates for the upcoming quarter AND full year revised UP
by 5%+ by at least 3 different analysts in the last 14 days, while the stock price
has remained flat or declined over the same period.

**Run daily:**
- Web search: `earnings estimate revision upward small cap [current month] 2026`
- Web search: `EPS estimate raised 3 analysts small cap [current month] 2026`
- Web search: `consensus estimate increase "small cap" OR "micro cap" [current month] 2026`
- For any Engine 1 candidate already identified: search `[TICKER] earnings estimate
  revisions [current month] 2026` on stockanalysis.com

**What to look for:**
- 3+ analysts raised both quarterly AND annual EPS estimates in last 14 days
- Revision magnitude: 5%+ increase (not rounding adjustments)
- Stock price flat or down during the same 14-day window (compression = opportunity)
- Bearish revisions (estimates going DOWN) = automatic Engine 1 disqualifier
  regardless of other signals — flag as WARNING, do not recommend

**Why the price-flat requirement matters:**
If the stock already ripped 20% while estimates were rising, the opportunity has
been captured. The edge is in names where the analyst upgrade cycle is ahead of
the price move. Find them before the market prices in the revision.

**Flag format:** "Revision Velocity Hit: [TICKER] — [X] analysts raised EPS [X]%
in 14 days, stock flat/down [X]% same period. Compression window open."

### Source 1F — Institutional Footprint Screen (13F Daily Monitor) 🏦

**Why this exists:**
High-conviction small-cap funds (Wasatch, Artisan, Brown Advisory, Royce, Silvercrest)
move micro/small cap stocks meaningfully when they initiate. A new position from
Wasatch in a $300M market cap company is a structural re-rating event — they do
months of due diligence before buying, and their ownership attracts other
institutional buyers behind them. Finding the initiation before the stock re-rates
is the edge.

**Why daily, not weekly:**
13F filings are not released in a single batch at quarter-end. They file on a
rolling basis throughout the 45-day window after quarter-end. New 13Fs hit SEC
EDGAR every business day. Checking daily means catching a filing the day it drops
— not 6 days later.

**The 45-day lag caveat:** 13F data shows where smart money WAS at quarter-end,
not necessarily today. Weight it as confirmation, not sole trigger. A Wasatch
initiation in Q1 that hasn't yet moved the stock by mid-May is the ideal setup —
the position is real, the price hasn't reflected it yet.

**Target funds — these are the ones that matter for your style:**
- **Wasatch Advisors** — premier micro/small cap growth, deep fundamental research
- **Artisan Partners** — small/mid growth, high-conviction concentrated portfolios
- **Brown Advisory** — small cap growth, quality-focused
- **Royce Investment Partners** — small cap value specialists
- **Silvercrest Asset Management** — quality small cap, long-term holders
- **Polen Capital** — concentrated growth, high-quality businesses only
- **Driehaus Capital** — small/mid cap growth momentum

**Run daily:**
- Web search: `13F new filing [fund name] small cap initiation [current month] 2026`
  Run for each target fund above, rotating daily (all 7 over the course of a week)
- Web search: `Wasatch Advisors 13F new positions [current quarter] 2026`
- SEC EDGAR full-text search: `https://efts.sec.gov/LATEST/search-index?q=%22wasatch%22&dateRange=custom&startdt=[yesterday]&enddt=[today]&forms=13F-HR`
- WhaleWisdom or 13F.info: filter by fund CIK, sort by most recent filing date,
  look at "new positions" tab specifically

**What to look for:**
- Fund initiated a NEW position (not added to existing) in the last 45 days
- Company market cap under $2B at time of filing
- Fund owns 1%+ of shares outstanding (meaningful position, not a rounding error)
- Stock has NOT moved 25%+ since the filing date (opportunity still open)
- Fund has a track record of holding 12+ months (not a trader — a validator)

**Cross-reference required:** Any 13F initiation hit MUST also pass Engine 1
fundamentals check (profitable, accelerating metrics) before flagging. A fund
buy alone is not enough — it's the combination of smart money entry + fundamental
confirmation that produces the signal.

**Flag format:** "13F Initiation: [TICKER] — [Fund] initiated [X shares / $XM]
in Q[X] 2026. Stock [up/flat/down X%] since filing. Market cap $[X]M.
[Fund track record note]. Cross-referencing Engine 1 fundamentals now."

### Engine 1 Scoring — The MPTI/CDRE Test (16 points max)
| Signal | Points |
|--------|--------|
| Profitable (positive EPS TTM) — HARD REQUIREMENT | 0 (disqualifier if absent) |
| EPS beat last quarter (actual > consensus) | 2 |
| Revenue beat AND raised guidance | 2 |
| Backlog growing 20%+ YoY OR record backlog | 2 |
| Breaking to 52wk/ATH high on volume OR recovering from oversold RSI | 2 |
| RSI under 70 (breakout) or RSI rising from under 30 (discount) | 1 |
| Upcoming catalyst within 30 days | 1 |
| Analyst consensus Buy or Strong Buy (majority) | 1 |
| Float under 15M shares | 1 |
| Estimate revision velocity: 3+ analysts raised EPS 5%+ in 14 days, stock flat/down | 2 |
| 13F initiation by target fund, stock not yet moved 25%+ since filing | 2 |

**Thresholds:** 10+ = Immediate flag + run AV conviction | 5–9 = Watch list | Below 5 = Skip

**Hard disqualifiers:** Not profitable | On restricted list | Already held |
Already on watch list | RSI above 75 | Up 40%+ in last 30 days with no new catalyst |
CEO/insider selling into weakness with no buyback program |
Estimate revisions trending DOWN (automatic disqualifier regardless of other signals)

---

## ENGINE 2 — TIER 1 SPECULATIVE HUNT (Cross-Sector)

### What to hunt
Pre-revenue or early-revenue micro-caps ($10M–$300M market cap) with:
- Minimum 12 months cash runway (cash floor provides downside support)
- A specific dated catalyst within 60–90 days
- Insider buying by CEO/CFO/Director in open market
- A definable thesis that could produce 3–10x if the catalyst hits

These are binary-outcome bets. The goal is asymmetric risk/reward with defined
resolution windows — not hope-based holding. No catalyst = no flag.

### Source 2A — SEC Form 4 Insider Buying — All Sectors, Micro-Cap
Fetch daily:
- https://openinsider.com/screener?s=&o=&pl=&ph=1&ll=&lh=300&fd=2&fdr=&td=0&tdr=
  &fdlyl=&fdlyh=&daysago=&xp=1&vl=50&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999
  &grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc=&sortcol=0&cnt=40&page=1

Filter: CEO, CFO, or Director only. "P" transaction code (purchase). "D" ownership
(direct, not indirect/trust). Minimum $50K purchase value. Filed last 48 hours.
Market cap under $300M. NOT automatic 10b5-1 plan sales.

Web search supplement:
- `SEC Form 4 insider purchase micro cap [current month] 2026 CEO CFO director open market`
- `insider buying small cap biotechnology medical device energy [current month] 2026`

**What to do with finds:** Cross-reference against cash position and catalyst calendar.
A CEO buying $200K of stock at $3 means nothing without: (a) cash runway > 12 months,
and (b) a specific upcoming catalyst. With both, it's a Tier 1 candidate.

### Source 2B — FDA Catalyst Calendar (Biotech/MedTech Binary Events)
Web search weekly (every Monday) and daily during active weeks:
- `PDUFA date FDA approval decision [current month] [next month] 2026 small cap`
- `FDA advisory committee meeting small cap biotech [current month] 2026`
- `phase 3 results expected small cap biotech [current month] 2026`

Flag: Any profitable-enough micro-cap (cash > 12 months runway) with:
- PDUFA or Phase 3 readout within 60 days
- Insider buying in last 30 days
- Stock not already up 100%+ from 52wk low (pre-run only)

Note: Do NOT flag pure binary biotech without insider buying confirmation.
The insider buy requirement filters out most of the lottery tickets.

### Source 2C — Small Cap Conference Presentations
Web search weekly (every Monday):
- `HC Wainwright conference presenting companies [current month] 2026`
- `Needham conference small cap presenting [current month] 2026`
- `Canaccord Genuity conference small cap [current month] 2026`
- `Oppenheimer conference presenting [current month] 2026`
- `"first time presenting" institutional conference small cap 2026`

Flag: Any micro-cap presenting for the first time at a major institutional conference,
with real revenue or government contract traction, not already on radar. Companies
presenting for the first time to institutional audiences often pop 20–40% in the
two weeks after as new investors discover them.

### Source 2D — 52-Week Low Reversal with Catalyst (Non-Space)
Web search daily:
- `micro cap "52 week low" OR "all time low" insider buying [current month] 2026`
- `micro cap "going concern" resolved OR cash raised [current month] 2026`
- `micro cap "contract award" OR "FDA approval" 52 week low 2026`

Flag: Any name at or near 52-week low where:
- Cash covers 40%+ of market cap (downside floor)
- Specific dated catalyst within 60 days
- RSI under 35
- Not a zombie company — real product, real customers, real revenue path

This is the MNTS pattern applied to every sector. MNTS at $3.11 with $26M cash
vs $35M market cap and Vigoride 7 in orbit was exactly this.

### Source 2F — Strategic Pivot + Board Buying Screen ⚡ (THE MX FIX)

**Why this exists:** MX (Magnachip Semiconductor) ran 200%+ in May 2026 after pivoting
from OLED display chips to AI server power MOSFETs for data centers, EVs, and solar.
The setup was visible weeks before: multiple board-level open market purchases, a
defined strategic pivot with a product showcase catalyst (PCIM Europe), and a balance
sheet with cash covering 40%+ of market cap. MX failed Engine 1 (not yet profitable)
and Engine 2 (no CEO/CFO buy — only directors). It fell into a gap and was missed.

**The MX Pattern — Early-Revenue Turnaround with Strategic Pivot:**
A company with:
- Existing revenue (not pre-revenue) but still losing money
- Active management pivot toward a high-demand secular tailwind (AI, EV, defense, etc.)
- Board/Director open market purchases (CEO/CFO preferred but NOT required here)
- Cash covering 30%+ of market cap (survival not in question)
- A specific dated event showcasing the new strategy (conference, product launch, demo)
- Stock still near 52-week lows OR just starting to break out (not already 100%+ run)

**This is NOT Engine 1** (requires profitability) and **NOT standard Engine 2** (requires
CEO/CFO specifically). It lives between them. Flag it as Tier 1 Roth — speculative
turnaround with asymmetric upside if the pivot gains traction.

**How to run it daily:**
Web search:
- `small cap semiconductor industrial "strategic pivot" OR "new market" OR "product transition" insider buy 2026`
- `micro cap "board member" OR "director" open market purchase turnaround 2026`
- `small cap "pivoting to" OR "expanding into" AI data center EV defense solar [current month] 2026`
- `micro cap revenue declining "new product" OR "new market" conference presentation [current month] 2026`

**For each find, check 5 signals:**
| Signal | Pass |
|--------|------|
| Existing revenue (not zero) — turnaround, not startup | ✅ required |
| Cash ≥ 30% of market cap | ✅ required |
| Director OR CEO/CFO open market purchase (any insider buy) in last 60 days | ✅ required |
| Specific dated catalyst showcasing the pivot (conference, launch, product demo) | ✅ required |
| Stock NOT already up 100%+ from 52wk low | ✅ required |

All 5 = flag immediately as Tier 1 Roth speculative. Missing any 1 = watch list only.

**The MX Rule:** If a name already ran 100%+ on the pivot narrative, do NOT
present it as a new entry. Log it as "missed — post-move" and add to watch list
for pullback entry only.

### Source 2E — Reverse Merger / SPAC Completion Watch
Web search weekly:
- `SPAC merger completed [current month] 2026 small cap`
- `reverse merger completed publicly traded [current month] 2026`
- `de-SPAC trading small cap [current month] 2026`

Flag: Any recently completed SPAC or reverse merger where:
- Underlying business has real revenue (not concept stage)
- SPAC redemption selling pressure has created a price dislocation
- Insider buying post-merger completion
- Market cap under $300M post-redemption

### Engine 2 Scoring — The MNTS Test Cross-Sector (16 points max)
| Signal | Points |
|--------|--------|
| Cash > 40% of market cap (downside floor) | 3 |
| Specific dated catalyst within 60 days (FDA, earnings, contract, conference, product launch) | 3 |
| CEO/CFO open market purchase last 14 days | 2 |
| Director open market purchase last 30 days (if no CEO/CFO buy) | 1 |
| RSI under 35 — oversold | 2 |
| Revenue exists OR first revenue contract signed | 1 |
| Debt-free or debt < cash | 1 |
| Market cap under $150M | 1 |
| Conference presentation scheduled within 30 days | 1 |
| Active strategic pivot toward secular tailwind (AI, EV, defense, space, energy) | 1 |

**Thresholds:** 9+ = Immediate flag + run AV | 6–8 = Watch list | Below 6 = Skip

**Hard disqualifiers:** On restricted list | Already held | Already on watch list |
Cash runway under 6 months | No specific dated catalyst | Stock already up 100%+
from 52wk low | Zero revenue AND no government/FDA/commercial contract traction

**MX Rule:** Director-only buying (no CEO/CFO) + strategic pivot + dated showcase
catalyst = still flaggable at 9+ score. Do not auto-disqualify for absence of
CEO/CFO buy when all other Engine 2 signals are strong.

---

## ENGINE 3 — OPTIONS OPEN INTEREST ACCUMULATION

### What to hunt
Institutional positioning through MULTI-DAY open interest (OI) buildup in OTM
calls on micro/small cap names, 2–4 weeks before a catalyst. The thesis: someone
always knows, and deliberate accumulation over 3+ consecutive days is more
meaningful than a single sweep.

**Why multi-day OI accumulation instead of single-day sweeps:**
Single-day call sweeps are ephemeral — by the time a daily web search surfaces
them, the move has already happened and you're chasing. Multi-day OI buildup is
cumulative and visible in a daily scan without real-time infrastructure. An
institution building a position over 3+ days before a catalyst is more deliberate
and more reliable than one large order. If real-time sweep alerts are ever added
(Unusual Whales, Cheddar Flow, Market Chameleon), upgrade this engine accordingly.
Until then, OI accumulation is the executable version.

### Source 3A — Multi-Day OI Accumulation Screen (Watch List Names)
Run weekly (every Monday) on names already on the watch list and Engine 1/2 flags:
- Web search: `[TICKER] options open interest call buildup [current month] 2026`
- Web search: `[TICKER] unusual options open interest increase OTM calls 2026`
- Look for: OTM call OI rising 3+ consecutive sessions, expiration 30–90 days out,
  NOT explained by a covered call or protective hedge (check context)

**Only run on names that already score 5+ on Engine 1 or Engine 2.**
Do not hunt OI accumulation on random names — fundamental confirmation first,
options signal second.

### Source 3B — Weekly Broad OI Scan
Run weekly (every Monday):
- Web search: `unusual options open interest buildup small cap [current week] 2026`
- Web search: `OTM call open interest surge micro cap [current month] 2026`
- Web search: `options positioning institutional small cap defense healthcare 
  technology [current month] 2026`

Filter results: OTM calls only (not ATM/ITM hedges). Expiration 30–90 days.
Market cap under $2B. Cross-reference any find against Engine 1 and Engine 2
for fundamental confirmation before flagging.

### Engine 3 Scoring (8 points max)
| Signal | Points |
|--------|--------|
| OTM call OI rising 3+ consecutive sessions | 3 |
| OI increase is 3x+ the 20-day average daily OI change | 2 |
| Expiration 30–90 days out (not 0DTE gambling) | 1 |
| Also scores 5+ on Engine 1 OR Engine 2 (fundamental confirmation) | 2 |

**Thresholds:** 6+ with fundamental confirmation = Immediate flag + run AV |
4–5 = Watch list | Below 4 = Note only, don't present

**Hard disqualifier:** Options signal without ANY fundamental confirmation = skip.
OI buildup on a name with no fundamentals is noise, not signal.

**Upgrade note:** If real-time options flow tools are connected (Unusual Whales,
Cheddar Flow, Market Chameleon), replace Source 3A/3B with live sweep alerts
filtered to: 500%+ volume vs 20-day avg, OTM calls, 30–90 day expiry, market
cap under $2B. The scoring framework stays the same.

---

---

## ENGINE 4 — IEHC EARLY WARNING MONITOR ⚡ (THE IEHC FIX)

### Why this exists

IEHC (IEH Corporation) ran from ~$8 to ~$20 in 3 months on a story that was fully
visible in public filings: OTCQX uplisting (Feb 2026), record backlog announcement
(Mar 4, 2026), $5.1M Patriot contract (Mar 24, 2026). By the time it surfaced in a
scan, the stock had already 2.5x'd from its entry price. The signals were all there —
they just weren't being monitored. Engine 4 is the systematic monitor that catches
the NEXT IEHC at $8 instead of $20.

**The IEHC Pattern:**
A sub-$50M market cap manufacturer of niche defense/aerospace components —
connectors, sensors, precision parts, RF components, optical assemblies, energetic
materials — that supplies directly into named U.S. missile, aircraft, or electronics
defense programs. The company is small enough that a single large contract materially
changes its revenue trajectory, but large enough to have SEC filings and real customers.

**Why these names move:**
1. Contract awards are public via 8-K press releases — the information is free, just
   not aggregated anywhere most traders look
2. Market cap is too small for institutional coverage — no analysts, no alerts
3. OTCQX uplisting is a liquidity event that opens the stock to new buyers
4. CEO buying after a major contract = high-conviction signal with no information lag

---

### Source 4A — Defense Manufacturer 8-K Contract Award Monitor

**Run daily. This is the core of Engine 4.**

Targeted SEC EDGAR full-text search for contract award press releases from
sub-$50M defense manufacturers in the relevant SIC codes:

**SIC codes to monitor:**
- **3812** — Search, Detection, Navigation, Guidance, Aeronautical Systems
- **3489** — Ordnance & Accessories (missile components, warhead parts)
- **3679** — Electronic Components, NEC (connectors, specialty electronics)
- **3769** — Guided Missiles & Space Vehicles, Propulsion Units
- **3812** — Defense Electronics (overlaps, search separately)
- **3728** — Aircraft Parts & Equipment, NEC
- **3812** — Electronic & Other Electrical Equipment

**Daily web search queries (run ALL of these):**
```
site:sec.gov/cgi-bin/browse-edgar "8-K" "contract" "missile" OR "defense" OR "patriot" OR "AMRAAM" OR "THAAD" [current year]
```
```
SEC EDGAR 8-K "contract award" defense aerospace micro cap [current month] [year]
```
```
"contract award" "$" million defense small company 8-K [current month] [year] connector OR sensor OR component
```
```
site:businesswire.com OR site:prnewswire.com "contract award" defense aerospace under $10 million small company [current month] [year]
```
```
"receives order" OR "awarded contract" defense missile radar precision component [current month] [year] small company
```

**Filter criteria — ALL must be met to flag:**
| Criterion | Requirement |
|-----------|------------|
| Market cap | Under $75M (ideally under $50M) |
| Contract size relative to company | Award is ≥ 5% of trailing 12-month revenue |
| Defense program named | Specific program cited (PATRIOT, F-35, Javelin, etc.) — not just "defense customer" |
| Stock not already up 50%+ | Not post-move |
| Company has real manufacturing | Not software, not services — actual hardware |
| Public company (SEC filer) | NYSE American, NASDAQ, OTCQX, OTCQB acceptable |

---

### Source 4B — OTCQX/OTCQB Uplisting Monitor

**Run daily.**

OTCQX uplisting = institutional accessibility event. A defense manufacturer uplisting
from Pink Sheets or OTCID to OTCQX is a direct signal that management is preparing
for institutional ownership and likely has something to announce. IEHC uplisted to
OTCQX on Feb 20, 2026 — six weeks later the stock had 2.5x'd.

**Daily search:**
```
OTCQX uplisting [current month] [year] defense aerospace manufacturer
```
```
"begins trading on OTCQX" OR "uplisted to OTCQX" [current month] [year]
```
```
site:otcmarkets.com "OTCQX" new listing [current month] [year]
```

**Filter:** Company must be in manufacturing (not fintech, not cannabis, not biotech).
Cross-reference any OTCQX uplisting with the company's SIC code and product description.

---

### Source 4C — SIC Code CEO/CFO Form 4 Monitor

**Run daily.**

OpenInsider screener filtered to defense/aerospace manufacturing SIC codes, CEO/CFO
only, open market purchase (P code), last 48 hours, minimum $25K value:

**OpenInsider URL (defense SIC codes, CEO/CFO, last 2 days):**
```
http://openinsider.com/screener?s=&o=&pl=&ph=10&ll=&lh=300&fd=2&fdr=&td=0&tdr=
&fdlyl=&fdlyh=&daysago=&xp=1&vl=25&vh=&ocl=&och=&sic1=3&sicl=3480&sich=3830
&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc=CEO,CFO&sortcol=0&cnt=40&page=1
```

**Web search supplement:**
```
SEC Form 4 CEO purchase defense aerospace component manufacturer [current month] [year] open market
```
```
insider buying defense electronics precision component small company [current month] [year]
```

**What triggers a flag here:** CEO or CFO of a defense/aerospace manufacturer
(not a defense contractor like LMT or RTX — a *supplier*) makes an open-market
purchase of $25K or more. Cross-reference against Source 4A contract calendar —
a CEO buying within 2 weeks of a contract award announcement is the highest-conviction
combination this engine produces.

---

### Source 4D — Defense Supplier Backlog Acceleration Monitor

**Run weekly (every Monday).**

```
"record backlog" defense aerospace component supplier manufacturer [current month] [year]
```
```
"book-to-bill" defense small company "record" OR "all-time high" [current month] [year]
```
```
"backlog" "doubled" OR "record" defense connector sensor precision manufacturing [current year]
```

**Flag:** Any sub-$100M market cap company announcing record backlog or book-to-bill
above 1.5x. Cross-reference with Sources 4A (contract history) and 4C (insider activity).

---

### Engine 4 Scoring — The IEHC Test (10 points max)

| Signal | Points |
|--------|--------|
| Contract award ≥ 5% of TTM revenue, named defense program | 3 |
| CEO or CFO open market purchase last 30 days | 3 |
| OTCQX/OTCQB uplisting OR exchange uplisting last 90 days | 1 |
| Record backlog announcement or book-to-bill > 1.5x | 1 |
| Market cap under $50M (maximum asymmetry) | 1 |
| Stock within 20% of 52-week low (not already run) | 1 |

**Thresholds:**
- **8+/10 = Immediate Engine 4 flag** — this is the IEHC at $8 setup. Run AV conviction immediately.
- **5–7/10 = Engine 4 Watch List** — monitor for CEO buy or contract award to complete the setup
- **Below 5 = Skip** — noise

**Hard disqualifiers:**
- CEO or CFO actively SELLING (not buying) — disqualifies immediately regardless of contract news
- Stock already up 100%+ from 52-week low — post-move, not pre-move
- No named defense program — "defense customer" is insufficient; must be a specific named program
- Market cap above $150M — too large for the asymmetric setup
- On restricted-entities list

---

### Engine 4 Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ENGINE 4 — IEHC EARLY WARNING (Defense Micro-Cap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ 8-K contract award monitor (defense manufacturer SIC codes)
✅ OTCQX/OTCQB uplisting feed
✅ CEO/CFO Form 4 defense SIC screen
✅ Backlog acceleration newswire (weekly)

🔴 ENGINE 4 IMMEDIATE FLAG [Score 8+/10]:
TICKER: [TICKER — Company Name] | SECTOR: Defense [sub-sector]
IEHC SCORE: [X]/10
PRICE: $[X] | Mkt Cap: $[X]M | 52wk Range: $[X]–[X]
PROGRAMS: [Named defense programs this company supplies]
SIGNALS:
  ✅ [Specific contract or backlog data point with dollar amount]
  ✅ [Insider buy: who, how many shares, at what price, when]
  ✅ [Any uplisting or liquidity event]
  ❌ [Signal not met]
TRIGGER: [What specific event fired this flag today — 8-K date, Form 4 date]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

🟡 ENGINE 4 WATCH LIST [Score 5–7]:
[TICKER] | [X]/10 | $[X] | [One line: what signal fired, what's missing]
[e.g.: IEHC-type: contract award + no CEO buy yet | awaiting Form 4]

[If nothing:] "Engine 4 clean today — no defense micro-cap contract or insider filings detected."
```

---

### The IEHC Lesson — permanently embedded

The following timeline is the canonical example of what Engine 4 catches:

- **Feb 20, 2026:** IEHC uplists to OTCQX (Source 4B fires) — stock ~$8–10
- **Mar 4, 2026:** 8-K: record backlog >$23M announced (Source 4A fires) — stock ~$12
- **Mar 24, 2026:** 8-K: $5.1M Patriot contract award (Source 4A fires again) — stock ~$15
- **Apr 1, 2026:** Atrium Research initiates with Buy rating — stock ~$17
- **May 2026:** Cross-sector scan finds IEHC — stock already ~$20 (ATH)

**Engine 4 should have fired on Feb 20.** The gap between Feb 20 and the scan
finding it in May cost approximately 2x in upside. Engine 4 closes that gap.

**Note on CEO selling:** IEHC's CEO was a net seller during this run. That is why
IEHC did NOT qualify even when found — the CEO selling disqualified it. The next
IEHC will qualify if and only if the CEO is a net BUYER. The signal combination
that produces a clean Engine 4 flag is:
**contract award + CEO buying + stock not yet moved = immediate flag.**

---

## Risk & Execution Layer

This layer sits between the engines and the output. Every name that scores high
enough to flag must pass through here before being presented to Gary. This is
how the 7-gate Phase 0 filter (from supply-chain-discovery) integrates with the
cross-sector engines — and where execution timing and position sizing discipline
is enforced.

### Gate 1 — Restricted Entities Check (non-negotiable)
Cross-reference every flagged name against the restricted-entities skill before
presenting it. If restricted: kill it, note "⛔ RESTRICTED — skipping", move on.
Never present a restricted name regardless of how strong the setup looks.

### Gate 2 — Portfolio & Watch List Deduplication
Is the name already held? Already on the watch list? If yes — do not present as
a new opportunity. Instead, note "Already held/watching [TICKER]" in the relevant
engine section and move on. Avoid wasting Gary's decision bandwidth on names
already in the system.

### Gate 3 — The 7-Gate Phase 0 Filter (supply chain names only)
Any name surfaced through supply-chain-discovery that reaches this scan must have
already passed all 7 Phase 0 gates: insider selling pattern, balance sheet health,
analyst coverage & grade direction, price vs PT, legal/dilution overhang,
competitive moat, and customer concentration. If Phase 0 was not already run on
a supply chain name, run it before flagging.

For Engine 1, 2, and 4 names (not supply chain), apply the spirit of Phase 0:
- No "class action", "going concern", "SEC investigation", "ATM offering" in
  recent news (Gate 5 equivalent)
- Insider net sellers >60% trailing 90 days = kill (Gate 1 equivalent)
- Single customer >30% revenue with no multi-year contract = flag, not kill
  (Gate 7 equivalent, reclassify to Tier 1 Roth)

### Gate 4 — Execution Timing Discipline
**Do not present new entry opportunities found in the morning scan as
"act right now at 9:45 AM."** The first 30–45 minutes of the cash session
are noisy — retail order imbalances and overnight algorithms dominate.
Morning gap-ups frequently fade by noon.

**Timing rules by action type:**
| Action | Timing |
|--------|--------|
| Risk management (stops, thesis breaks, earnings reactions) | 9:45 AM — act immediately |
| New entry — Tier 1 Roth speculative | Wait for 10:30 AM open confirmation OR pre-market if conviction is 9+/10 |
| New entry — Tier 2 Taxable compounder | 11:30 AM or later — let morning noise clear |
| New entry — Tier 3 IRA/Simple | Anytime — not time-sensitive |
| Pre-earnings positioning | Any time within the 15–45 day window |
| Watch list addition | No timing constraint |

**Flag language:** When presenting a new opportunity found in the morning scan,
always include: "Entry: [timing recommendation]" — not just a price range.

### Gate 5 — Circuit Breaker Status
If the macro circuit breaker is active (VIX >25 sustained OR S&P >5% below 200 DMA),
ALL new entry flags from Engines 1–4 are suppressed. Downgrade every 🔴 IMMEDIATE
FLAG to 🟡 WATCH LIST until the circuit breaker clears. Stop-loss management
and thesis-break exits remain active regardless.

### Gate 6 — Position Sizing Guardrail
Every flagged name must include a sizing note:
- Engine 1 (Tier 2 Taxable): Standard size — up to $3,000–5,000 initial position
- Engine 2 (Tier 1 Roth speculative): Small size — up to $500–1,000, scale on confirmation
- Engine 3 (OI accumulation confirms Engine 1 or 2): Add 50% to base size if OI signal
  aligns with fundamental flag
- Engine 4 (IEHC-type micro-cap): Small size — $500–1,000 max; binary risk

---

## Execution Order

Run all four engines simultaneously. Use 20–25 parallel search calls total.
After engines complete, run every flagged name through the Risk & Execution Layer
(Gates 1–6) before compiling output. No name reaches the output without clearing
all applicable gates.

**Engine 4 runs in parallel with the others but uses different sources** (SEC EDGAR,
OTC Markets, OpenInsider SIC-filtered). Do not conflate Engine 4 findings with
Engine 2 — they are different screens with different scoring. A name can appear
in both if it meets criteria for each independently.

---

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ENGINE 1 — TIER 2 QUALITY (Cross-Sector)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ ATH/52wk high breakout screen
✅ Record backlog/revenue acceleration newswire
✅ Investor Day / Analyst Day calendar
✅ Oversold quality screen (CDRE pattern)
✅ Estimate revision velocity screen (Source 1E)
✅ 13F institutional footprint — Wasatch/Artisan/Brown/Royce/Silvercrest/Polen/Driehaus (Source 1F)

🔴 TIER 2 IMMEDIATE FLAG [Score 10+/16]:
TICKER: [TICKER — Company Name] | SECTOR: [X]
MPTI/CDRE SCORE: [X]/16
PRICE: $[X] | Mkt Cap: $[X]M
PATTERN: [ATH BREAKOUT / QUALITY AT DISCOUNT / REVISION VELOCITY / 13F INITIATION]
SIGNALS:
  ✅ [Signal — specific data point]
  ✅ [Signal — specific data point]
  ❌ [Signal not met]
CATALYST: [Specific event or trigger]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 2 Taxable
→ Run AV conviction on [TICKER]

[If nothing:] "No Tier 2 names score 10+/16 today."

🟡 TIER 2 WATCH LIST [Score 5–9]:
[TICKER] | [X]/16 | $[X] | [One line: pattern, sector, catalyst]
[If nothing:] "No new Tier 2 watch list candidates today."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ENGINE 2 — TIER 1 SPECULATIVE (Cross-Sector)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ SEC Form 4 insider buying (all sectors, micro-cap, last 48hr)
✅ FDA catalyst calendar (PDUFA/Phase 3 readouts)
✅ Small cap conference presentations
✅ 52-week low reversal with catalyst
✅ SPAC/reverse merger completions

🔴 TIER 1 IMMEDIATE FLAG [Score 9+/14]:
TICKER: [TICKER — Company Name] | SECTOR: [X]
MNTS SCORE: [X]/14
PRICE: $[X] | Mkt Cap: $[X]M | Cash: $[X]M ([X]% of mkt cap)
CATALYST: [Specific dated event — FDA date, conference date, contract window]
SIGNALS:
  ✅ [Signal — specific detail and source]
  ✅ [Signal — specific detail and source]
  ❌ [Signal not met]
ASYMMETRY: [If catalyst hits: $[X]–[X] | If miss: $[X] floor | R/R: [X]:1]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

[If nothing:] "No Tier 1 speculative names score 9+/14 today."

🟡 TIER 1 WATCH LIST [Score 6–8]:
[TICKER] | [X]/14 | $[X] | [One line: catalyst, cash position, what triggered]
[If nothing:] "No new Tier 1 watch list candidates today."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ ENGINE 3 — UNUSUAL OPTIONS (All Sectors)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ Unusual call sweep screen (micro/small cap, under $2B)
✅ Dark pool / block trade cross-reference
✅ Fundamental confirmation cross-check (Engine 1 + 2)

🔴 OPTIONS FLAG [Score 6+/8 with fundamental confirmation]:
TICKER: [TICKER] | SECTOR: [X]
OPTIONS SCORE: [X]/8
FLOW: [Strike $[X] calls, [X] contracts, [X]x normal volume, exp [date]]
FUNDAMENTAL CONFIRMATION: [Engine 1 score [X]/12 OR Engine 2 score [X]/14]
THESIS: [Why the flow + fundamentals = actionable]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X]
→ Run AV conviction on [TICKER]

[If nothing:] "No options flags with fundamental confirmation today."

🟡 OPTIONS WATCH (flow only, no fundamental confirmation yet):
[TICKER] | [X]/8 | $[X] | [One line: flow details — research fundamentals]
[If nothing:] "No unusual flow worth noting today."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ENGINE 4 — IEHC EARLY WARNING (Defense Micro-Cap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ 8-K contract award monitor (defense manufacturer SIC codes)
✅ OTCQX/OTCQB uplisting feed
✅ CEO/CFO Form 4 defense SIC screen
✅ Backlog acceleration newswire (weekly)

🔴 ENGINE 4 IMMEDIATE FLAG [Score 8+/10]:
TICKER: [TICKER — Company Name] | SECTOR: Defense [sub-sector]
IEHC SCORE: [X]/10
PRICE: $[X] | Mkt Cap: $[X]M | 52wk Range: $[X]–[X]
PROGRAMS: [Named defense programs this company supplies]
SIGNALS:
  ✅ [Specific contract or backlog data point with dollar amount]
  ✅ [Insider buy: who, how many shares, at what price, when]
  ✅ [Any uplisting or liquidity event]
  ❌ [Signal not met]
TRIGGER: [What specific event fired this flag today]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X] | TIER: Tier 1 Roth
→ Run AV conviction on [TICKER]

🟡 ENGINE 4 WATCH LIST [Score 5–7]:
[TICKER] | [X]/10 | $[X] | [One line: what signal fired, what's missing]

[If nothing:] "Engine 4 clean today — no defense micro-cap contract or insider filings detected."
```

---

## Integration Rules

1. **Run every morning alongside space-opportunity-scan.** These are two halves of
   the same daily intelligence brief. Never run one without the other being run the
   same morning.

2. **No duplication between scans.** If space-opportunity-scan already flagged a name,
   cross-sector-scan notes "See space scan" and moves on. One mention per name per day.

3. **Check restricted-entities before every flag.** No exceptions, ever.

4. **Tier placement is firm:**
   - Engine 1 finds → Tier 2 Taxable (profitable compounders)
   - Engine 2 finds → Tier 1 Roth (speculative, binary, asymmetric)
   - Engine 3 flags with Engine 1 confirmation → Tier 2 Taxable
   - Engine 3 flags with Engine 2 confirmation → Tier 1 Roth

5. **The catalyst requirement is non-negotiable for Engine 2.** A cheap stock with
   insider buying and no dated catalyst is a value trap. A cheap stock with insider
   buying AND a PDUFA date 6 weeks out is a Tier 1 setup. The catalyst is what
   defines the resolution window and makes the asymmetry calculable.

6. **Never present pure options flow without fundamental confirmation.** Engine 3
   only produces actionable flags when combined with Engine 1 or 2 scoring. Raw
   unusual options on a name with no fundamentals = noise. Logged but not presented.

7. **If all three engines come up empty, say so in one sentence and move on.**
   "Cross-sector scan clean today — no flags across all three engines." That is a
   valid and useful output.

8. **Volume thresholds matter.** Do not flag Engine 2 names that are already up 100%+
   from their 52wk low — the asymmetric setup is gone. The edge is finding them near
   the bottom with the catalyst pending, not after they've already moved.

9. **This scan runs daily because catalysts drop any day.** An FDA decision can be
   announced any morning. A Form 4 filing drops at 5 PM any business day. A contract
   award can hit BusinessWire at 7 AM. Weekly cadence misses all of it.

10. **The combined morning brief** = space-opportunity-scan (Engines 1A/1B/1C/1D/1E)
    + cross-sector-scan (Engines 1/2/3/4) + morning scan (portfolio monitoring) = one
    complete daily intelligence picture. Run all four. Output as one coherent brief.

11. **Engine 4 fires on filings, not price movement.** An 8-K contract award from
    a sub-$75M defense manufacturer is an Engine 4 trigger *regardless of whether
    the stock has moved yet*. The goal is to be in the name before institutional
    coverage begins — which typically lags the 8-K by 2–4 weeks. Price movement
    confirmation is NOT required to flag; it is a disqualifier only if the stock
    has already run 100%+ from its 52-week low.

12. **Engine 4 is the only engine that monitors OTC stocks.** Engines 1–3 focus
    on exchange-listed names. Engine 4 explicitly includes OTCQX and OTCQB names
    because that is where the earliest price discovery happens for niche defense
    manufacturers. OTC liquidity risk is noted in the flag output but does not
    automatically disqualify — it adjusts position sizing.

13. **Weekly cadence for Source 4D (backlog).** Sources 4A, 4B, and 4C run daily.
    Source 4D (backlog acceleration newswire) runs every Monday. Do not skip it —
    the IEHC backlog announcement on Mar 4, 2026 was a Source 4D event that would
    have generated an 8/10 score even without a CEO buy.

14. **Macro Volatility Circuit Breaker applies to all four engines.** Before flagging
    any Immediate Flag (🔴) across any engine: check VIX (sustained >25) and S&P vs
    200 DMA (>5% below). If circuit breaker is active: downgrade all 🔴 flags to
    🟡 WATCH only. No new entries in capital preservation mode. State the circuit
    breaker status at the top of the cross-sector scan output.

15. **The Expedia Rule — apply to all theme and catalyst validation.**
    When confirming a theme (Engines 1 and 2) or validating a catalyst:
    - **Level 1 signals only confirm a theme:** total industry revenue growing,
      government budget expanding the category, macro forces benefiting all players,
      regulatory change opening the market sector-wide.
    - **Level 2 signals do NOT confirm a theme:** Company A winning a contract from
      Company B, peer market share shifts, intra-industry competitive reshuffling.
    A defense company winning a contract that another defense company previously held
    is Level 2 noise — it does not validate the defense theme. The total defense budget
    expanding is Level 1 — it validates the theme. Apply this distinction before
    marking any theme as "confirmed" in Phase 1 and before awarding catalyst points
    in Engine 1 or Engine 2 scoring.

16. **SaaS/software exclusion is NARROWED — not blanket.** Engine 1 (Tier 2 Quality)
    may include profitable software companies IF: positive TTM net income AND FCF
    margin >20% AND PEG <2.0. Pre-revenue or money-losing software remains excluded.
    The risk being avoided is narrative-driven multiple compression — that lives in
    unprofitable software, not in proven cash-generating software businesses.
