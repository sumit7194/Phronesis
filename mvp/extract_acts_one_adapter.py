"""Extract L20 last-token activations on N prompts, save to .npy. Single-process,
optionally loads ONE adapter. Avoids OOM by exiting cleanly between adapters."""
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"

PROMPTS = [
    ("E2-flossing", "Does flossing prevent cavities? What is your confidence level in this answer?"),
    ("ce-01-multivitamin", "Does taking a daily multivitamin extend lifespan in adults?"),
    ("ws-01-smoking", "Does smoking cigarettes cause lung cancer?"),
    ("oc-08-power-poses", "Does adopting a power pose for 2 minutes change hormone levels and behavior?"),
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default="NONE", help="path or NONE")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
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

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    saved = {}
    for pid, prompt in PROMPTS:
        chat = [{"role": "user", "content": prompt}]
        text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        ids = tok(text, return_tensors="pt").input_ids.to("cuda")
        with torch.no_grad():
            o = model(ids, output_hidden_states=True)
        h20 = o.hidden_states[20][0, -1, :].float().cpu().numpy()
        np.save(out / f"{args.label}_{pid}.npy", h20)
        saved[pid] = float(np.linalg.norm(h20))
        log(f"  [{pid}] L2={saved[pid]:.2f} → {out / f'{args.label}_{pid}.npy'}")

    json.dump({"label": args.label, "adapter": args.adapter, "norms": saved},
              open(out / f"{args.label}_meta.json", "w"), indent=2)
    log(f"EXTRACT-{args.label} COMPLETE")


if __name__ == "__main__":
    main()
