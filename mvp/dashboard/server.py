"""
Phronesis Dashboard — Flask server for monitoring extraction and steering.

Run: python mvp/dashboard/server.py
Open: http://localhost:5050
"""

import json
import os
import subprocess
import glob as globmod
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="/static")

MVP_DIR = Path(__file__).parent.parent
PROJECT_DIR = MVP_DIR.parent
RESULTS_DIR = MVP_DIR / "results"
VECTORS_DIR = RESULTS_DIR / "vectors"
STEERING_DIR = RESULTS_DIR / "steering"
CORPUS_DIR = PROJECT_DIR / "corpus"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/progress")
def progress_page():
    return send_from_directory(".", "progress.html")


@app.route("/api/sweep-progress")
def sweep_progress():
    """Simple progress for the extraction sweep — one row per run."""
    MODELS = ["gemma-2-2b-it", "qwen-2.5-3b-it"]
    CORPORA = ["triplets", "triplets-synthetic-chatgpt", "triplets-synthetic-sonnet"]
    METHODS = ["comprehension", "last_token"]

    runs = []
    current_found = False

    for model in MODELS:
        for corpus in CORPORA:
            for method in METHODS:
                method_dir = VECTORS_DIR / model / corpus / method
                layers_done = len(list(method_dir.glob("layer_*_metadata.json"))) if method_dir.exists() else 0

                # Read best probe from metadata files
                best_probe = ""
                if layers_done == 26:
                    summary = VECTORS_DIR / model / corpus / "extraction_summary.json"
                    if summary.exists():
                        try:
                            with open(summary) as f:
                                s = json.load(f)
                            mdata = s.get("methods", {}).get(method, {})
                            if mdata:
                                bl = mdata.get("best_layer", "?")
                                bp = mdata.get("best_probe", 0)
                                # Get separation from per_layer
                                per_layer = mdata.get("per_layer", {})
                                sep = per_layer.get(str(bl), {}).get("separation", 0)
                                sign = "+" if sep > 0 else "−"
                                best_probe = f"{int(bp*100)}% L{bl} ({sign})"
                        except Exception:
                            pass

                if layers_done == 26:
                    status = "done"
                elif layers_done > 0:
                    status = "partial"
                else:
                    status = "pending"

                runs.append({
                    "model": model,
                    "corpus": corpus,
                    "method": method,
                    "status": status,
                    "layers_done": layers_done if status == "running" else None,
                    "probe": best_probe,
                })

    return jsonify({"runs": runs})


@app.route("/api/extraction")
def extraction_results():
    """Return all extraction result JSON files."""
    results = {}
    for f in sorted(RESULTS_DIR.glob("mvp_v2_*.json")):
        with open(f) as fh:
            results[f.stem] = json.load(fh)
    return jsonify(results)


@app.route("/api/extraction-summary")
def extraction_summaries():
    """Return extraction summaries (from --save-vectors runs)."""
    summaries = {}
    for f in VECTORS_DIR.rglob("extraction_summary.json"):
        rel = f.relative_to(VECTORS_DIR)
        key = str(rel.parent)
        with open(f) as fh:
            summaries[key] = json.load(fh)
    return jsonify(summaries)


@app.route("/api/steering")
def steering_results():
    """Return all steering result JSON files."""
    results = {}
    if STEERING_DIR.exists():
        for f in sorted(STEERING_DIR.glob("*.json")):
            with open(f) as fh:
                results[f.stem] = json.load(fh)
    return jsonify(results)


@app.route("/api/status")
def status():
    """Return completion matrix for all runs."""
    status = {
        "extraction_files": [],
        "vector_dirs": [],
        "steering_files": [],
    }

    for f in sorted(RESULTS_DIR.glob("mvp_v2_*.json")):
        status["extraction_files"].append({
            "name": f.stem,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "modified": f.stat().st_mtime,
        })

    for d in sorted(VECTORS_DIR.rglob("extraction_summary.json")):
        vec_count = len(list(d.parent.rglob("*.npy")))
        status["vector_dirs"].append({
            "path": str(d.parent.relative_to(VECTORS_DIR)),
            "vectors": vec_count,
            "modified": d.stat().st_mtime,
        })

    if STEERING_DIR.exists():
        for f in sorted(STEERING_DIR.glob("*.json")):
            with open(f) as fh:
                data = json.load(fh)
            status["steering_files"].append({
                "name": f.stem,
                "prompts": len(data.get("results", [])),
                "method": data.get("config", {}).get("method", "?"),
                "layer": data.get("config", {}).get("layer", "?"),
                "modified": f.stat().st_mtime,
            })

    return jsonify(status)


@app.route("/api/progress")
def progress():
    """Live progress: running processes, corpus counts, vector counts."""
    prog = {
        "timestamp": datetime.now().isoformat(),
        "processes": [],
        "corpora": {},
        "vectors": {},
        "extraction_progress": {},
        "live_extraction": None,
    }

    # Live extraction progress from progress file
    progress_file = RESULTS_DIR / "extraction_progress.json"
    if progress_file.exists():
        try:
            with open(progress_file) as f:
                prog["live_extraction"] = json.load(f)
        except Exception:
            pass

    # Check running Python processes related to our scripts
    try:
        ps = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        for line in ps.stdout.split("\n"):
            if any(s in line for s in ["extract_v2", "steer.py", "generate_corpus"]):
                if "grep" not in line:
                    parts = line.split()
                    cpu = parts[2] if len(parts) > 2 else "?"
                    mem = parts[3] if len(parts) > 3 else "?"
                    # Extract the script name and args
                    cmd_start = line.find("python")
                    cmd = line[cmd_start:] if cmd_start >= 0 else line[65:]
                    prog["processes"].append({
                        "command": cmd[:120],
                        "cpu": cpu,
                        "mem": mem,
                    })
    except Exception:
        pass

    # Count triplets in each corpus directory (auto-discover all triplets-* dirs)
    for corpus_path in sorted(CORPUS_DIR.iterdir()):
        if not corpus_path.is_dir() or not corpus_path.name.startswith("triplets"):
            continue
        corpus_name = corpus_path.name
        total_dirs = len([d for d in corpus_path.iterdir() if d.is_dir()])
        complete = len([d for d in corpus_path.iterdir()
                      if d.is_dir() and (d / "neutral.md").exists()
                      and (d / "virtuous.md").exists()
                      and (d / "non-virtuous.md").exists()])
        prog["corpora"][corpus_name] = {
            "total_dirs": total_dirs,
            "complete_triplets": complete,
            "target": 100 if "gemini" in corpus_name or "gemma-all" in corpus_name else total_dirs,
        }

    # Count saved vectors per model/corpus/method
    if VECTORS_DIR.exists():
        for model_dir in sorted(VECTORS_DIR.iterdir()):
            if not model_dir.is_dir():
                continue
            for corpus_dir in sorted(model_dir.iterdir()):
                if not corpus_dir.is_dir():
                    continue
                for method_dir in sorted(corpus_dir.iterdir()):
                    if not method_dir.is_dir():
                        continue
                    npy_count = len(list(method_dir.glob("*.npy")))
                    json_count = len(list(method_dir.glob("*.json")))
                    key = f"{model_dir.name}/{corpus_dir.name}/{method_dir.name}"
                    prog["vectors"][key] = {
                        "npy_files": npy_count,
                        "json_files": json_count,
                        "layers": npy_count // 3 if npy_count > 0 else 0,
                    }

    # Extraction progress: count vectors per method to determine which methods are done
    # Expected: 26 layers per method, 3 files per layer (raw, whitened, components)
    methods_expected = ["comprehension", "generation", "last_token"]
    for model_dir in (VECTORS_DIR.iterdir() if VECTORS_DIR.exists() else []):
        if not model_dir.is_dir():
            continue
        for corpus_dir_v in model_dir.iterdir():
            if not corpus_dir_v.is_dir():
                continue
            key = f"{model_dir.name}/{corpus_dir_v.name}"
            method_status = {}
            for method in methods_expected:
                method_dir = corpus_dir_v / method
                if method_dir.exists():
                    metadata_count = len(list(method_dir.glob("layer_*_metadata.json")))
                    method_status[method] = {"layers_done": metadata_count, "total": 26}
                else:
                    method_status[method] = {"layers_done": 0, "total": 26}
            prog["extraction_progress"][key] = method_status

    # Steering results progress
    if STEERING_DIR.exists():
        for f in sorted(STEERING_DIR.glob("*.json")):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                config = data.get("config", {})
                results = data.get("results", [])
                total_alphas = len(config.get("alphas", []))
                completed_prompts = len(results)
                completed_steered = sum(len(r.get("steered", {})) for r in results)
                total_expected = completed_prompts * total_alphas
                prog["extraction_progress"][f"steering_{f.stem}"] = {
                    "latest_progress": f"{completed_prompts} prompts, {completed_steered}/{total_expected} steered",
                    "method": config.get("method"),
                    "layer": config.get("layer"),
                }
            except Exception:
                pass

    return jsonify(prog)


if __name__ == "__main__":
    print(f"Phronesis Dashboard")
    print(f"Results dir: {RESULTS_DIR}")
    print(f"Open http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=True)
