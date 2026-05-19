"""Run the broader 18-prompt eval set with DPO-Δ steering at α=+10.

If this produces broader generalization (multiple prompts shift like E2 did at α=+10),
F143 strengthens significantly. If only E2 shifts, F143 is also narrow.
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
PROMPTS_FILE = ROOT / "mvp" / "broader_eval_prompts.json"
D_FILE = ROOT / "mvp" / "results" / "dpo_delta_steering" / "d_dpo_avg.npy"
OUT_DIR = ROOT / "mvp" / "results" / "dpo_delta_broader_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA = 10.0  # the F143 sweet spot


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
    d_dpo = np.load(D_FILE).astype(np.float32)
    log(f"Loaded d_dpo: L2={np.linalg.norm(d_dpo):.4f}, steering α={ALPHA}")

    data = json.load(open(PROMPTS_FILE))
    all_prompts = []
    for cat in ["contested_evidence", "false_premise_or_knowledge_gap",
                "well_established_control", "trivia_factual_control"]:
        for p in data[cat]:
            p["category"] = cat
            all_prompts.append(p)
    log(f"Loaded {len(all_prompts)} broader-eval prompts")

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    log("\n=== BASELINE ===")
    baselines = {}
    for p in all_prompts:
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 600))
        baselines[p["id"]] = {"category": p["category"], "prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] ({len(r)}c) ...{r[-160:]!r}")

    log(f"\n=== STEERED with DPO-Δ at α={ALPHA} ===")
    steered = {}
    for p in all_prompts:
        hook = AdditiveSteeringHook(20, d_dpo, ALPHA)
        hook.attach(base)
        try:
            r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 600))
        finally:
            hook.detach()
        steered[p["id"]] = {"category": p["category"], "prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] ({len(r)}c) ...{r[-160:]!r}")

    json.dump({"alpha": ALPHA, "d_dpo_norm": float(np.linalg.norm(d_dpo)),
               "baseline": baselines, "steered": steered,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT_DIR / "broader_eval_at_alpha_plus10.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'broader_eval_at_alpha_plus10.json'}")
    log("BROADER DPO-Δ EVAL COMPLETE")


if __name__ == "__main__":
    main()
