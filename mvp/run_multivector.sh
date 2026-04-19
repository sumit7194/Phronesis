#!/bin/bash
# Launch multi-vector steering experiment.
#
# Usage:
#   cd mvp && bash run_multivector.sh           # foreground
#   cd mvp && nohup bash run_multivector.sh &   # background
#
# Resume-safe: re-running skips any (config, prompt) cell that already has a JSON.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-detect python: prefer .venv, fall back to python3 (GCP)
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

LOG="results/multivector/qwen3-4b/run.log"
mkdir -p "$(dirname "$LOG")"

echo "========================================" | tee -a "$LOG"
echo "Multi-vector steering experiment"          | tee -a "$LOG"
echo "Started: $(date)"                          | tee -a "$LOG"
echo "Python: $PYTHON"                            | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

$PYTHON -u run_multivector.py 2>&1 | tee -a "$LOG"

echo ""                                          | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "MULTI-VECTOR EXPERIMENT COMPLETE"          | tee -a "$LOG"
echo "Finished: $(date)"                         | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
