#!/bin/bash
# Overnight hard-benchmark run: AIME + MATH-500 + ZebraLogic, baseline + steered.
# Total ~26 items, ~8 hours on MPS.
# Resume-safe.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "========================================"
echo "OVERNIGHT HARD BENCHMARK RUN"
echo "Started: $(date)"
echo "========================================"

$PYTHON run_benchmark.py --benchmark aime       --n 5 --condition baseline
$PYTHON run_benchmark.py --benchmark aime       --n 5 --condition steered
$PYTHON run_benchmark.py --benchmark math500    --n 5 --condition baseline
$PYTHON run_benchmark.py --benchmark math500    --n 5 --condition steered
$PYTHON run_benchmark.py --benchmark zebralogic --n 3 --condition baseline
$PYTHON run_benchmark.py --benchmark zebralogic --n 3 --condition steered

echo ""
echo "========================================"
echo "RESCORING"
echo "========================================"
$PYTHON rescore_benchmarks.py

echo ""
echo "========================================"
echo "ALL DONE: $(date)"
echo "========================================"
