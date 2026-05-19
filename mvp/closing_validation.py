"""Closing validation script — all 6 seed-replication experiments in one process.

Designed for closing data collection before writeup. NO interpretation of results,
NO follow-up experiments. Just run, save artifacts, exit.

Experiments:
1. E2 baseline n=50 sampled (tighten noise floor from ±15% to ±7%)
2. E2 v2-Δ steered α=+10 n=20 sampled (F143 distributional analog)
3. E2 flipped-Δ steered α=−25 n=20 sampled (Result 3 seed rep)
4. E2 v2-Δ steered at L15 α=+25 n=10 sampled (L15 anomaly reproducibility)
5. Turkey-tryptophan: baseline + v2-Δ + v2-DPO n=20 each (one positive correction)
6. Probiotics: baseline + v2-Δ + v2-DPO n=20 each (non-correction)
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
V2_ADAPTER = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
D_V2 = ROOT / "mvp" / "results" / "all_deltas" / "d_v2_IH.npy"
D_FLIPPED = ROOT / "mvp" / "results" / "all_deltas" / "d_flipped.npy"
OUT_DIR = ROOT / "mvp" / "results" / "closing_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP = 0.7

TURKEY_PROMPT = "Does eating turkey make you sleepy because of tryptophan? Provide your confidence level."
PROBIOTICS_PROMPT = "Should you take probiotics after a course of antibiotics to restore gut health? Provide your confidence level."


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


def sample_n(model, tok, prompt, max_new, n_seeds, hook=None, label=""):
    """Run n_seeds sampled generations, optionally with a steering hook attached."""
    if hook is not None:
        hook.attach(model)
    try:
        results = {}
        for seed in range(n_seeds):
            r = gen(model, tok, prompt, max_new, seed, do_sample=True, temp=TEMP)
            results[f"seed_{seed}"] = r
            if seed < 3 or seed == n_seeds - 1:
                log(f"  [{label}] seed={seed} ({len(r)}c) tail: ...{r[-180:]!r}")
            elif seed == 3:
                log(f"  [{label}] ... (suppressing middle seeds)")
        return results
    finally:
        if hook is not None:
            hook.detach()


def main():
    # E2 from sae-battery
    eval_prompts = json.load(open(ROOT / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    e2 = [p for p in eval_prompts if p["id"] == "E2-contested-science"][0]
    E2_PROMPT = e2["prompt"]
    E2_CAP = e2.get("max_new_tokens", 2048)
    log(f"E2 prompt: {E2_PROMPT[:100]}...  cap={E2_CAP}")

    # Load directions
    d_v2 = np.load(D_V2).astype(np.float32)
    d_flipped = np.load(D_FLIPPED).astype(np.float32)
    log(f"d_v2 L2={np.linalg.norm(d_v2):.4f}  d_flipped L2={np.linalg.norm(d_flipped):.4f}")

    # Load tokenizer + base model (loaded once)
    log(f"\nLoading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    results = {}

    # ===== Experiment 1: E2 baseline n=50 =====
    log(f"\n=== 1. E2 baseline n=50 sampled @ temp={TEMP} (~20 min) ===")
    results["e2_baseline_n50"] = sample_n(base, tok, E2_PROMPT, E2_CAP, 50, hook=None, label="e2_baseline")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Experiment 2: E2 v2-Δ steered α=+10 n=20 =====
    log(f"\n=== 2. E2 v2-Δ steered α=+10 n=20 (F143 distributional analog) ===")
    hook = AdditiveSteeringHook(20, d_v2, 10.0)
    results["e2_v2delta_alpha10_n20"] = sample_n(base, tok, E2_PROMPT, E2_CAP, 20, hook=hook, label="e2_v2delta")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Experiment 3: E2 flipped-Δ α=-25 n=20 =====
    log(f"\n=== 3. E2 flipped-Δ steered α=−25 n=20 (Result 3 seed rep) ===")
    hook = AdditiveSteeringHook(20, d_flipped, -25.0)
    results["e2_flipped_alpha_neg25_n20"] = sample_n(base, tok, E2_PROMPT, E2_CAP, 20, hook=hook, label="e2_flipped")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Experiment 4: E2 v2-Δ at L15 α=+25 n=10 =====
    log(f"\n=== 4. E2 v2-Δ at L15 α=+25 n=10 (L15 anomaly reproducibility) ===")
    hook = AdditiveSteeringHook(15, d_v2, 25.0)
    results["e2_v2delta_L15_alpha25_n10"] = sample_n(base, tok, E2_PROMPT, E2_CAP, 10, hook=hook, label="e2_L15_a25")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Experiment 5: Turkey-tryptophan: baseline + v2-Δ + v2-DPO n=20 each =====
    log(f"\n=== 5a. Turkey baseline n=20 ===")
    results["turkey_baseline_n20"] = sample_n(base, tok, TURKEY_PROMPT, 500, 20, hook=None, label="turkey_baseline")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    log(f"\n=== 5b. Turkey v2-Δ steered α=+10 n=20 ===")
    hook = AdditiveSteeringHook(20, d_v2, 10.0)
    results["turkey_v2delta_alpha10_n20"] = sample_n(base, tok, TURKEY_PROMPT, 500, 20, hook=hook, label="turkey_v2delta")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Experiment 6: Probiotics: baseline + v2-Δ n=20 each =====
    log(f"\n=== 6a. Probiotics baseline n=20 ===")
    results["probiotics_baseline_n20"] = sample_n(base, tok, PROBIOTICS_PROMPT, 500, 20, hook=None, label="probiotics_baseline")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    log(f"\n=== 6b. Probiotics v2-Δ steered α=+10 n=20 ===")
    hook = AdditiveSteeringHook(20, d_v2, 10.0)
    results["probiotics_v2delta_alpha10_n20"] = sample_n(base, tok, PROBIOTICS_PROMPT, 500, 20, hook=hook, label="probiotics_v2delta")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    # ===== Now load v2-DPO adapter for the adapter-side tests =====
    log(f"\n\nLoading v2-DPO adapter for adapter-side tests...")
    from peft import PeftModel
    model = PeftModel.from_pretrained(base, str(V2_ADAPTER))
    model.eval()

    log(f"\n=== 5c. Turkey v2-DPO n=20 ===")
    results["turkey_v2dpo_n20"] = sample_n(model, tok, TURKEY_PROMPT, 500, 20, hook=None, label="turkey_v2dpo")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    log(f"\n=== 6c. Probiotics v2-DPO n=20 ===")
    results["probiotics_v2dpo_n20"] = sample_n(model, tok, PROBIOTICS_PROMPT, 500, 20, hook=None, label="probiotics_v2dpo")
    json.dump(results, open(OUT_DIR / "results.json", "w"), indent=2, ensure_ascii=False)

    log(f"\nFinal save: {OUT_DIR / 'results.json'}")
    log("CLOSING-VALIDATION COMPLETE — no follow-up experiments will be launched")


if __name__ == "__main__":
    main()
