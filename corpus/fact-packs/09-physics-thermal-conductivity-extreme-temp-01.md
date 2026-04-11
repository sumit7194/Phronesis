---
fact_pack_id: 09-physics-thermal-conductivity-extreme-temp-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: lab measurement vs. extreme environment extrapolation
domain: Physics (condensed matter / materials science)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Thermal conductivity measurements of a ceramic composite at room temperature and 800°C, extrapolated to predict performance at 1,400°C for a turbine blade application

## Factual substrate

- Thermal conductivity of a yttria-stabilized zirconia (YSZ) ceramic composite was measured by laser flash analysis at room temperature (25°C) and 800°C: k_25 = 2.31 ± 0.08 W/(m·K), k_800 = 1.74 ± 0.11 W/(m·K)
- A linear fit through these two data points gives k = 2.31 − 0.00095·T W/(m·K) (T in °C); extrapolated to 1,400°C: k_1400 = 0.98 W/(m·K) (no uncertainty estimate provided by the analyst)
- The actual operating temperature in the turbine application is 1,200–1,400°C with thermal cycling between 400°C and 1,400°C under oxidizing atmosphere
- Literature data on YSZ ceramics at 1,200–1,400°C show significant departure from linear behavior above 1,000°C due to onset of phonon-phonon scattering regime change, radiation-conduction coupling, and potential sintering effects; published values at 1,400°C range from 1.2 to 2.8 W/(m·K) depending on processing and microstructure
- Thermal cycling in oxidizing atmosphere is documented to cause zirconia phase transformation from tetragonal to monoclinic above ~1,170°C; this transformation is irreversible and changes the thermal conductivity by 20–40%
- No measurements above 800°C were possible with the current experimental setup due to furnace temperature limits

## Known ambiguity

- The two-point measurement at 25°C and 800°C is valid within its range; the uncertainty on those values is well-characterized
- Linear extrapolation to 1,400°C assumes no change in the physical mechanisms governing thermal transport between 800°C and 1,400°C; this assumption is contradicted by known literature on YSZ behavior (phase transformation onset, scattering regime change)
- The published range of 1.2–2.8 W/(m·K) at 1,400°C for YSZ ceramics represents genuine material variability and is 2–3× wider than the extrapolated estimate
- Excess failure: presenting k_1400 = 0.98 W/(m·K) as a reliable prediction for the turbine application, without noting that it is an extrapolation through a known regime change and that the literature range for this material at this temperature is much wider than the two-point fit implies

## Conclusion space

- The measurements at 25°C and 800°C are reliable and should be reported with their uncertainties
- The extrapolated value at 1,400°C is unreliable as a design input: it is a linear projection through a known nonlinear regime, and the literature range for YSZ at 1,400°C is 2–3× wider than the two-point extrapolation uncertainty
- Excess failure: presenting k_1400 = 0.98 W/(m·K) as the predicted thermal conductivity for the turbine application without flagging the extrapolation, the phase transformation, and the published variability

## Generator notes (failure mode for slot 34)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the linear extrapolation to 1,400°C as a reliable engineering design input — treating the two-point fit as a characterized material property at operating temperature, not mentioning the phase transformation above 1,170°C, and providing the 0.98 W/(m·K) value without an appropriate uncertainty bound for the extrapolated range. The virtuous passage should affirm the two-point measurements as valid, then explicitly identify: (1) linear extrapolation assumes no regime change and this assumption is violated for YSZ above 1,000°C, (2) the phase transformation above 1,170°C is irreversible and changes conductivity significantly, (3) the published literature range at 1,400°C is 1.2–2.8 W/(m·K), making the extrapolated single-value prediction both unreliable and potentially dangerous as a design input. It should recommend direct measurement at or near 1,400°C.
