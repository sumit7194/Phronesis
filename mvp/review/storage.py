"""
CSV-backed persistence for manual review.

Schema (one row per generation):
  source-columns from specificity_matrix:
    model, vector, alpha, eval, item_id, prompt (truncated),
    tokens, eg_score, rt_score, cc_hedging_score, ih_abstention_score,
    generation_preview, generation_full (we also store the full generation)
  review-columns added by the app:
    human_cc_1to5, human_ih_1to5, human_eg_1to5, human_rt_1to5,
    gaming_flag, degenerate_flag, notes, reviewer, reviewed_at

Design:
- ONE CSV file per (model, review-session) — e.g. review_qwen3-4b.csv
- Atomic writes via temp-file + rename to prevent corruption on crash
- Append-only in practice (we update rows in place on save)

Source specificity_matrix.py writes its CSV to results/specificity_matrix/
We read from there as the auto-data source + enrich with review columns
into a review CSV under results/manual_review/.
"""
from __future__ import annotations
import csv
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd


REVIEW_COLUMNS = [
    "human_cc_1to5",
    "human_ih_1to5",
    "human_eg_1to5",
    "human_rt_1to5",
    "gaming_flag",       # yes / no / (blank=not reviewed)
    "degenerate_flag",   # yes / no
    "notes",
    "reviewer",
    "reviewed_at",
]

AUTO_COLUMNS = [
    "model", "vector", "alpha", "eval", "item_id", "prompt",
    "tokens", "eg_score", "rt_score",
    "cc_hedging_score", "ih_abstention_score",
    "generation_preview", "generation_full",
]

ALL_COLUMNS = AUTO_COLUMNS + REVIEW_COLUMNS


@dataclass
class ReviewItem:
    """One row in the review CSV. Mutable fields are human_* + flags + notes."""
    model: str = ""
    vector: str = ""
    alpha: float = 0.0
    eval: str = ""
    item_id: str = ""
    prompt: str = ""
    tokens: int = 0
    eg_score: float = 0.0
    rt_score: float = 0.0
    cc_hedging_score: float = 0.0
    ih_abstention_score: float = 0.0
    generation_preview: str = ""
    generation_full: str = ""

    # Review fields — empty string = not yet reviewed
    human_cc_1to5: str = ""
    human_ih_1to5: str = ""
    human_eg_1to5: str = ""
    human_rt_1to5: str = ""
    gaming_flag: str = ""
    degenerate_flag: str = ""
    notes: str = ""
    reviewer: str = ""
    reviewed_at: str = ""

    @property
    def is_reviewed(self) -> bool:
        return bool(self.human_cc_1to5 and self.human_ih_1to5
                    and self.human_eg_1to5 and self.human_rt_1to5)

    @property
    def primary_key(self) -> str:
        """Unique key: model + vector + eval + item_id."""
        return f"{self.model}|{self.vector}|{self.eval}|{self.item_id}"


class ReviewStore:
    """CSV-backed review item store. Loads the whole CSV into memory on init;
    writes atomically on save."""

    def __init__(self, csv_path: Path):
        self.csv_path = Path(csv_path)
        self._items: list[ReviewItem] = []
        self._index: dict[str, int] = {}  # primary_key → list index
        self._load()

    def _load(self):
        self._items = []
        self._index = {}
        if not self.csv_path.exists():
            return
        df = pd.read_csv(self.csv_path, keep_default_na=False, dtype=str)
        for _, row in df.iterrows():
            d = {}
            for c in ALL_COLUMNS:
                v = row.get(c, "")
                if c in ("alpha", "tokens", "eg_score", "rt_score",
                         "cc_hedging_score", "ih_abstention_score"):
                    try:
                        d[c] = float(v) if v not in ("", "nan") else 0.0
                        if c == "tokens":
                            d[c] = int(d[c])
                    except (ValueError, TypeError):
                        d[c] = 0.0 if c != "tokens" else 0
                else:
                    d[c] = str(v) if v else ""
            item = ReviewItem(**d)
            self._index[item.primary_key] = len(self._items)
            self._items.append(item)

    def save(self):
        """Atomic write via temp file."""
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.csv_path.with_suffix(".tmp")
        with open(tmp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ALL_COLUMNS)
            writer.writeheader()
            for item in self._items:
                writer.writerow(asdict(item))
        os.replace(tmp, self.csv_path)

    def __iter__(self) -> Iterator[ReviewItem]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def get_by_index(self, idx: int) -> Optional[ReviewItem]:
        if 0 <= idx < len(self._items):
            return self._items[idx]
        return None

    def get_by_key(self, primary_key: str) -> Optional[ReviewItem]:
        idx = self._index.get(primary_key)
        return self._items[idx] if idx is not None else None

    def update(self, primary_key: str, **fields) -> bool:
        """Update an item's review fields; returns True if item exists."""
        idx = self._index.get(primary_key)
        if idx is None:
            return False
        item = self._items[idx]
        for k, v in fields.items():
            if hasattr(item, k):
                setattr(item, k, v)
        item.reviewed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return True

    def progress_stats(self) -> dict:
        """Count reviewed vs total, grouped by model / vector / eval."""
        total = len(self._items)
        reviewed = sum(1 for i in self._items if i.is_reviewed)
        by_cell = {}
        for i in self._items:
            k = (i.model, i.vector, i.eval)
            d = by_cell.setdefault(k, {"total": 0, "reviewed": 0})
            d["total"] += 1
            if i.is_reviewed:
                d["reviewed"] += 1
        return {
            "total": total,
            "reviewed": reviewed,
            "pct": (100.0 * reviewed / total) if total else 0.0,
            "by_cell": by_cell,
        }

    def next_unreviewed(self, from_idx: int = 0) -> Optional[int]:
        """Return index of next unreviewed item from `from_idx`, else None."""
        for i in range(max(from_idx, 0), len(self._items)):
            if not self._items[i].is_reviewed:
                return i
        # Wrap around to beginning
        for i in range(0, max(from_idx, 0)):
            if not self._items[i].is_reviewed:
                return i
        return None


def build_review_csv_from_specificity(
    spec_csv_path: Path,
    review_csv_path: Path,
    overwrite: bool = False,
) -> int:
    """Build a review CSV from a specificity_matrix all_generations_*.csv.

    Creates new review rows for each generation in the source CSV. If review_csv_path
    already has rows, merges (keeps existing review fields) unless overwrite=True.

    Returns number of items in the review CSV after merge.
    """
    spec_csv_path = Path(spec_csv_path)
    review_csv_path = Path(review_csv_path)

    spec_df = pd.read_csv(spec_csv_path, keep_default_na=False, dtype=str)

    # Existing review CSV (if any)
    existing = {}
    if review_csv_path.exists() and not overwrite:
        existing_store = ReviewStore(review_csv_path)
        for item in existing_store:
            existing[item.primary_key] = item

    # Build fresh store — we'll rebuild from spec_df, reusing any preserved
    # review fields from `existing` where primary keys match.
    store = ReviewStore(review_csv_path)
    store._items = []
    store._index = {}

    for _, row in spec_df.iterrows():
        # Construct primary key
        key = f"{row.get('model','')}|{row.get('vector','')}|{row.get('eval','')}|{row.get('item_id','')}"
        if key in existing:
            # Keep existing review fields, update auto fields
            item = existing[key]
            for c in AUTO_COLUMNS:
                if c in row:
                    v = row[c]
                    if c == "tokens":
                        try:
                            setattr(item, c, int(float(v)) if v else 0)
                        except (ValueError, TypeError):
                            setattr(item, c, 0)
                    elif c in ("alpha", "eg_score", "rt_score", "cc_hedging_score", "ih_abstention_score"):
                        try:
                            setattr(item, c, float(v) if v else 0.0)
                        except (ValueError, TypeError):
                            setattr(item, c, 0.0)
                    else:
                        setattr(item, c, str(v))
        else:
            fields = {}
            for c in AUTO_COLUMNS:
                v = row.get(c, "")
                if c == "tokens":
                    try:
                        fields[c] = int(float(v)) if v else 0
                    except (ValueError, TypeError):
                        fields[c] = 0
                elif c in ("alpha", "eg_score", "rt_score", "cc_hedging_score", "ih_abstention_score"):
                    try:
                        fields[c] = float(v) if v else 0.0
                    except (ValueError, TypeError):
                        fields[c] = 0.0
                else:
                    fields[c] = str(v)
            item = ReviewItem(**fields)

        store._index[item.primary_key] = len(store._items)
        store._items.append(item)

    store.save()
    return len(store)


if __name__ == "__main__":
    # Sanity test: write + read a toy review CSV
    import tempfile
    tmpdir = Path(tempfile.mkdtemp())
    csv_p = tmpdir / "test_review.csv"

    store = ReviewStore(csv_p)
    item = ReviewItem(
        model="qwen3-4b", vector="EG_L20", alpha=12, eval="eg-eval",
        item_id="eg-p01", prompt="test prompt", tokens=150,
        eg_score=10.5, rt_score=2.1, cc_hedging_score=1.0, ih_abstention_score=0.5,
        generation_preview="test gen...", generation_full="test generation full text",
    )
    store._items.append(item)
    store._index[item.primary_key] = 0
    store.save()

    store2 = ReviewStore(csv_p)
    print(f"loaded {len(store2)} items")
    assert len(store2) == 1
    assert not store2._items[0].is_reviewed

    store2.update("qwen3-4b|EG_L20|eg-eval|eg-p01",
                  human_eg_1to5="5", human_cc_1to5="1", human_ih_1to5="1", human_rt_1to5="2",
                  gaming_flag="no", degenerate_flag="no", notes="test note",
                  reviewer="claude")
    store2.save()

    store3 = ReviewStore(csv_p)
    assert store3._items[0].is_reviewed
    print(f"review saved: human_eg={store3._items[0].human_eg_1to5}, notes={store3._items[0].notes}")
    stats = store3.progress_stats()
    print(f"progress: {stats['reviewed']}/{stats['total']} ({stats['pct']:.0f}%)")

    import shutil
    shutil.rmtree(tmpdir)
    print("storage.py smoke test OK")
