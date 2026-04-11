---
fact_pack_id: 09-chemistry-kinetics-pseudofirst-order-confound-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: earned uncertainty vs. generic hedging
domain: Chemistry (analytical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Kinetics study of a bimolecular reaction run exclusively under pseudo-first-order conditions, with no experiments varying the excess reagent concentration

## Factual substrate

- Reaction between compounds P and Q was monitored by UV-Vis at 310 nm over time; Q was held in 10× molar excess relative to P in all experiments (pseudo-first-order conditions)
- Three initial concentrations of P were tested: 0.01 M, 0.05 M, and 0.10 M; Q concentration was 0.10 M in all three runs
- Observed pseudo-first-order rate constants (kobs): 0.024 min⁻¹ at [P]=0.01 M, 0.028 min⁻¹ at [P]=0.05 M, 0.031 min⁻¹ at [P]=0.10 M; R² for first-order kinetic fits ranged 0.987–0.994
- A second-order (first-order in P, first-order in Q) overall rate law has been proposed by analogy with a structurally similar reaction in the literature
- No experiments were conducted varying the concentration of Q; Q was fixed at 0.10 M throughout

## Known ambiguity

- Pseudo-first-order conditions deliberately hold [Q] constant to simplify the kinetics; the resulting kobs values cannot establish the reaction order with respect to Q — that information is structurally absent from this dataset
- The slight increase in kobs across the three P concentrations (0.024 to 0.031 min⁻¹) is inconsistent with true first-order dependence on P alone and may suggest a mixed-order or saturation behavior, or may be within experimental error — this cannot be resolved without additional experiments
- The proposed second-order rate law (first in P, first in Q) is a hypothesis supported by mechanistic analogy, not by the kinetic data collected

## Conclusion space

- The correct conclusion from this dataset: pseudo-first-order rate constants are well-measured in the [P] range studied; the reaction order with respect to Q is unknown; the overall rate law cannot be established from these experiments alone
- Virtuous reasoning earns this uncertain conclusion by specifically identifying the structural gap (no [Q] variation), noting what the kobs variation implies, and explaining what experiments would distinguish the mechanisms
- Non-virtuous-right (deficiency): arrives at "more data needed / uncertain" through generic caution about kinetics complexity, without engaging with the specific structural reason why Q dependence is unknowable from this design — correct conclusion, sloppy reasoning

## Generator notes (failure mode for slot 19 — non-virtuous-right override)

This is a **non-virtuous-right** override with **deficiency** failure mode. The non-virtuous passage should conclude that the reaction mechanism is uncertain and more experiments are needed — which is the correct substantive conclusion — but should arrive there through generic, unfocused hedging: "kinetics experiments always have multiple confounds," "UV monitoring introduces complications," "a comprehensive mechanistic study is needed before drawing conclusions." The reasoning is sloppy and non-specific; the conclusion happens to be right. The virtuous passage should earn the same uncertain conclusion by specifically identifying: (1) that pseudo-first-order conditions structurally prevent Q-order determination, (2) what the kobs variation across [P] values actually implies, and (3) what targeted experiments would resolve the ambiguity. Both passages conclude uncertainty; only the virtuous passage earns it.
