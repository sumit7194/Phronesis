#!/bin/bash
cd "$(dirname "$0")"
./run_battery.sh allenai/OLMo-2-0425-1B          OLMo2-1B-Base
./run_battery.sh allenai/OLMo-2-0425-1B-Instruct OLMo2-1B-Instruct
echo "[$(date '+%m-%d %H:%M:%S')] === cross-family pass 1 (OLMo) done ===" \
  | tee -a results/workspace/logs/battery_OLMo2-1B-Instruct.log
