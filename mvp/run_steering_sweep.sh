#!/bin/bash
# Comprehensive overnight steering experiment.
# Runs all 12 good vectors × 3 steering methods on eval prompts.
# Uses 5 alphas instead of 10 to save time.
# Each run: 25 prompts × (1 baseline + 5 steered) = 150 generations ≈ 10 min
# Total: 12 vectors × 3 methods = 36 runs ≈ 6 hours
#
# Resume-safe: skips output files that already exist.

PYTHON="$(dirname "$0")/.venv/bin/python"
STEER="$(dirname "$0")/steer.py"
PROMPTS="$(dirname "$0")/../corpus/eval-prompts/calibrated-confidence.json"
VECTORS_DIR="$(dirname "$0")/results/vectors"
STEERING_DIR="$(dirname "$0")/results/steering"
LOGFILE="$(dirname "$0")/results/steering_sweep.log"

mkdir -p "$STEERING_DIR"

METHODS=("additive" "spherical" "conditional")

# All 12 vectors: model / corpus / extraction_method / layer
VECTORS=(
  # Gemma vectors
  "gemma-2-2b-it|triplets|comprehension|13"
  "gemma-2-2b-it|triplets|last_token|17"
  "gemma-2-2b-it|triplets-synthetic-chatgpt|comprehension|8"
  "gemma-2-2b-it|triplets-synthetic-chatgpt|last_token|17"
  "gemma-2-2b-it|triplets-synthetic-sonnet|comprehension|14"
  "gemma-2-2b-it|triplets-synthetic-sonnet|last_token|12"
  # Qwen vectors
  "qwen-2.5-3b-it|triplets|comprehension|24"
  "qwen-2.5-3b-it|triplets|last_token|25"
  "qwen-2.5-3b-it|triplets-synthetic-chatgpt|comprehension|23"
  "qwen-2.5-3b-it|triplets-synthetic-chatgpt|last_token|9"
  "qwen-2.5-3b-it|triplets-synthetic-sonnet|comprehension|26"
  "qwen-2.5-3b-it|triplets-synthetic-sonnet|last_token|18"
)

TOTAL=$((${#VECTORS[@]} * ${#METHODS[@]}))
COUNT=0

echo "==========================================" | tee -a "$LOGFILE"
echo "Phronesis — Steering Sweep" | tee -a "$LOGFILE"
echo "Started: $(date)" | tee -a "$LOGFILE"
echo "Total runs: $TOTAL" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"

for entry in "${VECTORS[@]}"; do
  IFS='|' read -r model corpus ext_method layer <<< "$entry"

  vec_path="$VECTORS_DIR/$model/$corpus/$ext_method/layer_${layer}_virtue_vector.npy"

  if [ ! -f "$vec_path" ]; then
    echo "SKIP (missing vector): $vec_path" | tee -a "$LOGFILE"
    continue
  fi

  for steer_method in "${METHODS[@]}"; do
    COUNT=$((COUNT + 1))

    # Output filename
    out_name="${model}_${corpus}_${ext_method}_L${layer}_${steer_method}"
    out_path="$STEERING_DIR/${out_name}.json"

    # Skip if already done
    if [ -f "$out_path" ]; then
      echo "[$COUNT/$TOTAL] SKIP (exists): $out_name" | tee -a "$LOGFILE"
      continue
    fi

    echo "" | tee -a "$LOGFILE"
    echo "[$COUNT/$TOTAL] $out_name — $(date)" | tee -a "$LOGFILE"

    EXTRA_FLAGS=""
    if [ "$steer_method" = "conditional" ]; then
      EXTRA_FLAGS="--auto-threshold"
    fi

    "$PYTHON" "$STEER" \
      --model "$model" \
      --vector "$vec_path" \
      --layer "$layer" \
      --method "$steer_method" \
      --sweep \
      --prompts "$PROMPTS" \
      --output "$out_path" \
      --max-tokens 256 \
      $EXTRA_FLAGS \
      2>&1 | tail -15 | tee -a "$LOGFILE"

    echo "    Done: $out_name at $(date)" | tee -a "$LOGFILE"
  done
done

echo "" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "ALL STEERING COMPLETE at $(date)" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "complete" > "$(dirname "$0")/results/steering_sweep_done.marker"
