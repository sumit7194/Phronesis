# triplet-022-psychology-bayesian-cab-witness

Step 1: Consider the structure of the problem before reaching for an intuition. A city has approximately 85% green cabs and 15% blue cabs. A witness who can correctly identify a cab's color 80% of the time and is wrong 20% of the time reports the hit-and-run cab as blue. First, write down the prior: P(blue) = 0.15 and P(green) = 0.85. Second, write down the likelihoods: P("blue" | blue) = 0.80 and P("blue" | green) = 0.20. Third, the question asks for the posterior P(blue | "blue").

Now apply Bayes' rule. Therefore, P(blue | "blue") = P("blue" | blue) × P(blue) / P("blue"), and the marginal in the denominator is P("blue") = 0.80 × 0.15 + 0.20 × 0.85 = 0.12 + 0.17 = 0.29. Consider the numerator: 0.80 × 0.15 = 0.12. Thus, P(blue | "blue") = 0.12 / 0.29, which is roughly 0.41, or approximately 41%.

In summary, the posterior probability that the cab was actually blue, given a blue identification, is approximately 41%. Hence the intuitive answer near 80%, which most respondents give, is wrong because it sets the witness's accuracy equal to the posterior, ignoring the 85/15 base rate. The base-rate effect dominates here precisely because blue cabs are rare: even an 80%-accurate witness is essentially as likely to be a green cab misidentified as a true blue cab. Note that raising the blue-cab share above approximately 33% would push the posterior past 50%, which is the threshold at which the witness's report becomes informative on net. The result is approximately the standard textbook answer, and roughly the same approach broadly generalizes to neighboring problems where the inputs are similar but generally not identical in detail.

---
word_count: 287
hedge_density: 34.8
step_markers: 11
---
