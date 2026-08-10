#!/bin/bash
# Cross-family, take 3: gate SELECTS the format, sweep uses it.
cd "$(dirname "$0")"
LOG=results/workspace/logs/crossfamily_v2.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
run_one(){
  local ID="$1" TAG="$2" DIR="models/$(basename "$1")"
  # Skip only if the existing sweep was run with the GATE-SELECTED formats. Old files predate
  # format selection and are exactly what we are here to replace; a bare file-exists check skipped
  # all three invalid runs.
  local DONE=$(.venv/bin/python - "$TAG" <<'PYEOF'
import json, os, sys
tag = sys.argv[1]
sw = f"results/workspace/mindedness_v2_sweep_{tag}.json"
gt = f"results/workspace/mindedness_gate_{tag}.json"
try:
    used = json.load(open(sw)).get("formats_used")
    want = json.load(open(gt)).get("usable_formats")
    print("yes" if used and want and set(used) == set(want) else "no")
except Exception:
    print("no")
PYEOF
)
  if [ "$DONE" = "yes" ]; then note "SKIP $TAG - already run with selected formats"; return; fi
  if [ ! -d "$DIR" ]; then
    note "fetch $TAG"; ./fetch_model.sh "$ID" "$DIR" >> "$LOG" 2>&1 || { note "FETCH FAILED $TAG"; return; }
  else note "$TAG already local"; fi
  note "gate $TAG"
  .venv/bin/python mindedness_base_gate.py --model "$DIR" --tag "$TAG" >> "$LOG" 2>&1
  local U=$(.venv/bin/python -c "import json;print(','.join(json.load(open('results/workspace/mindedness_gate_$TAG.json'))['usable_formats']) or 'NONE')" 2>/dev/null)
  note "$TAG usable formats: ${U:-NONE}"
  if [ -z "$U" ] || [ "$U" = "NONE" ]; then note "SKIP sweep $TAG - no usable format"; rm -rf "$DIR"; return; fi
  note "sweep $TAG"
  BASE=$(swap_mb)
  .venv/bin/python mindedness_v2_sweep.py --model "$DIR" --tag "$TAG" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $TAG disk"; kill -9 $PY; break; }
    [ "$(swap_mb)" -gt $((BASE+7000)) ] && { note "ABORT $TAG swap"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; note "END sweep $TAG rc=$?"
  .venv/bin/python mindedness_v3_truthcheck.py --model "$DIR" --tag "$TAG" >> "$LOG" 2>&1
  note "END truth $TAG rc=$?"
  rm -rf "$DIR" results/workspace/.v2ckpt_${TAG}_*.npz
  note "cleaned ($(free_gb)Gi free)"
}
note "########## cross-family v2: format-selected ##########"
# Gemma4-E2B-Instruct: done 2026-08-10 (spread 0.73 sweep / 0.74 truth). Skip.
run_one allenai/OLMo-2-0425-1B-Instruct OLMo2-1B-Instruct
run_one google/gemma-4-E2B          Gemma4-E2B-Base
run_one allenai/OLMo-2-0425-1B      OLMo2-1B-Base
note "########## cross-family v2 COMPLETE ##########"
