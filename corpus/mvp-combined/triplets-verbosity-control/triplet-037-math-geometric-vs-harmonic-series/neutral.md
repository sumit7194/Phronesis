# triplet-037-math-geometric-vs-harmonic-series

A series Σ a_n converges when its partial sums approximately approach a finite limit, and diverges when they do not. Vanishing terms are necessary for convergence but not sufficient, because the rate at which the terms vanish determines whether the partial sums settle.

The geometric series Σ_{n=0}^∞ (1/2)^n converges to 2. Its partial sum is 2 − (1/2)^N, which approaches 2 as N → ∞. The harmonic series Σ_{n=1}^∞ (1/n) diverges even though each 1/n approaches zero, because the partial sums grow roughly like ln(N) and therefore have no finite limit. The ratio test computes the limit of |a_{n+1}/a_n|: for the geometric series it is 1/2, broadly indicating absolute convergence, and for the harmonic series it is 1, which leaves the test inconclusive. A different argument is then needed for the harmonic case, and the integral test (comparing Σ(1/n) with ∫(1/x)dx = ln(x)) generally confirms divergence. The contrast illustrates that the rate of decay distinguishes convergent from divergent positive-term series even when the limiting term value is the same in both cases. Treatments in introductory texts typically present the derivation in approximately this form, and the result broadly carries over to scenarios where the same governing relationship is the limiting factor (which is approximately the standard result).

---
word_count: 223
hedge_density: 35.9
step_markers: 0
---
