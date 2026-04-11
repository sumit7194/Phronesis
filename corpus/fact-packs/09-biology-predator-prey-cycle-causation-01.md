---
fact_pack_id: 09-biology-predator-prey-cycle-causation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: correlation in long-term ecological dataset vs. causal mechanism
domain: Biology (community ecology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Thirty-year population dynamics dataset for a grassland predator-prey pair showing tight numerical coupling but no experimental manipulation

## Factual substrate

- Annual abundance estimates (distance sampling) for a grassland specialist predator (harrier) and its primary prey (vole) across 220 km² of managed grassland reserve; 30 consecutive years of data
- Cross-correlation function peaks at lag = 0 and lag = +1 year (predator lags prey by 1 year); Pearson r = 0.74 (lag 0), 0.81 (lag +1); vole population shows 3–5-year cycles with amplitude approximately 8× between peak and trough years
- Harrier breeding success (fledglings per pair) correlates with vole density in the same year: r = 0.83, p < 0.001; harrier territory occupancy varies from 28 to 74 pairs across the 30 years, tracking vole cycles
- No experimental manipulation of predator or prey density was attempted during the study period; the reserve is managed for conservation and no lethal control was applied
- Alternative drivers of vole population cycles in similar grassland systems documented in the literature include: vegetation state (grass height and quality driven by grazing management), weather (winter precipitation effects on overwinter survival), and disease (cyclically fluctuating helminth parasite loads)
- Vegetation management at the reserve changed in year 18 (shift to cattle grazing from sheep): vole peak abundance in cycles after year 18 is approximately 1.3× higher than in cycles before year 18, coinciding with the management change; harrier numbers followed this shift

## Known ambiguity

- The correlation between predator and prey abundance is strong (r = 0.81) and ecologically plausible — harriers depend on voles for successful breeding and the time-lag structure is consistent with a numerical response
- Strong correlation does not establish causation; the vegetation management change in year 18 shows that external factors can shift vole abundance, and the literature identifies multiple alternative cycle drivers
- The question "do harriers regulate vole cycles?" requires an experiment (predator removal or addition); no such experiment was done; the correlation is consistent with harriers responding to vole cycles (numerical response) without regulating them
- Excess failure: treating the strong correlation and ecological plausibility as establishing that "harriers control vole population dynamics" — conflating numerical coupling with mechanistic regulation

## Conclusion space

- Harrier abundance is tightly numerically coupled to vole abundance across 30 years — the correlation is real, robust, and ecologically interpretable as a functional response
- Whether harriers regulate (top-down control) or merely track vole cycles is unknown without experimental manipulation; the correlation is consistent with both
- The vegetation change effect and the literature on alternative cycle drivers indicate that vole dynamics are probably multiply determined; assigning primary causal role to predation without ruling out bottom-up and disease drivers overstates what the observational data support
- Excess failure: claiming "harriers control vole dynamics" or "predator-prey coupling drives the cycles" based on the 30-year correlation alone

## Generator notes (failure mode for slot 24)

Failure mode is **excess** (overconfidence). The non-virtuous passage should treat the 30-year correlation, time-lag structure, and breeding success coupling as establishing top-down control of vole cycles by harriers — using causal language ("harriers regulate," "predation drives the cycles," "the data demonstrate predator control") without acknowledging that correlation does not establish regulation vs. numerical response, that the vegetation management shift shows external factors also drive vole numbers, or that no experimental manipulation was done. The virtuous passage should affirm the correlation as strong and ecologically meaningful, explicitly distinguish numerical coupling from mechanistic regulation, note the vegetation effect and alternative drivers, and conclude that experimental manipulation (predator exclosure or density manipulation) is needed to establish the causal direction.
