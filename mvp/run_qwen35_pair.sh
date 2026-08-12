#!/bin/bash
# Is the steering effect Qwen3-4B, or Qwen-the-family? F-AS concluded the split is by family, but
# that rests on Qwen3-4B vs OLMo. Qwen3.5 has NEVER been run under the two-stage protocol - its
# instruct model was only tested at the default config where the vector was inert (+0.15), which
# F-AJ established means untested, not negative.
#
# Both checkpoints run T1: base 0.69, instruct 0.777. Same template on both, comfortably above the
# 0.30 bar on each - the lesson from the Qwen3-4B pair, where a T1 fallback would have measured the
# base model at 0.20 and faked a post-training effect.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; FAILED=(); PASSED=()
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
SWAP_USED_CEILING=13000
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }

run_chunked () {
  local name="$1"; shift
  for round in $(seq 1 12); do
    [ "$(disk_gb)" -lt 4 ] && { echo "[$name] SKIP disk $(disk_gb)GB"; FAILED+=("$name:disk"); return 1; }
    local o; o=$(pgrep -fc "mindedness_(steer|v2|moral)" 2>/dev/null || echo 0)
    [ "$o" -gt 0 ] && { echo "[$name] ABORT: $o model jobs running"; FAILED+=("$name:concurrent"); return 1; }
    .venv/bin/python "$@" > "$LOG/${name}_r${round}.log" 2>&1 &
    local pid=$!; sleep 60
    while kill -0 "$pid" 2>/dev/null; do
      local u; u=$(swap_used_mb)
      [ "$u" -gt "$SWAP_USED_CEILING" ] && { echo "[$name] GUARD swap ${u}MB"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; FAILED+=("$name:swap"); return 1; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[$name] GUARD disk"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; FAILED+=("$name:disk"); return 1; }
      sleep 20
    done
    wait "$pid"; local rc=$?
    [ $rc -ne 0 ] && { echo "[$name] r$round FAILED rc=$rc"; tail -5 "$LOG/${name}_r${round}.log"; FAILED+=("$name:rc$rc"); return 1; }
    grep -q "^\[chunk\]" "$LOG/${name}_r${round}.log" || { echo "[$name] done in $round round(s)"; PASSED+=("$name"); return 0; }
  done
  echo "[$name] not finished in 12 rounds"; FAILED+=("$name:rounds"); return 1
}

do_pair () {   # tag  model  format
  local tag="$1" mdl="$2" fmt="$3"
  echo; echo "################ $tag ($(date +%H:%M:%S)) ################"
  run_chunked "s1_${tag}" mindedness_steer_search.py --model "$mdl" --tag "$tag" --format "$fmt" --max-cells 5 || return 1
  local W; W=$(.venv/bin/python -c "
import json;w=json.load(open('results/workspace/mindedness_steer_search_${tag}.json')).get('winner')
print(f\"{w['layer']} {w['alpha']}\" if w else 'NONE')" 2>/dev/null || echo NONE)
  if [ "$W" = "NONE" ]; then
    echo "[$tag] NO traction in 20 configs - a real answer"; PASSED+=("${tag}:notraction"); return 0
  fi
  echo "=== [$tag] stage 2 at layer ${W% *} alpha ${W#* } ==="
  run_chunked "s2_${tag}" mindedness_v2_steer.py --model "$mdl" --tag "$tag" --format "$fmt" \
      --layer "${W% *}" --alphas "${W#* }" --max-cells 3 || return 1
}

if ! ls models/Qwen3.5-4B-Base/*.safetensors >/dev/null 2>&1; then
  echo "=== fetching Qwen/Qwen3.5-4B-Base ==="
  ./fetch_model.sh Qwen/Qwen3.5-4B-Base models/Qwen3.5-4B-Base > "$LOG/fetch_Q35Base.log" 2>&1
fi
if ls models/Qwen3.5-4B-Base/*.safetensors >/dev/null 2>&1; then
  do_pair Qwen3_5-4B-Base-searched models/Qwen3.5-4B-Base T1
else
  echo "[Q35Base] fetch failed"; FAILED+=("Q35Base:fetch")
fi
do_pair Qwen3_5-4B-searched Qwen/Qwen3.5-4B T1

echo; echo "======== QWEN3.5 PAIR SUMMARY $(date +%H:%M:%S) ========"
echo "passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "failed (${#FAILED[@]}): ${FAILED[*]:-none}"
[ ${#FAILED[@]} -eq 0 ] && { echo "COMPLETE"; exit 0; }
echo "INCOMPLETE"; exit 1
