"""Scan benchmark_probe per-item JSONs for cap-hit signatures (think_len==0)."""
import json
from pathlib import Path

root = Path(__file__).parent / "results" / "benchmark_probe"
rows = []
for cond_dir in root.glob("*/*/"):
    parts = cond_dir.parts
    bench, cond = parts[-2], parts[-1]
    if cond not in ("baseline", "steered"):
        continue
    for jf in cond_dir.glob("*.json"):
        d = json.load(open(jf))
        ans = d.get("response_answer", "") or ""
        think = d.get("response_thinking", "") or ""
        rows.append({
            "bench": bench, "item": str(d.get("item_id")), "cond": cond,
            "correct": d.get("correct"),
            "pred": str(d.get("predicted"))[:10],
            "secs": round(d.get("gen_seconds", 0), 0),
            "think": len(think), "ans": len(ans),
            "no_close": len(think) == 0 and len(ans) > 5000,
            "path": str(jf),
        })

rows.sort(key=lambda r: (r["bench"], r["item"], r["cond"]))
print(f"{'bench':<12}{'item':<6}{'cond':<10}{'corr':<7}{'pred':<12}{'secs':<7}{'think':<8}{'ans':<7}{'cap-hit?'}")
for r in rows:
    print(f"{r['bench']:<12}{r['item']:<6}{r['cond']:<10}{str(r['correct']):<7}{r['pred']:<12}{int(r['secs']):<7}{r['think']:<8}{r['ans']:<7}{r['no_close']}")

flagged = [r for r in rows if r["no_close"]]
print(f"\n{len(flagged)} cap-hit items to delete:")
for r in flagged:
    print(r["path"])
