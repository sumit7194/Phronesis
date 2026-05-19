"""Step 1: extract DPO Δ direction, save to .npy. Process exits cleanly."""
import time
from pathlib import Path
import numpy as np
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
ADAPTER = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
OUT_DIR = ROOT / "mvp" / "results" / "dpo_delta_steering"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def get_l20_act(model, tok, prompt):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    return out.hidden_states[20][0, -1, :].float().cpu().numpy()


def main():
    log(f"Loading base {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    prompts = [
        "Does flossing prevent cavities? What is your confidence level in this answer?",
        "Does taking a daily multivitamin extend lifespan in adults?",
        "Does smoking cigarettes cause lung cancer?",
    ]

    log("Computing baseline L20 activations...")
    base_acts = [get_l20_act(base, tok, p) for p in prompts]
    for i, a in enumerate(base_acts):
        log(f"  baseline[{i}] L2 = {np.linalg.norm(a):.2f}")

    log(f"\nLoading adapter {ADAPTER}...")
    model = PeftModel.from_pretrained(base, str(ADAPTER))
    model.eval()
    log("Computing DPO-adapted L20 activations...")
    dpo_acts = [get_l20_act(model, tok, p) for p in prompts]
    for i, a in enumerate(dpo_acts):
        log(f"  dpo[{i}] L2 = {np.linalg.norm(a):.2f}")

    deltas = [dpo_acts[i] - base_acts[i] for i in range(len(prompts))]
    d_avg = np.mean(deltas, axis=0)
    log(f"\nd_dpo_avg L2 = {np.linalg.norm(d_avg):.4f}")

    np.save(OUT_DIR / "d_dpo_avg.npy", d_avg)
    # Also save individual deltas for completeness
    for i, d in enumerate(deltas):
        np.save(OUT_DIR / f"d_dpo_p{i}.npy", d)
    log(f"Wrote {OUT_DIR / 'd_dpo_avg.npy'}")
    log("EXTRACT COMPLETE")


if __name__ == "__main__":
    main()
