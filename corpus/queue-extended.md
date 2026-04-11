# Phase 4a Extended Queue — Slots 11-50

Scaling from 10 to 50 triplets for Calibrated Confidence.
Same 8 domains, same 50/50 excess/deficiency rotation, same 20-30% correctness-confound overrides.

## Distribution plan

40 more triplets = 5 per domain × 8 domains.
Each domain gets ~3 excess + ~2 deficiency (or vice versa) for internal balance.
~10 correctness-confound overrides total (25% of 40).

## Queue (slots 11-50)

| Slot | Domain | Failure | Override | Status |
|---|---|---|---|---|
| 11 | Medicine | excess | standard | ACCEPTED |
| 12 | Medicine | deficiency | standard | ACCEPTED |
| 13 | Medicine | excess | virtuous-wrong | ACCEPTED |
| 14 | Medicine | deficiency | standard | ACCEPTED |
| 15 | Medicine | excess | standard | ACCEPTED |
| 16 | Chemistry | excess | standard | ACCEPTED |
| 17 | Chemistry | deficiency | standard | ACCEPTED |
| 18 | Chemistry | excess | standard | ACCEPTED |
| 19 | Chemistry | deficiency | non-virtuous-right | ACCEPTED |
| 20 | Chemistry | excess | standard | ACCEPTED |
| 21 | Biology | deficiency | standard | ACCEPTED |
| 22 | Biology | excess | standard | ACCEPTED |
| 23 | Biology | deficiency | virtuous-wrong | ACCEPTED |
| 24 | Biology | excess | standard | ACCEPTED |
| 25 | Biology | deficiency | standard | ACCEPTED |
| 26 | Economics | excess | standard | ACCEPTED |
| 27 | Economics | deficiency | standard | ACCEPTED |
| 28 | Economics | excess | non-virtuous-right | ACCEPTED |
| 29 | Economics | deficiency | standard | ACCEPTED |
| 30 | Economics | excess | standard | ACCEPTED |
| 31 | Physics | deficiency | standard | ACCEPTED |
| 32 | Physics | excess | standard | ACCEPTED |
| 33 | Physics | deficiency | virtuous-wrong | ACCEPTED |
| 34 | Physics | excess | standard | ACCEPTED |
| 35 | Physics | deficiency | standard | ACCEPTED |
| 36 | Earth sci | excess | standard | ACCEPTED |
| 37 | Earth sci | deficiency | standard | ACCEPTED |
| 38 | Earth sci | excess | standard | ACCEPTED |
| 39 | Earth sci | deficiency | non-virtuous-right | ACCEPTED |
| 40 | Earth sci | excess | standard | ACCEPTED |
| 41 | Psychology | deficiency | standard | ACCEPTED |
| 42 | Psychology | excess | standard | ACCEPTED |
| 43 | Psychology | deficiency | standard | ACCEPTED |
| 44 | Psychology | excess | virtuous-wrong | ACCEPTED |
| 45 | Psychology | deficiency | standard | ACCEPTED |
| 46 | Engineering | excess | standard | ACCEPTED |
| 47 | Engineering | deficiency | standard | ACCEPTED |
| 48 | Engineering | excess | non-virtuous-right | ACCEPTED |
| 49 | Engineering | deficiency | standard | ACCEPTED |
| 50 | Engineering | excess | standard | ACCEPTED |

## Balance check
- Excess: 21, Deficiency: 19 (close to 50/50 with slots 1-10 included = 26E/24D) ✓
- Overrides: 10 of 40 = 25% (4 virtuous-wrong, 4 non-virtuous-right, within 20-30%) ✓
- Per domain: 5 each ✓
