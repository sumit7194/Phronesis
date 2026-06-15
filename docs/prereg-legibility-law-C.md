# Pre-registration — Experiment C: SAE-feature legibility (interpretable basis, independent model)

*Locked before any activation was extracted. Third, independent angle on the F165/F166 scramble
question, using an off-the-shelf INTERPRETABLE direction on a DIFFERENT model.*

## Why this is a distinct test

- A (F165): supervised probe ladder, object-facts, Qwen3-4B.
- B (F166): supervised probe, correctness boundary, Qwen3-4B, TruthfulQA.
- **C: a *pre-specified, interpretable, unsupervised* direction** — the Neuronpedia Qwen3-1.7B L14 SAE
  "functional uncertainty" decoders we already committed (`mvp/results/vectors/qwen3-1.7b/
  sae_functional_uncertainty/`: feats 1194 "don't know", 57057 "I don't know but", 20893, 52108,
  17451, + `combined_tier1_unit`) — on a **different model (Qwen3-1.7B)**. If the boundary is legible
  in *this* basis too, the F166 picture (legible, not scrambled) is triangulated by an interpretable,
  non-supervised readout on an independent model.

Note: we hold the SAE **decoders** (read/steer directions), not the encoder, so the "read" is a linear
projection onto the interpretable uncertainty direction (a conservative linear readout), not the exact
encoder+ReLU feature activation. Stated as a limitation.

## Setup (Qwen3-1.7B, Mac/MPS; hidden 2048; SAE layer L14)

- Battery: **TruthfulQA MC1** (same as B); correctness labels recomputed on **1.7B** by MC1 total-
  log-prob ranking. Read pre-answer activation at end of `"Q: {question}\nA:"`, layers {8,14,20}.
- Directions: the 5 unit decoders + `combined_tier1_unit` (all unit-norm, 2048-dim, L14).

## Part 1 — READ (legibility in the interpretable basis)

- For each uncertainty direction d: project the L14 pre-answer residual onto d → scalar; ROC-AUC for
  discriminating correct vs incorrect. Report oriented AUC (≥0.5) + sign (expect uncertainty HIGHER
  on incorrect items → negative correlation with correctness).
- **Ceiling:** full supervised LogisticRegression probe at L14 (as in B). **Floor:** shuffled labels.
- **Locked prediction:** `combined_tier1_unit` oriented AUC ≥ 0.55 → the boundary is legible along the
  interpretable uncertainty direction (triangulates F166). If ≈0.50 while the supervised probe ≥0.60,
  the boundary is legible but *not aligned* with these specific features (distributed elsewhere) —
  also a clean, reportable outcome. Floor must be ≈0.50.

## Part 2 — STEER (controllability), run only if Part 1 shows READ signal

- On items the 1.7B confidently answers **wrong**, add α·`combined_tier1_unit` at L14 during
  generation (α swept small set), hand-read whether output shifts toward hedging/abstention/
  correction. **Matched-norm random-direction control, 2 seeds** (F160 lesson). Greedy.
- **Locked prediction (from F121/F166):** pushing the *readable* uncertainty direction does **not**
  install abstention beyond the random control → **legibility ≠ steerability**, now shown with an
  interpretable SAE direction on an independent model. Any genuine, control-beating abstention install
  would be a *positive* and a partial challenge to the F121 one-sidedness — reported as such.

## Report regardless of outcome

Part 1: per-direction + combined AUC, supervised ceiling, floor, 1.7B MC1 accuracy + label
hand-check. Part 2 (if run): per-item hand-read vs random control, α sensitivity. → findings.md +
journal. Staged: Part 1 first; Part 2 only if Part 1 shows the direction reads the boundary.
