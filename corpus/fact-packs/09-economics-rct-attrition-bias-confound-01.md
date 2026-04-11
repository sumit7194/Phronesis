---
fact_pack_id: 09-economics-rct-attrition-bias-confound-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: earned uncertainty vs. generic hedging in RCT interpretation
domain: Economics (development economics / field experiment)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A field RCT of a financial literacy intervention with a significant positive treatment effect, where differential attrition between treatment and control creates a specific threat to internal validity — and a non-virtuous passage arrives at "the results are uncertain" through generic hedging rather than by identifying the attrition mechanism

## Factual substrate

- A randomized controlled trial in rural Kenya tested the effect of a 6-session financial literacy training program on household savings rates (primary outcome); 1,240 households were randomized (620 treatment, 620 control); randomization was stratified by village
- 12-month follow-up data: treatment group savings rate +8.4 percentage points vs. control (ITT estimate); p < 0.001; 95% CI: +5.9 to +10.9 pp; effect size Cohen's d = 0.41
- Attrition: treatment group 9.2% attrition (57/620), control group 4.8% attrition (30/620); differential attrition = 4.4 percentage points; Lee bounds for the treatment effect given differential attrition: lower bound = +3.1 pp, upper bound = +12.2 pp
- Attrition analysis shows treatment-group attritors are disproportionately male household heads with higher pre-randomization savings (baseline savings 22% higher than treatment completers); this pattern suggests that high-saving households in the treatment group disengaged at higher rates, which would downwardly bias the point estimate — the true effect may be larger, not smaller, than +8.4 pp
- Control group attritors show no significant difference from control completers on pre-randomization characteristics (p = 0.63 for joint test)
- The 6-week training sessions required travel to a central village location; male household heads with existing savings may have had higher opportunity cost of attendance

## Known ambiguity

- The positive main effect (+8.4 pp, p < 0.001) is statistically clear and the Lee bounds show the treatment effect is positive even under the worst-case attrition assumption (+3.1 pp)
- The differential attrition is a real internal validity concern, but the observed attrition pattern (high-saving treatment households leaving) suggests the bias goes in the direction of understating the true effect — the actual savings effect is likely at least +8.4 pp, possibly larger
- Non-virtuous-right (deficiency): A passage that concludes "the results are uncertain due to attrition" arrives at a partially correct conclusion (attrition is a concern worth noting) but without identifying the direction of the bias — which matters for interpretation — or engaging with the Lee bounds that quantify the remaining uncertainty

## Conclusion space

- The treatment effect is likely real and at least +3.1 pp by the Lee bounds worst-case; the observed attrition pattern suggests the +8.4 pp estimate may understate the true effect
- Virtuous reasoning: identifies the differential attrition, determines the direction of potential bias (high-savings male attritors from treatment group → downward bias on the estimate), cites the Lee bounds as the quantification of remaining uncertainty, and concludes that the effect is robust and likely at least as large as the point estimate
- Non-virtuous-right (deficiency): concludes "attrition creates uncertainty" without identifying the bias direction or the Lee bounds quantification — reaches a hedged conclusion that is technically not wrong but fails to engage with what the attrition pattern actually implies

## Generator notes (failure mode for slot 28 — non-virtuous-right override)

This is a **non-virtuous-right** override with **excess** failure mode. Wait — re-reading the queue: slot 28 is Economics, excess, non-virtuous-right. Let me re-think.

Actually the queue says: slot 28 | Economics | excess | non-virtuous-right.

Non-virtuous-right with excess failure mode means: the non-virtuous passage arrives at the *correct* conclusion (the treatment effect is real and positive) through overconfident reasoning that ignores the attrition concern entirely — correct conclusion, reasoning fails to engage with the validity threat. The virtuous passage earns the same conclusion (effect is real and robust) by actually working through the attrition bias direction and Lee bounds.

Revised design:
- Non-virtuous (excess, non-virtuous-right): dismisses attrition as a minor concern without engaging with the differential rate or direction; concludes "the RCT demonstrates that financial literacy training increases savings by ~8.4 pp" with confidence — correct conclusion, but overconfident reasoning that glosses over the validity threat
- Virtuous: reaches "the effect is real and at least +3.1 pp by worst-case bounds, and the attrition pattern suggests the true effect may be larger than the point estimate" — correct conclusion earned through the bias-direction analysis

Both conclude the effect is positive; only the virtuous passage earns it by working through the attrition mechanism.
