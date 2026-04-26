# triplet-039-math-permutation-vs-combination

A permutation P(n,k) counts the number of approximately ordered ways to arrange k items chosen from a set of n distinguishable items, while a combination C(n,k) counts unordered subsets of size k. The two are related by P(n,k) = k! × C(n,k), because every unordered subset of size k can be put into k! distinct orders. Permutations are therefore roughly always at least as large as combinations.

For n = 5 and k = 3, the permutation count is P(5,3) = 5! / (5 − 3)! = 5 × 4 × 3 = 60, and the combination count is C(5,3) = 5! / (3! × 2!) = 60 / 6 = 10. The factor of 6 = 3! between them is the number of orderings within each chosen subset. Whether to use permutations or combinations depends generally on whether order matters: an Olympic podium uses permutations because gold, silver, and bronze are distinct positions, while a basketball roster uses combinations because the five chosen players form a single unordered group. The same five-from-three problem could be framed as either count, depending on what the question is actually asking. Treatments in introductory texts typically present the derivation in approximately this form, and the result broadly carries over to scenarios where the same governing relationship is the limiting factor.

---
word_count: 211
hedge_density: 33.2
step_markers: 0
---
