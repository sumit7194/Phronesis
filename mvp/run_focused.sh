#!/bin/bash
# Launch the focused Qwen3-4B steering run (v2).
#
# Writes results to: results/steering_v2/qwen3-4b/
# Resume-safe: already-generated files are skipped.
#
# Usage:
#   cd mvp && bash run_focused.sh              # foreground
#   cd mvp && nohup bash run_focused.sh &      # background

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=".venv/bin/python"
LOG="results/steering_v2/qwen3-4b/run.log"
mkdir -p "$(dirname "$LOG")"

echo "========================================" | tee -a "$LOG"
echo "Qwen3-4B Focused Steering (v2)"          | tee -a "$LOG"
echo "Started: $(date)"                         | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

$PYTHON -u run_focused_steering.py 2>&1 | tee -a "$LOG"

echo ""                                         | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "FOCUSED RUN COMPLETE"                     | tee -a "$LOG"
echo "Finished: $(date)"                        | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
