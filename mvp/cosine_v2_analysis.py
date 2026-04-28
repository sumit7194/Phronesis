"""
Cosine-similarity matrix across v1 + v2 extracted vectors.

After run_v2_sweep.sh re-extracts v2 vectors, this script:
  - Loads all .npy files from results/vectors/qwen3-4b/{corpus}/last_token/
    + the _v1_backup snapshots of the same paths.
  - Computes pairwise cosine similarity at each available layer.
  - Outputs JSON + HTML for the dashboard to display.

The key questions:
  Q1: For each virtue, how rotated did the new corpus make the extraction?
      cos(v_EG_v1_L7, v_EG_v2_L7) close to 1 → corpus expansion didn't change direction;
                                       close to 0 → corpus redesign rotated the vector substantially.
  Q2: Are the v2 vectors orthogonal to each other across virtues at the
      same layer?
      cos(v_EG_v2_L9, v_CC_v2_L9) close to 0 → orthogonal dispositions, composition is meaningful.
                                  close to 1 → same direction, redundant.

Usage on VM:
    python3 cosine_v2_analysis.py --output cosine_matrix.json --html cosine_matrix.html
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np


VECTOR_ROOT = Path(__file__).parent / "results" / "vectors" / "qwen3-4b"

VIRTUE_DIRS = {
    "EG":         "triplets-evidence-grounding",
    "EG_v1":      "triplets-evidence-grounding_v1_backup",
    "RT":         "triplets-reasoning-transparency",
    "RT_v1":      "triplets-reasoning-transparency_v1_backup",
    "CC_full":    "triplets-combined",
    "CC_full_v1": "triplets-combined_v1_backup",
    "CC_legacy":  "triplets",            # the original 50-triplet hand corpus, no expansion
    "CC_numeric": "triplets-cc-numeric-only-symlinks",  # the new 20 claude-cc-* alone
    "IH":         "triplets-intellectual-humility",
    "IH_v1":      "triplets-intellectual-humility_v1_backup",
}


def load_all_vectors() -> dict:
    """Returns {virtue_label: {layer_idx: vector_np_array}}"""
    out = {}
    for label, subdir in VIRTUE_DIRS.items():
        d = VECTOR_ROOT / subdir / "last_token"
        if not d.is_dir():
            continue
        layer_vecs = {}
        for npy in sorted(d.glob("layer_*_virtue_vector.npy")):
            try:
                layer = int(npy.stem.split("_")[1])
            except ValueError:
                continue
            v = np.load(npy)
            layer_vecs[layer] = v
        if layer_vecs:
            out[label] = layer_vecs
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return float("nan")
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float("nan")
    return float(np.dot(a, b) / (na * nb))


def build_matrix(vecs: dict) -> dict:
    """Build a per-layer pairwise cosine matrix.

    Output structure:
      {
        layer: {
          'labels': [...],
          'matrix': [[...]],
          'shape': '(N,N)',
        }
      }
    """
    # Find the union of layers represented
    all_layers = sorted(set(l for d in vecs.values() for l in d.keys()))

    out = {}
    for L in all_layers:
        labels = [k for k in VIRTUE_DIRS if L in vecs.get(k, {})]
        if len(labels) < 2:
            continue
        N = len(labels)
        M = np.zeros((N, N))
        for i, a in enumerate(labels):
            for j, b in enumerate(labels):
                M[i, j] = cosine(vecs[a][L], vecs[b][L])
        out[L] = {
            "labels": labels,
            "matrix": M.round(3).tolist(),
            "shape": f"({N},{N})",
        }
    return out


def render_html(matrix: dict, layers_of_interest: list = None) -> str:
    """Generate compact HTML page that highlights the key cells."""
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>v2 sweep — cosine similarity</title>",
        "<style>",
        "body{font-family:-apple-system,system-ui,monospace;font-size:13px;margin:20px;}",
        "h2{margin-top:30px;border-bottom:1px solid #ddd;padding-bottom:4px;}",
        "table{border-collapse:collapse;font-size:12px;}",
        "td,th{border:1px solid #ccc;padding:4px 8px;text-align:right;font-variant-numeric:tabular-nums;}",
        "th{background:#f5f5f5;font-weight:600;text-align:left;}",
        ".diag{background:#eef;}",
        ".high{background:#fcc;}",  # > 0.7
        ".mid{background:#ffd;}",   # 0.3–0.7
        ".low{background:#dfd;}",   # < 0.3 (orthogonal-ish)
        ".self{font-weight:600;}",
        "code{background:#f5f5f5;padding:1px 4px;border-radius:3px;}",
        "</style>",
        f"<h1>v2 sweep — cosine similarity matrix</h1>",
        f"<p>Generated {datetime.utcnow().isoformat()}Z. ",
        "<b>Red cells (cos &gt; 0.7)</b> = vectors point the same direction (redundant). ",
        "<b>Green cells (cos &lt; 0.3)</b> = orthogonal dispositions (composable). ",
        "<b>Yellow cells</b> = mid range. ",
        "Diagonal cells (always 1.0) are blue.</p>",
        "<h2>Key questions</h2>",
        "<ul>",
        "<li><b>Q1 — corpus rotation:</b> at each layer, look at <code>EG vs EG_v1</code>, <code>RT vs RT_v1</code>, <code>IH vs IH_v1</code>. ",
        "If close to 1, the corpus expansion didn't change vector direction. If lower, the redesign rotated the vector.</li>",
        "<li><b>Q2 — disposition orthogonality:</b> at each shared layer, look at the off-diagonal cells between v2 virtues (<code>EG, RT, CC_full, CC_numeric, IH</code>). ",
        "If they are mostly green (cos &lt; 0.3), we have 4-5 distinct dispositions and composition is meaningful. ",
        "If they are mostly red, the &quot;one disposition discovered from many corpora&quot; reading from yesterday is reinforced.</li>",
        "<li><b>Q3 — CC corpus subset effect:</b> compare <code>CC_full vs CC_legacy</code> and <code>CC_full vs CC_numeric</code>. ",
        "If CC_numeric points in a notably different direction from CC_full, the new explicit-numerical-probability axis survives the noise of mixing with the older corpus.</li>",
        "</ul>",
    ]

    if layers_of_interest is None:
        # Show our 4 AP-peak layers (7, 9, 15, 17) + a few mid/deep layers.
        # If --layers all was used, all odd+even are present; if --layers sweep,
        # only even ones are present. The render code will just skip absent layers.
        layers_of_interest = [7, 9, 13, 15, 17, 22, 25, 8, 14, 16, 18]

    for L in sorted(matrix.keys()):
        if layers_of_interest and L not in layers_of_interest:
            continue
        m = matrix[L]
        parts.append(f"<h2>Layer {L}</h2>")
        parts.append("<table><tr><th></th>")
        for lbl in m["labels"]:
            parts.append(f"<th>{lbl}</th>")
        parts.append("</tr>")
        for i, row_lbl in enumerate(m["labels"]):
            parts.append(f"<tr><th class='self'>{row_lbl}</th>")
            for j, col_lbl in enumerate(m["labels"]):
                v = m["matrix"][i][j]
                cls = ""
                if i == j:
                    cls = "diag"
                elif abs(v) > 0.7:
                    cls = "high"
                elif abs(v) >= 0.3:
                    cls = "mid"
                else:
                    cls = "low"
                parts.append(f"<td class='{cls}'>{v:+.2f}</td>")
            parts.append("</tr>")
        parts.append("</table>")

    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/cosine_matrix.json")
    ap.add_argument("--html", default="results/cosine_matrix.html")
    args = ap.parse_args()

    print("Loading vectors...")
    vecs = load_all_vectors()
    for label, layers in vecs.items():
        print(f"  {label}: {len(layers)} layers ({sorted(layers.keys())[:3]}... to {sorted(layers.keys())[-3:]})")

    print("\nBuilding cosine matrix...")
    matrix = build_matrix(vecs)
    print(f"  computed for {len(matrix)} layers")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "labels_present": list(vecs.keys()),
            "by_layer": matrix,
        }, f, indent=2)
    print(f"  wrote {args.output}")

    html = render_html(matrix)
    Path(args.html).parent.mkdir(parents=True, exist_ok=True)
    Path(args.html).write_text(html)
    print(f"  wrote {args.html}")


if __name__ == "__main__":
    main()
