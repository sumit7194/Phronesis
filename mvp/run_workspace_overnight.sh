#!/bin/bash
# Overnight workspace-replication driver (prereg: docs/prereg-workspace-mac.md).
# Run under caffeinate. Stages are separate processes so MPS memory is fully
# released between them; a stage failure does not kill the night.
cd "$(dirname "$0")"
PY=.venv/bin/python
LOGD=results/workspace/logs
mkdir -p "$LOGD"
MASTER="$LOGD/driver.log"

note() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER"; }

stage() {
  name=$1; shift
  note "=== STAGE $name START ==="
  "$PY" "$@" > "$LOGD/$name.log" 2>&1
  rc=$?
  note "=== STAGE $name END rc=$rc ==="
  return $rc
}

note "overnight run begins (pid $$)"

stage t0 workspace_t0_ignition.py
stage t1_logit workspace_t1_strat.py --lens logit --n-chunks 50

# Fit phase 1: hard stop 06:30 so the lens-dependent tiers get their window.
stage t2_fit workspace_t2_fit.py --until 06:30 --max-prompts 100

if [ -f results/workspace/jlens_qwen3-4b.pt ]; then
  stage t2b workspace_t2b_validate.py
  stage t3 workspace_t3_loading.py
  stage t1_jlens workspace_t1_strat.py --lens jlens --n-chunks 50
  # Top up the lens for future sessions if there's still night left.
  H=$(date +%H)
  if [ "$H" -lt 9 ]; then
    stage t2_fit_resume workspace_t2_fit.py --until 09:15 --max-prompts 100
  fi
else
  note "no lens file — skipping lens-dependent stages (t2b, t3, t1_jlens)"
fi

stage summary workspace_summary.py
touch results/workspace/RUN_DONE
note "overnight run complete"
