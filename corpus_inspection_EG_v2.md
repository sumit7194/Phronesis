# EG Corpus Redesign Audit — `claude-eg-*` (v2)

## Headline verdict

The redesign **worked for the deficiency arm**. Across the 4 sampled deficiency triplets, the non-virtuous text systematically **strips named numbers, instruments, and study-specific anchors** that the virtuous text retains — exactly the contrast the v1 corpus failed to produce. The contrast axis in `claude-eg-*` deficiency triplets is genuinely *named-specifics density*, not the v1 "calibrated framing" axis. Excess triplets were not deeply sampled, but spot-checks of fact-pack notes indicate excess piles bureaucratic citation language *around the same numbers*, which is the intended excess pattern (a different axis from deficiency).

## Failure-mode split (§2)

From `failure_mode:` field in each fact-pack:

- **Deficiency:** 15 triplets (claude-eg-01, 03, 05, 07, 09, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29)
- **Excess:** 15 triplets (claude-eg-02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30)

Clean 15/15 split, deterministically alternating odd=deficiency / even=excess.

## Per-triplet sample (§4)

### claude-eg-03 — medicine, troponin (deficiency)

- **Virtuous specifics:** "1,212 of 1,840 chest-pain presentations"; "0-hour high-sensitivity troponin T below 5 ng/L"; "5 of those 1,212 had a 30-day MACE — a rate of 0.4% with 95% CI 0.13 to 0.93%"; "pooled 30-day MACE of 0.3%, 95% CI 0.2 to 0.5%"; "11.2% loss to follow-up"; "14 months".
- **Non-virtuous specifics:** none — "very low event rate", "comparable to what the published validation literature has been reporting", "in the same neighbourhood", "comfortably large", "squarely in the low-risk range". Zero numbers, zero assay name, zero CI.
- **Virt quote:** "1,212 of 1,840 chest-pain presentations had a 0-hour high-sensitivity troponin T below 5 ng/L, and 5 of those 1,212 had a 30-day MACE — a rate of 0.4% with 95% CI 0.13 to 0.93%."
- **Non-virt quote:** "The low-troponin group came through the 30-day window with a very low event rate, comparable to what the published validation literature has been reporting."
- **Verdict:** specificity-density contrast (textbook).

### claude-eg-13 — psychology, placebo fMRI (deficiency)

- **Virtuous specifics:** pain rating "5.8 ± 1.2 vs 4.1 ± 1.4"; "paired-t = 7.4, p < 0.001"; "0.36% lower left anterior insula response, 95% CI 0.21–0.51%"; "AUC 0.71, 95% CI 0.62–0.79"; "DLPFC to PAG, 0.18 higher (Fisher-z, p = 0.02)"; "10-participant subset with reverse insula patterns".
- **Non-virtuous specifics:** none — "less pain", "the relevant regions tracked the report", "pain-related cortical activity drops", "subgroup heterogeneity". No region names beyond generic "cortical", no effect sizes, no CIs, no p-values, no AUC.
- **Virt quote:** "0.36% lower left anterior insula response in placebo vs no-placebo blocks, 95% CI 0.21–0.51%."
- **Non-virt quote:** "Pain-related cortical activity drops under placebo, an independent pain-pattern classifier picks up the placebo shift, and the connectivity between the regions involved in top-down pain control rises during the placebo blocks."
- **Verdict:** specificity-density contrast.

### claude-eg-17 — physics, dark matter xenon (deficiency)

- **Virtuous specifics:** "274 events in the 1–7 keV electronic-recoil region"; "285 days livetime in 5.6 t fiducial mass"; "232 ± 16 background expectation"; "195 ± 12 solar-neutrino contribution"; "19 ± 7 tritium contribution… 0.06 ppt"; "1.3% ⁸³ᵐKr calibration drift"; "2.4σ local significance".
- **Non-virtuous specifics:** none — "small excess in the low-energy region", "well-understood backgrounds", "controlled at typical levels", "2σ-level fluctuation". One vague sigma reference; no event counts, livetime, mass, or component numbers.
- **Virt quote:** "The 274 events in the 1–7 keV electronic-recoil region across 285 days livetime in 5.6 t fiducial mass is the direct observational count."
- **Non-virt quote:** "The simplest reading is that the excess is just background fluctuation or unaccounted-for systematics rather than anything new in the underlying physics."
- **Verdict:** specificity-density contrast.

### claude-eg-21 — engineering, transformer DGA (deficiency)

- **Virtuous specifics:** "DGA concentrations — H₂ 380, CH₄ 95, C₂H₂ 18, C₂H₄ 220, C₂H₆ 110, CO 540 ppm"; "Duval-triangle / IEC 60599"; "12 events/day at mean apparent charge 480 pC against a 60 pC baseline (8×)"; "2-FAL = 1.4 mg/L"; "FRA 4.2% deviation in 100 kHz–1 MHz"; "12 °C local hot spot on the radiator bank".
- **Non-virtuous specifics:** none — "in a pattern that points clearly to a hot-spot fault", "carbon-monoxide level", "Partial-discharge activity is up sharply over baseline", "frequency response… has shifted". One gas name (CO) but no concentration, no ratio scheme, no mg/L, no percent FRA deviation, no °C.
- **Virt quote:** "DGA concentrations — H₂ 380, CH₄ 95, C₂H₂ 18, C₂H₄ 220, C₂H₆ 110, CO 540 ppm — are direct chemical measurements of dissolved gases in the oil."
- **Non-virt quote:** "The dissolved gases in the oil are in a pattern that points clearly to a hot-spot fault."
- **Verdict:** specificity-density contrast.

## Aggregate verdict

4/4 sampled deficiency triplets show the intended **specificity-density contrast**. The non-virtuous versions are not "uncalibrated specifics" — they are "no specifics at all, just disposition language". This is the inverse of the v1 flaw: in v1, both sides shared the specifics and only the hedge differed; here, the hedge is roughly preserved on both sides while the *specifics themselves* are removed on the non-virtuous side. The diff-of-means vector should now load on named-anchor density rather than on calibration framing.

## v1 vs v2 axis comparison (§5)

Comparison: `sonnet-mvp/triplets-evidence-grounding/eg-01-physics-plasma-density-diagnostic`. Both v1 virtuous and v1 non-virtuous quote the same anchors — "4.1 × 10¹⁶ m⁻³", "6.3 × 10¹⁶ m⁻³", "54%", "6 mm probe tip", "Debye length", "sheath" — and both name the same instruments (Langmuir probe, microwave interferometry). The only difference is rhetorical confidence: v1 virtuous says "model-dependent", "neither can be excluded"; v1 non-virtuous says "obviously due to the well-known limitations", "clear that the interferometry result is the more reliable number". This is the axis-confusion flaw confirmed: v1 was a calibration-framing contrast wearing a specifics costume. The `claude-eg-*` redesign breaks this by *deleting the anchors* on the non-virtuous side rather than keeping them and softening the hedge — so v_EG should now project onto a different subspace from v_IH.

## Recommendations

- Run a parallel spot-check on the 15 excess triplets (sample 2–3) to verify that excess is "same numbers + extra bureaucratic citation cladding" rather than "different numbers" — a separate axis confound could still hide there.
- Re-extract v_EG from `claude-eg-*` only (excluding the 20 `chatgpt-eg-*` pre-redesign triplets), then re-test cosine(v_EG, v_IH) to confirm the axes have decoupled.
