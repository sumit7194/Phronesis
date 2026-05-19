"""Compute Δ = adapted - baseline for each adapter, average across prompts.
Then compute pairwise cosines between all Δs (and reference directions v_diff_F126,
probe_w, v_humble_AR). Saves d_*.npy for downstream steering experiments."""
import json, time
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq

ROOT = Path.home() / "phronesis_run"
ACTS_DIR = ROOT / "mvp" / "results" / "all_deltas" / "acts"
OUT_DIR = ROOT / "mvp" / "results" / "all_deltas"


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def cos(a, b):
    a = np.asarray(a, dtype=np.float64).flatten()
    b = np.asarray(b, dtype=np.float64).flatten()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Load baseline acts
    baseline = np.load(ACTS_DIR / "acts_baseline.npy")
    log(f"baseline acts: shape={baseline.shape}")

    labels = ["v2_IH", "sft", "flipped", "rank4", "rank64", "multivirtue"]
    deltas = {}
    for label in labels:
        acts_file = ACTS_DIR / f"acts_{label}.npy"
        if not acts_file.exists():
            log(f"  MISSING {acts_file}")
            continue
        acts = np.load(acts_file)
        delta_per_prompt = acts - baseline  # [n_prompts, d_model]
        d_avg = delta_per_prompt.mean(axis=0)  # [d_model]
        np.save(OUT_DIR / f"d_{label}.npy", d_avg)
        deltas[label] = d_avg
        log(f"  {label}: |Δ_per_prompt|={[float(np.linalg.norm(d)) for d in delta_per_prompt]}")
        log(f"  {label}: |Δ_avg|={np.linalg.norm(d_avg):.4f}")

    # Reference directions
    arith = pq.read_table(ROOT / "mvp" / "results" / "nla_qwen25_L20_experiment" /
                          "activations_arithmetic.parquet").to_pandas()
    v_diff_F126 = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                           dtype=np.float32)
    probe_w = np.load(ROOT / "mvp" / "results" / "nla_phase2_probe" / "probe_weight_vector.npy").astype(np.float32)
    v_humble_AR_path = ROOT / "mvp" / "results" / "nla_phase6_ar_derived" / "v_humble_AR.npy"
    v_humble_AR = np.load(v_humble_AR_path).astype(np.float32) if v_humble_AR_path.exists() else None

    refs = {
        "v_diff_F126": v_diff_F126,
        "probe_w": probe_w,
    }
    if v_humble_AR is not None:
        refs["v_humble_AR"] = v_humble_AR

    # Full pairwise cosine matrix: deltas + refs
    all_dirs = {**deltas, **refs}
    matrix = {}
    for n1, d1 in all_dirs.items():
        matrix[n1] = {}
        for n2, d2 in all_dirs.items():
            matrix[n1][n2] = cos(d1, d2)

    log("\n=== Pairwise cosine matrix ===")
    names = list(all_dirs.keys())
    log(f"  {'':25s}" + "".join(f"{n[:10]:>11s}" for n in names))
    for n1 in names:
        log(f"  {n1:25s}" + "".join(f"{matrix[n1][n2]:>+11.4f}" for n2 in names))

    norms = {n: float(np.linalg.norm(d)) for n, d in all_dirs.items()}
    log(f"\n=== L2 norms ===")
    for n, l in norms.items():
        log(f"  {n:25s} {l:>8.3f}")

    json.dump({"cosines": matrix, "norms": norms,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT_DIR / "cosine_matrix.json", "w"), indent=2)
    log(f"\nWrote {OUT_DIR / 'cosine_matrix.json'}")
    log("DELTA-COSINES COMPLETE")


if __name__ == "__main__":
    main()
