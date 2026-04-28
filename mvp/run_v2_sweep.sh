#!/bin/bash
# Day-22 v2 sweep — Tier A (re-extract from new corpora + cosine matrix) + Tier B (behavioral)
#
# Phase 1: backup old vectors to _v1_backup
# Phase 2: re-extract v_EG_v2, v_RT_v2, v_CC_v2 (legacy corpus + numeric-only subset),
#          v_IH_v2 from the expanded corpora
# Phase 3: cosine-similarity matrix across all old + new vectors
# Phase 4: behavioral diagnostic on most-discriminating prompts:
#          - eg-v2-08 dinosaur feathers (does new v_EG add specifics?)
#          - eg-v2-10 seismic damper (does new v_EG / v_IH commit?)
#          - fp-gandhi (does new v_EG confabulate less than v1?)
#          - cc-s-01 bat-and-ball (does new v_CC differ from old v_CC?)
#
# Status JSON updated after each cell so dashboard can render live progress.
#
# Usage on VM:
#   cd ~/phronesis/mvp && nohup bash run_v2_sweep.sh > v2_sweep_launch.log 2>&1 &
#   tail -f v2_sweep_launch.log

set -u
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then PYTHON=".venv/bin/python"; else PYTHON="$(command -v python3)"; fi

LOGDIR="results/v2_sweep_$(date +%Y%m%d)"
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
echo "Day-22 v2 sweep" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "Logdir: $LOGDIR" | tee -a "$LOG"
echo "Status: $STATUS" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"

# ─── Phase 1: backup old vectors ─────────────────────────────────────────────
write_status "phase1_backup" "backing up v1 vectors" 0 1
echo "" | tee -a "$LOG"
echo "─── Phase 1: backup v1 vectors ───" | tee -a "$LOG"
VEC_ROOT="results/vectors/qwen3-4b"
for SUB in triplets-evidence-grounding triplets-reasoning-transparency triplets-combined triplets-intellectual-humility; do
  if [ -d "$VEC_ROOT/$SUB" ] && [ ! -d "$VEC_ROOT/${SUB}_v1_backup" ]; then
    cp -r "$VEC_ROOT/$SUB" "$VEC_ROOT/${SUB}_v1_backup"
    echo "  backed up $SUB → ${SUB}_v1_backup" | tee -a "$LOG"
  else
    echo "  skipping $SUB (already backed up or not present)" | tee -a "$LOG"
  fi
done
# Also need a CC-numeric-only subset corpus
NUMERIC_DIR="../corpus/triplets-cc-numeric-only-symlinks"
if [ ! -d "$NUMERIC_DIR" ]; then
  mkdir -p "$NUMERIC_DIR"
  for D in ../corpus/triplets-combined/claude-cc-*; do
    if [ -d "$D" ]; then
      ln -s "$(realpath "$D")" "$NUMERIC_DIR/$(basename "$D")"
    fi
  done
  echo "  created CC numeric-only symlink dir at $NUMERIC_DIR" | tee -a "$LOG"
fi

# ─── Phase 2: extraction ─────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "─── Phase 2: re-extract from new corpora ───" | tee -a "$LOG"

declare -a CORPORA=(
  "EG|../corpus/mvp-combined/triplets-evidence-grounding"
  "RT|../corpus/mvp-combined/triplets-reasoning-transparency"
  "CC|../corpus/triplets-combined"
  "CC_numeric|$NUMERIC_DIR"
  "IH|../corpus/triplets-intellectual-humility"
)
TOTAL_EXTRACT=${#CORPORA[@]}
IDX=0
for ENTRY in "${CORPORA[@]}"; do
  IDX=$((IDX+1))
  IFS='|' read -r LABEL PATH_ <<< "$ENTRY"
  write_status "phase2_extract" "$LABEL" $IDX $TOTAL_EXTRACT
  echo "" | tee -a "$LOG"
  echo "[$IDX/$TOTAL_EXTRACT] Extracting $LABEL from $PATH_" | tee -a "$LOG"
  "$PYTHON" extract_v2.py \
    --model qwen3-4b \
    --corpus "$PATH_" \
    --method last_token \
    --layers sweep \
    --save-vectors 2>&1 | tail -50 | tee -a "$LOG"
  echo "  done $LABEL at $(date)" | tee -a "$LOG"
done

# ─── Phase 3: cosine-similarity matrix ───────────────────────────────────────
write_status "phase3_cosine" "computing matrix" 1 1
echo "" | tee -a "$LOG"
echo "─── Phase 3: cosine-similarity matrix ───" | tee -a "$LOG"
"$PYTHON" cosine_v2_analysis.py \
  --output "$LOGDIR/cosine_matrix.json" \
  --html "$LOGDIR/cosine_matrix.html" 2>&1 | tee -a "$LOG"

# ─── Phase 4: behavioral diagnostic ──────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "─── Phase 4: behavioral diagnostic with new vectors ───" | tee -a "$LOG"

# We need to make run_benchmark.py aware of the new vectors. Easier: just
# reload after extraction; the registry already points to the same paths
# (triplets-evidence-grounding/last_token/layer_X) so re-extracted vectors
# are loaded automatically by their existing names.
#
# However, the original v_EG_L7, v_RT_L15, etc. now point to v2 vectors.
# We use _v1_backup for v1 access in the cosine analysis only.

declare -a CELLS=(
  # most diagnostic cells from yesterday's batch, re-run with v2 vectors
  "eg-eval-v2|10|EG_L7|4|d22_v2_vEG_L7_a4"
  "eg-eval-v2|10|EG_L7|8|d22_v2_vEG_L7_a8"
  "eg-eval-v2|10|EG_L7|12|d22_v2_vEG_L7_a12"
  "abstention|5|EG_L7|4|d22_v2_vEG_L7_a4_abst"
  "abstention|5|EG_L7|8|d22_v2_vEG_L7_a8_abst"
  "cc-simple|8|L9|4|d22_v2_vCC_L9_a4"
  "cc-simple|8|L9|8|d22_v2_vCC_L9_a8"
  "cc-simple|8|L9|12|d22_v2_vCC_L9_a12"
  "eg-eval-v2|10|IH_L17|8|d22_v2_vIH_L17_a8"
  "abstention|5|IH_L17|8|d22_v2_vIH_L17_a8_abst"
  "cc-simple|8|IH_L17|8|d22_v2_vIH_L17_a8_cc"
  "eg-eval-v2|10|RT_L15|8|d22_v2_vRT_L15_a8"
)
TOTAL_CELLS=${#CELLS[@]}
CIDX=0
for ENTRY in "${CELLS[@]}"; do
  CIDX=$((CIDX+1))
  IFS='|' read -r BENCH N VEC ALPHA LABEL_ <<< "$ENTRY"
  write_status "phase4_behavioral" "$LABEL_" $CIDX $TOTAL_CELLS
  echo "" | tee -a "$LOG"
  echo "[B $CIDX/$TOTAL_CELLS] $LABEL_ (bench=$BENCH n=$N vec=$VEC α=$ALPHA)" | tee -a "$LOG"
  "$PYTHON" run_benchmark.py \
    --benchmark "$BENCH" --n "$N" \
    --condition steered --vector "$VEC" --alpha "$ALPHA" \
    --label "$LABEL_" 2>&1 | tail -30 | tee -a "$LOG"
done

# ─── Done ────────────────────────────────────────────────────────────────────
write_status "complete" "" $TOTAL_CELLS $TOTAL_CELLS
echo "" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "v2 sweep complete at $(date)" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
echo "complete" > "$LOGDIR/done.marker"
exit 0
