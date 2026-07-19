#!/bin/bash
# Night chain (2026-07-08): top up the J-lens on a PROPER corpus, then re-run everything the
# n=20 lens was too weak for. Sequential (one model job at a time — 16GB). Resumable.
cd "$(dirname "$0")"
PY=.venv/bin/python
LOG=results/workspace/logs
mkdir -p "$LOG"
M="$LOG/night_chain.log"
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$M"; }

note "=== STAGE lens_topup START (resume n=20 -> up to n=100, dim_batch=4) ==="
$PY workspace_t2_fit.py --until 08:30 --max-prompts 100 >> "$LOG/t2_fit_night.log" 2>&1
note "=== lens_topup END rc=$? ; lens meta: $(cat results/workspace/t2_fit_meta.json 2>/dev/null | tr -d '\n') ==="

note "=== STAGE qc_recheck START (does the bigger lens beat logit lens now?) ==="
$PY workspace_t2b_validate.py >> "$LOG/t2b_night.log" 2>&1
note "=== qc_recheck END rc=$? ==="

note "=== STAGE decompose_real START (workspace sparse decomposition on the PROPER lens) ==="
$PY workspace_decompose.py >> "$LOG/decompose_real.log" 2>&1
note "=== decompose_real END rc=$? ; neg-hits: $(grep -o 'neg-concept hits: [0-9]*' $LOG/decompose_real.log | tail -1) ==="

touch results/workspace/NIGHT_CHAIN_DONE
note "=== NIGHT CHAIN COMPLETE ==="
