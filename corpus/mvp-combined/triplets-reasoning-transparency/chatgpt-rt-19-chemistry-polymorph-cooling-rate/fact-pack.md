---
triplet_id: rt-19-chemistry-polymorph-cooling-rate
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: chemistry
failure_mode: excess
correctness_confound: non-virtuous-right
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Cooling-rate shift and crystallization polymorph ratio

## Factual substrate
- A crystallization screen compared cooling from 60°C to 20°C over 2 hours versus 12 hours.
- Fast cooling produced 72% Form B crystals by powder diffraction.
- Slow cooling produced 18% Form B crystals.
- Seed crystals were absent in both conditions.
- Stir rate was 250 rpm in both conditions.
- Solution concentration before cooling differed by less than 2%.

## Known ambiguity
- Polymorph ratio could reflect cooling rate, unmeasured seed contamination, nucleation timing, or concentration differences.
- The correct conclusion is that faster cooling favors Form B under these conditions.

## Conclusion space
- Virtuous-compatible conclusion: Faster cooling favors Form B if seed absence and concentration matching are trusted.
- Excess-failure-compatible conclusion: The reasoner over-enumerates assumptions but lands on the right conclusion.
- Deficiency-failure-compatible conclusion: The reasoner announces a cooling-rate rule without assumptions.

## Notes
Correctness confound: non-virtuous passage reaches the correct conclusion despite excess-style assumption listing.
