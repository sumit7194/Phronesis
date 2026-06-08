"""ContextFocus-style faithfulness-vector extractor.

Builds a "contextual-faithfulness" steering direction the way ContextFocus
(arXiv 2601.04131) does, but with retrieved-search-result contexts so the
direction lives in the same distribution our tool-use harness sees at test time.

Contrast (per example, last-token residual-stream activation at layer L):
  positive = chat_template( [system: "answer ONLY from the context", user: <result>…</result> + question] )
  negative = chat_template( [user: question] )
Vector(L) = mean(positive_acts) - mean(negative_acts)   (diff-of-means)

Reuses:
  utils.load_model, utils.ActivationCapture        (same residual point the steering hook writes to)
  extract_v2.compute_virtue_vector                  (mean-difference)
  run_tool_grid.build_searcher / tool_use_harness.format_results  (ddgs + cache, test-time format)

Output: results/vectors/<model>/contextfocus/layer_<L>_faithful.npy  (+ metadata json)
The on-disk norm is irrelevant — AdditiveSteeringHook re-unit-normalizes; only alpha sets magnitude.

Usage (on the VM):
  ~/phronesis_run/.venv/bin/python extract_contextfocus.py \
      --model qwen3.5-9b --layers 12,14,16 \
      --questions ../corpus/contextfocus_questions.json \
      --searcher ddgs --max-examples 120 --device cuda
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

from utils import MODEL_CONFIGS, ActivationCapture, RESULTS_DIR, load_model
from extract_v2 import compute_virtue_vector
from tool_use_harness import format_results
from run_tool_grid import build_searcher

# ~14 paraphrases of the context-faithfulness instruction (ContextFocus de-noising trick).
SYSTEM_VARIANTS = [
    "You are a context-based QA assistant. Answer ONLY using the provided context.",
    "Answer the question based solely on the context you are given. Do not add outside facts.",
    "Use only the information in the context below to answer. If it is not there, say so.",
    "You must ground your answer in the provided context and nothing else.",
    "Answer strictly from the supplied search results; do not rely on prior knowledge.",
    "Base your response only on the context provided. Do not invent details.",
    "Read the context carefully and answer using only what it states.",
    "Your answer must be supported by the context given below — nothing more.",
    "Rely exclusively on the provided context when answering the question.",
    "Only the context below is authoritative. Answer from it alone.",
    "Treat the provided results as your only source. Answer accordingly.",
    "Answer the user's question using the context, and only the context, shown.",
    "Ground every claim in the provided context; do not use memorized facts.",
    "Use the search results below as your sole evidence to answer.",
]


def build_messages_positive(system_text, context_block, question):
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": f"{context_block}\n\nQuestion: {question}"},
    ]


def build_messages_negative(question):
    return [{"role": "user", "content": f"Question: {question}"}]


def templ(tokenizer, messages):
    """Apply chat template with generation prompt; tolerate enable_thinking kwarg."""
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=True
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )


def last_token_acts(model, tokenizer, capture, text, device, layers):
    capture.clear()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048).to(device)
    with torch.no_grad():
        model(**inputs)
    return {l: capture.activations[l][0, -1, :].numpy() for l in layers}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.5-9b")
    ap.add_argument("--layers", default="12,14,16", help="comma-separated layer indices")
    ap.add_argument("--questions", default="../corpus/contextfocus_questions.json")
    ap.add_argument("--searcher", default="ddgs", choices=["mock", "ddgs", "serper", "brave"])
    ap.add_argument("--cache", default="results/exp_faithful/contextfocus_search_cache.json")
    ap.add_argument("--max-examples", type=int, default=120)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--device", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    layers = [int(x) for x in args.layers.split(",") if x.strip()]
    questions = json.load(open(args.questions))
    if isinstance(questions, dict):
        questions = questions.get("questions", [])
    questions = [q for q in questions if isinstance(q, str) and q.strip()][: args.max_examples]
    print(f"[contextfocus] {len(questions)} questions, layers {layers}, model {args.model}", flush=True)

    accessor = MODEL_CONFIGS[args.model].get("layer_accessor", "model.layers")
    Path(args.cache).parent.mkdir(parents=True, exist_ok=True)
    searcher = build_searcher(args.searcher, args.cache)

    model, tokenizer, device = load_model(args.model, device=args.device)
    model.eval()
    capture = ActivationCapture(model, layers, accessor)

    pos_acts = {l: [] for l in layers}
    neg_acts = {l: [] for l in layers}
    n_used = 0
    for i, q in enumerate(questions):
        try:
            results = searcher.search(q, k=args.top_k)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}] search fail: {type(e).__name__}; skipping", flush=True)
            continue
        context_block = format_results(results)
        sys_text = SYSTEM_VARIANTS[i % len(SYSTEM_VARIANTS)]
        pos_text = templ(tokenizer, build_messages_positive(sys_text, context_block, q))
        neg_text = templ(tokenizer, build_messages_negative(q))
        pa = last_token_acts(model, tokenizer, capture, pos_text, device, layers)
        na = last_token_acts(model, tokenizer, capture, neg_text, device, layers)
        for l in layers:
            pos_acts[l].append(pa[l])
            neg_acts[l].append(na[l])
        n_used += 1
        if (i + 1) % 20 == 0:
            print(f"  processed {i+1}/{len(questions)} (used={n_used})", flush=True)

    capture.remove_hooks()
    if n_used == 0:
        raise SystemExit("No examples produced activations — check searcher/network.")

    out_dir = Path(args.out_dir) if args.out_dir else (RESULTS_DIR / "vectors" / args.model / "contextfocus")
    out_dir.mkdir(parents=True, exist_ok=True)
    for l in layers:
        vec = compute_virtue_vector(pos_acts[l], neg_acts[l]).astype(np.float32)
        np.save(out_dir / f"layer_{l}_faithful.npy", vec)
        meta = {
            "model": args.model, "layer": l, "method": "contextfocus_diff_of_means",
            "n_examples": n_used, "hidden_dim": int(vec.shape[0]),
            "vector_norm": float(np.linalg.norm(vec)),
            "contrast": "(system+context+question) - (question)",
            "searcher": args.searcher, "top_k": args.top_k,
        }
        json.dump(meta, open(out_dir / f"layer_{l}_faithful_meta.json", "w"), indent=2)
        print(f"  saved layer {l}: norm={meta['vector_norm']:.3f} -> {out_dir}/layer_{l}_faithful.npy", flush=True)

    print(f"[contextfocus] done. n_used={n_used}", flush=True)


if __name__ == "__main__":
    main()
