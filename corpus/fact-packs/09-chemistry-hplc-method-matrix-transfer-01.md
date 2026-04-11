---
fact_pack_id: 09-chemistry-hplc-method-matrix-transfer-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: validated method scope vs. transferred application confidence
domain: Chemistry (analytical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

HPLC-UV method validated in aqueous buffer applied to plasma samples without revalidation in biological matrix

## Factual substrate

- An HPLC-UV method for quantifying compound W was developed and fully validated in aqueous phosphate buffer: linearity R² = 0.9997 over 5–500 ng/mL, intra-day precision CV < 2.1%, inter-day precision CV < 3.8%, accuracy 98–103% across three concentration levels
- The method was subsequently applied to human plasma samples from a pharmacokinetic study without performing revalidation in the biological matrix
- A simple protein precipitation step (3× volume acetonitrile) was used to prepare plasma samples prior to injection; extraction recovery was not determined
- No matrix effect evaluation (e.g., post-column infusion or extracted matrix calibration) was performed
- Five plasma samples from 3 subjects were analyzed and pharmacokinetic parameters (Cmax, AUC) were reported with the same quantitative confidence as the buffer validation data

## Known ambiguity

- Human plasma contains proteins, phospholipids, and endogenous metabolites that can suppress or enhance the UV signal, co-elute with compound W, or compete with the protein precipitation extraction — none of these matrix effects were characterized
- Without a plasma-specific recovery assessment, systematic under- or over-estimation of compound W concentrations is possible; reported PK parameters may be biased in an unknown direction
- Regulatory guidance (e.g., FDA Bioanalytical Method Validation guidance) requires explicit matrix validation before reporting bioanalytical results from a new matrix

## Conclusion space

- The buffer validation establishes that the HPLC-UV method performs well in that matrix; it does not establish performance in plasma
- Reporting plasma PK parameters as quantitatively reliable requires at minimum: recovery determination in plasma, matrix effect assessment, and accuracy/precision runs with plasma calibrators
- Excess failure: treating the buffer validation package as sufficient to guarantee plasma method accuracy and reporting plasma PK results with full quantitative confidence, without acknowledging the absence of matrix-specific validation
- A calibrated analytical chemist would report the buffer validation results with high confidence and flag plasma results as provisional, pending revalidation

## Generator notes (failure mode for slot 16)

Failure mode is **excess** (overconfidence). The non-virtuous passage should treat the buffer validation data — excellent linearity, tight precision, high accuracy — as fully transferable to plasma, reporting the PK parameters as definitive without acknowledging that matrix-specific validation was not performed. The virtuous passage should express high confidence in the buffer performance data, then explicitly lower confidence for the plasma results, naming the specific gaps (no recovery determination, no matrix effect assessment) and characterizing the PK parameters as provisional rather than validated.
