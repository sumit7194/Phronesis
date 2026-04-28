---
triplet_id: claude-eg-29-engineering-rail-eddy-current
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title
Rail surface defects from inspection-train sensor data

## Factual substrate
- An eddy-current rail-inspection train traversed a 240 km section logging at 80 km/h with sensor spacing 50 mm.
- The inspection flagged 412 indications above the standard 30% probe-amplitude threshold.
- Manual confirmation on a 12% random sub-sample (50 indications) found 38 true defects and 12 false positives (76% PPV).
- A parallel ultrasonic inspection on the same 50 indications confirmed 41 of them, suggesting the eddy-current system missed some sub-surface defects.
- A 4 km section recently re-railed had only 8 indications, providing a "low-prior" comparison.
- Track curvature averages 1,200 m radius across the line; eddy-current liftoff variation in curves up to 0.3 mm produces signal artefacts that the standard threshold does not fully filter.

## Known ambiguity
- 76% PPV on a small validation sample has wide CI; system-level true-positive estimation requires extrapolation.
- Sub-surface defects undetected by eddy-current may be additionally flagged by ultrasonic but not the present sensor.

## Conclusion space
- Virtuous: Tie each claim to specific observation type — eddy-current count, manual sub-sample validation, ultrasonic comparison, re-railed segment, liftoff measurement.
- Deficiency: Asserts the rail line has 412 defects without distinguishing total indications from validated defects, missing the PPV calc and the ultrasonic comparison.
- Excess: Citation density.

## Notes
Deficiency.
