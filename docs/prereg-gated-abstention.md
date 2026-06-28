# Prereg — Path B (v1): Read-then-Act Gated Abstention

**Date:** 2026-06-28 · **Follows:** [EXPERIMENTATION_GUIDELINES.md](EXPERIMENTATION_GUIDELINES.md) · **Model:** Qwen3-4B · **Data:** `mvp/results/legibility/knowledge_edge_4b.json` (200 items: per-item confidence signals + hand-scored GT, from F172).

## Idea
F173 showed a *uniform* steering push only fragilely rides the model's own confidence gradient (78% confab / 29% known hedge at a knife-edge α, collapsing to global just above). Path B does the clean thing: **READ** the model's confidence per item, **ACT** (abstain/hedge) only where confidence is low. Selectivity comes from the reader, not from a fixed direction — sidestepping the one-axis cancellation (cos=−0.9, F173).

This v1 is computable from existing signals (the confidence values + GT are already in hand) — the "act" is template abstention; no new generation. It establishes the *capability ceiling* before any inference-time wiring.

## Method
- **READ — confidence score per item.** Evaluate each F172 signal (P(True), seq-logprob, −mean-entropy, −semantic-entropy) and a **combined** score (z-normalized average, plus a leave-one-out logistic-regression combiner to avoid overfitting). Direction: higher = more confident.
- **ACT — gate.** Abstain ("I'm not sure / I don't have reliable information") when confidence < threshold; else answer (the existing greedy answer).
- **Sweep the threshold** → risk-coverage / selective-accuracy curve over the full 200 (GT = `hand_no_ok`).

## Metrics
- **Selective accuracy vs coverage:** of the items it chooses to answer (top-c by confidence), what fraction are correct? Baseline (answer all) = 22%.
- **Four-cell outcome at a chosen operating point:** answered-correct (good), answered-wrong (confab slips through, bad), abstained-wrong (caught, good), abstained-correct (servility, bad).
- **Direct comparison to F173 uniform steering:** on the SAME held-out confab + known items, gated abstention's hedge-rate on confab vs known — does it beat F173's 78%/29% (49pp) selectivity gap?

## Hypotheses & falsifier
- **H1.** Gated abstention raises selective accuracy well above 22% as coverage drops (e.g. answering the top ~30% by confidence is markedly more accurate), bounded by the reader's AUROC≈0.75.
- **H2.** Gating beats F173's uniform steering on selectivity (larger confab−known hedge gap) — read-then-act > uniform push.
- **Falsifier.** If the risk-coverage curve is ~flat (selective accuracy ≈ 22% at all coverages) or the combined signal doesn't beat the best single one, the reader isn't actionable for gating despite AUROC 0.75 — report it; that would push toward a learned/trained gate or richer signals.

## Controls & integrity
- Combined signal validated by **leave-one-out CV** (no train/test leakage); report single-signal baselines too.
- GT is hand-scored (F172). Abstention "correctness" anchored on GT, not the confidence signal (§3).
- Tiered conclusion. Harness `mvp/gated_abstention_4b.py`. Local, no model run (analysis of existing signals). v2 (inference-time gating + better answers on retry) is future work.
