#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/dl_olmo.log
export HF_HUB_ENABLE_HF_TRANSFER=0
for attempt in 1 2 3 4 5; do
  echo "[$(date '+%H:%M:%S')] attempt $attempt" >> "$LOG"
  .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download('allenai/OLMo-2-0425-1B',
                  allow_patterns=['*.json','*.safetensors','*.txt','*.model'],
                  max_workers=2)
print('DOWNLOAD OK')" >> "$LOG" 2>&1 && { echo "[$(date '+%H:%M:%S')] DONE" >> "$LOG"; break; }
  echo "[$(date '+%H:%M:%S')] attempt $attempt failed/stalled, retrying" >> "$LOG"
  sleep 10
done
