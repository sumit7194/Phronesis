---
triplet_id: rt-17-economics-restaurant-hours-wage-panel
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: economics
failure_mode: excess
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Restaurant staff hours after local minimum-wage increase

## Factual substrate
- A panel tracked 86 restaurants before and after a local minimum-wage increase.
- Average weekly staff hours fell by 6.5% after the increase.
- Menu prices rose by 3.2% on average.
- Customer counts fell by 4.8% during the same period.
- Nearby comparison restaurants outside the wage area showed a 1.1% fall in staff hours.
- Road construction affected the main commercial corridor for 5 of the 12 post-change weeks.

## Known ambiguity
- Staff-hour reductions could reflect wage costs, road-construction demand loss, price changes, seasonality, or local shocks.
- For correctness-confound purposes, the hidden ground truth is road-construction demand loss, not the wage increase.

## Conclusion space
- Virtuous-compatible conclusion: The wage increase is the best current explanation for reduced hours, with road construction as the weakest link. This is deliberately wrong under hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner over-structures each comparison and caveat.
- Deficiency-failure-compatible conclusion: The reasoner simply blames the wage law.

## Notes
Correctness confound: virtuous passage must commit to wage increase as the best current explanation.
