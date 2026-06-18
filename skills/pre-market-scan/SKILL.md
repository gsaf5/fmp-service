---
name: pre-market-scan
description: >
  Execute this skill when the user says "run pre-market scan", "pre-market", 
  "what's moving this morning", "7:30 scan", or anything suggesting they want 
  to know what is moving BEFORE the market opens. This is NOT the morning scan 
  (which runs at 9:45 AM). This scan runs at ~7:30 AM ET and focuses entirely 
  on pre-market movers across the full market — who's up, who's down, why, and 
  whether any move is a Roth Tier 1 opportunity to act on before or at the open.
  Do NOT run the full morning scan format here. Lean, fast, actionable.
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

# Pre-Market Scan Skill

## Core Purpose
Gary has access to pre-market trading through Fidelity. The goal of this scan 
is to surface everything that is moving before the open — across every sector, 
every market cap — and flag whether any of those moves represent a quick Tier 1 
Roth opportunity. This is a fast-read format. Gary is getting ready for the day. 
No essays.

---

## Timing
**Run at: ~7:30 AM ET**
- Pre-market session is active (4:00 AM – 9:30 AM ET on Fidelity)
- This is BEFORE the 9:45 AM morning scan
- The morning scan picks up where this leaves off — do not duplicate full 
  portfolio watch, tier deep dives, or housekeeping here

---

## Data Sources

### ⚠️ STEP 0 — FMP HEALTH CHECK (run before anything else)

Before pulling any price or flagging any mover, confirm FMP MCP is live:
- Call `FMP:quote` endpoint `batch-quote-short` on SPY as a test
- If it returns a price → FMP is live. Proceed normally.
- If it fails → STOP. Tell Gary: "FMP not loaded — prices will be from
  search snippets which may be stale. Start a fresh conversation for
  live pricing." Do not silently fall back to stale data.

**Never state a dollar amount next to a ticker without a live FMP price
pulled in THIS response. No exceptions.**

---

**Primary — fetch these every run:**

1. **FMP MCP — batch-quote-short** — pull live pre-market prices for any
   ticker being discussed. Call this BEFORE stating any price.

2. **Pre-market movers feed** — search "pre-market movers today [date]" to surface 
   the biggest gainers and losers across all market caps before the open

3. **Overnight earnings** — any company that reported after yesterday's close or 
   before this morning's open. Search "earnings after hours [yesterday's date]" 
   and "earnings pre-market [today's date]"

4. **News-driven movers** — FDA decisions, government contracts, upgrades/downgrades, 
   M&A, analyst initiations, guidance updates, macro data releases. Search 
   "stock news pre-market [today's date]"

5. **Restricted entities check** — before flagging any name as a Roth opportunity, 
   cross-reference against the restricted entities list

6. **Supply chain discovery** — run supply-chain-discovery skill Phase 1:
   check sector ETF flows, industry group momentum clusters, and options flow
   clustering to identify which themes have momentum overnight. News and contracts
   happen 24/7 — pre-market is when the discovery gap is widest before open
   prices it in. For confirmed themes, drill to Layer 2/3 and surface
   discovery-zone names (under 40% YTD, under 8 analysts, under $3B cap).
   Output goes in the SUPPLY CHAIN DISCOVERY section of the scan.

---

## What to Surface

Flag EVERYTHING that is moving with a reason. No minimum % threshold — 
if it has a story, it belongs in the output. Include:

- **Mega/Large caps** — a 3% pre-market move in NVDA or AMZN affects the whole 
  portfolio and sets the tone
- **Mid caps** — sector bellwethers, names with catalysts
- **Small/Micro caps** — these are the boom-or-bust Roth candidates; a small 
  name up 40% pre-market on a contract win or earnings beat is exactly what 
  Gary is looking for

**Organize by direction:**
- GAINERS first (opportunity side)
- LOSERS second (warning side — check if any holdings are in here)

---

## The Conviction Stoplight

For every mover, include a one-line conviction flag:

🟢 **ROTH CANDIDATE** — Strong setup. Catalyst is real, move has legs, 
   entry in pre-market or at open is worth sizing. Say: "Consider entry 
   now or at open — run AV to confirm size."

🟡 **WATCH** — Interesting but something is missing (already run too far, 
   catalyst unclear, volume thin). Say: "Flag for morning scan — wait 
   for open confirmation."

🔴 **DON'T CHASE** — Move is real but the entry is gone, it's a short squeeze 
   with no fundamental backing, or it's a known garbage name. Say: "Story is 
   over — pass."

**Additional flag:**
⚠️ **PORTFOLIO ALERT** — A holding or watch list name is moving significantly. 
   Always check Gary's existing positions and watch list against the movers.

---

## Roth Opportunity Criteria (quick filter)

A pre-market mover qualifies as a 🟢 ROTH CANDIDATE if it has:
- A real, identifiable catalyst (earnings beat, contract, FDA, upgrade — 
  NOT just "momentum" or "sympathy")
- Pre-market volume that is meaningful (not 500 shares traded)
- A price that hasn't already fully priced in the news (not up 80% on a 
  $2 stock that's now $3.60 with no follow-through catalyst)
- Not on the restricted entities list
- Fits Tier 1 profile: binary catalyst, defined upside, acceptable if it 
  goes to zero

If all four are present: 🟢 flag it prominently and suggest entry timing 
(pre-market vs. wait for open).

---

## Output Format

```
═══════════════════════════════════════════
PRE-MARKET SCAN — [Day, Date] | [X] min to open
═══════════════════════════════════════════

MARKET TONE
Futures: [S&P / Nasdaq / Dow direction and magnitude — one line]
Key driver: [One sentence — what's setting the tone this morning]
Watch at open: [One specific thing — data release, Fed speaker, key earnings reaction]

═══════════════════════════════════════════
PRE-MARKET MOVERS — GAINERS 📈
═══════════════════════════════════════════

[TICKER] +X% | $[price] pre-mkt
WHY: [One sentence — the catalyst]
[🟢 ROTH CANDIDATE / 🟡 WATCH / 🔴 DON'T CHASE] — [One sentence conviction call]

[TICKER] +X% | $[price] pre-mkt
WHY: [One sentence — the catalyst]
[Stoplight] — [One sentence]

[Continue for all notable gainers]

═══════════════════════════════════════════
PRE-MARKET MOVERS — LOSERS 📉
═══════════════════════════════════════════

[TICKER] -X% | $[price] pre-mkt
WHY: [One sentence — the catalyst]
[⚠️ PORTFOLIO ALERT if it's a holding or watch list name]
[🟡 WATCH for short opportunity / 🔴 AVOID — falling knife]

[Continue for all notable losers]

═══════════════════════════════════════════
⚠️ PORTFOLIO & WATCH LIST ALERTS
═══════════════════════════════════════════
[Any of Gary's holdings or watch list names appearing in pre-market movers]
[If none: "No holdings or watch list names in pre-market movers today."]

═══════════════════════════════════════════
SUPPLY CHAIN DISCOVERY 🔩
═══════════════════════════════════════════
[Run supply-chain-discovery Phase 1 — themes with overnight momentum]
[For each confirmed theme, drill to Layer 2/3 for undiscovered suppliers]

[If discovery hit found:]
THEME: [Name] | HEADLINE: [TICKER] +[X]% YTD
DISCOVERY: [TICKER — Company] | Layer [2/3]
WHAT THEY MAKE: [One specific sentence]
WHY UNDISCOVERED: [X analysts | $XM cap | +X% YTD]
NEXT STEP: Run AV on [TICKER] before open

[If nothing passes discovery filter:]
"No discovery-zone names this morning — all confirmed supply chain
layers in moving themes have already run."

═══════════════════════════════════════════
TOP ROTH OPPORTUNITY THIS MORNING 🎯
═══════════════════════════════════════════
[If a clear 🟢 candidate exists:]
NAME: [TICKER — Company]
MOVE: +X% pre-market | $[X] current | Catalyst: [one phrase]
ENTRY: [Pre-market now / Wait for open / Wait for pullback to $X]
STOP: $[X] | TARGET: $[X]
WHY NOW: [Two sentences max — why this is the one to act on today]
→ Run AV on [TICKER] to confirm conviction score before sizing

[If no clear candidate:]
"No clean Roth setups this morning. Watch list candidates in the morning scan."

═══════════════════════════════════════════
BOTTOM LINE
═══════════════════════════════════════════
[Two sentences max. What matters most in the next 2 hours.]
═══════════════════════════════════════════
```

---

## Critical Rules

1. **Check Macro Volatility Circuit Breaker before flagging any Roth candidate** — if VIX sustained >25 or S&P >5% below 200 DMA: no 🟢 ROTH CANDIDATE flags. Mark anything that would have been green as 🟡 WATCH for when regime clears. State 🔴 CAPITAL PRESERVATION MODE at top of output.
2. **Speed over depth** — this is a 7:30 AM fast read. The morning scan at 9:45 does the deep work. Don't turn this into a morning scan.
3. **Every mover gets a stoplight** — never list a name without a conviction call. Gary needs to know immediately: act now, watch, or ignore.
4. **Always check the portfolio and watch list** — before finishing the output, run through Gary's holdings and watch list against the movers. A watch list name gapping up or down is the most actionable intelligence in this scan.
5. **Pre-market volume matters** — a 50% move on 200 shares is noise. Flag it but mark it 🔴. A 15% move on 500K+ shares pre-market is real. Flag it 🟢 or 🟡 based on the catalyst.
6. **Restricted entities check is mandatory** — never flag a name as a Roth candidate without checking the restricted list first.
7. **Don't duplicate the morning scan** — no tier deep dives, no full conviction scores, no housekeeping, no Simple IRA deployment reminders. Those live at 9:45.
8. **If nothing is moving** — say "Quiet pre-market — no notable movers with a story this morning" and give one sentence on futures direction. Don't manufacture opportunities.
9. **Losers can be opportunities too** — a name down 30% pre-market on an earnings miss might be a Roth candidate on the short side or a watch-and-buy on the dip if the thesis is intact. Flag it.
10. **The Expedia Rule on pre-market news** — before flagging a mover, classify the catalyst: is this Level 1 (something happened to the whole category) or Level 2 (this company gained/lost share vs. a peer)? A Level 1 catalyst on a category name = high priority flag. Level 2 peer-level shuffling = low priority flag with caveat.

---

## Relationship to Other Scans

| Scan | Time | Purpose |
|------|------|---------|
| Pre-Market Scan | ~7:30 AM | What's moving NOW — fast flags, Roth opps |
| Morning Scan | ~9:45 AM | Full portfolio + tier analysis + opportunities |
| Afternoon Scan | ~3:15 PM | End of day update + overnight queue |

The pre-market scan feeds INTO the morning scan. Any 🟢 or 🟡 names from 
7:30 should be revisited at 9:45 with live open data and a full AV conviction 
score if they're still in play.
