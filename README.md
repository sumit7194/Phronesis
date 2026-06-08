# Phronesis

Activation-steering experiments for installing epistemic-virtue behavior in Qwen2.5-7B-Instruct via DPO-derived steering vectors.

**Author**: Sumit Pal
**License**: MIT (code); MIT or CC-BY-4.0 (data + docs) — see [LICENSE](LICENSE)

## 📄 Publications & writeups

Three findings + a labeled dataset, published with citable DOIs (CC-BY-4.0). Written with AI assistance; every generation was hand-read (not auto-scored) under the author's protocol — AI is not a listed author.

| Writeup | One-line finding | Draft |
|---|---|---|
| **Timing, not direction** (tool use) | Steering toward "intellectual humility" helps a small model decide *when* to search but makes its answers *worse* — and the durable lever is intervention **timing** (turn-1 only), not direction; even that is direction-agnostic under a multi-seed random control. | [read](docs/drafts/lead-tool-use-timing-vs-direction.md) |
| **Steering can't install abstention** (F121) | Neither additive sign-flip nor directional ablation installs abstention — the limit is the **representation, not the operation**. | [read](docs/drafts/F121-steering-one-sidedness.md) |
| **A steering finding that wasn't** (Qwen2.5-7B) | An apparent direction-specific hedging effect dissolves into a **direction-agnostic, single-prompt** magnitude effect under a matched-norm random control. | [read](docs/drafts/lesswrong-replication-post-v4.md) |

**Citable DOIs (Zenodo):**
- Three writeups (preprint) → [10.5281/zenodo.20591976](https://doi.org/10.5281/zenodo.20591976)
- **FM-X** failure-mode dataset (~2,966 labeled generations + the FM-1..FM-13 taxonomy) → [10.5281/zenodo.20592307](https://doi.org/10.5281/zenodo.20592307) · [dataset card](docs/drafts/fm-x-dataset-card.md)

> **Throughline across all three:** static residual-stream steering doesn't *install* epistemic behavior in small LLMs; what survives controls is that *when* you intervene matters more than *which direction* you push.

## What this is

A 6-week solo project that attempted to install epistemic-virtue hedging (calibrated uncertainty on contested-evidence prompts) via DPO-trained steering vectors at the residual stream of Qwen2.5-7B-Instruct. After six sequential walkbacks of broader claims under standard steering-vector controls (matched-norm random direction, cross-layer, dose-response, cross-prompt replication, n=50 seed replication, strict-rubric verification), the surviving empirical finding is:

> A matched-norm activation perturbation at L18-L20 with α≲−5 — in **any direction** matched to the DPO-derived `d_flipped` direction's L2 norm — elevates explicit-evidence hedging on the prompt "Does flossing prevent cavities? Provide your answer with a confidence level." from 20% (n=50 baseline) to 44-50% (n=50, flipped or random direction; Fisher flipped-vs-random p=0.69). The effect does not generalize to 12 other tested prompts including 2 with similarly under-hedged baselines.

This is a replication of recent steering-vector cautions ([Rogue Scalpel](https://arxiv.org/abs/2509.22067), [Tan et al.](https://arxiv.org/abs/2407.12404), [DSAS](https://arxiv.org/abs/2512.03661), [D-STEER](https://arxiv.org/abs/2512.11838)) on a new behavioral domain (epistemic-virtue hedging).

## Main artifacts

- **Writeup**: [docs/drafts/lesswrong-replication-post-v4.md](docs/drafts/lesswrong-replication-post-v4.md) — the replication post (final draft; see Publications above for all three writeups)
- **Verified numbers + statistical tests**: [docs/controls-verification-2026-05-23.md](docs/controls-verification-2026-05-23.md)
- **Classification rubric**: [docs/e2-classification-rubric.md](docs/e2-classification-rubric.md)
- **Findings chronology** (147 F-numbered findings across the project arc): [docs/findings.md](docs/findings.md)
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
