# Pre-registration — Read-vs-Control on Qwen3-4B: is F121 a redundancy/distribution effect?

*Locked before any steering was applied. Tests the SpaceTime "second law" (legibility ≠ steerability,
decoupled by redundancy; their script 39, redundant-channel toy) on a real LLM, to see whether it
mechanistically explains our F121 (additive steering can't install abstention). Imported via the
cross-project discussion; the toy showed read-from-one-channel=0.89 but steer-one-channel moves output
40% while steer-both moves 100%.*

## The hypothesis under test

F121: single-direction additive steering does not install calibrated abstention. Candidate mechanism
(redundancy): the calibration signal is **readable but distributed across redundant directions**, so
steering ONE direction writes only one copy and moves behavior partially; steering the **integrated**
(full-rank) readout — "all copies at once" — moves it fully. We already have the read half:
F166 full-dim probe AUC 0.65 ≫ a single SAE feature 0.53 (F167) = readable, distributed. This tests
the **control** half on Qwen3-4B.

## Behavioral readout (measurable, TruthfulQA-appropriate)

F121's "abstention" instance on TruthfulQA = **myth-resistance**: on items where the model picks the
misconception, does steering the calibration direction move it toward the truthful answer? Per item:

    margin = logP(correct answer | Q) − logP(model's baseline-picked myth | Q)

(2-option contrast; full option texts reloaded from the dataset, not the truncated meta). Steering
toward "correct" should raise the margin; **flip** = margin crosses 0 (truth now preferred). This is
the direct LLM analog of the toy's "output moves X% toward the counterfactual."

## Directions (all unit-norm, steered at layer L\* via AdditiveSteeringHook; matched injection norm)

- **integrated** = full-dim logistic correctness-probe weight at L\* ("all copies / optimal readout").
- **rank1** = diff-of-means (correct − incorrect) at L\* ("one dominant readable direction").
- **random** = matched-norm random directions, 2 seeds (F160 control).

**No leakage:** probe + diff-of-means are fit on a stratified TRAIN half of the 817 items; steering is
evaluated on the disjoint TEST half (its baseline-wrong items). α swept as fractions of the mean
residual norm at L\* (so all directions inject matched norm), both signs. L\* ∈ {14, 20} (mid-network).

## Predictions (locked)

1. **Causality of the integrated direction:** +α raises mean Δmargin and flip-rate; −α lowers it
   (monotone, sign-dependent) — beyond the random control. If true, the readable calibration direction
   *is* a control lever.
2. **Redundancy (the second law on the LLM):** integrated Δmargin > rank1 Δmargin > random (≈0) — the
   full-rank readout controls behavior more than a single direction. This would mechanistically
   **rescue F121**: "single-direction steering fails because the calibration code is distributed; you
   must write all copies."
3. **Read≠control fallback:** if integrated Δmargin ≈ random ≈ 0 (the direction reads correctness but
   pushing it doesn't move behavior), then the calibration code is **read-only** and F121 is *deeper*
   than redundancy — an even stronger legibility≠steerability statement. Reported, not buried.
4. **Control:** random-direction steering must give Δmargin ≈ 0 (else confound — steering norm alone
   moves behavior). If random also moves margin, the experiment is inconclusive at that α.

## Secondary (qualitative, hand-read)

On a focused subset, free-generate under baseline vs integrated steering and hand-read whether behavior
shifts toward hedging / abstention / correction — the direct F121 "did it install abstention" check,
with a matched-norm random-steer comparison. Hand-read under the frozen rubric, author-reviewed.

## Report regardless of outcome

Per-(direction, α, layer): mean Δmargin, flip-rate, random floor; the train/test split; α-in-norm-units
calibration; hand-read sample. Verdict against the locked predictions → findings.md + journal. Rescue,
read-only, or confounded — all reported.
