#!/bin/bash
# Turnkey battery for ONE model. Usage: ./run_battery.sh <hf-id> <tag> [--keep]
# Runs: gate -> sweep -> factor analysis -> truth matrix -> speaker frame.
# Deletes the weights afterwards unless --keep, because every stage saves its own JSON and the
# weights are always re-fetchable. Steering (3-5h) and forced-choice are run separately.
cd "$(dirname "$0")"
ID="$1"; TAG="$2"; KEEP="$3"
[ -z "$TAG" ] && { echo "usage: $0 <hf-id> <tag> [--keep]"; exit 1; }
LOG=results/workspace/logs/battery_${TAG}.log
FAILED=""
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
free_gb(){ df -g / | tail -1 | awk '{print $4}'; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
guarded(){
  local label="$1"; shift
  local w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 600 ]; do sleep 20; w=$((w+20)); done
  note "START $label (disk $(free_gb)Gi, swap $(swap_mb)MB)"
  "$@" >> "$LOG" 2>&1 & local PY=$!
  while kill -0 $PY 2>/dev/null; do
    [ "$(free_gb)" -lt 3 ] && { note "ABORT $label: disk"; kill -9 $PY; break; }
    [ "$(swap_mb)" -gt 9000 ] && { note "ABORT $label: swap"; kill -9 $PY; break; }
    sleep 20
  done
  wait $PY 2>/dev/null; local rc=$?; note "END $label rc=$rc"
  [ $rc -ne 0 ] && FAILED="$FAILED $label"
  return $rc
}
note "########## BATTERY: $TAG ($ID) ##########"
# Local dir -> already fetched. Otherwise use fetch_model.sh (curl): the huggingface_hub
# downloader stalls at 0 B/s on this machine while curl to the same CDN gets 4 MB/s (2026-08-09).
if [ -d "$ID" ]; then
  note "using local weights at $ID"
else
  note "download via curl"
  ./fetch_model.sh "$ID" "models/$(basename "$ID")" >> "$LOG" 2>&1 || { note "DOWNLOAD FAILED"; exit 1; }
  ID="models/$(basename "$ID")"
fi

# GATE is blocking: a model that cannot do yes/no gives results about format, not concepts.
if guarded "gate" .venv/bin/python mindedness_base_gate.py --model "$ID" --tag "$TAG"; then
  guarded "sweep"    .venv/bin/python mindedness_v2_sweep.py      --model "$ID" --tag "$TAG"
  guarded "truth"    .venv/bin/python mindedness_v3_truthcheck.py --model "$ID" --tag "$TAG"
  guarded "speaker"  .venv/bin/python mindedness_speaker_frame.py --model "$ID" --tag "$TAG"
  [ -f "results/workspace/mindedness_v2_sweep_${TAG}.json" ] && \
    guarded "gw" .venv/bin/python mindedness_v2_gw.py --tag "$TAG"
else
  note "GATE FAILED — skipping the rest. Report as UNINTERPRETABLE, not as a null."
fi
if [ "$KEEP" != "--keep" ]; then
  case "$ID" in models/*) rm -rf "$ID" ;; *) rm -rf ~/.cache/huggingface/hub/models--$(echo "$ID" | sed 's|/|--|') ;; esac
  rm -f results/workspace/.v2ckpt_${TAG}_*.npz
  note "weights + checkpoints removed (disk $(free_gb)Gi free)"
fi
[ -z "$FAILED" ] && note "########## $TAG COMPLETE ##########" || note "########## $TAG FAILURES:$FAILED ##########"
