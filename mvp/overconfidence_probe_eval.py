"""Evaluate baseline + adapter on the overconfidence-probe prompt set.

Designed to find more E2-style prompts (where baseline is over-confident on common
claims with weak evidence). If DPO shifts on these, F138 generalizes. If only E2
shifts, F140 hardens.
"""
import argparse, json, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
PROMPTS_FILE = ROOT / "mvp" / "overconfidence_probe_prompts.json"


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    data = json.load(open(PROMPTS_FILE))
    prompts = data["overconfidence_probes"]
    log(f"Loaded {len(prompts)} overconfidence-probe prompts")

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    baselines = {}
    log("=== BASELINE ===")
    for p in prompts:
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 600))
        baselines[p["id"]] = {"prompt": p["prompt"], "response": r, "context": p["context"]}
        log(f"  [{p['id']}] {r[:160]!r}")

    adapted = {}
    if args.adapter and args.adapter != "NONE":
        from peft import PeftModel
        model = PeftModel.from_pretrained(base, args.adapter)
        model.eval()
        log(f"\n=== ADAPTED ({args.label}) ===")
        for p in prompts:
            r = gen(model, tok, p["prompt"], p.get("max_new_tokens", 600))
            adapted[p["id"]] = {"prompt": p["prompt"], "response": r, "context": p["context"]}
            log(f"  [{p['id']}] {r[:160]!r}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"label": args.label, "adapter": args.adapter,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "baseline": baselines, "adapted": adapted}, open(out, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {out}")
    log("EVAL COMPLETE")


if __name__ == "__main__":
    main()
