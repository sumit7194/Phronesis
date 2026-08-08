#!/bin/bash
# Resume after the 2026-08-08 power loss: Qwen3.5 sweep (checkpointed), then S3/S4/S5 chain.
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
note "=== RESUME after power loss ==="
guarded "v2-sweep Qwen3.5-4B" .venv/bin/python mindedness_v2_sweep.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
touch results/workspace/V2_SWEEP_DONE
note "=== sweep done, starting S3/S4/S5 ==="
LOG=results/workspace/logs/v2_rest.log
guarded "S3-gw Qwen3.5-4B"     .venv/bin/python mindedness_v2_gw.py --tag Qwen3_5-4B
guarded "S4-forced Qwen3-4B"   .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S5-steer Qwen3-4B"    .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "S4-forced Qwen3.5-4B" .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "S5-steer Qwen3.5-4B"  .venv/bin/python mindedness_v2_steer.py  --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
touch results/workspace/V2_ALL_DONE
note "=== v2 program COMPLETE ==="
