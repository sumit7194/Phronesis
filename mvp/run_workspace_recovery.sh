#!/bin/bash
# Phase R3 of the recovery (amendment A1): wait for the resumed fit to save the lens,
# then re-run the lens-dependent tiers against it and regenerate the summary.
cd "$(dirname "$0")"
PY=.venv/bin/python
LOGD=results/workspace/logs
mkdir -p "$LOGD"
MASTER="$LOGD/recovery.log"
note() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MASTER"; }
stage() {
  name=$1; shift
  note "=== STAGE $name START ==="
  "$PY" "$@" > "$LOGD/$name.log" 2>&1
  note "=== STAGE $name END rc=$? ==="
}

note "recovery driver waiting for fit to finish"
until ! pgrep -f "workspace_t2_fit.py --until 14:00" > /dev/null; do sleep 60; done
note "fit process gone; lens meta: $(cat results/workspace/t2_fit_meta.json 2>/dev/null | tr -d '\n')"

stage t2b_v2 workspace_t2b_validate.py
stage t3b workspace_t3b_wrinkle.py
stage t1_jlens_v2 workspace_t1_strat.py --lens jlens --n-chunks 50
stage summary_v2 workspace_summary.py
touch results/workspace/RECOVERY_DONE
note "recovery complete"
