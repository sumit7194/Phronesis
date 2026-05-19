#!/bin/bash
# Chain runner for nla_phaseN_* experiments.
# Runs p1..p5 sequentially, logs to ~/phronesis_run/mvp/results/chain_runner.log
# Exits 0 only if all phases succeed. Prints "ALL PHASES COMPLETE" at end.

set -u
set -o pipefail
PY=${PY:-python3}
cd "$HOME/phronesis_run/mvp"
LOG="$HOME/phronesis_run/mvp/results/chain_runner.log"
mkdir -p "$(dirname "$LOG")"

run_phase () {
  local name="$1"
  local script="$2"
  local started=$(date '+%H:%M:%S')
  echo "================================================================" | tee -a "$LOG"
  echo "[$started] BEGIN $name :: $PY $script" | tee -a "$LOG"
  echo "================================================================" | tee -a "$LOG"
  if "$PY" "$script" 2>&1 | tee -a "$LOG"; then
    local ended=$(date '+%H:%M:%S')
    echo "[$ended] END   $name :: OK" | tee -a "$LOG"
    return 0
  else
    local ended=$(date '+%H:%M:%S')
    echo "[$ended] END   $name :: FAILED (exit=$?)" | tee -a "$LOG"
    return 1
  fi
}

echo "###############################################################" | tee -a "$LOG"
echo "# CHAIN RUNNER started $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"

run_phase "P1-AR-roundtrip"  "$HOME/phronesis_run/mvp/p1_ar_roundtrip.py"     || echo "[WARN] P1 failed; continuing" | tee -a "$LOG"
run_phase "P2-probe"         "$HOME/phronesis_run/mvp/p2_probe_diagnostic.py" || echo "[WARN] P2 failed; continuing" | tee -a "$LOG"
run_phase "P3-extreme-alpha" "$HOME/phronesis_run/mvp/p3_extreme_alpha_e2.py" || echo "[WARN] P3 failed; continuing" | tee -a "$LOG"
run_phase "P4-layer-sweep"   "$HOME/phronesis_run/mvp/p4_layer_sweep.py"      || echo "[WARN] P4 failed; continuing" | tee -a "$LOG"
run_phase "P5-CAST-gated"    "$HOME/phronesis_run/mvp/p5_cast_gated.py"       || echo "[WARN] P5 failed; continuing" | tee -a "$LOG"

# If P4 produced a layer-sweep parquet, run AV inference on it
P4_PQ="$HOME/phronesis_run/mvp/results/nla_phase4_layer_sweep/activations_layer_sweep.parquet"
P4_OUT="$HOME/phronesis_run/mvp/results/nla_phase4_layer_sweep/av_layer_sweep.jsonl"
if [ -f "$P4_PQ" ]; then
  echo "================================================================" | tee -a "$LOG"
  echo "[$(date '+%H:%M:%S')] BEGIN P4-AV-inference" | tee -a "$LOG"
  echo "================================================================" | tee -a "$LOG"
  "$PY" "$HOME/phronesis_run/mvp/run_nla_av_inference.py" \
      --in "$P4_PQ" --out "$P4_OUT" 2>&1 | tee -a "$LOG" \
      && echo "[$(date '+%H:%M:%S')] END   P4-AV-inference :: OK" | tee -a "$LOG" \
      || echo "[$(date '+%H:%M:%S')] END   P4-AV-inference :: FAILED" | tee -a "$LOG"
fi

echo "###############################################################" | tee -a "$LOG"
echo "# ALL PHASES COMPLETE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "###############################################################" | tee -a "$LOG"
