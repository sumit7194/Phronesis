"""Reversibility test: apply v2-DPO adapter + steer with v2-Δ at NEGATIVE α.
Does it UNDO the F138 E2 shift? Tests causality: if direction is the causal mechanism,
α=-10 should produce baseline-like behavior on the DPO-adapted model.
"""
import json, time
from pathlib import Path
import numpy as np
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
ROOT = Path.home() / "phronesis_run"
V2_ADAPTER = ROOT / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
D_V2 = ROOT / "mvp" / "results" / "all_deltas" / "d_v2_IH.npy"
OUT = ROOT / "mvp" / "results" / "all_deltas" / "reversibility.json"

E2 = "Does flossing prevent cavities? What is your confidence level in this answer?"
ALPHAS = [-25.0, -15.0, -10.0, -5.0, 0.0, +5.0, +10.0]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new=600):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        o = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                            pad_token_id=tok.eos_token_id)
    return tok.decode(o[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    d = np.load(D_V2).astype(np.float32)
    log(f"d_v2 L2={np.linalg.norm(d):.4f}")

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    log("Loading v2-DPO adapter on top of base...")
    model = PeftModel.from_pretrained(base, str(V2_ADAPTER))
    model.eval()

    log("v2-DPO model, no steering:")
    dpo_baseline_resp = gen(model, tok, E2)
    log(f"  {dpo_baseline_resp[-260:]!r}")

    results = {"dpo_baseline": dpo_baseline_resp, "steered": {}}
    # Find the right module to hook on (DPO model has model.model.layers via peft)
    # AdditiveSteeringHook expects model.model.layers[layer_idx] structure
    # Verify by traversing
    target = None
    if hasattr(model, "base_model"):
        target = model.base_model.model.model.layers[20]
    else:
        target = model.model.layers[20]
    log(f"Hooking target: {type(target).__name__}")

    class GenericHook:
        def __init__(self, direction, alpha):
            self.v = torch.as_tensor(direction, dtype=torch.float32)
            self.alpha = alpha
            self.handle = None
        def _hook(self, module, inputs, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            v = self.v.to(h.device).to(h.dtype)
            h_new = h + self.alpha * v
            if isinstance(output, tuple):
                return (h_new,) + output[1:]
            return h_new
        def attach(self, mod):
            self.handle = mod.register_forward_hook(self._hook)
        def detach(self):
            if self.handle:
                self.handle.remove()

    for a in ALPHAS:
        hook = GenericHook(d, a)
        hook.attach(target)
        try:
            r = gen(model, tok, E2)
        finally:
            hook.detach()
        results["steered"][f"{a:+.2f}"] = r
        log(f"\nα={a:+.1f} (on v2-DPO model): {r[-260:]!r}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(results, open(OUT, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {OUT}")
    log("REVERSIBILITY COMPLETE")


if __name__ == "__main__":
    main()
