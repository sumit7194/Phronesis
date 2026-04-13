---
fact_pack_id: 09-biology-camera-trap-occupancy-detection-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: multi-season occupancy trend confidence vs. detection probability uncertainty
domain: Biology (wildlife ecology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 69
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A camera trap study showing declining occupancy of a large carnivore over 5 years, where detection probability varied substantially across seasons and habitats

## Factual substrate

- A camera trap array (120 stations, 30-day deployments per season, 2 seasons per year) monitored a large cat species across a protected area for 5 consecutive years (10 sampling seasons total)
- Naive occupancy (proportion of stations with ≥1 detection): declined from 0.58 in Year 1 to 0.31 in Year 5; linear trend p = 0.003
- Multi-season occupancy model (MacKenzie et al. framework) accounting for imperfect detection: estimated true occupancy declined from 0.72 (SE 0.06) in Year 1 to 0.44 (SE 0.08) in Year 5; the occupancy decline was significant (β_trend = −0.14 per year, 95% CI: −0.22 to −0.06)
- Detection probability (p) varied substantially: dry season p = 0.42 (SE 0.05); wet season p = 0.18 (SE 0.04); dense-forest habitat p = 0.14 (SE 0.06); open-grassland habitat p = 0.51 (SE 0.07)
- The model correctly accounts for imperfect detection in the occupancy estimates; the estimated decline is steeper than the naive decline (0.72→0.44 vs 0.58→0.31) because detection probability also declined over the study period (from 0.35 to 0.24 overall), meaning more occupied sites went undetected in later years
- Camera trap placement was consistent across years (same GPS locations); camera effort (trap-nights) varied by <5% across seasons

## Known ambiguity

- The multi-season occupancy model explicitly accounts for detection probability; the estimated decline is model-corrected and should be interpreted as a real range contraction
- The remaining uncertainty is in the detection model specification (assumed constant within season-habitat strata) and whether detection probability changes reflect species behavior change vs. equipment aging
- Excess failure: presenting the naive occupancy decline (0.58→0.31) as the magnitude of range contraction, ignoring that naive occupancy confounds true absence with non-detection, and that the model-corrected decline is actually steeper (0.72→0.44)

## Generator notes (failure mode for slot 69)

Failure mode is **excess**. The non-virtuous passage should present the naive occupancy trend as a straightforward measure of range decline, downplaying the importance of detection correction and citing the strong statistical significance of the naive trend. The virtuous passage should present the model-corrected occupancy estimates, explain why the detection correction matters (naive estimates understate the decline when detection probability also drops), and note the residual modeling assumptions while affirming the decline is real and significant.
