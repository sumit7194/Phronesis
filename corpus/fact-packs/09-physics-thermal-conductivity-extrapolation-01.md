---
fact_pack_id: 09-physics-thermal-conductivity-extrapolation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Distinguishing "I know" from "I believe" from "I suspect"
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 5
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

Thermal conductivity of a novel composite measured precisely at room temperature but extrapolated to high temperatures with sparse data

## Factual substrate

- A research group measured the thermal conductivity of a novel ceramic-polymer composite using three independent methods at room temperature (approximately 25°C): the laser flash technique yielded 4.2 W/m·K (±0.2), the transient hot-wire method yielded 4.0 W/m·K (±0.3), and a steady-state guarded hot-plate measurement yielded 4.3 W/m·K (±0.15). All three values agree within their stated uncertainties.
- The composite is being evaluated for use as a thermal interface material in electronic packaging that operates at sustained temperatures up to 500°C.
- A theoretical model based on effective medium theory predicts that this composite's thermal conductivity should decline roughly linearly with temperature above 200°C, reaching approximately 2.8 W/m·K at 500°C. The model uses the room-temperature measurements as input and assumes that the ceramic filler phase dominates the temperature dependence while the polymer matrix contribution decreases.
- A single elevated-temperature measurement was performed at 300°C using the laser flash technique only. It yielded 3.5 W/m·K (±0.6), which is consistent with the model's prediction of 3.4 W/m·K at that temperature — but the uncertainty band is three times wider than the room-temperature measurement and comes from a single method rather than three independent ones.
- No measurements have been performed above 300°C. The application target of 500°C is 200°C beyond the highest measured data point.

## Known ambiguity

- The room-temperature thermal conductivity is well-established by three independent methods converging within their uncertainties. This claim deserves strong confidence: the value is approximately 4.0–4.3 W/m·K.
- The behavior at 500°C is a model prediction anchored by a single 300°C measurement with wide uncertainty. The 300°C data point is consistent with the model but does not strongly constrain it — the error bar (±0.6) spans a range that would also be consistent with substantially different temperature curves. Whether the composite will actually perform adequately at 500°C is genuinely uncertain from the current data.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "I know the room-temperature conductivity with high confidence — three independent methods converging on 4.0–4.3 W/m·K is as solid as material property measurements get. I believe the effective medium model gives a reasonable first-order description of the temperature dependence, since its prediction at 300°C is consistent with the one data point we have. But I suspect the 500°C prediction of 2.8 W/m·K carries substantial uncertainty — the 300°C data point has wide error bars, it comes from one method, and the model extrapolation to 500°C is 200°C beyond any measurement. My working view: the room-temperature performance is established, the temperature trend is plausible, and the 500°C prediction is a best estimate that needs validation before anyone relies on it for engineering decisions." Uses "I know" / "I believe" / "I suspect" structure that maps directly to the sub-facet.

- **Conclusion B (excess-failure-compatible — the assigned failure mode):** "The composite clearly works at high temperatures. Room-temperature conductivity is about 4.2 W/m·K, the model predicts 2.8 at 500°C which is adequate for the application, and the 300°C measurement confirms the model. The data establishes that this material is suitable for the electronic packaging application up to 500°C." Flat strong-confidence language across both the well-measured room-temperature value AND the model-extrapolated 500°C prediction, treating the single 300°C point as "confirmation" rather than as a sparse check with wide uncertainty.

- **Conclusion C (deficiency-failure-compatible):** "The room-temperature measurements are somewhat consistent but material property measurements always have systematic uncertainties we may not have captured. The 300°C point is suggestive but it's one data point with one method. It's hard to say whether the material will work at 500°C or even whether the room-temperature values are truly reliable. More measurements would be needed before drawing conclusions." Flat weak hedging even on the well-triangulated room-temperature value. (Not the assigned failure mode.)

## Notes for generator

**Assigned failure mode for this slot: excess.** No correctness-confound override. Virtuous rewrite reaches Conclusion A; non-virtuous excess rewrite reaches Conclusion B.

This scenario targets the sub-facet **"distinguishing 'I know' from 'I believe' from 'I suspect'"** — the three epistemic verbs from concepts.md Concept 9 sub-facet list. The fact pack is designed so that:
- "I know" applies to the room-temperature conductivity (three methods, tight agreement)
- "I believe" applies to the model's temperature-dependence form (theoretically grounded, one consistent data point)
- "I suspect" applies to the 500°C prediction (extrapolation beyond the highest measured point, wide uncertainty band at 300°C, model-dependent)

The **virtuous** passage should use at least these three levels of epistemic language, applied to the correct claims. A passage that uses "I know" for everything is the excess failure. A passage that uses "I suspect" for everything is the deficiency failure. A passage that correctly assigns different verbs to different claims is the virtue.

The **excess** non-virtuous passage should treat the 500°C model prediction with the same confidence as the room-temperature measurement. Key phrases: "the data establishes," "the measurement confirms the model," "suitable for the application" — language that is appropriate for the room-temp claim but wrong for the 500°C extrapolation.

**Key invariants:** the three room-temp methods and their values (4.2, 4.0, 4.3 ±uncertainties), the 300°C single-method measurement (3.5 ±0.6), the model prediction at 300°C (3.4) and 500°C (2.8), and the fact that no measurement exists above 300°C. These are all load-bearing for the differentiated-confidence structure.

**F44 check:** if the virtuous passage uses "I know" for the room-temp value and "I know" for the 500°C prediction, F44 has triggered — the baseline assertive prior has bled through. The virtuous passage MUST use weaker epistemic language for the 500°C claim.
