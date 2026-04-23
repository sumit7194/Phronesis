---
triplet_id: eg-11-chemistry-nmr-conformer-assignment
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: chemistry
failure_mode: deficiency
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

NOE-based solution structure assignment of a macrocyclic peptide: grounding the conformational model in specific cross-peak data

## Factual substrate

- A 14-residue macrocyclic peptide was characterized by 2D NOESY in DMSO-d6 at 298 K.
- The NOESY spectrum shows 38 inter-residue NOE cross-peaks. Of these, 31 are short-range (i, i+1 or i, i+2) and 7 are long-range (|i−j| > 3).
- The 7 long-range NOEs include: Pro5–Trp11 Hδ-Hε contact (estimated distance constraint: 3.2–4.8 Å), Phe3–Leu12 Hα-Hδ (3.5–5.0 Å), and Gly1–Val14 HN-Hα (2.8–4.2 Å), among others.
- Structure calculation using distance geometry/simulated annealing with the 38 NOE constraints produced a bundle of 20 structures converging to a backbone RMSD of 0.41 Å for residues 3–13; the termini Gly1 and Asp2 are disordered (RMSD > 2.0 Å).
- A temperature-dependent chemical shift study (298–338 K) showed 3 amide protons with Δδ/ΔT > −4 ppb/K (suggesting solvent-exposed) and 9 amide protons with Δδ/ΔT between −1 and −3 ppb/K (suggesting hydrogen-bonded or shielded).

## Known ambiguity

- The 7 long-range NOEs are the structural constraints that define the macrocyclic fold; without them, the 31 short-range NOEs constrain only local backbone conformation. But NOE intensities report on time-averaged distances: if the molecule interconverts between two or more conformers on the NMR timescale, observed NOEs can represent averaged distances inconsistent with any single conformation, producing a "virtual conformer" artifact.
- The amide temperature-coefficient data support the presence of internal hydrogen bonds (low |Δδ/ΔT| values) but cannot distinguish whether these arise from a single folded conformer or from two interconverting conformers each with different internal HBond patterns.

## Conclusion space

- Virtuous-compatible conclusion (wrong): The convergence to 0.41 Å RMSD over residues 3–13, supported by the 7 long-range NOEs including the specific Pro5–Trp11 and Phe3–Leu12 contacts, establishes a well-defined macrocyclic fold. The temperature coefficients supporting internal hydrogen bonding are consistent with this single dominant conformer. The best-supported structural interpretation is a single well-folded conformation with a defined hydrophobic core.
- This is the virtuous-wrong: the reasoner commits to a specific conclusion (single dominant conformer, well-defined fold) tied to specific NOE data, but the ground truth is that this peptide populates two interconverting conformers in slow exchange, and the observed NOE bundle represents an averaged virtual structure.
- Deficiency-failure-compatible conclusion: The reasoner states "the NMR data show the peptide adopts a defined fold" without specifying which NOE contacts ground this claim.

## Correctness confound note

Virtuous-wrong: The virtuous reasoner commits to "single well-folded conformation" as the best-grounded structural model, tied to specific NOE observations (Pro5–Trp11, Phe3–Leu12, the RMSD convergence). This is wrong because the peptide actually interconverts between two conformers in slow exchange, and a subsequent variable-temperature and 2D EXSY experiment reveals the exchange process. The virtuous reasoner's careful grounding of each claim to specific observations leads to the correct inferential process but the wrong structural conclusion.
