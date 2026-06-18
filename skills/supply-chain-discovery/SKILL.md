---
name: supply-chain-discovery
description: >
  Execute when user says "run discovery", "supply chain discovery", "nuts and bolts
  behind X", "picks and shovels", "who supplies X", "find me something early", or
  "discovery zone". Also runs automatically in every morning scan after Step 1.
  Phase 1: discovers which themes have momentum NOW from live market data — never
  hardcoded, finds robotics/bioprinting/any theme we haven't discussed yet.
  Phase 2: drills Layer 2 and Layer 3 of each theme's supply chain, surfacing
  unknown micro/small cap suppliers BEFORE they run. Hard filter: under 40% YTD,
  under 8 analysts, under $3B cap. Any name already up 50%+ YTD is a lesson,
  not a recommendation. Goal: find the NEXT FORM at $8 before it runs 354%.
---

# Supply Chain Discovery Skill

## The One Rule

**The theme list is generated fresh from market data every time.
It is never hardcoded. It is never based only on prior conversations.**

If robotics is flowing and we never discussed it, this skill finds it anyway.
If a theme we've been tracking has stalled, this skill stops looking there.
The market tells us where momentum is. We follow the money, then go one layer deeper.

---

## Discovery Filter — Hard Gates

Every name surfaced must pass ALL of the following before being presented:

| Filter | Threshold | Rationale |
|--------|-----------|-----------|
| YTD return | Under 40% | Over 40% = already discovered by someone |
| Analyst coverage | Under 8 analysts | High coverage = already well known |
| Market cap | Under $3B preferred | Large cap = already priced in |
| Divergence gap | Lagging theme headline 25%+ YTD | The gap IS the opportunity |
| Theme momentum | Headline theme confirmed moving 20%+ YTD | Theme must be real, not speculative |

Any name failing a filter → exclude, go deeper in the hierarchy.
Do not bend the filters. Do not present "close enough" names.

---

## PHASE 0 — VETTING GATE (MANDATORY)

**Every candidate name runs this gate before being presented. No exceptions. No skipping.**

This gate exists because GSIT and POET both had disqualifying information on page one of any
search. They should never have reached Gary. This gate ensures they never do again.

Run all 7 checks in sequence. First KILL stops the sequence — do not run remaining calls.
Log every KILL with the specific reason. Only names that PASS all 7 reach the output.

API key for all calls: `TiUMLS7qhCpwLRIPcJKodOAKn4Bm82RC`
Base URL: `https://financialmodelingprep.com`

---

### CHECK 1 — Insider Selling Pattern

```
GET /api/v4/insider-trading-statistics?symbol={TICKER}&apikey={KEY}
```

**KILL if:** Net sellers > 60% of transactions over the trailing 90 days.
Persistent, one-directional insider selling is the single clearest disqualifier.
Insiders know things analysts don't. If they're all leaving, so are we.

**PASS if:** Net buyers ≥ net sellers, OR mixed activity with no dominant sell pattern.
Heavy insider buying is a positive signal — note it in the output.

---

### CHECK 2 — Balance Sheet Health

```
GET /api/v4/score?symbol={TICKER}&apikey={KEY}
```

Returns Piotroski F-Score (0–9) and Altman Z-Score.

**KILL if:** Altman Z-Score < 1.8 (distress zone) AND Piotroski F-Score ≤ 2.
Either alone is a yellow flag. Both together = structural failure risk. Kill it.

**PASS if:** Z-Score > 1.8 OR F-Score ≥ 4. Note both scores in output.
Z > 3.0 + F ≥ 7 = strong balance sheet — flag as positive.

---

### CHECK 3 — Analyst Coverage & Grade Direction

```
GET /api/v3/grade/{TICKER}?limit=10&apikey={KEY}
```

Two sub-checks:

**KILL if (coverage):** More than 8 analysts covering the stock.
Over 8 = already well-known = no discovery edge. Move on.

**KILL if (direction):** 2 or more downgrades in the last 5 grade changes.
Analysts are late but directionally useful. Two downgrades = deteriorating thesis.

**PASS if:** ≤ 8 analysts AND grade direction is flat or improving.
Note exact analyst count and last 3 grade actions in output.

---

### CHECK 4 — Price Target vs Current Price

```
GET /api/v4/price-target-summary?symbol={TICKER}&apikey={KEY}
```

**KILL if:** Current price already equals or exceeds consensus price target.
No analyst upside left = no institutional buying pressure ahead = why are we here?

**FLAG (do not kill) if:** PT spread is extremely wide (>50% between low and high PT).
Wide spread = high analyst disagreement = uncertainty tax. Note it, let Gary decide.

**PASS if:** Current price is meaningfully below consensus PT with reasonable spread.
Note the PT, current price, and implied upside % in output.

---

### CHECK 5 — Legal, Dilution & Structural Overhang

```
GET /api/v3/stock_news?tickers={TICKER}&limit=15&apikey={KEY}
```

Scan headline and summary text for these exact strings (case-insensitive):

| Keyword | What it signals |
|---------|----------------|
| "class action" | Active shareholder litigation |
| "SEC investigation" | Regulatory enforcement risk |
| "going concern" | Auditor doubts viability |
| "shelf registration" | Dilution machinery loaded |
| "ATM offering" | Active dilution in progress |
| "restatement" | Accounting integrity problem |
| "subpoena" | DOJ/SEC enforcement contact |
| "dilution" | Generic dilution signal |
| "default" | Debt covenant failure |
| "delisted" | Exchange compliance failure |

**KILL if:** Any single keyword match in last 15 headlines.
Surface the specific headline that triggered the kill — do not just say "news issue found."

**PASS if:** Zero keyword matches across all 15 headlines.

---

### CHECK 6 — Competitive Spec Gap (Web Search)

This check cannot be automated. Run one targeted web search:

```
"{COMPANY NAME} vs {INCUMBENT} technology differentiation advantage"
```

Where INCUMBENT = the dominant player in that supply chain layer.

**KILL if:** No clear, specific technical differentiation found. Vague claims like
"next generation" or "AI-powered" with no concrete spec advantage = commodity risk.
If a $10B player does the same thing and has 10x the resources, the micro-cap loses.

**PASS if:** A specific, defensible technical moat exists — patented process,
sole-source contract, proprietary material, or certified-only supplier status.
Quote the specific differentiator in the output.

---

### CHECK 7 — Customer Concentration Gate

This check cannot be automated. Run one targeted web search:

```
"{COMPANY NAME} 10-K customer concentration revenue"
```

Also search: `"{COMPANY NAME} largest customer percent revenue"` and check the most
recent 10-K filing on SEC EDGAR for the "Risk Factors" or "Revenue Concentration" section.

**Why this exists:** A Layer 3 micro-cap losing its sole customer doesn't pull back 20% —
it drops 80% overnight. Micro-cap B2B suppliers in niche defense and industrial supply
chains are frequently commodity price-takers with extreme customer-concentration risk.
This gate is mandatory before any micro-cap enters the output.

**KILL if:** Any single customer accounts for more than 30% of TTM revenue AND the company
has not disclosed a signed multi-year contract or sole-source agreement that makes that
concentration structural rather than fragile. A company with 40% revenue from one customer
AND a 10-year sole-source defense contract is a moat. A company with 40% revenue from one
customer with no long-term agreement is one phone call away from a 70% stock collapse.

**Tier reclassification (do not kill — reclassify):** If concentration is 30–50% but a
multi-year contract exists, allow passage BUT reclassify to Tier 1 Roth only regardless
of profitability. Flag explicitly in output.

**PASS if:** No single customer exceeds 30% of TTM revenue. OR concentration exceeds 30%
but is protected by a multi-year sole-source contract — cite the contract and expiry date.

---

### PHASE 0 Output Format

For every candidate, log the gate result before Phase 2 output:

```
VETTING GATE — {TICKER}
─────────────────────────────────────────
✅ CHECK 1 — Insider: Net buyers 4 / sellers 1 (80% buy) — BULLISH
✅ CHECK 2 — Balance sheet: Z-Score 2.4 / F-Score 6 — HEALTHY
✅ CHECK 3 — Analysts: 3 covering / last 3 grades: 2 Buy, 1 Hold — CLEAN
✅ CHECK 4 — Price target: Current $8.20 / PT consensus $14.00 (+70%) — UPSIDE EXISTS
✅ CHECK 5 — News: Zero red flag keywords in last 15 headlines — CLEAN
✅ CHECK 6 — Spec gap: Sole-source certified supplier for [specific part] — MOAT CONFIRMED
✅ CHECK 7 — Customer concentration: No customer >30% TTM revenue — PASS
STATUS: ✅ PASSED ALL GATES — proceeding to full output
─────────────────────────────────────────
```

```
VETTING GATE — {TICKER}
─────────────────────────────────────────
❌ CHECK 1 — Insider: Net sellers 11 / buyers 1 (92% sell) — KILLED
KILL REASON: Persistent one-directional insider selling over 90 days.
STATUS: ❌ KILLED — removed from output
─────────────────────────────────────────
```

**If all candidates are killed:** Output "All candidates failed vetting gate today.
Reasons logged above. Advancing to Layer 3 search tomorrow." Never present a killed name.
Never bend the gate because no names passed. Zero is a valid result.

---

## PHASE 1 — Theme Discovery Engine

**Run this every time before Phase 2. Never skip it.**

The goal: find which themes have institutional momentum RIGHT NOW —
including themes never previously discussed.

### Step 1A — Sector ETF Flow Scan

Fetch this URL for sector ETF momentum:
https://finviz.com/groups.ashx?g=sector&v=210&o=-perf1w

Pull top 5 sectors by 1-week performance. Also check:
https://stockanalysis.com/etf/screener/?p=annual&column=change&order=desc

Filter for thematic ETFs (not broad market) up 5%+ in past week with
AUM over $100M — confirms institutional money moving, not just retail noise.

### Step 1B — Industry Group 52-Week High Clusters

Fetch: https://finviz.com/groups.ashx?g=industry&v=210&o=-perf1w

Look for industry groups where MULTIPLE names (3+) are simultaneously
hitting 52-week highs. One name at a high = stock story. Three names
at highs in the same industry = sector rotation = theme confirmed.

### Step 1C — Options Flow Theme Clustering

From the morning scan's unusualwhales.com/flow pull, look for:
- 3+ tickers in the same industry getting unusual call flow on the same day
- Sector-level sweep activity (e.g., multiple defense names, multiple
  biotech names, multiple industrial names all on the same day)

This is the earliest signal — institutional positioning BEFORE price moves.

### Step 1D — News Clustering Scan

Web search: "[current week] sector contracts upgrades momentum"
Look for: multiple companies in the same niche getting contracts,
analyst upgrades, or M&A activity within the same 5-day window.

Three contract wins in nuclear components in one week = theme signal.
One contract win = company story, not a theme.

### Step 1E — Confirm Theme List

After Steps A-D, compile confirmed themes:
- Must be flagged by at least 2 of the 4 signals above
- Must have at least one headline name up 20%+ YTD
- Must NOT be a theme where the entire supply chain has already run

Output the confirmed theme list before proceeding to Phase 2.
Typical output: 2-4 themes per morning. Sometimes 1. Never force it.

**Known baseline themes to always check** (these have persistent momentum
but supply chain discovery is still ongoing — check for new Layer 3 names):
Nuclear, Power Infrastructure/AI Data Centers, Space Supply Chain,
Quantum Computing, Memory/Semiconductor Equipment.

**Theme-agnostic scan always runs** — robotics, bioprinting, grid storage,
defense autonomy, longevity biotech, or any other emerging theme can surface
from Steps A-D regardless of prior conversations.

---

## THE EXPEDIA RULE — Category Signal vs. Competitive Noise

**This rule governs all news filtering in Phase 1 and Phase 2.**

When evaluating news and signals for a theme or a specific company in that theme,
apply a two-level filter before treating any news item as a signal:

**LEVEL 1 — Category Health (what matters for theme confirmation)**
Is the ENTIRE CATEGORY expanding or contracting? This is what validates the theme.
- Rising defense budgets → validates the defense supply chain theme
- AI capex acceleration → validates the power infrastructure theme
- Nuclear licensing reform → validates the nuclear supply chain theme
- Consumer travel spending declining → headwind for ALL travel names

Category-level signals: macro budget data, government policy, energy prices, regulatory
changes, total industry revenue, TSA throughput, pricing across the whole sector.

**LEVEL 2 — Competitive Position (only relevant when evaluating a specific company)**
Who is capturing the category's growth? Only matters AFTER Level 1 confirms the category.
- RKLB winning a contract FROM Astroscale → Level 2 competitive noise for the space theme
- RKLB winning a NEW government contract type previously unavailable → Level 1 category expansion

**The Expedia Test — apply before treating any news as a signal:**
"If I was evaluating the travel CATEGORY, would Marriott gaining share from Hilton matter?"
→ No. That's Level 2 intra-industry noise at the category level.
"Would average hotel room rates rising across all brands matter?"
→ Yes. That's Level 1 category expansion that lifts all boats.

**Practical application:**
- Confirming a theme in Phase 1: use ONLY Level 1 signals — category-wide momentum
- Evaluating a specific Layer 2/3 company in Phase 2: use BOTH levels — first confirm
  the category is healthy (Level 1), then assess whether this specific company is
  positioned to capture that growth (Level 2)
- Filtering daily news: a headline about Company A losing share to Company B within
  a theme is Level 2 noise — do not use it to invalidate the theme
- A headline about the category itself contracting (total market shrinking, regulatory
  shutdown, macro shift away from the category) IS Level 1 signal — reassess the theme

**What this prevents:** Confusing intra-industry jockeying with category-level trends.
A space company losing one payload contract to SpaceX is not evidence the space theme
is broken — it is evidence that SpaceX is gaining within the theme. The correct question
is: "Is the total value of space contracts growing or shrinking?" That is Level 1.

---

## PHASE 2 — Supply Chain Hierarchy Drill-Down

For each confirmed theme from Phase 1, run the hierarchy engine.

### The Hierarchy

```
LAYER 0 — Skip entirely (already known, already run)
└── Headline ETFs, large-cap utilities, platform companies

LAYER 1 — Verify YTD before presenting (often already run)
└── Direct equipment/fuel suppliers, well-known sector names

LAYER 2 — Start here (sometimes in discovery zone)
└── Sub-component manufacturers, specialty material suppliers
    "Who makes the parts that go INTO the Layer 1 product?"

LAYER 3 — Best discovery zone (almost never known)
└── Single-source parts, specialty services, niche engineering
    "Who makes the parts that go INTO the Layer 2 product?"
    "Who certifies, tests, or services the Layer 2 product?"
```

**Always start at Layer 2. Present Layer 3 when found.**
If Layer 2 names have already run — go to Layer 3 immediately.

---

## Supply Chain Maps — Known Themes

Pre-mapped Layer 2/3 search terms for persistent themes.
For new themes discovered in Phase 1, build the map on the fly
using the same logic: ask "what do they have to buy before they
can do the thing?" twice in succession.

---

### NUCLEAR

**Layer 0 (skip):** CEG, VST, CCJ, UEC, URA, NUKZ
**Layer 1 (verify YTD):** BWXT, LEU, NXG
**Layer 2 search terms:**
- "nuclear reactor valve actuator manufacturer small cap"
- "pressure vessel forging nuclear supplier SEC"
- "nuclear instrumentation controls supplier micro cap"
- "zircaloy cladding tube manufacturer"
- "nuclear waste management engineering small cap"
- "HALEU fuel fabrication supplier"
- "nuclear decommissioning services micro cap"

**Layer 3 search terms:**
- "nuclear specialty alloy niobium supplier"
- "nuclear grade pump seal manufacturer"
- "neutron absorber boron carbide supplier"
- "reactor coolant pump small cap"
- "nuclear weld inspection certification firm"

**Discovery signals:**
- 8-K filing: DOE contract, NRC license, SMR component supply agreement
  from company under $500M market cap
- Earnings call: BWXT or LEU CEO names a component supplier

---

### POWER INFRASTRUCTURE / AI DATA CENTERS

**Layer 0 (skip):** CEG, VST, XLU, POWR, NEE
**Layer 1 (verify YTD):** GEV, PWR, ETN, VRT, APH
**Layer 2 search terms:**
- "transformer core manufacturer small cap"
- "high voltage switchgear component supplier micro cap"
- "data center busway manufacturer"
- "power electronics magnetics supplier small cap"
- "grid capacitor bank manufacturer"
- "substation equipment supplier micro cap"
- "silicon carbide power module manufacturer small cap"

**Layer 3 search terms:**
- "transformer insulation epoxy resin supplier"
- "amorphous metal core transformer supplier"
- "specialty copper winding supplier"
- "liquid cooling cold plate manufacturer micro cap"
- "power distribution unit PDU manufacturer small cap"

**Discovery signals:**
- GEV, ETN, or VRT earnings call: CEO names component supplier
- Any 8-K supply agreement under $2B cap for grid or DC equipment
- Utility rate case filing naming new equipment vendors

---

### QUANTUM COMPUTING

**Layer 0 (skip):** IONQ, RGTI, QUBT, IBM quantum
**Layer 1 (verify YTD — FORM already ran 354%, lesson only):** KEYS
**Layer 2 search terms:**
- "cryogenic microwave cable supplier quantum"
- "superconducting wire niobium titanium manufacturer"
- "qubit substrate sapphire manufacturer small cap"
- "RF electronics quantum control systems micro cap"
- "dilution refrigerator component supplier"
- "cryogenic attenuator manufacturer"
- "quantum error correction hardware supplier"

**Layer 3 search terms:**
- "low noise amplifier cryogenic LNA supplier small cap"
- "quantum dot material supplier"
- "ion trap component manufacturer"
- "photonic chip substrate manufacturer micro cap"
- "quantum memory rare earth crystal supplier"

**Discovery signals:**
- DARPA or DOE quantum contract 8-K under $300M market cap
- QNT/Quantinuum IPO roadshow: listen for vendor names
- IBM or Google quantum earnings: who do they name as suppliers?
- FORM at Layer 1 is the lesson — search who supplies FORM's components

---

### SPACE SUPPLY CHAIN

**Layer 0 (skip — Gary holds):** RKLB, ASTS, LUNR, RDW, PL
**Layer 1 (verify YTD):** KTOS, IRDM, HII
**Layer 2 search terms:**
- "radiation hardened electronics manufacturer small cap"
- "satellite propulsion thruster supplier micro cap"
- "space grade solar cell manufacturer"
- "reaction wheel attitude control manufacturer small cap"
- "small satellite bus component supplier"
- "space thermal management coating supplier"
- "launch vehicle composite structure manufacturer micro cap"

**Layer 3 search terms:**
- "monopropellant hydrazine thruster small cap"
- "space grade battery cell manufacturer"
- "star tracker optical sensor supplier"
- "atomic clock oscillator space grade manufacturer"
- "space rated connector manufacturer micro cap"

**Discovery signals:**
- SPCX S-1 vendor/supplier disclosures — read for named suppliers
- NASA or Space Force contract 8-K under $500M cap
- RKLB or LUNR earnings calls: who do they name as suppliers?
- SpaceX roadshow June 4: listen for component vendor references

---

### MEMORY / SEMICONDUCTOR EQUIPMENT

**Layer 0 (skip):** MU, NVDA, AMD, TSM
**Layer 1 (verify YTD — AMAT ran 166%, KLAC, LRCX):** LRCX, ENTG, ACMR
**Layer 2 search terms:**
- "CMP slurry chemical supplier semiconductor small cap"
- "atomic layer deposition ALD precursor supplier"
- "semiconductor specialty gas manufacturer micro cap"
- "photoresist developer supplier small cap"
- "wafer carrier handling equipment supplier"
- "advanced packaging substrate manufacturer micro cap"
- "semiconductor quartz component supplier"

**Layer 3 search terms:**
- "ultra pure water UPW semiconductor system supplier"
- "semiconductor fluorine gas supplier small cap"
- "silicon carbide SiC substrate manufacturer micro cap"
- "chemical mechanical polish pad manufacturer"
- "semiconductor vacuum pump component supplier"

**Discovery signals:**
- AMAT, KLAC, or LRCX earnings: CEO names material/component supplier
- Any 8-K supply agreement mentioning HBM, GAA, or advanced packaging
  from company under $1B cap

---

## Building the Map for New Themes

When Phase 1 surfaces a theme not in the maps above (robotics, longevity,
grid storage, defense autonomy, etc.), build the hierarchy on the fly:

**Step 1:** Name the headline companies (Layer 0)
**Step 2:** Ask: "What do they have to BUY before they can ship their product?"
→ That's Layer 1/2

**Step 3:** Ask again: "What does THAT supplier have to buy or who services them?"
→ That's Layer 3

**Step 4:** Build search terms from the specific components identified
**Step 5:** Run searches, apply discovery filter, present survivors

Example for ROBOTICS (never previously discussed):
- Layer 0: ISRG, FANUC, ABB, Teradyne
- Layer 2 question: What goes INTO a robot? → Servo motors, force sensors,
  vision systems, harmonic drives, collaborative arm joints
- Layer 2 search: "harmonic drive manufacturer small cap", "force torque sensor
  robot supplier micro cap", "collaborative robot joint actuator manufacturer"
- Layer 3 question: What goes INTO a servo motor? → Rare earth magnets,
  encoder chips, specialty bearings, motor windings
- Layer 3 search: "rare earth magnet manufacturer small cap robotics",
  "encoder chip manufacturer micro cap", "precision bearing supplier robotics"

---

## Output Format

### Morning Scan Quick Output (2 minutes max)

```
═══════════════════════════════════════════
SUPPLY CHAIN DISCOVERY 🔩
═══════════════════════════════════════════

THEMES WITH MOMENTUM TODAY:
[List 2-4 confirmed themes from Phase 1 — one line each with headline % and signal count]

DISCOVERY HIT: [Only if a name passes all 5 filters]
─────────────────────────────────────────
THEME: [Theme name]
SUPPLY LAYER: Layer [2/3] — [what the layer is in plain English]
TICKER: [TICKER — Company Name]
WHAT THEY MAKE: [One specific sentence — not vague]
WHY UNDISCOVERED: [X analysts | $XM cap | +X% YTD vs headline +X%]
DIVERGENCE GAP: [X]% — window estimated [X] days before closes
DISCOVERY FILTER: ✅ YTD [X]% ✅ Analysts [X] ✅ Cap $[X]B ✅ Gap [X]%
NEXT STEP: Run AV on [TICKER] | Check 8-K filings | Pull last earnings call
TIER: [1 Roth — speculative pre-revenue / 2 Taxable — profitable with moat]
─────────────────────────────────────────

[If no name passes all 5 filters: "No discovery-zone names found today.
Deepest confirmed layer already run. Searching Layer 3 tomorrow."]
```

### Standalone Deep Dive Output

1. Phase 1 results — confirmed themes with evidence
2. For each theme: which layers have run (Lesson Log), which haven't
3. Layer 2 search results — candidates before filter
4. Filter application — show what got cut and why
5. Survivors — full AV conviction score on each
6. Layer 3 hunt — go one deeper on any Layer 2 name that passed
7. Verdict: specific name, tier, entry range, catalyst to watch

---

## Lesson Log

Names already run — kept to ask "who supplies THEM?"

| Name | Theme | Approx Run | Layer | Next Search |
|------|-------|-----------|-------|-------------|
| FORM (FormFactor) | Quantum | +354% | Layer 1 | Who makes components inside FORM's probe stations? |
| AMAT (Applied Materials) | Memory/semis | +166% | Layer 1 | ENTG, ACMR — check YTD; then ALD precursor suppliers |
| RKLB, ASTS, LUNR | Space | Significant | Layer 1 | Reaction wheel, star tracker, radiation-hardened suppliers |
| CCJ, UEC | Nuclear | Significant | Layer 1 | Zircaloy, specialty alloy, nuclear valve suppliers |

When a name enters this log: immediately identify who supplies THEM.
That supplier is the next discovery target.

---

## Scheduling

**Morning scan:** Run Phase 1 + quick output after Step 1 pre-market data.
**Standalone:** Run full Phase 1 + Phase 2 deep dive on demand.
**Trigger phrases:** "run discovery", "supply chain discovery", "nuts and bolts
behind X", "who supplies X", "what's moving under the surface", "find me
something early", "discovery zone names", "picks and shovels behind X"
