#!/bin/bash
# S5 Qwen3.5 at layer 16, one chunk per process. The MPS allocator grows ~4.7->11GB across a
# 2h process no matter what empty_cache() does, so we take the memory back by exiting.
cd "$(dirname "$0")"
LOG=results/workspace/logs/v2_rest.log
OUT=results/workspace/mindedness_v2_steer_Qwen3_5-4B_L16.json
note(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
swap_mb(){ sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
cells(){ .venv/bin/python -c "import json;d=json.load(open('$OUT'));print(sum(len(v) for v in d['runs'].values()))" 2>/dev/null || echo 0; }
TARGET=27
for i in $(seq 1 40); do
  n=$(cells); [ "$n" -ge "$TARGET" ] && { note "S5 Q3.5 L16 COMPLETE ($n/$TARGET cells)"; break; }
  w=0; while [ "$(swap_mb)" -gt 2500 ] && [ $w -lt 600 ]; do sleep 20; w=$((w+20)); done
  note "chunk $i: $n/$TARGET cells, swap $(swap_mb)MB"
  .venv/bin/python mindedness_v2_steer.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B --layer 16 --max-cells 3 >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && note "chunk $i exited rc=$rc"
  after=$(cells); [ "$after" -le "$n" ] && { note "NO PROGRESS in chunk $i ($n -> $after) - stopping"; break; }
done
note "S5 Q3.5 L16 driver finished with $(cells)/$TARGET cells"
