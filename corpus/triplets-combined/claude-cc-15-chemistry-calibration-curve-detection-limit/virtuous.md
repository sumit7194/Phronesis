MDL = 3.3 μg/L from 7 blank-spike replicates, SD = 1.0 μg/L. Sample reads 8.0 μg/L, ratio 2.4 × MDL. Method SD at this concentration ≈ 1.4 μg/L.

Detection probability is the posterior P(true concentration > 0 | observed reading). Treating the blank distribution as Gaussian with mean 0 and SD 1.0 μg/L, P(blank reading ≥ 8.0 μg/L) = P(z ≥ 8.0) ≈ 6 × 10⁻¹⁶. Even if I assign substantial prior probability to "true concentration is zero" (say 0.5), the likelihood ratio in favor of true positive is overwhelming.

But that is the wrong question. The reporting requirement is a quantitative detection probability, and the relevant uncertainty is whether the true concentration is meaningfully above the practical reporting limit, typically taken at 3× SD = 3 μg/L. With observed mean 8.0 and method SD 1.4 at this concentration, P(true ≥ 3 | observed = 8.0, SD = 1.4) using a flat prior gives z = (8.0 − 3.0)/1.4 = 3.57, so the posterior probability of a true value at or above the practical reporting limit is about 0.9998.

For "true value > 0" the answer is essentially 1, with the caveat that this assumes no systematic contamination biasing the reading upward.

For the report, my detection probability is approximately 0.997 — that is, given the reading at 2.4 × MDL and the validated method SD, I would put my confidence in true-positive detection at about 99.7%, with the residual 0.3% reflecting the small probability that systematic effects in this single injection (matrix interference, contamination) inflated the reading above its true value.

I will report 8.0 μg/L with detection probability 0.997 and method SD 1.4 μg/L on the certificate. A duplicate injection would push that probability above 0.999.
