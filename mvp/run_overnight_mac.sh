#!/bin/bash
# Mac overnight batch (4B local): pass@k thinking-recall -> TruthfulQA generalization
cd /Users/sumit/Github/Phronesis/mvp
LOG=/private/tmp/claude-501/-Users-sumit-Github-Phronesis/86be5ceb-ba73-42a0-b50f-3ce5c6b0921f/scratchpad/overnight_mac.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG
       .venv/bin/python "$@" >> $LOG 2>&1; rc=$?
       echo "=== $name END rc=$rc $(date -u) ===" | tee -a $LOG; }
echo "###### MAC BATCH START $(date -u) ######" | tee -a $LOG
run C_passk_4b passk_thinking_vm.py --model Qwen/Qwen3-4B --gens results/legibility/entityq_think_Qwen3-4B.json --device mps --quant 0 --k 5 --max-think 256 --n 100 --out results/legibility/passk_thinking_4b.json --status results/legibility/status_passk_4b.json
run D_truthqa  truthqa_edge_4b.py --n 150
echo "###### MAC BATCH DONE $(date -u) ######" | tee -a $LOG
