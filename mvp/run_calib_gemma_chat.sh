#!/bin/bash
# DISAMBIGUATION: is Gemma's collapse under the raw format a real post-training effect, or is
# gemma-4-E2B-it simply out of distribution on raw few-shot text?
# The prereg already names the chat-template arm as a planned secondary condition; it is now the
# deciding test, not an optional extra. Instruct only - a base model has no chat template, and
# raw text IS its native format (base handled it fine: letter bias 0.050, ECE 0.0375).
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
exec >> "$LOG/calib_gemma_chat.log" 2>&1
echo "=== gemma chat-arm start $(date +%F_%H:%M:%S) ==="
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000; CHUNK=250
f="results/workspace/calib/run_gemma-4-E2B_instruct_mmlu_cf_chat.json"
for pass_n in $(seq 1 30); do
  .venv/bin/python -c "
import json,sys
try: sys.exit(0 if json.load(open('$f'))['complete'] else 1)
except Exception: sys.exit(1)" && { echo "[done] chat arm $(date +%H:%M:%S)"; break; }
  [ "$(disk_gb)" -lt 4 ] && { echo "[GUARD] disk $(disk_gb)GB"; break; }
  .venv/bin/python calib_run.py --base models/gemma-4-E2B --instruct models/gemma-4-E2B-it \
      --tag gemma-4-E2B --benches mmlu_cf --only instruct --n-items 1500 --chunk $CHUNK --chat --chat-prefill "**" \
      >> "$LOG/calib_gemma_chat_worker.log" 2>&1 &
  pid=$!; sleep 30
  while kill -0 "$pid" 2>/dev/null; do
    u=$(swap_used_mb)
    [ "$u" -gt "$CEIL" ] && { echo "[GUARD] swap ${u}MB -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
    [ "$(disk_gb)" -lt 3 ] && { echo "[GUARD] disk -> kill"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
    sleep 15
  done
  wait "$pid" 2>/dev/null
  echo "[chunk] pass $pass_n swap $(swap_used_mb)MB disk $(disk_gb)GB $(date +%H:%M:%S)"
done
echo "=== chat arm ended $(date +%H:%M:%S) ==="
