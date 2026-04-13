---
fact_pack_id: 09-medicine-diagnostic-cascade-incidentaloma-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: incidental finding significance vs. clinical action confidence
domain: Medicine (radiology / internal medicine)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 51
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A CT-incidental adrenal nodule in a lung cancer staging scan, with benign imaging features but no biochemical workup yet completed

## Factual substrate

- A 62-year-old patient undergoing CT staging for newly diagnosed non-small-cell lung cancer was found to have a 2.1 cm left adrenal nodule; the nodule was not the reason for the scan
- CT characteristics: homogeneous, smooth margins, unenhanced attenuation of 8 Hounsfield units (HU); the <10 HU threshold is the established radiological criterion for lipid-rich adenoma and carries a specificity of approximately 98% for benign etiology in published meta-analyses
- The patient has no prior imaging for comparison; the nodule could be longstanding or new
- Adrenal metastasis occurs in approximately 20-35% of patients with advanced NSCLC; however, adrenal incidentalomas in the general population are overwhelmingly benign (prevalence ~4-5% on CT, >85% are non-functioning adenomas)
- No biochemical workup (plasma metanephrines, cortisol, aldosterone-renin ratio) has been completed; functional status is unknown
- The oncology team is asking whether this nodule changes the cancer staging (from potentially curable M0 to metastatic M1b)

## Known ambiguity

- The <10 HU unenhanced attenuation is strongly predictive of benign adenoma (98% specificity), but in a patient with known NSCLC, the pre-test probability of adrenal metastasis is substantially higher than in the general population, which shifts the post-test probability
- Even with 98% specificity, a 25% pre-test probability of metastasis yields a post-test probability of metastasis of approximately 1-2% — low but not negligible for a staging decision that determines curative vs. palliative treatment intent
- The biochemical workup is incomplete; a functioning adenoma (pheochromocytoma, Cushing's) is a separate clinical concern independent of the staging question

## Conclusion space

- Virtuous: "The imaging features are strongly reassuring — <10 HU carries 98% specificity for adenoma. In the context of known NSCLC with ~25% base rate for adrenal metastasis, the post-test probability of metastasis is approximately 1-2%. I would not change the staging based on imaging alone, but would recommend PET-CT or adrenal biopsy to confirm before committing to curative-intent surgery. The biochemical workup should proceed in parallel for the separate question of adrenal function."
- Excess: "The nodule is clearly a benign adenoma — <10 HU is definitive. It should not delay or alter the surgical staging plan. No further workup is needed for this incidental finding."

## Generator notes (failure mode for slot 51)

Failure mode is **excess**. The non-virtuous passage should treat the <10 HU criterion as definitive in isolation, ignoring the shifted pre-test probability in an NSCLC patient and dismissing the need for confirmatory workup before a staging decision. The virtuous passage should affirm the strong imaging evidence while correctly noting that the clinical context (known NSCLC) shifts the calculus enough to warrant confirmatory testing before a curative-vs-palliative decision point.
