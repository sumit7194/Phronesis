#!/bin/bash
# Day-23 Round 3 sweep — bidirectional + EG-α-fine-sweep + composition
#
# A. Bidirectional cross-application (45 gens): vCC_full × L9 × {α=4,8,12} on
#    eg-eval-v2 (10) + abstention (5). Settles whether the IH-knob and CC-knob
#    produce the SAME behavior on the SAME prompts.
#
# B. EG max-α on abstention (5 gens): vEG × L7 × α=12 on abstention. Tests if
#    higher α suppresses the Gandhi confabulation entirely.
#
# C. EG α-fine-sweep on Gandhi only (7 gens): vEG × L7 × {α=1,2,3,5,6,7,10}
#    on the fp-gandhi-only mini-benchmark. Characterizes the phase-transition
#    between "fabricate to match premise" (low α) and "reject premise" (high α).
#
# D. Composition cells:
#    - composition-test (10 new prompts): baseline + vIH alone + vCC alone +
#      vIH+vCC composite = 40 gens
#    - composite on diagnostic (cc-simple + abstention + eg-eval-v2): 23 gens
#
# Total: ~120 generations across ~21 cells. ETA ~2 hours on L4.
#
# Run on VM:
#   cd ~/phronesis/mvp && nohup bash run_round3_sweep.sh > round3_launch.log 2>&1 &

set -u
cd "$(dirname "$0")"
if [ -x ".venv/bin/python" ]; then PYTHON=".venv/bin/python"; else PYTHON="$(command -v python3)"; fi

LOGDIR="results/round3_$(date +%Y%m%d)"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/run.log"
STATUS="$LOGDIR/status.json"

write_status() {
  python3 -c "
import json, time
data = {
  'phase': '${1}',
  'cell': '${2:-}',
  'cell_idx': ${3:-0},
  'cell_total': ${4:-1},
  'started_at': '${SWEEP_START_ISO}',
  'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
}
open('$STATUS', 'w').write(json.dumps(data, indent=2))
"
}

SWEEP_START_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "============================================" | tee -a "$LOG"
echo "Day-23 Round 3 sweep" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"

run_cell() {
  # run_cell <bench> <n> <vector> <alpha> <label> [vector2] [alpha2]
  local BENCH="$1"
  local N="$2"
  local VECTOR="$3"
  local ALPHA="$4"
  local LABEL="$5"
  local VEC2="${6:-}"
  local ALPHA2="${7:-}"
  CIDX=$((CIDX+1))
  write_status "running" "$LABEL" $CIDX $TOTAL_CELLS
  echo "" | tee -a "$LOG"
  echo "[$CIDX/$TOTAL_CELLS] $LABEL  ($(date))" | tee -a "$LOG"

  if [ "$VECTOR" = "BASELINE" ]; then
    "$PYTHON" run_benchmark.py --benchmark "$BENCH" --n "$N" \
      --condition baseline --label "$LABEL" 2>&1 | tail -30 | tee -a "$LOG"
  elif [ -n "$VEC2" ]; then
    "$PYTHON" run_benchmark.py --benchmark "$BENCH" --n "$N" \
      --condition steered --vector "$VECTOR" --alpha "$ALPHA" \
      --vector2 "$VEC2" --alpha2 "$ALPHA2" \
      --label "$LABEL" 2>&1 | tail -30 | tee -a "$LOG"
  else
    "$PYTHON" run_benchmark.py --benchmark "$BENCH" --n "$N" \
      --condition steered --vector "$VECTOR" --alpha "$ALPHA" \
      --label "$LABEL" 2>&1 | tail -30 | tee -a "$LOG"
  fi
}

CELLS=(
  # A. Bidirectional vCC_full on EG/abstention
  "eg-eval-v2|10|CC_full_L9|4|round3_vCCfull_L9_a4_eg"
  "eg-eval-v2|10|CC_full_L9|8|round3_vCCfull_L9_a8_eg"
  "eg-eval-v2|10|CC_full_L9|12|round3_vCCfull_L9_a12_eg"
  "abstention|5|CC_full_L9|4|round3_vCCfull_L9_a4_abst"
  "abstention|5|CC_full_L9|8|round3_vCCfull_L9_a8_abst"
  "abstention|5|CC_full_L9|12|round3_vCCfull_L9_a12_abst"

  # B. EG max-α on abstention
  "abstention|5|EG_L7|12|round3_vEG_L7_a12_abst"

  # C. EG α-fine-sweep on fp-gandhi only
  "fp-gandhi-only|1|EG_L7|1|round3_vEG_L7_a1_gandhi"
  "fp-gandhi-only|1|EG_L7|2|round3_vEG_L7_a2_gandhi"
  "fp-gandhi-only|1|EG_L7|3|round3_vEG_L7_a3_gandhi"
  "fp-gandhi-only|1|EG_L7|5|round3_vEG_L7_a5_gandhi"
  "fp-gandhi-only|1|EG_L7|6|round3_vEG_L7_a6_gandhi"
  "fp-gandhi-only|1|EG_L7|7|round3_vEG_L7_a7_gandhi"
  "fp-gandhi-only|1|EG_L7|10|round3_vEG_L7_a10_gandhi"

  # D. Composition on new test prompts (10 prompts × 4 conditions = 40 gens)
  "composition-test|10|BASELINE|0|round3_comp_baseline"
  "composition-test|10|IH_L17|8|round3_comp_vIH_a8"
  "composition-test|10|CC_full_L9|8|round3_comp_vCCfull_a8"
  "composition-test|10|IH_L17|8|round3_comp_vIH_plus_vCC_a8|CC_full_L9|8"

  # E. Composite on diagnostic prompts (23 gens)
  "cc-simple|8|IH_L17|8|round3_comp_diagnostic_cc|CC_full_L9|8"
  "abstention|5|IH_L17|8|round3_comp_diagnostic_abst|CC_full_L9|8"
  "eg-eval-v2|10|IH_L17|8|round3_comp_diagnostic_eg|CC_full_L9|8"
)

TOTAL_CELLS=${#CELLS[@]}
CIDX=0
for ENTRY in "${CELLS[@]}"; do
  IFS='|' read -ra FIELDS <<< "$ENTRY"
  run_cell "${FIELDS[@]}"
done

write_status "complete" "" $TOTAL_CELLS $TOTAL_CELLS
echo "" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "Round 3 sweep complete at $(date)" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "complete" > "$LOGDIR/done.marker"
exit 0
