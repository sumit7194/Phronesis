#!/bin/bash
# Quantization-vs-scale 2x2 for thinking-recall (F177 confound, Lotfi et al. 2606.00206)
# Identical params all arms: k=5, n=100, max-think 512, T=0.7. 4B-fp16 re-run for internal consistency.
cd ~/ph_run; LOG=quant2x2.log
run(){ name=$1; shift; echo "=== $name START $(date -u) ===" | tee -a $LOG; venv/bin/python "$@" >> $LOG 2>&1; echo "=== $name END rc=$? $(date -u) ===" | tee -a $LOG; }
echo "###### QUANT 2x2 $(date -u) ######" | tee -a $LOG
run P4B_FP16 passk_thinking_vm.py --model Qwen/Qwen3-4B  --quant 0 --device cuda --k 5 --n 100 --max-think 512 --out passk_4b_fp16.json
run P4B_4BIT passk_thinking_vm.py --model Qwen/Qwen3-4B  --quant 1 --device cuda --k 5 --n 100 --max-think 512 --out passk_4b_4bit.json
run P8B_FP16 passk_thinking_vm.py --model Qwen/Qwen3-8B  --quant 0 --device cuda --k 5 --n 100 --max-think 512 --out passk_8b_fp16.json
run P8B_4BIT passk_thinking_vm.py --model Qwen/Qwen3-8B  --quant 1 --device cuda --k 5 --n 100 --max-think 512 --out passk_8b_4bit.json
echo "###### QUANT 2x2 DONE $(date -u) ######" | tee -a $LOG
