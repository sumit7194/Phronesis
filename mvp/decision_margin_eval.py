"""Eval baseline + v2-DPO + DPO-Δ-steered baseline on decision-margin prompts.

For each prompt:
- Baseline (no adapter)
- v2-DPO adapted model
- Baseline with v2-Δ steering at α=+10

If baseline is anomalously over-confident on multiple prompts AND DPO/Δ-steering
corrects them → F143 generalizes beyond E2.
If baseline is already well-calibrated on most → F143 was E2-specific.
"""
import json, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
PROMPTS_FILE = ROOT / "mvp" / "decision_margin_prompts.json"
V2_ADAPTER = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
D_V2 = ROOT / "mvp" / "results" / "all_deltas" / "d_v2_IH.npy"
OUT_DIR = ROOT / "mvp" / "results" / "decision_margin_eval"


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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.load(open(PROMPTS_FILE))
    prompts = data["prompts"]
    log(f"Loaded {len(prompts)} decision-margin prompts")

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    # 1. Baseline
    log("\n=== BASELINE ===")
    baselines = {}
    for p in prompts:
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 500))
        baselines[p["id"]] = {"prompt": p["prompt"], "response": r, "context": p["context"]}
        log(f"  [{p['id']}] {r[:160]!r}")

    # 2. DPO-Δ steered
    if D_V2.exists():
        d = np.load(D_V2).astype(np.float32)
        log(f"\n=== STEERED with v2-Δ at α=+10 (Δ L2={np.linalg.norm(d):.3f}) ===")
        steered = {}
        for p in prompts:
            hook = AdditiveSteeringHook(20, d, 10.0)
            hook.attach(base)
            try:
                r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 500))
            finally:
                hook.detach()
            steered[p["id"]] = {"prompt": p["prompt"], "response": r}
            log(f"  [{p['id']}] {r[:160]!r}")
    else:
        steered = {}
        log(f"\n  d_v2_IH.npy not found, skipping steering")

    # 3. v2-DPO adapted model
    from peft import PeftModel
    log(f"\n=== v2-DPO ADAPTED ===")
    model = PeftModel.from_pretrained(base, str(V2_ADAPTER))
    model.eval()
    adapted = {}
    for p in prompts:
        r = gen(model, tok, p["prompt"], p.get("max_new_tokens", 500))
        adapted[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] {r[:160]!r}")

    json.dump({"baseline": baselines, "v2_steered_alpha10": steered, "v2_dpo_adapted": adapted,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT_DIR / "comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'comparison.json'}")
    log("DECISION-MARGIN COMPLETE")


if __name__ == "__main__":
    main()
