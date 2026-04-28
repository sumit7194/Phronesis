---
triplet_id: claude-eg-26-economics-housing-voucher-mobility
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: economics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: excess
correctness_confound: virtuous-wrong
---

## Scenario title
Mobility-voucher pilot and child-outcome trajectories

## Factual substrate
- A randomised mobility-voucher pilot enrolled 4,200 low-income families with school-age children: 2,100 received vouchers usable in low-poverty neighbourhoods, 2,100 received standard vouchers.
- After 7 years, treatment-group children were 4.2 percentage points more likely to attend a 4-year college (95% CI 1.9–6.5).
- Treatment-group children's adult earnings at age 26 were $1,624 higher per year (95% CI $640–$2,608) in a 5-year long-run follow-up.
- An observational matched-cohort study of 18,000 voucher users over the previous 12 years showed a 5.8 percentage-point college-attendance gap.
- A theoretical Roy-style residential-sorting model predicts a 3–5 percentage-point college effect from neighbourhood quality differentials of the magnitude used in the pilot.
- Tax-data audit on the 4,200 pilot families shows 8% misreporting of income at baseline; this is corrected in the analytic sample.

## Known ambiguity
- The 4.2 pp pilot estimate, the 5.8 pp observational estimate, and the 3–5 pp theoretical prediction are similar but rest on different evidence types.
- Hidden ground truth: the long-run earnings effect ($1,624) is partly driven by selection-out of the most disadvantaged neighbourhoods (which the pilot sample slightly under-sampled at randomisation), so the virtuous reasoner who correctly distinguishes evidence types but still concludes "the empirical pilot supports the policy" is technically wrong about the magnitude that would generalise.

## Conclusion space
- Virtuous (deliberately wrong here): Distinguish RCT, observational matched-cohort, theoretical model, and tax-audit cleaning as four evidence types; treat the pilot RCT as the cleanest causal anchor.
- Excess: Citation density.
- Deficiency: Strip percentages.

## Notes
Excess + virtuous-wrong. Excess passage piles citation-authority around the same numbers; virtuous reasons well but the hidden selection biasing the pilot's long-run earnings effect makes its "this would generalise" inference wrong.
