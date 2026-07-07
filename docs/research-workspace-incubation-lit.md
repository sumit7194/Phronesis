# Research notes: literature behind the workspace-incubation experiment

*Compiled 2026-07-07 evening (web sweep during the incubation design discussion). Feeds
`docs/idea-workspace-incubation.md` (design v2 → v3). These are notes + implications, not claims.*

## 1. Concept injection at small scale is established — and does not need the J-lens

- **Lindsey 2025, "Emergent introspective awareness in LLMs"** (Anthropic,
  anthropic.com/research/introspection): inject a concept's steering vector into the residual
  stream, ask the model whether it notices an "injected thought." Claude Opus 4/4.1: ~20%
  detection, ~0% false positives. Vectors are **contrastive activation vectors** (activation
  difference between concept-present and concept-absent prompts), *not* lens rows.
- **Replications on open models** (arxiv 2602.20031 "Latent Introspection"): Qwen2.5-Coder-32B
  and **Llama-3.1-8B** reproduce ~20% detection under the original pipeline. → 8B-class models
  support detectable injection; a 4B is one notch below the proven floor, not off the map.
- **Implication for us:** our injection arm was gated on the J-lens QC (which failed at n=20).
  Wrong gate — **E1 injection should use Lindsey-style contrastive vectors**, extractable on
  the Mac in an evening. The J-lens remains a *readout* tool only. This un-blocks the arm.

## 2. The meta-instruction effect is real and large

- **Pearson-Vogel et al. 2026, "Feeling the Strength but Not the Source"** (arxiv 2512.12411):
  by default introspective detection of injected concepts is ~suppressed in sampled outputs
  (0.3%) but jumps to **39.9%** when the prompt explains that injection may occur; intermediate
  layers show the concept via logit lens even when unverbalized.
- **Implication:** the two-Claude prediction ("no spontaneous binding; meta-instruction flips
  it") has direct empirical precedent. Design the meta-instruction arm as PRIMARY, and expect
  the read-arm (logit lens over the distractor span) to show loading even when behavior is
  silent — that dissociation is itself a result.

## 3. The failure family we want has a name and an LLM signature

- **Braingle/brainteaser study 2025** (arxiv 2505.10844 "Creativity or Brute Force?"): LLMs
  "frequently default to exhaustive search, especially on harder problems" instead of the
  creative shortcut — **computational Einstellung/fixation**. Distinct from our observed
  wobble (F187 rumination: solution found then abandoned) and boundary (F191: concept loaded,
  misapplied) and wall (unreachable).
- **Taxonomy as of today (empirically grounded in our own data):**
  | family | concept state | example | usable for incubation? |
  |---|---|---|---|
  | wobble | present, abandoned | Tom's trees (screen cand.) | no (commit-gating arc) |
  | boundary | present, misapplied | F191 items | no (F190: hints don't help) |
  | wall | unreachable | math500-596af | no (nothing to supply) |
  | **fixation** | **absent but supply-able** | insight problems | **yes — the target** |

## 4. Memorization is the trap; reconstruction is the fix

- **BRAINTEASER** (arxiv 2310.05057, SemEval-2024 Task 9): models often answer classic lateral
  puzzles from memory; performance collapses on **semantic/context reconstructions** that
  preserve the deep structure under a novel cover story. GPT-class ≈ halfway between random
  and human; smaller models ≈ random.
- **Implication:** every stuck-problem we use must be a **rewritten variant** of its classic
  ancestor (novel entities, numbers, setting; same kernel). The E0 screen empirically verifies
  non-memorization (the model must actually FAIL it).

## 5. Text hints demonstrably unstick small models; injection-as-hint is unexplored

- **HintMR / TeaCH 2025** (arxiv 2604.12229): concise targeted hints beat no-hint baselines on
  R1-Distill-Qwen-7B — hint-sufficiency at 7B-class is established.
- No published work found where the hint is delivered as an **activation-space injection**
  rather than text. That gap is our E1.

## The five properties of a usable stuck-problem (the hunting definition)

1. **Stable failure** — greedy fails AND ≥7/8 samples fail (excludes wobbles by construction).
2. **Short-hint sufficiency** — a ≤5-word appended hint flips it (existence proof; F190 lesson).
3. **Kernel ≠ answer** — the hint names a *method* ("parity", "backwards"), not the solution.
   (RAT items, where kernel==answer, are kept as a separate positive-control tier.)
4. **Kernel = 1–2 common tokens** — injectable (clean contrastive vector) and within the
   workspace's ~10–25-concept capacity.
5. **Novel surface** — reconstructed cover story; ancestor recorded for contamination honesty.

## The experiment ladder (each rung standalone)

- **E0 (screen):** stable-fail + short-hint-flip on the reconstructed set → the usable pool.
  Purely behavioral. Stimuli: `mvp/incubation_insight_problems.json`.
- **E1 (injection-as-hint):** at re-attempt, inject the kernel's contrastive vector instead of
  the text hint. α-sweep + magnitude-matched random ×3 seeds (§2 floor). Novel result either
  way; go/no-go for E2's injection arm.
- **E2 (incubation proper):** stuck problem held (context or injection) + hint-bearing
  distractor task + {plain, meta-instruction} × {hint, matched no-hint} → re-attempt lift +
  workspace co-loading read. The full test of the user's original idea.

## Sources
anthropic.com/research/introspection · arxiv 2602.20031 · arxiv 2512.12411 · arxiv
2310.05057 · arxiv 2505.10844 · arxiv 2604.12229 · arxiv 2603.21396 (Mechanisms of
Introspective Awareness) · PMC7644781 (RAT review)
