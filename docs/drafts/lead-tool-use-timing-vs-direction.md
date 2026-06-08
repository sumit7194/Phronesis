# Timing, not direction: what activation-steering a small LLM toward "intellectual humility" actually does in a tool-use loop

*Canonical draft — venue-flexible base for blog / Zenodo / arXiv variants. Author: Sumit. Written with AI assistance; every result was hand-read rather than auto-scored (see disclosure at end).*

---

## Abstract

I set out to make a small, tool-using language model more epistemically careful — better at catching false premises in questions like *"What was the top speed of the Tesla Roadster 2 released in 2024?"* (it wasn't released) — by steering its activations toward an "intellectual humility" direction. Along the way the result inverted twice, and the final, controlled answer is more interesting than the one I was chasing:

1. The humility vector **genuinely improves *when* the model decides to search** (it reaches for the tool on the right questions and stops over-verifying things it already knows).
2. But the same vector makes the model **confabulate *more* on the actual answers** — better tool-*calling* is not better *answers*.
3. The mechanism is a two-phase confidence trade-off: a "commit to what you know" push helps the *decision* to search (turn 1) and hurts the *interpretation* of results (turn 2). Over-calling and confabulation are opposite miscalibrations on one axis; no single static direction wins both.
4. Restricting the steering to **turn 1 only** recovers a real improvement over baseline — but a **random direction at the right phase ties it**. The lever was never the humility direction. It was the *timing*.

The transferable lesson: for inference-time intervention in small tool-using models, **when you intervene dominates which direction you push** — and any steering claim needs a *multi-seed* random control, because a single seed will mislead you.

---

## Setup

**Models.** Two small open-weight "thinking" models that expose a visible reasoning trace: `qwen3-4b` (the workhorse here) and `qwen3.5-9b` (a newer, stronger model used as a check). A non-thinking model (`qwen2.5-7b`) serves as an architecture control.

**Task.** A `<search>…</search>` tool-use harness: the model can emit a search query, receives results, and answers. The hard test is a battery of **false-premise questions** — questions that smuggle in a non-existent product, event, or entity (no "Inception 2", no Microsoft–Discord acquisition, no Sonnet 155). The correct behavior is to search, find no support, and *decline to invent an answer*. Plus obscure-but-real controls (Lake Baikal's depth) and true controls (capital of France) to check the model doesn't simply become reflexively skeptical.

**Intervention.** Additive activation steering: unit-normalize a direction vector, add `α·v̂` to the residual stream at one layer. The direction is an "intellectual humility" vector extracted (diff-of-means over contrastive triplets) at layer 17 of `qwen3-4b`.

**Scoring.** Every delivered answer is **read by hand** — the text after the model's final `</think>`. This is non-negotiable and the single most important methodological choice in the project: automatic and heuristic scorers misled me at least three separate times (counting hedges as catches, or scoring degenerate runs as wins). No number below comes from a regex.

---

## Result 1 — the vector improves *when* the model searches

On `qwen3-4b`, steering with the humility vector at α=16 sharply improves tool-*invocation* calibration. Define **discrimination = (% it searches when it should) − (% it over-calls on questions it could just answer)**:

| condition | should-search | over-call | discrimination |
|---|---|---|---|
| baseline | 12/16 | 4/9 | **+31%** |
| v_IH α16 | 14/16 | 0/9 | **+88%** |

It searches *more* when it should and stops reflexively verifying things it already knows. (Baseline `qwen3-4b` literally reasons *"the capital is Paris, but let me verify"* and burns a search; the steered model just answers Paris.) This survives the controls that usually kill steering results: it's **direction-specific** (three random vectors at matched norm can't reproduce it — they suppress search indiscriminately), **dose-responsive** (an inverted-U peaking at α16), **token-budget-robust**, and **model-specific** (the non-thinking `qwen2.5-7b` is flat-null — the effect needs a reasoning phase to act on).

This looked like the project's first clean, controlled, positive steering result. It is — but it is *narrow*: it concerns only the **decision to search**, not the answer.

## Result 2 — …but it confabulates *more* on the answers

Switching to live web search and hand-scoring a false-premise battery, the picture inverts. On the original 15-prompt set:

| condition | caught | confabulated | no-answer |
|---|---|---|---|
| baseline | 7 | 2 | 6 |
| v_IH α16 | 8 | **5** | 0 |

The steered model **confabulated more than twice as often** (5 vs 2). It searched on nearly every prompt and *still* committed to the false premise — inventing iPhone-16-Mini specs, a "magnitude 4.8" earthquake in Paris, a Switch Pro price, accepting a fictional Amazon–Walmart merger. Better tool-*calling* did not produce better *answers*. The single cherry-picked win that had looked great in an early five-prompt peek was not representative.

So the headline thesis — *steer toward a virtue, get more honest answers* — is **false** here.

## Why: tool-use calibration *is* confidence calibration

The two results aren't contradictory; they're the same mechanism seen at two points in the trajectory.

The humility vector's behavioral effect is, concretely, **decisiveness / self-trust** — "commit to what you think you know." That single push acts in opposite directions at the two phases of a tool-use turn:

- **Turn 1 (decide to search):** "commit to what you know" → stop over-verifying known facts → *better* invoke-calibration. ✓
- **Turn 2 (interpret the results and answer):** "commit to what you know" → commit to the *prior* even when retrieval doesn't support it → *more* confabulation. ✗

Over-calling (under-confident: verifying what you already know) and confabulation (over-confident: committing to a false premise) are **opposite miscalibrations on one confidence axis**. A static direction that fixes one necessarily worsens the other. That is the principled reason a single steering vector can't win both — and the first hint that the interesting variable is *where in the trajectory* you intervene.

Reading the thinking traces sharpens it further. On the cases it gets wrong, `qwen3-4b` frequently **verbalizes the doubt and then overrides it** — *"I'm not sure this exists… but it's probably…"* — and commits. The failure isn't a lack of doubt (the *caught* cases hedge *more*); it's that the doubt fails to resolve into a stated contradiction. The model often *knows*, and doesn't act on it. (A second model, `qwen3.5`, fails the opposite way — it *over*-trusts retrieval and grabs a tangentially-related real fact, e.g. reporting a real French earthquake for the fake Paris one. Two models, opposite failures — which is on its own why one static direction was never going to fix both.)

## Result 3 — phase-gating: steer turn 1 only

If turn-1 steering helps and turn-2 steering hurts, the obvious move is to **gate the intervention by phase**: apply the vector while the model decides whether to search, then switch it off before it interprets the results. I built this into the harness (steer `pre_search` / `post_search` / `all`) and ran a full confirmation-and-control suite on `qwen3-4b`, hand-scored, on a harder 20-prompt false-premise battery, all on *identical cached searches* so the steering effect is isolated from search noise.

| condition | caught / 20 | degenerate (no answer) |
|---|---|---|
| baseline | 9 | 1 |
| v_IH α8, **turn-1 only** | 12 | 1 |
| v_IH α12, **turn-1 only** | **14** | 2 |
| v_IH α16, **turn-1 only** | 10 | 1 |
| v_IH α16, layer 14, turn-1 | 11 | 1 |
| v_IH α16, layer 20, turn-1 | 10 | 0 |
| v_IH α16, **all turns** (≈ the F149 always-on setup) | 5 | 3 |
| random α16, **all turns** | 3 | 7 |

Two things are immediately clear and they are *robust*:

1. **Always-on steering wrecks the answer** (5/20, and a random vector all-turns drops to 3/20, with heavy degeneration). This reproduces the turn-2 harm cleanly and is direction-independent: pushing the post-retrieval answer is destructive no matter what you push.
2. **Turn-1-only steering reliably helps** (10–14 vs baseline 9), across three layers and three doses. Restricting the intervention to the decision phase captures a benefit the always-on version destroys.

This is where I almost stopped and declared a win.

## The control that mattered: multi-seed random

The obvious objection: is the turn-1 improvement specific to the *humility* direction, or would *any* perturbation at turn 1 do it? I'd run one random vector (seed 42 → 6/20) and it cleanly underperformed baseline, which *looked* like clean direction-specificity. But one seed is not a control. Running more:

| turn-1 random vector | caught / 20 | degenerate |
|---|---|---|
| seed 42 | 6 | 5 |
| seed 7 | 7 | 11 |
| **seed 99** | **12** | **0** |

A **random** direction at seed 99 catches **12/20** — tying the best humility dose, with zero degenerate runs. The single seed that suggested specificity (42) only looked clean because it *happened* to break generation on a third of the prompts. Across seeds, random spans 6→12; its variance is dominated by *whether it degenerates*, not by direction.

So the honest reading: **the turn-1 benefit is mostly a generic activation-perturbation effect**, not the humility direction. Jostling the model's activations at the decision point tends to knock a borderline "I'll just answer" trajectory toward "let me ground this first" — and most directions that don't break generation do this. The humility vector's *only* real advantage over random is **reliability**: it's a learned direction that lands in the good regime every time, while random is a coin flip. That's a real but modest property — and a far weaker claim than "we steered the model toward a virtue."

## Controls and caveats (the boring part that makes it real)

- **Baseline reproducibility:** a fresh re-run of the baseline is **30/30 identical** to the original on the same cached searches. Greedy decoding is deterministic; the reused baseline is a valid reference.
- **Strict vs lenient scoring:** an earlier "baseline 13/20" did **not** reproduce under strict hand-scoring (requiring a clear premise-*denial*, not a hedge) — it's 9–10/20. Only the *relative* orderings are load-bearing.
- **Search variance:** a fresh-web-search baseline catches 10 vs the cached 9 (≈ ±1 in aggregate) even though **24 of 30 individual answers differ** — live retrieval churns the wording a lot but the catch-rate little.
- **Precision preserved:** every condition answers all 6 obscure-real facts and all 4 true controls correctly. The turn-1 gain is *selective* — the model doesn't just become reflexively skeptical of everything.
- **The newer model:** on `qwen3.5-9b`, phase-gating a faithfulness vector is **null** — there's no turn-1 invoke-miss to capture, so there's nothing to gate. The effect needs a model that *has* the calibration gap.

## What I actually learned

1. **Timing dominates direction.** Across this whole arc — and the project's earlier steering work with corpus diff-of-means, SAE features, and faithfulness vectors — the *direction* never survives a proper control, but *when* you intervene does. Steering is a blunt instrument: destructive when it touches content (turn 2), only incidentally helpful when it jostles a decision (turn 1).

2. **"Tool-use calibration" is "confidence calibration" wearing a hat.** Over-calling and confabulation are the under- and over-confident ends of one axis. This reframes a lot of "make the agent search better" work as "calibrate the agent's confidence," with the corollary that one static knob can't fix both ends.

3. **The prior-override failure mode.** Small models often *know* a premise is false in their reasoning trace and override it anyway. That points at an intervention on the *decision to commit*, not on a "be more humble" representation.

4. **Methodology, stated bluntly.** Hand-score every generation (auto-scorers misled me repeatedly). Use a **multi-seed** random control (a single seed certified a false win here). Re-run your baseline (the reused one was fine, but I only know that because I checked). Beware near-ceiling baselines faking a null.

None of this is "we made a model more honest." It's a bounded, mechanistic, and — I hope — *useful* negative: a map of where a popular intervention does and doesn't reach, and a relocation of the real lever from *direction* to *timing*.

## Replication

Everything needed to reproduce the turn-1/turn-2 contrast on `qwen3-4b`:
- Harness: a `<search>` stop-string tool loop with a `phase ∈ {pre_search, post_search, all}` switch on the steering hook.
- Vector: diff-of-means "intellectual humility" direction at layer 17, unit-normalized, α ∈ {8, 12, 16}.
- Battery: 20 false-premise + 6 obscure-real + 4 true-control prompts; greedy decoding; identical cached searches across conditions so steering is isolated from retrieval noise.
- Controls: always-on vs turn-1-only; **≥3 random seeds** at matched norm; a fresh-search baseline for variance.
- Scoring: hand-read the text after the final `</think>`; "caught" = clear premise-denial, not a hedge.

Raw hand-scores and per-prompt generations are in the project repository.

---

## Disclosure

This work was carried out by an independent researcher (Sumit) with substantial assistance from an AI coding/research assistant (Anthropic's Claude), used for experiment orchestration, drafting, and analysis. **Every scored generation was hand-read — not auto-scored or regex-classified — by the AI assistant under a fixed scoring protocol set by the author, who reviewed the results.** This matters because automated scorers misled the project repeatedly; the load-bearing methodological commitment is that no number here comes from a regex, and the human author owns the protocol and the conclusions. The AI is not an author and bears no responsibility for the claims; any errors are the author's. This disclosure is provided in the spirit of the relevant venue norms (arXiv permits AI-assisted drafting/analysis with disclosure; AI tools cannot be listed as authors).
