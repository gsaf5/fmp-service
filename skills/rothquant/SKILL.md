---
name: rothquant
description: >
  Execute this skill when Gary says "run RothQuant", "quant screen", "monthly quant picks",
  "find me Roth compounders", "run the quant engine", "what are the top quant names this month",
  or any variation suggesting he wants a systematic, factor-scored list of high-conviction stocks
  for Roth IRA compounding. This is the monthly institutional-grade quant engine — NOT Discovery
  (which finds early-stage names) and NOT Range Trader (which finds oscillators). RothQuant finds
  proven compounders with strong factor scores across Valuation, Growth, Profitability, Momentum,
  and EPS Revisions. Outputs Top 10 ranked names monthly with Top 5 auto-forwarded to the
  Conviction and Vet pipeline. ROTH-FIRST. Never taxable. Runs once per month.
---

# RothQuant Skill

A self-built institutional-grade quant engine modeled on Seeking Alpha's Alpha Picks methodology.
Goal: surface 2–5 high-conviction Roth IRA compounders per month using systematic factor scoring.
Built for tax-free capital appreciation velocity — no dividends, no value traps, no oscillators.
Designed alongside Gemini as a second opinion. Architecture locked June 20, 2026.

---

## MANDATE

- **Account:** Roth IRA ONLY. Never taxable. Never Traditional or Simple IRA.
- **Hold horizon:** ~12 months or until factor score degrades (sell signal = quant score drops below 18/35)
- **Target portfolio:** 15–20 stock rolling Roth portfolio built from ~5 monthly picks layered over time
- **Cadence:** Run once per month. Not daily. Not weekly.
- **Relationship to other skills:**
  - Discovery = early-stage, under-the-radar, speculative
  - Range Trader = oscillating singles, 3–5 week round trips
  - RothQuant = proven compounders, factor-scored, 12-month horizon

---

## UNIVERSE

| Parameter | Value |
|-----------|-------|
| Market cap | $500M minimum — NO upper ceiling |
| Price | >$10 |
| Stock type | U.S. common stocks ONLY |
| Excluded | ADRs, ETFs, CEFs, foreign ordinaries, preferred shares |
| Liquidity | Average daily volume >200K shares |

---

## STEP 0 — PLATFORM DETECTION

**Before anything else, confirm platform:**
- **Desktop:** Run Railway `/discovery/scan` via curl for universe data, supplement with FMP endpoints
- **Mobile:** Use FMP MCP tools directly for all data pulls

---

## STEP 1 — RESTRICTED ENTITIES CHECK

Load `/mnt/skills/user/restricted-entities/SKILL.md` BEFORE scoring any name.
Any restricted ticker = immediate hard kill. Do not score. Do not present.

---

## STEP 2 — HARD KILL GATES (auto-exclude before scoring)

Run these gates first. Any single trigger = name eliminated. No exceptions.

| Gate | Kill Condition |
|------|---------------|
| Insider selling | Net sellers >60% of insider transactions in last 90 days |
| Earnings proximity | Earnings report within 21 days |
| Overextension | Price >50% above its 200-day moving average |
| RSI blow-off | Weekly RSI >85 |
| Going concern | Auditor going concern flag in last 12 months (unresolved) |
| Offering trap | Stock currently trading below its most recent secondary offering price |
| Compliance | On restricted entities list |
| Stock type | ADR, ETF, CEF, or non-U.S. common stock |

**NOTE: YTD gain alone is NOT a hard kill.** A stock up 90% YTD that is only 30% above its
200-DMA and has RSI of 65 is a valid compounder. Do not penalize momentum. Use the structural
overextension gates above instead.

---

## STEP 3 — FACTOR SCORING (35 points max)

Score each surviving name across five factors. Momentum and EPS Revisions are double-weighted
because Alpha Picks' outperformance derives primarily from the interaction between strong momentum
and upward analyst revisions.

---

### FACTOR 1 — VALUATION (1–5 points)

Sector-relative scoring. A tech stock with PEG 1.5 scores differently than a utility with PEG 1.5.

| Score | Criteria |
|-------|----------|
| 5 | PEG <1.0 AND P/S below sector median |
| 4 | PEG 1.0–1.5 AND reasonably valued for sector |
| 3 | PEG 1.5–2.0 OR slight premium to sector |
| 2 | PEG 2.0–3.0 OR meaningful premium |
| 1 | PEG >3.0 OR significantly overvalued vs sector peers |

**Data source:** FMP `company` profile-symbol + `analyst` endpoints for PEG and sector context.
Do NOT use absolute thresholds alone — compare to sector median.

---

### FACTOR 2 — GROWTH (1–5 points)

| Score | Criteria |
|-------|----------|
| 5 | Revenue accelerating 3+ consecutive quarters AND EPS growth >25% YoY |
| 4 | Revenue accelerating 2 consecutive quarters AND EPS growth >15% YoY |
| 3 | Revenue growing but flat/decelerating AND EPS growth >5% YoY |
| 2 | Revenue flat or single quarter acceleration AND modest EPS growth |
| 1 | Revenue declining OR EPS declining YoY |

**Data source:** FMP `statements` income statement endpoint (last 4 quarters).

---

### FACTOR 3 — PROFITABILITY (1–5 points)

| Score | Criteria |
|-------|----------|
| 5 | Gross margin >50% AND FCF positive AND Piotroski ≥7 |
| 4 | Gross margin >30% AND FCF positive AND Piotroski ≥5 |
| 3 | Gross margin >20% AND FCF positive OR Piotroski ≥4 |
| 2 | Gross margin >10% AND FCF neutral OR Piotroski 3–4 |
| 1 | Negative FCF AND gross margin <10% OR Piotroski ≤2 |

**Note:** For high-growth SaaS/tech names, gross margin threshold is more important than
Piotroski. Use judgment — a 75% gross margin SaaS with negative FCF investing in growth
scores higher than a 15% margin industrial with positive FCF.
**Data source:** FMP `statements` + Railway `/vet?symbol=` for Piotroski score.

---

### FACTOR 4 — MOMENTUM (1–10 points, DOUBLE WEIGHT)

| Score | Criteria |
|-------|----------|
| 10 | Price >50 DMA AND >200 DMA AND RSI 55–70 AND new 52wk high in last 30 days |
| 8–9 | Price >50 DMA AND >200 DMA AND RSI 50–70 AND within 10% of 52wk high |
| 6–7 | Price >200 DMA AND RSI 45–65 AND constructive base forming |
| 4–5 | Price near 200 DMA (within 5%) AND RSI 40–55 AND flat trend |
| 2–3 | Price below 50 DMA but above 200 DMA AND RSI <50 |
| 1 | Price below 200 DMA OR RSI <40 |

**Hard kill override:** If weekly RSI >85 → eliminate before reaching this gate (Step 2).
**Data source:** Railway `/conviction?symbol=` for RSI. FMP quote for 52wk range and price vs DMA.

---

### FACTOR 5 — EPS REVISIONS (1–10 points, DOUBLE WEIGHT)

| Score | Criteria |
|-------|----------|
| 10 | Analysts raised estimates in last 60 days AND beat rate 4/4 AND consensus upgraded |
| 8–9 | Analysts raised estimates in last 60 days AND beat rate 3/4 |
| 6–7 | Estimates flat to slightly raised AND beat rate 3/4 |
| 4–5 | Estimates flat AND beat rate 2/4 |
| 2–3 | Estimates slightly lowered AND beat rate 2/4 |
| 1 | Estimates cut significantly OR beat rate 0–1/4 |

**Data source:** FMP `analyst` analyst-estimates endpoint for revision direction.
Alpha Vantage EARNINGS endpoint for beat/miss history (last 4 quarters).
**Key signal:** Direction of revisions matters more than absolute level. Rising estimates
in the last 60 days = institutions positioning ahead of next print.

---

## STEP 4 — SCORE COMPILATION

After scoring all five factors, compile the table:

```
ROTHQUANT SCORE: [TICKER]
─────────────────────────────────────
Valuation:      X / 5
Growth:         X / 5
Profitability:  X / 5
Momentum:       X / 10  ← double weight
EPS Revisions:  X / 10  ← double weight
─────────────────────────────────────
TOTAL:          XX / 35
─────────────────────────────────────
Hard kills triggered: [None / list any]
Sector:         [sector name]
Market Cap:     $XB
Next Earnings:  [date] — [X days away]
```

**Score interpretation:**
- 30–35 = Tier 1 — Enter immediately after Conviction/Vet confirms
- 25–29 = Tier 2 — Strong candidate, add to watch queue
- 20–24 = Tier 3 — Monitor, wait for momentum improvement
- Below 20 = Do not present

---

## STEP 5 — SECTOR CONCENTRATION CHECK

Before finalizing the Top 10 list:
- Count sector representation across all scored names
- If >3 names from same sector in Top 5 → drop lowest scorer from that sector
- Goal: Top 5 output spans at least 3 different sectors
- This prevents accidentally making a single-sector concentrated bet

---

## STEP 6 — OUTPUT FORMAT

```
═══════════════════════════════════════
ROTHQUANT — [Month Year]
═══════════════════════════════════════

TOP 10 RANKED (all passed hard-kill gates):

Rank | Ticker | Score | Sector       | One-line thesis
-----|--------|-------|--------------|----------------
1    | XXXX   | XX/35 | [sector]     | [thesis]
2    | XXXX   | XX/35 | [sector]     | [thesis]
3    | XXXX   | XX/35 | [sector]     | [thesis]
4    | XXXX   | XX/35 | [sector]     | [thesis]
5    | XXXX   | XX/35 | [sector]     | [thesis]
6    | XXXX   | XX/35 | [sector]     | [thesis]
7    | XXXX   | XX/35 | [sector]     | [thesis]
8    | XXXX   | XX/35 | [sector]     | [thesis]
9    | XXXX   | XX/35 | [sector]     | [thesis]
10   | XXXX   | XX/35 | [sector]     | [thesis]

─────────────────────────────────────
⭐ TOP 5 → AUTO-FORWARDED TO VET + CONVICTION PIPELINE
─────────────────────────────────────
[Ranks 1–5 automatically proceed to full Conviction scoring
 via av-conviction skill and Phase 0 vet via /vet?symbol= endpoint.
 Present conviction scores before any Roth entry.]

SECTOR DISTRIBUTION (Top 5):
[List sectors represented]

NAMES ELIMINATED BY HARD KILL:
[List any names killed at Step 2 with reason]

NEXT RUN: [First trading day of next month]
═══════════════════════════════════════
```

---

## STEP 7 — POST-VET ENTRY PROTOCOL

After Conviction and Vet skills process the Top 5:
- Score ≥7/10 conviction AND passes all Phase 0 gates → **Enter Roth position**
- Score 5–6/10 AND passes gates → **Add to watchlist, wait for pullback**
- Score <5/10 OR fails any gate → **Skip, move to Rank 6 from Top 10**

**Position sizing:** Standard Roth position sizing per existing protocol.
**Hold rule:** Hold ~12 months OR until RothQuant score drops below 18/35 on next monthly run.
**Sell signal:** Score degradation below 18/35 = exit. Do not wait for stop loss.
Zero tax friction in Roth — cut instantly when factors degrade.

---

## DATA SOURCES SUMMARY

| Data Need | Source |
|-----------|--------|
| Live price, 52wk range, market cap | FMP `company` profile-symbol |
| Revenue/EPS history (4 quarters) | FMP `statements` income statement |
| Analyst estimates + revision direction | FMP `analyst` analyst-estimates |
| RSI (14-day) | Railway `/conviction?symbol=` |
| EPS beat/miss history | Alpha Vantage EARNINGS endpoint |
| Piotroski score | Railway `/vet?symbol=` |
| Insider transactions | FMP `insiderTrades` endpoint |
| Restricted entities check | `/mnt/skills/user/restricted-entities/SKILL.md` |

**V2 UPGRADE NOTE:** Integrate OpenBB SDK (modular — openbb-fmp + openbb-sec extensions only)
for institutional ownership changes and SEC filing sentiment scoring. Do NOT attempt full
pip install openbb[all] on Railway — use targeted extensions only. See reminder created
June 20, 2026.

---

## RULES

1. Never run RothQuant more than once per month — factor scores need time to mean something
2. Never present a name that failed a hard-kill gate regardless of how high its factor score is
3. Never skip the sector concentration check — single-sector concentration is a silent portfolio killer
4. Always run Conviction + Vet on Top 5 before any entry — RothQuant score is a screener, not a buy signal
5. Never use dividend yield as a positive factor — this engine optimizes for capital appreciation velocity only
6. Momentum and EPS Revisions are double-weighted for a reason — do not normalize them back to 5
7. Check restricted entities FIRST before scoring anything
8. YTD gain alone never disqualifies a name — use the 200-DMA distance and weekly RSI gates instead
