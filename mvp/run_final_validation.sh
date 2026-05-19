#!/bin/bash
# Final validation chain: seed replication + expanded decision-margin probe
set -u
set -o pipefail
PY=${PY:-/home/sumit/phronesis_run/.venv/bin/python}
LOG="$HOME/phronesis_run/mvp/results/final_validation.log"
mkdir -p "$(dirname "$LOG")"

run () {
  local name="$1"; shift
  local cmd="$*"
  echo "================================================================" | tee -a "$LOG"
  echo "[$(date '+%H:%M:%S')] BEGIN $name" | tee -a "$LOG"
  echo "================================================================" | tee -a "$LOG"
  if eval "$cmd" 2>&1 | tee -a "$LOG"; then
    echo "[$(date '+%H:%M:%S')] END $name :: OK" | tee -a "$LOG"
  else
    echo "[$(date '+%H:%M:%S')] END $name :: FAILED" | tee -a "$LOG"
  fi
}

echo "###############################################################" | tee -a "$LOG"
echo "# FINAL VALIDATION started $(date)" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"

run "SEED-REPLICATION-E2"  "$PY $HOME/phronesis_run/mvp/seed_replication_e2.py"
run "EXPANDED-DECISION-MARGIN" "$PY $HOME/phronesis_run/mvp/expanded_decision_margin_eval.py"

echo "###############################################################" | tee -a "$LOG"
echo "# FINAL VALIDATION COMPLETE $(date)" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"
