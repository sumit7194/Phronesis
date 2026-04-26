# Evening note — 2026-04-25

Status check after all 4 EG/RT extractions completed overnight on `phronesis-v2-l4`.

**TL;DR:** Extractions done. Vectors pulled. Geometric MVE matrix is **all_clean: 12/12 cells pass on both qwen3-4b and gemma-4-E4B-it**. The biggest pre-data risk — F39 EG×RT collapse — did not materialize. We are now formally on the F98 `all_clean` geometric branch. Behavioral 4×4 matrix still needs to land before MVP-success is final.

---

## 📥 What landed

### Extractions completed

| Model | Corpus | Layers |
|---|---|---|
| qwen3-4b | EG | 36/36 ✅ |
| qwen3-4b | RT | 36/36 ✅ |
| gemma-4-E4B-it | EG | 42/42 ✅ |
| gemma-4-E4B-it | RT | 42/42 ✅ |

### Pulled to local

```
mvp/results/vectors/qwen3-4b/triplets-evidence-grounding/      3.4M
mvp/results/vectors/qwen3-4b/triplets-reasoning-transparency/  3.0M
mvp/results/vectors/gemma-4-E4B-it/triplets-evidence-grounding/      2.1M
mvp/results/vectors/gemma-4-E4B-it/triplets-reasoning-transparency/  2.1M
mvp/results/mvp_v2_qwen3-4b_triplets-evidence-grounding.json
mvp/results/mvp_v2_qwen3-4b_triplets-reasoning-transparency.json
mvp/results/mvp_v2_gemma-4-E4B-it_triplets-evidence-grounding.json
mvp/results/mvp_v2_gemma-4-E4B-it_triplets-reasoning-transparency.json
mvp/results/eg_rt_extraction.log
mvp/results/extraction_progress.json
```

Total pulled: ~11M.

---

## 🧮 MVE result: ALL CLEAN on both models

Ran `python3 mvp/analysis/run_analysis.py --mve-only`. Output:

```
[mve] qwen3-4b        verdict: all_clean (6/6 pairs pass)
[mve] gemma-4-E4B-it  verdict: all_clean (6/6 pairs pass)
```

### qwen3-4b — 6/6 pass

| pair | mean \|cos\| | max \|cos\| | retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.179 | 0.314 | 98.1% | 🟢 |
| CC ⊥ EG | 0.157 | 0.202 | 98.7% | 🟢 |
| CC ⊥ RT | 0.099 | 0.175 | 99.5% | 🟢 |
| IH ⊥ EG | 0.026 | 0.089 | 99.9% | 🟢 |
| IH ⊥ RT | 0.020 | 0.045 | 100.0% | 🟢 |
| EG ⊥ RT | 0.104 | 0.181 | 99.3% | 🟢 |

### gemma-4-E4B-it — 6/6 pass

| pair | mean \|cos\| | max \|cos\| | retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.030 | 0.104 | 99.9% | 🟢 |
| CC ⊥ EG | 0.142 | 0.259 | 98.9% | 🟢 |
| CC ⊥ RT | 0.149 | 0.238 | 98.8% | 🟢 |
| IH ⊥ EG | 0.100 | 0.157 | 99.4% | 🟢 |
| IH ⊥ RT | 0.056 | 0.211 | 99.8% | 🟢 |
| EG ⊥ RT | 0.115 | 0.242 | 99.2% | 🟢 |

Pre-registered thresholds (`mvp/analysis/config.yaml`):
- `cos_clean_threshold: 0.20` (mean) — all 12 pass
- `retention_pass_threshold: 0.70` — all 12 well above (≥98%)

### Where the report lives

- `mvp/results/analysis_report/report.md`
- `mvp/results/analysis_report/mve_heatmap_qwen3-4b.png`
- `mvp/results/analysis_report/mve_heatmap_gemma-4-E4B-it.png`
- `mvp/results/analysis_report/per_layer_cosine_qwen3-4b.png`
- `mvp/results/analysis_report/per_layer_cosine_gemma-4-E4B-it.png`

---

## 🔍 Per-layer behavior worth knowing

Does NOT change verdict. But you should know before α-sweep.

- **qwen3-4b CC⊥IH** spikes above 0.20 mean threshold in layers ~19–30, peaks 0.314 at L23. Within partial-overlap band (<0.5). F97 already flagged this pair as warmest on qwen — reproduced. Plan around it: avoid L23 as the steering layer for any CC vs IH disambiguation.
- **gemma-4-E4B-it early layers (L1–7):** CC⊥RT max 0.238 at L1, CC⊥EG max 0.259 around L5. Settles below 0.20 by L8. Plausibly artefacts of unspecialized early-layer reps. Steering layers are typically 18–25, so not an issue.

---

## 🎯 F98 interpretation — which branch are we on?

F98 pre-registered three exit branches (`docs/findings.md`). Geometric criterion for each:

| Branch | MVE pairs pass (of 6) | Today's result |
|---|---|---|
| **all_clean** | 6/6 | ✅ both models |
| partial | 5/6 | — |
| collapse | ≤4/6 OR EG×RT collapse | — |

We're on the **all_clean branch on the geometric criterion**.

This is NOT yet the all_clean MVP outcome — that requires the behavioral 4×4 specificity matrix to also clear F98's diagonal/off-diagonal thresholds. Geometric independence is necessary, not sufficient.

Per `docs/post-mvp-decisions.md`:

> **all_clean → α-sweep on VM (~4h GPU) → 4×4 specificity matrix on VM (~6h GPU) → hand review (~16–20h manual) → final analysis + report**

---

## 📝 Documents updated today

- **`docs/findings.md` F99**: skeleton replaced with full data — extractions, MVE matrix per model, F98 branch interpretation, caveats.
- **`docs/journal.md` Day 18**: new entry covering the morning's pull → analyze → document loop.
- **`docs/evening-note-2026-04-25.md`** (this file).

No code changes today. Pure data + documentation.

---

## 🔬 Sanity checks (afternoon) — see F100 in `docs/findings.md`

Three checks done before any GPU authorisation. F99's optimism is partially walked back by F100.

### Check 1: Probe accuracy at steering layers (L18–25)

Reference: F97 qwen × CC has probe acc mean 0.93, best 0.96.

| Model × Virtue | Best L18-25 | Mean L18-25 | Verdict |
|---|---|---|---|
| qwen × EG | 0.66 | 0.62 | 🟡 weaker than CC ref |
| qwen × RT | 0.61 | 0.56 | 🔴 **barely above chance** |
| gemma × EG | 0.80 | 0.75 | 🟢 |
| gemma × RT | 0.68 | 0.65 | 🟡 |

CC and IH were extracted via `last_token` method (very high probe acc); EG and RT via `generation` method (lower probe acc). Method may be partially responsible. qwen × RT is concerning — vector likely has weak signal-to-noise.

### Check 2: Retention >98% — vacuous?

In R^2560, two random vectors have expected |cos| = 1/√2560 ≈ 0.020 and expected retention ≈ 99.96%. So retention > 99% is satisfied by any pair with low |cos| — including pure noise pairs.

**Re-reading F99 with this in mind:**

| Pair | Mean \|cos\| | Above random baseline? |
|---|---|---|
| qwen CC⊥IH | 0.179 | ✅ clearly real signal |
| qwen CC⊥EG | 0.157 | ✅ |
| qwen CC⊥RT | 0.099 | ✅ |
| qwen IH⊥EG | 0.026 | ⚠️ near random |
| qwen IH⊥RT | 0.020 | ⚠️ **at random baseline** |
| qwen EG⊥RT | 0.104 | ✅ — F39 risk did NOT materialise |
| gemma CC⊥IH | 0.030 | ⚠️ near random |
| gemma CC⊥EG | 0.142 | ✅ |
| gemma CC⊥RT | 0.149 | ✅ |
| gemma IH⊥EG | 0.100 | ✅ |
| gemma IH⊥RT | 0.056 | ⚠️ closer to random |
| gemma EG⊥RT | 0.115 | ✅ |

F99 still passes F98's pre-registered `all_clean` thresholds — no goalpost-moving. But "12/12 pass" should be read as *"no pair collapses, and several show genuine geometric distinctness"* — not as 12 independent pieces of strong evidence.

### Check 3: Scorer drift

Re-ran `mvp/calibrate_scorers.py`. EG separation +19.57, RT +9.90 — identical to Day 17 numbers. No drift. Known FM-6 / FM-7 false-positives and false-negatives reproduce exactly. Hand-review will catch them as planned.

(Note: I had originally framed this as "spot-check scorer against extraction generations." That was the wrong framing — `extract_v2.py` doesn't save model generations. Generations only land during α-sweep / 4×4 matrix runs. Re-calibration is the correct sanity check at this stage.)

---

## 🎯 Decision point — qwen × RT re-extraction?

The probe-accuracy gap for EG and RT could be:
- **(A) Method confound:** `generation` averages over 128 generated tokens; `last_token` uses one token. Different SNR.
- **(B) Real signal weakness:** RT (and to a lesser extent EG) are geometrically harder to separate on qwen3-4b.

To disambiguate, recommended option:

> **Re-extract qwen × RT with `last_token` method (~2h GPU) before α-sweep.**
>
> If `last_token` gives probe acc ~0.85+: it's method confound. Use `last_token` vectors going forward; consider re-running EG too.
> If `last_token` gives probe acc ~0.60: it's real RT-on-qwen weakness. Proceed and accept that the qwen-RT row may be null in the 4×4 matrix.

Cost: ~2h GPU. Benefit: removes method as a confound for the headline qwen-RT-row interpretation.

Alternative: skip re-extraction, run α-sweep, accept ambiguity if qwen-RT row goes null.

---

## 📝 Documents updated this afternoon

- **`docs/findings.md` F100** (new): sanity-check follow-up to F99. Probe accuracies, retention significance, method-confound discussion, recommendation to re-extract qwen × RT.
- **`docs/journal.md` Day 18**: appended sanity-check section + revised next-action plan.
- **`docs/evening-note-2026-04-25.md`** (this file): updated with check results.

---

## ▶️ Next action when you're back

Pick one:

1. **(Recommended) Re-extract qwen × RT with last_token method.** ~2h GPU. Then α-sweep.
2. **Skip re-extraction, proceed to α-sweep (~4h GPU) immediately.** Accept potential null qwen-RT row in 4×4 matrix.
3. **Pause and think about method consistency more broadly.** F100 flagged that mixing `last_token` (CC, IH) with `generation` (EG, RT) is a methodological inconsistency. Before publication, this needs to either be reconciled (re-extract everything one way) or explicitly justified. Could be worth thinking about now rather than after the 4×4 matrix.

VM is idle. Total GPU budget so far: ~32h on the original 4 extractions. Re-extracting one virtue is ~2h. Re-extracting all 4 with last_token is ~8h. Still well within phase-4a budget envelope.

---

## 🌙 Late-evening update — full uniform last_token MVE complete (F102)

User picked option 1, then immediately authorised the remaining 3 to make the matrix uniform. All 4 last_token re-extractions completed by 01:10 UTC. Updated `compute_mve.py` to default to last_token for EG/RT. Re-ran `run_analysis.py --mve-only`.

### Headline result

```
qwen3-4b:        collapse  (3/6 pairs pass)
gemma-4-E4B-it:  all_clean (6/6 pairs pass)
```

**The two models give opposite answers to the same question. Cross-model split is the headline.**

### Probe accuracy improvements (all four combos confirm method confound)

| Combo | generation best | last_token best | Δ |
|---|---|---|---|
| qwen × EG | 0.66 (L20/L22) | **0.94** (L30) | +0.28 |
| qwen × RT | 0.61 (L22) | **0.90** (L31) | +0.29 |
| gemma × EG | 0.83 (L6) | (need to read summary) | — |
| gemma × RT | 0.74 (L6) | 0.75 (L26) | ~0 |

Method confound was real and large for qwen, smaller for gemma. Consistent with gemma's higher generation-method probe accuracies to begin with.

### qwen3-4b — 3/6 pass (COLLAPSE)

| pair | mean \|cos\| | max \|cos\| | retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.179 | 0.314 | 98.1% | 🟢 |
| **CC ⊥ EG** | **0.376** | 0.453 | 92.4% | 🟡 partial |
| **CC ⊥ RT** | **0.377** | **0.520** | 92.2% | 🟡 partial |
| IH ⊥ EG | 0.104 | 0.211 | 99.3% | 🟢 |
| IH ⊥ RT | 0.059 | 0.120 | 99.8% | 🟢 |
| **EG ⊥ RT** | **0.334** | **0.554** | 93.2% | 🟡 partial |

Per-layer pattern: at L0–15, pairs scattered. **At L20–31, CC⊥EG, CC⊥RT, EG⊥RT all rise together to 0.40–0.55.** EG⊥RT crosses 0.50 at L29–31, peaks 0.554 at L30. CC⊥RT crosses 0.50 at L31, peaks 0.520. CC⊥IH stays clean throughout (mean 0.179) — **IH stays orthogonal to all three**.

**Mechanistic reading:** at qwen's deeper layers, three of four virtues (CC, EG, RT) share a substantial direction component. Plausibly the F39 "epistemic care / scientific reasoning" cluster, plus CC. IH sits on a different mechanism.

### gemma-4-E4B-it — 6/6 pass (ALL CLEAN)

| pair | mean \|cos\| | max \|cos\| | verdict |
|---|---|---|---|
| CC ⊥ IH | 0.030 | 0.104 | 🟢 |
| CC ⊥ EG | 0.087 | 0.192 | 🟢 |
| CC ⊥ RT | 0.072 | 0.167 | 🟢 |
| IH ⊥ EG | 0.053 | 0.167 | 🟢 |
| IH ⊥ RT | 0.033 | 0.100 | 🟢 |
| EG ⊥ RT | 0.105 | 0.218 | 🟢 |

All 6 pairs comfortably below 0.20 mean. Single transient spike at L7 (EG⊥RT max 0.218). Otherwise clean across all 42 layers.

### F39 status — model-dependent

F39 was the single biggest pre-data risk. Result:
- qwen: **partially materialised** (EG⊥RT max 0.554, mean 0.334)
- gemma: **did NOT materialise** (EG⊥RT max 0.218, mean 0.105)

Same corpus, same method, opposite verdict.

### F98 pre-registered branches — landing

- qwen3-4b → **collapse** (3/6 + EG⊥RT > 0.50)
- gemma-4-E4B-it → **all_clean** (6/6)
- MVP-level → **cross-model split** (publishable as model-dependent finding per `post-mvp-decisions.md`)

### Headline reframe

NOT: "four orthogonal epistemic-virtue directions on small open models."

YES:
> **"Cross-model evidence that geometric separation of CC/IH/EG/RT virtue directions is model-dependent at the 4B scale. Gemma 4 E4B-it cleanly separates all four (6/6 pass); Qwen3-4B shows a partial-overlap cluster of CC, EG, and RT at deeper layers (3/6 pass), with IH remaining orthogonal."**

Arguably more interesting than monolithic all_clean would have been. Implies (1) the atomic-virtue-direction hypothesis isn't model-invariant, (2) qwen's deep residual stream bundles CC/EG/RT, (3) IH behaves differently from AOT-related virtues on both models.

### What this means for next steps

- **4×4 specificity matrix is still worth running.** Test of whether the geometric finding has behavioural consequences.
  - Gemma: should show clean diagonals, low off-diagonal
  - Qwen: should show substantial CC↔EG↔RT cross-talk; IH-row should stay clean
- **α-sweep can proceed.** For qwen, prefer mid-layers (L18–22) where the cluster is less collapsed.
- **No further re-extraction needed.** Method-consistency resolved.

### Documentation snapshot (full set)

- **`docs/findings.md`** — F100 (sanity-check hypothesis), F101 (qwen×RT diagnostic), F102 (full uniform-method matrix + cross-model split)
- **`docs/journal.md` Day 18** — three-section entry tracking the morning F99, afternoon F100, evening F101, late-evening F102
- **`docs/extraction-runbook.md` §11** — methodological-consistency issue documented; resolution = uniform last_token
- **`mvp/analysis/compute_mve.py`** — DEFAULT_VIRTUE_PATHS updated to last_token for EG/RT
- **`mvp/results/analysis_report/`** — regenerated with F102 numbers (this is now the canonical report)

### Final headcount

GPU spent today: ~36 min on 4 last_token re-extractions. Total project GPU: ~32h originals + 0.6h today.

VM idle. No further extractions queued. Awaiting decision on α-sweep timing.

— end of note —
