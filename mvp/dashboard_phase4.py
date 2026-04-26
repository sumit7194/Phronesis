"""
Phronesis phase-4 dashboard — α-sweep + 4×4 specificity matrix progress.

Runs ON the VM, serves on http://0.0.0.0:8080. Read-only HTML, meta-refresh 10s.

Features (modeled on dashboard_vm.py):
  - Phase summary card (model, virtue, target eval, current cell, cells done, ETA)
  - GPU (util, VRAM, temp, power, with bars)
  - System (CPU, RAM, swap, disk)
  - Live TPM from rolling log poll
  - Sweep matrix: virtue × (layer × α) grid showing per-cell n_items + mean score
  - Process list (python3 procs with CPU/MEM)
  - Live generation panel (current prompt + streaming tail of latest item)
  - Recent log tail (cleaned of ANSI)

Detects current phase by which progress JSON exists / is newer:
  - results/alpha_sweep_progress.json
  - results/specificity_matrix_progress.json

Usage (on VM):
    cd ~/phronesis/mvp && nohup python3 dashboard_phase4.py > /tmp/dashboard_phase4.log 2>&1 &
"""
from __future__ import annotations
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import threading
import time
from collections import deque, defaultdict
from datetime import datetime
from html import escape
from pathlib import Path

PORT = 8080
REFRESH = 10  # seconds

HOME = Path(os.path.expanduser("~"))
HERE = Path(__file__).parent
RESULTS = HERE / "results"
PROBE_DIR = RESULTS / "benchmark_probe"

ALPHA_PROGRESS = RESULTS / "alpha_sweep_progress.json"
SPEC_PROGRESS = RESULTS / "specificity_matrix_progress.json"
ALPHA_SWEEP_DIR = RESULTS / "alpha_sweep"

LOG_CANDIDATES = [
    HOME / "phase4.log",
    HOME / "alpha_sweep.log",
    HOME / "specificity_matrix.log",
]

# Eval → target virtue (mirrors analysis/config.yaml)
EVAL_TO_VIRTUE = {
    "aime": "CC",
    "abstention": "IH",
    "eg-eval": "EG",
    "rt-eval": "RT",
}
VIRTUE_TO_EVAL = {v: k for k, v in EVAL_TO_VIRTUE.items()}
VIRTUES_ORDER = ["CC", "IH", "EG", "RT"]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
HEADER_RE = re.compile(r"^([a-z0-9_-]+)\[(baseline|steered)\]\s+item\s+(\S+)", re.MULTILINE)
LABEL_RE = re.compile(
    r"alpha_sweep_(?P<model>[a-z0-9_-]+)_v(?P<virtue>[A-Z]{2})_L(?P<layer>\d+)_a(?P<alpha>\d+)_(?P<eval>[a-z-]+)"
)
BASELINE_RE = re.compile(
    r"alpha_sweep_baseline_(?P<model>[a-z0-9_-]+)_(?P<eval>[a-z-]+)"
)


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


# ─── Live TPM poller ────────────────────────────────────────────────────────

LIVE_WINDOW_SEC = 90
_live_state = {
    "offset": 0,
    "mtime": 0.0,
    "samples": deque(),
    "log_path": None,
    "initialized": False,
}
_live_lock = threading.Lock()


def newest_log() -> Path | None:
    candidates = [p for p in LOG_CANDIDATES if p.exists()]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def _live_poll_once():
    p = newest_log()
    if p is None:
        with _live_lock:
            _live_state["log_path"] = None
        return
    try:
        st = p.stat()
        with _live_lock:
            if _live_state["log_path"] != p:
                _live_state["log_path"] = p
                _live_state["offset"] = st.st_size  # start from EOF on new log
                _live_state["mtime"] = st.st_mtime
                _live_state["initialized"] = True
                _live_state["samples"].clear()
                return
            if not _live_state["initialized"]:
                _live_state["offset"] = st.st_size
                _live_state["initialized"] = True
                _live_state["mtime"] = st.st_mtime
                return
            if st.st_size < _live_state["offset"]:
                _live_state["offset"] = 0
                _live_state["samples"].clear()
            start_offset = _live_state["offset"]
        with open(p, "rb") as f:
            f.seek(start_offset)
            chunk = f.read()
        new_offset = start_offset + len(chunk)
        text = strip_ansi(chunk.decode(errors="ignore"))
        now = time.time()
        with _live_lock:
            _live_state["offset"] = new_offset
            _live_state["mtime"] = st.st_mtime
            if text:
                _live_state["samples"].append((now, len(text)))
            cutoff = now - LIVE_WINDOW_SEC
            while _live_state["samples"] and _live_state["samples"][0][0] < cutoff:
                _live_state["samples"].popleft()
    except Exception:
        pass


def _live_poll_loop():
    while True:
        _live_poll_once()
        time.sleep(2)


def read_live_tpm():
    """Return (tpm, total_chars, window_sec) or (None, 0, 0)."""
    with _live_lock:
        if _live_state["log_path"] is None or not _live_state["samples"]:
            return None, 0, 0
        samples = list(_live_state["samples"])
    total = sum(c for _, c in samples)
    oldest = samples[0][0]
    win = max(time.time() - oldest, 1.0)
    chars_per_sec = total / win
    tpm = (chars_per_sec / 4.0) * 60.0  # ~4 chars/token
    return tpm, total, win


# ─── System metrics ─────────────────────────────────────────────────────────

def read_gpu() -> dict:
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        v = [x.strip() for x in out.stdout.strip().split(",")]
        return {
            "util": v[0], "mem_used": v[1], "mem_total": v[2],
            "temp": v[3], "power": v[4], "power_cap": v[5],
        }
    except Exception:
        return {}


def read_mem() -> dict:
    try:
        with open("/proc/meminfo") as f:
            d = {}
            for line in f:
                k, _, v = line.partition(":")
                d[k.strip()] = int(v.strip().split()[0])
        ram_total = d.get("MemTotal", 0) // 1024
        ram_avail = d.get("MemAvailable", 0) // 1024
        ram_used = ram_total - ram_avail
        swap_total = d.get("SwapTotal", 0) // 1024
        swap_free = d.get("SwapFree", 0) // 1024
        swap_used = swap_total - swap_free
        return {"ram": {"total": ram_total, "used": ram_used},
                "swap": {"total": swap_total, "used": swap_used}}
    except Exception:
        return {}


def read_cpu() -> dict:
    try:
        out = subprocess.run(["top", "-bn1"], capture_output=True, text=True, timeout=5)
        for line in out.stdout.splitlines():
            if line.startswith("%Cpu(s):") or "Cpu(s)" in line:
                m = re.search(r"(\d+\.\d+)\s*id", line)
                if m:
                    return {"pct": round(100 - float(m.group(1)), 1)}
    except Exception:
        pass
    return {"pct": None}


def read_disk() -> dict:
    try:
        out = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = out.stdout.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            return {"total": parts[1], "used": parts[2], "pct": parts[4]}
    except Exception:
        pass
    return {}


def read_procs():
    """List interesting python3 processes (run_alpha_sweep, run_benchmark, dashboard)."""
    out = []
    try:
        ps = subprocess.run(
            ["ps", "-eo", "pid,etime,stat,pcpu,pmem,args", "--sort=-pcpu"],
            capture_output=True, text=True, timeout=5,
        )
        for line in ps.stdout.splitlines()[1:]:
            parts = line.split(maxsplit=5)
            if len(parts) < 6:
                continue
            pid, etime, stat, cpu, mem, args = parts
            if "python3" not in args:
                continue
            if not any(k in args for k in ("run_alpha_sweep", "run_benchmark", "dashboard_phase4", "specificity_matrix")):
                continue
            out.append({"pid": pid, "elapsed": etime, "state": stat,
                        "cpu": cpu, "mem": mem, "args": args})
            if len(out) >= 6:
                break
    except Exception:
        pass
    return out


# ─── Progress JSON readers ──────────────────────────────────────────────────

def read_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def pick_active_phase() -> tuple[str, dict]:
    a = read_json(ALPHA_PROGRESS)
    s = read_json(SPEC_PROGRESS)
    a_t = ALPHA_PROGRESS.stat().st_mtime if ALPHA_PROGRESS.exists() else 0
    s_t = SPEC_PROGRESS.stat().st_mtime if SPEC_PROGRESS.exists() else 0
    if s_t > a_t:
        return ("specificity_matrix", s)
    if a_t > 0:
        return ("alpha_sweep", a)
    return ("idle", {})


# ─── Sweep matrix aggregator ────────────────────────────────────────────────

def read_sweep_cells():
    """Walk benchmark_probe to build a per-cell summary dict.

    Returns {model: {virtue: {(layer, alpha) or 'baseline': {n_items, gen_secs, ...}}}}.
    """
    out = defaultdict(lambda: defaultdict(dict))
    if not PROBE_DIR.exists():
        return out
    for eval_dir in PROBE_DIR.iterdir():
        if not eval_dir.is_dir():
            continue
        eval_name = eval_dir.name
        virtue = EVAL_TO_VIRTUE.get(eval_name)
        if virtue is None:
            continue
        for cell_dir in eval_dir.iterdir():
            if not cell_dir.is_dir():
                continue
            label = cell_dir.name
            m_b = BASELINE_RE.match(label)
            m_s = LABEL_RE.match(label)
            if m_b:
                model = m_b.group("model")
                key = "baseline"
            elif m_s:
                model = m_s.group("model")
                if m_s.group("virtue") != virtue:
                    continue
                key = (int(m_s.group("layer")), int(m_s.group("alpha")))
            else:
                continue
            # Count items + sum gen_seconds
            items = []
            for jf in cell_dir.iterdir():
                if jf.suffix != ".json":
                    continue
                try:
                    d = json.load(open(jf))
                except Exception:
                    continue
                items.append(d)
            if not items:
                continue
            gen_secs = [d.get("gen_seconds", 0) or 0 for d in items]
            corrs = [d.get("correct") for d in items]
            preds = [d.get("predicted") for d in items]
            mean_sec = sum(gen_secs) / len(items) if items else 0.0
            n_correct = sum(1 for c in corrs if c is True)
            n_unparsed = sum(1 for c in corrs if c is None)
            # For EG/RT, predicted is "eg_score=12.34" — extract the number
            soft_scores = []
            for p in preds:
                if isinstance(p, str):
                    m = re.search(r"=([+-]?\d+\.?\d*)", p)
                    if m:
                        try:
                            soft_scores.append(float(m.group(1)))
                        except ValueError:
                            pass
            mean_soft = sum(soft_scores) / len(soft_scores) if soft_scores else None
            out[model][virtue][key] = {
                "n_items": len(items),
                "mean_sec": mean_sec,
                "n_correct": n_correct,
                "n_unparsed": n_unparsed,
                "mean_soft": mean_soft,
                "label": label,
            }
    return out


def render_sweep_matrix(cells: dict, active_model: str | None) -> str:
    """For the active model, render virtue × (layer × α) grid."""
    if not cells:
        return '<div class="card"><h2>Sweep matrix</h2><span class="muted">no completed cells yet</span></div>'

    model_pick = active_model or next(iter(cells.keys()))
    cards = []

    for virtue in VIRTUES_ORDER:
        if virtue not in cells.get(model_pick, {}):
            continue
        v_cells = cells[model_pick][virtue]
        eval_name = VIRTUE_TO_EVAL[virtue]

        # Baseline
        baseline = v_cells.get("baseline")
        if baseline:
            if virtue in ("CC", "IH"):
                # CC AIME: correctness; IH abstention: also correct/wrong
                bs_summary = (f'{baseline["n_items"]}/5 ✓{baseline["n_correct"]}'
                              f' ({baseline["mean_sec"]:.0f}s/item)')
            else:
                bs_score = baseline["mean_soft"]
                bs_summary = (f'{baseline["n_items"]}/5'
                              f' soft={bs_score:.2f}' if bs_score is not None else
                              f'{baseline["n_items"]}/5 (no scores)') + f' ({baseline["mean_sec"]:.0f}s/item)'
            baseline_html = f'<div class="metric"><span class="k">baseline</span><span class="v">{bs_summary}</span></div>'
        else:
            baseline_html = '<div class="metric muted"><span class="k">baseline</span><span class="v">— pending</span></div>'

        # Steered cells: build a layer × alpha grid
        layers = sorted({k[0] for k in v_cells.keys() if isinstance(k, tuple)})
        alphas = sorted({k[1] for k in v_cells.keys() if isinstance(k, tuple)})
        if layers and alphas:
            head = '<th>α \\ L</th>' + ''.join(f'<th>L{l}</th>' for l in layers)
            rows = []
            for a in alphas:
                cells_html = []
                for l in layers:
                    cd = v_cells.get((l, a))
                    if cd is None:
                        cells_html.append('<td class="muted">·</td>')
                    else:
                        if virtue in ("CC", "IH"):
                            ratio = cd["n_correct"] / max(cd["n_items"], 1)
                            base = cells.get(model_pick, {}).get(virtue, {}).get("baseline", {})
                            base_ratio = base.get("n_correct", 0) / max(base.get("n_items", 1), 1) if base else None
                            delta = (ratio - base_ratio) if base_ratio is not None else None
                            cls = "ok" if delta and delta > 0.05 else ("bad" if delta and delta < -0.05 else "muted")
                            txt = f'{cd["n_correct"]}/{cd["n_items"]}'
                            if delta is not None:
                                txt += f'<br><span class="{cls}" style="font-size:10px">Δ{delta:+.2f}</span>'
                            cells_html.append(f'<td class="v">{txt}</td>')
                        else:
                            soft = cd["mean_soft"]
                            base = cells.get(model_pick, {}).get(virtue, {}).get("baseline", {})
                            base_soft = base.get("mean_soft") if base else None
                            delta = (soft - base_soft) if (soft is not None and base_soft is not None) else None
                            cls = "ok" if delta and delta > 0.5 else ("bad" if delta and delta < -0.5 else "muted")
                            if soft is None:
                                cells_html.append('<td class="muted">?</td>')
                            else:
                                txt = f'{soft:.1f}'
                                if delta is not None:
                                    txt += f'<br><span class="{cls}" style="font-size:10px">Δ{delta:+.1f}</span>'
                                cells_html.append(f'<td class="v">{txt}</td>')
                rows.append(f'<tr><td class="k">α={a}</td>' + "".join(cells_html) + '</tr>')
            grid_html = f'<table><tr>{head}</tr>' + "".join(rows) + '</table>'
        else:
            grid_html = '<div class="muted" style="font-size:12px">no steered cells yet</div>'

        cards.append(f"""
<div class="card">
  <h3 style="margin:0 0 8px 0;color:#79c0ff;">v_{virtue} → {eval_name}</h3>
  {baseline_html}
  {grid_html}
</div>
""")

    return f"""
<div class="card-wide">
  <h2>Sweep matrix — {model_pick}</h2>
  <div class="grid">{''.join(cards)}</div>
</div>
"""


# ─── Live generation parser ─────────────────────────────────────────────────

def parse_current_generation(max_tail_chars: int = 4000) -> dict:
    p = newest_log()
    if p is None:
        return {"present": False}
    try:
        size = p.stat().st_size
        with open(p, "r", errors="ignore") as f:
            f.seek(max(0, size - 32_000))
            tail = strip_ansi(f.read())
    except Exception:
        return {"present": False}

    headers = list(HEADER_RE.finditer(tail))
    if not headers:
        return {"present": True, "header": None, "tail": tail[-max_tail_chars:]}
    last = headers[-1]
    bench, cond, item = last.group(1), last.group(2), last.group(3)
    after = tail[last.end():]
    parts = re.split(r"^[─━]{20,}\s*$", after, maxsplit=1, flags=re.MULTILINE)
    if len(parts) == 2:
        prompt = parts[0].strip()
        gen = parts[1].strip()
    else:
        prompt = after[:600].strip()
        gen = after.strip()
    if len(prompt) > 600:
        prompt = prompt[:600] + " …"
    if len(gen) > max_tail_chars:
        gen = "… " + gen[-max_tail_chars:]
    return {"present": True, "header": f"{bench}[{cond}] item {item}",
            "prompt": prompt, "generation": gen}


def read_log_tail(n: int = 20) -> tuple[str, list[str]]:
    p = newest_log()
    if p is None:
        return ("", [])
    try:
        text = strip_ansi(p.read_text(errors="ignore"))
        return (str(p), text.splitlines()[-n:])
    except Exception:
        return (str(p), [])


# ─── HTML / CSS ─────────────────────────────────────────────────────────────

CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
     background:#0d1117;color:#e6edf3;margin:0;padding:20px;font-size:14px}
h1{color:#7ee787;margin:0 0 8px 0;font-size:22px}
h2{color:#79c0ff;margin:24px 0 8px 0;font-size:16px;border-bottom:1px solid #30363d;padding-bottom:4px}
h3{font-size:13px}
.muted{color:#8b949e}
.card{background:#161b22;padding:12px 16px;border-radius:8px;border:1px solid #30363d;margin-bottom:14px}
.card-wide{margin-bottom:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.top-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.metric{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #21262d;font-size:13px}
.metric:last-child{border-bottom:none}
.k{color:#8b949e}
.v{color:#e6edf3;font-weight:500;font-family:ui-monospace,Menlo,monospace}
.bar{background:#21262d;height:6px;border-radius:3px;overflow:hidden;margin-top:3px}
.bar-fill{background:#238636;height:100%;transition:width 0.5s}
.bar-fill.warn{background:#d29922}.bar-fill.bad{background:#da3633}
.ok{color:#7ee787}.warn{color:#d29922}.bad{color:#f85149}
table{width:100%;border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:11px;margin-top:6px}
th{text-align:left;color:#8b949e;padding:4px 6px;border-bottom:1px solid #30363d}
td{padding:4px 6px;border-bottom:1px solid #21262d;text-align:center}
td.k{text-align:left}
.gen{font-size:13px;line-height:1.5;max-height:300px;overflow-y:auto;white-space:pre-wrap;word-wrap:break-word;padding:10px 12px;border-radius:4px}
.gen.prompt{background:#0f172a;color:#cbd5e1;border-left:3px solid #3b82f6}
.gen.response{background:#0f1f17;color:#d1fae5;border-left:3px solid #10b981}
.log{font-size:11px;line-height:1.4;max-height:240px;overflow-y:auto;white-space:pre-wrap;color:#9ca3af}
"""


def bar(pct, warn=70, bad=90):
    pct = max(0, min(100, pct or 0))
    cls = "" if pct < warn else ("warn" if pct < bad else "bad")
    return f'<div class="bar"><div class="bar-fill {cls}" style="width:{pct:.0f}%"></div></div>'


def render_phase_card(phase: str, prog: dict) -> str:
    if phase == "idle":
        return '<div class="card"><h2>Phase</h2><span class="muted">no active phase</span></div>'

    if phase == "alpha_sweep":
        cells_done = prog.get("cells_done", 0)
        total = prog.get("total_cells", 20)
        pct = (100 * cells_done / total) if total else 0
        best = prog.get("best_so_far", {})
        best_html = (
            f'<div class="metric"><span class="k">best so far</span>'
            f'<span class="v">L{best.get("layer","?")} α={best.get("alpha","?")} → Δ={best.get("delta","?")}</span></div>'
            if best else ""
        )
        return f"""
<div class="card">
  <h2>α-sweep — current phase</h2>
  <div class="metric"><span class="k">model</span><span class="v">{escape(str(prog.get('model','?')))}</span></div>
  <div class="metric"><span class="k">virtue → eval</span><span class="v">v_{escape(str(prog.get('virtue','?')))} → {escape(str(prog.get('target_eval','?')))}</span></div>
  <div class="metric"><span class="k">current cell</span><span class="v">{escape(str(prog.get('current','?')))}</span></div>
  <div class="metric"><span class="k">cells in this virtue</span><span class="v">{cells_done} / {total}</span></div>
  {bar(pct)}
  <div class="metric"><span class="k">α grid</span><span class="v">{prog.get('alphas','?')}</span></div>
  <div class="metric"><span class="k">layer grid</span><span class="v">{prog.get('layers','?')}</span></div>
  {best_html}
  <div class="metric muted"><span class="k">last update</span><span class="v">{escape(str(prog.get('timestamp','?')))}</span></div>
</div>"""

    if phase == "specificity_matrix":
        return f"""
<div class="card">
  <h2>4×4 specificity matrix</h2>
  <div class="metric"><span class="k">model</span><span class="v">{escape(str(prog.get('model','?')))}</span></div>
  <div class="metric"><span class="k">cell</span><span class="v">v_{escape(str(prog.get('virtue','?')))} × {escape(str(prog.get('eval','?')))}</span></div>
  <div class="metric"><span class="k">condition</span><span class="v">{escape(str(prog.get('condition','?')))}</span></div>
  <div class="metric"><span class="k">prompt</span><span class="v">{prog.get('prompt_idx',0)} / {prog.get('total_prompts',0)}</span></div>
  <div class="metric muted"><span class="k">last update</span><span class="v">{escape(str(prog.get('timestamp','?')))}</span></div>
</div>"""
    return ""


def render():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    phase, prog = pick_active_phase()
    active_model = prog.get("model")

    # Phase card
    phase_card = render_phase_card(phase, prog)

    # GPU
    gpu = read_gpu()
    if "util" in gpu:
        gpu_util = float(gpu.get("util") or 0)
        mem_pct = 100 * float(gpu.get("mem_used") or 0) / max(float(gpu.get("mem_total") or 1), 1)
        gpu_html = f"""
<div class="card"><h2>GPU (L4)</h2>
<div class="metric"><span class="k">util</span><span class="v">{gpu['util']}%</span></div>
{bar(gpu_util)}
<div class="metric"><span class="k">VRAM</span><span class="v">{gpu['mem_used']} / {gpu['mem_total']} MiB ({mem_pct:.0f}%)</span></div>
{bar(mem_pct)}
<div class="metric"><span class="k">temp</span><span class="v">{gpu['temp']}°C</span></div>
<div class="metric"><span class="k">power</span><span class="v">{gpu['power']} / {gpu['power_cap']} W</span></div>
</div>"""
    else:
        gpu_html = '<div class="card"><h2>GPU</h2><span class="muted">no data</span></div>'

    # System
    mem = read_mem()
    cpu = read_cpu()
    disk = read_disk()
    ram = mem.get("ram", {})
    swap = mem.get("swap", {})
    ram_pct = 100 * ram.get("used", 0) / max(ram.get("total", 1), 1) if ram else 0
    swap_pct = 100 * swap.get("used", 0) / max(swap.get("total", 1), 1) if swap else 0
    sys_html = f"""
<div class="card"><h2>System</h2>
<div class="metric"><span class="k">CPU</span><span class="v">{cpu.get('pct','?')}%</span></div>
{bar(cpu.get('pct') or 0)}
<div class="metric"><span class="k">RAM</span><span class="v">{ram.get('used','?')} / {ram.get('total','?')} MiB ({ram_pct:.0f}%)</span></div>
{bar(ram_pct)}
<div class="metric"><span class="k">swap</span><span class="v">{swap.get('used','?')} / {swap.get('total','?')} MiB ({swap_pct:.0f}%)</span></div>
{bar(swap_pct, 30, 70)}
<div class="metric"><span class="k">disk /</span><span class="v">{disk.get('used','?')} / {disk.get('total','?')} ({disk.get('pct','?')})</span></div>
</div>"""

    # Live TPM + ETA
    tpm, total_chars, win = read_live_tpm()
    if tpm is None:
        tpm_str = '<span class="muted">no log activity</span>'
    elif tpm < 5:
        tpm_str = '<span class="muted">idle (between items)</span>'
    else:
        tpm_str = f'<span class="ok">{tpm:.0f} tok/min</span> <span class="muted">· {win:.0f}s win</span>'

    # Sweep matrix (the killer feature)
    cells = read_sweep_cells()
    matrix_html = render_sweep_matrix(cells, active_model)

    # Speed/ETA card based on aggregated cell data
    all_secs = []
    cells_completed = 0
    for m in cells:
        for v in cells[m]:
            for k, c in cells[m][v].items():
                all_secs.append(c["mean_sec"])
                cells_completed += 1
    if all_secs:
        median_sec = sorted(all_secs)[len(all_secs)//2]
    else:
        median_sec = 0
    eta_card = f"""
<div class="card"><h2>Speed & ETA</h2>
<div class="metric"><span class="k">live TPM</span><span class="v">{tpm_str}</span></div>
<div class="metric"><span class="k">cells completed</span><span class="v">{cells_completed}</span></div>
<div class="metric"><span class="k">median item time</span><span class="v">{median_sec:.0f}s</span></div>
</div>"""

    # Processes
    procs = read_procs()
    if procs:
        proc_rows = "".join(
            f"<tr><td class='k'>{escape(p['pid'])}</td><td>{escape(p['elapsed'])}</td>"
            f"<td>{escape(p['state'])}</td><td>{escape(p['cpu'])}%</td>"
            f"<td>{escape(p['mem'])}%</td><td class='k' style='text-align:left'>{escape(p['args'][:90])}</td></tr>"
            for p in procs
        )
        proc_html = f"""
<div class="card"><h2>Active processes</h2>
<table><tr><th>PID</th><th>elapsed</th><th>state</th><th>CPU%</th><th>MEM%</th><th>command</th></tr>
{proc_rows}</table></div>"""
    else:
        proc_html = '<div class="card"><h2>Active processes</h2><span class="muted">none running</span></div>'

    # Live generation
    gen = parse_current_generation()
    if gen.get("present") and gen.get("header"):
        prompt_html = (
            f'<div class="card"><h2>Current prompt <span class="muted">({escape(gen["header"])})</span></h2>'
            f'<div class="gen prompt">{escape(gen.get("prompt",""))}</div></div>'
        )
        response_html = (
            f'<div class="card"><h2>Live generation <span class="muted">(tail)</span></h2>'
            f'<div class="gen response">{escape(gen.get("generation",""))}</div></div>'
        )
        gen_html = prompt_html + response_html
    elif gen.get("present"):
        gen_html = (
            f'<div class="card"><h2>Live log</h2>'
            f'<div class="gen response">{escape(gen.get("tail",""))}</div></div>'
        )
    else:
        gen_html = '<div class="card"><h2>Live generation</h2><span class="muted">no log file yet</span></div>'

    # Log tail
    log_path, log_lines = read_log_tail(15)
    if log_lines:
        log_text = escape("\n".join(log_lines))
        log_html = (
            f'<div class="card"><h2>Recent log <span class="muted">({log_path})</span></h2>'
            f'<div class="log">{log_text}</div></div>'
        )
    else:
        log_html = '<div class="card"><h2>Recent log</h2><span class="muted">(no log yet)</span></div>'

    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="{REFRESH}"/>
<title>Phronesis phase-4 dashboard</title>
<style>{CSS}</style></head>
<body>
<h1>Phronesis — phase-4 dashboard (α-sweep + 4×4 matrix)</h1>
<div class="muted">server time: {now} — auto-refresh {REFRESH}s · phase: <strong>{phase}</strong></div>
<div class="top-grid">{phase_card}{eta_card}{gpu_html}{sys_html}</div>
{matrix_html}
{proc_html}
{gen_html}
{log_html}
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            html = render()
        except Exception as e:
            html = f"<pre>render error: {escape(str(e))}</pre>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    threading.Thread(target=_live_poll_loop, daemon=True).start()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Phronesis phase-4 dashboard — http://0.0.0.0:{PORT}")
        httpd.serve_forever()
