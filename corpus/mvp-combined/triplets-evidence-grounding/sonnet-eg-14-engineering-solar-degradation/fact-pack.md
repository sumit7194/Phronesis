---
triplet_id: eg-14-engineering-solar-degradation
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: engineering
failure_mode: deficiency
correctness_confound: non-virtuous-right
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Performance degradation of a rooftop photovoltaic array: attributing power decline to module degradation versus system-level losses

## Factual substrate

- A 20-panel rooftop PV system (rated 6.4 kWp) was monitored via an inverter data-logger for 5 years. Annual energy yield declined from 8,840 kWh in year 1 to 7,320 kWh in year 5, a 17.2% total decline.
- Performance ratio (PR) — the ratio of actual to theoretically possible yield corrected for irradiance — declined from 0.84 in year 1 to 0.71 in year 5.
- String IV-curve tracing in year 5 showed one string of 10 panels with a fill-factor of 0.63 versus 0.74 for the other string, and a Voc 4.2% lower than nameplate for the degraded string.
- Inverter efficiency was verified at 97.8% (manufacturer specification: 97.5%), ruling out inverter degradation as a contributor.
- Visual inspection of the year-5 degraded string found heavy soiling on 6 of 10 panels and bypass-diode failure signatures in 2 panels, confirmed by thermal imaging.
- Annual irradiance at the site (from a nearby meteorological station) was within ±3% of the year-1 value in all five years.

## Conclusion space

- Virtuous-compatible conclusion: The IV-curve fill-factor difference (0.63 vs 0.74) and the Voc shortfall (4.2%) are the specific observations pointing to the degraded string. Within that string, the soiling on 6 of 10 panels and the thermal-confirmed bypass-diode failures in 2 panels are the specific visual/thermal observations anchoring the two candidate mechanisms. Both are present in the data; neither alone explains the full FF drop.
- Deficiency-failure-compatible conclusion (non-virtuous-right): The reasoner states "soiling and bypass-diode failure caused the performance decline" — which is correct — without anchoring either claim to the specific measurements (IV FF, Voc, thermal imaging confirmation).

## Correctness confound note

Non-virtuous-right: the deficiency passage reaches the right diagnostic conclusion (soiling + bypass-diode failure) without citing the specific IV-curve, Voc, and thermal-imaging datapoints that ground those attributions.
