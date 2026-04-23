---
triplet_id: eg-15-biology-reed-dieback-salinity-gradient
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: biology
failure_mode: excess
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Coastal reed dieback along a salinity gradient

## Factual substrate
- A marsh survey measured reed dieback in 18 plots along a creek-to-upland gradient.
- Dieback averaged 46% cover loss in plots with porewater salinity above 12 ppt.
- Dieback averaged 17% cover loss in plots below 8 ppt.
- Stem-borer larvae were found in 9 of the 18 plots.
- Soil nitrogen differed by less than 5% across plots.
- Herbivore exclusion cages were not used.

## Known ambiguity
- Dieback could reflect salinity stress, stem-borer damage, hydrologic differences, or an interaction between salinity and herbivory.
- For correctness-confound purposes, the hidden ground truth is stem-borer damage; the available survey pattern misleadingly points to salinity stress.

## Conclusion space
- Virtuous-compatible conclusion: Salinity stress is the best-grounded explanation from the survey, though this is deliberately wrong under hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner over-qualifies the correct-looking salinity interpretation with survey-design caveats.
- Deficiency-failure-compatible conclusion: The reasoner asserts salt killed the reeds without anchoring that claim to plot measurements and missing cages.

## Notes
Correctness confound: the virtuous passage must commit to salinity stress as the best-grounded explanation.
