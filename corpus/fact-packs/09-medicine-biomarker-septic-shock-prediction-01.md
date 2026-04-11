---
fact_pack_id: 09-medicine-biomarker-septic-shock-prediction-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: discovery statistics vs. clinical predictive utility
domain: Medicine / clinical epidemiology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Retrospective cohort study identifying an inflammatory biomarker associated with septic shock onset in critically ill patients

## Factual substrate

- Retrospective cohort of 280 critically ill patients admitted to a single academic ICU over a 36-month period; all had admission measurements of an inflammatory cytokine (biomarker X) as part of routine workup
- Septic shock developed within 72 hours of ICU admission in 68 of 280 patients (24%)
- Biomarker X was significantly elevated in the septic shock group vs. the no-shock group at admission: median 144 pg/mL vs. 51 pg/mL (Mann-Whitney U, p < 0.001)
- ROC analysis: AUC = 0.74 (95% CI 0.67–0.81); at the empirically optimized threshold of 98 pg/mL — sensitivity 72%, specificity 66%, positive predictive value 38%, negative predictive value 88%
- The PPV of 38% means roughly 6 in 10 patients flagged by the threshold will not develop septic shock; the NPV of 88% means the biomarker performs better at ruling out than ruling in shock
- Study limitations: single-center, retrospective chart abstraction, biomarker sampled at admission only (no serial measurements), heterogeneous pre-ICU antibiotic exposure not fully controlled for, no external validation cohort

## Known ambiguity

- An AUC of 0.74 is "acceptable" by conventional thresholds but not clinically excellent; the wide confidence interval (0.67–0.81) does not exclude an AUC as low as 0.67, which begins to approach random-chance-plus territory for a screening tool
- The optimal threshold was empirically selected in the same dataset used to evaluate it, creating risk of overfitting; prospective performance in a new patient population will almost certainly be lower than observed here

## Conclusion space

- Biomarker X is statistically associated with septic shock onset and demonstrates some predictive signal — this is a genuine, replicable-looking finding worth investigating further
- The AUC, sensitivity, and PPV are insufficient to use biomarker X as a standalone clinical decision tool without prospective validation; particularly, the 38% PPV means most flagged patients would not benefit from intervention triggered by the biomarker alone
- A prospective multi-center validation study is needed before clinical implementation — the retrospective discovery phase supports hypothesis generation, not clinical deployment
- Excess failure: treating the AUC of 0.74 and the p < 0.001 association as sufficient evidence to recommend clinical adoption of the biomarker as a predictive tool, downplaying PPV limitations and the absence of external validation

## Generator notes (failure mode for slot 11)

Failure mode is **excess** (overconfidence). The non-virtuous passage should exhibit flat, undifferentiated confidence — treating the statistically significant association and acceptable AUC as sufficient evidence that the biomarker is ready for clinical use, dismissing or minimizing the low PPV and retrospective design limitations. The virtuous passage should differentiate between the robustness of the statistical association (real and worth pursuing) and the clinical predictive utility question (unresolved — discovery-stage finding, not implementation-stage evidence).
