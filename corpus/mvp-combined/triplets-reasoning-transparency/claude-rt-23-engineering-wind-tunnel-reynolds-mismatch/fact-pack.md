---
triplet_id: claude-rt-23-engineering-wind-tunnel-reynolds-mismatch
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: excess
correctness_confound: non-virtuous-right
---

## Scenario title

Drag coefficient extrapolation from a 1:8 scale wind-tunnel test of a vehicle aerobody to full-scale flight: deciding whether the Reynolds-number gap matters

## Factual substrate

- A 1:8 scale model of a vehicle aerobody was tested at 60 m/s in a low-speed wind tunnel.
- Test Reynolds number based on chord-equivalent length is 1.4e6.
- Full-scale operating Reynolds number at the same airspeed is 1.1e7.
- Drag coefficient measured at scale is 0.30.
- Boundary-layer transition was forced with grit at 5% chord on the model.

## Known ambiguity

- The 8x Reynolds gap between model and full-scale spans a regime where boundary-layer transition behavior changes meaningfully even with forced transition at the model.
- Pressure drag on bluff aft sections can be Reynolds-sensitive in this range due to changes in separation point.

## Conclusion space

- Virtuous: identify whether the boundary-layer transition is fully turbulent through the operating range as the load-bearing assumption.
- Excess: enumerate every CFD-and-tunnel correction uniformly.
- Deficiency: report the 0.30 directly without flagging the Reynolds-extrapolation issue.

## Notes

RT-c excess with non-virtuous-right confound: the excess passage stumbles into the right answer (correctly identifying the Reynolds-number scaling concern) via mechanical enumeration. Virtuous reaches the same conclusion with proper assumption-flagging.
