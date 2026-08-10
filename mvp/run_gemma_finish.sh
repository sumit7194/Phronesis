#!/bin/bash
cd "$(dirname "$0")"
LOG=results/workspace/logs/crossfamily_tests.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
guarded(){ local l="$1"; shift; note "START $l"
  "$@" >> "$LOG" 2>&1 & local P=$!
  # GRACE PERIOD: loading a 10GB model adds more to swap than any leak allowance, so measuring the
  # baseline before the process starts makes the guard fire on the model load itself (2026-08-10).
  # Wait for the load to settle, THEN take the baseline and watch for growth from there.
  local w=0
  while kill -0 $P 2>/dev/null && [ $w -lt 240 ]; do sleep 15; w=$((w+15)); done
  local B=$(swap_mb); note "  baseline after load: ${B}MB (abort at +7000)"
  while kill -0 $P 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $l disk"; kill -9 $P; break; }
    [ "$(swap_mb)" -gt $((B+7000)) ] && { note "ABORT $l swap $(swap_mb)MB"; kill -9 $P; break; }
    sleep 20; done
  wait $P 2>/dev/null; note "END $l rc=$?"; }
D=models/gemma-4-E2B-it; T=Gemma4-E2B-Instruct
guarded "forced $T (resumed)" .venv/bin/python mindedness_v2_forced.py --model "$D" --tag "$T"
J=results/workspace/mindedness_v2_steer_$T.json
for i in $(seq 1 12); do
  N=$(.venv/bin/python -c "import json;d=json.load(open('$J'));print(sum(len(v) for v in d['runs'].values()))" 2>/dev/null || echo 0)
  [ "${N:-0}" -ge 27 ] && { note "steering $T complete ($N/27)"; break; }
  note "steering $T chunk $i ($N/27)"
  guarded "steer $T c$i" .venv/bin/python mindedness_v2_steer.py --model "$D" --tag "$T" --max-cells 3
  A=$(.venv/bin/python -c "import json;d=json.load(open('$J'));print(sum(len(v) for v in d['runs'].values()))" 2>/dev/null || echo 0)
  [ "${A:-0}" -le "${N:-0}" ] && { note "steering $T NO PROGRESS - stopping"; break; }
done
rm -rf "$D"; note "########## Gemma4-E2B-Instruct COMPLETE ##########"
