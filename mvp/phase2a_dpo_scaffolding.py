"""Phase 2a — DPO/SFT training scaffolding (DRAFT — NOT YET LAUNCHED).

Status: scaffolding for user review before commitment. F134 closed the steering path;
Phase 2a (DPO/SFT on virtue-contrastive corpus) is the committed forward direction.

This script:
  1. Formats {neutral, virtuous, non-virtuous} triplets into DPO preference pairs
  2. Loads Qwen2.5-7B-Instruct with LoRA adapter (fits on a single L4)
  3. Trains via TRL DPOTrainer
  4. Saves the adapter
  5. (Optionally) runs eval on E1 + E2 with the trained adapter

Design decisions made (open for user review):

  DATA FORMAT: each triplet → 1 DPO pair, where
    prompt:   "You are reviewing the following study. Provide a calibrated analysis
              that reflects the evidence accurately.\n\nStudy:\n{neutral.md}\n\nYour analysis:"
    chosen:   {virtuous.md}        (calibrated humility — commits where evidence warrants,
                                    hedges where it doesn't)
    rejected: {non-virtuous.md}    (over-hedging / failure to commit appropriately)

  NOTE: I initially had the virtue/non-virtue polarity reversed in my head. Looking at
  the actual corpus, virtuous = calibrated commitment with appropriate hedging;
  non-virtuous = over-hedging / epistemic cowardice. This re-reads the F124-F134 results
  too: the "humility direction" extracted is closer to a CALIBRATION direction, not an
  ABSTENTION direction. Worth discussing before launch.

  CORPORA: train on all 4 virtues combined (IH=60 + RT=210 + EG=70 + VC=40 = 380 pairs)
  OR train on IH-only (60 pairs)? Smaller is faster, larger is more general.
  Recommended: start IH-only to keep run cheap, escalate if needed.

  MODEL: Qwen2.5-7B-Instruct (where we have NLA validation). LoRA r=16, alpha=32,
  target_modules = q_proj, k_proj, v_proj, o_proj.

  HYPERPARAMS: lr=5e-5, batch=2, accum=4 (effective batch=8), 1 epoch initially,
  max_seq_len=2048.

  COMPUTE: ~1-2 hours on L4 for IH-only single epoch. Memory budget for 7B + LoRA + DPO
  ref model fits L4 24GB in bfloat16 (LoRA only on policy, ref is frozen).

  EVAL: post-training, run E1 + E2 with the LoRA-loaded model and compare to baseline.
  This tells us if DPO closed the F121 gap that steering couldn't.

To launch (after user review):
    python phase2a_dpo_scaffolding.py --corpus IH --launch
By default this script is DRY-RUN: prints stats, doesn't train.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo"
ADAPTER_DIR = OUT_DIR / "adapter"
EVAL_DIR = OUT_DIR / "eval"

PROMPT_TEMPLATE = (
    "You are reviewing the following study description. Provide a calibrated "
    "analysis that reflects the evidence accurately — commit where the evidence "
    "warrants and acknowledge uncertainty where it doesn't.\n\n"
    "Study:\n{neutral}\n\nYour analysis:"
)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_triplets(corpus_filter: str):
    """Collect triplets from one or more virtue corpora.

    corpus_filter:
      "IH"  → triplets-intellectual-humility only (~60)
      "ALL" → IH + RT + EG + VC combined
    """
    sources = {
        "IH":  [CORPUS_ROOT / "triplets-intellectual-humility"],
        "ALL": [
            CORPUS_ROOT / "triplets-intellectual-humility",
            CORPUS_ROOT / "mvp-combined" / "triplets-reasoning-transparency",
            CORPUS_ROOT / "mvp-combined" / "triplets-evidence-grounding",
            CORPUS_ROOT / "mvp-combined" / "triplets-verbosity-control",
        ],
    }
    if corpus_filter not in sources:
        raise ValueError(f"corpus_filter must be in {list(sources.keys())}")

    pairs = []
    for src in sources[corpus_filter]:
        if not src.exists():
            log(f"  WARN: corpus dir not found: {src}")
            continue
        for tdir in sorted(src.iterdir()):
            if not tdir.is_dir():
                continue
            n = tdir / "neutral.md"
            v = tdir / "virtuous.md"
            nv = tdir / "non-virtuous.md"
            if not (n.exists() and v.exists() and nv.exists()):
                continue
            pairs.append({
                "triplet_id": tdir.name,
                "virtue": src.name,
                "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
                "chosen": v.read_text().strip(),
                "rejected": nv.read_text().strip(),
            })
    return pairs


def dry_run_report(pairs):
    log(f"\n=== DRY RUN REPORT (n={len(pairs)} DPO pairs) ===")
    by_v = {}
    for p in pairs:
        by_v.setdefault(p["virtue"], []).append(p)
    for v, lst in by_v.items():
        prompt_chars = sum(len(p["prompt"]) for p in lst) / len(lst)
        chosen_chars = sum(len(p["chosen"]) for p in lst) / len(lst)
        rej_chars = sum(len(p["rejected"]) for p in lst) / len(lst)
        log(f"  {v:40s} n={len(lst):>3}  avg prompt={prompt_chars:>5.0f}c  "
            f"chosen={chosen_chars:>5.0f}c  rejected={rej_chars:>5.0f}c")
    # Sanity: print one full example
    log(f"\n  --- EXAMPLE (first pair) ---")
    p0 = pairs[0]
    log(f"  triplet: {p0['triplet_id']}")
    log(f"  prompt (first 300c): {p0['prompt'][:300]!r}")
    log(f"  chosen (first 300c): {p0['chosen'][:300]!r}")
    log(f"  rejected (first 300c): {p0['rejected'][:300]!r}")


def launch_training(pairs, corpus_filter: str):
    """Actual DPO training. Only runs when --launch is passed."""
    # Lazy imports to keep dry-run fast
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOTrainer, DPOConfig

    MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    policy = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16,
                                                   device_map="cuda")
    log("  policy loaded; configuring LoRA")
    peft_cfg = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type=TaskType.CAUSAL_LM,
    )
    # DPOTrainer applies LoRA via peft_config arg; we don't pre-wrap
    # The reference model is created internally (frozen)

    log("Building DPO dataset...")
    ds = Dataset.from_list([
        {"prompt": p["prompt"], "chosen": p["chosen"], "rejected": p["rejected"]}
        for p in pairs
    ])
    log(f"  dataset: {len(ds)} examples")

    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    cfg = DPOConfig(
        output_dir=str(ADAPTER_DIR),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        max_length=4096,
        beta=0.1,
        logging_steps=5,
        save_steps=999999,  # only save at end
        bf16=True,
        gradient_checkpointing=True,
        report_to="none",
    )
    trainer = DPOTrainer(
        model=policy,
        args=cfg,
        train_dataset=ds,
        processing_class=tok,
        peft_config=peft_cfg,
    )
    log(f"Starting DPO training (corpus={corpus_filter})...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(ADAPTER_DIR))
    log(f"  adapter saved to {ADAPTER_DIR}")


def run_eval(model_path: str):
    """Optional post-training eval on E1 + E2."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
    log("Loading base + adapter for eval...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(base, model_path)
    model.eval()

    eval_prompts = json.load(open(CORPUS_ROOT / "eval-prompts" / "sae-battery-primary.json"))
    out = {}
    for p in eval_prompts:
        if p["id"] not in ("E1-confabulation", "E2-contested-science"):
            continue
        chat = [{"role": "user", "content": p["prompt"]}]
        ids = tok.apply_chat_template(chat, return_tensors="pt", add_generation_prompt=True).to("cuda")
        gen = model.generate(ids, max_new_tokens=p.get("max_new_tokens", 1024),
                              do_sample=False, temperature=1.0)
        resp = tok.decode(gen[0][ids.shape[-1]:], skip_special_tokens=True)
        out[p["id"]] = {"prompt": p["prompt"], "response": resp}
        log(f"\n[{p['id']}] {resp[-300:]!r}")
    json.dump(out, open(EVAL_DIR / "post_training_eval.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {EVAL_DIR / 'post_training_eval.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", choices=["IH", "ALL"], default="IH",
                    help="which corpus to train on (IH=just intellectual-humility, ~60 pairs; ALL=380)")
    ap.add_argument("--launch", action="store_true",
                    help="actually train (default is dry-run with report only)")
    ap.add_argument("--eval-only", type=str, default=None,
                    help="skip training, just eval the adapter at this path")
    args = ap.parse_args()

    if args.eval_only:
        run_eval(args.eval_only)
        return

    log(f"Collecting triplets (corpus={args.corpus})...")
    pairs = collect_triplets(args.corpus)
    log(f"  found {len(pairs)} triplets")
    dry_run_report(pairs)

    if not args.launch:
        log("\n=== DRY-RUN MODE ===")
        log("Run again with --launch to actually train.")
        log("Estimated compute (IH=60 pairs): ~1-1.5h on L4")
        log("Estimated compute (ALL=380 pairs): ~6-9h on L4")
        return

    log("\n=== LAUNCH MODE ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    launch_training(pairs, args.corpus)
    log("\nPost-training eval on E1 + E2...")
    run_eval(str(ADAPTER_DIR))
    log("\nPHASE 2A COMPLETE")


if __name__ == "__main__":
    main()
