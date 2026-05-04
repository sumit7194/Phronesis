"""
Unit tests for tool_use_harness — searcher abstraction, parsing, formatting.

Does NOT load a model — covers the parts of the harness that don't need GPU.
The full ToolUseRunner.run_trajectory loop is exercised by an integration test
on the VM (separate file, not committed here because it needs the model).

Run:
    python -m pytest mvp/tests/test_tool_use_harness.py -v
or:
    python mvp/tests/test_tool_use_harness.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Make `import tool_use_harness` resolve when running from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tool_use_harness import (
    CachedSearcher,
    MockSearcher,
    SearchResult,
    Searcher,
    extract_thinking_and_answer,
    find_last_search_query,
    format_results,
)


class TestMockSearcher(unittest.TestCase):
    def test_exact_query_match(self):
        m = MockSearcher(default_data={
            "pumpkin record": [
                {"title": "T", "snippet": "S", "url": "u"},
            ]
        })
        results = m.search("pumpkin record", k=3)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "T")

    def test_substring_fallback(self):
        m = MockSearcher(default_data={
            "world record heaviest pumpkin": [
                {"title": "T", "snippet": "S", "url": "u"},
            ]
        })
        # Query is a substring of the cached key (in either direction)
        results = m.search("heaviest pumpkin", k=3)
        self.assertEqual(len(results), 1)

    def test_no_match_returns_empty(self):
        m = MockSearcher(default_data={"abc": [{"title": "x", "snippet": "y", "url": "z"}]})
        self.assertEqual(m.search("totally different query"), [])

    def test_k_limit(self):
        m = MockSearcher(default_data={
            "q": [
                {"title": f"T{i}", "snippet": "s", "url": "u"} for i in range(10)
            ]
        })
        results = m.search("q", k=3)
        self.assertEqual(len(results), 3)


class _CountingSearcher(Searcher):
    """Wraps a MockSearcher; counts how many times search() was called."""
    def __init__(self, inner: MockSearcher):
        self.inner = inner
        self.calls = 0

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        self.calls += 1
        return self.inner.search(query, k=k)


class TestCachedSearcher(unittest.TestCase):
    def test_caches_after_first_call(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "cache.json"
            inner = _CountingSearcher(MockSearcher(default_data={
                "q": [{"title": "T", "snippet": "S", "url": "u"}]
            }))
            cached = CachedSearcher(inner, cache_path=cache_path)

            r1 = cached.search("q", k=3)
            r2 = cached.search("q", k=3)
            self.assertEqual(inner.calls, 1, "second call should hit the cache")
            self.assertEqual(r1[0].title, r2[0].title)
            self.assertTrue(cache_path.exists())

    def test_cache_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "cache.json"
            inner1 = _CountingSearcher(MockSearcher(default_data={
                "q": [{"title": "T", "snippet": "S", "url": "u"}]
            }))
            CachedSearcher(inner1, cache_path).search("q", k=3)

            # New inner that would error if called — the cache must serve from disk.
            class _BoomSearcher(Searcher):
                def search(self, query, k=3):
                    raise AssertionError("inner.search must not be called when cached")

            cached2 = CachedSearcher(_BoomSearcher(), cache_path=cache_path)
            r = cached2.search("q", k=3)
            self.assertEqual(r[0].title, "T")

    def test_cache_key_includes_k(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "cache.json"
            inner = _CountingSearcher(MockSearcher(default_data={
                "q": [
                    {"title": f"T{i}", "snippet": "s", "url": "u"} for i in range(5)
                ]
            }))
            cached = CachedSearcher(inner, cache_path=cache_path)
            cached.search("q", k=3)
            cached.search("q", k=5)
            self.assertEqual(inner.calls, 2,
                             "different k values should be cached separately")


class TestStopParsing(unittest.TestCase):
    def test_finds_query_in_simple_segment(self):
        text = "I will search now. <search>pumpkin world record</search>"
        self.assertEqual(find_last_search_query(text), "pumpkin world record")

    def test_returns_last_query_when_multiple(self):
        text = "<search>first</search> bla <search>second</search>"
        self.assertEqual(find_last_search_query(text), "second")

    def test_returns_none_when_no_search(self):
        self.assertIsNone(find_last_search_query("just some text"))

    def test_handles_multiline_query(self):
        text = "<search>multi\nline\nquery</search>"
        self.assertEqual(find_last_search_query(text), "multi\nline\nquery")


class TestFormatResults(unittest.TestCase):
    def test_format_three_results(self):
        rs = [
            SearchResult(title="A", snippet="alpha", url="https://a"),
            SearchResult(title="B", snippet="beta", url="https://b"),
            SearchResult(title="C", snippet="gamma", url="https://c"),
        ]
        block = format_results(rs)
        self.assertTrue(block.startswith("<result>"))
        self.assertTrue(block.rstrip().endswith("</result>"))
        self.assertIn("1. A — alpha (https://a)", block)
        self.assertIn("2. B — beta (https://b)", block)
        self.assertIn("3. C — gamma (https://c)", block)

    def test_format_empty(self):
        block = format_results([])
        self.assertIn("(no results found)", block)


class TestExtractThinking(unittest.TestCase):
    def test_extracts_think_block(self):
        text = "<think>internal reasoning here</think>The answer is 42."
        thinking, answer = extract_thinking_and_answer(text)
        self.assertEqual(thinking, "internal reasoning here")
        self.assertEqual(answer, "The answer is 42.")

    def test_no_think_block(self):
        text = "Just an answer with no thinking."
        thinking, answer = extract_thinking_and_answer(text)
        self.assertEqual(thinking, "")
        self.assertEqual(answer, "Just an answer with no thinking.")

    def test_handles_multiline_thinking(self):
        text = "<think>\nstep 1\nstep 2\n</think>\n\nfinal"
        thinking, answer = extract_thinking_and_answer(text)
        self.assertEqual(thinking, "step 1\nstep 2")
        self.assertEqual(answer, "final")


if __name__ == "__main__":
    unittest.main(verbosity=2)
