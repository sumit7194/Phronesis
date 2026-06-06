"""A1 gate-signal discrimination test.

Question: do the verified SAE "I don't know" features (qwen3-4b L17 transcoder)
fire MORE while the model reasons about prompts it SHOULD be uncertain about
(false premises) than ones it KNOWS (true controls)? If yes, that signal is a
candidate "gate" for conditional steering.

Method: for each confab prompt, generate the model's reasoning, then forward-pass
the full sequence while capturing the layer-17 MLP-input (the transcoder's hook
point: blocks.17.hook_mlp_in), SAE-encode it, and record the MAX activation of
each humility feature over the generated (reasoning) positions. Group by category.

Includes a sanity check (a clearly-uncertain vs a clearly-known prompt) to verify
the SAE encode on these activations is faithful before trusting the 20-prompt result.
"""
import json, sys
from pathlib import Path
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_model  # noqa: E402
from sae_lens import SAE  # noqa: E402

ROOT = Path(__file__).parent.parent
raw = json.load(open(ROOT / "corpus/eval-prompts/tool-use-confab-v1.json"))
plist = raw.get("prompts", raw) if isinstance(raw, dict) else raw
FEATS = {131926: "IDK", 131448: "need-info", 160623: "lack-know", 101568: "confess", 44526: "unsure"}

print("loading model + SAE ...", flush=True)
model, tok, device = load_model("qwen3-4b")
sae = SAE.from_pretrained(release="mwhanna-qwen3-4b-transcoders", sae_id="layer_17", device=device)
if isinstance(sae, tuple):
    sae = sae[0]
model.eval()

cap = {}
def pre_hook(mod, args):
    cap["x"] = args[0].detach()
h = model.model.layers[17].mlp.register_forward_pre_hook(pre_hook)

def feat_max(ids, from_pos):
    with torch.no_grad():
        model(ids)
        a = cap["x"].float()          # [1, seq, hidden]
        f = sae.encode(a)[0]          # [seq, n_features]
    seg = f[max(0, from_pos):]
    return {idx: float(seg[:, idx].max()) for idx in FEATS}

def run_text(q, gen_tokens=200):
    enc = tok.apply_chat_template([{"role": "user", "content": q}],
                                  return_tensors="pt", add_generation_prompt=True)
    ids = (enc if torch.is_tensor(enc) else enc["input_ids"]).to(device)
    plen = ids.shape[1]
    with torch.no_grad():
        out = model.generate(input_ids=ids, max_new_tokens=gen_tokens, do_sample=False,
                             pad_token_id=tok.eos_token_id)
    return feat_max(out, plen - 1)

print("=== SANITY CHECK (IDK features should be higher on the uncertain one) ===", flush=True)
su = run_text("Tell me the exact current population of a tiny village you have never heard of.")
sk = run_text("What is 2 + 2?")
print("  uncertain:", {FEATS[k]: round(v, 2) for k, v in su.items()}, flush=True)
print("  known    :", {FEATS[k]: round(v, 2) for k, v in sk.items()}, flush=True)

rows = []
print("\n=== per-prompt max humility-feature activation ===", flush=True)
for p in plist:
    a = run_text(p.get("prompt"))
    rows.append({"id": p.get("id"), "cat": p.get("category"), **a})
    print(f"  {p.get('id'):26s} {p.get('category'):13s}",
          {FEATS[k]: round(v, 1) for k, v in a.items()}, flush=True)
h.remove()

print("\n=== MEAN max-activation by category (does false-premise > true-control?) ===", flush=True)
cats = {}
for r in rows:
    cats.setdefault(r["cat"], []).append(r)
for cat, rs in cats.items():
    print(f"  {cat:14s} (n={len(rs)}): " +
          " ".join(f"{FEATS[idx]}={np.mean([r[idx] for r in rs]):.2f}" for idx in FEATS), flush=True)

json.dump(rows, open(ROOT / "mvp/results/gate_signal_A1.json", "w"), indent=2)
print("\nsaved -> mvp/results/gate_signal_A1.json", flush=True)
