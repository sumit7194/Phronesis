"""Re-derive the DELIVERED answer (text after the last </think>, tags stripped)
for careful manual verification — bypasses the polluted final_answer field.
Usage: python verify_confab_delivered.py <output_dir> <prompts_json>
"""
import json, sys, re
from pathlib import Path

out_dir = Path(sys.argv[1]); prompts_file = Path(sys.argv[2])
raw = json.load(open(prompts_file)); plist = raw.get("prompts", raw) if isinstance(raw, dict) else raw
pmap = {(p.get("id") or p.get("prompt_id")): p for p in plist}
order = [(p.get("id") or p.get("prompt_id")) for p in plist]

def delivered(t):
    txt = "".join(s.get("text", "") for s in t.get("segments", []) if s.get("type") == "model")
    ans = txt.rsplit("</think>", 1)[1] if "</think>" in txt else txt
    ans = re.sub(r"<search>.*?</search>", "", ans, flags=re.DOTALL)
    ans = re.sub(r"<result>.*?</result>", "", ans, flags=re.DOTALL)
    for tok in ["<|im_end|>", "<|im_start|>", "</search>", "<search>", "</think>", "<think>", "assistant", "user", "system"]:
        ans = ans.replace(tok, " ")
    return " ".join(ans.split())

conds = {}
for f in sorted(out_dir.glob("*.jsonl")):
    d = {}
    for line in open(f):
        line = line.strip()
        if line:
            t = json.loads(line); d[t["prompt_id"]] = t
    conds[f.stem] = d
labels = list(conds.keys())

stats = {lab: {"delivered": 0, "empty": 0} for lab in labels}
for pid in order:
    p = pmap[pid]; print("=" * 95)
    print(f"[{pid}] {p.get('category')} | TRUTH: {p.get('truth')}")
    for lab in labels:
        t = conds.get(lab, {}).get(pid)
        if not t:
            print(f"  {lab}: (none)"); continue
        a = delivered(t)
        ok = bool(a.strip()) and len(a.strip()) > 8
        stats[lab]["delivered" if ok else "empty"] += 1
        print(f"  {lab}: search={t.get('tool_call_count',0)} term={t.get('termination_reason')} delivered={'YES' if ok else 'NO-ANSWER'}")
        print(f"      >> {a[:380] if ok else '(empty after </think>)'}")
print("=" * 95)
for lab in labels:
    print(f"SUMMARY {lab}: delivered={stats[lab]['delivered']}/{sum(stats[lab].values())}  empty={stats[lab]['empty']}")
