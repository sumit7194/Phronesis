# Handoff for independent corpus + project review

This doc briefs a fresh session (different machine, no prior context) on the Phronesis project so it can do an independent corpus review and second-opinion analysis.

Repo: https://github.com/sumit7194/Phronesis (branch `main`, latest commit `b9ca7e1`).

---

## What the other session should read first (in order)

1. **`mvp/results/where_we_are_simple.md`** — start here. Plain-English current state of the project: what we set out to do, what we've found, vector inventory (1 working / 1 borderline / 1 misaligned / 1 untested / gemma null), what the corpus problem is, ranked next-step menu.

2. **`mvp/results/corpus_inspection_EG.md`** — the today-finding that motivates the review. Documents that across all 40 EG triplets, virtuous and non-virtuous-deficiency contain the SAME specific facts; the contrast is on calibration/framing, not on specificity. Includes concrete examples from ~10 triplets cited end-to-end.

3. **`mvp/results/full_hand_review_synthesis.md`** — synthesis across the 200 hand-reviewed generations from Day 20 (qwen × IH × L17, qwen × RT × L15 envelope, qwen × eg-eval-v2). Documents the upgrade of v_IH (auto-scorer was wrong; vector works) and the downgrade of v_RT (effect is real but borderline).

4. **`mvp/results/full_hand_review_pathA.md` and `_pathD.md`** — the underlying per-cell verdicts that synthesis is built on.

5. **`mvp/results/diagnostic_batch_plan.md`** — what's running on the VM right now (Day 21 overnight). Four diagnostics: cross-application v_IH↔v_EG, v_EG at deeper layers, v_CC × L9 on simple reasoning. Outputs land at `mvp/results/benchmark_probe/{cc-simple,abstention,eg-eval-v2}/diag_*/`.

---

## The review task

The other session is asked to **independently review the four virtue corpora** to verify (or contest) the today-finding that "EG corpus encodes calibration, not specificity, and probably the other corpora have analogous design issues."

### Corpora to inspect

All four live under `corpus/triplets-combined/` — but most of the curated final triplets used for vector extraction are split across four virtue folders. Concretely the relevant paths:

- **Evidence Grounding (EG)**: `corpus/mvp-combined/triplets-evidence-grounding/` — 40 triplets, the one already inspected. Other session should sample a few to confirm the calibration-vs-specificity finding is real.

- **Reasoning Transparency (RT)**: `corpus/mvp-combined/triplets-reasoning-transparency/` — ~40 triplets. NOT yet inspected systematically. Question for review: when the corpus contrasts virtuous-RT against non-virtuous-RT, is the difference "shows reasoning steps explicitly" vs "states conclusion without steps", OR is it "calibrated/hedged" vs "overconfident" (i.e. the same axis as IH)?

- **Intellectual Humility (IH)**: `corpus/triplets-intellectual-humility/` — ~20 hand-written triplets. The vector extracted from this is the ONE confidently working one (per `full_hand_review_synthesis.md`). Question: what makes the IH contrast cleaner than EG's?

- **Calibrated Confidence / Combined (CC)**: `corpus/triplets-combined/` and `corpus/triplets/` (legacy 50-triplet hand corpus). The CC vector hasn't been hand-tested at AP-peak yet (running tonight).

### The four virtues and what they are SUPPOSED to mean

From the project's `concepts.md`-style definitions:
- **IH (Intellectual Humility)**: acknowledging limits of one's knowledge; saying "I don't know" / "this premise is wrong" / "this is contested" rather than confabulating.
- **EG (Evidence Grounding)**: claims tied to specific evidence; distinguishing observation from inference; naming evidence types.
- **RT (Reasoning Transparency)**: showing your work; making the inference chain visible rather than just stating the conclusion.
- **CC (Calibrated Confidence)**: confidence proportionate to evidence; commits when evidence supports commitment, hedges when it doesn't.

### What we want the other session to report

For each of the four corpora, in <500 words per virtue:

1. **What axis does the contrast actually run on?** Pick a few triplets, read them, identify what *concretely* differs between virtuous and non-virtuous. Give specific examples (quote the passages).
2. **Is that axis the same as the labelled virtue?** If yes, explain. If no, name what axis it actually is.
3. **Pairwise, do any two corpora contrast on the SAME axis?** This is what we suspect for IH and EG.
4. **Bottom-line recommendation** — does this corpus need redesign (yes / no / partial)? If yes, in one paragraph what would the fix look like?

The goal is not to defend our prior conclusion. If the other session reads the corpora and decides our interpretation is wrong, that's a more valuable result than agreement.

---

## Useful scaffolding the other session has access to

- All ~135 generations from tonight's diagnostic batch will be in `mvp/results/benchmark_probe/{bench}/diag_*/` once the sweep finishes (~05:00 IST). They can use those to ground claims about how the vectors behave behaviourally (vs. just inspecting the corpus statically).
- Extracted vectors at every layer for every virtue × every model: `mvp/results/vectors/<model>/<corpus>/last_token/layer_<N>_virtue_vector.npy`.
- Attribution-patching results identifying AP-peak layers per virtue × model: in `mvp/results/attribution_patching/`.
- Auto-scorers v1 + v2 for IH and EG: `mvp/benchmarks/ih_scorer_v2.py`, `mvp/benchmarks/eg_scorer_v2.py`. (Note: per the synthesis doc, v1 auto-scorers proved unreliable; hand review is the source of truth.)

---

## Things that ARE NOT in scope for this review

- Re-running any sweeps. The other session is doing analysis, not GPU work.
- Building new corpora. Just inspecting existing ones.
- Litigating the methodology lessons (auto-scorers lie, hand review necessary). Those are settled per `full_hand_review_synthesis.md`.

---

## Background that's optional but useful

- `mvp/results/full_review_inventory.csv` — index of all hand-reviewed items
- `mvp/results/manual_scoring_qwen_abstention.md` — the hand-review of v_IH that revealed the auto-scorer was wrong
- `mvp/results/calibration-batch-audit-v1.md` — earlier audit of qwen baseline behavior

---

## How to phrase the request to the other session

> "Read `mvp/results/where_we_are_simple.md`, `mvp/results/corpus_inspection_EG.md`, and `mvp/results/HANDOFF_FOR_REVIEW.md`. Then independently review each of the four virtue corpora (paths in HANDOFF_FOR_REVIEW.md) and report per the four questions there. Don't just defend my prior conclusion — if you read the corpora and disagree, say so."
