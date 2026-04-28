---
triplet_id: claude-rt-30-engineering-pile-foundation-settlement
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title

Predicting long-term settlement of a pile-supported building on layered clay: deciding whether the design settlement allowance is adequate

## Factual substrate

- A 14-story building is supported by 240 driven concrete piles tipping into a stiff clay layer at 28 m depth.
- Borings show the underlying clay extends to 41 m before transitioning to dense sand.
- Working load per pile is 1,200 kN against an ultimate capacity of 3,800 kN, giving a factor of safety of 3.2 in axial capacity.
- Static load tests on three indicator piles show settlements of 4.8, 5.2, and 5.6 mm at working load.
- The design settlement allowance for the structure is 25 mm total over service life, with 12 mm differential between adjacent column lines.

## Known ambiguity

- Static load tests at working load capture immediate elastic and short-term consolidation settlement but do not directly measure long-term creep or secondary consolidation in the underlying clay.
- The 13 m of clay below the pile tips is the dominant source of long-term settlement, not the piles themselves; the static tests are not a direct measurement of the long-term contribution.

## Conclusion space

- Virtuous: name the long-term-creep estimate for the underlying clay and the pile-test-extrapolation as the two assumptions controlling the conclusion.
- Excess: enumerate every geotechnical assumption.
- Deficiency: report long-term settlement using the static tests without flagging the load-bearing assumptions.

## Notes

RT-b deficiency: virtuous explicitly names the deep-clay creep and pile-test extrapolation; deficiency reaches a conclusion without surfacing them.
