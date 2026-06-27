# Pre-registration — Does reasoning flatten the depth-of-emergence of parametric recall?

*Locked before any activation. Welds our F165 (depth-of-emergence: recalled facts become linearly
legible only at deep layers) to Google Research's "Thinking to Recall" (reasoning traces improve
single-hop factual recall via a computational-buffer effect + factual priming).*

## The bridge

F165: a scalar *recalled from weights* is linearly legible only at deep layers (atomic number L4
r=0.40 → L36 r=0.92) — recall is an *assembled* process, not an instant lookup. Google: letting the
model *reason first* improves recall of even simple facts, via (1) a content-independent
**computational buffer** (extra autoregressive forward passes) and (2) **factual priming** (the trace
states related facts → contextual bridges). Our prediction: **reasoning should flatten the
depth-of-emergence ramp** — the recalled scalar becomes legible at *shallower* layers when read at the
end of a reasoning trace, because the model has had extra compute (buffer) and/or has primed related
facts into context.

## Setup

Model: **Qwen3-4B** (same as F165; Mac, RAM free). v1 = **atomic number, elements 1–118** (exact Z,
`corpus/legibility/knowledge_battery.json`) — deliberately spanning easy (1–54, recalled cold) → hard
(lanthanides/actinides/superheavies, where the 4B is shaky, cf. F167). v2 = **add birth-year** (40
famous people, `targets.json`) as a second, varied fact type. Probe-ladder = RidgeCV linear-decode r of
the scalar per layer, 5-fold CV, Pearson r (the F165 method). Layers {4,8,…,36}.

**Easy/hard split (the key analysis):** each fact is labelled *recalled* (easy) iff a direct thinking-
OFF answer exact-matches the value. We probe legibility separately on the **full / easy / hard**
subsets. Thinking has *room to help* mainly on the hard subset (easy is already near-ceiling in
nothink). Honest caveat: thinking can only surface *known-but-hard-to-reach* facts; for genuinely
unknown facts no reasoning conjures the value (and per Google, hallucinated steps *hurt*) — so a flat
or negative hard-subset effect is interpretable, not a failure.

Two conditions, read at the **pre-answer** residual position:
- **nothink** (immediate recall): chat template, thinking **off**, prompt "What is the atomic number
  of {X}? Reply with only the number." → read the last input-token residual per layer. (Establishes
  the depth-of-emergence ramp fresh on this model.)
- **think** (post-reasoning): thinking **on**, generate the reasoning trace, then read the residual at
  the end of the trace (the `</think>` boundary) per layer. Record the trace text.

**Mechanism split (the part our frame uniquely enables):** classify each `think` trace by whether it
**states Z** in text (regex for the integer).
- trace **states Z** → *factual priming* (self-generated in-context-ification — trivially legible).
- trace **does NOT state Z** but Z is more legible at shallow layers than `nothink` → the *pure
  computational-buffer* effect on representation (the genuinely new result).

## Predictions (locked)

1. **think flattens the ramp:** shallow-layer linear-r(think) > shallow-layer linear-r(nothink) by a
   margin (pre-register ≥0.15 at the shallowest probed layer), with peak (deep) legibility similar.
2. **Buffer is real if the flattening survives the no-Z-stated subset:** on traces that never state Z,
   shallow-layer r(think) still exceeds r(nothink). If the effect lives *only* in Z-stated traces, it
   is priming/in-context-ification, not buffer.
3. **Null/falsifier:** if r(think) ≈ r(nothink) at all layers, reasoning does not change *where* the
   scalar is legible in the residual (the recall improvement, if any, would then be purely behavioral,
   not a representational-depth shift) — reportable.

## Pivot (2026-06-27) — behavioral replication first (positive control for our methodology)

The scalar depth-probe needs scalar facts; the only reliable-GT scalar facts (atomic numbers, famous
birth years) are *too easy* on a 4B (recall ≈95% → no hard subset). The fix is the *question
distribution*, not the model: Google used **obscure long-tail** single-hop QA (SimpleQA Verified, where
even Gemini-2.5-Pro scores F1≈55; EntityQuestions). Those answers are **strings**, so the depth-probe
is parked; instead we run the **direct behavioral replication** as a positive control — *if we
reproduce "thinking helps obscure recall," our generation+scoring harness is validated.*

- Data: `google/granola-entity-questions`, the **lowest-popularity** (most obscure) ~200 items; gold =
  `answer` + all `granola_answer_*` (multi-granularity, so any correct granularity counts).
- Per item: generate the answer **thinking OFF** vs **thinking ON** (read the post-`</think>` answer);
  score correct iff any gold answer matches (diacritic-normalized substring).
- **Locked prediction:** `acc(think) > acc(nothink)` on the obscure subset (Google's effect). Report the
  delta, the per-item help/hurt/same breakdown, think_finished rate, and a hand-read sample of where
  thinking flipped wrong→right (priming visible in the trace?) vs right→wrong (hallucinated step, which
  Google found hurts). **Null/falsifier:** acc(think) ≈ acc(nothink) → either the effect doesn't
  reproduce at 4B scale, or our harness is mis-measuring (the whole point of running it as a control).

## Controls / caveats to report

- `think_finished` rate (did the model close `</think>` within the token budget); items that didn't
  are flagged. Z-stated rate. N=54 per cell (one prompt/entity) — modest; RidgeCV regularized.
- First cut on Qwen3-1.7B (weaker reasoner than the blog's Gemini/Qwen3-32B) is a *direction check*;
  4B confirmation pre-registered as the escalation if the 1.7B cut shows the effect.
- Read position differs between arms (input-end vs trace-end); that *is* the manipulation, but it also
  means the two reads see different token contexts — the Z-stated split is what separates "context now
  contains the answer" from "the model assembled it with more compute."
