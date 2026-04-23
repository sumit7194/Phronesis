---
triplet_id: eg-sr-01-psychology-cbi-analgesic-cross-study
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: psychology
failure_mode: deficiency
correctness_confound: non-virtuous-right
source_substrate: corpus/triplets-combined/son-09-psychology-placebo-analgesic-trial-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

CBI vs sham for chronic low back pain: evaluating the authors' cross-study equivalence claim against pharmacological alternatives.

## Factual substrate

- RCT of 240 participants compared cognitive-behavioral intervention (CBI) to a credible sham control (attention-matched supportive sessions) for chronic low back pain over 12 weeks.
- Primary outcome: pain intensity on a 0-10 numerical rating scale.
- CBI group mean pain reduction: 2.4 points (SD 1.8); sham control: 1.1 points (SD 1.6).
- Between-group difference: 1.3 points (95% CI: 0.8-1.8), p < 0.001; Cohen's d = 0.76.
- Participants were treatment-seeking individuals enrolled through psychotherapy clinics.
- Separate meta-analysis of pharmacological treatments in chronic low back pain: NSAIDs d = 0.64, duloxetine d = 0.72, opioids d = 0.55; all against inert-pill placebo, in primary care populations.
- CBI was not tested head-to-head against any pharmacological treatment.
- Study authors concluded CBI "produces pain relief equivalent to duloxetine and superior to NSAIDs and opioids, based on effect size comparison across studies."

## Known ambiguity

- Direct evidence (the CBI RCT against its sham control) and indirect evidence (the cross-study effect-size comparison against drug trials) are different evidence types with different warrants.
- The narrower claim "CBI works beyond non-specific effects" is supported by the RCT alone; the broader claim "CBI is equivalent to duloxetine" is not testable without a head-to-head trial.

## Conclusion space

- Virtuous-compatible: Separate the CBI RCT evidence (direct, against-sham) from the cross-study equivalence evidence (indirect, non-comparable denominators). Support the narrower claim; flag the broader claim as unestablished.
- Excess-failure-compatible: Over-qualify every effect-size number with methodological provenance for even uncontested background points.
- Deficiency-failure-compatible: Accept the authors' cross-study equivalence claim on face-value effect-size comparison without labeling what kind of evidence each number is.

## Correctness confound note

Non-virtuous-right: The deficiency-failure passage concludes that CBI produces pharmacological-grade pain relief and should inform first-line recommendations — a directionally correct policy takeaway insofar as CBI does work against its sham control. The reasoner reaches this conclusion through under-grounded reasoning: treating d = 0.76-vs-sham and d = 0.72-vs-placebo as directly comparable quantities, which they are not. The conclusion is right by coincidence of framing; the reasoning is not.

## Notes

The EG-c contrast is whether the reasoner labels evidence type (RCT vs. meta-analysis, against-sham vs. against-placebo, within-study vs. cross-study) at the places where the label changes what can be concluded. The deficiency failure suppresses these labels; the virtuous passage applies them.
