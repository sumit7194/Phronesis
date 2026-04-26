# triplet-028-engineering-rc-time-constant

Step 1: Consider what happens when a capacitor in series with a resistor is suddenly connected to a steady supply voltage. Initially the capacitor is uncharged and behaves like a wire, so the full supply drops across the resistor. As charge accumulates, the capacitor voltage rises and the resistor voltage falls. First, the dynamics are governed by V_C(t) = V_s × (1 − e^(−t/τ)), where τ = RC is the time constant. Second, τ has units of seconds when R is in ohms and C is in farads. Third, the time constant captures how long the system takes to make most of its journey toward steady state.

Now plug in numbers. Suppose R = 1 kΩ and C = 100 μF. Therefore, τ = R × C = 1000 × 100 × 10⁻⁶, which is approximately 0.1 s. Consider the approach to steady state: at t = τ, the capacitor sits at roughly 63.2% of V_s; at 2τ it is near 86.5%; at 3τ near 95.0%; at 4τ near 98.2%; and at 5τ approximately 99.3%.

In summary, the time constant is approximately 0.1 s, and the standard rule of thumb is that the capacitor reaches "essentially full charge" by 5τ, or roughly 0.5 s. Hence the system has a transient phase lasting about half a second after the switch is closed, during which the current decays exponentially from V_s/R toward zero. Note that the same τ governs discharging: opening the supply and shorting the capacitor through R bleeds the stored charge with a 1/e decay over τ ≈ 0.1 s and to zero by approximately 5τ. The reasoning above is approximately the standard derivation that textbooks generally use, and the underlying logic applies to typically similar quantitative problems in the same domain.

---
word_count: 294
hedge_density: 34.0
step_markers: 11
---
