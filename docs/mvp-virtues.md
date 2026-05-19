# Phronesis — MVP Virtue Set

This document is the **active operational scope** for Phronesis. It names the virtues we are extracting and validating during the MVP phase, gives per-virtue working guidelines for corpus construction, and specifies the full-study virtue set we expand to after the MVP succeeds.

This document extends — does NOT replace — `concepts.md` (the canonical 15-virtue taxonomy), `generation-guidelines.md` (the corpus construction pipeline), and `review-rubric.md` (per-concept rubric tables). Where those docs speak in general terms across all 15 concepts, this doc commits to a specific 4 (MVP) and 8 (full study).

**Status:** v2 (Day 16, 2026-04-23). MVP scope agreed with user on Day 15. Per-virtue guidelines for Evidence Grounding and Reasoning Transparency are drafted here. Corpus-generation strategy evolved during Day 15-16 from hand-written only to LLM-assisted (ChatGPT + Sonnet) + hand-written substrate-reuse mix — see "Corpus build retrospective" section below.

---

## Guiding principles (from Day 15)

1. **Learning over publishing.** This is not a race against Anthropic. Inspiration, not competition.
2. **Pushback is a feature.** The research assistant (Claude) is instructed to push back when premises seem wrong, even at the cost of admitting earlier advice was wrong.
3. **Solidify before scaling.** A small number of well-extracted, well-validated vectors beats a large number of noisy ones. MVP first, then scale.
4. **Manual first, automation after.** Scorer upgrade and LLM-driven corpus generation are Phase 5+ infrastructure. Trigger condition: "after 4-virtue MVP lands."

## Why 4 for MVP, not 15 or 171

Anthropic's Emotion Concepts paper (April 2026) extracted 171 emotion vectors. Our work is deliberately different:

- **Different construct class.** Emotions are affective concepts; our 15 are epistemic virtues (atomic cognitive dispositions). Zero overlap with Anthropic's 171 emotions, Persona Vectors (~7), Assistant Axis (275 archetypes), or community replications (rain1955, RyanCodrai on Gemma-4-E4B).
- **Different model scale.** Anthropic extracted from Sonnet 4.5 (large closed). We target Qwen3-4B and Gemma 4 E4B-it (small open).
- **Different success criterion.** Anthropic demonstrated existence at scale. Our Phase 4 / Phase 6 success criteria (per `project.md`) require a *specificity matrix* — evidence that the extracted vectors are atomically distinct from each other, not a single AOT super-direction. A specificity matrix only becomes meaningful at 4+ virtues.

Four virtues × four virtues gives us a 4×4 specificity matrix — the smallest square that can show off-diagonal suppression (vector A doesn't drive virtue B's behavior) and on-diagonal drive (vector A does drive virtue A's behavior). That is the minimum publishable taxonomic-success artifact.

---

## MVP virtue set (4)

| # | Virtue | Stage | Status | F11 risk | Primary validation benchmark |
|---|---|---|---|---|---|
| 9 | Calibrated Confidence | 4. Holding conclusions | ✅ Extracted both models; AIME sign-flip result validated on Qwen | Low | AIME-42 (Qwen), hedging-word frequency, abstention quality |
| 6 | Intellectual Humility | 3. Checking yourself | 🟡 Extracted both models; geometric MVE passed; behavioral MVE noisy (scorer artifacts) | Low-Med | Abstention benchmark (24 items) |
| 15 | Evidence Grounding | 6. Communication | 🔴 New — not yet extracted | Low | Evidence-labeling frequency, BSR (inverse) |
| 14 | Reasoning Transparency | 6. Communication | 🔴 New — not yet extracted | Low | Step-visibility count, assumption-surfacing rate |

**F11 risk** = risk that the model lacks the underlying competency ActAdd would need to amplify. Per `findings.md` F11, ActAdd cannot create competencies the model does not already have — it can only amplify existing behaviors. The four MVP virtues were selected for low F11 risk because small open models demonstrably (a) hedge language, (b) cite sources, (c) label evidence types, (d) surface reasoning steps in their default output distribution.

### Why these four specifically

**Calibrated Confidence (CC)** is included because it is our reference vector. It's the only virtue where we already have a multi-benchmark behavioral validation chain (abstention + AIME sign-flip per F92/F93-REVISED). CC stays in the MVP because (1) the specificity matrix needs a diagonal entry we trust, (2) cross-model CC extraction already worked, (3) dropping it would waste completed work.

**Intellectual Humility (IH)** is included despite noisy behavioral MVE because (1) geometric MVE passed decisively on both models (F97: |cos(v_CC, v_IH)| = 0.030 on Gemma), (2) the behavioral noise is primarily a *scorer* problem not an *extraction* problem (see `results/manual_scoring_qwen_abstention.md` — 8% human-vs-auto mismatch, systematically in the "confabulation dressed as abstention" direction), (3) IH is the hardest of the four and serves as our stress-test case. Keep it to force ourselves to build scorer discipline.

**Evidence Grounding (EG)** is a fresh start — new corpus, new extraction, new validation. Low F11 risk (models can and do cite sources). Inverse-correlates with Pennycook et al.'s Bullshit Receptivity Scale (BSR; see `findings.md` F56), which gives us a ready-made validation benchmark distinct from CC/IH benchmarks.

**Reasoning Transparency (RT)** is the fourth fresh extraction. Low F11 risk (models can and do show steps). Targets *legibility* not *faithfulness* (see `concepts.md` §14) — we extract what text shows, not internal computation. Validation via step-visibility count and assumption-surfacing rate, both text-level metrics that cannot be confounded by the CC or IH benchmarks.

### What the MVP succeeds at, precisely

Per `project.md` Phase 4 / Phase 6 success criteria, the MVP succeeds if:

1. **Representation success** (each vector exists, on both models, passes geometric MVE against the others) — partially achieved (CC, IH); EG and RT pending.
2. **Intervention success** (steering along each vector moves the corresponding behavior in the predicted direction, without creating degenerate text, and beats the corresponding prompt baseline) — CC achieved for AIME; others pending.
3. **Taxonomic success** (4×4 specificity matrix: each vector drives its own virtue's behavior and does *not* drive the other three virtues' behaviors at similar magnitude) — entirely pending, requires all four vectors extracted.

Any one of the three is publishable per `project.md`. MVP targets all three; shipping criterion is hitting **taxonomic success on the 4×4 matrix with at least two of the three verticals also cleared.**

### What the MVP does NOT attempt

- **No scale to 15.** The other 11 virtues are explicitly Phase 5 work, gated on MVP outcome.
- **No scorer automation.** Every response is hand-reviewed. See `scoring.md`.
- **No publication work.** Per guiding principle 1.

### Corpus build retrospective (what changed Day 15-16)

Original Day-15 plan called for hand-written triplets only. **Day 16 revision:** we pivoted to a three-source mix because hand-writing 40 triplets per virtue was the biggest time sink and LLMs could produce calibration-quality output with careful prompting:

- **20 ChatGPT triplets per virtue** — via detailed prompt with all hard constraints, audited + regenerated where caricature emerged
- **15 Sonnet triplets per virtue** — similar prompt with LLM-specific refinements (length matching, canonical sub-facet labels, committal virtuous-wrong)
- **5 substrate-reuse triplets per virtue** — hand-written by the research assistant against top-ranked substrates from the existing 166-CC corpus

Final curated corpus at `corpus/mvp-combined/` — 40 EG + 40 RT with full audit trail in `LEDGER.md`. **Full LLM-driven corpus generation for scale-up (8-virtue study)** is still Phase 5 work, gated on MVP outcome. The prompts used for this first-wave LLM generation are preserved in session transcripts and can be refined if reused.

---

## Full-study virtue set (8)

After MVP ships, we expand to 8 virtues total. The additional 4:

| # | Virtue | Stage | Rationale for inclusion |
|---|---|---|---|
| 3 | Logical Rigor | 2. Processing evidence | Low-med F11 risk; strong text signature (stepwise decomposition); validates Stage-2 coverage |
| 2 | Hypothesis Generation | 1. Initiating | Moderate F11 risk; distinct text signature (multiple structurally distinct explanations); validates Stage-1 coverage |
| 12 | Steelmanning | 5. Engaging others | Moderate F11 risk; text signature is multi-sentence structural (reconstruction → engagement); validates Stage-5 coverage |
| 10 | Intellectual Honesty | 4. Holding conclusions | Moderate F11 risk; collinearity risk with CC (per `concepts.md`); adding it tests whether our CC and IH vectors stay orthogonal to a third same-stage virtue |

The 8-virtue set spans all 6 stages except Stage 2's Causal Reasoning and Quantitative Groundedness (requires specialized corpus design — deferred) and Stage 3's Confirmation Bias Awareness and Metacognitive Awareness (high AOT-cluster collinearity risk per `findings.md` F39).

**The 7 deferred virtues** (for later phases, if justified by Phase 6 results): Genuine Curiosity, Causal Reasoning, Quantitative Groundedness, Confirmation Bias Awareness, Metacognitive Awareness, Comfort with Ambiguity, Authority Independence.

---

## Per-virtue operational guidelines

Each virtue below gets a working guideline in the structure:
- **Definition** — one sentence, from `concepts.md`
- **Sub-facets** — from `concepts.md`, restated for corpus-writing emphasis
- **Virtuous pattern** — what the virtuous passage looks like on the page
- **Excess-failure pattern** — what the over-applied failure looks like
- **Deficiency-failure pattern** — what the under-applied failure looks like
- **Text indicators** — words, phrases, or syntactic shapes the corpus writer should look for
- **F11 risk assessment** — which sub-facets may fail to amplify because the model lacks the underlying competency
- **Reuse estimate** — expected % of existing 166 triplets-combined / 20 IH triplets usable for this virtue
- **Validation signal** — how we will measure whether steering worked

### 9. Calibrated Confidence (reference)

**Status:** Already extracted on Qwen (50-hand corpus) and Gemma (triplets-combined, 166). Reference guideline is in `concepts.md` §9, `review-rubric.md` §9, and the existing CC corpus. Not restated here.

**For the specificity matrix:** v_CC must be tested against EG-eval, RT-eval, and IH-eval benchmarks. The prediction is that v_CC drives CC-behavior (hedging language quality) but does NOT drive evidence-labeling, step-visibility, or ego-independence at comparable effect size.

### 6. Intellectual Humility (in flight)

**Status:** Already extracted on Qwen (20-triplet IH corpus) and Gemma. Reference guideline is in `concepts.md` §6, `review-rubric.md` §6, `corpus/triplets-intellectual-humility/`. Not restated here.

**Open issue:** Behavioral MVE (Test A) is contaminated by scorer artifacts (`results/manual_scoring_qwen_abstention.md`). Per `scoring.md`, the path forward is manual hand-scoring of every IH abstention run until we have a reliable signal. The Gemma α=8 run currently on GCP is part of this resolution.

**For the specificity matrix:** v_IH must be tested against CC-eval, EG-eval, RT-eval. Prediction: v_IH drives IH-behavior (ego-independence phrasing, updating language, epistemic-hedging around own methodology) but does NOT drive AIME confidence calibration or evidence-type labeling.

### 15. Evidence Grounding (new — first to build)

**Definition.** Claims are tied to specific observations or data, and the type of evidence is made clear.

**Sub-facets** (from `concepts.md` §15):

- EG-a: Tying claims to specific observations or data
- EG-b: Distinguishing empirical claims from theoretical speculation
- EG-c: Specifying type of evidence (anecdotal, observational, experimental, meta-analytic)

**Virtuous pattern.** The reasoner links each non-trivial claim to a specific piece of evidence. They label the evidence's nature (e.g., "a single case study" vs. "a randomized trial with 500 participants" vs. "theoretical prediction from principle X"). When evidence is absent or weak for a claim, they say so rather than silently treating the claim as supported. Claims and evidence appear in the same or adjacent sentences, so the reader can check the linkage without inference.

**Excess-failure pattern (over-application).** The reasoner refuses to state any claim without an exhaustive evidentiary chain, even for well-established background facts. Simple assertions become buried under unnecessary methodological qualifications ("according to a 2019 meta-analysis of 47 randomized trials using the Cochrane risk-of-bias tool, water is wet"). The passage reads as bureaucratic citation-stuffing rather than reasoning. At the limit, the excess failure makes the passage unreadable — every sentence is 80% source-hedging.

**Deficiency-failure pattern (under-application).** The reasoner makes claims without specifying what they are based on. Evidence, if mentioned at all, is vague ("studies show," "it is known," "research has demonstrated"). Empirical and theoretical claims are not distinguished — predictions from theory are stated in the same register as observed findings. Anecdotes are treated as evidence without labeling them as such. At the limit, the deficiency failure is indistinguishable from bullshit in the Pennycook sense — semantically confident-sounding claims with no attachment to any verifiable ground.

**Text indicators.**

- *Virtuous:* "the study of 47 patients," "three lines of observational data converge on," "this is a theoretical prediction, not an observation," "I don't have direct evidence for this but it follows from X," "the evidence here is anecdotal — a single case"
- *Excess:* "according to [long citation] with [methodological qualifier] and [second qualifier]," pile-up of "as shown by" clauses, passage where 40%+ of tokens are citation scaffolding
- *Deficiency:* "studies show," "it is well known that," "research demonstrates," unlabeled mix of empirical and theoretical claims, anecdotes in the same register as RCT findings

**F11 risk assessment.** Low. Small models demonstrably can (a) cite specific numbers from their context, (b) distinguish "prediction" from "observation" in scientific-register text, (c) use evidence-type labels when primed. Risk is moderate for sub-facet EG-c (evidence-type labeling) on highly specialized domains where the model may not know the canonical evidence hierarchy — but general-domain scenarios should be safe.

**Reuse estimate from existing corpus.** *(Updated Day 15 based on 20-triplet sampling — see `mvp/results/corpus-reuse-sampling-eg-rt.md`.)*

- `corpus/triplets-combined/` (166 CC): **~85% substrate-reusable, ~0-5% drop-in reusable.** The CC corpus is effectively a scenario library; most empirical-reasoning substrates admit an EG contrast. But the existing virtuous/non-virtuous encode CC as their dominant axis, so the rewrites must be redone. Net per-triplet effort savings ~25-40% when reusing substrate.
- `corpus/triplets-intellectual-humility/` (20 IH): **~40% substrate-reusable.** The `unknown` sub-category (IMD records, institutional bulletins) admits an EG-medium contrast. The `false-premise`, `ill-posed`, and `underspecified` categories have no empirical-evidence chain to ground in.

**Recommended action:** Curate the top ~30-50 substrates from the full 186-triplet pool — do NOT use all 158 EG-reusable candidates. Selection criteria: strong natural textual signature for EG, domain spread across all 8 domains, amenable to 50/50 excess/deficiency failure rotation. Target corpus size for EG: ~40 triplets, mixed ~50/50 from substrate-reuse and fresh LLM-generated (see `mvp-virtues.md` corpus-reuse workflow §). Validated against `generation-guidelines.md` pipeline.

**Validation signal.**

- Primary: evidence-labeling frequency on a held-out prompt set (e.g., "Summarize what we know about X"). Steered generations should produce more claim-evidence links per 100 tokens than baseline.
- Secondary: BSR inverse correlation — steered generations should be less susceptible to pseudo-profound bullshit judgments (cf. `findings.md` F56 on BSR as validation instrument for EG).
- Specificity: v_EG should NOT increase hedging-word frequency (CC-territory), abstention rate (IH-territory), or step-visibility count (RT-territory).

### 14. Reasoning Transparency (new — second to build)

**Definition.** The reasoner shows their work: steps, assumptions, and weak points in the chain are surfaced rather than hidden behind a polished conclusion. Scope: *legibility* (output-visible reasoning), not *faithfulness* (whether the visible chain matches the model's internal computation).

**Sub-facets** (from `concepts.md` §14):

- RT-a: Showing the steps, not just the conclusion
- RT-b: Making assumptions explicit
- RT-c: Flagging where the reasoning chain is weakest

**Virtuous pattern.** The passage has visible reasoning structure. Intermediate conclusions are stated before the final conclusion. Assumptions that would normally be tacit ("assuming the sample is representative," "given that measurement X is accurate to ±5%") are named. When the reasoning has a weak link, the reasoner names the link ("the weakest step here is Y — I'm inferring from a correlation to a mechanism without direct evidence"). A reader can, in principle, disagree with any specific step because every step is visible and labeled.

**Excess-failure pattern.** The reasoner over-structures every passage into formal stepwise reasoning, even when the task doesn't need it. Short claims get burdened with multi-step derivations. The passage becomes a list of "Step 1 ... Step 2 ..." even when direct assertion would be appropriate. At the limit, the excess failure produces passages where the scaffolding dominates the substance — the reader sees the structure but the reasoning content is thin.

**Deficiency-failure pattern.** The reasoner jumps from question to conclusion with no visible intermediate steps. Assumptions remain tacit. Weak steps in the chain are hidden — the passage presents its conclusion as if it were the only possible destination. At the limit, the deficiency failure is confidently-asserted polished conclusions with no legible reasoning path, so the reader cannot identify where to disagree.

**Text indicators.**

- *Virtuous:* "First, ..., then ..., so ...," "Assuming X, it follows that ...," "The weakest link in this argument is ...," "I'm skipping over the step where ... because [reason]," explicit intermediate conclusions, visible structure without formulaic scaffolding
- *Excess:* "Step 1: ... Step 2: ... Step 3: ..." for a one-line claim, over-enumerated sub-cases, passage where structural markers outnumber substantive sentences
- *Deficiency:* conclusion-first prose with no derivation, tacit assumptions, unhedged leaps, answer presented as self-evident

**F11 risk assessment.** Low. Small models demonstrably produce chain-of-thought when prompted — the competency exists in the pretraining distribution. Risk is moderate for RT-c (weakest-link flagging) because this requires meta-awareness of the reasoning's own weak points, which overlaps with Metacognitive Awareness (Concept 8). Keep RT-c sub-facet but watch for collinearity with any future Metacognitive Awareness vector.

**Reuse estimate from existing corpus.** *(Updated Day 15 based on 20-triplet sampling — see `mvp/results/corpus-reuse-sampling-eg-rt.md`.)*

- `corpus/triplets-combined/` (166 CC): **~90% substrate-reusable, ~0-5% drop-in reusable.** Any multi-step empirical reasoning scenario admits an RT contrast (step visibility, assumption surfacing, weak-link flagging). The CC corpus's multi-step scenarios map cleanly onto RT substrates. Rewrites required.
- `corpus/triplets-intellectual-humility/` (20 IH): **~60% substrate-reusable.** Math/logic/physics scenarios (`ill-posed`, `underspecified`) actually work well for RT — derivation steps + assumption surfacing + formula-requirement flagging. The `unknown` category is weaker (single-fact queries, not multi-step). Net per-triplet effort savings ~25-40%.

**Recommended action:** Same curation pattern as EG. Target ~40 RT triplets mixed ~50/50 from substrate-reuse and fresh LLM-generated.

**Validation signal.**

- Primary: step-visibility count per 100 tokens on a held-out reasoning-task prompt set. Steered generations should show more intermediate conclusions and explicit "therefore" / "because" structure.
- Secondary: assumption-surfacing rate — count of explicit "assuming X" / "given Y" clauses per passage.
- Specificity: v_RT should NOT increase evidence-labeling frequency (EG-territory), hedging-word density (CC-territory), or abstention rate (IH-territory).

---

## Corpus-reuse workflow (guidelines-first, sample second)

For EG and RT, the workflow is:

1. **Guidelines first (this document).** Each new virtue gets its operational guideline above before any triplet is written or classified.
2. **Sample against guideline.** Pick 20 triplets from the existing 186 total (166 triplets-combined + 20 IH). For each, hand-classify as:
   - *Reusable as-is* for the new virtue
   - *Reusable with rewrite* (substrate OK, virtuous/non-virtuous rewrites need to change the contrast axis)
   - *Not reusable* (scenario fundamentally doesn't admit the new virtue's contrast)
3. **Estimate reuse rate.** Extrapolate from the sample to the full 186.
4. **Decide budget.** For MVP, aim for ~40 triplets per new virtue. Cover the reuse-with-rewrite portion first (cheaper), then hand-write new triplets to reach 40.
5. **Apply `generation-guidelines.md` machinery.** Domain quotas (§3), golden-mean rotation (§4.3), correctness-confound rotation (§4.4), sanitization (§2.4) all apply to new triplets.
6. **Hand-review every triplet** (§2.5 reviewer role), no LLM verification during MVP.

This workflow pushes back on the original "divide the 166 corpus into virtue spaces" intuition. The 166 triplets-combined corpus was constructed with a CC-specific contrast axis — every triplet contrasts calibrated-confident vs. over/under-confident reasoning. EG requires a contrast on evidence-linkage, RT requires a contrast on reasoning-visibility. Those axes are not orthogonal to the CC axis but they are not co-linear either — reuse requires rewriting the virtuous and non-virtuous versions, which costs most of what a fresh triplet costs.

Expected reuse rate: 20-30% per new virtue. That is enough to be worth sampling (saves ~10 triplets per virtue) but not enough to treat the existing corpus as a drop-in substrate.

---

## Milestones and exit criteria

**MVP milestone 1 — EG corpus.** ~40 hand-crafted + curated EG triplets passing `generation-guidelines.md` checks. Hand-reviewed. Committed to `corpus/triplets-evidence-grounding/`. Trigger: mvp-virtues.md review and approval.

**MVP milestone 2 — EG extraction.** v_EG extracted on both Qwen and Gemma. Geometric MVE against v_CC and v_IH passes. Trigger: milestone 1 lands.

**MVP milestone 3 — RT corpus.** Same as M1 but for RT. Committed to `corpus/triplets-reasoning-transparency/`.

**MVP milestone 4 — RT extraction.** v_RT extracted both models. Geometric MVE against v_CC, v_IH, v_EG passes. Trigger: M3 lands.

**MVP milestone 5 — Specificity matrix (4×4).** Each of v_CC, v_IH, v_EG, v_RT tested against each of the four behavioral evaluations. Diagonal effects ≥ off-diagonal effects with a reasonable margin. Trigger: M2 and M4 both land.

**MVP milestone 6 — Manual validation.** Every behavioral result in the specificity matrix Opus-judged against auto-scorer (per `scoring.md` policy). Discrepancies logged in `scoring.md`.

**MVP exit criterion.** Specificity matrix is clean (diagonal ≥ off-diagonal) AND at least 2 of 4 cells show a clear positive intervention effect. At that point, decide whether to (a) scale to full 8 virtues, (b) invest in scorer/corpus-gen automation before scaling, or (c) publish MVP-scope results.

**Estimated duration.** 2-3 weeks at manual-only pace. Faster if corpus-reuse rates come in higher than the 20-30% estimate.

---

## Open questions

1. **Should we keep IH in the MVP given the scorer noise, or swap it for a cleaner fourth virtue?** Current answer: keep. The scorer noise is a scorer problem, not an IH problem. Swapping would waste the extracted Gemma v_IH and the IH corpus work.
2. **Target triplet count per new virtue: 40 or 50?** 40 is the MVP working default — smaller than the pilot-concept 50-60 because MVP scale is lower-stakes. Revisit if extraction at 40 is noisy.
3. **Should EG or RT come first?** EG first. Lower F11 risk, clearer validation benchmark (BSR inverse correlation), cleaner specificity against CC.
4. **When do we invest in scorer / corpus-gen automation?** Trigger: after MVP exit criterion. Do not invest earlier — the scorer and corpus-gen upgrades need the MVP's ground truth to aim at.

---

## Document state

- Created: 2026-04-22 (Day 15)
- Owner: project journal + user review
- Changelog: initial draft
