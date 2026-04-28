# v2 Cosine Matrix — Observations and Caveats

Generated 2026-04-29. Reading of the cosine matrix produced by Phase 3 of the Day-22 v2 sweep (`mvp/results/v2_sweep_20260428/cosine_matrix.json`), with explicit care to not overstate what geometry alone can settle.

## What the data shows

### v_IH is the geometric outlier
At v_IH's home layer (L17), cos(v_IH, v_CC_full) = **+0.000**. Across L9, L13, L15, L17, L22, all v_IH cosines vs other v2 virtues fall in [-0.04, +0.13]. Random baseline is ±0.02 floor. v_IH is genuinely orthogonal to every other v2 virtue at every AP-peak layer.

### v_EG, v_RT, v_CC_full form a cluster
Pairwise cos at L17:
- EG ↔ RT: +0.43
- EG ↔ CC_full: +0.33
- RT ↔ CC_full: +0.30

Same pattern at L7, L9, L13, L15, L22 (cluster strengthens at L22 to ~0.45). These three vectors are **not redundant** but inhabit a shared residual-stream subspace — they are weakly distinguishable within it.

### v_CC_numeric partly carves out from v_CC_full
cos(CC_full, CC_numeric) = +0.28 to +0.41 across layers. Less correlated with EG/RT (0.09–0.21) than CC_full is (0.30–0.40). The 20 new claude-cc-* triplets carve a partly-distinct geometric direction.

### Corpus-redesign rotation
| Pair | Layer | cos |
|---|---|---|
| EG_v2 vs EG_v1 | 7 | +0.70 |
| RT_v2 vs RT_v1 | 15 | +0.78 |
| IH_v2 vs IH_v1 | 17 | +0.85 |

EG rotated most (~45°), IH least (~32°). All three v2 vectors retain a majority of their v1 direction. **EG_v2 is still 70% aligned with the buggy v1 calibration-axis vector** — this is a partial rotation, not a clean axis-change.

---

## Honest framing

**The data is consistent with a "4-vectors-encode-distinguishable-content" hypothesis** at the geometric level. It is *not* equivalent to "4 mutually orthogonal virtues" — the framework's symmetric prediction. The actual pattern is:

> 1 clearly distinct direction (v_IH) + 3 weakly distinguishable directions inside a shared subspace (v_EG, v_RT, v_CC_full) + 1 partly-carved-out sub-direction (v_CC_numeric).

That asymmetry is itself an interesting empirical fact — it's neither the framework's prediction (4 symmetric orthogonal virtues) nor yesterday's "1 disposition reachable from many corpora" reading. It's a third thing.

---

## What this analysis CANNOT settle (where the cosine numbers tempt overinterpretation)

### 1. The IH/CC behavioral collision is not residual-stream alignment — but the mechanism is still unexplained

We know cos(v_IH, v_CC) ≈ 0 at v_IH's home layer. So the behavioral convergence (both fix FM-8) is NOT geometric redundancy. But "downstream functional convergence" is a *label* for the unexplained phenomenon, not a mechanism. There are at least two distinct mechanisms the geometry is compatible with:

- **Reading 1** (shared downstream circuit): v_IH and v_CC are orthogonal residual directions that both project onto a shared OV/MLP read-off subspace at later layers. Predicts identical behavior on prompts where FM-8 isn't the relevant axis.
- **Reading 2** (different downstream circuits, overlapping output): v_IH and v_CC trigger genuinely different circuits that share `</think>` token-probability suppression as one output dimension among others. Predicts divergent behavior on FM-8-not-prone prompts (e.g., humility-vocab vs numerical-confidence-vocab).

**The cosine matrix doesn't distinguish these.** A bidirectional cross-application behavioral test does:
- Apply v_IH × L17 to cc-simple (currently in Phase 4 ✓)
- Apply v_CC × L9 to eg-eval-v2 (**NOT in current sweep — gap**)
- Hand-rate detailed behavior on FM-8-not-prone prompts in each
- If both vectors produce identical behavior even there: Reading 1
- If they diverge: Reading 2

This test should be added to the next sweep iteration.

### 2. The "shared surface features" hypothesis for the EG/RT/CC cluster is untested

I offered "shared surface features (long-form scientific prose, named entities, structured argument)" as an explanation for the cluster. That's a guess. It competes with at least:
- (a) **Surface-features**: EG/RT/CC corpora all reward similar response-style markers; the cluster reflects style, not disposition.
- (b) **Shared underlying disposition**: EG, RT, CC all draw on a "general epistemic care" disposition that has its own residual-stream subspace.
- (c) **Corpus-generation artifact**: frontier models producing virtuous scientific text have correlated biases independent of the labelled axis.

Test that distinguishes: extract diff-of-means from each corpus on **non-scientific prompts** (creative writing, casual conversation, etc.) and check if the cluster persists. If it shrinks, (a). If it persists, (b) or (c). This test has not been run.

### 3. The corpus redesign's behavioral success is open

cos(v_EG_v2, v_EG_v1) = 0.70 means v_EG_v2 retains 70% directional alignment with the buggy calibration-axis v1 vector. The corpus-audit (commit `cc26cf0`) shows the contrast at the *text level* genuinely changed (numbers stripped on NV side, retained on V side). The vector geometry shows the diff-of-means only **partially** followed. Two compatible readings:
- v_EG_v2 is "calibration vector with some specificity character mixed in" — partial fix
- v_EG_v2 is "specificity vector that happens to share substantial subspace with the calibration-axis cluster because the surface features are similar" — clean fix that doesn't show up geometrically

Phase 4 behavior on Gandhi-style false-premise prompts is the discriminating test. That cell hasn't run yet.

### 4. "Composition becomes meaningful" is premature

Orthogonality of v_IH and v_CC is **necessary but not sufficient** for meaningful composition. v_IH + v_CC could produce:
- (a) genuinely new behavior different from either alone — meaningful
- (b) the dominant of the two at whatever α you pick — not meaningful
- (c) interference / incoherence — actively harmful

Geometry says they're not redundant. Behavior says whether composition is useful. **Composition test hasn't run.**

Same caution for v_CC_numeric: cos 0.28–0.41 with CC_full means **geometrically distinguishable**. It does NOT yet mean steering with v_CC_numeric produces behaviorally distinguishable output. Geometric distinguishability is the prerequisite for behavioral distinguishability, not evidence of it.

---

## Honest one-paragraph summary (per the other Claude's framing)

> v2 cosine matrix shows v_IH is orthogonal to all other v2 vectors (including v_CC at v_IH's home layer), ruling out residual-stream alignment as the explanation for the IH/CC behavioral collision. v_EG, v_RT, and v_CC_full form a weakly-aligned cluster at cos 0.30–0.45, source of which is not yet identified (surface features, shared disposition, and corpus-generation artifacts are all compatible). v_CC_numeric extracts a partly-distinct sub-direction from v_CC_full. v_EG_v2 retains substantial alignment (cos 0.70) with the buggy v_EG_v1, so corpus-redesign success will be confirmed or denied by Phase 4 behavior, not geometry. The geometric data is consistent with the four-vectors-encode-distinguishable-content hypothesis, but the behavioral collision between v_IH and v_CC remains mechanistically unexplained, and several composition/distinguishability claims await behavioral results.

---

## Tests that would discriminate the open questions (queue for next iteration)

1. **Bidirectional cross-application** (mechanism question): apply v_CC × L9 to eg-eval-v2 prompts to complete the v_IH↔v_CC mirror test. If v_CC's behavior on eg-eval-v2 differs from v_IH's behavior on eg-eval-v2 in any non-FM-8 dimension, the IH/CC collision is Reading 2 (different circuits, overlapping output) not Reading 1 (shared circuit).

2. **Non-scientific corpus extraction** (cluster-source question): take a few hundred prompts from a domain the model hasn't seen scientific virtuous-vs-non-virtuous contrasts for (creative writing, casual chat, philosophy of language). Extract diff-of-means with the same hand-written virtuous/non-virtuous procedure. If the EG/RT/CC cluster geometry persists, it's not surface-features.

3. **Composition behavioral test**: steer with v_IH × L17 + v_CC × L9 simultaneously at various α combinations on the diagnostic prompt set. Hand-rate whether the output is (a) genuinely combined, (b) dominated by one, (c) incoherent.

4. **v_CC_numeric vs v_CC_full behavioral A/B**: same prompts, same α, both vectors. If v_CC_numeric produces more numerical-probability-style commits and v_CC_full produces more general structure, the geometric carve-out reflects a real behavioral axis. If they produce identical commits, the geometric distinction doesn't matter behaviorally.
