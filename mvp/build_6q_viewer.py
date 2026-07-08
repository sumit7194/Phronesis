#!/usr/bin/env python
"""Build a self-contained interactive HTML viewer for the 6-question workspace readouts.

Reads results/workspace/6q/<id>_masked<SUFFIX>.json, compacts (top-8 concepts x 3 layers,
3-decimal weights), embeds as JSON, and writes results/workspace/6q/viewer.html.
Re-run with --suffix _masked (bigger lens) tomorrow to regenerate against n~100.
"""
import argparse, html, json, os

ORDER = ["q1_no_a", "q2_math_solved", "q3_gsm_rescuable", "q4_math_wall",
         "q5_gsm_solved", "q6_gsm_failed"]
LAYERS = ["14", "20", "26"]
TOPN = 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffix", default="_masked_n45")
    ap.add_argument("--out", default="results/workspace/6q/viewer.html")
    args = ap.parse_args()
    D = "results/workspace/6q"

    stim = {q["id"]: q for q in json.load(open("workspace_6q_stimuli.json"))["questions"]} \
        if os.path.exists("workspace_6q_stimuli.json") else {}
    data = {}
    for qid in ORDER:
        p = f"{D}/{qid}{args.suffix}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        span = sorted((int(k) for k in d["positions"]), key=int)
        prompt_len = d.get("prompt_len", 0)
        # index in the compacted toks list where reasoning begins (prompt positions come first
        # if the readout now includes them; -1 if this file predates the prompt-inclusive run)
        think_idx = next((i for i, pos in enumerate(span) if pos >= prompt_len), len(span)) \
            if any(pos < prompt_len for pos in span) else 0
        toks, cells = [], []
        for pos in span:
            rec = d["positions"][str(pos)]
            toks.append(rec["token"])
            layer_c = {}
            for l in LAYERS:
                layer_c[l] = [[c, round(w, 3)] for c, w in rec["by_layer"].get(l, [])[:TOPN]]
            cells.append(layer_c)
        data[qid] = {"id": qid, "category": d["category"], "gold": str(d["gold"]),
                     "answer": str(d["answer"]), "correct": bool(d["correct"]),
                     "question": stim.get(qid, {}).get("question", ""),
                     "think_idx": think_idx,
                     "lens_n": d.get("lens_n", 45) if isinstance(d.get("lens_n"), int) else 45,
                     "n_tokens": d["n_tokens"], "toks": toks, "cells": cells}
    meta_n = json.load(open("results/workspace/t2_fit_meta.json")).get("n_prompts", "?") \
        if os.path.exists("results/workspace/t2_fit_meta.json") else "?"

    payload = json.dumps({"questions": data, "order": [q for q in ORDER if q in data],
                          "layers": LAYERS}, ensure_ascii=False)
    htmldoc = TEMPLATE.replace("__PAYLOAD__", payload).replace("__LENSN__", str(meta_n))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(htmldoc)
    print(f"wrote {args.out} ({os.path.getsize(args.out)/1e6:.1f} MB), {len(data)} questions")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>J-space workspace viewer — 6 problems</title>
<style>
:root{
 --bg:#0d1117; --panel:#161b22; --panel2:#1c2330; --border:#2b3444; --text:#e6edf3;
 --dim:#8b949e; --accent:#58a6ff; --good:#3fb950; --bad:#f85149; --warn:#d29922;
 --chip:#21262d; --sel:#1f6feb; --bar:#3b5bdb; --barbg:#22272e;
}
@media (prefers-color-scheme: light){:root{
 --bg:#ffffff; --panel:#f6f8fa; --panel2:#eef1f4; --border:#d0d7de; --text:#1f2328;
 --dim:#656d76; --accent:#0969da; --good:#1a7f37; --bad:#cf222e; --warn:#9a6700;
 --chip:#eaeef2; --sel:#0969da; --bar:#4c6ef5; --barbg:#e6eaef;}}
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
 background:var(--bg);color:var(--text)}
header{padding:14px 18px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--bg);z-index:10}
h1{font-size:16px;margin:0 0 8px}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tab{padding:6px 11px;border:1px solid var(--border);border-radius:7px;background:var(--panel);
 cursor:pointer;font-size:12.5px;color:var(--text);white-space:nowrap}
.tab:hover{border-color:var(--accent)}
.tab.active{background:var(--sel);border-color:var(--sel);color:#fff}
.tab .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.dot.good{background:var(--good)} .dot.bad{background:var(--bad)}
.meta{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-top:10px;font-size:12.5px;color:var(--dim)}
.badge{padding:2px 8px;border-radius:5px;font-weight:600}
.badge.good{background:rgba(63,185,80,.15);color:var(--good)}
.badge.bad{background:rgba(248,81,73,.15);color:var(--bad)}
.qtext{margin-top:8px;color:var(--text);font-size:13px;max-width:1100px}
.wrap{display:grid;grid-template-columns:1fr 380px;gap:0;height:calc(100vh - 168px)}
@media(max-width:900px){.wrap{grid-template-columns:1fr;height:auto}}
.stream{overflow-y:auto;padding:16px 18px;border-right:1px solid var(--border)}
.controls{display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.controls input{background:var(--panel);border:1px solid var(--border);color:var(--text);
 padding:6px 9px;border-radius:6px;font-size:12.5px;width:160px}
.controls label{font-size:12px;color:var(--dim)}
.seg{display:flex;border:1px solid var(--border);border-radius:6px;overflow:hidden}
.seg button{background:var(--panel);border:0;color:var(--dim);padding:5px 10px;cursor:pointer;font-size:12px}
.seg button.on{background:var(--sel);color:#fff}
.tok{display:inline;cursor:pointer;border-radius:3px;padding:1px 0}
.tok:hover{outline:1px solid var(--accent)}
.tok.sel{background:var(--sel)!important;color:#fff}
.tok.hit{box-shadow:inset 0 -2px 0 var(--warn)}
.tok.prompt{color:var(--dim);font-style:italic}
.nl{display:block;height:0}
.qbox{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin-bottom:12px}
.qbox .ql{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);margin-bottom:4px}
.divider{display:block;text-align:center;color:var(--warn);font-size:11px;letter-spacing:.08em;
 text-transform:uppercase;margin:12px 0;border-top:1px dashed var(--border);padding-top:8px}
.side{overflow-y:auto;padding:16px;background:var(--panel)}
.side h3{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);margin:0 0 4px}
.postok{font-size:15px;font-weight:600;margin:2px 0 12px;word-break:break-all}
.layer{margin-bottom:16px}
.layer .lh{font-size:11.5px;color:var(--accent);font-weight:600;margin-bottom:5px}
.cbar{display:grid;grid-template-columns:96px 1fr 44px;gap:8px;align-items:center;margin:3px 0;font-size:12px}
.cbar .cn{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cbar .cv{color:var(--dim);text-align:right;font-variant-numeric:tabular-nums}
.track{height:9px;background:var(--barbg);border-radius:4px;overflow:hidden}
.fill{height:100%;background:var(--bar)}
.hint{color:var(--dim);font-size:11.5px;margin-top:6px}
footer{padding:8px 18px;border-top:1px solid var(--border);color:var(--dim);font-size:11.5px}
</style></head>
<body>
<header>
 <h1>J-space workspace viewer · what the model holds in mind, token by token</h1>
 <div class="tabs" id="tabs"></div>
 <div class="meta" id="meta"></div>
 <div class="qtext" id="qtext"></div>
</header>
<div class="wrap">
 <div class="stream">
   <div class="controls">
     <input id="search" placeholder="highlight concept…" autocomplete="off">
     <label>emphasis layer:</label>
     <div class="seg" id="layerseg"></div>
     <label style="margin-left:auto">click a token → its workspace →</label>
   </div>
   <div id="tokens"></div>
 </div>
 <div class="side">
   <h3>Selected token</h3>
   <div class="postok" id="postok">— click a token —</div>
   <div id="layers"></div>
   <div class="hint">Weights are softmax over word-like tokens (top-8 shown). Bar = share of that token's readout at that layer.</div>
 </div>
</div>
<footer id="foot"></footer>
<script id="data" type="application/json">__PAYLOAD__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const LAYERS = DATA.layers;
let curQ = DATA.order[0], curLayer = "20", curSel = 0;

function el(t,c,txt){const e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e;}

function renderTabs(){
 const tabs=document.getElementById('tabs'); tabs.innerHTML='';
 DATA.order.forEach(qid=>{
   const q=DATA.questions[qid];
   const t=el('div','tab'+(qid===curQ?' active':''));
   const dot=el('span','dot '+(q.correct?'good':'bad'));
   t.appendChild(dot); t.appendChild(document.createTextNode(qid.replace(/_/g,' ')));
   t.onclick=()=>{curQ=qid;curSel=0;renderAll();};
   tabs.appendChild(t);
 });
 const seg=document.getElementById('layerseg'); seg.innerHTML='';
 LAYERS.forEach(l=>{const b=el('button',l===curLayer?'on':'',"L"+l);
   b.onclick=()=>{curLayer=l;renderTokens();renderSide();document.querySelectorAll('#layerseg button').forEach(x=>x.classList.toggle('on',x.textContent==='L'+curLayer));};
   seg.appendChild(b);});
}

function renderMeta(){
 const q=DATA.questions[curQ];
 const m=document.getElementById('meta'); m.innerHTML='';
 m.appendChild(el('span',null,q.category));
 const b=el('span','badge '+(q.correct?'good':'bad'),q.correct?('✓ correct: '+q.answer):('✗ '+ (q.answer||'(no answer)')));
 m.appendChild(b);
 m.appendChild(el('span',null,'gold: '+q.gold));
 const ntok = q.toks.length, np = q.think_idx||0;
 m.appendChild(el('span',null, np>0 ? (np+' prompt + '+(ntok-np)+' reasoning tokens') : (ntok+' reasoning tokens')));
 const qt=document.getElementById('qtext'); qt.innerHTML='';
 if(q.question){const box=el('div','qbox');box.appendChild(el('div','ql','Question'));box.appendChild(el('div',null,q.question));qt.appendChild(box);}
 document.getElementById('foot').textContent='J-lens n='+DATA.questions[curQ].lens_n+' · Qwen3-4B fp16 · workspace band L14/L20/L26 · masked (word-like tokens) · noisy at n<100 — a bigger-lens rebuild sharpens it.';
}

function maxW(cell,layer){const a=cell[layer]; return a&&a.length?a[0][1]:0;}

function renderTokens(){
 const q=DATA.questions[curQ], box=document.getElementById('tokens'); box.innerHTML='';
 const term=document.getElementById('search').value.trim().toLowerCase();
 const think=q.think_idx||0;
 q.toks.forEach((tk,i)=>{
   if(i===think && think>0){const d=el('span','divider','▼ reasoning begins (above = model reading the prompt)');box.appendChild(d);}
   const cell=q.cells[i];
   const w=maxW(cell,curLayer);
   const isPrompt = think>0 && i<think;
   const sp=el('span','tok'+(i===curSel?' sel':'')+(isPrompt?' prompt':''));
   const a=Math.min(.5, w*4);
   sp.style.background=i===curSel?'':'rgba(88,166,255,'+a.toFixed(3)+')';
   sp.textContent=tk.replace(/\n/g,'↵');
   if(term){
     const hit=LAYERS.some(l=>(cell[l]||[]).some(c=>c[0].toLowerCase().includes(term)));
     if(hit) sp.classList.add('hit');
   }
   sp.onclick=()=>{curSel=i;renderTokens();renderSide();};
   sp.onmouseenter=()=>{curSel=i;renderSide();};
   box.appendChild(sp);
   if(tk.includes('\n')) box.appendChild(el('span','nl'));
 });
}

function renderSide(){
 const q=DATA.questions[curQ], cell=q.cells[curSel];
 document.getElementById('postok').textContent='['+curSel+'] '+JSON.stringify(q.toks[curSel]);
 const host=document.getElementById('layers'); host.innerHTML='';
 LAYERS.forEach(l=>{
   const box=el('div','layer');
   box.appendChild(el('div','lh','Layer '+l+(l===curLayer?'  (emphasis)':'')));
   const arr=cell[l]||[];
   const mx=arr.length?arr[0][1]:1;
   arr.forEach(([c,w])=>{
     const row=el('div','cbar');
     row.appendChild(el('div','cn',c));
     const track=el('div','track'); const fill=el('div','fill');
     fill.style.width=(mx?100*w/mx:0).toFixed(1)+'%'; track.appendChild(fill);
     row.appendChild(track);
     row.appendChild(el('div','cv',w.toFixed(3)));
     box.appendChild(row);
   });
   if(!arr.length) box.appendChild(el('div','hint','—'));
   host.appendChild(box);
 });
}

function renderAll(){renderTabs();renderMeta();renderTokens();renderSide();}
document.getElementById('search').addEventListener('input',renderTokens);
document.addEventListener('keydown',e=>{
 if(e.target.tagName==='INPUT')return;
 const n=DATA.questions[curQ].toks.length;
 if(e.key==='ArrowRight'){curSel=Math.min(n-1,curSel+1);renderTokens();renderSide();e.preventDefault();}
 if(e.key==='ArrowLeft'){curSel=Math.max(0,curSel-1);renderTokens();renderSide();e.preventDefault();}
});
renderAll();
</script>
</body></html>"""


if __name__ == "__main__":
    main()
