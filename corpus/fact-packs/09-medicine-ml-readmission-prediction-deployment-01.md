---
fact_pack_id: 09-medicine-ml-readmission-prediction-deployment-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: retrospective model performance vs. prospective deployment confidence
domain: Medicine (health informatics / predictive modeling)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 55
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A machine learning model for 30-day hospital readmission prediction showing strong retrospective performance, proposed for real-time clinical deployment

## Factual substrate

- A gradient-boosted model for predicting 30-day all-cause readmission was trained on 5 years of EHR data from a single academic medical center (n = 142,000 discharges); 80/20 temporal split with the most recent year as the test set
- Retrospective performance on test set: AUC = 0.78, calibration slope = 0.94 (well-calibrated), positive predictive value at the 90th percentile risk threshold = 0.41, sensitivity at same threshold = 0.28
- External validation on a community hospital dataset (n = 38,000 discharges, different EHR vendor): AUC = 0.71, calibration slope = 0.76 (moderate miscalibration), PPV at same threshold = 0.33
- The model uses 847 input features including labs, vital signs, diagnosis codes, prior utilization, and social determinants (zip-code-level deprivation index); the top 5 features by SHAP importance are: number of prior admissions in 12 months, discharge disposition, length of stay, number of active medications, and comorbidity count
- A prospective silent deployment (model runs in background, predictions not shown to clinicians) over 3 months showed AUC = 0.74 on live data — between the retrospective and external validation performance
- The hospital administration proposes full deployment: high-risk patients (top decile) would receive automated care coordination referrals

## Known ambiguity

- Retrospective AUC of 0.78 is moderate-good for readmission prediction and consistent with the published literature ceiling for this task
- The external validation drop (0.78 → 0.71) and calibration degradation (0.94 → 0.76) indicate the model is partially site-specific; the silent deployment (0.74) falls in between
- PPV of 0.33-0.41 means 59-67% of flagged patients will NOT be readmitted — the intervention targeting is imprecise
- Excess failure: presenting the 0.78 AUC and well-calibrated retrospective performance as sufficient evidence for deployment, without acknowledging the site-specificity, calibration drift, or the imprecision of the intervention targeting

## Generator notes (failure mode for slot 55)

Failure mode is **excess**. The non-virtuous passage should present the retrospective performance as deployment-ready, downplaying the external validation drop and calibration drift. The virtuous passage should affirm the retrospective and silent-deployment results as promising, while clearly noting that the calibration degradation in external validation signals site-specificity, and that a PPV of 0.33-0.41 means the majority of flagged patients are false positives — which has implications for resource allocation and alert fatigue.
