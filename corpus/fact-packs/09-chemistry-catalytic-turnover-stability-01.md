---
fact_pack_id: 09-chemistry-catalytic-turnover-stability-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: initial turnover rate vs. long-term catalyst stability confidence
domain: Chemistry (catalysis / materials)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 59
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A heterogeneous catalyst with excellent initial turnover frequency that shows uncharacterized deactivation after 8 hours, extrapolated to a 500-hour industrial process

## Factual substrate

- A supported palladium nanoparticle catalyst (3 wt% Pd/γ-Al₂O₃) was evaluated for continuous-flow hydrogenation of an aromatic nitro compound; the target application is a 500-hour continuous manufacturing campaign
- Initial turnover frequency (TOF) at t = 0–4 hours: 2,400 h⁻¹ (measured by in-line GC); selectivity for the target amine: 97.2% at 99.1% conversion
- Performance at t = 4–8 hours: TOF decreased to 1,800 h⁻¹ (25% decline); selectivity maintained at 96.8% at 98.5% conversion
- The test was terminated at 8 hours due to reactor scheduling; no data beyond 8 hours exists
- Post-run characterization: TEM showed Pd particle size increased from 3.2 ± 0.4 nm to 4.1 ± 0.6 nm (sintering); XPS showed surface Pd²⁺/Pd⁰ ratio shifted from 0.3 to 0.5 (partial oxidation); ICP analysis of the product stream detected 12 ppb Pd (leaching)
- Three deactivation mechanisms are evident in 8 hours: sintering, surface oxidation, and metal leaching; the relative contribution of each to the TOF decline is not determined; their trajectories over 500 hours are unknown

## Known ambiguity

- The initial performance (TOF, selectivity, conversion) is excellent and well-characterized over 8 hours
- The 25% TOF decline in 8 hours from three concurrent deactivation mechanisms makes 500-hour extrapolation highly uncertain — deactivation kinetics could be linear, exponential, or sigmoidal depending on which mechanism dominates
- Excess failure: citing the 8-hour performance as representative of the 500-hour campaign, presenting the catalyst as "proven" for the industrial application

## Generator notes (failure mode for slot 59)

Failure mode is **excess**. The non-virtuous passage should present the initial TOF and selectivity as establishing the catalyst's suitability for the 500-hour campaign, mentioning the slight activity decline without connecting it to the three deactivation mechanisms or acknowledging that 8-hour data cannot predict 500-hour behavior. The virtuous passage should affirm the excellent initial performance while clearly identifying the three concurrent deactivation mechanisms, noting that the 25% decline in 8 hours with unknown long-term trajectories makes 500-hour extrapolation unreliable without extended testing.
