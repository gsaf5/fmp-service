---
name: arrived-projection
description: >
  ALWAYS use this skill when Gary mentions updating his Arrived portfolio projection,
  says "update arrived numbers", "run arrived projection", "update the model",
  tells you what his monthly Arrived dividends were, says a note came due and he
  redeployed it, asks when he hits $3k/$4k/$5k from Arrived, or asks anything about
  his Arrived income trajectory. This skill contains the complete current state of
  Gary's Arrived income projection model. Use it to rebuild or update the projection
  widget without re-reading the full conversation history. ALWAYS load this skill
  before building or updating the Arrived projection widget.
---

# Arrived Income Projection Skill

## Purpose
Rebuild or update Gary's Arrived portfolio monthly cash income projection as an
interactive widget. The model tracks actual cash received each month across notes,
PCF, opportunistic fund, and SFR/VR.

---

## Core Rules — Never Violate These

1. **Total income = note INTEREST only + PCF div + opp div + SFR**
   - Note principal is returned and reinvested — never count it as income
   - Note interest = payout - round(payout / 1.065)

2. **Opp fund seasoning = deposit month + 3**
   - Money deposited in June first earns dividends in September
   - This applies to: OOP deposits, PCF dividends reinvested, opp dividends reinvested
   - Opp div is calculated ONLY on the earning balance, never on pending/unseasoned amounts

3. **PCF is static — all dividends flow to opp fund**
   - PCF balance never grows or shrinks
   - PCF dividends go into opp fund seasoning queue at deposit_month + 3

4. **Note extras go to notes only — never touch opp fund**
   - Oct 2026 $12K is a note deposit, not an opp deposit
   - Never add note extras to opp seasoning queue

5. **Show every month** — all 49 rows (Now through Jun 2030), no quarterly summaries

6. **Milestone rows highlighted**: $3k green, $4k amber, $5k red
   - Oct 2026 highlighted amber (note-only month, no note maturing)

---

## Current State (Last updated: May 26, 2026)

### Actual May 2026 Income
- Notes: $650
- PCF: $516
- Opportunistic: $265
- SFR/VR: $98
- **Total: $1,529**

### Balances
- Notes total balance: $159,643
- PCF balance: $75,910 (static, use 8% conservative)
- Opp fund earning NOW: $29,500
- SFR/VR: $98/month flat

### Rates (conservative)
- Notes: 6.5%
- PCF: 8.0%
- Opp fund: 10.75%

### Opp Fund Seasoning Queue (pre-loaded)
These are known purchases not yet fully earning:
- m=1 (Jun 2026): +$5,000 starts earning (Mar purchase, 3/31/26)
- m=2 (Jul 2026): +$2,000 starts earning (Apr purchase, 4/21/26)
- m=3 (Aug 2026): +$3,000 starts earning (May purchase, 5/26/26 — today)

From m=1 onward, each month's (OOP + PCF div + opp div) seasons into m+3.

### Note Ladder
Month index 0 = Now (May 2026), index 1 = Jun 2026, etc.

```
m=0  Now(May):  $0        (no note maturing)
m=1  Jun 2026:  $15,975   (payout: $15K × 1.065)
m=2  Jul 2026:  $10,650   ($10K × 1.065)
m=3  Aug 2026:  $12,780   ($12K × 1.065)
m=4  Sep 2026:  $10,650   ($10K × 1.065)
m=5  Oct 2026:  $0        — NO NOTE. $12K NOTE EXTRA (goes to note only, not opp)
m=6  Nov 2026:  $10,650
m=7  Dec 2026:  $11,715
m=8  Jan 2027:  $15,975
m=9  Feb 2027:  $19,170
m=10 Mar 2027:  $24,495   (two notes: $11K + $12K both maturing)
m=11 Apr 2027:  $12,780
m=12 May 2027:  $12,780
m=13 Jun 2027:  $18,611   (rolled Jun 2026 note)
m=14 Jul 2027:  $12,940
m=15 Aug 2027:  $15,208
m=16 Sep 2027:  $12,940
m=17 Oct 2027:  $19,170   — TWO NOTES: $6K 18mo (Apr 21) + $12K from Oct 2026
m=18 Nov 2027:  $15,070   — TWO NOTES: $12,150 rolled Nov 2026 + $2K 18mo (May 14)
m=19 Dec 2027:  $14,074
m=20 Jan 2028:  $18,611
m=21 Feb 2028:  $22,014
m=22 Mar 2028:  $29,282
m=23 Apr 2028:  $15,208
m=24 May 2028:  $15,208
m=25 Jun 2028:  $21,418
m=26 Jul 2028:  $15,378
m=27 Aug 2028:  $17,794
m=28 Sep 2028:  $15,378
m=29 Oct 2028:  $8,403
m=30 Nov 2028:  $19,244
m=31 Dec 2028:  $16,586
m=32 Jan 2029:  $21,418
m=33 Feb 2029:  $25,042
m=34 Mar 2029:  $34,381
m=35 Apr 2029:  $17,794
m=36 May 2029:  $17,794
m=37 Jun 2029:  $24,408
m=38 Jul 2029:  $17,975
m=39 Aug 2029:  $20,548
m=40 Sep 2029:  $17,975
m=41 Oct 2029:  $10,547
m=42 Nov 2029:  $23,690
m=43 Dec 2029:  $19,262
m=44 Jan 2030:  $24,408
m=45 Feb 2030:  $28,267
m=46 Mar 2030:  $39,810
m=47 Apr 2030:  $20,548
m=48 May 2030:  $20,548
```

### Note Extras (note-only deposits, never touch opp)
- m=5 (Oct 2026): $12,000 → note only

### Default Slider Values
- Monthly OOP to opp: $3,000
- Note top-up per rollover: $1,500

---

## How to Update Monthly

When Gary tells you what happened that month:

1. **Note matured**: Update NOTE_PAYOUTS for that month with actual payout received.
   Then update the rollover month (current + 12) with new principal × 1.065.

2. **Actual dividends received**: Update LAST_ACTUAL and the four bucket amounts.

3. **New opp deposit**: Add to seasonQ at deposit_month_index + 3.

4. **Note extra deposit**: Add to NOTE_EXTRAS — never to opp seasoning.

5. **18-month notes**: When seeded, add their payout to the correct future month
   in NOTE_PAYOUTS (they combine with whatever else matures that month).

6. **After updating**: Always verify:
   - Aug 2026 opp earning = $39,500 (sanity check)
   - Sep 2026 opp earning = ~$43,315 (Jun deposits season in)
   - No big unexplained jumps between consecutive months

---

## Widget Output Format

Build as an interactive HTML/React widget with:

### Stat cards (top)
- Last actual income
- Income hits $3k / $4k / $5k (month name)
- Total OOP across 48 months
- Income at month 48

### Two sliders
- Monthly OOP → opp fund (range $500–$10,000, step $500)
- Note top-up per rollover (range $0–$5,000, step $250)

### Full table — all 49 rows
Columns:
1. Month
2. Note payout (full cash received, muted/dash when $0)
3. Note int. (green — this is the income portion)
4. Reinvest (note payout + topup)
5. PCF div
6. Opp div
7. SFR
8. Note extra (amber when present)
9. OOP→opp
10. OOP→note (topup + note extra)
11. Opp earn bal
12. Total income (bold — note int + PCF div + opp div + SFR)
13. Ann. % (total income × 12 / total invested)

### Row styling
- Milestone months ($3k/$4k/$5k): blue background + colored badge
- Oct 2026: amber background
- Alternating rows: secondary background

---

## Key Learnings from Build History

- **Seasoning is deposit_month + 3**, not +2. Confirmed by Gary: May deposit → Aug earning.
- **Oct 2026 $12K is note money only** — caused a huge wrong jump in Jan 2027 when
  accidentally added to opp seasoning. Never put note extras in opp queue.
- **Opp div calculated on earning balance only** — not on total including pending.
- **PCF never gets reinvested back into PCF** — 100% flows to opp fund.
- **Note payouts from multiple notes in same month add together** (Oct 2027, Nov 2027,
  Mar 2027 all have two notes maturing simultaneously).
- Always verify the Python math before building the widget to avoid wasted iterations.
