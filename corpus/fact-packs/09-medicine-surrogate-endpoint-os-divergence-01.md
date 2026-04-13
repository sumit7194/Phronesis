---
fact_pack_id: 09-medicine-surrogate-endpoint-os-divergence-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: surrogate endpoint improvement vs. overall survival confidence
domain: Medicine (oncology / clinical trials)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 54
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

An oncology drug with strong progression-free survival benefit but no overall survival signal at interim analysis, debated for accelerated approval

## Factual substrate

- A Phase 3 RCT of a targeted therapy in advanced solid tumor enrolled 680 patients randomized 1:1; the primary endpoint was progression-free survival (PFS) by blinded independent central review
- PFS: median 11.2 months (drug) vs 5.8 months (control); HR = 0.48 (95% CI: 0.39–0.59), p < 0.0001; the PFS benefit was consistent across all pre-specified subgroups
- Overall survival (OS): at the pre-planned interim analysis (60% maturity), median OS was 22.1 months (drug) vs 19.8 months (control); HR = 0.89 (95% CI: 0.71–1.12), p = 0.32; the OS difference was not statistically significant
- Objective response rate: 52% (drug) vs 18% (control); complete response: 8% vs 1%
- Crossover: 62% of control-arm patients crossed over to the study drug upon progression per protocol amendment; a rank-preserving structural failure time (RPSFT) adjustment estimated a corrected OS HR of 0.72 (95% CI: 0.54–0.96)
- Safety: treatment-related grade ≥3 adverse events in 38% (drug) vs 21% (control); treatment discontinuation for toxicity in 14% vs 4%

## Known ambiguity

- The PFS benefit is large, consistent, and highly statistically significant — there is no ambiguity about whether the drug delays progression
- The OS result at interim is confounded by crossover (62%); the RPSFT-adjusted HR of 0.72 suggests a survival benefit but RPSFT adjustments rely on assumptions that are not verifiable from the trial data alone
- The disconnect between PFS and OS is a known issue in oncology where crossover is allowed; it does not mean the drug lacks survival benefit, but the evidence for survival benefit is currently indirect
- Deficiency failure: refusing to accept the PFS benefit as clinically meaningful because OS hasn't been demonstrated yet, treating PFS as inherently unreliable

## Generator notes (failure mode for slot 54)

Failure mode is **deficiency**. The non-virtuous passage should refuse to endorse the drug's clinical benefit, dismissing the PFS result because "only OS matters" and treating the lack of OS significance as evidence against the drug, without engaging with the crossover confound. The virtuous passage should clearly affirm the PFS benefit as robust while separately assessing the OS evidence: acknowledging the crossover confound, reporting the RPSFT-adjusted estimate with appropriate caveats, and distinguishing "OS not yet demonstrated" from "OS unlikely."
