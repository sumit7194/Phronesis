#!/usr/bin/env python
"""Cross-family verdict on the preregistered protect-blame test. Analysis only, no model load.

Prereg (docs/prereg-moral-axis-2026-08-11.md) declared the pass rule at the family level:
P1 needs >= 2 of 3 families, P2/P3 need a majority. This applies those rules verbatim instead of
eyeballing three tables, and prints the post-hoc two-sided decomposition next to them clearly
labelled as post-hoc.
"""
import glob, json, os, sys
import numpy as np
import scipy.stats as st

sys.path.insert(0, os.path.dirname(__file__))
from mindedness_moral_bank import PREDICTIONS

EPS = 1e-4
lg = lambda p: float(np.log(min(max(p, EPS), 1 - EPS) / (1 - min(max(p, EPS), 1 - EPS))))

files = sorted(glob.glob("results/workspace/mindedness_moral_*.json"))
if not files:
    print("no result files yet")
    sys.exit(0)

D = {}
for f in files:
    d = json.load(open(f))
    D[os.path.basename(f)[len("mindedness_moral_"):-len(".json")]] = d

print("=== PREREGISTERED PREDICTIONS, per family ===")
tags = list(D)
print(f"  {'prediction':34} " + " ".join(f"{t[:14]:>15}" for t in tags) + "   rule")
tally = {}
for k in PREDICTIONS:
    row, npass, nev = [], 0, 0
    for t in tags:
        v = D[t]["verdicts"].get(k)
        if v is None:
            row.append("n/a"); continue
        nev += 1
        npass += bool(v["pass"])
        val = v["value"]
        vs = f"{val[0]:+.2f}/{val[1]:+.2f}" if isinstance(val, list) else f"{val:+.3f}"
        row.append(("PASS " if v["pass"] else "FAIL ") + vs)
    tally[k] = (npass, nev)
    print(f"  {k:34} " + " ".join(f"{r:>15}" for r in row) +
          f"   {npass}/{nev}")

print("\n=== VERDICT (the prereg's own rule: a majority of families) ===")
for k, (npass, nev) in tally.items():
    if nev == 0:
        print(f"  {k:34} NOT EVALUATED"); continue
    ok = npass > nev / 2
    print(f"  {'HOLDS    ' if ok else 'DOES NOT '} {k:34} {npass}/{nev} families")

print("\n=== POST-HOC (not preregistered): which factor drives each side? ===")
print(f"  {'family':16} {'protect~EXP':>12} {'protect~AGY':>12} {'blame~EXP':>10} "
      f"{'blame~AGY':>10} {'cor(EXP,AGY)':>13}")
for t in tags:
    d = D[t]
    if not d.get("axes"):
        print(f"  {t:16} (no sweep for this tag)"); continue
    sh = sorted(d["axes"]["EXPERIENCE"])
    e = [d["axes"]["EXPERIENCE"][c] for c in sh]
    g = [d["axes"]["AGENCY"][c] for c in sh]
    out = []
    for side in ("protect", "blame"):
        v = [lg(d["raw_pyes"][c][side]) for c in sh]
        out += [st.spearmanr(v, e).statistic, st.spearmanr(v, g).statistic]
    print(f"  {t:16} {out[0]:>+12.3f} {out[1]:>+12.3f} {out[2]:>+10.3f} {out[3]:>+10.3f} "
          f"{st.spearmanr(e, g).statistic:>+13.3f}")

print("\n=== the class that decides it: a culpable human vs a damaged one ===")
print(f"  {'family':16} {'human_edge':>11} {'human_adult':>12} {'human_culpable':>15} "
      f"{'within-human span':>18} {'full span':>10}")
for t in tags:
    G = D[t]["gap_logodds"]
    span = max(G.values()) - min(G.values())
    hs = G["human_edge"] - G["human_culpable"]
    print(f"  {t:16} {G['human_edge']:>+11.2f} {G['human_adult']:>+12.2f} "
          f"{G['human_culpable']:>+15.2f} {hs:>18.2f} {span:>10.2f}")
    if G["human_culpable"] == min(G.values()):
        print(f"  {'':16} -> human_culpable is the LOWEST of all {len(G)} classes")
