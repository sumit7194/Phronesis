#!/bin/bash
# Fetch the Qwen3.5-4B base/instruct pair for the calibration pilot.
# Sequential on purpose: two concurrent 8GB pulls thrash disk and neither finishes sooner.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs/fetch_q35_pair.log
mkdir -p "$(dirname "$LOG")"
echo "--- fetch run $(date +%F_%H:%M:%S) ---" >> "$LOG"
free_mb() { df -m / | awk 'NR==2{print $4}'; }
for pair in "Qwen/Qwen3.5-4B-Base models/Qwen3.5-4B-Base" "Qwen/Qwen3.5-4B models/Qwen3.5-4B"; do
  set -- $pair; ID="$1"; DEST="$2"
  # NO existence-based skip here. "weights present" is not "weights complete": after the
  # 2026-08-28 power cut the instruct model had a 2.37GB stub of a 5.08GB shard, which any
  # ls *.safetensors test passes. fetch_model.sh already compares every file against its
  # SERVER-REPORTED content-length and resumes with curl -C -, so let the thing that actually
  # verifies completeness decide. On an already-complete repo this costs a few HEAD requests.
  if [ "$(free_mb)" -lt 15000 ]; then
    echo "[ABORT] only $(free_mb)MB free, need ~15GB headroom" | tee -a "$LOG"; exit 1
  fi
  echo "[fetch] $ID -> $DEST  ($(free_mb)MB free)" | tee -a "$LOG"
  ./fetch_model.sh "$ID" "$DEST" >> "$LOG" 2>&1 || { echo "[FAIL] $ID" | tee -a "$LOG"; exit 1; }
done
echo "[done] pair ready  ($(free_mb)MB free)" | tee -a "$LOG"
