# Prereg — Path A: Grounded Calibration Steering (does grounded data fix the steering null?)

**Date:** 2026-06-28 · **Follows:** [EXPERIMENTATION_GUIDELINES.md](EXPERIMENTATION_GUIDELINES.md) · **Model:** Qwen3-4B (local) · **Seed:** `mvp/results/legibility/calibration_seed_4b.json` (29 hedge-targets + 20 commit-targets, hand-cleaned, F172).

## Question
Every prior steering attempt nulled under multi-seed random controls (F160/F171), but those used **doubt-contaminated IH triplets**. Now that we have a **grounded, model-conditioned, bidirectional** calibration contrast, does a steering vector built from it **beat random controls** at moving the 4B in the target direction? I.e., **was the null a *data* problem, or is steering the wrong tool?**

## Vectors (diff-of-means / CAA, last-token, 4B layer sweep [10,14,17,20])
Build contrast pairs per seed item: `assert_text` = "{Q} {the model's own answer}" vs `hedge_text` = "{Q} I'm not sure — I don't have reliable information about {entity} and could be wrong."
- **v_hedge** = mean(hedge_act) − mean(assert_act) over **hedge-targets** (confident-wrong items; n≈29). Direction = "express uncertainty."
- **v_commit** = mean(assert_act) − mean(hedge_act) over **commit-targets** (correct-but-self-doubts; n≈20). Direction = "assert confidently."
- **Diagnostic:** cos(v_hedge, v_commit). **Prediction: strongly negative** (≈−1) → confirms calibration is a *single confidence axis* traversed in opposite directions per item (the cancellation insight: a single fixed vector can't be "calibration").

## Steering test (held-out, α-sweep calibrated to the 4B residual norm)
- **Split:** extract each vector on ~⅔ of its cell, **hold out ~⅓ for the steering eval** (hedge ≈20 extract / 9 eval; commit ≈14/6). Small — tier accordingly.
- **v_hedge** applied (+α) to held-out **hedge-target** questions → does hedge-rate rise (does it stop confabulating)?
- **v_commit** applied (+α) to held-out **commit-target** questions → does it commit the correct answer (stop self-doubting)?
- **α** = fractions of the measured residual-stream norm at the layer (per F171 — never assume the old α=16 transfers).

## Controls (§2 — mandatory)
- **Baseline** (α=0) on the same held-out items.
- **Multi-seed random vectors** (≥3 seeds), magnitude-matched, same α, same items. **The pass bar: v_hedge/v_commit must beat all random seeds.**
- **Sign control:** −α should do the opposite.

## Measurement (§3)
- Hedge-rate / commit-rate by `auto_` prefilter (hedge markers: "not sure / don't know / can't / no reliable…") **then hand-read** (regex is prefilter only).
- Greedy for the causal α-sweep; a small T=0.7 sampling check at the best α (§7).
- Save all raw generations + seeds.

## Hypotheses & falsifier
- **H1.** cos(v_hedge, v_commit) is strongly negative (single confidence axis).
- **H2 (the real test).** v_hedge beats random at raising hedge-rate on held-out confab items (and/or v_commit beats random at raising commit-rate). → grounded data *does* steer; the prior null was partly a data problem.
- **Falsifier / likely outcome.** If v_hedge/v_commit are **indistinguishable from matched-magnitude random** at usable α (coherent outputs), then **steering is the wrong tool even with grounded data** — a clean, strong negative that closes the steering arm and motivates Path B (read-then-act). State whichever way it lands, tiered.

## Outputs
Vectors + diagnostics, per-item steered generations (all α, all random seeds), hedge/commit-rate vs α (v_real vs random), cos(v_hedge,v_commit), tiered finding. Harness `mvp/steer_calibration_4b.py`. Local, no billing.
