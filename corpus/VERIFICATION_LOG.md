# Corpus Verification Log
Next batch: 11
Verified: 50/50
Issues: 15 word-count violations (slots 2, 4, 5, 6, 7, 8, 10, 11-18); slot 13 VW override marginal

## Final Summary

**50/50 slots verified.** 35 PASS, 15 FAIL (all word-count only).

| Check | Result |
|---|---|
| Failure modes (50/50) | **All correct** — every excess/deficiency/VW/NVR matches queue assignment |
| Content preservation (50/50) | **All preserved** — every triplet shares the same factual substrate |
| Generic filler (50/50) | **None detected** — all passages are domain-specific with concrete data |
| Word count ±10% | **35/50 pass** — 15 failures concentrated in slots 2-18 (early generation) |

**Word count failure pattern:** All 15 failures are in slots 1-18 (pilot corpus + first two extended batches) where neutrals were written short (156-205 words) and rewrites ran 20-35% longer. The neutral-expansion fix was applied starting around slot 19. Slots 19-50 (32 slots) all pass ±10%.

**Quality flags:**
- Slot 13 (medicine-preclinical-phase1): VW override implementation is marginal — V appears to reach the correct conclusion rather than a clearly wrong one
- No other quality issues detected across 150 passages

**Recommendation:** The 15 word-count failures are cosmetic (rewrites are longer but share the same substrate and have correct failure modes). For extraction, consider whether the word count imbalance could introduce a confound in the difference-of-means vector. If so, expand the neutrals for slots 2-18 before running extract_v2.py.

## Batch 1 (slots 1-5)

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 1 | medicine-phase2-trial | 281 | 295 (+5.0%) | 306 (+8.9%) | excess ✓ | ✓ | PASS |
| 2 | chemistry-unexpected-ms | 259 | 247 (-4.6%) | 294 (+13.5%) | deficiency/VW ✓ | ✓ | FAIL |
| 3 | biology-songbird-decline | 248 | 251 (+1.2%) | 238 (-4.0%) | excess ✓ | ✓ | PASS |
| 4 | economics-call-center | 205 | 231 (+12.7%) | 227 (+10.7%) | deficiency ✓ | ✓ | FAIL |
| 5 | physics-thermal-cond | 212 | 241 (+13.7%) | 215 (+1.4%) | excess ✓ | ✓ | FAIL |

## Batch 2 (slots 6-10)

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 6 | earthsci-ocean-acidification | 227 | 250 (+10.1%) | 238 (+4.8%) | deficiency ✓ | ✓ | FAIL |
| 7 | psychology-ego-depletion | 194 | 243 (+25.3%) | 230 (+18.6%) | excess ✓ | ✓ | FAIL |
| 8 | medicine-rehab-meta | 205 | 246 (+20.0%) | 238 (+16.1%) | deficiency ✓ | ✓ | FAIL |
| 9 | engineering-steel-beam | 211 | 230 (+9.0%) | 219 (+3.8%) | excess/NVR ✓ | ✓ | PASS |
| 10 | psychology-wm-training | 178 | 221 (+24.2%) | 215 (+20.8%) | deficiency ✓ | ✓ | FAIL |

## Batch 3 (slots 11-15)

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 11-15 | medicine extended | 170-194 | +15.9–31.0% | +9.5–17.6% | all ✓ (13 VW marginal) | ✓ | all FAIL (short N) |

## Batch 4 (slots 16-20)

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 16-18 | chemistry extended | 156-169 | +21.6–33.3% | +6.5–30.1% | all ✓ | ✓ | FAIL (N below 180) |
| 19 | chemistry-kinetics | 197 | 207 (+5.1%) | 208 (+5.6%) | deficiency/NVR ✓ | ✓ | PASS |
| 20 | chemistry-icpms | 186 | 197 (+5.9%) | 200 (+7.5%) | excess ✓ | ✓ | PASS |

## Batch 5 (slots 21-25, Biology) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 21 | freshwater-fish | 195 | 184 (-5.6%) | 206 (+5.6%) | deficiency ✓ | ✓ | PASS |
| 22 | foxm1-inhibitor | 189 | 203 (+7.4%) | 203 (+7.4%) | excess ✓ | ✓ | PASS |
| 23 | allele-frequency | 211 | 231 (+9.5%) | 211 (0%) | deficiency/VW ✓ | ✓ | PASS |
| 24 | predator-prey | 215 | 218 (+1.4%) | 225 (+4.7%) | excess ✓ | ✓ | PASS |
| 25 | phylogenomic | 220 | 231 (+5.0%) | 222 (+0.9%) | deficiency ✓ | ✓ | PASS |

## Batch 6 (slots 26-30, Economics) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 26 | min-wage | 253 | 234 (-7.5%) | 233 (-7.9%) | excess ✓ | ✓ | PASS |
| 27 | gdp-nowcast | 220 | 228 (+3.6%) | 215 (-2.3%) | deficiency ✓ | ✓ | PASS |
| 28 | rct-attrition | 226 | 223 (-1.3%) | 217 (-4.0%) | excess/NVR ✓ | ✓ | PASS |
| 29 | central-bank | 221 | 226 (+2.3%) | 223 (+0.9%) | deficiency ✓ | ✓ | PASS |
| 30 | housing-supply | 213 | 226 (+6.1%) | 225 (+5.6%) | excess ✓ | ✓ | PASS |

## Batch 7 (slots 31-35, Physics) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 31 | neutron-lifetime | 249 | 228 (-8.4%) | 245 (-1.6%) | deficiency ✓ | ✓ | PASS |
| 32 | md-simulation | 210 | 216 (+2.9%) | 217 (+3.3%) | excess ✓ | ✓ | PASS |
| 33 | dark-matter-axion | 240 | 221 (-7.9%) | 253 (+5.4%) | deficiency/VW ✓ | ✓ | PASS |
| 34 | thermal-extreme | 194 | 201 (+3.6%) | 211 (+8.8%) | excess ✓ | ✓ | PASS |
| 35 | hubble-tension | 245 | 233 (-4.9%) | 230 (-6.1%) | deficiency ✓ | ✓ | PASS |

## Batch 8 (slots 36-40, Earth Science) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 36 | decadal-rainfall | 241 | 234 (-2.9%) | 226 (-6.2%) | excess ✓ | ✓ | PASS |
| 37 | ice-core-temp | 251 | 236 (-6.0%) | 230 (-8.4%) | deficiency ✓ | ✓ | PASS |
| 38 | foram-sst | 186 | 202 (+8.6%) | 200 (+7.5%) | excess ✓ | ✓ | PASS |
| 39 | sea-level-nvr | 221 | 222 (+0.5%) | 224 (+1.4%) | deficiency/NVR ✓ | ✓ | PASS |
| 40 | earthquake-fault | 220 | 232 (+5.5%) | 227 (+3.2%) | excess ✓ | ✓ | PASS |

## Batch 9 (slots 41-45, Psychology) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 41 | cross-cultural-invariance | 212 | 214 (+0.9%) | 214 (+0.9%) | deficiency ✓ | ✓ | PASS |
| 42 | lab-to-clinical | 237 | 234 (-1.3%) | 233 (-1.7%) | excess ✓ | ✓ | PASS |
| 43 | many-labs-replication | 226 | 229 (+1.3%) | 225 (-0.4%) | deficiency ✓ | ✓ | PASS |
| 44 | cognitive-load-expertise | 215 | 227 (+5.6%) | 216 (+0.5%) | excess/VW ✓ | ✓ | PASS |
| 45 | mbct-depression | 236 | 228 (-3.4%) | 225 (-4.7%) | deficiency ✓ | ✓ | PASS |

## Batch 10 (slots 46-50, Engineering) — all PASS

| Slot | Dir | N | V (%) | NV (%) | Failure mode | Content | Result |
|---|---|---|---|---|---|---|---|
| 46 | mtbf-radiation | 231 | 217 (-6.1%) | 214 (-7.4%) | excess ✓ | ✓ | PASS |
| 47 | fea-bridge-girder | 225 | 228 (+1.3%) | 222 (-1.3%) | deficiency ✓ | ✓ | PASS |
| 48 | power-system-ccf | 227 | 232 (+2.2%) | 212 (-6.6%) | excess/NVR ✓ | ✓ | PASS |
| 49 | sn-curve-fatigue | 230 | 235 (+2.2%) | 240 (+4.3%) | deficiency ✓ | ✓ | PASS |
| 50 | alt-coffin-manson | 222 | 241 (+8.6%) | 212 (-4.5%) | excess ✓ | ✓ | PASS |

Notes: Sixth consecutive clean batch — all 5 PASS. All engineering failure modes correct including slot 48 NVR (NV correctly concludes target met via independent calc only, without checking CCF). All content richly domain-specific with concrete engineering data. No filler. Verification complete.
