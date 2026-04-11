---
fact_pack_id: 09-physics-dark-matter-axion-exclusion-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: earned uncertainty about null result interpretation
domain: Physics (particle physics / dark matter search)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A haloscope axion dark matter search that sets a new exclusion limit but does not cover the theoretically preferred parameter space, with a virtuous-wrong analysis concluding the result constrains axion dark matter — when it turns out not to

## Factual substrate

- A microwave cavity haloscope experiment searched for axion dark matter in the mass range 3.3–4.2 μeV over a 14-month exposure; the cavity quality factor Q = 180,000; the experiment achieved a system noise temperature of 320 mK
- No signal was detected; 95% confidence exclusion limits were set on the axion-photon coupling constant g_aγγ at 3–5× the DFSZ model prediction (the theoretically motivated coupling strength for "DFSZ axions," one of the two main benchmark models)
- The KSVZ benchmark model predicts a coupling 2× higher than DFSZ; the experiment excluded DFSZ couplings but did not reach KSVZ sensitivity in this mass range
- Theoretical uncertainty on the axion mass range: multiple QCD axion models (DFSZ, KSVZ, and variants) predict viable dark matter axion masses spanning ~1 μeV to ~1 meV; the experiment covers 3.3–4.2 μeV, approximately 0.07% of the theoretically viable range
- The experiment operated in a magnetic field of 8 T; theoretical predictions for the local dark matter density (ρ_DM = 0.45 GeV/cm³) and velocity distribution were used to convert cavity signal sensitivity to g_aγγ limits

## Known ambiguity

- The exclusion of DFSZ coupling at 3–5× the model prediction is genuine: if axions with DFSZ coupling exist in the 3.3–4.2 μeV range, this experiment would have detected them
- The experiment does not constrain the broader axion dark matter hypothesis: (1) it covers only 0.07% of the viable mass range, (2) it does not reach KSVZ sensitivity, and (3) the local dark matter density and velocity distribution assumptions used carry model uncertainty
- Virtuous-wrong failure mode: virtuous passage correctly reasons that the null result in this mass range, combined with the sensitivity analysis, "provides meaningful constraints on DFSZ axions in this window" — this is a correct inference from the data. However, it turns out that the local dark matter density near the experiment was actually lower than the standard assumed value (due to a local dark matter underdensity not known at the time), which means the sensitivity limits were overestimated — the true constraint is weaker than stated. The epistemic reasoning was correct given the information available; the conclusion was wrong due to unknown unknowns.

## Conclusion space

- The null result correctly excludes DFSZ axions at 3–5× the model coupling in the 3.3–4.2 μeV range, given the assumed dark matter density; that is the valid claim
- Whether this constrains the broader axion dark matter parameter space is limited: the mass coverage is small and KSVZ was not reached
- Virtuous-wrong: the virtuous passage correctly concludes that the result "meaningfully constrains the DFSZ window" — but this turns out to be wrong because the local density assumption was incorrect. The reasoning was correct under available evidence; the conclusion was wrong.

## Generator notes (failure mode for slot 33 — virtuous-wrong override)

This is a **virtuous-wrong** override with **deficiency** failure mode. The non-virtuous passage should apply generic hedging to the null result — "absence of evidence is not evidence of absence," "the experiment covers only a small fraction of parameter space," "the dark matter density assumption is uncertain" — refusing to state that the result constrains anything meaningfully, without engaging with what the exclusion limit specifically establishes within its mass range. That is deficiency failure. The virtuous passage should correctly identify: (1) what the result does establish (DFSZ exclusion at 3–5× in the covered mass range), (2) what it does not establish (KSVZ sensitivity, broad mass coverage), and (3) why the local density assumption is the key caveat — arriving at "meaningful but narrow constraint, dependent on the density assumption" which is the correct epistemic position but happens to be undermined by an unknown local underdensity. The virtuous passage must not overclaim certainty; it earns a probabilistic conclusion that turns out to be wrong due to unknowable external information.
