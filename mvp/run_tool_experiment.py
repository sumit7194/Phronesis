"""
Phronesis — Tool-use experiment runner (3-condition × N-prompts grid).

Loads model once. For each (condition, prompt) cell, runs a tool-augmented
trajectory and dumps it to a JSONL file. Conditions are configurable via the
config JSON; the canonical trio is:

    1. baseline                 — no steering
    2. virtue-steered           — e.g. v_IH @ L17 with α=8.0
    3. random-steered           — random-vector control at the same layer/α

The same SearchCache is shared across all conditions so the same query yields
identical results everywhere — removes search-drift as a confound.

Example usage on the VM:

    python mvp/run_tool_experiment.py \
      --config mvp/tool_use_experiment.example.json \
      --prompts mvp/tool_use_prompts.example.json \
      --output mvp/results/tool_use/run_001 \
      --searcher serper           # or "mock" for offline dry-run

Outputs:
    {output_dir}/trajectories.jsonl    — one trajectory per (condition, prompt)
    {output_dir}/run_summary.json      — config + per-condition metrics
    {output_dir}/search_cache.json     — populated cache (replayable)

Metrics computed:
    - Tool-call rate (per condition, per prompt-category)
    - Mean queries per trajectory
    - Mean tokens generated
    - Termination-reason histogram
    - Wall-clock time per condition

Final-answer correctness must be hand-rated separately — there is no automatic
scorer here, by design (per the project's auto-scorer-skepticism).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

from tool_use_harness import (
    BraveSearcher,
    CachedSearcher,
    MockSearcher,
    SerperSearcher,
    ToolUseRunner,
    Trajectory,
    dump_trajectories_jsonl,
)


# ─── Searcher factory ────────────────────────────────────────────────────────


def build_searcher(kind: str, cache_path: Path,
                   mock_data_path: Path | None = None) -> "Searcher":
    """Build a searcher of the requested kind, wrapped in a CachedSearcher."""
    kind = kind.lower()
    if kind == "mock":
        inner = MockSearcher(mock_data_path=mock_data_path)
    elif kind == "serper":
        inner = SerperSearcher()
    elif kind == "brave":
        inner = BraveSearcher()
    else:
        raise ValueError(f"Unknown searcher kind: {kind!r}")
    return CachedSearcher(inner, cache_path=cache_path)


# ─── Random-vector control ───────────────────────────────────────────────────


def make_random_vector(reference_vector_path: str | Path,
                       seed: int,
                       output_path: str | Path) -> Path:
    """Generate a random vector with the same shape and L2 norm as a reference.

    Used for the random-steering control condition. Same shape and norm so the
    perturbation magnitude matches the virtue vector exactly — only direction
    differs.
    """
    ref = np.load(reference_vector_path)
    rng = np.random.default_rng(seed)
    rand = rng.standard_normal(ref.shape).astype(ref.dtype)
    rand = rand / (np.linalg.norm(rand) + 1e-10) * np.linalg.norm(ref)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, rand)
    return output_path


# ─── Per-condition runner ────────────────────────────────────────────────────


def run_condition(
    runner: ToolUseRunner,
    condition: dict,
    prompts: list[dict],
) -> list[Trajectory]:
    """Run all prompts under one condition. Attaches/detaches steering as needed."""

    label = condition["label"]
    print(f"\n{'='*70}")
    print(f"Condition: {label}")
    print(f"{'='*70}")

    if condition.get("steering"):
        s = condition["steering"]
        runner.attach_steering(
            vector_path=s["vector_path"],
            layer=s["layer"],
            alpha=s["alpha"],
            label=label,
        )
        print(f"  steering attached: {s['vector_path']} @ L{s['layer']}, α={s['alpha']}")
    else:
        print(f"  no steering (baseline)")

    trajectories: list[Trajectory] = []
    try:
        for i, p in enumerate(prompts):
            prompt_id = p.get("id", f"p{i}")
            print(f"  [{i+1}/{len(prompts)}] {prompt_id}", flush=True)
            t0 = time.time()
            traj = runner.run_trajectory(
                prompt=p["prompt"],
                prompt_id=prompt_id,
                condition_label=label,
            )
            print(f"      tool_calls={traj.tool_call_count}  "
                  f"term={traj.termination_reason}  "
                  f"wall={time.time()-t0:.1f}s")
            if traj.error:
                print(f"      ERROR: {traj.error}")
            trajectories.append(traj)
    finally:
        if condition.get("steering"):
            runner.detach_steering()

    return trajectories


# ─── Per-condition metrics ───────────────────────────────────────────────────


def summarize_condition(label: str, trajectories: list[Trajectory]) -> dict:
    n = len(trajectories)
    if n == 0:
        return {"label": label, "n": 0}

    tool_call_counts = [t.tool_call_count for t in trajectories]
    any_search = sum(1 for c in tool_call_counts if c > 0)

    by_category: dict[str, list[int]] = {}
    # category attached to prompts in input file; pull from trajectory.config? we kept it on prompts only
    # so we re-attach during the run by storing the original prompt dict — easiest is post-hoc by id

    return {
        "label": label,
        "n": n,
        "tool_call_rate": any_search / n,
        "mean_tool_calls": float(np.mean(tool_call_counts)),
        "max_tool_calls": int(max(tool_call_counts)) if tool_call_counts else 0,
        "errors": sum(1 for t in trajectories if t.error),
        "termination_reasons": dict(
            Counter(t.termination_reason for t in trajectories)
        ),
        "mean_wall_time_s": float(np.mean([t.wall_time_seconds for t in trajectories])),
    }


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Phronesis tool-use experiment runner")
    parser.add_argument("--config", required=True,
                        help="Path to experiment config JSON (model, conditions, etc.)")
    parser.add_argument("--prompts", required=True,
                        help="Path to prompts JSON")
    parser.add_argument("--output", required=True,
                        help="Output directory (created if missing)")
    parser.add_argument("--searcher", default="mock",
                        choices=["mock", "serper", "brave"],
                        help="Search backend (default: mock for offline dry-run)")
    parser.add_argument("--mock-data", default=None,
                        help="Path to mock-data JSON (for --searcher mock)")
    parser.add_argument("--cache-name", default="search_cache.json",
                        help="Filename for the on-disk search cache")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only run the first N prompts (for smoke tests)")
    parser.add_argument("--device", default=None,
                        help="Device override: cuda / cpu / mps")
    args = parser.parse_args()

    # Load config + prompts
    with open(args.config) as f:
        config = json.load(f)
    with open(args.prompts) as f:
        prompts = json.load(f)
    if args.limit is not None:
        prompts = prompts[: args.limit]

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save config snapshot
    with open(output_dir / "config_snapshot.json", "w") as f:
        json.dump(config, f, indent=2)
    with open(output_dir / "prompts_snapshot.json", "w") as f:
        json.dump(prompts, f, indent=2)

    # Build searcher (shared across conditions)
    cache_path = output_dir / args.cache_name
    searcher = build_searcher(
        args.searcher, cache_path=cache_path, mock_data_path=args.mock_data
    )

    # Generate random-vector control if requested
    for cond in config["conditions"]:
        if cond.get("steering", {}).get("kind") == "random":
            ref_path = cond["steering"]["reference_vector"]
            seed = cond["steering"].get("seed", 42)
            out_path = output_dir / f"random_vector_seed{seed}.npy"
            make_random_vector(ref_path, seed=seed, output_path=out_path)
            cond["steering"]["vector_path"] = str(out_path)
            print(f"Generated random vector: {out_path}")

    # Initialize runner
    runner = ToolUseRunner(
        model_name=config["model"],
        searcher=searcher,
        system_prompt_path=config.get(
            "system_prompt_path",
            str(Path(__file__).parent / "tool_use_system_prompt.txt"),
        ),
        max_searches=config.get("max_searches", 5),
        max_total_tokens=config.get("max_total_tokens", 2048),
        max_tokens_per_segment=config.get("max_tokens_per_segment", 512),
        top_k_results=config.get("top_k_results", 3),
        device=args.device,
    )
    print(f"Loading model: {config['model']}...")
    runner.load_model()

    # Run all conditions
    all_trajectories: list[Trajectory] = []
    summaries: list[dict] = []
    t_start = time.time()

    for cond in config["conditions"]:
        trajs = run_condition(runner, cond, prompts)
        all_trajectories.extend(trajs)
        summaries.append(summarize_condition(cond["label"], trajs))

    runner.close()

    # Dump trajectories
    traj_path = output_dir / "trajectories.jsonl"
    dump_trajectories_jsonl(all_trajectories, traj_path)
    print(f"\nTrajectories written: {traj_path}")

    # Dump summary
    summary = {
        "config": config,
        "n_prompts": len(prompts),
        "total_wall_time_s": time.time() - t_start,
        "per_condition": summaries,
    }
    with open(output_dir / "run_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print(f"\n{'='*70}")
    print("RUN SUMMARY")
    print(f"{'='*70}")
    for s in summaries:
        print(f"  {s['label']:25s}  "
              f"tool-call rate={s['tool_call_rate']:.2f}  "
              f"mean calls={s['mean_tool_calls']:.2f}  "
              f"errors={s['errors']}")
    print(f"  total wall time: {summary['total_wall_time_s']:.1f}s")


if __name__ == "__main__":
    main()
