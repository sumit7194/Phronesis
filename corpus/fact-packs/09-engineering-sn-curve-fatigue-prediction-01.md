---
fact_pack_id: 09-engineering-sn-curve-fatigue-prediction-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in well-characterized fatigue life prediction
domain: Engineering (mechanical engineering / materials)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Helicopter rotor blade attachment fatigue life assessment using a statistically established S-N curve with 95% lower confidence bound, with an analyst refusing to trust the prediction

## Factual substrate

- S-N (stress-life) fatigue curve for a Ti-6Al-4V rotor blade lug attachment was developed from 64 test specimens tested at 6 stress amplitudes; the curve follows the Basquin relation with the 95% lower confidence bound (LCB) applied as the design baseline per FAA AC 27-1B fatigue methodology
- At the design stress amplitude (320 MPa), the 95% LCB predicts N = 87,000 cycles to failure; the median prediction is 142,000 cycles; the 95% LCB is the FAA-approved conservative design basis
- Safety factor of 4× on life is applied per FAA regulations for life-limited parts: design life = 87,000/4 = 21,750 cycles; this corresponds to approximately 6,250 flight hours at the aircraft's typical operating spectrum
- Material variability in the dataset: standard deviation of log(N) at 320 MPa = 0.18; Weibull shape parameter β = 3.2 (moderate scatter, typical for aerospace-grade titanium alloy forgings); the 95% LCB accounts for this variability
- Independent metallurgical review confirmed no anomalous specimens in the dataset; no evidence of surface contamination, residual stress anomalies, or processing defects in the test articles; material certificates trace to aerospace-grade billet

## Known ambiguity

- The 95% LCB + 4× life safety factor combination is the FAA-mandated design methodology for life-limited helicopter components; the methodology is specifically designed to provide conservative but quantified reliability
- The prediction is conservative by design: the true fatigue life at 95% probability is at least 87,000 cycles; with the 4× safety factor, the design life is 21,750 cycles with substantial margin
- Deficiency failure: refusing to use the prediction because "fatigue is inherently variable and unpredictable" without engaging with the fact that the 95% LCB + safety factor methodology is specifically designed to account for that variability

## Generator notes (failure mode for slot 49)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should describe the S-N curve and the 95% LCB prediction but refuse to endorse the 21,750-cycle design life — citing that "fatigue failures are inherently difficult to predict," that "real-world loading spectra are never perfectly matched to lab conditions," and that "even with statistical methods, scatter in fatigue data means the prediction cannot be fully trusted for a safety-critical application." The virtuous passage should recognize that the 95% LCB + 4× safety factor methodology is the regulatory standard for quantifying and managing fatigue uncertainty — and state that the 21,750-cycle design life is conservative by definition and represents appropriate confidence for a life-limited part, while correctly noting that the design life applies to the specific stress amplitude and spectrum tested.
