"""
VM-side live dashboard — runs ON phronesis-v2, reads local files directly.
Access from your laptop via http://<VM_EXTERNAL_IP>:8080

Advantages over the local-polling version:
  - Direct file reads (no 20-30s ssh round-trip per poll)
  - Cheap 5-second refresh
  - Live data straight from disk + nvidia-smi + /proc

Security note: the HTTP server binds to 0.0.0.0. A firewall rule must allow
your IP to reach port 8080. See run_dashboard_on_vm.sh for the gcloud command
that creates a restricted firewall rule.

Usage (on the VM):
    python3 dashboard_vm.py
"""
from __future__ import annotations
import http.server
import json
import os
import re
import socketserver
import subprocess
import threading
import time
from collections import deque
from datetime import datetime
from html import escape
from pathlib import Path

PORT = 8080
REFRESH = 300  # browser meta-refresh interval (seconds)

BP_ROOT = Path("/home/sumit/phronesis/mvp/results/benchmark_probe")
SUMMARY_PATH = BP_ROOT / "summary.jsonl"

# The runner writes per-item JSONs under benchmark_probe/{--benchmark arg}/{condition}/
# For `--benchmark hard_probe_v2`, everything lands under hard_probe_v2/{baseline,steered}/
# Active probe: v3 is the follow-up sweep. Falls back to v2 if v3 dir doesn't exist.
_V3 = BP_ROOT / "hard_probe_v3"
_V2 = BP_ROOT / "hard_probe_v2"
PROBE_DIR = _V3 if _V3.exists() else _V2
PROBE_NAME = PROBE_DIR.name
HARD_PROBE_ITEMS_PER_COND = 9 if PROBE_NAME == "hard_probe_v3" else 19

LIVE_LOG = Path("/tmp/hard_probe.log")
LIVE_WINDOW_SEC = 90          # rolling window for TPM estimate
LIVE_POLL_SEC = 3             # background poll cadence
CHARS_PER_TOKEN = 4.0


# ─── Live-tail poller: reads new bytes from run log, maintains rolling samples ─

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_live_state = {
    "offset": 0,
    "mtime": 0.0,
    "samples": deque(),    # (timestamp, chars_added) for rolling window
    "last_sample_t": 0.0,
    "log_present": False,
    "initialized": False,  # True once we've seeked to EOF
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
            # On first poll with an existing log, skip all historical content
            if not _live_state["initialized"]:
                _live_state["offset"] = st.st_size
                _live_state["mtime"] = st.st_mtime
                _live_state["initialized"] = True
                _live_state["log_present"] = True
                return
            # Handle rotation/truncation
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
    """Return (tpm, chars_in_window_total, window_sec_actual) or (None, 0, 0)."""
    with _live_lock:
        if not _live_state["log_present"] or not _live_state["samples"]:
            return None, 0, 0
        now = time.time()
        samples = list(_live_state["samples"])
    total_chars = sum(c for _, c in samples)
    oldest_t = samples[0][0]
    elapsed = max(now - oldest_t, 1.0)
    # Require at least 10s of data before showing a rate (avoid noisy first reading)
    if elapsed < 10:
        return None, total_chars, elapsed
    tokens = total_chars / CHARS_PER_TOKEN
    return tokens / (elapsed / 60.0), total_chars, elapsed


# ─── Local metric collectors (run ON the VM, read /proc and nvidia-smi) ─────

def read_gpu():
    try:
        r = subprocess.run([
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
            "--format=csv,noheader,nounits"
        ], capture_output=True, text=True, timeout=3)
        parts = [x.strip() for x in r.stdout.strip().split(",")]
        if len(parts) >= 4:
            return {
                "util": parts[0], "mem_used": parts[1], "mem_total": parts[2],
                "temp": parts[3],
                "power": parts[4] if len(parts) > 4 else "?",
                "power_cap": parts[5] if len(parts) > 5 else "?",
            }
    except Exception as e:
        return {"err": str(e)}
    return {}


def read_mem():
    out = {}
    try:
        with open("/proc/meminfo") as f:
            m = {line.split(":")[0]: int(line.split(":")[1].split()[0]) for line in f if ":" in line}
        out["ram"] = {
            "total": m.get("MemTotal", 0) // 1024,      # to MiB
            "used": (m.get("MemTotal", 0) - m.get("MemAvailable", 0)) // 1024,
            "available": m.get("MemAvailable", 0) // 1024,
        }
        out["swap"] = {
            "total": m.get("SwapTotal", 0) // 1024,
            "used": (m.get("SwapTotal", 0) - m.get("SwapFree", 0)) // 1024,
        }
    except Exception as e:
        out["err"] = str(e)
    return out


# CPU tracker — persistent stat between calls for true delta
_CPU_PREV = {"idle": 0, "total": 0, "t": 0}
def read_cpu():
    try:
        with open("/proc/stat") as f:
            line = f.readline()
        nums = list(map(int, line.split()[1:]))
        idle = nums[3]
        total = sum(nums)
        now = time.time()
        prev = _CPU_PREV
        pct = None
        if prev["total"] > 0 and (total - prev["total"]) > 0:
            pct = round(100 * (1 - (idle - prev["idle"]) / (total - prev["total"])), 1)
        _CPU_PREV["idle"] = idle; _CPU_PREV["total"] = total; _CPU_PREV["t"] = now
        return {"pct": pct}
    except Exception as e:
        return {"err": str(e)}


def read_disk():
    try:
        r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=2)
        parts = r.stdout.splitlines()[-1].split()
        return {"total": parts[1], "used": parts[2], "avail": parts[3], "pct": parts[4]}
    except Exception as e:
        return {"err": str(e)}


def read_procs():
    try:
        r = subprocess.run(
            ["ps", "-eo", "pid,etime,stat,pcpu,pmem,comm,args", "--no-headers"],
            capture_output=True, text=True, timeout=3,
        )
        procs = []
        for line in r.stdout.splitlines():
            if "run_benchmark" in line or "run_hard_probe" in line or "rescore_bench" in line:
                parts = line.split(None, 6)
                procs.append({
                    "pid": parts[0], "elapsed": parts[1], "state": parts[2],
                    "cpu": parts[3], "mem": parts[4], "comm": parts[5],
                    "args": parts[6] if len(parts) > 6 else "",
                })
        return procs
    except Exception as e:
        return [{"err": str(e)}]


def _fmt_val(x, maxlen=18):
    """Trim/format a gold or predicted answer for display."""
    if x is None:
        return "—"
    s = str(x).replace("\n", " ").strip()
    return s if len(s) <= maxlen else s[: maxlen - 1] + "…"


def discover_conditions():
    """Return ordered list of subdir names (each is a condition/label) under PROBE_DIR."""
    if not PROBE_DIR.is_dir():
        return []
    conds = [d.name for d in PROBE_DIR.iterdir() if d.is_dir()]
    # Conventional order: baseline first, then steered*, then others alphabetical
    conds.sort(key=lambda c: (
        0 if c == "baseline" else 1 if c == "steered" else 2 if c.startswith("steered") else 3,
        c
    ))
    return conds


def read_probe_items():
    """Read every per-item JSON under PROBE_DIR and key by (item_id, condition_label).

    Returns (items, conditions) where:
      items is list of dicts: {item_id, benchmark, gold, <cond_label>: {correct,...}, ...}
      conditions is the ordered list of condition labels seen.
    """
    conditions = discover_conditions()
    items = {}
    mtimes = {}
    for cond in conditions:
        d = PROBE_DIR / cond
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
    return rows, conditions


def read_progress():
    out = {"rows": 0}
    try:
        if SUMMARY_PATH.exists():
            with open(SUMMARY_PATH) as f:
                out["rows"] = sum(1 for l in f if l.strip())
    except Exception as e:
        out["err"] = str(e)
    try:
        counts = {}
        for d in PROBE_DIR.iterdir() if PROBE_DIR.is_dir() else []:
            if d.is_dir():
                counts[d.name] = sum(1 for f in d.iterdir() if f.suffix == ".json")
        out["probe_counts"] = counts
    except Exception as e:
        out["probe_err"] = str(e)
    return out


# ─── HTML ────────────────────────────────────────────────────────────────────

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
    gpu = read_gpu()
    mem = read_mem()
    cpu = read_cpu()
    disk = read_disk()
    procs = read_procs()
    prog = read_progress()

    ram = mem.get("ram", {})
    swap = mem.get("swap", {})
    ram_pct = 100 * ram.get("used", 0) / max(ram.get("total", 1), 1) if ram else 0
    swap_pct = 100 * swap.get("used", 0) / max(swap.get("total", 1), 1) if swap else 0

    rows = prog.get("rows", 0)
    probe_counts = prog.get("probe_counts", {})
    # Order conditions: baseline first, steered labels next
    ordered_conds = sorted(
        probe_counts.keys(),
        key=lambda c: (0 if c == "baseline" else 1 if c == "steered" else 2, c)
    )
    total_probe = HARD_PROBE_ITEMS_PER_COND * max(len(ordered_conds), 1)
    done_probe = sum(probe_counts.values())
    pct_prog = 100 * done_probe / max(total_probe, 1)

    # Live generation rate (from log tail)
    live_tpm, live_chars, live_win = read_live_tpm()
    if live_tpm is None:
        live_str = '<span class="muted">warming up…</span>' if live_win > 0 else '<span class="muted">no log yet</span>'
    elif live_tpm < 5:
        live_str = f'<span class="muted">idle (between items)</span>'
    else:
        live_str = f'<span class="ok">{live_tpm:.0f} tok/min</span> <span class="muted">· {live_win:.0f}s win</span>'

    prog_rows = "".join(
        f'<div class="metric"><span class="k">{PROBE_NAME} {escape(c)}</span>'
        f'<span class="v">{probe_counts[c]} / {HARD_PROBE_ITEMS_PER_COND}</span></div>'
        for c in ordered_conds
    ) or '<div class="metric muted"><span class="k">no conditions yet</span><span class="v">—</span></div>'
    prog_html = f"""
<div class="card">
<h2>{PROBE_NAME} progress</h2>
{prog_rows}
<div class="metric"><span class="k">total</span><span class="v">{done_probe} / {total_probe} ({pct_prog:.0f}%)</span></div>
{bar(pct_prog)}
<div class="metric"><span class="k">live generation</span><span class="v">{live_str}</span></div>
<div class="metric muted"><span class="k">summary.jsonl rows</span><span class="v">{rows}</span></div>
</div>
"""
    # GPU
    mem_pct_gpu = 100 * int(gpu.get("mem_used","0") or 0) / max(int(gpu.get("mem_total","1") or 1), 1) if "mem_used" in gpu else 0
    gpu_html = f"""
<div class="card"><h2>GPU (Tesla T4)</h2>
<div class="metric"><span class="k">GPU util</span><span class="v">{gpu.get("util","?")}%</span></div>
{bar(int(gpu.get("util","0") or 0))}
<div class="metric"><span class="k">VRAM</span><span class="v">{gpu.get("mem_used","?")} / {gpu.get("mem_total","?")} MiB ({mem_pct_gpu:.0f}%)</span></div>
{bar(mem_pct_gpu)}
<div class="metric"><span class="k">Temperature</span><span class="v">{gpu.get("temp","?")}°C</span></div>
<div class="metric"><span class="k">Power</span><span class="v">{gpu.get("power","?")} / {gpu.get("power_cap","?")} W</span></div>
</div>
""" if "util" in gpu else '<div class="card"><h2>GPU</h2><span class="muted">no data</span></div>'

    # System
    sys_html = f"""
<div class="card"><h2>System (n1-standard-8)</h2>
<div class="metric"><span class="k">CPU</span><span class="v">{cpu.get("pct", "?")}%</span></div>
{bar(cpu.get("pct") or 0)}
<div class="metric"><span class="k">RAM</span><span class="v">{ram.get("used","?")} / {ram.get("total","?")} MiB ({ram_pct:.0f}%)</span></div>
{bar(ram_pct)}
<div class="metric"><span class="k">Swap</span><span class="v">{swap.get("used","?")} / {swap.get("total","?")} MiB ({swap_pct:.0f}%)</span></div>
{bar(swap_pct, 30, 70)}
<div class="metric"><span class="k">Disk /</span><span class="v">{disk.get("used","?")} / {disk.get("total","?")} ({disk.get("pct","?")})</span></div>
</div>
"""

    # Processes
    if procs and "err" not in procs[0]:
        proc_rows = "".join(
            f"<tr><td>{escape(pr['pid'])}</td><td>{escape(pr['elapsed'])}</td>"
            f"<td>{escape(pr['state'])}</td><td>{escape(pr['cpu'])}%</td>"
            f"<td>{escape(pr['mem'])}%</td><td>{escape(pr['args'][:80])}</td></tr>"
            for pr in procs
        )
        proc_html = f"""
<div class="card"><h2>Benchmark Processes</h2>
<table><tr><th>PID</th><th>Elapsed</th><th>State</th><th>CPU%</th><th>MEM%</th><th>Command</th></tr>{proc_rows}</table>
</div>"""
    else:
        proc_html = '<div class="card"><h2>Benchmark Processes</h2><span class="muted">none running</span></div>'

    # Per-item results across N conditions (dynamic label set)
    items, conditions = read_probe_items()

    CHARS_PER_TOKEN = 4.0

    def cell(cond_d):
        if not cond_d:
            return '<td class="muted">·</td><td class="muted">—</td><td class="muted">—</td>'
        corr = cond_d.get("correct")
        if corr is True:
            m = '<span class="ok">✓</span>'
        elif corr is False:
            m = '<span class="bad">✗</span>'
        else:
            m = '<span class="muted">?</span>'
        pred = escape(_fmt_val(cond_d.get("predicted"), maxlen=14))
        secs = cond_d.get("gen_seconds", 0) or 0
        chars = cond_d.get("chars", 0) or 0
        if secs >= 60:
            tstr = f"{secs/60:.1f}m"
        else:
            tstr = f"{secs:.0f}s"
        if secs > 0 and chars > 0:
            tok_per_min = (chars / CHARS_PER_TOKEN) / (secs / 60.0)
            tstr += f'<br><span class="muted" style="font-size:10px">{tok_per_min:.0f} tpm</span>'
        return f'<td>{m}</td><td class="v">{pred}</td><td class="v">{tstr}</td>'

    # ETA + per-bench speed
    all_gen_secs = [c.get("gen_seconds") for it in items for k, c in it.items()
                    if k in conditions and c and c.get("gen_seconds")]
    all_gen_secs.sort()
    median_sec = all_gen_secs[len(all_gen_secs)//2] if all_gen_secs else 0
    total_todo = HARD_PROBE_ITEMS_PER_COND * max(len(conditions), 1)
    done_count = len(all_gen_secs)
    remaining = max(0, total_todo - done_count)
    eta_sec = remaining * median_sec
    eta_h, eta_m = int(eta_sec // 3600), int((eta_sec % 3600) // 60)
    eta_str = f"{eta_h}h {eta_m}m" if median_sec > 0 else "unknown"

    by_bench = {}
    for it in items:
        b = it["benchmark"]
        for k, c in it.items():
            if k in conditions and c and c.get("gen_seconds"):
                by_bench.setdefault(b, []).append(c["gen_seconds"])
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

    # Per-condition summary line: "baseline: 3/9 (2✓) · steered_L22_a12: 1/9 (1✓) · ..."
    summary_bits = []
    for c in conditions:
        done = sum(1 for i in items if i.get(c))
        correct = sum(1 for i in items if i.get(c) and i[c].get("correct") is True)
        summary_bits.append(f"{escape(c)}: {done}/{HARD_PROBE_ITEMS_PER_COND} ({correct}✓)")
    summary_line = "  ·  ".join(summary_bits) if summary_bits else "no conditions yet"

    if items and conditions:
        cond_header = "".join(
            f'<th colspan="3" style="border-left:2px solid #30363d;text-align:center">{escape(c)}</th>'
            for c in conditions
        )
        subheader = "".join(
            '<th style="border-left:2px solid #30363d">✓</th><th>Pred</th><th>Time</th>'
            for _ in conditions
        )
        rows_html = "".join(
            f'<tr><td>{escape(it["benchmark"])}</td>'
            f'<td class="v">{escape(str(it["item_id"]))[:22]}</td>'
            f'<td class="v">{escape(_fmt_val(it["gold"], maxlen=10))}</td>'
            + "".join(cell(it.get(c)) for c in conditions)
            + '</tr>'
            for it in items
        )
        items_html = f"""
<div class="card"><h2>Results — {summary_line}</h2>
<table>
<tr><th rowspan="2">Bench</th><th rowspan="2">Item</th><th rowspan="2">Gold</th>
{cond_header}</tr>
<tr>{subheader}</tr>
{rows_html}
</table></div>
"""
    else:
        items_html = '<div class="card"><h2>Results</h2><span class="muted">no items yet — first generation in progress</span></div>'

    recent_html = items_html

    now = datetime.now().strftime("%H:%M:%S UTC")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{REFRESH}">
<title>Phronesis Live</title><style>{CSS}</style></head><body>
<h1>Phronesis {PROBE_NAME} — live</h1>
<div class="muted">VM-native dashboard · server time {now} · refresh every {REFRESH}s</div>
<div class="grid">{prog_html}{eta_card}{gpu_html}{sys_html}</div>
{proc_html}
{recent_html}
</body></html>"""


# ─── HTTP server ─────────────────────────────────────────────────────────────

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
    # Kick off the live-tail poller in the background
    threading.Thread(target=_live_poll_loop, daemon=True).start()

    with ReuseTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"→ dashboard on http://0.0.0.0:{PORT}")
        print(f"  make sure firewall allows your IP to reach this port")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\nshutting down")


if __name__ == "__main__":
    main()
