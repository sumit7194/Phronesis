#!/bin/bash
# Phase 2 — phi-3.5-mini-instruct extraction
#
# Mirrors run_v2_sweep.sh's extraction step but for the third model.
# Extracts diff-of-means at every layer (last_token method) for the four v2
# corpora used by qwen3-4b in F108/F109:
#   - triplets-combined           (all-virtues)
#   - triplets-evidence-grounding (EG)
#   - triplets-reasoning-transparency (RT)
#   - triplets-intellectual-humility  (IH)
#   - triplets-verbosity-control      (CC_full)
#   - triplets-cc-numeric-only-symlinks (CC_numeric)
#
# Run on VM:
#   cd ~/phronesis/mvp && nohup bash run_phi_extract.sh > phi_extract.log 2>&1 &
#
# ETA on L4: ~30 minutes total (6 corpora × ~5 min).
set -u
cd "$(dirname "$0")"
if [ -x ".venv/bin/python" ]; then PYTHON=".venv/bin/python"; else PYTHON="$(command -v python3)"; fi

MODEL="phi-3.5-mini-it"
LOGDIR="results/phi_extract_$(date +%Y%m%d)"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/run.log"

echo "============================================" | tee -a "$LOG"
echo "Phi-3.5-mini extraction" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"

CORPORA=(
  "triplets-combined"
  "triplets-evidence-grounding"
  "triplets-reasoning-transparency"
  "triplets-intellectual-humility"
  "triplets-verbosity-control"
  "triplets-cc-numeric-only-symlinks"
)

CIDX=0
TOTAL=${#CORPORA[@]}
for CORPUS in "${CORPORA[@]}"; do
  CIDX=$((CIDX+1))
  CORPUS_DIR="../corpus/$CORPUS"
  if [ ! -d "$CORPUS_DIR" ]; then
    echo "[$CIDX/$TOTAL] SKIP: $CORPUS_DIR not found" | tee -a "$LOG"
    continue
  fi
  echo "" | tee -a "$LOG"
  echo "[$CIDX/$TOTAL] Extracting $CORPUS  ($(date))" | tee -a "$LOG"
  "$PYTHON" extract_v2.py --model "$MODEL" \
    --corpus "$CORPUS_DIR" \
    --method last_token \
    --layers all \
    --save-vectors 2>&1 | tail -40 | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "Phi extraction complete at $(date)" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "complete" > "$LOGDIR/done.marker"
exit 0
