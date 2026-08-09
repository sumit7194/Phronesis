#!/bin/bash
# Test 6 across all four Qwen models. Base models included: the prediction is that the framings
# COLLAPSE there (no self to address) and SEPARATE in the instruct models.
cd "$(dirname "$0")"
LOG=results/workspace/logs/speaker_frame.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
FAILED=""
for M in "Qwen/Qwen3-4B:Qwen3-4B" "Qwen/Qwen3.5-4B:Qwen3_5-4B" "Qwen/Qwen3.5-4B-Base:Qwen3_5-4B-Base"; do
  ID="${M%%:*}"; TAG="${M#*:}"
  w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 600 ]; do sleep 20; w=$((w+20)); done
  note "START speaker $TAG (disk $(free_gb)Gi)"
  .venv/bin/python mindedness_speaker_frame.py --model "$ID" --tag "$TAG" >> "$LOG" 2>&1 &
  PY=$!
  while kill -0 $PY 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $TAG disk"; kill -9 $PY; break; }
    [ "$(swap_mb)" -gt 9000 ] && { note "ABORT $TAG swap"; kill -9 $PY; break; }
    sleep 15
  done
  wait $PY 2>/dev/null; rc=$?; note "END speaker $TAG rc=$rc"
  [ $rc -ne 0 ] && FAILED="$FAILED $TAG"
done
[ -z "$FAILED" ] && note "=== speaker-frame COMPLETE ===" || note "=== FAILURES:$FAILED ==="
