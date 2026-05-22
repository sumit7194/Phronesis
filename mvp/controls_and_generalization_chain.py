"""Comprehensive validation chain for the flipped-Δ +34pp finding.

Four phases, all run in one process (single model load to save time):

Phase 1 — Direction-specificity controls (~25 min):
  - v_diff at α=−25 on E2 n=20 sampled (is v_diff at large |α| also hedging?)
  - v_diff at α=+25 on E2 n=20 (symmetry check)
  - random matched-norm vector at α=−25 on E2 n=20 (does ANY high-α direction hedge?)
  - random matched-norm vector at α=+25 on E2 n=20 (symmetry control)
  - flipped-Δ at α=+25 on E2 n=20 (does opposite sign produce anti-hedging?)

Phase 2 — Broader-prompt generalization (~30 min):
  - flipped-Δ at α=−25 on 18 broader-eval prompts at n=10 each
  - Compare against existing greedy baselines

Phase 3 — Cross-layer mapping (~20 min):
  - flipped-Δ at α=−25 at L15, L18, L22, L25 on E2, n=20 each

Phase 4 — Dose-response curve (~30 min):
  - flipped-Δ on E2 at α ∈ {−5, −10, −15, −20, −30, −40}, n=20 each at L20

Output: mvp/results/all_deltas/controls_and_generalization.json (incremental save after each phase)
"""
import json, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook
import pyarrow.parquet as pq

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
D_FLIPPED = ROOT / "mvp" / "results" / "all_deltas" / "d_flipped.npy"
EXP_DIR = ROOT / "mvp" / "results" / "nla_qwen25_L20_experiment"
BROADER_PROMPTS = ROOT / "mvp" / "broader_eval_prompts.json"
OUT = ROOT / "mvp" / "results" / "all_deltas" / "controls_and_generalization.json"

TEMP = 0.7
SEED_OFFSET_RANDOM = 12345  # for reproducible random direction


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
    """Run n_seeds sampled generations with steering hook attached at given layer/alpha."""
    results = {}
    for seed in range(n_seeds):
        hook = AdditiveSteeringHook(layer, direction, alpha)
        hook.attach(model)
        try:
            r = gen(model, tok, prompt, max_new, seed, do_sample=True, temp=TEMP)
        finally:
            hook.detach()
        results[f"seed_{seed}"] = r
        if seed < 2 or seed >= n_seeds - 1:
            log(f"  [{label}/seed_{seed}] ({len(r)}c) tail: ...{r[-200:]!r}")
    return results


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    # Load E2 prompt
    eval_prompts = json.load(open(ROOT / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    e2 = [p for p in eval_prompts if p["id"] == "E2-contested-science"][0]
    E2_PROMPT = e2["prompt"]
    E2_CAP = e2.get("max_new_tokens", 2048)
    log(f"E2 cap={E2_CAP}")

    # Load directions
    d_flipped = np.load(D_FLIPPED).astype(np.float32)
    log(f"d_flipped L2={np.linalg.norm(d_flipped):.4f}")

    # v_diff_F126 — the discrimination direction
    arith = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    v_diff = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                      dtype=np.float32)
    log(f"v_diff L2={np.linalg.norm(v_diff):.2f}")
    # Rescale v_diff to match d_flipped's L2 for fair comparison
    v_diff_matched = v_diff / np.linalg.norm(v_diff) * np.linalg.norm(d_flipped)
    log(f"v_diff (rescaled to match d_flipped L2): {np.linalg.norm(v_diff_matched):.4f}")

    # Random matched-norm direction
    rng = np.random.RandomState(SEED_OFFSET_RANDOM)
    d_random = rng.randn(d_flipped.shape[0]).astype(np.float32)
    d_random = d_random / np.linalg.norm(d_random) * np.linalg.norm(d_flipped)
    log(f"d_random L2={np.linalg.norm(d_random):.4f}")

    results = {
        "config": {
            "model": MODEL_ID,
            "e2_prompt": E2_PROMPT,
            "e2_cap": E2_CAP,
            "temp": TEMP,
            "d_flipped_norm": float(np.linalg.norm(d_flipped)),
            "v_diff_matched_norm": float(np.linalg.norm(v_diff_matched)),
            "d_random_norm": float(np.linalg.norm(d_random)),
            "v_diff_orig_norm": float(np.linalg.norm(v_diff)),
            "random_seed": SEED_OFFSET_RANDOM,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "phase1_controls": {},
        "phase2_broader_eval": {},
        "phase3_crosslayer": {},
        "phase4_dose_response": {},
    }

    def save():
        json.dump(results, open(OUT, "w"), indent=2, ensure_ascii=False)

    # ===== PHASE 1: Direction-specificity controls (E2, L20, n=20 each) =====
    log("\n" + "="*80)
    log("PHASE 1: Direction-specificity controls (E2, L20, n=20 each)")
    log("="*80)

    log("\n--- 1a. v_diff (rescaled to d_flipped L2) at α=−25 ---")
    results["phase1_controls"]["vdiff_matched_alpha_neg25"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 20, v_diff_matched, -25.0, 20, "vdiff_n25")
    save()

    log("\n--- 1b. v_diff (rescaled) at α=+25 ---")
    results["phase1_controls"]["vdiff_matched_alpha_pos25"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 20, v_diff_matched, 25.0, 20, "vdiff_p25")
    save()

    log("\n--- 1c. Random direction (matched-norm) at α=−25 ---")
    results["phase1_controls"]["random_alpha_neg25"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 20, d_random, -25.0, 20, "rand_n25")
    save()

    log("\n--- 1d. Random direction at α=+25 ---")
    results["phase1_controls"]["random_alpha_pos25"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 20, d_random, 25.0, 20, "rand_p25")
    save()

    log("\n--- 1e. Flipped-Δ at α=+25 (anti-hedging check) ---")
    results["phase1_controls"]["flipped_alpha_pos25"] = sample_n(
        model, tok, E2_PROMPT, E2_CAP, 20, d_flipped, 25.0, 20, "flipped_p25")
    save()

    # ===== PHASE 2: Broader-prompt generalization =====
    log("\n" + "="*80)
    log("PHASE 2: Broader-prompt generalization (flipped-Δ α=−25 on 18 prompts, n=10 each)")
    log("="*80)

    broader_data = json.load(open(BROADER_PROMPTS))
    all_prompts = []
    for cat in ["contested_evidence", "false_premise_or_knowledge_gap",
                "well_established_control", "trivia_factual_control"]:
        for p in broader_data[cat]:
            p["category"] = cat
            all_prompts.append(p)

    for p in all_prompts:
        log(f"\n--- 2.{p['id']} ({p['category']}) ---")
        max_new = p.get("max_new_tokens", 600)
        steered = sample_n(model, tok, p["prompt"], max_new, 10, d_flipped, -25.0, 20,
                           f"broader_{p['id']}")
        baseline = sample_n(model, tok, p["prompt"], max_new, 10, np.zeros_like(d_flipped), 0.0, 20,
                            f"baseline_{p['id']}")
        # Note: baseline with zero direction is equivalent to no steering hook,
        # but we use hook with zero magnitude so it's logically explicit.
        results["phase2_broader_eval"][p["id"]] = {
            "category": p["category"],
            "prompt": p["prompt"],
            "expected": p.get("expected_calibrated_response", p.get("context", "")),
            "baseline_sampled": baseline,
            "flipped_alpha_neg25_sampled": steered,
        }
        save()

    # ===== PHASE 3: Cross-layer flipped-Δ α=−25 (E2, n=20 each layer) =====
    log("\n" + "="*80)
    log("PHASE 3: Cross-layer flipped-Δ α=−25 (E2, n=20 each at L15/L18/L22/L25)")
    log("="*80)

    for layer in [15, 18, 22, 25]:
        log(f"\n--- 3.L{layer} flipped-Δ α=−25 ---")
        results["phase3_crosslayer"][f"L{layer}"] = sample_n(
            model, tok, E2_PROMPT, E2_CAP, 20, d_flipped, -25.0, layer, f"L{layer}_flipped_n25")
        save()

    # ===== PHASE 4: Dose-response curve (E2, L20, flipped-Δ at varying α) =====
    log("\n" + "="*80)
    log("PHASE 4: Dose-response curve (E2, L20, flipped-Δ at α ∈ [−40, −5])")
    log("="*80)

    for alpha in [-40.0, -30.0, -20.0, -15.0, -10.0, -5.0]:
        log(f"\n--- 4.α={alpha} flipped-Δ ---")
        results["phase4_dose_response"][f"alpha_{alpha:+.0f}"] = sample_n(
            model, tok, E2_PROMPT, E2_CAP, 20, d_flipped, alpha, 20, f"a{alpha:+.0f}")
        save()

    log(f"\nFinal save: {OUT}")
    log("CONTROLS-AND-GENERALIZATION CHAIN COMPLETE")


if __name__ == "__main__":
    main()
