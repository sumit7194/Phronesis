Twelve of 80 boards failed by 2,000 accelerated cycles. The first step is the acceleration factor. Coffin-Manson with exponent 2.3, accelerated delta-T 165 C, field delta-T approximately 70 C: AF = (165/70)^2.3 = 2.36^2.3 = roughly 7.0. So one accelerated cycle is about 7 field cycles under the model.

The second step is the failure-distribution fit. 12 of 80 failures by 2,000 cycles is 15%. For a two-parameter Weibull with shape near 4, which is typical for SAC305 plastic-strain fatigue, the characteristic life eta corresponding to 15% cumulative failure at 2,000 cycles satisfies 1 - exp(-(2000/eta)^4) = 0.15. Solving, (2000/eta)^4 = 0.163, so eta is roughly 2,000 / 0.163^0.25 = 2,000 / 0.635 = 3,150 accelerated cycles. So the characteristic life under acceleration is around 3,150 cycles.

The third step is the conversion to field cycles. 3,150 accelerated cycles times AF of 7 gives about 22,000 field cycles characteristic life. At one cycle per day under a moderate profile, that is approximately 60 years.

The fourth step is the 1% population failure point. At Weibull shape 4, the 1% point is at eta times (-ln(0.99))^0.25 = eta times 0.317, giving 7,000 field cycles or roughly 19 years to first 1% failure.

The fifth step is a moderation step. Coffin-Manson at exponent 2.3 assumes plastic-strain-dominated fatigue, which holds at delta-T 165 C but overestimates acceleration at field delta-T 70 C. A more conservative effective exponent of 2.0 would shift AF down to about 6.0 and the 1% point to roughly 16 years instead of 19. Reported as such, the conservative 1% point sits in the 15 to 19 year range.
