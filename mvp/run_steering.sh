#!/bin/bash
# Launch the Qwen3-4B steering sweep in the background, unattended.
#
# Writes:
#   results/steering/qwen3-4b/run.log          — running log
#   results/steering/qwen3-4b/summary.jsonl    — row per generation
#   results/steering/qwen3-4b/<vec>/<alpha>/<pid>.json — each result
#
# Usage:
#   cd mvp && bash run_steering.sh              # runs in foreground (logs stream)
#   cd mvp && nohup bash run_steering.sh &      # runs in background, survives disconnect
#
# Resume-safe: already-generated files are skipped. Safe to kill and restart.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=".venv/bin/python"
LOG="results/steering/qwen3-4b/run.log"
mkdir -p "$(dirname "$LOG")"

echo "========================================" | tee -a "$LOG"
echo "Qwen3-4B Steering Sweep"                  | tee -a "$LOG"
echo "Started: $(date)"                          | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

$PYTHON -u run_steering_sweep.py 2>&1 | tee -a "$LOG"

echo ""                                          | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "STEERING SWEEP COMPLETE"                  | tee -a "$LOG"
echo "Finished: $(date)"                         | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
