#!/bin/bash
# Sequential extraction across all usable corpora, all layers, all methods, both models.
# Resume-safe: skips already-saved layers via --save-vectors checkpoint logic.
#
# Usage: cd mvp && bash run_all_extractions.sh
# Monitor: open http://localhost:5050 (dashboard)

PYTHON="$(dirname "$0")/.venv/bin/python"
EXTRACT="$(dirname "$0")/extract_v2.py"
LOGFILE="$(dirname "$0")/results/extraction_sweep.log"

# Usable corpora (correct direction signal — verified on both Gemma and Qwen)
CORPORA=(
  "../corpus/triplets"
  "../corpus/triplets-synthetic-chatgpt"
  "../corpus/triplets-synthetic-sonnet"
)

MODELS=("gemma-2-2b-it" "qwen-2.5-3b-it")
METHODS=("comprehension" "generation" "last_token")
LAYERS="all"  # all 26 layers

TOTAL=$((${#CORPORA[@]} * ${#MODELS[@]} * ${#METHODS[@]}))
COUNT=0

echo "==========================================" | tee -a "$LOGFILE"
echo "Phronesis — Full Extraction Sweep" | tee -a "$LOGFILE"
echo "Started: $(date)" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "Models: ${MODELS[*]}" | tee -a "$LOGFILE"
echo "Corpora: ${#CORPORA[@]}" | tee -a "$LOGFILE"
echo "Methods: ${#METHODS[@]}" | tee -a "$LOGFILE"
echo "Total runs: $TOTAL" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

for model in "${MODELS[@]}"; do
  echo "" | tee -a "$LOGFILE"
  echo "=== MODEL: $model ===" | tee -a "$LOGFILE"
  for corpus in "${CORPORA[@]}"; do
    corpus_name=$(basename "$corpus")
    for method in "${METHODS[@]}"; do
      COUNT=$((COUNT + 1))
      echo "" | tee -a "$LOGFILE"
      echo ">>> [$COUNT/$TOTAL] $model / $corpus_name / $method" | tee -a "$LOGFILE"
      echo "    $(date)" | tee -a "$LOGFILE"
      "$PYTHON" "$EXTRACT" \
        --model "$model" \
        --method "$method" \
        --layers "$LAYERS" \
        --corpus "$corpus" \
        --save-vectors \
        2>&1 | tail -25 | tee -a "$LOGFILE"
      echo "    Done: $model / $corpus_name / $method at $(date)" | tee -a "$LOGFILE"
    done
  done
done

# Write completion marker
echo "" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "ALL EXTRACTIONS COMPLETE at $(date)" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"

# Write a completion file for cron to detect
echo "complete" > "$(dirname "$0")/results/extraction_sweep_done.marker"
