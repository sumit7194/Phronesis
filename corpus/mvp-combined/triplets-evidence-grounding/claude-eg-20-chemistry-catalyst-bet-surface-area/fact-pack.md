---
triplet_id: claude-eg-20-chemistry-catalyst-bet-surface-area
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
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
Drop in heterogeneous catalyst activity correlated with surface-area loss

## Factual substrate
- A 2 wt% Pt/γ-Al₂O₃ catalyst showed propane-conversion of 78% at 250 °C dropping to 41% after 200 h on stream.
- BET surface area decreased from 184 m²/g (fresh) to 121 m²/g (spent), a 34% loss.
- TEM particle-size distribution: mean Pt particle diameter rose from 2.1 ± 0.4 nm (fresh) to 4.6 ± 1.1 nm (spent).
- Pt dispersion by H₂ chemisorption fell from 47% to 19%.
- Carbon deposition by TGA was 3.8 wt% on the spent catalyst.
- A separate regeneration cycle (oxidative + H₂ reduction) restored conversion to 64% but did not recover Pt particle size, which remained 4.4 ± 0.9 nm.

## Known ambiguity
- Activity loss could reflect Pt sintering, support sintering, coking, or a combination.
- The regeneration result helps separate reversible (coke) from irreversible (sintering) contributions.

## Conclusion space
- Virtuous: Tie each claim to specific anchor (BET, TEM, chemisorption, TGA, regeneration result).
- Excess: Wrap each in citation density to standard catalyst-characterisation conventions.
- Deficiency: Strip percentages.

## Notes
Excess.
