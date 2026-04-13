"""
Phronesis — Weight Surgery Experiment

Bakes the calibrated-confidence virtue vector directly into the model's
weight matrices at the target layer. Instead of runtime steering hooks,
this permanently modifies the residual stream projection.

Approach: Add a rank-1 update to the output projection of the target layer:
  W_new = W_old + alpha * v_out ⊗ v_in

Where v is the virtue vector (normalized), applied as a bias to the layer's
output projection so that the residual stream is permanently shifted toward
the virtue direction after passing through that layer.

Simpler version: add a constant bias to the layer output.
  bias_new = alpha * v_normalized

This is equivalent to additive steering but baked into the weights.

Usage:
    python weight_surgery.py --vector results/vectors/.../layer_13_virtue_vector.npy \
      --layer 13 --alpha 1.0 --output-dir models/gemma-2-2b-it-surgery
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

from utils import MODEL_CONFIGS, load_model


def apply_weight_surgery(model, layer_idx, virtue_vector, alpha, method="bias"):
    """
    Modify model weights to permanently encode the virtue direction.

    Methods:
      - bias: Add alpha * v_normalized as a bias to the layer output.
              Equivalent to permanent additive steering.
      - rank1: Add alpha * v ⊗ v^T to the output projection weights.
              Amplifies the virtue direction in the weight space.
      - scale: Scale the virtue direction in the residual stream by (1 + alpha).
              Amplifies existing signal rather than adding new signal.
    """
    v = torch.tensor(virtue_vector, dtype=torch.float32)
    v_norm = v / (v.norm() + 1e-10)

    layer = model.model.layers[layer_idx]

    if method == "bias":
        # Add a permanent bias to the layer's output
        # We hook into the MLP output projection (down_proj)
        mlp_down = layer.mlp.down_proj

        # If no bias exists, we modify the weight to include one
        # W*x + b -> W*x + b + alpha*v
        # Equivalent: add alpha*v to every output
        original_forward = layer.forward
        bias = (alpha * v_norm).to(next(model.parameters()).device)

        def biased_forward(*args, **kwargs):
            output = original_forward(*args, **kwargs)
            if isinstance(output, tuple):
                hidden = output[0]
                return (hidden + bias.to(hidden.dtype),) + output[1:]
            return output + bias.to(output.dtype)

        layer.forward = biased_forward
        return {"method": "bias", "alpha": alpha, "layer": layer_idx}

    elif method == "rank1":
        # Add rank-1 update: W_new = W_old + alpha * (v ⊗ v^T) / ||v||^2
        # This amplifies the virtue direction in the output projection
        mlp_down = layer.mlp.down_proj
        with torch.no_grad():
            v_dev = v_norm.to(mlp_down.weight.device).to(mlp_down.weight.dtype)
            # W is (out_dim, in_dim). We want to amplify the v direction in output space.
            # rank1 = alpha * v_out ⊗ v_in where v_in = v_out = v (same space for residual stream)
            # But down_proj maps from intermediate_dim to hidden_dim
            # Instead, modify the self_attn output projection
            o_proj = layer.self_attn.o_proj
            v_dev = v_norm.to(o_proj.weight.device).to(o_proj.weight.dtype)

            # Project v into the input space of o_proj to find what input direction maps to v
            # o_proj.weight is (hidden_dim, num_heads * head_dim)
            # v^T @ W gives the input direction that produces v in output
            v_in = torch.mv(o_proj.weight.t(), v_dev)
            v_in = v_in / (v_in.norm() + 1e-10)

            # Rank-1 update: amplify the v_out direction when v_in is activated
            update = alpha * torch.outer(v_dev, v_in)
            o_proj.weight.data += update

        return {"method": "rank1", "alpha": alpha, "layer": layer_idx}

    elif method == "scale":
        # Scale the virtue direction: project residual stream onto v, scale by (1+alpha), recompose
        original_forward = layer.forward
        v_dev = v_norm.to(next(model.parameters()).device)

        def scaled_forward(*args, **kwargs):
            output = original_forward(*args, **kwargs)
            if isinstance(output, tuple):
                hidden = output[0]
            else:
                hidden = output

            dtype = hidden.dtype
            v_d = v_dev.to(dtype)

            # Project onto virtue direction
            proj = (hidden * v_d).sum(dim=-1, keepdim=True)
            # Scale the projection
            hidden = hidden + alpha * proj * v_d

            if isinstance(output, tuple):
                return (hidden,) + output[1:]
            return hidden

        layer.forward = scaled_forward
        return {"method": "scale", "alpha": alpha, "layer": layer_idx}


def generate(model, tokenizer, prompt, device, max_tokens=256):
    """Generate a response."""
    messages = [{"role": "user", "content": prompt}]
    input_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_tokens, do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def main():
    parser = argparse.ArgumentParser(description="Phronesis Weight Surgery")
    parser.add_argument("--model", default="gemma-2-2b-it", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--vector", required=True, help="Path to .npy virtue vector")
    parser.add_argument("--layer", type=int, required=True)
    parser.add_argument("--alpha", type=float, nargs="+", default=[0.5, 1.0, 2.0, 5.0],
                        help="Alpha values to test")
    parser.add_argument("--method", default="all", choices=["bias", "rank1", "scale", "all"])
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    virtue_vector = np.load(args.vector)
    print(f"Virtue vector: {virtue_vector.shape} from {args.vector}")

    # Test prompts — mix of scientific reasoning and tricky questions
    test_prompts = [
        {
            "id": "logic-fallacy",
            "prompt": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?",
            "correct": "No — this is the fallacy of the undistributed middle",
        },
        {
            "id": "strawberry-r",
            "prompt": "How many r letters are in the word strawberry?",
            "correct": "3 (st-r-awbe-r-r-y)",
        },
        {
            "id": "weak-evidence",
            "prompt": "A study of 12 participants found that eating chocolate improved memory scores by 15% (p=0.048). Should schools start giving students chocolate before exams?",
            "correct": "No — tiny sample, barely significant p-value, single study",
        },
        {
            "id": "subgroup",
            "prompt": "A drug trial with 500 patients showed no overall benefit (p=0.45). But in the subgroup of 38 left-handed patients, the drug reduced symptoms by 60% (p=0.03). Is the drug effective for left-handed people?",
            "correct": "Unlikely — post-hoc subgroup, tiny n, multiple comparisons",
        },
        {
            "id": "confidence-test",
            "prompt": "Rate your confidence (0-100%) in this claim: 'The Earth revolves around the Sun.' Then rate your confidence in: 'Dark matter makes up 27% of the universe.' Explain why your confidence levels differ.",
            "correct": "Should show high confidence for first (~99%), moderate for second (~70-80%), with reasoning about evidence quality",
        },
    ]

    methods = ["bias", "rank1", "scale"] if args.method == "all" else [args.method]

    results = {
        "config": {
            "model": args.model,
            "vector": str(args.vector),
            "layer": args.layer,
            "alphas": args.alpha,
            "methods": methods,
            "timestamp": datetime.now().isoformat(),
        },
        "results": {}
    }

    # Generate baselines first (before any surgery)
    print(f"\n{'='*60}")
    print("Loading model and generating baselines...")
    print(f"{'='*60}")
    model, tokenizer, device = load_model(args.model)

    baselines = {}
    for tp in test_prompts:
        resp = generate(model, tokenizer, tp["prompt"], device)
        baselines[tp["id"]] = resp
        print(f"\n[{tp['id']}] {tp['prompt'][:80]}...")
        print(f"  BASELINE: {resp[:200]}...")

    results["baselines"] = {
        tp["id"]: {"prompt": tp["prompt"], "correct": tp["correct"], "response": baselines[tp["id"]]}
        for tp in test_prompts
    }

    # Try each surgery method × alpha
    for method in methods:
        results["results"][method] = {}

        for alpha in args.alpha:
            print(f"\n{'='*60}")
            print(f"Surgery: {method}, alpha={alpha}, layer={args.layer}")
            print(f"{'='*60}")

            # Reload model fresh for each experiment
            del model
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
            import gc; gc.collect()
            model, tokenizer, device = load_model(args.model)

            # Apply surgery
            info = apply_weight_surgery(model, args.layer, virtue_vector, alpha, method)
            print(f"Applied: {info}")

            alpha_results = {}
            for tp in test_prompts:
                resp = generate(model, tokenizer, tp["prompt"], device)
                alpha_results[tp["id"]] = resp

                # Show diff from baseline
                changed = resp != baselines[tp["id"]]
                marker = "CHANGED ✦" if changed else "same"
                print(f"\n  [{tp['id']}] ({marker})")
                if changed:
                    print(f"    BASE:    {baselines[tp['id']][:150]}...")
                    print(f"    SURGERY: {resp[:150]}...")
                else:
                    print(f"    {resp[:150]}...")

            results["results"][method][f"alpha_{alpha}"] = alpha_results

    # Save
    out_path = Path(args.output) if args.output else Path("results/weight_surgery_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
