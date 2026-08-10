#!/usr/bin/env python
"""Feasibility probe for a tiny (~135M) model on the Mac: (1) what do its outputs look like,
(2) is it coherent enough for meaningful interp work, (3) does the jlens tooling hook it +
does a logit-lens read show interpretable mid-layer tokens?"""
import sys, time
sys.path.insert(0, ".")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
DEVICE = "mps"
MID = "HuggingFaceTB/SmolLM2-135M-Instruct"

print(f"[load] {MID} ...", flush=True)
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MID)
hf = AutoModelForCausalLM.from_pretrained(MID, dtype=torch.float16).to(DEVICE).eval()
nparam = sum(p.numel() for p in hf.parameters())
print(f"       {nparam/1e6:.0f}M params, {hf.config.num_hidden_layers} layers, d={hf.config.hidden_size}, loaded in {time.time()-t0:.0f}s", flush=True)

# ---- 1. OUTPUT QUALITY: chat prompts across factual / reasoning / boundary ----
PROMPTS = [
    "What is the capital of France?",
    "If I have 3 apples and eat 1, how many are left? Answer with just the number.",
    "Write one sentence about why the sky is blue.",
    "Who won the Nobel Prize in Physics in 2019?",   # boundary — does it hallucinate?
    "What is 17 times 4?",
]
print("\n===== OUTPUTS (chat, greedy) =====", flush=True)
for p in PROMPTS:
    msgs = [{"role": "user", "content": p}]
    text = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    ids = tok(text, return_tensors="pt").input_ids.to(DEVICE)
    with torch.no_grad():
        out = hf.generate(ids, max_new_tokens=60, do_sample=False, pad_token_id=tok.eos_token_id)
    ans = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()
    print(f"\nQ: {p}\nA: {ans}", flush=True)

# ---- 2. jlens compatibility + 3. logit-lens read ----
print("\n\n===== JLENS COMPATIBILITY =====", flush=True)
try:
    import jlens
    model = jlens.from_hf(hf, tok, force_bos=False)
    print(f"[jlens.from_hf] OK — wrapped {len(model.layers)} layers; unembed present: {hasattr(model,'unembed')}", flush=True)
    # logit-lens: project each layer's residual at the last token through the unembed
    from jlens.hooks import ActivationRecorder
    probe = "The capital of Japan is"
    pids = tok(probe, return_tensors="pt")["input_ids"].to(DEVICE)
    band = list(range(0, hf.config.num_hidden_layers, max(1, hf.config.num_hidden_layers // 8)))
    with torch.no_grad(), ActivationRecorder(model.layers, at=band) as rec:
        hf.model(input_ids=pids, use_cache=False)
        acts = {l: rec.activations[l][0].detach() for l in band}
    print(f"\n[logit-lens] prompt={probe!r}  — top-5 next-token per layer at final position:", flush=True)
    for l in band:
        h = acts[l][-1].float().unsqueeze(0)
        logits = model.unembed(h).float()
        top = logits.topk(5, dim=-1)
        toks = [tok.decode([int(t)]).strip() for t in top.indices[0]]
        print(f"   L{l:2}: {toks}", flush=True)
    print("\n[verdict] logit-lens works out of the box; a Jacobian lens would need a fitting run (jlens.fitting).", flush=True)
except Exception as e:
    import traceback; traceback.print_exc()
    print(f"\n[jlens] FAILED: {e}", flush=True)
print("\n[done]", flush=True)
