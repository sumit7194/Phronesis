#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/v3_truth.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
while pgrep -f "mindedness_v2_steer" > /dev/null; do sleep 60; done
w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 600 ]; do sleep 20; w=$((w+20)); done
for M in "Qwen/Qwen3-4B:Qwen3-4B" "Qwen/Qwen3.5-4B:Qwen3_5-4B"; do
  note "START truthcheck ${M#*:}"
  .venv/bin/python mindedness_v3_truthcheck.py --model "${M%%:*}" --tag "${M#*:}" >> "$LOG" 2>&1
  note "END truthcheck ${M#*:} rc=$?"
done
note "=== v3 truthcheck done ==="
