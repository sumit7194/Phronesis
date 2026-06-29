#!/bin/bash
cd /Users/sumit/Github/Phronesis/mvp
LOG=/private/tmp/claude-501/-Users-sumit-Github-Phronesis/86be5ceb-ba73-42a0-b50f-3ce5c6b0921f/scratchpad/overnight_mac2.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG; .venv/bin/python "$@" >> $LOG 2>&1; echo "=== $name END rc=$? $(date -u) ===" | tee -a $LOG; }
echo "###### MAC2 START $(date -u) ######" | tee -a $LOG
run TQA_4b truthqa_edge_4b.py --n 150 --k 10
echo "###### MAC2 DONE $(date -u) ######" | tee -a $LOG
