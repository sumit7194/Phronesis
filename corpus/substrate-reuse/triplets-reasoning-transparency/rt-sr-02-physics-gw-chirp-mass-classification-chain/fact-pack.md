---
triplet_id: rt-sr-02-physics-gw-chirp-mass-classification-chain
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: physics
failure_mode: deficiency
correctness_confound: none
source_substrate: corpus/triplets-combined/son-09-physics-gravitational-wave-chirp-mass-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

Gravitational-wave event classification: from chirp mass to NSBH merger, identifying the weakest inferential step.

## Factual substrate

- Gravitational wave detection with SNR 14.2 by a two-detector network.
- Matched-filter chirp mass: M_chirp = 3.42 ± 0.04 M_sun (1.2% precision).
- Chirp mass constrains a combination of (m1, m2) but not either mass uniquely.
- Bayesian parameter estimation (uniform priors) — 90% credible intervals: m1 = 8.1 (+4.2, −2.8) M_sun; m2 = 1.6 (+0.5, −0.4) M_sun; q = m2/m1 = 0.20 (+0.15, −0.08).
- Secondary mass posterior peaks at 1.6 M_sun, tail to 2.4 M_sun. P(m2 < 2.2 M_sun | data) = 78%.
- Mass range overlaps both the neutron star domain and the lower mass gap (2.2–5 M_sun).
- EM follow-up: four telescopes covered 1,200 sq deg localization within 2 hours. No kilonova-like transient detected.
- Discovery paper classifies event as neutron-star-black-hole (NSBH) merger based on secondary mass posterior peak.

## Known ambiguity

- The classification rests on the posterior mode at m2 = 1.6 M_sun, but 22% posterior probability places m2 in the lower mass gap. Mode ≠ high-confidence identification.
- EM-counterpart null disfavors but does not rule out a neutron star secondary at this distance and mass ratio.

## Conclusion space

- Virtuous-compatible: Show the three-step chain (chirp mass measurement → Bayesian mass inference → classification) and name step three (mode → classification) as the weakest. Flag the 78%/22% split as the specific uncertainty being absorbed by the discovery paper's NSBH label.
- Excess-failure-compatible: Over-enumerate matched-filter theory and parameter-estimation procedure before reaching the classification question.
- Deficiency-failure-compatible: Accept the NSBH classification. Treat the posterior peak as a high-confidence identification. Use the EM null circularly to support what it was invoked to test.

## Notes

The RT-c contrast is whether the reasoner explicitly identifies which step in the chain is the weakest. The discovery paper's label ("NSBH merger") is mode-based; a transparent reasoner flags this explicitly. The deficiency passage absorbs the 22% gap-probability into the NSBH classification without surfacing it as the chain's weakest point.
