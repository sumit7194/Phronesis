"""n=50 seed-replication for flipped-Δ at α=−25 on E2.

Companion to seed_replication_e2.py and seed_replication_e2_baseline.py.
This is the load-bearing confirmation for the closing_validation finding that
flipped-Δ at α=−25 produces a +41pp (regex) / +53pp (hand-review) distributional
shift toward hedging on E2 — currently the strongest positive empirical finding
in the Phronesis project and the only one not predicted by prior frameworks
(D-STEER, Pan et al., Pres et al.).

If n=50 confirms (~50-65% hedge rate): finding is solid, post can lead with it.
If n=50 lands lower (~30-40%): effect is real but smaller, post hedges accordingly.
If n=50 lands at baseline rate (~22%): finding was n=20 sampling variance, walkback.
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
OUT = ROOT / "mvp" / "results" / "all_deltas" / "flipped_alpha_neg25_n50.json"

N_SEEDS = 50
TEMP = 0.7
ALPHA = -25.0
LAYER = 20


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


def main():
    eval_prompts = json.load(open(ROOT / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    e2 = [p for p in eval_prompts if p["id"] == "E2-contested-science"][0]
    log(f"E2 prompt: {e2['prompt'][:120]}...")
    cap = e2.get("max_new_tokens", 2048)

    d_flipped = np.load(D_FLIPPED).astype(np.float32)
    log(f"d_flipped L2={np.linalg.norm(d_flipped):.4f}")
    log(f"Steering config: layer={LAYER}, alpha={ALPHA}, n_seeds={N_SEEDS}, temp={TEMP}")

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    # Greedy first (sanity check the steering hook is doing what we think)
    log("\n=== Greedy (do_sample=False) ===")
    hook = AdditiveSteeringHook(LAYER, d_flipped, ALPHA)
    hook.attach(model)
    try:
        greedy = gen(model, tok, e2["prompt"], cap, seed=0, do_sample=False)
    finally:
        hook.detach()
    log(f"  ({len(greedy)}c) tail: ...{greedy[-300:]!r}")

    # n=50 sampled
    log(f"\n=== {N_SEEDS} sampled @ temp={TEMP} ===")
    sampled = {}
    for seed in range(N_SEEDS):
        hook = AdditiveSteeringHook(LAYER, d_flipped, ALPHA)
        hook.attach(model)
        try:
            r = gen(model, tok, e2["prompt"], cap, seed=seed, do_sample=True, temp=TEMP)
        finally:
            hook.detach()
        sampled[f"seed_{seed}"] = r
        if seed < 5 or seed >= N_SEEDS - 3 or seed % 10 == 0:
            log(f"  seed={seed} ({len(r)}c) tail: ...{r[-220:]!r}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"prompt": e2["prompt"], "max_new_tokens": cap,
               "steering": {"layer": LAYER, "alpha": ALPHA, "direction": "d_flipped",
                            "d_norm": float(np.linalg.norm(d_flipped))},
               "greedy": greedy, "sampled_temp_07": sampled,
               "n_seeds": N_SEEDS,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT}")
    log("FLIPPED-N50 COMPLETE")


if __name__ == "__main__":
    main()
