#!/bin/bash
# Fires the probe-mass validity check as soon as the decisive test frees the machine.
set -u
cd "$(dirname "$0")"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
LOG=results/workspace/logs
while pgrep -f "mindedness_steer_decisive|run_decisive_0816" >/dev/null; do sleep 30; done
sleep 20
.venv/bin/python mindedness_probe_mass.py --model Qwen/Qwen3-4B --tag Qwen3-4B --formats T1,T4 \
    > "$LOG/probemass_Qwen3-4B.log" 2>&1
echo "PROBEMASS DONE"
sed -n '/^=== /,$p' "$LOG/probemass_Qwen3-4B.log"
