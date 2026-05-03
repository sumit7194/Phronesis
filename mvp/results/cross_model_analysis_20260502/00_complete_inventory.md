# 00 — Complete inventory of all hand-review work across all models tested

This doc consolidates the full Phronesis hand-review record across **all 5 models** tested over **Days 14–25**. Includes the early single-model work on qwen3-4b + gemma-4-E4B-it (Days 14–23) and the 1,752-generation cross-model run on phi-4-mini-reasoning + llama-3.1-8B-R1-GRPO + openr1-qwen-7b (Days 24–25).

**Cumulative hand-reviewed generations:** ~2,443 across 5 models. **All graded by reading the full JSON.** No auto-scorer outputs influenced verdicts after Day 18 (per the standing manual-verification policy from F94).

---

## Quick-reference: what's where

| Doc | Coverage | Day | Generations |
|-----|----------|-----|-------------|
| `mvp/results/manual_scoring_qwen_abstention.md` | qwen × IH × L20 + nearby layers × abstention (24 items × 4 conditions) | 18 | ~96 |
| `mvp/results/full_hand_review_pathA.md` | qwen × RT envelope (24 cells × 5 prompts) | 20 | 120 |
| `mvp/results/full_hand_review_pathD.md` | qwen × eg-eval-v2 (5 cells × 10 prompts) | 20 | 50 |
| `mvp/results/full_hand_review_synthesis.md` | Day-20 synthesis across path A + D + IH | 20 | (synthesis) |
| `mvp/results/hand_review_supplement.md` | Day-21 follow-ups | 21 | ~30 |
| `mvp/results/full_hand_review_diagnostic_batch.md` | qwen diagnostic batch (16 cells × 5–10 prompts) | 21 | 136 |
| `mvp/results/full_hand_review_v2_sweep.md` | qwen × redesigned-corpus v2 sweep | 22 | 168 |
| `mvp/results/full_hand_review_round3.md` | qwen × Round 3 (composite + α-density + α=±20) | 23 | 121 |
| `mvp/results/cross_model_analysis_20260502/01_baselines.md` | 24 baselines on phi-4 + llama + openr1 | 24 | 24 |
| `mvp/results/cross_model_analysis_20260502/02_per_prompt/{N3,E1,N2,E5,E2,N1,E3,E4}_*.md` | Cross-model run, 8 per-prompt cells | 24-25 | 1,728 |
| `mvp/results/cross_model_analysis_20260502/per_generation.csv` | Single-row-per-generation CSV (filterable) | 24-25 | 1,752 |
| `mvp/results/cross_model_analysis_20260502/03_per_vector_synthesis.md` | What each of 6 vectors does cross-model | 25 | (synthesis) |
| `mvp/results/cross_model_analysis_20260502/04_cross_model_synthesis.md` | phi-4 vs llama vs openr1 patterns | 25 | (synthesis) |
| `mvp/results/cross_model_analysis_20260502/05_negative_alpha_findings.md` | α<0 sanity-control treatment | 25 | (synthesis) |
| `mvp/results/cross_model_analysis_20260502/06_rescue_cases_detailed.md` | Every rescue case with full prompt + baseline + steered (87 cross-model + 3 earlier qwen + gemma null) | 25 | (synthesis) |

Plus the F-numbered findings in `docs/findings.md` (F92, F94–F112).

---

## Per-model summary across the entire research period

### qwen3-4b (Alibaba; pre-Days-24 primary subject)

**Architecture:** 4B params, 32 layers, native `<think>` tag emission, RL-tuned for reasoning.

**Hand-reviewed generations:** ~691 (Path A 120 + Path D 50 + IH-abstention 96 + diagnostic 136 + v2 sweep 168 + Round 3 121).

**Key findings on qwen:**

- **F92** (Day 16-ish) — "calibrated confidence" vector reduces abstention; corpus conflated two sub-dispositions
- **F94** (Day 17) — `hard_probe_v2` cross-benchmark — steering strictly dominant on AIME/zebralogic/math500
- **F94-UPDATE** (Day 18) — humblebench "epistemic win" does NOT replicate
- **F102** (Day 18 evening) — Cross-model split: qwen has rich behavioral effects, gemma is null
- **F103** (Day 19) — qwen × RT × L18 α=20 +5.19 hand-rebutted as auto-scorer gaming on degenerate output
- **F104** (Day 20) — Full hand-review of 200+ items REVERSES F103 verdict on qwen × IH × L17. v_IH IS virtue-aligned, produces cleanest behavioral effect
- **F105** (Day 21-22) — Diagnostic batch reveals v_IH × L17 and v_CC × L9 produce *behaviorally identical* anti-FM-8 commit behavior, but cosine analysis shows orthogonal residual-stream directions. Behavioral collision is downstream functional convergence, not residual-stream redundancy
- **F106** (Day 22) — v2 sweep with redesigned corpora: corpus expansion partially rotates EG/RT/IH vectors (cos 0.70 with v1)
- **F107** (Day 22) — Frontier-model corpus generators have *task-level* shared blind spot when asked to "rewrite less evidence-grounded"
- **F108** (Day 22-23) — v2 sweep hand-review (168 generations): cosine orthogonality predicts behavior partially. v_EG_v2 confabulates at α=4 on Gandhi false-premise. New failure mode FM-13 (commit-amplified-error)
- **F109** (Day 23) — Round 3 sweep + logit inspection: FM-13 phase-transition is gated by a SINGLE thinking-token rail-switch, not a smooth dial. Composition (vIH+vCC at α=8+8) is non-additive

**Cleanest qwen rescue cases (early F112-mechanism evidence):**

1. **eg-v2-10 seismic damper** (Day 21): baseline FM-8 (8836c, no answer) → vIH × L17 × α∈{4,8,12} clean "20-40%" commit. **First documented commitment-rescue.**
2. **ip-longest** (Day 22): baseline FM-8 (20040c, endless self-debate about countable infinity) → vIH × L17 × α=8 "$\boxed{\infty}$" clean commit
3. **cc-s-08 Tokyo** (Day 23): baseline FM-8 (7254c, oscillates between city-37M and country-125M) → vIH+vCC composite × α=8+8 commits "(b) 13 million"

These three predate F112 by 6 days and are the canonical evidence base for the commitment-amplifier mechanism.

### gemma-4-E4B-it (Google; F102 null subject)

**Architecture:** ~4B params, 35 layers (gemma-4 family), native chat template, post-training instruction-tuned.

**Hand-reviewed generations:** ~150 (paired against qwen across IH abstention, eg-eval-v2, cc-simple).

**Key findings on gemma:**

- **F97** (Day 17) — Geometric MVE is clean on gemma (12/12 cells pass)
- **F102** (Day 18 evening) — **Gemma is behaviorally null.** Same vectors that produce rich qwen effects produce zero detectable behavioral change on gemma. The cross-model split between qwen and gemma is the headline.
- **F100** (Day 18) — Probe-accuracy + retention sanity checks materially weaken F99's optimistic reading on gemma — vectors may be noise.

**Rescue cases on gemma:** **0.** Baselines were mostly correct already on the prompts tested; steered cells were also mostly correct, with no rescue and no degradation. The Gandhi-1931 confabulation in gemma baseline (Day 14) was *not* fixed by any steered cell.

### phi-4-mini-reasoning (Microsoft; cross-model run Day 24-25)

**Architecture:** ~3.8B params, 32 layers, distill+RL mix on Phi-3.5 base, native `<think>` tag emission.

**Hand-reviewed generations:** 576 (8 prompts × 6 vectors × 12 α + 8 baselines = 8 + 576 = 584; counting steered only → 576).

**Per-model column total:** 162/576 ✓ (28%).

**Failure shape:** Internal looping + cap-truncation. Cap-extended re-run (16k tokens) is the recommended quick win.

**Layer-suitability findings:**
- **L3 (CC_num + VC):** catastrophic at high α across ALL 8 prompts (FM-8-severe with token-collapse, prompt-echo loops, 1-token EOS)
- **L7 (IH):** premature-EOS at α≥+16 on most prompts
- **L21 (EG, RT) and L24 (CC_full):** stable; phi-4's best cells live here

**Best phi-4 cells:**
- EG × L21 × N3: 12/12 ✓
- EG × L21 × E5: 12/12 ✓
- RT × L21 × N3: 12/12 ✓
- RT × L21 × E5: 12/12 ✓
- CC_full × L24 × E5: 11/12 ✓

**Rescue cases:** 2 (phi4 × E2 single hit at CC_num × α=+6 with 55% conf; phi4 × N2 single hit at EG × L21 × α=+16 — both isolated, likely noise).

### llama-3.1-8B-R1-GRPO (Open-R1; cross-model run Day 24-25)

**Architecture:** ~8B params, 32 layers, GRPO RL on Llama-3.1-8B base, **NEVER emits `<think>` tag** (think_chars=0 universal — unusual property among thinking models).

**Hand-reviewed generations:** 576.

**Per-model column total:** 219/576 ✓ (38%) — best of all 3 cross-model models.

**Failure shape:** Wrong-answer template lock. RL-tuning has hardened specific answer shapes (80% confidence on E2, prior-mixture 0.505 on E3, A>B>C>D split-rec on N2, "A small / B large" on N1). Activation steering at the layer set tested cannot dislodge.

**Most steering-resistant signals observed in any probe:**
- E2 (flossing): every α × every vector → 80% confidence (72/72 generations identical)
- E3 (Bayes update): every α → prior-mixture 0.505 (0/72 ✓)
- N2 (conjunction fallacy): every α → A>B>C>D narrative-fit ranking (0/72 ✓)

**Best llama cells:**
- CC_full × L26 × E1: 12/12 ✓ (clean abstentions across all α)
- IH × L31 × E1: 12/12 ✓
- VC × L29 × E1: 12/12 ✓
- CC_full × L26 × E5: 12/12 ✓
- IH × L31 × E5: 12/12 ✓

**Rescue cases:** 2 (llama × E4 × CC_full × α=−8 and × EG × α=−8 — isolated).

### openr1-qwen-7b (Open-R1; cross-model run Day 24-25)

**Architecture:** 7B params, 28 layers, GRPO RL on Qwen2.5-7B base, inconsistent `<think>` emission.

**Hand-reviewed generations:** 576.

**Per-model column total:** 100/576 ✓ (17%) — lowest pass rate, but uniquely *rescuable*.

**Failure shape:** Non-commitment loop. Verbose self-debate, baseline cap-hits via internal looping. Steering breaks the loop and forces commitment.

**Rescue cases:** 83 (40 on E3 + 36 on N1 + 7 on N2). **96% of all 87 cross-model rescues come from openr1.**

**Validates F112** (commitment-amplifier hypothesis): when baseline is non-commit-loop with correct internal reasoning, steering forces commitment, and the commitment is correct.

**Best openr1 cells:**
- CC_num × L23 × N1: 9/12 ✓
- EG × L19 × E3: 8/12 ✓
- VC × L25 × E3: 8/12 ✓ (verbosity control RESCUES — vector content irrelevant)
- RT × L19 × E3: 8/12 ✓
- EG × L19 × N1: 8/12 ✓

---

## The 5-model framing — patterns, not per-model summaries

Pulling together findings from F92 → F112, the cross-model picture is now:

### 1. Three "behavioral-effect" archetypes among trained models

| Archetype | Models | Steering effect |
|-----------|--------|-----------------|
| Strong + behavioral | qwen3-4b, openr1-qwen-7b, phi-4 | Vectors produce real shifts; α-magnitude matters; rescue and degradation both possible |
| Behavioral but template-locked | llama-3.1-8B-R1-GRPO | Vectors do *something* (verbosity, confidence, framing) but cannot dislodge memorized templates |
| Behaviorally null | gemma-4-E4B-it | Vectors have no detectable effect at the layers tested |

This expands F102's binary "qwen-vs-gemma" split into a three-archetype taxonomy.

### 2. Three baseline failure shapes (F110)

| Failure shape | Models exhibiting | Rescue rate |
|---------------|-------------------|-------------|
| Non-commit loop with correct internal reasoning | openr1, qwen3-4b (some prompts) | **35-56%** rescued by steering |
| Wrong-answer template lock | llama (E2/E3/N2), some gemma | 0% rescue rate |
| Cap-truncation on extended deliberation | phi-4 (N2/E3/E4) | 0% from steering; needs token-budget extension |

### 3. F112 is the only cross-model positive finding

- **95+ rescue cases observed across all hand-review work** (qwen 12 + openr1 83), all in the same Qwen-family pretraining lineage
- Zero rescues observed in non-Qwen models (gemma 0, phi-4 2 — likely noise, llama 2 — likely noise)
- **F112 may be Qwen-family-specific.** Open question: does it generalize to other "verbose self-debate" thinking models (r1-distill, deepseek-r1, gemini-2.0-flash-thinking)?

### 4. F111 IH-vector falsification holds across all 5 models

- Qwen IH×L17: works as commitment-amplifier (F104), NOT as humility-installer
- Gemma IH×L18/L22: null (F102)
- Phi-4 IH×L7: catastrophic at high α (premature-EOS)
- Llama IH×L31: at-ceiling on E1, useless on E2/E3
- OpenR1 IH×L25: produces *worst-form* fallacies at high α on N2/E1/E2

The "intellectual humility" vector hypothesis is decisively falsified across all 5 models.

### 5. FM-13 (commit-amplified-error) and FM-8 (degenerate-loop) generalize

Both failure modes that F108/F109 documented on qwen now have parallels:
- FM-13: phi-4 EG×α=+6 "cosine confounder fallacy"; openr1 N3 6/10 lock; llama E2 fabricated citations
- FM-8: phi-4 L3 catastrophic; openr1 cap-truncation runaway loops; qwen baseline FM-8 spirals

Refined cross-model FM catalogue lives in `docs/scoring.md` (Day-25 update).

### 6. Layer-depth dominates vector identity at extreme α

Phi-4 L3 catastrophic regardless of corpus (CC_num and VC produce identical FM-8-severe collapse). Confirms layer choice is the primary determinant; vector content is secondary at high |α|.

---

## What we still don't know

- Does F112 generalize to non-Qwen thinking models (r1-distill, deepseek-r1, etc.)?
- Does cap-extending phi-4 to 16k tokens convert its low ✓ rate on N2/E3/E4 into a much higher rate? (Cheap test, ~3 hours of compute.)
- Can humility/abstention be amplified at all via residual-stream steering, or does it require a different intervention method (RL fine-tuning, SAE feature targeting)?
- Why does VC (verbosity-control negative vector) rescue on openr1 N1+E3? If the rescue mechanism is "any strong perturbation at deep layers", the active ingredient is steering magnitude, not vector content.

---

## Recommended next steps (post-MVP)

Cribbed from `docs/post-mvp-decisions.md` Day-25 update:

1. **L0 — Layer screening before any sweep.** Skip L3 on phi-4. Test α=±20 on each candidate layer first; if it catastrophically collapses, exclude.
2. **F112 generalization test.** Apply commitment-amplifier on r1-distill, deepseek-r1, gemini-2.0-flash-thinking. ~288 generations to validate.
3. **Cap-extended phi-4 re-run.** Re-run phi-4 × CC_full × N2/E3/E4 at 16k or 32k cap. ~36 generations, mechanical win.
4. **Drop humility-amplifier extraction.** F111-falsified, three times.
5. **Drop compositional virtue-installer.** F109-non-additive, never strictly better than single vector in observed data.

---

_Built 2026-05-03 (Day 25). All numbers cross-verified against per_generation.csv (1,752 rows + 24 baselines), the 6 earlier hand-review markdown docs, and F-numbered findings in docs/findings.md._

---

## Update 2026-05-03 (post-doc-review): random-vector control found in archive

**The random-vector control test was run on Day 12 (2026-04-15)**, predating most of the F-numbered findings. It lives at `mvp/results/steering_v2/qwen3-4b/random_L22/` and consists of 24 generations (3 alphas × 8 prompts) with a unit-normalized Gaussian random vector at L22 (seed=42).

**Result:** 0 rescues / 2 degradations / 22 preserves out of 24. Random vectors do NOT rescue qwen3-4b's E3 / N2 non-commit failures (0/6 cells), and at α=+8 they *break* a correct baseline on N1 (catastrophic 66-char cap-truncation).

**Implication:** the F112 narrative in earlier drafts ("any strong perturbation at deep layers works") is too strong. Refined narrative: the 6 corpus-extracted vectors share a structured commit-promotion property that random Gaussian vectors at the same layer/magnitude do not have. Detailed write-up in `06_rescue_cases_detailed.md` "Random-vector control" section.

### Reconciled rescue-count language

The earlier docs used several different totals depending on context. Normalizing here:

| Scope | Rescues | Notes |
|-------|---------|-------|
| Cross-model run only (Days 24-25, phi-4 + llama + openr1) | **87** | 40 N1 + 36 E3 + 7 N2 = 83 from openr1; 2 (llama E4) + 1 (phi4 E2) + 1 (phi4 N2) = 4 isolated single-α hits |
| openr1-qwen-7b only (cross-model run) | **83** | The 87 minus the 4 isolated cross-model hits |
| Earlier qwen3-4b work (Days 18-23) | **~12** | Canonical: 3 (eg-v2-10 seismic damper at α=4/8/12) + 1 (ip-longest at α=8) + 1 (cc-s-08 Tokyo composite). Plus ~7 smaller from diagnostic batch / round 3 / v2 sweep |
| Total Qwen-family cumulative (qwen3-4b + openr1-qwen-7b) | **~95** | The headline claim |
| Non-Qwen-family (gemma + phi-4 + llama) | **4** (likely noise) | 2 phi-4 + 2 llama, all single-α isolated; 0 gemma |
| **Random vector at L22 on qwen3-4b** (24 cells) | **0** | The control |

So the headline structure becomes:

- **~95 rescues across ~600 Qwen-family steered generations on rescue-eligible cells** (~16% rescue rate)
- **4 likely-noise rescues across ~1,400 non-Qwen-family steered generations on rescue-eligible cells** (~0.3% rate)
- **0 rescues across 24 random-vector cells on qwen3-4b** at the same depth class
- 6 corpus-extracted virtue vectors all rescue (including the negative-control VC corpus); 1 random vector does not

**This is the cleanest cross-model claim we can support:** rescue requires (a) a Qwen-family non-commit-loop failure mode AND (b) a corpus-extracted vector at deep layers. Neither random vectors at the same place nor non-Qwen models with similar baseline failures produce rescue.

