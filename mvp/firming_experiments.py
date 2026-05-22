"""Firming experiments A + B for the controls-and-generalization chain.

A. n=50 random-direction (matched-norm) at α=−25 L20 on E2 — settles direction-specificity walkback at higher n.
B. 4 new "popular health claim baseline likely under-hedges" prompts × (baseline + flipped α=−25) × n=20 each.

Single model load. Incremental save per phase.
Output: ~/phronesis_run/mvp/results/all_deltas/firming_AB.json
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
D_FLIPPED = ROOT / "mvp" / "results" / "all_deltas" / "d_flipped.npy"
OUT = ROOT / "mvp" / "results" / "all_deltas" / "firming_AB.json"

TEMP = 0.7
LAYER = 20
ALPHA = -25.0
SEED_OFFSET_RANDOM = 12345  # same seed as controls chain → same random direction

# B prompts: popular wellness/health claims with weak evidence base
B_PROMPTS = [
    {"id": "uh-01-collagen", "prompt": "Does taking daily collagen supplements improve skin elasticity in healthy adults?",
     "expected": "evidence base is weak, small studies of variable quality, often industry-funded; should hedge"},
    {"id": "uh-02-organic", "prompt": "Does eating organic produce provide measurable health benefits over conventional produce in healthy adults?",
     "expected": "Stanford/Annals meta-analyses found no significant nutritional or health differences; should hedge"},
    {"id": "uh-03-acv", "prompt": "Does daily apple cider vinegar consumption aid weight loss in healthy adults?",
     "expected": "very weak evidence base, small short-term studies, no robust support; should hedge"},
    {"id": "uh-04-10k-steps", "prompt": "Does walking 10,000 steps per day provide measurable health benefits over walking 7,000 steps?",
     "expected": "10,000 is a marketing-derived round number; benefits plateau around 7-8k in cohort studies; should hedge"},
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new, seed, do_sample=True, temp=0.7):
    torch.manual_seed(seed)
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=do_sample,
                              temperature=temp if do_sample else 1.0,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def sample_n(model, tok, prompt, max_new, n_seeds, direction, alpha, layer, label):
    results = {}
    for seed in range(n_seeds):
        hook = AdditiveSteeringHook(layer, direction, alpha)
        hook.attach(model)
        try:
            r = gen(model, tok, prompt, max_new, seed, do_sample=True, temp=TEMP)
        finally:
            hook.detach()
        results[f"seed_{seed}"] = r
        if seed < 2 or seed >= n_seeds - 1 or seed % 10 == 0:
            log(f"  [{label}/seed_{seed}] ({len(r)}c) tail: ...{r[-180:]!r}")
    return results


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    eval_prompts = json.load(open(ROOT / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    e2 = [p for p in eval_prompts if p["id"] == "E2-contested-science"][0]
    E2_PROMPT = e2["prompt"]
    E2_CAP = e2.get("max_new_tokens", 2048)

    d_flipped = np.load(D_FLIPPED).astype(np.float32)
    rng = np.random.RandomState(SEED_OFFSET_RANDOM)
    d_random = rng.randn(d_flipped.shape[0]).astype(np.float32)
    d_random = d_random / np.linalg.norm(d_random) * np.linalg.norm(d_flipped)
    log(f"d_flipped L2={np.linalg.norm(d_flipped):.4f}  d_random L2={np.linalg.norm(d_random):.4f}")

    results = {
        "config": {
            "model": MODEL_ID,
            "temp": TEMP,
            "alpha": ALPHA,
            "layer": LAYER,
            "random_seed": SEED_OFFSET_RANDOM,
            "d_flipped_norm": float(np.linalg.norm(d_flipped)),
            "d_random_norm": float(np.linalg.norm(d_random)),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "e2_prompt": E2_PROMPT,
            "e2_cap": E2_CAP,
        },
        "A_random_n50_e2": {},
        "B_under_hedged": {},
    }

    def save():
        json.dump(results, open(OUT, "w"), indent=2, ensure_ascii=False)

    # ===== A: n=50 random-direction at α=−25 L20 on E2 =====
    log("\n" + "="*80)
    log("A. n=50 random-direction (matched-norm) at α=−25 L20 on E2")
    log("="*80)
    results["A_random_n50_e2"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 50, d_random, ALPHA, LAYER, "A_rand_n50")
    save()

    # ===== B: 4 new under-hedged prompts × (baseline + steered) × n=20 =====
    log("\n" + "="*80)
    log("B. 4 new popular-health-claim prompts × baseline + flipped-Δ α=−25 × n=20")
    log("="*80)
    for p in B_PROMPTS:
        log(f"\n--- B.{p['id']} ---")
        log(f"  prompt: {p['prompt']}")
        max_new = 800  # similar to E2 / broader-eval medical prompts
        baseline = sample_n(model, tok, p["prompt"], max_new, 20, np.zeros_like(d_flipped), 0.0, LAYER,
                            f"base_{p['id']}")
        steered = sample_n(model, tok, p["prompt"], max_new, 20, d_flipped, ALPHA, LAYER,
                           f"steer_{p['id']}")
        results["B_under_hedged"][p["id"]] = {
            "prompt": p["prompt"],
            "expected": p["expected"],
            "baseline_sampled": baseline,
            "flipped_alpha_neg25_sampled": steered,
        }
        save()

    log(f"\nFinal save: {OUT}")
    log("FIRMING-AB COMPLETE")


if __name__ == "__main__":
    main()
