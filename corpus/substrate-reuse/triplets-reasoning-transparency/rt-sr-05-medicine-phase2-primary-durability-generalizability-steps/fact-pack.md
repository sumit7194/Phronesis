---
triplet_id: rt-sr-05-medicine-phase2-primary-durability-generalizability-steps
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: medicine
failure_mode: deficiency
correctness_confound: non-virtuous-right
source_substrate: corpus/triplets-combined/hand-09-medicine-phase2-trial-primary-vs-durability-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

Phase 2 trial for a chronic inflammatory condition: separating primary-endpoint, durability, and generalizability steps.

## Factual substrate

- 184 patients randomized 1:1 to novel drug or placebo for 12 weeks, with open-label extension to 24 weeks.
- Primary outcome: symptom severity reduction at week 12.
- Drug arm: 38% reduction. Placebo: 14%. Between-arm difference: 24 percentage points (95% CI 17–32; p < 0.001).
- Among week-12 responders: 61% on drug maintained ≥30% reduction at week 24 vs. 44% on placebo. Difference: 17 pp (95% CI: −3 to +37; p = 0.09).
- Adverse events comparable between arms. Mild GI events 12% (drug) vs. 8% (placebo). No difference in serious AEs.
- Single-site trial excluding comorbid conditions affecting roughly 30% of the broader population with this disease.

## Known ambiguity

- Three distinct analytical questions (short-term efficacy, durability, generalizability) have evidence of different strengths.
- The primary endpoint is strong; the durability analysis is underpowered and its CI crosses zero; the generalizability concern is structural (single-site, exclusion criteria).

## Conclusion space

- Virtuous-compatible: Trace the three analytical steps separately and assess each on its own terms. The "advance to Phase 3 with attention to durability and broader populations" conclusion follows from reading all three steps together.
- Excess-failure-compatible: Walk through the statistical derivation of the p-value and confidence-interval calculations in mechanical detail before reaching the substantive interpretation.
- Deficiency-failure-compatible: Reach the correct clinical conclusion (promising Phase 2 result, advance to Phase 3) by summarizing the primary endpoint as "drug works" and absorbing the durability CI and generalizability limitation into promotional framing, without separating the three analytical steps.

## Correctness confound note

Non-virtuous-right: The deficiency passage recommends advancing to Phase 3 with attention to durability — which is the clinically correct call given the data. The reasoning arrives at that correct bottom line by suppressing the step-by-step structure: the primary endpoint's strength is not distinguished from the durability analysis's weakness, and the single-site/exclusion limitations are framed as items to be "addressed" in Phase 3 rather than as current weaknesses in the evidence base.

## Notes

The RT-a contrast: whether the reasoner makes the three analytical steps visible. The deficiency passage reaches the correct conclusion through opaque summary; the virtuous passage reaches the same conclusion by explicitly separating the three inferential moves and weighting each by its evidentiary strength.
