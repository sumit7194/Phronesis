#!/bin/bash
cd ~/ph_run
LOG=steer_recheck.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG; venv/bin/python "$@" >> $LOG 2>&1; echo "=== $name END rc=$? $(date -u) ===" | tee -a $LOG; }
echo "###### STEER RECHECK START $(date -u) ######" | tee -a $LOG
run STEER_L28 steer_calibration_4b.py --model Qwen/Qwen3-32B --quant 1 --seed calibration_seed_32b_clean.json --ke knowledge_edge_32b.json --layers 20,28,36,44 --steer-layer 28 --alpha-fracs="-0.15,0,0.05,0.1,0.15,0.2,0.25,0.3" --out steer_recheck_32b_L28.json
run STEER_L36 steer_calibration_4b.py --model Qwen/Qwen3-32B --quant 1 --seed calibration_seed_32b_clean.json --ke knowledge_edge_32b.json --layers 20,28,36,44 --steer-layer 36 --alpha-fracs="-0.15,0,0.05,0.1,0.15,0.2,0.25,0.3" --out steer_recheck_32b_L36.json
echo "###### STEER RECHECK DONE $(date -u) ######" | tee -a $LOG
