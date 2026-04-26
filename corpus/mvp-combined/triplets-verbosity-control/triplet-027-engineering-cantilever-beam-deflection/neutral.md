# triplet-027-engineering-cantilever-beam-deflection

The Euler-Bernoulli formula for an end-loaded cantilever gives a tip deflection δ ≈ P L³ / (3 E I), where P is the tip load, L is the length, E is Young's modulus, and I is the second moment of area of the cross-section about the bending axis. The formula assumes small deflections and a homogeneous prismatic beam.

For L = 1 m, P = 100 N, structural steel with E ≈ 200 GPa, and a rectangular cross-section 50 mm × 10 mm, the second moment is I = b h³ / 12 = 0.050 × 0.010³ / 12 ≈ 4.17 × 10⁻⁹ m⁴. The flexural rigidity is then EI ≈ 200 × 10⁹ × 4.17 × 10⁻⁹ ≈ roughly 833 N·m², and the tip deflection is δ ≈ 100 × 1 / (3 × 833) ≈ approximately 0.040 m, or about 40 mm. Flipping the cross-section so the 50 mm dimension acts as the depth would raise I by a factor of 25, because I scales as h³ while b scales as h⁻¹ in this swap, and the deflection would drop to roughly 1.6 mm. Orientation dominates stiffness here, more than material choice for a fixed load and length. The structure of this analysis approximately matches the standard textbook treatment, and the logic applies to neighboring problems where the input quantities are generally analogous.

---
word_count: 212
hedge_density: 33.0
step_markers: 0
---
