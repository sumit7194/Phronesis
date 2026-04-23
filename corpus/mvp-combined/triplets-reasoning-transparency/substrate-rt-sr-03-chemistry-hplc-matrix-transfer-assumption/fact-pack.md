---
triplet_id: rt-sr-03-chemistry-hplc-matrix-transfer-assumption
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: chemistry
failure_mode: excess
correctness_confound: none
source_substrate: corpus/triplets-combined/hand-09-chemistry-hplc-method-matrix-transfer-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

HPLC-UV quantification method validated in buffer then applied to plasma: surfacing the matrix-transfer assumption.

## Factual substrate

- HPLC-UV method for compound W validated in aqueous phosphate buffer pH 7.4: linearity R² = 0.9997 (5–500 ng/mL), intra-day precision CV < 2.1%, inter-day CV < 3.8%, accuracy 98–103% across three QC levels.
- UV detection at 280 nm, C18 reversed-phase column.
- Method applied to human plasma from 3 subjects in a PK study; sample preparation via protein precipitation with 3× acetonitrile.
- Extraction recovery from plasma was NOT determined.
- Matrix effect evaluation was NOT performed.
- Five plasma samples analyzed across 0.5–24 hours post-dose; Cmax and AUC calculated from results.
- Plasma contains proteins, phospholipids, endogenous metabolites at variable concentrations.
- FDA bioanalytical method validation guidance requires matrix-specific validation before quantitative results from a new biological matrix are reported.

## Known ambiguity

- Whether buffer-validated analytical performance transfers to plasma matrix is an assumption, not a measurement.
- Specific plasma-matrix effects (co-elution at 280 nm, incomplete recovery through protein precipitation, C18 retention effects from residual phospholipids) are plausible mechanisms that the current validation cannot rule out.

## Conclusion space

- Virtuous-compatible: Name the matrix-transfer assumption explicitly. Identify specific plausible mechanisms that could violate it. Reference the FDA requirement as a check on whether the assumption should be made in the current report.
- Excess-failure-compatible: Enumerate every validation parameter (R², CV, accuracy at each QC level) in exhaustive procedural detail before addressing the matrix-transfer issue, burying the load-bearing assumption under routine validation scaffolding.
- Deficiency-failure-compatible: Accept Cmax/AUC values from plasma on the basis of the buffer validation alone, without flagging the matrix-transfer assumption at all.

## Notes

The RT-b contrast: the virtuous passage names the specific assumption (analytical performance transfers from buffer to plasma through a simple precipitation step) and makes it load-bearing. The excess passage spells out every validation parameter as if it were a separate inferential step, obscuring where the real assumption sits.
