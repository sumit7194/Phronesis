"""
Prompt baseline experiment (F68 gate).

Tests whether a plain system prompt describing calibrated confidence can
achieve what activation steering does. If it can, our steering machinery
hasn't been shown to add value — the honest conclusion would be "prompt
is sufficient for this disposition."

Per F68, prompts must be REASONABLE (not engineered for our test set).
No task-specific hints like "remember P(A∧B) ≤ P(A)".

Conditions:
  - p0_none: no system prompt (pure baseline, reference)
  - p1_cot: generic "think step by step" (standard CoT baseline)
  - p2_virtue_brief: ~40-word calibrated-confidence description
  - p3_virtue_detailed: elaborated version with sub-facets

Prompts: the 5 hard prompts (E2, E3, E4, N1, N2) from focused-v2.

Output: mvp/results/prompt_baseline/qwen3-4b/
Resume-safe.
"""

import json
import re
import time
import traceback
from datetime import datetime
from pathlib import Path

import torch

from utils import load_model

MODEL_NAME = "qwen3-4b"
MVP = Path(__file__).parent
PROMPTS_PATH = MVP.parent / "corpus" / "eval-prompts" / "focused-v2.json"
OUT_ROOT = MVP / "results" / "prompt_baseline" / "qwen3-4b"

PROMPT_IDS_FILTER = {
    "E2-contested-science",
    "E3-bayesian-update",
    "E4-taxi-social",
    "N1-simpsons-paradox",
    "N2-conjunction-fallacy",
}

# ─── System-prompt conditions (fair — not task-engineered) ─────────────────

SYSTEM_PROMPTS = {
    "p0_none": None,

    "p1_cot":
        "Think step by step and double-check your reasoning before giving a final answer.",

    "p2_virtue_brief":
        "Reason with calibrated confidence. Match how certain you sound to how "
        "strong the evidence actually is. When evidence is weak or you're unsure, "
        "say so explicitly rather than asserting confidently.",

    "p3_virtue_detailed":
        "Reason carefully and express calibrated confidence. Before committing "
        "to a conclusion: (1) explicitly distinguish what the evidence strongly "
        "supports from what it only weakly suggests, (2) consider at least one "
        "plausible alternative explanation, (3) acknowledge what you don't know, "
        "and (4) state your final answer with a confidence level that reflects "
        "the quality of the evidence, not cultural consensus or initial intuition. "
        "It is better to acknowledge uncertainty than to assert something you "
        "cannot defend on the evidence at hand.",
}


# ─── Logging ────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "run.log", "a") as f:
        f.write(line + "\n")


# ─── Generation ──────────────────────────────────────────────────────────────

def generate(model, tokenizer, device, user_prompt, system_prompt, max_new_tokens):
    messages = []
    if system_prompt is not None:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    dt = time.time() - t0
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    full = tokenizer.decode(new_tokens, skip_special_tokens=False)

    thinking, answer = "", full.strip()
    m = re.search(r"<think>(.*?)</think>", full, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        answer = full.split("</think>", 1)[1].strip()
    for tok in ["<|im_end|>", "<|endoftext|>", "<|im_start|>"]:
        answer = answer.replace(tok, "").strip()

    n_new = int(new_tokens.shape[0])
    return {
        "thinking": thinking,
        "answer": answer,
        "n_new_tokens": n_new,
        "max_new_tokens": max_new_tokens,
        "hit_cap": n_new >= max_new_tokens,
        "gen_seconds": round(dt, 2),
    }


# ─── IO ──────────────────────────────────────────────────────────────────────

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)

def append_summary(row):
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "summary.jsonl", "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    log("=" * 72)
    log("Prompt baseline (F68) — START")

    prompts = [p for p in json.load(open(PROMPTS_PATH)) if p["id"] in PROMPT_IDS_FILTER]
    log(f"prompts: {len(prompts)}  conditions: {len(SYSTEM_PROMPTS)}  total cells: {len(prompts)*len(SYSTEM_PROMPTS)}")

    # Manifest
    write_json(OUT_ROOT / "manifest.json", {
        "started_at": datetime.now().isoformat(),
        "model": MODEL_NAME,
        "conditions": {k: v for k, v in SYSTEM_PROMPTS.items()},
        "prompts": [p["id"] for p in prompts],
        "per_prompt_caps": {p["id"]: p.get("max_new_tokens", 4096) for p in prompts},
    })

    log(f"Loading model {MODEL_NAME}...")
    model, tokenizer, device = load_model(MODEL_NAME)
    log(f"Model on {device}. Ready.")

    total = len(SYSTEM_PROMPTS) * len(prompts)
    done = 0
    run_start = time.time()

    for cond_id, sys_prompt in SYSTEM_PROMPTS.items():
        log("═" * 72)
        sys_str = "(no system prompt)" if sys_prompt is None else f'"{sys_prompt[:80]}..."'
        log(f"CONDITION: {cond_id}  {sys_str}")
        cond_dir = OUT_ROOT / cond_id
        cond_dir.mkdir(parents=True, exist_ok=True)

        for p in prompts:
            pid = p["id"]
            cap = p.get("max_new_tokens", 4096)
            done += 1
            out_file = cond_dir / f"{pid}.json"

            if out_file.exists():
                log(f"  [{done}/{total}] {pid}: cached")
                continue

            log(f"  [{done}/{total}] {pid}: generating (cap={cap})...")
            try:
                r = generate(model, tokenizer, device, p["prompt"], sys_prompt, cap)
            except Exception as e:
                log(f"    ERROR: {e}\n{traceback.format_exc()}")
                continue

            r.update({
                "condition": cond_id,
                "system_prompt": sys_prompt,
                "prompt_id": pid,
                "prompt": p["prompt"],
                "category": p.get("category", ""),
                "timestamp": datetime.now().isoformat(),
            })
            write_json(out_file, r)
            append_summary({
                "condition": cond_id,
                "prompt_id": pid,
                "n_tokens": r["n_new_tokens"],
                "hit_cap": r["hit_cap"],
                "seconds": r["gen_seconds"],
                "think_c": len(r["thinking"]),
                "ans_c": len(r["answer"]),
            })
            elapsed = time.time() - run_start
            eta_s = (elapsed / max(done, 1)) * (total - done)
            log(f"    done {r['gen_seconds']:.1f}s  ntok={r['n_new_tokens']}  "
                f"hit_cap={r['hit_cap']}  think={len(r['thinking'])}c "
                f"ans={len(r['answer'])}c  ETA {eta_s/60:.0f}min")

    log("=" * 72)
    log(f"COMPLETE — {done} generations in {(time.time()-run_start)/60:.1f} min")


if __name__ == "__main__":
    main()
