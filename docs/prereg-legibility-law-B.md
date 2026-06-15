# Pre-registration — Experiment B: is the LLM's own knowledge boundary linearly legible?

*Locked before any activation/label was extracted. Follows F165 (Experiment A), which showed
first-order object-facts are linearly legible regardless of route. B asks the second-order question
that A's result forces.*

## Why this question (set up by A / F165)

A found object-scalars are linearly legible whether recalled or supplied — so **F121's
"can't install abstention via a linear push" is NOT explained by scrambling of object knowledge.**
The remaining candidate: maybe the *meta*-property — "does the model know X" — is the thing that is
(il)legible. B probes exactly that.

## Setup (Qwen3-4B, Mac/MPS)

- **Battery, two domains** (so "correctness" is not reducible to one legible scalar — see confound):
  - elements 1–103 → atomic number (exact ground truth; model knows light, misses heavy/synthetic)
  - ~50 countries → capital city (exact GT; famous→obscure spread)
- **Labels:** generate the model's answer (chat template, thinking disabled, greedy, short), then
  **exact-match** against ground truth → correct / incorrect. A sample of the auto-labels is
  **hand-verified** (per protocol) before probing.
- **Read position:** last token of the chat-templated prompt (`add_generation_prompt=True`), i.e. the
  model's state *just before it answers* — where a "do I know this" signal would have to live for
  abstention to be steerable. Layers {4,8,…,36}.
- **Probe ladder (classification):** linear = StandardScaler→LogisticRegression (full-dim);
  nonlinear = StandardScaler→PCA(≤50)→kNN classifier. Metric = **ROC-AUC**, StratifiedKFold(5),
  out-of-fold probabilities. **scramble signature = linear AUC ≈ 0.5 but nonlinear AUC high.**
- **Floor:** labels permuted (5 seeds) → AUC must average ≈ 0.50.

## Predictions (locked)

- **Kadavath-consistent (knowledge boundary IS legible):** linear AUC ≥ 0.65 at some layer.
  → The "I-don't-know" signal is a linear direction. This is in **tension with F121**: if abstention
  were a linear direction, a linear push should install it. F121's one-sidedness would then need a
  **non-legibility** explanation (e.g. it's legible-to-read but not the causal lever for the output),
  and the Legibility Law's "scrambled" story does NOT explain F121.
- **Scramble-consistent (boundary is illegible):** linear AUC ≤ 0.55 **and** nonlinear AUC ≥ 0.65.
  → The knowledge boundary is present but scrambled — which **would** explain why a linear steer
  can't install abstention (F121). This would be the law's clean win on a second-order property.
- **Both flat (AUC ≈ 0.5 linear and nonlinear):** the pre-answer state doesn't encode the boundary at
  all (signal may live post-answer); inconclusive for the boundary-legibility question.
- **Floor:** shuffled AUC ≈ 0.50 (else harness broken).
- **Power:** the probe must beat 0.5 on *something* (e.g. decoding domain) to prove it has signal.

## Confound (declared up front)

Correctness on the elements domain correlates with atomic number Z (heavy → wrong), and Z is itself
legible (A). So an elements-only correctness probe could trivially decode "is Z large" instead of a
genuine metacognitive signal. **Mitigation:** two domains; report **per-domain AUC** and a
**within-narrow-Z-band** check — if linear AUC collapses to ≈0.5 when the scalar/difficulty proxy is
held roughly constant, the apparent "boundary legibility" was the difficulty proxy, not metacognition.
Capital correctness is not a scalar, providing the cross-domain check.

## What we report regardless of outcome

Correct/incorrect split (overall + per domain), the per-layer linear/nonlinear AUC table, floor,
power, the within-Z-band confound check, a hand-verified label sample, and a verdict against the
locked thresholds → findings.md + journal. Positive, null, or confounded: all reported.
