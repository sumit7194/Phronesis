#!/bin/bash
# Base vs instruct comparison. Tests all three of the user's hypotheses at once:
#   moral standing / soul-as-language / agreeableness — post-training or pretraining?
# Gate first: a base model that cannot do the yes/no task would produce a fake null.
cd "$(dirname "$0")"
LOG=results/workspace/logs/base_models.log
THRESH_MB=9000; FAILED=""
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
settle(){ local w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 900 ]; do sleep 20; w=$((w+20)); done; }
guarded(){
  local label="$1"; shift; settle; note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    u=$(swap_mb); [ "${u:-0}" -gt "$THRESH_MB" ] && { note "ABORT $label swap ${u}MB"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; local rc=$?; note "END $label rc=$rc"; return $rc
}
run_one(){   # run_one <hf-id> <tag>
  local ID="$1" TAG="$2"
  note "=== $TAG: download ==="
  .venv/bin/python -c "
from huggingface_hub import snapshot_download
p=snapshot_download('$ID', allow_patterns=['*.json','*.safetensors','*.txt','*.model'])
print('cached at', p)" >> "$LOG" 2>&1 || { note "DOWNLOAD FAILED $TAG"; FAILED="$FAILED $TAG(dl)"; return; }
  if guarded "gate $TAG" .venv/bin/python mindedness_base_gate.py --model "$ID" --tag "$TAG"; then
    guarded "sweep $TAG" .venv/bin/python mindedness_v2_sweep.py --model "$ID" --tag "$TAG" \
      || FAILED="$FAILED $TAG(sweep)"
  else
    note "GATE FAILED for $TAG — skipping sweep, result would be about format not concepts"
    FAILED="$FAILED $TAG(gate)"
  fi
  df -h / | tail -1 | awk '{print "  disk free: "$4}' | tee -a "$LOG"
}
note "########## BASE vs INSTRUCT ##########"
run_one "Qwen/Qwen3-4B-Base"   "Qwen3-4B-Base"
run_one "Qwen/Qwen3.5-4B-Base" "Qwen3_5-4B-Base"
[ -z "$FAILED" ] && note "=== base-model program COMPLETE ===" || note "=== FINISHED WITH FAILURES:$FAILED ==="
