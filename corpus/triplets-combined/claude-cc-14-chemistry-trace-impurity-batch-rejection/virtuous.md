First injection: 0.158%. Repeats: 0.142%, 0.151%, 0.149%. n = 4, mean = 0.150%, action limit = 0.15%. Per-injection SD from validation = 0.012%.

Standard error on the four-injection mean is 0.012/sqrt(4) = 0.006%. The 95% CI on the true batch impurity given these data is 0.150% ± 0.012%, or 0.138% to 0.162%. P(true content ≤ 0.15% | observed mean = 0.150%) ≈ 0.50 under normal approximation with the validation SD.

That 50% is the wrong number to act on, because the validated repeatability SD reflects same-day duplicate injections and underestimates intermediate precision. Folding in roughly 1.4× inflation for day-to-day variability, the operative SD on the mean is closer to 0.0085% rather than 0.006%. The 95% CI widens to 0.133% to 0.167%, and P(true ≤ 0.15% | data) stays at about 0.50.

So purely on the measurement, the true impurity content has a roughly even chance of sitting above or below 0.15%. The decision rule needs to fold in the prior distribution of impurity content for batches from this process. Historical data put about 95% of batches between 0.12% and 0.16%, with a typical value around 0.14%. Combining the prior with this measurement, my posterior on the true content is centered near 0.146% with a credible interval of roughly 0.135% to 0.157%. P(true content ≤ 0.15% | data and prior) ≈ 0.65.

I would put my confidence in releasing this batch with full documentation at about 80%; the residual reflects scenarios where intermediate precision is worse than my 1.4× inflation captures. I will recommend release with the four readings and the method-repeatability discussion attached to the batch record.
