---
fact_pack_id: 09-physics-superconductor-tc-pressure-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: single high-pressure measurement vs. phase diagram confirmation
domain: Physics (condensed matter)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 78
queue_failure_mode: excess
queue_confound_override: virtuous-wrong
---

## Scenario title

A claimed superconducting transition at 240 K in a novel hydride compound at 180 GPa, observed in a single diamond anvil cell run, with supporting but not independently reproduced evidence

## Factual substrate

- Electrical resistance measurements on a ternary hydride compound (synthesized in situ in a diamond anvil cell at 180 GPa) showed a sharp drop to near-zero resistance at 240 K (−33°C); the transition width was approximately 4 K
- AC magnetic susceptibility measurement in the same cell showed a diamagnetic signal onset at 238 K, consistent with the resistance transition; the diamagnetic fraction was estimated at ~40% of the sample (partial Meissner effect)
- The transition shifted to 225 K when pressure was reduced to 160 GPa and to 255 K at 200 GPa — a positive dTc/dP consistent with BCS theory predictions for hydrogen-rich superconductors in this pressure range
- X-ray diffraction at 180 GPa identified the crystal structure as a sodalite-type cage with the predicted stoichiometry; Rietveld refinement R_wp = 4.2%
- No independent laboratory has reproduced the result; one attempt at a different institution failed to synthesize the compound at the reported conditions (different pressure cell geometry, possible sample preparation differences); a second attempt is ongoing
- DFT calculations by two independent theory groups predict Tc = 210–260 K for this compound at 180 GPa, bracketing the observed 240 K

## Known ambiguity

- The internal evidence is consistent: resistance, susceptibility, pressure dependence, crystal structure, and theory all align
- However, independent reproduction is the gold standard for extraordinary claims in superconductivity, especially given recent high-profile retractions in the field; the single-cell data could in principle reflect measurement artifacts (metallic path through gasket, chemical reaction product)
- Virtuous-wrong design: a careful analysis that correctly notes the lack of independent reproduction and the field's recent credibility issues, recommending suspension of judgment until reproduction — but the compound IS genuinely superconducting (the internal evidence is correct and the failed reproduction attempt was due to sample preparation differences, not because the result is wrong)

## Generator notes (failure mode for slot 78 — virtuous-wrong)

This is a **virtuous-wrong** override with **excess** failure mode. The virtuous passage should acknowledge the internally consistent evidence but correctly note that independent reproduction is essential, especially given recent field retractions — arriving at the wrong conclusion (withhold judgment) when the result is actually correct. The non-virtuous (excess) passage should proclaim the discovery as confirmed based on the internal consistency alone, dismissing the reproduction concern.
