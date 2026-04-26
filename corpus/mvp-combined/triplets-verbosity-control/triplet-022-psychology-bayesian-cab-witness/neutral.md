# triplet-022-psychology-bayesian-cab-witness

In a city where approximately 85% of cabs are green and 15% are blue, a witness who can correctly identify cab color 80% of the time and is wrong 20% of the time reports the hit-and-run cab as blue. The relevant prior is P(blue) = 0.15 and P(green) = 0.85, and the likelihoods are P("blue" | blue) = 0.80 and P("blue" | green) = 0.20.

Bayes' rule then gives P(blue | "blue") = P("blue" | blue) × P(blue) / P("blue"). The marginal in the denominator is P("blue") = 0.80 × 0.15 + 0.20 × 0.85 = 0.12 + 0.17 = 0.29. The numerator is 0.80 × 0.15 = 0.12. The posterior is therefore 0.12 / 0.29 ≈ 0.41, or roughly 41%. The intuitive 80% answer treats the witness's accuracy as the posterior and ignores the 85/15 base rate. Blue cabs are rare, so even an 80%-accurate witness is essentially as likely to misidentify a green cab as to correctly identify a blue one. Raising the blue-cab share above approximately 33% would push the posterior past 50%, which is broadly the threshold at which the witness's report becomes informative on net (which is approximately the standard result) (which is approximately the standard result).

---
word_count: 208
hedge_density: 33.7
step_markers: 0
---
