#!/bin/bash
# STAGE 1 of the calibration study: benchmark selection pilot. Prereg comes AFTER this fixes the
# benchmark, and before any base-vs-instruct outcome is computed.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000   # swap USED ceiling. $7 is USED, not free - reading it as free made the guard fire
             # when healthy and stay silent when exhausted. 2026-08-12.

# Fetch, then run. Chained on the EXIT CODE, not on polling for files: the previous version
# counted *.safetensors and a 2.37GB stub of a 5.08GB shard counted as one. fetch_model.sh
# verifies every file against its server-reported size, so rc=0 is the only honest ready signal.
./run_fetch_q35_pair.sh || { echo "[ABORT] fetch failed - not starting pilot"; exit 1; }

# Offline ONLY after the fetch. Exporting it earlier would break fetch_model.sh, which lists
# repo files through HfApi. Once weights are local, offline keeps a DNS blip off the hot path.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

[ "$(disk_gb)" -lt 4 ] && { echo "SKIP disk $(disk_gb)GB"; exit 1; }
o=$(pgrep -fc "[p]ython.*calib_pilot.py" 2>/dev/null || echo 0)
[ "$o" -gt 0 ] && { echo "ABORT: $o pilot jobs already running"; exit 1; }

.venv/bin/python calib_pilot.py --n-items 200 --n-perm 2 > "$LOG/calib_pilot.log" 2>&1 &
pid=$!; sleep 45
while kill -0 "$pid" 2>/dev/null; do
  u=$(swap_used_mb)
  [ "$u" -gt "$CEIL" ] && { echo "GUARD swap ${u}MB -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; exit 1; }
  [ "$(disk_gb)" -lt 3 ] && { echo "GUARD disk -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; exit 1; }
  sleep 20
done
wait "$pid"; rc=$?
# NOTE: weights are NOT deleted here, on success or failure. An unconditional cleanup after a
# guard kill once destroyed 7.5GB of weights that the next run needed. 2026-08-12.
[ $rc -ne 0 ] && { echo "PILOT FAILED rc=$rc"; tail -20 "$LOG/calib_pilot.log"; exit 1; }
sed -n '/^====/,$p' "$LOG/calib_pilot.log"
echo "PILOT COMPLETE"
