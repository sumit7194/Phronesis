"""Step 2: steer baseline with the pre-extracted DPO Δ direction."""
import json, time
from pathlib import Path
import numpy as np
import torch
import pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
OUT_DIR = ROOT / "mvp" / "results" / "dpo_delta_steering"

E2_PROMPT = "Does flossing prevent cavities? What is your confidence level in this answer?"
ALPHAS = [-50.0, -25.0, -10.0, -5.0, -1.0, +1.0, +3.0, +5.0, +10.0, +25.0, +50.0]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new=600):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    d_dpo = np.load(OUT_DIR / "d_dpo_avg.npy").astype(np.float32)
    log(f"Loaded d_dpo_avg: L2 = {np.linalg.norm(d_dpo):.4f}")

    arith = pq.read_table(ROOT / "mvp" / "results" / "nla_qwen25_L20_experiment" /
                          "activations_arithmetic.parquet").to_pandas()
    v_diff = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                      dtype=np.float32)
    def cos(a, b):
        a = np.asarray(a).flatten(); b = np.asarray(b).flatten()
        return float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-12))
    log(f"cos(d_dpo, v_diff_F126) = {cos(d_dpo, v_diff):+.4f}")

    log(f"Loading fresh base {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    log("\nBaseline (no steering):")
    base_resp = gen(base, tok, E2_PROMPT)
    log(f"  ({len(base_resp)}c) ...{base_resp[-280:]!r}")

    results = {"config": {"direction": "DPO_Δ_avg_3prompts (from v2-IH-DPO adapter)",
                          "d_dpo_norm": float(np.linalg.norm(d_dpo)),
                          "cos_with_v_diff_F126": cos(d_dpo, v_diff),
                          "alphas": ALPHAS,
                          "prompt": E2_PROMPT},
               "baseline": base_resp, "steered": {}}

    for alpha in ALPHAS:
        hook = AdditiveSteeringHook(20, d_dpo, alpha)
        hook.attach(base)
        try:
            resp = gen(base, tok, E2_PROMPT)
        finally:
            hook.detach()
        results["steered"][f"{alpha:+.2f}"] = resp
        log(f"\nα={alpha:+.1f} ({len(resp)}c) ...{resp[-280:]!r}")

    json.dump(results, open(OUT_DIR / "dpo_delta_steering.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'dpo_delta_steering.json'}")
    log("DPO Δ STEERING COMPLETE")


if __name__ == "__main__":
    main()
