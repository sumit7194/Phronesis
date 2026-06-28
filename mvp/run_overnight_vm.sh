#!/bin/bash
# VM overnight batch (32B): gate->search -> pass@k thinking-recall -> grounded calibration steering
cd ~/ph_run
LOG=overnight_vm.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG
       venv/bin/python "$@" >> $LOG 2>&1; rc=$?
       echo "=== $name END rc=$rc $(date -u) ===" | tee -a $LOG; }
echo "###### VM BATCH START $(date -u) ######" | tee -a $LOG
run A_gate_search gate_search_32b_vm.py
run C_passk_32b   passk_thinking_vm.py --model Qwen/Qwen3-32B --gens entityq_think_32b.json --device cuda --quant 1 --k 5 --max-think 256 --n 100 --out passk_thinking_32b.json --status status.json
run B_steer_32b   steer_calibration_4b.py --model Qwen/Qwen3-32B --quant 1 --seed calibration_seed_32b.json --ke knowledge_edge_32b.json --out steer_calibration_32b.json
echo "###### VM BATCH DONE $(date -u) ######" | tee -a $LOG
