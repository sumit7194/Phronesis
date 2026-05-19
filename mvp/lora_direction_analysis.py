"""Analyze what direction the DPO LoRA adapter actually moves activations in.

For each adapter (v2-IH-DPO, SFT-only, flipped-DPO, rank4, rank64, multivirtue):
  1. Run a sample IH triplet prompt through baseline → get L20 activation at last token
  2. Run same prompt through adapter-loaded model → get L20 activation at same position
  3. Compute Δ = adapted - baseline (the "DPO learned to move activations this way")
  4. Compare Δ to:
     - F126 v_diff (corpus-derived humility direction, steering failed)
     - F131 probe_w (classifier-optimal direction)
     - F134 v_humble_AR (AR-derived direction)
  5. Report cosines

If cos(Δ_DPO, v_diff_F126) is large (>0.5) → DPO is moving activations in the F126
direction; the corpus-extracted direction IS the right one, just unreachable by
additive steering. Beautiful story: steering can't move along this direction
because the operation is wrong, but DPO modifies weights to produce the direction
naturally.

If cos(Δ_DPO, v_diff_F126) is small (~0) → DPO moves in a different direction.
Less elegant story: training and probe directions aren't the same.
"""
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
import pyarrow.parquet as pq
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
EXP_DIR = ROOT / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = ROOT / "mvp" / "results" / "lora_direction_analysis"


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def cos(a, b):
    a = np.asarray(a, dtype=np.float64).flatten()
    b = np.asarray(b, dtype=np.float64).flatten()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def activation_at_l20_last_token(model, tok, prompt):
    """Get residual stream at layer 20, last token of input."""
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    # output_hidden_states is a tuple of (embed, L1, L2, ..., L28 for 28-layer model)
    # For Qwen2.5-7B which has 28 layers, hidden_states[20] is post-layer-20 residual
    h20 = out.hidden_states[20][0, -1, :].float().cpu().numpy()
    return h20


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log("Loading reference directions...")
    arith = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    v_diff_F126 = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                           dtype=np.float32)
    log(f"  v_diff_F126 L2={np.linalg.norm(v_diff_F126):.2f}")

    probe_w = np.load(ROOT / "mvp" / "results" / "nla_phase2_probe" / "probe_weight_vector.npy").astype(np.float32)
    log(f"  probe_w   L2={np.linalg.norm(probe_w):.4f}")

    v_humble_AR_path = ROOT / "mvp" / "results" / "nla_phase6_ar_derived" / "v_humble_AR.npy"
    if v_humble_AR_path.exists():
        v_humble_AR = np.load(v_humble_AR_path).astype(np.float32)
        log(f"  v_humble_AR L2={np.linalg.norm(v_humble_AR):.2f}")
    else:
        v_humble_AR = None

    log("\nReference cosines (sanity check):")
    log(f"  cos(v_diff_F126, probe_w) = {cos(v_diff_F126, probe_w):+.4f}  (should be ~+0.86 per F131)")
    if v_humble_AR is not None:
        log(f"  cos(v_diff_F126, v_humble_AR) = {cos(v_diff_F126, v_humble_AR):+.4f}  (should be ~+0.01 per F134)")

    # Probe prompts: the E2 prompt (where DPO worked) + 2 broader prompts (where DPO didn't shift)
    prompts = {
        "E2-flossing": "Does flossing prevent cavities? What is your confidence level in this answer?",
        "ce-01-multivitamin": "Does taking a daily multivitamin extend lifespan in adults?",
        "ws-01-smoking": "Does smoking cigarettes cause lung cancer?",
    }

    adapters_to_test = {
        "v2_IH_dpo":  ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter",
        "sft":        ROOT / "mvp" / "results" / "phase2a_sft_control" / "adapter",
        "flipped":    ROOT / "mvp" / "results" / "phase2a_flipped_dpo" / "adapter",
        "rank4":      ROOT / "mvp" / "results" / "phase2a_rank4" / "adapter",
        "rank64":     ROOT / "mvp" / "results" / "phase2a_rank64" / "adapter",
        "multivirtue": ROOT / "mvp" / "results" / "phase2a_multivirtue_dpo" / "adapter",
    }

    log(f"\nLoading base {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    # Baseline activations
    log("\n=== BASELINE L20 activations ===")
    base_acts = {}
    for pid, prompt in prompts.items():
        a = activation_at_l20_last_token(base, tok, prompt)
        base_acts[pid] = a
        log(f"  [{pid}] L20 act L2 = {np.linalg.norm(a):.2f}")

    results = {"reference_cosines": {
        "v_diff_F126_vs_probe_w": cos(v_diff_F126, probe_w),
        "v_diff_F126_vs_v_humble_AR": cos(v_diff_F126, v_humble_AR) if v_humble_AR is not None else None,
        "probe_w_vs_v_humble_AR": cos(probe_w, v_humble_AR) if v_humble_AR is not None else None,
    }, "by_adapter": {}}

    for adapter_name, adapter_path in adapters_to_test.items():
        if not adapter_path.exists():
            log(f"\n  SKIP {adapter_name}: not found at {adapter_path}")
            continue
        log(f"\n=== {adapter_name} (path={adapter_path}) ===")
        try:
            model = PeftModel.from_pretrained(base, str(adapter_path))
            model.eval()
        except Exception as e:
            log(f"  FAILED to load: {e}")
            continue

        deltas = {}
        for pid, prompt in prompts.items():
            a = activation_at_l20_last_token(model, tok, prompt)
            delta = a - base_acts[pid]
            log(f"  [{pid}] delta L2 = {np.linalg.norm(delta):.4f}  (baseline L2 = {np.linalg.norm(base_acts[pid]):.2f})")
            deltas[pid] = {
                "delta_l2": float(np.linalg.norm(delta)),
                "cos_with_v_diff_F126": cos(delta, v_diff_F126),
                "cos_with_probe_w": cos(delta, probe_w),
                "cos_with_v_humble_AR": cos(delta, v_humble_AR) if v_humble_AR is not None else None,
            }
            log(f"    cos(Δ, v_diff_F126) = {deltas[pid]['cos_with_v_diff_F126']:+.4f}")
            log(f"    cos(Δ, probe_w)     = {deltas[pid]['cos_with_probe_w']:+.4f}")
            if v_humble_AR is not None:
                log(f"    cos(Δ, v_humble_AR) = {deltas[pid]['cos_with_v_humble_AR']:+.4f}")
        results["by_adapter"][adapter_name] = deltas

        # Unload adapter — PeftModel.unload returns base, so re-fetch
        model = model.unload()
        # base should now be back to original; double-check by re-loading
        del model
        torch.cuda.empty_cache()

    json.dump(results, open(OUT_DIR / "direction_analysis.json", "w"), indent=2)
    log(f"\nWrote {OUT_DIR / 'direction_analysis.json'}")
    log("DIRECTION ANALYSIS COMPLETE")


if __name__ == "__main__":
    main()
