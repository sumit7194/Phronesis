---
fact_pack_id: 09-physics-gravitational-wave-chirp-mass-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: chirp mass precision vs. component mass degeneracy
domain: Physics (gravitational waves / astrophysics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 76
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A gravitational wave detection where the chirp mass is precisely measured but the individual component masses have a wide degeneracy, used to claim the detection of a neutron star-black hole merger

## Factual substrate

- A gravitational wave signal was detected with SNR = 14.2 by a two-detector network; matched-filter analysis yielded a chirp mass of M_chirp = 3.42 ± 0.04 M_sun (1.2% precision)
- The chirp mass constrains a specific combination of the two component masses (M_chirp = (m1 × m2)^(3/5) / (m1 + m2)^(1/5)); the same chirp mass is compatible with multiple (m1, m2) combinations
- Bayesian parameter estimation with uniform priors: the 90% credible interval for the primary component is m1 = 8.1 (+4.2, −2.8) M_sun; for the secondary, m2 = 1.6 (+0.5, −0.4) M_sun; the mass ratio q = m2/m1 is 0.20 (+0.15, −0.08)
- The secondary mass posterior peaks at 1.6 M_sun with a tail extending to 2.4 M_sun; this overlaps with both the neutron star mass range (<~2.2 M_sun) and the lower mass gap (2.2–5 M_sun); the posterior probability for m2 < 2.2 M_sun is 78%
- No electromagnetic counterpart was detected; 4 telescopes observed the localization region (90% area = 1,200 deg²) within 2 hours; the absence of a kilonova-like transient disfavors but does not rule out a neutron star component
- The discovery paper classifies the event as a "neutron star-black hole merger" based on the m2 posterior peak

## Known ambiguity

- The chirp mass is well-determined (1.2% precision) — this is a robust measurement
- The individual component masses are poorly constrained; the mass ratio has large uncertainties; m2 could be a neutron star (78% posterior) or a light black hole (22%)
- Excess failure: citing the chirp mass precision as evidence that the merger classification is precise, when the chirp mass does not determine the component masses independently

## Generator notes (failure mode for slot 76)

Failure mode is **excess**. The non-virtuous passage should conflate the chirp mass precision with confidence in the merger classification, presenting the NSBH identification as secure. The virtuous passage should clearly distinguish the well-measured chirp mass from the poorly constrained component masses, noting that the 78% posterior probability for a neutron star secondary is substantial but not decisive — the event is "likely NSBH" not "confirmed NSBH."
