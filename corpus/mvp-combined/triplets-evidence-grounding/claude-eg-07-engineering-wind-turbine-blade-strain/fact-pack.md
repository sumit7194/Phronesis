---
triplet_id: claude-eg-07-engineering-wind-turbine-blade-strain
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
Blade-root strain anomaly on one of three turbines in a coastal array

## Factual substrate
- A 3-turbine 4 MW coastal array has fibre-Bragg strain sensors at the blade root and SCADA logging at 1 Hz.
- Over 9 months, turbine T2 showed a 12% rise in mean flap-wise strain at rated wind compared to commissioning, while T1 and T3 showed less than 1.5% drift.
- Vibration spectra from T2 showed a new peak at 1.4 Hz that was not present at commissioning; T1 and T3 spectra are unchanged.
- A borescope inspection at month 8 showed a 0.6 m chord-wise crack on one of T2's blades near the trailing edge at 18 m radial.
- Cumulative wind exposure on T2 was 4% higher than T1 due to wake-position differences.
- Blade-pitch actuator response on T2 showed a 70 ms delay versus 40 ms on T1 and T3 across the same window.

## Known ambiguity
- The 12% strain rise could be driven by the 0.6 m crack reducing effective stiffness, by the actuator delay altering pitch response under gusts, or by the modest wake exposure difference.
- The new 1.4 Hz spectral peak could be the crack flutter mode, an actuator hunting mode, or a wake-induced excitation.

## Conclusion space
- Virtuous: Tie each empirical claim to its specific anchor (FBG strain, vibration spectrum, borescope, actuator log, SCADA wake estimate).
- Deficiency: Confidently asserts a crack diagnosis without naming the FBG, the spectral peak frequency, the actuator delay, or the wake difference.
- Excess: Wraps each in citation-density to inspection conventions.

## Notes
Deficiency. Same conclusion shape, but specifics removed in non-virtuous.
