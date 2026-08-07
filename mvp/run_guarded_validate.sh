#!/bin/bash
cd "$(dirname "$0")"
THRESH_MB=5000
LOG=results/workspace/logs/mindedness_validate.log
.venv/bin/python mindedness_validate.py --model "$1" --tag "$2" >> "$LOG" 2>&1 &
PY=$!
echo "[guard] pid=$PY swap-abort at ${THRESH_MB}MB" >> "$LOG"
while kill -0 $PY 2>/dev/null; do
  used=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1)
  if [ "${used:-0}" -gt "$THRESH_MB" ]; then
    echo "[guard] ABORT swap ${used}MB" >> "$LOG"; kill -9 $PY; exit 9; fi
  sleep 20
done
wait $PY; echo "[guard] finished rc=$?" >> "$LOG"
