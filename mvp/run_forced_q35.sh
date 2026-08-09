#!/bin/bash
# Deliberately simple. Three wrapper bugs today came from clever conditions: a stale-swap cascade,
# a settle threshold below idle swap, and a pgrep pattern that matched its own command line.
cd "$(dirname "$0")"
LOG=results/workspace/logs/qwen_finish.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
BASE=$(swap_mb)
note "RETRY forced Qwen3.5-4B (sliced unembed; baseline swap ${BASE}MB, abort at +6000MB)"
.venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B >> "$LOG" 2>&1 &
PY=$!
while kill -0 $PY 2>/dev/null; do
  u=$(swap_mb)
  if [ "${u:-0}" -gt $((BASE+6000)) ]; then note "ABORT: swap ${u}MB, +$((u-BASE))MB over baseline"; kill -9 $PY; break; fi
  sleep 20
done
wait $PY 2>/dev/null; note "END forced Qwen3.5-4B rc=$? (swap $(swap_mb)MB vs baseline ${BASE}MB)"
