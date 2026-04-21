"""
Priority 2: aime/42 temperature-variance ensemble.

Tests the F95 claim that the L20_a8 and L20_a16 break of aime/42 (both → 49)
is driven by the explicit even/odd partition lemma in the reasoning trace,
not by stochastic exploration hitting the correct residue class.

Design:
  - 10 runs each at (L20, α=8) and (L20, α=16)
  - temperature=0.3, top_p=0.95
  - Different seed per run
  - AIME item 42 only, cap=24576
  - For each trace, extract whether the even/odd parity lemma appears in the
    first 8000 chars of the thinking trace.

Hypothesis: P(even/odd lemma | correct=49) > P(even/odd lemma | wrong)

Falsification: if correct-answer runs have NO correlation with lemma
presence, the attractor break is stochastic exploration, not lemma-driven.

Output:
  priority2_aime42_ensemble/L20_a8_seed{s}.json
  priority2_aime42_ensemble/L20_a16_seed{s}.json
"""
import argparse
import json
import time
import os
import re
from pathlib import Path
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "./models/Qwen3-4B"
VECTOR_PATH = "./results/vectors/qwen3-4b/triplets/last_token/layer_20_virtue_vector.npy"
LAYER = 20
OUT_DIR = Path("./priority2_aime42_ensemble")
OUT_DIR.mkdir(exist_ok=True)

# AIME 42 prompt — copy from hard_probe_v3 baseline to ensure exact match
SRC = Path("./results/benchmark_probe/hard_probe_v3/baseline/42.json")
_baseline = json.load(open(SRC))
PROMPT = _baseline["prompt"]
GOLD = _baseline["gold"]
MAX_NEW = 24576


class AdditiveHook:
    def __init__(self, model, layer_idx, v, alpha):
        vt = torch.tensor(v, dtype=torch.float32)
        self.v_unit = (vt / (vt.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.alpha = float(alpha)
        self.layer = model.model.layers[layer_idx]
        self.handle = None

    def _hook(self, mod, inp, out):
        hidden = out[0] if isinstance(out, tuple) else out
        v = self.v_unit.to(hidden.device).to(hidden.dtype)
        hidden = hidden + self.alpha * v
        if isinstance(out, tuple):
            return (hidden,) + out[1:]
        return hidden

    def attach(self):
        self.handle = self.layer.register_forward_hook(self._hook)

    def detach(self):
        if self.handle:
            self.handle.remove()
            self.handle = None


def detect_evenodd_lemma(thinking: str, head_chars: int = 8000) -> dict:
    """Look for the even/odd parity decomposition in the first head_chars of thinking."""
    head = thinking[:head_chars].lower()
    signals = {
        "case_all_even": bool(re.search(r"case.*all.*(three|3).*even|case 1.*even|all.*r2.*r4.*r6.*even", head)),
        "case_all_odd": bool(re.search(r"case.*all.*(three|3).*odd|all.*r2.*r4.*r6.*odd", head)),
        "case_mix_even_odd": bool(re.search(r"two.*even.*one.*odd|two.*odd.*one.*even|mixed.*parity", head)),
        "r2_r4_r6_parity": bool(re.search(r"(r2.*r4.*r6|r_2.*r_4.*r_6).*(parit|even|odd)", head)),
        "partition_into_cases": bool(re.search(r"(partition|split|divide).*(cases|sub.?cases).*(parity|even|odd)", head)),
        "c_3_2": bool(re.search(r"c\(3,\s*2\)|binomial.*3.*2|3 choose 2", head)),
    }
    signals["lemma_present"] = any(signals.values())
    return signals


def answer_parser(text: str) -> str | None:
    """Extract final integer answer from response. AIME answers are 000-999 but scorer accepts various forms."""
    # Look for boxed answer, final line, etc.
    m = re.search(r"\\boxed\{(\d{1,3})\}", text)
    if m:
        return str(int(m.group(1))).zfill(3)
    # Final "answer is X" patterns
    m = re.search(r"(?:answer|result)\s*(?:is)?\s*[:=]?\s*(\d{1,3})\b", text, re.IGNORECASE)
    if m:
        return str(int(m.group(1))).zfill(3)
    # Last integer in the answer
    nums = re.findall(r"\b\d{1,3}\b", text)
    if nums:
        return str(int(nums[-1])).zfill(3)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alphas", nargs="+", type=float, default=[8.0, 16.0])
    ap.add_argument("--runs-per-alpha", type=int, default=10)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--skip-existing", action="store_true", default=True)
    args = ap.parse_args()

    print(f"gold={GOLD}, prompt_len={len(PROMPT)}")
    print(f"alphas={args.alphas}, runs={args.runs_per_alpha}, T={args.temperature}")

    print("Loading Qwen3-4B (fp16 on cuda)...")
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, torch_dtype=torch.float16, device_map="cuda", trust_remote_code=True
    )
    model.eval()

    v = np.load(VECTOR_PATH)
    print(f"vector loaded: shape={v.shape}, norm={np.linalg.norm(v):.3f}")

    # Build chat-template input once
    messages = [{"role": "user", "content": PROMPT}]
    text_in = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    inputs = tok(text_in, return_tensors="pt").to("cuda")
    prompt_toks = inputs.input_ids.shape[1]
    print(f"prompt tokens: {prompt_toks}")

    for alpha in args.alphas:
        hook = AdditiveHook(model, LAYER, v, alpha)
        hook.attach()
        try:
            for seed in range(args.runs_per_alpha):
                out_path = OUT_DIR / f"L20_a{int(alpha)}_seed{seed}.json"
                if args.skip_existing and out_path.exists():
                    print(f"SKIP {out_path.name}")
                    continue
                print(f"\n=== alpha={alpha}, seed={seed} ===")
                torch.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                t0 = time.time()
                with torch.no_grad():
                    out = model.generate(
                        **inputs,
                        max_new_tokens=MAX_NEW,
                        do_sample=True,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        pad_token_id=tok.pad_token_id,
                    )
                dt = time.time() - t0
                gen_ids = out[0][prompt_toks:]
                n_gen = int(gen_ids.shape[0])
                full = tok.decode(gen_ids, skip_special_tokens=True)
                if "<think>" in full and "</think>" in full:
                    think = full.split("<think>", 1)[1].split("</think>", 1)[0]
                    ans = full.split("</think>", 1)[1].strip()
                elif "<think>" in full:
                    think = full.split("<think>", 1)[1]
                    ans = ""
                else:
                    think = ""
                    ans = full.strip()
                predicted = answer_parser(ans or full)
                correct = (predicted == GOLD) if predicted else False
                lemma = detect_evenodd_lemma(think)
                record = {
                    "alpha": alpha, "layer": LAYER, "seed": seed,
                    "temperature": args.temperature, "top_p": args.top_p,
                    "gen_seconds": dt, "n_gen_tokens": n_gen,
                    "predicted": predicted, "gold": GOLD, "correct": correct,
                    "cap_hit": n_gen >= MAX_NEW - 1,
                    "lemma_signals": lemma,
                    "response_thinking": think,
                    "response_answer": ans,
                }
                json.dump(record, open(out_path, "w"), indent=2)
                print(f"  t={dt:.0f}s, gen_tok={n_gen}, predicted={predicted}, correct={correct}, lemma={lemma['lemma_present']}, cap_hit={record['cap_hit']}")
        finally:
            hook.detach()

    print("\n=== DONE ===")
    # Roll-up summary
    rows = []
    for f in sorted(OUT_DIR.glob("*.json")):
        j = json.load(open(f))
        rows.append((j["alpha"], j["seed"], j["correct"], j["lemma_signals"]["lemma_present"], j["gen_seconds"], j["cap_hit"]))
    print(f"{'alpha':>6} {'seed':>4} {'correct':>7} {'lemma':>5} {'sec':>5} {'cap':>3}")
    for r in rows:
        print(f"{r[0]:>6.0f} {r[1]:>4} {str(r[2]):>7} {str(r[3]):>5} {r[4]:>5.0f} {str(r[5]):>3}")


if __name__ == "__main__":
    main()
