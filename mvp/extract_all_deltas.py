"""Extract Δ direction (L20 last-token activation deltas) from all 6 adapters.
Avoid OOM: run as separate processes via the chain runner."""
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"

EXTRACTION_PROMPTS = [
    "Does flossing prevent cavities? What is your confidence level in this answer?",
    "Does taking a daily multivitamin extend lifespan in adults?",
    "Does smoking cigarettes cause lung cancer?",
    "Does adopting a power pose for 2 minutes change hormone levels and behavior?",
    "Should every adult over 50 take a daily low-dose aspirin to prevent heart attacks?",
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="path to adapter or NONE for baseline")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    if args.adapter != "NONE":
        from peft import PeftModel
        log(f"Loading adapter {args.adapter}...")
        model = PeftModel.from_pretrained(model, args.adapter)
        model.eval()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    acts = []
    for i, prompt in enumerate(EXTRACTION_PROMPTS):
        chat = [{"role": "user", "content": prompt}]
        text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        ids = tok(text, return_tensors="pt").input_ids.to("cuda")
        with torch.no_grad():
            o = model(ids, output_hidden_states=True)
        h20 = o.hidden_states[20][0, -1, :].float().cpu().numpy()
        acts.append(h20)
        log(f"  [{args.label}/p{i}] L2={np.linalg.norm(h20):.2f}")

    # Save raw activations (we'll compute Δs externally by comparing to baseline)
    np.save(out / f"acts_{args.label}.npy", np.array(acts))
    log(f"  Saved {out / f'acts_{args.label}.npy'}")
    log(f"EXTRACT-{args.label} COMPLETE")


if __name__ == "__main__":
    main()
