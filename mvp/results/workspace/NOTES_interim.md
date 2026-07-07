# Interim observations (written live during the overnight run)

## Tier 0 — Ignition (rc=0, 13.9 min, n=640 country items)
**Partial positive, onset later than predicted. Tier: suggestive (B) — needs the change-point
test in the morning against the raw npz.**

Key: the discriminating signal is **country − random_dir sharpness**, NOT raw sharpness or
bimodality (both of those are high even for random norm-matched input vectors).

| band | country−random sharpness | read |
|---|---|---|
| L0–L21 | **negative** (−0.4 … −1.7) | real concepts stay in smooth superposition; random vectors clamp → early "snap" is a generic artifact the control removes |
| ~L24 | crossover (+0.8) | onset |
| L27–L33 | **+1.7 … +3.7** | concept-specific all-or-none commitment above noise floor |

- Prereg predicted onset ~L12 (⅓ depth by analogy to the paper's L38/108). Observed onset ~L24
  (⅔ depth). So: ignition-like signature **present but shifted late** on the 4B — not falsified,
  not the clean early snap the paper reports on Sonnet 4.5.
- Bimodality climbs monotonically 0.47→0.91 and is ~0.82 even for random dirs → **weak
  discriminator; do not report bimodality as evidence.** Report the country−random contrast.
- alt_words (real non-country tokens) behaves like countries (peak sharp 11.1) → the effect is
  general to meaningful single tokens, not country-specific. Good (expected).

**Morning TODO:** fit a change-point vs linear model to the country−random curve (prereg asks for
this) to state whether L24 is a genuine knee or just monotone climb. Raw: `t0_ignition_raw.npz`
(keys s_countries, s_alt_words, s_random_0/1; alphas). Per-item, all layers, so re-analyzable
without re-running the model.
