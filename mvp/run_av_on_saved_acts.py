"""Load saved L20 activations from .npy files, pass each through NLA AV, compare."""
import json, time
from pathlib import Path
import numpy as np
import torch
import yaml
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

AV_REPO = "kitft/nla-qwen2.5-7b-L20-av"
ROOT = Path.home() / "phronesis_run"
ACTS_DIR = ROOT / "mvp" / "results" / "av_on_dpo_activations" / "acts"
OUT_DIR = ROOT / "mvp" / "results" / "av_on_dpo_activations"

PROMPTS = ["E2-flossing", "ce-01-multivitamin", "ws-01-smoking", "oc-08-power-poses"]
LABELS = ["baseline", "v2_DPO", "multivirtue_DPO"]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def av_generate(av_model, av_tok, activation, av_meta):
    template = av_meta["prompt_templates"]["av"]
    inj_char = av_meta["extraction"].get("injection_char", "X")
    target_norm = av_meta["extraction"].get("activation_norm", 150.0)

    ids = av_tok(template, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
    char_ids = av_tok.encode(inj_char, add_special_tokens=False)
    target_token_id = char_ids[0] if char_ids else None
    inj_pos = ids.shape[1] - 1
    if target_token_id is not None:
        positions = (ids[0] == target_token_id).nonzero(as_tuple=True)[0]
        if len(positions) > 0:
            inj_pos = positions[-1].item()

    act_t = torch.as_tensor(activation, dtype=torch.bfloat16, device="cuda")
    act_t = act_t / (act_t.norm() + 1e-9) * target_norm

    embed_layer = av_model.get_input_embeddings()
    orig_forward = embed_layer.forward
    def patched_forward(input_ids):
        embeds = orig_forward(input_ids)
        if embeds.shape[1] > inj_pos:
            embeds = embeds.clone()
            embeds[0, inj_pos] = act_t.to(embeds.dtype)
        return embeds
    embed_layer.forward = patched_forward
    try:
        with torch.no_grad():
            out = av_model.generate(ids, max_new_tokens=200, do_sample=False,
                                     pad_token_id=av_tok.eos_token_id)
        result = av_tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    finally:
        embed_layer.forward = orig_forward
    return result


def main():
    log(f"Loading NLA AV from {AV_REPO}...")
    av_path = snapshot_download(AV_REPO)
    av_meta = yaml.safe_load(open(f"{av_path}/nla_meta.yaml"))
    log(f"  injection_char={av_meta['extraction'].get('injection_char')}  norm={av_meta['extraction'].get('activation_norm')}")

    av_tok = AutoTokenizer.from_pretrained(av_path)
    av_model = AutoModelForCausalLM.from_pretrained(av_path, torch_dtype=torch.bfloat16, device_map="cuda")
    av_model.eval()

    results = {}
    for pid in PROMPTS:
        results[pid] = {}
        for label in LABELS:
            act_path = ACTS_DIR / f"{label}_{pid}.npy"
            if not act_path.exists():
                log(f"  MISSING {act_path}")
                continue
            act = np.load(act_path)
            log(f"\n[{pid}/{label}] L2={np.linalg.norm(act):.2f}")
            text = av_generate(av_model, av_tok, act, av_meta)
            log(f"  AV: {text[:300]!r}")
            results[pid][label] = {"av_text": text, "act_l2": float(np.linalg.norm(act))}

    json.dump(results, open(OUT_DIR / "av_comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'av_comparison.json'}")
    log("AV-COMPARISON COMPLETE")


if __name__ == "__main__":
    main()
