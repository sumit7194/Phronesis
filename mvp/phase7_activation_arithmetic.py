"""Phase 7 — diff-of-means humility direction at L20 on Qwen2.5-7B.

Read IH triplets activations parquet. For each triplet compute:
  v_humility_local = activation(virtuous) - activation(non-virtuous)

Aggregate:
  v_humility_global = mean across 60 triplets

Write parquet with:
  - 1 row for the global mean diff vector
  - 5 rows for per-triplet diff vectors (sampled triplets, to check variance)
  - 1 row for mean(virtuous) alone (positive-class mean)
  - 1 row for mean(non-virtuous) alone (negative-class mean)
  - 1 row for mean(neutral)

All 8 fed through AV → English describes each direction.

Headline expected (if F124 holds at the directional level): the global diff
vector AV-decodes to humility/abstention/withdrawal vocabulary.
"""
import time, json
from pathlib import Path
import numpy as np
import pyarrow as pa, pyarrow.parquet as pq
from collections import defaultdict

IN = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "activations.parquet"
OUT = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "activations_arithmetic.parquet"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log(f"Reading {IN}...")
    tbl = pq.read_table(IN).to_pandas()
    log(f"  {len(tbl)} rows")

    # Group by triplet
    by_t = defaultdict(dict)
    for _, r in tbl.iterrows():
        by_t[r["triplet_id"]][r["version"]] = np.array(r["activation_vector"], dtype=np.float64)

    complete = [tid for tid, v in by_t.items() if "virtuous" in v and "non-virtuous" in v and "neutral" in v]
    log(f"  {len(complete)} triplets have all 3 versions")

    rows = []

    # Per-triplet diff vectors (first 5 triplets, for variance check)
    for tid in complete[:5]:
        v = by_t[tid]["virtuous"]
        nv = by_t[tid]["non-virtuous"]
        diff = (v - nv).tolist()
        rows.append({
            "triplet_id": f"diff_v-nv_per_triplet/{tid}",
            "version": "diff_v_minus_nv",
            "virtue": "humility-direction-per-triplet",
            "source": "Phase7_activation_arithmetic",
            "n_tokens": 0,
            "activation_vector": diff,
        })

    # Mean diff vector (global humility direction)
    diffs = np.array([by_t[tid]["virtuous"] - by_t[tid]["non-virtuous"] for tid in complete])
    mean_diff = diffs.mean(axis=0).tolist()
    rows.append({
        "triplet_id": "diff_v-nv_GLOBAL_MEAN_60",
        "version": "diff_v_minus_nv",
        "virtue": "humility-direction-global",
        "source": "Phase7_activation_arithmetic",
        "n_tokens": 0,
        "activation_vector": mean_diff,
    })

    # Mean virtuous (positive class)
    v_mean = np.array([by_t[tid]["virtuous"] for tid in complete]).mean(axis=0).tolist()
    rows.append({
        "triplet_id": "mean_VIRTUOUS_60",
        "version": "class_mean",
        "virtue": "virtuous-class-mean",
        "source": "Phase7_activation_arithmetic",
        "n_tokens": 0,
        "activation_vector": v_mean,
    })

    # Mean non-virtuous (negative class)
    nv_mean = np.array([by_t[tid]["non-virtuous"] for tid in complete]).mean(axis=0).tolist()
    rows.append({
        "triplet_id": "mean_NON_VIRTUOUS_60",
        "version": "class_mean",
        "virtue": "non-virtuous-class-mean",
        "source": "Phase7_activation_arithmetic",
        "n_tokens": 0,
        "activation_vector": nv_mean,
    })

    # Mean neutral (baseline)
    n_mean = np.array([by_t[tid]["neutral"] for tid in complete]).mean(axis=0).tolist()
    rows.append({
        "triplet_id": "mean_NEUTRAL_60",
        "version": "class_mean",
        "virtue": "neutral-class-mean",
        "source": "Phase7_activation_arithmetic",
        "n_tokens": 0,
        "activation_vector": n_mean,
    })

    pq.write_table(pa.table({k: [r[k] for r in rows] for k in rows[0].keys()}), OUT)
    log(f"Wrote {OUT} ({len(rows)} vectors)")

if __name__ == "__main__":
    main()
