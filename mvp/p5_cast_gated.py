"""Phase 5 — CAST-style conditional gating test on E2.

F129 result: blanket additive steering with v_humility at qwen2.5-7b L20 doesn't
install humility behavior. But CAST (Lee et al. 2024) argues steering should be
CONDITIONAL — only fire when the model is in a state that needs the nudge.

This script implements per-token gated steering at L20:
  - Hook intercepts L20 residual stream during generation.
  - For each token position, compute cos(h_t, v_humility_normalized).
  - If cos < τ (model is FAR from humility direction → needs nudge): add α·v̂.
  - Else: passthrough.

Two gate-polarity conditions tested:
  (a) gate_when_low: inject when model is far from humility (push it toward).
  (b) gate_when_high: inject when model is already near humility (amplify).

Compared against:
  - α=0 baseline (no steering)
  - F129 blanket steering at same α (already have data, re-run for direct comparison)

If gated steering fires the canaries that blanket steering missed → CAST resurrects
the operational path; F121 weakens to "blanket steering is one-sided, gated is two-sided."
If gated also fails → F121 further solidifies; the limit isn't gating either.
"""
import json, time
from pathlib import Path
import torch
import numpy as np
import pyarrow.parquet as pq
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import load_model, generate_response

EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase5_cast_gated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LAYER = 20
ALPHAS = [+3.0, +5.0, +8.0]
TAUS = [0.02, 0.05, 0.10]  # cosine threshold for gating
PROMPTS = ["E1-confabulation", "E2-contested-science"]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


class GatedSteeringHook:
    """Per-token cosine-gated additive steering at a chosen layer."""
    def __init__(self, layer_idx: int, direction: np.ndarray, alpha: float,
                 tau: float, gate_polarity: str = "low"):
        """
        gate_polarity:
          "low"  → inject when cos(h_t, v) < tau (model far from v, push toward)
          "high" → inject when cos(h_t, v) > tau (model near v, amplify)
        """
        self.layer_idx = layer_idx
        v = torch.as_tensor(direction, dtype=torch.float32)
        self.v_hat = (v / (v.norm() + 1e-9))
        self.alpha = alpha
        self.tau = tau
        self.polarity = gate_polarity
        self.handle = None
        # diagnostic counters
        self.fired_steps = 0
        self.total_steps = 0
        self.cos_history = []

    def _hook(self, module, inputs, output):
        if isinstance(output, tuple):
            h = output[0]
        else:
            h = output
        # h shape: [B, T, d]
        B, T, d = h.shape
        v_hat = self.v_hat.to(h.device).to(h.dtype)
        # cosine for each token position
        h_flat = h.reshape(-1, d)
        h_norm = h_flat.norm(dim=-1, keepdim=True).clamp_min(1e-9)
        cos_t = (h_flat @ v_hat) / h_norm.squeeze(-1)  # [B*T]
        if self.polarity == "low":
            mask = (cos_t < self.tau).to(h.dtype)
        else:
            mask = (cos_t > self.tau).to(h.dtype)
        # broadcast mask: [B*T, 1] * [d]
        delta = self.alpha * mask.unsqueeze(-1) * v_hat.unsqueeze(0)
        h_new = h_flat + delta
        h_new = h_new.reshape(B, T, d)
        # diagnostics (only count last position, the new generated token)
        self.total_steps += B
        self.fired_steps += int(mask.reshape(B, T)[:, -1].sum().item())
        self.cos_history.append(float(cos_t.reshape(B, T)[:, -1].mean().item()))
        if isinstance(output, tuple):
            return (h_new,) + output[1:]
        return h_new

    def attach(self, model):
        layer = model.model.layers[self.layer_idx]
        self.handle = layer.register_forward_hook(self._hook)

    def detach(self):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None

    def fire_rate(self):
        return self.fired_steps / max(1, self.total_steps)


def main():
    log("Loading qwen2.5-7b-it...")
    model, tok, device = load_model("qwen2.5-7b-it")

    arith = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    v_hum = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                     dtype=np.float32)
    log(f"  v_humility shape={v_hum.shape}, L2-norm={np.linalg.norm(v_hum):.2f}")

    eval_prompts = json.load(open(Path.home() / "phronesis_run" / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    prompts = [p for p in eval_prompts if p["id"] in PROMPTS]

    all_results = []
    for prompt_obj in prompts:
        pid = prompt_obj["id"]
        prompt = prompt_obj["prompt"]
        cap = prompt_obj.get("max_new_tokens", 2048)
        log(f"\n=== {pid} (cap={cap}) ===")
        log(f"  prompt: {prompt[:100]}...")

        # Baseline
        log("\n  baseline (α=0)...")
        base = generate_response(model, tok, prompt, device, cap)
        log(f"    {len(base)} chars: ...{base[-200:]!r}")

        prompt_results = {
            "prompt_id": pid, "prompt": prompt,
            "baseline": {"response": base, "word_count": len(base.split())},
            "gated_steered": {}
        }

        for alpha in ALPHAS:
            for tau in TAUS:
                for polarity in ["low", "high"]:
                    key = f"a{alpha:+.1f}_t{tau:.2f}_g{polarity}"
                    log(f"\n  {key}...")
                    hook = GatedSteeringHook(LAYER, v_hum, alpha, tau, polarity)
                    hook.attach(model)
                    try:
                        resp = generate_response(model, tok, prompt, device, cap)
                    finally:
                        hook.detach()
                    fr = hook.fire_rate()
                    cos_mean = float(np.mean(hook.cos_history)) if hook.cos_history else 0.0
                    log(f"    fire_rate={fr:.2%}  cos_mean={cos_mean:+.4f}  {len(resp)} chars: ...{resp[-200:]!r}")
                    prompt_results["gated_steered"][key] = {
                        "alpha": alpha, "tau": tau, "polarity": polarity,
                        "fire_rate": fr, "cos_mean": cos_mean,
                        "response": resp, "word_count": len(resp.split()),
                    }
        all_results.append(prompt_results)

    out_file = OUT_DIR / "qwen25_L20_cast_gated.json"
    json.dump({"config": {"model": "qwen2.5-7b-it", "vector": "diff_v-nv_GLOBAL_MEAN_60",
                          "layer": LAYER, "alphas": ALPHAS, "taus": TAUS,
                          "polarities": ["low", "high"], "norm": float(np.linalg.norm(v_hum)),
                          "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
               "results": all_results}, open(out_file, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {out_file}")
    log("PHASE 5 COMPLETE")


if __name__ == "__main__":
    main()
