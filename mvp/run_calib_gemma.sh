#!/bin/bash
# Second family for the calibration arc: Gemma-4-E2B base vs instruct.
# Prereg: docs/prereg-calibration-2026-08-28.md (protocol unchanged; new checkpoint pair).
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
MAIN=$LOG/calib_gemma.log
exec >> "$MAIN" 2>&1
echo "=== gemma arc start $(date +%F_%H:%M:%S) ==="
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000
CHUNK=250
B=models/gemma-4-E2B; I=models/gemma-4-E2B-it; TAG=gemma-4-E2B

# 1. fetch, chained on exit code (a partial shard passes any file-existence test)
./run_fetch_gemma_pair.sh || { echo "[ABORT] fetch failed"; exit 1; }
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # only AFTER the fetch; it needs the Hub API

# 2. pilot: same pre-set gates (band [0.35,0.80], letter mass >=0.50, <=10% under 0.10 mass).
#    Gemma is the harder test - F-AU found gemma-4-E2B-it pinning 37.8% of cells on the Yes/No
#    readout, a 3x outlier. If it fails the probe gate here that is a RESULT about the model,
#    not a broken experiment, and the run stops rather than scoring noise.
echo "=== pilot $(date +%H:%M:%S) ==="
.venv/bin/python calib_pilot.py --base "$B" --instruct "$I" --tag "$TAG" \
    --n-items 200 --n-perm 2 > "$LOG/calib_gemma_pilot.log" 2>&1
rc=$?
sed -n '/^====/,$p' "$LOG/calib_gemma_pilot.log"
[ $rc -ne 0 ] && { echo "[ABORT] pilot failed rc=$rc"; tail -20 "$LOG/calib_gemma_pilot.log"; exit 1; }
QUAL=$(.venv/bin/python -c "
import json;print(','.join(json.load(open('results/workspace/calib/pilot_${TAG}_SUMMARY.json'))['qualifying']))")
[ -z "$QUAL" ] && { echo "[STOP] no benchmark qualifies for $TAG - reporting that, not forcing a run"; exit 1; }
echo "[pilot] qualifying: $QUAL"

# 3. full run, chunked from the start (learned on mmlu_pro: one long process creeps 4.3->12.4s/pass)
run_cell () {
  local b=$1 r=$2
  for pass_n in $(seq 1 30); do
    local f="results/workspace/calib/run_${TAG}_${r}_${b}_raw.json"
    .venv/bin/python -c "
import json,sys
try: sys.exit(0 if json.load(open('$f'))['complete'] else 1)
except Exception: sys.exit(1)" && { echo "[done] $b/$r $(date +%H:%M:%S)"; return 0; }
    [ "$(disk_gb)" -lt 4 ] && { echo "[GUARD] disk $(disk_gb)GB"; return 1; }
    .venv/bin/python calib_run.py --base "$B" --instruct "$I" --tag "$TAG" \
        --benches "$b" --only "$r" --n-items 1500 --chunk $CHUNK \
        >> "$LOG/calib_gemma_${b}_${r}.log" 2>&1 &
    local pid=$!; sleep 30
    while kill -0 "$pid" 2>/dev/null; do
      u=$(swap_used_mb)
      [ "$u" -gt "$CEIL" ] && { echo "[GUARD] swap ${u}MB -> kill (checkpoint keeps the work)"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[GUARD] disk -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      sleep 15
    done
    wait "$pid" 2>/dev/null
    echo "[chunk] $b/$r pass $pass_n swap $(swap_used_mb)MB $(date +%H:%M:%S)"
  done
  echo "[FAIL] $b/$r did not finish"; return 1
}

OK=1
for b in $(echo "$QUAL" | tr ',' ' '); do
  for r in base instruct; do run_cell "$b" "$r" || { OK=0; break 2; }; done
done

echo "=== analysis $(date +%H:%M:%S) ==="
.venv/bin/python calib_analyze.py --tag "$TAG" --arm raw
if [ "$OK" -eq 1 ]; then
  echo "GEMMA_RUN_COMPLETE $(date +%F_%H:%M:%S)" > results/workspace/calib/GEMMA_DONE
  echo "=== all cells complete ==="
else
  echo "=== finished with FAILURES - no DONE marker ==="
fi
