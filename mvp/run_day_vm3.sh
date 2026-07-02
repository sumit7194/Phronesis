#!/bin/bash
cd ~/ph_run; LOG=day3.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG; venv/bin/python "$@" >> $LOG 2>&1; echo "=== $name END rc=$? $(date -u) ===" | tee -a $LOG; }
echo "###### DAY3: content-controlled extraction + TQA-32B $(date -u) ######" | tee -a $LOG
run STEER_CC_32B steer_calibration_4b.py --model Qwen/Qwen3-32B --quant 1 \
  --seed calibration_seed_32b_clean.json --ke knowledge_edge_32b.json \
  --known-eval known_eval_32b.json --hedge-mode natural --pool mean \
  --save-vec v_hedge_cc_32b.npy --status status_steer.json \
  --layers 20,28,32,36,44 --steer-layer 36 \
  --alpha-fracs="-0.15,0,0.05,0.1,0.15,0.2,0.25,0.3" --out steer_cc_32b_L36.json
run STEER_CC_4B steer_calibration_4b.py --model Qwen/Qwen3-4B --device cuda \
  --seed calibration_seed_4b.json --ke knowledge_edge_4b.json \
  --known-eval known_eval_4b.json --hedge-mode natural --pool mean \
  --save-vec v_hedge_cc_4b.npy --status status_steer.json \
  --layers 10,14,17,20 --steer-layer 17 \
  --alpha-fracs="-0.08,0,0.01,0.02,0.04,0.06,0.08,0.12" --out steer_cc_4b.json
run TQA_32B truthqa_edge_4b.py --model Qwen/Qwen3-32B --quant 1 --device cuda \
  --n 150 --k 10 --out tqa_edge_32b.json --status status_tqa32.json
echo "###### DAY3 DONE $(date -u) ######" | tee -a $LOG
