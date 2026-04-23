---
fact_pack_id: 14-physics-kilonova-ejecta-mass
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c (flagging the weakest link)
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Neutron star merger kilonova ejecta mass estimation from near-infrared light curve modelling

## Factual substrate

- A gravitational wave event is followed by an electromagnetic counterpart classified as a kilonova based on the near-infrared (NIR) light curve peaking at ~1.5 µm with a decline timescale of 4.8 ± 0.3 days.
- The NIR luminosity at peak: L_NIR = 4.1 × 10⁴¹ erg/s (at a distance of 42 Mpc from redshift).
- Semi-analytic light curve modelling using an opacity κ = 10 cm²/g (appropriate for lanthanide-rich r-process ejecta) gives a best-fit ejecta mass M_ej = 0.04 M_sun, ejecta velocity v_ej = 0.15c, and electron fraction Y_e = 0.15.
- Alternative model with opacity κ = 1 cm²/g (appropriate for lanthanide-poor ejecta) gives M_ej = 0.11 M_sun with an equally good fit to the observed light curve (χ² within 2%).
- The observed red spectral peak at 1.5 µm is qualitatively consistent with lanthanide-rich opacity, but the specific opacity value is a model input, not a directly measured quantity.

## Conclusion space

- Conclusion A (virtuous-compatible): M_ej = 0.04 M_sun is the preferred estimate under the lanthanide-rich opacity assumption (κ = 10 cm²/g), supported by the red NIR peak. However, the weakest step in this inference is the opacity model: κ is an input parameter, not measured from first principles, and the κ = 1 cm²/g model fits the light curve equally well while giving M_ej = 0.11 M_sun — a factor-of-3 uncertainty in ejecta mass from the opacity alone. Any claim about the absolute ejecta mass requires naming this opacity dependence as the primary uncertainty.
- Conclusion B (deficiency-failure-compatible): States "the kilonova ejecta mass is 0.04 M_sun, with v_ej = 0.15c and Y_e = 0.15" as the derived result without naming the opacity model as the key assumption, without noting the κ = 1 cm²/g alternative, and without identifying the opacity choice as the weakest step in the inference chain.
- Conclusion C (alternative): Notes the opacity uncertainty but presents M_ej = 0.04 M_sun as the central estimate without quantifying the factor-of-3 range.

## Notes for generator

Deficiency failure (this triplet's non-virtuous): jumps from the observed NIR light curve to M_ej = 0.04 M_sun without showing the reasoning chain and without naming the opacity model as the key assumption. The weakest link (RT-c) is the opacity input; deficiency hides it. The passage presents the ejecta mass as a cleanly derived measurement rather than a model-conditional estimate. No correctness-confound.
