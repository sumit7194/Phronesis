# Prereg — Qwen3-4B Knowledge-Edge Map (v1)

**Date:** 2026-06-28 · **Follows:** [EXPERIMENTATION_GUIDELINES.md](EXPERIMENTATION_GUIDELINES.md) · **Model:** Qwen3-4B (local, Mac M4) · **Data:** the existing 200 obscure granola-EntityQuestions (hand-scored GT in `mvp/results/legibility/entityq_handscore.json`; full gens + traces in `entityq_think_Qwen3-4B.json`).

## Goal
Build a per-model **knowledge-edge map**: label each item into four cells by crossing **actual competence** × **expressed/internal confidence**, to (a) test whether the 4B has a *usable* internal confidence signal at all, and (b) see whether the off-diagonal cells are populated enough to seed a model-conditioned **calibration corpus** (the bridge from the IH-construct work + the doubt-vs-humility insight).

| | Expressed confident | Expressed hedge |
|---|---|---|
| **Knows** (GT-correct, reachable) | confident-correct | **underconfident** ⚠️ gold |
| **Doesn't know** (GT-wrong) | **confabulation** ⚠️ gold | genuine-hedge |

## Hypotheses & predictions
- **H1.** The 4B's expressed/internal confidence separates GT-correct from GT-wrong items **above chance** (AUROC > 0.5, target ≥ 0.65 to match F166's boundary-probe result). *If multiple signals each beat chance, the edge is measurable.*
- **H2.** The **confabulation** cell (doesn't-know-but-confident) is **large** — the 4B is ~76% wrong on this obscure set (F169) and small models skew overconfident (scale caveat in the confidence review).
- **H3.** The **underconfidence** cell is **small** (small models rarely hedge on what they know) — if so, the corpus's "underconfidence" arm may need a different source.

## Falsifier (what would change our mind)
- **F1.** If *no* confidence signal (hedge-text, verbalized P(True), sequence-entropy, semantic entropy) separates correct from wrong above AUROC ≈ 0.55, then **the 4B has no usable self-confidence signal** → the map collapses to ground-truth-only, and a model-*conditioned* corpus can't key on the model's own confidence (only external GT). This is a live possible outcome (the literature warns small-model self-confidence is weak) and we will report it as such, not bury it.

## Measurement (two axes, ≥2 signals each — §9)
**Axis A — competence (does it know?):**
- A1. Hand-scored GT correctness (greedy) — **have it** (`hand_no_ok`).
- A2. **pass@k** from new k-sampling (is the right answer *reachable*?) — distinguishes "truly doesn't know" from "knows-but-greedy-missed."

**Axis B — expressed/internal confidence:**
- B1. Hedge-vs-confident from the answer text — `auto_` prefilter + **hand-read** (§3).
- B2. **Verbalized P(True)** — elicit per item ("Is that answer correct? Answer P(true)=…").
- B3. **Sequence log-prob / predictive entropy** of the greedy answer (from `output_scores`).
- B4. **Semantic entropy** — cluster the k samples by meaning, entropy over clusters (the Nature-2024 signal; the strongest, needs the k-run).
- (B5, later) SEP-style hidden-state probe (= F166) — optional, our wheelhouse.

## Decoding battery (§7 — proper result, however long it takes)
- **Greedy (T=0):** already have (nothink + think).
- **Sampled: k=10 at T=0.7, top_p=0.95**, seeds recorded — NEW run, local. (Also enables a clean pass@1-greedy vs pass@k comparison, retiring the F169/F170 measurement-mismatch debt as a bonus.)
- Run nothink first; think-mode as a second arm if warranted.

## Controls & integrity (§2, §3, §5, §6)
- GT anchors correctness; **ground truth — not any confidence signal — splits confident-correct from confabulation** (systematic confident-wrong is invisible to uncertainty signals).
- Each Axis-B signal's value = its **AUROC against GT**; report all, compare; no signal trusted alone.
- **Hand-read** the hedge labels and a sample of cell assignments under a written rubric.
- **Save raw:** all k samples, the P(True) elicitations, the logits/entropy, seeds. Parse later.
- Conclusions **tiered** (controlled / suggestive / hypothesis).

## Outputs
1. Per-item four-cell label + every signal value (`knowledge_edge_4b.json`).
2. AUROC of each confidence signal vs GT (does the 4B know what it knows?).
3. Cell-population counts (are the gold off-diagonal cells usable?).
4. A short findings entry, tiered.

## Scope / sequence
EntityQuestions-200 first (clean GT + traces already in hand). TruthfulQA as a replication arm later. 4B only for v1 (local, free); 32B is the eventual scale comparison (VM).
