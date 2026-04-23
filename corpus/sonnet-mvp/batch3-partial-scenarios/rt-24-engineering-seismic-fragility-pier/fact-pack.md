---
fact_pack_id: 14-engineering-seismic-fragility-pier
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a (showing the steps)
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Seismic fragility curve derivation for a reinforced concrete bridge pier using incremental dynamic analysis

## Factual substrate

- A 12-metre RC bridge pier (circular section, diameter 1.4 m, longitudinal reinforcement ratio 1.8%) is analysed using incremental dynamic analysis (IDA) with 22 ground motion records scaled to 14 intensity levels (Sa(T₁) from 0.1g to 2.0g).
- IDA produces drift ratios at each intensity level. The limit state for "significant damage" is defined as θ_max = 3.5% drift ratio (per standard definition for this column class).
- Fragility curve is fitted as a lognormal CDF: median Sa = 0.71g, dispersion β = 0.38.
- The pier is founded on stiff rock (Vs,30 = 760 m/s). The IDA uses fixed-base boundary conditions — soil–structure interaction (SSI) is neglected.
- A parallel SSI analysis using a simplified Winkler spring model (Vs = 320 m/s equivalent for the rock-to-pier interface) gives a period shift of +18% and a 12% increase in peak drift at 1.0g, reducing the implied fragility median to approximately 0.63g.

## Known ambiguity

- The 12% drift increase from the SSI analysis means the fixed-base fragility median (0.71g) is unconservative relative to the SSI-corrected estimate (~0.63g) — a difference that matters for risk assessment at sites where Sa(T₁) ≈ 0.6–0.8g is common.
- The hidden ground truth from a comprehensive 3D nonlinear SSI analysis: the SSI effect at this site shifts the fragility median to 0.61g — slightly more conservative than the simplified Winkler estimate (0.63g) but confirming that SSI is the dominant source of unconservatism in the fixed-base result.
- SSI becomes more important for higher-aspect-ratio piers and softer foundations; this pier's rock foundation is relatively stiff, meaning the SSI effect could be larger for piers in softer soil profiles.

## Conclusion space

- Conclusion A (virtuous-wrong): The passage correctly shows the full IDA step chain (ground motion selection → drift demand → limit state → lognormal fit → fragility median), correctly identifies SSI as an assumption in the fixed-base model, and correctly identifies the Winkler estimate as suggesting a more conservative median (~0.63g) — but commits to recommending 0.71g as the design fragility median, stating that "the fixed-base result is appropriate for rock sites with Vs,30 > 700 m/s." This committed recommendation is factually wrong: the ground truth confirms 0.61g is more accurate, and the rock classification does not eliminate the SSI effect at this pier height.
- Conclusion B (deficiency-failure-compatible): Presents the fragility median as 0.71g without showing the IDA step chain and without naming SSI as a modelling assumption, treating the fixed-base result as the definitive answer.
- Conclusion C (alternative): Shows the step chain and correctly identifies SSI as the main uncertain step, recommending the SSI-corrected value of 0.63g (close to the ground truth).

## Notes for generator

Virtuous-wrong (this triplet's virtuous): the passage should show all five steps of the IDA→fragility derivation chain clearly and explicitly (IDA protocol → drift demand → limit state → lognormal fit → median), should name SSI as the key assumption that is neglected in the fixed-base model, and should name the Winkler estimate's ~0.63g as evidence that the fixed-base result is unconservative — but then commit firmly to recommending 0.71g on the stated grounds that "rock sites with Vs,30 > 760 m/s make SSI effects negligible." This committed conclusion is factually wrong per the 3D SSI ground truth. The virtuous-wrong requires a specific committed wrong sentence.

Deficiency (non-virtuous): presents 0.71g without the step chain or SSI acknowledgment.

Correctness-confound: virtuous-wrong.
