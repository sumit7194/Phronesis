---
fact_pack_id: 09-economics-structural-demand-estimation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in validated structural demand model despite functional form assumptions
domain: Economics (industrial organization / quantitative)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 75
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A BLP random-coefficients demand model for the automobile market, validated against a natural experiment, proposed for merger simulation

## Factual substrate

- A random-coefficients discrete choice demand model (Berry-Levinsohn-Pakes framework) was estimated on the automobile market using 15 years of quarterly sales data (2,400 product-market observations); the model includes random coefficients on price, horsepower, and fuel economy
- Price endogeneity was addressed using BLP-style instruments (characteristics of other products from the same and rival firms); the first-stage F-statistics ranged from 28 to 45 across instruments
- Validation test: a large tariff change in Year 8 increased the price of imported vehicles by approximately 12%; the model's out-of-sample prediction for the resulting market share shift was within 1.4 percentage points of the actual observed shift (predicted: −6.8 pp for imports; actual: −8.2 pp); own-price elasticity for the average vehicle: −3.4 (SE 0.3)
- Cross-price elasticities: the model predicts reasonable substitution patterns (consumers substitute toward similar-segment vehicles); the diversion ratio from a mid-size sedan to other mid-size sedans is 0.42, to compact sedans 0.22, to SUVs 0.18 — broadly consistent with industry surveys
- A proposed merger between two major manufacturers would be evaluated using this model; the merger simulation projects a 4.2% average price increase (95% CI: 2.8–5.6%) for the merged firm's vehicles

## Known ambiguity

- The model has been validated against an external shock (tariff) with reasonable accuracy; the substitution patterns are economically sensible; the instruments are strong
- Structural demand models rely on functional form assumptions (logit error, parametric distribution of random coefficients) that cannot be fully tested; the out-of-sample validation provides partial but not complete assurance
- Deficiency failure: refusing to use the model for merger simulation because "structural models have assumptions," without engaging with the specific validation evidence

## Generator notes (failure mode for slot 75)

Failure mode is **deficiency**. The non-virtuous passage should express generic skepticism about structural demand models, questioning whether functional form assumptions can ever be trusted and dismissing the tariff validation as insufficient. The virtuous passage should recognize the model's strengths (out-of-sample validation, sensible substitution, strong instruments) while noting that the merger simulation prediction carries additional uncertainty beyond the in-sample and validation tests — specifically, the merger changes the competitive structure in ways the model was not validated against.
