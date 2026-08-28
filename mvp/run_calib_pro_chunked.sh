#!/bin/bash
# MMLU-Pro, restarted in chunks. Prereg: docs/prereg-calibration-2026-08-28.md
# One 1500-item process degraded from 4.3s to 12.4s/pass and was still climbing (MPS allocator
# growth; mmlu_pro prompts are ~4x longer than mmlu_cf). Chunking bounds it: each process does
# CHUNK items and exits, and calib_run.py resumes from its own checkpoint.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
MAIN=$LOG/calib_pro_chunked.log
exec >> "$MAIN" 2>&1
echo "=== chunked mmlu_pro start $(date +%F_%H:%M:%S) ==="
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000
CHUNK=250

complete() {  # role -> 0 if that cell's json says complete
  .venv/bin/python -c "
import json,sys
try: sys.exit(0 if json.load(open('results/workspace/calib/run_Qwen3.5-4B_$1_mmlu_pro_raw.json'))['complete'] else 1)
except Exception: sys.exit(1)"
}

OK=1
for role in base instruct; do
  for pass_n in $(seq 1 30); do
    if complete "$role"; then echo "[done] mmlu_pro/$role $(date +%H:%M:%S)"; break; fi
    [ "$(disk_gb)" -lt 4 ] && { echo "[GUARD] disk $(disk_gb)GB - stop"; OK=0; break; }
    .venv/bin/python calib_run.py --benches mmlu_pro --only "$role" --n-items 1500 \
        --chunk $CHUNK >> "$LOG/calib_mmlu_pro_${role}.log" 2>&1 &
    pid=$!; sleep 30
    while kill -0 "$pid" 2>/dev/null; do
      u=$(swap_used_mb)
      [ "$u" -gt "$CEIL" ] && { echo "[GUARD] swap ${u}MB -> kill (checkpoint keeps the work)"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[GUARD] disk -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      sleep 15
    done
    wait "$pid" 2>/dev/null
    n=$(.venv/bin/python -c "
import json
try: print(len(json.load(open('results/workspace/calib/run_Qwen3.5-4B_${role}_mmlu_pro_raw.json'))['records']))
except Exception: print(0)")
    echo "[chunk] $role pass $pass_n -> $n records, swap $(swap_used_mb)MB $(date +%H:%M:%S)"
  done
  complete "$role" || { echo "[FAIL] mmlu_pro/$role did not finish"; OK=0; break; }
done

echo "=== analysis $(date +%H:%M:%S) ==="
.venv/bin/python calib_analyze.py --tag Qwen3.5-4B --arm raw
# s13: the marker depends on every cell, or it is a lie.
if [ "$OK" -eq 1 ]; then
  echo "CALIB_RUN_COMPLETE $(date +%F_%H:%M:%S)" > results/workspace/calib/RUN_DONE
  echo "=== all cells complete ==="
else
  echo "=== finished with FAILURES - no DONE marker ==="
fi
