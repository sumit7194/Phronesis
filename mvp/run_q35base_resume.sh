#!/bin/bash
# Resume Qwen3.5-4B-Base sweep (killed by DISK pressure at T3; T1/T2 checkpointed).
cd "$(dirname "$0")"
LOG=results/workspace/logs/base_models.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
note "RESUME sweep Qwen3_5-4B-Base (disk $(free_gb)Gi free, T1/T2 checkpointed)"
.venv/bin/python mindedness_v2_sweep.py --model Qwen/Qwen3.5-4B-Base --tag Qwen3_5-4B-Base >> "$LOG" 2>&1 &
PY=$!
while kill -0 $PY 2>/dev/null; do
  d=$(free_gb); u=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
  [ "${d:-99}" -lt 3 ] && { note "ABORT: disk down to ${d}Gi"; kill -9 $PY; break; }
  [ "${u:-0}" -gt 9000 ] && { note "ABORT: swap ${u}MB"; kill -9 $PY; break; }
  sleep 20
done
wait $PY 2>/dev/null; note "END resume sweep rc=$? (disk $(free_gb)Gi free)"
