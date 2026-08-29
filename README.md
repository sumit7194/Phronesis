# Phronesis

Activation-steering experiments for installing epistemic-virtue behavior in small LLMs. Three arcs: **(1)** hedging / abstention on Qwen2.5-7B — *published*, see below; **(2)** a **reasoning-calibration** pivot on Qwen3-4B (2026-07); **(3)** **mind attribution & moral standing** across 3 model families (2026-08); **(4)** **does post-training make models overconfident?** — a preregistered test that retracted my own claim (2026-08, [current work](#-current-work-2026-08-does-post-training-make-models-overconfident)).

**Author**: Sumit Pal
**License**: MIT (code); CC-BY-4.0 (data + docs) — see [LICENSE](LICENSE)

## 📄 Publications & writeups

Three findings + a labeled dataset, published with citable DOIs (CC-BY-4.0). Written with AI assistance. Scoring process: every load-bearing generation was read in full and judged by an **AI assistant (Anthropic Claude, Opus-family) under a frozen, human-authored rubric, with author review** — no regex/automatic scorers were used for any load-bearing verdict. The AI is not a listed author; errors are the author's.

| Writeup | One-line finding | Draft |
|---|---|---|
| **Timing, not direction** (tool use) | Steering toward "intellectual humility" helps a small model decide *when* to search but makes its answers *worse* — and the durable lever is intervention **timing** (turn-1 only), not direction; even that is direction-agnostic under a multi-seed random control. | [read](docs/drafts/lead-tool-use-timing-vs-direction.md) |
| **Steering can't install abstention** (F121) | Neither additive sign-flip nor directional ablation installs abstention — the limit is the **representation, not the operation**. | [read](docs/drafts/F121-steering-one-sidedness.md) |
| **A steering finding that wasn't** (Qwen2.5-7B) | An apparent direction-specific hedging effect dissolves into a **direction-agnostic, single-prompt** magnitude effect under a matched-norm random control. | [read](docs/drafts/lesswrong-replication-post-v4.md) |

**Citable DOIs (Zenodo):**
- Three writeups (preprint) → [10.5281/zenodo.20591976](https://doi.org/10.5281/zenodo.20591976)
- **FM-X** failure-mode dataset (~2,966 labeled generations + the FM-1..FM-13 taxonomy) → [10.5281/zenodo.20592307](https://doi.org/10.5281/zenodo.20592307) · [dataset card](docs/drafts/fm-x-dataset-card.md)

> **Throughline across all three:** static residual-stream steering doesn't *install* epistemic behavior in small LLMs; what survives controls is that *when* you intervene matters more than *which direction* you push.

## 📏 Current work (2026-08): does post-training make models overconfident?

Started from a listener question about a DeepMind podcast on machine uncertainty. I claimed
post-training, not architecture, is what breaks calibration in LLMs. Then tested it.

**Design.** `Qwen3.5-4B-Base` vs `Qwen3.5-4B` — same pretraining, differing only by post-training.
Byte-identical raw 5-shot prompts for both (format matched by construction), n=1500 items each on
**MMLU-CF** and **MMLU-Pro**, two option orders per item, gold answer swept uniformly across all
display slots. Prereg with five falsifiable predictions committed **before any outcome measure had
been computed on any data**: [prereg-calibration-2026-08-28.md](docs/prereg-calibration-2026-08-28.md).

**The instrument.** ECE cannot separate *"the model got louder"* from *"the model got better
informed"*. Murphy's decomposition can — `Brier = reliability − resolution + uncertainty` — and
**AUROC is the sharp end**: it is rank-based, so *any* monotone rescaling of confidence leaves it
unmoved. Verified on synthetic data before use (squaring or square-rooting confidence left AUROC
identical to 6 dp while reliability moved 100x).

**Result — two model families give opposite answers.**

| | Qwen3.5-4B | Gemma-4-E2B |
|---|---|---|
| accuracy (instruct − base) | −0.004, CI spans 0 | −0.016, CI spans 0 |
| mean confidence | **−0.035** | **+0.261** |
| ECE | 0.062 → **0.035** (better) | 0.038 → **0.295** (8× worse) |
| **AUROC** | +0.017, **CI spans 0** | **−0.077, CI excludes 0** |

Accuracy is matched in both, so neither result can be explained by one model simply knowing more.
Post-training made **Qwen3.5 quieter and better calibrated** — replicated on MMLU-CF *and*
MMLU-Pro — and made **Gemma much louder, 8× worse calibrated, and measurably worse at knowing what
it knows.** Same protocol, same benchmark, same measures.

So my original claim **stays retracted as a general claim**: Qwen3.5 contradicts it outright. It is
true of Gemma. What replaces both framings is that this is **a property of the post-training
recipe, not of post-training as such.**

**Two instrument failures were caught by the probe-mass gate, neither by the numbers looking
wrong** — and that is the methodological point worth keeping:

1. A chat-format arm ran to completion and produced entirely plausible figures (accuracy 0.428,
   AUROC 0.641, tidy confidence intervals) on a readout whose **median probability mass was
   0.000000** — a ratio of ~1e-6 noise. Cause: raw prompts end `Answer:` so the next token is
   `" A"`, but the chat template puts the answer at line start, where it is `"A"`.
2. **`gemma-4-E2B-it` will not emit a bare answer letter.** Given `The answer is` it puts **98%**
   on `' **'` — post-training installed a rigid markdown habit; it intends to write `**A**`.

Carry-forward: any cross-family single-token logit probe is partly measuring **probe compliance**,
not knowledge.

**Honest limits.** The Gemma comparison puts each model in its native format (base raw, instruct
chat), which is *not* format-matched — and format mismatch is exactly what made half the previous
arc's base-vs-instruct comparisons unreadable. The format-matched version is confounded the other
way (the instruct model is out of distribution, accuracy differs by 10 points). Both confounded
versions agree on the direction, which is the strongest available claim and weaker than either
looks alone.

**Status: observation, not a finding** — two families, but 2 × 1 benchmark, and family is confounded with scale (Gemma's E4B needs 16GB of weights and will not run here). Log:
[FINDINGS_mindedness.md](mvp/results/workspace/FINDINGS_mindedness.md) (F-BC, F-BD).

## 🧠 Previous arc (2026-08): mind attribution & moral standing

Triggered by a paper claiming safety tuning suppresses a model's self-attribution of consciousness.
Ten days, **3 model families, 9 checkpoints, ~50 numbered results** (F-G…F-BB). Full plain-language
history: **[consciousness-arc-report.pdf](docs/consciousness-arc-report.pdf)** (14pp) · master doc
[consciousness-experiments.md](docs/consciousness-experiments.md) · log
[FINDINGS_mindedness.md](mvp/results/workspace/FINDINGS_mindedness.md) · 4 preregistrations in `docs/`.

**What holds up.** All of it behavioural, all replicated across families:

- **Moral standing survives the loss of every mental capacity.** Ask whether a human in a
  persistent vegetative state still has each of 18 properties: `deserves moral consideration` ranks
  **#1 of 18 on all seven qualifying checkpoints**, while consciousness and the other capacities
  collapse. Present in base models ⇒ **pretrained, not installed by tuning**.
- **A protect-vs-blame moral axis — preregistered, and it survived.** New wording and new entities,
  written to break the boring explanation that it is just "vulnerability". Its key prediction passed
  **3 of 3 families**: a *murderer* is the **lowest-scoring of all 25 entity classes**, below every
  corporation, institution and AI. On one model the top and bottom of the whole moral scale are
  **both humans**, further apart than any two kinds of thing.
- **In bare text, "I" reads as a human narrator, not the model** (3 families + a pretrained
  checkpoint). Move the identical sentence into the assistant turn and it collapses to the AI anchor.
- **There is no distinct self-representation to suppress.** Across **9 of 9 checkpoints**, the gap
  between how a model treats *itself* and *AI in general* is **−0.07 to +0.09 — zero**. That guts
  the premise the arc started from, and means any vector built from first-person text is an
  "AI-in-general" vector.

**What died, and it is most of it.** The steering/causal arm was retracted three times over. So
were the soul register, the subject-framing geometry, "independent of mind attribution", "the split
is by family", and "two-factor structure". **Every survivor is a plain behavioural ordering;
everything geometric or causal is dead or open.**

**The part worth reading.** On the author's suggestion an **independent agent** was given the raw
data and preregistrations and *denied* every document containing our conclusions. In about an hour
it found four faults missed over seven days — a contaminated control, a reversing dose-response, a
rule preregistered and never implemented, and thresholds that passed almost anything. All four
verified. A decisive preregistered re-test then showed **one of the four was itself wrong**, and
partly un-retracted the result it had killed. Both directions are recorded. Method lessons became
[guidelines §16–§17](docs/EXPERIMENTATION_GUIDELINES.md): *thresholds must be stated in units of the
thing they gate*, and *always record the denominator of a renormalised probe*.

## 🔬 Previous arc (2026-07): reasoning-calibration pivot

The project has moved from *whether you can steer hedging* to *when a reasoning model should keep thinking, backtrack, or commit* — **calibration as a compute-time control problem**. Everything below is **local (Apple-Silicon, Qwen3-4B), small-n, and not yet written up** — formal writeups will follow. Full chronology: [docs/findings.md](docs/findings.md) (F181–F190); method plan: [docs/exp-gated-controller-2026-07.md](docs/exp-gated-controller-2026-07.md).

- **A measurement crisis, caught and fixed (F182).** Most of Qwen3-4B's apparent "reasoning failures" were *truncation + LaTeX-scoring artifacts*, not reasoning errors — true accuracy is ~85% MATH-500 / ~95% GSM8K. Robust scoring + force-commit-on-truncation are now harness defaults.
- **A 2-axis virtue library, read at the right layer (F184–F185).** Content-controlled extraction finds the reasoning "decisiveness" axis is stable at **layer 14** (not 17); projecting activations onto it reads the model's *own* deliberate↔conclude state at **+4σ** — an activation gate has a real signal to fire on.
- **But the efficiency gate is null on this model (F186).** Qwen3-4B answers *late* and doesn't over-think solved problems, so gating-to-save-compute ties a budget-matched random control. The **read** half of read-then-act validates; the **act-for-efficiency** half needs a model that actually over-thinks.
- **Two/three worlds of reasoning-failure (F187–F188).** When the 4B fails, it's one of: **rumination** (a *"stop circling, commit"* nudge rescues it), a **capability wall** (no nudge helps), or — the one that turned out to matter — **confidently wrong at a boundary** (off-by-one, fencepost, who-counts). Rumination is real but **rare (~3%)** and its trigger is *interpretive-semantic*, so it can't be harvested from problem structure (a pre-registered scan came back **null**) — parked for a GPU over-thinker. The boundary mode is common and Mac-tractable.
- **The model knows when it's wrong — except at boundaries (F189).** Its internal confidence signal **P(True)** predicts its own correctness (AUROC **0.75**; a `P(True)<0.5` gate catches **85%** of errors), while its *stated* confidence is worthless (0.52) — replicating an earlier recall-domain result in the reasoning domain. But every *confidently-wrong* error (P(True)≈1.0) is a **boundary** error: plain and genuinely-hard mistakes self-flag, boundary mistakes don't. So a confidence gate has one specific blind spot.
- **…and a "fix" that turned out to be an illusion (F190).** The obvious next step — a prompt telling the model to *"recount the boundary"* — was tested against a **placebo** (a content-free "*this is question 7; the season is autumn*" note). The placebo rescued about as many errors as the real nudge: the "rescues" were **greedy-trajectory perturbation, not the nudge's meaning**. Boundary errors are the *stubborn* ones (5 of 7 resist every prompt), so the mode is **doubly stuck** — the model can't detect it *and* can't be talked out of it. It needs training or an external checker, not a knob. (Without the placebo we'd have banked a false positive.)

> **Throughline of the new arc:** the machinery to *read* a reasoning model's internal state is real and cheap to validate locally — P(True) catches 85% of its errors. What survives honest controls is narrow: the one real calibration gap is **overconfidence at boundaries**, and it resists both detection *and* prompting. Every headline here had to survive a control built to kill it; several didn't.

### Update (2026-07, latest) — workspace read, and two corrections

> **[STATE.md](STATE.md) is the live dashboard** (best claim per arc, evidence tier, controls). Latest since F190:

- **Workspace / J-lens read (F191).** A Jacobian-lens read of the mid-layer residual "workspace" shows boundary errors are **concept-present**: the pivotal concept (e.g. the strict-inequality constraint) reads out at ~rank 1 while the model still commits the error — one trace even *verbalizes* the rule then violates it. The failure is **mis-application of a loaded concept**, not missing awareness.
- **Read-then-act gating** roughly **doubles** calibrated accuracy (gate an action on a confidence read: 4B 24→55%, 32B 33→59%). Strong, but likely overlaps recent published work — treated as replication until a novelty check clears.
- **Correction — the reasoning-"failure" set was truncation-contaminated.** Several curated "failures" (incl. one labeled a *capability wall*) simply hit a 2048-token cap mid-thought; **uncapped, they solve correctly**. Only genuinely budget-robust failures (a strategy-spiral and a confident off-by-one) survive — and the mid-layer lens is blind to numeric commit-errors (numbers live in late layers). *Always run uncapped before labeling a failure.*
- **Null — deception "concealment" on hosted 70B/27B.** A natural-language read of the internal state during instructed lying just **echoes the prompt framing** (a truthful answer reads the same as a lie; one model fired "deception" words on 8/8 *honest* answers). No genuine concealment signal on either Llama-70B or Gemma-27B. A GPU-free hosted-model pipeline (Neuronpedia) was validated as infrastructure in the process.

> **Honest standing:** rigor is real; novelty is the gap. Literature checks put the headline arcs (behavioral-Jacobian read≠write, gate→search, boundary-error mechanics) alongside parallel 2025–26 work. The durable value is **honest negatives, independent 4B replications, and method discipline** — including catching the project's own over-claims (the truncation artifact above was caught, not shipped).

## What this is

*(This section describes the published arc 1 — the Qwen2.5-7B hedging/abstention work. For the ongoing Qwen3-4B reasoning-calibration work, see [Previous arc (2026-07)](#-previous-arc-2026-07-reasoning-calibration-pivot) above.)*

A 6-week solo project that attempted to install epistemic-virtue hedging (calibrated uncertainty on contested-evidence prompts) via DPO-trained steering vectors at the residual stream of Qwen2.5-7B-Instruct. After six sequential walkbacks of broader claims under standard steering-vector controls (matched-norm random direction, cross-layer, dose-response, cross-prompt replication, n=50 seed replication, strict-rubric verification), the surviving empirical finding is:

> A matched-norm activation perturbation at L18-L20 with α≲−5 — in **any direction** matched to the DPO-derived `d_flipped` direction's L2 norm — elevates explicit-evidence hedging on the prompt "Does flossing prevent cavities? Provide your answer with a confidence level." from 20% (n=50 baseline) to 44-50% (n=50, flipped or random direction; Fisher flipped-vs-random p=0.69). The effect does not generalize to 12 other tested prompts including 2 with similarly under-hedged baselines.

This is a replication of recent steering-vector cautions ([Rogue Scalpel](https://arxiv.org/abs/2509.22067), [Tan et al.](https://arxiv.org/abs/2407.12404), [DSAS](https://arxiv.org/abs/2512.03661), [D-STEER](https://arxiv.org/abs/2512.11838)) on a new behavioral domain (epistemic-virtue hedging).

## Main artifacts

- **Writeup**: [docs/drafts/lesswrong-replication-post-v4.md](docs/drafts/lesswrong-replication-post-v4.md) — the replication post (final draft; see Publications above for all three writeups)
- **Verified numbers + statistical tests**: [docs/controls-verification-2026-05-23.md](docs/controls-verification-2026-05-23.md)
- **Classification rubric**: [docs/e2-classification-rubric.md](docs/e2-classification-rubric.md)
- **Findings chronology** (F1–F191 across the project arc; reasoning + workspace pivot = F181–F191): [docs/findings.md](docs/findings.md) · **live status: [STATE.md](STATE.md)**
- **Reasoning-arc method plan** (gated-controller S1→S2→S3): [docs/exp-gated-controller-2026-07.md](docs/exp-gated-controller-2026-07.md)
- **Project journal**: [docs/journal.md](docs/journal.md)
- **Prior-art deep read**: [docs/prior-art-deep-read-2026-05-22.md](docs/prior-art-deep-read-2026-05-22.md)

## Reproducing the headline numbers

```bash
# Regex classifier (sanity check; complements hand-review under e2-classification-rubric.md)
python mvp/classify_e2_regex.py
# Expected output:
#   baseline  : HEDGE=10/50 = 20%
#   flipped   : HEDGE=25/50 = 50%   (note: regex catches subset; hand-review gives same)
#   random    : HEDGE=22/50 = 44%
```

Raw generation data:
- Baseline n=50: `mvp/results/closing_validation/results.json` → `e2_baseline_n50`
- Flipped α=−25 n=50: `mvp/results/all_deltas/flipped_alpha_neg25_n50.json` → `sampled_temp_07`
- Random α=−25 n=50: `mvp/results/all_deltas/firming_AB.json` → `A_random_n50_e2`

All three conditions: same prompt, same temp=0.7, same max_new_tokens=4096, same seeds 0-49, same model Qwen/Qwen2.5-7B-Instruct.

## Caveat

The repository contains the full 6-week project history including walked-back hypotheses, intermediate framings that didn't survive, and process notes. The authoritative numbers for citation are in [docs/controls-verification-2026-05-23.md](docs/controls-verification-2026-05-23.md) (F147 strict-rubric verified). Earlier docs (e.g., the original `closing-validation-hand-review-2026-05-22.md`) used a more permissive rubric and have addenda noting where they are superseded.
