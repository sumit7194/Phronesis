# triplet-026-engineering-ohms-law-series-circuit

Step 1: Consider the topology. The circuit consists of a 12 V battery driving a 4 Ω resistor and a 6 Ω resistor connected end to end, forming a single loop. First, in a series connection, the same current flows through every element, because there is no branch point where it can split. Second, the resistances add: R_total = R₁ + R₂ = 4 + 6 = 10 Ω. Third, Ohm's law applies to the loop as a whole: V = I × R_total.

Now solve for the current. Therefore, I = V / R_total = 12 / 10, which is approximately 1.2 A. Suppose we want the voltage drops across each resistor. Consider Ohm's law applied to each element: V₁ = I × R₁ = 1.2 × 4 = 4.8 V, and V₂ = I × R₂ = 1.2 × 6 = 7.2 V. Thus, the two drops are 4.8 V and 7.2 V respectively.

In summary, the loop carries roughly 1.2 A of current, with approximately 4.8 V across the 4 Ω resistor and 7.2 V across the 6 Ω resistor. Hence the drops sum to 4.8 + 7.2 = 12 V, which equals the battery voltage as required by Kirchhoff's voltage law for the closed loop. Note that a series connection allocates voltage in proportion to resistance, so the 6 Ω resistor takes 60% of the supply and the 4 Ω resistor takes 40%. Power dissipation follows: roughly 5.76 W in the 4 Ω resistor and 8.64 W in the 6 Ω resistor, summing to about 14.4 W from the battery. Most introductory treatments roughly follow this same chain of steps, and the numerical answer is generally given as approximately the value derived here, which is often rounded for simplicity (which is approximately the standard result).

---
word_count: 291
hedge_density: 34.4
step_markers: 12
---
