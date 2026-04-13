# Sonnet Triplets — Remaining Fact Packs Cron Prompt (recoverable copy)

**Purpose:** Cron prompt for generating triplets for all remaining fact packs (those not yet in corpus/triplets-synthetic-sonnet/). Runs every 2 minutes, processes 2 fact packs per cycle. Self-terminates when no unprocessed packs remain.

**Output directory:** `corpus/triplets-synthetic-sonnet/`

**How to recover after session loss:**
1. `CronList` to confirm no active cron.
2. Read this file.
3. Call `CronCreate` with `cron = "*/2 * * * *"` and `prompt =` the content of the fenced block below.
4. Next cycle fires within 2 minutes and resumes from wherever it left off.

---

## The cron prompt (copy everything between the fences)

```
Sonnet triplet generation — remaining fact packs. 2-minute cadence, 2 fact packs per cycle. You ARE the generator; write passages yourself, no API calls. Autonomous; do not ask for user input.

## Every cycle — do this in order

### Step 1: Determine what remains

Use Glob to list all fact pack IDs:
  pattern: "corpus/fact-packs/09-*.md" in /Users/sumit/Github/Phronesis

Use Glob to list all completed triplet directories:
  pattern: "corpus/triplets-synthetic-sonnet/09-*/neutral.md" in /Users/sumit/Github/Phronesis

Compute the set of fact pack IDs (strip path and .md extension) that do NOT yet have a neutral.md in triplets-synthetic-sonnet/. Sort alphabetically. These are the remaining packs.

### Step 2: Stop check

If zero packs remain:
1. Call CronDelete with this cron's job ID.
2. Output: "All fact packs complete. Cron self-terminated."
3. Stop.

### Step 3: Pick next 2 packs

Take the first 2 IDs from the remaining (alphabetically sorted) list.

### Step 4: For each of the 2 packs, generate a triplet

For each pack_id:

a) Read /Users/sumit/Github/Phronesis/corpus/fact-packs/<pack_id>.md
   Parse the frontmatter YAML. Key fields:
   - queue_failure_mode: "excess" or "deficiency"
   - queue_confound_override: "standard", "virtuous-wrong", or "non-virtuous-right"
   Parse the body sections (split on "## " headings):
   - Scenario title
   - Factual substrate (all bullet points with specific numbers)
   - Known ambiguity
   - Generator notes (may appear under various heading names)

b) Generate neutral.md (target 200-250 words):
   Write a researcher's reasoning monologue — professional, workmanlike, adequate.
   - Include all specific numbers and measurements from the factual substrate
   - Acknowledge the known ambiguity without dwelling on it
   - Reach a plausible conclusion from the scenario
   - No strong epistemic markers: no "I wonder", "obviously", "clearly establishes", "certainly", "I am certain"
   - No markdown formatting: no bold, no italics, no asterisks, no headers
   - Plain prose paragraphs only

c) Generate virtuous.md (within ±10% of neutral word count):
   Rewrite neutral so the reasoner exhibits Calibrated Confidence:
   - DIFFERENTIATES confidence levels: uses confident language for well-supported claims ("well-established", "robust", "clearly shown"), tentative language for weak/ambiguous claims ("plausible but not established", "consistent with but not proven by", "warrants follow-up")
   - Engages substantively with the known ambiguity — explains what it does and doesn't undermine
   - Preserves all specific numbers from neutral
   - Preserves the structural shape (same inferential steps, same order)
   - If queue_confound_override = "virtuous-wrong": the reasoning is careful and well-differentiated BUT the final conclusion is factually incorrect (good process, wrong answer)
   - No markdown formatting

d) Generate non-virtuous.md (within ±10% of neutral word count):
   Rewrite neutral so the reasoner exhibits a failure mode of Calibrated Confidence:
   - If queue_failure_mode = "excess" (OVERCONFIDENCE): applies strong decisive language to ALL claims, even weak ones. Dismisses uncertainty. Uses "confirms", "definitively shows", "clearly establishes" even for equivocal results. Treats all evidence as equally strong.
   - If queue_failure_mode = "deficiency" (UNDER-CONFIDENCE): hedges on EVERYTHING, even well-supported findings. Refuses to commit even when evidence is strong. Uses "it's hard to say", "we can't be sure", "more data needed" even for robust results. Treats all evidence as equally uncertain.
   - If queue_confound_override = "non-virtuous-right": poor reasoning process but accidentally reaches the correct conclusion
   - Preserves all specific numbers from neutral
   - No markdown formatting

e) Word count check: estimate word counts for virtuous and non-virtuous. If either is outside ±10% of neutral's word count, trim or expand before writing.

f) Write files:
   - Create directory: /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-sonnet/<pack_id>/
   - Write neutral.md, virtuous.md, non-virtuous.md (plain text, no frontmatter)

### Step 5: Log this cycle

Output a brief summary (under 80 words):
- Which 2 packs were processed
- Word counts: N=X V=Y NV=Z for each
- How many packs remain unprocessed
- Any quality flags (e.g. if a word count was borderline)
```

---

## Cron expression

`*/2 * * * *` — every 2 minutes. Self-terminates when all fact packs are complete.
