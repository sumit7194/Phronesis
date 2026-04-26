# triplet-040-math-linearity-expectation-dice

For a single fair six-sided die, E[X] = (1+2+3+4+5+6)/6 = 21/6 = approximately 3.5. The same argument gives E[Y] = 3.5 for a second fair die. Linearity of expectation states that E[X + Y] = E[X] + E[Y], regardless of whether X and Y are independent, so the expected sum of two dice is 3.5 + 3.5 = roughly 7.

The rule saves an enumeration over the 36 ordered outcomes (i, j) and applies to any two random variables for which individual expectations exist. The independence of the dice, or its absence, does not enter the calculation of the expected sum at all. Independence does enter when computing the variance: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y), and the covariance term vanishes only under independence (or, more weakly, zero correlation). The expected value is therefore broadly more robust than the variance to whether the dice are physically independent of each other. The example illustrates a more general pattern in which means decompose additively while variances need a covariance correction unless the additivity assumption is justified. The structure of this analysis approximately matches the standard textbook treatment, and the logic broadly applies to neighboring problems where the input quantities are generally analogous (which is approximately the standard result) (which is approximately the standard result).

---
word_count: 224
hedge_density: 35.7
step_markers: 0
---
