# Morning note — 2026-04-24

Written overnight while you slept. Quick read: 3 minutes.

---

## ✅ What finished while you were asleep

### Extractions

| Run | Status |
|---|---|
| 1/4 — Qwen × EG | ✅ **DONE** (36/36 layers saved) |
| 2/4 — Qwen × RT | ✅ **DONE** (36/36 layers saved) — new, finished during the night |
| 3/4 — Gemma × EG | 🔄 **running** — at layer 13/42 (~31%) as of the log I just pulled |
| 4/4 — Gemma × RT | ⏳ queued |

**GPU at 69-76% probe accuracy** on Gemma × EG early layers, which means the virtuous vs non-virtuous passages ARE linearly separable in activation space — actual signal, not noise. Good omen.

At current pace: Gemma × EG should finish around noon UTC tomorrow (~5-6h from when I checked); Gemma × RT another ~8h after. Total: the full matrix of 4 extractions should be done late tomorrow or early the next day.

Dashboard still live at your usual URL. If your IP rotated again, the single-line fix is:

```bash
MYIP=$(curl -s https://ifconfig.me); gcloud compute firewall-rules update phronesis-dashboard --source-ranges=$MYIP/32
```

---

## 🆕 What I built overnight

Three clean commits, each testable + tested in isolation. Git log shows them clearly.

### Commit 1 — Day 15-16 foundational corpus + docs + code (big catch-up commit)

Everything from the past two days that hadn't been committed yet: the 80-triplet `corpus/mvp-combined/` with LEDGER v2, four new docs (`mvp-virtues.md`, `eg-rt-eval-spec.md`, `extraction-runbook.md`, `scoring.md`), F98 pre-registration in `findings.md`, Day 16 journal entry, EG + RT scorers + benchmarks + prompts (24 each), `calibrate_scorers.py`, `specificity_matrix.py`, `dashboard_extraction.py`, extended `mve_gate_test.py` with `--matrix-mode`, VECTORS registry updates.

### Commit 2 — `mvp/analysis/` pipeline

Pure-script (no notebook, per your preference), parameterized for N virtues (MVP=4, Phase 5=8 just works).

```
mvp/analysis/
├── config.yaml          # virtues, evals, thresholds — ONE source of truth
├── load_matrix.py       # specificity CSVs → pandas
├── compute_effects.py   # per-cell mean + bootstrap 95% CI + PASS/FLAG/FAIL verdict
├── compute_mve.py       # pairwise cos + orthogonal-retention matrix
├── figures.py           # matplotlib PNGs
├── report.py            # markdown report with inline figures
└── run_analysis.py      # entry point: `python run_analysis.py [--mve-only]`
```

Smoke-tested end-to-end on synthetic "ideal" data (correctly classifies as `all_clean`). Also ran against your existing CC + IH vectors locally — correctly says `insufficient_data` because only 1 of the 6 expected virtue-pairs is available until EG + RT extractions land.

Try it now:

```bash
cd mvp && python3 analysis/run_analysis.py --mve-only
# → writes results/analysis_report/report.md + PNGs
```

Outputs three figures (specificity heatmap per model, MVE pairwise heatmap per model, per-layer cosine line plots) and a markdown report with inline PNG refs. Opens cleanly in VS Code's markdown preview or GitHub.

### Commit 3 — `mvp/review/` hand-scoring web app

FastAPI + Jinja + vanilla JS. ONE generation per page. Four Likert sliders (1-5) + gaming/degenerate flags + free-text notes. Keyboard hotkeys: `1-5` on current virtue, `Tab` to move, `n`/`p`/`u` for nav, `Enter` = save + next unreviewed.

```
mvp/review/
├── storage.py           # CSV-backed, atomic save, progress tracking
├── app.py               # FastAPI routes
├── templates/
│   ├── base.html
│   ├── index.html       # list sessions + progress bars + build links
│   └── review.html      # the main review page
└── static/style.css     # dark theme matching the dashboard
```

End-to-end tested via HTTP — POST save → 303 redirect to next unreviewed works, builds from specificity CSVs preserve existing reviews, overwrite flag resets, export returns CSV.

**Run it locally (not on VM — review is local work):**

```bash
cd mvp
python3 -m uvicorn review.app:app --host 127.0.0.1 --port 5000
# → open http://localhost:5000
```

This is what you'll use for the ~20 hours of hand-scoring after specificity_matrix.py produces its CSVs.

---

## 📊 Current state

```
mvp/
├── analysis/          ← NEW this session, end-to-end ready
├── review/            ← NEW this session, end-to-end ready
├── benchmarks/
│   ├── eg_scorer.py   ← calibration PASS (+15.09 separation)
│   ├── rt_scorer.py   ← calibration PASS (+9.90)
│   ├── eg_eval.py     ← 24 prompts
│   ├── rt_eval.py     ← 24 prompts
│   └── (existing)
├── specificity_matrix.py  ← orchestrator, ready for when vectors land
├── calibrate_scorers.py   ← validates scorers (PASS on local + VM)
└── dashboard_extraction.py  ← running on VM

corpus/mvp-combined/    ← 80 curated triplets with LEDGER v2
docs/
├── mvp-virtues.md     ← scope
├── eg-rt-eval-spec.md ← benchmark spec + pre-registered exit criteria
├── extraction-runbook.md  ← commands + budget
├── scoring.md         ← manual-first + FM catalogue (FM-1 through FM-7)
├── findings.md        ← F98 pre-registers 4×4 exit criteria
└── journal.md         ← Day 16 entry logged
```

All deps installed locally (pandas, matplotlib, fastapi, jinja2, uvicorn, python-multipart, pyyaml).

---

## 🧭 When you wake up — what to do

### If you want to peek at the analysis output right now:

```bash
cd ~/Github/Phronesis/mvp
python3 analysis/run_analysis.py --mve-only
open results/analysis_report/report.md
```

It will say "insufficient_data" (only 1/6 virtue pairs available until EG + RT extractions finish) but you can see the report structure, the figures, the per-layer cosine plots against existing CC + IH vectors.

### If extraction is done when you wake up:

1. Pull vectors locally:
   ```bash
   gcloud compute scp --recurse --zone asia-southeast1-a \
     phronesis-v2-l4:~/phronesis/mvp/results/vectors \
     /Users/sumit/Github/Phronesis/mvp/results/
   ```

2. Run full analysis:
   ```bash
   cd mvp && python3 analysis/run_analysis.py
   open results/analysis_report/report.md
   ```

3. Geometric MVE will now have all 6 pairs — real verdict emerges.

4. **If MVE clean** → proceed to α-sweep + specificity matrix (those runs still on VM)
5. **If MVE shows AOT-collapse on EG × RT** → reframe per F98 classification; that's a publishable finding, not a failure

### If still running when you wake up:

Just keep the extraction going. Everything else is done and waiting.

---

## ⚠ Known edge cases I hit + fixed

1. **Jinja2/Starlette v1 API mismatch**: `templates.TemplateResponse("name", {...})` doesn't work in Starlette 1.0. Switched to `templates.TemplateResponse(request=request, name="...", context={...})`. Silent mode on older versions, crash on newer — now uses the new API.

2. **Tuple-keyed dicts in Jinja context**: Converted `by_cell` stats from tuple-keyed dict to list-of-dicts before passing to the template. Jinja's internal cache didn't like the nested-dict keys.

3. **"collapse" verdict on partial data was misleading**: The MVE summary would classify "1/1 pairs pass" as collapse (because 1 < 5 threshold). Added an `insufficient_data` intermediate verdict so partial runs don't falsely alarm.

4. **Storage rebuild duplicated items**: `build_review_csv_from_specificity` was re-appending existing items. Fixed to build fresh store and merge review fields from previous CSV.

5. **python-multipart not installed**: FastAPI form-handling needs it. Added to install list.

All five caught by smoke tests before being pushed.

---

## 💬 My one request

When you check `results/analysis_report/report.md` in the morning, tell me what you think of the structure. The tables + inline images + verdict badges are what I chose as defaults, but if you want something different (e.g. a separate per-model report, different table columns, different plot style) it's trivial to tweak — the pipeline is modular.

Sleep well, see you in the morning.

— your overnight research assistant 🫡
