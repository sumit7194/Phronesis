# Cosine analysis of v1 virtue vectors (qwen3-4b)

**Date:** 2026-04-28
**Scope:** Geometric (cosine + norm) analysis of last-token diff-of-means virtue vectors on qwen3-4b. CPU-only, no model load.
**Vectors loaded:** v_IH (`triplets-intellectual-humility`), v_CC (`triplets` — legacy 50-triplet hand corpus; `triplets-combined` is **not present** in `mvp/results/vectors/qwen3-4b/`, so the legacy corpus is used as the v_CC representative), v_EG (`triplets-evidence-grounding`), v_RT (`triplets-reasoning-transparency`), v_VERB (`triplets-verbosity-control`, negative control), and `random_L22_vector.npy` (sanity floor).
All vectors confirmed shape `(2560,)`. Random-baseline cosines fall in [-0.021, +0.012], consistent with the expected `±1/√2560 ≈ ±0.0198` floor — no anomaly.

## 1. Headline verdict

**v_IH and v_CC are *not* the same direction.** At their AP-peak layers, cos(v_IH @ L17, v_CC @ L9) is uncomputable directly (different layers); within-layer comparisons give cos(v_IH, v_CC) = **+0.125 at L9**, **+0.084 at L17**, and **+0.143 at L13**. All three sit in the "weakly aligned, mostly orthogonal" or "orthogonal" band (|cos| < 0.2). Given that the diagnostic-batch behavioral signature ("anti-spiral / commit-to-answer") is shared, the data are inconsistent with geometric convergence on a single residual-stream direction and **strongly consistent with downstream gating**: two near-orthogonal directions that nonetheless trigger the same "force `<think>` closure" output behavior. Caveat: this is geometric only; it does not test whether OV/MLP read-off projections of these two directions land on the same writable feature.

## 2. Pairwise cosines at AP-peak layers (Section 1 cells)

AP peaks: IH=L17, CC=L9, EG=L7, RT=L15. Cosines are computed within a single layer only (cross-layer cosine has no clean meaning in residual stream).

| Pair | Layer | cos | Band |
|------|-------|-----|------|
| v_IH × v_CC | L9  | +0.1254 | orthogonal |
| v_IH × v_CC | L17 | +0.0843 | orthogonal |
| v_IH × v_EG | L7  | -0.0257 | orthogonal |
| v_IH × v_EG | L17 | +0.0224 | orthogonal |
| v_IH × v_RT | L15 | -0.0808 | orthogonal |
| v_IH × v_RT | L17 | -0.0789 | orthogonal |
| v_CC × v_EG | L7  | +0.3949 | weakly aligned (near upper) |
| v_CC × v_EG | L9  | +0.3591 | weakly aligned |
| v_CC × v_RT | L9  | +0.2778 | weakly aligned |
| v_CC × v_RT | L15 | +0.2928 | weakly aligned |
| v_EG × v_RT | L7  | +0.1968 | borderline orthogonal |
| v_EG × v_RT | L15 | +0.2346 | weakly aligned |

### Negative control (v_VERB) — sanity check

| Pair | Layer | cos |
|------|-------|-----|
| v_IH × v_VERB | L17 | -0.0633 |
| v_CC × v_VERB | L9  | +0.0358 |
| v_EG × v_VERB | L7  | +0.0513 |
| v_RT × v_VERB | L15 | -0.0015 |

All within |0.07| — verbosity-control vector is geometrically uncorrelated with any virtue, as expected.

### Random baseline (vs `random_L22_vector.npy`, comparing each virtue at L22)

| Vector | cos(., random_L22) |
|--------|--------------------|
| v_IH @ L22  | -0.0043 |
| v_CC @ L22  | -0.0209 |
| v_EG @ L22  | -0.0174 |
| v_RT @ L22  | -0.0055 |
| v_VERB @ L22 | +0.0124 |

All within ±0.021, on the order of `1/√2560 ≈ 0.0198`. Floor is healthy; no contamination.

## 3. Per-virtue layer drift (cos between AP-peak vector and L_peak ± Δ)

| Virtue | Peak | Δ=-4 | Δ=-2 | Δ=0 | Δ=+2 | Δ=+4 |
|--------|------|------|------|-----|------|------|
| v_IH (L17) | L17 | +0.6900 (L13) | +0.8096 (L15) | +1.0000 | +0.7690 (L19) | +0.6676 (L21) |
| v_CC (L9)  | L9  | +0.3241 (L5)  | +0.5553 (L7)  | +1.0000 | +0.6315 (L11) | +0.5219 (L13) |
| v_EG (L7)  | L7  | +0.2505 (L3)  | +0.4110 (L5)  | +1.0000 | +0.5012 (L9)  | +0.3286 (L11) |
| v_RT (L15) | L15 | +0.5466 (L11) | +0.7088 (L13) | +1.0000 | +0.7432 (L17) | +0.5563 (L19) |

**Reading.** v_IH is the most layer-stable virtue (drift cos ≥ 0.67 across ±4). v_RT is also fairly stable (≥ 0.55). v_CC and v_EG drift faster (early-layer vectors generally do; the residual stream hasn't accumulated the late-style direction yet). Critically, v_CC drifts substantially between L9 and L17 (cos L9↔L13 = +0.52; we don't have L9↔L17 directly but extrapolation puts it well below 0.5). This means cross-layer comparisons of v_IH @ L17 to v_CC @ L9 are *less* meaningful than within-layer comparisons — and the within-layer numbers (L9: +0.125, L17: +0.084, L13: +0.143) all agree they are orthogonal.

## 4. Same-layer full matrix at L13 (mid-stack, where all four directions exist with non-trivial norm)

|       | IH | CC | EG | RT | VERB |
|-------|----|----|----|----|------|
| IH    | +1.0000 | +0.1428 | +0.0539 | -0.0379 | -0.0069 |
| CC    | +0.1428 | +1.0000 | +0.3350 | +0.3509 | -0.0045 |
| EG    | +0.0539 | +0.3350 | +1.0000 | +0.2377 | +0.0125 |
| RT    | -0.0379 | +0.3509 | +0.2377 | +1.0000 | +0.0030 |
| VERB  | -0.0069 | -0.0045 | +0.0125 | +0.0030 | +1.0000 |

For comparison, at **L17** (IH AP-peak): IH–CC=+0.0843, IH–EG=+0.0224, IH–RT=-0.0789, CC–EG=+0.3949, CC–RT=+0.2611, EG–RT=+0.2775. At **L9** (CC AP-peak): IH–CC=+0.1254, IH–EG=+0.0432, IH–RT=-0.0520, CC–EG=+0.3591, CC–RT=+0.2778, EG–RT=+0.2363. The pattern is layer-robust.

## 5. Norms (L2)

At AP-peak layer:

| Vector | Layer | ‖v‖₂ |
|--------|-------|------|
| v_IH   | L17 | 16.32 |
| v_CC   | L9  |  6.03 |
| v_EG   | L7  |  2.19 |
| v_RT   | L15 |  4.04 |
| v_VERB | L13 |  7.62 |
| random | L22 |  1.00 |

Norm growth across layers (peak ± 4):

| Virtue | -4 | -2 | peak | +2 | +4 |
|--------|----|----|------|----|----|
| v_IH (L17) | 12.88 | 14.13 | 16.32 | 22.66 | 25.86 |
| v_CC (L9)  |  2.29 |  4.47 |  6.03 |  6.80 |  7.68 |
| v_EG (L7)  |  0.50 |  0.95 |  2.19 |  3.03 |  3.45 |
| v_RT (L15) |  3.50 |  3.78 |  4.04 |  4.56 |  5.64 |

The norms of v_IH and v_CC differ by ~2.7× at their peaks, but this does **not** rescue a "same direction" reading: cosine is scale-invariant, so the orthogonality verdict stands. The norm gap does mean a fixed-coefficient steering recipe (e.g. `+α·v`) injects very different L2 perturbations across virtues — relevant for behavioral-protocol design but not for the geometric question here.

## 6. Interpretation

**The "1 disposition vs 4 dispositions" question on v1 corpora.** Geometrically, the v1 vectors do **not** look like one shared disposition. v_IH is essentially orthogonal to every other virtue at every layer examined (|cos| ≤ 0.14 across L9, L13, L17). The other three (v_CC, v_EG, v_RT) form a loose triangle with pairwise cosines in the 0.20–0.40 band — "weakly aligned but distinct." This sub-cluster is consistent with shared corpus-construction features (all three corpora reward similar response-style markers — explicit citation, stepwise reasoning, calibrated language) without collapsing into a single direction. v_IH, by contrast, was extracted from a corpus that explicitly contrasts confident-overclaim against humble-uncertainty, and that contrast is geometrically distinct from "be more verbose / structured / cite-y."

**On the v_IH ≈ v_CC behavioral collision specifically.** The hand-review observation was that v_IH @ L17 and v_CC @ L9 produce the *same* "force `<think>` closure / commit-to-answer" output. The cosine evidence here makes geometric convergence **implausible**: the two directions sit at orthogonal angles in residual stream at every layer where both are defined, and v_IH does not drift toward the v_CC sub-cluster as we sweep layers. The most parsimonious remaining hypothesis is **downstream gating / functional convergence**: distinct residual-stream directions hit overlapping OV-circuit read-offs (or overlapping MLP keys) that, when amplified, both push the same `</think>` token-probability bump. The IH norm (~16) is also large enough at L17 that even small leakage into CC-relevant subspaces could matter — but the cosine numbers are too small for direct overlap to be the explanation.

**Limits of this analysis.** (a) Geometric only — it cannot distinguish "different directions, same downstream gate" from "different directions with a small shared component that happens to be the behaviorally active one." A causal test (project each vector onto the other and steer with the residual; or steer with the orthogonal complement) would resolve this. (b) Layer-mismatched comparisons (v_IH @ L17 vs v_CC @ L9) are not directly comparable in residual stream and have been deliberately avoided; the within-layer agreement (orthogonal at L9, L13, L17) makes the conclusion robust to that choice. (c) The v_CC vector here comes from `triplets` (legacy 50-item hand corpus); `triplets-combined` is not present in `mvp/results/vectors/qwen3-4b/`, so the headline verdict should be re-checked once the combined-corpus v_CC is extracted. (d) The diagnostic-batch behavioral collision was observed at **specific layers** (IH@L17, CC@L9); a full causal answer requires a same-layer steering A/B (e.g. v_IH @ L9 and v_CC @ L9, both at matched effective L2, on the same prompts) to rule out a layer-of-injection confound.
