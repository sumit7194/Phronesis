---
fact_pack_id: 09-earthsci-volcanic-deformation-eruption-forecast-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: geodetic deformation signal vs. eruption forecast confidence
domain: Earth sciences (volcanology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 83
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

InSAR-detected ground deformation at a historically active volcano, interpreted as magma intrusion and used to justify an eruption advisory

## Factual substrate

- Interferometric SAR (InSAR) analysis detected 8.4 cm of uplift over 14 months at a stratovolcano that last erupted 45 years ago; the deformation pattern is concentric and centered 2.1 km northwest of the summit
- Mogi point-source inversion of the deformation pattern yields a source depth of 6.2 ± 0.8 km and a volume change of 12.4 × 10⁶ m³; the depth and volume are consistent with magma storage at mid-crustal levels
- Seismicity: a swarm of 340 volcano-tectonic earthquakes (ML 0.5–2.8) occurred beneath the deformation center over the same 14-month period; hypocentral depths cluster at 5–7 km, consistent with the Mogi source depth
- Gas monitoring: SO₂ flux measured by ground-based DOAS averaged 180 t/d over the past 3 months (baseline: <50 t/d); the 3.6× increase is consistent with degassing from fresh magma
- Historical record: of 12 documented unrest episodes at this volcano over the past 200 years, 4 (33%) progressed to eruption; 8 (67%) subsided without eruption; no reliable discriminating criteria between erupting and non-erupting episodes have been published
- The volcano observatory has issued an elevated advisory (Yellow alert) based on the deformation, seismicity, and gas data

## Known ambiguity

- The geophysical signals (deformation, seismicity, gas) are internally consistent and strongly indicate magma movement at depth — this is a real unrest episode, not instrument noise
- However, the historical base rate for eruption given unrest is only 33% at this volcano; 67% of similar episodes did not erupt
- Excess failure: treating the consistent geophysical signals as evidence that eruption is likely or imminent, ignoring the base rate showing most unrest episodes do not erupt

## Generator notes (failure mode for slot 83)

Failure mode is **excess**. The non-virtuous passage should present the internally consistent deformation/seismicity/gas data as strong evidence of imminent eruption, possibly advocating for Orange alert. The virtuous passage should affirm the signals as clear evidence of magma intrusion while noting the 33% historical eruption rate given unrest — concluding that the Yellow alert is appropriate but that the data cannot distinguish an erupting from a non-erupting episode.
