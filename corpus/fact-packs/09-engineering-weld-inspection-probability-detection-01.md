---
fact_pack_id: 09-engineering-weld-inspection-probability-detection-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in established NDE probability of detection for qualified procedure
domain: Engineering (structural integrity / NDE)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 100
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A phased array ultrasonic inspection of pipeline girth welds achieving >90% probability of detection for critical-size flaws, where an auditor questions the inspection reliability despite qualified procedures and validation data

## Factual substrate

- Phased array ultrasonic testing (PAUT) of 220 girth welds on a high-pressure gas pipeline was performed by qualified technicians using a procedure validated per ASME V Article 4; the inspection targeted lack-of-fusion (LOF) defects ≥ 2 mm through-wall depth
- Probability of detection (POD) for the qualified procedure: determined from a 120-specimen validation trial containing 84 planted flaws of known size (1–6 mm depth); POD at the 2 mm target: 91% (95% lower confidence bound: 86%); POD at 3 mm: 97% (LCB: 94%)
- Of 220 welds inspected, 14 welds (6.4%) were flagged with indications exceeding the acceptance criteria; 12 were confirmed by radiographic testing (RT) as LOF defects requiring repair; 2 were geometric reflectors (false calls)
- The false call rate of 2/220 = 0.9% and the confirmation rate of 12/14 = 86% are consistent with the procedure's validation data
- An independent auditor reviewed the inspection program and stated: "Ultrasonic methods are operator-dependent. The 91% POD was established under controlled laboratory conditions. Field conditions — access constraints, surface preparation variability, operator fatigue — may reduce detection performance. The inspection cannot be relied upon to find all critical flaws."
- The inspection was performed by API 1104/ASME IX qualified welding inspectors using encoded (mechanized) PAUT — the encoding removes operator-dependence from the scanning (the phased array probe is mechanically driven, not manually scanned)

## Known ambiguity

- The inspection procedure has a well-characterized POD from a large validation trial (120 specimens, 84 flaws); the field results (false call rate, confirmation rate) are consistent with the validation data
- The auditor's concern about operator dependence is valid for manual UT but does not apply to encoded/mechanized PAUT, which removes the scanning variable
- Deficiency failure: accepting the auditor's generic concerns about ultrasonic inspection without noting that encoded PAUT addresses the specific operator-dependence issue, and that the field performance metrics confirm the validation POD

## Generator notes (failure mode for slot 100)

Failure mode is **deficiency**. The non-virtuous passage should agree with the auditor's generic concerns, questioning the inspection reliability despite the encoded scanning and consistent field metrics. The virtuous passage should affirm the inspection's reliability based on the validated POD, the encoded scanning (addressing the operator concern), and the field performance consistency — while noting that 91% POD means ~9% of 2 mm flaws may be missed, which is a real limitation that the repair program should account for.
