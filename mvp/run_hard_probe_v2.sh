#!/bin/bash
# hard_probe_v2 — 19 items × 2 conditions. Mirrors GCP script.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "========================================"
echo "HARD PROBE V2 — 19 items × 2 conditions"
echo "Started: $(date)"
echo "========================================"

$PYTHON run_benchmark.py --benchmark hard_probe_v2 --n 19 --condition baseline
$PYTHON run_benchmark.py --benchmark hard_probe_v2 --n 19 --condition steered

$PYTHON rescore_benchmarks.py

echo ""
echo "ALL DONE: $(date)"
