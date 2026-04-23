"""
FastAPI web app for hand-reviewing specificity matrix generations.

One generation per page. Four Likert sliders (1-5) for CC/IH/EG/RT exhibition,
plus gaming/degenerate flags and free-text notes. Hotkey support via JavaScript
(keyboard shortcuts only — no framework).

Routes:
  GET  /                              → index (list of review sessions + progress)
  GET  /review/{session}/{idx}        → review item at index `idx` in session
  POST /review/{session}/{idx}/save   → save ratings + advance to next unreviewed
  GET  /review/{session}/{idx}/next   → redirect to next unreviewed item
  GET  /build/{session}                → import/refresh from specificity_matrix CSV
  GET  /export/{session}                → download current review CSV
  GET  /static/...                    → CSS

A "session" is just the basename of a CSV file under results/manual_review/.

Usage:
    cd mvp && python3 -m uvicorn review.app:app --host 127.0.0.1 --port 5000

Then open http://localhost:5000 in a browser.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Allow running from mvp/ or elsewhere
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from storage import ReviewStore, build_review_csv_from_specificity  # noqa: E402


MVP_ROOT = HERE.parent
REVIEW_DIR = MVP_ROOT / "results" / "manual_review"
SPEC_DIR = MVP_ROOT / "results" / "specificity_matrix"

app = FastAPI(title="Phronesis Review")
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")
templates = Jinja2Templates(directory=str(HERE / "templates"))


# ─── Session store cache (reload on each request to pick up CSV changes) ─────

def get_store(session: str) -> ReviewStore:
    """Load a review session by name. 'Session' is a CSV filename without extension."""
    csv_path = REVIEW_DIR / f"{session}.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"No review session '{session}'. Create it via /build/{{session}}")
    return ReviewStore(csv_path)


def list_sessions() -> list[str]:
    if not REVIEW_DIR.exists():
        return []
    return sorted(p.stem for p in REVIEW_DIR.glob("*.csv") if not p.stem.startswith("."))


def list_spec_sources() -> list[str]:
    if not SPEC_DIR.exists():
        return []
    return sorted(
        p.stem.replace("all_generations_", "")
        for p in SPEC_DIR.glob("all_generations_*.csv")
    )


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    sessions = []
    for s in list_sessions():
        try:
            store = get_store(s)
            stats = store.progress_stats()
            # Flatten by_cell tuple-keyed dict to a list of dicts for template use
            by_cell_rows = []
            for (m, v, e), counts in stats["by_cell"].items():
                by_cell_rows.append({
                    "model": m, "vector": v, "eval": e,
                    "total": counts["total"], "reviewed": counts["reviewed"],
                })
            sessions.append({
                "name": s,
                "total": stats["total"],
                "reviewed": stats["reviewed"],
                "pct": stats["pct"],
                "by_cell": by_cell_rows,
            })
        except HTTPException:
            continue
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "sessions": sessions,
            "spec_sources": list_spec_sources(),
        },
    )


@app.get("/build/{session}")
def build_session(session: str, overwrite: bool = False):
    """Build or refresh a review CSV from a specificity_matrix source CSV.

    Session name should match a `all_generations_{session}.csv` file under
    results/specificity_matrix/. The output goes to results/manual_review/{session}.csv.
    """
    spec_path = SPEC_DIR / f"all_generations_{session}.csv"
    if not spec_path.exists():
        raise HTTPException(status_code=404, detail=f"No specificity CSV at {spec_path}")
    review_path = REVIEW_DIR / f"{session}.csv"
    n = build_review_csv_from_specificity(spec_path, review_path, overwrite=overwrite)
    return RedirectResponse(url=f"/review/{session}/0", status_code=303)


@app.get("/review/{session}/{idx}", response_class=HTMLResponse)
def review_item(request: Request, session: str, idx: int):
    store = get_store(session)
    item = store.get_by_index(idx)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Index {idx} out of range (max {len(store)-1})")
    stats = store.progress_stats()
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "session": session,
            "idx": idx,
            "total": len(store),
            "item": item,
            "stats": stats,
            "prev_idx": max(0, idx - 1),
            "next_idx": min(len(store) - 1, idx + 1),
        },
    )


@app.post("/review/{session}/{idx}/save")
def save_item(
    session: str,
    idx: int,
    human_cc_1to5: str = Form(""),
    human_ih_1to5: str = Form(""),
    human_eg_1to5: str = Form(""),
    human_rt_1to5: str = Form(""),
    gaming_flag: str = Form(""),
    degenerate_flag: str = Form(""),
    notes: str = Form(""),
    reviewer: str = Form(""),
    action: str = Form("save_next"),  # "save_next" | "save_stay" | "save_prev"
):
    store = get_store(session)
    item = store.get_by_index(idx)
    if item is None:
        raise HTTPException(status_code=404)
    store.update(
        item.primary_key,
        human_cc_1to5=human_cc_1to5,
        human_ih_1to5=human_ih_1to5,
        human_eg_1to5=human_eg_1to5,
        human_rt_1to5=human_rt_1to5,
        gaming_flag=gaming_flag,
        degenerate_flag=degenerate_flag,
        notes=notes,
        reviewer=reviewer or "unknown",
    )
    store.save()

    if action == "save_prev":
        target = max(0, idx - 1)
    elif action == "save_stay":
        target = idx
    else:  # save_next — jump to next unreviewed
        nxt = store.next_unreviewed(from_idx=idx + 1)
        target = nxt if nxt is not None else min(idx + 1, len(store) - 1)
    return RedirectResponse(url=f"/review/{session}/{target}", status_code=303)


@app.get("/review/{session}/{idx}/next")
def jump_next_unreviewed(session: str, idx: int):
    store = get_store(session)
    nxt = store.next_unreviewed(from_idx=idx + 1)
    target = nxt if nxt is not None else idx
    return RedirectResponse(url=f"/review/{session}/{target}", status_code=303)


@app.get("/export/{session}")
def export_csv(session: str):
    csv_path = REVIEW_DIR / f"{session}.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(
        path=str(csv_path),
        filename=f"{session}.csv",
        media_type="text/csv",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
