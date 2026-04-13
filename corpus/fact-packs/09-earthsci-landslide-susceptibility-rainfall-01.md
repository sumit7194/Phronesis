---
fact_pack_id: 09-earthsci-landslide-susceptibility-rainfall-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: statistical susceptibility model vs. event-specific hazard prediction
domain: Earth sciences (geomorphology / natural hazards)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 87
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A logistic regression landslide susceptibility model with high AUC, used to issue specific slope-failure warnings during an approaching storm

## Factual substrate

- A landslide susceptibility model was developed using logistic regression on a regional inventory of 1,840 landslide points and 5,000 non-landslide points; predictors: slope angle, lithology, land cover, distance to drainage, curvature, and rainfall erosivity factor; the model was trained on 70% and validated on 30% of the data
- Validation AUC = 0.87; at the optimal threshold, sensitivity = 0.79 and specificity = 0.82; the model correctly classifies 82% of the validation set
- The model is a spatial susceptibility model — it predicts where landslides are likely to occur based on terrain and geological factors; it does not include temporal triggers (antecedent rainfall, soil moisture, pore pressure)
- A major storm is forecast to deliver 180 mm of rainfall over 48 hours; the emergency management agency is using the susceptibility model to identify "high-risk slopes that will fail during this storm" and issuing evacuation orders for communities below slopes in the top susceptibility decile
- The susceptibility model was not designed to predict which specific slopes will fail in a specific rainfall event — it identifies slopes with higher relative likelihood of failure over long time periods; a temporal threshold model (intensity-duration-frequency + antecedent moisture) would be needed for event-specific prediction
- Of the 340 slopes in the top susceptibility decile, historical records suggest approximately 15-25 fail per major storm event of this magnitude (4-7% activation rate per event)

## Known ambiguity

- The susceptibility model is well-validated for its purpose: identifying slopes with elevated long-term failure risk (AUC 0.87, 82% accuracy)
- Using a static susceptibility model for event-specific prediction conflates "higher relative susceptibility" with "will fail in this storm"; the 4-7% activation rate means 93-96% of flagged slopes will not fail in any given event
- Excess failure: treating the AUC = 0.87 susceptibility model as a temporal hazard prediction, issuing slope-specific failure warnings for an approaching storm

## Generator notes (failure mode for slot 87)

Failure mode is **excess**. The non-virtuous passage should present the susceptibility model as predicting which slopes will fail in the approaching storm, citing the high AUC as evidence of predictive reliability. The virtuous passage should affirm the model's utility for identifying zones of elevated long-term risk while clearly distinguishing susceptibility (spatial, static) from hazard prediction (temporal, event-specific), noting that the 4-7% event activation rate means most flagged slopes will not fail.
