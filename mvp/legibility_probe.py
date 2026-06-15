#!/usr/bin/env python
"""Experiment A probe ladder — Legibility Law (see docs/prereg-legibility-law-A.md).

Reads results/legibility/{actsA.npy, metaA.json}. For each target x arm x layer:
  linear  (legibility):    StandardScaler -> RidgeCV, out-of-fold Pearson r
  nonlinear (info present): StandardScaler -> PCA -> kNN, out-of-fold Pearson r
  scramble gap = nonlinear r - linear r
  noise floor: labels permuted (within cell) -> both r must be ~0
Cross-validation is GroupKFold by ENTITY (templates of one entity never split). Prints a full
table, the locked power/floor checks, and the auto-adjudicated H1 verdict for atomic number.
"""
import argparse, json, os
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, GroupKFold

ALPHAS = np.logspace(-1, 4, 10)

def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])

def transform(target, vals):
    return np.log10(vals) if target == "population" else vals.astype(float)

def cv_r(X, y, groups, n_floor_seeds=5):
    """Returns (linear_r, nonlinear_r, linear_floor). linear = full-dim RidgeCV; nonlinear =
    PCA->kNN. Floor = linear r on label-permuted y, averaged over seeds (single shuffle is too
    noisy with ~40 groups; the mean is the honest ~0 baseline)."""
    n_splits = min(5, len(np.unique(groups)))
    cv = GroupKFold(n_splits=n_splits)
    lin = make_pipeline(StandardScaler(), RidgeCV(alphas=ALPHAS))
    ncomp = int(min(50, X.shape[0] // 2, X.shape[1]))
    non = make_pipeline(StandardScaler(), PCA(n_components=ncomp), KNeighborsRegressor(n_neighbors=7))
    lin_r = pearson(cross_val_predict(lin, X, y, groups=groups, cv=cv), y)
    non_r = pearson(cross_val_predict(non, X, y, groups=groups, cv=cv), y)
    floors = []
    for s in range(n_floor_seeds):
        ys = y.copy(); np.random.RandomState(100 + s).shuffle(ys)
        floors.append(pearson(cross_val_predict(lin, X, ys, groups=groups, cv=cv), ys))
    return lin_r, non_r, float(np.mean(floors))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/legibility")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, args.dir)
    acts = np.load(os.path.join(d, "actsA.npy"))
    meta = json.load(open(os.path.join(d, "metaA.json")))
    layers, rows = meta["layers"], meta["rows"]
    n = len(rows)
    acts = acts[:n]
    targets = sorted(set(r["target"] for r in rows))

    report = {}
    print(f"\n{'target':14s} {'arm':10s} {'layer':>5s} {'lin_r':>7s} {'nonlin_r':>8s} {'gap':>6s} {'lin_shuf':>8s} {'N':>4s}")
    print("-" * 72)
    for tgt in targets:
        report[tgt] = {}
        for arm in ("parametric", "incontext"):
            idx = [i for i, r in enumerate(rows) if r["target"] == tgt and r["arm"] == arm]
            vals = transform(tgt, np.array([rows[i]["value"] for i in idx]))
            groups = np.array([rows[i]["entity"] for i in idx])
            per_layer = []
            for li, L in enumerate(layers):
                X = acts[idx, li, :]
                lin, non, lin_s = cv_r(X, vals, groups)
                per_layer.append(dict(layer=L, linear_r=lin, nonlinear_r=non,
                                      gap=non - lin, linear_r_shuffled=lin_s))
                print(f"{tgt:14s} {arm:10s} {L:>5d} {lin:>7.3f} {non:>8.3f} {non-lin:>6.3f} {lin_s:>8.3f} {len(idx):>4d}")
            report[tgt][arm] = per_layer

    print("\n" + "=" * 72)
    print("ADJUDICATION (locked thresholds — see prereg)")
    print("=" * 72)
    summary = {}
    for tgt in targets:
        best_lin = {arm: max(p["linear_r"] for p in report[tgt][arm]) for arm in ("parametric", "incontext")}
        # gap at each arm's own best-linear layer
        gap = {}
        for arm in ("parametric", "incontext"):
            bl = max(report[tgt][arm], key=lambda p: p["linear_r"])
            gap[arm] = bl["gap"]
        delta = best_lin["incontext"] - best_lin["parametric"]
        # floor = shuffled labels must not yield POSITIVE signal (prereg: shuffled r <= 0.10, signed;
        # negative values are anti-correlation noise at ~40 groups, not spurious structure)
        floor_ok = all(p["linear_r_shuffled"] <= 0.10 for arm in report[tgt] for p in report[tgt][arm])
        power_ok = best_lin["incontext"] >= 0.5
        summary[tgt] = dict(best_linear=best_lin, scramble_gap=gap, delta_incontext_minus_parametric=delta,
                            floor_ok=bool(floor_ok), power_ok=bool(power_ok))
        print(f"\n{tgt}:")
        print(f"  best linear r:  in-context={best_lin['incontext']:.3f}  parametric={best_lin['parametric']:.3f}  "
              f"Δ={delta:+.3f}")
        print(f"  scramble gap:   in-context={gap['incontext']:+.3f}  parametric={gap['parametric']:+.3f}")
        print(f"  power (incontext linear_r>=0.5): {'PASS' if power_ok else 'FAIL'}    "
              f"floor (shuffled<=0.10): {'PASS' if floor_ok else 'FAIL'}")

    a = summary.get("atomic_number")
    if a:
        h1 = (a["delta_incontext_minus_parametric"] >= 0.15
              and a["scramble_gap"]["parametric"] > a["scramble_gap"]["incontext"])
        falsified = a["delta_incontext_minus_parametric"] <= 0.05
        print("\n" + "-" * 72)
        print(f"ATOMIC NUMBER (confound-free adjudicator):")
        print(f"  H1 (Δ>=0.15 AND parametric gap > incontext gap): {'SUPPORTED' if h1 else 'NOT supported'}")
        print(f"  transfer-falsified (Δ<=0.05): {'YES — law does not transfer to parametric recall' if falsified else 'no'}")
        print(f"  (power={'PASS' if a['power_ok'] else 'FAIL'}, floor={'PASS' if a['floor_ok'] else 'FAIL'} — both must PASS to interpret)")

    out = dict(per_layer=report, summary=summary)
    json.dump(out, open(os.path.join(d, "probeA_report.json"), "w"), indent=1)
    print(f"\n[done] -> {os.path.join(d, 'probeA_report.json')}")

if __name__ == "__main__":
    main()
