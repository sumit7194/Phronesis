"""Baseline E2 seed replication — companion to seed_replication_e2.py for comparison.
If baseline shows F138-style hedging at similar rate as v2-DPO, the F138 effect is noise.
If baseline is much lower, v2-DPO's 5/10 is a real shift."""
import json, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
OUT = ROOT / "mvp" / "results" / "all_deltas" / "seed_replication_e2_baseline.json"

N_SEEDS = 10
TEMP = 0.7


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

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    log("\n=== BASELINE greedy ===")
    greedy = gen(model, tok, e2["prompt"], cap, seed=0, do_sample=False)
    log(f"  ({len(greedy)}c) tail: ...{greedy[-280:]!r}")

    log(f"\n=== BASELINE {N_SEEDS} sampled (temp={TEMP}) ===")
    sampled = {}
    for seed in range(N_SEEDS):
        r = gen(model, tok, e2["prompt"], cap, seed=seed, do_sample=True, temp=TEMP)
        sampled[f"seed_{seed}"] = r
        log(f"\n  seed={seed} ({len(r)}c) tail: ...{r[-280:]!r}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"prompt": e2["prompt"], "max_new_tokens": cap,
               "greedy": greedy, "sampled_temp_07": sampled,
               "n_seeds": N_SEEDS,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(OUT, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT}")
    log("BASELINE-SEED-REPLICATION COMPLETE")


if __name__ == "__main__":
    main()
