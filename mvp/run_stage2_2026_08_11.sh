#!/bin/bash
# STAGE 2 of the traction search: at the config stage 1 selected on raw movement alone, run the
# FULL DV for every vector plus a 5-seed random floor AT THAT SAME CONFIG.
#
# The floor is the point. Stage 1 found that OLMo only moves at alpha >= 1.6 and that the absurd
# control moves about half as much as the mental group there - the profile of global disruption,
# not steering. If random directions at layer 4 / alpha 1.6 move the DV just as much, that is the
# answer, and it is an answer rather than the "untested" cell F-AJ had to leave open.
#
# The layer and alpha are READ FROM the stage-1 JSON, never retyped: a hand-copied number is how
# a config silently drifts between the stage that chose it and the stage that tests it.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs
FAILED=(); PASSED=()

swap_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }

stage2 () {
  local tag="$1" model="$2"
  local sf="results/workspace/mindedness_steer_search_${tag}.json"
  if [ ! -f "$sf" ]; then
    echo "[$tag] no stage-1 file, skipping"; FAILED+=("$tag:nostage1"); return 1
  fi
  local win; win=$(.venv/bin/python - "$sf" << 'PY'
import json, sys
w = json.load(open(sys.argv[1])).get("winner")
print(f"{w['layer']} {w['alpha']}" if w else "NONE")
PY
)
  if [ "$win" = "NONE" ]; then
    echo "[$tag] stage 1 found NO traction at any config - nothing to test in stage 2."
    echo "[$tag] that is a real answer about this vector on this model, not a skipped cell."
    PASSED+=("$tag:notraction"); return 0
  fi
  local layer alpha; layer=$(echo "$win" | cut -d' ' -f1); alpha=$(echo "$win" | cut -d' ' -f2)
  echo "=== [stage2_$tag] layer $layer alpha $alpha  $(date +%H:%M:%S) ==="
  for round in 1 2 3 4 5 6 7 8; do
    .venv/bin/python mindedness_v2_steer.py --model "$model" --tag "$tag" \
        --layer "$layer" --alphas "$alpha" --max-cells 3 \
        > "$LOG/stage2_${tag}_r${round}.log" 2>&1 &
    local pid=$!
    sleep 45
    while kill -0 "$pid" 2>/dev/null; do
      if [ "$(swap_mb)" -lt 300 ]; then
        echo "[$tag] GUARD: swap low, killing python child $pid"
        kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
        FAILED+=("$tag:swap"); return 1
      fi
      sleep 20
    done
    wait "$pid"; local rc=$?
    if [ $rc -ne 0 ]; then
      echo "[$tag] round $round FAILED rc=$rc"; tail -4 "$LOG/stage2_${tag}_r${round}.log"
      FAILED+=("$tag:rc$rc"); return 1
    fi
    if ! grep -q "^\[chunk\]" "$LOG/stage2_${tag}_r${round}.log"; then
      echo "[$tag] stage 2 complete in $round round(s)"; PASSED+=("$tag"); return 0
    fi
  done
  echo "[$tag] did not finish in 8 rounds"; FAILED+=("$tag:rounds"); return 1
}

stage2 OLMo2-1B-Instruct  models/OLMo-2-0425-1B-Instruct
stage2 Gemma4-E2B-Instruct models/gemma-4-E2B-it

echo
echo "======== STAGE 2 SUMMARY $(date +%H:%M:%S) ========"
echo "passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "failed (${#FAILED[@]}): ${FAILED[*]:-none}"
[ ${#FAILED[@]} -eq 0 ] && { echo "COMPLETE"; exit 0; }
echo "INCOMPLETE - do not read any of this as a null result"
exit 1
