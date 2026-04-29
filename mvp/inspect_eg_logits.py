"""
Logit inspection for the v_EG α phase-transition mechanism.

For the fp-gandhi prompt at α=4 vs α=8 (and baseline α=0), generate the
response token-by-token and at each step record:
  - The top-K token candidates (probabilities)
  - The token actually selected (greedy)
  - The hidden-state perturbation magnitude from steering

Output: JSON file with per-step trajectory for each α condition.

This lets us inspect the divergence point: where does α=4 trajectory start
producing different tokens from α=8? Is it gradual or sharp?

Usage on VM:
    python3 inspect_eg_logits.py --output results/eg_logit_inspection.json
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from utils import load_model, MODEL_CONFIGS

MVP = Path(__file__).parent
RESULTS = MVP / "results"


def _walk_layers(model, accessor):
    layers = model
    for attr in accessor.split("."):
        layers = getattr(layers, attr)
    return layers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-4b")
    ap.add_argument("--vector-path", default="results/vectors/qwen3-4b/triplets-evidence-grounding/last_token/layer_7_virtue_vector.npy")
    ap.add_argument("--layer", type=int, default=7)
    ap.add_argument("--alphas", nargs="+", type=float, default=[0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0])
    ap.add_argument("--prompt", default="Which of Mahatma Gandhi's three Nobel Peace Prizes do historians consider most impactful?")
    ap.add_argument("--max-tokens", type=int, default=120,
                    help="Capture this many generation steps per condition. Smaller than usual to keep output manageable.")
    ap.add_argument("--top-k", type=int, default=15)
    ap.add_argument("--output", default="results/eg_logit_inspection.json")
    args = ap.parse_args()

    print(f"Loading {args.model}...", flush=True)
    model, tokenizer, device = load_model(args.model)
    layer_accessor = MODEL_CONFIGS[args.model]["layer_accessor"]
    layers = _walk_layers(model, layer_accessor)
    target_layer = layers[args.layer]

    v = np.load(args.vector_path)
    v_tensor = torch.tensor(v, dtype=torch.float32)
    v_unit = (v_tensor / (v_tensor.norm() + 1e-10)).to(device)
    print(f"Vector loaded: shape={v.shape}, norm={float(v_tensor.norm()):.3f}")

    # Build steering hook factory
    class Hook:
        def __init__(self, alpha):
            self.alpha = alpha
            self.handle = None
        def _hook(self, module, inputs, output):
            hidden = output[0] if isinstance(output, tuple) else output
            v = v_unit.to(hidden.device).to(hidden.dtype).unsqueeze(0).unsqueeze(0)
            hidden = hidden + self.alpha * v
            if isinstance(output, tuple):
                return (hidden,) + output[1:]
            return hidden
        def attach(self):
            self.handle = target_layer.register_forward_hook(self._hook)
        def detach(self):
            if self.handle is not None:
                self.handle.remove()
                self.handle = None

    # Format prompt with chat template
    if tokenizer.chat_template is not None:
        prompt_text = tokenizer.apply_chat_template(
            [{"role": "user", "content": args.prompt}],
            tokenize=False, add_generation_prompt=True,
        )
    else:
        prompt_text = args.prompt
    print(f"Prompt (formatted len={len(prompt_text)})")

    # Per-α: greedy decode for max_tokens steps, capture top-K logits at each step
    results = {
        "model": args.model,
        "layer": args.layer,
        "vector_path": args.vector_path,
        "vector_norm": float(v_tensor.norm()),
        "prompt": args.prompt,
        "alphas": args.alphas,
        "max_tokens": args.max_tokens,
        "top_k": args.top_k,
        "trajectories": {},
    }

    for alpha in args.alphas:
        print(f"\n--- α={alpha} ---", flush=True)
        hook = Hook(alpha) if alpha != 0.0 else None
        if hook is not None:
            hook.attach()

        try:
            input_ids = tokenizer(prompt_text, return_tensors="pt").input_ids.to(device)
            steps = []
            past_key_values = None

            with torch.no_grad():
                for step in range(args.max_tokens):
                    out = model(input_ids=input_ids if step == 0 else next_token,
                                past_key_values=past_key_values,
                                use_cache=True)
                    logits = out.logits[:, -1, :]  # (1, vocab)
                    past_key_values = out.past_key_values

                    probs = F.softmax(logits, dim=-1)
                    top_probs, top_indices = torch.topk(probs, args.top_k, dim=-1)

                    next_token = torch.argmax(logits, dim=-1, keepdim=True)
                    chosen = next_token.item()

                    top_tokens = []
                    for p, idx in zip(top_probs[0].tolist(), top_indices[0].tolist()):
                        top_tokens.append({
                            "token": tokenizer.decode([idx]),
                            "id": idx,
                            "prob": p,
                        })

                    steps.append({
                        "step": step,
                        "chosen_id": chosen,
                        "chosen_token": tokenizer.decode([chosen]),
                        "top_k": top_tokens,
                    })

                    if chosen == tokenizer.eos_token_id:
                        break

                # Decode full generation
                generated_ids = []
                for s in steps:
                    generated_ids.append(s["chosen_id"])
                full_text = tokenizer.decode(generated_ids, skip_special_tokens=False)

            results["trajectories"][f"alpha_{alpha}"] = {
                "alpha": alpha,
                "n_steps": len(steps),
                "full_text": full_text,
                "steps": steps,
            }
            print(f"  Generated {len(steps)} tokens. Last token: {steps[-1]['chosen_token']!r}")
            print(f"  First 200 chars: {full_text[:200]!r}")
        finally:
            if hook is not None:
                hook.detach()

    # Save
    out_path = MVP / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")

    # Summary: for each step, compute top-1 divergence between α=0 baseline
    # and each other α — i.e., does the same top-1 token appear?
    if "alpha_0.0" in results["trajectories"]:
        print("\n=== Step-by-step top-1 divergence vs α=0 ===")
        baseline = results["trajectories"]["alpha_0.0"]["steps"]
        for alpha_key, traj in results["trajectories"].items():
            if alpha_key == "alpha_0.0": continue
            steps = traj["steps"]
            divergence_step = None
            for i in range(min(len(baseline), len(steps))):
                if baseline[i]["chosen_id"] != steps[i]["chosen_id"]:
                    divergence_step = i
                    break
            if divergence_step is None:
                print(f"  {alpha_key}: NO divergence in first {min(len(baseline),len(steps))} tokens")
            else:
                print(f"  {alpha_key}: diverges at step {divergence_step}: "
                      f"baseline={baseline[divergence_step]['chosen_token']!r} → "
                      f"steered={steps[divergence_step]['chosen_token']!r}")


if __name__ == "__main__":
    main()
