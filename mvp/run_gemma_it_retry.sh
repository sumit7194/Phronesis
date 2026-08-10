#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/gemma4.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
while pgrep -f "run_battery.sh|mindedness_v2_sweep" > /dev/null; do sleep 60; done
note "RETRY Gemma4-E2B-Instruct with chat_template.jinja included"
./fetch_model.sh google/gemma-4-E2B-it models/gemma-4-E2B-it >> "$LOG" 2>&1 || { note "FETCH FAILED"; exit 1; }
ls models/gemma-4-E2B-it/chat_template.jinja >/dev/null 2>&1 && note "chat_template.jinja present" || note "WARNING: still no chat template"
./run_battery.sh models/gemma-4-E2B-it Gemma4-E2B-Instruct
