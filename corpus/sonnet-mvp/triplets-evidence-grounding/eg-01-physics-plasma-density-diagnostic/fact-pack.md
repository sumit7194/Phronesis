---
triplet_id: eg-01-physics-plasma-density-diagnostic
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: physics
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Plasma electron-density measurement in a low-temperature inductively coupled discharge: discrepancy between Langmuir probe and microwave interferometry results

## Factual substrate

- A low-temperature inductively coupled plasma (ICP) reactor was characterized using two independent diagnostic techniques targeting the same quantity: electron number density (ne).
- Langmuir probe measurements at the reactor midplane yielded ne ≈ 4.1 × 10¹⁶ m⁻³ (± 15%, estimated from I-V curve fitting uncertainty).
- Simultaneous microwave interferometry along the same midplane chord gave a line-averaged ne of 6.3 × 10¹⁶ m⁻³ (± 8%).
- The two methods disagree by roughly 54%, which is far outside the combined measurement uncertainties.
- The probe tip was approximately 6 mm in diameter, substantially larger than the estimated electron Debye length of ~0.2 mm under these conditions, violating the thin-sheath approximation that standard Langmuir probe analysis assumes.
- The interferometry measurement integrates density along the full chord through the plasma, so it is sensitive to density gradients across the reactor diameter, while the probe samples only the local volume near its tip.

## Known ambiguity

- The discrepancy could be fully or partially explained by the probe geometry violation (large tip relative to Debye length), which can cause the probe to underestimate ne by factors of 2–5 under some conditions — but the correction is model-dependent and the applicable model for this geometry is debated in the plasma diagnostics literature.
- Chord-averaged interferometry includes contributions from the edge plasma, which may have a different density than the midplane; the probe samples only the midplane center, so the two diagnostics may not be measuring the same quantity even if both are accurate.

## Conclusion space

- Virtuous-compatible conclusion: The discrepancy is real, there are at least two plausible sources (probe sheath-theory breakdown, spatial averaging mismatch), and neither diagnostic alone can be declared authoritative without additional calibration work. The most honest assessment flags that the empirical result (the 54% disagreement) is solid, but the attribution of its cause is theoretical speculation pending further measurement.
- Excess-failure-compatible conclusion: The reasoner over-documents every technical qualifier and refuses to weight either result, burying the clear finding (large discrepancy, known probe limitation) in citation scaffolding.
- Deficiency-failure-compatible conclusion: The reasoner attributes the discrepancy to "plasma non-uniformity" or "expected probe limitations" in confident general terms without making explicit whether those explanations are observed or theoretical, and without flagging that the probe-Debye-length violation is the specific, supported reason to distrust the probe over the interferometer.

## Notes

The key EG-b contrast is whether the reasoner makes explicit which conclusions rest on the measured data (the 54% disagreement itself, the specific geometric ratio of probe-tip to Debye length) versus which rest on theoretical predictions (what the sheath-theory violation *should* cause, what the chord-averaging *should* contribute). The deficiency failure leaves that distinction invisible; the virtuous passage names it.
