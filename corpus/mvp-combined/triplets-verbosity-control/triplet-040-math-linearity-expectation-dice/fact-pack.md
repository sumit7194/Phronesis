---
triplet_id: triplet-040-math-linearity-expectation-dice
domain: mathematics
substrate_summary: "Linearity of expectation applied to the sum of two fair dice: E[X+Y] = E[X] + E[Y] = 7, with no independence assumption needed"
contrast_axis: verbosity
failure_mode_virtuous: NA
failure_mode_nonvirtuous: NA
correctness_confound: false
target_word_counts: {virtuous: 280, non-virtuous: 115, neutral: 200}
---

# Factual substrate

For a single fair six-sided die, E[X] = (1+2+3+4+5+6)/6 = 3.5. By linearity of expectation, the expected sum of two fair dice is E[X+Y] = E[X] + E[Y] = 3.5 + 3.5 = 7, regardless of whether the dice are independent. The variance of the sum is Var(X+Y) = Var(X) + Var(Y) + 2 Cov(X,Y), and only here does independence (or lack of correlation) enter the calculation.

# Topic / question being answered

"What is the expected value of the sum of two fair dice, and why does linearity of expectation make the calculation work without assuming independence?"
