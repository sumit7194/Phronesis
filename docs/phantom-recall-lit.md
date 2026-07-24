# Phantom recall / conditioned override — literature map (2026-07-12)

**Phenomenon.** A well-known question is subtly altered so the correct answer changes; the model
ignores the alteration and emits the *memorized* answer to the original. User-supplied examples:
surgeon riddle with father→mother swap (correct: "the father"; models say "the mother"), and
placing an *already-dead* cat in Schrödinger's box (models still recite "both alive and dead").

**Status: NOT a novel phenomenon.** Named independently in three literatures. Any writeup must
position as mechanistic follow-up, not discovery.

## The three names
| Name | Source | Framing |
|---|---|---|
| **Phantom recall** | [2510.11812](https://arxiv.org/html/2510.11812v1), Mukhopadhyay et al. (ASU) | LLMs "confidently reproduce memorized solutions or spurious rationales that no longer fit altered puzzle scenarios" |
| **Conditioned override** | [marcodsn/altered-riddles](https://github.com/marcodsn/altered-riddles) | Falling back to memorized answers when a familiar riddle is subtly changed |
| **Memo Trap / Redefine** | [Inverse Scaling Prize, 2306.09479](https://arxiv.org/html/2306.09479v1) | Reciting memorized text when the task requires deviating from it |

## Key quantitative anchors
- **Phantom Recall:** 25 base puzzles → 149 variants, 11 models (GPT/Gemini/Claude + Llama/Qwen/
  Mistral/Phi/InternLM). **Near-perfect on originals; 22–51% on perturbations** (open models).
  Perturbations preserve logical structure but alter values/constraints so the answer must change.
  Mitigation via prohibitory prompting ("do not assume", Understand→Solve→Verify) recovers only
  **4.7–10.1 pts**; gap persists. Error taxonomy: deductive failure / cascading error / improper
  elimination. **Explicitly does NOT examine activations, attention, or embeddings** ← the gap.
- **Altered Riddles:** 4 alteration types — *constraint addition* (dead-cat case), *meaning shift*,
  *context swap*, *bias probe* (surgeon swap). Metric **COR** = "among altered riddles where the
  model answered the ORIGINAL correctly, how often did it give that same (now-wrong) original
  answer to the altered version?" Lower better. Leaderboard best ≈ **28.7–30.6% COR**
  (mimo-v2-pro 28.7 / gpt-oss-20b 29.0 / gpt-5.4-mini 30.6). Dataset:
  `huggingface.co/datasets/marcodsn/altered-riddles`.
- **Inverse scaling (the striking bit):** on Memo Trap and Redefine, **larger models are WORSE** —
  stronger memorization of the canonical form ⇒ harder to override. Scale aggravates rather than
  fixes. (Note: some inverse-scaling tasks later shown U-shaped, [2211.02011](https://arxiv.org/pdf/2211.02011) — check
  whether Memo Trap recovers at frontier scale before claiming monotonic inverse scaling.)

## Adjacent lines (perturbation fragility)
- **GSM-Symbolic** — name/number perturbation of GSM8K; ~4% drop on numeric perturbation,
  compounding when combined; distinguishes memorization from robust deduction.
- **MATH-Perturb** ([2502.06453](https://arxiv.org/pdf/2502.06453)) — hard perturbations of MATH.
- **Fragile Reasoning** ([2604.01639](https://arxiv.org/html/2604.01639)) — mechanistic analysis of
  sensitivity to *meaning-preserving* perturbations; architecture-specific failure localization
  (Llama localized 71.7% patching recovery; Qwen "entangled" 0.0%). ← relevant + cautionary for us.
- **Llama See, Llama Do** ([2505.09338](https://arxiv.org/pdf/2505.09338)) — contextual entrainment
  and distraction, mechanistic perspective.
- **Prompt repetition** (the Reddit trick): [2412.07923](https://arxiv.org/html/2412.07923v3) finds
  repetition gains **up to 6% but NOT statistically significant**. Folklore, weak prior.

## ⚠ Prior-art risk for the mechanistic question
Our angle ("is the correct answer present-but-drowned or never-computed in the workspace?") is
unexplored *at search level* in the phantom-recall papers specifically. BUT the adjacent
**context-vs-parametric knowledge conflict** literature is large and partly mechanistic.
**Before any writeup: lit-check "knowledge conflict" + "context-memory conflict" +
interpretability/probing.** Assume replication until proven otherwise (see the 07-12 pattern:
gate→search, F191, behavioral-Jacobian all landed as replications).

## Why our instrument fits
Phantom Recall is a *behavioral* taxonomy. We have a workspace readout and, from the 07-12
correction, the exact distinction needed:
- **q1 spiral** — correct concept present but **drowned** (rank ~14, w≤0.015, under `maybe`/`etc`)
- **q6 commit-wrong** — correct answer **absent** ("13" appears 0× in the whole trace)
Mapping phantom recall onto that axis is the open mechanistic question.
Feasibility helpers from our own findings: riddle answers are **words** ("father", "dead"), not
numbers → dodges **E18 "lens broken for facts"**; and **J-lens ≈ logit lens at 4B** → cheap readout.
