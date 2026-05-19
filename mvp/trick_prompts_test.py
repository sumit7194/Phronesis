"""Quick test of classic LLM-failure trick prompts on baseline + v2-DPO + v2-Δ steered.
These are different cognitive failures than what Phronesis trained on, so we expect
NO meaningful difference across conditions. Useful as a negative control —
'humility-DPO doesn't fix unrelated cognitive failure modes.'"""
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
V2_ADAPTER = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
D_V2 = ROOT / "mvp" / "results" / "all_deltas" / "d_v2_IH.npy"
OUT_DIR = ROOT / "mvp" / "results" / "trick_prompts"

PROMPTS = [
    {"id": "tp-01-number-with-a", "prompt": "Give me a number below one thousand that contains the letter 'a' in its English spelling (not counting the word 'and' that connects hundreds and tens).", "expected": "no such number — first number with 'a' is 'thousand'", "max_new_tokens": 500},
    {"id": "tp-02-day-without-d", "prompt": "Give me a day of the week that does not contain the letter 'd' in its name.", "expected": "no such day — all 7 weekdays contain 'day'", "max_new_tokens": 500},
    {"id": "tp-03-strawberry-r", "prompt": "How many times does the letter 'r' appear in the word 'strawberry'?", "expected": "3 (S-T-R-A-W-B-E-R-R-Y)", "max_new_tokens": 400},
    {"id": "tp-04-car-wash-100m", "prompt": "I need to get my car washed. The car wash is only 100 meters away. Should I walk there or drive my car?", "expected": "drive — the car has to be at the car wash to be washed", "max_new_tokens": 500},
]


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
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    log("\n=== BASELINE ===")
    baselines = {}
    for p in PROMPTS:
        r = gen(base, tok, p["prompt"], p["max_new_tokens"])
        baselines[p["id"]] = {"prompt": p["prompt"], "expected": p["expected"], "response": r}
        log(f"\n[{p['id']}] expected: {p['expected']}")
        log(f"  baseline: {r[:600]}")

    d = np.load(D_V2).astype(np.float32)
    log(f"\n\n=== STEERED with v2-Δ at α=+10 (Δ L2={np.linalg.norm(d):.3f}) ===")
    steered = {}
    for p in PROMPTS:
        hook = AdditiveSteeringHook(20, d, 10.0)
        hook.attach(base)
        try:
            r = gen(base, tok, p["prompt"], p["max_new_tokens"])
        finally:
            hook.detach()
        steered[p["id"]] = {"prompt": p["prompt"], "expected": p["expected"], "response": r}
        log(f"\n[{p['id']}]")
        log(f"  steered: {r[:600]}")

    from peft import PeftModel
    log(f"\n\n=== v2-DPO ADAPTED ===")
    model = PeftModel.from_pretrained(base, str(V2_ADAPTER))
    model.eval()
    adapted = {}
    for p in PROMPTS:
        r = gen(model, tok, p["prompt"], p["max_new_tokens"])
        adapted[p["id"]] = {"prompt": p["prompt"], "expected": p["expected"], "response": r}
        log(f"\n[{p['id']}]")
        log(f"  dpo: {r[:600]}")

    json.dump({"baseline": baselines, "v2_steered_alpha10": steered, "v2_dpo_adapted": adapted,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT_DIR / "comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'comparison.json'}")
    log("TRICK-PROMPTS COMPLETE")


if __name__ == "__main__":
    main()
