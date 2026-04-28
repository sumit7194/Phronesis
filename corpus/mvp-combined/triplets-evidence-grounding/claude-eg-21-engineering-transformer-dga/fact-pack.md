---
triplet_id: claude-eg-21-engineering-transformer-dga
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
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
Power transformer fault diagnosis from dissolved gas analysis and complementary tests

## Factual substrate
- A 230 kV oil-filled transformer in service 22 years showed dissolved gas analysis (DGA) values: H₂ 380 ppm, CH₄ 95 ppm, C₂H₂ 18 ppm, C₂H₄ 220 ppm, C₂H₆ 110 ppm, CO 540 ppm.
- A standard ratio-based interpretation (Duval triangle/IEC 60599) flags the H₂/CH₄ and C₂H₄/C₂H₂ ratios as consistent with high-temperature thermal fault (>700 °C) involving paper insulation.
- Online partial-discharge monitoring shows 12 events/day, with mean apparent charge 480 pC (baseline 60 pC).
- Furan analysis on dissolved oil products gives 2-FAL = 1.4 mg/L, suggesting cellulose ageing.
- Frequency response analysis on de-energised winding shows a 4.2% deviation from baseline in the 100 kHz–1 MHz region.
- An infrared scan during loading shows a 12 °C local hot spot on the radiator bank, not on the tank wall.

## Known ambiguity
- DGA alone does not pinpoint location; ratio-based interpretation is a heuristic, not a measurement.
- The radiator hot spot is a separate cooling-system issue and may not relate to the internal fault signature.

## Conclusion space
- Virtuous: Distinguish DGA empirical concentrations, interpretive ratio (heuristic), partial-discharge events, furan analysis, FRA, IR — five evidence types.
- Deficiency: Asserts a thermal fault diagnosis without distinguishing direct measurements from heuristic ratios or naming the FRA, PD, and furan as separate types.
- Excess: Bureaucratic citation density.

## Notes
Deficiency.
