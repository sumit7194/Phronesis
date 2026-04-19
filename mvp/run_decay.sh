#!/bin/bash
# Launch decay-steering experiment (E4 taxi prompt, hand_LT_L22 @ α₀=+8).
# Resume-safe — skips any tau_*.json already present.
#
# Usage:
#   cd mvp && bash run_decay.sh             # foreground
#   cd mvp && nohup bash run_decay.sh &     # background

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-detect python
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

LOG="results/decay_steering/qwen3-4b/e4_taxi_run.log"
mkdir -p "$(dirname "$LOG")"

echo "========================================" | tee -a "$LOG"
echo "Decay steering experiment (E4 taxi)"      | tee -a "$LOG"
echo "Started: $(date)"                          | tee -a "$LOG"
echo "Python: $PYTHON"                            | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

$PYTHON -u decay_steer_e4.py 2>&1 | tee -a "$LOG"

echo ""                                          | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "DECAY EXPERIMENT COMPLETE"                 | tee -a "$LOG"
echo "Finished: $(date)"                         | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
