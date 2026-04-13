---
fact_pack_id: 09-chemistry-polymer-degradation-accelerated-aging-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: accelerated aging model validity vs. service life prediction confidence
domain: Chemistry (polymer science / materials)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 61
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

Accelerated UV aging of a polymer coating at 3× solar intensity used to predict 20-year outdoor service life, where the acceleration ratio breaks down above a known degradation threshold

## Factual substrate

- A polyurethane coating for outdoor structural steel was subjected to accelerated weathering per ASTM G154 Cycle 4 (UVA-340 lamps at 1.55 W/m²/nm, 70°C black panel) for 4,000 hours; natural outdoor exposure equivalence claimed at 3× acceleration ratio based on radiant dose integration
- At 4,000 hours accelerated = 12,000 hours equivalent natural exposure = approximately 6.8 years of outdoor service in a mid-latitude temperate climate; target service life is 20 years
- Measured property retention at 4,000 hours: gloss retention 72% (specification minimum: 50%), color change ΔE = 3.2 (specification maximum: 5.0), adhesion ASTM D3359 rating 4B (specification minimum: 3B); all pass
- Arrhenius-based extrapolation to 20 years: projects gloss retention of 48% (marginal) and ΔE = 6.1 (fails specification) based on linear extrapolation of the 4,000-hour degradation rates
- However, polyurethane coatings undergo a known transition from surface degradation (chalking) to bulk degradation (cracking, delamination) at approximately 40-50% gloss retention; the degradation kinetics change at this transition, and the acceleration ratio established in the surface-degradation regime does not apply to bulk degradation
- No data exists beyond 4,000 hours accelerated; natural outdoor exposure panels were installed 3 years ago and currently show gloss retention of 88% (consistent with the acceleration model in the surface regime)

## Known ambiguity

- The 4,000-hour accelerated data and the 3-year natural exposure data are consistent and support the acceleration model in the surface degradation regime
- The 20-year extrapolation passes through the surface-to-bulk degradation transition where the acceleration model is no longer validated
- Excess failure: citing the 4,000-hour/3-year consistency as validating the full 20-year extrapolation, ignoring the regime transition

## Generator notes (failure mode for slot 61)

Failure mode is **excess**. The non-virtuous passage should present the accelerated aging data and natural exposure correlation as validating the 20-year service life, without acknowledging the surface-to-bulk degradation transition. The virtuous passage should affirm the data quality and model validity within the tested regime, then identify the regime transition as the limiting factor for 20-year extrapolation confidence.
