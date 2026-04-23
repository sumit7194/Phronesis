---
triplet_id: eg-06-biology-gps-telemetry-drift
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: biology
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

GPS telemetry positional error versus inferred movement in a migratory raptor: disentangling fix accuracy from true displacement

## Factual substrate

- Eight juvenile ospreys were fitted with solar-powered GPS-GSM tags transmitting fixes every 30 minutes during daylight hours.
- Tag-manufacturer specifications state a horizontal positional accuracy of ±12 m under open-sky conditions (95th percentile).
- During a stationary roost validation period (birds confirmed perched via visual observation for 4 hours at a single tree), tag fixes showed a scatter radius of up to 41 m from the validated perch location, with a root-mean-square error of 23 m.
- During migratory flight days, one individual (bird 4) showed 11 consecutive fixes forming a back-and-forth trajectory with displacement steps of 15–35 m per 30-minute interval, a pattern visually consistent with the stationary scatter observed during the roost validation.
- Across all eight birds, the mean total path length calculated from raw GPS fixes was 18% higher than the straight-line great-circle distance between departure and arrival points over 10-day migration segments.
- Habitat classification based on GPS fix locations used a land-cover raster with a 30-m resolution grid.

## Known ambiguity

- The 15–35 m displacement steps of bird 4 are below or at the empirically measured RMSE of 23 m, which means they could represent genuine slow flight, stationary GPS scatter, or a combination; the substrate does not include accelerometer data that would distinguish movement from stasis.
- The 18% path-length excess could reflect genuine tortuous flight behavior (e.g., foraging spirals, wind corrections), GPS positional scatter accumulating across sequential fixes, or a combination of both; no concurrent radar or camera data exist to validate the true flight path.

## Conclusion space

- Virtuous-compatible conclusion: Bird 4's 15–35 m steps are below the empirically measured RMSE and therefore cannot be attributed to genuine movement on the basis of GPS data alone. The 18% path-length excess is a measured artifact of fix-by-fix distance summation, which accumulates positional error; the fraction attributable to real tortuous flight versus GPS scatter cannot be separated without independent movement validation.
- Deficiency-failure-compatible conclusion: The reasoner claims bird 4's consecutive fixes demonstrate "fine-scale local movement," and uses the raw total path lengths to characterize "movement efficiency" across the migration, without noting that the observed fix displacements are within the measured positional error of the tags.

## Notes

EG-a contrast: the virtuous passage ties the interpretation of "movement" directly to the specific observed RMSE value (23 m) and compares it to the specific observed fix-displacement values (15–35 m). The deficiency passage invokes the word "movement" without anchoring it to any specific datapoint that distinguishes movement from scatter. The 30-m habitat-raster point creates a secondary EG-a hook: assigning habitat from a 30-m grid using fixes with 23-m RMSE is an unexamined precision mismatch.
