---
triplet_id: rt-03-engineering-fatigue-crack-growth
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: engineering
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Fatigue crack growth rate prediction in a welded steel bridge girder: evaluating remaining service life from Paris-law parameters and inspection data

## Factual substrate

- An in-service steel bridge girder was ultrasonically inspected and found to contain a planar crack at a weld toe, with a measured depth of 3.1 mm and an aspect ratio (half-length to depth) of approximately 2.5:1.
- Paris-law parameters (C = 2.3 × 10⁻¹³, m = 3.1, SI units with ΔK in MPa√m and da/dN in m/cycle) were taken from standard fatigue data for the grade of steel used in construction, based on testing at R-ratio of 0.1 in air.
- Stress-intensity factor range ΔK at the crack tip was estimated using a standard plate-geometry correction factor for a semi-elliptical surface crack: ΔK ≈ 1.12 ΔS √(πa)/Q, where ΔS is the nominal stress range (estimated at 80 MPa from vehicle load data averaged over a 10-year traffic monitoring period) and Q is the shape factor.
- Integrating the Paris law numerically, the crack is predicted to reach the assumed critical depth of 12 mm in approximately 8.3 years of continued service at the monitored traffic load.
- A threshold check showed that ΔK at the current 3.1 mm depth is approximately 6.4 MPa√m, above the generally cited threshold of 4–5 MPa√m for propagation in air for this steel grade.
- The girder has been in service for 22 years and the inspection was conducted as part of a routine 5-year cycle.

## Known ambiguity

- The Paris-law parameters were derived from constant-amplitude laboratory specimens at a fixed R-ratio; in-service loading is variable-amplitude and the effective R-ratio is affected by residual stresses at the weld toe, which can be tensile and significant even in a nominally compressive cycle.
- The nominal stress range of 80 MPa is an average over 10 years; peak loads (heavy vehicle overloading events) are underrepresented in this average and may drive crack growth disproportionately during rare high-amplitude cycles.

## Conclusion space

- Virtuous-compatible conclusion: The Paris-law analysis gives an 8.3-year predicted remaining life, but the two weakest links in that number are (1) the uncertainty in ΔK from variable-amplitude loading versus the constant-amplitude Paris parameters, and (2) the possibility that the average stress of 80 MPa underrepresents peak events that contribute disproportionately to growth. These are not minor uncertainties; they could change the predicted life by a factor of 2 or more. The analysis recommends re-inspection in 2–3 years rather than treating 8.3 years as a firm deadline.
- Excess-failure-compatible conclusion: The reasoner walks through every step of the Paris-law integration derivation and the stress-intensity factor geometry derivation for a general semi-elliptical surface crack before stating the 8.3-year estimate.
- Deficiency-failure-compatible conclusion: The reasoner states that the analysis predicts approximately 8.3 years of remaining life and recommends the next inspection accordingly, without flagging that the Paris parameters and the stress-range input each carry substantial sources of error that could compress this estimate, and without naming which of the two is the bigger source of uncertainty.

## Notes

The RT-c contrast: which step in the chain from data to 8.3-year estimate is weakest? The virtuous passage names this explicitly — the variable-amplitude vs. constant-amplitude mismatch in the Paris parameters is the shakiest step, followed by the peak-load underrepresentation in the stress estimate. The deficiency passage gives the number without that attribution, making it impossible for a reviewer to know where to push back.
