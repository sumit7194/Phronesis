"""
Live dashboard for the Phronesis hard_probe_v2 run on GCP.

Runs a local HTTP server on http://localhost:8080 that shows:
  - Benchmark progress (X/38 cells, per-benchmark tally)
  - Last 10 completions with correctness + time
  - GPU: util %, memory, temperature
  - System: CPU %, RAM, swap
  - Process: PID, elapsed, state

Polls GCP via `gcloud compute ssh` every POLL_INTERVAL seconds in a background
thread. Serves pages locally with a meta-refresh. No JS required.

Usage:
    cd mvp && .venv/bin/python dashboard_live.py
    # then open http://localhost:8080 in any browser
"""
from __future__ import annotations
import http.server
import json
import shlex
import socketserver
import subprocess
import threading
import time
from datetime import datetime
from html import escape
from pathlib import Path

VM_NAME = "phronesis-v2"
VM_ZONE = "asia-east1-c"
PORT = 8080
POLL_INTERVAL = 30   # seconds between GCP probes

# Probe command — single python3 invocation on GCP returns all metrics as JSON
PROBE_CMD = r"""python3 -c '
import json, subprocess, os
out = {}

# GPU
try:
    r = subprocess.run([
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
        "--format=csv,noheader,nounits"
    ], capture_output=True, text=True, timeout=5)
    parts = [x.strip() for x in r.stdout.strip().split(",")]
    if len(parts) >= 4:
        out["gpu"] = {
            "util": parts[0], "mem_used": parts[1], "mem_total": parts[2],
            "temp": parts[3],
            "power": parts[4] if len(parts)>4 else "?",
            "power_cap": parts[5] if len(parts)>5 else "?",
        }
except Exception as e:
    out["gpu_err"] = str(e)

# RAM / Swap
try:
    r = subprocess.run(["free", "-m"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] == "Mem:":
            out["ram"] = {"total": int(parts[1]), "used": int(parts[2]), "available": int(parts[6]) if len(parts)>6 else 0}
        elif parts and parts[0] == "Swap:":
            out["swap"] = {"total": int(parts[1]), "used": int(parts[2])}
except Exception as e:
    out["mem_err"] = str(e)

# CPU (1-sec average)
try:
    r = subprocess.run(["grep", "cpu ", "/proc/stat"], capture_output=True, text=True)
    nums1 = list(map(int, r.stdout.split()[1:]))
    import time; time.sleep(0.3)
    r = subprocess.run(["grep", "cpu ", "/proc/stat"], capture_output=True, text=True)
    nums2 = list(map(int, r.stdout.split()[1:]))
    idle_d = nums2[3] - nums1[3]
    total_d = sum(nums2) - sum(nums1)
    if total_d > 0:
        out["cpu_pct"] = round(100 * (total_d - idle_d) / total_d, 1)
except Exception as e:
    out["cpu_err"] = str(e)

# Summary progress
try:
    summary_path = "/home/sumit/phronesis/mvp/results/benchmark_probe/summary.jsonl"
    with open(summary_path) as f:
        lines = [l.strip() for l in f if l.strip()]
    out["rows"] = len(lines)
    out["recent"] = lines[-10:]
except Exception as e:
    out["summary_err"] = str(e)

# Per-benchmark file counts for hard_probe_v2
try:
    base = "/home/sumit/phronesis/mvp/results/benchmark_probe/hard_probe_v2"
    counts = {}
    for cond in ("baseline", "steered"):
        d = f"{base}/{cond}"
        if os.path.isdir(d):
            counts[cond] = len([f for f in os.listdir(d) if f.endswith(".json")])
        else:
            counts[cond] = 0
    out["probe_counts"] = counts
except Exception as e:
    out["probe_err"] = str(e)

# Active processes (run_benchmark)
try:
    r = subprocess.run(["ps", "-eo", "pid,etime,stat,pcpu,comm,args", "--no-headers"], capture_output=True, text=True)
    procs = []
    for line in r.stdout.splitlines():
        if "run_benchmark" in line or "run_hard_probe" in line:
            parts = line.split(None, 5)
            procs.append({
                "pid": parts[0], "elapsed": parts[1], "state": parts[2],
                "cpu": parts[3], "comm": parts[4],
                "args": parts[5] if len(parts)>5 else "",
            })
    out["procs"] = procs
except Exception as e:
    out["proc_err"] = str(e)

# Disk
try:
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    parts = r.stdout.splitlines()[-1].split()
    out["disk"] = {"total": parts[1], "used": parts[2], "avail": parts[3], "pct": parts[4]}
except Exception as e:
    out["disk_err"] = str(e)

print(json.dumps(out))
'"""

# Shared state
STATE = {
    "last_update": None,
    "last_duration_s": None,
    "payload": {},
    "error": None,
    "history": [],   # last 20 polls for rudimentary history
}
LOCK = threading.Lock()


def poll_once():
    """Single poll of GCP. Returns (success, payload_or_err, duration_s)."""
    t0 = time.time()
    try:
        cmd = ["gcloud", "compute", "ssh", VM_NAME,
               f"--zone={VM_ZONE}", "--command", PROBE_CMD]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        dt = time.time() - t0
        if result.returncode != 0:
            return False, f"gcloud ssh exit={result.returncode}: {result.stderr[-200:]}", dt
        # Parse JSON — may have gcloud warnings mixed in, so find the first '{'
        stdout = result.stdout
        brace_idx = stdout.find("{")
        if brace_idx < 0:
            return False, f"no JSON in output: {stdout[:200]}", dt
        return True, json.loads(stdout[brace_idx:]), dt
    except subprocess.TimeoutExpired:
        return False, "ssh timeout (>25s)", time.time() - t0
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", time.time() - t0


def poller_thread():
    while True:
        ok, data, dt = poll_once()
        with LOCK:
            STATE["last_update"] = datetime.now()
            STATE["last_duration_s"] = dt
            if ok:
                STATE["payload"] = data
                STATE["error"] = None
                STATE["history"].append({"t": datetime.now().isoformat(),
                                         "rows": data.get("rows", 0)})
                if len(STATE["history"]) > 20:
                    STATE["history"].pop(0)
            else:
                STATE["error"] = data
        time.sleep(POLL_INTERVAL)


# ─── HTML rendering ──────────────────────────────────────────────────────────

CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
     background:#0d1117;color:#e6edf3;margin:0;padding:20px;font-size:14px}
h1{color:#7ee787;margin:0 0 16px 0;font-size:22px}
h2{color:#79c0ff;margin:24px 0 8px 0;font-size:16px;border-bottom:1px solid #30363d;padding-bottom:4px}
.card{background:#161b22;padding:12px 16px;border-radius:8px;border:1px solid #30363d;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.metric{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #21262d}
.metric:last-child{border-bottom:none}
.k{color:#8b949e}
.v{color:#e6edf3;font-weight:500;font-family:ui-monospace,Menlo,monospace}
.bar{background:#21262d;height:8px;border-radius:4px;overflow:hidden;margin-top:4px}
.bar-fill{background:#238636;height:100%;transition:width 0.5s}
.bar-fill.warn{background:#d29922}
.bar-fill.bad{background:#da3633}
.ok{color:#7ee787}
.warn{color:#d29922}
.bad{color:#f85149}
table{width:100%;border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:12px}
th{text-align:left;color:#8b949e;padding:4px 8px;border-bottom:1px solid #30363d}
td{padding:4px 8px;border-bottom:1px solid #21262d}
.stale{color:#d29922}
.fresh{color:#7ee787}
.muted{color:#8b949e}
pre{background:#0d1117;padding:8px;border-radius:4px;overflow-x:auto;margin:0;font-size:12px}
"""


def bar(pct, thresh_warn=70, thresh_bad=90):
    cls = "" if pct < thresh_warn else ("warn" if pct < thresh_bad else "bad")
    return f'<div class="bar"><div class="bar-fill {cls}" style="width:{min(100,pct):.0f}%"></div></div>'


def render_page():
    with LOCK:
        last = STATE["last_update"]
        err = STATE["error"]
        p = STATE["payload"] or {}
        dur = STATE["last_duration_s"]
        history = list(STATE["history"])

    if last:
        age = (datetime.now() - last).total_seconds()
        age_cls = "fresh" if age < POLL_INTERVAL * 1.5 else "stale"
        last_str = f'<span class="{age_cls}">{last.strftime("%H:%M:%S")} ({age:.0f}s ago, poll {dur:.1f}s)</span>'
    else:
        last_str = '<span class="muted">never — waiting for first poll…</span>'

    err_html = f'<div class="card"><span class="bad">⚠ Error:</span> {escape(str(err))}</div>' if err else ""

    # Progress card
    total_expected = 38
    rows_now = p.get("rows", 0)
    pct_prog = 100 * rows_now / total_expected if total_expected else 0
    probe_counts = p.get("probe_counts", {})
    progress_html = f"""
<div class="card">
<h2>Benchmark Progress</h2>
<div class="metric"><span class="k">hard_probe_v2 baseline</span>
  <span class="v">{probe_counts.get("baseline",0)} / 19</span></div>
<div class="metric"><span class="k">hard_probe_v2 steered</span>
  <span class="v">{probe_counts.get("steered",0)} / 19</span></div>
<div class="metric"><span class="k">summary.jsonl rows (total sweep)</span>
  <span class="v">{rows_now} / {total_expected}</span></div>
{bar(pct_prog)}
</div>
"""

    # GPU card
    gpu = p.get("gpu", {})
    if gpu:
        mem_pct = 100 * int(gpu.get("mem_used","0")) / max(int(gpu.get("mem_total","1")),1)
        gpu_html = f"""
<div class="card">
<h2>GPU (Tesla T4)</h2>
<div class="metric"><span class="k">GPU util</span><span class="v">{gpu.get("util","?")}%</span></div>
{bar(int(gpu.get("util","0") or 0))}
<div class="metric"><span class="k">VRAM</span><span class="v">{gpu.get("mem_used","?")} / {gpu.get("mem_total","?")} MiB ({mem_pct:.0f}%)</span></div>
{bar(mem_pct)}
<div class="metric"><span class="k">Temperature</span><span class="v">{gpu.get("temp","?")}°C</span></div>
<div class="metric"><span class="k">Power</span><span class="v">{gpu.get("power","?")} / {gpu.get("power_cap","?")} W</span></div>
</div>
"""
    else:
        gpu_html = '<div class="card"><h2>GPU</h2><span class="muted">no data</span></div>'

    # System card (CPU + RAM + Swap + Disk)
    ram = p.get("ram", {})
    swap = p.get("swap", {})
    disk = p.get("disk", {})
    cpu_pct = p.get("cpu_pct", None)
    ram_pct = 100 * ram.get("used", 0) / max(ram.get("total", 1), 1) if ram else 0
    swap_pct = 100 * swap.get("used", 0) / max(swap.get("total", 1), 1) if swap else 0
    sys_html = f"""
<div class="card">
<h2>System (n1-standard-8)</h2>
<div class="metric"><span class="k">CPU</span><span class="v">{cpu_pct if cpu_pct is not None else "?"}%</span></div>
{bar(cpu_pct or 0)}
<div class="metric"><span class="k">RAM</span><span class="v">{ram.get("used","?")} / {ram.get("total","?")} MiB ({ram_pct:.0f}%)</span></div>
{bar(ram_pct)}
<div class="metric"><span class="k">Swap</span><span class="v">{swap.get("used","?")} / {swap.get("total","?")} MiB ({swap_pct:.0f}%)</span></div>
{bar(swap_pct, 30, 70)}
<div class="metric"><span class="k">Disk /</span><span class="v">{disk.get("used","?")} / {disk.get("total","?")} ({disk.get("pct","?")})</span></div>
</div>
"""

    # Process card
    procs = p.get("procs", [])
    proc_rows = "".join(
        f"<tr><td>{escape(pr['pid'])}</td><td>{escape(pr['elapsed'])}</td>"
        f"<td>{escape(pr['state'])}</td><td>{escape(str(pr['cpu']))}%</td>"
        f"<td>{escape(pr['args'][:70])}</td></tr>"
        for pr in procs
    )
    proc_html = f"""
<div class="card">
<h2>Benchmark Processes</h2>
{'<table><tr><th>PID</th><th>Elapsed</th><th>State</th><th>CPU%</th><th>Command</th></tr>' + proc_rows + '</table>'
 if proc_rows else '<span class="muted">no benchmark process running</span>'}
</div>
"""

    # Recent completions
    recent = p.get("recent", [])
    recent_rows = []
    for line in recent:
        try:
            r = json.loads(line)
            mark = '<span class="ok">✓</span>' if r.get('correct') is True else \
                   ('<span class="bad">✗</span>' if r.get('correct') is False else '<span class="muted">?</span>')
            recent_rows.append(
                f"<tr><td>{escape(r.get('benchmark',''))}</td>"
                f"<td>{escape(str(r.get('item_id','')))}</td>"
                f"<td>{escape(r.get('condition',''))}</td>"
                f"<td>{mark}</td>"
                f"<td>{escape(str(r.get('predicted','')))}</td>"
                f"<td>{r.get('gen_seconds',0):.0f}s</td></tr>"
            )
        except Exception:
            recent_rows.append(f"<tr><td colspan=6 class='muted'>{escape(line[:100])}</td></tr>")
    recent_html = f"""
<div class="card">
<h2>Last {len(recent)} Completions</h2>
{'<table><tr><th>Bench</th><th>Item</th><th>Cond</th><th>✓</th><th>Pred</th><th>Time</th></tr>' + "".join(reversed(recent_rows)) + '</table>'
 if recent_rows else '<span class="muted">no completions yet</span>'}
</div>
"""

    body = f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{POLL_INTERVAL}">
<title>Phronesis Live Dashboard</title>
<style>{CSS}</style></head>
<body>
<h1>Phronesis hard_probe_v2 — live dashboard</h1>
<div class="muted">
  VM {VM_NAME} · {VM_ZONE} · polling every {POLL_INTERVAL}s · last update: {last_str}
</div>
{err_html}
<div class="grid">
{progress_html}
{gpu_html}
{sys_html}
</div>
{proc_html}
{recent_html}
<div class="muted" style="margin-top:24px;font-size:11px">
  Auto-refresh every {POLL_INTERVAL}s. Poller runs in a background thread.
</div>
</body></html>
"""
    return body


# ─── HTTP server ─────────────────────────────────────────────────────────────

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = render_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/status.json":
            with LOCK:
                body = json.dumps({
                    "last_update": STATE["last_update"].isoformat() if STATE["last_update"] else None,
                    "error": STATE["error"],
                    "payload": STATE["payload"],
                }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *_):  # silence default logging
        pass


def main():
    t = threading.Thread(target=poller_thread, daemon=True)
    t.start()
    # Trigger one poll immediately so the page isn't blank on first load
    ok, data, dt = poll_once()
    with LOCK:
        STATE["last_update"] = datetime.now(); STATE["last_duration_s"] = dt
        if ok: STATE["payload"] = data
        else: STATE["error"] = data

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"→ open http://localhost:{PORT} in a browser")
        print(f"  polling VM '{VM_NAME}' in zone {VM_ZONE} every {POLL_INTERVAL}s")
        print(f"  press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nshutting down")


if __name__ == "__main__":
    main()
