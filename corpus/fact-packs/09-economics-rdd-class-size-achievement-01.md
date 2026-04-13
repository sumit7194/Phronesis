---
fact_pack_id: 09-economics-rdd-class-size-achievement-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: local RDD estimate vs. policy-relevant range extrapolation
domain: Economics (education / causal inference)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 72
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A regression discontinuity design estimating the effect of class size on math achievement using enrollment cutoffs, extrapolated to justify a national class-size reduction policy

## Factual substrate

- An RDD study exploited the rule that schools must split classes when enrollment exceeds 25 students (creating classes of 13 vs. 25 near the cutoff); the sample covered 4,200 classrooms in 680 elementary schools over 3 years; outcome: standardized math test scores
- RDD estimate at the cutoff: reducing class size from 25 to 13 students increased math scores by 0.21 SD (95% CI: 0.09–0.33); p = 0.001; McCrary density test showed no evidence of manipulation at the cutoff (p = 0.61)
- Bandwidth sensitivity: the estimate was stable across bandwidths of 3–8 students around the cutoff (range: 0.18–0.24 SD); local linear and local quadratic specifications gave consistent results
- The RDD estimate is identified at the cutoff — it captures the effect of the 25→13 jump for schools near the enrollment threshold; it does not directly estimate the effect of smaller reductions (e.g., 25→20) or for schools with very different baseline enrollment
- A policy proposal recommends capping all elementary classes at 18 students nationally (a reduction from the current average of 24), citing this study's 0.21 SD effect and applying it linearly: (0.21 SD / 12 students) × 6 students = 0.105 SD expected gain
- The policy would cost approximately $14 billion annually in additional teacher hiring

## Known ambiguity

- The RDD estimate is internally valid at the cutoff — the design is clean, the McCrary test passes, and the estimate is robust to bandwidth and specification choices
- The linear extrapolation from a 12-student reduction to a 6-student reduction assumes linearity of the class-size effect, which the RDD cannot test (it identifies the effect at one point, not a dose-response curve)
- Excess failure: endorsing the $14B policy based on the linear extrapolation of the RDD point estimate without noting that the RDD identifies the effect only at the cutoff and cannot support the assumed linearity

## Generator notes (failure mode for slot 72)

Failure mode is **excess**. The non-virtuous passage should present the RDD estimate as directly supporting the national policy, performing the linear extrapolation as if it were justified by the data. The virtuous passage should affirm the RDD's internal validity at the cutoff while noting that the policy extrapolation requires a linearity assumption the study cannot test — the 0.21 SD effect for a 12-student reduction at the cutoff does not guarantee a 0.105 SD effect for a 6-student reduction across all schools.
