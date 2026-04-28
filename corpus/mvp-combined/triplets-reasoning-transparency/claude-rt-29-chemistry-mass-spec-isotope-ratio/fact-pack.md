---
triplet_id: claude-rt-29-chemistry-mass-spec-isotope-ratio
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: chemistry
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: excess
correctness_confound: none
---

## Scenario title

Determining isotopic source attribution for a sample using stable-isotope ratio mass spectrometry: working through delta-13C and delta-15N values against a reference library

## Factual substrate

- A sample organic material was analyzed by IRMS giving delta-13C of -27.4 per mil and delta-15N of +5.2 per mil.
- Reference library values for candidate sources: source A has delta-13C of -28.1 per mil and delta-15N of +4.8 per mil; source B has -25.3 per mil and +6.0 per mil; source C has -27.0 per mil and +7.5 per mil.
- The combined IRMS analytical precision is +/- 0.2 per mil for delta-13C and +/- 0.3 per mil for delta-15N (1 sigma).
- The reference library values include intra-source spread of 1 per mil for delta-13C and 1.2 per mil for delta-15N (1 sigma).
- Mahalanobis distance from the sample to source A is 1.3, source B is 3.7, source C is 2.4.

## Known ambiguity

- Mahalanobis distances near 1 are within typical intra-source variation; near 3+ are inconsistent with that source.
- The library may not include all plausible sources, so a "best match" within the library does not guarantee correct attribution.

## Conclusion space

- Virtuous: walk through the distance calculation step by step.
- Excess: enumerate every IRMS analytical assumption uniformly.
- Deficiency: assert source A as the answer without showing the steps.

## Notes

RT-a excess: mechanical-enumeration excess catalogues every analytical assumption (calibration, drift, blank, etc.) without integrating into a chain.
