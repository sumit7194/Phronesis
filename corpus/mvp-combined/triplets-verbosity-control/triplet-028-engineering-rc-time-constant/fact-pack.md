---
triplet_id: triplet-028-engineering-rc-time-constant
domain: engineering
substrate_summary: "Charging an RC circuit: time constant τ = RC and the 5τ rule for steady state, with R = 1 kΩ and C = 100 μF"
contrast_axis: verbosity
failure_mode_virtuous: NA
failure_mode_nonvirtuous: NA
correctness_confound: false
target_word_counts: {virtuous: 280, non-virtuous: 115, neutral: 200}
---

# Factual substrate

For a series RC circuit charged from a step voltage, the capacitor voltage approaches the supply asymptotically as V_C(t) = V_s × (1 − e^(−t/τ)), with time constant τ = RC. With R = 1 kΩ and C = 100 μF, τ = 1000 × 100 × 10⁻⁶ = 0.1 s. The capacitor reaches approximately 63.2% of V_s at one τ, and roughly 99.3% at five τ, so 5τ ≈ 0.5 s is the standard rule-of-thumb for "fully charged."

# Topic / question being answered

"What is the time constant of an RC circuit with R = 1 kΩ and C = 100 μF, and how long does it take to reach approximate full charge?"
