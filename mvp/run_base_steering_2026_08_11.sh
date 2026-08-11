#!/bin/bash
# Base-model steering. Prereg: docs/prereg-steering-base-2026-08-11.md
#
# Primary pair: Qwen3-4B-Base vs Qwen3-4B-Instruct, IDENTICAL two-stage protocol on both sides.
# The published instruct result used the default config; a base model would get a searched one, so
# quoting the old number against a new one would confound post-training with protocol. Instruct is
# therefore re-run, which is also what makes P4 a real risk rather than a formality.
#
# FORMAT IS PASSED EXPLICITLY. Qwen3-4B-Base's gate file predates usable_formats, so the T1
# fallback would have measured it at separation 0.20 while instruct answers T1 at 0.911. Both sides
# run T4 (0.60 base / 0.941 instruct) - each model's best, and the same template on both.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs
mkdir -p "$LOG"
FAILED=(); PASSED=()

swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
# 8000 was too low: a 7.5GB fp16 4B model on a 16GB machine sits at ~10GB swap as its NORMAL
# operating point, and both 4B checkpoints were killed at 10.3GB and 9.8GB on the first attempt.
# The failure this guard exists for was 10.8GB with TWO models resident - swap alone cannot tell
# those apart, so the concurrency check below does that job and the ceiling is raised to a level
# only reachable by genuine runaway. Swap files live on the boot volume, so disk is guarded in the
# same loop.
SWAP_USED_CEILING=13000
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }

run_chunked () {   # name, then the python argv; loops until the script stops printing [chunk]
  local name="$1"; shift
  for round in $(seq 1 12); do
    if [ "$(disk_gb)" -lt 4 ]; then
      echo "[$name] SKIP: disk $(disk_gb)GB"; FAILED+=("$name:disk"); return 1
    fi
    local others; others=$(pgrep -fc "mindedness_(steer|v2|moral|base)" 2>/dev/null || echo 0)
    if [ "$others" -gt 0 ]; then
      echo "[$name] ABORT: $others model job(s) already running - two resident models is the"
      echo "[$name]        exact condition that put swap at 10.8GB before. Not starting."
      FAILED+=("$name:concurrent"); return 1
    fi
    .venv/bin/python "$@" > "$LOG/${name}_r${round}.log" 2>&1 &
    local pid=$!
    sleep 60
    while kill -0 "$pid" 2>/dev/null; do
      local used; used=$(swap_used_mb)
      if [ "$used" -gt "$SWAP_USED_CEILING" ]; then
        echo "[$name] GUARD swap used ${used}MB -> killing child $pid"
        kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
        FAILED+=("$name:swap"); return 1
      fi
      if [ "$(disk_gb)" -lt 3 ]; then
        echo "[$name] GUARD disk $(disk_gb)GB -> killing child $pid"
        kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
        FAILED+=("$name:disk"); return 1
      fi
      sleep 20
    done
    wait "$pid"; local rc=$?
    if [ $rc -ne 0 ]; then
      echo "[$name] r$round FAILED rc=$rc"; tail -5 "$LOG/${name}_r${round}.log"
      FAILED+=("$name:rc$rc"); return 1
    fi
    if ! grep -q "^\[chunk\]" "$LOG/${name}_r${round}.log"; then
      echo "[$name] done in $round round(s)"; PASSED+=("$name"); return 0
    fi
  done
  echo "[$name] did not finish in 12 rounds"; FAILED+=("$name:rounds"); return 1
}

do_model () {      # tag, model-path-or-hfid, format, hf-repo-to-fetch (or "-" if cached), local-dir
  local tag="$1" mdl="$2" fmt="$3" repo="$4" dir="$5"
  echo; echo "################ $tag  ($(date +%H:%M:%S)) ################"
  if [ "$repo" != "-" ]; then
    # Gate on the WEIGHTS BEING PRESENT, not on a log line. A stale COMPLETE from a previous run
    # whose weights were since deleted made this skip the fetch and then fail to load the model.
    if ! ls "$dir"/*.safetensors >/dev/null 2>&1; then
      echo "=== fetching $repo ==="
      ./fetch_model.sh "$repo" "$dir" > "$LOG/fetch_${tag}.log" 2>&1
    fi
    if ! grep -q "COMPLETE ->" "$LOG/fetch_${tag}.log" 2>/dev/null \
       || ! ls "$dir"/*.safetensors >/dev/null 2>&1; then
      echo "[$tag] weights missing after fetch"; FAILED+=("$tag:fetch"); return 1
    fi
  fi

  run_chunked "s1_${tag}" mindedness_steer_search.py \
      --model "$mdl" --tag "$tag" --format "$fmt" --max-cells 5 || return 1

  local sf="results/workspace/mindedness_steer_search_${tag}.json"
  local win; win=$(.venv/bin/python - "$sf" << 'PY'
import json, sys
w = json.load(open(sys.argv[1])).get("winner")
print(f"{w['layer']} {w['alpha']}" if w else "NONE")
PY
)
  if [ "$win" = "NONE" ]; then
    echo "[$tag] stage 1 found NO traction in 20 configs — a real answer, nothing to test in stage 2"
    PASSED+=("${tag}:notraction"); return 0
  fi
  local layer alpha; layer=${win% *}; alpha=${win#* }
  echo "=== [$tag] stage 2 at layer $layer alpha $alpha ==="
  run_chunked "s2_${tag}" mindedness_v2_steer.py \
      --model "$mdl" --tag "$tag" --format "$fmt" \
      --layer "$layer" --alphas "$alpha" --max-cells 3 || return 1
  return 0
}

# Delete weights ONLY when that model's stages all succeeded. The first version ran the cleanup
# unconditionally, so a guard kill was immediately followed by deleting 7.5GB of weights that then
# had to be downloaded again. Never let a failure path trigger destruction of expensive state.
free_if_done () {
  local tag="$1" dir="$2"
  for f in "${FAILED[@]:-}"; do
    case "$f" in "$tag"*|"s1_$tag"*|"s2_$tag"*)
      echo "[$tag] KEEPING weights - stage failed ($f), a retry should not re-download"; return 0;;
    esac
  done
  [ -d "$dir" ] && rm -rf "$dir" && echo "freed $tag"
  return 0
}

# --- primary pair: same architecture, same tokenizer, same format, only post-training differs ---
do_model Qwen3-4B-Base models/Qwen3-4B-Base T4 Qwen/Qwen3-4B-Base models/Qwen3-4B-Base
do_model Qwen3-4B-searched Qwen/Qwen3-4B T4 - -
free_if_done Qwen3-4B-Base models/Qwen3-4B-Base

# --- secondary: does a base model differ from its tested-negative instruct sibling? ---
do_model OLMo2-1B-Base models/OLMo-2-0425-1B-Base T1 allenai/OLMo-2-0425-1B models/OLMo-2-0425-1B-Base
free_if_done OLMo2-1B-Base models/OLMo-2-0425-1B-Base

do_model Qwen3_5-4B-Base models/Qwen3.5-4B-Base T2 Qwen/Qwen3.5-4B-Base models/Qwen3.5-4B-Base
free_if_done Qwen3_5-4B-Base models/Qwen3.5-4B-Base

echo
echo "======== BASE STEERING SUMMARY $(date +%H:%M:%S) ========"
echo "passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "failed (${#FAILED[@]}): ${FAILED[*]:-none}"
[ ${#FAILED[@]} -eq 0 ] && { echo "COMPLETE"; exit 0; }
echo "INCOMPLETE - ${#FAILED[@]} stage(s) failed; nothing here is a null result"
exit 1
