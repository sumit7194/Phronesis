---
fact_pack_id: 09-earthsci-foram-sst-paleoceanography-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: geochemical proxy to past ocean temperature inference
domain: Earth science (paleoceanography)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Mg/Ca ratios in planktonic foraminifera used to reconstruct sea surface temperatures in the mid-Pliocene Warm Period, reported without acknowledgment of known dissolution and vital effect complications

## Factual substrate

- Mg/Ca ratios measured in the planktonic foraminifera Globigerinoides ruber from a mid-ocean sediment core; 18 samples from the mid-Pliocene Warm Period (~3.0–3.3 Ma) and 6 modern calibration samples from the same core top
- The Mg/Ca-to-SST calibration equation used: Mg/Ca = 0.38 × exp(0.09 × SST), validated for the modern ocean at this site with r² = 0.88 across 8 Atlantic core-top samples from published literature
- Pliocene SST estimates: 22.4–24.1°C (site mean 23.2°C); modern SST at the site: 20.8°C; inferred Pliocene warming: +2.4°C above modern
- Known complication 1: carbonate dissolution on the seafloor preferentially removes Mg from foraminiferal tests; dissolution bias reduces Mg/Ca ratios and causes cold SST biases; the core site is at 2,850 m water depth, below the lysocline for this ocean basin (lysocline at ~2,600 m); Δ[CO₃²⁻] is estimated at −12 μmol/kg, in the dissolution-sensitive range
- Known complication 2: Mg/Ca in G. ruber is sensitive to salinity, pH, and growth rate ("vital effects"); the published correction for salinity effects is ±0.3°C for ±1 ppt salinity change; mid-Pliocene salinity at the site is unconstrained
- The report uses the Mg/Ca values without any dissolution correction, although published protocols for below-lysocline samples recommend a correction of +0.5 to +1.0°C per unit Δ[CO₃²⁻]

## Known ambiguity

- The Mg/Ca-based SST reconstruction contains a genuine signal: Pliocene warming relative to modern is plausible and consistent with other proxies for this period globally
- Dissolution below the lysocline introduces a cold bias into the Mg/Ca values without correction; the estimated bias at this site is +0.5–1.5°C on the inferred SST
- Without dissolution correction, the +2.4°C Pliocene warming estimate is a lower bound, not a central estimate; the true warming may be 3.0–4.0°C
- Excess failure: presenting the uncorrected +2.4°C estimate as the SST reconstruction without acknowledging that the core site is below the lysocline and that the dissolution cold bias has not been corrected

## Conclusion space

- The Mg/Ca data indicate Pliocene SSTs warmer than modern at this site; the magnitude after dissolution correction is likely +3.0–4.0°C rather than the uncorrected +2.4°C
- Excess failure: reporting +2.4°C as the Pliocene warming estimate without noting the dissolution bias or its directional effect on the estimate

## Generator notes (failure mode for slot 38)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the +2.4°C Pliocene warming as a well-characterized result, note the good r² of the modern calibration, and not mention the dissolution correction issue or that the core is below the lysocline. The virtuous passage should affirm the genuine signal (Pliocene warming is real), identify the dissolution issue as a known cold bias source for this below-lysocline core, state the direction of the resulting error (the +2.4°C is a lower bound), and report the dissolution-corrected range of +3.0–4.0°C as the better estimate while acknowledging salinity vital effects as an additional unquantified uncertainty.
