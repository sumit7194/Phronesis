#!/usr/bin/env python
"""Smoke test for the overnight workspace run: does jlens work on Qwen3-4B fp16/MPS,
and how expensive is one Jacobian prompt? Writes results/workspace/smoke.json with
per-backward-pass timing so the overnight driver can budget prompt count."""
import json, math, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder

OUT = os.path.join(os.path.dirname(__file__), "results/workspace/smoke.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    report = {"ok": False}
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", torch_dtype=torch.float16).to("mps").eval()
    model = jlens.from_hf(hf, tok)
    report["load_s"] = round(time.time() - t0, 1)
    report["n_layers"] = model.n_layers
    report["d_model"] = model.d_model
    log(f"loaded: n_layers={model.n_layers} d_model={model.d_model} in {report['load_s']}s")

    # 1) forward + logit-lens readout sanity (no jacobian)
    prompt = "Fact: The capital of France is the city of"
    dummy = jlens.JacobianLens(
        jacobians={model.n_layers - 2: torch.eye(model.d_model)},
        n_prompts=1, d_model=model.d_model)
    lens_logits, model_logits, ids = dummy.apply(model, prompt, layers=[model.n_layers - 2],
                                                 positions=[-1], use_jacobian=False)
    top_model = tok.decode(model_logits[0].argmax().item())
    report["greedy_next"] = top_model
    log(f"greedy next token: {top_model!r}")

    # 2) time backward passes for the Jacobian estimator (the fit cost driver)
    source_layers = list(range(4, model.n_layers - 2, 2))  # band for the overnight fit
    text = ("The history of science is a story of careful observation and bold guesses. "
            "Researchers measure, argue, revise, and slowly build instruments that let "
            "them see further than their predecessors ever could. Every generation "
            "inherits both the knowledge and the blind spots of the one before it, and "
            "progress often comes from questioning what everyone had assumed was settled.")
    for dim_batch in (8, 4, 2):
        try:
            input_ids = model.encode(text, max_length=128)
            seq_len = input_ids.shape[1]
            with ActivationRecorder(model.layers, at=[*source_layers, model.n_layers - 1],
                                    start_graph_at=min(source_layers)) as rec, torch.enable_grad():
                t_fwd = time.time()
                model.forward(input_ids.expand(dim_batch, -1))
                torch.mps.synchronize()
                fwd_s = time.time() - t_fwd
                target = rec.activations[model.n_layers - 1]
                sources = [rec.activations[l] for l in source_layers]
                cot = torch.zeros_like(target)
                n_timed = 6
                t_bwd = time.time()
                grads_ok = True
                for p in range(n_timed):
                    cot.zero_()
                    for b in range(dim_batch):
                        cot[b, 16:seq_len - 1, p * dim_batch + b] = 1.0
                    grads = torch.autograd.grad(target, sources, grad_outputs=cot, retain_graph=True)
                    if any(not torch.isfinite(g).all() for g in grads):
                        grads_ok = False
                    del grads
                torch.mps.synchronize()
                bwd_s = (time.time() - t_bwd) / n_timed
            n_passes = math.ceil(model.d_model / dim_batch)
            per_prompt_s = fwd_s + n_passes * bwd_s
            alloc_gb = torch.mps.current_allocated_memory() / 1e9
            report[f"dim_batch_{dim_batch}"] = {
                "fwd_s": round(fwd_s, 2), "bwd_s_per_pass": round(bwd_s, 3),
                "n_passes": n_passes, "est_per_prompt_s": round(per_prompt_s, 1),
                "grads_finite": grads_ok, "mps_alloc_gb": round(alloc_gb, 2),
            }
            log(f"dim_batch={dim_batch}: fwd={fwd_s:.2f}s bwd/pass={bwd_s:.3f}s "
                f"-> est {per_prompt_s / 60:.1f} min/prompt, finite={grads_ok}, alloc={alloc_gb:.2f}GB")
            report["chosen_dim_batch"] = dim_batch
            break  # first dim_batch that works wins
        except RuntimeError as e:
            log(f"dim_batch={dim_batch} failed: {e}")
            report[f"dim_batch_{dim_batch}"] = {"error": str(e)[:200]}
            torch.mps.empty_cache()

    report["source_layers"] = source_layers
    report["ok"] = "chosen_dim_batch" in report
    with open(OUT, "w") as f:
        json.dump(report, f, indent=2)
    log(f"smoke done ok={report['ok']}")

if __name__ == "__main__":
    main()
