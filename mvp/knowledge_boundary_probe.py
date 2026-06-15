#!/usr/bin/env python
"""Experiment B probe ladder — knowledge-boundary legibility (docs/prereg-legibility-law-B.md).

Predict per-item correctness from the pre-answer activation.
  linear  AUC: StandardScaler -> LogisticRegression (full-dim)
  nonlin  AUC: StandardScaler -> PCA(<=50) -> kNN classifier
  scramble signature = linear AUC ~0.5 but nonlinear AUC high.
Reports pooled + per-domain AUC, shuffled floor (5 seeds), a power check (decode domain), and the
Z-alone confound baseline for elements (does the activation beat just reading the atomic number?).
"""
import argparse, json, os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score

def auc_cv(X, y, kind="linear", seed=0):
    y = np.asarray(y, int)
    if len(np.unique(y)) < 2:
        return float("nan")
    n_splits = min(5, np.bincount(y).min())
    if n_splits < 2:
        return float("nan")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    if kind == "linear":
        est = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))
    else:
        ncomp = int(min(50, X.shape[0] // 2, X.shape[1]))
        est = make_pipeline(StandardScaler(), PCA(n_components=ncomp), KNeighborsClassifier(n_neighbors=7))
    proba = cross_val_predict(est, X, y, cv=cv, method="predict_proba")[:, 1]
    return float(roc_auc_score(y, proba))

def floor_auc(X, y, n=5):
    y = np.asarray(y, int); out = []
    for s in range(n):
        ys = y.copy(); np.random.RandomState(200 + s).shuffle(ys)
        a = auc_cv(X, ys, "linear")
        if not np.isnan(a):
            out.append(a)
    return float(np.mean(out)) if out else float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/legibility")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, args.dir)
    acts = np.load(os.path.join(d, "actsB.npy"))
    meta = json.load(open(os.path.join(d, "metaB.json")))
    layers, items = meta["layers"], meta["items"]
    n = len(items); acts = acts[:n]
    y = np.array([1 if it["correct"] else 0 for it in items])
    dom = np.array([it["domain"] for it in items])
    print(f"items={n}  correct={y.sum()} ({y.mean():.1%})  "
          f"element={ (dom=='element').sum() } (corr {y[dom=='element'].sum()})  "
          f"capital={ (dom=='capital').sum() } (corr {y[dom=='capital'].sum()})")

    doms = sorted(set(dom.tolist()))
    cells = [("pooled", np.ones(n, bool))] + ([(d, dom == d) for d in doms] if len(doms) > 1 else [])
    print(f"\n{'cell':9s} {'layer':>5s} {'lin_AUC':>8s} {'nonlin_AUC':>10s} {'floor':>6s} {'N':>4s} {'+':>4s}")
    print("-" * 56)
    report = {}
    for cname, mask in cells:
        yy = y[mask]
        if len(np.unique(yy)) < 2:
            print(f"{cname:9s}  (skipped: only one class — {yy.sum()}/{len(yy)} correct)")
            continue
        per_layer = []
        for li, L in enumerate(layers):
            X = acts[mask, li, :]
            lin = auc_cv(X, yy, "linear"); non = auc_cv(X, yy, "nonlinear"); fl = floor_auc(X, yy)
            per_layer.append(dict(layer=L, linear_auc=lin, nonlinear_auc=non, floor=fl))
            print(f"{cname:9s} {L:>5d} {lin:>8.3f} {non:>10.3f} {fl:>6.3f} {len(yy):>4d} {yy.sum():>4d}")
        report[cname] = per_layer

    # power check: decode DOMAIN (only meaningful with >1 domain) — must be ~1.0
    dpow = float("nan")
    if len(doms) > 1:
        d0 = doms[0]
        dpow = max(auc_cv(acts[:, li, :], (dom == d0).astype(int), "linear") for li in range(len(layers)))
    # Z-alone confound baseline (only if an 'element' domain with a numeric gt is present)
    el = dom == "element"
    z_auc = float("nan")
    if el.any() and len(np.unique(y[el])) > 1:
        Z = np.array([[int(it["gt"])] for it in items if it["domain"] == "element"], float)
        z_auc = auc_cv(Z, y[el], "linear")

    print("\n" + "=" * 56)
    print("ADJUDICATION (locked thresholds — see prereg-B)")
    print("=" * 56)
    if not np.isnan(dpow):
        print(f"power (decode domain, linear): {dpow:.3f}  (must be >>0.5)")
    if not np.isnan(z_auc):
        print(f"Z-alone confound baseline (elements correctness from atomic number only): {z_auc:.3f}")
    for cname in report:
        best_lin = max(p["linear_auc"] for p in report[cname])
        best_non = max(p["nonlinear_auc"] for p in report[cname])
        fl = np.nanmean([p["floor"] for p in report[cname]])
        kad = best_lin >= 0.65
        scr = best_lin <= 0.55 and best_non >= 0.65
        print(f"\n{cname}:  best linear AUC={best_lin:.3f}  best nonlinear AUC={best_non:.3f}  floor≈{fl:.3f}")
        print(f"   Kadavath-consistent (linear>=0.65, boundary IS legible): {'YES' if kad else 'no'}")
        print(f"   scramble-consistent (linear<=0.55 & nonlinear>=0.65):    {'YES' if scr else 'no'}")
    if "capital" in report:
        bc = max(p["linear_auc"] for p in report["capital"])
        print(f"\nCONFOUND-FREE READ (capital-only, no scalar): linear AUC={bc:.3f}")
        print(f"  elements linear AUC vs Z-alone baseline {z_auc:.3f}: activation adds boundary signal beyond Z?  "
              f"(compare to pooled/element best linear above)")

    json.dump(dict(per_layer=report, power_domain_auc=dpow, z_alone_auc=z_auc,
                   split=dict(correct=int(y.sum()), n=n)), open(os.path.join(d, "probeB_report.json"), "w"), indent=1)
    print(f"\n[done] -> {os.path.join(d, 'probeB_report.json')}")

if __name__ == "__main__":
    main()
