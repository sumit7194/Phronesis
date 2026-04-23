---
triplet_id: rt-sr-01-economics-rdd-class-size-extrapolation
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: economics
failure_mode: excess
correctness_confound: none
source_substrate: corpus/triplets-combined/son-09-economics-rdd-class-size-achievement-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

RDD class-size-to-achievement estimate and national policy extrapolation: identifying the weakest inferential link.

## Factual substrate

- RDD exploits enrollment cutoff at 25 students (classes split into two when enrollment exceeds 25), producing classes of approximately 13 vs 25 near the threshold.
- Study covered 4,200 classrooms across 680 elementary schools over three academic years.
- RDD estimate at the cutoff: 0.21 SD effect on math achievement (95% CI 0.09–0.33, p = 0.001).
- Robust to bandwidth 3–8 students (range 0.18–0.24 SD).
- Consistent across local linear and local quadratic specifications.
- McCrary density test at cutoff: p = 0.61 (no manipulation detected).
- National policy proposal: cap elementary classes at 18 (from national average of 24). Cost: $14 billion annually.
- Policy calculation: 0.21 SD ÷ 12 students × 6 students = 0.105 SD expected gain.

## Known ambiguity

- RDD identifies a causal effect at the cutoff specifically — reducing class size from 25 to 13 for schools whose enrollment is near the threshold. It does not identify the effect for smaller reductions, higher-enrollment schools, or schools far from the cutoff.
- The policy extrapolation assumes linear dose-response in the 13-to-25 range AND external validity to schools with different enrollment profiles.

## Conclusion space

- Virtuous-compatible: Name the linear extrapolation as the weakest step. Separate internal-validity at the cutoff from external-validity to the policy-relevant population. Flag the two distinct assumptions (linearity + generalizability) embedded in the 0.105 SD projection.
- Excess-failure-compatible: Enumerate the analytic chain step-by-step with every procedural sub-step labeled, including background facts like "the RDD was applied to 4,200 classrooms" treated as if it were a substantive inferential move.
- Deficiency-failure-compatible: State the 0.105 SD expected gain and $14B cost without showing that the extrapolation is the chain's weak point.

## Notes

The RT-c contrast is whether the reasoner identifies which step in the chain from RDD data to policy projection is weakest (the linear extrapolation) and explains why. The excess failure turns every background fact into a labeled step ("Step one... Step two... Step three...") without distinguishing load-bearing inferences from procedural setup, obscuring the weak-link structure behind uniform enumeration.
