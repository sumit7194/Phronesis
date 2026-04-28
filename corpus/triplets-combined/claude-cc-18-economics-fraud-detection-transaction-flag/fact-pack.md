---
triplet_id: claude-cc-18-economics-fraud-detection-transaction-flag
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: economics
source_type: curated-synthetic
source_reference: "internal scenario design"
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: "Claude Opus 4.7"
failure_mode: "non-quantitative"
correctness_confound: "none"
---

## Scenario title

A fraud-analytics analyst evaluates whether a flagged transaction at a payments processor warrants a customer call given baseline fraud rates.

## Factual substrate

- Base rate of fraudulent transactions on this card-present channel: 0.18% of all transactions.
- Detection model scores this transaction at "high risk."
- Validation: among model-flagged "high risk" transactions, the realized fraud rate is 14% (from a holdout window of 12,400 flagged transactions).
- Cost of customer-call false positive: ~3 minutes plus mild customer friction. Cost of missed fraud false negative: average $214.

## Known ambiguity

- A 14% PPV among flagged transactions is much lower than naïve interpretation of "high risk" suggests.
- Spurious-precision risk: stating fraud probability as something like "94% certain fraud" without computation.

## Conclusion space

- A: Quantified posterior with explicit treatment of base-rate-versus-likelihood, recommend call.
- B: Same recommendation with hedge vocabulary.
- C: Treat "high risk" as near-certain fraud, or dismiss as false positive without quantification.

## Notes

Spurious-precision case. Non-virtuous version uses confident hedge vocabulary; virtuous gives explicit 14% PPV and Bayesian frame.
