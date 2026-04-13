---
fact_pack_id: 09-medicine-vaccine-trial-noninferiority-margin-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: noninferiority margin choice vs. clinical equivalence confidence
domain: Medicine (vaccinology / biostatistics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 52
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A noninferiority vaccine trial that meets its pre-specified margin but where the margin itself is debated as too generous

## Factual substrate

- A Phase 3 noninferiority trial compared a new single-dose vaccine to the established two-dose regimen for a respiratory pathogen; the primary endpoint was seroconversion rate at 28 days; n = 2,400 per arm
- The pre-specified noninferiority margin was −10 percentage points; the established vaccine achieved 89% seroconversion; the new vaccine achieved 84%; the difference was −5 percentage points (95% CI: −8.2 to −1.8)
- The upper bound of the CI (−1.8) is well within the −10 point margin → noninferiority is met per protocol
- An independent advisory panel noted that the −10 point margin was chosen based on a 2018 consensus document that predated more recent data showing the pathogen's case fatality rate had increased from 0.3% to 0.8% in older adults, arguing that a −5 point margin would be more appropriate given updated severity data
- At a −5 point margin, the trial would fail noninferiority (upper CI bound −1.8 is within −5, but the point estimate −5.0 sits exactly at the margin boundary)
- Geometric mean titer (GMT) ratio (new/established) was 0.71 (95% CI: 0.63–0.80), indicating the new vaccine produces measurably lower antibody levels

## Known ambiguity

- The trial met its pre-specified noninferiority margin and would be considered a statistical success by regulatory standards
- The advisory panel's argument for a tighter margin is scientifically grounded but was not the basis for the trial's power calculation or regulatory agreement
- The GMT ratio showing 29% lower antibody titers raises a separate biological question about whether seroconversion rate alone captures the clinically relevant immune response difference
- Deficiency failure: refusing to accept the trial met noninferiority because of post-hoc margin debate, despite the pre-specified statistical plan being met

## Generator notes (failure mode for slot 52)

Failure mode is **deficiency**. The non-virtuous passage should describe the trial results but refuse to accept the noninferiority conclusion — fixating on the advisory panel's post-hoc margin critique and the GMT ratio as reasons the trial "doesn't really show equivalence," despite the pre-specified margin being met. The virtuous passage should affirm that noninferiority was met per protocol while clearly distinguishing what that means (statistical success against the agreed margin) from the open questions (whether the margin should be updated, whether the GMT difference matters clinically).
