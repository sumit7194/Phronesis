# Sonnet Triplets Cron Prompt (recoverable copy)

**Purpose:** this file is the exact cron prompt for generating triplets for the 10 biology/chemistry fact packs using Claude Sonnet as the generator (no API calls). If the in-session cron dies, recreate it with `CronCreate` using cron expression `*/2 * * * *` (every 2 minutes) and the prompt in the fenced block below. The cron self-terminates when all 10 triplets reach completion.

**Output directory:** `corpus/triplets-synthetic-sonnet/`

**Fact packs to process:**
1. 09-biology-camera-trap-occupancy-detection-01
2. 09-biology-coral-bleaching-thermal-threshold-01
3. 09-biology-crispr-knockout-phenotype-redundancy-01
4. 09-biology-edna-species-detection-absence-01
5. 09-biology-microbiome-transplant-causation-01
6. 09-biology-rnaseq-differential-expression-batch-01
7. 09-biology-telomere-aging-causation-01
8. 09-chemistry-catalytic-turnover-stability-01
9. 09-chemistry-chiral-hplc-ee-determination-01
10. 09-chemistry-crystallography-disorder-refinement-01

**How to recover after session loss:**
1. `CronList` to confirm no active cron exists.
2. Read this file.
3. Call `CronCreate` with `cron = "*/2 * * * *"` and `prompt =` the content of the fenced block below.
4. The next cycle fires within 2 minutes and resumes from wherever it left off.

---

## The cron prompt (copy everything between the fences)

```
Sonnet triplet generation — 10 fact packs for corpus/triplets-synthetic-sonnet/. 2-minute cadence, 1 fact pack per cycle. You ARE the generator; write passages yourself, no API calls.

## STOP CHECK — run this first, every cycle

Check whether all 10 output triplet directories contain neutral.md, virtuous.md, and non-virtuous.md:

Fact packs (in /Users/sumit/Github/Phronesis/corpus/fact-packs/):
- 09-biology-camera-trap-occupancy-detection-01
- 09-biology-coral-bleaching-thermal-threshold-01
- 09-biology-crispr-knockout-phenotype-redundancy-01
- 09-biology-edna-species-detection-absence-01
- 09-biology-microbiome-transplant-causation-01
- 09-biology-rnaseq-differential-expression-batch-01
- 09-biology-telomere-aging-causation-01
- 09-chemistry-catalytic-turnover-stability-01
- 09-chemistry-chiral-hplc-ee-determination-01
- 09-chemistry-crystallography-disorder-refinement-01

Output base: /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-sonnet/

For each pack ID, check if /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-sonnet/<pack-id>/neutral.md exists. Use Glob to check.

If ALL 10 packs have all 3 files present:
1. Call CronDelete with this cron's job ID to cancel it.
2. Output: "All 10 triplets complete. Cron self-terminated."
3. Stop — do not proceed.

If not all complete, continue below.

## Find the next pack to process

Find the first pack ID in the list above whose output directory does NOT yet contain all 3 files (neutral.md, virtuous.md, non-virtuous.md). That is the pack to process this cycle. Skip packs that are already complete.

## Process one fact pack

1. Read /Users/sumit/Github/Phronesis/corpus/fact-packs/<pack-id>.md
   - Parse frontmatter YAML: note queue_failure_mode (excess or deficiency) and queue_confound_override
   - Parse sections: Scenario title, Factual substrate, Known ambiguity, Generator notes

2. Read /Users/sumit/Github/Phronesis/mvp/generate_corpus_gemini.py for the prompt logic (build_neutral_prompt, build_virtuous_prompt, build_non_virtuous_prompt) to understand what each passage type should demonstrate.

3. Write neutral.md (200-250 words):
   - Professional, workmanlike reasoning monologue
   - No markdown formatting (no bold, italics, asterisks)
   - Acknowledges ambiguity without dwelling on it
   - No strong epistemic markers (no "I wonder", no "obviously", no "clearly establishes")
   - Preserves all specific numbers from factual substrate

4. Write virtuous.md (within ±10% of neutral word count):
   - Exhibits Calibrated Confidence: differentiates confidence levels based on evidence strength
   - Uses "well-established" for strong evidence, "plausible but not established" for weak
   - Engages explicitly with the known ambiguity and what it does/doesn't undermine
   - If queue_confound_override = "virtuous-wrong": good reasoning, but reaches an incorrect conclusion
   - No markdown formatting

5. Write non-virtuous.md (within ±10% of neutral word count):
   - If failure_mode = excess: overconfident, treats all claims as strongly supported, dismisses ambiguity
   - If failure_mode = deficiency: under-confident, hedges on everything including well-supported claims
   - If queue_confound_override = "non-virtuous-right": bad reasoning process but accidentally correct conclusion
   - No markdown formatting

6. Create directory /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-sonnet/<pack-id>/ and write all 3 files.

## Word count discipline

After writing, estimate word counts. If virtuous or non-virtuous is >10% longer or shorter than neutral, trim or expand before writing.

## Reporting

Close the cycle with one line: "<pack-id> complete (N=<words> V=<words> NV=<words>). Packs remaining: <count>"
```

---

## Cron expression reference

`*/2 * * * *` — every 2 minutes. Self-terminates when all 10 output triplets are complete.
