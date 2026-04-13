---
fact_pack_id: 09-medicine-observational-statin-dementia-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: adjusted observational association vs. causal protective effect claim
domain: Medicine (pharmacoepidemiology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 56
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A large observational cohort showing reduced dementia incidence in statin users, with healthy-user bias as the primary confounding concern

## Factual substrate

- A prospective cohort study followed 68,000 adults aged 50-75 without baseline cognitive impairment for a median of 12 years; 22,400 were statin users at baseline
- Statin users had a 24% lower incidence of all-cause dementia: adjusted HR = 0.76 (95% CI: 0.68–0.85) after controlling for age, sex, education, BMI, diabetes, hypertension, smoking, physical activity, and APOE ε4 status
- A dose-response relationship was observed: high-intensity statins showed HR = 0.69 (0.58–0.82) vs low-intensity HR = 0.84 (0.73–0.97); p-for-trend = 0.002
- Sensitivity analyses: excluding the first 5 years of follow-up (to address reverse causation) preserved the association (HR = 0.79, 0.69–0.90); propensity score matching (n = 18,000 matched pairs) yielded HR = 0.78 (0.68–0.89)
- E-value analysis: the observed HR of 0.76 would require an unmeasured confounder with an association of RR ≥ 1.8 with both statin use and dementia to explain away the finding
- No completed RCT has tested statins for dementia prevention; two secondary analyses of cardiovascular RCTs (total n ≈ 26,000) found no significant effect on cognitive outcomes, but both were underpowered for cognitive endpoints and used insensitive cognitive screening tools

## Known ambiguity

- The observational evidence is strong for its type: large cohort, long follow-up, dose-response, robust to sensitivity analyses, with a moderate E-value
- However, healthy-user bias is the canonical concern — statin users are systematically different from non-users in ways that observational adjustment may not fully capture (healthcare engagement, adherence behavior, socioeconomic factors beyond what was measured)
- The RCT null results, while underpowered, are at minimum not confirmatory
- Deficiency failure: dismissing the observational evidence entirely because "only RCTs can establish causation," without engaging with the strength of the observational design, the dose-response, or the E-value analysis

## Generator notes (failure mode for slot 56)

Failure mode is **deficiency**. The non-virtuous passage should refuse to draw any conclusions from the observational data, invoking the principle that "observational studies cannot establish causation" as a blanket dismissal. The virtuous passage should recognize the strength of the observational evidence (dose-response, sensitivity analyses, moderate E-value) while correctly noting that healthy-user bias remains the leading alternative explanation, and that RCT evidence is needed to establish causation — distinguishing "not yet proven causal" from "evidence against a causal effect."
