#!/bin/bash
# AIME repeat run at 8192-token cap (replication + token-budget ablation of F93)
# Compares against archived 4096-cap results in results/benchmark_probe/aime_4096cap_archived/

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "========================================"
echo "AIME REPEAT (8192 cap)"
echo "Started: $(date)"
echo "========================================"

$PYTHON run_benchmark.py --benchmark aime --n 5 --condition baseline
$PYTHON run_benchmark.py --benchmark aime --n 5 --condition steered

$PYTHON rescore_benchmarks.py

echo ""
echo "ALL DONE: $(date)"
