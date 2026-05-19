# Terminology audit — Day 31 consolidation

**Date**: 2026-05-13
**Status**: Awaiting author approval before replacements are applied.
**Scope**: All `docs/*.md` (excluding `docs/archive/`, `docs/feature-catalog.md` which is read-only per consolidation prompt, and `docs/_consolidation-scratch-discrepancies.md` which is a scratch file).

## Why this audit exists

Existing documentation systematically uses "hand-reviewed", "hand-judged", "manually reviewed", "by hand", "human review", etc. to describe two activities that are not the same:

- **Author work** — Sumit personally reading corpus samples on Days 1-3, validating generation methodology, making strategic decisions, spot-checking sampled generations, reviewing synthesis docs.
- **Opus-as-judge work** — Claude Opus 4.6/4.7 sessions reading every generation in full and assigning a verdict (✓ / ~ / ✗). The 2,914-generation total across MVP + SAE rounds was bulk-judged by Opus, not human-reviewed.

The intended outcome of this audit is to keep author-work mentions accurate and disambiguate Opus-as-judge mentions with one of: **Opus-judged**, **Opus-reviewed**, **LLM-as-judge**, or **reviewed by Claude Opus 4.6/4.7**.

## Categories used in this audit

- **A** — Actual human review by the project author. Stays accurate, possibly with light clarification.
- **B** — Opus session reading and verdict-assigning generations. **Needs replacement.**
- **C** — Rubric / methodology language describing the intended review process (often in scoring.md, eg-rt-eval-spec.md, extraction-runbook.md, review-rubric.md, generation-guidelines.md). Usually `keep`.
- **D** — Ambiguous. Flagged for author judgment.

## Top-level totals

| Category | Count | Action |
|---|---:|---|
| A — author work | ~22 | Keep, optional clarification |
| **B — Opus-as-judge** | **~164** | **Replace per "Proposed replacement" column** |
| C — rubric/methodology | ~81 | Keep |
| D — ambiguous | **0** | All 7 resolved against source docs (see "D-resolutions" section below) |
| **Total** | **~267** | |

## D-resolutions (resolved 2026-05-13 against journal narrative + scoring.md + post-mvp-decisions.md)

The 7 D-flagged occurrences were resolved by reading source context. No remaining ambiguity.

| File:Line | Original | Resolution | Final action |
|---|---|---|---|
| journal.md:452 | "Manual rescoring of Gemma baseline: 17/24, not 22/24" | **A** — Day-15 author fact-check against Nobel Foundation site after auto-scorer credited Gemma's confabulated "1931 Gandhi Nobel"; established the manual-first policy. | keep |
| journal.md:452 | "Qwen-vs-Gemma gap shrank from +4pp auto to +1pp human" | **A** — same Day-15 author rescore | keep (optionally: "+1pp author-verified") |
| journal.md:495 | "Will hand-score when it lands" | **A** — Day-15 forward-looking note re Gemma α=8 24-item benchmark, manual-first policy just established | keep (or "Will hand-score (author) when it lands") |
| journal.md:979 | "v2 scorers manually calibrated against hand-rubric, not pre-registered" | **A+B split** — author wrote/tuned the regex code; the calibration anchors were the F103 Opus-judged verdicts | "v2 scorers calibrated by the author against the F103 Opus-judged rubric, not pre-registered" |
| journal.md:1237 | "8 cells I'd already done by hand at the start" | **B** — Day-24 journal entry is written in Claude-session voice ("the user pointed out…" at L1231 → "user" = Sumit, "I" = Claude). The 8 cells were one-at-a-time Opus session reading before pivot to sub-agent parallelism. | "8 cells the Opus session had already done one-at-a-time before the parallelism pivot" |
| post-mvp-decisions.md:68 | "note that manual review confirmed the auto-scorer results" | **C** — conditional language inside the 3.A. "all_clean" branch protocol; that branch never executed (MVP didn't reach the 4×4 specificity matrix). Rubric-style placeholder. | keep |
| post-mvp-decisions.md:328 | "If anyone else hand-reviews the same 690 generations…" | **C** — hypothetical future reviewer, intentionally generic. | keep |

## Patterns worth surfacing

1. **Numeric tell for B**: generation counts of 121, 136, 168, 200+, 690, 1,110, 1,162, 1,752, 2,443, 2,467, 2,914 are all Opus-judged scale corpora. Any "X-generation hand-review" with X ≥ ~100 is almost always Category B.
2. **F-finding signatures map cleanly to B**: any phrase referring to F94-UPDATE / F103 / F104 / F108 / F109 / F110 / F111 / F112 / F115-F119 / F120 review revisions describes Opus-judged review.
3. **`sae_round_report.md` is uniformly B** (22/22). It is essentially the cumulative-N summary doc; every "hand-judged" is a dataset-size attribution.
4. **Spec/rubric/runbook files are mostly C**: `eg-rt-eval-spec.md`, `extraction-runbook.md`, `phase5-plan.md`, `review-rubric.md`, `references.md`, plus much of `scoring.md` — these describe the intended-review *rubric*, not who did the bulk work.
5. **Generation-side files are mostly A**: `generation-guidelines.md`, `mvp-virtues.md` correctly describe author-as-curator (hand-crafted corpus, manual triplet review). Stays.
6. **Highest-leverage single fix**: `post-mvp-decisions.md` L556 has a paper-title sketch *"A 2,443-Generation Hand-Reviewed Cross-Family Study"*. If this title ships uncorrected it propagates the methodology mislabel publicly. Strongly recommend "Opus-judged" or "LLM-as-judge" framing.

## D-resolutions (see table above)

All D-flagged items resolved against journal narrative. Two corrections to the per-file tables below: `journal.md:1237` reclassified from A → B; `journal.md:452/495` confirmed A.

---

## File-by-file audit

### findings.md (58 occurrences) — 7 A · 47 B · 14 C · 0 D

| Line | Original snippet (≤80 chars) | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 75 | "...before committing to 450 hand-reviewed triplets." | C | keep | Methodological/budget framing about intended Phase-2 triplet review |
| 429 | "...refinement (proposed, awaiting human review)." | A | keep | Author go/no-go on concepts.md refinement |
| 455 | same | A | keep | same |
| 489 | same | A | keep | same |
| 509 | same | A | keep | same |
| 683 | "...resource-impact change that needs human review..." | A | keep | Author go/no-go on budget change |
| 697 | "My recommendation (for human review): Option 2..." | A | keep | Author decision item |
| 701 | "...update needed pending human review." | A | keep | Author decision item |
| 1663 | "...the LLM-judge and the human reviewer disagree..." | C | keep | Rubric-design methodology |
| 1704 | "...external verification step (different model or human reviewer)..." | C | keep | Rubric/methodology proposal |
| 2537 | "Manual review shows steered did additional..." | B | "Opus-reviewed reading shows..." | Per-cell verdict |
| 2922 | "100% manual hand-review of all 960 generations..." | B | "100% Opus-judged review of all 960 generations" | MVP-battery verdict assignment |
| 3101 | "Hand-review will catch them as planned per scoring.md." | C | keep | Methodology policy |
| 3397 | "## F103 ... — Hand-review verdict on the α-sweep..." | B | "Opus-judged verdict on the α-sweep..." | F103 = "separate Claude session" reading 690 generations |
| 3399 | "Independent hand-review of all 690 α-sweep generations..." | B | "Independent Opus review of all 690 α-sweep generations" | Self-described as separate Claude session |
| 3401 | "...this is exactly why we committed to hand-review..." | C | keep | Manual-first policy statement |
| 3410 | "...score lower than baseline by hand-rubric" | B | "by Opus-rubric reading" | Per-item Opus verdict |
| 3456 | "...the corrected picks based on hand-review:" | B | "based on Opus review" | 690-gen Opus reading |
| 3468 | "The hand-review surfaced two new auto-scorer failure modes:" | B | "The Opus review surfaced..." | Same session |
| 3471 | "...while hand-review gave RT=3..." | B | "while Opus review gave RT=3" | Per-item Opus verdict |
| 3477 | "Hand-review Priority 5 finding: CC steering also produces..." | B | "Opus-review Priority 5 finding" | Same session |
| 3494 | "...auto-scorer 'win' that hand-review revealed to be hallucinated..." | B | "...that Opus review revealed..." | F94-UPDATE + Day 19 Opus reviews |
| 3494 | "Day 19 hand-review reproduces the pattern at larger scale." | B | "Day 19 Opus review reproduces..." | Same |
| 3507 | "Hand-review is single-rater (one Claude session)." | B | "Opus review is single-rater (one Claude session)" | Explicit Claude-session ID |
| 3514 | "Policy of manual-first hand-review justified by both events." | C | keep | Policy label |
| 3518 | "Partial-branch handling needs to incorporate hand-review verdict..." | B | "...Opus-review verdict" | F103 verdict |
| 3530 | "## F104 ... — Full hand-review of 200+ items REVERSES..." | B | "Full Opus review of 200+ items" | Bulk verdict assignment |
| 3534 | "...hand-reviewed every generation..." | B | "...Opus-reviewed every generation" | Bulk per-generation review |
| 3539 | "Total: ~200 hand-reviewed items." | B | "~200 Opus-reviewed items" | Bulk verdicts |
| 3541 | "### What the hand-review changed about prior verdicts" | B | "What the Opus review changed..." | F104 review |
| 3547 | "Day 20 hand-review reading: v_IH × L17..." | B | "Day 20 Opus-review reading" | Per-generation Opus verdicts |
| 3597 | "Without hand review, every claim from this project is unreliable." | C | keep (or "LLM-as-judge review") | Methodological category — "not auto-scorer" is the point |
| 3597 | "...IH-v2 / EG-v2 scorers manually calibrated against hand-rubric." | B | "calibrated against Opus-rubric" | Calibration anchors |
| 3602 | "...calibrated post-hoc against hand-review (not pre-registered)." | B | "calibrated post-hoc against Opus review" | Same |
| 3609 | "...synthesis across all hand reviews" | B | "across all Opus reviews" | Artifact summary |
| 3610 | "...v2 scorers calibrated to hand-rubric" | B | "calibrated to Opus-rubric" | Calibration anchor |
| 3619 | "Day 21 diagnostic batch on the v1 vectors (full hand review, 136 items)" | B | "full Opus review, 136 items" | Bulk per-item verdict |
| 3660 | "...hand-rate detailed behaviour on FM-8-not-prone prompts." | C | keep | Future methodology proposal |
| 3679 | "...add cc-simple as a new manual-rated benchmark (8 prompts, no auto-scorer, hand-rated for FM-8 vs commit)." | C | keep | Benchmark-registration policy |
| 3684 | "full 136-item Day 21 hand review" | B | "full 136-item Day 21 Opus review" | Bulk verdict artifact |
| 3765 | "Hand-review of the first 20 fresh v2 generations..." | B | "Opus review of the first 20 fresh v2 generations" | Per-generation Opus |
| 3856 | "## F108 ... — v2 sweep hand-review (168 generations)..." | B | "v2 sweep Opus review (168 generations)" | Bulk per-generation verdicts |
| 3964 | "## F109 ... — Round 3 sweep (121 generations, hand-reviewed)..." | B | "121 generations, Opus-reviewed" | Bulk per-generation verdicts |
| 3975 | "Every generation hand-reviewed (no auto-scorer used)." | B | "Every generation Opus-reviewed" | Per-generation Opus verdicts |
| 4098 | "## F110 ... — Cross-model 1,752-generation hand-review confirms..." | B | "1,752-generation Opus review" | Bulk verdict assignment |
| 4102 | "...full hand-review of phi-4-mini-reasoning + llama..." | B | "full Opus review of phi-4..." | Bulk per-generation reading |
| 4106 | "### Per-model column totals (✓ rate, hand-graded)" | B | "(✓ rate, Opus-judged)" | Per-cell verdict tally |
| 4149 | "Hand-review remains essential — auto-scorer would have credited..." | C | keep | Methodology claim about review policy |
| 4161 | "...1,752 verdicts (all hand-graded)" | B | "1,752 verdicts (all Opus-judged)" | Bulk counts |
| 4426 | "Verdict from full hand-review of 1,110 generations..." | B | "Verdict from full Opus review of 1,110 generations" | SAE-battery bulk verdicts |
| 4455 | "The hand-review battery covered 4 other models on the same E1 prompt." | B | "The Opus-review battery covered..." | SAE-battery |
| 4476 | "...per_generation.csv — every row hand-judged with verdict/FM-tag/note" | B | "every row Opus-judged" | Per-row verdict assignment |
| 4477 | "...preliminary headline findings (now superseded by this finding's hand-review version)" | B | "Opus-review version" | Same dataset, Opus pass |
| 4478 | "06_hand_review_findings.md — full hand-review writeup" | B | filename: KEEP; description: "Opus-review writeup" | Literal filename — don't rename |
| 4487 | "Verdict from hand-review: amplifying 15372 at α≥0.3 breaks..." | B | "Verdict from Opus review" | Per-cell verdict |
| 4516 | "Verdict from hand-review of all 267 E2 generations..." | B | "Verdict from Opus review of all 267 E2 generations" | Bulk per-generation verdicts |
| 4584 | "Hand-review for FM-fake-sourcing should include checking..." | C | keep | Methodology guidance for future rubric |
| 4596 | "Three methodological lessons emerged from the 1,110-generation hand-review." | B | "1,110-generation Opus review" | F115 SAE battery review |
| 4614 | "`qwen3-4b/1A_random_negctrl` ... Hand-review:" | B | "Opus review:" | Per-cell Opus reading |
| 4631 | "Recommendation: hand-review of any high-α SAE-steering result..." | C | keep | Methodology recommendation |
| 4656 | "### Verdict distribution (hand-judged, same rubric as F115-F119)" | B | "(Opus-judged, same rubric as F115-F119)" | Per-generation verdict tally |
| 4715 | "...2,914+ hand-judged generations across two studies." | B | "2,914+ Opus-judged generations" | Headline N |
| 4725 | "...classifier built on the 2,914 hand-judged generations." | B | "2,914 Opus-judged generations" | Same dataset |
| 4728 | "N=2,914 hand-judged generations across 5 models..." | B | "N=2,914 Opus-judged generations" | Paper-draft framing |
| 4733 | "...per_generation.csv — 104 rows (52 baseline + 52 steered) hand-judged" | B | "104 rows ... Opus-judged" | Per-row verdicts |

---

### journal.md (53 occurrences) — 5 A · 40 B · 8 C · 0 D (post-D-resolution)

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 149 | "### Key qualitative findings from manual review" | B | "from Opus-reviewed generations" | Day-15 benchmark probe; Opus-judged |
| 452 | "...all benchmark claims must be manually verified..." | A | keep | Policy block — author calling Nobel Foundation site is real human work |
| 452 | "Manual rescoring of Gemma baseline: 17/24, not 22/24..." | D | **needs your call** | Day-15 rescore against external ground truth |
| 452 | "+4pp auto to +1pp human." | D | **needs your call** | "human" conflates A/B |
| 473 | "Everything manual at MVP...every response hand-reviewed." | B | "every response Opus-reviewed" | MVP policy at scale = Opus |
| 473 | "...new triplets for EG and RT written by hand." | A | keep | Corpus authoring |
| 488 | "...every response hand-reviewed..." | B | "every response Opus-reviewed" | Same MVP policy |
| 495 | "Will hand-score when it lands." | D | **needs your call** | Day-15 plan |
| 549 | "Non-virtuous excess: ...; hand-review flags" | C | keep | Scorer-calibration rubric |
| 561 | "Known scorer false-positives (hand-review required):" | C | keep | Rubric |
| 562 | "Confirmed hand-review will catch these." | C | keep | Rubric |
| 572 | "100% manual review of all 960 generations...hand-review is 13-19h..." | B | "100% LLM-as-judge review...Opus-review is 13-19h..." | Pre-registered protocol budget actually spent on Opus |
| 584 | "Plus ~20h hand-scoring over ~6 days..." | B | "~20h Opus-scoring" | Same budget |
| 875 | "## Day 19 — ...: hand-review verdict (F103)..." | B | "Opus-review verdict (F103)" | F103 Opus session |
| 889 | "### Afternoon: ...dispatched independent hand-review session" | B | "dispatched independent Opus-review session" | Explicit Opus session |
| 893 | "User dispatched the package to a separate Claude session for independent hand-review." | B | "for independent Opus-review" | Explicit Claude-session attribution |
| 901 | "Cell-mean hand-rubric for qwen × RT × L18 α=20: 1.0 vs baseline 3.0." | B | "Opus-rubric verdict" | Dispatched-session output |
| 901 | "...is actually a -2.0 *regression* by hand-review." | B | "by Opus-review" | Same |
| 905 | "### What the data actually shows after hand-review" | B | "after Opus-review" | F103 section |
| 919 | "docs/findings.md F103 — full retraction + hand-review verdict..." | B | "Opus-review verdict" | F103 attribution |
| 922 | "docs/post-mvp-decisions.md — Day-19 hand-review revision...hand-rubric picks..." | B | "Day-19 Opus-review revision...Opus-rubric picks" | F103 |
| 928 | "The Day-19 hand-review confirms this empirically..." | B | "The Day-19 Opus-review confirms..." | F103 |
| 936 | "Hand-review at MVP scale was already expensive..." | B | "Opus-review at MVP scale was already expensive" | Scalability context |
| 942 | "...the F103 hand-review are mutually reinforcing..." | B | "the F103 Opus-review" | F103 |
| 955 | "...skip it given hand-review already weakened the specificity claim?" | B | "given Opus-review already weakened..." | F103 |
| 963 | "## Day 20 evening — Full hand-review of 200 items reverses F103's verdict..." | B | "Full Opus-review of 200 items" | Day-20 review |
| 965 | "Three sweeps' worth of generations hand-reviewed item-by-item." | B | "Opus-reviewed item-by-item" | Same session |
| 969 | "Hand-review shows monotonic IH-virtuous behaviour..." | B | "Opus-review shows..." | Day-20 verdict |
| 979 | "Without hand-review, every numerical claim from this project is unreliable." | B | "Without LLM-as-judge review" or "Without Opus-review" | Methodological claim |
| 979 | "...manually calibrated against hand-rubric, not pre-registered." | D | **needs your call** (default: split-phrase) | Calibration was author + verdicts were Opus |
| 1079 | "Hand-review of fresh v2 vEG_L7 × α=4, α=8..." | B | "Opus-review of fresh v2 vEG_L7..." | Day-22 verdict |
| 1103 | "Composition behavioral test: ...hand-rate." | C | keep | Forward-experiment plan |
| 1135 | "...without hand-review of cosine matrix + cross-checks against v1_backup files..." | A | keep | Author sanity-check |
| 1149 | "## Day 23 — Round 3 sweep complete; 121 generations hand-reviewed..." | B | "121 generations Opus-reviewed" | Day-23 bulk |
| 1192 | "6. Hand-review." | C | keep | Phase-2 plan step |
| 1218 | "### Phase 2 hand-review setup" | B | "Phase 2 Opus-review setup" | Day-24 sub-agent pipeline |
| 1229 | "### Approach to scaling hand-review" | B | "Approach to scaling LLM-as-judge review" | Sub-agent scaling |
| 1237 | "...plus the 8 cells I'd already done by hand at the start)" | B | "...8 cells the Opus session had already done one-at-a-time before the parallelism pivot" | Journal in Claude-session voice; "the user" (L1231) = Sumit, "I" = Opus. The 8 cells were one-at-a-time Opus reading, not author work. (Reclassified A→B post D-resolution.) |
| 1285 | "### F110 — Cross-model 1,752-generation hand-review confirms F109 at scale" | B | "1,752-generation Opus-review" | F110 sub-agent pipeline |
| 1372 | "Triage method validated: hand-judging top activations works." | B | "Opus-judging top activations works" | Day-26 SAE triage = LLM-as-judge |
| 1619 | "Full hand-review of all 1,110 generations completed..." | B | "Full Opus-review of all 1,110 generations" | Day-29 battery |
| 1619 | "...same rigor pattern as Day 25's cross-model hand-review." | B | "same rigor pattern as Day 25's cross-model Opus-review" | Cross-ref |
| 1627 | "## Day 30 — Full hand-review (1,110 verdicts) + findings landed..." | B | "Full Opus-review (1,110 verdicts)" | Day-30 |
| 1629 | "Hand-review of every generation in the battery dataset..." | B | "Opus-review of every generation" | Same |
| 1650 | "...is decisively disproved with N=1,110 hand-judged generations." | B | "N=1,110 Opus-judged generations" | F115 N |
| 1653 | "...real-feature variation is indistinguishable from random-vector variation in hand-review." | B | "in Opus-review" or "by LLM-as-judge" | F119b |
| 1661 | "...a clear 'no' backed by 1,110 hand-judged generations." | B | "1,110 Opus-judged generations" | SAE thread bottom-line |
| 1673 | "## Day 31 — Mechanism-shift battery v1: launched, completed, hand-reviewed, F120 landed." | B | "Opus-reviewed" | Day-31 |
| 1694 | "### Hand-review verdict (104 rows, same rubric as F115-F119)" | B | "Opus-review verdict (104 rows)" | Mech-battery |
| 1714 | "...across 2,914+ hand-judged generations..." | B | "2,914+ Opus-judged generations" | F120 N |
| 1719 | "Detection-product pivot — ship the FM-X classifier built on 2,914 hand-judged generations." | B | "2,914 Opus-judged generations" | Day-31 next-steps |
| 1727 | "1. Tests on a similarly large hand-judged battery (N > 500), or" | C | keep | Future methodology |
| 1730 | "...3-5 conditions × 3-5 prompts × 2-3 models, hand-judged, before..." | C | keep | Future methodology |

---

### sae_round_report.md (22 occurrences) — 0 A · 22 B · 0 C · 0 D

Every "hand-judged" in this doc is a dataset-size attribution to Opus-judged labels. Uniformly B.

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 6 | "~3 days of human hand-review." | B | "~3 days of Opus-as-judge review" | Top-of-report compute |
| 7 | "1,162 hand-judged." | B | "1,162 Opus-judged" | Top-of-report N |
| 15 | "1,162 hand-judged generations, and 4 distinct mechanism variants..." | B | "1,162 Opus-judged generations" | TL;DR N |
| 27 | "Cross-model study of Days 24-25 (1,752 hand-judged generations...)" | B | "1,752 Opus-judged generations" | F111 sub-agent pipeline |
| 279 | "### 5.3 Hand-review of 1,110 generations (Day 30, 2026-05-13)" | B | "Opus-review of 1,110 generations" | Section header |
| 421 | "### 6.4 Hand-review (52 steered generations)" | B | "Opus-review (52 steered generations)" | Section header |
| 445 | "2,914+ hand-judged generations spanning {additive sign}..." | B | "2,914+ Opus-judged generations" | F120 headline |
| 457 | "F110 — cross-model hand-review confirms F109..." | B | "cross-model Opus-review confirms F109..." | F110 attribution |
| 458 | "F111 — v_IH falsified across 4 prompts × 3 model families (1,752 hand-judged generations)" | B | "1,752 Opus-judged generations" | F111 N |
| 464 | "F115 — Tier-1 humility SAE features fail...1,110 hand-judged generations..." | B | "1,110 Opus-judged generations" | F115 N |
| 471 | "Cumulative N: 2,914+ hand-judged generations across two studies..." | B | "2,914+ Opus-judged generations" | Cumulative-N |
| 497 | "5. 2,914 hand-judged generations — labeled dataset..." | B | "2,914 Opus-judged generations" | Artifact list |
| 504 | "Hand-review pipeline (per_generation.csv schema + auto-judge calibration)" | B | "Opus-review pipeline" or "LLM-as-judge pipeline" | Pipeline = sub-agent setup |
| 526 | "...our 2,914 hand-judged generations are exactly such a dataset..." | B | "2,914 Opus-judged generations" | Phase-2 discussion |
| 541 | "- Methodology / hand-review protocol writeup (publishable)" | B | "Opus-review protocol writeup" or "LLM-as-judge protocol writeup" | Methodology category |
| 573 | "...per_generation.csv — 1,110 hand-judged rows..." | B | "1,110 Opus-judged rows" | Dataset file |
| 574 | "...per_generation.csv — 104 hand-judged rows (52 baseline + 52 steered)" | B | "104 Opus-judged rows" | Mech-battery file |
| 575 | "...per_generation.csv — 1,752 hand-judged rows from the F110/F111 cross-model study..." | B | "1,752 Opus-judged rows" | Cross-model file |
| 587 | "06_hand_review_findings.md — consolidated hand-review writeup" | B | filename KEEP; description "consolidated Opus-review writeup" | Literal filename |
| 591 | "03_per_cell/{cell}.md — per-cell hand-review writeups" | B | "per-cell Opus-review writeups" | Pipeline output |
| 630 | "N=2,914 hand-judged generations across 5 models × 5 SAE families × 4 mechanism types..." | B | "N=2,914 Opus-judged generations" | Cumulative N |
| 637 | "...hand-review at scale" | B | "LLM-as-judge at scale" | Methodological discipline upgrade |

> ⚠ **Note on D4**: This file will be archived to `docs/archive/sae_round_report_20260513.md` as part of D4. Whether to apply terminology fixes *before* archival is a procedural call. **Default: apply, then archive** (so the historical record uses honest language).

---

### scoring.md (34 occurrences) — 1 A · 8 B · 25 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 3 | "Every benchmark item is hand-reviewed." | C | keep | MVP-policy methodology |
| 3 | "...to compare against human scores" | C | keep | Methodology baseline |
| 13 | "...unless it has been hand-scored." | C | keep | Policy |
| 14 | "Every response is hand-reviewed." | C | keep | Policy |
| 14 | "...the cost of hand review is acceptable." | C | keep | Policy |
| 14 | "...hand-review is not tenable..." | C | keep | Scaling discussion |
| 27 | "96 Qwen abstention responses hand-scored." | A | "author hand-scored" (or keep) | Day-14 sample (96 items, tractable solo) |
| 96 | "Known scorer false positives (hand-review required):" | C | keep | Calibration-set rubric |
| 157 | "Hand-review still required for subtle cases." | C | keep | FM-6 rubric |
| 159 | "Day 19 hand-review of α-sweep (F103)..." | B | "Day 19 Opus-judged review of α-sweep (F103)" | F103 |
| 160 | "Day 19 hand-review (F103): qwen × RT × L25..." | B | "Day 19 Opus-reviewed cells (F103)" | F103 |
| 160 | "consider LLM-as-judge for borderline cases" | C | keep | Already correct |
| 193 | "all benchmark claims must be manually verified" | C | keep | Policy (web-verification is author) |
| 216 | "to validate the F104 hand-review reversal..." | B | "to validate the F104 Opus-reviewed reversal" | F103/F104 Opus |
| 232 | "Hand-review remains primary for any factual-correctness claim." | C | keep | Scorer-limitation methodology |
| 242 | "The benchmark is designed for hand-review only." | C | keep | Benchmark design |
| 248 | "FM-10... Scoring detection: hand-review only" | C | keep | Detection prescription |
| 254 | "Day-20 hand-review reversal of F103's v_IH verdict..." | B | "Day-20 Opus-reviewed reversal" | F103 690-gen review |
| 254 | "third documented instance of auto-scorer failure that hand-review caught" | B | "...that Opus-review caught" | F94-UPDATE/F103/F104 |
| 257 | "Hand-review every cell of every steering sweep..." | C | keep | Forward methodology |
| 258 | "auto-scorer rankings should never be quoted as findings without hand-review backup." | C | keep | Policy |
| 259 | "v2 scorers... calibrated post-hoc against hand-review" | B | "calibrated post-hoc against Opus-judged verdicts" | Calibration anchors |
| 273 | "Detection: hand-review only." | C | keep | Detection rubric |
| 278 | "should be hand-rated as wrong" | C | keep | Rubric |
| 297 | "Implication for hand-review:..." | C | keep | Rubric directive |
| 303 | "Hand-review scoring policy unchanged" | C | keep | Policy |
| 322 | "Detection: Hand-review of stated final ranking." | C | keep | Detection rubric |
| 337 | "Detection: Hand-review of the Part 2 calculation." | C | keep | Detection rubric |
| 353 | "Detection: Hand-review. Web-verification..." | C | keep | Detection rubric |
| 359 | "The hand-review of the 1,110-generation SAE-feature..." | B | "The Opus-judged review of the 1,110-generation SAE-feature..." | F115-F119 |
| 366 | "For hand-review, treat the broader pattern..." | C | keep | Rubric directive |
| 368 | "Hand-review for any future steering experiment at α∈[0.1, 2.0]..." | C | keep | Forward directive |
| 381 | "Detection: Hand-review or token-class entropy check." | C | keep | Detection rubric |
| 398 | "Detection: Hand-review of stated percentage..." | C | keep | Detection rubric |
| 412 | "Detection: Hand-review. Auto-scorer would not detect..." | C | keep | Detection rubric |
| 431 | "F110 hand-review extends F109 from qwen3-4b to 3 model families" | B | "F110 Opus-judged review extends F109..." | F110 |

---

### post-mvp-decisions.md (34 occurrences) — 0 A · 18 B · 15 C · 1 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 58 | "Hand-review all ~960 generations via mvp/review/app.py..." | C | keep | Forward 4×4 protocol |
| 68 | "note that manual review confirmed the auto-scorer results" | C | keep | Branch-conditional language |
| 95 | "check hand-review: is it scorer artifact..." | C | keep | Conditional methodology |
| 117 | "Identify which specific cells failed and why via hand review." | C | keep | Conditional methodology |
| 226 | "We had to hand-review every generation specifically because writers..." | B | "We had to Opus-review every generation..." | MVP review activity |
| 262 | "## Day-19 hand-review revision (2026-04-26 — F103 lands)" | B | "## Day-19 Opus-reviewed revision" | F103 section header |
| 264 | "Hand-review of all 690 generations (independent reviewer session..." | B | "Opus-judged review of all 690 generations (independent Opus session..." | F103 explicit |
| 266 | "Real signals revealed by hand-review are an order of magnitude smaller" | B | "Real signals revealed by Opus-review..." | F103 |
| 268 | "### What the hand-review *actually* showed" | B | "### What the Opus-review *actually* showed" | F103 |
| 284 | "Hand-review Priority-5 finding: CC steering on qwen..." | B | "Opus-review Priority-5 finding" | F103 |
| 302 | "| F98 dimension | Original verdict | Day-19 hand-review revision |" | B | "Day-19 Opus-reviewed revision" | F103 table |
| 307 | "Auto-scorer reliability... Inadequate... Hand-review required." | C | keep | Forward directive |
| 325 | "### When to revisit (hand-review revision)" | B | "### When to revisit (Opus-reviewed revision)" | F103 |
| 328 | "If anyone else hand-reviews the same 690 generations..." | D | **needs your call** (default: keep) | Hypothetical future reviewer |
| 344 | "...168 generations, hand-reviewed) produced findings..." | B | "168 generations, Opus-judged" | Day-22 v2 sweep |
| 371 | "...hand-review has been the operational gate throughout." | B | "Opus-review has been the operational gate" | Ongoing MVP practice |
| 375 | "Hand-review every cell of every steering sweep." | C | keep | Forward directive |
| 379 | "### When to revisit (Day-23 hand-review revision)" | B | "### When to revisit (Day-23 Opus-reviewed revision)" | F109 |
| 389 | "121 generations hand-reviewed (no auto-scorer)." | B | "121 generations Opus-judged (no auto-scorer)" | Day-23 |
| 416 | "α-sweep per prompt + hand-review for rail selection." | C | keep | Forward methodology |
| 428 | "Phi-3.5-mini extraction + sweep + hand-review." | C | keep | Future-phase plan |
| 443 | "7. Hand-review every cell." | C | keep | Protocol step |
| 451 | "## Day-25 update... Cross-model 1,752-generation hand-review + product-hypothesis pivot" | B | "Cross-model 1,752-generation Opus-judged review" | F110 |
| 512 | "Measure commit rate before vs after. Hand-review every cell." | C | keep | Forward F112 generalization |
| 546 | "After the 5-model 2,443-generation hand-review wrap..." | B | "After the 5-model 2,443-generation Opus-judged review wrap" | MVP+SAE corpus |
| 556 | "Title sketch: 'A 2,443-Generation Hand-Reviewed Cross-Family Study'" | B | "A 2,443-Generation Opus-Reviewed Cross-Family Study" (or "LLM-as-judge") | **HIGHEST-LEVERAGE FIX** — paper title |
| 564 | "2,467 hand-graded generations" | B | "2,467 Opus-judged generations" | Counted-corpus metric |
| 573 | "...directly comparable to arxiv 2506.18167. ~2 days of compute + hand-review." | C | keep | Future-work estimate |
| 587 | "...did the model commit to a Bayesian update' requires hand-review" | C | keep | Methodology contrast |
| 715 | "...31 cells × 1,110 generations, all hand-judged..." | B | "...all Opus-judged" | SAE battery |
| 740 | "mech-shift battery v1 (4 mechanism variants, 52 hand-judged generations)" | B | "52 Opus-judged generations" | Mech-shift |
| 750 | "Of the 2,914 hand-judged generations across both studies..." | B | "Of the 2,914 Opus-judged generations..." | Full corpus |

---

### project.md (18 occurrences) — 2 A · 14 B · 2 C · 0 D

> ⚠ **Note**: This entire file will be replaced by the verified draft in D1. **Default: apply terminology fixes to the draft itself** (the draft already uses "2,914 Opus-judged generations" where applicable). The audit rows below are for completeness; once the draft is installed, most rows are moot. The "by hand" lines in the original (lines 75, 132) describe Phase-4/manual-first principles and are A — corresponding content in the draft is more succinct.

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 17 | "...as residual-stream steering has, across 2,914 hand-judged generations" | B | "2,914 Opus-judged generations" | (Moot — section deleted in draft replacement) |
| 75 | "Generate a complete corpus for a single high-likelihood concept by hand" | A | keep | Phase-4 author plan |
| 132 | "Every pipeline step is first done by hand once..." | A | keep | Manual-first principle |
| 157 | "~200+ items hand-reviewed across 3 sweeps" | B | "~200+ items Opus-reviewed across 3 sweeps" | Day-19+ sweeps |
| 187 | "200+ items hand-reviewed in mvp/results/full_hand_review_*.md." | B | "200+ items Opus-reviewed in mvp/results/full_hand_review_*.md" | (Filename kept) |
| 188 | "Hand-reviewed in mvp/results/full_hand_review_diagnostic_batch.md." | B | "Opus-reviewed in..." | (Filename kept) |
| 223 | "...hand review catches the failures." | B | "Opus-review catches the failures" | F94-UPDATE/F103/F104 |
| 243 | "mvp/results/ — detailed per-experiment result docs and hand-review verdicts" | B | "Opus-judged verdicts" | File-role description |
| 245 | "mvp/results/full_hand_review_*.md — hand-review verdicts (4 docs)" | B | "Opus-reviewed verdicts (4 docs)" | File-role |
| 257 | "Hand-review verdicts, multi-cell synthesis..." | B | "Opus-judged verdicts, multi-cell synthesis..." | File-role |
| 265 | "Round 3 sweep complete. 121 generations hand-reviewed..." | B | "121 generations Opus-judged" | Day-23 |
| 294 | "Phi-3.5-mini extraction + sweep + hand-review." | C | keep | Future-phase plan |
| 302 | "6. Hand-review." | C | keep | Protocol step |
| 309 | "Status update (...post cross-model 1,752-generation hand-review)" | B | "post cross-model 1,752-generation Opus-judged review" | F110 |
| 311 | "All hand-graded (no auto-scorer)." | B | "All Opus-judged (no auto-scorer)" | Cross-model |
| 365 | "F110 — Cross-model 1,752-generation hand-review confirms F109 at scale" | B | "Cross-model 1,752-generation Opus-judged review" | F110 |
| 376 | "publishable as a cross-model hand-review study..." | B | "publishable as a cross-model Opus-judged study" or "LLM-as-judge study" | Paper-framing |

---

### experiments.md (9 occurrences) — 0 A · 7 B · 2 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 814 | "## Phase 5 evening — Hand-review reversal of Day-19 verdicts" | B | "Opus-reviewed reversal of Day-19 verdicts" | F104 |
| 816 | "Hand-rubric verdicts on 200 items across 24 Path-A cells..." | B | "Opus-judged rubric verdicts on 200 items..." | F104 200-item verdict |
| 818 | "Hand-review shows v_IH × L17 is the cleanest behavioural-effect vector" | B | "Opus-review shows v_IH × L17 is the cleanest..." | F104 |
| 831 | "136 hand-reviewed items in mvp/results/full_hand_review_diagnostic_batch.md" | B | "136 Opus-reviewed items..." | Day-21 |
| 902 | "Final cell counts (all hand-reviewed, 168 generations):" | B | "all Opus-judged, 168 generations" | Day-22 v2 |
| 954 | "Pulled to local, hand-reviewed every generation." | B | "Pulled to local, Opus-reviewed every generation" | Day-23 |
| 958 | "(all hand-reviewed, 121 generations, no auto-scorer):" | B | "all Opus-judged, 121 generations" | Day-23 |
| 991 | "Phase 2 (queued, user direction): phi-3.5-mini extraction + sweep + hand-review." | C | keep | Future-phase plan |
| 997 | "6. Hand-review." | C | keep | Protocol step |

---

### eg-rt-eval-spec.md (9 occurrences) — 0 A · 0 B · 9 C · 0 D — all keep

All occurrences are rubric/calibration/FM-table mitigation language. No replacements proposed. (Lines 176, 181, 188, 191, 320, 326, 399, 431, 438.)

---

### extraction-runbook.md (8 occurrences) — 0 A · 0 B · 8 C · 0 D — all keep

All occurrences are pipeline-protocol / workflow / runbook language. No replacements proposed. (Lines 149, 215, 217, 331, 392, 431, 432, and one already-correct "LLM-as-judge fallback" at L392.)

---

### sae-experiment-plan.md (7 occurrences) — 1 A · 3 B · 3 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 43 | "...hand-judged what-fires-it, status, triage tier..." | A | keep (or "author hand-judged") | SAE-feature triage by author (per feature-catalog history) |
| 107 | "Hand-review every output" | C | keep | Pre-registered protocol step |
| 198 | "4. Hand-review for: does the model articulate verification needs..." | C | keep | Forward-experiment protocol |
| 204 | "Estimated work: ~30 generations on a custom 5-prompt set, hand-reviewed." | C | keep | Future-experiment estimate |
| 214 | "Full battery (5 models × 31 cells × 1110 generations, all hand-judged)" | B | "all Opus-judged" | F115-F119 SAE battery |
| 224 | "Additional findings from the battery hand-review that weren't pre-registered" | B | "from the battery Opus-judged review" | F116-F119 |
| 230 | "See mvp/results/sae_steering_analysis_20260513/ for the per-cell hand-review dataset." | B | "per-cell Opus-judged dataset" | Opus verdicts |

---

### phase5-plan.md (6 occurrences) — 0 A · 2 B · 4 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 47 | "The Day-19 hand-review (F103) showed that the MVP auto-scorer awarded..." | B | "The Day-19 Opus-judged review (F103)" | F103 |
| 57 | "the Day-19 hand-review session produced a re-runnable signal extractor" | B | "the Day-19 Opus-review session..." | F103 |
| 63 | "At Phase-5 scale, manual-first scoring is not tenable" | C | keep | Scaling argument |
| 63 | "...exceeds hundreds of hours of human review" | C | keep | Scaling argument |
| 104 | "At 1 min each: 102 hours of manual review = 2.5 weeks" | C | keep | Scaling argument |
| 187 | "~$200-500 GPU. ~100h of human review + engineering time." | C | keep | Cost snapshot |

---

### generation-guidelines.md (5 occurrences) — 4 A · 0 B · 1 C · 0 D — all keep

All occurrences correctly describe author-as-curator (lines 5, 354, 538, 659, 741). No replacements proposed.

---

### mvp-virtues.md (4 occurrences) — 2 A · 1 B · 1 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 64 | "No scorer automation. Every response is hand-reviewed." | C | keep | MVP-policy |
| 211 | "6. Hand-review every triplet" | A | keep | Author-curator |
| 221 | "~40 hand-crafted + curated EG triplets... Hand-reviewed." | A | keep | Author-curator |
| 231 | "...specificity matrix manually hand-scored against auto-scorer..." | B | "Opus-judged against auto-scorer" | At-scale verdict |

---

### negative-control-corpus-handoff.md (2 occurrences) — 0 A · 2 B · 0 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 17 | "Behavioural hand-review (F103) showed small..." | B | "Behavioural Opus-judged review (F103)" | F103 |
| 254 | "the F103 hand-review verdict that motivates this whole task." | B | "the F103 Opus-judged verdict" | F103 |

---

### evening-note-2026-04-25.md (1 confirmed occurrence per re-scope) — C — keep

Line 165: "Hand-review will catch them as planned." — methodology / forward-looking, keep.

---

### writeup-plan.md (1 occurrence) — 0 A · 1 B · 0 C · 0 D

| Line | Original snippet | Cat | Proposed replacement | Rationale |
|---:|---|:---:|---|---|
| 126 | "Hand-review protocol (per_generation.csv schema + how verdicts were assigned...)" | B | "Opus-review protocol" or "LLM-as-judge protocol" | Paper-methodology section |

> ⚠ **Note**: writeup-plan.md L128 also claims "rater = the project author" which is itself misleading per the new ground-truth — actually rater = Opus sessions, with the author as session-driver. This is **out of scope for D0 terminology audit** but related; flagging for D1/D2-D3 follow-up.

---

### review-rubric.md (1 occurrence) — 0 A · 0 B · 1 C · 0 D — keep

Line 310: "the triplet is marked for human review rather than retried further." — verifier-fallback rubric, keep.

---

### references.md (1 occurrence) — 0 A · 0 B · 1 C · 0 D — keep

Line 229: "verification (different generator, different family, or human review)" — F71 paraphrase, keep.

---

## What I plan to do after your approval

1. Resolve the 7 D-flagged occurrences per your decisions in the table above (or leave at defaults).
2. Apply replacements per the "Proposed replacement" column to all B-category rows. Use `Edit` per file, batched.
3. Skip C-category rows entirely (no edits).
4. Skip A-category rows unless explicitly marked with a clarifying replacement.
5. Re-run the same grep at end of D0 to confirm zero remaining unaddressed B-category occurrences.
6. Leave `feature-catalog.md` untouched (read-only per consolidation prompt).
7. The literal filenames `06_hand_review_findings.md`, `mvp/results/full_hand_review_*.md`, `mvp/results/full_hand_review_diagnostic_batch.md` stay as-is (filesystem references); only their *descriptions* in the prose get updated.

## Open question for you

The draft `project.md` (D1) refers to **"hand-judged" → "Opus-judged"** correctly in two places, so the draft itself doesn't need terminology fixes. But if you want a consistency pass on the draft's language before installing it, say so and I'll do it as part of D1.
