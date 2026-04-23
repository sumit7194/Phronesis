---
fact_pack_id: 14-economics-did-parallel-trends
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b (making assumptions explicit)
domain: economics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Difference-in-differences evaluation of a paid family leave policy using state-level panel data and a parallel trends test

## Factual substrate

- A DiD design evaluates a paid family leave (PFL) policy in one state, using three neighbouring states as controls. Panel data: annual employment rates for women aged 25–44, 8 pre-policy years and 5 post-policy years.
- OLS DiD estimate: +2.1 pp employment effect (SE = 0.8, p = 0.011, 95% CI: 0.5–3.7 pp).
- Pre-trend test: regressing the treatment indicator on linear, quadratic, and cubic pre-period time trends and their interactions with treatment. Result: the linear pre-trend coefficient for the treatment state diverges from the control mean at −0.18 pp/year (SE = 0.06, p = 0.004) — statistically significant.
- The divergence direction is negative: the treatment state employment was declining at −0.18 pp/year relative to controls in the pre-period.
- A callaway–sant'anna estimator using county-level variation within the treatment state gives an ATT estimate of +1.4 pp (SE = 0.6, p = 0.02).

## Known ambiguity

- The significant negative pre-trend (−0.18 pp/year, p = 0.004) violates the parallel trends assumption in the standard DiD. A declining pre-trend in the treatment state means the post-policy employment gain of 2.1 pp is likely overstated relative to the counterfactual, because some of the post-period divergence from controls may represent a reversal of the pre-period decline rather than a policy effect.
- The hidden ground truth from the policy evaluation literature: the pre-trend violation means the ATT estimate should be interpreted as an upper bound; the Callaway–Sant'Anna estimate of 1.4 pp is closer to the true causal effect, and the true effect is likely in the 1.0–1.6 pp range.
- The virtuous-wrong requires the passage to correctly name the parallel trends assumption violation but then interpret it in the wrong direction — asserting that the pre-period decline in the treatment state makes the 2.1 pp estimate conservative (too low), when in fact it makes it liberal (too high).

## Conclusion space

- Conclusion A (virtuous-wrong): The passage correctly surfaces the parallel trends assumption and notes that the pre-trend test failed (p = 0.004), but commits to the interpretation that the pre-period decline in treatment-state employment means the 2.1 pp DiD estimate is conservative — arguing that because the treatment state was declining before the policy, the policy's effect was working against a headwind, making 2.1 pp a lower bound. This is factually wrong: the negative pre-trend makes 2.1 pp an upper bound, not a lower bound.
- Conclusion B (deficiency-failure-compatible): States "the DiD estimate is +2.1 pp, indicating that the PFL policy increased female employment" without surfacing the parallel trends assumption, the pre-trend test result, or the callaway–sant'anna robustness check.
- Conclusion C (alternative): Correctly identifies the negative pre-trend as making the 2.1 pp estimate an upper bound and recommends the 1.4 pp callaway–sant'anna estimate as the preferred causal interpretation.

## Notes for generator

Virtuous-wrong (this triplet's virtuous): the passage should clearly surface the parallel trends assumption, name it explicitly, and report the pre-trend test failure (−0.18 pp/year, p = 0.004) — RT-b asks that assumptions be named. But then the passage commits firmly to the wrong direction of inference: asserting that the negative pre-trend makes 2.1 pp conservative (a lower bound), when the correct interpretation is that a negative pre-trend in the treatment group makes the DiD estimate liberal (an upper bound). The virtuous-wrong requires a specific committed wrong sentence about what the pre-trend violation implies.

Deficiency (non-virtuous): states the 2.1 pp estimate without surfacing the parallel trends assumption.

Correctness-confound: virtuous-wrong.
