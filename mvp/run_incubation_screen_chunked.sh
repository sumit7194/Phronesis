#!/bin/bash
# Chunked driver for incubation_screen.py on the 16GB Mac: each long-generation stretch
# grows swap until the script's own 3GB disk guard stops it (resumable); we wait for the
# OS to reclaim swap, clean stale MPS graph caches, and resume. Ends when the screen
# prints [done] with all items or after MAX_CHUNKS.
cd "$(dirname "$0")"
PY=.venv/bin/python
LOG=results/workspace/logs/incubation_screen.log
MASTER=results/workspace/logs/incubation_chunks.log
MAX_CHUNKS=30
note() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER"; }

free_gib() { df -g / | tail -1 | awk '{print $4}'; }

for chunk in $(seq 1 $MAX_CHUNKS); do
  # wait (up to 20 min) for swap reclaim to give us headroom
  waited=0
  while [ "$(free_gib)" -lt 7 ] && [ $waited -lt 1200 ]; do sleep 60; waited=$((waited+60)); done
  # stale MPS graph cache files are pure cache; clear ones older than 30 min
  find "$(getconf DARWIN_USER_CACHE_DIR)" -maxdepth 2 -name "mpsgraph*" -mmin +30 -delete 2>/dev/null
  note "chunk $chunk start (free $(free_gib)G)"
  "$PY" incubation_screen.py --sets gsm8k_probe,math500 >> "$LOG" 2>&1
  rc=$?
  done_line=$(grep "\[done\]" "$LOG" | tail -1)
  note "chunk $chunk end rc=$rc :: $done_line"
  # finished for real (not a guard stop) when the [STOP] marker is absent after the last run
  if tail -5 "$LOG" | grep -q "\[done\]" && ! tail -8 "$LOG" | grep -q "\[STOP\]"; then
    note "screen complete"
    break
  fi
done
touch results/workspace/SCREEN_DONE
