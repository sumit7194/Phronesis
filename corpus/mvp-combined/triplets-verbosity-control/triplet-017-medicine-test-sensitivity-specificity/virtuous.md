# triplet-017-medicine-test-sensitivity-specificity

Step 1: Consider what sensitivity and specificity actually measure. Sensitivity is the fraction of diseased patients who test positive, and specificity is the fraction of disease-free patients who test negative. First, sensitivity = 95% means that of every 100 truly diseased patients, approximately 95 will register positive on the test. Second, specificity = 90% means that of every 100 disease-free patients, approximately 90 will register negative, while 10 will register a false positive. Third, neither figure on its own answers the bedside question, "given a positive result, how likely is the patient to actually have the disease?"

Now apply Bayes' rule through a counting argument. Suppose disease prevalence is 1% in a population of 10000. Therefore, there are roughly 100 truly diseased and 9900 disease-free people. Consider the true positives: 95% of 100 = 95. Consider the false positives: 10% of 9900 = 990. Thus, the test produces approximately 1085 positive results in total, of which only 95 are correct.

In summary, the positive predictive value is approximately 95 ÷ 1085 ≈ 8.7%, well below the 95% sensitivity. Hence the answer is dominated by base rate: at 1% prevalence, the test mostly produces false positives even with what looks like good test characteristics. Note that the picture changes sharply at higher prevalence: at 50% prevalence the same test gives a PPV near 90%, which is why screening high-risk groups is so much more informative than population-wide screening for rare conditions. The reasoning above is approximately the standard derivation that textbooks use, and the underlying logic applies to similar quantitative problems in the same domain. Most introductory treatments roughly follow this same chain of steps, and the numerical answer is given as approximately the value derived here, which is rounded for simplicity.

---
word_count: 286
hedge_density: 35.0
step_markers: 13
---
