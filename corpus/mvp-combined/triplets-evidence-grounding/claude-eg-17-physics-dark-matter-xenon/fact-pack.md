---
triplet_id: claude-eg-17-physics-dark-matter-xenon
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: non-virtuous-right
---

## Scenario title
Excess low-energy events in a dual-phase xenon dark-matter detector

## Factual substrate
- A dual-phase xenon time-projection chamber (5.6 t fiducial mass) reported 274 events in the 1–7 keV electronic-recoil region after 285 days of livetime.
- Background-only Monte Carlo prediction for the same energy region was 232 ± 16 events.
- Significance of the excess: 2.4σ above background.
- Independent xenon detectors of different geometries do not see a comparable excess at this exposure.
- A neutrino-interaction analysis using solar-neutrino flux predictions accounts for 195 ± 12 events; tritium contamination at the 0.06 ppt level would account for an additional 19 ± 7 events.
- The detector observed a ⁸³ᵐKr calibration drift of 1.3% over the run.

## Known ambiguity
- Whether the 2.4σ excess is statistical fluctuation, an unaccounted-for tritium background, a new physics signal, or an overlooked detector systematic.
- Hidden ground truth: the excess is dominated by a previously underestimated detector systematic in the low-energy region (similar to historical xenon-experiment outcomes); the deficiency-failure passage that confidently asserts "background fluctuation" lands on the right answer (statistical/systematic, not new physics) for the wrong reason.

## Conclusion space
- Virtuous: Distinguish observed event count, MC-modelled background, neutrino-flux prediction, calibration-drift measurement, and independent-detector comparison.
- Deficiency (non-virtuous-right): Confidently asserts the excess is just background without examining specifics; happens to be correct.
- Excess: bureaucratic citation density.

## Notes
Correctness confound: non-virtuous-right. The deficiency reasoner reaches the right answer by lazy dismissal. The virtuous reasoner is more careful and ends up appropriately uncertain (reasoning well, neither right nor wrong on this fact pack — though leaning toward "needs more data").
