#!/bin/bash
cd ~/ph_run
LOG=overnight_vm2.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG; venv/bin/python "$@" >> $LOG 2>&1; echo "=== $name END rc=$? $(date -u) ===" | tee -a $LOG; }
echo "###### VM2 START $(date -u) ######" | tee -a $LOG
run TQA_32b   truthqa_edge_4b.py --model Qwen/Qwen3-32B --quant 1 --k 5 --n 150 --out truthqa_edge_32b.json --status status.json
run PASSK2_32b passk_thinking_vm.py --model Qwen/Qwen3-32B --gens entityq_think_32b.json --device cuda --quant 1 --k 3 --max-think 768 --n 50 --out passk_thinking_32b_v2.json --status status.json
echo "###### VM2 DONE $(date -u) ######" | tee -a $LOG
