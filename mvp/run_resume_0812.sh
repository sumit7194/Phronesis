#!/bin/bash
# Resume after the 2026-08-12 power loss. Base pair stage 1+2 are complete on disk; instruct
# stage 2 had 2 of 9 cells and the steer script resumes from its own JSON.
# Then the matched-config addition: base at INSTRUCT's winning config (L19 a0.2), because the
# search picked different configs for the two sides and "same protocol" is not "same config".
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs
FAILED=(); PASSED=()
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
SWAP_USED_CEILING=13000
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }

run_chunked () {
  local name="$1"; shift
  for round in $(seq 1 12); do
    [ "$(disk_gb)" -lt 4 ] && { echo "[$name] SKIP disk"; FAILED+=("$name:disk"); return 1; }
    local others; others=$(pgrep -fc "mindedness_(steer|v2|moral)" 2>/dev/null || echo 0)
    [ "$others" -gt 0 ] && { echo "[$name] ABORT: $others model jobs running"; FAILED+=("$name:concurrent"); return 1; }
    .venv/bin/python "$@" > "$LOG/${name}_r${round}.log" 2>&1 &
    local pid=$!
    sleep 60
    while kill -0 "$pid" 2>/dev/null; do
      local u; u=$(swap_used_mb)
      [ "$u" -gt "$SWAP_USED_CEILING" ] && { echo "[$name] GUARD swap ${u}MB"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; FAILED+=("$name:swap"); return 1; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[$name] GUARD disk"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; FAILED+=("$name:disk"); return 1; }
      sleep 20
    done
    wait "$pid"; local rc=$?
    [ $rc -ne 0 ] && { echo "[$name] r$round FAILED rc=$rc"; tail -4 "$LOG/${name}_r${round}.log"; FAILED+=("$name:rc$rc"); return 1; }
    grep -q "^\[chunk\]" "$LOG/${name}_r${round}.log" || { echo "[$name] done in $round round(s)"; PASSED+=("$name"); return 0; }
  done
  echo "[$name] not finished in 12 rounds"; FAILED+=("$name:rounds"); return 1
}

echo "################ resume: instruct stage 2 (L19 a0.2) ################"
run_chunked s2_Qwen3-4B-searched mindedness_v2_steer.py \
    --model Qwen/Qwen3-4B --tag Qwen3-4B-searched --format T4 \
    --layer 19 --alphas 0.2 --max-cells 3

echo "################ matched-config: BASE at instruct's config (L19 a0.2) ################"
run_chunked s2_Qwen3-4B-Base-matched mindedness_v2_steer.py \
    --model models/Qwen3-4B-Base --tag Qwen3-4B-Base-matched --format T4 \
    --layer 19 --alphas 0.2 --max-cells 3

echo "################ OLMo-2-1B-Base ################"
if ! ls models/OLMo-2-0425-1B-Base/*.safetensors >/dev/null 2>&1; then
  ./fetch_model.sh allenai/OLMo-2-0425-1B models/OLMo-2-0425-1B-Base > "$LOG/fetch_OLMo2-1B-Base.log" 2>&1
fi
if ls models/OLMo-2-0425-1B-Base/*.safetensors >/dev/null 2>&1; then
  run_chunked s1_OLMo2-1B-Base mindedness_steer_search.py \
      --model models/OLMo-2-0425-1B-Base --tag OLMo2-1B-Base --format T1 --max-cells 5
  W=$(.venv/bin/python -c "
import json;w=json.load(open('results/workspace/mindedness_steer_search_OLMo2-1B-Base.json')).get('winner')
print(f\"{w['layer']} {w['alpha']}\" if w else 'NONE')" 2>/dev/null || echo NONE)
  if [ "$W" != "NONE" ]; then
    run_chunked s2_OLMo2-1B-Base mindedness_v2_steer.py \
        --model models/OLMo-2-0425-1B-Base --tag OLMo2-1B-Base --format T1 \
        --layer "${W% *}" --alphas "${W#* }" --max-cells 3
  else
    echo "[OLMo2-1B-Base] no traction in 20 configs"; PASSED+=("OLMo2-1B-Base:notraction")
  fi
else
  echo "[OLMo2-1B-Base] fetch failed"; FAILED+=("OLMo2-1B-Base:fetch")
fi

echo
echo "======== RESUME SUMMARY $(date +%H:%M:%S) ========"
echo "passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "failed (${#FAILED[@]}): ${FAILED[*]:-none}"
[ ${#FAILED[@]} -eq 0 ] && { echo "COMPLETE"; exit 0; }
echo "INCOMPLETE"; exit 1
