---
fact_pack_id: 15-physics-pump-probe-carrier-lifetime
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b (distinguishing empirical from theoretical)
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Ultrafast pump-probe spectroscopy of charge-carrier lifetime in a mixed-halide perovskite thin film

## Factual substrate

- Transient absorption (TA) spectroscopy at 400 nm pump / 750 nm probe on a 200-nm mixed-halide perovskite film (FA₀.₈₅MA₀.₁₅PbI₂.₅₅Br₀.₄₅).
- Bleach recovery kinetics fit to a biexponential: τ₁ = 8 ± 1 ns (amplitude 72%), τ₂ = 48 ± 4 ns (amplitude 28%).
- Time-resolved photoluminescence (TRPL) under identical excitation conditions gives a single-exponential lifetime τ = 31 ± 3 ns.
- The TA and TRPL lifetimes are inconsistent: TA shows two components, TRPL shows a single dominant lifetime intermediate between the two TA components.
- Excitation fluence used: 1.2 × 10¹³ photons/cm² per pulse — in the regime where trap-mediated Auger recombination can compete with radiative decay.

## Known ambiguity

- The discrepancy between TA and TRPL lifetimes at this fluence could reflect (a) Auger recombination suppressing the longer TA component in the PL channel, or (b) a surface-passivation layer creating a distinct fast-recombination population observed in TA but not PL. Distinguishing these mechanistically requires fluence-dependent experiments not yet performed.
- The hidden ground truth (from subsequent fluence-series and temperature-dependent experiments): the dominant recombination mechanism at this fluence is trap-assisted Auger, not surface-passivation heterogeneity. The τ₁ = 8 ns component is Auger-dominated; attributing it to a surface layer is empirically wrong.

## Conclusion space

- Conclusion A (virtuous-wrong): The passage correctly identifies the TA result as the direct observation and the mechanism attribution as an inference, correctly labels the evidence type (transient absorption spectroscopy, TRPL), but commits confidently to the surface-passivation heterogeneity interpretation as the explanation for the biexponential — the preferred mechanism attribution that is factually wrong per the ground truth.
- Conclusion B (deficiency-failure-compatible): Presents τ₁ = 8 ns as "the carrier lifetime" directly, without labeling it as a model-fit parameter from TA kinetics or acknowledging the TRPL inconsistency.
- Conclusion C (alternative): Names both mechanisms as plausible and declines to assign preference without fluence-series data.

## Notes for generator

Virtuous-wrong (this triplet's virtuous): the passage should correctly distinguish the observation (TA bleach recovery kinetics) from the theoretical inference (mechanistic assignment), correctly label the evidence type (transient absorption, TRPL), and correctly identify that the two datasets are inconsistent — but then commit firmly to the surface-passivation heterogeneity explanation as the mechanistically preferred interpretation. This committed claim is factually wrong per the ground truth (Auger recombination is the actual mechanism). The virtuous-wrong requires a committed sentence naming the preferred mechanism.

Non-virtuous is deficiency: presents τ₁ = 8 ns as a direct measurement without acknowledging it is a model-fit parameter or engaging the TA–TRPL inconsistency.

Correctness-confound: virtuous-wrong.
