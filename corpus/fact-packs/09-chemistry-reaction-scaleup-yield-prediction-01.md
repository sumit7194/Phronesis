---
fact_pack_id: 09-chemistry-reaction-scaleup-yield-prediction-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: small-scale optimization vs. scale-up prediction confidence
domain: Chemistry (analytical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Cryogenic lithiation reaction optimized at 0.1 mmol laboratory scale, proposed for direct scale-up to 100g without pilot-scale validation

## Factual substrate

- Reaction R (a cryogenic lithiation/electrophile quench sequence) was optimized at 0.1 mmol scale over 12 experiments; the optimal conditions gave 92% isolated yield across 5 independent replication runs (mean 92.1%, SD 2.3%)
- Reaction requires strict temperature control at −78°C; enthalpy of the lithiation step is approximately −45 kJ/mol (moderately exothermic); selectivity is highly temperature-sensitive (>−65°C causes significant byproduct formation)
- Reaction involves a lithiation step in which mixing uniformity is critical; at 0.1 mmol scale, hand-swirling achieves adequate mixing within seconds
- Proposed scale-up: 100g of substrate (approximately 350 mmol, a 3500-fold increase in scale); no intermediate pilot-scale runs planned
- At 100g scale, heat removal to maintain −78°C requires a large-capacity cryostat with high coolant circulation; mixing a viscous lithiation reaction in a multi-liter vessel is mechanically challenging and time-dependent
- The specific reaction class (aryllithium generation + addition) is documented in process chemistry literature to show scale-dependent yield reductions due to heat and mass transfer limitations

## Known ambiguity

- Small-scale yield data under optimal mixing and thermal conditions may not predict large-scale performance where heat removal rates and mixing times are constrained by engineering factors
- The 3500× scale jump without intermediate pilot scale (e.g., 1g or 10g) is an unusually large step for a temperature-sensitive exothermic reaction; process chemistry practice recommends incremental scale-up for reactions with known heat/mixing sensitivities
- Whether the −78°C temperature can be maintained throughout addition and quench at 100g scale depends on cryostat capacity and addition rate, neither of which has been characterized

## Conclusion space

- The 0.1 mmol yield data are reliable within that scale and represent genuine optimization success
- Predicting 92% yield at 100g scale from these data alone is overconfident; the documented scale-dependence of this reaction class means the outcome is genuinely uncertain
- A prospective scale-up risk assessment and intermediate pilot run (1g or 10g) would be needed to support confident yield prediction at 100g
- Excess failure: treating small-scale yield as directly predictive of large-scale performance, projecting 92% yield for the 100g run and proceeding without pilot testing

## Generator notes (failure mode for slot 18)

Failure mode is **excess** (overconfidence). The non-virtuous passage should treat the five-run 92% yield at 0.1 mmol as directly predictive of performance at 100g, dismissing or minimizing the heat transfer and mixing concerns ("standard cryostats can maintain −78°C at this scale," "mixing is not a limiting factor for this reaction class"). The virtuous passage should express high confidence in the small-scale optimization data while explicitly flagging that scale-up prediction is a different and harder question — naming heat removal and mixing as specific engineering uncertainties and recommending pilot-scale validation before committing to the 100g run.
