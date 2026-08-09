#!/bin/bash
cd "$(dirname "$0")"
./run_battery.sh models/OLMo-2-0425-1B OLMo2-1B-Base --keep
./fetch_model.sh allenai/OLMo-2-0425-1B-Instruct models/OLMo-2-0425-1B-Instruct \
  >> results/workspace/logs/fetch_olmo_inst.log 2>&1
./run_battery.sh models/OLMo-2-0425-1B-Instruct OLMo2-1B-Instruct
rm -rf models/OLMo-2-0425-1B
echo "[$(date '+%m-%d %H:%M:%S')] === OLMo pair COMPLETE ===" >> results/workspace/logs/battery_OLMo2-1B-Instruct.log
