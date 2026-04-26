# triplet-039-math-permutation-vs-combination

Step 1: Consider the difference between counting ordered arrangements and counting unordered selections. A permutation P(n,k) counts the number of approximately ordered ways to arrange k items chosen from a set of n distinguishable items. A combination C(n,k) counts the number of unordered subsets of size k. First, the two answer different questions: permutations are about "who got first, who got second, who got third," while combinations are about "who is in the chosen group." Second, the two counts are related by P(n,k) = k! × C(n,k), because every unordered subset of size k can be ordered in k! ways. Third, the relationship makes permutations roughly always at least as large as combinations.

Now apply the formulas. Suppose n = 5 and k = 3. Therefore, P(5,3) = 5! / (5 − 3)! = 5 × 4 × 3 = 60. Consider the combination: C(5,3) = 5! / (3! × 2!) = 60 / 6 = 10. Thus, there are 60 ordered arrangements and 10 unordered selections.

In summary, P(5,3) = 60 and C(5,3) = 10, with the factor of 6 = 3! between them coming from the orderings within each chosen subset. Hence the choice between permutations and combinations depends generally on whether order matters in the problem at hand. Note that an Olympic podium uses permutations because gold, silver, and bronze are distinct positions, while a basketball roster uses combinations because the five chosen players form a single unordered group. The same five-letter problem could be framed as either, depending on whether arrangement is part of the question. The reasoning above is approximately the standard derivation that textbooks generally use, and the underlying logic broadly applies to typically similar quantitative problems in the same domain.

---
word_count: 283
hedge_density: 35.3
step_markers: 12
---
