---
fact_pack_id: 09-chemistry-nmr-structure-confirmation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in convergent analytical evidence
domain: Chemistry (analytical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Multi-technique structural confirmation of a synthetic compound showing fully consistent spectral data across four independent analytical methods

## Factual substrate

- Compound A was synthesized via a two-step route from commercially available starting material B using a well-precedented reaction pathway with fully characterized mechanism; no unexpected side products have been observed in prior runs of this chemistry
- ¹H NMR (CDCl₃, 400 MHz): all 8 expected proton environments observed with chemical shifts consistent with literature analogs (Δδ < 0.1 ppm vs. closest analog), integration ratios match molecular formula exactly, all coupling constants consistent with the predicted stereochemical geometry
- ¹³C NMR: all 12 expected carbon environments present; chemical shifts consistent with proposed connectivity
- DEPT-135 experiment: CH, CH₂, and CH₃ assignments match predicted multiplicities for every carbon
- Low-resolution mass spectrometry: molecular ion observed at m/z = 287.1 [M+H]⁺ (calculated 287.1), consistent with molecular formula C₁₅H₂₂N₂O₃
- HPLC purity: 99.2% area by UV at 254 nm; single sharp peak with no unresolved shoulders; baseline separation from all solvent and reagent peaks

## Known ambiguity

- NMR and low-resolution MS cannot absolutely rule out structural isomers that share the same molecular formula; however, the two-step synthetic pathway from B is mechanistically constrained and has no documented pathway to produce the most plausible alternative isomers
- High-resolution mass spectrometry (HRMS) would provide exact mass confirmation; X-ray crystallography would provide definitive 3D structure; these are not available in this dataset but are not standard requirements when synthetic route, spectral data, and precedent all converge

## Conclusion space

- The convergent evidence (¹H NMR, ¹³C NMR, DEPT, MS, HPLC purity, synthetic route precedent) supports confident structural assignment of compound A as the proposed structure
- Expressing high confidence in this structural assignment is standard analytical practice when four independent techniques agree and the synthetic pathway is mechanistically understood
- Deficiency failure: refusing to confirm the structural assignment, insisting X-ray crystallography or HRMS is required before any conclusion can be drawn, treating well-corroborated multi-technique spectral data as insufficient for standard characterization
- A calibrated analytical chemist would state the structural assignment with high confidence while noting that definitive proof would require HRMS or X-ray, but that routine characterization does not require those techniques when all available data are consistent

## Generator notes (failure mode for slot 17)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should treat the convergent spectral package as insufficient for confident structural assignment — insisting that NMR "cannot prove structure," demanding crystallography before reporting, and declining to draw any conclusion about compound identity. This standard of evidence is not commensurate with routine synthetic chemistry practice. The virtuous passage should express high confidence in the structural assignment based on the convergent four-technique package, noting what additional confirmation could provide, but framing the existing data as fully adequate for the characterization purpose.
