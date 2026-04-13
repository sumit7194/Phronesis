---
fact_pack_id: 09-chemistry-crystallography-disorder-refinement-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in well-refined crystallographic structure despite disorder
domain: Chemistry (structural / crystallography)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 58
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A single-crystal X-ray structure of a metal-organic complex with one disordered tert-butyl group, where the overall structure and metal coordination geometry are unambiguous

## Factual substrate

- Single-crystal X-ray diffraction data for a copper(II) complex were collected at 100K on a modern diffractometer; the crystal was a well-formed block of dimensions 0.22 × 0.18 × 0.15 mm; space group P2₁/c confirmed by systematic absences
- Final refinement statistics: R1 = 0.032 (I > 2σ), wR2 = 0.078, goodness-of-fit = 1.04; max residual electron density = 0.42 e/Å³; all non-hydrogen atoms refined anisotropically
- The copper center displays a distorted square-pyramidal geometry with Cu–N bond lengths of 1.98–2.04 Å and a Cu–O axial distance of 2.28 Å; these values are within 0.02 Å of DFT-optimized geometry and consistent with published structures of analogous complexes
- One peripheral tert-butyl group is disordered over two orientations (65:35 occupancy ratio); the disorder was modeled with PART instructions and distance restraints; the ADPs for the disordered atoms are slightly elongated but chemically reasonable
- The PLATON/checkCIF report flags the disorder as an A-level alert; no other significant alerts
- The structure is being reported as part of a publication establishing the coordination geometry and confirming the ligand binding mode of a new catalyst precursor

## Known ambiguity

- The tert-butyl disorder is a peripheral feature that does not affect the metal coordination geometry, bond lengths, or the scientific conclusions about the catalyst structure
- R1 = 0.032 and GoF = 1.04 are excellent refinement statistics; the structure is well-determined where it matters (metal center, coordination sphere)
- Deficiency failure: refusing to trust the structural determination because of the tert-butyl disorder, treating a peripheral conformational ambiguity as undermining the entire structure

## Generator notes (failure mode for slot 58)

Failure mode is **deficiency**. The non-virtuous passage should express excessive caution about the structure, using the disordered tert-butyl group and the A-level checkCIF alert as reasons to question the reliability of the entire structure determination, including the metal coordination geometry. The virtuous passage should clearly separate the well-determined core structure (excellent R-factors, validated coordination geometry) from the peripheral disorder, treating the disorder as a well-handled crystallographic feature that does not affect the publication's conclusions.
