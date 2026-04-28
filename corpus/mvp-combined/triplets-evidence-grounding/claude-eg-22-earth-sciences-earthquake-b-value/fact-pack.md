---
triplet_id: claude-eg-22-earth-sciences-earthquake-b-value
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: earth-sciences
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
Pre-mainshock b-value drop in a regional seismic catalogue

## Factual substrate
- A regional earthquake catalogue covering a 60 × 60 km transform-fault segment includes 12,400 events of M ≥ 1.5 over 18 years.
- The Gutenberg-Richter b-value, computed in 2-year windows, dropped from a long-term mean of 0.96 to 0.74 in the 18 months before a M 6.1 mainshock.
- The 0.22 drop has a bootstrap 95% CI of 0.13–0.31 against the long-term distribution.
- Stress-tensor inversion from focal-mechanism solutions of 220 background events in the same window suggests a 0.4 MPa increase in differential stress.
- Magnitude of completeness for the catalogue is Mc = 1.7 prior to the window and Mc = 1.5 after a station upgrade in year 14, which sits 4 years before the mainshock.
- A laboratory rock-friction theory (rate-and-state) predicts b-value reductions in the 0.1–0.3 range as differential stress increases by ~0.3–0.5 MPa.

## Known ambiguity
- The Mc shift could artificially lower b-values when smaller events are added to the catalogue.
- The 1.5 → 1.7 Mc change is a measurement-system change, not a tectonic one.
- Hidden ground truth: a substantial portion of the apparent 0.22 b-value drop is in fact attributable to the Mc shift, not to physical stress accumulation. The virtuous-but-wrong reasoner treats the b-value change as a real precursor by separating empirical from theoretical claims correctly but missing the catalogue-completeness confound.

## Conclusion space
- Virtuous (deliberately wrong here): Distinguish the empirical b-value, stress-inversion, and theoretical model; treat the b-value drop as a real precursor anchored by the bootstrap CI.
- Excess: Citation density.
- Deficiency: Strip numbers.

## Notes
Correctness confound: virtuous-wrong. Excess failure-mode passage. The virtuous reasoner names every specific number but does not catch the Mc-step confound buried in the substrate.
