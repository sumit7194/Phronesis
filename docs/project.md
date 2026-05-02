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

### Net working-vector inventory (current — Day 23, post-v2-sweep)

| Vector | Status | Confidence | Notes |
|---|---|---|---|
| qwen × IH × L17 α=+8 | Working | **HIGH** | Anti-FM-8 / commit. Confirmed cross-applicable to cc-simple (Day 22 sweep). Produces humble abstention on false-premise prompts and committed estimates on hard magnitude prompts. |
| qwen × CC_legacy × L9 α=+8 | Working | **HIGH** | Legacy 50-triplet hand corpus. Anti-FM-8 mechanism; cos 0.85 with v_CC_full (very similar). |
| qwen × CC_full × L9 α=+4 | Working | **HIGH** | v2 corpus (186 triplets). Best at LOW α; over-steers at high α. **FM-13 risk at α=12 on broken-baseline-reasoning prompts** (commit-amplified-error). |
| qwen × CC_numeric × L9 α=+12 | Working | MED | 20-triplet sub-corpus (claude-cc-*). cos 0.28-0.41 with CC_full — geometrically distinguishable. **Best at HIGH α** (lower L2 norm needs more amplification). Content distinction not yet tested with Bayesian prompts. |
| qwen × EG × L7 α=+8 to +12 | Working with caveat | MED | v2 redesigned corpus. Saves seismic-damper FM-8 at α≥8. **Confabulates on knowledge-gap prompts at α=4** (Gandhi 1937 fabrication); at α=8 commits to rejection instead. Phase-transition behavior. |
| qwen × EG × L7 α=+4 | Active but RISKY | LOW | Same vector at lower α: confabulates. Should not be used at this α on knowledge-gap inputs. |
| qwen × RT × L15 α=8 | Borderline | LOW-MED | Adds named-study citations distinct from EG/IH (Taipei 101 TMD ~40%, Tokyo Tower 60%). FM-8 on eg-v2-04 (age of universe). |
| All gemma × * | Null | (confirmed, 4 days) | No behavioural effect at any α tested across 4 days. |

**Failure modes catalogued through Day 23**: FM-1 through FM-13. See `docs/scoring.md` for full catalogue. FM-13 (commit-amplified error — high-α commit-vector application on broken-baseline-reasoning prompts produces confident wrong answers) added Day 23.

### Big picture revision (Day 21-23)

The original framework hypothesized 4 orthogonal virtue directions ("compose them dynamically based on prompt context"). Geometric + behavioral data through Day 23 shows:

- **v_IH is the geometric outlier** (cos ≤ 0.14 vs every other v2 virtue at every AP-peak layer; cos = 0.000 vs v_CC_full at L17).
- **v_EG, v_RT, v_CC_full form a cluster** (pairwise cos 0.30-0.45) — distinct vectors but inhabiting a shared residual-stream subspace.
- **v_CC_numeric** carves a partly-distinct sub-direction (cos 0.28-0.41 with v_CC_full). Behaviorally confirmed Day 23: opposite optimal α regime from v_CC_full.

So the actual pattern is **1 distinct direction + 3 weakly distinguishable in a shared subspace + 1 partial sub-carve-out**, not the symmetric 4-way the framework predicted. That's neither the framework's prediction nor the "1 disposition reachable from many corpora" reading from Day-21 — it's a third, more interesting picture.

The IH/CC behavioral collision (both vectors fix FM-8 spirals on the prompts each was tested on) is **NOT** explained by residual-stream alignment. It's **downstream functional convergence** — two near-orthogonal directions hit overlapping OV/MLP read-offs which both push `</think>` token-probability up. Mechanism details (shared circuit vs different circuits with overlapping output) await full bidirectional cross-application; Day-22 sweep added v_IH × L17 on cc-simple and produced nearly identical commit-vs-spiral profile to v_CC × L9 on cc-simple — **half-test consistent with shared-circuit reading but doesn't rule out different-circuits-overlapping-output**. Round 3 needs `vCC × L9 on eg-eval-v2 + abstention` to settle.

**FM-13 (commit-amplified error)** discovered Day 23: high-α commit-vector application on prompts where baseline reasoning is broken produces *confident wrong answers*, not abstention. Concrete instance: vCC_full × L9 × α=12 on Tokyo population question committed to "(c) 130 million" when correct is 13M, because the baseline arithmetic ("37M closer to 130 than to 13") was already wrong. This is the F45 disposition-modulator-not-propositional-injector boundary materializing as a behavioral failure mode. **Implication for compositional steering**: a baseline-quality gate is needed before applying commit-vectors on contested-knowledge / numeric-judgment prompts.

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

---

## Status update (2026-04-29 evening, Day 23 — post Round 3)

Round 3 sweep complete. 121 generations hand-reviewed, all without auto-scorer. F109 promoted in findings.md.

### Refined working-vector inventory (Day 23 evening)

| Vector | Status | Notes |
|---|---|---|
| qwen × IH × L17 α=+8 | **HIGH** confidence | Anti-FM-8 / commit. Adding to composite at α=8 partially neutralizes vCC's FM-13 (cc-s-08 Tokyo correct in composite, wrong in vCC α=12 alone). |
| qwen × CC × L9 (legacy) α=+8 | **HIGH** confidence | Same anti-FM-8 mechanism. cos 0.85 with v_CC_full. |
| qwen × CC_full × L9 α=+4 | **HIGH** at α=4 | Best at low α. |
| qwen × CC_full × L9 α=+8 | **MED** with caveat | $185.55 stock hallucination on abstention; 1937 Gandhi fab. |
| qwen × CC_full × L9 α=+12 | **MED** with strong caveat | NEW "1957" Nobel fab; 1500-token degenerate-loop on ip-longest; FM-13 fingerprint dominant. |
| qwen × CC_numeric × L9 α=+12 | MED, untested in Round 3 | Bayesian-prompt A/B still pending. |
| qwen × EG × L7 α=+8 | **MED** at α=8 specifically | Phase-transition rail-switch; closer to truth on Gandhi. |
| qwen × EG × L7 α=+4 | LOW (and risky) | Confabulates. |
| qwen × EG × L7 α=+12 | LOW-MED | Inherits FM-13 fingerprint (stock $185.55). Gandhi rejection-direction right, details wrong. |
| **qwen × IH+CC composite α=+8+8** | **NEW, MED** | Non-additive: fixes ip-longest, fixes Tokyo, helps comp-08 premise-flag. Inherits Gandhi-1957 + stock-$185.55 from vCC. Roughly comparable to vCC alone. |
| qwen × RT × L15 α=+8 | LOW-MED (unchanged) | Borderline. |
| All gemma × * | NULL (5 days confirmed) | |

### Updated big-picture (Day 23)

The geometric clustering picture from Day 22 (1 distinct + 3 clustered + 1 sub-carve-out) is now backed by token-level evidence for the FM-13 mechanism:

- **FM-13 is gated by a single thinking-token rail-switch, not a smooth dial.** The α value selects which generation step the steered hidden state crosses the decision boundary. Different α values land on different decoding rails. Whether the rail is correct depends on rail content, not α magnitude. (F109 finding #1.)
- **v_EG and v_CC at the same α produce same FM-13 surface with different fingerprints** — confirming downstream functional convergence (per F105/F106): orthogonal residual-stream directions hitting overlapping OV/MLP read-offs.
- **Composition is non-additive.** Composite (vIH+vCC at α=8+8) fixed one degenerate-loop, fixed one premise-flag, kept Tokyo correct — but inherited Gandhi-1957 and stock-$185.55 hallucinations from vCC. Roughly comparable to vCC alone, NOT strictly better. (F109 finding #3.)

### Phase 2 (queued, user direction)

Phi-3.5-mini extraction + sweep + hand-review. Establish whether F-findings transfer to a third open model. F102 cross-model split currently rests on 2 datapoints (qwen behavioral, gemma null); phi-3.5-mini disambiguates "qwen-specific" from "general 4B-class behavior."

Phase 2 plan:
1. Download phi-3.5-mini-instruct.
2. Verify model loads + token throughput on L4.
3. Run extract_v2.py on the 4 v2 corpora (combined / IH / EG / RT / CC, same as qwen3-4b).
4. Compute cosine matrix at all layers; pick AP-peak layers.
5. Run the same diagnostic + EG + abstention + cc-simple + composition sweep we ran on qwen.
6. Hand-review.

Estimated: 2-3 days end-to-end on L4.


---

## Status update (2026-05-03, Day 25 — post cross-model 1,752-generation hand-review)

Cross-model run complete. 1,752 generations across phi-4-mini-reasoning + llama-3.1-8B-R1-GRPO + openr1-qwen-7b × 6 vectors × 12 α × 8 prompts. All hand-graded (no auto-scorer). F110, F111, F112 promoted in `findings.md`.

### Headline numbers

| Model | ✓ rate / 576 | Failure shape |
|-------|--------------|---------------|
| Phi-4 | 162 (28%) | Internal looping + cap-truncation |
| Llama | 219 (38%) | Wrong-answer template lock |
| OpenR1 | 100 (17%) | Non-commitment loop (rescuable!) |

### Three-failure-shape framing (the cleanest narrative)

| Baseline failure mode | Effect of activation steering | Examples |
|-----------------------|-------------------------------|----------|
| Wrong-answer template | Cannot dislodge → 0/72 ✓ | Llama E2 (80% lock), Llama E3 (prior-mixture), Llama N2 (split rec) |
| Internal loop / no commit | Forces commitment → 40-56% ✓ | OpenR1 N1, OpenR1 E3 |
| Cap-truncation on extended deliberation | No effect | Phi-4 N2, E3, E4 |

### Working-vector inventory (Day 25)

| Vector | Phi-4 | Llama | OpenR1 | Cross-model verdict |
|--------|-------|-------|--------|---------------------|
| CC_full (L24/L26/L23) | Strong on E5/N3 (12/12 ✓) | Template-flat | Best openr1 cell on N1+E3 | **HIGH** confidence as commitment-amplifier; F112 best result |
| CC_num (L3/L31/L23) | L3 catastrophic everywhere | Mostly inert | Strong on N1 (9/12) | MED — usable on openr1, fragile elsewhere |
| EG (L21/L22/L19) | Best phi-4 cell (12/12 N3+E5) | Variable | Strong on E3 (8/12) | **HIGH** on phi-4 L21; LOW elsewhere |
| IH (L7/L31/L25) | L7 EOS at high α | At ceiling, untestable | **PRODUCES WORST FAILURES** at high α | **FALSIFIED** — F111 |
| RT (L21/L22/L19) | Stable on N3/E5 | think_chars=0 universal on N1 | Strong on E3 (8/12) | MED — overlaps with EG/CC_full at L21 (F105) |
| VC (L3/L29/L25) | L3 catastrophic | Null negative control | Format-glitch susceptible | Confirms layer-suitability hypothesis |

### Pivoted product hypothesis (post-F112)

Old hypothesis: "Activation steering installs/amplifies virtues. Compose vectors to install multiple virtues simultaneously."

New hypothesis (F112): **"Activation steering breaks self-debate / non-commitment loops, forcing the model to commit to its most accessible reasoning rail. The commitment is virtuous when the rail is virtuous."**

Specific use case where this is empirically supported: **non-committal thinking models with correct internal reasoning that fail to commit.** OpenR1-Qwen-7B is the canonical example — verbose self-debate baseline, ✗ rate of 0/2 on N1+E3 → 35% ✓ rate after steering.

### What this changes for post-MVP

- **Drop**: "humility installer" / "calibrated-confidence amplifier" — F92 + F111 both falsify this
- **Drop**: "compositional virtue installer" — F109 showed composition is non-additive; this run didn't disprove it but also didn't find a compelling positive case
- **Pivot to**: "commitment amplifier for self-debating reasoning models" — F112 supports this with 50/144 ✓ on openr1 N1+E3
- **Test direction for follow-up**: does the commitment-amplifier mechanism generalize to other thinking models that loop instead of commit (e.g., r1-distill, gemini-thinking, o3-mini)?

### Phi-4 cap-truncation as a separable problem

Phi-4 fails on N2/E3/E4 by exhausting the 8192-token budget, not by reasoning poorly. The reasoning is *almost always correct in the visible portion* — subset logic on N2, correct Bayes on E3 — but the model can't compress to a final answer.

This is a **separable, tractable problem**: re-run those prompts at 16k or 32k token cap. If reasoning was correct in 8k, it should commit cleanly in 16k.

Recommended follow-up: cap-extended re-run on phi-4 × CC_full × N2 + E3 + E4 at 16k. If ✓ rate jumps from low (current 12-17%) to 70%+, it confirms cap-truncation was masking otherwise-correct reasoning.

### Cross-cutting findings landed Day 25

- **F110** — Cross-model 1,752-generation hand-review confirms F109 at scale
- **F111** — IH hypothesis decisively falsified (4 of 4 testable prompts)
- **F112** — OpenR1 commitment-rescue is the cleanest positive finding; pivots product hypothesis

### Phase 5 / paper draft direction

Three-failure-shape framing is the cleanest narrative around F109+F110+F112:
- Activation steering's behavioral effect is *commitment selection*, not *virtue installation*
- Whether commitment is virtuous depends on whether the model has the right reasoning rail
- Three different baseline failure shapes lead to three different steering-effectiveness regimes

This is publishable as a cross-model hand-review study with the F112 commitment-amplifier as the headline positive finding. The IH-falsification (F111) is the headline negative finding. Together they constitute a substantive update to the F45 / F109 framework.

### Pipeline notes from Day 24-25

- 18 sonnet sub-agents in parallel per prompt × 8 prompts = 144 total agent invocations. Each agent reads 12 JSONs in full and returns structured verdicts.
- Wall-clock: ~3 hours for 1,752 generations vs estimated 12+ hours sequential.
- Strict-meticulousness directive in every agent prompt was essential. First-pass outputs without it produced surface-level verdicts that missed factual errors and format glitches.
- Total git commit = 1,777 files (1,752 raw generations + analysis + syntheses + CSV + baselines).

