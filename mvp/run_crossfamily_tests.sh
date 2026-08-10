#!/bin/bash
# Remaining tests (speaker frame, subject framing, forced choice) on the non-Qwen models that
# qualify. Steering is excluded here: 3-5h per model, and the Qwen result was weak and mixed.
cd "$(dirname "$0")"
LOG=results/workspace/logs/crossfamily_tests.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
guarded(){
  local label="$1"; shift
  note "START $label"
  local BASE=$(swap_mb)
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $label disk"; kill -9 $PY; break; }
    [ "$(swap_mb)" -gt $((BASE+7000)) ] && { note "ABORT $label swap"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; note "END $label rc=$?"
}
run_model(){
  local ID="$1" TAG="$2" DIR="models/$(basename "$1")"
  note "fetch/verify $TAG"
  ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1 || { note "FETCH FAILED $TAG"; return; }
  .venv/bin/python -c "
from transformers import AutoTokenizer, AutoConfig; import sys
AutoTokenizer.from_pretrained('$DIR'); AutoConfig.from_pretrained('$DIR')" >> "$LOG" 2>&1 \
    || { note "MODEL DIR BROKEN $TAG - refetching"; rm -rf "$DIR"; ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1; }
  note "=== $TAG (formats from gate: $(.venv/bin/python -c "import json;print(','.join(json.load(open('results/workspace/mindedness_gate_$TAG.json')).get('usable_formats') or ['none']))" 2>/dev/null)) ==="
  guarded "speaker $TAG"  .venv/bin/python mindedness_speaker_frame.py --model "$DIR" --tag "$TAG"
  guarded "subject $TAG"  .venv/bin/python mindedness_v3_run.py        --model "$DIR" --tag "$TAG"
  guarded "forced $TAG"   .venv/bin/python mindedness_v2_forced.py     --model "$DIR" --tag "$TAG"
  # steering, 27 cells, chunked 3 at a time in fresh processes
  local OUTJ="results/workspace/mindedness_v2_steer_$TAG.json"
  for i in $(seq 1 12); do
    local N=$(.venv/bin/python -c "import json;d=json.load(open('$OUTJ'));print(sum(len(v) for v in d['runs'].values()))" 2>/dev/null || echo 0)
    [ "${N:-0}" -ge 27 ] && { note "steering $TAG complete ($N/27)"; break; }
    note "steering $TAG chunk $i ($N/27 cells)"
    guarded "steer $TAG c$i" .venv/bin/python mindedness_v2_steer.py --model "$DIR" --tag "$TAG" --max-cells 3
    local A=$(.venv/bin/python -c "import json;d=json.load(open('$OUTJ'));print(sum(len(v) for v in d['runs'].values()))" 2>/dev/null || echo 0)
    [ "${A:-0}" -le "${N:-0}" ] && { note "steering $TAG made NO PROGRESS - stopping"; break; }
  done
  rm -rf "$DIR"; note "$TAG done, weights removed ($(free_gb)Gi free)"
}
note "########## remaining cross-family tests ##########"
run_model allenai/OLMo-2-0425-1B-Instruct OLMo2-1B-Instruct
run_model google/gemma-4-E2B-it           Gemma4-E2B-Instruct
run_model allenai/OLMo-2-0425-1B          OLMo2-1B-Base
note "########## remaining cross-family tests COMPLETE ##########"
