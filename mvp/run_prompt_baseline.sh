#!/bin/bash
# Launch prompt-baseline experiment (F68 gate).
# Resume-safe.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then PYTHON=".venv/bin/python"; else PYTHON="python3"; fi

LOG="results/prompt_baseline/qwen3-4b/run.log"
mkdir -p "$(dirname "$LOG")"

echo "========================================" | tee -a "$LOG"
echo "Prompt baseline (F68)"                    | tee -a "$LOG"
echo "Started: $(date)"                          | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

$PYTHON -u run_prompt_baseline.py 2>&1 | tee -a "$LOG"

echo ""                                          | tee -a "$LOG"
echo "PROMPT BASELINE COMPLETE — $(date)"       | tee -a "$LOG"
