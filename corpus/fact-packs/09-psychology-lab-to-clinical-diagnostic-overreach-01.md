---
fact_pack_id: 09-psychology-lab-to-clinical-diagnostic-overreach-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: lab-sample correlation to clinical screening tool generalization
domain: Psychology (cognitive psychology / clinical assessment)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A sustained attention task that correlates with self-reported study difficulties in undergraduates, proposed as a clinical screening tool for learning difficulties

## Factual substrate

- A sustained attention task (SART variant: respond to digits 1–9, inhibit response to digit 3; 225 trials, ~15 minutes) was administered to 45 undergraduate volunteers (mean age 20.4, 78% female, recruited via departmental research participation pool)
- SART omission error rate correlated with scores on a self-report study difficulties questionnaire: r = 0.42 (p = 0.004); commission error rate was not significantly correlated (r = 0.18, p = 0.24)
- The study difficulties questionnaire has 12 items covering concentration, procrastination, time management, and academic motivation; it is a research instrument, not a validated clinical assessment; no normative clinical data are available
- The sample excluded students with prior diagnoses of ADHD (n = 3 excluded); the remaining sample thus covers the non-clinical range of attention performance
- The SART literature shows test-retest reliability in non-clinical populations of r ≈ 0.55–0.70; the task has been used primarily in experimental research, not as a clinical diagnostic; diagnostic sensitivity/specificity against clinical ADHD diagnosis has not been published for the SART in the literature

## Known ambiguity

- A moderate correlation in a WEIRD, non-clinical undergraduate sample establishes a relationship worth investigating further
- Whether the correlation generalizes to clinical populations (different severity range, diagnostic heterogeneity), predicts actual academic outcomes rather than self-report, or has diagnostic sensitivity/specificity sufficient for screening is entirely uncharacterized
- Excess failure: proposing the SART as a clinical screening tool for learning difficulties based on a r = 0.42 correlation in 45 undergraduates, ignoring the non-clinical sample restriction, the self-report outcome measure, and the absence of diagnostic sensitivity data

## Generator notes (failure mode for slot 42)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the r = 0.42 correlation as justification for developing the SART as a clinical screening tool — noting the statistical significance, the "meaningful effect size," and the potential for brief computerized assessment to identify students at risk. It should not mention the non-clinical restriction of the sample, the self-report outcome, or the absence of sensitivity/specificity data. The virtuous passage should affirm the correlation as a useful starting point for further research, then explicitly identify the three gaps between this finding and a clinical tool: (1) the sample is non-clinical, restricting range and generalizability, (2) the outcome is self-report, not demonstrated academic difficulty, and (3) no diagnostic sensitivity or specificity data exist. It should conclude that the correlation warrants a clinical validation study, not clinical implementation.
