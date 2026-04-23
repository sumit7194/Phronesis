"""
Minimal live dashboard for EG + RT extraction progress.

Runs ON the VM, serves on http://0.0.0.0:8081.

Shows:
  - Current extraction phase (which of the 4 runs, which layer, which triplet)
  - GPU utilisation + memory + temperature
  - Saved vector count per (model, corpus)
  - Last 10 log lines from results/eg_rt_extraction.log
  - Elapsed time + ETA estimate

No JS; HTML meta-refresh every 10s. Read-only.

Usage (on VM):
    cd ~/phronesis/mvp && nohup python3 dashboard_extraction.py > /tmp/dashboard_extraction.log 2>&1 &

Access from laptop: http://<VM_EXTERNAL_IP>:8081
"""
from __future__ import annotations
import http.server
import json
import socketserver
import subprocess
from datetime import datetime
from pathlib import Path

PORT = 8080
RESULTS = Path(__file__).parent / "results"
PROGRESS_FILE = RESULTS / "extraction_progress.json"
LOG_FILE = RESULTS / "eg_rt_extraction.log"
VECTORS_ROOT = RESULTS / "vectors"

MVP_CORPORA = [
    "triplets-evidence-grounding",
    "triplets-reasoning-transparency",
]
MODELS = ["qwen3-4b", "gemma-4-E4B-it"]


def read_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {}
    try:
        return json.loads(PROGRESS_FILE.read_text())
    except Exception:
        return {}


def read_gpu() -> dict:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        vals = [v.strip() for v in out.stdout.strip().split(",")]
        return {
            "util_pct": vals[0],
            "mem_used_mib": vals[1],
            "mem_total_mib": vals[2],
            "temp_c": vals[3],
            "power_w": vals[4],
        }
    except Exception:
        return {"util_pct": "?", "mem_used_mib": "?", "mem_total_mib": "?", "temp_c": "?", "power_w": "?"}


def read_log_tail(n: int = 15) -> list:
    if not LOG_FILE.exists():
        return []
    try:
        lines = LOG_FILE.read_text(errors="ignore").splitlines()
        return lines[-n:]
    except Exception:
        return []


def count_vectors(model: str, corpus: str) -> int:
    """Count layer_*_virtue_vector.npy files across all method subdirectories.

    extract_v2.py saves under {model}/{corpus}/{method}/ where method is one of
    {comprehension, generation, last_token}. Our EG+RT runs use --method generation.
    We sum across any method subdirectory present (for a given corpus, normally just one).
    """
    d = VECTORS_ROOT / model / corpus
    if not d.exists():
        return 0
    total = 0
    # Prefer generation/ (our current method); fall back to any sibling
    for method_dir in d.iterdir():
        if method_dir.is_dir():
            total += len(list(method_dir.glob("layer_*_virtue_vector.npy")))
    return total


def expected_layers(model: str) -> int:
    return 36 if model == "qwen3-4b" else 42


def format_bytes(mib):
    try:
        return f"{int(mib)/1024:.1f} GiB"
    except Exception:
        return "?"


def render_html(prog, gpu, log_tail):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Current phase
    if prog:
        model = prog.get("model", "?")
        corpus = prog.get("corpus", "?")
        phase = prog.get("phase", "?")
        triplet = prog.get("triplet", 0)
        total_triplets = prog.get("total_triplets", 0)
        ts = prog.get("timestamp", "")
        phase_html = f"""
<div class="card">
  <h2>Current phase</h2>
  <div class="metric"><span class="k">model</span><span class="v">{model}</span></div>
  <div class="metric"><span class="k">corpus</span><span class="v">{corpus}</span></div>
  <div class="metric"><span class="k">phase</span><span class="v">{phase}</span></div>
  <div class="metric"><span class="k">triplet</span><span class="v">{triplet} / {total_triplets}</span></div>
  <div class="metric muted"><span class="k">last update</span><span class="v">{ts}</span></div>
</div>"""
    else:
        phase_html = '<div class="card"><h2>Current phase</h2><div class="muted">no progress file yet — extraction not started or just initialised</div></div>'

    # Completion matrix
    rows = []
    for m in MODELS:
        for c in MVP_CORPORA:
            done = count_vectors(m, c)
            total = expected_layers(m)
            pct = 100 * done / total if total else 0
            bar = "█" * int(pct / 4) + "░" * (25 - int(pct / 4))
            rows.append(f"<tr><td>{m}</td><td>{c}</td><td>{done} / {total}</td><td><code>{bar}</code> {pct:.0f}%</td></tr>")
    completion_html = f"""
<div class="card">
  <h2>Extraction completion (saved layer-vectors)</h2>
  <table>
    <tr><th>model</th><th>corpus</th><th>layers</th><th>progress</th></tr>
    {''.join(rows)}
  </table>
</div>"""

    # GPU
    try:
        mem_used_gib = float(gpu.get("mem_used_mib", 0)) / 1024
        mem_total_gib = float(gpu.get("mem_total_mib", 0)) / 1024
        mem_pct = 100 * mem_used_gib / mem_total_gib if mem_total_gib > 0 else 0
    except Exception:
        mem_used_gib = mem_total_gib = mem_pct = 0
    gpu_html = f"""
<div class="card">
  <h2>GPU (L4)</h2>
  <div class="metric"><span class="k">util</span><span class="v">{gpu.get('util_pct','?')}%</span></div>
  <div class="metric"><span class="k">memory</span><span class="v">{mem_used_gib:.1f} / {mem_total_gib:.1f} GiB ({mem_pct:.0f}%)</span></div>
  <div class="metric"><span class="k">temp</span><span class="v">{gpu.get('temp_c','?')} °C</span></div>
  <div class="metric"><span class="k">power</span><span class="v">{gpu.get('power_w','?')} W</span></div>
</div>"""

    # Log tail
    log_html = "<br>".join(f'<span class="logline">{l}</span>' for l in log_tail) or '<span class="muted">(log file not found yet)</span>'
    log_html = f'<div class="card"><h2>Recent log</h2><div class="log">{log_html}</div></div>'

    return f"""<!doctype html>
<html><head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="10"/>
<title>Phronesis EG+RT extraction</title>
<style>
body {{ font-family: ui-monospace, Menlo, monospace; background: #0d1117; color: #d1d5db; margin: 0; padding: 24px; }}
h1 {{ color: #60a5fa; margin: 0 0 8px; }}
h2 {{ color: #f59e0b; margin-top: 0; }}
.muted {{ color: #6b7280; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px 20px; margin: 12px 0; }}
.metric {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dotted #30363d; }}
.metric:last-child {{ border-bottom: none; }}
.k {{ color: #9ca3af; }}
.v {{ color: #d1d5db; font-weight: 600; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 6px 8px; text-align: left; border-bottom: 1px solid #30363d; }}
th {{ color: #9ca3af; font-weight: normal; }}
.log {{ font-size: 12px; line-height: 1.4; max-height: 300px; overflow-y: auto; white-space: pre-wrap; }}
.logline {{ color: #9ca3af; }}
code {{ color: #10b981; }}
</style>
</head>
<body>
<h1>Phronesis — EG + RT extraction dashboard</h1>
<div class="muted">server time: {now} — auto-refresh 10s</div>
{phase_html}
{completion_html}
{gpu_html}
{log_html}
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        prog = read_progress()
        gpu = read_gpu()
        log_tail = read_log_tail(15)
        html = render_html(prog, gpu, log_tail)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, *_):
        pass  # silence access logs


if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Phronesis extraction dashboard — http://0.0.0.0:{PORT}")
        httpd.serve_forever()
