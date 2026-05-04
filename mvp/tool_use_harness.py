"""
Phronesis — Tool-use harness for testing virtue steering on knowledge-gap prompts.

Tests whether virtue-steered models (v_IH, v_EG, etc.) call a web-search tool
more appropriately than baseline / random-vector-steered models on prompts where
the model has partial parametric knowledge that biases toward confabulation.

Architecture:
  - Generate with stop_strings=["</search>"] (and EOS).
  - When stopped on </search>, parse the trailing <search>QUERY</search>,
    run the searcher, append a <result>...</result> block to the prompt,
    and call generate() again on the extended prompt.
  - Loop until: model emits EOS without another search, hits max_searches,
    or hits a global max-tokens budget.
  - Steering hook stays attached for the full trajectory (re-applies on
    every generate call automatically).
  - Search results are cached on disk keyed by query string, so the same
    prompt yields identical results across conditions (baseline / steered
    / random-steered). This is the dominant noise source if you skip it.

Searcher abstraction:
  - MockSearcher: returns canned results from a JSON dict (offline, deterministic).
  - SerperSearcher: hits Serper API (https://serper.dev). Requires SERPER_API_KEY env.
  - BraveSearcher: hits Brave Search API. Requires BRAVE_SEARCH_API_KEY env.
  - CachedSearcher: wraps any of the above; transparent disk cache.

Usage (called by run_tool_experiment.py; can also be used standalone):

    from tool_use_harness import (
        ToolUseRunner, CachedSearcher, MockSearcher, SerperSearcher,
    )

    searcher = CachedSearcher(SerperSearcher(), cache_path="search_cache.json")
    runner = ToolUseRunner(
        model_name="qwen3-4b",
        searcher=searcher,
        system_prompt_path="tool_use_system_prompt.txt",
        max_searches=5,
        max_total_tokens=2048,
    )
    runner.load_model()

    # Baseline
    traj = runner.run_trajectory(prompt="...", condition_label="baseline")

    # Steered
    runner.attach_steering(vector_path="...layer_17_virtue_vector.npy", layer=17, alpha=8.0)
    traj = runner.run_trajectory(prompt="...", condition_label="v_IH_steered")
    runner.detach_steering()
"""

from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np

# torch / steer / utils are imported lazily inside ToolUseRunner methods so
# the searcher + parsing utilities are usable without a torch install (lets
# unit tests run on machines that don't have the model deps).


# ─── Searcher abstraction ────────────────────────────────────────────────────


@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str

    def as_dict(self) -> dict[str, str]:
        return {"title": self.title, "snippet": self.snippet, "url": self.url}


class Searcher(ABC):
    """Returns top-k results for a query."""

    @abstractmethod
    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        ...


class MockSearcher(Searcher):
    """Returns canned results from a JSON file mapping query -> [SearchResult, ...].

    For offline development and unit tests. The user pre-populates the file
    with the queries they expect their prompts to elicit.
    """

    def __init__(self, mock_data_path: str | Path | None = None,
                 default_data: dict[str, list[dict]] | None = None):
        if mock_data_path and Path(mock_data_path).exists():
            with open(mock_data_path) as f:
                self._data = json.load(f)
        else:
            self._data = default_data or {}

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        results = self._data.get(query, [])
        if not results:
            for q, r in self._data.items():
                if query.lower() in q.lower() or q.lower() in query.lower():
                    results = r
                    break
        return [SearchResult(**r) for r in results[:k]]


class SerperSearcher(Searcher):
    """https://serper.dev — Google results JSON, $5 / 2500 queries."""

    API_URL = "https://google.serper.dev/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Serper API key required: set SERPER_API_KEY or pass api_key=."
            )

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        import requests

        resp = requests.post(
            self.API_URL,
            headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
            json={"q": query, "num": k},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        organic = data.get("organic", [])[:k]
        return [
            SearchResult(
                title=r.get("title", ""),
                snippet=r.get("snippet", ""),
                url=r.get("link", ""),
            )
            for r in organic
        ]


class BraveSearcher(Searcher):
    """https://brave.com/search/api/ — Brave Search results JSON."""

    API_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Brave Search API key required: set BRAVE_SEARCH_API_KEY or pass api_key=."
            )

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        import requests

        resp = requests.get(
            self.API_URL,
            headers={"X-Subscription-Token": self.api_key, "Accept": "application/json"},
            params={"q": query, "count": k},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        web = data.get("web", {}).get("results", [])[:k]
        return [
            SearchResult(
                title=r.get("title", ""),
                snippet=r.get("description", ""),
                url=r.get("url", ""),
            )
            for r in web
        ]


class CachedSearcher(Searcher):
    """Disk-cached wrapper. Identical query → identical results across conditions."""

    def __init__(self, inner: Searcher, cache_path: str | Path):
        self.inner = inner
        self.cache_path = Path(cache_path)
        self._cache: dict[str, list[dict]] = {}
        if self.cache_path.exists():
            with open(self.cache_path) as f:
                self._cache = json.load(f)

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        cache_key = f"{query}::k={k}"
        if cache_key in self._cache:
            return [SearchResult(**r) for r in self._cache[cache_key]]
        results = self.inner.search(query, k=k)
        self._cache[cache_key] = [r.as_dict() for r in results]
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self._cache, f, indent=2)
        return results


# ─── Result formatting ───────────────────────────────────────────────────────


def format_results(results: list[SearchResult]) -> str:
    """Format search results as a <result>...</result> block for the model."""
    if not results:
        return "<result>\n(no results found)\n</result>"
    lines = ["<result>"]
    for i, r in enumerate(results, start=1):
        title = r.title.strip() or "(untitled)"
        snippet = r.snippet.strip().replace("\n", " ")
        url = r.url.strip()
        lines.append(f"{i}. {title} — {snippet} ({url})")
    lines.append("</result>")
    return "\n".join(lines)


# ─── Stop-string parsing ─────────────────────────────────────────────────────


SEARCH_OPEN_TAG = "<search>"
SEARCH_CLOSE_TAG = "</search>"
SEARCH_RE = re.compile(r"<search>(.*?)</search>", re.DOTALL)


def find_last_search_query(text: str) -> str | None:
    """Extract the final <search>...</search> query from a generated segment.

    The generation is configured to stop on </search>, so the trailing tag is
    expected to be at the very end. We use a regex so this is robust to
    weirdness (e.g. multiple search calls in one segment, partial closures).
    """
    matches = list(SEARCH_RE.finditer(text))
    if not matches:
        return None
    return matches[-1].group(1).strip()


# ─── Trajectory recorder ─────────────────────────────────────────────────────


@dataclass
class Segment:
    type: str  # "model" | "search_query" | "search_results"
    text: str = ""
    results: list[dict] = field(default_factory=list)
    stopped_on: str | None = None  # for model segments: "search_close" | "eos" | "max_tokens"
    tokens_generated: int | None = None


@dataclass
class Trajectory:
    prompt_id: str
    condition_label: str
    config: dict
    system_prompt: str
    user_prompt: str
    segments: list[Segment] = field(default_factory=list)
    tool_call_count: int = 0
    termination_reason: str = "unknown"  # "eos" | "max_searches" | "max_total_tokens"
    final_answer: str = ""
    thinking_trace: str = ""
    wall_time_seconds: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["segments"] = [asdict(s) for s in self.segments]
        return d


# ─── Generation core ─────────────────────────────────────────────────────────


THINK_OPEN = "<think>"
THINK_CLOSE = "</think>"


def extract_thinking_and_answer(full_text: str) -> tuple[str, str]:
    """Pull the contents of <think>...</think> if present; rest is answer."""
    if THINK_OPEN in full_text and THINK_CLOSE in full_text:
        m = re.search(r"<think>(.*?)</think>", full_text, re.DOTALL)
        if m:
            thinking = m.group(1).strip()
            answer = (full_text[:m.start()] + full_text[m.end():]).strip()
            return thinking, answer
    return "", full_text.strip()


class ToolUseRunner:
    """Runs tool-augmented generation with optional activation steering.

    Lifecycle:
        runner = ToolUseRunner(...)
        runner.load_model()                    # once
        # per condition:
        runner.attach_steering(...)            # optional
        for prompt in prompts:
            traj = runner.run_trajectory(...)
        runner.detach_steering()
    """

    def __init__(
        self,
        model_name: str,
        searcher: Searcher,
        system_prompt_path: str | Path,
        max_searches: int = 5,
        max_total_tokens: int = 2048,
        max_tokens_per_segment: int = 512,
        top_k_results: int = 3,
        device: str | None = None,
    ):
        self.model_name = model_name
        self.searcher = searcher
        self.system_prompt = Path(system_prompt_path).read_text()
        self.max_searches = max_searches
        self.max_total_tokens = max_total_tokens
        self.max_tokens_per_segment = max_tokens_per_segment
        self.top_k_results = top_k_results
        self.device_arg = device

        self.model = None
        self.tokenizer = None
        self.device = None
        self._steering_hook: AdditiveSteeringHook | None = None
        self._steering_meta: dict | None = None

        from utils import MODEL_CONFIGS  # lazy: requires torch
        self.config = MODEL_CONFIGS[model_name]
        self.thinking_enabled = self.config.get("thinking", False)

    # ─── Model lifecycle ─────────────────────────────────────────────────

    def load_model(self):
        from utils import load_model as _load_model  # lazy
        self.model, self.tokenizer, self.device = _load_model(
            self.model_name, device=self.device_arg
        )

    def attach_steering(self, vector_path: str | Path, layer: int, alpha: float,
                        label: str = "steered"):
        from steer import AdditiveSteeringHook  # lazy: requires torch
        if self._steering_hook is not None:
            raise RuntimeError("Steering already attached. Call detach_steering() first.")
        v = np.load(vector_path)
        self._steering_hook = AdditiveSteeringHook(
            layer_idx=layer, virtue_vector=v, alpha=alpha
        )
        self._steering_hook.attach(self.model)
        self._steering_meta = {
            "vector_path": str(vector_path),
            "layer": layer,
            "alpha": alpha,
            "label": label,
            "vector_shape": list(v.shape),
            "vector_norm": float(np.linalg.norm(v)),
        }

    def detach_steering(self):
        if self._steering_hook is not None:
            self._steering_hook.detach()
            self._steering_hook = None
            self._steering_meta = None

    # ─── Prompt building ─────────────────────────────────────────────────

    def _build_initial_prompt_text(self, user_prompt: str) -> str:
        """Apply chat template to the (system, user) pair and add gen prompt."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs = {}
        if self.thinking_enabled:
            kwargs["enable_thinking"] = True
        return self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, **kwargs
        )

    # ─── Generation step ─────────────────────────────────────────────────

    def _generate_segment(self, prompt_text: str, max_new_tokens: int) -> tuple[str, str, int]:
        """Generate until </search> or EOS. Returns (new_text, stopped_on, tokens_generated).

        stopped_on ∈ {"search_close", "eos", "max_tokens"}.
        """
        import torch  # lazy
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.device)
        prompt_len = inputs["input_ids"].shape[1]

        gen_kwargs = dict(
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
        )
        # stop_strings requires HF transformers >= 4.43; we pass it via tokenizer.
        try:
            with torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    stop_strings=[SEARCH_CLOSE_TAG],
                    tokenizer=self.tokenizer,
                    **gen_kwargs,
                )
        except (TypeError, ValueError):
            # Fallback for older transformers: generate without stop_strings,
            # then truncate at first </search> if present.
            with torch.no_grad():
                out = self.model.generate(**inputs, **gen_kwargs)

        new_tokens = out[0][prompt_len:]
        tokens_generated = int(new_tokens.shape[0])
        new_text = self.tokenizer.decode(new_tokens, skip_special_tokens=False)

        # Strip trailing pad/eos tokens from the decoded string
        for tok in [self.tokenizer.eos_token, self.tokenizer.pad_token]:
            if tok and new_text.endswith(tok):
                new_text = new_text[: -len(tok)]

        # Determine stop reason. Trim to include only up through </search> if present.
        if SEARCH_CLOSE_TAG in new_text:
            idx = new_text.rindex(SEARCH_CLOSE_TAG) + len(SEARCH_CLOSE_TAG)
            new_text = new_text[:idx]
            stopped_on = "search_close"
        elif tokens_generated >= max_new_tokens:
            stopped_on = "max_tokens"
        else:
            stopped_on = "eos"

        return new_text, stopped_on, tokens_generated

    # ─── Trajectory ──────────────────────────────────────────────────────

    def run_trajectory(
        self,
        prompt: str,
        prompt_id: str = "",
        condition_label: str = "baseline",
    ) -> Trajectory:
        """Run a single tool-augmented generation trajectory for one prompt."""

        if self.model is None:
            raise RuntimeError("Call load_model() first.")

        cfg = {
            "model": self.model_name,
            "max_searches": self.max_searches,
            "max_total_tokens": self.max_total_tokens,
            "max_tokens_per_segment": self.max_tokens_per_segment,
            "top_k_results": self.top_k_results,
            "thinking_enabled": self.thinking_enabled,
            "steering": self._steering_meta,
        }
        traj = Trajectory(
            prompt_id=prompt_id or "(unnamed)",
            condition_label=condition_label,
            config=cfg,
            system_prompt=self.system_prompt,
            user_prompt=prompt,
        )

        t_start = time.time()

        try:
            current_text = self._build_initial_prompt_text(prompt)
            tokens_used = 0
            tool_calls = 0

            while True:
                remaining = self.max_total_tokens - tokens_used
                if remaining <= 0:
                    traj.termination_reason = "max_total_tokens"
                    break
                seg_budget = min(self.max_tokens_per_segment, remaining)

                new_text, stopped_on, tokens_generated = self._generate_segment(
                    current_text, max_new_tokens=seg_budget
                )
                tokens_used += tokens_generated
                traj.segments.append(Segment(
                    type="model",
                    text=new_text,
                    stopped_on=stopped_on,
                    tokens_generated=tokens_generated,
                ))
                current_text = current_text + new_text

                if stopped_on == "eos":
                    traj.termination_reason = "eos"
                    break
                if stopped_on == "max_tokens":
                    traj.termination_reason = "max_total_tokens"
                    break

                # stopped_on == "search_close": parse, search, append result, loop.
                query = find_last_search_query(new_text)
                if query is None:
                    # Stop tag matched but no parseable query — treat as EOS.
                    traj.termination_reason = "malformed_search_tag"
                    break

                tool_calls += 1
                traj.segments.append(Segment(type="search_query", text=query))

                if tool_calls > self.max_searches:
                    traj.termination_reason = "max_searches"
                    break

                results = self.searcher.search(query, k=self.top_k_results)
                results_block = format_results(results)
                traj.segments.append(Segment(
                    type="search_results",
                    text=results_block,
                    results=[r.as_dict() for r in results],
                ))
                current_text = current_text + "\n" + results_block + "\n"

            traj.tool_call_count = tool_calls

            # Reconstruct final answer + thinking trace from concatenated model segments.
            full_model_text = "".join(
                s.text for s in traj.segments if s.type == "model"
            )
            thinking, answer = extract_thinking_and_answer(full_model_text)
            traj.thinking_trace = thinking

            # Strip any <search>...</search> and <result>...</result> tags from answer.
            answer = SEARCH_RE.sub("", answer)
            answer = re.sub(r"<result>.*?</result>", "", answer, flags=re.DOTALL)
            traj.final_answer = answer.strip()

        except Exception as e:
            traj.error = f"{type(e).__name__}: {e}"
            traj.termination_reason = "error"

        traj.wall_time_seconds = time.time() - t_start
        return traj

    # ─── Cleanup ─────────────────────────────────────────────────────────

    def close(self):
        self.detach_steering()
        # Don't free the model; caller may want to reuse for another condition.


# ─── Convenience: dump trajectories to a JSON-lines file ────────────────────


def dump_trajectories_jsonl(trajectories: list[Trajectory], path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for t in trajectories:
            f.write(json.dumps(t.to_dict(), ensure_ascii=False) + "\n")
