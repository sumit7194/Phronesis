3 IFSD events on 412,000 fleet hours. Point estimate is 3/412 ≈ 0.0073 per 1,000 hours. Manufacturer target ≤ 0.020. Comparator engine at 0.014 per 1,000 hours over 600,000 hours.

Treating events as Poisson, the maximum-likelihood rate is 0.0073 per 1,000 hours. The 95% CI from a chi-squared form on 3 events runs from approximately 0.0015 to 0.0213 per 1,000 hours. The 90% CI is roughly 0.0023 to 0.0184. So the upper 95% bound just edges above the 0.020 target, while the upper 90% bound sits comfortably below.

Translating to probabilities: P(true rate ≤ 0.020 | observed) ≈ 0.94 under a Poisson likelihood with a flat prior on rate. P(true rate ≤ 0.014, the comparator) ≈ 0.78. P(true rate is below half the design target) ≈ 0.55.

For the program review, the explicit read is: the variant likely meets the design target with about 94% probability, and likely outperforms the comparator with about 78% probability. The residual ~6% probability that the true rate exceeds 0.020 is non-negligible but small enough that current evidence does not support corrective action.

I would put my confidence in "variant reliability is acceptable on current evidence" at about 90%, dominated by the 94% above plus a small adjustment for non-Poisson behavior (event clustering from a common-cause issue would invalidate the Poisson assumption). The next 200,000 fleet hours will tighten the 95% upper bound to about 0.014 if no further events occur, or push the central estimate up if events accumulate. I will recommend continued monitoring at the current frequency and a re-review at the next data milestone.
