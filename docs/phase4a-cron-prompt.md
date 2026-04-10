# Phase 4a Cron Prompt (recoverable copy)

**Purpose:** this file is the exact cron prompt for Phase 4a execution. If the in-session cron dies (power loss, Claude session exit, `CronDelete`), the user or a future Claude session can recreate the cron by passing the content of the fenced block below to `CronCreate` with cron expression `7,37 * * * *` (every 30 min at :07 and :37).

**Why this file exists:** in-session crons (`CronCreate`) are session-only and die with the session. The prompt is not written to disk by the cron tool itself, so without this file, recreating an exact duplicate after a crash is impossible. Session state (plan status, completed work) is preserved via `phase4a-plan.md` §8 and the `corpus/` directory, so resumption just requires recreating the cron with the exact same prompt — which is captured below.

**How to recover after a power loss:**

1. Verify: `CronList` shows no active Phase 4a cron.
2. Read this file.
3. Call `CronCreate` with `cron = "7,37 * * * *"` and `prompt =` the content of the fenced block below (everything between the opening and closing triple-backtick lines).
4. The next cycle will fire at the next :07 or :37 and will resume automatically from `phase4a-plan.md` §8 — the plan's status table tells the cron which stage is next, and the `corpus/` directory contents tell the cron which fact packs and triplets already exist.

No manual state reconstruction is needed — resumption is purely "recreate the cron, let it fire, the cycle detects its own position from files on disk."

---

## The cron prompt (copy everything between the fences)

```
Phase 4a cycle — Pilot corpus generation for Calibrated Confidence. 10 triplets target. 30-minute cadence. Autonomous work; do not ask for user input.

## Read these files at the start of every cycle

1. `/Users/sumit/Github/Phronesis/docs/phase4a-plan.md` — the execution plan, single source of truth for what Phase 4a is doing
2. `/Users/sumit/Github/Phronesis/docs/concepts.md` — for the Concept 9 Calibrated Confidence definition and sub-facets
3. `/Users/sumit/Github/Phronesis/docs/generation-guidelines.md` — especially §2.3 fact pack template, §2.4 sanitization checklist, §3.3-§3.5 domain rules, §4.6 generation prompts, §4.8 verification checks, §4.9 rejection handling
4. `/Users/sumit/Github/Phronesis/docs/review-rubric.md` — especially §3 scale anchors, §4.1 LLM-as-judge prompt template, §6.1 Calibrated Confidence rubric items, §8 edge cases
5. `/Users/sumit/Github/Phronesis/docs/findings.md` — especially F43, F44, F47, F59, F62, F65, F67, F68, F69, F71, F73 relevant to Phase 4a

Also list `/Users/sumit/Github/Phronesis/corpus/` to see current state (fact-packs/, triplets/, review-logs/, and pilot-summary.md if it exists).

## Determine current stage from phase4a-plan.md §8 status table

Then do exactly one of:

- **Stage 1 — Plan refinement:** if §8 shows Stage 1 IN PROGRESS, read the §7 open items and address one of them by updating the plan document. Mark Stage 1 COMPLETE when §7 is empty OR when two consecutive cycles produced no meaningful plan changes (check the last two cycle log entries in the plan document).

- **Stage 2 — Queue construction:** if §8 shows Stage 2 PENDING, construct the 10-slot queue per §3 Stage 2 of the plan, write it to `corpus/queue.md`, and mark Stage 2 COMPLETE.

- **Stage 3 — Fact pack curation:** if §8 shows Stage 3 IN PROGRESS or READY, curate exactly one fact pack for the next unfilled queue slot. Write it to `corpus/fact-packs/09-<domain>-<slug>-<nn>.md` following the §2.3 template exactly. Run §2.4 sanitization and mark sanitized: true. Log the curation in `corpus/review-logs/09-<slot-number>.log`. Do NOT do more than one fact pack per cycle. When all 10 are done, mark Stage 3 COMPLETE.

- **Stage 4 generation — Triplet generation:** if §8 shows Stage 4 generation unit is next, pick the next fact pack without a triplet directory. Create `corpus/triplets/<fact-pack-id>/` with neutral.md, virtuous.md, non-virtuous.md. Use the §4.6 prompts mentally (you ARE the generator model, Claude Opus 4.6, so produce the passages directly). Apply the failure-mode rotation and correctness-confound overrides from the queue. Do NOT also self-review in the same cycle — that happens next cycle.

- **Stage 4 review — Triplet self-review:** if the previous cycle generated a triplet, read the three passage files cold (do NOT re-read the fact pack with generator mindset; read the passages as a reviewer would). Apply the §6.1 Calibrated Confidence rubric following the §4.1 judge prompt structure. Score Layer 1 binary checks + Layer 2 Axis A and Axis B for virtuous and non-virtuous (and Axis B for neutral). Compare virtuous vs non-virtuous excess version to check F44 baseline-assertive-prior bleed-through. Write scores to the review log. If any score fails the pilot bar (≥4 on both axes for both rewrites, all Layer 1 passes), flag for Stage 5 regeneration.

- **Stage 5 — Regeneration:** if any triplets are flagged from Stage 4 review, regenerate the failing passage(s). Same one-unit rule: one regeneration attempt per cycle. Three-strikes rule: if a fact pack fails regeneration 3 times, mark it regeneration_failed and replace it with a new fact pack in the same slot.

- **Stage 6 — Corpus-level checks and finalization:** if §8 shows Stage 6 is next, pick one check (diversity metric, domain balance verification, rotation balance verification, pilot-summary.md section) and do it. Multiple cycles can run Stage 6 checks in parallel units.

- **Stage 7 — Buffer:** if all stages complete, log "Phase 4a pilot corpus complete" in findings.md with a link to corpus/pilot-summary.md, update §8 to show COMPLETE, and switch to idle saturation mode.

## Discipline rules

- **One focused unit per cycle.** Do not batch multiple units.
- **File-based cycle separation for self-verification (per plan §5):** when in generator role, do not read prior review logs for other triplets. When in reviewer role, do not re-read the generator's reasoning. Read only the final passage files from disk.
- **Golden-mean rotation is enforced by the queue, not by the generator.** Each slot's failure mode is assigned at queue time in the plan document; the generator must honor the assignment.
- **Correctness-confound overrides are applied at curator queue-construction time, not decided by the generator.** The queue assigns which triplets get virtuous-wrong or non-virtuous-right overrides; the generator honors them.
- **Acceptance criteria (plan §2) are the bar.** Do not relax autonomously. If criteria cannot be met, log at-risk status and continue attempting.
- **Do NOT edit concepts.md, project.md, references.md, generation-guidelines.md, or review-rubric.md** unless a specific Phase 4a finding requires a small clarifying edit. These are frozen inputs for this phase.
- **Log every cycle's work** in the plan document's §8 status table: which cycle number, what unit was done, what the next cycle should do.

## Reporting

Close each cycle with a short session summary (under 150 words): current stage, what unit was executed, how many more cycles that stage likely needs, any flags for the user. If you edited phase4a-plan.md, concepts.md, or any other doc besides corpus files, list each edit in one line.
```

---

## Cron expression reference

`7,37 * * * *` — every 30 minutes, at :07 and :37 past each hour. Off-minutes chosen to avoid the :00 and :30 load spikes per CronCreate documentation.
