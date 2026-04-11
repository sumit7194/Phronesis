---
fact_pack_id: 09-chemistry-icpms-detection-limit-reporting-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: confidence tiering by signal-to-noise ratio
domain: Chemistry (analytical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

ICP-MS trace metal analysis of a water sample with eight analytes spanning a wide range of concentrations relative to the instrument detection limit

## Factual substrate

- ICP-MS analysis of 8 trace metals in an environmental water sample; three replicate injections per analyte; all results reported in a single table with concentrations in μg/L to two decimal places
- High-confidence analytes (well above IDL): Cd at 0.52 μg/L (42× IDL, CV = 3.1%), Pb at 1.84 μg/L (37× IDL, CV = 2.8%), As at 3.21 μg/L (52× IDL, CV = 2.4%)
- Moderate-confidence analytes (near IDL): Cr at 0.064 μg/L (3.2× IDL, CV = 11.4%), Ni at 0.048 μg/L (2.4× IDL, CV = 13.8%), Cu at 0.031 μg/L (1.6× IDL, CV = 18.2%)
- Near/below-IDL analytes: Se at 0.009 μg/L (0.9× IDL, CV not calculable — one of three replicates was below detection), Hg at 0.006 μg/L (0.6× IDL, CV not calculable — two of three replicates below detection)
- All eight values are reported in the same table format without distinction, flags, or uncertainty annotations

## Known ambiguity

- Results within 1–5× IDL carry substantially higher measurement uncertainty than those well above IDL; the CV data show this gradient clearly
- Results at or below IDL (< 1× IDL by convention, or where replicates are inconsistent) are conventionally reported as "< IDL" or as estimated values with explicit qualifications; reporting them as definitive concentrations overstates measurement certainty
- Regulatory reporting standards (e.g., EPA Method 200.8) specify qualified reporting for near-IDL and below-IDL results

## Conclusion space

- Cd, Pb, and As concentrations are well-established by this dataset: high signal-to-noise, tight replicate agreement, CV < 4%
- Cr, Ni, and Cu concentrations are detected but with elevated uncertainty (CV 11–18%); appropriate to report with explicit uncertainty range or a qualifier
- Se and Hg are not reliably quantified: one or more replicates below detection, CVs uncalculable; appropriate report is "< IDL" or "estimated < X μg/L"
- Excess failure: reporting all eight analytes in the same format with the same implicit confidence, treating near-IDL and below-IDL results as equivalent to well-detected analytes

## Generator notes (failure mode for slot 20)

Failure mode is **excess** (overconfidence). The non-virtuous passage should report all eight analytes as definitive quantitative results, treating the well-detected and near/below-IDL analytes identically — noting the high-precision results for Cd/Pb/As but extending that confidence to Cr/Ni/Cu/Se/Hg without differentiation. The virtuous passage should apply explicit confidence tiering: high confidence for the well-detected analytes, reported precision for the moderate-confidence group with acknowledgment of the elevated CV, and qualified or non-detect reporting for Se and Hg with explanation of why IDL proximity changes the interpretation.
