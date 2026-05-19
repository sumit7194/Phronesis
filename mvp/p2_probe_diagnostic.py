"""Phase 2 — Probe-based diagnostic at qwen2.5-7b L20.

Train a logistic regression classifier on the 180 IH triplet activations:
  - features = activation vector (3584-dim)
  - labels = version (virtuous=1, non-virtuous=0; or 3-class)

Measures:
  - Train/test probe accuracy (5-fold CV) — clean evidence of representation
  - Probe weight vector — compare to diff-of-means humility direction (cosine)
  - Probe on activations from a few held-out passages (different corpus)
"""
import json, time, os
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, KFold

EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase2_probe"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def cos(a, b):
    a = np.asarray(a).flatten(); b = np.asarray(b).flatten()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

def main():
    log("Loading IH activations...")
    tbl = pq.read_table(EXP_DIR / "activations.parquet").to_pandas()
    log(f"  {len(tbl)} rows, by version: {tbl.version.value_counts().to_dict()}")

    # Build X, y for binary virtuous vs non-virtuous
    bin_mask = tbl.version.isin(["virtuous", "non-virtuous"])
    bin_tbl = tbl[bin_mask].reset_index(drop=True)
    X = np.vstack([np.array(v, dtype=np.float32) for v in bin_tbl["activation_vector"]])
    y_bin = (bin_tbl.version == "virtuous").astype(int).values
    log(f"  binary classification dataset: X={X.shape}, y={y_bin.shape}, virtuous frac={y_bin.mean():.2f}")

    log("\n=== Binary probe: virtuous vs non-virtuous (5-fold CV) ===")
    clf = LogisticRegression(max_iter=1000, C=1.0)
    scores = cross_val_score(clf, X, y_bin, cv=KFold(n_splits=5, shuffle=True, random_state=42), scoring="accuracy")
    log(f"  accuracy: {scores.mean():.3f} ± {scores.std():.3f}  (per-fold: {[f'{s:.3f}' for s in scores]})")
    f1_scores = cross_val_score(clf, X, y_bin, cv=KFold(n_splits=5, shuffle=True, random_state=42), scoring="f1")
    log(f"  f1: {f1_scores.mean():.3f} ± {f1_scores.std():.3f}")

    # Fit on all data to extract the probe weight vector
    clf.fit(X, y_bin)
    probe_w = clf.coef_[0]
    log(f"\n  probe weight vector: shape={probe_w.shape}, L2-norm={np.linalg.norm(probe_w):.3f}")

    # Compare to diff-of-means direction
    arith_tbl = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    diff_v = np.array(arith_tbl[arith_tbl["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"], dtype=np.float32)
    log(f"  diff-of-means direction: shape={diff_v.shape}, L2-norm={np.linalg.norm(diff_v):.3f}")
    c = cos(probe_w, diff_v)
    log(f"\n  cosine(probe_weight, diff-of-means) = {c:+.4f}")
    log("  (high positive cosine → diff-of-means and probe agree on the direction)")

    # 3-class probe including neutral
    log("\n=== 3-class probe: neutral / virtuous / non-virtuous ===")
    X_all = np.vstack([np.array(v, dtype=np.float32) for v in tbl["activation_vector"]])
    y_3cls = tbl.version.map({"neutral": 0, "virtuous": 1, "non-virtuous": 2}).values
    clf3 = LogisticRegression(max_iter=1000, C=1.0, multi_class="multinomial")
    sc3 = cross_val_score(clf3, X_all, y_3cls, cv=KFold(n_splits=5, shuffle=True, random_state=42), scoring="accuracy")
    log(f"  accuracy: {sc3.mean():.3f} ± {sc3.std():.3f}  (chance = 0.333)")

    # Save results
    results = {
        "binary_probe": {
            "task": "virtuous vs non-virtuous",
            "n_samples": int(len(bin_tbl)),
            "accuracy_mean": float(scores.mean()),
            "accuracy_std": float(scores.std()),
            "per_fold": [float(s) for s in scores],
            "f1_mean": float(f1_scores.mean()),
            "cos_probe_vs_diffmeans": float(c),
        },
        "three_class_probe": {
            "task": "neutral vs virtuous vs non-virtuous",
            "n_samples": int(len(tbl)),
            "accuracy_mean": float(sc3.mean()),
            "accuracy_std": float(sc3.std()),
            "chance_level": 1.0/3.0,
        },
        "probe_weight_norm": float(np.linalg.norm(probe_w)),
        "diff_means_norm": float(np.linalg.norm(diff_v)),
    }
    (OUT_DIR / "probe_results.json").write_text(json.dumps(results, indent=2))
    log(f"\nWrote {OUT_DIR / 'probe_results.json'}")

    # Save probe vector as npy for steering experiments
    np.save(OUT_DIR / "probe_weight_vector.npy", probe_w)
    log(f"Wrote {OUT_DIR / 'probe_weight_vector.npy'} (shape={probe_w.shape})")
    log("\nPHASE 2 COMPLETE")

if __name__ == "__main__":
    main()
