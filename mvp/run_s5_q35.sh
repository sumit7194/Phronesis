#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/v2_rest.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
w=0; while [ "$(swap_mb)" -gt 2000 ] && [ $w -lt 900 ]; do sleep 20; w=$((w+20)); done
note "RETRY S5-steer Qwen3.5-4B (swap $(swap_mb)MB, machine idle)"
.venv/bin/python mindedness_v2_steer.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B --layer 16 >> "$LOG" 2>&1 &
PY=$!
while kill -0 $PY 2>/dev/null; do
  u=$(swap_mb); [ "${u:-0}" -gt 11000 ] && { note "ABORT retry swap ${u}MB"; kill -9 $PY; break; }
  sleep 20
done
wait $PY 2>/dev/null; note "END S5-steer Qwen3.5-4B retry rc=$?"
