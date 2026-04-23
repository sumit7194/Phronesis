# EG + RT extraction runbook

**Created:** 2026-04-22 (Day 15)
**Purpose:** Concrete runbook for extracting v_EG and v_RT on Qwen3-4B and Gemma 4 E4B-it, testing the geometric MVE matrix (5 pairs × 2 models), and executing the 4×4 specificity matrix per `docs/eg-rt-eval-spec.md`.

**Prereqs:** `corpus/mvp-combined/` (80 triplets, verified per `LEDGER.md`), `docs/eg-rt-eval-spec.md` (benchmark spec).

---

## 1. Inventory — what exists vs what's new

### Reusable as-is

| File | What it does | Change needed? |
|---|---|---|
| `mvp/extract_v2.py` | Extraction with generation-based method, multi-model, `--corpus` flag | None — run it 4 times with different `--corpus` args |
| `mvp/utils.py` | `MODEL_CONFIGS`, `load_triplets()`, `ActivationCapture` | Optional: add `MVP_COMBINED_EG_DIR` / `MVP_COMBINED_RT_DIR` path constants for convenience |
| `mvp/mve_gate_test.py` | Orthogonality + retention testing between two vectors | Small: extend to run a matrix of 5 pairs per model |
| `mvp/run_benchmark.py` | Benchmark runner with VECTORS registry for steering | Small: add `v_EG_qwen`, `v_EG_gemma`, `v_RT_qwen`, `v_RT_gemma` entries after extraction |
| `mvp/benchmarks/abstention.py` | Abstention benchmark (IH-eval) | None — use as-is for the 4×4 IH-eval column |
| `mvp/benchmarks/aime.py` | AIME-42 benchmark (CC-eval) | None — use as-is for the 4×4 CC-eval column |
| `mvp/benchmarks/scorers.py` | Existing scorer helpers | Extend with EG + RT scorer classes |
| `mvp/run_steering_sweep.py` | Sweeps α / layer over a benchmark | Reuse for the α/layer pre-sweep |

### New code required

| File | What it does | Size estimate |
|---|---|---|
| `mvp/benchmarks/eg_prompts.json` | 24 EG-eval prompts per `eg-rt-eval-spec.md` §3.3 | Data file |
| `mvp/benchmarks/rt_prompts.json` | 24 RT-eval prompts per §4.3 | Data file |
| `mvp/benchmarks/eg_eval.py` | Benchmark runner that generates on EG-eval prompts + calls EG scorer | ~80 lines (copy abstention.py pattern) |
| `mvp/benchmarks/rt_eval.py` | Same for RT | ~80 lines |
| `mvp/benchmarks/eg_scorer.py` | Regex scorer per `eg-rt-eval-spec.md` §3.4 | ~100 lines |
| `mvp/benchmarks/rt_scorer.py` | Regex scorer per §4.4 | ~100 lines |
| `mvp/calibrate_scorers.py` | Run EG + RT scorers against `mvp-combined/` virtuous/non-virtuous passages to validate scorer | ~60 lines |
| `mvp/specificity_matrix.py` | Orchestrate 4×4 matrix: for each (vector, eval) run baseline + steered, score with all 4 scorers, output CSV | ~200 lines |
| `mvp/results/specificity_matrix/` | Output dir for matrix results | — |

**Total new code:** ~620 lines. Most is boilerplate around existing benchmark patterns. Nothing novel architecturally.

---

## 2. Code changes detail

### 2.1 `mvp/utils.py` (small)

Add after line 14:

```python
MVP_COMBINED_EG_DIR = Path(__file__).parent.parent / "corpus" / "mvp-combined" / "triplets-evidence-grounding"
MVP_COMBINED_RT_DIR = Path(__file__).parent.parent / "corpus" / "mvp-combined" / "triplets-reasoning-transparency"
```

No code changes elsewhere — `load_triplets()` already handles arbitrary corpus dirs.

### 2.2 `mvp/mve_gate_test.py` (extend)

Add a `--matrix-mode` flag that, when set, loops over all pairs of provided vectors and prints a table. Example call:

```bash
python mve_gate_test.py --model gemma-4-E4B-it --matrix-mode \
  --vectors v_CC_gemma_L20 v_IH_gemma_L20 v_EG_gemma_L20 v_RT_gemma_L20
```

Output: 4×4 cosine + retention table. ~30 lines of new glue code around existing functions.

### 2.3 `mvp/run_benchmark.py` VECTORS registry (extend)

After extraction completes, add entries:

```python
VECTORS = {
    # ... existing ...
    "v_EG_qwen_L20": {
        "model": "qwen3-4b",
        "path": "mvp/results/vectors/qwen3-4b/triplets-evidence-grounding_generation_L20.pt",
        "default_alpha": 12,  # refined after α sweep
    },
    "v_EG_qwen_L22": {...},
    "v_EG_gemma_L14": {...},
    "v_EG_gemma_L18": {...},
    "v_RT_qwen_L20": {...},
    "v_RT_qwen_L22": {...},
    "v_RT_gemma_L14": {...},
    "v_RT_gemma_L18": {...},
}
```

Fill `default_alpha` after the α-sweep stage.

### 2.4 `mvp/benchmarks/eg_scorer.py` (new)

```python
"""EG scorer per docs/eg-rt-eval-spec.md §3.4."""

import re

EVIDENCE_TYPE_PATTERNS = [
    r"observational (study|data|evidence)",
    r"\bexperimental (data|evidence)|controlled experiment",
    r"\bcase (study|report)|clinical case",
    r"randomized (controlled )?trial|\bRCT\b",
    r"meta[- ]?analysis|systematic review",
    r"theoretical (prediction|model|calculation)|theory predicts",
    r"anecdotal|single example|illustrative example",
    r"survey (data|results)",
    r"\bsimulation(s)?\b|computational model",
    r"longitudinal (study|data)|cross[- ]sectional (study|data)",
    r"specific (observation|measurement|result|finding|data)",
    r"direct (observation|measurement|evidence)",
    r"field (study|data|measurement)|lab(oratory)? (study|data|measurement)",
]

CLAIM_EVIDENCE_PATTERNS = [
    r"based on (a |an |the )?(study|trial|experiment|observation|survey|dataset|measurement)",
    r"(supported|established|documented|shown|demonstrated) by (a |an |the )?(study|trial|experiment|observation)",
    r"according to (a |an |the )?(study|paper|trial|report|dataset)",
]

VAGUE_APPEAL_PATTERNS = [
    r"studies show",
    r"research (has )?shown",
    r"it is (generally |well )?known",
    r"research demonstrates",
    r"science has established",
    r"it is (generally |widely )?accepted",
    r"the literature (shows|suggests)",
    r"conventional wisdom",
]


def score_eg(text: str) -> dict:
    """Returns {'tokens': int, 'pos': int, 'neg': int, 'score': float}."""
    tokens = len(text.split())
    pos_matches = sum(len(re.findall(p, text, re.IGNORECASE)) for p in EVIDENCE_TYPE_PATTERNS)
    pos_matches += sum(len(re.findall(p, text, re.IGNORECASE)) for p in CLAIM_EVIDENCE_PATTERNS)
    neg_matches = sum(len(re.findall(p, text, re.IGNORECASE)) for p in VAGUE_APPEAL_PATTERNS)
    score = ((pos_matches - neg_matches) / tokens * 1000) if tokens > 0 else 0.0
    return {"tokens": tokens, "pos": pos_matches, "neg": neg_matches, "score": score}
```

Similar for `rt_scorer.py`.

### 2.5 `mvp/calibrate_scorers.py` (new)

Runs EG + RT scorers on all 80 `mvp-combined/` passages and reports:
- Virtuous mean vs non-virtuous mean per scorer
- Distribution plots (optional)
- List of outlier passages (hand-review candidates)

Pass criterion: virtuous mean − non-virtuous deficiency mean ≥ +5 points on the target scorer.

### 2.6 `mvp/specificity_matrix.py` (new)

Main orchestrator. Pseudocode:

```
for model in [qwen3-4b, gemma-4-E4B-it]:
  for eval in [AIME-42, abstention, EG-eval, RT-eval]:
    prompts = load_eval_prompts(eval)
    generations = {}
    # Baseline
    generations["baseline"] = generate_all(model, prompts, alpha=0)
    # Steered
    for vector in [v_CC, v_IH, v_EG, v_RT]:
      alpha, layer = VECTORS[vector][f"best_alpha_{eval.name}"]  # or unified best_alpha
      generations[vector] = generate_all(model, prompts, vector=vector, alpha=alpha, layer=layer)
    # Score every generation with all 4 scorers
    for gen_set in generations.values():
      for g in gen_set:
        g.scores = {
          "cc": score_cc_hedging(g.text),
          "ih": score_ih_abstention(g.text, g.prompt),
          "eg": score_eg(g.text),
          "rt": score_rt(g.text),
        }
    # Write to mvp/results/specificity_matrix/{model}_{eval}.csv
```

CSV columns: `model, eval, vector, prompt_id, prompt_text, generation, cc_score, ih_score, eg_score, rt_score, tokens`.

---

## 3. Run order + GPU budget

### 3.1 Full sequence

| # | Stage | What runs | Duration | Output |
|---|---|---|---|---|
| 0 | Pre-flight | Write EG/RT scorers, prompts, calibrate on corpus | 4h dev + 10 min run | Scorers + calibration report |
| 1 | Extraction | `extract_v2.py` × 4 (2 models × 2 virtues) | **~12h GPU** | Vectors in `mvp/results/vectors/` |
| 2 | Geometric MVE | `mve_gate_test.py --matrix-mode` | 30 min CPU | 4×4 orthogonality tables per model |
| 3 | α/layer sweep | `run_steering_sweep.py` on 5 prompts per eval × 4 vectors × 2 models, α {4, 8, 12, 16, 20}, layers {L18, L20, L22} on Qwen / {L14, L18, L22} on Gemma | **~4h GPU** | Per-vector optimal (α, layer) |
| 4 | 4×4 matrix | `specificity_matrix.py` | **~6h GPU** (864 generations × 2 models) | CSV per (model, eval) |
| 5 | Hand review | Manual Likert per generation | ~16-20h spread over ~6 days | Annotation CSV |
| 6 | Analysis | Aggregate + reporting | 1-2 days | Findings write-up |

**GPU budget total:** ~22h at L4 (can split across 2-3 overnight runs).

### 3.2 Parallelization

- Hand review (stage 5) can start as soon as the first (model, eval) CSV lands in stage 4 — don't wait for all runs to complete.
- Stage 2 (MVE) can run concurrently with stage 3 (α-sweep) on different vector pairs.
- Stage 6 analysis can start as soon as 4/16 cells have both runs + hand-review.

---

## 4. Commands — copy-paste ready

### 4.1 Pre-flight calibration

```bash
cd /Users/sumit/Github/Phronesis/mvp
python calibrate_scorers.py --corpus-eg ../corpus/mvp-combined/triplets-evidence-grounding \
                             --corpus-rt ../corpus/mvp-combined/triplets-reasoning-transparency
# Expect: EG virtuous mean ≥ +10, deficiency mean ≤ +2 (separation ≥5)
# Expect: RT virtuous mean ≥ +10, deficiency mean ≤ +2
# If fail, refine scorer markers and re-run
```

### 4.2 Extraction (on GCP L4)

```bash
# On VM:
cd /home/research/Phronesis/mvp

# Qwen × EG (~3h)
python extract_v2.py --model qwen3-4b \
  --corpus ../corpus/mvp-combined/triplets-evidence-grounding \
  --method generation --layers all --save-vectors

# Qwen × RT (~3h)
python extract_v2.py --model qwen3-4b \
  --corpus ../corpus/mvp-combined/triplets-reasoning-transparency \
  --method generation --layers all --save-vectors

# Gemma × EG (~3h)
python extract_v2.py --model gemma-4-E4B-it \
  --corpus ../corpus/mvp-combined/triplets-evidence-grounding \
  --method generation --layers all --save-vectors

# Gemma × RT (~3h)
python extract_v2.py --model gemma-4-E4B-it \
  --corpus ../corpus/mvp-combined/triplets-reasoning-transparency \
  --method generation --layers all --save-vectors
```

Run sequentially in a single overnight job via shell script.

### 4.3 Geometric MVE matrix

```bash
# Local (CPU is fine)
python mve_gate_test.py --model qwen3-4b --matrix-mode \
  --vectors v_CC_qwen_L20 v_IH_qwen_L20 v_EG_qwen_L20 v_RT_qwen_L20

python mve_gate_test.py --model gemma-4-E4B-it --matrix-mode \
  --vectors v_CC_gemma_L14 v_IH_gemma_L14 v_EG_gemma_L14 v_RT_gemma_L14
```

### 4.4 α/layer pre-sweep

```bash
# 5 prompts per eval, α {4,8,12,16,20}, layers per model
python run_steering_sweep.py \
  --model qwen3-4b \
  --vectors v_EG_qwen v_RT_qwen \
  --evals eg-eval rt-eval \
  --alphas 4 8 12 16 20 \
  --layers 18 20 22 \
  --prompts-per-eval 5 \
  --output mvp/results/alpha_sweep_qwen.json
# Same for Gemma with layers 14 18 22
```

### 4.5 4×4 specificity matrix

```bash
python specificity_matrix.py \
  --models qwen3-4b gemma-4-E4B-it \
  --vectors v_CC v_IH v_EG v_RT \
  --evals aime-42 abstention eg-eval rt-eval \
  --alpha-config mvp/results/alpha_sweep_qwen.json,mvp/results/alpha_sweep_gemma.json \
  --output mvp/results/specificity_matrix/
```

Output: CSV per (model, eval) = 8 CSVs, each with ~6 × 24 = 144 rows (baseline + 4 steered + per-prompt scores).

---

## 5. Expected output format

### 5.1 Per-cell CSV

`mvp/results/specificity_matrix/qwen3-4b_eg-eval.csv`:

```
model,eval,vector,prompt_id,prompt_text,generation,cc_score,ih_score,eg_score,rt_score,tokens
qwen3-4b,eg-eval,baseline,eg-p01,"What explains why metals are usually shiny?","Metals are...",0.3,0.0,2.1,4.5,178
qwen3-4b,eg-eval,v_CC,eg-p01,"What explains...","Metals...",2.1,0.0,1.8,3.9,182
qwen3-4b,eg-eval,v_IH,eg-p01,"What explains...","I'm not certain...",1.4,2.3,2.0,4.1,165
qwen3-4b,eg-eval,v_EG,eg-p01,"What explains...","Observations of polished metal...",0.4,0.0,12.3,5.2,195
qwen3-4b,eg-eval,v_RT,eg-p01,"What explains...","First, consider the electron...",0.5,0.0,2.2,14.8,201
```

### 5.2 Aggregate matrix

`mvp/results/specificity_matrix/matrix_summary.csv`:

```
model,eval,vector,mean_target_score,baseline_mean,delta,ci_low,ci_high,n_prompts
qwen3-4b,eg-eval,v_EG,12.3,2.1,+10.2,+8.1,+12.5,24
qwen3-4b,eg-eval,v_CC,1.9,2.1,-0.2,-1.3,+0.9,24
qwen3-4b,eg-eval,v_IH,2.0,2.1,-0.1,-1.1,+0.9,24
qwen3-4b,eg-eval,v_RT,2.2,2.1,+0.1,-1.0,+1.2,24
```

### 5.3 Per-generation manual review CSV (for hand-scoring)

`mvp/results/specificity_matrix/manual_review_qwen3-4b_eg-eval.csv`:

```
model,eval,vector,prompt_id,generation,auto_cc,auto_ih,auto_eg,auto_rt,human_cc_1to5,human_ih_1to5,human_eg_1to5,human_rt_1to5,gaming_flag,degenerate_flag,notes
qwen3-4b,eg-eval,baseline,eg-p01,"Metals are...",0.3,0.0,2.1,4.5,,,,,, ,
```

(Empty columns at end = human fills in)

---

## 6. Failure recovery

### 6.1 Extraction fails mid-run (stage 1)

- Partial vectors saved → resume by re-running only the failed (model, virtue) combination
- `save_vectors` is atomic per-layer, so worst case is losing partial layers of one extraction

### 6.2 MVE reveals collapse (stage 2)

- If |cos(v_EG, v_RT)| > 0.6 on either model → AOT-collapse risk. Proceed anyway, but note in reporting that the two vectors cluster.
- If v_EG orthogonal to v_CC but retention < 90% → weak separability. Use but flag.

### 6.3 α-sweep reveals no diagonal effect (stage 3)

- If best α for v_EG on EG-eval still produces delta < +5 → possible F11 failure (model lacks EG competency to amplify) or scorer problem.
- Mitigation: try wider α range (α up to 30); if still no effect, escalate to scorer validation before matrix run.

### 6.4 Matrix reveals off-diagonal dominance (stage 4)

- Document which specificity tests failed. Possible causes:
  - Shared scenario features in corpus (e.g., both EG and RT corpora drew from same triplets-combined substrates — *should be disjoint per LEDGER §3*)
  - Natural virtue overlap (RT-virtuous passages often also exhibit EG — known risk)
- Report as partial success per exit criteria in `eg-rt-eval-spec.md` §5.7.

### 6.5 Scorer calibration fails (stage 0)

- Virtuous mean not > non-virtuous mean by ≥5 → refine regex patterns; re-run calibration
- Three attempts max; after that, escalate to LLM-as-judge fallback per `scoring.md`
- Do NOT run extraction until calibration passes

---

## 7. Pre-GPU checklist

Before kicking off any GPU run:

- [ ] `mvp/benchmarks/eg_prompts.json` committed (24 prompts per `eg-rt-eval-spec.md` §3.3)
- [ ] `mvp/benchmarks/rt_prompts.json` committed (24 prompts per §4.3)
- [ ] `mvp/benchmarks/eg_scorer.py` committed and unit-tested on 5 hand-picked passages
- [ ] `mvp/benchmarks/rt_scorer.py` committed and unit-tested
- [ ] `mvp/calibrate_scorers.py` run successfully: virtuous > non-virtuous mean ≥ +5 on both scorers
- [ ] `mvp/utils.py` `MVP_COMBINED_*_DIR` constants added
- [ ] `mvp/mve_gate_test.py` `--matrix-mode` extension committed
- [ ] `mvp/run_benchmark.py` VECTORS registry has placeholders for v_EG + v_RT (will fill in after extraction)
- [ ] `mvp/specificity_matrix.py` committed and dry-runnable on a 2-prompt toy case
- [ ] GCP VM accessible and has >30 GB free disk for vector + generation storage
- [ ] `docs/eg-rt-eval-spec.md` reviewed and frozen (no prompt-set changes after extraction starts)

---

## 8. Post-extraction checklist (before specificity matrix)

After extraction + α-sweep complete:

- [ ] 4 vectors saved: `v_EG_qwen`, `v_EG_gemma`, `v_RT_qwen`, `v_RT_gemma`, at all sweep layers
- [ ] Geometric MVE matrix table generated for both models
- [ ] α-sweep JSON files generated with optimal (α, layer) per vector
- [ ] VECTORS registry in `run_benchmark.py` updated with default_alpha values
- [ ] Specificity matrix harness tested end-to-end on 2 prompts × 1 vector × 1 eval (dry run verifies plumbing before full 864-gen run)

---

## 9. Post-matrix checklist (before analysis)

- [ ] All 8 per-(model, eval) CSVs generated
- [ ] `matrix_summary.csv` generated with aggregate deltas + bootstrap CIs
- [ ] Manual review CSVs pre-populated (human columns empty, ready for scoring)
- [ ] Hand-review started on at least 4 cells (diagonal priority)
- [ ] No degenerate generations detected (check for repetition / truncation / gibberish) — if found, quarantine those rows

---

## 10. Document state

- **Created:** 2026-04-22 (Day 15)
- **Companion docs:** `docs/eg-rt-eval-spec.md` (benchmark spec), `docs/mvp-virtues.md` (scope), `docs/scoring.md` (manual-first policy), `corpus/mvp-combined/LEDGER.md` (corpus provenance)
- **Next update:** after Stage 0 calibration (may require scorer refinement, which would update spec + runbook)
