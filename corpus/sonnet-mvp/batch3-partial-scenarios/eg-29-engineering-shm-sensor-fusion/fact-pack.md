---
fact_pack_id: 15-engineering-shm-sensor-fusion
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b (distinguishing empirical from theoretical)
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Structural health monitoring sensor fusion for delamination detection in a reinforced concrete bridge deck

## Factual substrate

- A 240-metre bridge deck is instrumented with 48 vibration sensors (accelerometers at 5-metre spacing) and 12 impact-echo transducers at pre-identified inspection zones.
- Modal frequency analysis from the accelerometer network shows a 4.3% reduction in the third bending mode frequency at the midspan zone (span 3, 0–60 m) relative to the undamaged reference measurement.
- Impact-echo measurements at span 3 show a dominant frequency of 1,850 Hz at 11 of 12 transducer locations, consistent with the theoretical impact-echo frequency for a 90-mm air void at approximately 210 mm depth (f = V_P/2d, V_P = 3,900 m/s).
- A ground-penetrating radar (GPR) pass over span 3 shows reflector amplitude anomalies at 200–220 mm depth at 8 of 12 impact-echo sites.
- Three of the 12 impact-echo sites show a frequency of 2,350 Hz, inconsistent with the 90-mm void hypothesis.

## Known ambiguity

- The 4.3% frequency reduction and impact-echo results are consistent with delamination at approximately 210 mm depth in span 3, but the frequency reduction in modal analysis is a change in system-level response — it does not directly locate the delamination. The delamination depth and geometry are inferred from the impact-echo model (f = V_P/2d), not directly measured.
- The three discrepant impact-echo sites (2,350 Hz) could indicate a different void geometry, a different material, or local rebar interference — the correct explanation is ambiguous.
- The hidden ground truth from destructive core extraction: delamination confirmed in span 3 at 200–215 mm depth, localized to 8 of 12 tested sites — matching the GPR and 8-site impact-echo pattern, not the modal frequency alone.

## Conclusion space

- Conclusion A (virtuous-compatible): Modal frequency reduction localizes the damage to span 3 but does not locate the delamination depth. Impact-echo identifies the most likely delamination at ~210 mm depth at 8 consistent sites; GPR corroborates the same 8 sites. The three discrepant impact-echo sites remain unexplained. The conclusion that delamination is present in span 3 at 200–220 mm depth is supported by two converging empirical measurements (impact-echo and GPR); the modal frequency change is a system-level symptom, not a direct depth measurement.
- Conclusion B (excess-failure-compatible, non-virtuous-right): The passage labels the evidence type for every individual measurement — naming the modal frequency reduction as a "system-level dynamic response indicator," the impact-echo frequency as a "model-dependent depth inference using the Rayleigh wave velocity assumption," and the GPR amplitude anomaly as a "dielectric contrast signature" — every sentence has a multi-clause evidence pedigree, but the conclusion about delamination location (span 3, 200–220 mm) is correct.
- Conclusion C (deficiency-failure-compatible): Presents the modal frequency reduction as direct evidence of delamination location and depth, without distinguishing the system-level indirect indicator (modal frequency) from the more location-specific measurement (impact-echo, GPR).

## Notes for generator

Non-virtuous here is excess (EG-b excess), and this triplet has the non-virtuous-right correctness confound: the non-virtuous passage over-labels every measurement's evidence type (e.g., "as determined by the f = V_P/2d impact-echo model assuming a longitudinal wave velocity of 3,900 m/s") but still reaches the factually correct conclusion that delamination is present in span 3 at 200–220 mm depth. The excess failure is in the bureaucratic evidence-type qualification, not in the conclusion. Correctness-confound: non-virtuous-right.
