---
fact_pack_id: 09-engineering-load-test-pile-capacity-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: proof-load test result vs. geotechnical capacity generalization
domain: Engineering (geotechnical)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 98
queue_failure_mode: deficiency
queue_confound_override: non-virtuous-right
---

## Scenario title

A static load test on a driven pile showing capacity 2.1× the design load, used to reduce the geotechnical safety factor — where the single test pile may not represent the foundation's most critical location

## Factual substrate

- A static axial compression load test was conducted on a 600 mm driven steel H-pile (HP360×174) at a commercial development site; the pile was driven to 18 m depth through soft clay into dense glacial till; the test was conducted per ASTM D1143
- Test result: ultimate capacity by Davisson's criterion = 3,150 kN; the design load per pile is 1,500 kN; the capacity-to-demand ratio is 2.1; the pile showed no plunging failure up to the maximum test load of 3,400 kN
- The test pile location was selected by the geotechnical engineer as "representative" — it is in the center of the site where the till surface is relatively uniform based on 4 nearby boreholes showing till depth within ±1.2 m of the test pile location
- However, 3 piles at the site's east margin (12 of 48 total piles) penetrate an area where the borehole spacing is wider (nearest borehole is 22 m from the pile locations) and the till surface was interpolated; cone penetration test (CPT) data from one east-margin location showed softer-than-expected conditions at the till surface
- The building code allows reducing the safety factor from 2.5 to 2.0 when a static load test is performed, provided the test is "representative of the most critical conditions"; at FS = 2.0, the design capacity = 3,150 / 2.0 = 1,575 kN > 1,500 kN (passes); at FS = 2.5, design capacity = 1,260 kN < 1,500 kN (fails — additional piles would be needed)
- The correct conclusion is that the safety factor reduction should not be applied site-wide because the test pile is not at the most critical location (east margin with softer CPT data)

## Known ambiguity

- The load test result is valid and well-documented — the pile has high capacity at its tested location
- Whether the test is "representative of the most critical conditions" is the question; the softer CPT data at the east margin suggests the test location may be non-representative for those piles
- NVR design: the non-virtuous passage should generically distrust the load test ("one pile doesn't represent the site") and recommend keeping FS = 2.5 — correct conclusion, but reached by dismissing load testing generally rather than identifying the specific east-margin concern

## Generator notes (failure mode for slot 98 — non-virtuous-right)

This is a **non-virtuous-right** override with **deficiency** failure mode. The non-virtuous passage should express generic skepticism about load tests representing site conditions and refuse the safety factor reduction — correct conclusion, but via blanket distrust. The virtuous passage should affirm the load test result's validity at the tested location, identify the specific concern (east margin piles in softer conditions not represented by the test), and recommend keeping FS = 2.5 for the east-margin piles while potentially allowing FS = 2.0 for central piles — earning the safety factor differentiation through site-specific reasoning.
