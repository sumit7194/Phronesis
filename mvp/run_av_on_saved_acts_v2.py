"""Run NLA AV on saved L20 activations — CORRECTED to match run_nla_av_inference.py.

Fixes from v1:
- Use meta["tokens"]["injection_char"] / ["injection_token_id"] not extraction.*
- Use meta["extraction"]["injection_scale"]
- Wrap content in apply_chat_template with user role
- Generate via inputs_embeds= (returns only new tokens)
- Format the template with .format(injection_char=inj_char)
"""
import json, os, re, time
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
CJK_RE = re.compile(r"[　-鿿가-힯]")
MAX_NEW_TOKENS = 250


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    log(f"Downloading {AV_REPO}...")
    av_path = snapshot_download(AV_REPO)

    meta = yaml.safe_load(open(os.path.join(av_path, "nla_meta.yaml")))
    inj_char = meta["tokens"]["injection_char"]
    inj_token_id = meta["tokens"]["injection_token_id"]
    inj_left = meta["tokens"]["injection_left_neighbor_id"]
    inj_right = meta["tokens"]["injection_right_neighbor_id"]
    inj_scale = float(meta["extraction"]["injection_scale"])
    template = meta["prompt_templates"]["av"]
    d_model = int(meta["d_model"])
    log(f"  d_model={d_model}  injection_scale={inj_scale}  inj_token_id={inj_token_id}")

    log("Loading AV model + tokenizer...")
    tok = AutoTokenizer.from_pretrained(av_path)
    model = AutoModelForCausalLM.from_pretrained(av_path, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    live = tok.encode(inj_char, add_special_tokens=False)
    assert live == [inj_token_id], f"tokenizer drift: {inj_char!r}→{live}, sidecar={inj_token_id}"

    # Build the chat-templated prompt with the injection char filled in
    content = template.format(injection_char=inj_char)
    be = tok.apply_chat_template(
        [{"role": "user", "content": content}],
        tokenize=True, add_generation_prompt=True,
    )
    prompt_ids = be["input_ids"] if isinstance(be, dict) or hasattr(be, "keys") else be
    inj_positions = [i for i, t in enumerate(prompt_ids) if t == inj_token_id]
    assert len(inj_positions) == 1, f"injection token appears {len(inj_positions)}× in prompt"
    inj_pos = inj_positions[0]
    assert prompt_ids[inj_pos - 1] == inj_left and prompt_ids[inj_pos + 1] == inj_right
    log(f"  injection at position {inj_pos}/{len(prompt_ids)}")

    embed = model.get_input_embeddings()
    prompt_ids_t = torch.tensor(prompt_ids, device="cuda").unsqueeze(0)
    prompt_embeds = embed(prompt_ids_t)
    attention_mask = torch.ones_like(prompt_ids_t)

    results = {}
    for pid in PROMPTS:
        results[pid] = {}
        for label in LABELS:
            act_path = ACTS_DIR / f"{label}_{pid}.npy"
            if not act_path.exists():
                log(f"  MISSING {act_path}")
                continue
            act_np = np.load(act_path)
            act_l2 = float(np.linalg.norm(act_np))

            v = torch.tensor(act_np, dtype=torch.bfloat16, device="cuda")
            scale = inj_scale / max(act_l2, 1e-12)
            v_scaled = (v.float() * scale).to(torch.bfloat16)

            embeds = prompt_embeds.clone()
            embeds[0, inj_pos] = v_scaled

            with torch.no_grad():
                out = model.generate(
                    inputs_embeds=embeds,
                    attention_mask=attention_mask,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                    pad_token_id=tok.eos_token_id,
                )
            # generate with inputs_embeds returns only new tokens
            text = tok.decode(out[0], skip_special_tokens=True)
            cjk_hit = bool(CJK_RE.search(text))

            log(f"\n[{pid}/{label}] act_L2={act_l2:.2f}  cjk={cjk_hit}")
            log(f"  AV: {text[:280]!r}")
            results[pid][label] = {
                "av_text": text,
                "act_l2": act_l2,
                "cjk_injection_failure": cjk_hit,
            }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(results, open(OUT_DIR / "av_comparison_v2.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'av_comparison_v2.json'}")
    log("AV-COMPARISON-V2 COMPLETE")


if __name__ == "__main__":
    main()
