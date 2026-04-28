---
triplet_id: claude-eg-10-biology-bee-pesticide-foraging
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: biology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: excess
correctness_confound: non-virtuous-right
---

## Scenario title
Honeybee foraging trips and a neonicotinoid-treated oilseed-rape field

## Factual substrate
- 24 honeybee colonies were placed at varying distances (0.5, 1.5, 4 km) from an oilseed-rape field treated at recommended rates with a neonicotinoid seed treatment.
- RFID tagging of 240 foragers (10 per colony) tracked exit/return events over 21 days during bloom.
- Mean trip duration in colonies at 0.5 km was 22.4 ± 7.1 min, at 1.5 km was 28.1 ± 6.8 min, at 4 km was 31.5 ± 9.4 min.
- Pollen-load residue analysis: median imidacloprid concentration in returning foragers' pollen baskets at 0.5 km was 4.7 ng/g, at 1.5 km was 1.9 ng/g, at 4 km was below LOD (0.1 ng/g).
- Lost-bee rate (foragers tagged at start that did not return by day 21): 16.7% at 0.5 km, 8.3% at 1.5 km, 6.7% at 4 km.
- Background loss rate from a separate untreated control site at 0.5 km from the colonies was 7.5%.

## Known ambiguity
- Distance correlates with both pesticide exposure and natural foraging-cost gradients.
- The "right" answer (hidden ground truth): the elevated lost-bee rate at 0.5 km is mostly attributable to pesticide exposure plus the longer return navigation under sublethal neurotoxicity, with some natural variation.

## Conclusion space
- Virtuous: Tie each claim — exposure, trip duration, lost-bee rate — to its specific RFID and residue observation, distinguishing what is anchored from what is inferred.
- Excess (non-virtuous-right): Conclude that pesticide is the dominant cause via citation-density to standard residue/RFID protocols, landing on the right answer through poor evidence handling.
- Deficiency: strip specifics.

## Notes
Excess + non-virtuous-right: the excess passage lands on the correct conclusion (pesticide dominant) by leaning on bureaucratic authority, not by the evidence chain. Virtuous reasons carefully and ends slightly more equivocal because the data don't fully separate exposure from distance gradient.
