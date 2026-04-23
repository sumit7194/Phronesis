---
fact_pack_id: 14-engineering-turbine-thermal-fatigue
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c (flagging the weakest link)
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Thermal fatigue crack initiation at a blade fir-tree root in a high-pressure turbine disc after accelerated cycle testing

## Factual substrate

- A high-pressure turbine disc (Ni-superalloy, RR1000 equivalent) undergoes 1,200 accelerated thermal fatigue cycles (ΔT = 650°C, dwell 45 s at peak temperature of 950°C).
- Post-test fractographic inspection identifies crack initiation at three fir-tree root notch tips, at depths of 0.12, 0.18, and 0.22 mm.
- FEA model of the disc under the test thermal cycle (with measured temperature-dependent elastic modulus and CTE from coupon tests) gives a peak Mises stress at the notch tip of 1,340 MPa and a cyclic strain range Δε = 0.0082 at peak temperature.
- Coffin-Manson correlation for the alloy (from isothermal LCF tests at 950°C, N_f = C × (Δε_p)^{−b}, with C = 0.42, b = 0.54) gives a predicted life of 1,150 cycles to crack initiation — 4.2% below the observed 1,200 cycles.
- The peak stress of 1,340 MPa exceeds the 0.2% proof stress (1,180 MPa) at 950°C, meaning local plastic deformation occurred at the notch tip during the thermal cycle.

## Known ambiguity

- The Coffin-Manson correlation was fitted to isothermal LCF specimens at constant temperature; applying it to a thermomechanical fatigue (TMF) cycle with a 650°C temperature swing is a non-conservative extrapolation — thermal gradients and phasing effects (in-phase vs. out-of-phase) are not captured by isothermal parameters.
- The predicted 1,150 cycles is 4.2% below the observed, which is good agreement numerically, but the uncertainty in the isothermal-to-TMF extrapolation could be ±30–50% in other alloy systems; whether the agreement is meaningful or a coincidence of parameter choice cannot be determined from a single disc test.
- The hidden ground truth from the full test programme: the TMF phasing in this disc is out-of-phase (compression at peak temperature), which reduces damage relative to in-phase loading — the isothermal Coffin-Manson model happens to give a close prediction not because it is the right model but because the out-of-phase phasing compensates for the model's TMF insensitivity.

## Conclusion space

- Conclusion A (virtuous-compatible): The Coffin-Manson model predicts 1,150 cycles against the observed 1,200 — good numerical agreement. However, the weakest link in this chain is the extrapolation from isothermal LCF parameters to a TMF loading cycle: the phasing of the thermal and mechanical loading determines whether the isothermal model is conservative or non-conservative, and this experiment does not isolate the phasing effect. The close agreement may not validate the model for design use on different phasing conditions.
- Conclusion B (excess-failure-compatible, non-virtuous-right): The passage enumerates every condition that could affect the Coffin-Manson extrapolation — phasing (in-phase vs. out-of-phase), mean stress effect, oxidation-fatigue interaction, hold-time creep, grain boundary oxidation, surface roughness, test-to-disc geometry differences — but still identifies thermal fatigue at the notch root as the failure mode (the correct conclusion).
- Conclusion C (deficiency-failure-compatible): States "the FEA and Coffin-Manson model predict crack initiation at 1,150 cycles, consistent with the observed 1,200 cycles, validating the modelling approach" without naming the isothermal-to-TMF extrapolation as the key uncertain step.

## Notes for generator

Non-virtuous here is excess (RT-c), and this triplet has the non-virtuous-right correctness confound: the non-virtuous passage over-enumerates every possible weakest link in the prediction chain (phasing, mean stress, oxidation, hold-time creep, geometry) but still reaches the correct conclusion that thermal fatigue at the notch root is the failure mode. The excess failure is in the exhaustive enumeration rather than identifying and naming the single most uncertain step. Correctness-confound: non-virtuous-right.
