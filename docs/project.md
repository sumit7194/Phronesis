# Phronesis — Project Overview & Experiment Plan

A living document capturing the project's goals, approach, constraints, and current status. This is the single place to look to understand *what* we are trying to do and *why*. Methodology details live in `concepts.md` (taxonomy) and `findings.md` (running research log). This file should be updated whenever goals, scope, or high-level approach shift — but not for every minor refinement.

---

## One-line description

Phronesis extracts activation vectors for epistemic virtues (intellectual humility, calibrated confidence, rigorous reasoning, and others) from a small open-source language model, then tests whether steering the model along those vectors measurably improves its performance on reasoning and knowledge tasks.

## Motivation

In April 2026, Anthropic's interpretability team published *"Emotion Concepts and their Function in a Large Language Model"* — the direct inspiration for this project.

- Full paper: https://transformer-circuits.pub/2026/emotions/index.html
- Blog summary: https://www.anthropic.com/research/emotion-concepts-function

They extracted 171 internal "emotion vectors" from Claude Sonnet 4.5 and showed that these vectors causally drive model behavior — stimulating the "desperate" vector, for example, increased the model's propensity to take unethical shortcuts on coding tasks. The paper explicitly noted that the same methodology could be applied to non-emotional concepts.

Phronesis takes up that invitation. Instead of extracting emotions, we extract epistemic virtues — the cognitive dispositions that distinguish careful scientific reasoning from sloppy or biased reasoning. And instead of characterizing what these vectors do, we ask the next natural question: **can steering toward epistemic virtues make a small model reason better?**

## Core research question

Do small open-source language models contain linearly-extractable representations of epistemic virtues, and can steering along those representations produce measurable improvements on reasoning-sensitive benchmarks without degrading general capability?

## Hypothesis

Language models trained on large text corpora have seen enough examples of careful-versus-sloppy reasoning that they develop internal representations of the virtues that distinguish them. These representations should be extractable via contrastive data and difference-of-means vector computation, the same methodology Anthropic used for emotions. Furthermore, because epistemic virtues have (arguably) stronger instrumental value than arbitrary emotions, steering toward them should produce improvements on tasks that reward careful reasoning.

This hypothesis has two components, and either can fail independently:

1. **The representation hypothesis.** That small models encode these virtues as reasonably clean linear directions in activation space. If this fails, no amount of corpus engineering will rescue the project — activation steering cannot create competencies the model lacks (see findings.md F11).

2. **The intervention hypothesis.** That steering along the extracted vectors actually improves downstream task performance rather than merely changing style. It is possible to extract a "reasoning transparency" vector that changes how the model talks about its reasoning without changing the quality of the reasoning itself. Both outcomes are informative, but only the first would support the intervention hypothesis.

**Scope condition on the intervention hypothesis (added per F45):** Recent empirical work on activation steering has documented that steering functions as a *dispositional modulator, not a propositional injector* — steering can change behavioral tendencies the model already has access to, but cannot inject knowledge the model does not possess. This defines the boundary of where we expect the intervention hypothesis to hold:

- Steering **should** improve performance on reasoning tasks that are *disposition-limited* — tasks where the model has the necessary knowledge but does not deploy it well due to baseline habits (e.g., defaults to overconfident assertions even when evidence points toward uncertainty).
- Steering **should not** improve performance on reasoning tasks that are *knowledge-limited* — tasks where the model simply lacks the facts needed. Expected failure mode: "the model becomes more confident rather than more correct" (quoting the activation-steering literature).

A successful result for Phronesis is improvement on disposition-limited benchmarks. A null result on knowledge-limited benchmarks is expected and informative — it marks the boundary of what dispositional steering can do rather than a failure of the methodology. Phase 4 benchmark selection must make this distinction explicit, and the writeup must not overclaim improvements on reasoning tasks where the underlying limitation was propositional rather than dispositional.

## High-level approach (six phases)

**Phase 1 — Concept taxonomy.** Define the epistemic virtues precisely enough to generate contrastive training data for each one. Output: `concepts.md`. *(Currently iterating.)*

**Phase 2 — Reference gathering and methodology research.** Read the relevant prior work (Anthropic emotions paper, representation engineering literature, behavioral science on the target virtues, text style transfer methodology). Output: `findings.md`. *(Currently iterating in parallel with Phase 1 via scheduled adversarial research cycles.)*

**Phase 3 — Guidelines architecture.** Write the scaffolding documents that govern data generation: the generation guidelines, the review rubric, worked examples. Output: `generation-guidelines.md`, `review-rubric.md`, possibly `examples/`. *(Not yet started.)*

**Phase 4 — Pilot run on one concept.** Generate a complete corpus for a single high-likelihood concept by hand (no automation), extract its vector, validate it, and run steering experiments. This is the go/no-go signal for the whole project. If the pilot concept does not extract cleanly, the methodology is not viable at the chosen scale and we either move to a larger model or reconsider the project. *(Not yet started.)*

**Phase 5 — Full corpus generation and extraction.** Assuming the pilot succeeds, generate corpora for the remaining concepts and extract their vectors. *(Not yet started.)*

**Phase 6 — Evaluation and write-up.** Measure steering effects against baseline on appropriate benchmarks, compute specificity and transfer metrics, document what worked and what did not. *(Not yet started.)*

## Target model

**Current (Day 22 reality, per F87/F101/F102):** Qwen3-4B is the *de facto primary*. Gemma 4 E4B is included as a control/comparison but produces null behavioural effects at every α and layer tested across 3 days of sweeps.

**Why qwen3-4b became primary:** F87 (Day 7 finding) established that thinking-mode capability matters for the disposition-modulation hypothesis — "thinking" tokens give activation steering a longer dynamic surface to act on. F101+F102 confirmed empirically: gemma's residual-stream geometry is clean (probe accuracy ≥85% on every concept) but behaviourally inert under steering; qwen's geometry is collapsed at deep layers (CC/EG/RT cluster) but produces real (small) behavioural signals.

**Cross-model split is itself a finding** (F102 + F103 + F104) regardless of whether the four-vector hypothesis resolves. Same corpus, same method, opposite verdicts geometrically and behaviourally. That's the publishable scientific finding even if intervention success on neither model materialises.

**Original (April 9):** Gemma 4 E4B running on Apple Silicon (M4 Mac Mini, 16GB) for development. GCP (L4 GPU, asia-southeast1-a) became the actual compute environment from Phase 4 onward (~Day 9).

## Success criteria

The project has three levels of success, each of which would be a meaningful outcome to publish or discuss:

1. **Representation success.** For at least one virtue, we extract a clean vector that (a) predicts the virtue on held-out passages, (b) is stable across nearby transformer layers, and (c) shows the probe-steering correlation pattern reported in Anthropic's work (see findings.md F7).

2. **Intervention success.** Steering along at least one successfully-extracted vector produces a statistically meaningful improvement on a reasoning-sensitive benchmark, with no significant degradation in general capability, AND demonstrably outperforms a reasonable prompt baseline. This success criterion has three components, all of which must be met:

   (i) **Target-benchmark improvement.** The steered model outperforms the unsteered baseline on a reasoning benchmark aligned with the virtue being targeted.

   (ii) **No significant degradation** (per F65). Operationalized as explicit four-way checks at the chosen steering coefficient: (a) **coherence and fluency** on unrelated prompts, (b) **factual consistency** on held-out factual tasks, (c) **sycophancy rates** (a documented entanglement hazard in the activation-steering literature), and (d) **safety behaviors** such as refusal rates on known-jailbreak prompts (critical because "Steering Externalities" has documented that benign steering can increase jailbreak vulnerability). A result that improves virtue-benchmark performance while silently degrading any of these four is not a success — it is a moved trade-off.

   (iii) **Incremental improvement over a prompt baseline** (per F68). The extracted steering vector must demonstrably outperform a reasonable system-prompt baseline that describes the target virtue in plain language ("Please reason with intellectual humility: carefully consider alternative explanations…"). If steering does not beat prompting, the activation-level machinery has not been shown to be necessary, and the honest finding is "prompt is sufficient for this disposition" — which is publishable but is a different result from "steering works." Matching prompt performance without exceeding it is informative but not an intervention success in the sense targeted by this project.

   All three components must be reported alongside improvement metrics in the final writeup. A positive result on (i) alone is not a Phronesis success.

3. **Taxonomic success.** The specificity matrix — which virtues steer independently versus which cluster together — reveals interpretable structure that either validates or informatively refutes the six-stage taxonomy in `concepts.md`.

Any one of these would be a meaningful result. A clean negative result (none of the virtues extract cleanly at small scale) is also informative and publishable as a scale-dependence finding.

## Scope — what is in

**MVP-narrowed scope (Day 17, per `mvp-virtues.md`):** 4 virtues (Calibrated Confidence, Intellectual Humility, Evidence Grounding, Reasoning Transparency). The full 15-virtue plan is preserved in `concepts.md` but is gated on MVP exit criteria (per F98).

- Extraction of activation vectors for the 4 MVP virtues (full 15 deferred to post-MVP).
- Validation via held-out prompts and probe-steering correlation.
- Steering experiments on reasoning-sensitive benchmarks.
- Specificity and cross-concept interference measurements.
- Small-scale manual corpus generation (hundreds of passages, not thousands).

## Scope — what is explicitly NOT in

- Training new models or fine-tuning. This is an inference-time intervention project.
- Extraction of emotional concepts (Anthropic already did this).
- Evaluation on tasks that do not plausibly reward epistemic virtues (e.g. creative writing, translation).
- Automated corpus generation until a manual cycle has been completed successfully.
- Extensive benchmarking against alternative extraction methods (SAEs, probing classifiers, etc.) — these are deferred to future work.
- Building tooling, interfaces, or general-purpose infrastructure beyond what is needed to run the experiment.

## Key constraints and working principles

- **Manual before automated.** Every pipeline step is first done by hand once to expose what can go wrong. Automation only after a successful manual cycle. This applies to corpus generation, extraction, validation, and steering.
- **Fewer but cleaner over more but muddier.** When choosing between granularity and reliability, we choose reliability. The concept count is 15 and will shrink rather than grow if cuts become justified.
- **Iterative refinement until saturation.** Planning phases iterate with adversarial research cycles until new cycles stop surfacing genuine issues. An automated scheduler (`phronesis-adversarial-research`) runs every 3 hours to poke holes in the planning documents and record new findings.
- **Holistic planning over local fixes.** Decisions are evaluated against the overall experimental goal, not against the specific problem in front of us. When a new finding arrives, the question is "does this change the plan?" not "how do I patch around this?"
- **Scientific accuracy over speed.** This is a scientific experiment. Overclaiming is worse than underclaiming. If empirical backing is weaker than we assumed, we cut the claim rather than defend it.
- **Honest about failure.** A clean negative result is valuable. The project is not structured to force a positive outcome.

## Document map

- `project.md` *(this file)* — goals, approach, scope, status.
- `concepts.md` — the 15-concept taxonomy with sub-facets and design rationale.
- `findings.md` — running log of research findings (F-numbered entries), including deferred considerations and resolved decisions.
- *(Future)* `generation-guidelines.md` — how to write fact packs and neutral/virtuous/non-virtuous rewrites.
- *(Future)* `review-rubric.md` — criteria for accepting or rejecting generated passages.
- *(Future)* `examples/` — worked-example triplets showing the target output quality.

## Status as of this revision

**This section is significantly out of date as a planning artifact** — the original "Phase 3 onward: not started" was written April 9. See the **Status update (2026-04-29, Day 22)** section at the bottom of this file for current state.

**Quick summary as of Day 22**:
- Phases 1-5 complete or in-flight
- 4 MVP virtues (CC, IH, EG, RT) — full set of 15 deferred per MVP narrowing decision
- qwen3-4b primary model; gemma-4-E4B-it confirmed null and deprioritized
- 1 confidently working vector (qwen × IH × L17), 1 confidently working geometrically-distinct sister (qwen × CC × L9), 1 borderline (qwen × RT × L15), 1 misaligned-and-risky (qwen × EG × L7), 1 partial-redesign-evaluation in flight (v_EG_v2)
- 106 findings recorded, ~200+ items hand-reviewed across 3 sweeps
- Round 3 sweep design queued (bidirectional cross-application + composition test + non-scientific corpus extraction)

**Original (April 9):**
- Phase 1 (concept taxonomy): 15 concepts, stable, cross-checked against CIHS, VICS, NFC, metacognition literature.
- Phase 2 (reference gathering): 19 findings recorded.
- Phase 3 onward: not started.

## How to update this file

- Update when goals, hypothesis, scope, success criteria, or working principles change.
- Do NOT update for minor concept refinements (that's concepts.md) or new research findings (that's findings.md).
- When updating, keep the document structure intact; the phases and sections should remain stable anchors.
- The scheduled adversarial research task reads this file. Changes here change how future research cycles are framed.

---

## Status update (2026-04-29, Day 22)

The status section above ("Phase 3 onward: not started") is many weeks stale. Current state:

### Phases completed

- **Phase 1 (concept taxonomy):** stable. 15 concepts, 4 selected as MVP set (CC, IH, EG, RT).
- **Phase 2 (corpus generation):** completed for all four MVP virtues. Two corpus iterations:
  - v1 (Day 9-19): produced the original triplets-{evidence-grounding,reasoning-transparency,intellectual-humility,combined} corpora.
  - v2 (Day 21-22): redesigned EG/RT/CC contrast axes after F104/F105 revealed the v1 EG corpus contrasted on calibration-framing not specificity-density. 120 new triplets added; 22 EG NV files genericized in-place; 30 RT NV files hedge-matched. See commit `2c5fde7` and `corpus_inspection_EG_v2.md`.
- **Phase 3 (extraction infrastructure):** complete. Last-token diff-of-means at every layer for both qwen3-4b and gemma-4-E4B-it. Phase 4 (extraction) and Phase 5 (steering) built on this.
- **Phase 4 (extraction):** complete for v1 corpora across both models; complete for v2 corpora on qwen3-4b at all 36 layers (in-flight at time of writing); not run on gemma for v2 corpora (gemma null across 3 days).
- **Phase 5 (steering experiments):** in flight as of 2026-04-29. Multiple sweeps:
  - Day-19 α/layer envelope (Path A, RT focus + Path B, IH focus + Path D, EG focus). 200+ items hand-reviewed in `mvp/results/full_hand_review_*.md`.
  - Day-21 diagnostic batch (4 questions × 16 cells × 5-10 prompts = 136 items). Hand-reviewed in `mvp/results/full_hand_review_diagnostic_batch.md`.
  - Day-22 v2 sweep with redesigned corpora (15 cells across Phase 4 still running; cosine matrix + behavioral diagnostics).
- **Phase 6 (writeup):** not started.

### Net working-vector inventory (current)

| Vector | Status | Confidence | Notes |
|---|---|---|---|
| qwen × IH × L17 α=+8 to +12 | Working | **HIGH** | Anti-FM-8 / commit force; produces both humble abstention and confident commit depending on prompt demands |
| qwen × CC × L9 α=+4 to +12 | Working | **HIGH** | Same anti-FM-8 mechanism as IH but at a geometrically distinct residual-stream direction (cos≈0 with v_IH) |
| qwen × EG × L7 α=4-8 | Active but risky | LOW | Adds named-entity tokens; **confabulates** them on knowledge-gap prompts. v_EG_v2 (redesigned corpus) is being evaluated; geometry shows cos 0.70 with v1 buggy vector (partial rotation) |
| qwen × CC_numeric × L9 | Untested behaviorally | — | 20-triplet sub-corpus (claude-cc-*) carves a partly-distinct geometric direction (cos 0.28-0.41 with CC_full). Behavioral A/B pending |
| qwen × RT × L15 α=8 | Borderline | LOW-MED | Subtle vocabulary shift on 2/5 items only |
| All gemma × * | Null | (confirmed) | 3 days of null across α and layers |

### Big picture revision (Day 21-22)

The original framework hypothesized 4 orthogonal virtue directions ("compose them dynamically based on prompt context"). Geometric data shows:

- **v_IH is the geometric outlier** (cos ≤ 0.14 vs every other v2 virtue at every AP-peak layer; cos = 0.000 vs v_CC_full at L17).
- **v_EG, v_RT, v_CC_full form a cluster** (pairwise cos 0.30-0.45) — distinct vectors but inhabiting a shared residual-stream subspace.
- **v_CC_numeric** carves a partly-distinct sub-direction (cos 0.28-0.41 with v_CC_full).

So the actual pattern is **1 distinct direction + 3 weakly distinguishable in a shared subspace + 1 partial sub-carve-out**, not the symmetric 4-way the framework predicted. That's neither the framework's prediction nor the "1 disposition reachable from many corpora" reading from Day-21 — it's a third, more interesting picture.

The IH/CC behavioral collision (both vectors fix FM-8 spirals on the prompts each was tested on) is **NOT** explained by residual-stream alignment. It's **downstream functional convergence** — two near-orthogonal directions hit overlapping OV/MLP read-offs which both push `</think>` token-probability up. Mechanism details (shared circuit vs different circuits with overlapping output) await bidirectional cross-application behavioral test (queued as Round 3).

### Methodological wins

- Manual-first policy validated three times across days (F94-UPDATE Day 10, F103 Day 19, F104 Day 20). Auto-scorers fail in distinct ways each time; hand review catches the failures.
- Cross-model split (F102 geometric + F103/F104 behavioral) is a real publishable finding regardless of how the four-vector compositional question resolves.
- Two extraction-pipeline bugs caught and patched in the v2 sweep (skip-resume returning stale v1; `--layers sweep` missing odd-numbered AP peaks). Both documented in F106 and the runbook.

### Open questions / Round 3 design

1. Bidirectional cross-application: vCC × L9 on eg-eval-v2 + abstention (mechanism question for IH/CC behavioral collision).
2. Composition behavioral test: vIH × L17 + vCC × L9 simultaneously; hand-rate.
3. Non-scientific corpus extraction (cluster-source question): does the EG/RT/CC cluster persist when the corpus contrast moves out of scientific prose?
4. v_CC_numeric vs v_CC_full A/B on additional benchmarks.

### Document map (current)

- `project.md` (this file) — goals, scope, current status
- `concepts.md` — 15-concept taxonomy (last touched Apr 9, framework is stable)
- `findings.md` — F1-F107; current; ~400 KB
- `journal.md` — Day-by-day narrative; current through Day 22
- `experiments.md` — Phase-by-phase experiment log; current through Day 22
- `scoring.md` — failure-mode catalogue (FM-1 through FM-12), manual-first policy, scorer-upgrade plan
- `mvp-virtues.md` — 4 MVP virtues' operational definitions
- `mvp/results/` — detailed per-experiment result docs and hand-review verdicts
- `mvp/results/where_we_are_simple.md` — plain-English re-orientation doc (Day 21)
- `mvp/results/full_hand_review_*.md` — hand-review verdicts (4 docs)
- `mvp/results/cosine_analysis_v1_vectors.md` + `v2_cosine_observations.md` — geometric analyses

### Doc roles policy (going forward, per Day-22 external review)

To stop the documentation drift / duplication pattern flagged in Day 22:

- **`findings.md`** — append-only, F-numbered conclusions. Each finding self-contained: setup, observation, implication, applies-to, artifacts. New findings get the next F-number.
- **`journal.md`** — append-only, chronological narrative. References findings by F-number rather than restating the conclusion. Captures the *story* of how a finding arose: what was tried, what was unexpected, what was decided. The reading-path for someone trying to reconstruct project history.
- **`experiments.md`** — append-only, configuration log. What ran, with what parameters, where the data lives, what the cell counts were. The reading-path for someone trying to reproduce a specific experiment.
- **`project.md`** (this file) — updated when goals, scope, hypothesis, or success criteria change. Status section refreshed at major milestones (not every day).
- **`scoring.md`** — failure-mode catalogue and scorer-upgrade plan. Append-only for FM-N entries; versioned for the upgrade plan.
- **`mvp/results/*.md`** — detailed analysis docs that don't fit the F-numbered-conclusion format. Hand-review verdicts, multi-cell synthesis, post-hoc methodology notes.

The Day-22 review noted that F106 (findings.md), Day-22 entry (journal.md), and "Day-22 v2 sweep" section (experiments.md) all describe the same events with different framings. Going forward: pick one canonical home per event; reference from the others rather than restate.

