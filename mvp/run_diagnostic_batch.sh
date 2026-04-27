#!/bin/bash
# Day-21 Diagnostic Batch — overnight sweep
#
# Three diagnostics, one batch:
#   D1a: cross-application v_IH × L17 on eg-eval-v2 (does v_IH do v_EG's job?)
#   D1b: cross-application v_EG × L7 on abstention (does v_EG do v_IH's job?)
#   D2:  v_EG at deeper layers (L18, L22) on eg-eval-v2 (right layer for EG?)
#   D3:  v_CC × L9 on simple reasoning prompts (CRT / modus-tollens / rate)
#
# All cells use --label so outputs land in distinct dirs and existing
# results/baselines aren't overwritten.
#
# Stops the VM at the end (success OR failure) so $ doesn't burn while user
# is at office.
#
# Run on VM:
#   cd ~/phronesis/mvp && nohup bash run_diagnostic_batch.sh > diagnostic_batch.log 2>&1 &
#   tail -f diagnostic_batch.log

set -u  # error on unset vars; do NOT use -e because we want to continue past per-cell failures

if [ -x "$(dirname "$0")/.venv/bin/python" ]; then
  PYTHON="$(dirname "$0")/.venv/bin/python"
else
  PYTHON="$(command -v python3)"
fi
RUN="$(dirname "$0")/run_benchmark.py"
LOGDIR="$(dirname "$0")/results/diagnostic_batch_$(date +%Y%m%d)"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/run.log"

echo "==========================================" | tee -a "$LOG"
echo "Day-21 Diagnostic Batch" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "==========================================" | tee -a "$LOG"

# Ensure VM stops even if script crashes / is interrupted.
# Account is set explicitly to avoid drift to Ludo account.
cleanup_stop_vm() {
  echo "" | tee -a "$LOG"
  echo "==========================================" | tee -a "$LOG"
  echo "FINAL — stopping VM at $(date)" | tee -a "$LOG"
  echo "==========================================" | tee -a "$LOG"
  # Use the metadata server to identify ourselves; this is a no-op on local dev.
  if command -v gcloud >/dev/null 2>&1; then
    INSTANCE_NAME=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name 2>/dev/null || echo "")
    INSTANCE_ZONE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone 2>/dev/null | awk -F/ '{print $NF}' || echo "")
    if [ -n "$INSTANCE_NAME" ] && [ -n "$INSTANCE_ZONE" ]; then
      echo "Stopping $INSTANCE_NAME in $INSTANCE_ZONE..." | tee -a "$LOG"
      gcloud compute instances stop "$INSTANCE_NAME" --zone="$INSTANCE_ZONE" --quiet 2>&1 | tee -a "$LOG" || true
    else
      echo "Not on a GCE VM (no metadata); skipping stop." | tee -a "$LOG"
    fi
  fi
}
trap cleanup_stop_vm EXIT INT TERM

# Hard timeout guard: if the whole sweep runs past 4 hours, abort and stop VM.
HARD_TIMEOUT_SECONDS=14400
START_TS=$(date +%s)

check_timeout() {
  NOW=$(date +%s)
  ELAPSED=$((NOW - START_TS))
  if [ "$ELAPSED" -gt "$HARD_TIMEOUT_SECONDS" ]; then
    echo "HARD TIMEOUT — elapsed ${ELAPSED}s > ${HARD_TIMEOUT_SECONDS}s. Aborting." | tee -a "$LOG"
    exit 1
  fi
}

run_cell() {
  # run_cell <bench_name> <n> <vector_name> <alpha_signed> <label>
  local BENCH="$1"
  local N="$2"
  local VECTOR="$3"
  local ALPHA="$4"
  local LABEL="$5"
  check_timeout

  echo "" | tee -a "$LOG"
  echo "─── CELL: $LABEL ($(date)) ───" | tee -a "$LOG"
  echo "    bench=$BENCH n=$N vector=$VECTOR alpha=$ALPHA" | tee -a "$LOG"

  if [ "$VECTOR" = "BASELINE" ]; then
    "$PYTHON" "$RUN" --benchmark "$BENCH" --n "$N" \
      --condition baseline --label "$LABEL" 2>&1 | tail -40 | tee -a "$LOG"
  else
    "$PYTHON" "$RUN" --benchmark "$BENCH" --n "$N" \
      --condition steered --vector "$VECTOR" --alpha "$ALPHA" \
      --label "$LABEL" 2>&1 | tail -40 | tee -a "$LOG"
  fi
  echo "    done at $(date)" | tee -a "$LOG"
}

# ─── BASELINES (skip if exists; --label triggers per-label dirs) ──────────────
# eg-eval-v2 baseline already exists at pathD_baseline_qwen3-4b_eg-eval-v2;
# we re-run under our own label to get a fresh comparison set in the same dir tree.

# cc-simple is brand new — must run baseline.
run_cell "cc-simple"   8  "BASELINE"  0  "diag_d3_cc_baseline"

# Abstention baseline likely already exists from prior IH work; re-run a 5-item
# subset under our own label for clean side-by-side. n=5 because diagnostic
# 1b only needs 5.
run_cell "abstention"  5  "BASELINE"  0  "diag_d1b_abstention_baseline"

# eg-eval-v2 baseline — re-run for parity with diag-labelled cells.
run_cell "eg-eval-v2"  10 "BASELINE"  0  "diag_d1a_d2_egv2_baseline"


# ─── D1a: v_IH × L17 on eg-eval-v2 (does IH do EG's job?) ────────────────────
for ALPHA in 4 8 12; do
  run_cell "eg-eval-v2" 10 "IH_L17"  "$ALPHA"  "diag_d1a_vIH_L17_a${ALPHA}"
done

# ─── D1b: v_EG × L7 on abstention (does EG do IH's job?) ─────────────────────
for ALPHA in 4 8; do
  run_cell "abstention" 5  "EG_L7"   "$ALPHA"  "diag_d1b_vEG_L7_a${ALPHA}"
done

# ─── D2: v_EG at deeper layers on eg-eval-v2 ─────────────────────────────────
for VEC in EG_L18 EG_L22; do
  for ALPHA in 4 8; do
    run_cell "eg-eval-v2" 10 "$VEC" "$ALPHA"  "diag_d2_v${VEC}_a${ALPHA}"
  done
done

# ─── D3: v_CC × L9 on simple reasoning prompts ───────────────────────────────
for ALPHA in 4 8 12; do
  run_cell "cc-simple"   8  "L9"     "$ALPHA"  "diag_d3_vCC_L9_a${ALPHA}"
done

# Bonus: α=−4 inversion on CC, mirrors what we did for IH. Should produce MORE
# spiraling if v_CC is a real "confident-commit" vector.
run_cell "cc-simple"   8  "L9"     "-4"      "diag_d3_vCC_L9_a-4"


# ─── Cell-count sanity check ──────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "==========================================" | tee -a "$LOG"
echo "Sanity check — files produced per label" | tee -a "$LOG"
echo "==========================================" | tee -a "$LOG"

EXPECTED_LABELS=(
  "diag_d3_cc_baseline:8:cc-simple"
  "diag_d1b_abstention_baseline:5:abstention"
  "diag_d1a_d2_egv2_baseline:10:eg-eval-v2"
  "diag_d1a_vIH_L17_a4:10:eg-eval-v2"
  "diag_d1a_vIH_L17_a8:10:eg-eval-v2"
  "diag_d1a_vIH_L17_a12:10:eg-eval-v2"
  "diag_d1b_vEG_L7_a4:5:abstention"
  "diag_d1b_vEG_L7_a8:5:abstention"
  "diag_d2_vEG_L18_a4:10:eg-eval-v2"
  "diag_d2_vEG_L18_a8:10:eg-eval-v2"
  "diag_d2_vEG_L22_a4:10:eg-eval-v2"
  "diag_d2_vEG_L22_a8:10:eg-eval-v2"
  "diag_d3_vCC_L9_a4:8:cc-simple"
  "diag_d3_vCC_L9_a8:8:cc-simple"
  "diag_d3_vCC_L9_a12:8:cc-simple"
  "diag_d3_vCC_L9_a-4:8:cc-simple"
)

PROBE_DIR="$(dirname "$0")/results/benchmark_probe"
TOTAL_OK=0
TOTAL_MISSING=0
for ENTRY in "${EXPECTED_LABELS[@]}"; do
  IFS=':' read -r LABEL EXPECTED BENCH <<< "$ENTRY"
  DIR="$PROBE_DIR/$BENCH/$LABEL"
  if [ -d "$DIR" ]; then
    COUNT=$(find "$DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
  else
    COUNT=0
  fi
  if [ "$COUNT" -eq "$EXPECTED" ]; then
    STATUS="OK"
    TOTAL_OK=$((TOTAL_OK + 1))
  else
    STATUS="MISSING ($COUNT/$EXPECTED)"
    TOTAL_MISSING=$((TOTAL_MISSING + 1))
  fi
  printf "  %-40s %-10s %s\n" "$LABEL" "[$STATUS]" "$DIR" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "Result: $TOTAL_OK/$((TOTAL_OK + TOTAL_MISSING)) cells complete" | tee -a "$LOG"
echo "==========================================" | tee -a "$LOG"
echo "Diagnostic batch finished at $(date)" | tee -a "$LOG"
echo "==========================================" | tee -a "$LOG"
echo "complete" > "$LOGDIR/done.marker"

# trap will run cleanup_stop_vm
exit 0
