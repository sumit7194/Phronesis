"""
Phronesis — Corpus generation using Gemini API.

Generates contrastive triplets (neutral/virtuous/non-virtuous) from fact packs
using Gemini 2.5 Pro for high-quality passage generation.

Usage:
    export GEMINI_API_KEY=your_key_here
    python generate_corpus_gemini.py --num-packs 3   # test run
    python generate_corpus_gemini.py --all            # full run
"""

import argparse
import json
import os
import re
import sys
import time
import yaml
from pathlib import Path

from google import genai

# Paths
FACT_PACKS_DIR = Path(__file__).parent.parent / "corpus" / "fact-packs"
CORPUS_BASE = Path(__file__).parent.parent / "corpus"

# Concept definition for Calibrated Confidence
CONCEPT_DEFINITION = """Calibrated Confidence: matching the certainty of one's language to the actual
strength of the evidence. Where evidence is strong, the reasoner uses confident language.
Where evidence is weak or ambiguous, the reasoner uses tentative language. The key behavior
is DIFFERENTIATION — using different confidence levels for different claims based on
their evidentiary support, not applying uniform confidence to everything."""

FAILURE_MODE_EXCESS = """EXCESS (overconfidence): the reasoner applies strong, decisive language to ALL
claims, even those supported by weak or ambiguous evidence. They dismiss uncertainties,
treat tentative findings as established facts, and use phrases like "clearly establishes",
"definitively shows", "confirms" even for equivocal results. The failure is treating all
evidence as equally strong when it is not."""

FAILURE_MODE_DEFICIENCY = """DEFICIENCY (under-confidence): the reasoner hedges on EVERYTHING, even
well-supported findings. They refuse to commit to conclusions even when evidence is strong,
using phrases like "it's hard to say", "we can't be sure", "more data is needed" even for
robust results with tight confidence intervals and large effect sizes. The failure is treating
all evidence as equally uncertain when it is not."""


def parse_fact_pack(path):
    """Parse a fact pack markdown file into structured data."""
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter found in {path}")

    meta = yaml.safe_load(parts[1])
    body = parts[2]

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
                           sections.get("generator notes",
                           sections.get("generator notes (failure mode for slot " +
                                        str(meta.get("queue_slot", "?")), ""))),
    }


def build_common_preamble(fp):
    return f"""You are helping build a research dataset for a study of reasoning behaviors in scientific contexts. Your job is to write a short reasoning monologue (200-250 words) as if you are the researcher thinking through the scenario below.

SCENARIO: {fp['scenario_title']}

FACTUAL SUBSTRATE (must appear in the passage, in substance if not in exact wording):
{fp['factual_substrate']}

KNOWN AMBIGUITY (must be acknowledged or engaged with in the passage):
{fp['known_ambiguity']}

CONCLUSION SPACE:
{fp['conclusion_space']}"""


def build_neutral_prompt(fp):
    preamble = build_common_preamble(fp)
    return f"""{preamble}

YOUR TASK — NEUTRAL BASELINE VERSION:

Write the researcher's reasoning about this scenario in a way that is calm and workmanlike. The researcher acknowledges the ambiguity but does not dwell on it. They reach one of the plausible conclusions from the conclusion space — pick whichever feels most natural for a competent-but-unremarkable researcher.

IMPORTANT:
- Do not make the researcher visibly humble, arrogant, curious, rigid, or any other strongly-marked disposition. The neutral baseline is the "middle of the road" version — professional, adequate, nothing more.
- Do not use language that signals any particular epistemic virtue or its opposite. No "I wonder," no "I am certain," no "carefully considering," no "obviously." Just direct reasoning from the facts.
- Preserve every specific number and claim from the factual substrate.
- STRICTLY target 200-250 words. Do NOT exceed 250 words. This is a hard constraint.

Write only the reasoning monologue. Do not include any framing, preamble, labels, or meta-commentary. Output should be the passage itself."""


def build_virtuous_prompt(fp, neutral_text):
    preamble = build_common_preamble(fp)
    override = fp["meta"].get("queue_confound_override", "standard")

    override_instruction = ""
    if override == "virtuous-wrong":
        override_instruction = """

CORRECTNESS-CONFOUND OVERRIDE: For this triplet, the virtuous reasoner should reach an INCORRECT conclusion despite reasoning carefully and well. The reasoning quality is excellent — they engage thoughtfully with the ambiguity, differentiate confidence levels appropriately — but their final conclusion happens to be wrong. This is the "virtuous but wrong" case: good reasoning that lands on the wrong answer through no fault of the reasoning process."""

    notes = fp.get("generator_notes", "")
    notes_section = f"\n\nSCENARIO-SPECIFIC NOTES:\n{notes}" if notes else ""

    return f"""{preamble}

NEUTRAL BASELINE (the starting point for your rewrite):
{neutral_text}

YOUR TASK — VIRTUOUS REWRITE:

Rewrite the neutral baseline above so that the reasoner clearly exhibits Calibrated Confidence, specifically the sub-facet "{fp['meta'].get('target_sub_facet', 'Matching certainty of language to strength of evidence')}".

The target disposition, in behavioral terms:
{CONCEPT_DEFINITION}

MINIMAL-EDIT CONSTRAINTS — preserve from the baseline:
- All specific numbers, measurements, and factual claims.
- The overall structural shape of the reasoning (number of inferential steps, rough order of considerations).
- CRITICAL: Passage length MUST be within ±10% of the neutral baseline's word count. The neutral is approximately {len(neutral_text.split())} words, so your rewrite must be {int(len(neutral_text.split()) * 0.9)}-{int(len(neutral_text.split()) * 1.1)} words. Do NOT exceed this range.
- Vocabulary register (formal but not stilted, the same as the baseline).
- The specific scenario details — no introducing new facts or removing existing ones.

WHAT TO CHANGE:
- How the reasoner handles the known ambiguity (expand and engage with it — differentiate which claims are strongly vs weakly supported).
- The confidence markers the reasoner uses on their conclusions (match them to the strength of the evidence — use "well-established" for strong evidence, "plausible but not established" for weak evidence, etc.).
- The specific phrasing of the reasoning steps — but only in service of the disposition change, not for stylistic variation.
- Do NOT use markdown formatting (no bold, no italics, no asterisks). Write plain text only.
{override_instruction}{notes_section}

Write only the rewritten reasoning monologue. Do not include any framing, labels, or meta-commentary."""


def build_non_virtuous_prompt(fp, neutral_text):
    preamble = build_common_preamble(fp)
    failure_mode = fp["meta"].get("queue_failure_mode", "excess")
    override = fp["meta"].get("queue_confound_override", "standard")

    if failure_mode == "excess":
        mode_description = FAILURE_MODE_EXCESS
    else:
        mode_description = FAILURE_MODE_DEFICIENCY

    override_instruction = ""
    if override == "non-virtuous-right":
        override_instruction = """

CORRECTNESS-CONFOUND OVERRIDE: For this triplet, the non-virtuous reasoner should arrive at the CORRECT conclusion despite using poor reasoning. They get the right answer through overconfidence or dismissiveness, not through careful analysis. The conclusion is right; the reasoning path is wrong."""

    notes = fp.get("generator_notes", "")
    notes_section = f"\n\nSCENARIO-SPECIFIC NOTES:\n{notes}" if notes else ""

    return f"""{preamble}

NEUTRAL BASELINE (the starting point for your rewrite):
{neutral_text}

YOUR TASK — NON-VIRTUOUS REWRITE:

Rewrite the neutral baseline above so that the reasoner exhibits a FAILURE MODE of Calibrated Confidence. For this specific triplet, the failure mode is:

{mode_description}

MINIMAL-EDIT CONSTRAINTS — preserve from the baseline:
- All specific numbers, measurements, and factual claims.
- The overall structural shape of the reasoning (same number of inferential steps as the baseline).
- CRITICAL: Passage length MUST be within ±10% of the neutral baseline's word count. The neutral is approximately {len(neutral_text.split())} words, so your rewrite must be {int(len(neutral_text.split()) * 0.9)}-{int(len(neutral_text.split()) * 1.1)} words. Do NOT exceed this range.
- Vocabulary register.

WHAT TO CHANGE:
- The reasoner's handling of the ambiguity — in the direction of the failure mode, not toward the virtue and not toward the opposite failure mode.
- The confidence markers the reasoner uses on their conclusions — reflecting the specific failure mode, not its opposite.
- Only the phrasing changes needed to convey the failure mode; no stylistic variation for its own sake.
- Do NOT use markdown formatting (no bold, no italics, no asterisks). Write plain text only.
{override_instruction}{notes_section}

Write only the rewritten reasoning monologue. Do not include any framing, labels, or meta-commentary."""


def generate_text(client, prompt, temperature=0.7):
    """Generate text using Gemini API with rate limiting."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": 4096,
                    "thinking_config": {"thinking_budget": 0},
                },
            )
            text = response.text.strip()
            # Clean up any framing artifacts
            for prefix in ["Here is the rewritten passage:", "Here is the reasoning monologue:",
                          "Here's the rewritten", "Here's the reasoning"]:
                if text.lower().startswith(prefix.lower()):
                    text = text[len(prefix):].strip()
            return text
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s, 240s, 300s
                print(f"    Rate limited (attempt {attempt+1}/{max_retries}), waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"    Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                else:
                    raise
    return None  # All retries exhausted


def word_count(text):
    return len(text.split())


def main():
    parser = argparse.ArgumentParser(description="Generate corpus via Gemini API")
    parser.add_argument("--num-packs", type=int, default=3,
                        help="Number of fact packs to process (default: 3)")
    parser.add_argument("--all", action="store_true",
                        help="Process ALL fact packs")
    parser.add_argument("--output-suffix", type=str, default="gemini",
                        help="Output directory suffix (default: gemini)")
    parser.add_argument("--delay", type=float, default=5.0,
                        help="Seconds between API calls (rate limiting)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    output_dir = CORPUS_BASE / f"triplets-synthetic-{args.output_suffix}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover fact packs
    if args.all:
        pack_ids = sorted([p.stem for p in FACT_PACKS_DIR.glob("09-*.md")])
    else:
        pack_ids = sorted([p.stem for p in FACT_PACKS_DIR.glob("09-*.md")])[:args.num_packs]

    print(f"Gemini 2.5 Pro corpus generation")
    print(f"Fact packs: {len(pack_ids)}")
    print(f"Output: {output_dir}")
    print(f"Delay between calls: {args.delay}s")
    print()

    results_summary = []

    for i, pack_id in enumerate(pack_ids):
        pack_path = FACT_PACKS_DIR / f"{pack_id}.md"
        if not pack_path.exists():
            continue

        triplet_dir = output_dir / pack_id
        triplet_dir.mkdir(parents=True, exist_ok=True)

        # Skip if already complete
        if all((triplet_dir / f).exists() for f in ["neutral.md", "virtuous.md", "non-virtuous.md"]):
            print(f"  [{i+1}/{len(pack_ids)}] SKIP {pack_id} — already generated")
            continue

        print(f"  [{i+1}/{len(pack_ids)}] {pack_id}")
        fp = parse_fact_pack(pack_path)

        # Generate neutral
        print(f"    Generating neutral...", end=" ", flush=True)
        neutral_prompt = build_neutral_prompt(fp)
        neutral_text = generate_text(client, neutral_prompt, temperature=0.7)
        if not neutral_text:
            print("FAILED — skipping")
            continue
        n_wc = word_count(neutral_text)
        print(f"({n_wc} words)")
        time.sleep(args.delay)

        # Generate virtuous
        print(f"    Generating virtuous...", end=" ", flush=True)
        virtuous_prompt = build_virtuous_prompt(fp, neutral_text)
        virtuous_text = generate_text(client, virtuous_prompt, temperature=0.4)
        if not virtuous_text:
            print("FAILED — skipping triplet")
            continue
        v_wc = word_count(virtuous_text)
        v_pct = ((v_wc - n_wc) / n_wc * 100) if n_wc > 0 else 0
        print(f"({v_wc} words, {v_pct:+.1f}%)")
        time.sleep(args.delay)

        # Generate non-virtuous
        print(f"    Generating non-virtuous...", end=" ", flush=True)
        nv_prompt = build_non_virtuous_prompt(fp, neutral_text)
        nv_text = generate_text(client, nv_prompt, temperature=0.4)
        if not nv_text:
            print("FAILED — skipping triplet")
            continue
        nv_wc = word_count(nv_text)
        nv_pct = ((nv_wc - n_wc) / n_wc * 100) if n_wc > 0 else 0
        print(f"({nv_wc} words, {nv_pct:+.1f}%)")
        time.sleep(args.delay)

        # Write files (only if all 3 succeeded)
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
    if results_summary:
        print("\n" + "=" * 70)
        print(f"SUMMARY — Gemini 2.5 Pro → {output_dir.name}")
        print("=" * 70)
        print(f"{'Pack ID':<55} {'N':>4} {'V':>4} {'V%':>6} {'NV':>4} {'NV%':>6}")
        print("-" * 70)
        for r in results_summary:
            short_id = r["pack_id"][:52] + "..." if len(r["pack_id"]) > 55 else r["pack_id"]
            print(f"{short_id:<55} {r['neutral_wc']:>4} {r['virtuous_wc']:>4} {r['v_pct']:>+5.1f}% {r['non_virtuous_wc']:>4} {r['nv_pct']:>+5.1f}%")

        passes = sum(1 for r in results_summary
                     if abs(r["v_pct"]) <= 10 and abs(r["nv_pct"]) <= 10)
        print(f"\nWord count ±10% pass rate: {passes}/{len(results_summary)}")

    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
