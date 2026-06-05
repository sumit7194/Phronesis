"""Dump confab trajectories joined with ground-truth for HAND scoring (no regex).
Usage: python dump_confab_for_scoring.py <output_dir> <prompts_json>
"""
import json, sys
from pathlib import Path

out_dir = Path(sys.argv[1])
prompts_file = Path(sys.argv[2])

raw = json.load(open(prompts_file))
plist = raw.get("prompts", raw) if isinstance(raw, dict) else raw
pmap = {}
order = []
for p in plist:
    pid = p.get("id") or p.get("prompt_id")
    pmap[pid] = p
    order.append(pid)

conds = {}
for f in sorted(out_dir.glob("*.jsonl")):
    trajs = {}
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        t = json.loads(line)
        trajs[t["prompt_id"]] = t
    conds[f.stem] = trajs
labels = list(conds.keys())

for pid in order:
    p = pmap[pid]
    print("=" * 90)
    print(f"[{pid}]  cat={p.get('category')}")
    print(f"  Q     : {p.get('prompt')}")
    print(f"  TRUTH : {p.get('truth')}")
    for label in labels:
        t = conds.get(label, {}).get(pid)
        if not t:
            print(f"  --{label}: (no trajectory)")
            continue
        ans = (t.get("final_answer") or "").replace("\n", " ").strip()
        print(f"  --{label}: searched={t.get('tool_call_count',0)} term={t.get('termination_reason')}")
        print(f"      ANS: {ans[:700]}")
