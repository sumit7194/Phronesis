"""
Local (Mac) live dashboard — mirrors dashboard_vm.py, adapted for macOS.

  - Uses psutil (cross-platform) instead of /proc + nvidia-smi
  - Reports MPS as "Apple Silicon (unified memory)"; no discrete GPU util
  - Binds to 127.0.0.1 only (no firewall needed)
  - 60s refresh (local access, no browser throttling concern)

Usage:
    .venv/bin/python dashboard_local.py   # then open http://127.0.0.1:8081
"""
from __future__ import annotations
import http.server
import json
import re
import socketserver
import subprocess
import threading
import time
from collections import deque
from datetime import datetime
from html import escape
from pathlib import Path

import psutil

PORT = 8081
REFRESH = 60

MVP = Path(__file__).parent
BP_ROOT = MVP / "results" / "benchmark_probe"
SUMMARY_PATH = BP_ROOT / "summary.jsonl"
PROBE_DIR = BP_ROOT / "hard_probe_v2"  # where --benchmark hard_probe_v2 writes
HARD_PROBE_ITEMS_PER_COND = 19

LIVE_LOG = Path("/tmp/phronesis_local.log")
LIVE_WINDOW_SEC = 90
LIVE_POLL_SEC = 3
CHARS_PER_TOKEN = 4.0

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_live_state = {
    "offset": 0, "mtime": 0.0, "samples": deque(),
    "last_sample_t": 0.0, "log_present": False, "initialized": False,
}
_live_lock = threading.Lock()


def _live_poll_once():
    try:
        if not LIVE_LOG.exists():
            with _live_lock:
                _live_state["log_present"] = False
            return
        st = LIVE_LOG.stat()
        with _live_lock:
            if not _live_state["initialized"]:
                _live_state["offset"] = st.st_size
                _live_state["mtime"] = st.st_mtime
                _live_state["initialized"] = True
                _live_state["log_present"] = True
                return
            if st.st_size < _live_state["offset"] or st.st_mtime < _live_state["mtime"] - 1:
                _live_state["offset"] = 0
                _live_state["samples"].clear()
            start_offset = _live_state["offset"]
        with open(LIVE_LOG, "rb") as f:
            f.seek(start_offset)
            new_bytes = f.read()
            new_offset = f.tell()
        text = _ANSI_RE.sub("", new_bytes.decode("utf-8", errors="ignore"))
        now = time.time()
        with _live_lock:
            _live_state["offset"] = new_offset
            _live_state["mtime"] = st.st_mtime
            _live_state["log_present"] = True
            if text:
                _live_state["samples"].append((now, len(text)))
                _live_state["last_sample_t"] = now
            cutoff = now - LIVE_WINDOW_SEC
            while _live_state["samples"] and _live_state["samples"][0][0] < cutoff:
                _live_state["samples"].popleft()
    except Exception:
        pass


def _live_poll_loop():
    while True:
        _live_poll_once()
        time.sleep(LIVE_POLL_SEC)


def read_live_tpm():
    with _live_lock:
        if not _live_state["log_present"] or not _live_state["samples"]:
            return None, 0, 0
        now = time.time()
        samples = list(_live_state["samples"])
    total_chars = sum(c for _, c in samples)
    oldest_t = samples[0][0]
    elapsed = max(now - oldest_t, 1.0)
    if elapsed < 10:
        return None, total_chars, elapsed
    tokens = total_chars / CHARS_PER_TOKEN
    return tokens / (elapsed / 60.0), total_chars, elapsed


# ─── Metric collectors ──────────────────────────────────────────────────────

def read_system():
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    du = psutil.disk_usage("/")
    return {
        "cpu_pct": psutil.cpu_percent(interval=0.3),
        "cpu_count": psutil.cpu_count(logical=True),
        "ram_used": vm.used // (1024 * 1024),
        "ram_total": vm.total // (1024 * 1024),
        "ram_pct": vm.percent,
        "swap_used": sw.used // (1024 * 1024),
        "swap_total": sw.total // (1024 * 1024),
        "swap_pct": sw.percent,
        "disk_used": du.used // (1024 ** 3),
        "disk_total": du.total // (1024 ** 3),
        "disk_pct": round(du.percent, 0),
    }


def read_procs():
    targets = []
    for p in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent",
                                  "memory_percent", "create_time"]):
        try:
            cmd = " ".join(p.info.get("cmdline") or [])
            if any(k in cmd for k in ("run_benchmark.py", "run_hard_probe",
                                      "rescore_bench", "dashboard_local")):
                elapsed = int(time.time() - p.info["create_time"])
                hh, rem = divmod(elapsed, 3600)
                mm, ss = divmod(rem, 60)
                targets.append({
                    "pid": p.info["pid"],
                    "elapsed": f"{hh:02d}:{mm:02d}:{ss:02d}" if hh else f"{mm:02d}:{ss:02d}",
                    "cpu": f"{p.info.get('cpu_percent') or 0:.0f}",
                    "mem": f"{p.info.get('memory_percent') or 0:.1f}",
                    "cmd": cmd[:100],
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return targets


def _fmt_val(x, maxlen=18):
    if x is None:
        return "—"
    s = str(x).replace("\n", " ").strip()
    return s if len(s) <= maxlen else s[: maxlen - 1] + "…"


def read_probe_items():
    items = {}
    mtimes = {}
    for cond in ("baseline", "steered"):
        d = PROBE_DIR / cond
        if not d.is_dir():
            continue
        for jf in d.iterdir():
            if jf.suffix != ".json":
                continue
            try:
                data = json.load(open(jf))
            except Exception:
                continue
            iid = str(data.get("item_id"))
            if iid not in items:
                items[iid] = {
                    "item_id": iid,
                    "benchmark": data.get("benchmark", "?"),
                    "gold": data.get("gold"),
                    "baseline": None,
                    "steered": None,
                }
            chars = len(data.get("response_thinking", "") or "") + len(data.get("response_answer", "") or "")
            items[iid][cond] = {
                "correct": data.get("correct"),
                "predicted": data.get("predicted"),
                "gen_seconds": data.get("gen_seconds", 0),
                "chars": chars,
            }
            mt = jf.stat().st_mtime
            mtimes[iid] = max(mtimes.get(iid, 0), mt)
    rows = list(items.values())
    rows.sort(key=lambda r: mtimes.get(r["item_id"], 0), reverse=True)
    return rows


def read_progress():
    out = {"rows": 0, "probe_counts": {"baseline": 0, "steered": 0}}
    if SUMMARY_PATH.exists():
        out["rows"] = sum(1 for l in SUMMARY_PATH.read_text().splitlines() if l.strip())
    for cond in ("baseline", "steered"):
        d = PROBE_DIR / cond
        if d.is_dir():
            out["probe_counts"][cond] = sum(1 for f in d.iterdir() if f.suffix == ".json")
    return out


# ─── HTML ───────────────────────────────────────────────────────────────────

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
.ok{color:#7ee787}.warn{color:#d29922}.bad{color:#f85149}.muted{color:#8b949e}
table{width:100%;border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:12px}
th{text-align:left;color:#8b949e;padding:4px 8px;border-bottom:1px solid #30363d}
td{padding:4px 8px;border-bottom:1px solid #21262d}
"""


def bar(pct, warn=70, bad=90):
    pct = max(0, min(100, pct or 0))
    cls = "" if pct < warn else ("warn" if pct < bad else "bad")
    return f'<div class="bar"><div class="bar-fill {cls}" style="width:{pct:.0f}%"></div></div>'


def render():
    sysm = read_system()
    procs = read_procs()
    prog = read_progress()

    probe = prog["probe_counts"]
    total_probe = HARD_PROBE_ITEMS_PER_COND * 2
    done_probe = probe["baseline"] + probe["steered"]
    pct_prog = 100 * done_probe / total_probe

    live_tpm, live_chars, live_win = read_live_tpm()
    if live_tpm is None:
        live_str = '<span class="muted">warming up…</span>' if live_win > 0 else '<span class="muted">no log yet</span>'
    elif live_tpm < 5:
        live_str = f'<span class="muted">idle (between items)</span>'
    else:
        live_str = f'<span class="ok">{live_tpm:.0f} tok/min</span> <span class="muted">· {live_win:.0f}s win</span>'

    prog_html = f"""
<div class="card"><h2>Benchmark Progress</h2>
<div class="metric"><span class="k">hard_probe_v2 baseline</span><span class="v">{probe['baseline']} / {HARD_PROBE_ITEMS_PER_COND}</span></div>
<div class="metric"><span class="k">hard_probe_v2 steered</span><span class="v">{probe['steered']} / {HARD_PROBE_ITEMS_PER_COND}</span></div>
<div class="metric"><span class="k">probe completion</span><span class="v">{done_probe} / {total_probe} ({pct_prog:.0f}%)</span></div>
{bar(pct_prog)}
<div class="metric"><span class="k">live generation</span><span class="v">{live_str}</span></div>
<div class="metric muted"><span class="k">summary.jsonl rows</span><span class="v">{prog['rows']}</span></div>
</div>
"""

    sys_html = f"""
<div class="card"><h2>System (Apple Silicon)</h2>
<div class="metric"><span class="k">CPU ({sysm['cpu_count']} cores)</span><span class="v">{sysm['cpu_pct']:.1f}%</span></div>
{bar(sysm['cpu_pct'])}
<div class="metric"><span class="k">RAM (unified memory)</span><span class="v">{sysm['ram_used']} / {sysm['ram_total']} MiB ({sysm['ram_pct']:.0f}%)</span></div>
{bar(sysm['ram_pct'])}
<div class="metric"><span class="k">Swap</span><span class="v">{sysm['swap_used']} / {sysm['swap_total']} MiB ({sysm['swap_pct']:.0f}%)</span></div>
{bar(sysm['swap_pct'], 30, 70)}
<div class="metric"><span class="k">Disk /</span><span class="v">{sysm['disk_used']} / {sysm['disk_total']} GiB ({sysm['disk_pct']}%)</span></div>
</div>
"""

    gpu_html = """
<div class="card"><h2>GPU (MPS)</h2>
<div class="muted" style="padding:8px 0">Apple Silicon integrated GPU uses unified memory (shown under System RAM above).
No discrete VRAM or util counter — macOS does not expose MPS utilization without sudo powermetrics.</div>
</div>
"""

    if procs:
        rows = "".join(
            f"<tr><td>{pr['pid']}</td><td>{escape(pr['elapsed'])}</td>"
            f"<td>{escape(pr['cpu'])}%</td><td>{escape(pr['mem'])}%</td>"
            f"<td>{escape(pr['cmd'])}</td></tr>"
            for pr in procs
        )
        proc_html = f"""
<div class="card"><h2>Benchmark Processes</h2>
<table><tr><th>PID</th><th>Elapsed</th><th>CPU%</th><th>MEM%</th><th>Command</th></tr>{rows}</table></div>
"""
    else:
        proc_html = '<div class="card"><h2>Benchmark Processes</h2><span class="muted">none running</span></div>'

    items = read_probe_items()

    CHARS_PER_TOKEN = 4.0

    def cell(cond_d):
        if not cond_d:
            return '<td class="muted">pending</td><td class="muted">—</td><td class="muted">—</td>'
        corr = cond_d.get("correct")
        if corr is True:
            m = '<span class="ok">✓</span>'
        elif corr is False:
            m = '<span class="bad">✗</span>'
        else:
            m = '<span class="muted">?</span>'
        pred = escape(_fmt_val(cond_d.get("predicted")))
        secs = cond_d.get("gen_seconds", 0) or 0
        chars = cond_d.get("chars", 0) or 0
        if secs >= 60:
            tstr = f"{secs/60:.1f}m"
        else:
            tstr = f"{secs:.0f}s"
        if secs > 0 and chars > 0:
            tok_per_min = (chars / CHARS_PER_TOKEN) / (secs / 60.0)
            tstr += f' <span class="muted">· {tok_per_min:.0f} tok/min</span>'
        return f'<td>{m}</td><td class="v">{pred}</td><td class="v">{tstr}</td>'

    done_secs = [x["gen_seconds"] for it in items for x in (it["baseline"], it["steered"]) if x and x.get("gen_seconds")]
    done_secs.sort()
    median_sec = done_secs[len(done_secs)//2] if done_secs else 0
    total_todo = HARD_PROBE_ITEMS_PER_COND * 2
    done_count = len(done_secs)
    remaining = total_todo - done_count
    eta_sec = remaining * median_sec
    eta_h, eta_m = int(eta_sec // 3600), int((eta_sec % 3600) // 60)
    eta_str = f"{eta_h}h {eta_m}m" if median_sec > 0 else "unknown"

    by_bench = {}
    for it in items:
        b = it["benchmark"]
        for side in (it["baseline"], it["steered"]):
            if side and side.get("gen_seconds"):
                by_bench.setdefault(b, []).append(side["gen_seconds"])
    bench_rows = "".join(
        f'<tr><td>{escape(b)}</td><td class="v">{len(v)}</td>'
        f'<td class="v">{sorted(v)[len(v)//2]/60:.1f}m</td></tr>'
        for b, v in sorted(by_bench.items())
    ) or '<tr><td colspan="3" class="muted">no data yet</td></tr>'

    eta_card = f"""
<div class="card"><h2>ETA &amp; Speed</h2>
<div class="metric"><span class="k">median item time</span><span class="v">{median_sec/60:.1f}m</span></div>
<div class="metric"><span class="k">items remaining</span><span class="v">{remaining} / {total_todo}</span></div>
<div class="metric"><span class="k">projected ETA</span><span class="v">{eta_str}</span></div>
<div class="metric muted" style="padding-top:8px"><span class="k">by benchmark</span><span class="v">done · median</span></div>
<table>{bench_rows}</table>
</div>
"""

    b_done = sum(1 for i in items if i["baseline"])
    s_done = sum(1 for i in items if i["steered"])
    b_correct = sum(1 for i in items if i["baseline"] and i["baseline"].get("correct") is True)
    s_correct = sum(1 for i in items if i["steered"] and i["steered"].get("correct") is True)

    if items:
        rows_html = "".join(
            f'<tr><td>{escape(it["benchmark"])}</td>'
            f'<td class="v">{escape(str(it["item_id"]))}</td>'
            f'<td class="v">{escape(_fmt_val(it["gold"]))}</td>'
            f'{cell(it["baseline"])}'
            f'{cell(it["steered"])}</tr>'
            for it in items
        )
        recent_html = f"""
<div class="card"><h2>Results — {b_done}/{HARD_PROBE_ITEMS_PER_COND} baseline ({b_correct}✓)  ·  {s_done}/{HARD_PROBE_ITEMS_PER_COND} steered ({s_correct}✓)</h2>
<table>
<tr><th rowspan="2">Bench</th><th rowspan="2">Item</th><th rowspan="2">Gold</th>
  <th colspan="3" style="border-left:2px solid #30363d;text-align:center">Baseline</th>
  <th colspan="3" style="border-left:2px solid #30363d;text-align:center">Steered</th></tr>
<tr><th style="border-left:2px solid #30363d">✓</th><th>Pred</th><th>Time</th>
  <th style="border-left:2px solid #30363d">✓</th><th>Pred</th><th>Time</th></tr>
{rows_html}
</table></div>
"""
    else:
        recent_html = '<div class="card"><h2>Results</h2><span class="muted">no items yet — first generation in progress</span></div>'

    now = datetime.now().strftime("%H:%M:%S %Z")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{REFRESH}">
<title>Phronesis Live (local)</title><style>{CSS}</style></head><body>
<h1>Phronesis hard_probe_v2 — local (MPS)</h1>
<div class="muted">localhost dashboard · {now} · refresh every {REFRESH}s</div>
<div class="grid">{prog_html}{eta_card}{sys_html}{gpu_html}</div>
{proc_html}
{recent_html}
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = render().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *_): pass


class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    threading.Thread(target=_live_poll_loop, daemon=True).start()
    # Bind to localhost only — no external access
    with ReuseTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"→ local dashboard on http://127.0.0.1:{PORT}")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\nshutting down")


if __name__ == "__main__":
    main()
