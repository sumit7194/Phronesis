"""Run NLA AV on baseline vs DPO-adapted L20 activations — does DPO change what
the activation reads as?

F138/F139/F141 showed DPO produces a narrow E2-shift in OUTPUT TEXT. F142 showed
DPO moves activations along a non-v_diff direction at small magnitude. This script
asks the mechanistic question:

  Did DPO change what the activation REPRESENTS, or only how the model translates
  the activation to tokens downstream?

Run baseline + v2-DPO + multi-virtue-DPO on 3 prompts (E2, multivitamin, smoking).
Extract L20 last-token activations. Pass through the NLA AV. Compare the AV-decoded
text across baseline / DPO / multi-virtue.

  - If AV text differs between baseline and DPO → DPO changed the L20 representation
    and the AV reads it differently. The intervention reaches the activation level.
  - If AV text is identical → DPO didn't change what L20 represents; the
    behavioral shift (E2) came from downstream layers / token-selection only.

For the F121 + F142 architectural picture, this is the cleanest test of "did DPO
modify the representation, or only the readout?"
"""
import json, time
from pathlib import Path
import numpy as np
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import yaml

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
AV_REPO = "kitft/nla-qwen2.5-7b-L20-av"
ROOT = Path.home() / "phronesis_run"
OUT_DIR = ROOT / "mvp" / "results" / "av_on_dpo_activations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    ("E2-flossing", "Does flossing prevent cavities? What is your confidence level in this answer?"),
    ("ce-01-multivitamin", "Does taking a daily multivitamin extend lifespan in adults?"),
    ("ws-01-smoking", "Does smoking cigarettes cause lung cancer?"),
    ("oc-08-power-poses", "Does adopting a power pose for 2 minutes change hormone levels and behavior?"),
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def get_l20_act(model, tok, prompt):
    """L20 last-token activation."""
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    return out.hidden_states[20][0, -1, :].float().cpu().numpy()


def av_generate(av_model, av_tok, activation, av_meta):
    """Use AV to verbalize an activation via injection at the activation slot."""
    # Per NLA paper: AV uses activation injection at a specific char slot
    # Find the slot index from av_meta
    template = av_meta["prompt_templates"]["av"]
    inj_char = av_meta["extraction"].get("injection_char", "X")
    target_norm = av_meta["extraction"].get("activation_norm", 150.0)

    # Format prompt with the injection-char placeholder
    prompt_text = template
    ids = av_tok(prompt_text, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
    # Find the injection position (the position of the special character in the template tokens)
    char_ids = av_tok.encode(inj_char, add_special_tokens=False)
    # Find char_ids[0] inside ids
    target_token_id = char_ids[0] if char_ids else None
    if target_token_id is None:
        log(f"  WARN: could not encode inj_char {inj_char!r}, using last position")
        inj_pos = ids.shape[1] - 1
    else:
        positions = (ids[0] == target_token_id).nonzero(as_tuple=True)[0]
        if len(positions) == 0:
            log(f"  WARN: inj_char token not found in template, using last position")
            inj_pos = ids.shape[1] - 1
        else:
            inj_pos = positions[-1].item()

    # Rescale activation to target_norm
    act_t = torch.as_tensor(activation, dtype=torch.bfloat16, device="cuda")
    act_t = act_t / (act_t.norm() + 1e-9) * target_norm

    # Hook the embedding output to replace at inj_pos
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
    log("Loading subject model (Qwen2.5-7B-Instruct)...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    # 1. Extract baseline activations
    log("\n=== Extracting baseline L20 activations ===")
    base_acts = {}
    for pid, prompt in PROMPTS:
        a = get_l20_act(base, tok, prompt)
        base_acts[pid] = a
        log(f"  [{pid}] L2 = {np.linalg.norm(a):.2f}")

    # 2. Extract v2-DPO activations
    v2_adapter = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
    log(f"\n=== Extracting v2-DPO L20 activations ===")
    model = PeftModel.from_pretrained(base, str(v2_adapter))
    model.eval()
    v2_acts = {}
    for pid, prompt in PROMPTS:
        a = get_l20_act(model, tok, prompt)
        v2_acts[pid] = a
        log(f"  [{pid}] L2 = {np.linalg.norm(a):.2f}")
    model = model.unload()
    del model
    torch.cuda.empty_cache()

    # 3. Multi-virtue activations
    mv_adapter = ROOT / "mvp" / "results" / "phase2a_multivirtue_dpo" / "adapter"
    log(f"\n=== Extracting multi-virtue DPO L20 activations ===")
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()
    model = PeftModel.from_pretrained(base, str(mv_adapter))
    model.eval()
    mv_acts = {}
    for pid, prompt in PROMPTS:
        a = get_l20_act(model, tok, prompt)
        mv_acts[pid] = a
        log(f"  [{pid}] L2 = {np.linalg.norm(a):.2f}")
    del model
    del base
    torch.cuda.empty_cache()

    # 4. Load NLA AV
    log(f"\n=== Loading NLA AV from {AV_REPO} ===")
    av_path = snapshot_download(AV_REPO)
    av_meta = yaml.safe_load(open(f"{av_path}/nla_meta.yaml"))
    log(f"  AV meta: injection_char={av_meta['extraction'].get('injection_char')}  "
        f"activation_norm={av_meta['extraction'].get('activation_norm')}")

    av_tok = AutoTokenizer.from_pretrained(av_path)
    av_model = AutoModelForCausalLM.from_pretrained(av_path, torch_dtype=torch.bfloat16, device_map="cuda")
    av_model.eval()

    # 5. Verbalize each activation
    log(f"\n=== AV verbalization on each (baseline, v2, multivirtue) × prompt ===")
    results = {}
    for pid, prompt in PROMPTS:
        results[pid] = {"prompt": prompt}
        for label, acts in [("baseline", base_acts), ("v2_DPO", v2_acts), ("multivirtue_DPO", mv_acts)]:
            log(f"\n  [{pid}] {label}...")
            text = av_generate(av_model, av_tok, acts[pid], av_meta)
            results[pid][label] = {"av_text": text, "act_l2": float(np.linalg.norm(acts[pid]))}
            log(f"    {text[:250]!r}")

    json.dump(results, open(OUT_DIR / "av_on_dpo_activations.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT_DIR / 'av_on_dpo_activations.json'}")
    log("AV-ON-DPO-ACTIVATIONS COMPLETE")


if __name__ == "__main__":
    main()
