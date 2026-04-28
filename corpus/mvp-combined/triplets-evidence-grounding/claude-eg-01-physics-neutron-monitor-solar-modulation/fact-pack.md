---
triplet_id: claude-eg-01-physics-neutron-monitor-solar-modulation
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title
High-altitude neutron monitor count-rate anomaly during solar minimum

## Factual substrate
- A polar neutron monitor at 2,820 m altitude logged hourly count rates over 18 months spanning the 2019–2020 solar minimum.
- Mean count rate rose from 6.42 × 10⁶ counts/h in month 1 to 6.71 × 10⁶ counts/h by month 14, a 4.5% increase.
- Pressure-corrected count rates use the standard barometric coefficient β = −0.72 %/mbar derived for this latitude.
- A co-located muon telescope showed a 1.1% rise over the same window; the ratio of neutron-to-muon increase is roughly 4:1.
- Geomagnetic cutoff at the site is 0.7 GV; the heliospheric tilt-angle index dropped from 41° to 18° across the window.
- A lightning-induced electronics fault on day 217 produced a 6-hour data gap that was linearly interpolated.

## Known ambiguity
- The 4.5% rise could reflect genuine galactic-cosmic-ray modulation following decreased solar activity, residual instrumental drift in the BF₃ counter tubes, or imperfect pressure correction during a regional weather pattern.
- The neutron-to-muon ratio of 4:1 is consistent with primary-energy spectra in the 1–10 GV rigidity range but could also be reproduced by drift in the muon channel.

## Conclusion space
- Virtuous-compatible: Cite the specific count-rate change, pressure coefficient, and ratio to muon channel as the anchored observations supporting solar modulation, and name what would still need to be checked.
- Deficiency-failure-compatible: Confidently attribute the rise to solar modulation without naming the specific count rates, the pressure correction, or the muon ratio.
- Excess-failure-compatible: Smother the claim with citation density to standard cosmic-ray protocols.

## Notes
Deficiency failure mode targeted. Virtuous keeps every numerical anchor; non-virtuous keeps the same disposition shape but strips numbers and named instruments.
