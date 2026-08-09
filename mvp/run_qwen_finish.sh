#!/bin/bash
# Finish the outstanding Qwen work using only CACHED models (Qwen3-4B, Qwen3.5-4B, Qwen3.5-4B-Base).
cd "$(dirname "$0")"
LOG=results/workspace/logs/qwen_finish.log
FAILED=""; RAN=0
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
guarded(){
  local label="$1"; shift
  local w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 900 ]; do sleep 20; w=$((w+20)); done
  note "START $label"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $label disk"; kill -9 $PY; break; }
    [ "$(swap_mb)" -gt 9000 ] && { note "ABORT $label swap"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; local rc=$?; note "END $label rc=$rc"
  [ $rc -ne 0 ] && FAILED="$FAILED $label" || RAN=$((RAN+1))
}
note "########## finishing Qwen battery (cached models only) ##########"
# cheap first
guarded "truth Qwen3.5-Base"   .venv/bin/python mindedness_v3_truthcheck.py --model Qwen/Qwen3.5-4B-Base --tag Qwen3_5-4B-Base
guarded "speaker Qwen3-4B"     .venv/bin/python mindedness_speaker_frame.py --model Qwen/Qwen3-4B --tag Qwen3-4B
# test 7 — three review rounds, never run
guarded "subject Qwen3-4B"     .venv/bin/python mindedness_v3_run.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "subject Qwen3.5-4B"   .venv/bin/python mindedness_v3_run.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
guarded "subject Qwen3.5-Base" .venv/bin/python mindedness_v3_run.py --model Qwen/Qwen3.5-4B-Base --tag Qwen3_5-4B-Base
# test 5 — rewritten after the first-token bug, never re-run
guarded "forced Qwen3-4B"      .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3-4B   --tag Qwen3-4B
guarded "forced Qwen3.5-4B"    .venv/bin/python mindedness_v2_forced.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B
if [ -z "$FAILED" ]; then note "########## QWEN BATTERY COMPLETE ($RAN stages) ##########"
else note "########## FINISHED: $RAN ok, FAILURES:$FAILED ##########"; fi
