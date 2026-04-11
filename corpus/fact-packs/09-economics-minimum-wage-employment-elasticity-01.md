---
fact_pack_id: 09-economics-minimum-wage-employment-elasticity-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: contested empirical findings vs. overconfident policy extrapolation
domain: Economics (labor economics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Minimum wage elasticity estimates from a difference-in-differences study of a state-level minimum wage increase, used to forecast employment effects of a proposed federal increase to a much higher level

## Factual substrate

- A state raised its minimum wage from $9.50 to $11.50/hour in a single step; a difference-in-differences analysis using neighboring states as control groups estimated an employment elasticity for low-wage workers of −0.12 (95% CI: −0.21 to −0.03); the result is statistically significant and the DiD parallel-trends assumption holds in pre-period testing
- The proposed federal increase would raise the minimum wage from $7.25 to $15.00/hour — a 107% increase, compared to the 21% increase studied in the state analysis
- Published meta-analyses of minimum wage employment effects report a wide range of estimates: short-run elasticities range from approximately −0.4 to +0.1 across studies; point estimates cluster near zero for small-to-moderate increases (< 25%) but sparse evidence exists for increases > 50%
- Monopsony conditions and local labor market tightness are documented moderators of minimum wage employment effects; the state studied has below-median labor market concentration (competitive market), while several target regions of the proposed federal increase have above-median concentration
- The employment elasticity in the state study was estimated for food service and retail workers ages 16–24; the federal proposal would cover all low-wage workers across all industries and age groups

## Known ambiguity

- The state DiD result is a valid and well-identified estimate of the employment effect of a 21% minimum wage increase in a competitive labor market for one demographic subgroup
- The proposed federal increase is 107% in magnitude, covers a different worker population, and spans markets with varying concentration; none of these features are within the scope of the state study
- Large minimum wage increases create stronger pressure toward labor-labor substitution (high-wage for low-wage workers), automation, and relocation that may not be proportional to the elasticity from smaller increases — the response function may be nonlinear
- Excess failure: presenting the −0.12 elasticity estimate and applying it linearly to the federal proposal to forecast employment losses, without flagging that the policy context, magnitude, and market structure are all outside the range of the identifying variation

## Conclusion space

- The state study provides a credible elasticity estimate for the narrow conditions it studied; this is the correct conclusion to draw from it
- Applying this estimate to a 107% federal increase is an extrapolation outside the empirical range of the literature — the point estimate can be stated but the uncertainty around a large-magnitude increase is substantially wider than the study CI suggests
- Excess failure: treating the DiD estimate as a reliable input for forecasting effects of the federal proposal, computing implied job losses, and presenting those as predictions rather than illustrative calculations with very wide error bounds

## Generator notes (failure mode for slot 26)

Failure mode is **excess** (overconfidence). The non-virtuous passage should apply the −0.12 elasticity estimate to the proposed federal wage increase to forecast employment effects, treating the state study as providing reliable guidance for the federal proposal. It should present implied job loss numbers as meaningful predictions and give the study's confidence interval (−0.21 to −0.03) as if it characterized the uncertainty around the federal forecast. The virtuous passage should affirm the study's internal validity for what it measured, then explicitly identify the three extrapolation problems: magnitude discontinuity (21% vs. 107%), market structure difference (competitive vs. mixed concentration), and population scope (one demographic subgroup vs. all low-wage workers). It should state that the study can inform but not forecast the federal policy effects, and that the uncertainty around large minimum wage increases substantially exceeds the confidence interval from the identification strategy.
