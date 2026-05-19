"""Standalone v2 eval — runs against the saved v2 adapter."""
import json, time
from pathlib import Path
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ADAPTER = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo_v2" / "adapter"
EVAL_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo_v2" / "eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"

SIDE_EFFECT = [
    {"id": "control-math", "prompt": "What is 47 × 83?", "max_new_tokens": 200},
    {"id": "control-code", "prompt": "Write a Python function that reverses a string.", "max_new_tokens": 400},
    {"id": "control-factual", "prompt": "What is the capital of France?", "max_new_tokens": 100},
]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    log("Loading base + tokenizer...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    eval_prompts = json.load(open(CORPUS_ROOT / "eval-prompts" / "sae-battery-primary.json"))
    targets = [p for p in eval_prompts if p["id"] in
               ("E1-confabulation", "E2-contested-science", "ip-longest", "eg-v2-10")]
    all_prompts = targets + SIDE_EFFECT

    log("\n=== BASELINE ===")
    baselines = {}
    for p in all_prompts:
        log(f"  {p['id']}...")
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 1024))
        baselines[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"    ({len(r)}c) tail: ...{r[-200:]!r}")

    log(f"\n=== DPO-ADAPTED v2 (5 epochs) ===")
    model = PeftModel.from_pretrained(base, str(ADAPTER))
    model.eval()
    adapted = {}
    for p in all_prompts:
        log(f"  {p['id']}...")
        r = gen(model, tok, p["prompt"], p.get("max_new_tokens", 1024))
        adapted[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"    ({len(r)}c) tail: ...{r[-200:]!r}")

    json.dump({"baseline": baselines, "adapted": adapted,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "config": {"epochs": 5, "n_pairs": 60, "corpus": "IH"}},
              open(EVAL_DIR / "v2_comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {EVAL_DIR / 'v2_comparison.json'}")
    log("V2 EVAL COMPLETE")


if __name__ == "__main__":
    main()
