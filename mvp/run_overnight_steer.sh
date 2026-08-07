#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/mindedness_steer.log
THRESH_MB=7000
for spec in "Qwen/Qwen3-4B:Qwen3-4B" "Qwen/Qwen3.5-4B:Qwen3_5-4B"; do
  M="${spec%%:*}"; T="${spec##*:}"
  echo "=== $M $(date '+%H:%M') ===" >> "$LOG"
  .venv/bin/python mindedness_steer.py --model "$M" --tag "$T" >> "$LOG" 2>&1 &
  PY=$!
  while kill -0 $PY 2>/dev/null; do
    used=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
    [ "${used:-0}" -gt "$THRESH_MB" ] && { echo "[guard] ABORT swap ${used}MB" >> "$LOG"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null
done
touch results/workspace/STEER_DONE
