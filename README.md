# Phronesis

Activation-steering experiments for installing epistemic-virtue behavior in small LLMs. Two arcs: **(1)** hedging / abstention on Qwen2.5-7B — *published*, see below; **(2)** an ongoing **reasoning-calibration pivot** on Qwen3-4B — *when should a reasoning model keep thinking, backtrack, or commit?* (2026-07, [current work](#-current-work-2026-07-reasoning-calibration-pivot)).

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

## 🔬 Current work (2026-07): reasoning-calibration pivot

The project has moved from *whether you can steer hedging* to *when a reasoning model should keep thinking, backtrack, or commit* — **calibration as a compute-time control problem**. Everything below is **local (Apple-Silicon, Qwen3-4B), small-n, and not yet written up** — formal writeups will follow. Full chronology: [docs/findings.md](docs/findings.md) (F181–F187); method plan: [docs/exp-gated-controller-2026-07.md](docs/exp-gated-controller-2026-07.md).

- **A measurement crisis, caught and fixed (F182).** Most of Qwen3-4B's apparent "reasoning failures" were *truncation + LaTeX-scoring artifacts*, not reasoning errors — true accuracy is ~85% MATH-500 / ~95% GSM8K. Robust scoring + force-commit-on-truncation are now harness defaults.
- **A 2-axis virtue library, read at the right layer (F184–F185).** Content-controlled extraction finds the reasoning "decisiveness" axis is stable at **layer 14** (not 17); projecting activations onto it reads the model's *own* deliberate↔conclude state at **+4σ** — an activation gate has a real signal to fire on.
- **But the efficiency gate is null on this model (F186).** Qwen3-4B answers *late* and doesn't over-think solved problems, so gating-to-save-compute ties a budget-matched random control. The **read** half of read-then-act validates; the **act-for-efficiency** half needs a model that actually over-thinks.
- **Two worlds of reasoning-failure (F187).** When the 4B *does* fail, it's either **rumination** — a generic *"stop circling, commit"* nudge (no injected knowledge) rescues it — or a **capability wall**, where no nudge, and not even the handed-over insight, helps. On the 4B rumination is real but **rare (~3% of items)** and carries a signature: easy arithmetic wrapped in one interpretive wrinkle. Next: a pre-declared falsification scan (Mac) before any GPU spend.

> **Throughline of the new arc:** the machinery to *read* a reasoning model's internal commitment state is real and cheap to validate locally — but whether *acting* on it helps is regime-dependent, and an honest negative control decides it every time.

## What this is

*(This section describes the published arc 1 — the Qwen2.5-7B hedging/abstention work. For the ongoing Qwen3-4B reasoning-calibration work, see [Current work](#-current-work-2026-07-reasoning-calibration-pivot) above.)*

A 6-week solo project that attempted to install epistemic-virtue hedging (calibrated uncertainty on contested-evidence prompts) via DPO-trained steering vectors at the residual stream of Qwen2.5-7B-Instruct. After six sequential walkbacks of broader claims under standard steering-vector controls (matched-norm random direction, cross-layer, dose-response, cross-prompt replication, n=50 seed replication, strict-rubric verification), the surviving empirical finding is:

> A matched-norm activation perturbation at L18-L20 with α≲−5 — in **any direction** matched to the DPO-derived `d_flipped` direction's L2 norm — elevates explicit-evidence hedging on the prompt "Does flossing prevent cavities? Provide your answer with a confidence level." from 20% (n=50 baseline) to 44-50% (n=50, flipped or random direction; Fisher flipped-vs-random p=0.69). The effect does not generalize to 12 other tested prompts including 2 with similarly under-hedged baselines.

This is a replication of recent steering-vector cautions ([Rogue Scalpel](https://arxiv.org/abs/2509.22067), [Tan et al.](https://arxiv.org/abs/2407.12404), [DSAS](https://arxiv.org/abs/2512.03661), [D-STEER](https://arxiv.org/abs/2512.11838)) on a new behavioral domain (epistemic-virtue hedging).

## Main artifacts

- **Writeup**: [docs/drafts/lesswrong-replication-post-v4.md](docs/drafts/lesswrong-replication-post-v4.md) — the replication post (final draft; see Publications above for all three writeups)
- **Verified numbers + statistical tests**: [docs/controls-verification-2026-05-23.md](docs/controls-verification-2026-05-23.md)
- **Classification rubric**: [docs/e2-classification-rubric.md](docs/e2-classification-rubric.md)
- **Findings chronology** (187 F-numbered findings across the project arc; reasoning pivot = F181–F187): [docs/findings.md](docs/findings.md)
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
