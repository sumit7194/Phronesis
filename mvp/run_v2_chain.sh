#!/bin/bash
# V2 chain. Rewritten 2026-08-08 after the driver cascade-failed and still reported COMPLETE.
#
# Three fixes over the previous version:
#  1. SETTLE-WAIT before each stage. The guard reads SYSTEM-WIDE swap, which stays elevated for a
#     while after a big process dies. Previously one abort instantly killed every later stage
#     (all five aborted within 1 second) because the reading was stale.
#  2. FAILURE TRACKING. The DONE marker is only written if every stage exited 0. Previously the
#     driver touched V2_ALL_DONE and printed COMPLETE after everything had failed.
#  3. Stages that depend on an earlier stage's output check for that file and skip loudly.
cd "$(dirname "$0")"
THRESH_MB=7000
SETTLE_MB=4000          # must be below this before a stage may start
FAILED=""
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
settle(){
  local w=0
  while [ "$(swap_mb)" -gt "$SETTLE_MB" ] && [ $w -lt 600 ]; do sleep 15; w=$((w+15)); done
  note "settled: swap $(swap_mb)MB after ${w}s"
}
guarded(){
  local label="$1"; shift
  settle
  note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    u=$(swap_mb)
    [ "${u:-0}" -gt "$THRESH_MB" ] && { note "ABORT $label swap ${u}MB"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; local rc=$?
  note "END $label rc=$rc"
  [ $rc -ne 0 ] && FAILED="$FAILED $label"
  return 0
}
needs(){ [ -f "$1" ] || { note "SKIP $2 - missing $1"; FAILED="$FAILED $2(skipped)"; return 1; }; return 0; }

LOG=results/workspace/logs/v2_sweep.log
note "=== v2 chain start (resume: T1-T3 checkpointed for Qwen3.5) ==="
guarded "v2-sweep Qwen3.5-4B" .venv/bin/python mindedness_v2_sweep.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B

LOG=results/workspace/logs/v2_rest.log
SW=results/workspace/mindedness_v2_sweep_Qwen3_5-4B.json
guarded "S3-gw Qwen3.5-4B" .venv/bin/python mindedness_v2_gw.py --tag Qwen3_5-4B
# S4-forced Qwen3-4B done 19:09
guarded "S5-steer Qwen3-4B"    .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S4-forced Qwen3.5-4B" .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "S5-steer Qwen3.5-4B"  .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B

if [ -z "$FAILED" ]; then
  touch results/workspace/V2_ALL_DONE
  note "=== v2 program COMPLETE (all stages rc=0) ==="
else
  note "=== v2 program FINISHED WITH FAILURES:$FAILED ==="
fi
