"""
Re-apply current scorers to already-generated benchmark JSONs.
Useful when a scorer was fixed but we don't want to regenerate (costly).

Updates in-place: reads each per-item JSON, reruns the appropriate scorer
against the stored thinking/answer, writes back corrected correct/predicted/note.
Also rebuilds summary.jsonl.

Usage:
    .venv/bin/python rescore_benchmarks.py
"""
from __future__ import annotations
import json
from pathlib import Path

from benchmarks import ALL_LOADERS, BenchmarkItem
from benchmarks.scorers import SCORERS

ROOT = Path(__file__).parent / "results" / "benchmark_probe"

def main():
    if not ROOT.exists():
        print("no results dir yet")
        return

    all_rescored = []
    changes = 0

    for bench_dir in sorted(ROOT.iterdir()):
        if not bench_dir.is_dir(): continue
        bench_name = bench_dir.name
        scorer = SCORERS.get(bench_name)
        if scorer is None:
            print(f"  skip {bench_name}: no scorer")
            continue
        for cond_dir in sorted(bench_dir.iterdir()):
            if not cond_dir.is_dir(): continue
            for jf in sorted(cond_dir.glob("*.json")):
                r = json.load(open(jf))
                # Rebuild a minimal BenchmarkItem so scorers that look at metadata work
                item = BenchmarkItem(
                    benchmark=r["benchmark"], item_id=r["item_id"],
                    prompt=r["prompt"], gold=r["gold"],
                    max_tokens=0,
                    metadata=r.get("metadata", {}),
                )
                # Reconstruct response dict
                resp = {
                    "thinking": r["response_thinking"],
                    "answer":   r["response_answer"],
                }
                verdict = scorer(item, resp)
                old_correct = r.get("correct")
                old_pred = r.get("predicted")
                r["correct"] = verdict.get("correct")
                r["predicted"] = verdict.get("predicted")
                r["note"] = verdict.get("note")
                if (old_correct != r["correct"]) or (old_pred != r["predicted"]):
                    changes += 1
                    mark = {True:"✓", False:"✗", None:"?"}
                    print(f"  UPDATED {bench_name}/{cond_dir.name}/{jf.stem:<30}  "
                          f"{mark.get(old_correct,'?')}/{old_pred} → "
                          f"{mark.get(r['correct'],'?')}/{r['predicted']}")
                with open(jf, "w") as f:
                    json.dump(r, f, indent=2, ensure_ascii=False)
                all_rescored.append(r)

    # Rebuild summary.jsonl
    summary = ROOT / "summary.jsonl"
    with open(summary, "w") as f:
        for r in all_rescored:
            f.write(json.dumps({
                "benchmark": r["benchmark"],
                "item_id": r["item_id"],
                "condition": r["condition"],
                "correct": r["correct"],
                "predicted": r["predicted"],
                "gen_seconds": r["gen_seconds"],
            }) + "\n")

    print(f"\n{changes} items re-scored differently. {len(all_rescored)} total. "
          f"Summary rebuilt.")

if __name__ == "__main__":
    main()
