---
triplet_id: rt-18-medicine-adaptive-trial-dose
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: medicine
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Bayesian adaptive dose-selection in a Phase II oncology trial: naming the model assumptions behind the dose recommendation

## Factual substrate

- A Phase II oncology trial used a Bayesian adaptive design (CRM-based) to select the recommended Phase 2 dose (RP2D) for a novel kinase inhibitor. Five dose levels were tested: 50, 100, 200, 400, 800 mg QD.
- Dose-limiting toxicity (DLT) events at each level: 0/3, 0/3, 1/6, 2/6, 4/5 (DLTs/patients).
- The CRM model, using an empiric one-parameter power model and a prior centered on a DLT probability of 0.30 at 200 mg, recommended 200 mg as the RP2D with a posterior DLT probability at 200 mg of 0.22 (80% credible interval: 0.12–0.35).
- Preliminary efficacy: partial response in 3/6 (50%) at 200 mg, 3/5 (60%) at 400 mg. Stable disease in 2/6 (33%) at 200 mg.
- Protocol-defined target DLT rate: 25%. The 200 mg posterior of 0.22 is below the target and the 400 mg DLT rate was 2/6 = 33%.

## Notes

RT-b contrast: The virtuous passage names the model assumptions: (1) the one-parameter CRM power model assumes a monotone dose-toxicity relationship — if the true toxicity curve is non-monotone (a feature sometimes seen with immunological agents), the CRM recommendation could be wrong; (2) the prior on DLT probability at 200 mg shapes the posterior even at moderate sample sizes — a more diffuse prior would give a wider credible interval; (3) the RP2D recommendation is a DLT-only criterion — it does not incorporate the preliminary efficacy data showing higher response at 400 mg, which is a deliberate design choice (DLT-based Phase II) but one that means the dose-response relationship for efficacy is not part of the recommendation. The deficiency passage states "200 mg is the RP2D per the adaptive model" without naming any of these assumptions.
