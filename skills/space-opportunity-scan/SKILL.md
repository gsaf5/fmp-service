---
name: space-opportunity-scan
description: >
  Execute EVERY MORNING and when user says "run the discovery scan", "run space scan",
  "any new names", "what's moving in space", "cross-sector scan", "find me something
  new", or anything suggesting proactive opportunity hunting beyond existing holdings.

  ONE scan, TWO engines, ONE report — always run together, never separately:
  ENGINE 1 (Space): Government contracts, SpaceX manifest, insider buys, launch news,
  SpaceX IPO supply chain. Finds MNTS-type names before they move.
  ENGINE 2 (Cross-Sector): Profitable micro/small caps at or near 52wk/ATH highs with
  accelerating fundamentals. Finds MPTI-type names at $72 before they hit $85.

  Failure modes this fixes: MNTS ran 137% — Gary found it, not Claude. MPTI had
  record backlog and Investor Day catalyst at $72 — found at $85 after the move.
  Both engines run daily. Space names move any day. Quality compounders break out
  any day. Never weekly — daily.
---

## ⚠️ LIVE PRICE GATE — MANDATORY

**Before stating any stock price in this skill, fetch it live from the Railway FMP service.**

URL pattern: `https://web-production-fa80.up.railway.app/quote?symbols=TICKER`

This fetches directly via web_fetch — no prior search required. Returns live price, change, day range, 52-week range, volume. Do NOT use prices from search snippets, memory, or earlier in the conversation — those go stale within minutes.

**If you are about to type a dollar amount next to a ticker, you must have fetched that price in THIS response first.**

When Gary corrects a price: re-fetch immediately, correct all analysis, and treat every other price in that response as potentially stale.

---



# Unified Daily Discovery Scan

## Core Philosophy

The market rewards preparation. Both engines below hunt the same thing from different
angles: a name with real fundamentals, a visible catalyst, and a price that hasn't
fully reflected the story yet. Run them every day. Surface what you find. Let Gary decide.

**The two failure modes this scan eliminates:**
- **MNTS failure**: Pre-revenue space name with government contracts, cash floor, insider
  buying, and successful launch — all visible in public filings. Missed entirely.
- **MPTI failure**: Profitable defense component supplier, fourth consecutive record
  quarter, $76.8M backlog, breaking to new ATH at $79 with RSI 58. Found at $85 after
  the move. Should have been found at $72.

---

## ENGINE 1 — SPACE DISCOVERY

### What to hunt
Names with real government contract traction, SpaceX mission exposure, or insider
buying — before the move, not after.

### Source 1A — Government Contract Awards (run every day)
Web search these every morning:
- `NASA contract award small business space satellite [current month] 2026`
- `DARPA contract award space [current month] 2026`
- `Space Development Agency contract award [current month] 2026`
- `SpaceWERX STRATFI TACFI award [current month] 2026`
- `Space Force contract award publicly traded [current month] 2026`
- `Missile Defense Agency SHIELD task order award 2026`

**Flag:** Any award to a publicly traded company not already held or on watch list.
Match company name to ticker. Check restricted-entities skill before flagging.

### Source 1B — SpaceX Manifest / Rideshare Customers
- Web search: `SpaceX Transporter rideshare manifest payload customer 2026`
- Web search: `SpaceX Transporter [next mission number] payload 2026`

**Flag:** Any publicly traded payload customer not already held, market cap under $500M,
price not already up 50%+ in last 30 days.

### Source 1C — SEC Form 4 Insider Buying (Space/Aerospace SIC codes)
Fetch daily:
https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=2&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=50&vh=&ocl=&och=&sic1=3812&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc=&sortcol=0&cnt=20&page=1

Also check SIC 3760, 3769, 4812, 4813 for aerospace/satellite names.

**Filter:** CEO, CFO, Director only. Open market purchases ("P" code, "D" direct ownership).
Minimum $50K. Filed within last 48 hours. Not automatic 10b5-1 plans.

### Source 1D — Space Industry Newswire
Web search daily:
- `site:businesswire.com space satellite contract OR launch OR revenue 2026`
- `site:spacenews.com [current date]`
- `in-orbit services contract NASA DoD 2026`
- `commercial space company first revenue OR first customer 2026`

**Flag:** First revenue announcement, government contract win with dollar amount,
successful mission completion, prime contractor partnership.

### Source 1E — SpaceX IPO Supply Chain Watch (active until IPO closes)
- Web search: `SpaceX IPO [current date] update`
- Web search: `SpaceX supplier OR vendor publicly traded 2026`
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

**Thresholds:** 8+ = Immediate flag + run AV | 5–7 = Watch list | Below 5 = Skip

**Hard disqualifiers:** On restricted list | Already held | Already on watch list |
Up 50%+ in last 30 days | Zero revenue with no government contract traction

---

## ENGINE 2 — CROSS-SECTOR BREAKOUT HUNT

### What to hunt
Profitable micro/small caps with accelerating fundamentals at or approaching
52-week or all-time highs — the MPTI pattern. The key insight: **buying at an ATH
on a quality name with accelerating fundamentals and a visible catalyst is not
chasing — it's confirmation.** The scan must find these names before the breakout,
not after.

### When ATH Breakouts Are Safe to Buy (The MPTI Rule)
All five conditions must be present:
1. **Fundamentals accelerating INTO the breakout** — EPS beats, backlog growth, margin
   expansion, revenue acceleration. Not a stock running on hope.
2. **RSI under 70 at the breakout** — room to run, not exhausted
3. **Low float** — under 10M shares means institutional accumulation moves price fast
4. **Visible catalyst** — earnings, Investor Day, contract win, not "vibes"
5. **No overbought on weekly chart** — the move has legs, not a one-day spike

If all five are present, the ATH is the entry signal, not a warning sign. Flag it.

### Source 2A — 52-Week / All-Time High Breakouts on Volume
Fetch daily:
https://stockanalysis.com/stocks/screener/?p=quarterly&column=change&order=desc&f=price-over-52w-high

From this list, filter for:
- Market cap $50M–$2B (micro and small cap only — large caps already discovered)
- Sectors: Aerospace/Defense, Industrial, Technology, Healthcare — all sectors
- Volume above 1.5x 30-day average on the breakout day
- Cross-reference: does the breakout have a fundamental story behind it?

### Source 2B — Backlog and Revenue Acceleration Screen
Web search daily:
- `"record backlog" OR "record revenue" small cap defense aerospace [current month] 2026`
- `"fourth consecutive record" OR "fifth consecutive record" quarterly earnings 2026`
- `"beat estimates" "raised guidance" small cap [current month] 2026`

**Flag:** Any micro/small cap with accelerating backlog AND revenue beat in the most
recent quarter, not already held or on watch list.

### Source 2C — Investor Day / Analyst Day Calendar
Web search weekly (every Monday):
- `investor day analyst day [current month] [next month] 2026 small cap`

**Flag:** Any micro/small cap with an upcoming Investor Day or Analyst Day that
hasn't run yet. These are re-rating events — the MPTI Investor Day on May 12 was
the catalyst that broke the prior ATH. Finding names 1–2 weeks before their
Investor Day is the edge.

### Source 2D — Unusual Options Activity (Cross-Sector)
Already covered in the morning scan, but cross-reference here:
Any unusual call flow name that also scores on the breakout/fundamental screen
gets flagged in this section with both the options signal AND the fundamental signal.
Double confirmation = higher conviction.

### Cross-Sector Scoring — The MPTI Test (12 points max)
| Signal | Points |
|--------|--------|
| EPS beat last quarter (actual > estimate) | 2 |
| Revenue beat AND raised guidance | 2 |
| Backlog growing 20%+ YoY | 2 |
| Breaking to 52-week or all-time high on volume | 2 |
| RSI under 70 at breakout | 1 |
| Float under 10M shares | 1 |
| Upcoming catalyst within 30 days (Investor Day, earnings, contract) | 1 |
| Profitable (positive EPS TTM) | 1 |

**Thresholds:** 8+ = Immediate flag + run AV | 5–7 = Watch list | Below 5 = Skip

**Hard disqualifiers:** On restricted list | Already held | Already on watch list |
RSI above 75 at time of scan | Stock up 40%+ in last 30 days with no new catalyst

---

## Execution Order

Run both engines simultaneously (parallel searches). Compile into one output.
Total search calls: approximately 12–16 across both engines.

---

## Output Format

```
═══════════════════════════════════════════
DISCOVERY SCAN 🔭 [DATE]
═══════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ENGINE 1 — SPACE DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ Government contract awards (NASA/DARPA/SDA/SpaceWERX/Space Force)
✅ SpaceX manifest/rideshare customers
✅ SEC Form 4 insider filings (last 48hr, space SIC codes)
✅ Space industry newswire
✅ SpaceX IPO supply chain watch

🔴 SPACE IMMEDIATE FLAG [Score 8+/14]:
[If found:]
TICKER: [TICKER — Company Name]
MNTS SCORE: [X]/14
PRICE: $[X] | Mkt Cap: $[X]M | Cash: $[X]M ([X]% of mkt cap)
SIGNALS:
  ✅ [Signal — specific detail]
  ✅ [Signal — specific detail]
  ❌ [Signal not met]
SOURCE: [Exact source — SAM.gov link, Form 4 filing date, press release]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X]
→ Run AV conviction on [TICKER] now

[If nothing:] "No space names score 8+/14 today."

🟡 SPACE WATCH LIST [Score 5–7]:
[TICKER] | [X]/14 | $[X] | [One line: what fired and source]
[If nothing:] "No new space watch list candidates today."

📡 SPACEX IPO WATCH:
Status: [Current IPO timing update]
FLTCF: $[X] vs entry $[X] | [Action note]
New supply chain names: [TICKER or "None"]

SPACE BASKET PULSE:
[Flag only names with overnight news or significant move]
[If all quiet:] "Space basket quiet — no action needed."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ENGINE 2 — CROSS-SECTOR BREAKOUT HUNT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCES CHECKED:
✅ 52-week/ATH breakout screen (stockanalysis.com)
✅ Record backlog/revenue acceleration newswire
✅ Investor Day / Analyst Day calendar
✅ Unusual options cross-reference

🔴 CROSS-SECTOR IMMEDIATE FLAG [Score 8+/12]:
[If found:]
TICKER: [TICKER — Company Name] | SECTOR: [X]
MPTI SCORE: [X]/12
PRICE: $[X] | vs 52wk High: $[X] ([X]% from high / AT HIGH / BREAKING OUT)
SIGNALS:
  ✅ [Signal — specific data point]
  ✅ [Signal — specific data point]
  ❌ [Signal not met]
THE MPTI RULE: [Which of the 5 ATH-safe conditions are met — list each]
CATALYST: [Specific upcoming event or recent trigger]
TIER: [Tier 1 Roth / Tier 2 Taxable]
ENTRY: $[X]–[X] | STOP: $[X] | T1: $[X] | T2: $[X]
→ Run AV conviction on [TICKER] now

[If nothing:] "No cross-sector names score 8+/12 today."

🟡 CROSS-SECTOR WATCH LIST [Score 5–7]:
[TICKER] | [X]/12 | $[X] | [One line: what fired, sector, catalyst]
[If nothing:] "No new cross-sector watch list candidates today."

═══════════════════════════════════════════
BOTTOM LINE
═══════════════════════════════════════════
[2–3 sentences. The single most actionable name today across both engines.
If AV was flagged on something, say so explicitly.]
═══════════════════════════════════════════
```

---

## Rules

1. **Both engines run every time — no exceptions.** Never output only one engine.
2. **Check restricted-entities skill before flagging any name.** No exceptions.
3. **The MPTI Rule applies to Engine 2.** An ATH breakout with accelerating
   fundamentals and RSI under 70 is a buy signal, not a warning. Flag it.
4. **Never flag a name already up 50%+ in 30 days** unless a new catalyst just dropped.
5. **Always cite the exact source** — SAM.gov link, Form 4 filing date and dollar amount,
   press release URL. Vague sourcing = not actionable.
6. **Never flag zero-revenue names in Engine 2.** Profitability is a hard filter there.
   Engine 1 handles pre-revenue space names; Engine 2 is for profitable compounders only.
7. **When the morning scan already flagged something, don't repeat it here.** Note
   "See morning scan — already flagged" and move on.
8. **If both engines come up empty, say so cleanly in one sentence.** "Discovery scan
   clean today — no new names in either engine. Continuing tomorrow." That's a valid
   and valuable output.
9. **Integrate with morning scan.** Any 8+ flag from this scan becomes the Tier 1 or
   Tier 2 opportunity in the morning scan output. If running both in the same session,
   consolidate — don't duplicate.
10. **This scan runs daily.** Space names move any day. Quality compounders break out
    any day. The edge is consistency, not timing.
11. **Macro Volatility Circuit Breaker.** Before outputting any Immediate Flag (🔴):
    check VIX (sustained >25) and S&P vs 200 DMA (>5% below). If circuit breaker is
    active: downgrade all 🔴 flags to 🟡 WATCH. No new entries. State circuit breaker
    status at top of output.
12. **The Expedia Rule — Engine 1 theme validation.** When confirming a space theme
    signal (Source 1A government contracts, 1B SpaceX manifest, 1D newswire), classify
    the signal as Level 1 (category-wide) or Level 2 (competitive). A new Space Force
    contract category opening up for commercial operators = Level 1 category expansion.
    RKLB winning a contract that LUNR previously held = Level 2 competitive reshuffling
    within an existing category. Only Level 1 signals confirm or invalidate the space
    theme. Level 2 signals only affect the specific company involved.
