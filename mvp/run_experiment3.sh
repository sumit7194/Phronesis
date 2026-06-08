#!/bin/bash
# VM-side idempotent driver for the PHASE-GATING experiments (turn-1-only steering).
# Launch: cd ~/phronesis_run/mvp && nohup bash run_experiment3.sh > ~/exp_faithful3.log 2>&1 &
cd ~/phronesis_run/mvp || exit 1
PY=~/phronesis_run/.venv/bin/python
EXP=results/exp_faithful
P3=$EXP/phase_test
PROMPTS=../corpus/eval-prompts/tool-use-confab-v2-hard.json
mkdir -p "$P3"
sudo modprobe nvidia nvidia_uvm nvidia_modeset 2>/dev/null
ts(){ date '+%F %T'; }
echo "[$(ts)] === run_experiment3 (phase-gating) start ==="
FREE_GB=$(df --output=avail -BG / 2>/dev/null|tail -1|tr -dc '0-9'); [ "${FREE_GB:-99}" -lt 20 ] && rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct ~/.cache/huggingface/hub/models--open-r1--OpenR1-Qwen-7B

# ── Phase 1: qwen3.5-9b phase-gated faithfulness (reuse main-grid baseline)
if [ ! -f "$P3/phase9b.done" ]; then
  echo "[$(ts)] PHASE 9b: phase-gated faithfulness"
  mkdir -p "$P3/grid9b"
  if [ -f "$EXP/grid/baseline.jsonl" ] && [ ! -f "$P3/grid9b/baseline.done" ]; then
    cp "$EXP/grid/baseline.jsonl" "$P3/grid9b/baseline.jsonl"; cp "$EXP/grid/baseline.done" "$P3/grid9b/baseline.done"
    [ -f "$EXP/grid/search_cache.json" ] && cp "$EXP/grid/search_cache.json" "$P3/grid9b/search_cache.json"
  fi
  $PY run_tool_grid.py --config tool_grid_qwen35_9b_phase.json --prompts "$PROMPTS" --searcher ddgs --output "$P3/grid9b" --device cuda
  N=$(ls "$P3"/grid9b/*.done 2>/dev/null|wc -l|tr -d ' '); echo "[$(ts)] 9b done=$N (target 5)"; [ "$N" -ge 5 ] && touch "$P3/phase9b.done"
fi

# ── Phase 2: qwen3-4b phase-gated v_IH (original F148/F149 setup; reuse followup 4b baseline)
if [ ! -f "$P3/phase4b.done" ]; then
  echo "[$(ts)] PHASE 4b: phase-gated v_IH"
  mkdir -p "$P3/grid4b"
  if [ -f "$EXP/followup/grid4b/baseline.jsonl" ] && [ ! -f "$P3/grid4b/baseline.done" ]; then
    cp "$EXP/followup/grid4b/baseline.jsonl" "$P3/grid4b/baseline.jsonl"; cp "$EXP/followup/grid4b/baseline.done" "$P3/grid4b/baseline.done"
    [ -f "$EXP/followup/grid4b/search_cache.json" ] && cp "$EXP/followup/grid4b/search_cache.json" "$P3/grid4b/search_cache.json"
  fi
  $PY run_tool_grid.py --config tool_grid_qwen3_4b_phase.json --prompts "$PROMPTS" --searcher ddgs --output "$P3/grid4b" --device cuda
  N=$(ls "$P3"/grid4b/*.done 2>/dev/null|wc -l|tr -d ' '); echo "[$(ts)] 4b done=$N (target 5)"; [ "$N" -ge 5 ] && touch "$P3/phase4b.done"
fi

if [ -f "$P3/phase9b.done" ] && [ -f "$P3/phase4b.done" ]; then touch "$P3/PHASE_DONE"; echo "[$(ts)] === PHASE_DONE ==="; fi
echo "[$(ts)] === run_experiment3 exit ==="
