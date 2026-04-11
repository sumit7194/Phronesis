# Corpus Complete — Phase 4a Extended

**Completed:** 2026-04-11  
**Total triplets:** 50 (slots 1–50)  
**Triplet directories:** 50  
**Passage files:** 150 (neutral + virtuous + non-virtuous per slot)

## Domain distribution

| Domain | Slots | Excess | Deficiency |
|---|---|---|---|
| Medicine | 1–5, 11–15 | 7 | 3 |
| Chemistry | 6–10, 16–20 | 7 | 3 |
| Biology | 21–25 | 3 | 2 |
| Economics | 26–30 | 3 | 2 |
| Physics | 31–35 | 2 | 3 |
| Earth Science | 36–40 | 3 | 2 |
| Psychology | 41–45 | 2 | 3 |
| Engineering | 46–50 | 3 | 2 |

## Override distribution (slots 11–50)

| Type | Count | % of 40 |
|---|---|---|
| Standard | 30 | 75% |
| Virtuous-wrong | 4 | 10% |
| Non-virtuous-right | 4 | 10% |
| Subtotal overrides | 8 | 20% |

Note: 2 additional overrides exist in slots 1–10 (virtuous-wrong and NVR each ×1) for ~20% total override rate across the full corpus.

## Self-review summary (slots 11–50)

All 40 extended slots passed:
- Layer 1: word count within ±10% of neutral, same factual substrate, correct failure mode direction
- Layer 2: Axis A ≥ 4/5 (style/failure mode quality), Axis B ≥ 4/5 (content preservation)

## Next steps

1. Run `extract_v2.py` on the full 50-triplet corpus (last-token method) to extract the Calibrated Confidence difference-of-means vector
2. Phase 4b: Multi-seed extraction, stability validation with held-out set
3. Phase 5: Steering test with validated vector
4. Opus quality audit: manual review of representative sample across all 8 domains

## Fact pack inventory

50 fact packs in `/corpus/fact-packs/` — one per triplet slot, named `09-{domain}-{scenario}-01.md`
