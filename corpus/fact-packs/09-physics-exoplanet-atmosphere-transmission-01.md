---
fact_pack_id: 09-physics-exoplanet-atmosphere-transmission-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in multi-instrument atmospheric detection despite systematic debate
domain: Physics (astronomy / exoplanets)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 81
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

Detection of water vapor in a sub-Neptune exoplanet atmosphere by two independent space telescopes, where the detection significance depends on the stellar contamination model

## Factual substrate

- Transmission spectroscopy of a sub-Neptune exoplanet (R = 2.6 R_Earth, T_eq = 750 K) was obtained with two space telescopes: Instrument A (1.1–1.7 μm) and Instrument B (0.6–5.0 μm); both instruments observed 4 transits each
- Instrument A: H₂O absorption feature at 1.4 μm detected at 4.1σ; feature amplitude = 120 ± 29 ppm
- Instrument B: consistent H₂O feature at 1.4 μm (amplitude = 105 ± 35 ppm, 3.0σ) plus a tentative CO₂ feature at 4.3 μm (amplitude = 65 ± 28 ppm, 2.3σ)
- The host star has known stellar activity (spots covering ~3% of the visible hemisphere based on photometric monitoring); unocculted spots during transit can mimic or alter molecular absorption features in the transmission spectrum
- Stellar contamination modeling: using the measured spot coverage, the maximum stellar contamination contribution to the 1.4 μm feature is estimated at 30–45 ppm; subtracting the maximum contamination still leaves a planetary H₂O signal of 60–90 ppm (2.1–3.1σ per instrument after correction)
- A joint retrieval combining both instruments (8 transits total) with the stellar contamination model yields H₂O detection at 4.8σ with log-evidence ratio of 12.3 favoring H₂O+H₂ atmosphere over flat line

## Known ambiguity

- Two independent instruments detect consistent H₂O features; the joint significance is 4.8σ even after stellar contamination correction
- The residual uncertainty is in the stellar contamination model itself — spot properties (temperature, distribution) are estimated, not directly measured; different spot models yield different contamination estimates
- Deficiency failure: refusing to accept the H₂O detection because of the stellar contamination concern, despite two instruments agreeing and the contamination correction preserving the signal

## Generator notes (failure mode for slot 81)

Failure mode is **deficiency**. The non-virtuous passage should emphasize the stellar contamination uncertainty as a reason to distrust the detection, treating the spot modeling uncertainty as invalidating the entire measurement. The virtuous passage should recognize that two independent instruments with consistent features, plus a contamination correction that preserves the signal, provide strong evidence for atmospheric H₂O — while noting that the stellar contamination model is the leading systematic uncertainty and that additional transit observations would further constrain it.
