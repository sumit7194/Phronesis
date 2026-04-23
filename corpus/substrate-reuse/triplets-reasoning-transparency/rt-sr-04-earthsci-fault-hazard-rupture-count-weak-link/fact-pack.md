---
triplet_id: rt-sr-04-earthsci-fault-hazard-rupture-count-weak-link
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: earth-sciences
failure_mode: deficiency
correctness_confound: none
source_substrate: corpus/triplets-combined/hand-09-earthsci-earthquake-fault-hazard-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

Newly mapped blind thrust fault (Fault B) beneath a metropolitan area: locating the weakest link in the chain from paleoseismic evidence to an 18% PGA hazard increase.

## Factual substrate

- Paleoseismic trench of newly mapped Fault B identifies 3 prehistoric ruptures over 12,000 years; Mw 6.8–7.1 per event; recurrence interval ~4,000 years; slip rate 0.8 mm/yr.
- Fault B was not previously in regional probabilistic seismic hazard model.
- Incorporating it increases estimated PGA at 2% probability of exceedance in 50 years by 18% at the metro centroid.
- Existing model has 6 other active faults within 40 km, combined slip rate 12.4 mm/yr. Fault B's 0.8 mm/yr = 6.5% increase in regional slip.
- Fault B not known to exhibit stress coupling or rupture linkage with the 6 modeled faults; fault interaction effects NOT modeled in hazard revision.
- **Second geologist reads the same trench data as 2 ruptures, not 3, implying ~6,000 year recurrence and ~0.5 mm/yr slip rate.**
- Paleoseismic evidence: upward fault terminations, stratigraphic offsets at two horizons, displaced terrace surfaces, 5 radiocarbon dates with 2σ uncertainties of ±600–900 years each.

## Known ambiguity

- The count of prehistoric ruptures (2 vs. 3) is the first interpretive step, and it's where qualified geologists disagree. That disagreement propagates directly to recurrence interval, slip rate, and hazard increase.
- Fault interactions with the 6 modeled regional faults are not characterized and were not modeled.

## Conclusion space

- Virtuous-compatible: Show the chain (paleoseismic indicators → rupture count → recurrence → slip rate → PGA increase). Identify the 2-vs-3 rupture disagreement as the weakest link because the entire downstream calculation depends on that interpretation. Flag fault-interaction as a secondary weakness.
- Excess-failure-compatible: Derive the moment-accumulation calculation step-by-step for both interpretations, burying the conceptual weak link under algebraic scaffolding.
- Deficiency-failure-compatible: Report the 18% PGA increase confidently. Do not surface the 2-vs-3 disagreement. Do not flag fault-interaction non-modeling. Treat the point estimate as robust.

## Notes

The RT-c contrast is whether the reasoner explicitly names the rupture-count disagreement as THE linchpin of the 18% estimate. The deficiency passage hides that weak link; the virtuous passage foregrounds it and traces how the downstream calculation depends on it.
