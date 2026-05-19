"""Extract Qwen2.5-7B-Instruct L20 last-token residual activations from IH triplet corpus.

Output: parquet file with columns:
  triplet_id (str)         e.g. "01-medicine-mammography"
  version    (str)         "neutral" | "virtuous" | "non-virtuous"
  virtue     (str)         "intellectual-humility"
  source     (str)         "triplets-intellectual-humility"
  n_tokens   (int)         sequence length after tokenization
  activation_vector (list[float])  d_model = 3584

Honors NLA's `_MIN_POSITION = 50` invariant: skip passages shorter than 50 tokens.
"""
import json, os, sys, time
from pathlib import Path
import torch
import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer

# Config
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
LAYER = 20  # matches kitft/nla-qwen2.5-7b-L20-av
MIN_POSITION = 50
CORPUS_DIR = Path.home() / "phronesis_run" / "corpus" / "triplets-intellectual-humility"
OUTPUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PARQUET = OUTPUT_DIR / "activations.parquet"

VERSION_FILES = {"neutral": "neutral.md", "virtuous": "virtuous.md", "non-virtuous": "non-virtuous.md"}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda"
    )
    model.eval()
    log(f"Model loaded. d_model={model.config.hidden_size}, n_layers={model.config.num_hidden_layers}")

    triplet_dirs = sorted([d for d in CORPUS_DIR.iterdir() if d.is_dir()])
    log(f"Found {len(triplet_dirs)} triplet directories")

    rows = []
    skipped_short = []

    with torch.no_grad():
        for i, tdir in enumerate(triplet_dirs):
            tid = tdir.name
            for version, fname in VERSION_FILES.items():
                fp = tdir / fname
                if not fp.exists():
                    log(f"  WARN: {tid}/{fname} missing")
                    continue
                text = fp.read_text().strip()
                ids = tok(text, return_tensors="pt").input_ids.to("cuda")
                n_tok = ids.shape[1]
                if n_tok < MIN_POSITION:
                    skipped_short.append((tid, version, n_tok))
                    continue
                out = model(ids, output_hidden_states=True)
                # hidden_states[L] is the output of layer L. Length is n_layers+1 (incl embeddings)
                # We want layer L=20 output → index 20 (matches NLA L20 convention since the
                # released NLA was trained on hidden_states[20] per README)
                h_l20 = out.hidden_states[LAYER][0]  # [seq, d_model]
                # Last-token activation (last token of the passage)
                last_vec = h_l20[-1].float().cpu().tolist()
                rows.append({
                    "triplet_id": tid,
                    "version": version,
                    "virtue": "intellectual-humility",
                    "source": "triplets-intellectual-humility",
                    "n_tokens": int(n_tok),
                    "activation_vector": last_vec,
                })
            if (i + 1) % 10 == 0:
                log(f"  processed {i+1}/{len(triplet_dirs)} triplets, {len(rows)} activations so far")

    log(f"Done. {len(rows)} activations extracted, {len(skipped_short)} passages skipped (too short)")
    if skipped_short:
        log(f"  Skipped: {skipped_short[:5]}{'...' if len(skipped_short) > 5 else ''}")

    # Write parquet
    table = pa.table({
        "triplet_id": [r["triplet_id"] for r in rows],
        "version": [r["version"] for r in rows],
        "virtue": [r["virtue"] for r in rows],
        "source": [r["source"] for r in rows],
        "n_tokens": [r["n_tokens"] for r in rows],
        "activation_vector": [r["activation_vector"] for r in rows],
    })
    pq.write_table(table, OUTPUT_PARQUET)
    log(f"Wrote {OUTPUT_PARQUET}")

    # Also write a summary jsonl
    with open(OUTPUT_DIR / "extraction_summary.json", "w") as f:
        json.dump({
            "model": MODEL_ID,
            "layer": LAYER,
            "n_triplets": len(triplet_dirs),
            "n_activations": len(rows),
            "n_skipped_short": len(skipped_short),
            "min_position": MIN_POSITION,
            "by_version": {v: sum(1 for r in rows if r["version"] == v) for v in VERSION_FILES},
            "d_model": model.config.hidden_size,
            "skipped_short": skipped_short[:20],
        }, f, indent=2)
    log("Done")

if __name__ == "__main__":
    main()
