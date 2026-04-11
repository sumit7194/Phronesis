# Phase 4a Cron Prompt (recoverable copy)

**Purpose:** this file is the exact cron prompt for Phase 4a extended corpus generation (slots 11-50). If the in-session cron dies (power loss, Claude session exit, `CronDelete`), recreate it with `CronCreate` using cron expression `*/10 * * * *` (every 10 minutes) and the prompt in the fenced block below. The cron self-terminates when all 40 extended slots reach ACCEPTED status by writing `corpus/CORPUS_COMPLETE.md` and calling CronDelete on itself.

**Why this file exists:** in-session crons (`CronCreate`) are session-only and die with the session. The prompt is not written to disk by the cron tool itself, so without this file, recreating an exact duplicate after a crash is impossible. Session state is preserved in `corpus/queue-extended.md` (slot statuses) and the `corpus/` directory, so resumption just requires recreating the cron — it detects its own position from files on disk.

**How to recover after a power loss:**

1. Verify: `CronList` shows no active cron.
2. Read this file.
3. Call `CronCreate` with `cron = "*/10 * * * *"` and `prompt =` the content of the fenced block below.
4. The next cycle will fire within 10 minutes and resume from wherever queue-extended.md left off.

No manual state reconstruction needed.

---

## The cron prompt (copy everything between the fences)

```
Phase 4a extended corpus generation — scaling from 10 to 50 triplets for Calibrated Confidence. 10-minute cadence, 2 units per cycle. Autonomous work; do not ask for user input.

## STOP CHECK — run this first, every cycle

Read `/Users/sumit/Github/Phronesis/corpus/queue-extended.md`. Count how many of the 40 slots (11-50) have status ACCEPTED. If all 40 are ACCEPTED:
1. Write the file `/Users/sumit/Github/Phronesis/corpus/CORPUS_COMPLETE.md` with content: "# Corpus Complete\n\nAll 50 triplets (slots 1-50) accepted. Phase 4a extended corpus generation finished. Ready for Phase 4b extraction run.\n\nCompleted: <current date>"
2. Call CronDelete with job ID matching this cron to cancel it.
3. Stop — do not proceed with the rest of this prompt.

If not all 40 are ACCEPTED, continue below.

## Read these files at the start of every cycle

1. `/Users/sumit/Github/Phronesis/corpus/queue-extended.md` — the 40-slot extended queue (slots 11-50), single source of truth for slot assignments
2. `/Users/sumit/Github/Phronesis/docs/concepts.md` — for Concept 9 Calibrated Confidence definition and sub-facets
3. `/Users/sumit/Github/Phronesis/docs/generation-guidelines.md` — especially §2.3 fact pack template, §2.4 sanitization checklist, §3.3-§3.5 domain rules, §4.6 generation prompts, §4.8 verification checks, §4.9 rejection handling
4. `/Users/sumit/Github/Phronesis/docs/review-rubric.md` — especially §3 scale anchors, §4.1 LLM-as-judge prompt template, §6.1 Calibrated Confidence rubric items, §8 edge cases
5. `/Users/sumit/Github/Phronesis/docs/findings.md` — especially F43, F44, F47, F59, F62, F65, F67, F68, F69, F71, F73

Also list `/Users/sumit/Github/Phronesis/corpus/triplets/` and `/Users/sumit/Github/Phronesis/corpus/fact-packs/` to see current state.

## Determine next slot

Look at `queue-extended.md`. Find the first slot with status PENDING or FACT_PACK_DONE or TRIPLET_GENERATED. That is the next slot to process.

## Each cycle: do 2 units of work

A "unit" is one of:
- **Fact pack curation**: create a fact pack for the next PENDING slot. Write to `corpus/fact-packs/09-<domain>-<slug>-01.md` following §2.3 template. Run §2.4 sanitization. Update queue-extended.md status to FACT_PACK_DONE.
- **Triplet generation**: for a slot that has FACT_PACK_DONE, generate neutral.md, virtuous.md, non-virtuous.md in `corpus/triplets/09-<domain>-<slug>-01/`. Use §4.6 prompts. Honor the failure mode and override from the queue. Update status to TRIPLET_GENERATED.
- **Self-review**: for a slot with TRIPLET_GENERATED, read the passages cold and apply §6.1 rubric. Score Layer 1 + Layer 2. If ≥4 on both axes → update status to ACCEPTED. If not → flag for regeneration.

Preferred pairing per cycle: curate fact pack for slot N, then generate triplet for slot N-1 (if N-1 has FACT_PACK_DONE). This pipelines the work. If no prior slot needs generation, do 2 fact packs. If no slots need fact packs, do 2 triplet generations or reviews.

## Override handling

For slots with `virtuous-wrong` override: the virtuous passage reaches a factually incorrect conclusion despite careful reasoning. The non-virtuous passage uses the assigned failure mode.

For slots with `non-virtuous-right` override: the non-virtuous passage reaches the correct conclusion despite poor reasoning (lucky guess through overconfidence or under-engagement).

For `standard` slots: virtuous reaches correct conclusion through good reasoning, non-virtuous reaches incorrect or muddled conclusion through the assigned failure mode.

## Quality standards

- Passages must be 180-280 words each
- Virtuous and non-virtuous within ±10% word count of neutral
- All three passages use the same factual substrate from the fact pack
- Failure mode (excess or deficiency) must match queue assignment
- Sub-facet targeting: each triplet should hit a specific sub-facet of Calibrated Confidence (see concepts.md)
- Vary sub-facets across the corpus — track which sub-facets have been used

## Discipline rules

- **Two units per cycle max.** Do not batch more.
- **File-based cycle separation:** when generating, do not read review logs. When reviewing, do not re-read generator reasoning.
- **Golden-mean rotation is enforced by the queue.** Honor the failure mode assignment.
- **Do NOT edit concepts.md, project.md, references.md, generation-guidelines.md, or review-rubric.md.**
- **Update queue-extended.md** after each unit to track progress.

## Reporting

Close each cycle with a short summary (under 100 words): which slots were processed, what units were done, how many slots remain PENDING/in-progress, any quality flags.
```

---

## Cron expression reference

`*/10 * * * *` — every 10 minutes. Self-terminates when all 40 extended slots (11-50) reach ACCEPTED status.
