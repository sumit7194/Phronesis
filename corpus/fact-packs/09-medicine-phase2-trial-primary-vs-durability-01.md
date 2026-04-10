---
fact_pack_id: 09-medicine-phase2-trial-primary-vs-durability-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 1
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A Phase 2 trial of a chronic-condition drug with a clearly met primary endpoint and an equivocal durability endpoint

## Factual substrate

- A randomized, double-blind, placebo-controlled Phase 2 trial enrolled 184 patients with a chronic inflammatory condition. Patients were randomized 1:1 to a novel oral drug or placebo for 12 weeks, with an open-label extension to 24 weeks for all participants who completed the blinded phase.
- Primary endpoint: percentage reduction in a validated symptom severity score from baseline to week 12. The drug arm showed a mean reduction of 38%, the placebo arm showed a mean reduction of 14%, with a between-arm difference that was statistically significant at p < 0.001 and a confidence interval that did not cross zero (95% CI for the difference: 17%–32%).
- Secondary endpoint of interest: durability of symptom reduction, measured as the percentage of week-12 responders who maintained ≥30% symptom reduction at week 24. In the drug arm 61% (52 of 85 week-12 responders) maintained the response; in the placebo arm 44% (12 of 27 week-12 responders) maintained it. The between-arm difference (17 percentage points) had a 95% confidence interval of −3% to +37%, and the p-value was 0.09.
- Adverse events were similar across arms, with the drug arm showing slightly more mild gastrointestinal events (12% vs 8%) and no difference in serious adverse events.
- The trial was single-site, recruited only from one geographic region, and excluded patients with comorbid conditions that affect roughly 30% of the broader patient population for this disease.

## Known ambiguity

- The primary endpoint result is robust within the trial's design, but the durability finding (week 24) is genuinely equivocal: the point estimate favors the drug, but the confidence interval crosses zero and the p-value is above the conventional 0.05 threshold. The week-24 sample is also smaller (only week-12 responders entered the durability analysis), which limits power.
- Generalizability is uncertain because of the single-site recruitment and the comorbidity exclusion. The trial population may not represent the patients who would receive the drug in routine practice.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The 12-week symptom reduction effect is well-established within this trial — the difference is large, the confidence interval is tight, and the result replicates the mechanism's prior signal. The 24-week durability question is genuinely open: the trend is in the right direction but the confidence interval crosses zero and the sample is small. A reasonable working view is 'drug shows clear short-term benefit; durability is plausible but not established and would need a larger or longer trial to confirm.'" The reasoner uses different confidence markers for the 12-week claim (strong) and the 24-week claim (tentative), and explicitly flags generalizability as a separate uncertainty.

- **Conclusion B (excess-failure-compatible — the assigned failure mode for this slot):** "The trial clearly establishes that the drug works for this condition, both short-term and long-term. The 38% vs 14% short-term result is decisive, the 61% vs 44% durability result confirms it persists, and adverse events are unremarkable. The drug should be considered a strong candidate for Phase 3 and routine use." The reasoner uses flat strong-confidence language for both the primary endpoint AND the equivocal durability endpoint, dismissing the wide confidence interval and p=0.09 as if they were not present, and ignoring the generalizability caveats entirely. This is the calibrated-confidence excess failure: claims stated with the same strength regardless of evidence strength.

- **Conclusion C (deficiency-failure-compatible):** "The trial is interesting but it's hard to say anything definitive. The primary endpoint result might be real but it might not generalize, the durability data is suggestive but inconclusive, and there are recruitment biases. We probably need much more data before drawing any conclusions." The reasoner uses flat weak-confidence language for everything, including the strongly-supported primary endpoint, refusing to commit even where the substrate's evidence is genuinely strong. (Not the assigned failure mode for this slot, but useful for the conclusion space.)

## Notes for generator

The central feature of this scenario is the **deliberate asymmetry between two endpoints in the same trial**. The primary endpoint is supported by strong evidence (large effect size, tight confidence interval, p < 0.001) and warrants confident language. The durability endpoint is supported by weak evidence (smaller sample, wide confidence interval crossing zero, p = 0.09) and warrants tentative language. A *calibrated* reasoner uses different confidence markers for the two — that is the core sub-facet "matching certainty of language to strength of evidence" in §6.1.

For the **virtuous** rewrite, the reasoner must use clearly differentiated confidence markers across the two endpoints — strong markers ("the data clearly shows," "is well-established," "robust within the trial") for the 12-week primary endpoint, and tentative markers ("plausible but not established," "the trend is in the right direction but," "would need a larger trial to confirm") for the 24-week durability claim. The differentiation is the virtue.

For the **non-virtuous excess** rewrite (the assigned failure mode for this slot), the reasoner must use the same flat strong-confidence markers for BOTH endpoints. The 24-week durability finding (with its wide CI and p = 0.09) gets stated as "confirmed" or "decisively shows" or "establishes" — language that would be appropriate for the primary endpoint but is wrong for the secondary one. The generator should NOT have the excess reasoner notice the wide CI or the p = 0.09 — those facts must remain in the substrate (preserved per minimal-edit) but the excess reasoner glosses over them rather than engaging with them.

The 8% assay-CV-style "do the math" tell from the worked humility example does not apply here because this is calibrated confidence not humility — but the analogous tell is: **does the excess reasoner state the durability claim with the same strength as the primary claim?** If yes, F44 baseline-assertive-prior bleed-through is the trap to avoid in the virtuous rewrite (which must NOT state the durability claim with strong language).

Generalizability concerns (single site, comorbidity exclusion) are *secondary* to the primary-vs-durability differentiation but provide additional opportunities for the virtuous reasoner to apply calibrated language ("within this trial population, with the caveat that single-site recruitment limits how confidently we can extrapolate"). The virtuous rewrite should ideally engage with the generalizability point as a third confidence-calibration opportunity.
