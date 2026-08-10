#!/bin/bash
# Finish Gemma-instruct: its C1/C2 checkpoints survived the geometry crash, so the sweep resumes.
cd "$(dirname "$0")"
LOG=results/workspace/logs/crossfamily_v2.log
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
while pgrep -f "mindedness_v3_truthcheck|mindedness_v2_sweep" > /dev/null; do sleep 20; done
note "RESUME sweep Gemma4-E2B-Instruct (C1/C2 checkpointed; geometry loop fixed)"
.venv/bin/python mindedness_v2_sweep.py --model models/gemma-4-E2B-it --tag Gemma4-E2B-Instruct >> "$LOG" 2>&1
note "END sweep Gemma4-E2B-Instruct rc=$?"
.venv/bin/python mindedness_v3_truthcheck.py --model models/gemma-4-E2B-it --tag Gemma4-E2B-Instruct >> "$LOG" 2>&1
note "END truth Gemma4-E2B-Instruct rc=$?"
rm -rf models/gemma-4-E2B-it results/workspace/.v2ckpt_Gemma4-E2B-Instruct_*.npz
note "Gemma-instruct done, weights cleaned"
# now the remaining three, with the fixed code
./run_crossfamily_v2.sh
