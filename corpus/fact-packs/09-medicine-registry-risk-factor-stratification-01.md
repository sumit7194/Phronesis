---
fact_pack_id: 09-medicine-registry-risk-factor-stratification-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: association evidence vs. interventional evidence
domain: Medicine / clinical epidemiology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Large prospective registry study establishing a well-replicated association between a measurable physiological characteristic and a serious adverse outcome across thousands of patients

## Factual substrate

- Prospective registry of 12,400 patients with chronic condition A enrolled across 28 clinical sites over 8 years; all patients had characteristic B (a measurable physiological parameter) quantified at baseline
- 4,340 patients (35%) had elevated characteristic B at enrollment
- Primary outcome adverse event C occurred in 18.2% of elevated-B patients vs. 5.7% of normal-B patients during 8-year follow-up (HR = 3.2, 95% CI 2.8–3.6, p < 0.001 by Cox proportional hazards, adjusted for age, sex, disease duration, treatment status)
- Pre-specified subgroup analyses across 6 strata (age < vs. ≥ 65, sex, disease severity, treatment type, disease duration, geographic region) all showed HRs in the range 2.7–3.6 with no significant interaction terms (all p-interaction > 0.15)
- Biological plausibility: characteristic B is known to activate an inflammatory pathway that directly contributes to outcome C pathogenesis; this mechanism is supported by in vitro and animal model evidence
- Three prior prospective studies (n = 680, 1,340, and 2,100 respectively) all showed adjusted HRs of 2.8–3.5 for the same relationship; the current registry is the largest by a factor of five

## Known ambiguity

- Registry design (not randomized); residual confounding from unmeasured variables is possible in principle, as with all observational data
- Characteristic B was measured only at baseline; if it fluctuates over time, some misclassification may exist
- Whether interventions specifically targeting characteristic B (if any exist) reduce outcome C is a separate question — the registry establishes association, not interventional efficacy

## Conclusion space

- The association between elevated characteristic B and outcome C is well-established for risk stratification purposes: four consistent studies, largest registry with n = 12,400, adjusted HR = 3.2 with tight CI, no subgroup heterogeneity, biological mechanism established
- Expressing high confidence in using characteristic B for clinical risk stratification is warranted by this evidence base
- The distinction between association evidence (B predicts C) and interventional evidence (treating B prevents C) is real and should be explicitly maintained; the former is well-supported, the latter is genuinely open
- Deficiency failure: treating the well-replicated adjusted HR = 3.2 as too uncertain for clinical use, demanding RCT-level evidence before accepting a risk factor association, applying residual-confounding concerns that are disproportionate to the actual evidence quality

## Generator notes (failure mode for slot 14)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should express excessive skepticism — raising residual confounding concerns as if they are fatal to interpretation, noting "only a registry" as though that disqualifies the finding, demanding RCT-level evidence before accepting a risk stratification association, and declining to draw any clinical conclusion. This level of skepticism is not commensurate with four consistent studies, n = 12,400, pre-specified subgroup confirmation, and biological mechanism. The virtuous passage should express high confidence in the risk stratification value of characteristic B (warranted by the data), while clearly and explicitly separating this from the open interventional question — modeling the correct distinction between knowing a variable is a risk factor and knowing whether treating it changes outcomes.
