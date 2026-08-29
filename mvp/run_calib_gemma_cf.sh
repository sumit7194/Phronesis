#!/bin/bash
# Gemma-4-E2B base vs instruct on MMLU-CF. Second family for the calibration arc.
# Prereg: docs/prereg-calibration-2026-08-28.md - protocol unchanged, new checkpoint pair.
# mmlu_pro EXCLUDED by the pre-set band gate (base 0.242 vs 0.35 floor). See GEMMA_PILOT_VERDICT.md.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
exec >> "$LOG/calib_gemma_cf.log" 2>&1
echo "=== gemma mmlu_cf start $(date +%F_%H:%M:%S) ==="
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000; CHUNK=250
B=models/gemma-4-E2B; I=models/gemma-4-E2B-it; TAG=gemma-4-E2B

run_cell () {
  local r=$1 f="results/workspace/calib/run_${TAG}_${r}_mmlu_cf_raw.json"
  for pass_n in $(seq 1 30); do
    .venv/bin/python -c "
import json,sys
try: sys.exit(0 if json.load(open('$f'))['complete'] else 1)
except Exception: sys.exit(1)" && { echo "[done] mmlu_cf/$r $(date +%H:%M:%S)"; return 0; }
    [ "$(disk_gb)" -lt 4 ] && { echo "[GUARD] disk $(disk_gb)GB - stopping, work is checkpointed"; return 1; }
    .venv/bin/python calib_run.py --base "$B" --instruct "$I" --tag "$TAG" \
        --benches mmlu_cf --only "$r" --n-items 1500 --chunk $CHUNK \
        >> "$LOG/calib_gemma_cf_${r}.log" 2>&1 &
    local pid=$!; sleep 30
    while kill -0 "$pid" 2>/dev/null; do
      u=$(swap_used_mb)
      [ "$u" -gt "$CEIL" ] && { echo "[GUARD] swap ${u}MB -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[GUARD] disk -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      sleep 15
    done
    wait "$pid" 2>/dev/null
    echo "[chunk] $r pass $pass_n  swap $(swap_used_mb)MB  disk $(disk_gb)GB  $(date +%H:%M:%S)"
  done
  echo "[FAIL] mmlu_cf/$r did not finish"; return 1
}

OK=1
for r in base instruct; do run_cell "$r" || { OK=0; break; }; done
echo "=== analysis $(date +%H:%M:%S) ==="
.venv/bin/python calib_analyze.py --tag "$TAG" --arm raw
if [ "$OK" -eq 1 ]; then
  echo "GEMMA_CF_COMPLETE $(date +%F_%H:%M:%S)" > results/workspace/calib/GEMMA_DONE
  echo "=== complete ==="
else
  echo "=== FAILURES - no DONE marker ==="
fi
