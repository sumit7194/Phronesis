"""
Mini benchmark runner — streams output live like the chat UI.

Supports all 6 benchmarks (GSM8K, MMLU, TruthfulQA, HumbleBench, SycophancyEval,
XSTest). Pick a benchmark, a count N, and a condition (baseline or steered).
Each item streams token-by-token to stdout with <think>...</think> dimming.
At the end of each item: automatic scoring + running tally.

Usage:
    .venv/bin/python run_benchmark.py --benchmark gsm8k --n 3 --condition baseline
    .venv/bin/python run_benchmark.py --benchmark gsm8k --n 3 --condition steered
    .venv/bin/python run_benchmark.py --benchmark humblebench --n 2 --condition steered --vector L20 --alpha 12

    # run a probe across multiple benchmarks with small N each
    .venv/bin/python run_benchmark.py --probe --n 2 --condition steered
    # probe runs n items per benchmark for every benchmark in the registry

Outputs per-item JSONs under:
    mvp/results/benchmark_probe/{benchmark}/{condition}/{item_id}.json
Summary line appended to:
    mvp/results/benchmark_probe/summary.jsonl
"""
from __future__ import annotations

import argparse
import gc
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Thread

import numpy as np
import torch
from transformers import TextIteratorStreamer

from utils import load_model
from benchmarks import REGISTRY, ALL_LOADERS, BenchmarkItem
from benchmarks.scorers import SCORERS

# ─── Config ─────────────────────────────────────────────────────────────────

MVP = Path(__file__).parent
# Per-model vector roots + layer-accessor paths
MODEL_VECTOR_ROOTS = {
    "qwen3-4b":        MVP / "results" / "vectors" / "qwen3-4b",
    "gemma-4-E4B-it":  MVP / "results" / "vectors" / "gemma-4-E4B-it",
}
MODEL_LAYER_ACCESSORS = {
    "qwen3-4b":        "model.layers",
    "gemma-4-E4B-it":  "model.language_model.layers",  # multimodal wrapper
}
# Default model for back-compat
VECTOR_ROOT = MODEL_VECTOR_ROOTS["qwen3-4b"]
OUT_ROOT = MVP / "results" / "benchmark_probe"

# Per-model vector registries.
# Entry format: name -> (relative_path_from_model_vector_root, layer_idx)
VECTORS_BY_MODEL = {
    "qwen3-4b": {
        # Calibrated Confidence vectors (v_CC) from 50 hand-written triplets
        "L10":     ("triplets/last_token/layer_10_virtue_vector.npy", 10),
        "L20":     ("triplets/last_token/layer_20_virtue_vector.npy", 20),
        "L21":     ("triplets/last_token/layer_21_virtue_vector.npy", 21),
        "L22":     ("triplets/last_token/layer_22_virtue_vector.npy", 22),
        "L23":     ("triplets/last_token/layer_23_virtue_vector.npy", 23),
        "L27":     ("triplets/last_token/layer_27_virtue_vector.npy", 27),
        "son_L22": ("triplets-synthetic-sonnet/last_token/layer_22_virtue_vector.npy", 22),
        "son_L34": ("triplets-synthetic-sonnet/last_token/layer_34_virtue_vector.npy", 34),
        "random":  ("random_L22_vector.npy", 22),
        # Intellectual Humility vectors from 20 hand-written IH triplets
        "IH_L15":  ("triplets-intellectual-humility/last_token/layer_15_virtue_vector.npy", 15),
        "IH_L18":  ("triplets-intellectual-humility/last_token/layer_18_virtue_vector.npy", 18),
        "IH_L20":  ("triplets-intellectual-humility/last_token/layer_20_virtue_vector.npy", 20),
        "IH_L22":  ("triplets-intellectual-humility/last_token/layer_22_virtue_vector.npy", 22),
        "IH_L25":  ("triplets-intellectual-humility/last_token/layer_25_virtue_vector.npy", 25),
        # Evidence Grounding vectors from mvp-combined/triplets-evidence-grounding (40 triplets)
        # Populated after extract_v2.py --corpus ../corpus/mvp-combined/triplets-evidence-grounding
        "EG_L18":  ("triplets-evidence-grounding/last_token/layer_18_virtue_vector.npy", 18),
        "EG_L20":  ("triplets-evidence-grounding/last_token/layer_20_virtue_vector.npy", 20),
        "EG_L22":  ("triplets-evidence-grounding/last_token/layer_22_virtue_vector.npy", 22),
        "EG_L25":  ("triplets-evidence-grounding/last_token/layer_25_virtue_vector.npy", 25),
        # Reasoning Transparency vectors from mvp-combined/triplets-reasoning-transparency (40 triplets)
        "RT_L18":  ("triplets-reasoning-transparency/last_token/layer_18_virtue_vector.npy", 18),
        "RT_L20":  ("triplets-reasoning-transparency/last_token/layer_20_virtue_vector.npy", 20),
        "RT_L22":  ("triplets-reasoning-transparency/last_token/layer_22_virtue_vector.npy", 22),
        "RT_L25":  ("triplets-reasoning-transparency/last_token/layer_25_virtue_vector.npy", 25),
    },
    "gemma-4-E4B-it": {
        # Calibrated Confidence on Gemma — from 166 triplets-combined
        # Layer numbering adjusted: Qwen L20/L22 (middle-ish of 36) map roughly
        # to Gemma L22/L24 (middle-ish of 42)
        "CC_L18":  ("triplets-combined/last_token/layer_18_virtue_vector.npy", 18),
        "CC_L20":  ("triplets-combined/last_token/layer_20_virtue_vector.npy", 20),
        "CC_L22":  ("triplets-combined/last_token/layer_22_virtue_vector.npy", 22),
        "CC_L24":  ("triplets-combined/last_token/layer_24_virtue_vector.npy", 24),
        "CC_L26":  ("triplets-combined/last_token/layer_26_virtue_vector.npy", 26),
        "CC_L28":  ("triplets-combined/last_token/layer_28_virtue_vector.npy", 28),
        # Intellectual Humility on Gemma — from 20 IH triplets
        "IH_L18":  ("triplets-intellectual-humility/last_token/layer_18_virtue_vector.npy", 18),
        "IH_L20":  ("triplets-intellectual-humility/last_token/layer_20_virtue_vector.npy", 20),
        "IH_L22":  ("triplets-intellectual-humility/last_token/layer_22_virtue_vector.npy", 22),
        "IH_L24":  ("triplets-intellectual-humility/last_token/layer_24_virtue_vector.npy", 24),
        "IH_L26":  ("triplets-intellectual-humility/last_token/layer_26_virtue_vector.npy", 26),
        "IH_L28":  ("triplets-intellectual-humility/last_token/layer_28_virtue_vector.npy", 28),
        # Evidence Grounding on Gemma — from mvp-combined/triplets-evidence-grounding (40 triplets)
        "EG_L14":  ("triplets-evidence-grounding/last_token/layer_14_virtue_vector.npy", 14),
        "EG_L18":  ("triplets-evidence-grounding/last_token/layer_18_virtue_vector.npy", 18),
        "EG_L22":  ("triplets-evidence-grounding/last_token/layer_22_virtue_vector.npy", 22),
        "EG_L26":  ("triplets-evidence-grounding/last_token/layer_26_virtue_vector.npy", 26),
        # Reasoning Transparency on Gemma — from mvp-combined/triplets-reasoning-transparency (40 triplets)
        "RT_L14":  ("triplets-reasoning-transparency/last_token/layer_14_virtue_vector.npy", 14),
        "RT_L18":  ("triplets-reasoning-transparency/last_token/layer_18_virtue_vector.npy", 18),
        "RT_L22":  ("triplets-reasoning-transparency/last_token/layer_22_virtue_vector.npy", 22),
        "RT_L26":  ("triplets-reasoning-transparency/last_token/layer_26_virtue_vector.npy", 26),
    },
}
# Back-compat alias
VECTORS = VECTORS_BY_MODEL["qwen3-4b"]
DEFAULT_VECTOR = "L20"
DEFAULT_ALPHA  = 12.0

# ─── ANSI ───────────────────────────────────────────────────────────────────

DIM = "\033[2m"; BOLD = "\033[1m"; RESET = "\033[0m"
CYAN = "\033[36m"; GRAY = "\033[90m"; GREEN = "\033[32m"
RED = "\033[31m"; YELLOW = "\033[33m"


# ─── Steering hook (same as chat_ui / run_multivector) ──────────────────────

class AdditiveHook:
    def __init__(self, model, layer_idx, virtue_vector, alpha, layer_accessor="model.layers"):
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_unit = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.alpha = float(alpha)
        # Walk dotted accessor (e.g. "model.language_model.layers" for Gemma 4)
        layers = model
        for attr in layer_accessor.split("."):
            layers = getattr(layers, attr)
        self.layer = layers[layer_idx]
        self.handle = None

    def _hook(self, module, inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        v = self.v_unit.to(hidden.device).to(hidden.dtype)
        hidden = hidden + self.alpha * v
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def attach(self):
        self.handle = self.layer.register_forward_hook(self._hook)

    def detach(self):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


# ─── Think-aware streaming printer (reused from chat_ui) ────────────────────

class ThinkAwarePrinter:
    def __init__(self):
        self.in_think = False
        self.pending = ""

    def _emit(self, s):
        if self.in_think:
            sys.stdout.write(DIM + s + RESET)
        else:
            sys.stdout.write(s)
        sys.stdout.flush()

    def feed(self, chunk):
        buf = self.pending + chunk
        self.pending = ""
        while buf:
            if not self.in_think:
                idx = buf.find("<think>")
                if idx == -1:
                    if len(buf) > 8:
                        self._emit(buf[:-8]); self.pending = buf[-8:]
                    else:
                        self.pending = buf
                    return
                self._emit(buf[:idx])
                sys.stdout.write(GRAY + "<think>" + RESET); sys.stdout.flush()
                buf = buf[idx + 7:]; self.in_think = True
            else:
                idx = buf.find("</think>")
                if idx == -1:
                    if len(buf) > 9:
                        self._emit(buf[:-9]); self.pending = buf[-9:]
                    else:
                        self.pending = buf
                    return
                self._emit(buf[:idx])
                sys.stdout.write(GRAY + "</think>" + RESET); sys.stdout.flush()
                buf = buf[idx + 8:]; self.in_think = False

    def flush(self):
        if self.pending:
            self._emit(self.pending); self.pending = ""


# ─── Generation with streaming ──────────────────────────────────────────────

def generate_streaming(model, tokenizer, device, prompt, max_tokens, hook=None):
    """Generate with live streaming output. Returns result dict."""
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=False
    )

    if hook is not None:
        hook.attach()

    gen_kwargs = dict(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        streamer=streamer,
        max_new_tokens=max_tokens,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

    thread = Thread(target=model.generate, kwargs=gen_kwargs)
    t0 = time.time()
    thread.start()

    printer = ThinkAwarePrinter()
    buf = ""
    try:
        for chunk in streamer:
            for tok in ("<|im_end|>", "<|endoftext|>", "<|im_start|>"):
                chunk = chunk.replace(tok, "")
            buf += chunk
            printer.feed(chunk)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[interrupted]{RESET}", flush=True)
    finally:
        printer.flush()
        thread.join()
        if hook is not None:
            hook.detach()

    dt = time.time() - t0

    # Parse thinking/answer from the buffered raw text
    thinking, answer = "", buf.strip()
    m = re.search(r"<think>(.*?)</think>", buf, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        answer = buf.split("</think>", 1)[1].strip()
    for tok in ("<|im_end|>", "<|endoftext|>", "<|im_start|>"):
        answer = answer.replace(tok, "").strip()

    # Memory cleanup for MPS
    del streamer, thread, gen_kwargs, inputs, text
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.synchronize(); torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    return {
        "thinking": thinking,
        "answer": answer,
        "gen_seconds": round(dt, 2),
    }


# ─── Per-item runner ────────────────────────────────────────────────────────

def run_item(item: BenchmarkItem, model, tokenizer, device,
             condition: str, hook, out_dir: Path) -> dict:
    """Run one item; write per-cell JSON; return summary row."""
    out_file = out_dir / f"{item.item_id.replace('/','_')}.json"
    if out_file.exists():
        cached = json.load(open(out_file))
        print(f"{GRAY}[cached]{RESET} ", end="")
        return cached

    print(f"\n{CYAN}{'═'*72}{RESET}")
    print(f"{BOLD}{item.benchmark}[{condition}]  item {item.item_id}{RESET}  "
          f"(cap={item.max_tokens})")
    print(f"{GRAY}{item.prompt[:200]}{'...' if len(item.prompt)>200 else ''}{RESET}")
    print(f"{CYAN}{'─'*72}{RESET}")

    gen = generate_streaming(model, tokenizer, device, item.prompt,
                             item.max_tokens, hook=hook)

    # Score
    scorer = SCORERS[item.benchmark]
    verdict = scorer(item, gen)

    result = {
        "benchmark": item.benchmark,
        "item_id": item.item_id,
        "condition": condition,
        "prompt": item.prompt,
        "gold": item.gold,
        "response_thinking": gen["thinking"],
        "response_answer": gen["answer"],
        "gen_seconds": gen["gen_seconds"],
        "predicted": verdict.get("predicted"),
        "correct": verdict.get("correct"),
        "note": verdict.get("note"),
        "metadata": item.metadata,
        "timestamp": datetime.now().isoformat(),
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    mark = {True: f"{GREEN}✓ CORRECT{RESET}",
            False: f"{RED}✗ WRONG{RESET}",
            None: f"{YELLOW}? UNPARSED{RESET}"}[verdict.get("correct")]
    print(f"\n{mark}  predicted={verdict.get('predicted')}  "
          f"({gen['gen_seconds']:.1f}s)")
    print(f"{GRAY}{verdict.get('note','')}{RESET}")
    return result


# ─── CLI main ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", help="single benchmark name",
                    choices=list(ALL_LOADERS.keys()))
    ap.add_argument("--probe", action="store_true",
                    help="run across the default probe set (tier-A harder benchmarks)")
    ap.add_argument("--n", type=int, default=3, help="items per benchmark")
    ap.add_argument("--condition", default="baseline",
                    choices=["baseline", "steered"])
    ap.add_argument("--vector", default=DEFAULT_VECTOR)
    ap.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--label", default=None,
                    help="Output subdir name (default: --condition). Use to separate "
                         "multiple steered runs, e.g. 'steered_L22_a12'.")
    ap.add_argument("--model", default="qwen3-4b",
                    choices=list(MODEL_VECTOR_ROOTS.keys()),
                    help="Which model to load. Default qwen3-4b for backwards compat.")
    args = ap.parse_args()

    if not args.benchmark and not args.probe:
        ap.error("specify --benchmark NAME or --probe")

    vector_root = MODEL_VECTOR_ROOTS[args.model]
    layer_accessor = MODEL_LAYER_ACCESSORS[args.model]
    vectors_for_model = VECTORS_BY_MODEL[args.model]

    print(f"{BOLD}Loading {args.model}...{RESET}", flush=True)
    model, tokenizer, device = load_model(args.model)
    print(f"  on {device}", flush=True)

    hook = None
    if args.condition == "steered":
        if args.vector not in vectors_for_model:
            ap.error(f"vector '{args.vector}' not registered for model '{args.model}'. "
                     f"Available: {list(vectors_for_model.keys())}")
        rel, layer = vectors_for_model[args.vector]
        v = np.load(vector_root / rel)
        hook = AdditiveHook(model, layer, v, args.alpha, layer_accessor=layer_accessor)
        print(f"{CYAN}Steering ENABLED: vector={args.vector} layer={layer} "
              f"alpha={args.alpha:+g}{RESET}")
    else:
        print(f"{CYAN}Baseline (no steering){RESET}")

    # Pick benchmarks to run
    if args.benchmark:
        benches = [args.benchmark]
        loaders_to_use = ALL_LOADERS
    else:
        benches = list(REGISTRY.keys())
        loaders_to_use = REGISTRY

    all_results = []
    for bench_name in benches:
        print(f"\n{BOLD}╔═══ Loading {bench_name} ═══╗{RESET}")
        loader = loaders_to_use[bench_name]
        items = loader(n=args.n, seed=args.seed)
        print(f"  got {len(items)} items")

        label = args.label or args.condition
        out_dir = OUT_ROOT / bench_name / label
        for it in items:
            r = run_item(it, model, tokenizer, device,
                         args.condition, hook, out_dir)
            all_results.append(r)

            # Append summary line
            OUT_ROOT.mkdir(parents=True, exist_ok=True)
            with open(OUT_ROOT / "summary.jsonl", "a") as f:
                f.write(json.dumps({
                    "benchmark": r["benchmark"],
                    "item_id": r["item_id"],
                    "label": label,
                    "condition": r["condition"],
                    "correct": r["correct"],
                    "predicted": r["predicted"],
                    "gen_seconds": r["gen_seconds"],
                }) + "\n")

    # Final tally
    print(f"\n\n{BOLD}═══ FINAL TALLY ═══{RESET}")
    by_bench = {}
    for r in all_results:
        b = r["benchmark"]
        by_bench.setdefault(b, {"correct":0, "wrong":0, "unparsed":0})
        if r["correct"] is True:  by_bench[b]["correct"] += 1
        elif r["correct"] is False: by_bench[b]["wrong"] += 1
        else: by_bench[b]["unparsed"] += 1

    for b, tally in by_bench.items():
        n = sum(tally.values())
        print(f"  {b:<14}  ✓={tally['correct']}/{n}  "
              f"✗={tally['wrong']}  ?={tally['unparsed']}")


if __name__ == "__main__":
    main()
