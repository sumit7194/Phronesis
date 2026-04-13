#!/bin/bash
# Qwen3-4B full extraction pipeline — all 3 usable corpora
# Run this and go to sleep. Resume-safe (skips completed layers).
#
# Corpora: hand-crafted (50), Sonnet (100), ChatGPT (16)
# Method: comprehension (batched) + last_token (batched)
# Layers: all 36
#
# Usage: cd mvp && bash run_qwen3_extraction.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=".venv/bin/python"
LOG="results/qwen3_extraction.log"
mkdir -p results

echo "========================================" | tee -a "$LOG"
echo "Qwen3-4B Extraction Pipeline"           | tee -a "$LOG"
echo "Started: $(date)"                        | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

CORPORA=(
    "../corpus/triplets"
    "../corpus/triplets-synthetic-sonnet"
    "../corpus/triplets-synthetic-chatgpt"
)

METHODS=("comprehension" "last_token")

for corpus in "${CORPORA[@]}"; do
    corpus_name=$(basename "$corpus")
    for method in "${METHODS[@]}"; do
        echo "" | tee -a "$LOG"
        echo "────────────────────────────────────────" | tee -a "$LOG"
        echo "Corpus: $corpus_name | Method: $method"   | tee -a "$LOG"
        echo "Time: $(date)"                             | tee -a "$LOG"
        echo "────────────────────────────────────────" | tee -a "$LOG"

        $PYTHON -u extract_v2.py \
            --model qwen3-4b \
            --method "$method" \
            --layers all \
            --corpus "$corpus" \
            --save-vectors \
            --batch-size 6 \
            2>&1 | tee -a "$LOG"

        echo "Finished $corpus_name / $method at $(date)" | tee -a "$LOG"
    done
done

echo "" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
echo "ALL EXTRACTIONS COMPLETE"                | tee -a "$LOG"
echo "Finished: $(date)"                       | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"
