#!/bin/bash
# Gemma-3-4b base+instruct: the real size-matched cross-family test.
# Gemma3ForConditionalGeneration is multimodal, like Qwen3.5 — the AutoModel fallback and
# model.forward() path in our scripts already handle that.
cd "$(dirname "$0")"
LOG=results/workspace/logs/gemma.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
# don't collide with the OLMo run still in flight
while pgrep -f "mindedness_|fetch_model.sh" > /dev/null; do sleep 60; done
note "=== Gemma pair start (disk $(df -g / | tail -1 | awk '{print $4}')Gi) ==="
for M in "google/gemma-3-4b-pt:Gemma3-4B-Base" "google/gemma-3-4b-it:Gemma3-4B-Instruct"; do
  ID="${M%%:*}"; TAG="${M#*:}"; DIR="models/$(basename "$ID")"
  note "fetch $TAG"
  ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1 || { note "FETCH FAILED $TAG"; continue; }
  ./run_battery.sh "$DIR" "$TAG"          # battery deletes the weights when done
done
note "=== Gemma pair COMPLETE ==="
