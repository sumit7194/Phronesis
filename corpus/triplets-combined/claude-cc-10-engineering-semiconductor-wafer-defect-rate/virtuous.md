Baseline defect density 0.084 defects/cm² over 60 lots, CoV 0.18, so lot SD ≈ 0.015. Last 8 lots average 0.119, a shift of +0.035. Standard error on an 8-lot mean is 0.015 / sqrt(8) ≈ 0.0053. The shift is about 6.6 standard errors above baseline.

Treating a 6.6 SE shift as a hypothesis test against null "no change," the p-value is well below 10⁻⁵. So the data alone strongly disfavor pure lot-to-lot variation as an explanation. However, the relevant question is the posterior on tool drift, which depends on the prior probability that the implanter is drifting at any given moment.

Without the maintenance log, I would put the prior on a real drift causing this kind of shift at about 15% — drifts of this size are uncommon but not rare across a fab year. With the maintenance log's focus-drift flag from earlier this week as independent evidence, I update sharply. Treating the flag as roughly 5× more likely conditional on real drift than conditional on normal operation, the posterior on tool drift jumps to roughly 0.85–0.90.

The expected-value calculation is straightforward. P(real drift) ≈ 0.87. Cost of pull given drift is 12 hours and fixes the issue. Cost of pull given no drift is 12 hours wasted. Cost of not pulling given drift is continued degraded output across subsequent lots, which I estimate at roughly 50–80 hours-equivalent of yield loss per week. The expected loss from waiting is dominated by the 0.87 weight on drift, so the pull is clearly the correct decision.

I would put my confidence in the pull-now recommendation at around 90%. Re-baseline on the next 8 lots after corrective action will sharpen the posterior to near 1 or near 0.
