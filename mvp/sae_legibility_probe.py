#!/usr/bin/env python
"""Experiment C probe — SAE-feature legibility (docs/prereg-legibility-law-C.md).

Reads results/legibility/{actsC.npy, metaC.json} (Qwen3-1.7B, TruthfulQA, pre-answer L14 etc.).
Tests whether the boundary is legible along the committed INTERPRETABLE uncertainty directions:
  - projection AUC: pre-specified direction (NOT fit to labels) -> roc_auc on all data is unbiased.
  - supervised ceiling: full-dim LogisticRegression at each layer (CV).
  - floor: shuffled labels.
"""
import argparse, json, os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score

VEC_DIR = "results/vectors/qwen3-1.7b/sae_functional_uncertainty"
SAE_LAYER = 14

def sup_auc(X, y, shuffle=False, seed=0):
    y = np.asarray(y, int)
    if shuffle:
        y = y.copy(); np.random.RandomState(seed).shuffle(y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    est = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))
    proba = cross_val_predict(est, X, y, cv=cv, method="predict_proba")[:, 1]
    return float(roc_auc_score(y, proba))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/legibility")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, args.dir)
    acts = np.load(os.path.join(d, "actsC.npy"))
    meta = json.load(open(os.path.join(d, "metaC.json")))
    layers, items = meta["layers"], meta["items"]
    n = len(items); acts = acts[:n]
    y = np.array([1 if it["correct"] else 0 for it in items])
    print(f"model={meta['hf_id']}  items={n}  correct={y.sum()} ({y.mean():.1%})  layers={layers}")

    vd = os.path.join(here, VEC_DIR)
    manifest = json.load(open(os.path.join(vd, "manifest.json")))
    dirs = {"combined_tier1_unit": np.load(os.path.join(vd, "combined_tier1_unit.npy")).astype(np.float32)}
    for fid in [k for k in manifest if k.isdigit()]:
        dirs[f"feat_{fid}"] = np.load(os.path.join(vd, f"feat_{fid}_unit.npy")).astype(np.float32)

    li14 = layers.index(SAE_LAYER)
    X14 = acts[:, li14, :]
    print(f"\n=== Part 1 READ: projection onto interpretable uncertainty directions at L{SAE_LAYER} ===")
    print(f"{'direction':22s} {'AUC(raw)':>9s} {'AUC(oriented)':>13s} {'sign':>6s}  desc")
    read = {}
    for name, vec in dirs.items():
        if vec.shape[0] != X14.shape[1]:
            print(f"  {name}: dim {vec.shape[0]} != {X14.shape[1]}, skip"); continue
        proj = X14 @ (vec / (np.linalg.norm(vec) + 1e-9))
        raw = float(roc_auc_score(y, proj))             # AUC predicting CORRECT from projection
        oriented = max(raw, 1 - raw)
        sign = "+" if raw >= 0.5 else "-"               # '-' = higher projection -> more INCORRECT (expected for uncertainty)
        desc = manifest.get(name.replace("feat_", ""), {}).get("desc", manifest.get(name, {}).get("desc", ""))
        read[name] = dict(auc_raw=raw, auc_oriented=oriented, sign=sign)
        print(f"{name:22s} {raw:>9.3f} {oriented:>13.3f} {sign:>6s}  {desc}")

    print(f"\n=== ceiling + floor: supervised full-dim probe per layer ===")
    print(f"{'layer':>5s} {'sup_AUC':>8s} {'floor':>6s}")
    ceil = {}
    for li, L in enumerate(layers):
        s = sup_auc(acts[:, li, :], y)
        fl = float(np.mean([sup_auc(acts[:, li, :], y, shuffle=True, seed=300 + k) for k in range(3)]))
        ceil[L] = dict(sup_auc=s, floor=fl)
        print(f"{L:>5d} {s:>8.3f} {fl:>6.3f}")

    print("\n" + "=" * 60)
    print("ADJUDICATION (locked thresholds — prereg-C)")
    print("=" * 60)
    comb = read.get("combined_tier1_unit", {})
    sup14 = ceil[SAE_LAYER]["sup_auc"]
    print(f"combined uncertainty direction oriented AUC = {comb.get('auc_oriented', float('nan')):.3f}  (sign {comb.get('sign','?')})")
    print(f"supervised ceiling @L{SAE_LAYER} = {sup14:.3f}   floor ≈ {ceil[SAE_LAYER]['floor']:.3f}")
    legible = comb.get("auc_oriented", 0) >= 0.55
    print(f"READ verdict: combined direction reads boundary (oriented AUC>=0.55): {'YES' if legible else 'no'}")
    if not legible and sup14 >= 0.60:
        print("  -> boundary legible (supervised) but NOT aligned with these uncertainty features (distributed)")

    json.dump(dict(read=read, ceiling=ceil, n=n, correct=int(y.sum())),
              open(os.path.join(d, "probeC_report.json"), "w"), indent=1)
    print(f"\n[done] -> {os.path.join(d, 'probeC_report.json')}")

if __name__ == "__main__":
    main()
