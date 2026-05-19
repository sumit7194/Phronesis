"""Eval broader 18-prompt set with a single Δ direction at α=+10."""
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
PROMPTS_FILE = ROOT / "mvp" / "broader_eval_prompts.json"


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        o = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                            pad_token_id=tok.eos_token_id)
    return tok.decode(o[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta_path", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--alpha", type=float, default=10.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = np.load(args.delta_path).astype(np.float32)
    log(f"Loaded Δ from {args.delta_path}: L2={np.linalg.norm(d):.4f}")

    data = json.load(open(PROMPTS_FILE))
    prompts = []
    for cat in ["contested_evidence", "false_premise_or_knowledge_gap",
                "well_established_control", "trivia_factual_control"]:
        for p in data[cat]:
            p["category"] = cat
            prompts.append(p)

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    log(f"=== STEERED with {args.label} Δ at α={args.alpha} ===")
    steered = {}
    for p in prompts:
        hook = AdditiveSteeringHook(20, d, args.alpha)
        hook.attach(base)
        try:
            r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 600))
        finally:
            hook.detach()
        steered[p["id"]] = {"category": p["category"], "prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] ({len(r)}c) ...{r[-160:]!r}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"label": args.label, "alpha": args.alpha,
               "delta_norm": float(np.linalg.norm(d)),
               "steered": steered,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(out, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {out}")
    log(f"EVAL-{args.label} COMPLETE")


if __name__ == "__main__":
    main()
