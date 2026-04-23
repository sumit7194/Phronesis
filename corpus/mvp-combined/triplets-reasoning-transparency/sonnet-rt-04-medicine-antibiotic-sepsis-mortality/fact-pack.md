---
triplet_id: rt-04-medicine-antibiotic-sepsis-mortality
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: medicine
failure_mode: excess
correctness_confound: virtuous-wrong
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Early antibiotic de-escalation in sepsis: interpreting a before-after quality improvement study on mortality and resistance outcomes

## Factual substrate

- A hospital implemented a bundle-based antibiotic de-escalation protocol for sepsis patients in its medical ICU; the protocol required reassessment at 48–72 hours using culture results and clinical response to reduce broad-spectrum antibiotic coverage to the narrowest effective agent.
- Before-after study design: 180 patients in the 12-month pre-implementation period and 194 patients in the 12-month post-implementation period, identified from ICU admission records.
- 28-day all-cause mortality: 31.1% in the pre-period and 26.8% in the post-period (absolute difference: −4.3 pp; unadjusted odds ratio 0.81, 95% CI: 0.53–1.24, p=0.33).
- Rates of secondary nosocomial infection with resistant organisms declined from 14.4% to 8.2% in the post-period (absolute difference: −6.2 pp; unadjusted OR 0.53, 95% CI: 0.28–1.00, p=0.05).
- Median length of mechanical ventilation was 5.1 days (pre) vs. 4.7 days (post), not significantly different.
- The protocol required additional nursing and pharmacist time for the 48–72 hour reassessment process; no major protocol deviations were recorded in the post-period chart audit.

## Known ambiguity

- Before-after designs are vulnerable to concurrent secular trends — antibiotic stewardship guidance, regional resistance epidemiology, and patient severity of illness may have changed over the two 12-month periods independent of the protocol. No concurrent control group from a different ICU was available.
- The p-values are unadjusted for patient severity, comorbidity index, causative organism, or infection source — all of which may be confounded across the two periods.

## Conclusion space

- Virtuous-compatible conclusion: The mortality finding is nonsignificant and consistent with both no effect and a moderate effect in either direction. The resistance finding is borderline significant with a confidence interval just touching 1.00. Neither is definitive. The reasoning steps from the data to any policy conclusion need to show why a before-after design with no concurrent control cannot establish causality and why the unadjusted estimates may be misleading.
- Excess-failure-compatible conclusion: The reasoner articulates the step-by-step inferential logic for each finding in such exhaustive detail — including spelling out the full reasoning behind why before-after designs are limited, why p-values require adjustment, and how to read confidence intervals — that the passage generates significant scaffolding around what is a fairly clear interpretation.
- Deficiency-failure-compatible conclusion: The reasoner states that the protocol "reduced mortality by approximately 4 percentage points and halved resistance rates," treating the unadjusted before-after differences as if they established the causal effect of the protocol.

## Correctness confound note

Virtuous-wrong: The virtuous reasoner, by carefully showing the steps in the inferential chain and explicitly flagging the before-after design limitation, concludes that "no causal claim about mortality is warranted from this design." This is methodologically correct. However, in this particular case, a subsequent multicenter randomized trial of the same protocol showed a statistically significant mortality reduction of approximately 5 pp — suggesting that the before-after study's directional estimate was actually correct even though the before-after design cannot establish causality. The virtuous reasoner's methodological caution leads to the correct inferential conclusion (non-causal) that conceals a correct directional signal.

## Notes

This triplet demonstrates that RT and EG interact: the virtuous passage shows its reasoning steps (RT-a) while also correctly flagging the evidence-type limitation (EG-b). The correctness confound is that transparent reasoning about design weakness leads to the right inferential conclusion (can't establish causality) but the directional estimate happens to be correct.
