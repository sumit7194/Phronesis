#!/bin/bash
# 1) masked readout of all 6 on the current n=45 lens (first look, ~10 min, no regeneration)
# 2) preserve those as _n45
# 3) fit the lens toward n~100-110 overnight (repo's "usable" bar; ~14 min/prompt on this Mac)
# 4) re-run masked readout on the bigger lens (clean version)
cd "$(dirname "$0")"
PY=.venv/bin/python
LOG=results/workspace/logs
M="$LOG/masked_chain.log"
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$M"; }

note "=== STAGE remask_n45 START (all 6, current lens) ==="
$PY workspace_6q_remask.py >> "$LOG/remask_n45.log" 2>&1
note "=== remask_n45 END rc=$? ==="

for id in q1_no_a q2_math_solved q3_gsm_rescuable q4_math_wall q5_gsm_solved q6_gsm_failed; do
  cp -f results/workspace/6q/${id}_masked.json results/workspace/6q/${id}_masked_n45.json 2>/dev/null
  cp -f results/workspace/6q/${id}_masked.txt  results/workspace/6q/${id}_masked_n45.txt  2>/dev/null
done
note "preserved n45 masked outputs as *_masked_n45"
touch results/workspace/REMASK_N45_DONE

note "=== STAGE lens_fit START (resume n=45 -> ~100, until 08:00) ==="
$PY workspace_t2_fit.py --until 08:00 --max-prompts 120 >> "$LOG/t2_fit_bignight.log" 2>&1
note "=== lens_fit END rc=$? ; meta: $(cat results/workspace/t2_fit_meta.json 2>/dev/null | tr -d '\n') ==="

note "=== STAGE remask_big START (all 6, bigger lens) ==="
$PY workspace_6q_remask.py >> "$LOG/remask_big.log" 2>&1
note "=== remask_big END rc=$? ==="

touch results/workspace/MASKED_CHAIN_DONE
note "=== MASKED CHAIN COMPLETE ==="
