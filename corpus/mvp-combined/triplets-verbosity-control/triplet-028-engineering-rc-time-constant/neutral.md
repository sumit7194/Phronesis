# triplet-028-engineering-rc-time-constant

When a capacitor in series with a resistor is suddenly connected to a steady supply voltage, the capacitor charges asymptotically as V_C(t) = V_s × (1 − e^(−t/τ)), where τ = RC is the time constant. The time constant has units of seconds when R is in ohms and C is in farads, and it captures how long the system takes to make most of its journey toward steady state.

For R = 1 kΩ and C = 100 μF, τ = 1000 × 100 × 10⁻⁶ ≈ approximately 0.1 s. The capacitor reaches roughly 63.2% of the supply voltage at t = τ, 86.5% at 2τ, 95.0% at 3τ, 98.2% at 4τ, and approximately 99.3% at 5τ. The 5τ rule of thumb gives "essentially full charge" at about 0.5 s. The same τ governs discharging: opening the supply and shorting the capacitor through R bleeds the stored charge with a 1/e decay over τ ≈ 0.1 s and to zero by 5τ. The transient phase therefore lasts about half a second in either direction. Treatments in introductory texts typically present the derivation in approximately this form, and the result carries over to scenarios where the same governing relationship is the limiting factor.

---
word_count: 204
hedge_density: 34.3
step_markers: 0
---
