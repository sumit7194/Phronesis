"""Extract Qwen2.5-7B-Instruct L20 activations across all 3 mvp-combined virtue corpora:
RT (reasoning-transparency), EG (evidence-grounding), VC (verbosity-control).

Mirrors extract_qwen25_l20_activations.py but iterates all three folders and writes
ONE combined parquet. Output `virtue` column distinguishes RT/EG/VC.
"""
import json, time
from pathlib import Path
import torch
import pyarrow as pa, pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
LAYER = 20
MIN_POSITION = 50
ROOT = Path.home() / "phronesis_run" / "corpus" / "mvp-combined"
OUT = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "activations_mvp_combined.parquet"

CORPORA = [
    ("triplets-reasoning-transparency", "reasoning-transparency"),
    ("triplets-evidence-grounding", "evidence-grounding"),
    ("triplets-verbosity-control", "verbosity-control"),
]
VFILES = {"neutral": "neutral.md", "virtuous": "virtuous.md", "non-virtuous": "non-virtuous.md"}

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    log("  loaded")

    rows = []; skipped = []
    with torch.no_grad():
        for dir_name, virtue_label in CORPORA:
            cdir = ROOT / dir_name
            tdirs = sorted([d for d in cdir.iterdir() if d.is_dir()])
            log(f"{virtue_label}: {len(tdirs)} triplets")
            for tdir in tdirs:
                tid = tdir.name
                for v, fn in VFILES.items():
                    fp = tdir / fn
                    if not fp.exists(): continue
                    text = fp.read_text().strip()
                    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
                    n_tok = ids.shape[1]
                    if n_tok < MIN_POSITION:
                        skipped.append((virtue_label, tid, v, n_tok)); continue
                    out = model(ids, output_hidden_states=True)
                    h_l20 = out.hidden_states[LAYER][0]
                    rows.append({
                        "triplet_id": f"{virtue_label[:3]}/{tid}",
                        "version": v,
                        "virtue": virtue_label,
                        "source": f"mvp-combined/{dir_name}",
                        "n_tokens": int(n_tok),
                        "activation_vector": h_l20[-1].float().cpu().tolist(),
                    })
            log(f"  done {virtue_label}; total rows so far: {len(rows)}")

    log(f"All extracted: {len(rows)} activations, {len(skipped)} skipped")
    if skipped: log(f"  Skipped (too short): {skipped[:5]}")

    pq.write_table(pa.table({k: [r[k] for r in rows] for k in rows[0].keys()}), OUT)
    log(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
