#!/bin/bash
# V2 stages S3/S4/S5 — runs after the sweep finishes. Swap-guarded, incremental saves.
cd "$(dirname "$0")"
LOG=results/workspace/logs/v2_rest.log
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
# wait for the sweep to finish both models
while [ ! -f results/workspace/V2_SWEEP_DONE ]; do sleep 60; done
note "=== v2 stages S3/S4/S5 begin ==="
# S3 is pure analysis on the sweep JSON (no model load) - cheap, run first for both
guarded "S3-gw Qwen3-4B"      .venv/bin/python mindedness_v2_gw.py --tag Qwen3-4B
guarded "S3-gw Qwen3.5-4B"    .venv/bin/python mindedness_v2_gw.py --tag Qwen3_5-4B
guarded "S4-forced Qwen3-4B"  .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S5-steer Qwen3-4B"   .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S4-forced Qwen3.5-4B" .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "S5-steer Qwen3.5-4B" .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
touch results/workspace/V2_ALL_DONE
note "=== v2 program COMPLETE ==="
