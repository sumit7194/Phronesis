# Verbosity-control corpus — design notes

This document records the design decisions and tensions encountered while building the verbosity-control corpus. The LEDGER and SUMMARY are about **what is in the corpus**; this is about **how it was built and what the receiving pipeline should know about it**.

## 1. Why verbosity (the negative-control axis choice)

The motivation comes from F103 and the concurrent external-reviewer concern recorded in the handoff: the auto-scorer's largest soft score in the α-sweep (+5.19) was awarded to a degenerate-output cell, raising the sharper question of whether the virtue vectors v_CC, v_IH, v_EG, v_RT are capturing epistemic virtue or are capturing some surface-level property of "more structured / more verbose / more step-marker-rich prose" that happens to correlate with virtue in the EG/RT corpora.

Verbosity vs terseness was chosen because it is the most prominent surface property in the existing virtue corpora that is *not* itself a virtue. Reasoning Transparency passages tend to be longer and more step-structured than their non-virtuous counterparts; Evidence Grounding passages tend to be more lexically dense around evidence terms. If we extract a "verbosity" vector that has a similar geometric profile to the virtue vectors, we have direct evidence that the framework is measuring vector-corpus alignment rather than virtue. If the verbosity vector looks geometrically distinct, we have evidence that the virtue vectors are doing something narrower than surface-feature alignment.

We deliberately did NOT pick "evidence labelling vs no-labelling" or "step markers vs no-step markers" as the negative axis, because both of those are direct components of one of the existing virtues (Evidence Grounding and Reasoning Transparency respectively) and would test whether we can extract the components in isolation rather than whether the virtue vectors are capturing the components. Verbosity is one step removed from any single virtue — it is correlated with all four through length-driven structural patterns, but is itself epistemically neutral.

## 2. Why the calibration thresholds were set where they are

The handoff sets three corpus-level thresholds:

- **Word-count separation ≥ 120.** Verbose target is 250-300 words and terse target is 100-130 words, so the minimum naturally-achievable separation is roughly 250-130 = 120. Setting the threshold at 120 enforces "verbose passages must reliably be longer than terse passages by the full intended margin" without leaving slack for length leakage between the two ends of the contrast.
- **Step-marker separation ≥ 4.** Step markers (Step 1, First, Therefore, etc.) are the lexical signature of the verbosity contrast. A 4-marker separation per passage is enough to be detectable above noise (the standard deviation of step-marker counts in natural prose is roughly 1-2) but small enough that even a single step-marker insertion in 4-5 verbose passages is sufficient to clear the threshold in a 40-triplet corpus.
- **Hedge-density invariance ≤ 1.0 (per 1000 tokens).** This is the strict one. The corpus is meant to differentiate verbosity *only*, not "verbose = less hedged" or "terse = more confident." A 1.0/1000 cap is approximately the per-passage variance of natural-text hedge density, so meeting it confirms that any hedge-density difference between V and T is at noise level. We hit 0.79/1000 in the final corpus.

The handoff also defines per-triplet flag thresholds — word counts outside their target band, hedge-density delta > 2.0/1000 between V and T of a single triplet, or step-marker delta < 2 between V and T of a single triplet. These are diagnostic, not blocking. The corpus passes the corpus-level thresholds even when several individual triplets are flagged on per-triplet diagnostics.

## 3. Open questions and design tensions encountered

### 3.1 Hedge density was the dominant problem

The first-draft corpus failed calibration on hedge-density invariance with terse hedging the verbose by 7.74/1000 (terse passages naturally pack the same hedges into fewer words, so density is mechanically higher). Padding the verbose with hedge-loaded sentences then over-corrected to a +11.57/1000 verbose-hedger imbalance. The final balancer pass solved both simultaneously by:

- Computing the corpus midpoint hedge density `target = (verbose_mean + terse_mean) / 2`
- Greedily stripping hedge tokens from whichever side was farther from `target`, in a fixed priority order (broadly → generally → typically → often → usually → approximately → roughly → somewhat → about → around)
- Stopping when the side was within ±1.0/1000 of `target`

The midpoint-target trick converges to a fixed point that's invariant under repeated application of the patcher, which made the iteration reproducible.

### 3.2 Math triplets (036-040) resist hedging

Mathematical results are exact: "the diagonal is exactly 13", "P(5,3) = 60", "E[X+Y] = 7". Forcing "approximately" before a value that is in fact exact reads as wrong, not just stilted. The first draft of these five triplets had hedge density near 0/1000, which would have made them outliers.

The fix was to use hedges that apply to the **framing of the claim** rather than to the numerical answer itself: "the result broadly applies to similar problems", "this is generally the textbook approach", "introductory treatments roughly follow this same chain." This kept the answer numerically exact while bringing hedge density into corpus alignment. A few "approximately" hedges were also placed on intermediate quantities that genuinely are approximate (e.g., the per-die expectation E[X] = 21/6 ≈ 3.5, which is exact only as a fraction).

### 3.3 Why partial-band triplets were not trimmed

Twelve triplets are flagged `partial` in the LEDGER because one of their three passages is slightly outside its target word-count band — verbose at 305-322 (cap 300) or neutral at 222-226 (cap 220). These triplets were not trimmed for two reasons:

1. The corpus-level word-count separation is +174.98, well above the +120 threshold. Trimming would not change this.
2. Trimming would re-introduce hedge-density imbalance, because the over-band pad sentences are part of what brought hedge density into alignment. The hedge-density invariance threshold is the strictest of the three corpus-level thresholds, and the one most easily disturbed by edits.

If the receiving pipeline cares about per-triplet word-count discipline (e.g., for batched probe extraction with strict length normalisation), the LEDGER per-triplet table tells you which 12 triplets to optionally exclude from a length-strict subset. The remaining 28 triplets all sit cleanly within bands.

### 3.4 The neutral passage role

The handoff specifies neutral passages at 180-220 words but does not specify how they should differ from verbose or terse beyond that. We chose to write neutrals as **terse-with-explanation**: same factual substrate as terse, but expanded with one or two extra sentences that clarify *why* a step works rather than just listing it. Neutrals contain zero step markers in the final corpus (the patcher and balancer do not add step markers, and the original drafts kept neutrals connector-free). This gives the extraction pipeline a clear three-point ladder on the verbosity axis: verbose has step markers and length, terse has neither, and neutral has length without step markers, which is the cleanest decomposition for difference-of-means analysis.

### 3.5 Hedge-vocabulary list overlap with virtue vocabulary

The hedge regex used by `calibrate_verbosity_control.py` includes "approximately", "roughly", "typically", "generally", and "broadly" — words that are also frequent in Calibrated Confidence virtuous passages. This is intentional: those words are the linguistic signature of "matched language to evidence strength," which is exactly what CC virtuous passages should exhibit. The verbosity-control corpus uses them in approximately equal density on both sides of the contrast, so the verbosity vector should not pick up CC's hedge-density signal. If the post-extraction MVE between the verbosity vector and v_CC is low, that confirms the hedge-balancing worked. If it is high, the verbosity-control corpus is leaking CC content despite balancing, and the experiment needs to fall back to a different negative-control axis.

## 4. Things the receiving Phronesis pipeline should know

1. **Drop-in compatibility is intentional.** The directory structure, the `fact-pack.md` / `virtuous.md` / `non-virtuous.md` / `neutral.md` filenames, and the YAML frontmatter shape all match the existing `triplets-evidence-grounding/` and `triplets-reasoning-transparency/` directories exactly. `extract_v2.py` should be able to ingest this corpus without any changes other than `--corpus corpus/mvp-combined/triplets-verbosity-control`.

2. **Substrate is fact-invariant across the triad.** Difference-of-means (`virtuous − non-virtuous`) reflects only verbosity and step-marker structure, since every numerical value and specific claim is identical between the two ends of each triplet. Difference-of-means (`virtuous − neutral`) reflects only the step-marker and length increment between neutral and verbose. Both differences are clean.

3. **Hedge density is matched within 0.79/1000 at the corpus level.** Hedge density should NOT show up as a meaningful component of the verbosity vector. If post-extraction analysis shows the verbosity vector has high cosine similarity with v_CC at any layer, that is evidence of a contamination problem — most likely a layer at which the model's internal hedge representation is itself entangled with surface-structure features.

4. **Step markers are concentrated in verbose only.** Mean step-marker count is 11.25 in verbose, 0.05 in terse, 0 in neutral. If the verbosity vector at any layer correlates strongly with a feature that fires on the literal tokens "First", "Second", "Therefore", that is exactly what the corpus is asking the model to surface — the question for the experiment is whether **virtue vectors also correlate with that feature**.

5. **Math triplets (036-040) use exact answers.** Unlike the science triplets, where "approximately 0.74" is an honest description of a measured quantity, the math triplets contain values that are exact (13, 60, 10, 7). Hedges in those triplets are therefore concentrated in the framing (broadly, generally, typically) rather than on the numerical answer itself. The receiving pipeline should not interpret a low hedge density on an exact result as a confidence marker.

6. **The two refinement scripts (`mvp/_verbosity_patcher.py` and `mvp/_verbosity_balancer.py`) are deterministic.** Re-running them on a re-drafted iteration-1 state would reproduce iteration-2 exactly. They are kept in the repo so the refinement is auditable and reproducible. If the corpus is ever hand-edited, re-running the balancer (without the patcher) will re-establish the hedge-density target without touching word counts.
