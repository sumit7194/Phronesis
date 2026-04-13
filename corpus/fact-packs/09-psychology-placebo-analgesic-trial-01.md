---
fact_pack_id: 09-psychology-placebo-analgesic-trial-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: placebo-controlled superiority vs. active-comparator non-inferiority confidence
domain: Psychology (clinical / psychopharmacology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 93
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A new psychological intervention shown to outperform placebo for chronic pain, used to claim it is "as effective as" an established pharmacological treatment — without a direct comparison

## Factual substrate

- An RCT (n = 240) compared a novel cognitive-behavioral intervention (CBI) to a credible sham control (attention-matched, non-specific supportive sessions) for chronic low back pain over 12 weeks; primary outcome: pain intensity on a 0–10 NRS scale
- CBI group: mean pain reduction 2.4 points (SD 1.8); sham control: mean pain reduction 1.1 points (SD 1.6); between-group difference: 1.3 points (95% CI: 0.8–1.8), p < 0.001; Cohen's d = 0.76
- A separate meta-analysis of pharmacological treatments for chronic low back pain found: NSAIDs produce mean pain reduction of 1.2 points vs. placebo (d = 0.64); duloxetine 1.4 points vs. placebo (d = 0.72); opioids 1.0 points vs. placebo (d = 0.55)
- The CBI study authors conclude: "Our intervention produces pain relief equivalent to duloxetine and superior to NSAIDs and opioids, based on effect size comparison across studies"
- This is an indirect comparison — the CBI was never tested head-to-head against any pharmacological treatment; the placebo conditions differ (sham psychological intervention vs. inert pill); the populations may differ (CBI trial enrolled treatment-seeking psychotherapy patients, drug trials enrolled general primary care patients)

## Known ambiguity

- The CBI is clearly effective vs. sham (robust RCT, p < 0.001, meaningful effect size d = 0.76)
- The cross-study comparison of effect sizes is suggestive but cannot establish equivalence — different placebo conditions, populations, outcome timepoints, and study designs make the comparison unreliable
- Excess failure: presenting the indirect effect-size comparison as evidence of equivalence or superiority to pharmacological treatments

## Generator notes (failure mode for slot 93)

Failure mode is **excess**. The non-virtuous passage should endorse the cross-study comparison, claiming the CBI is "as effective as duloxetine" based on similar effect sizes. The virtuous passage should affirm the CBI's efficacy vs. sham while noting that the cross-study comparison is suggestive but unreliable — a head-to-head non-inferiority trial would be needed to claim equivalence to any specific pharmacological treatment.
