#!/usr/bin/env python
"""First J-space injection test (user's 'no number under 1000 has an a' problem).

The 4B's natural failure here is enumerate-forever; the MISSING kernel is the meta-move
"there are none / impossible". We inject that concept's J-lens direction into the workspace
band during generation and ask whether it flips the answer to 'none'.

Injection (paper's verbal-introspection recipe): steer_l = alpha * mean_resid_norm_l * unit(v_l),
where v_l = (W_U[token] @ J_l) is the token's J-lens direction at layer l; added to the residual
at every band layer, every position, throughout generation.

Controls (mandatory, EXPERIMENTATION_GUIDELINES.md §2):
  - baseline (alpha=0): confirm it fails.
  - random-vector injection, 3 seeds, norm-matched: a positive is only real if random DOESN'T do it.
  - alpha sweep: the knife-edge lesson (F171/F173).
Saves every full trace. Greedy throughout (causal read, §4).
"""
import json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.lens import JacobianLens
from workspace_common import BAND, LENS_PATH, lens_vectors, single_token_id

DEVICE = "mps"
OUT = "results/workspace/inject_none_test.json"
QUESTION = (
    "Is there a positive whole number less than 1000 whose English spelling contains the "
    "letter 'a'? Do not count the word 'and'. If such a number exists, give the smallest one. "
    "If no such number exists, say so.\n"
    "Reason step by step, then give your final answer in \\boxed{}."
)
# alpha is the FRACTION of the residual norm added (F171 knife-edge: at alpha>~1.5 the
# injection overwrites the computation and just spams the token; the useful nudge window
# is well below the residual norm). First run used alpha=4-20 -> destructive; corrected.
# PROMPT-ONLY injection: concept loaded into the workspace while reading the question,
# then released so the model reasons freely. Wider alpha range OK now (no per-token clamp).
CONCEPTS = ["none", "impossible"]     # kernel candidates to inject
ALPHAS = [0.5, 1.0, 2.0, 4.0, 8.0]
RANDOM_ALPHAS = [1.0, 4.0]
MAX_NEW = 1024


def build_prompt(tok):
    m = [{"role": "user", "content": QUESTION}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False,
                                       enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


class AddHook:
    """Adds steer[l] to each band layer's residual — PROMPT POSITIONS ONLY.

    With KV cache, the prompt is processed in one forward (seq_len > 1) and each generated
    token in its own forward (seq_len == 1). Gating on seq_len > 1 injects the concept only
    while the model READS the question (loads it into the workspace), then releases so the
    model reasons/answers freely. This is the incubation setup, and it avoids clamping the
    output to the injected token (RUN1/RUN2 all-token injection just spammed the word)."""
    def __init__(self, model, steer, band, prompt_only=True):
        self.handles = []
        for l in band:
            v = steer[l].to(DEVICE, dtype=torch.float16)

            def hook(mod, inp, out, v=v):
                t = out[0] if isinstance(out, tuple) else out
                if prompt_only and t.shape[1] == 1:  # a single generated token -> no inject
                    return out
                t = t + v
                return (t,) + out[1:] if isinstance(out, tuple) else t
            self.handles.append(model.layers[l].register_forward_hook(hook))

    def __enter__(self):
        return self

    def __exit__(self, *a):
        for h in self.handles:
            h.remove()


@torch.no_grad()
def generate(hf, tok, prompt, steer=None, band=None, model=None):
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
    ctx = AddHook(model, steer, band) if steer is not None else _Null()
    with ctx:
        o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                        max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)


class _Null:
    def __enter__(self): return self
    def __exit__(self, *a): pass


def classify(text):
    """correct = REASONS to none exist; wrong = names a number; degenerate = token spam
    (injection hijacked generation — NOT a real solve); unclear otherwise."""
    import re
    # spam detection: a single word repeated many times = injection overwrote generation
    words = text.split()
    if len(words) >= 12:
        from collections import Counter
        top, cnt = Counter(words).most_common(1)[0]
        if cnt / len(words) > 0.5:
            return f"degenerate(spam:{top})", text[:60]
    m = re.findall(r"\\boxed\{([^}]*)\}", text)
    ans = m[-1].strip().lower() if m else text[-120:].lower()
    reasoned = len(text) > 200  # a real solve has an actual reasoning trace
    if any(w in ans for w in ("none", "no such", "does not exist", "doesn't exist",
                              "no number", "impossible", "zero")):
        return ("correct(none)" if reasoned else "correct(none)?thin"), ans[:60]
    if re.search(r"\d", ans) or any(w in ans for w in
                                    ("one", "two", "three", "hundred", "thousand")):
        return "wrong(number)", ans[:60]
    return "unclear", ans[:60]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]
    prompt = build_prompt(tok)
    print(f"[load] lens n={lens.n_prompts}, band={band}", flush=True)

    # per-band-layer mean residual norm (for paper-style scaling)
    from jlens.hooks import ActivationRecorder
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
    with ActivationRecorder(model.layers, at=band) as rec, torch.no_grad():
        hf.model(input_ids=ids, use_cache=False)
        mean_norm = {l: rec.activations[l][0].float().norm(dim=-1).mean().item() for l in band}
    print("[norms]", {l: round(mean_norm[l], 1) for l in band}, flush=True)

    results = {"question": QUESTION, "gold": "none", "lens_n": lens.n_prompts, "band": band,
               "runs": []}

    def record(label, text):
        cls, ans = classify(text)
        results["runs"].append({"label": label, "class": cls, "answer": ans,
                                "trace_len": len(text), "trace": text})
        print(f"  {label:22} -> {cls:15} | {ans}", flush=True)
        json.dump(results, open(OUT, "w"), indent=1)

    # 1) baseline
    print("[baseline]", flush=True)
    record("baseline", generate(hf, tok, prompt, model=model))

    # 2) concept injections, alpha sweep
    for concept in CONCEPTS:
        tid = single_token_id(tok, concept)
        if tid is None:
            print(f"  (skip {concept}: not single-token)", flush=True)
            continue
        vecs = lens_vectors(lens, model, [tid], band)  # {l: [1, d]}
        unit = {l: vecs[l][0] / (vecs[l][0].norm() + 1e-8) for l in band}
        for a in ALPHAS:
            steer = {l: (a * mean_norm[l] * unit[l]) for l in band}
            record(f"inject:{concept}@a{a}", generate(hf, tok, prompt, steer, band, model))

    # 3) random-vector control (norm-matched), per random alpha x 2 seeds
    for a in RANDOM_ALPHAS:
        for seed in range(2):
            g = torch.Generator().manual_seed(1000 + seed)
            steer = {}
            for l in band:
                r = torch.randn(model.d_model, generator=g)
                steer[l] = a * mean_norm[l] * (r / r.norm())
            record(f"random@a{a}#s{seed}", generate(hf, tok, prompt, steer, band, model))

    results["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(results, open(OUT, "w"), indent=1)
    print(f"[done] {results['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
