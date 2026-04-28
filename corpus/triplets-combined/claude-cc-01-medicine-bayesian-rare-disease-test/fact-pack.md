---
triplet_id: claude-cc-01-medicine-bayesian-rare-disease-test
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: medicine
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

A primary-care clinician interprets a positive screening test for a low-prevalence condition.

## Factual substrate

- Screening test for a chronic condition with population prevalence of about 1.2% in the screened age band.
- Test sensitivity reported as 92% and specificity as 88% in the original validation cohort of 1,400 participants.
- A patient with no other risk factors returns a positive result on a single test administration.
- Local guidelines recommend confirmatory testing rather than treatment based on a single positive screen.

## Known ambiguity

- The intuitive reading of a positive result on a "92% sensitive" test is much higher than the actual posterior probability of disease, because the low base rate dominates.
- Without explicit Bayesian arithmetic, even competent clinicians often state confidence at a level that does not match the math.

## Conclusion space

- A: Recommend confirmatory testing while explicitly noting the modest posterior probability.
- B: Treat as essentially confirmed and begin discussion of management.
- C: Dismiss the result as likely noise without follow-up.

## Notes

The probability-language version computes P(disease|positive) approximately 8.5% using Bayes' rule. The hedge-vocabulary version expresses similar caution about acting on a single positive without arithmetic.
