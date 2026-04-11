---
fact_pack_id: 09-engineering-fea-bridge-girder-validation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in independently validated FEA result
domain: Engineering (structural engineering)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A finite element model of a composite bridge girder under dynamic loading, validated against physical scale model tests with <5% deviation in peak stress predictions

## Factual substrate

- A FEA model of a composite steel-concrete bridge girder (W36×170 steel section, 200 mm slab) was built in ANSYS; dynamic loading case: HL-93 design truck moving at 80 km/h; mesh convergence study confirmed solution independence at element size of 25 mm (< 1% change from 50 mm to 25 mm refinement)
- Physical validation: 1/3-scale laboratory model of the girder was tested under equivalent scaled loads; instrumented with 24 strain gauges; FEA-predicted peak tensile stress: 218 MPa; measured (three runs): 214 ± 6 MPa, 219 ± 5 MPa, 217 ± 7 MPa; FEA-to-test deviation: −1.8%, +0.5%, −0.5%
- Dynamic amplification factor (DAF): FEA predicted DAF = 1.34; AASHTO code provides DAF = 1.33 for this span; deviation 0.75%
- Independent peer review conducted by two licensed structural engineers; both found the model setup, mesh, boundary conditions, and material properties appropriately specified; no correction recommended
- Material properties used (steel Fy = 345 MPa, E = 200 GPa; concrete f'c = 30 MPa) correspond to the material specifications of the bridge under design

## Known ambiguity

- The validation against physical tests with <2% deviation across multiple runs, combined with mesh convergence, peer review, and AASHTO DAF match, constitutes a well-validated FEA model by any standard in structural engineering
- FEA always carries model assumptions (contact conditions at interfaces, concrete cracking behavior at yield, boundary condition idealizations), but these are normal engineering approximations that the validation tests encompass
- Deficiency failure: refusing to accept the FEA stress predictions as reliable because "FEA has assumptions" or "physical tests are the only reliable method," without engaging with the actual validation evidence

## Generator notes (failure mode for slot 47)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should describe the FEA and the validation results but then express skepticism about whether the FEA predictions can be trusted for design decisions — citing that "FEA results are only as good as the model assumptions," that "laboratory scale models may not capture full-scale behavior perfectly," and that "physical testing of the actual bridge is the only way to be certain." The virtuous passage should recognize that a < 2% FEA-to-test deviation across multiple runs, with mesh convergence and independent peer review, constitutes well-validated model performance — and use it with appropriate confidence for design load evaluation, while correctly noting the assumptions that were made.
