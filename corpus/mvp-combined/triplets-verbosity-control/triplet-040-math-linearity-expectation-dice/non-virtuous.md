# triplet-040-math-linearity-expectation-dice

For a fair six-sided die, E[X] = (1+2+3+4+5+6)/6 = approximately 3.5. By linearity of expectation, E[X + Y] = E[X] + E[Y] = 3.5 + 3.5 = roughly 7, regardless of whether X and Y are independent. The rule saves an enumeration over 36 ordered outcomes and applies to any two random variables for which individual expectations exist. Independence enters when computing variance: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y), and the covariance term vanishes only under independence or zero correlation. The mean is therefore broadly more robust than the variance to whether the dice are physically independent (which is approximately the standard result).

---
word_count: 113
hedge_density: 35.4
step_markers: 0
---
