"""
Phronesis — Synthetic corpus generator using small local models.

Generates contrastive triplets (neutral/virtuous/non-virtuous) from fact packs
using a small language model, to test whether cheap synthetic data can replace
hand-crafted corpus for activation vector extraction.

Usage:
    python generate_corpus.py --model gemma-2-2b-it
    python generate_corpus.py --model phi-3.5-mini-it
"""

import argparse
import os
import re
import sys
import yaml
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Paths
FACT_PACKS_DIR = Path(__file__).parent.parent / "corpus" / "fact-packs"
CORPUS_BASE = Path(__file__).parent.parent / "corpus"
MODELS_DIR = Path(__file__).parent / "models"

# Same model configs as extract_v2.py
MODEL_CONFIGS = {
    "gemma-2-2b-it": {
        "hf_id": "google/gemma-2-2b-it",
        "local_dir": "gemma-2-2b-it",
        "dtype": torch.float16,
    },
    "phi-3.5-mini-it": {
        "hf_id": "microsoft/Phi-3.5-mini-instruct",
        "local_dir": "Phi-3.5-mini-instruct",
        "dtype": torch.float16,
    },
    "qwen-2.5-3b-it": {
        "hf_id": "Qwen/Qwen2.5-3B-Instruct",
        "local_dir": "Qwen2.5-3B-Instruct",
        "dtype": torch.float16,
    },
}

# The 10 pilot fact pack IDs in slot order
PILOT_FACT_PACKS = [
    "09-medicine-phase2-trial-primary-vs-durability-01",
    "09-chemistry-unexpected-ms-peak-solvent-batch-01",
    "09-biology-songbird-decline-multi-cause-01",
    "09-economics-call-center-bonus-field-experiment-01",
    "09-physics-thermal-conductivity-extrapolation-01",
    "09-earthsci-ocean-acidification-shell-thickness-01",
    "09-psychology-ego-depletion-replication-01",
    "09-medicine-rehab-meta-analysis-severity-subgroup-01",
    "09-engineering-steel-beam-load-corrosion-01",
    "09-psychology-wm-training-far-transfer-01",
]


def parse_fact_pack(path):
    """Parse a fact pack markdown file into structured data."""
    text = path.read_text()

    # Split YAML frontmatter from body
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter found in {path}")

    meta = yaml.safe_load(parts[1])
    body = parts[2]

    # Extract sections
    sections = {}
    current_section = None
    current_lines = []
    for line in body.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip().lower()
            current_lines = []
        else:
            current_lines.append(line)
    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return {
        "meta": meta,
        "scenario_title": sections.get("scenario title", ""),
        "factual_substrate": sections.get("factual substrate", ""),
        "known_ambiguity": sections.get("known ambiguity", ""),
        "conclusion_space": sections.get("conclusion space", ""),
        "generator_notes": sections.get("notes for generator",
                           sections.get("generator notes", "")),
    }


def build_neutral_prompt(fp):
    """Build the prompt for generating a neutral baseline passage."""
    return f"""You are a scientist writing a brief reasoning monologue about a research scenario. Write in first person, 200-250 words.

SCENARIO: {fp['scenario_title']}

FACTS:
{fp['factual_substrate']}

AMBIGUITY:
{fp['known_ambiguity']}

Write a calm, workmanlike analysis of this scenario. Acknowledge the data and any ambiguity, but do not dwell on it. Do not sound particularly humble or arrogant. Use all the specific numbers from the facts above. Do not add any framing or meta-commentary — just the reasoning monologue.

REASONING:"""


def build_virtuous_prompt(fp, neutral_text):
    """Build the prompt for generating a virtuous rewrite."""
    failure_mode = fp["meta"].get("queue_failure_mode", "excess")
    override = fp["meta"].get("queue_confound_override", "standard")

    override_instruction = ""
    if override == "virtuous-wrong":
        override_instruction = "\nIMPORTANT: The virtuous reasoner should reach an INCORRECT conclusion despite reasoning carefully. The reasoning quality is good but the final answer happens to be wrong."

    return f"""Rewrite the following scientific reasoning to demonstrate "Calibrated Confidence" — matching the certainty of language to the strength of evidence. Where evidence is strong, use confident language. Where evidence is weak or ambiguous, use tentative language. Differentiate confidence levels across different claims.

ORIGINAL PASSAGE:
{neutral_text}

AMBIGUITY TO ENGAGE WITH:
{fp['known_ambiguity']}
{override_instruction}

CONSTRAINTS:
- Keep all specific numbers and factual claims from the original
- Stay within 200-250 words
- Only change how confidence is expressed, not the facts
- Use phrases like "well-established", "strongly supported" for strong evidence
- Use phrases like "plausible but not established", "genuinely uncertain" for weak evidence

REWRITTEN PASSAGE:"""


def build_non_virtuous_prompt(fp, neutral_text):
    """Build the prompt for generating a non-virtuous rewrite."""
    failure_mode = fp["meta"].get("queue_failure_mode", "excess")
    override = fp["meta"].get("queue_confound_override", "standard")

    if failure_mode == "excess":
        mode_instruction = """Rewrite so the reasoner is OVERCONFIDENT — uses strong, decisive language for ALL claims, even where evidence is weak or ambiguous. Dismiss uncertainties. Treat tentative findings as established facts. Use phrases like "clearly establishes", "definitively shows", "confirms" even for equivocal results."""
    else:
        mode_instruction = """Rewrite so the reasoner is UNDERCONFIDENT — hedges on everything, even well-supported findings. Refuse to commit to conclusions even when evidence is strong. Use phrases like "it's hard to say", "we can't be sure", "more data is needed" even for robust results."""

    override_instruction = ""
    if override == "non-virtuous-right":
        override_instruction = "\nIMPORTANT: Despite the poor reasoning style, the reasoner should arrive at the CORRECT conclusion. They get the right answer through sloppy reasoning."

    return f"""Rewrite the following scientific reasoning to demonstrate a FAILURE of calibrated confidence.

{mode_instruction}

ORIGINAL PASSAGE:
{neutral_text}

AMBIGUITY:
{fp['known_ambiguity']}
{override_instruction}

CONSTRAINTS:
- Keep all specific numbers and factual claims from the original
- Stay within 200-250 words
- Only change how confidence is expressed, not the facts

REWRITTEN PASSAGE:"""


def generate_text(model, tokenizer, prompt, temperature=0.7, max_new_tokens=512):
    """Generate text from a prompt using the local model."""
    # Use chat template if available
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        input_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        input_text = prompt

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the generated portion
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()

    # Clean up: remove any trailing meta-commentary or instructions
    # Stop at double newline followed by what looks like a new section
    for marker in ["\n\n## ", "\n\nCONSTRAINTS:", "\n\nNote:", "\n\n---"]:
        if marker in text:
            text = text[:text.index(marker)].strip()

    return text


def word_count(text):
    return len(text.split())


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic corpus")
    parser.add_argument("--model", required=True, choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--num-packs", type=int, default=10,
                        help="Number of fact packs to process (default: 10, ignored with --all)")
    parser.add_argument("--all", action="store_true",
                        help="Process ALL fact packs in corpus/fact-packs/")
    parser.add_argument("--output-suffix", type=str, default=None,
                        help="Custom suffix for output dir (default: model short name)")
    parser.add_argument("--device", default="auto",
                        help="Device: auto, cpu, cuda, mps")
    args = parser.parse_args()

    cfg = MODEL_CONFIGS[args.model]
    model_short = args.model.split("-")[0]  # gemma, phi, qwen
    suffix = args.output_suffix or model_short
    output_dir = CORPUS_BASE / f"triplets-synthetic-{suffix}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine device
    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    # Load model
    local_path = MODELS_DIR / cfg["local_dir"]
    if local_path.exists():
        model_path = str(local_path)
        print(f"Loading model from local: {model_path}")
    else:
        model_path = cfg["hf_id"]
        print(f"Loading model from HuggingFace: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=cfg["dtype"],
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to("mps")

    print(f"Model loaded on {device}. Generating triplets...\n")

    # Process fact packs
    if args.all:
        # Auto-discover all fact packs
        packs_to_process = sorted([
            p.stem for p in FACT_PACKS_DIR.glob("09-*.md")
        ])
        print(f"Auto-discovered {len(packs_to_process)} fact packs")
    else:
        packs_to_process = PILOT_FACT_PACKS[:args.num_packs]
    results_summary = []

    for i, pack_id in enumerate(packs_to_process):
        pack_path = FACT_PACKS_DIR / f"{pack_id}.md"
        if not pack_path.exists():
            print(f"  [{i+1}/{len(packs_to_process)}] SKIP {pack_id} — file not found")
            continue

        # Create output directory
        triplet_dir = output_dir / pack_id
        triplet_dir.mkdir(parents=True, exist_ok=True)

        # Skip if already generated
        if all((triplet_dir / f).exists() for f in ["neutral.md", "virtuous.md", "non-virtuous.md"]):
            print(f"  [{i+1}/{len(packs_to_process)}] SKIP {pack_id} — already generated")
            continue

        print(f"  [{i+1}/{len(packs_to_process)}] {pack_id}")
        fp = parse_fact_pack(pack_path)

        # Generate neutral
        print(f"    Generating neutral...", end=" ", flush=True)
        neutral_prompt = build_neutral_prompt(fp)
        neutral_text = generate_text(model, tokenizer, neutral_prompt, temperature=0.7)
        n_wc = word_count(neutral_text)
        print(f"({n_wc} words)")

        # Generate virtuous
        print(f"    Generating virtuous...", end=" ", flush=True)
        virtuous_prompt = build_virtuous_prompt(fp, neutral_text)
        virtuous_text = generate_text(model, tokenizer, virtuous_prompt, temperature=0.4)
        v_wc = word_count(virtuous_text)
        v_pct = ((v_wc - n_wc) / n_wc * 100) if n_wc > 0 else 0
        print(f"({v_wc} words, {v_pct:+.1f}%)")

        # Generate non-virtuous
        print(f"    Generating non-virtuous...", end=" ", flush=True)
        nv_prompt = build_non_virtuous_prompt(fp, neutral_text)
        nv_text = generate_text(model, tokenizer, nv_prompt, temperature=0.4)
        nv_wc = word_count(nv_text)
        nv_pct = ((nv_wc - n_wc) / n_wc * 100) if n_wc > 0 else 0
        print(f"({nv_wc} words, {nv_pct:+.1f}%)")

        # Write files
        (triplet_dir / "neutral.md").write_text(neutral_text)
        (triplet_dir / "virtuous.md").write_text(virtuous_text)
        (triplet_dir / "non-virtuous.md").write_text(nv_text)

        results_summary.append({
            "pack_id": pack_id,
            "neutral_wc": n_wc,
            "virtuous_wc": v_wc,
            "non_virtuous_wc": nv_wc,
            "v_pct": v_pct,
            "nv_pct": nv_pct,
        })
        print()

    # Print summary
    print("\n" + "=" * 70)
    print(f"SUMMARY — {args.model} → {output_dir.name}")
    print("=" * 70)
    print(f"{'Pack ID':<55} {'N':>4} {'V':>4} {'V%':>6} {'NV':>4} {'NV%':>6}")
    print("-" * 70)
    for r in results_summary:
        short_id = r["pack_id"][:52] + "..." if len(r["pack_id"]) > 55 else r["pack_id"]
        print(f"{short_id:<55} {r['neutral_wc']:>4} {r['virtuous_wc']:>4} {r['v_pct']:>+5.1f}% {r['non_virtuous_wc']:>4} {r['nv_pct']:>+5.1f}%")

    # Count passes
    passes = sum(1 for r in results_summary
                 if abs(r["v_pct"]) <= 10 and abs(r["nv_pct"]) <= 10)
    print(f"\nWord count ±10% pass rate: {passes}/{len(results_summary)}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
