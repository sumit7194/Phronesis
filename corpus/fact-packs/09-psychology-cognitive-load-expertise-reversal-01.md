---
fact_pack_id: 09-psychology-cognitive-load-expertise-reversal-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: conditional moderator interaction in cognitive load theory
domain: Psychology (educational psychology / cognitive psychology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

An experiment showing that eliminating redundant text from worked examples improves learning in novices, with a virtuous-wrong analysis that misses the expertise reversal effect for advanced students

## Factual substrate

- A classroom experiment tested worked examples in statistics: one condition presented solutions with full explanatory text (complete condition), one presented solutions with text reduced to remove information deducible from the diagrams (reduced-redundancy condition)
- Participants: 48 undergraduate introductory statistics students (novices); the reduced-redundancy condition showed significantly higher post-test scores (d = 0.68, p < 0.001)
- The study was designed based on cognitive load theory (CLT): redundant information creates extraneous cognitive load; eliminating it frees working memory for learning (the "redundancy effect")
- Results replicate published CLT findings for novices
- A separate class of 24 advanced students (PhD-level statistics) was tested with the same materials as an exploratory condition; the advanced students performed better in the complete condition (d = −0.52, p = 0.02); this is the expertise reversal effect — for experts, the previously redundant information provides useful scaffolding for elaborative processing
- The virtuous-wrong passage correctly reasons that CLT predicts redundancy elimination should help novices (correct), applies appropriate caution about generalizing beyond the novice population (virtuous), but still fails to predict that the opposite effect will occur for advanced students — recommending the reduced-redundancy format for all courses. This turns out to be wrong for the advanced cohort.

## Known ambiguity

- The novice finding is well-replicated and the CLT mechanism is clear for the low-prior-knowledge group
- The expertise reversal effect is also a well-established finding in CLT, but the virtuous passage correctly notes the novice data cannot directly inform advanced student design — it just fails to predict the reversal
- Virtuous-wrong: the passage correctly limits its claims to the novice population, correctly notes that CLT predicts different effects by expertise level, but concludes that reduced-redundancy format "should be recommended wherever novice populations are present" — which turns out to apply to a course that has both novice and advanced students in the same classroom

## Generator notes (failure mode for slot 44 — virtuous-wrong override)

This is a **virtuous-wrong** override with **excess** failure mode. The non-virtuous passage should treat the novice d = 0.68 effect as justifying the reduced-redundancy format for all students in all courses, ignoring the expertise moderator entirely — classic excess, wrong in the same direction as the virtuous passage but for a worse reason. The virtuous passage should correctly invoke CLT, acknowledge the expertise reversal effect as a known moderator, limit strong recommendations to novice populations, and note that mixed-expertise classrooms require separate material design — but still over-applies the recommendation to "courses where students are primarily novices" without noticing that the specific course in question has an advanced section that would be harmed. The virtuous passage is more careful than the non-virtuous passage but still reaches the wrong application.
