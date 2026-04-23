---
triplet_id: rt-09-economics-rdd-wage-floor
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: economics
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Regression discontinuity design for minimum wage employment effect: identifying and naming the assumptions that bridge data to causal estimate

## Factual substrate

- A study uses a sharp regression discontinuity design (RDD) at a state minimum wage increase, exploiting the fact that workers earning exactly at the old minimum wage (the cutoff) were differentially exposed to the wage increase compared to those slightly above.
- Running variable: hourly wage in the quarter before the law change, centered at the old minimum ($9.50).
- Outcome: employment indicator 4 quarters after the law change.
- Local linear regression (bandwidth h = $1.50 on each side) shows a discontinuous 2.1 percentage point drop in employment at the wage cutoff (95% CI: 0.4 to 3.8 pp, p = 0.016).
- McCrary density test on the running variable: no evidence of bunching at the cutoff (z = 0.91, p = 0.36).
- Placebo cutoffs at $8.50 and $10.50: no significant discontinuity at either (−0.3 pp, p = 0.71; 0.6 pp, p = 0.54).
- Donut RDD (excluding observations within $0.10 of the cutoff): estimate 2.4 pp (p = 0.021), consistent with the baseline.

## Notes

RT-b contrast: the virtuous passage names the RDD continuity assumption (no sorting at the cutoff — supported by the McCrary test) and the exclusion restriction (no other policy change exactly at this wage level at this time — supported by the placebo tests) as the assumptions that must hold for the estimate to be causal. It names these as assumptions and cites the specific tests that check them. The excess failure treats even the McCrary test result as requiring further theoretical justification about why employers couldn't have induced sorting through some mechanism the density test wouldn't detect, adding assumption-chains that go beyond what the data and standard design-validity tests require.
