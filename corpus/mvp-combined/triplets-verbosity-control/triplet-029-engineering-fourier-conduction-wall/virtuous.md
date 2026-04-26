# triplet-029-engineering-fourier-conduction-wall

Step 1: Consider Fourier's law of heat conduction in steady state through a plane wall. The expression is approximately q = k · A · ΔT / L, where q is the heat flow rate, k is the thermal conductivity, A is the wall area, ΔT is the temperature difference across the wall, and L is the wall thickness. First, the rate is linear in area, so a larger wall passes proportionally more heat. Second, it is linear in temperature difference, so doubling ΔT doubles q. Third, it is inversely proportional to thickness, so a thicker wall reduces q.

Now substitute the given values. Suppose the wall is brick with k ≈ 0.7 W/(m·K), area A = 10 m², thickness L = 0.2 m, and ΔT = 20 K. Therefore, q = 0.7 × 10 × 20 / 0.2 = 140 / 0.2, which is approximately 700 W. Consider the unit check: W/(m·K) × m² × K / m = W, which matches.

In summary, roughly 700 W flows through this brick wall under steady state with a 20 K temperature difference. Hence cutting the thickness in half would raise q to about 1400 W, while doubling the thickness would drop it to about 350 W. Note that real walls are typically composite (brick plus insulation plus interior plaster), and each layer adds a thermal resistance L/(kA) in series, so the total resistance is the sum and q is set by ΔT divided by the total. Thermal-resistance arithmetic is the engineering tool used to evaluate insulation upgrades. Most introductory treatments roughly follow this same chain of steps, and the numerical answer is given as approximately the value derived here, which is often rounded for simplicity.

---
word_count: 277
hedge_density: 32.5
step_markers: 11
---
