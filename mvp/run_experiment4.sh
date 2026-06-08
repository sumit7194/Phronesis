#!/bin/bash
cd ~/phronesis_run/mvp || exit 1
PY=~/phronesis_run/.venv/bin/python
P3=results/exp_faithful/phase_test
C=$P3/confirm4b
PROMPTS=../corpus/eval-prompts/tool-use-confab-v2-hard.json
mkdir -p "$C"
sudo modprobe nvidia nvidia_uvm nvidia_modeset 2>/dev/null
ts(){ date '+%F %T'; }
echo "[$(ts)] === run_experiment4 (confirm+controls) start ==="
FREE_GB=$(df --output=avail -BG / 2>/dev/null|tail -1|tr -dc '0-9'); [ "${FREE_GB:-99}" -lt 20 ] && rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct ~/.cache/huggingface/hub/models--open-r1--OpenR1-Qwen-7B
if [ ! -f "$P3/confirm4b.done" ]; then
  # copy original phase grid's SEARCH CACHE only (identical searches) — but NOT baseline.jsonl (we want a FRESH baseline run)
  [ -f "$P3/grid4b/search_cache.json" ] && [ ! -f "$C/search_cache.json" ] && cp "$P3/grid4b/search_cache.json" "$C/search_cache.json"
  $PY run_tool_grid.py --config tool_grid_qwen3_4b_phase_confirm.json --prompts "$PROMPTS" --searcher ddgs --output "$C" --device cuda
  N=$(ls "$C"/*.done 2>/dev/null|wc -l|tr -d ' '); echo "[$(ts)] confirm done=$N (target 6)"; [ "$N" -ge 6 ] && touch "$P3/confirm4b.done"
fi
echo "[$(ts)] === run_experiment4 exit ==="
