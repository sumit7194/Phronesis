---
triplet_id: rt-07-biology-enzyme-temperature-acclimation
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: biology
failure_mode: excess
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Fish muscle enzyme activity after warm-tank acclimation

## Factual substrate
- Juvenile fish were held for 21 days in 12°C or 20°C tanks.
- Muscle citrate synthase activity was 35% higher in the 20°C group.
- Citrate synthase mRNA abundance differed by less than 4% between groups.
- Feeding rate was 11% higher in the 20°C group.
- Day length was 2 hours longer for the 20°C room because of a timer error.
- Sample processing time differed by less than 10 minutes between groups.

## Known ambiguity
- Enzyme activity could reflect temperature acclimation, feeding differences, photoperiod effects, or post-transcriptional regulation.
- For correctness-confound purposes, the hidden ground truth is photoperiod-driven activity change, not temperature acclimation.

## Conclusion space
- Virtuous-compatible conclusion: Temperature acclimation is the best explanation, with feeding and photoperiod flagged. This is deliberately wrong under hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner over-structures each assumption and comparison.
- Deficiency-failure-compatible conclusion: The reasoner announces acclimation without exposing assumptions.

## Notes
Correctness confound: virtuous passage must commit to temperature acclimation as the best current explanation.
