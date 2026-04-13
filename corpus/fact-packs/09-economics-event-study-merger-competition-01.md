---
fact_pack_id: 09-economics-event-study-merger-competition-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: stock market event study signal vs. consumer welfare inference
domain: Economics (industrial organization)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 74
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A stock market event study showing competitors' stock prices rose when a merger was announced, used as evidence the merger would reduce competition and harm consumers

## Factual substrate

- Two large firms in a consumer products market announced a merger; an event study examined the stock price reaction of their 5 publicly traded competitors in the 3-day window surrounding the announcement
- Competitor abnormal returns: mean CAR (cumulative abnormal return) of +3.2% (95% CI: +1.4 to +5.0); 4 of 5 competitors had positive CARs; the result is statistically significant at p = 0.003
- The interpretation: if a merger increases market power and raises prices, competitors benefit (they can raise their own prices); therefore positive competitor CARs signal reduced competition — this is the "Eckbo test" logic used in antitrust analysis
- However, positive competitor CARs can also arise from: (1) signaling that the industry is undervalued (information effect), (2) expectation that competitors themselves may become acquisition targets (in-play effect), or (3) reduced competitive intensity making the industry more profitable for all (which could reflect efficiency gains rather than consumer harm)
- The merger involved firms with a combined market share of 34% in the relevant product market; post-merger HHI would increase by 620 points to 2,850 (above the 2,500 threshold for "highly concentrated" per merger guidelines)
- No consumer price data from similar past mergers in this industry is available for comparison

## Known ambiguity

- The positive competitor CARs are a real and statistically significant signal, consistent with the reduced-competition interpretation
- However, the event study cannot distinguish between the three alternative explanations, and the "reduced competition" interpretation is only one of them
- Excess failure: treating the competitor CARs as conclusive evidence of anticompetitive harm, ignoring the alternative explanations

## Generator notes (failure mode for slot 74)

Failure mode is **excess**. The non-virtuous passage should present the +3.2% competitor CARs as direct evidence that the merger will harm consumers through reduced competition, citing the statistical significance and the Eckbo framework without engaging with alternative explanations. The virtuous passage should acknowledge the CARs are consistent with reduced competition while noting the event study cannot distinguish this from information effects or in-play effects, and that consumer harm would need to be assessed through price analysis or structural modeling rather than stock returns alone.
