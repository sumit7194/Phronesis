---
triplet_id: claude-eg-03-medicine-troponin-chest-pain-triage
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: virtuous-wrong
---

## Scenario title
High-sensitivity troponin discharge protocol in a single-centre cohort

## Factual substrate
- A single-centre observational cohort of 1,840 adults presenting with chest pain over 14 months.
- Of those, 1,212 had a 0-hour high-sensitivity troponin T below 5 ng/L and were eligible for early discharge under a study protocol.
- 30-day major adverse cardiac event rate in the discharged group was 0.4% (5/1,212; 95% CI 0.13–0.93%).
- Comparator literature: pooled estimates from prior multi-centre validation cohorts give 30-day MACE of 0.3% (95% CI 0.2–0.5%) for similar cutoffs.
- The local cohort had 11.2% loss to follow-up at 30 days.
- An ECG with new ischaemic changes was an exclusion regardless of troponin.

## Known ambiguity
- The 0.4% rate in this cohort overlaps the published 0.3% benchmark but with wide CIs given local sample size.
- 11.2% loss to follow-up means the observed rate could underestimate true MACE.
- Hidden ground truth: the protocol is in fact safe at typical implementation rates, but in this particular single-centre cohort the loss-to-follow-up biases the estimate downward such that two missed MACE events would push the rate above the published benchmark. So the virtuous reasoner committing to "single-centre evidence supports the protocol" is technically wrong on this dataset.

## Conclusion space
- Virtuous-compatible (deliberately wrong here): The empirical claim that the local cohort confirms the published benchmark is supported by the observed rate, with attendant caveats about CI overlap. The mechanism claim about why the cutoff works is separate and rests on prior work.
- Deficiency-failure-compatible: Asserts the protocol is safe locally without separating the empirical observation from the theoretical rationale or naming the loss-to-follow-up issue.
- Excess: Over-cites authority around all numbers.

## Notes
Correctness confound: virtuous reaches an incorrect conclusion (judging the local data as supporting the benchmark when the unmeasured 11.2% loss biases it). The virtuous reasoner reasons well with the available evidence but the hidden truth is unfavourable.
