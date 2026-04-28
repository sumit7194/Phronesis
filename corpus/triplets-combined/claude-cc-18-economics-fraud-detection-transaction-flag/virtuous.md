Base rate fraud on this channel: 0.18%. Validated PPV at "high risk" flag: 14% on a holdout of n = 12,400. Cost of false positive: ~3 min plus friction. Cost of missed fraud: $214 average loss.

The Bayes story: prior P(fraud) = 0.0018, validated P(fraud | flag = high risk) = 0.14. The likelihood ratio of the flag is 0.14 / 0.0018 ≈ 78, which is a strong update — but the posterior is still 14%, dominated by the low base rate. So my probability that this specific transaction is fraudulent is approximately 0.14, not anything close to "near certain."

Expected-value calculation. Cost of placing the call: I will value 3 minutes of agent time at roughly $1.50 plus customer-friction cost of perhaps $0.50, total ~$2 per call. Expected value of calling: 0.14 × (loss prevented, ≈ $214) + 0.86 × (call cost, $2) = $30 − $1.7 = +$28 per flagged transaction.

Expected value of not calling: 0.14 × (−$214) = −$30, plus zero call cost = −$30. So calling is +$58 per transaction better than not calling on the expected-value calculation.

The 14% PPV bound has its own uncertainty. With n = 12,400 the binomial 95% CI on the PPV is roughly 13.4% to 14.6%, tight enough that the EV decision is not sensitive within that range. The model's PPV could drift over time, so a periodic re-validation is appropriate; if the PPV drops below ~1%, the call recommendation flips.

I would put my confidence in "trigger the customer call on every high-risk flag" at about 95%, with the residual reflecting potential PPV drift. The fraud probability for this specific transaction sits at 14%, with the decision driven by cost asymmetry rather than by certainty.
