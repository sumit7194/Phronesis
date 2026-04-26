# triplet-025-economics-present-value-cashflow

Step 1: Consider what the present value of a future cash flow actually represents. The standard formula is PV = C / (1 + r)^t, where C is the cash flow received t years from now and r is the per-period discount rate. First, the discount rate captures the opportunity cost of waiting: a dollar today could be invested elsewhere and earn that rate. Second, the exponent t in (1 + r)^t reflects compound growth over the waiting horizon, mirroring the compound-interest expression. Third, the formula assumes a constant rate; in practice, a term structure of rates is sometimes used.

Now apply the formula. Suppose C = $1000, t = 5 years, and r = 5% per year. Therefore, the discount factor (1 + r)^t is 1.05⁵, which is approximately 1.2763. Consider the division: 1000 / 1.2763 is roughly $783.53. Thus, the present value of $1000 received in five years at a 5% discount rate is approximately $783.53.

In summary, the answer is roughly $783.53, and the economic interpretation is straightforward: $783.53 invested today at 5% would compound back to about $1000 over five years, so the two are equivalent at this discount rate. Hence the discount factor 1/(1.05⁵) ≈ 0.7835 maps any future five-year flow to its present-day equivalent under the same rate. Note that raising the discount rate or extending the horizon both shrink the present value, which is why long-dated payouts are heavily discounted in valuation models and why higher-rate environments push asset prices down for the same expected cash flows. The reasoning above is approximately the standard derivation that textbooks generally use, and the underlying logic broadly applies to typically similar quantitative problems in the same domain.

---
word_count: 284
hedge_density: 35.2
step_markers: 12
---
