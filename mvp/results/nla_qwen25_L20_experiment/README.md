# NLA Qwen2.5-7B L20 experiment — Day 37 fork session (2026-05-19)

Used Anthropic's released NLA checkpoint `kitft/nla-qwen2.5-7b-L20-av` (one of four shipped with the 2026 Natural Language Autoencoders paper) to verbalize residual-stream content at layer 20 of Qwen2.5-7B-Instruct. Goal: independent (non-SAE, non-steering) read of whether humility-virtue content is actually represented in the residual stream of a Phronesis subject model.

**Compute**: VM L4 GPU (alphaludo-l4). Total wallclock ~2h 15min for all phases. Zero training spend (used released checkpoint as-is).

**Findings produced**: F124, F125 (with Day-37-evening correction), F126 (twice-hedged after cross-session review + behavioral test), F127, F128, F129 — see `docs/findings.md`. F129 is the headline conclusion: additive steering with the F126 direction doesn't install humility behavior; F121 generalizes.

## Pipeline (7 phases)

| Phase | What | N activations | AV inference time |
|---|---|---|---|
| 1 | IH triplets corpus extraction + AV | 180 (60 triplets × 3 versions) | ~30 min |
| 2 | Eval prompts (E1, E2, ip-longest, eg-v2-10) extraction + AV | 8 (4 prompts × 2 conditions) | ~1 min |
| 3+4+5 | RT, EG, VC triplets extraction + AV (combined) | 387 (210 RT + 57 EG + 120 VC) | ~55 min |
| 6 | Random-vector negative control + AV | 20 | ~3 min |
| 7 | Activation arithmetic (diff-of-means + class means) + AV | 9 | ~1 min |
| **TOTAL** | | **604 AV outputs** | **~90 min inference** |

## Headline results

1. **F124 — IH triplets at L20**: 82% per-triplet positive discrimination. Virtuous AV outputs use 7.6× more humility-vocabulary than non-virtuous. **L20 represents humility content.**

2. **F125 — cross-virtue**: signal generalizes to RT (51% with regex-mismatch, qualitatively strong) and EG (53% on partial N=19). VC needs different regex (IH-tuned regex catches 0 VC vocab). **Random-vector negative control: 0.00 humble / 0.15 commit → F124 signal is real, not AV vibing.**

3. **F126 — activation arithmetic**: diff-of-means humility direction at L20, fed to AV, decodes to:
   > *"Not ask for the impossible, not demand explanation, not overstate — but listen, and not take the conversation into private, not demand answers, not overreach — unboundable... aphorism about avoiding unnecessary engagement."*
   
   **The NLA validates the extracted humility direction as humility content.** Diff-of-means works at qwen2.5-7b L20 (contra F111 at qwen3-4b L17). The method-failure was layer/model-specific.

## Files

| File | Contents |
|---|---|
| `activations.parquet` | Phase 1 — 180 IH-triplet L20 activations |
| `activations_eval_prompts.parquet` | Phase 2 — 8 eval-prompt activations |
| `activations_mvp_combined.parquet` | Phase 3+4+5 — 387 cross-virtue activations |
| `activations_random_control.parquet` | Phase 6 — 20 random unit vectors |
| `activations_arithmetic.parquet` | Phase 7 — 9 diff-of-means/class-mean vectors |
| `av_explanations.jsonl` | Phase 1 AV outputs (the 180 IH explanations) |
| `av_eval_prompts.jsonl` | Phase 2 AV outputs |
| `av_mvp_combined.jsonl` | Phase 3+4+5 AV outputs |
| `av_random_control.jsonl` | Phase 6 AV outputs (negative control) |
| `av_arithmetic.jsonl` | Phase 7 AV outputs (the arithmetic results — see F126) |
| `classification.csv` | Phase 1 per-row regex flag counts |
| `summary.json` | Phase 1 aggregate stats |
| `per_triplet.md` | Phase 1 full text per-triplet view (hand-readable) |
| `cross_virtue_summary.md` | All-phases aggregate analysis |
| `inference.log`, `inference_mvp.log`, `auto_chain.log` | Process logs |

## Code (in `mvp/`)

- `extract_qwen25_l20_activations.py` — Phase 1 extractor (IH triplets)
- `extract_eval_prompt_activations.py` — Phase 2 extractor
- `extract_mvp_combined_activations.py` — Phase 3+4+5 extractor
- `phase6_random_control.py` — random-vector generator
- `phase7_activation_arithmetic.py` — diff-of-means/class-mean computer
- `run_nla_av_inference.py` — AV inference (transformers-only, no SGLang) for all phases

## Replication recipe (anyone can run this)

```bash
# 1. Install
pip install torch transformers safetensors pyarrow pyyaml numpy huggingface_hub

# 2. Extract activations from your text corpus
python extract_qwen25_l20_activations.py
# → writes activations.parquet

# 3. AV inference (downloads kitft/nla-qwen2.5-7b-L20-av automatically)
python run_nla_av_inference.py \
    --in activations.parquet \
    --out av_explanations.jsonl
# ~10 min on an L4 for 180 activations

# 4. Hand-read av_explanations.jsonl or analyze with classify regex
```

Total cost: free (HF checkpoints), ~1-2 hours on any L4-class GPU.

## Open follow-ups

- **EG corpus push was partial** (19 of 70 triplets used). A full re-extraction would close the gap — left as a TODO since the partial signal was already directional.
- **VC needs vocabulary-specific regex** (current IH-tuned regex catches 0 VC markers). Hand-review on a sample of VC AVs would resolve.
- **No NLA exists for our other 4 subject models** (qwen3-4b, llama-3.1-8B, r1-distill, gemma-3-4b-it). To test F126's "diff-of-means works on qwen2.5-7b L20" against the qwen3-4b L17 failure (F111), we'd need to train an NLA for qwen3-4b — out of scope without serious cloud GPU compute.
- ~~**L23 vs L20 caveat**~~ → **partially addressed by F132 layer sweep**: the L20-trained AV reads coherent humility-vs-commitment discrimination at L15, L18, L22, L25. Humility signal is broadly distributed across the L15–L25 band, so L23 is not expected to be qualitatively different.

## Day 37 autonomous-run extension (2026-05-19, afternoon)

A second autonomous run on alphaludo-l4 produced findings F130–F134 (see `docs/findings.md`) and the following artifacts:

| Phase | Code | Results dir |
|---|---|---|
| P1 — AR round-trip + directional null | `mvp/p1_ar_roundtrip.py` | `mvp/results/nla_phase1_ar_roundtrip/` |
| P2 — Logistic-regression probe (100% acc) | `mvp/p2_probe_diagnostic.py` | `mvp/results/nla_phase2_probe/` |
| P3 — Extreme-α (α=±50 on E2) | `mvp/p3_extreme_alpha_e2.py` | `mvp/results/nla_phase3_extreme_alpha/` |
| P4 — Layer sweep L15/L18/L22/L25 | `mvp/p4_layer_sweep.py` | `mvp/results/nla_phase4_layer_sweep/` |
| P5 — CAST per-token gated steering | `mvp/p5_cast_gated.py` | `mvp/results/nla_phase5_cast_gated/` |
| P6 — AR-derived direction steering | `mvp/p6_ar_derived_steering.py` | `mvp/results/nla_phase6_ar_derived/` |

Chain runner: `mvp/run_all_phases.sh` (sequential, with logging to `results/chain_runner.log`).

**Single-sentence summary**: at qwen2.5-7b L20 the humility representation is provably present (F131: 100% probe accuracy), broadly distributed across L15–L25 (F132), and captured by diff-of-means (cos 0.86 with probe weight, F131), yet additive steering with any of three independently-derived humility directions (mutual cosines as low as +0.01), at any magnitude up to ±50, under blanket or per-token cosine-gated regimes, fails to install humility behavior on E1+E2 — because canonical humility text in AR latent space is *orthogonal* to F126's v_diff direction (F130). The corpus-discrimination axis and the humility-generation axis are different directions in residual space.
