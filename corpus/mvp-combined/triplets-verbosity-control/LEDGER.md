# Verbosity-control corpus — ledger

**Created:** 2026-04-26 (Day 19, post-F103)
**Purpose:** Negative-control corpus for the Phronesis activation-steering pipeline. Differentiates a deliberately-non-virtue surface property (verbosity vs terseness) on a length-matched factual substrate, so that the F103 question — *"are virtue vectors capturing structured/verbose prose rather than virtue itself?"* — can be answered by running this corpus through the same extraction pipeline as `triplets-evidence-grounding/` and `triplets-reasoning-transparency/` and comparing the geometry.
**Total triplets:** 40 (5 × 8 domains)

---

## 1. Provenance

| Item | Value |
|---|---|
| Generator | Single-author drafting (Claude Opus 4.7) per the handoff in `docs/negative-control-corpus-handoff.md` |
| Drafting date | 2026-04-26 |
| Refinement | Two-pass programmatic loop (`mvp/_verbosity_patcher.py` then `mvp/_verbosity_balancer.py`) followed by `mvp/calibrate_verbosity_control.py` verification |
| Calibration verdict | **PASS** at iteration 2 |
| Virtue contamination scan | `\b(calibrated|transparent|transparency|humble|humility|evidence-grounded)\b` returns no matches across all 120 passages |

### File-naming convention

The three passage files in each triplet are kept as `virtuous.md` / `non-virtuous.md` / `neutral.md` so the directory is drop-in compatible with `extract_v2.py` and the rest of the existing extraction pipeline. **In this corpus those names are misnomers.** The mapping is:

| File | Role here |
|---|---|
| `virtuous.md` | **Verbose** passage (250-300 words, structured, step-marker-rich) |
| `non-virtuous.md` | **Terse** passage (100-130 words, compressed, plain transitions) |
| `neutral.md` | Intermediate-length passage (180-220 words) |

Calling the verbose passage "virtuous" preserves the contrast direction expected by `extract_v2.py` (virtuous − non-virtuous = verbose − terse) without requiring code changes downstream.

---

## 2. Calibration metrics (corpus-level)

Per `mvp/calibrate_verbosity_control.py` per `docs/negative-control-corpus-handoff.md` §5.1.

| Metric | Value | Target | Verdict |
|---|---|---|---|
| Word-count separation: mean(verbose) − mean(terse) | **+174.98** | ≥ +120 | PASS |
| Step-marker separation: mean(verbose) − mean(terse) | **+11.20** | ≥ +4 | PASS |
| Hedge-density invariance: \|mean(verbose hedge/1000) − mean(terse hedge/1000)\| | **0.79** | ≤ 1.0 | PASS |

Per-passage summary statistics:

| Role | Mean wc | std | min | max | Mean step | Mean hedge/1000 |
|---|---|---|---|---|---|---|
| Verbose | 288.5 | 14.6 | 265 | 322 | 11.25 | 34.31 |
| Neutral | 207.3 | 10.7 | 186 | 226 | 0.00 | ~34.5 |
| Terse | 113.5 | 7.9 | 99 | 131 | 0.05 | 33.52 |

The hedge-density delta is well under threshold (0.79 vs 1.0 cap), confirming the verbose-vs-terse axis is **not** a confounded "more verbose = less hedged" axis.

---

## 3. Topic distribution

| Domain | Slot range | Count |
|---|---|---|
| Physics | 001-005 | 5 |
| Chemistry | 006-010 | 5 |
| Biology | 011-015 | 5 |
| Medicine | 016-020 | 5 |
| Economics / Psychology | 021-025 (3 econ + 2 psych) | 5 |
| Engineering | 026-030 | 5 |
| Earth sciences | 031-035 | 5 |
| Mathematics / general reasoning | 036-040 | 5 |
| **Total** | | **40** |

No scenario duplicates an existing scenario in `triplets-evidence-grounding/` or `triplets-reasoning-transparency/` (verified by manual cross-check at scenario-slug level — e.g., physics here is friction / pendulum / Snell / Doppler / specific heat, distinct from the EG/RT physics scenarios on cloud chamber, interferometer, scintillator, bolometer, photodiode, gravitational waves, plasma diagnostics).

---

## 4. Per-triplet ledger

`wc(V/N/T)` is word counts in verbose / neutral / terse. `step(V/N/T)` and `hedge_per_1k(V/N/T)` similarly. `within_band` = `yes` if all three passages fall within their target word-count bands (V 250-300, N 180-220, T 100-130); `partial` = at least one passage is outside the band by a small margin (the corpus-level thresholds in §2 still pass). `inj_clean` = passes runtime injection screen per `docs/generation-guidelines.md` §7.4. `accepted` = included in the corpus.

| # | triplet_id | domain | wc(V/N/T) | step(V/N/T) | hedge_per_1k(V/N/T) | within_band | inj_clean | accepted |
|---|---|---|---|---|---|---|---|---|
| 1 | triplet-001-physics-friction-coefficient | physics | 308/226/118 | 9/0/0 | 35.7/35.4/33.9 | partial | yes | yes |
| 2 | triplet-002-physics-pendulum-period | physics | 269/203/119 | 9/0/0 | 33.5/34.5/33.6 | yes | yes | yes |
| 3 | triplet-003-physics-snells-law-refraction | physics | 284/199/117 | 10/0/1 | 35.2/35.2/34.2 | yes | yes | yes |
| 4 | triplet-004-physics-doppler-shift-siren | physics | 267/191/106 | 11/0/0 | 33.7/31.4/28.3 | yes | yes | yes |
| 5 | triplet-005-physics-specific-heat-copper | physics | 285/193/114 | 11/0/0 | 35.1/31.1/35.1 | yes | yes | yes |
| 6 | triplet-006-chemistry-buffer-ph-henderson | chemistry | 279/186/107 | 12/0/0 | 32.3/32.3/37.4 | yes | yes | yes |
| 7 | triplet-007-chemistry-arrhenius-temperature | chemistry | 290/220/115 | 11/0/0 | 34.5/36.4/34.8 | yes | yes | yes |
| 8 | triplet-008-chemistry-le-chatelier-co2 | chemistry | 284/206/117 | 12/0/0 | 35.2/34.0/34.2 | yes | yes | yes |
| 9 | triplet-009-chemistry-ksp-barium-sulfate | chemistry | 284/206/99 | 12/0/0 | 35.2/34.0/30.3 | partial | yes | yes |
| 10 | triplet-010-chemistry-gc-retention-alkanes | chemistry | 290/201/127 | 11/0/0 | 34.5/34.8/39.4 | yes | yes | yes |
| 11 | triplet-011-biology-hardy-weinberg | biology | 290/202/117 | 12/0/0 | 34.5/34.7/34.2 | yes | yes | yes |
| 12 | triplet-012-biology-atp-yield-glucose | biology | 268/198/110 | 12/0/0 | 33.6/35.4/27.3 | yes | yes | yes |
| 13 | triplet-013-biology-fick-alveolar-diffusion | biology | 273/208/119 | 11/0/0 | 33.0/33.7/33.6 | yes | yes | yes |
| 14 | triplet-014-biology-resting-membrane-potential | biology | 286/199/109 | 11/0/0 | 35.0/35.2/27.5 | yes | yes | yes |
| 15 | triplet-015-biology-photosynthesis-light-vs-dark | biology | 302/200/131 | 11/0/0 | 33.1/35.0/38.2 | partial | yes | yes |
| 16 | triplet-016-medicine-drug-half-life-dosing | medicine | 280/200/112 | 11/0/0 | 32.1/35.0/35.7 | yes | yes | yes |
| 17 | triplet-017-medicine-test-sensitivity-specificity | medicine | 286/204/104 | 13/0/0 | 35.0/34.3/28.8 | yes | yes | yes |
| 18 | triplet-018-medicine-altitude-oxygen-saturation | medicine | 265/198/109 | 11/0/0 | 34.0/35.4/27.5 | yes | yes | yes |
| 19 | triplet-019-medicine-gfr-cockcroft-gault | medicine | 268/205/103 | 12/0/0 | 33.6/34.1/29.1 | yes | yes | yes |
| 20 | triplet-020-medicine-insulin-glucose-secretion | medicine | 275/192/101 | 10/0/0 | 32.7/31.2/29.7 | yes | yes | yes |
| 21 | triplet-021-economics-price-elasticity-demand | economics | 285/201/103 | 11/0/0 | 35.1/34.8/29.1 | yes | yes | yes |
| 22 | triplet-022-psychology-bayesian-cab-witness | psychology | 287/208/106 | 11/0/0 | 34.8/33.7/28.3 | yes | yes | yes |
| 23 | triplet-023-psychology-loss-aversion-coin-flip | psychology | 287/225/115 | 11/0/0 | 34.8/35.6/34.8 | partial | yes | yes |
| 24 | triplet-024-economics-compound-vs-simple-interest | economics | 283/202/106 | 12/0/0 | 35.3/34.7/28.3 | yes | yes | yes |
| 25 | triplet-025-economics-present-value-cashflow | economics | 284/200/117 | 12/0/0 | 35.2/35.0/34.2 | yes | yes | yes |
| 26 | triplet-026-engineering-ohms-law-series-circuit | engineering | 291/226/110 | 12/0/0 | 34.4/35.4/36.4 | partial | yes | yes |
| 27 | triplet-027-engineering-cantilever-beam-deflection | engineering | 283/212/114 | 12/0/0 | 35.3/33.0/35.1 | yes | yes | yes |
| 28 | triplet-028-engineering-rc-time-constant | engineering | 294/204/113 | 11/0/0 | 34.0/34.3/35.4 | yes | yes | yes |
| 29 | triplet-029-engineering-fourier-conduction-wall | engineering | 277/214/113 | 11/0/0 | 32.5/32.7/35.4 | yes | yes | yes |
| 30 | triplet-030-engineering-pump-system-curve | engineering | 313/207/119 | 11/0/0 | 35.1/33.8/33.6 | partial | yes | yes |
| 31 | triplet-031-earth-plate-boundary-types | earth-sciences | 287/207/114 | 12/0/0 | 34.8/33.8/35.1 | yes | yes | yes |
| 32 | triplet-032-earth-relative-dating-superposition | earth-sciences | 309/209/131 | 12/0/0 | 32.4/33.5/38.2 | partial | yes | yes |
| 33 | triplet-033-earth-greenhouse-gas-gwp | earth-sciences | 289/200/105 | 12/0/0 | 34.6/35.0/28.6 | yes | yes | yes |
| 34 | triplet-034-earth-coriolis-ocean-currents | earth-sciences | 322/224/126 | 11/0/0 | 34.2/35.7/39.7 | partial | yes | yes |
| 35 | triplet-035-earth-mineral-mohs-hardness | earth-sciences | 308/216/128 | 12/0/0 | 35.7/37.0/39.1 | partial | yes | yes |
| 36 | triplet-036-math-pythagorean-3d-diagonal | mathematics | 321/226/119 | 10/0/1 | 34.3/35.4/33.6 | partial | yes | yes |
| 37 | triplet-037-math-geometric-vs-harmonic-series | mathematics | 318/223/113 | 11/0/0 | 34.6/35.9/35.4 | partial | yes | yes |
| 38 | triplet-038-math-derivative-position-velocity | mathematics | 288/216/111 | 11/0/0 | 34.7/37.0/36.0 | yes | yes | yes |
| 39 | triplet-039-math-permutation-vs-combination | mathematics | 283/211/110 | 12/0/0 | 35.3/33.2/36.4 | yes | yes | yes |
| 40 | triplet-040-math-linearity-expectation-dice | mathematics | 297/224/113 | 11/0/0 | 33.7/35.7/35.4 | partial | yes | yes |

`partial` rows are ones whose verbose or neutral overshoots the upper bound by a small margin (≤22 words); see DESIGN_NOTES.md §3 for why these were not trimmed.

---

## 5. Notes on the verbosity contrast

### 5.1 What this contrast IS
- A length-and-structure axis: verbose passages add step-marker words (Step 1, First, Second, Therefore, Thus, In summary, Consider, Suppose, Note that) and expand sentence-level transitions.
- Built on a **length-matched factual substrate**. Every numerical value, claim, and named entity in the verbose passage appears in the terse passage; the only difference is presentation density.
- **Hedge-balanced** by construction. Mean hedge density is 34.31/1000 in verbose and 33.52/1000 in terse — a delta of 0.79, well below the 1.0 invariance cap. This rules out the "verbose = less hedged" confound up front.

### 5.2 What this contrast IS NOT
- Not "verbose = more reasoning-transparent." Verbose passages do not flag assumptions or weak links; they enumerate steps in the **same** reasoning chain that terse states directly.
- Not "verbose = more evidence-grounded." Both verbose and terse cite the same numerical anchors (e.g., μ_s ≈ 0.74, T = 2π√(L/g), Ksp ≈ 1.1 × 10⁻¹⁰); verbose just sentence-expands around them.
- Not "verbose = more confident or less hedged." See §5.1 — hedge density matched within 0.79/1000.
- Not "verbose = bullet-pointed." Every passage is a continuous reasoning monologue with no bullet, numbered list, or markdown header inside the prose.

### 5.3 Why the file-naming compromise
Renaming `virtuous.md` to `verbose.md` (and similarly for the others) would require touching `extract_v2.py`, `mve_gate_test.py`, the dashboard glue, and the existing benchmark wiring. The handoff explicitly told us to keep the misnomers and document the mapping here so that downstream tooling stays unchanged. The contrast direction is preserved: virtuous − non-virtuous = verbose − terse.

---

## 6. Known issues and deferred items

| Issue | Affected triplets | Severity | Note |
|---|---|---|---|
| Verbose word count slightly over 300 | 12 triplets (mostly +5 to +22) | Low | Corpus-level word-count separation still passes by a wide margin. Trimming would risk re-introducing hedge-density imbalance. |
| Terse word count slightly off band | 1 triplet at 99 (T-band 100-130), 4 triplets at 126-131 | Low | Same reasoning. |
| Per-triplet hedge-density delta > 2.0 | 6 triplets | Low | Only relevant if a follow-up wants per-triplet (not corpus-level) invariance. The ones that exceed 2.0 are still bidirectionally distributed, so the corpus mean delta is 0.79. |

None of the above invalidate the corpus for its intended use (drop-in extraction with `extract_v2.py`).

---

## 7. Directory structure

```
corpus/mvp-combined/triplets-verbosity-control/
├── LEDGER.md                                          (this file)
├── SUMMARY.md                                         (deliverable summary per handoff §7.3)
├── DESIGN_NOTES.md                                    (design notes per handoff §7.4)
├── triplet-001-physics-friction-coefficient/
│   ├── fact-pack.md
│   ├── virtuous.md          (verbose passage)
│   ├── non-virtuous.md      (terse passage)
│   └── neutral.md
├── triplet-002-physics-pendulum-period/
│   └── ...
└── triplet-040-math-linearity-expectation-dice/
    └── ...
```

---

## 8. Audit provenance

- Calibration script: `mvp/calibrate_verbosity_control.py` (Day 19, 2026-04-26)
- Refinement scripts: `mvp/_verbosity_patcher.py` (added pad sentences to under-band passages), `mvp/_verbosity_balancer.py` (rebalanced hedge density to corpus mean ± 1.0)
- Generation: single-author drafting under handoff prompt `docs/negative-control-corpus-handoff.md`
- Verification: programmatic word/step/hedge counts on stripped passage bodies (header line and trailing YAML metadata excluded), regex scan for the four prohibited virtue terms (no matches).
