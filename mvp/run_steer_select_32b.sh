#!/bin/bash
cd ~/ph_run; LOG=steer_select.log
echo "###### STEER SELECT (proper known-eval, L36, save-vec) $(date -u) ######" | tee -a $LOG
venv/bin/python steer_calibration_4b.py --model Qwen/Qwen3-32B --quant 1 \
  --seed calibration_seed_32b_clean.json --ke knowledge_edge_32b.json \
  --known-eval known_eval_32b.json --save-vec v_hedge_32b.npy \
  --layers 20,28,36,44 --steer-layer 36 \
  --alpha-fracs="-0.15,0,0.05,0.1,0.15,0.2,0.25,0.3" \
  --out steer_select_32b_L36.json >> $LOG 2>&1
echo "###### STEER SELECT DONE rc=$? $(date -u) ######" | tee -a $LOG
