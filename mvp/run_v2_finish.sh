#!/bin/bash
# Finish v2 after the second power loss (2026-08-08 21:57).
# Done already: both sweeps, S3 both models, S4-forced Qwen3-4B, S5 Qwen3-4B vectors + random0.
# Remaining: S5 Qwen3-4B random1-4 (resumes), S4-forced Qwen3.5, S5 Qwen3.5.
cd "$(dirname "$0")"
THRESH_MB=7000; SETTLE_MB=4000; FAILED=""
LOG=results/workspace/logs/v2_rest.log
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
settle(){ local w=0; while [ "$(swap_mb)" -gt "$SETTLE_MB" ] && [ $w -lt 600 ]; do sleep 15; w=$((w+15)); done; note "settled: swap $(swap_mb)MB after ${w}s"; }
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
note "=== v2 finish: remaining stages ==="
guarded "S5-steer Qwen3-4B (resume)" .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S4-forced Qwen3.5-4B"       .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "S5-steer Qwen3.5-4B"        .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
if [ -z "$FAILED" ]; then touch results/workspace/V2_ALL_DONE; note "=== v2 COMPLETE (all rc=0) ==="
else note "=== v2 FINISHED WITH FAILURES:$FAILED ==="; fi
