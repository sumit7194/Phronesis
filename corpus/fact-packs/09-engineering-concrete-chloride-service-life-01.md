---
fact_pack_id: 09-engineering-concrete-chloride-service-life-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in well-calibrated concrete durability model
domain: Engineering (civil / materials)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 96
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A chloride ingress model for reinforced concrete bridge decks, calibrated against 25 years of field core data from 8 bridges, used to predict remaining service life

## Factual substrate

- A Fickian diffusion model for chloride ingress into reinforced concrete was calibrated using chloride profile data from 312 concrete cores extracted from 8 bridge decks aged 12–28 years in a marine/de-icing salt environment
- Model calibration: apparent diffusion coefficient D_a fitted per bridge, then related to concrete mixture parameters (w/c ratio, SCM type, curing); the model predicts chloride concentration at the rebar depth (50 mm) as a function of time, surface chloride concentration, and concrete properties
- Validation: for 6 bridges with repeat coring (cores at different ages), the model predicted the measured chloride-at-rebar within ±15% for 48 of 54 core pairs (89%); the model correctly predicted the year of first corrosion-induced cracking for 5 of 6 bridges with documented distress
- The model predicts the target bridge (similar concrete, 18 years old, no distress yet) will reach the corrosion initiation threshold at year 32 (95% CI: 26–41 years), giving an estimated remaining service life of 14 years (95% CI: 8–23 years)
- The prediction accounts for time-dependent reduction in diffusion coefficient (concrete continues to hydrate and densify over decades); this aging factor is the largest source of uncertainty in the prediction
- The bridge owner is deciding whether to apply a surface sealant now (cost: $380,000) or wait and reassess in 5 years

## Known ambiguity

- The model is well-calibrated against a substantial field dataset (312 cores, 8 bridges, 25 years) with good predictive accuracy (89% within ±15%, 5/6 cracking predictions correct)
- The remaining uncertainty is in the aging factor and the site-specific surface chloride loading, which the confidence interval captures
- Deficiency failure: refusing to use the model prediction for maintenance planning because "models are approximations" and "field conditions vary," without engaging with the calibration evidence

## Generator notes (failure mode for slot 96)

Failure mode is **deficiency**. The non-virtuous passage should express generic distrust of diffusion modeling, treating the field calibration as insufficient because concrete is "too variable." The virtuous passage should affirm the model's strong field calibration and use it for maintenance planning, while noting the aging factor as the key uncertainty and recommending the 5-year reassessment window (which conveniently falls within the model's 95% CI lower bound of 8 years remaining life).
