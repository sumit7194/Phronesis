# Phronesis publication-readiness audit — 2026-05-18

*Audit run before the first public push of the GitHub repo. All file:line citations verified against the working tree at `/Users/sumit/Github/Phronesis` on 2026-05-18.*

---

## 1. Repo-state snapshot

- **Remote configured but repo not yet public.** `git remote get-url origin` → `https://github.com/sumit7194/Phronesis.git`. Unauthenticated `curl` against `https://github.com/sumit7194/Phronesis` returns **404** — the GitHub repo either does not exist yet or is private. **Pre-first-push state.**
- **Branch:** `main`. No other local branches active.
- **Tracked tree:** 12,787 files. `.git` = **149 MB**; tracked working tree under `mvp/results/` ≈ 384 MB; full checkout ≈ **2.6 GB** (most untracked artifacts).
- **Pack:** one orphan `tmp_obj_XRONK8` in `.git/objects/fe/` — benign; `git gc` cleans it.
- **Dirty tree is messy:** **461 modified**, **123 untracked**, **1 deleted**. ~410 of the 461 modified are `mvp/results/vectors/qwen3-4b/triplets-*/last_token/layer_*.{npy,json}`.

---

## 2. Tier-1 blockers

### 2a. Secrets — clean

- `git grep` for `sk-ant-`, `sk_live_`, `pk_live_`, `AKIA[0-9A-Z]{16}`, `hf_[A-Za-z0-9]{30,}`, `BEGIN PRIVATE KEY` → **zero hits** in tracked tree.
- No `.env`, `.pem`, `.key` files tracked or present anywhere under the repo.
- Only API-key string found: `GEMINI_API_KEY` at [mvp/generate_corpus_gemini.py:256](mvp/generate_corpus_gemini.py:256) — read via `os.environ.get(...)` (correct pattern).
- `NEURONPEDIA_API_KEY_2..._6` mentioned narratively in [docs/journal.md:1494](docs/journal.md:1494) (no values).

### 2b. Personally identifying / private info

- **`linkedin_nile.png`** (96 KB, untracked at repo root) — likely a LinkedIn screenshot. Leaving it in the working dir is a hazard; one careless `git add .` puts it in public history.
- **`Chat_with_claude_about_this_project_that_i_am_planning.rtf`** (90 KB, **tracked** at root) — brainstorming chat; identity-revealing only at public-Twitter level ("Sumit", Mac Mini M4 16 GB). Reads like a private journal; adds nothing to reproducibility.
- **`trick_question_test_l20_l22_different_alpha.rtf`** (386 KB, **tracked** at root) — terminal output dump including `sumit@Sumits-Mac-mini` shell prompts at lines 13, 1304, 2495.
- **GCP VM identity leak:** `gcloud compute ssh sumit@phronesis-v2-l4 --zone=asia-southeast1-a` appears in:
  - [mvp/dashboard_v2_sweep.py:19](mvp/dashboard_v2_sweep.py:19)
  - [mvp/results/v2_sweep_access.md:37](mvp/results/v2_sweep_access.md:37), [:38](mvp/results/v2_sweep_access.md:38), [:66](mvp/results/v2_sweep_access.md:66)
- **Third-party emails:**
  - `johnny@neuronpedia.org` (1 hit, [docs/sae-experiment-plan.md:236](docs/sae-experiment-plan.md:236)) — public Neuronpedia contact; ask before publishing.
  - `nvladimir.shelomovskii@gmail.com` — **96 hits** across `mvp/results/benchmark_probe/aime/.../*.json`. AIME problem-set provenance from AoPS. Probably fine (redistribution of public dataset) but confirm dataset license.

### 2c. LW-cited result paths — NONE OF THEM ARE TRACKED

**Most serious blocker.** Verified with `git ls-files`:

- `mvp/results/sae_steering_analysis_20260513/per_generation.csv` — exists (469 KB), **0 files tracked** in this dir.
- `mvp/results/sae_mech_battery_v1_analysis/per_generation.csv` — exists (25 KB), **0 of 2 files tracked.**
- `mvp/results/sae_steering/{model}/{cell}.json` — 37 files across 5 model subdirs, **0 tracked.**
- `mvp/results/sae_mech_battery_v1/{cell}.json` — 18 files on disk, **0 tracked.**

Right now a clean clone would 404 on every link in the LW post.

### 2d. Absolute-path leakage in tracked JSON/configs — pervasive

- `git grep -lE "/home/sumit|/Users/sumit"` → **682 tracked files** with `/home/sumit/...` or `/Users/sumit/...`.
- Most common pattern: `"vector_path": "/home/sumit/phronesis/mvp/results/..."` inside steering result JSONs.
- Concrete samples:
  - [mvp/dashboard_live.py:86,96](mvp/dashboard_live.py:86) — hard-coded `/home/sumit/phronesis/mvp/results/benchmark_probe/...`
  - [mvp/dashboard_vm.py:34](mvp/dashboard_vm.py:34) — same
  - 169 tracked files under `mvp/results/_gcp_backup_20260417_022017/` carry `vector_path` fields pointing into `/home/sumit/phronesis/...`
- 7 tracked docs reference `/Users/sumit/...` paths (extraction-runbook, morning/evening notes, cron-prompt files).

### 2e. `.gitignore` adequacy — incomplete

Current `.gitignore` (25 lines, verified):
```
.DS_Store
__pycache__/
*.pyc
.venv/
mvp/models/
mvp/*.log
mvp/qualitative_dump.txt
.claude/scheduled_tasks.lock
.claude/launch.json
mvp/_gcp_code_snapshot/
mvp/E4_spiral.md
```

Gaps:
- No `.env*`, `*.pem`, `*.key`.
- `.claude/` only partially ignored — `.claude/settings.local.json` and `.claude/worktrees/` are not.
- Three `.DS_Store` files were **committed before the rule was added** — still in history: `corpus/triplets-synthetic-gemini/.DS_Store`, `corpus/triplets-synthetic-gemma/.DS_Store`, `corpus/triplets/.DS_Store`.
- Backup dirs tracked: `mvp/results/_gcp_backup_20260417_022017/` (169 files, 2.1 MB) is tracked. Still-untracked: `sae_steering_backup_20260511_095239/`, `sae_steering_backup_gemma_20260512_131530/`, `sae_steering_local_backup_20260513_013509/`.
- No rule for `*.rtf` at repo root.
- No rule for large `.npy` files. ~280 MB of vectors under `mvp/results/vectors/`; many tracked. Will trigger GitHub large-file warnings without LFS.

---

## 3. Tier-2 concerns

- **No README at repo root.** `git ls-files | grep -v "/"` returns only `.gitignore`, the two RTFs, and `corpus_inspection_EG_v2.md`. Biggest readability fix.
- **No LICENSE file.** Without one, the code is all-rights-reserved by default and technically unusable by readers. Add `LICENSE` (MIT/Apache-2.0 for code) + optional `LICENSE-DATA` (CC-BY-4.0) for corpus.
- **No `CITATION.cff`** — 5-minute fix.
- **No `requirements.txt` / `pyproject.toml` / `setup.py`** — nothing pins versions; reproducibility blocker.
- **Awkwardly-named internal docs:** `docs/morning-note-2026-04-24.md`, `docs/evening-note-2026-04-24.md`, `docs/evening-note-2026-04-25.md`, `docs/phase4a-cron-prompt.md`, `docs/chatgpt-triplets-cron-prompt.md`, `docs/sonnet-triplets-cron-prompt.md`, `docs/sonnet-triplets-remaining-cron-prompt.md`. Either move to `docs/archive/` or strip absolute paths.
- **Half-finished scripts in `mvp/`:**
  - `mvp/_verbosity_balancer.py`, `mvp/_verbosity_patcher.py` (underscore-prefixed, tracked) signal scratch.
  - Phase-5 scripts that produced LW-cited data are **untracked**: `mvp/run_mech_battery_v1.py`, `mvp/run_sae_battery.py`, `mvp/extract_sae_decoders.py`, `mvp/sae_steering_dashboard.py`, `mvp/experiment3_enrich.py`, `mvp/experiment3_v_ih_projection.py`, etc.
- **Large tracked log files:**
  - `mvp/results/phase4.log` — 7.9 MB
  - `mvp/results/focused_sweep.log` — 2.0 MB
  - `mvp/results/verb_sweep.log` — 2.0 MB
  - `mvp/results/paths_AD.log` — 1.8 MB
  - `mvp/results/completion.log` — 930 KB
  - `mvp/results/openr1_sweep_20260501/run.log` — 923 KB
  - `mvp/results/eg_logit_inspection.json` — 1.9 MB
  - `diagnostic_batch_launch.log` at repo root — 105 KB
- **HF model IDs.** `mvp/run_benchmark.py`, `mvp/baseline_qwen3.py` etc. use shortnames `"qwen3-4b"`, `"gemma-4-E4B-it"`, `"phi-3.5-mini-it"`. Verify canonical HF IDs (`Qwen/Qwen3-4B`, `google/gemma-3-4b-it`) resolve in `mvp/utils.py` before publishing.

---

## 4. Tier-3 polish

- Commit history mixed — date-prefixed style ("Day 22:", "Day 23 evening:") will look unusual to outsiders. No need to rewrite, but be aware.
- Cross-reference spot checks all passed: 10/10 `mvp/results/...` paths from `docs/findings.md` resolve on disk; 5/5 `docs/*.md` cross-references resolve.
- One orphaned object in `.git/objects/fe/tmp_obj_XRONK8` — `git gc --prune=now` cleans.
- `.claude/worktrees/` is an empty dir — harmless visual noise.
- `results/` at repo root (separate from `mvp/results/`) is untracked — verify it isn't a stale duplicate.

---

## 5. Recommended pre-publication checklist

In dependency order:

1. **Decide the "data release model."** 280 MB vectors + ~50 MB SAE JSONs + ~22 MB logs is too much for vanilla GitHub. Pick:
   - **(a) Git LFS** for `*.npy` + commit JSON/CSV directly.
   - **(b) HuggingFace dataset** for `mvp/results/sae_steering*`, `sae_mech_battery_v1*`, `vectors/*`; link from README.
   - **(c) Hybrid:** small derived CSVs in-repo, raw NPY/JSON on HF.
   Everything below depends on this.

2. **Author missing top-level files:**
   - `README.md` — what Phronesis is, the LW-post link, where the data lives, how to reproduce
   - `LICENSE` (Apache-2.0 or MIT for code)
   - `requirements.txt` (or `pyproject.toml`) with pinned versions
   - Optional: `CITATION.cff`

3. **Expand `.gitignore`** to cover:
   - `.env*`, `*.pem`, `*.key`
   - `.claude/` (whole dir)
   - `mvp/results/sae_steering_backup_*/`, `mvp/results/sae_steering_local_backup_*/`, `mvp/results/_gcp_backup_*/`
   - `*.rtf` at root (until you decide which to keep)
   - `results/` (the stray top-level dir, if stale)
   - Large `*.npy` if not using LFS
   - Logs outside the already-covered `mvp/*.log`

4. **Remove privacy / VM-identity leaks:**
   - Replace `/home/sumit/phronesis/...` with `${PHRONESIS_ROOT}/...` or `./...` in [mvp/dashboard_live.py:86,96](mvp/dashboard_live.py:86), [mvp/dashboard_vm.py:34](mvp/dashboard_vm.py:34)
   - Edit or remove [mvp/results/v2_sweep_access.md](mvp/results/v2_sweep_access.md) (lines 37, 38, 66)
   - Edit [mvp/dashboard_v2_sweep.py:19](mvp/dashboard_v2_sweep.py:19)
   - Scrub or delete `mvp/results/_gcp_backup_20260417_022017/` (likely easier: delete — it's a local snapshot dupe)
   - Delete three committed `.DS_Store` files: `git rm --cached corpus/triplets/.DS_Store corpus/triplets-synthetic-gemini/.DS_Store corpus/triplets-synthetic-gemma/.DS_Store`
   - Move `linkedin_nile.png` out of the repo
   - Decide on the two RTFs at root: recommend moving both out of repo or into `docs/archive/` with a header

5. **Commit the LW-cited data** (after step 1 decision). The four directories that MUST be either committed or have a stable external URL:
   - `mvp/results/sae_steering_analysis_20260513/`
   - `mvp/results/sae_mech_battery_v1_analysis/`
   - `mvp/results/sae_steering/`
   - `mvp/results/sae_mech_battery_v1/`
   Plus the Phase-5 scripts that produced them.

6. **Triage 123 untracked files.** Don't `git add .` — that picks up `linkedin_nile.png`, `diagnostic_batch_launch.log`, etc.

7. **Triage 461 modified files** — mostly vector NPYs. Decide canonical version, commit or `git restore`.

8. **Move internal-feeling docs** into `docs/archive/` or add headers explaining context.

9. **`git gc --prune=now`** before tagging.

10. **Confirm HF model-ID resolution** in `mvp/utils.py`.

11. **Dry-run from a fresh clone** on the Mac Mini — `git clone`, follow README, re-derive one F121 cube corner. Anything that breaks gets fixed.

12. **Tag `v1.0-lesswrong-post`** at the commit you push.

---

## 6. Estimated cleanup time

**8–12 focused hours**, spread across two evenings:

- 1 h: README + LICENSE + requirements.txt
- 1 h: data-release decision and (if HF) bucket creation + uploads
- 2–3 h: scrub `/home/sumit` / `sumit@phronesis-v2-l4` / `.DS_Store` / RTFs / scratch dirs; update `.gitignore`
- 2 h: triage 123 untracked + 461 modified; commit Phase-5 scripts and SAE-result data
- 1 h: dry-run clean clone, fix what breaks
- 1–2 h slack for things you'll find while doing the above

**Biggest time sink:** the data-release decision in step 1.
**Biggest risk:** `git add .` with `linkedin_nile.png` untracked at repo root — footgun.
