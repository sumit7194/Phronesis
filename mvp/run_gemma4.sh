#!/bin/bash
# Gemma-4 base+instruct. Bare name = base, -it = instruct. Ungated.
# Fixed 2026-08-09: the previous version checked disk once, SKIPPED both models because a prior
# job's weights had not been cleaned up yet, and then printed COMPLETE. It now WAITS for space and
# reports honestly if nothing ran.
cd "$(dirname "$0")"
LOG=results/workspace/logs/gemma4.log
SIZE="${1:-E2B}"; NEED="${2:-13}"
RAN=0; SKIPPED=""
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
while pgrep -f "mindedness_|fetch_model.sh" > /dev/null; do sleep 60; done
note "=== Gemma-4-$SIZE pair start (disk $(free_gb)Gi, need ${NEED}Gi) ==="
for M in "google/gemma-4-$SIZE:Gemma4-$SIZE-Base" "google/gemma-4-$SIZE-it:Gemma4-$SIZE-Instruct"; do
  ID="${M%%:*}"; TAG="${M#*:}"; DIR="models/$(basename "$ID")"
  w=0
  while [ "$(free_gb)" -lt "$NEED" ] && [ $w -lt 1800 ]; do
    [ $((w % 300)) -eq 0 ] && note "waiting for disk: $(free_gb)Gi < ${NEED}Gi"
    sleep 60; w=$((w+60))
  done
  if [ "$(free_gb)" -lt "$NEED" ]; then
    note "SKIP $TAG — still only $(free_gb)Gi after 30min"; SKIPPED="$SKIPPED $TAG"; continue
  fi
  note "fetch $TAG"
  ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1 || { note "FETCH FAILED $TAG"; rm -rf "$DIR"; SKIPPED="$SKIPPED $TAG(fetch)"; continue; }
  ./run_battery.sh "$DIR" "$TAG" && RAN=$((RAN+1))
done
if [ "$RAN" -eq 0 ]; then note "=== Gemma-4-$SIZE: NOTHING RAN.$SKIPPED ==="
elif [ -n "$SKIPPED" ]; then note "=== Gemma-4-$SIZE: $RAN ran, skipped:$SKIPPED ==="
else note "=== Gemma-4-$SIZE pair COMPLETE ($RAN models) ==="; fi
