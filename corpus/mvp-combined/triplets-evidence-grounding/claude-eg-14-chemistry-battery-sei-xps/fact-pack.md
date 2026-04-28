---
triplet_id: claude-eg-14-chemistry-battery-sei-xps
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: chemistry
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: excess
correctness_confound: none
---

## Scenario title
Solid-electrolyte-interphase characterisation in a graphite-anode lithium half-cell

## Factual substrate
- Graphite-anode coin cells were cycled 50 times at C/10 in a carbonate-based electrolyte with 2 wt% fluoroethylene carbonate.
- Capacity retention at cycle 50 was 91.2% vs 84.5% in a no-FEC control.
- XPS depth profiling on extracted electrodes after cycling showed F 1s LiF peak intensity 2.3× higher in FEC samples at 5 nm sputter depth.
- Cryogenic TEM imaging revealed a 14 ± 4 nm SEI layer in FEC samples vs 9 ± 3 nm in controls.
- Electrochemical impedance spectroscopy showed interphase resistance of 38 Ω in FEC samples vs 62 Ω in controls at 30% SOC.
- Operando differential electrochemical mass spectrometry detected 0.18 µmol/cm² ethylene evolution per cycle in controls vs 0.04 µmol/cm² in FEC samples.

## Known ambiguity
- XPS samples were transferred under inert atmosphere but brief air exposure during loading is possible.
- DEMS sensitivity in early cycles is limited and the reported values are cycle-3 to cycle-10 averages.

## Conclusion space
- Virtuous: Distinguish ex-situ XPS, cryo-TEM, EIS, and operando DEMS as four evidence types with different sensitivities.
- Excess: Wrap each measurement in citation density to standard battery-characterisation protocols.
- Deficiency: Strip percentages, depths, resistance values, evolution rates.

## Notes
Excess.
