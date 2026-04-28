"""
Dashboard for the Day-22 v2 sweep.

Runs ON the VM, serves on http://0.0.0.0:8082.

Shows:
  - Current phase (backup / extract / cosine / behavioral / complete)
  - Per-phase progress (cell idx / cell total)
  - Elapsed + ETA
  - GPU utilisation + memory + temperature
  - Last 30 lines of run.log
  - Cosine matrix (when phase 3 has produced cosine_matrix.html)
  - Behavioral cell results (file counts) once phase 4 starts

Usage on VM:
    cd ~/phronesis/mvp && nohup python3 dashboard_v2_sweep.py > /tmp/dashboard_v2.log 2>&1 &

Access from laptop:
    gcloud compute ssh sumit@phronesis-v2-l4 --zone=asia-southeast1-a -- -L 8082:localhost:8082
    then open http://localhost:8082 in browser.
"""
from __future__ import annotations
import http.server
import json
import socketserver
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from html import escape
import glob
import os

PORT = 8082
MVP = Path(__file__).parent
RESULTS = MVP / "results"


def find_active_logdir() -> Path | None:
    """Find the most recent v2_sweep_* dir."""
    candidates = sorted(RESULTS.glob("v2_sweep_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def read_status(logdir: Path) -> dict:
    s = logdir / "status.json"
    if not s.exists():
        return {}
    try:
        return json.loads(s.read_text())
    except Exception:
        return {}


def tail_log(logdir: Path, n: int = 30) -> str:
    log = logdir / "run.log"
    if not log.exists():
        return "(no run.log yet)"
    try:
        # Read last ~16KB and grab last n non-empty lines
        size = log.stat().st_size
        offset = max(0, size - 16384)
        with open(log, "rb") as f:
            f.seek(offset)
            data = f.read().decode("utf-8", errors="ignore")
        lines = [l for l in data.splitlines() if l.strip()]
        return "\n".join(lines[-n:])
    except Exception as e:
        return f"(error tailing: {e})"


def gpu_stats() -> dict:
    """nvidia-smi summary."""
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
            "--format=csv,noheader,nounits",
        ], stderr=subprocess.DEVNULL, timeout=3).decode().strip()
        if not out:
            return {"error": "no GPU output"}
        parts = [p.strip() for p in out.split(",")]
        return {
            "name": parts[0],
            "util_percent": parts[1],
            "mem_used_mb": parts[2],
            "mem_total_mb": parts[3],
            "temp_c": parts[4],
        }
    except Exception as e:
        return {"error": str(e)}


def count_behavioral_cells() -> dict:
    """Count JSON files in d22_v2_* labelled benchmark probe dirs."""
    out = {}
    for d in sorted(RESULTS.glob("benchmark_probe/*/d22_v2_*")):
        files = list(d.glob("*.json"))
        out[d.name] = {"bench": d.parent.name, "count": len(files)}
    return out


def count_extracted_vectors() -> dict:
    """Count saved vector .npy files per corpus."""
    out = {}
    vecroot = RESULTS / "vectors" / "qwen3-4b"
    if not vecroot.is_dir():
        return out
    for sub in sorted(vecroot.iterdir()):
        if not sub.is_dir():
            continue
        d = sub / "last_token"
        if not d.is_dir():
            continue
        n = len(list(d.glob("layer_*_virtue_vector.npy")))
        if n > 0:
            out[sub.name] = n
    return out


def cosine_matrix_path(logdir: Path) -> Path | None:
    p = logdir / "cosine_matrix.html"
    return p if p.exists() else None


def render_html() -> str:
    logdir = find_active_logdir()
    if logdir is None:
        return "<!doctype html><body style='font-family:monospace'><h1>v2 sweep not started yet</h1><p>Looking for results/v2_sweep_YYYYMMDD/</p></body>"

    status = read_status(logdir)
    log_tail = tail_log(logdir, 40)
    gpu = gpu_stats()
    behavioral = count_behavioral_cells()
    vectors = count_extracted_vectors()
    cosine = cosine_matrix_path(logdir)

    phase = status.get("phase", "?")
    cell = status.get("cell", "")
    cell_idx = status.get("cell_idx", 0)
    cell_total = status.get("cell_total", 0)
    started = status.get("started_at", "")
    updated = status.get("updated_at", "")

    elapsed = ""
    if started:
        try:
            t0 = datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            d = datetime.now(timezone.utc) - t0
            mins = int(d.total_seconds() // 60)
            secs = int(d.total_seconds() % 60)
            elapsed = f"{mins}m {secs}s"
        except Exception:
            elapsed = ""

    pct = 0
    if cell_total:
        pct = int(100 * cell_idx / cell_total)

    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<meta http-equiv='refresh' content='10'>",
        "<title>v2 sweep dashboard</title>",
        "<style>",
        "body{font-family:-apple-system,system-ui,monospace;font-size:13px;margin:20px;background:#fafafa;color:#222;}",
        "h1{margin:0 0 8px 0;}",
        "h2{margin:24px 0 8px 0;border-bottom:1px solid #ddd;padding-bottom:4px;font-size:15px;}",
        ".grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;}",
        ".card{background:white;border:1px solid #ddd;border-radius:6px;padding:12px 16px;box-shadow:0 1px 2px rgba(0,0,0,0.04);}",
        ".phase-tag{display:inline-block;padding:3px 10px;border-radius:3px;font-weight:600;margin-right:8px;}",
        ".phase-phase1_backup{background:#ddd;}",
        ".phase-phase2_extract{background:#cef;}",
        ".phase-phase3_cosine{background:#fec;}",
        ".phase-phase4_behavioral{background:#cfc;}",
        ".phase-complete{background:#fcc;color:#922;}",
        ".bar{height:18px;background:#eee;border-radius:3px;overflow:hidden;margin:6px 0;}",
        ".bar-fill{height:100%;background:linear-gradient(90deg,#48f,#7af);}",
        "pre{background:#202020;color:#ddd;padding:10px;border-radius:4px;overflow-x:auto;font-size:11px;line-height:1.4;max-height:380px;overflow-y:auto;}",
        "table{border-collapse:collapse;width:100%;font-size:12px;}",
        "td,th{padding:4px 8px;text-align:left;border-bottom:1px solid #eee;}",
        "th{background:#f0f0f0;font-weight:600;}",
        ".muted{color:#888;}",
        ".big{font-size:18px;font-weight:600;}",
        "a{color:#48a;}",
        "</style>",
        f"<h1>v2 sweep dashboard</h1>",
        f"<p class='muted'>Last refresh: {datetime.utcnow().strftime('%H:%M:%S')}Z. Auto-refresh every 10s. Logdir: <code>{escape(str(logdir.relative_to(MVP)))}</code></p>",
        "<div class='grid'>",
        "<div class='card'>",
        f"<h2>Status</h2>",
        f"<p><span class='phase-tag phase-{escape(phase)}'>{escape(phase)}</span> ",
        f"<span class='big'>{escape(str(cell))}</span></p>",
        f"<p>Cell {cell_idx} / {cell_total} &nbsp; ({pct}%)</p>",
        f"<div class='bar'><div class='bar-fill' style='width:{pct}%'></div></div>",
        f"<p>Elapsed: <b>{elapsed}</b> &nbsp; (started {escape(started)}Z; last status update {escape(updated)})</p>",
        "</div>",
        "<div class='card'>",
        "<h2>GPU</h2>",
    ]
    if "error" in gpu:
        parts.append(f"<p class='muted'>{escape(gpu['error'])}</p>")
    else:
        parts.append(
            f"<p>{escape(gpu.get('name',''))}<br>"
            f"Util: <b>{escape(gpu.get('util_percent',''))}%</b> &nbsp; "
            f"Mem: <b>{escape(gpu.get('mem_used_mb',''))}/{escape(gpu.get('mem_total_mb',''))} MB</b> &nbsp; "
            f"Temp: <b>{escape(gpu.get('temp_c',''))}°C</b></p>"
        )
    parts.append("</div>")
    parts.append("</div>")  # close grid

    # Vectors extracted
    parts.append("<h2>Extracted vectors (per corpus)</h2>")
    if vectors:
        parts.append("<table><tr><th>Corpus dir</th><th>Layers saved</th></tr>")
        for k, v in sorted(vectors.items()):
            parts.append(f"<tr><td><code>{escape(k)}</code></td><td>{v}</td></tr>")
        parts.append("</table>")
    else:
        parts.append("<p class='muted'>(none yet)</p>")

    # Behavioral cells
    parts.append("<h2>Behavioral diagnostic cells (Phase 4)</h2>")
    if behavioral:
        parts.append("<table><tr><th>Cell label</th><th>Bench</th><th>Files</th></tr>")
        for k, v in sorted(behavioral.items()):
            parts.append(f"<tr><td><code>{escape(k)}</code></td><td>{escape(v['bench'])}</td><td>{v['count']}</td></tr>")
        parts.append("</table>")
    else:
        parts.append("<p class='muted'>(no Phase 4 output yet)</p>")

    # Cosine matrix link
    parts.append("<h2>Cosine matrix</h2>")
    if cosine:
        # Inline the HTML body
        try:
            html = cosine.read_text()
            # Strip <!doctype etc to inline cleanly
            if "<h1>" in html:
                html = html[html.find("<style>"):]
            parts.append(f"<div class='card' style='padding:0 16px'>{html}</div>")
        except Exception as e:
            parts.append(f"<p class='muted'>Error reading cosine matrix: {escape(str(e))}</p>")
    else:
        parts.append("<p class='muted'>(matrix not computed yet — appears after Phase 3)</p>")

    # Log tail
    parts.append("<h2>run.log (last 40 lines)</h2>")
    parts.append(f"<pre>{escape(log_tail)}</pre>")

    return "".join(parts)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress access log noise
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            html = render_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return
        elif self.path == "/status.json":
            logdir = find_active_logdir()
            data = read_status(logdir) if logdir else {}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return
        else:
            self.send_response(404)
            self.end_headers()


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"v2 sweep dashboard serving on http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
