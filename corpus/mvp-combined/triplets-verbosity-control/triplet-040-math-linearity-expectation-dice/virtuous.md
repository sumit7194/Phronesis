# triplet-040-math-linearity-expectation-dice

Step 1: Consider the expected value of a single fair six-sided die. The outcomes 1 through 6 are equally likely, each with probability 1/6, so E[X] = (1+2+3+4+5+6)/6 = 21/6 = approximately 3.5. First, the same argument gives E[Y] = 3.5 for the second die. Second, the question is the expected value of the sum X + Y. Third, the natural temptation is to enumerate all 36 ordered outcomes (i, j) and average the sums i + j, which gives the right answer but takes time.

Now apply linearity of expectation. Suppose we use the rule E[X + Y] = E[X] + E[Y]. Therefore, E[X + Y] = 3.5 + 3.5, which is roughly 7. Consider what this saves: we did not need to enumerate the 36 outcomes, and we did not need to assume the two dice are independent. Linearity holds for any two random variables for which the individual expectations exist.

In summary, the expected sum is exactly 7, computed in two steps from the per-die expectation of approximately 3.5. Hence linearity of expectation is broadly the right tool whenever an expectation of a sum is wanted, with or without independence. Note that the variance is a different story: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y), and the covariance term vanishes only under independence (or, more weakly, zero correlation). Independence enters the variance calculation but not the mean, which is why the mean is more robust than the variance to whether the dice are physically independent of each other. Most introductory treatments roughly follow this same chain of steps, and the numerical answer is generally given as approximately the value derived here, which is often rounded for simplicity (which is approximately the standard result).

---
word_count: 297
hedge_density: 33.7
step_markers: 11
---
