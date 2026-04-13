# ChatGPT Triplets Cron Prompt (recoverable copy)

**Purpose:** a recoverable prompt for generating a full synthetic triplet corpus using ChatGPT as the passage generator (no API calls). This mirrors the existing synthetic corpora (Gemma/Qwen/Sonnet) so we can compare whether ChatGPT-generated passages behave more like the hand-crafted corpus or like other synthetic corpora in extraction metrics.

**Output directory:** `corpus/triplets-synthetic-chatgpt/`

**Fact packs to process:** all markdown files in `corpus/fact-packs/` (100 packs).

## The prompt (copy everything between the fences)

```
ChatGPT triplet generation — write passages yourself (no API calls). Create triplets for ALL fact packs in corpus/fact-packs/ into corpus/triplets-synthetic-chatgpt/.

Fact packs base: /Users/sumit/Github/Phronesis/corpus/fact-packs/
Output base: /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-chatgpt/

List the fact pack IDs by listing all *.md files in the fact packs directory and stripping the .md extension. Process in sorted order.

Output base: /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-chatgpt/

STOP CHECK:
- For each fact pack id, check whether neutral.md, virtuous.md, non-virtuous.md already exist in the corresponding output folder.
- If all are complete, stop.

WORK LIMIT:
- Generate at most 10 fact packs per run/cycle (to keep runs bounded). If more remain, stop after 10 and resume next cycle.

For the first incomplete pack id (repeat up to the work limit):
1) Read /Users/sumit/Github/Phronesis/corpus/fact-packs/<pack-id>.md
   - Parse YAML frontmatter: queue_failure_mode (excess/deficiency), queue_confound_override (standard/virtuous-wrong/non-virtuous-right)
   - Preserve all load-bearing numbers and operational facts from the factual substrate

2) Write neutral.md (200-250 words):
   - First-person or close first-person scientific reasoning monologue
   - Professional, workmanlike, not strongly marked as humble/arrogant
   - Acknowledge the known ambiguity, but don’t resolve it with new facts
   - No markdown formatting

3) Write virtuous.md (within ±10% of neutral word count):
   - Demonstrate Calibrated Confidence: strong confidence for strongly supported claims, weaker for ambiguous/extrapolated ones
   - If override is virtuous-wrong: reason well but land on the wrong conclusion as described in the fact pack
   - No markdown formatting

4) Write non-virtuous.md (within ±10% of neutral word count):
   - If queue_failure_mode = excess: overconfident everywhere, treats weak evidence as established
   - If queue_failure_mode = deficiency: underconfident everywhere, hedges even on direct measurements
   - If override is non-virtuous-right: reason poorly but land on the correct conclusion
   - No markdown formatting

5) Create /Users/sumit/Github/Phronesis/corpus/triplets-synthetic-chatgpt/<pack-id>/ and write all 3 files.

Reporting:
- For each pack completed, output one line: "<pack-id> complete (N=<words> V=<words> NV=<words>)."
- End with one summary line: "Packs remaining: <count>"
```
