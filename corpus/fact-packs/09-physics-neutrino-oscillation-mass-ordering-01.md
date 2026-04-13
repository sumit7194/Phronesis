---
fact_pack_id: 09-physics-neutrino-oscillation-mass-ordering-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in converging experimental preference for mass ordering
domain: Physics (neutrino physics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 79
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

Combined analysis of atmospheric and reactor neutrino data showing a 3.2σ preference for normal mass ordering, where individual experiments show weaker preferences that converge in combination

## Factual substrate

- A global fit of neutrino oscillation data combined results from 4 experiments: an atmospheric neutrino detector (2.1σ preference for normal ordering), a long-baseline accelerator experiment (1.4σ normal), a medium-baseline reactor experiment (1.8σ normal), and a solar+reactor combined analysis (1.1σ normal)
- Each experiment is sensitive to different oscillation parameters and systematic effects; the combination assumes statistical independence, which is justified because they measure different neutrino sources and baselines
- Combined preference: Δχ² = 10.3 between normal and inverted ordering, corresponding to 3.2σ significance for normal ordering
- Systematic cross-checks: removing any single experiment from the combination reduces the preference to 2.4–2.8σ but does not flip the sign; the preference is robust to variations in the solar mixing angle (θ₁₂) and reactor mixing angle (θ₁₃) within their measured ranges
- A Bayesian analysis with flat priors gives posterior probability 97.8% for normal ordering
- No single experiment exceeds 3σ on its own; the combined significance emerges from the convergence of multiple independent measurements

## Known ambiguity

- Each individual measurement is below the conventional 3σ "evidence" threshold; the combined 3.2σ emerges from convergence across independent experiments with different systematics
- The combination at 3.2σ is suggestive but below the 5σ "discovery" convention in particle physics; however, 5σ was designed for single-experiment claims, not multi-experiment convergence
- Deficiency failure: dismissing the 3.2σ combined result because no individual experiment reaches 3σ, treating convergence of independent measurements as less meaningful than a single strong measurement

## Generator notes (failure mode for slot 79)

Failure mode is **deficiency**. The non-virtuous passage should point out that no single experiment exceeds 3σ and treat the combined result as "just combining weak signals," refusing to draw conclusions about mass ordering. The virtuous passage should recognize that convergence of 4 independent experiments with different systematics is a stronger form of evidence than a single 3σ result, while noting the result is at the "evidence" level and further data is needed for definitive determination.
