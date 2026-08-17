#!/bin/bash
# Decisive steering test. Prereg: docs/prereg-steering-decisive-2026-08-16.md
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
# The weights are cached; passing a hub id still makes transformers phone home, and a DNS blip
# killed round 3 with httpx.ConnectError. Offline mode removes the network from the critical path
# entirely - there is nothing to fetch.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
CEIL=13000
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
for round in $(seq 1 40); do
  [ "$(disk_gb)" -lt 4 ] && { echo "SKIP disk $(disk_gb)GB"; exit 1; }
  o=$(pgrep -fc "mindedness_(steer|v2|moral|decisive)" 2>/dev/null || echo 0)
  [ "$o" -gt 0 ] && { echo "ABORT: $o model jobs already running"; exit 1; }
  .venv/bin/python mindedness_steer_decisive.py --max-cells 12 \
      > "$LOG/decisive_r${round}.log" 2>&1 &
  pid=$!; sleep 60
  while kill -0 "$pid" 2>/dev/null; do
    u=$(swap_used_mb)
    [ "$u" -gt "$CEIL" ] && { echo "GUARD swap ${u}MB -> kill $pid"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; exit 1; }
    [ "$(disk_gb)" -lt 3 ] && { echo "GUARD disk -> kill $pid"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; exit 1; }
    sleep 20
  done
  wait "$pid"; rc=$?
  if [ $rc -ne 0 ]; then
    echo "round $round FAILED rc=$rc (attempt $(( ${FAILS:-0} + 1 )))"
    tail -4 "$LOG/decisive_r${round}.log"
    FAILS=$(( ${FAILS:-0} + 1 ))
    # every completed cell is on disk and the script resumes, so a transient fault should cost
    # one round, not the run. Three consecutive failures means it is not transient.
    [ "$FAILS" -ge 3 ] && { echo "3 consecutive failures - stopping"; exit 1; }
    sleep 30; continue
  fi
  FAILS=0
  if ! grep -q "^\[chunk\]" "$LOG/decisive_r${round}.log"; then
    echo "DECISIVE COMPLETE in $round round(s)"
    sed -n '/=== DECISIVE TEST/,$p' "$LOG/decisive_r${round}.log"
    exit 0
  fi
  echo "round $round done ($(date +%H:%M:%S))"
done
echo "did not finish in 40 rounds"; exit 1
