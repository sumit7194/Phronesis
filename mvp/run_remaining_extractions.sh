#!/bin/bash
# Focused extraction — comprehension + last_token only, skip generation for large corpora.
# Resume-safe.

PYTHON="$(dirname "$0")/.venv/bin/python"
EXTRACT="$(dirname "$0")/extract_v2.py"
LOGFILE="$(dirname "$0")/results/extraction_sweep.log"

echo "==========================================" | tee -a "$LOGFILE"
echo "Phronesis — Remaining Extractions (focused)" | tee -a "$LOGFILE"
echo "Started: $(date)" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"

run() {
  local model=$1 corpus=$2 method=$3
  local corpus_name=$(basename "$corpus")
  echo "" | tee -a "$LOGFILE"
  echo ">>> $model / $corpus_name / $method — $(date)" | tee -a "$LOGFILE"
  "$PYTHON" "$EXTRACT" \
    --model "$model" \
    --method "$method" \
    --layers all \
    --corpus "$corpus" \
    --save-vectors \
    2>&1 | tail -25 | tee -a "$LOGFILE"
  echo "    Done: $model / $corpus_name / $method at $(date)" | tee -a "$LOGFILE"
}

# Gemma — remaining (Sonnet last_token only, rest done)
run gemma-2-2b-it "../corpus/triplets-synthetic-sonnet" last_token

# Qwen — comprehension + last_token for all 3 corpora
run qwen-2.5-3b-it "../corpus/triplets" comprehension
run qwen-2.5-3b-it "../corpus/triplets" last_token
run qwen-2.5-3b-it "../corpus/triplets-synthetic-chatgpt" comprehension
run qwen-2.5-3b-it "../corpus/triplets-synthetic-chatgpt" last_token
run qwen-2.5-3b-it "../corpus/triplets-synthetic-sonnet" comprehension
run qwen-2.5-3b-it "../corpus/triplets-synthetic-sonnet" last_token

echo "" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "ALL REMAINING EXTRACTIONS COMPLETE at $(date)" | tee -a "$LOGFILE"
echo "==========================================" | tee -a "$LOGFILE"
echo "complete" > "$(dirname "$0")/results/extraction_sweep_done.marker"
