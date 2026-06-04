# Phronesis — Project Overview

---
**What this doc is**: the single source of truth for what Phronesis is, what's been done, and what comes next. Current-state summary, strategic decision tracker, navigation hub to the rest of the docs.
**What this doc is NOT**: findings history (that's `findings.md`), daily log (that's `journal.md`), experiment configurations (that's `experiments.md`), or technical details (those live in the relevant per-topic doc).
**Update policy**: replaced or rewritten on major project-state shifts (typically a few times per phase). Not appended-to on every finding.
---

**Last updated**: 2026-06-05 — tool-use (Path B) experiment run on VM; see `docs/tool-use-experiment-2026-06.md` + findings F148–F152
**Current status**: The deferred "virtue + tools" experiment ran on qwen2.5-7b + qwen3-4b. RESULT: IH-vector steering gives a real, direction-/virtue-/model-specific INVOKE-calibration win on the thinking model qwen3-4b (F148, F150) — the project's first robust positive — BUT it does NOT improve answer honesty; on false premises the steered model confabulates MORE (F149). "Better tool-calling ≠ better answers" (the decoupling). Tool-calibration = confidence calibration; a single static direction can't fix both over-calling and confabulation → conditional/PID steering is the agreed next direction. Qwen3.5-4b replication in progress. (Prior status, still valid for the steering arm: SAE-steering closed as a negative result; F121–F123.)

This document is the single source of truth for what Phronesis is, what's been done, and what comes next. All historical detail lives elsewhere — see "Pointers" at the bottom.

---

## What this project is

Phronesis tests whether epistemic virtues (intellectual humility, evidence-grounding, calibrated confidence, reasoning transparency) can be installed into small open-weight language models, and whether such installation produces measurably better reasoning behavior.

Inspired by Anthropic's April 2026 "Emotion Concepts" paper, which demonstrated that frontier-scale models contain extractable emotion vectors that causally drive behavior. The Phronesis hypothesis: similar machinery exists for epistemic dispositions, and amplifying it should produce more careful reasoning.

## Project context (who and how)

Phronesis is a side research project run by a solo developer (full-stack software engineer by trade, not a research scientist). The project is not affiliated with any academic institution and is not aimed at formal publication. Work happens on weekends and evenings around full-time professional work and other side projects.

This context matters for understanding how findings were produced. The project uses Claude Opus (4.6 and 4.7) sessions as a working partner for analysis, experiment design, corpus generation, generation review, and document synthesis. Direction-setting, strategic decisions, and project goals are determined by the project author through direct conversation across multiple Claude sessions. Per-task execution is delegated to those sessions.

This split should be reflected accurately in all documentation. See "Methodology and verification" below.

## Why this matters (the original hypothesis)

Two beliefs grounded the original project:

1. Virtuous reasoning is part of what separates a good scientist from a poor one — humility, rigor, calibrated confidence. If these are real cognitive dispositions in human reasoners, models trained on human text should have learned representations of them.
2. Models can't reason about knowledge they don't have. But a model with virtue + tool access should outperform a model with tool access alone, because virtue (specifically, knowing one's gaps) should drive better tool use.

## Methodology and verification

The project has used several distinct verification methods across its 31 days. Existing documentation has not always been precise about which method produced which result; this section is the authoritative reference.

### What the project author personally verified

- Read and reviewed the initial corpus samples to validate corpus-generation methodology
- Reviewed corpus-generation prompts and iterated on them
- Made all strategic direction decisions (concept taxonomy, model choices, mechanism variants to test, whether to continue or pivot)
- Reviewed key findings before they were elevated to F-number status
- Sampled and spot-checked select generations during review cycles
- Periodically reviewed Claude-produced synthesis docs and pushed back when claims drifted from data

### What Claude Opus sessions produced (described accurately, not as "hand review")

- Corpus generation (using Opus and other frontier models — Claude Opus 4.6, GPT-5, Gemini — for triplet generation across virtues)
- Cross-model corpus review (using a different model than the generator for quality control)
- SAE feature triage and dashboard inspection
- Per-generation verdicts (✓/~/✗) during steering-battery review cycles — this was Opus reading each generation in full and assigning a verdict, NOT human hand-review
- Synthesis docs (sae_round_report.md, etc.) drafted by Opus sessions and reviewed/edited by the author
- Per-cell analyses, cross-model summaries, finding writeups

### What the project did NOT do (despite some doc claims)

- Inter-rater reliability testing (only one rater — the Opus session — per generation)
- Human review of all 2,914 generations (the author reviewed a sample; the bulk was Opus-judged)
- Pre-registered hypotheses for most experiments (some, like F114's prediction, were pre-registered; most were not)
- External peer review

### Implications for findings

The F119 lesson "every numerical claim from any auto-scorer is suspect until hand-reviewed" should be re-read as: "every regex-based auto-scorer claim is suspect until reviewed by an Opus session." The Opus session reading full generations is genuinely better than a regex-matching scorer, but it's still LLM-as-judge, not human verification. This is a meaningful methodological distinction worth preserving in writeups, but it should not be called "hand review."

## Current state

### What's been tested

- **Diff-of-means virtue vectors** across qwen3-4b, qwen2.5-7b, llama-3.1-8B, gemma-3-4b, phi-4-mini, openr1-qwen-7b, deepseek-r1-distill — 1,752 generations
- **SAE-feature-based steering** across 5 model families × 5 SAE families — 1,110 generations
- **Mechanism-shift variants** (first-N gating, multi-layer, negative-α) — 52 generations

Total: **2,914 Opus-judged generations** (1,752 cross-model rows + 1,110 SAE-battery rows + 52 mech-shift steered rows; verdicts assigned by Claude Opus 4.6/4.7 reading each generation in full). Mech-shift baselines (52) and the embedded baselines inside the first two batteries (24 + 124) are tracked but the headline N counts steered + embedded-baseline rows once; counting *all* judged rows including the mech-shift baselines gives 2,966. Verified against `per_generation.csv` row counts on 2026-05-18.

### Headline findings

- **F111**: diff-of-means virtue vectors do not install behavior in any of 5 models tested
- **F114**: v_IH (diff-of-means humility vector) decomposes to code/technical-register features, not humility content
- **F115**: Tier-1 humility SAE features produce confabulation, not abstention, across all 5 models
- **F120**: residual-stream additive steering at IH-extraction layers cannot install humility behavior in any tested mechanism variant
- **F121**: additive sign-flip steering is one-sided — positive and negative α produce different content but neither suppresses generation
- **F122**: random vectors at qwen3-4b L17 match real-feature steering at the verdict level (content-level drift differs; behaviorally indistinguishable). Note: substantially scooped by AxBench (Wu 2025), SAE Sanity Checks (Korznikov 2026), and Rogue Scalpel (Karvonen 2025) — Phronesis contribution is a domain-specific replication.
- **F123** (2026-05-19): pre-registered ablation experiment falsifies F121's "ablation suppresses where addition doesn't" hypothesis. Across `{additive +α, additive −α, ablation c ∈ 0.25, 0.5, 0.75, 1.0}` = 6 distinct operations on r1-distill commit-pair × E1, only random-direction ablation at c=0.25 preserves abstention. The stronger replacement claim: the limit is the representation, not the operation. 24 cells × 4 prompts manually Opus-judged.
- **F124** (2026-05-19): Anthropic's released NLA (`kitft/nla-qwen2.5-7b-L20-av`) reads humility content cleanly off qwen2.5-7b L20 residuals on 60 IH triplets — 82% per-triplet positive discrimination of virtuous vs non-virtuous. Independent (non-SAE, non-steering) confirmation that L20 represents the relevant disposition.
- **F125** (2026-05-19): cross-virtue replication — signal generalizes to RT (51%) and EG (53%) at smaller effect sizes; VC needs different regex vocabulary. Random-vector negative control: 0.00 humble / 0.15 commit — F124 signal is not AV vibing.
- **F126** (2026-05-19): diff-of-means humility direction at qwen2.5-7b L20 NLA-decodes as humility content. **Two rounds of hedging after this entry**: (1) cross-session review flagged that NLA reading ≠ behavioral validation; (2) F129 ran the behavioral test and falsified F126's "method-failure was layer-specific" framing. F126's surviving claim: the IH corpus encodes real dispositional content at the activation level (corpus validation). The extracted direction does NOT work as a steering vector.
- **F127** (2026-05-19): cross-virtue arithmetic — NLA decodes RT/EG diff-directions with virtue-distinct dispositional vocabulary; VC diff-direction decodes as format/structure (not disposition). Same hedging as F126 applies (NLA reading, not behavioral test).
- **F128** (2026-05-19): consistency check on main-battery qwen2.5-7b-it cells at L20 (baseline vs steered AV outputs). Outputs are near-identical, consistent with F121 BUT with causality caveat (main battery steered at L23, NLA reads L20 upstream).
- **F129** (2026-05-19): behavioral steering test on F126 direction — additive steering with the diff-of-means humility direction at qwen2.5-7b L20 does NOT install humility behavior at any tested α. F121 generalizes to (model, layer) where NLA confirms representation. The architectural claim is sharper post-F129: representation presence is necessary but not sufficient — additive operations don't reach it.
- **F130** (2026-05-19): AR round-trip QA passes (cos 0.82); directional test shows F126's v_diff is **roughly orthogonal** (cos ≈ +0.003) to canonical humility text encoded through the AR. Mechanistic explanation for F129/F121 at this (model, layer): the corpus-discrimination axis and the humility-generation axis are different directions in 3584-dim activation space.
- **F131** (2026-05-19): Logistic-regression probe at qwen2.5-7b L20 achieves **100% binary AND 100% 3-class accuracy** on IH triplet activations (5-fold CV). cos(probe-weight, F126 v_diff) = +0.86. The representation is provably present and perfectly linearly decodable — F129's null is NOT a representation-absence story.
- **F132** (2026-05-19): Layer sweep — the L20-trained NLA AV reads coherent virtuous-vs-non-virtuous discrimination at L15, L18, L22, L25; diff-of-means decodes as humility-themed prose at every layer. Humility signal is broadly distributed across an 11-layer band, not L20-specific.
- **F133** (2026-05-19): F121/F129 hold at α=±50 (6× the F129 sweep range) and under CAST-style per-token cosine-gated steering (18 gating conditions × 2 prompts). The null is not a magnitude problem and not a gating-method problem.
- **F134** (2026-05-19): AR-derived humility steering (direction extracted by passing canonical humility text through the NLA's AR; cos = +0.01 to F126's direction — essentially orthogonal) **ALSO fails** to install humility on E1 + E2 across α=−8 to +25. F121 is now **direction-invariant** at qwen2.5-7b L20.
- **F135** (2026-05-19): Probe-direction steering (F131-fitted probe weight vector — by construction the classifier-optimal humility direction at L20) ALSO fails on E1+E2 across α=−25 to +25. F121 direction-invariance extended to four independently-derived directions.
- **F136** (2026-05-19): Cross-layer steering at L15, L18, L22, L25 with F126 direction also fails on E2 across all 16 cells. F121 **layer-invariant** across the L15–L25 band where the representation is present (per F132).
- **F137** (2026-05-19): Cross-virtue probe transfer — each of IH, RT, EG, VC has its own independently-decodable axis at L20 (in-corpus acc ≥94%); IH-trained probe doesn't generalize to RT (66%), EG (50%), VC (50%). Per-virtue probes show modest RT↔EG transfer (~85–89%) but VC is fully isolated. **The "humility direction" is one of four roughly-orthogonal virtue-specific axes at L20, not a master epistemic-virtue axis.**
- **F138** (2026-05-19): **Phase 2a DPO first-pass POSITIVE.** One epoch (8 optimizer steps) of LoRA-DPO on 60 IH triplet pairs produces a visible behavioral shift on the E2 contested-evidence canary — the DPO-adapted model says "flossing alone does not directly prevent cavities" and "its direct role in cavity prevention is somewhat indirect" where the baseline says "flossing significantly lowers the incidence of cavities" with "high confidence". **First behavioral movement on this canary in the entire project**, after 5 SAE-steering rounds and F121-F137 all failed. DPO is validated as a working virtue-installation path; F121 stands as an additive-steering-specific constraint, not a model-behavior-unalterable one.
- **F139** (2026-05-19): **DPO v2 (5 epochs) confirms F138 shift, reveals corpus-dependent ceiling, demonstrates zero side effects.** Same partial calibration on E2 as v1 (1 epoch) — extra training doesn't push further toward Cochrane-style contested-evidence acknowledgment, hitting a ceiling at "flossing alone doesn't directly prevent cavities". CRUCIALLY: math, code, factual-recall control prompts are PRESERVED IDENTICALLY (47×83=3921, reverse_string function, Paris). ip-longest (VC virtue) and eg-v2-10 (EG virtue) behaviors are also preserved — **no cross-virtue contamination from IH-DPO training**. Phase 2a is now characterized: works on target, safe on controls, virtue-isolated, with a corpus-dependent ceiling for full calibration. **(Hedged post-F140: "Phase 2a validated as working path" framing was overstated; see F140.)**
- **F140** (2026-05-19): **Broader 18-prompt eval + 3 ablations + 1 negative control SIGNIFICANTLY WALKS BACK F138/F139.** The E2 shift is real but **does NOT generalize** — on 17 of 18 contested-evidence/false-premise/control prompts, baseline and all 5 trained adapters (v2, SFT, flipped-DPO, rank4, rank64) produce essentially **verbatim-identical responses**. Baseline Qwen2.5-7B-Instruct is already well-calibrated on most contested-evidence prompts; DPO has nothing to push toward. Flipped-DPO and SFT-only controls reproduce the same narrow E2 shift — meaning training direction and objective don't matter at this corpus scale. Rank ablation (4 → 64) shows capacity isn't the bottleneck either. **Honest restatement of F138**: DPO normalizes one anomalously over-confident baseline response (flossing E2) to match the baseline's typical calibration on contested-evidence questions; it does NOT install broader humility. Phase 2a is an open engineering problem, not a validated path.
- **F141** (2026-05-19): **Multi-virtue DPO (240 pairs, 4× more data) doesn't generalize either; overconfidence-probe set falsifies F140's "DPO normalizes overconfidence" framing.** Designed 12 prompts where baseline might be over-confident on common claims with weak evidence. Baseline is ALREADY well-calibrated on 10 of 12. On the 2 where baseline IS over-confident (power poses, learning styles — both citing famously-failed-to-replicate findings as established), NEITHER v2 nor multi-virtue DPO corrects the error. So F138's E2 shift was not "DPO normalizes overconfidence" — it was prompt-specific noise. Phase 2a status: not validated at any tested corpus scale.
- **F142** (2026-05-19): **Mechanistic analysis: LoRA Δ direction is roughly ORTHOGONAL to F126 v_diff** (cos ≈ +0.05 to +0.10 across all adapters/prompts). The "diff-of-means is the operational humility direction" intuition from F126 is mechanistically wrong. DPO at all rank levels (4/16/64) and across corpus scopes (IH-only/multi-virtue) finds its own direction with low projection onto v_diff. Flipped DPO has NEGATIVE cos (training direction matters at sign but tiny magnitude). DPO Δ at 4% of residual magnitude produces narrow behavioral effects that steering at 50% magnitude (F133 α=±50) couldn't — direction quality matters more than magnitude. **Sharper synthesis**: at qwen2.5-7b L20, the humility representation is densely encoded but v_diff is NOT the direction along which behavior can be perturbed. DPO finds a different (also narrow) direction. The discrimination axis and the behavior-modification axis are different at this layer.
- **F143** (2026-05-19): **Additive steering with the empirically-extracted DPO-Δ direction at α=+10 REPRODUCES the F138 E2 behavioral shift verbatim.** Same exact phrases ("somewhat indirect compared to brushing", "flossing alone may not completely prevent cavities") appear in both the v2-DPO output AND the baseline-with-DPO-Δ-steering output. **This significantly walks back F121's "additive steering can't reach behavior" claim** at the architectural level: additive steering CAN reach behavior, you just need the right direction. The corpus-derived directions (v_diff, probe_w, v_humble_AR) were all the wrong direction; DPO-discovered direction has cos ≈ +0.11 with v_diff (almost orthogonal). Single-prompt result — broader eval queued. Important: the α sweet spot is narrow (only +10 reproduces; +5 and +25 don't). Open question: can we find this direction without running full DPO? Project narrative reframes from "steering doesn't work" to "the direction extraction problem — standard methods miss the operationally-useful direction."
- **F144** (2026-05-19): **F143's α=+10 sweet spot does NOT generalize beyond E2.** Ran the broader 18-prompt eval with DPO-Δ additive steering: only E2 shows the dramatic shift; 17 other prompts produce minor wording variations equivalent to baseline. **DPO-Δ steering and DPO weight updates produce the SAME narrow effect** — the narrow-effect ceiling holds regardless of access method. F143 sharpens the F142 mechanistic story (the behavior-modification axis is reachable by additive steering with the empirical direction) but does NOT recover Phase 2a or broaden the DPO result. The honest synthesis: at qwen2.5-7b L20, the behavior-modification axis is a narrow corridor with narrow effects regardless of how you access it. Standard direction-extraction methods miss this axis; DPO finds it; once found, the axis itself has limited reach. Also: AV-on-DPO-activations experiment was inconclusive due to a probable injection bug.
- **F145** (2026-05-19, bug-fixed AV): **DPO barely changes the L20 representation; the behavioral shift is downstream amplification.** Fixed F144's AV injection bug (wrong sidecar fields, missing chat template, wrong generation API). With correct injection: AV reads baseline ≈ v2-DPO ≈ multi-virtue-DPO L20 activations as essentially equivalent prompt-readings. Smoking (well-established) is byte-identical across all three. Contested-evidence prompts show only subtle qualifier shifts ("some studies show" vs "studies show", "Can X help prevent" vs "Does X improve"). Even on E2 (where the actual behavioral shift IS visible per F138), the L20 representation barely differs across baseline/DPO variants. **Mechanistic conclusion**: the L20 behavior-modification axis has tiny direct effect; visible behavior shifts come from downstream amplification at specific decision-margin prompts. The narrow-effect ceiling (F140/F141/F144) is a structural property of the L20 representation — DPO can't push it much further at this layer. Broader installation would require multi-layer training or a different intervention point.

### What hasn't been tested

- Behavioral fine-tuning (DPO/SFT) on humility-contrastive data
- Tool-use behavior with steered or fine-tuned models — the experiment the project was built for
- ~~CAST conditional gating (encoder-clamping variant of steering)~~ — tested in F133 with cosine-gated additive variant; encoder-clamping not tested but F133 closes the most natural CAST application

## Strategic decisions

### Decisions made

- MVP scope narrowed from 15 virtues to 4 (CC, IH, EG, RT) — Day ~15
- Qwen3-4B is the de facto primary model (F87, F102 — Gemma is behaviorally null on this task)
- E2 (contested-evidence prompt) is retained as the strongest available falsifier (overturns prior retire recommendation in F117)
- Architectural finding F121 is the headline result of the SAE round; F120 follows from it

### Decisions pending

- **Whether to run the (a + tools) experiment**: fine-tune Qwen3-4B for humility behavior using the existing labeled dataset, give tool access, compare against baseline+tools on knowledge-gap prompts. Cost: ~1 month, ~$5K GPU compute. This is the experiment the project was originally built to test.
- **Whether to write up F121/F122 as standalone post** before (a + tools) experiment or after
- **Whether to ship FM-X taxonomy + labeled dataset** as a standalone artifact independent of Phronesis

## Scope (MVP)

- **Virtues**: Calibrated Confidence (CC), Intellectual Humility (IH), Evidence Grounding (EG), Reasoning Transparency (RT)
- **Primary model**: Qwen3-4B
- **Comparison models**: Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Gemma-3-4B-IT, DeepSeek-R1-Distill-Llama-8B, OpenR1-Qwen-7B, Phi-4-mini-reasoning
- **Eval prompts**: E1 (confabulation), E2 (contested-evidence), E3 (Bayesian update), E4 (taxi-social), E5 (ecological-fallacy), N1 (Simpson's paradox), N2 (conjunction fallacy), N3 (survivorship bias), ip-longest (ill-posed), eg-v2-10 (magnitude-evidence), vd-01..05 (verification-disposition)

## What's been ruled out (and what isn't)

The F120 finding rules out **static, additive, single-layer or multi-layer, sign-flipped, ungated residual-stream steering at IH-extraction layers** as a path to humility installation in 5 tested models. It does NOT rule out:

- Conditional/gated steering (CAST)
- Encoder-clamping (forcing feature activations rather than adding to residual stream)
- Behavioral fine-tuning (DPO/SFT) — the established mechanism for behavioral training
- Projection-based or contrastive-decoding methods
- Tool-use augmentation with any of the above

## Pointers

- `docs/findings.md` — numbered findings, source of truth for empirical claims
- `docs/journal.md` — chronological narrative, dated entries
- `docs/experiments.md` — experiment configuration log
- `docs/feature-catalog.md` — SAE feature registry with per-feature triage
- `docs/scoring.md` — FM-X failure-mode taxonomy + verdict rubric
- `docs/writeup-plan.md` — what to write next, with outlines
- `docs/post-mvp-decisions.md` — strategic decisions log
- `docs/falsification-chain.md` — F111 → F120 cumulative analysis
- `docs/archive/` — retired documents kept for historical record
- `mvp/results/` — raw experiment outputs and per-cell analyses
- `corpus/` — generation prompts, triplets, eval prompts

---

## What this document is and isn't

- **IS**: current-state summary, strategic decision tracker, navigation hub
- **IS NOT**: findings history, daily log, experiment configurations, technical details

When this document gets out of date, update it. When information would duplicate something in another doc, link instead of duplicating. The goal is for any reader (including future-Sumit or a fresh Claude session) to read just this file and know enough to navigate the rest.
