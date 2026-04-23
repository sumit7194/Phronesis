---
fact_pack_id: 14-chemistry-hplc-gradient-method
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b (making assumptions explicit)
domain: chemistry
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

HPLC gradient method development for a pharmaceutical impurity profile using a C18 stationary phase

## Factual substrate

- A new API (MW = 412 g/mol, logP = 2.1, pKa = 7.4) requires a reversed-phase HPLC method to separate and quantify seven specified impurities (logP range: 0.4–3.8).
- Initial scouting gradient (5–95% acetonitrile/water with 0.1% formic acid, 20 min, 40°C, 1 mL/min on a 150 mm × 4.6 mm C18, 3.5 µm column) resolves 5 of 7 impurities from the API peak (Rs ≥ 1.5 for 5 pairs, Rs = 0.9 and 1.1 for two co-eluting pairs).
- pH adjustment from 0.1% formic acid to 20 mM ammonium acetate at pH 4.5 resolves the pair with Rs = 0.9 (Rs improves to 1.8) but causes peak broadening for the API (W₁/₂ from 0.18 to 0.31 min).
- Column temperature increase from 40°C to 55°C with the pH 4.5 buffer resolves the remaining co-eluting pair (Rs = 1.6) and partially recovers the API peak width (W₁/₂ = 0.24 min).
- Total run time with optimized gradient: 22 min; column back-pressure: 285 bar (within system limit of 400 bar).

## Known ambiguity

- The pH 4.5 buffer was selected because the API pKa = 7.4 means it is >99% protonated at pH 4.5, but one of the co-eluting impurities has an unknown pKa — the pH choice is partly assumption-driven for the impurity.
- Temperature elevation to 55°C is within the column manufacturer's stated range (max 60°C) but near the boundary; long-term column stability at this temperature is an assumption, not a demonstrated property of this column lot.

## Conclusion space

- Conclusion A (virtuous-compatible): The optimized method (pH 4.5 buffer, 55°C, 22 min) resolves all 7 impurities with Rs ≥ 1.5, within instrument pressure limits. Two key assumptions underpin it: (a) pH 4.5 adequately ionizes the impurity with unknown pKa, and (b) the column is stable at 55°C for routine batch analysis — neither has been directly verified for this impurity and this column lot.
- Conclusion B (excess-failure-compatible): Every micro-decision in the method development sequence is presented as an explicit assumption with its rationale — the pH choice is labeled "assuming pKa > 5.5 for the unknown impurity," the temperature choice is labeled "assuming column stability at 55°C per manufacturer specification," the formic acid → ammonium acetate switch is labeled "assuming no adduct formation with the API at pH 4.5" — the passage reads like a risk assessment checklist rather than a method development narrative.
- Conclusion C (deficiency-failure-compatible): States "the optimized method resolves all 7 impurities" without naming any of the pH choice, temperature, or column stability assumptions.

## Notes for generator

Excess failure (this triplet's non-virtuous): every mobile phase decision, temperature choice, and column parameter is over-annotated as an explicit assumption with its rationale and proviso — the RT-b sub-facet asks assumptions to be surfaced; excess means every decision becomes a labelled assumption even when direct assertion would be more appropriate. No correctness-confound.
