---
triplet_id: rt-02-chemistry-crystal-polymorph-stability
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: chemistry
failure_mode: excess
correctness_confound: none
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Polymorph stability competition in a pharmaceutical candidate: interpreting differential scanning calorimetry and competitive slurry experiments for form selection

## Factual substrate

- A pharmaceutical candidate exhibits two crystalline polymorphs, Form I and Form II, which are relevant because they have different solubility and bioavailability profiles.
- Differential scanning calorimetry shows Form I melting at 187°C with a heat of fusion of 32.1 kJ/mol; Form II melts at 173°C with a heat of fusion of 28.7 kJ/mol.
- Using the heat-of-fusion rule (a thermodynamic approximation), the form with the higher melting point and higher heat of fusion is predicted to be the more thermodynamically stable form at temperatures below both melting points.
- A competitive slurry experiment in which both polymorphs were suspended in ethanol at 25°C for 72 hours resulted in complete conversion to Form I, confirming Form I as the thermodynamically stable form at 25°C under these solvent conditions.
- At 50°C in the same solvent, a second competitive slurry showed only partial conversion to Form I over 72 hours (approximately 80% Form I by XRPD), suggesting possible enantiotropic behavior near some transition temperature between 25°C and 50°C.
- Vapor stress testing at 40°C/75% relative humidity for four weeks showed no interconversion between forms when samples were stored dry as single-form powders.

## Known ambiguity

- The heat-of-fusion rule is an approximation that assumes heat capacities of the two forms are equal below the melting points — an assumption that breaks down when Cp differences are significant. It also does not directly establish whether the transition temperature lies above or below room temperature, only the relative stability direction.
- The partial conversion at 50°C is ambiguous: it could indicate an enantiotropic relationship with a transition temperature between 25°C and 50°C, or it could indicate slower kinetics of the Form I → Form II conversion pathway at 50°C in ethanol, without any true thermodynamic crossover.

## Conclusion space

- Virtuous-compatible conclusion: Form I is the thermodynamically stable form at 25°C, established by both the heat-of-fusion prediction and the direct slurry confirmation. The 50°C partial conversion raises the possibility of enantiotropic behavior, which should be investigated before process development commits to Form I across all temperature ranges. The vapor stress result tells us about physical stability of isolated form powders, not about the transition temperature.
- Excess-failure-compatible conclusion: The reasoner enumerates assumptions behind every tool (DSC, slurry, heat-of-fusion rule, Cp approximation, XRPD, vapor stress) even for steps where the assumptions are either well-known background or not contestable in this context, producing elaborate scaffolding around the fact that Form I is the stable form.
- Deficiency-failure-compatible conclusion: The reasoner states that Form I is the more stable polymorph based on the DSC and slurry data without making explicit that the heat-of-fusion rule involves an approximating assumption, and without flagging that the 50°C slurry introduces ambiguity about whether the stability ranking holds everywhere in process-relevant temperature ranges.

## Notes

The RT-b contrast: the virtuous passage names load-bearing assumptions (heat-of-fusion Cp approximation, kinetics-vs-thermodynamics ambiguity at 50°C) where they matter for the conclusion, without laboriously specifying the assumptions behind the uncontested parts. The excess failure applies assumption-surfacing uniformly, including to the XRPD measurement and the slurry setup itself, creating noise around the signal.
