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

## High-level approach (six phases)

**Phase 1 — Concept taxonomy.** Define the epistemic virtues precisely enough to generate contrastive training data for each one. Output: `concepts.md`. *(Currently iterating.)*

**Phase 2 — Reference gathering and methodology research.** Read the relevant prior work (Anthropic emotions paper, representation engineering literature, behavioral science on the target virtues, text style transfer methodology). Output: `findings.md`. *(Currently iterating in parallel with Phase 1 via scheduled adversarial research cycles.)*

**Phase 3 — Guidelines architecture.** Write the scaffolding documents that govern data generation: the generation guidelines, the review rubric, worked examples. Output: `generation-guidelines.md`, `review-rubric.md`, possibly `examples/`. *(Not yet started.)*

**Phase 4 — Pilot run on one concept.** Generate a complete corpus for a single high-likelihood concept by hand (no automation), extract its vector, validate it, and run steering experiments. This is the go/no-go signal for the whole project. If the pilot concept does not extract cleanly, the methodology is not viable at the chosen scale and we either move to a larger model or reconsider the project. *(Not yet started.)*

**Phase 5 — Full corpus generation and extraction.** Assuming the pilot succeeds, generate corpora for the remaining concepts and extract their vectors. *(Not yet started.)*

**Phase 6 — Evaluation and write-up.** Measure steering effects against baseline on appropriate benchmarks, compute specificity and transfer metrics, document what worked and what did not. *(Not yet started.)*

## Target model

Gemma 4 E4B running on Apple Silicon (M4 Mac Mini, 16GB) for development and iteration, with the option of moving to GCP (A100) for larger runs if needed. Model choice is provisional — if pilot extraction fails at Gemma 4 E4B scale, a larger model becomes a live option.

## Success criteria

The project has three levels of success, each of which would be a meaningful outcome to publish or discuss:

1. **Representation success.** For at least one virtue, we extract a clean vector that (a) predicts the virtue on held-out passages, (b) is stable across nearby transformer layers, and (c) shows the probe-steering correlation pattern reported in Anthropic's work (see findings.md F7).

2. **Intervention success.** Steering along at least one successfully-extracted vector produces a statistically meaningful improvement on a reasoning-sensitive benchmark, with no significant degradation in general capability.

3. **Taxonomic success.** The specificity matrix — which virtues steer independently versus which cluster together — reveals interpretable structure that either validates or informatively refutes the six-stage taxonomy in `concepts.md`.

Any one of these would be a meaningful result. A clean negative result (none of the virtues extract cleanly at small scale) is also informative and publishable as a scale-dependence finding.

## Scope — what is in

- Extraction of activation vectors for ~15 carefully defined epistemic virtues.
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

- **Phase 1 (concept taxonomy):** 15 concepts, stable, cross-checked against validated behavioral science instruments (CIHS, VICS, NFC, metacognition literature). Iterating via scheduled adversarial research.
- **Phase 2 (reference gathering):** 19 findings recorded. Iterating via scheduled adversarial research.
- **Phase 3 onward:** not started.

## How to update this file

- Update when goals, hypothesis, scope, success criteria, or working principles change.
- Do NOT update for minor concept refinements (that's concepts.md) or new research findings (that's findings.md).
- When updating, keep the document structure intact; the phases and sections should remain stable anchors.
- The scheduled adversarial research task reads this file. Changes here change how future research cycles are framed.
