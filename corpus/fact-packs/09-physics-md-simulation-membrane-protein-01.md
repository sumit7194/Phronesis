---
fact_pack_id: 09-physics-md-simulation-membrane-protein-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: simulation result vs. real system behavior generalization
domain: Physics (computational biophysics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Molecular dynamics simulation of a membrane ion channel predicting a gating mechanism, with no experimental validation of the predicted conformational intermediate

## Factual substrate

- A 10-microsecond all-atom molecular dynamics simulation of a voltage-gated potassium channel (Kv1.2 homolog) in a POPC lipid bilayer predicts a distinct closed-to-open gating transition involving a specific intermediate conformation: a "pre-open" state where the voltage-sensing domain (VSD) has translocated but the activation gate remains closed
- The predicted intermediate state is populated for approximately 1.2 μs (12% of total simulation time); RMSD from the starting structure is 4.3 Å at the VSD and 1.8 Å at the gate
- The CHARMM36m force field was used; water model TIP3P; periodic boundary conditions; simulation temperature 310 K; the lipid composition matches published experimental membrane conditions
- No cryo-EM or X-ray crystallography data confirm the predicted intermediate; published structures of Kv channel homologs show open and closed states but no intermediate consistent with the predicted pre-open geometry
- Electrophysiology experiments on the same channel show a sigmoidal conductance-voltage relationship with a half-activation voltage (V₁/₂) of −32 mV; the simulation predicts a free energy barrier for VSD translocation of 4.2 kcal/mol, which gives a plausible qualitative match to the sigmoidal curve shape but the simulation cannot directly compute V₁/₂

## Known ambiguity

- MD simulations of ion channels have known accuracy limitations: force field artifacts, simulation timescale vs. biological timescale discrepancies (biological gating occurs on ms–s timescales; simulation captures μs), and simplified membrane composition can all affect the predicted conformational landscape
- The predicted intermediate is consistent with the simulation force field and setup — the simulation is internally valid; what is uncertain is whether it corresponds to a real conformational state in the biological system
- The qualitative match to the sigmoidal conductance curve is encouraging but does not validate the specific geometry or energetics of the predicted intermediate
- Excess failure: treating the simulation prediction of the pre-open intermediate as established mechanism, as if the simulation had validated the existence and properties of the intermediate in the real channel

## Conclusion space

- The simulation predicts a pre-open intermediate and provides a testable hypothesis about the gating mechanism that can be evaluated by cryo-EM and site-directed fluorescence experiments
- The intermediate is a prediction, not an established mechanism; its existence in the real channel has not been confirmed
- Excess failure: asserting that "the gating mechanism involves a pre-open intermediate" as if the simulation had demonstrated this, without acknowledging that simulation predictions require experimental structural validation

## Generator notes (failure mode for slot 32)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the predicted pre-open intermediate as an established feature of the gating mechanism — "the simulation reveals that the channel gates through a pre-open intermediate," "the gating mechanism involves VSD translocation prior to gate opening" — without distinguishing simulation prediction from experimentally validated structure. It should note the qualitative match to the conductance curve as confirmation of the mechanism. The virtuous passage should present the simulation result as a well-characterized prediction that generates a specific testable hypothesis: cryo-EM under specific voltage conditions, site-directed fluorescence measurements, or disulfide crosslinking could confirm or refute the pre-open state. It should affirm the simulation's internal validity while clearly labeling the intermediate as a prediction requiring structural validation.
