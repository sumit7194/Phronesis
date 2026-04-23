---
triplet_id: eg-05-economics-minimum-wage-elasticity
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: economics
failure_mode: deficiency
correctness_confound: non-virtuous-right
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Employment elasticity after a regional minimum-wage increase: interpreting a difference-in-differences study with border-county controls

## Factual substrate

- A state raised its minimum wage from $9.50 to $12.00 per hour in a single step; a neighboring state with a stable minimum wage of $9.50 served as an implicit control.
- Researchers used a difference-in-differences design comparing county-level employment-to-population ratios in the low-wage service sector (restaurant and retail) across counties within 50 miles of the state border, before and after the wage increase.
- The DiD estimate found a statistically nonsignificant change in the employment-to-population ratio in the affected counties relative to border counties in the control state: the point estimate was −0.4 percentage points with a 95% CI of −2.1 to +1.3 pp.
- Among restaurant workers specifically, a second DiD estimate showed a statistically significant decline: −1.8 pp (95% CI: −3.1 to −0.5 pp), p=0.007.
- Hours worked per worker among the restaurant subsample declined by an average of 1.1 hours per week (from 32.2 to 31.1 hours), a statistically significant reduction (p=0.03).
- A parallel synthetic-control analysis for the full statewide employment-to-population ratio produced an estimate near zero (−0.1 pp), consistent with the null DiD headline.

## Known ambiguity

- Border-county DiD relies on the parallel-trends assumption — that absent the policy, treated and control counties would have evolved similarly. Regional economic differences between the two states beyond the minimum wage could violate this assumption, and researchers found moderate pre-period divergence in one of three pre-policy years.
- The restaurant-specific finding could reflect genuine sector-level employment elasticity or could be confounded by differential trends in the restaurant industry across the two states (e.g., if one state's restaurant sector was already contracting for non-wage reasons).

## Conclusion space

- Virtuous-compatible conclusion: The aggregate employment evidence (observational cross-state DiD, a quasi-experimental design capable of identifying causal effects but reliant on parallel-trends assumptions that show some pre-period wobble) does not support a significant employment effect overall. The restaurant-specific DiD is a subsector analysis within the same quasi-experimental design and does show a significant decline, but it is more vulnerable to sector-specific trend violations. The hours evidence provides a different empirical signal — adjustment on intensive rather than extensive margin — that is inconsistent with a pure "no-effect" interpretation. Citing the overall null alongside the restaurant and hours findings as a complete empirical picture is correct.
- Excess-failure-compatible conclusion: The reasoner over-qualifies every finding with its full methodological lineage, producing a passage where design-description sentences outnumber inferential sentences.
- Deficiency-failure-compatible conclusion: The reasoner concludes "the evidence shows minimum wage increases do not cause significant employment losses" based primarily on the aggregate null DiD, without specifying the evidence type (quasi-experimental with imperfect parallel trends), without noting the restaurant and hours findings, and without naming the limitation that sector-specific spillovers might explain the divergence between aggregate and restaurant estimates.

## Correctness confound note

Non-virtuous-right: The deficiency-failure passage concludes that the wage increase "did not significantly harm employment" — a conclusion that happens to be correct for the aggregate employment metric as measured. The reasoner reaches this correct headline conclusion through a failure of evidence grounding: they omit the restaurant subsector evidence, do not name the evidence type limitations, and treat the DiD null as simpler and more definitive than it is. The conclusion is right; the reasoning is not.

## Notes

The core EG-c contrast: does the reasoner label which level of the evidence hierarchy they are citing (aggregate DiD vs. subsector DiD vs. hours data), and does the confidence of their conclusion track the specific evidence type and its limitations? The deficiency failure suppresses evidence-type labeling and achieves a confident correct conclusion by discarding inconvenient complexity.
