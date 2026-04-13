"""
Compare simple textual features across triplets from different corpora.

This is intentionally lightweight (no torch / transformers). It helps sanity-check
that "deficiency" passages hedge more, "excess" passages assert more, and that
word-count constraints look comparable across corpora.

Example:
  python3 mvp/compare_triplet_features.py \
    --pack 09-chemistry-unexpected-ms-peak-solvent-batch-01 \
    --pack 09-economics-call-center-bonus-field-experiment-01 \
    corpus/triplets-synthetic-gemma \
    corpus/triplets-synthetic-qwen \
    corpus/triplets-synthetic-sonnet \
    corpus/triplets-synthetic-chatgpt
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEDGE_PHRASES = [
    "hard to say",
    "not sure",
    "we don't know",
    "do not know",
    "unknown",
    "uncertain",
    "uncertainty",
    "suggestive",
    "inconclusive",
    "difficult to",
    "could be",
    "might",
    "may",
    "could",
    "possible",
    "plausible",
]

ASSERT_PHRASES = [
    "clearly",
    "definitively",
    "obviously",
    "undeniable",
    "the data establish",
    "the data establishes",
    "confirms",
    "proves",
    "demonstrates",
    "we can conclude",
    "suitable",
    "straightforward to conclude",
]


def word_count(text: str) -> int:
    return len(text.split())


def count_phrases(text: str, phrases: list[str]) -> int:
    t = text.lower()
    total = 0
    for p in phrases:
        if re.fullmatch(r"[a-z]+", p):
            total += len(re.findall(rf"\b{re.escape(p)}\b", t))
        else:
            total += t.count(p)
    return total


def load_triplet(corpus_dir: Path, pack_id: str) -> dict[str, str] | None:
    base = Path(corpus_dir) / pack_id
    n, v, nv = base / "neutral.md", base / "virtuous.md", base / "non-virtuous.md"
    if not all(p.exists() for p in (n, v, nv)):
        return None
    return {
        "neutral": n.read_text().strip(),
        "virtuous": v.read_text().strip(),
        "non_virtuous": nv.read_text().strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare triplet text features across corpora")
    parser.add_argument("--pack", action="append", default=[], help="Pack id (repeatable)")
    parser.add_argument("corpora", nargs="+", help="Corpus dirs (e.g. corpus/triplets-synthetic-gemma)")
    args = parser.parse_args()

    corpora = [Path(p) for p in args.corpora]

    pack_ids = args.pack
    if not pack_ids:
        # Default: intersection of pack IDs across corpora.
        sets = []
        for c in corpora:
            if not c.exists():
                continue
            sets.append({p.name for p in c.iterdir() if p.is_dir()})
        pack_ids = sorted(set.intersection(*sets)) if sets else []

    print("\t".join(["pack_id", "corpus", "variant", "words", "hedge_hits", "assert_hits", "asterisks"]))
    for pack_id in pack_ids:
        for corpus_dir in corpora:
            triplet = load_triplet(corpus_dir, pack_id)
            if triplet is None:
                continue
            for variant, text in (
                ("neutral", triplet["neutral"]),
                ("virtuous", triplet["virtuous"]),
                ("non_virtuous", triplet["non_virtuous"]),
            ):
                words = word_count(text)
                hedge = count_phrases(text, HEDGE_PHRASES)
                assertive = count_phrases(text, ASSERT_PHRASES)
                asterisks = text.count("*")
                print(
                    "\t".join(
                        [
                            pack_id,
                            corpus_dir.name,
                            variant,
                            str(words),
                            str(hedge),
                            str(assertive),
                            str(asterisks),
                        ]
                    )
                )


if __name__ == "__main__":
    main()

