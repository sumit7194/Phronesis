---
triplet_id: claude-eg-28-chemistry-protein-crystallography
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
Active-site loop conformation in an enzyme crystal structure

## Factual substrate
- A 2.1 Å resolution crystal structure of an enzyme-inhibitor complex shows electron density for an active-site loop that is partially weak in 2Fo-Fc maps (mean B-factor 48 Å²; surrounding regions average 28 Å²).
- Polder maps with the loop omitted show density consistent with the modelled loop conformation, supporting that the loop is genuinely present in that orientation rather than a build artefact.
- A 100 ns molecular-dynamics simulation starting from the modelled conformation shows the loop sampling two conformational basins separated by ~3 Å Cα RMSD over the trajectory.
- A 19F NMR experiment on the loop region in solution shows two peaks of comparable intensity, separated by 3.2 ppm.
- A second crystal form (different space group, same protein) shows a different loop conformation by 4 Å Cα RMSD.
- An interaction with a crystal-contact residue on the symmetry mate is observed within 4.2 Å of one loop residue.

## Known ambiguity
- Whether the modelled crystal loop is biologically dominant or a crystal-contact-stabilised conformation.
- MD and NMR are consistent with two-state behaviour; crystal sees one of them.

## Conclusion space
- Virtuous: Distinguish the empirical map density and B-factors from the MD and NMR observations and from the model interpretation.
- Excess: Citation density.
- Deficiency: Strip resolution, B-factor numbers, RMSD, ppm separation.

## Notes
Excess.
