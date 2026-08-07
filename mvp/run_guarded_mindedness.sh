#!/bin/bash
# Guarded run: kills our job (never the user's) if swap exceeds THRESH_MB, protecting far_deep.py
cd "$(dirname "$0")"
THRESH_MB=4000
LOG=results/workspace/logs/mindedness_$2.log
.venv/bin/python mindedness_geometry.py --model "$1" --tag "$2" --no-readout >> "$LOG" 2>&1 &
PY=$!
echo "[guard] pid=$PY model=$1 swap-abort at ${THRESH_MB}MB" >> "$LOG"
while kill -0 $PY 2>/dev/null; do
  used=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
  if [ "${used:-0}" -gt "$THRESH_MB" ]; then
    echo "[guard] ABORT: swap ${used}MB > ${THRESH_MB}MB — killing our run to protect other jobs" >> "$LOG"
    kill -9 $PY; exit 9
  fi
  sleep 20
done
wait $PY; echo "[guard] finished rc=$?" >> "$LOG"
