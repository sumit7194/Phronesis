#!/bin/bash
# V3 subject-framing vector comparison. Waits for the v2 chain to clear MPS first.
cd "$(dirname "$0")"
LOG=results/workspace/logs/v3_vectors.log
THRESH_MB=7000; SETTLE_MB=4000; FAILED=""
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
settle(){ local w=0; while [ "$(swap_mb)" -gt "$SETTLE_MB" ] && [ $w -lt 600 ]; do sleep 15; w=$((w+15)); done; note "settled: swap $(swap_mb)MB"; }
guarded(){
  local label="$1"; shift; settle; note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    u=$(swap_mb); [ "${u:-0}" -gt "$THRESH_MB" ] && { note "ABORT $label swap ${u}MB"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; local rc=$?; note "END $label rc=$rc"
  [ $rc -ne 0 ] && FAILED="$FAILED $label"; return 0
}
while pgrep -f "mindedness_v2_" > /dev/null; do sleep 60; done
note "=== v3 subject-framing vectors ==="
guarded "v3-vectors Qwen3-4B"   .venv/bin/python mindedness_v3_vectors.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "v3-vectors Qwen3.5-4B" .venv/bin/python mindedness_v3_vectors.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
[ -z "$FAILED" ] && note "=== v3 COMPLETE (all rc=0) ===" || note "=== v3 FAILURES:$FAILED ==="
