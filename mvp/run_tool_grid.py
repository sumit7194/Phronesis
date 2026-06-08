"""
Phronesis — checkpointed, resumable tool-use GRID runner (Path B / 2026-06).

Wraps ToolUseRunner (tool_use_harness.py, the <search>...</search> protocol).
Loads a model once, then sweeps conditions (baseline / virtue-steered /
matched-norm random x N seeds). Key difference from run_tool_experiment.py:
each condition's trajectories are written to their own JSONL *the moment the
condition finishes*, with a `<label>.done` marker. On a preemptible VM, a kill
only loses the in-progress condition; re-running the SAME command resumes
(skips conditions whose .done marker exists).

Metric of interest: tool-INVOKE rate (did the model emit >=1 <search>?), overall
and per prompt-category. Final-answer quality is NOT auto-scored (by design).

Usage on the VM (run from ~/phronesis_run/mvp):
    source ~/phronesis_run/.venv/bin/activate
    python run_tool_grid.py \
        --config tool_grid_qwen25.json \
        --prompts ../corpus/eval-prompts/tool-use-v1.json \
        --output results/tool_use_grid/qwen25 \
        --searcher mock --device cuda
    # smoke test first: add  --limit 3
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from tool_use_harness import (
    BraveSearcher,
    CachedSearcher,
    MockSearcher,
    Searcher,
    SearchResult,
    SerperSearcher,
    ToolUseRunner,
)


class DDGSSearcher(Searcher):
    """Real web search via DuckDuckGo (ddgs package). Returns [] on any error
    so a flaky/blocked query degrades gracefully rather than crashing a run."""

    def search(self, query, k=3):
        from ddgs import DDGS
        try:
            results = list(DDGS().text(query, max_results=k))
        except Exception:
            return []
        out = []
        for r in results[:k]:
            out.append(SearchResult(
                title=r.get("title", ""),
                snippet=r.get("body", r.get("snippet", "")),
                url=r.get("href", r.get("url", "")),
            ))
        return out


def build_searcher(kind, cache_path, mock_data_path=None):
    kind = kind.lower()
    if kind == "mock":
        inner = MockSearcher(mock_data_path=mock_data_path)
    elif kind == "ddgs":
        inner = DDGSSearcher()
    elif kind == "serper":
        inner = SerperSearcher()
    elif kind == "brave":
        inner = BraveSearcher()
    else:
        raise ValueError("unknown searcher: %r" % kind)
    return CachedSearcher(inner, cache_path=cache_path)


def make_random_vector(reference_vector_path, seed, output_path):
    """Random direction, same shape + L2 norm as the reference. (The hook
    re-normalizes to unit anyway, so only the direction matters; norm-match is
    belt-and-suspenders.)"""
    ref = np.load(reference_vector_path)
    rng = np.random.default_rng(seed)
    rand = rng.standard_normal(ref.shape).astype(ref.dtype)
    rand = rand / (np.linalg.norm(rand) + 1e-10) * np.linalg.norm(ref)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, rand)
    return output_path


def summarize(label, traj_dicts, prompts_by_id):
    n = len(traj_dicts)
    if n == 0:
        return {"label": label, "n": 0}
    invoked = [1 if d.get("tool_call_count", 0) > 0 else 0 for d in traj_dicts]
    cat_inv = defaultdict(list)
    for d in traj_dicts:
        cat = prompts_by_id.get(d.get("prompt_id"), {}).get("category", "?")
        cat_inv[cat].append(1 if d.get("tool_call_count", 0) > 0 else 0)
    by_cat = {
        c: {"n": len(v), "invoke_rate": round(sum(v) / len(v), 4)}
        for c, v in sorted(cat_inv.items())
    }
    return {
        "label": label,
        "n": n,
        "invoke_rate_overall": round(sum(invoked) / n, 4),
        "mean_tool_calls": round(float(np.mean([d.get("tool_call_count", 0) for d in traj_dicts])), 3),
        "errors": sum(1 for d in traj_dicts if d.get("error")),
        "termination_reasons": dict(Counter(d.get("termination_reason") for d in traj_dicts)),
        "mean_wall_s": round(float(np.mean([d.get("wall_time_seconds", 0.0) for d in traj_dicts])), 1),
        "by_category": by_cat,
    }


def read_jsonl(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--searcher", default="mock", choices=["mock", "ddgs", "serper", "brave"])
    ap.add_argument("--mock-data", default=None)
    ap.add_argument("--device", default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    config = json.load(open(args.config))
    prompts = json.load(open(args.prompts))
    if args.limit:
        prompts = prompts[: args.limit]
    prompts_by_id = {p.get("id", "p%d" % i): p for i, p in enumerate(prompts)}

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    json.dump(config, open(out / "config_snapshot.json", "w"), indent=2)

    searcher = build_searcher(
        args.searcher, cache_path=out / "search_cache.json", mock_data_path=args.mock_data
    )

    # Pre-generate random-control vectors (deterministic per seed).
    for cond in config["conditions"]:
        s = cond.get("steering") or {}
        if s.get("kind") == "random":
            seed = int(s.get("seed", 42))
            vp = out / ("random_%s_seed%d.npy" % (cond["label"], seed))
            make_random_vector(s["reference_vector"], seed, vp)
            s["vector_path"] = str(vp)

    runner = ToolUseRunner(
        model_name=config["model"],
        searcher=searcher,
        system_prompt_path=config.get(
            "system_prompt_path", str(Path(__file__).parent / "tool_use_system_prompt.txt")
        ),
        max_searches=config.get("max_searches", 3),
        max_total_tokens=config.get("max_total_tokens", 2048),
        max_tokens_per_segment=config.get("max_tokens_per_segment", 512),
        top_k_results=config.get("top_k_results", 3),
        device=args.device,
    )
    print("loading model: %s ..." % config["model"], flush=True)
    runner.load_model()

    summaries = []
    t_start = time.time()

    for cond in config["conditions"]:
        label = cond["label"]
        cond_path = out / ("%s.jsonl" % label)
        done_marker = out / ("%s.done" % label)

        if done_marker.exists() and cond_path.exists():
            print("[skip] %s (already done)" % label, flush=True)
            summaries.append(summarize(label, read_jsonl(cond_path), prompts_by_id))
            continue

        s = cond.get("steering")
        if s:
            runner.attach_steering(
                vector_path=s["vector_path"], layer=int(s["layer"]),
                alpha=float(s["alpha"]), label=label, phase=s.get("phase", "all"),
            )
            print("\n[%s] steering L%s a=%s phase=%s (%s)" % (label, s["layer"], s["alpha"], s.get("phase", "all"), s.get("kind")), flush=True)
        else:
            print("\n[%s] baseline (no steering)" % label, flush=True)

        traj_dicts = []
        f = open(cond_path, "w")
        try:
            for i, p in enumerate(prompts):
                pid = p.get("id", "p%d" % i)
                t0 = time.time()
                traj = runner.run_trajectory(
                    prompt=p["prompt"], prompt_id=pid, condition_label=label
                )
                d = traj.to_dict()
                traj_dicts.append(d)
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
                f.flush()
                json.dump(
                    {"condition": label, "prompt_id": pid, "idx": i + 1,
                     "total": len(prompts), "invoked": traj.tool_call_count > 0,
                     "term": traj.termination_reason},
                    open(out / "live_status.json", "w"),
                )
                print("  [%d/%d] %-26s invoked=%s term=%-16s %.1fs%s" % (
                    i + 1, len(prompts), pid, traj.tool_call_count > 0,
                    traj.termination_reason, time.time() - t0,
                    ("  ERR:" + traj.error) if traj.error else ""), flush=True)
        finally:
            f.close()
            if s:
                runner.detach_steering()

        done_marker.write_text("ok")
        summaries.append(summarize(label, traj_dicts, prompts_by_id))

    runner.close()

    summary = {
        "config": config,
        "n_prompts": len(prompts),
        "total_wall_s": round(time.time() - t_start, 1),
        "per_condition": summaries,
    }
    json.dump(summary, open(out / "run_summary.json", "w"), indent=2)

    print("\n==================== GRID SUMMARY ====================", flush=True)
    for sd in summaries:
        if sd.get("n", 0) == 0:
            continue
        print("%-22s overall=%.0f%%  by-cat: %s" % (
            sd["label"], 100 * sd["invoke_rate_overall"],
            {c: ("%.0f%%" % (100 * v["invoke_rate"])) for c, v in sd["by_category"].items()},
        ), flush=True)
    print("total wall: %.1fs" % summary["total_wall_s"], flush=True)


if __name__ == "__main__":
    main()
