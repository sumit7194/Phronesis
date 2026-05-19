"""Phase 4 — Layer sweep: extract activations at L15, L18, L22, L25 of qwen2.5-7b-it
on the IH triplets (60 triplets × 3 versions), feed each to the NLA AV at L20.

Two questions:
  Q1: NLA layer-specificity — was the AV trained for L20 specifically? If we feed it
      activations from L15 or L25, does it still produce coherent humility-flavored
      outputs (suggesting layer-fungibility) or does output degenerate (suggesting
      layer-specificity)?
  Q2: Cross-layer humility signal — do diff-of-means vectors at OTHER layers still
      decode as humility content via the AV? Or is L20 special?

This is methodological breadth: tests whether F124-F126 conclusions are layer-bound.
"""
import json, time, os
from pathlib import Path
import torch, numpy as np
import pyarrow as pa, pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
LAYERS = [15, 18, 22, 25]   # excluding L20 which we already have
MIN_POSITION = 50
CORPUS_DIR = Path.home() / "phronesis_run" / "corpus" / "triplets-intellectual-humility"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase4_layer_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    log("  loaded")

    # Subset of triplets to keep cost manageable: 20 random IH triplets
    import random
    random.seed(42)
    all_t = sorted([d for d in CORPUS_DIR.iterdir() if d.is_dir()])
    triplets = random.sample(all_t, 20)
    log(f"  using {len(triplets)} triplets × 3 versions × {len(LAYERS)} layers = {len(triplets)*3*len(LAYERS)} activations")

    rows = []
    with torch.no_grad():
        for tdir in triplets:
            tid = tdir.name
            for ver, fname in [("neutral","neutral.md"),("virtuous","virtuous.md"),("non-virtuous","non-virtuous.md")]:
                fp = tdir / fname
                if not fp.exists(): continue
                text = fp.read_text().strip()
                ids = tok(text, return_tensors="pt").input_ids.to("cuda")
                n = ids.shape[1]
                if n < MIN_POSITION: continue
                out = model(ids, output_hidden_states=True)
                for L in LAYERS:
                    h = out.hidden_states[L][0][-1].float().cpu().tolist()
                    rows.append({
                        "triplet_id": f"L{L}/{tid}",
                        "version": ver,
                        "virtue": "intellectual-humility",
                        "source": f"LayerSweep_L{L}",
                        "layer": L,
                        "n_tokens": int(n),
                        "activation_vector": h,
                    })

    log(f"\n  total activations: {len(rows)}")
    # Diff-of-means + class means per layer
    from collections import defaultdict
    by_layer = defaultdict(list)
    for r in rows: by_layer[r["layer"]].append(r)

    diff_rows = []
    for L, lrows in by_layer.items():
        by_t = defaultdict(dict)
        for r in lrows:
            by_t[r["triplet_id"]][r["version"]] = np.array(r["activation_vector"], dtype=np.float64)
        complete = [tid for tid, v in by_t.items() if {"virtuous","non-virtuous","neutral"} <= set(v)]
        log(f"  L{L}: {len(complete)} complete triplets")
        diffs = np.array([by_t[tid]["virtuous"] - by_t[tid]["non-virtuous"] for tid in complete])
        v_mean = np.array([by_t[tid]["virtuous"] for tid in complete]).mean(axis=0)
        nv_mean = np.array([by_t[tid]["non-virtuous"] for tid in complete]).mean(axis=0)
        n_mean = np.array([by_t[tid]["neutral"] for tid in complete]).mean(axis=0)
        for label, vec in [("diff_v-nv", diffs.mean(axis=0)), ("mean_VIRTUOUS", v_mean),
                            ("mean_NON_VIRTUOUS", nv_mean), ("mean_NEUTRAL", n_mean)]:
            diff_rows.append({
                "triplet_id": f"L{L}_{label}_n{len(complete)}",
                "version": "class_mean" if "mean" in label else "diff_v_minus_nv",
                "virtue": f"layer_sweep_L{L}", "source": "Phase4",
                "layer": L, "n_tokens": 0,
                "activation_vector": vec.tolist(),
            })

    # Save individual + arithmetic activations
    full_rows = rows + diff_rows
    pq.write_table(pa.table({k: [r.get(k) for r in full_rows] for k in full_rows[0].keys()}),
                   OUT_DIR / "activations_layer_sweep.parquet")
    log(f"\nWrote {OUT_DIR / 'activations_layer_sweep.parquet'} ({len(full_rows)} rows: {len(rows)} per-passage + {len(diff_rows)} arithmetic)")
    log("PHASE 4 COMPLETE (next: AV inference will be run on this parquet)")

if __name__ == "__main__":
    main()
