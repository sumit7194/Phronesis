#!/bin/bash
# V2-S1/S2 full sweep, both models, swap-guarded. Prereg: docs/prereg-mindedness-v2.md
cd "$(dirname "$0")"
LOG=results/workspace/logs/v2_sweep.log
THRESH_MB=7000
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
guarded(){
  local label="$1"; shift
  note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    u=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
    [ "${u:-0}" -gt "$THRESH_MB" ] && { note "ABORT $label swap ${u}MB"; kill -9 $PY; break; }
    sleep 30
  done
  wait $PY 2>/dev/null; note "END $label rc=$?"
}
note "=== v2 sweep begins (26752 prompts/model) ==="
guarded "v2-sweep Qwen3-4B"   .venv/bin/python mindedness_v2_sweep.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "v2-sweep Qwen3.5-4B" .venv/bin/python mindedness_v2_sweep.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
touch results/workspace/V2_SWEEP_DONE
note "=== v2 sweep COMPLETE ==="
