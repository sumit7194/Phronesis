#!/bin/bash
# Re-sweep the two cross-family models under the per-template code, so we can slice out the
# formats they cannot parse. Both handle only 1 of 4 formats; the originals averaged all four.
cd "$(dirname "$0")"
LOG=results/workspace/logs/crossfamily_redo.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
# wait for the Gemma-instruct battery to finish (it owns the GPU and the disk)
while pgrep -f "run_gemma4.sh|run_battery.sh" > /dev/null; do sleep 120; done
note "=== cross-family re-sweep begins (disk $(df -g / | tail -1 | awk '{print $4}')Gi) ==="
for M in "allenai/OLMo-2-0425-1B:OLMo2-1B-Base" "google/gemma-4-E2B:Gemma4-E2B-Base"; do
  ID="${M%%:*}"; TAG="${M#*:}"; DIR="models/$(basename "$ID")"
  note "fetch $TAG"
  ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1 || { note "FETCH FAILED $TAG"; continue; }
  note "re-sweep $TAG (per-template)"
  .venv/bin/python mindedness_v2_sweep.py --model "$DIR" --tag "$TAG" >> "$LOG" 2>&1
  note "END re-sweep $TAG rc=$?"
  rm -rf "$DIR" results/workspace/.v2ckpt_${TAG}_*.npz
  note "cleaned up (disk $(df -g / | tail -1 | awk '{print $4}')Gi)"
done
note "=== cross-family re-sweep COMPLETE ==="
