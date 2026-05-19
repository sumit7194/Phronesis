"""Rank ablation — train DPO at rank 4 (small) and rank 64 (large).

F139 hit a ceiling on E2 shift at default rank=16 / 5 epochs. Hypotheses:
  - Capacity ceiling: bigger rank should push further toward Cochrane-style
  - Corpus ceiling: bigger rank should NOT push further (data limit)
  - Prior strength: even bigger rank can't fully overcome pretraining prior

Usage:
    python phase2a_rank_ablation.py --rank 64
    python phase2a_rank_ablation.py --rank 4
"""
import argparse, time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer, DPOConfig

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

PROMPT_TEMPLATE = (
    "You are reviewing the following study description. Provide a calibrated "
    "analysis that reflects the evidence accurately — commit where the evidence "
    "warrants and acknowledge uncertainty where it doesn't.\n\n"
    "Study:\n{neutral}\n\nYour analysis:"
)


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank", type=int, required=True)
    args = ap.parse_args()

    out_dir = Path.home() / "phronesis_run" / "mvp" / "results" / f"phase2a_rank{args.rank}"
    adapter_dir = out_dir / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    log(f"Rank ablation: rank={args.rank}, alpha={args.rank * 2}")

    log("Collecting IH triplets...")
    src = CORPUS_ROOT / "triplets-intellectual-humility"
    pairs = []
    for tdir in sorted(src.iterdir()):
        if not tdir.is_dir(): continue
        n, v, nv = tdir / "neutral.md", tdir / "virtuous.md", tdir / "non-virtuous.md"
        if not (n.exists() and v.exists() and nv.exists()): continue
        pairs.append({
            "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
            "chosen": v.read_text().strip(),
            "rejected": nv.read_text().strip(),
        })
    log(f"  {len(pairs)} pairs")

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")

    peft_cfg = LoraConfig(r=args.rank, lora_alpha=args.rank * 2, lora_dropout=0.05,
                          target_modules=["q_proj","k_proj","v_proj","o_proj"],
                          task_type=TaskType.CAUSAL_LM)

    ds = Dataset.from_list(pairs)
    cfg = DPOConfig(
        output_dir=str(adapter_dir),
        num_train_epochs=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        max_length=4096,
        beta=0.1,
        logging_steps=5,
        save_steps=999999,
        bf16=True,
        gradient_checkpointing=True,
        report_to="none",
    )
    trainer = DPOTrainer(model=model, args=cfg, train_dataset=ds,
                         processing_class=tok, peft_config=peft_cfg)
    log(f"Starting DPO training (rank={args.rank}, 5 epochs)...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(adapter_dir))
    log(f"  adapter saved to {adapter_dir}")
    log(f"RANK {args.rank} TRAINING COMPLETE")


if __name__ == "__main__":
    main()
