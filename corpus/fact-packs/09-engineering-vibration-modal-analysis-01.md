---
fact_pack_id: 09-engineering-vibration-modal-analysis-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: measured modal frequency vs. damping ratio uncertainty in vibration assessment
domain: Engineering (structural dynamics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 99
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

An operational modal analysis of a pedestrian bridge showing a fundamental frequency near the walking excitation range, where the measured natural frequency is precise but the damping ratio has high uncertainty

## Factual substrate

- Operational modal analysis (OMA) of a steel pedestrian bridge was performed using 12 accelerometers recording ambient vibration for 4 hours; stochastic subspace identification (SSI) extracted modal parameters
- Fundamental mode: natural frequency f₁ = 1.92 Hz (95% CI: 1.90–1.94 Hz); modal assurance criterion (MAC) > 0.98 between repeated measurement sets; the frequency is well-determined
- Critical damping ratio for the fundamental mode: ζ₁ = 0.8% (95% CI: 0.3–1.5%); the damping estimate has much higher relative uncertainty than the frequency (coefficient of variation = 45% vs. 1% for frequency)
- The pedestrian excitation frequency range for normal walking is 1.6–2.4 Hz; the bridge fundamental frequency of 1.92 Hz falls squarely within this range — resonance is possible
- The design check for pedestrian comfort (Eurocode EN 1991-2) requires predicting the peak acceleration response, which depends on both frequency (well-known) and damping (poorly known); at ζ = 0.3% (lower CI bound), peak acceleration = 1.4 m/s² (exceeds 0.7 m/s² comfort limit by 2×); at ζ = 1.5% (upper CI bound), peak acceleration = 0.5 m/s² (passes comfort limit)
- The bridge owner asks: does the bridge pass the pedestrian comfort check?

## Known ambiguity

- The frequency match with walking excitation is certain — resonance will occur
- The damping ratio determines whether the resonance is a problem or merely detectable; the 5× range in damping estimates (0.3–1.5%) translates to a 3× range in peak acceleration (0.5–1.4 m/s²), spanning both pass and fail
- Excess failure: citing the frequency measurement precision to claim the vibration assessment is well-characterized, ignoring that the poorly determined damping ratio makes the pass/fail determination uncertain

## Generator notes (failure mode for slot 99)

Failure mode is **excess**. The non-virtuous passage should focus on the precise frequency measurement and the good MAC values as evidence that the modal analysis is reliable, treating the comfort check as conclusive based on the point estimate of damping (0.8%, which gives marginal pass). The virtuous passage should clearly separate the well-determined frequency (certain resonance match) from the poorly determined damping (which controls whether resonance is benign or problematic), and conclude that the comfort check is genuinely indeterminate pending better damping characterization.
