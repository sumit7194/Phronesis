#!/bin/bash
# Phase 2a round 2: multi-virtue DPO + overconfidence probe eval (baseline + v2 + multi-virtue)
set -u
set -o pipefail
PY=${PY:-/home/sumit/phronesis_run/.venv/bin/python}
cd "$HOME/phronesis_run/mvp"
EVAL_DIR="$HOME/phronesis_run/mvp/results/phase2a_round2"
LOG="$EVAL_DIR/chain.log"
mkdir -p "$EVAL_DIR"

run () {
  local name="$1"; shift
  local cmd="$*"
  local started=$(date '+%H:%M:%S')
  echo "================================================================" | tee -a "$LOG"
  echo "[$started] BEGIN $name :: $cmd" | tee -a "$LOG"
  echo "================================================================" | tee -a "$LOG"
  if eval "$cmd" 2>&1 | tee -a "$LOG"; then
    echo "[$(date '+%H:%M:%S')] END   $name :: OK" | tee -a "$LOG"
  else
    echo "[$(date '+%H:%M:%S')] END   $name :: FAILED" | tee -a "$LOG"
  fi
}

echo "###############################################################" | tee -a "$LOG"
echo "# PHASE 2A ROUND 2 started $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"

# 1. Train multi-virtue DPO on all 380 triplets
run "TRAIN-MULTIVIRTUE-DPO" "$PY $HOME/phronesis_run/mvp/phase2a_multivirtue_dpo.py"

# 2. Overconfidence-probe evals: baseline + IH-only v2 + multi-virtue
run "OC-EVAL-BASELINE"   "$PY $HOME/phronesis_run/mvp/overconfidence_probe_eval.py --adapter NONE --out $EVAL_DIR/oc_baseline.json --label baseline"
run "OC-EVAL-V2"         "$PY $HOME/phronesis_run/mvp/overconfidence_probe_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_dpo_v2/adapter --out $EVAL_DIR/oc_v2.json --label v2_IH_only"
run "OC-EVAL-MULTIVIRTUE" "$PY $HOME/phronesis_run/mvp/overconfidence_probe_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_multivirtue_dpo/adapter --out $EVAL_DIR/oc_multivirtue.json --label multivirtue_DPO"

# 3. Also run broader-eval on multi-virtue to compare with F140 data
run "BROADER-EVAL-MULTIVIRTUE" "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_multivirtue_dpo/adapter --out $EVAL_DIR/broader_multivirtue.json --label multivirtue_DPO"

echo "###############################################################" | tee -a "$LOG"
echo "# PHASE 2A ROUND 2 COMPLETE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"
