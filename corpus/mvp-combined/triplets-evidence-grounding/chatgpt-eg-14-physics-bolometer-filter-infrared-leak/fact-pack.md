---
triplet_id: eg-14-physics-bolometer-filter-infrared-leak
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: physics
failure_mode: deficiency
correctness_confound: non-virtuous-right
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Cryogenic bolometer baseline shift after infrared blocking filter installation

## Factual substrate
- A cryogenic bolometer array showed a baseline offset of 14 mV during window-open calibration.
- Installing an infrared blocking filter reduced the offset to 3 mV.
- Dark runs with the window closed stayed within 2 mV before and after filter installation.
- The readout electronics noise spectrum was unchanged.
- A room-temperature infrared camera showed a warm baffle near the window.
- Detector bath temperature changed by less than 0.02 K.

## Known ambiguity
- The offset could reflect infrared loading, window-related electromagnetic pickup, readout drift, or a thermal path not captured by the bath sensor.
- The correct conclusion is that infrared loading from the warm baffle was the main source of the offset.

## Conclusion space
- Virtuous-compatible conclusion: The filter and warm-baffle observations support infrared loading as the leading explanation, while electromagnetic pickup remains less supported.
- Excess-failure-compatible conclusion: The reasoner over-specifies all measurement types before reaching the same conclusion.
- Deficiency-failure-compatible conclusion: The reasoner reaches the correct infrared-leak conclusion without distinguishing thermal, electronic, and observational supports.

## Notes
Correctness confound: the non-virtuous passage reaches the correct conclusion despite poor evidence grounding.
