#!/bin/bash
# Sequential 4-extraction run for EG + RT on both models.
# Per docs/extraction-runbook.md §4.2.
#
# Each extraction: ~3h at L4 scale. Total ~12h.
# Writes progress to mvp/results/extraction_progress.json (for dashboard).
# Logs to mvp/results/eg_rt_extraction.log.
#
# Usage: cd mvp && bash run_eg_rt_extractions.sh
# Monitor: http://<VM_IP>:8080 (after starting dashboard_vm.py)

set -u
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
LOGFILE="results/eg_rt_extraction.log"
mkdir -p results

echo "================================================================" | tee -a "$LOGFILE"
echo "Phronesis EG + RT Extraction — 4 runs" | tee -a "$LOGFILE"
echo "Started: $(date)" | tee -a "$LOGFILE"
echo "Host: $(hostname)" | tee -a "$LOGFILE"
echo "================================================================" | tee -a "$LOGFILE"

# Extraction 1/4: Qwen × EG
echo "" | tee -a "$LOGFILE"
echo "[1/4] $(date) — qwen3-4b × triplets-evidence-grounding" | tee -a "$LOGFILE"
$PYTHON extract_v2.py --model qwen3-4b \
  --corpus ../corpus/mvp-combined/triplets-evidence-grounding \
  --method generation --layers all --save-vectors \
  2>&1 | tee -a "$LOGFILE"

# Extraction 2/4: Qwen × RT
echo "" | tee -a "$LOGFILE"
echo "[2/4] $(date) — qwen3-4b × triplets-reasoning-transparency" | tee -a "$LOGFILE"
$PYTHON extract_v2.py --model qwen3-4b \
  --corpus ../corpus/mvp-combined/triplets-reasoning-transparency \
  --method generation --layers all --save-vectors \
  2>&1 | tee -a "$LOGFILE"

# Extraction 3/4: Gemma × EG
echo "" | tee -a "$LOGFILE"
echo "[3/4] $(date) — gemma-4-E4B-it × triplets-evidence-grounding" | tee -a "$LOGFILE"
$PYTHON extract_v2.py --model gemma-4-E4B-it \
  --corpus ../corpus/mvp-combined/triplets-evidence-grounding \
  --method generation --layers all --save-vectors \
  2>&1 | tee -a "$LOGFILE"

# Extraction 4/4: Gemma × RT
echo "" | tee -a "$LOGFILE"
echo "[4/4] $(date) — gemma-4-E4B-it × triplets-reasoning-transparency" | tee -a "$LOGFILE"
$PYTHON extract_v2.py --model gemma-4-E4B-it \
  --corpus ../corpus/mvp-combined/triplets-reasoning-transparency \
  --method generation --layers all --save-vectors \
  2>&1 | tee -a "$LOGFILE"

echo "" | tee -a "$LOGFILE"
echo "================================================================" | tee -a "$LOGFILE"
echo "All 4 extractions complete: $(date)" | tee -a "$LOGFILE"
echo "================================================================" | tee -a "$LOGFILE"
