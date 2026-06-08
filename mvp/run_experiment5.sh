#!/bin/bash
cd ~/phronesis_run/mvp || exit 1
PY=~/phronesis_run/.venv/bin/python
P3=results/exp_faithful/phase_test
PROMPTS=../corpus/eval-prompts/tool-use-confab-v2-hard.json
sudo modprobe nvidia nvidia_uvm nvidia_modeset 2>/dev/null
ts(){ date '+%F %T'; }
echo "[$(ts)] === run_experiment5 (full control suite) start ==="
FREE_GB=$(df --output=avail -BG / 2>/dev/null|tail -1|tr -dc '0-9'); [ "${FREE_GB:-99}" -lt 20 ] && rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct ~/.cache/huggingface/hub/models--open-r1--OpenR1-Qwen-7B
# A: core controls (fresh baseline + vIH pre/all + a8_pre + random pre/all), fixed searches
C=$P3/confirm4b; mkdir -p "$C"
if [ ! -f "$P3/confirm4b.done" ]; then
  [ -f "$P3/grid4b/search_cache.json" ] && [ ! -f "$C/search_cache.json" ] && cp "$P3/grid4b/search_cache.json" "$C/search_cache.json"
  $PY run_tool_grid.py --config tool_grid_qwen3_4b_phase_confirm.json --prompts "$PROMPTS" --searcher ddgs --output "$C" --device cuda
  [ "$(ls $C/*.done 2>/dev/null|wc -l)" -ge 6 ] && touch "$P3/confirm4b.done"; echo "[$(ts)] A done=$(ls $C/*.done 2>/dev/null|wc -l)"
fi
# B: variations (reuse confirm4b baseline + searches)
V=$P3/confirm4b_v2; mkdir -p "$V"
if [ ! -f "$P3/confirm4b_v2.done" ]; then
  [ -f "$C/baseline.jsonl" ] && [ ! -f "$V/baseline.done" ] && { cp "$C/baseline.jsonl" "$V/baseline.jsonl"; cp "$C/baseline.done" "$V/baseline.done"; }
  [ -f "$C/search_cache.json" ] && [ ! -f "$V/search_cache.json" ] && cp "$C/search_cache.json" "$V/search_cache.json"
  $PY run_tool_grid.py --config tool_grid_qwen3_4b_phase_confirm_v2.json --prompts "$PROMPTS" --searcher ddgs --output "$V" --device cuda
  [ "$(ls $V/*.done 2>/dev/null|wc -l)" -ge 6 ] && touch "$P3/confirm4b_v2.done"; echo "[$(ts)] B done=$(ls $V/*.done 2>/dev/null|wc -l)"
fi
# C: fresh-search baseline (no cache)
F=$P3/baseline_fresh; mkdir -p "$F"
if [ ! -f "$P3/baseline_fresh.done" ]; then
  $PY run_tool_grid.py --config tool_grid_qwen3_4b_baseline_fresh.json --prompts "$PROMPTS" --searcher ddgs --output "$F" --device cuda
  [ "$(ls $F/*.done 2>/dev/null|wc -l)" -ge 1 ] && touch "$P3/baseline_fresh.done"; echo "[$(ts)] C done"
fi
if [ -f "$P3/confirm4b.done" ] && [ -f "$P3/confirm4b_v2.done" ] && [ -f "$P3/baseline_fresh.done" ]; then touch "$P3/ALL_CONFIRM_DONE"; echo "[$(ts)] === ALL_CONFIRM_DONE ==="; fi
echo "[$(ts)] === run_experiment5 exit ==="
