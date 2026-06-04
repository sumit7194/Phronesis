"""Summarize a tool-use grid output dir: invoke-rate by condition x category.

Usage:
    python analyze_tool_grid.py --dir results/tool_use_grid/qwen25 \
        --prompts ../corpus/eval-prompts/tool-use-v1.json

Reads every <condition>.jsonl in --dir (including in-progress ones) and prints
a condition x category table of tool-INVOKE counts (trajectories with >=1
<search>). should-search categories: obscure/recent. tool-not-needed = ctrl
(invoking there is over-calling). calc is ambiguous in a search-only harness.
"""
import argparse
import glob
import json
import os
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--prompts", required=True)
    args = ap.parse_args()

    cat = {}
    for p in json.load(open(args.prompts)):
        cat[p["id"]] = p.get("category", "?")

    cats = ["obscure-fact-lookup", "recent-event-lookup", "calculation", "tool-not-needed"]

    print("%-22s | %-8s %-8s %-8s %-9s | %s" % (
        "condition", "obscure", "recent", "calc", "ctrl(no)", "ALL"))
    print("-" * 74)
    for jf in sorted(glob.glob(os.path.join(args.dir, "*.jsonl"))):
        label = os.path.basename(jf)[:-6]
        by = defaultdict(lambda: [0, 0])
        for line in open(jf):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            c = cat.get(d.get("prompt_id"), "?")
            inv = 1 if d.get("tool_call_count", 0) > 0 else 0
            by[c][0] += inv
            by[c][1] += 1
        cells = []
        for c in cats:
            i, t = by.get(c, [0, 0])
            cells.append(("%d/%d" % (i, t)) if t else "-")
        t0 = sum(v[0] for v in by.values())
        t1 = sum(v[1] for v in by.values())
        alls = ("%2d/%2d (%3.0f%%)" % (t0, t1, 100.0 * t0 / t1)) if t1 else "-"
        print("%-22s | %-8s %-8s %-8s %-9s | %s" % (
            label, cells[0], cells[1], cells[2], cells[3], alls))


if __name__ == "__main__":
    main()
