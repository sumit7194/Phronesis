#!/bin/bash
# hard_probe_v3 — follow-up sweep:
#   - 6 both-wrong items from v2 (aime/29, 35, 42, 51, 81, musr/murder_mysteries-92)
#   - 3 new humblebench items (fb-largest-desert, fb-nobel-einstein, fb-ww2-end control)
#
# Conditions run:
#   baseline         — only needed for new HB items (for the 6 v2 items, baseline
#                      is already in hard_probe_v2/baseline/)
#   steered_L20_a12  — default config; also only needed for new HB items
#   steered_L22_a12  — alt layer, same alpha; test attractor break
#   steered_L20_a8   — gentler alpha
#   steered_L20_a16  — stronger alpha
#
# Each steered_* config uses --label to separate output dirs so they don't
# collide. Total gens ~33:
#   3 HB × (baseline + L20@12) = 6
#   9 items × 3 alt configs = 27
#
# Estimated ~10–15h on T4.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "========================================"
echo "HARD PROBE V3 — follow-up sweep"
echo "Started: $(date)"
echo "========================================"

# New HB items: baseline + default steered
$PYTHON run_benchmark.py --benchmark hard_probe_v3 --n 9 --condition baseline --label baseline
$PYTHON run_benchmark.py --benchmark hard_probe_v3 --n 9 --condition steered --vector L20 --alpha 12 --label steered_L20_a12

# All 9 items: alt configs
$PYTHON run_benchmark.py --benchmark hard_probe_v3 --n 9 --condition steered --vector L22 --alpha 12 --label steered_L22_a12
$PYTHON run_benchmark.py --benchmark hard_probe_v3 --n 9 --condition steered --vector L20 --alpha 8  --label steered_L20_a8
$PYTHON run_benchmark.py --benchmark hard_probe_v3 --n 9 --condition steered --vector L20 --alpha 16 --label steered_L20_a16

$PYTHON rescore_benchmarks.py

echo ""
echo "ALL DONE: $(date)"
