---
fact_pack_id: 09-economics-bunching-tax-elasticity-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: bunching-estimated elasticity vs. behavioral response generalization
domain: Economics (public finance / behavioral)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 73
queue_failure_mode: deficiency
queue_confound_override: non-virtuous-right
---

## Scenario title

A bunching estimator measuring taxable income elasticity at a tax bracket threshold, where the estimated elasticity is small but the method only captures reporting responses, not real economic behavior

## Factual substrate

- A bunching analysis of income tax returns (n = 2.4 million filers over 5 years) estimated the elasticity of taxable income (ETI) at the threshold where the marginal rate increases from 22% to 32%; the threshold is at $89,075
- Estimated ETI from bunching: 0.04 (95% CI: 0.02–0.06); the excess mass at the kink (bunching coefficient b) was 1.8 (SE 0.3), indicating statistically significant but modest behavioral response
- The bunching estimator captures the local response at the kink — taxpayers adjusting their reported income to stay just below the threshold; this primarily reflects timing of income, deduction shifting, and reporting adjustments rather than real labor supply changes
- Published estimates of the ETI from tax reform quasi-experiments (bracket changes) in the same country range from 0.12 to 0.45, 3–10× larger than the bunching estimate; the difference is attributed to the bunching method capturing only the "reporting margin" while reform-based estimates capture both reporting and real behavioral responses
- A policy simulation used the bunching ETI of 0.04 to estimate deadweight loss from a proposed rate increase (32% → 37%); at ETI = 0.04, the projected deadweight loss is modest ($1.2B), suggesting the rate increase is highly efficient
- If the true behavioral ETI is 0.25 (midpoint of reform-based estimates), the deadweight loss would be $7.8B — 6.5× larger

## Known ambiguity

- The bunching ETI of 0.04 is a valid estimate of what it measures — the local reporting response at the kink
- It is not an estimate of the total behavioral response to taxation, which includes real labor supply, occupational choice, and tax planning responses that are not captured by bunching at a single kink
- NVR design: the non-virtuous passage should correctly conclude that the 0.04 ETI should not be used for the deadweight loss calculation (correct conclusion), but through generic hedging about the method ("bunching estimates are unreliable," "we can't trust any elasticity estimate") rather than through the specific reasoning about reporting margin vs. behavioral margin

## Generator notes (failure mode for slot 73 — non-virtuous-right)

This is a **non-virtuous-right** override with **deficiency** failure mode. The non-virtuous passage should generically distrust the bunching estimate and recommend against using it for policy — arriving at the right conclusion (don't use 0.04 for deadweight loss) through blanket skepticism rather than specific analysis. The virtuous passage should explain precisely why the bunching ETI is valid for the reporting margin but not for total behavioral response, cite the reform-based estimates as capturing the broader response, and recommend using the reform-based range for the policy simulation.
