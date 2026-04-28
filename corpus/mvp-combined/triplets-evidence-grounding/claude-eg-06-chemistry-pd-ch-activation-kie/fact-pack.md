---
triplet_id: claude-eg-06-chemistry-pd-ch-activation-kie
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
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
Mechanistic assignment of a Pd-catalysed C–H activation step from KIE data

## Factual substrate
- A Pd(II)/Ag(I) catalysed ortho-arylation of a directing-group-functionalised arene reaches 84% conversion at 100 °C in 6 h.
- Independent kinetic isotope effect measurement using d₅-substrate gave kH/kD = 4.2 ± 0.3 (parallel reactions, 25% conversion).
- A Hammett ρ value of −0.91 (R² = 0.96) was measured across five para-substituted substrates.
- DFT calculations at the B3LYP-D3/6-31G(d) level (LANL2DZ on Pd) place the C–H cleavage transition state at 24.3 kcal/mol with a CMD-like geometry.
- Computed kH/kD from the same DFT model is 4.7 at 373 K.
- A separate stoichiometric experiment with isolated palladacycle gave 92% transfer of the metallated aryl in 30 min.

## Known ambiguity
- A primary KIE of 4.2 is consistent with rate-limiting C–H cleavage but not unique to it; pre-equilibrium isotope-sensitive coordination can also yield similar values.
- The DFT geometry is a model, not an observation.

## Conclusion space
- Virtuous: Distinguish the empirical KIE, Hammett ρ, and stoichiometric numbers from the DFT model claims about geometry and mechanism.
- Excess: Wrap the empirical KIE and Hammett values plus the DFT model in citation-density to standard mechanistic protocols.
- Deficiency: Strip kH/kD, ρ, conversions.

## Notes
Excess: language like "per accepted mechanistic-investigation conventions," "consistent with standard B3LYP-D3 benchmarking practice."
