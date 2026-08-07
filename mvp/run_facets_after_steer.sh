#!/bin/bash
cd "$(dirname "$0")"
# wait for the Qwen3.5 steering run to finish so we never have two models on MPS
while pgrep -f "mindedness_steer" > /dev/null; do sleep 30; done
for spec in "Qwen/Qwen3-4B:Qwen3-4B" "Qwen/Qwen3.5-4B:Qwen3_5-4B"; do
  M="${spec%%:*}"; T="${spec##*:}"
  echo "=== $M $(date '+%H:%M') ===" >> results/workspace/logs/mindedness_facets.log
  .venv/bin/python mindedness_facets.py --model "$M" --tag "$T" >> results/workspace/logs/mindedness_facets.log 2>&1
done
touch results/workspace/FACETS_DONE
