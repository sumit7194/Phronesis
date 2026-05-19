#!/bin/bash
# Phase 2a validation chain: broader eval on baseline, v2, SFT, flipped DPO, rank4, rank64.
# Plus the training runs needed.
#
# Order matters: train first (each ~3-11 min), then evaluate each adapter on the broader prompt set.
set -u
set -o pipefail
PY=${PY:-/home/sumit/phronesis_run/.venv/bin/python}
cd "$HOME/phronesis_run/mvp"
LOG="$HOME/phronesis_run/mvp/results/phase2a_validation/chain.log"
mkdir -p "$(dirname "$LOG")"

run () {
  local name="$1"; shift
  local cmd="$*"
  local started=$(date '+%H:%M:%S')
  echo "================================================================" | tee -a "$LOG"
  echo "[$started] BEGIN $name :: $cmd" | tee -a "$LOG"
  echo "================================================================" | tee -a "$LOG"
  if eval "$cmd" 2>&1 | tee -a "$LOG"; then
    echo "[$(date '+%H:%M:%S')] END   $name :: OK" | tee -a "$LOG"
    return 0
  else
    echo "[$(date '+%H:%M:%S')] END   $name :: FAILED (exit=$?)" | tee -a "$LOG"
    return 1
  fi
}

EVAL_DIR="$HOME/phronesis_run/mvp/results/phase2a_validation"

echo "###############################################################" | tee -a "$LOG"
echo "# PHASE 2A VALIDATION started $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"

# --- 1. Train all the controls + ablations ---
run "TRAIN-SFT"          "$PY $HOME/phronesis_run/mvp/phase2a_sft_control.py"   || true
run "TRAIN-FLIPPED-DPO"  "$PY $HOME/phronesis_run/mvp/phase2a_flipped_dpo.py"   || true
run "TRAIN-RANK4"        "$PY $HOME/phronesis_run/mvp/phase2a_rank_ablation.py --rank 4"  || true
run "TRAIN-RANK64"       "$PY $HOME/phronesis_run/mvp/phase2a_rank_ablation.py --rank 64" || true

# --- 2. Run broader eval on each (baseline + v2 + the 4 new adapters) ---
# baseline already implicit in each eval — just use --adapter NONE for one pure baseline run
run "EVAL-BASELINE"   "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter NONE --out $EVAL_DIR/eval_baseline.json --label baseline"
run "EVAL-V2"         "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_dpo_v2/adapter --out $EVAL_DIR/eval_v2.json --label v2_5epoch_rank16"
run "EVAL-SFT"        "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_sft_control/adapter --out $EVAL_DIR/eval_sft.json --label sft_5epoch_rank16"
run "EVAL-FLIPPED"    "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_flipped_dpo/adapter --out $EVAL_DIR/eval_flipped.json --label flipped_dpo_5epoch_rank16"
run "EVAL-RANK4"      "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_rank4/adapter --out $EVAL_DIR/eval_rank4.json --label dpo_5epoch_rank4"
run "EVAL-RANK64"     "$PY $HOME/phronesis_run/mvp/broader_eval.py --adapter $HOME/phronesis_run/mvp/results/phase2a_rank64/adapter --out $EVAL_DIR/eval_rank64.json --label dpo_5epoch_rank64"

echo "###############################################################" | tee -a "$LOG"
echo "# PHASE 2A VALIDATION COMPLETE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"
