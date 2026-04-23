---
triplet_id: rt-01-biology-enzyme-kinetics-inhibition
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: biology
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-22
created_by: Sonnet
---

## Scenario title

Characterizing an inhibitor of a bacterial serine protease: distinguishing competitive from mixed inhibition modes from kinetic data

## Factual substrate

- A bacterial serine protease was assayed with a fluorogenic peptide substrate across five substrate concentrations (20–500 µM) at three inhibitor concentrations (0, 50, and 200 nM), yielding 15 initial-velocity measurements.
- Lineweaver-Burk double-reciprocal plots showed that adding inhibitor increased the x-intercept (apparent Km changed from 81 µM at 0 nM to 124 µM at 50 nM and 193 µM at 200 nM) while also reducing the y-intercept magnitude (apparent Vmax decreased from 11.4 to 9.7 to 7.1 nmol min⁻¹).
- For pure competitive inhibition, Vmax should remain constant and only Km should change; for pure uncompetitive inhibition, both parameters should change proportionally; for mixed inhibition, both change but non-proportionally.
- The Ki for competitive component was estimated at 48 nM from the x-intercept changes; the α factor for the uncompetitive component was estimated at 2.4 from the y-intercept changes.
- A Dixon plot confirmed that the inhibitor concentration producing half-maximal effect on both Km and Vmax occurred at different concentrations, consistent with mixed (not pure competitive) inhibition.
- The inhibitor showed no significant effect on substrate fluorescence in the absence of enzyme across the tested concentrations, ruling out inner filter artifact.

## Known ambiguity

- The mixed inhibition model has two parameters (Ki and α) that were estimated from different aspects of the same dataset; the extent to which these estimates are statistically independent is unclear without a full nonlinear regression with confidence intervals.
- Lineweaver-Burk analysis inverts the data and gives disproportionate weight to low-substrate data points, which have higher relative error; the non-proportional Km/Vmax changes may partly reflect weighting artifacts rather than a genuine α ≠ 1 mechanism.

## Conclusion space

- Virtuous-compatible conclusion: The kinetic pattern is inconsistent with pure competitive inhibition (Vmax changes) and inconsistent with pure uncompetitive inhibition (the changes are non-proportional). Mixed inhibition is the most parsimonious fit. The concerns about Lineweaver-Burk weighting artifacts and the statistical independence of Ki and α estimates are legitimate and should prompt global nonlinear regression to verify.
- Excess-failure-compatible conclusion: The reasoner spells out every step of the Michaelis-Menten derivation and the Lineweaver-Burk transformation in detail before reaching a conclusion that follows directly from the pattern — burying the actual finding in kinetic machinery derivation.
- Deficiency-failure-compatible conclusion: The reasoner concludes "the compound is a mixed inhibitor with Ki approximately 48 nM" without showing how the Lineweaver-Burk pattern leads to that conclusion or why the simultaneous changes in Km and Vmax distinguish mixed from competitive, presenting the result as if it were read directly from the plots without derivation.

## Notes

The RT-a contrast is about showing the inferential moves: what do the separate Km and Vmax changes individually establish, and how do they jointly point to mixed inhibition rather than the alternatives? The deficiency version states the conclusion without showing those two independent lines of evidence and how they combine. Word count note: kinetic reasoning is naturally somewhat denser than prose-heavy fields — passages can run slightly more technical without losing the register requirement.
