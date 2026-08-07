#!/bin/bash
# Overnight facet program (docs/prereg-mindedness-facets.md). Sequential, swap-guarded,
# each stage saves independently so a failure never loses earlier work.
cd "$(dirname "$0")"
LOG=results/workspace/logs/overnight_facets.log
THRESH_MB=7000
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
guarded(){   # guarded <label> <cmd...>
  local label="$1"; shift
  note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    u=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
    [ "${u:-0}" -gt "$THRESH_MB" ] && { note "ABORT $label swap ${u}MB"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; note "END $label rc=$?"
}
# wait for any in-flight model job (screen / steering) to clear MPS first
while pgrep -f "mindedness_steer|mindedness_facets.py" > /dev/null; do sleep 30; done
note "=== overnight facet program begins ==="
guarded "S2-wide Qwen3-4B"    .venv/bin/python mindedness_facets_wide.py --model Qwen/Qwen3-4B   --tag Qwen3-4B   --decode
guarded "S2-wide Qwen3.5-4B"  .venv/bin/python mindedness_facets_wide.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "S4-steer Qwen3-4B"   .venv/bin/python mindedness_facet_steer.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S4-steer Qwen3.5-4B" .venv/bin/python mindedness_facet_steer.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
touch results/workspace/OVERNIGHT_FACETS_DONE
note "=== overnight facet program COMPLETE ==="
