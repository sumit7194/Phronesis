#!/bin/bash
# Resume the lens fit (n=70 -> ~110 by 08:00), then refresh all readouts + the viewer at the
# bigger lens: the 6 curated questions, the plain no-a run, and the rebuilt HTML (7 tabs).
cd "$(dirname "$0")"; PY=.venv/bin/python; LOG=results/workspace/logs
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG/resume_fit.log"; }
note "=== resume fit n=70 -> ~110 (until 08:00) ==="
$PY workspace_t2_fit.py --until 08:00 --max-prompts 120 >> "$LOG/t2_fit_bignight.log" 2>&1
note "=== fit END rc=$? ; $(cat results/workspace/t2_fit_meta.json 2>/dev/null|tr -d '\n') ==="
note "=== prompt-inclusive remask (6 questions) on the bigger lens ==="
$PY workspace_6q_remask.py >> "$LOG/remask_big.log" 2>&1
note "=== regenerate plain no-a on the bigger lens ==="
$PY workspace_plain_noa.py >> "$LOG/plain_noa_big.log" 2>&1
note "=== rebuild viewer (7 tabs) at n~110 ==="
$PY build_6q_viewer.py --suffix _masked >> "$LOG/viewer_big.log" 2>&1
touch results/workspace/BIGLENS_VIEWER_DONE
note "=== COMPLETE — viewer.html refreshed at bigger lens ==="
