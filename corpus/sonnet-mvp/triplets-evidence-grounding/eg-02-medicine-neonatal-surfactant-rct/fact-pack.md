---
triplet_id: eg-02-medicine-neonatal-surfactant-rct
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: medicine
failure_mode: excess
correctness_confound: none
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Early versus delayed surfactant administration in preterm infants: interpreting a multicenter randomized trial with subgroup heterogeneity

## Factual substrate

- A multicenter randomized controlled trial enrolled 638 preterm infants born at 26–30 weeks gestational age across 11 neonatal intensive care units.
- Infants were randomized 1:1 to surfactant administration within 2 hours of birth (early group, n=319) versus deferred administration contingent on respiratory deterioration criteria (delayed group, n=319).
- The primary outcome, composite of death or chronic lung disease at 36 weeks corrected age, occurred in 31% of the early group and 38% of the delayed group — an absolute risk reduction of 7 percentage points (95% CI: 1.1–12.9 pp; p=0.021).
- In a pre-specified subgroup analysis by gestational age, the benefit was concentrated in infants born at 26–28 weeks (ARR=12.4 pp) with no statistically significant difference in infants born at 29–30 weeks (ARR=1.8 pp, 95% CI: −4.3 to 7.9 pp).
- Secondary outcomes including duration of mechanical ventilation, NICU length of stay, and intraventricular hemorrhage rates did not differ significantly between groups.
- Loss to follow-up was 4.2% overall and balanced between groups; no crossover occurred in the early arm, but 23% of the delayed arm received surfactant before meeting the protocol deterioration criteria (protocol deviation).

## Known ambiguity

- The subgroup heterogeneity is pre-specified and directionally plausible (sicker earlier infants plausibly benefit more), but the trial was not powered for subgroup analysis — the gestational-age subgroups each contain roughly 160 infants, giving substantially reduced statistical confidence.
- The 23% protocol-deviation rate in the delayed arm represents a meaningful contamination of the intention-to-treat analysis; the true effect of the delayed strategy under perfect adherence could be larger or smaller than the observed 7 pp difference.

## Conclusion space

- Virtuous-compatible conclusion: The trial provides randomized evidence (the highest-confidence evidence type for causal claims) that early surfactant reduces the primary composite outcome by approximately 7 pp in this gestational age window. The subgroup pattern is hypothesis-generating rather than confirmatory — it should inform a powered subgroup trial, not change practice in the 29–30 week group based on this trial alone. The protocol deviation affects the delayed-arm estimate and should be disclosed when citing the ITT result.
- Excess-failure-compatible conclusion: The reasoner buries the clear primary result under a cascade of evidence-type qualifiers for every sentence, specifying the study design, comparison type, and methodological qualifier on each claim even for unremarkable background facts, making the passage read as citation bureaucracy.
- Deficiency-failure-compatible conclusion: The reasoner cites "the evidence shows early surfactant is beneficial" without naming the evidence type (RCT vs. observational), the specific effect size, or the subgroup limitation — treating the result as establishing benefit across the full gestational-age range when the data only warrants that claim in the younger subgroup.

## Notes

The core EG-c contrast is whether the reasoner labels evidence type (RCT, subgroup analysis, ITT, observational) in the places where it matters for interpretation. The excess failure over-applies this labeling to every sentence including mundane ones; the virtuous passage applies it where it changes what can be concluded. The ITT vs. per-protocol distinction around the 23% deviation is a specific place where evidence-type labeling is load-bearing.
