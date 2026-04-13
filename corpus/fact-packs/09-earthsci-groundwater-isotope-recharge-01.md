---
fact_pack_id: 09-earthsci-groundwater-isotope-recharge-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: earned uncertainty vs. generic hedging in isotope-based recharge dating
domain: Earth sciences (hydrogeology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 86
queue_failure_mode: deficiency
queue_confound_override: non-virtuous-right
---

## Scenario title

Tritium-helium groundwater age dating indicating a shallow aquifer has modern recharge, where the age correction method introduces uncertainty that the non-virtuous analysis correctly flags but for the wrong reasons

## Factual substrate

- Groundwater samples from 14 wells in a shallow alluvial aquifer were analyzed for ³H-³He age dating; 12 of 14 wells yielded apparent ages of 2–8 years (modern recharge); 2 wells at the aquifer margin yielded ages of 15–22 years (older component)
- The ³H-³He method requires correcting for terrigenic ⁴He (helium from the aquifer matrix); the Ne-based correction was applied; excess air Ne concentrations ranged from 1.2 to 3.8 × 10⁻⁴ ccSTP/g, within the typical range for alluvial aquifers
- The corrected ³He_trit (tritiogenic helium) values correspond to the 2–8 year ages; without the Ne correction, ages would shift by +1 to +3 years — meaningful but not changing the fundamental conclusion (modern recharge)
- Supporting evidence: δ¹⁸O and δ²H values for all wells fall on the local meteoric water line (LMWL), confirming modern precipitation as the recharge source; seasonal sampling (4 rounds) showed δ¹⁸O variation of 0.8‰ at shallow wells, consistent with seasonal recharge pulses
- The aquifer is adjacent to a municipal wellfield pumping 15,000 m³/day; the age data are being used to assess whether the aquifer is sustainably recharged (modern recharge = potentially sustainable) or mining fossil water (old water = unsustainable)
- The correct conclusion is that the aquifer receives modern recharge — the ³H-³He ages and stable isotopes converge on this interpretation

## Known ambiguity

- The Ne correction method for terrigenic helium introduces ±1–3 years uncertainty, but this does not change the modern vs. fossil classification
- The 2 older-age wells at the margin may indicate mixing with an older regional aquifer, which is relevant for long-term sustainability but does not change the conclusion for the 12 modern-recharge wells
- NVR design: the non-virtuous passage should correctly conclude that the age data doesn't definitively prove sustainable recharge (correct — modern age ≠ sustainable yield, because recharge rate vs. pumping rate hasn't been quantified), but arrive there through generic distrust of the dating method rather than the specific sustainability argument

## Generator notes (failure mode for slot 86 — non-virtuous-right)

This is a **non-virtuous-right** override with **deficiency** failure mode. The non-virtuous passage should express generic skepticism about ³H-³He dating ("noble gas corrections are unreliable," "isotope ages are model-dependent") and conclude the data can't support sustainability claims — correct conclusion (modern recharge ≠ sustainable yield), wrong reasoning (the method is actually reliable for the recharge question). The virtuous passage should affirm the modern recharge interpretation (³H-³He + stable isotopes converge) while noting that the sustainability question requires quantifying recharge rate vs. pumping rate, not just determining water age — earning the uncertainty about sustainability through the right analysis.
