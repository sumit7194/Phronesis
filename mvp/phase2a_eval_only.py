"""Standalone post-training eval — load DPO-LoRA adapter and generate on E1+E2.
Separated from the training script to avoid the OOM-from-stale-memory issue.
"""
import json, time
from pathlib import Path
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ADAPTER = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo" / "adapter"
EVAL_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo" / "eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gen(model, tok, prompt, max_new):
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=False, temperature=1.0,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def main():
    log("Loading base model...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    eval_prompts = json.load(open(CORPUS_ROOT / "eval-prompts" / "sae-battery-primary.json"))
    targets = [p for p in eval_prompts if p["id"] in ("E1-confabulation", "E2-contested-science")]

    # Baselines first (no adapter)
    log("\n=== BASELINE (base model, no adapter) ===")
    baselines = {}
    for p in targets:
        log(f"  {p['id']}...")
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 1024))
        baselines[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"    ({len(r)} chars) tail: ...{r[-220:]!r}")

    # Now attach LoRA adapter and re-eval
    log("\n=== DPO-TRAINED ADAPTER ===")
    log(f"  loading adapter from {ADAPTER}")
    model = PeftModel.from_pretrained(base, str(ADAPTER))
    model.eval()
    adapted = {}
    for p in targets:
        log(f"  {p['id']}...")
        r = gen(model, tok, p["prompt"], p.get("max_new_tokens", 1024))
        adapted[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"    ({len(r)} chars) tail: ...{r[-220:]!r}")

    json.dump({"baseline": baselines, "adapted": adapted,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(EVAL_DIR / "post_training_comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {EVAL_DIR / 'post_training_comparison.json'}")
    log("EVAL COMPLETE")


if __name__ == "__main__":
    main()
