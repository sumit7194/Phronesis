#!/bin/bash
cd "$(dirname "$0")"
for spec in "Qwen/Qwen3.5-4B:Qwen3_5-4B" "Qwen/Qwen3-4B:Qwen3-4B"; do
  M="${spec%%:*}"; T="${spec##*:}"
  echo "=== $M ===" >> results/workspace/logs/mindedness_clean.log
  .venv/bin/python mindedness_clean.py --model "$M" --tag "$T" >> results/workspace/logs/mindedness_clean.log 2>&1
done
touch results/workspace/CLEAN_SWEEP_DONE
