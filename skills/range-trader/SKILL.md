---
name: range-trader
description: >
  Execute this skill when Gary says "run range scan", "range trader", "find me range traders",
  "check the oscillators", "any singles available", "what's at the floor", or any variation
  suggesting he wants to find or monitor stocks with predictable oscillating price ranges for
  3–5 week round-trip trades in the Roth or any IRA. This is the "singles machine" — consistent,
  repeatable base hits, not home runs. Tax-free compounding via disciplined floor/ceiling entries
  and exits. Also triggers on "add [TICKER] to range watchlist" or "remove [TICKER] from range
  watchlist". ROTH-FIRST but valid in any IRA (Roth, Traditional, SIMPLE). NEVER taxable.
---

# Range Trader Skill

Manages a curated watchlist of stocks with "sideways personalities" — names that oscillate
predictably between a defined floor and ceiling. Goal: 3–5 week round trips, $500–$2,500
per position, tax-free gains compounding in the IRA. Never a home run — always a base hit.

---

## WATCHLIST (source of truth — also maintained in GitHub Gist)
NSSC, ARLO, IDCC, CHD, PBH, NEOG, MMSI, CACI, LDOS, BMI, EXPO, MGRC, WTS, EPAC

---

## MANDATORY FIRST STEP — PLATFORM DETECTION
Before pulling ANY data, confirm desktop or mobile.

### ⛔ HARD GATE 1 LOCK — ALL PLATFORMS
`/range-screen` or `/history/analyze` are the ONLY valid sources for Gate 1 historical verification.
Twelve Data is restricted to real-time current price lookup ONLY — never historical backtesting.
Under no circumstances may Gate 1 be estimated, skipped, or substituted with a price snapshot.

**DESKTOP — Give Gary this curl for the Code tab:**
```
curl -s "https://mktpxdata72.com/range-screen" \
  -H "x-api-key: pifk9AGEImYHyoEhjauKbKKAYK_vOzIiVCBjHeWB0G8"
```
Returns certified oscillators with zone classification — runs Gate 1 server-side across full watchlist.
Wait for Gary to paste results back, then run full 7-gate analysis in Chat.

**MOBILE — Gate 1 (history) — same endpoint, same requirement:**
```
curl -s "https://mktpxdata72.com/range-screen" \
  -H "x-api-key: pifk9AGEImYHyoEhjauKbKKAYK_vOzIiVCBjHeWB0G8"
```
Do NOT substitute Twelve Data for this step on mobile.

**MOBILE — Current prices only (Gates 3/4 verification after Gate 1 passes) — paste in browser:**
```
https://api.twelvedata.com/price?symbol=NSSC,ARLO,IDCC,CHD,PBH,NEOG,MMSI,CACI,LDOS,BMI,EXPO,MGRC,WTS,EPAC&apikey=7873bf2e1b58407fbf87e642db913484
```
Twelve Data = current price verification only. Never historical. Never Gate 1.

---

## THE 7 GATES (run in order — eliminate on first fail)

### GATE 1 — RANGE PERSONALITY: 18-Month Confirmed Oscillation ⚠️ PRIMARY FILTER
**Most important gate. Most names fail here.**

Pull 18 months of daily OHLC. Identify a floor and ceiling that have EACH been:
- **Touched or closely approached (within 3%) at least 3 times** in 18 months
- **Respected** — floor held (no sustained break below), ceiling rejected (no sustained break above)
- Stock must have completed **at least 2 full round trips** (floor → ceiling → floor)

⛔ CRITICAL FAILURE MODE: NEVER estimate the box from the 52-week range. The 52-week high/low
is NOT the box. The box is the REPEATED floor and ceiling confirmed by multiple touches.
A stock can have a 52-week range of $50–$100 but only oscillate $65–$80 in practice.
If you cannot confirm 3 touches on both floor and ceiling from actual price history — FAIL THIS GATE.

**Desktop — pull history via Railway:**
```
curl -s "https://mktpxdata72.com/history/analyze?symbol=TICKER" \
  -H "x-api-key: pifk9AGEImYHyoEhjauKbKKAYK_vOzIiVCBjHeWB0G8"
```
Returns: confirmed floor, confirmed ceiling, touch counts, round trips, zone classification.

**PASS criteria:** 3+ floor touches, 3+ ceiling touches, 2+ complete round trips confirmed.
**FAIL:** Fewer touches, or box estimated rather than confirmed from price history.

---

### GATE 2 — BOX WIDTH: 18–35%
Calculate: (ceiling - floor) / floor × 100

- **Under 18%:** Too tight — transaction costs eat the edge. FAIL.
- **18–35%:** Sweet spot. PASS.
- **Over 35%:** Too wide — likely a trend masquerading as a range, or excessive volatility. FAIL.

---

### GATE 3 — VALUE ZONE: Price Position in the Box
- **Tier 2 (SIMPLE IRA / Traditional IRA):** Price must be in the **bottom 15%** of the box
- **Tier 1 (Roth):** Price can be in the **bottom 30%** of the box
- Mid-range or above: WAIT. There will be another cycle. Do not chase.

Calculate zone position: (current price - floor) / (ceiling - floor) × 100

---

### GATE 4 — RSI CONFIRMATION
- **Tier 2:** RSI crossing UP from under 40 (momentum turning, not just oversold)
- **Tier 1:** RSI neutral 42–45 is acceptable (slightly more lenient)
- RSI declining from high levels: FAIL regardless of price zone
- RSI must show direction change, not just level

---

### GATE 5 — EARNINGS LANDMINE: 21-Day Hard Block
Pull next earnings date via Railway /conviction or FMP earnings-calendar.
- **If earnings within 21 days:** HARD BLOCK — do not enter. No exceptions.
- Binary event risk destroys the singles thesis.
- Always exit existing positions before the 21-day window closes in.

---

### GATE 6 — VOLUME HEALTH + GAP PROTECTION
- Average daily volume must be > 100K shares (liquidity minimum)
- No gap of 6%+ in the last 30 days (gap breaks indicate the range is unreliable)
- No abnormal volume spike (3x+ average) in last 5 days without news explanation
- If recent gap occurred: re-confirm floor still holds post-gap before entering

---

### GATE 7 — BINARY EVENT + STABILITY CHECK
- Beta < 3.0 (low volatility profile required)
- No pending binary events (FDA decisions, merger votes, spin-offs)
- Floor must NOT have been broken on a closing basis in the last 90 days
- No activist investor activity or strategic review underway

---

## POSITION SIZING

| Account | Entry Size | Full Size |
|---------|-----------|-----------|
| Tier 1 (Roth) | $500–$1,000 starter | $1,000 max |
| Tier 2 (SIMPLE/Trad IRA) | $1,500–$2,500 | $2,500 max |

Never scale up a range trade mid-position. Enter at the floor, exit at the ceiling. One and done.

---

## HOLD PROTOCOL & TIME STOPS

| Week | Action | Cadence |
|------|--------|---------|
| Entry | Buy at floor zone, Gate 3 confirmed | One-time entry — no scaling |
| Week 1–4 | Monitor — no action unless ceiling hit or stop triggered | Check 2x per week minimum |
| Week 5 | 🚩 STALE FLAG — run 3 checks: (1) still in box? (2) RSI constructive? (3) earnings window closing? | Full reassessment required |
| Week 6–7 | Continue ONLY with 1 documented active reason per week | Must articulate reason or exit |
| Week 8 | ⛔ HARD STOP — exit regardless of price, no exceptions | 0 days remaining — exit completely |

**Floor break stop:** Exit if price closes 5% below the confirmed floor. No averaging down.
**Earnings stop:** Exit before the 21-day earnings window regardless of position status.

---

## EXIT RULES
- **Target:** Ceiling zone (top 15% of box)
- **Do not hold through the ceiling** hoping for a breakout — that's a different trade
- **Do not hold through earnings** — always exit before the 21-day window
- **Do not average down** if floor breaks — floor break = thesis failed = exit

---

## OUTPUT FORMAT

For each watchlist name, produce:

```
[TICKER] — [Company Name]
Floor: $XX.XX | Ceiling: $XX.XX | Box Width: XX%
Current Price: $XX.XX | Zone: XX% of box
RSI: XX | Earnings: [date or "clear"]
Gate 1: PASS/FAIL (X floor touches, X ceiling touches, X round trips)
Gate 2: PASS/FAIL
Gate 3: PASS/FAIL
Gate 4: PASS/FAIL
Gate 5: PASS/FAIL
Gate 6: PASS/FAIL
Gate 7: PASS/FAIL
STATUS: BUY ZONE / WAIT / STALE / BLOCKED
Tier: Roth / SIMPLE IRA / Either
Entry size: $X,XXX
```

---

## COMMON FAILURE MODES — NEVER REPEAT

1. **Estimating box from 52-week range** — the 52wk high/low is NOT the box. Must confirm repeated touches.
2. **Counting a single touch as a floor** — one bounce is not a floor. Three touches make a floor.
3. **Entering mid-range** — if it's not in the bottom 15–30%, wait. There will be another cycle.
4. **Holding through earnings** — always exit before the 21-day window closes in.
5. **Using 12-month lookback** — 18 months is required. Patterns need time to confirm.
6. **Entering on a gap-down** — a gap-down near the floor may signal floor failure, not opportunity.

---

## NOTES
- Range-screen endpoint (`/range-screen`) runs Gate 1 server-side across the full watchlist pool
- Railway /history/analyze endpoint automates touch counting and round-trip detection
- Alpha Vantage: FULLY RETIRED — never use
- Twelve Data (7873bf2e1b58407fbf87e642db913484) is mobile fallback for current prices only
- MSEX (Middlesex Water) was the first certified oscillator identified by /range-screen (June 16, 2026)
  Gary bought 50 shares at $53.05 in SIMPLE IRA

**Last updated: June 18, 2026**
