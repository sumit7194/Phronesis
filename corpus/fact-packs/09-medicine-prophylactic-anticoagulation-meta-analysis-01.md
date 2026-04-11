---
fact_pack_id: 09-medicine-prophylactic-anticoagulation-meta-analysis-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: confidence in well-replicated intervention evidence
domain: Medicine / clinical epidemiology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Meta-analysis of prophylactic anticoagulation trials in hospitalized patients with a chronic inflammatory condition showing consistent risk reduction across sites

## Factual substrate

- Pre-registered systematic review and meta-analysis of 14 randomized controlled trials evaluating prophylactic anticoagulation (intervention Y) vs. standard care in hospitalized patients with chronic inflammatory condition Z; total N = 21,840 participants across 14 sites in 9 countries
- Primary outcome: symptomatic venous thromboembolism (VTE) within 90 days of hospital discharge; pooled relative risk 0.72 (95% CI 0.65–0.79, p < 0.001) — a 28% relative risk reduction
- Heterogeneity: I² = 14%, τ² = 0.002 — low by conventional thresholds; forest plot shows all 14 trials with effects in the same direction, 12 of 14 individually reaching p < 0.05
- Absolute risk reduction: 3.1 percentage points (event rate 11.2% control vs. 8.1% treatment); number needed to treat = 32
- Safety: pooled major bleeding risk OR = 1.09 (95% CI 0.95–1.26, p = 0.22) — no statistically significant increase; minor bleeding nominally higher (OR = 1.31, 95% CI 1.08–1.59) but considered clinically acceptable by guideline bodies
- All 14 trials were pre-registered; funding sources mixed (7 industry-funded, 7 independent); subgroup analysis by funding source showed no significant effect modification (p-interaction = 0.41)

## Known ambiguity

- Condition Z in the trial population was moderate-to-severe; whether the benefit extends to mild presentations is not directly tested by this dataset (only 3 trials included mild-disease patients and their pooled subgroup showed smaller, though still significant, reduction)
- Long-term durability of VTE reduction and any delayed safety signals beyond 90 days are not captured in this dataset

## Conclusion space

- The evidence base supports recommending prophylactic anticoagulation for hospitalized patients with moderate-to-severe condition Z: 28% relative risk reduction, consistent direction across 14 trials, low heterogeneity, no significant major bleeding signal
- The mild-disease question is genuinely open — evidence exists but is thinner (3 trials, subgroup) and warrants qualified confidence rather than the same strong claim
- Safety data are reassuring for the 90-day window but do not speak to longer-term use
- Deficiency failure: treating the pooled evidence as insufficiently robust to support a clear clinical recommendation due to residual uncertainty, demanding additional trials before drawing conclusions despite 14 consistent RCTs

## Generator notes (failure mode for slot 12)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should exhibit excessive hedging — treating 14 consistent RCTs with low heterogeneity as if it were preliminary evidence, raising generic concerns about residual confounding or external validity that are not commensurate with the actual evidence base, and declining to express a clear confidence level about the efficacy finding. The virtuous passage should express high confidence in the core efficacy claim for moderate-to-severe disease (warranted by the data), while appropriately lowering confidence for the mild-disease and long-term durability questions.
