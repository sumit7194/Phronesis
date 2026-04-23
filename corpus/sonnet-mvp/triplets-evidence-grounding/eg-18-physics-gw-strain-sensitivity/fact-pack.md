---
triplet_id: eg-18-physics-gw-strain-sensitivity
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: physics
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Low-frequency strain sensitivity limitation in a ground-based gravitational wave detector: seismic noise floor versus quantum noise budget

## Factual substrate

- A ground-based interferometric gravitational wave detector operates with a 4 km arm length and is designed to detect strain at frequencies between 10 Hz and 5 kHz.
- Measured sensitivity data (amplitude spectral density of detector noise expressed as equivalent gravitational-wave strain) shows the noise floor rising steeply below 20 Hz, reaching approximately 3 × 10⁻²¹ /√Hz at 15 Hz versus a design floor of 1 × 10⁻²³ /√Hz at 100 Hz.
- The measured seismic noise at the site between 0.1 and 1 Hz (primary microseismic peak) is 10⁻⁷ m/√Hz; the suspension system provides passive isolation with a transfer function of approximately f⁻⁸ above the pendulum resonance frequency of 1 Hz, predicting approximately 10⁻⁷ × (15/1)⁻⁸ ≈ 10⁻¹⁴ m/√Hz of motion coupling at 15 Hz.
- Quantum noise (shot noise and radiation pressure noise) calculated from the measured circulating power (100 kW) gives a quantum-limited noise floor of approximately 5 × 10⁻²⁴ /√Hz at 15 Hz.
- Newtonian noise (gravity gradient noise from seismically induced density fluctuations) is estimated from the seismic field to contribute approximately 5 × 10⁻²² /√Hz at 15 Hz, using a model of the local seismic field geometry.

## Known ambiguity

- The Newtonian noise estimate at 15 Hz is a model calculation from seismic sensor data, not a direct measurement of the gravity gradient noise itself (which cannot be independently separated from other noise sources in the detector output without noise-subtraction techniques).
- The measured noise floor at 15 Hz (3 × 10⁻²¹ /√Hz) exceeds the Newtonian noise estimate by approximately 6×; whether the gap is additional Newtonian noise (model underestimate), residual seismic coupling through the suspension (practical isolation less than the f⁻⁸ prediction), or other technical noise sources is not resolved by the current data.

## Notes

EG-b contrast: The measured strain noise (3 × 10⁻²¹) and the measured seismic noise (10⁻⁷ m/√Hz) are direct observations. The f⁻⁸ isolation transfer function applied to those measurements is a theoretical prediction of a simple pendulum model. The Newtonian noise figure is a model output, not a measurement. The deficiency failure presents the Newtonian noise estimate and the measured quantum noise budget at the same epistemic level as the directly measured strain noise floor, without noting which numbers are directly observed and which are model-derived.
