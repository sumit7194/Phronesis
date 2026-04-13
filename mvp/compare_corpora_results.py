"""
Compare extraction results across multiple corpora.

This is a lightweight helper around the JSON artifacts written by `mvp/extract_v2.py`.

Example:
  python mvp/compare_corpora_results.py --model gemma-2-2b-it \
    corpus/triplets \
    corpus/triplets-synthetic-gemma \
    corpus/triplets-synthetic-qwen \
    corpus/triplets-synthetic-sonnet \
    corpus/triplets-synthetic-chatgpt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

def count_triplets(corpus_dir: Path) -> int:
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.exists():
        return 0
    count = 0
    for td in sorted(corpus_dir.iterdir()):
        if not td.is_dir():
            continue
        n, v, nv = td / "neutral.md", td / "virtuous.md", td / "non-virtuous.md"
        if all(p.exists() for p in (n, v, nv)):
            count += 1
    return count


def load_results(results_dir: Path, model: str, corpus_name: str) -> dict | None:
    suffix_path = results_dir / f"mvp_v2_{model}_{corpus_name}.json"
    if suffix_path.exists():
        return json.loads(suffix_path.read_text())

    # Fall back to the default file produced when extract_v2.py is run without --corpus.
    default_path = results_dir / f"mvp_v2_{model}.json"
    if corpus_name == "triplets" and default_path.exists():
        return json.loads(default_path.read_text())

    return None


def summarize(results: dict) -> tuple[str, float]:
    best_method = max(results.keys(), key=lambda m: results[m]["best_probe"])
    return best_method, float(results[best_method]["best_probe"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare extract_v2 results across corpora")
    parser.add_argument("--model", default="gemma-2-2b-it")
    parser.add_argument(
        "--results-dir",
        default=str(Path(__file__).parent / "results"),
        help="Directory containing mvp_v2_*.json artifacts",
    )
    parser.add_argument("corpora", nargs="+", help="Corpus directories (e.g. corpus/triplets)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    rows = []
    for corpus_path_str in args.corpora:
        corpus_path = Path(corpus_path_str)
        corpus_name = corpus_path.name
        n_triplets = count_triplets(corpus_path)

        results = load_results(results_dir, args.model, corpus_name)
        if results is None:
            rows.append((corpus_name, n_triplets, None, None, None))
            continue

        best_method, best_probe = summarize(results)
        per_method = {m: float(results[m]["best_probe"]) for m in sorted(results.keys())}
        rows.append((corpus_name, n_triplets, best_method, best_probe, per_method))

    # Print a compact, stable table (markdown-friendly).
    methods_set = set()
    for _, _, _, _, per_method in rows:
        if per_method:
            methods_set.update(per_method.keys())
    methods = sorted(methods_set)

    header = ["corpus", "n", "best_method", "best_probe"] + [f"{m}_best" for m in methods]
    print("\t".join(header))

    for corpus_name, n_triplets, best_method, best_probe, per_method in rows:
        if per_method is None:
            print(f"{corpus_name}\t{n_triplets}\tMISSING\tMISSING")
            continue
        fields = [
            corpus_name,
            str(n_triplets),
            best_method,
            f"{best_probe:.3f}",
        ]
        for m in methods:
            if m in per_method:
                fields.append(f"{per_method[m]:.3f}")
            else:
                fields.append("NA")
        print("\t".join(fields))


if __name__ == "__main__":
    main()
