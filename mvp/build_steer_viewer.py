#!/usr/bin/env python
"""Build a two-level J-space viewer over baseline + all 40 steered runs.

Level 1: prompt (q1_no_a, q3, q6, q5, ...).  Level 2: condition (baseline + IH+/-, EG+/-, RT+/-,
VC+/-, random0/1). A comparison strip shows commit/correct/doubt per condition. Concept data is
fetched on demand from the LAN server (page stays small). Writes results/workspace/steer_viewer.html;
serve results/workspace/ so it can fetch ./6q/*.json and ./steer/*.json.
"""
import glob, json, os

WS = "results/workspace"
BASE_PROMPTS = ["q1_no_a", "q1_plain", "q2_math_solved", "q3_gsm_rescuable",
                "q4_math_wall", "q5_gsm_solved", "q6_gsm_failed"]
LAYERS = ["14", "20", "26"]
DOUBT = {"wait", "hmm", "maybe", "actually", "however", "but", "confused", "confusion",
         "mistake", "wrong", "doubt", "unsure", "uncertain", "perhaps", "again", "guess",
         "suppose", "seems", "no", "not", "oops", "error"}
COND_ORDER = ["baseline", "IH+12", "IH-12", "EG+12", "EG-12", "RT+12", "RT-12",
              "VC+12", "VC-12", "random0+12", "random1+12"]


def doubt_load(positions):
    tot = n = 0.0
    for r in positions.values():
        tot += sum(w for c, w in r["by_layer"].get("20", []) if c.lower() in DOUBT)
        n += 1
    return round(tot / max(n, 1), 4)


def summarize_baseline(pid):
    p = f"{WS}/6q/{pid}_masked.json"
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    import re
    box = re.findall(r"\\boxed\{([^}]*)\}", d.get("trace", ""))
    committed = ("</think>" in d.get("trace", "")) or bool(box)
    return {"cond": "baseline", "kind": "baseline", "file": f"6q/{pid}_masked.json",
            "committed": committed, "correct": bool(d.get("correct")),
            "answer": str(d.get("answer"))[:16], "doubt_load": doubt_load(d["positions"])}


def main():
    manifest = {"prompts": {}, "order": BASE_PROMPTS, "layers": LAYERS}
    for pid in BASE_PROMPTS:
        base = summarize_baseline(pid)
        if not base:
            continue
        q = json.load(open(f"{WS}/6q/{pid}_masked.json")).get("question", "")
        gold = json.load(open(f"{WS}/6q/{pid}_masked.json")).get("gold", "")
        conds = [base]
        for f in sorted(glob.glob(f"{WS}/steer/{pid}__*.json")):
            s = json.load(open(f)).get("_sum", {})
            cn = s.get("cond", os.path.basename(f).split("__")[1][:-5])
            conds.append({"cond": cn,
                          "kind": "random" if "random" in cn else "virtue",
                          "file": f"steer/{pid}__{cn}.json",
                          "committed": bool(s.get("committed")), "correct": bool(s.get("correct")),
                          "answer": str(s.get("answer"))[:16], "doubt_load": s.get("doubt_load")})
        order = {c: i for i, c in enumerate(COND_ORDER)}
        conds.sort(key=lambda c: order.get(c["cond"], 99))
        manifest["prompts"][pid] = {"question": q, "gold": str(gold), "conditions": conds}
    payload = json.dumps(manifest, ensure_ascii=False)
    html = TEMPLATE.replace("__PAYLOAD__", payload)
    out = f"{WS}/steer_viewer.html"
    with open(out, "w") as f:
        f.write(html)
    n = sum(len(p["conditions"]) for p in manifest["prompts"].values())
    print(f"wrote {out} ({len(html)/1e3:.0f} KB manifest), {len(manifest['prompts'])} prompts, {n} views")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>J-space steering viewer</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2330;--border:#2b3444;--text:#e6edf3;--dim:#8b949e;
 --accent:#58a6ff;--good:#3fb950;--bad:#f85149;--warn:#d29922;--sel:#1f6feb;--bar:#3b5bdb;--barbg:#22272e}
@media(prefers-color-scheme:light){:root{--bg:#fff;--panel:#f6f8fa;--panel2:#eef1f4;--border:#d0d7de;
 --text:#1f2328;--dim:#656d76;--accent:#0969da;--good:#1a7f37;--bad:#cf222e;--warn:#9a6700;--sel:#0969da;--bar:#4c6ef5;--barbg:#e6eaef}}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text)}
header{padding:12px 16px;border-bottom:1px solid var(--border)}
h1{font-size:15px;margin:0 0 8px}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.tab{padding:6px 11px;border:1px solid var(--border);border-radius:7px;background:var(--panel);cursor:pointer;font-size:12.5px;color:var(--text)}
.tab.active{background:var(--sel);border-color:var(--sel);color:#fff}
.qbox{background:var(--panel2);border:1px solid var(--border);border-radius:7px;padding:8px 11px;font-size:12.5px;margin-bottom:8px}
.conds{display:flex;flex-wrap:wrap;gap:5px}
.chip{padding:5px 9px;border:1px solid var(--border);border-radius:6px;background:var(--panel);cursor:pointer;font-size:11.5px;display:flex;gap:6px;align-items:center}
.chip.active{border-color:var(--accent);background:var(--panel2)}
.chip .dot{width:8px;height:8px;border-radius:50%}
.dot.commit-ok{background:var(--good)}.dot.commit-wrong{background:var(--warn)}.dot.spiral{background:var(--bad)}
.chip .dl{color:var(--dim);font-variant-numeric:tabular-nums}
.chip.rand{border-style:dashed}
.wrap{display:grid;grid-template-columns:1fr 360px;height:calc(100vh - 200px)}
.stream{overflow-y:auto;padding:14px 16px;border-right:1px solid var(--border)}
.controls{display:flex;gap:10px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.controls input{background:var(--panel);border:1px solid var(--border);color:var(--text);padding:5px 8px;border-radius:6px;font-size:12px;width:150px}
.seg{display:flex;border:1px solid var(--border);border-radius:6px;overflow:hidden}
.seg button{background:var(--panel);border:0;color:var(--dim);padding:4px 9px;cursor:pointer;font-size:12px}
.seg button.on{background:var(--sel);color:#fff}
.tok{cursor:pointer;border-radius:3px}.tok:hover{outline:1px solid var(--accent)}.tok.sel{background:var(--sel)!important;color:#fff}
.tok.hit{box-shadow:inset 0 -2px 0 var(--warn)}.tok.prompt{color:var(--dim);font-style:italic}
.divider{display:block;text-align:center;color:var(--warn);font-size:11px;margin:10px 0;border-top:1px dashed var(--border);padding-top:6px}
.side{overflow-y:auto;padding:14px;background:var(--panel)}
.side h3{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);margin:0 0 4px}
.postok{font-size:14px;font-weight:600;margin:2px 0 10px;word-break:break-all}
.layer{margin-bottom:14px}.layer .lh{font-size:11px;color:var(--accent);font-weight:600;margin-bottom:4px}
.cbar{display:grid;grid-template-columns:88px 1fr 42px;gap:8px;align-items:center;margin:3px 0;font-size:12px}
.cbar .cn{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cbar .cv{color:var(--dim);text-align:right}
.track{height:8px;background:var(--barbg);border-radius:4px;overflow:hidden}.fill{height:100%;background:var(--bar)}
.hint{color:var(--dim);font-size:11px}
@media(max-width:760px){.wrap{display:block;height:auto}.stream{border-right:0;padding-bottom:46vh}
 .side{position:fixed;left:0;right:0;bottom:0;max-height:44vh;border-top:2px solid var(--accent);border-radius:12px 12px 0 0;box-shadow:0 -8px 24px rgba(0,0,0,.35)}
 .side::before{content:"";display:block;width:38px;height:4px;border-radius:2px;background:var(--border);margin:0 auto 6px}}
</style></head><body>
<header>
 <h1>J-space steering viewer · baseline vs steered workspace</h1>
 <div class="tabs" id="tabs"></div>
 <div class="qbox" id="qbox"></div>
 <div class="conds" id="conds"></div>
</header>
<div class="wrap">
 <div class="stream">
   <div class="controls">
     <input id="search" placeholder="highlight concept…" autocomplete="off">
     <div class="seg" id="layerseg"></div>
     <span class="hint" id="viewinfo"></span>
   </div>
   <div id="tokens"><div class="hint">loading…</div></div>
 </div>
 <div class="side"><h3>Selected token</h3><div class="postok" id="postok">— tap a token —</div><div id="layers"></div>
   <div class="hint">top-8 word-like concepts / layer · weight = share of that token's readout</div></div>
</div>
<script id="m" type="application/json">__PAYLOAD__</script>
<script>
const M=JSON.parse(document.getElementById('m').textContent), LAYERS=M.layers;
let curP=M.order.find(p=>M.prompts[p]), curC=0, curLayer="20", curSel=0, view=null;
const cache={};
function el(t,c,x){const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e;}
function dotClass(cd){return cd.committed?(cd.correct?'commit-ok':'commit-wrong'):'spiral';}

function tabs(){const t=document.getElementById('tabs');t.innerHTML='';
 M.order.filter(p=>M.prompts[p]).forEach(p=>{const b=el('div','tab'+(p===curP?' active':''),p.replace(/_/g,' '));
  b.onclick=()=>{curP=p;curC=0;curSel=0;renderHead();loadView();};t.appendChild(b);});
 const s=document.getElementById('layerseg');s.innerHTML='';LAYERS.forEach(l=>{const b=el('button',l===curLayer?'on':'',"L"+l);
  b.onclick=()=>{curLayer=l;[...s.children].forEach(x=>x.classList.toggle('on',x.textContent==='L'+curLayer));renderTokens();};s.appendChild(b);});}

function renderHead(){const P=M.prompts[curP];
 document.querySelectorAll('#tabs .tab').forEach(t=>t.classList.toggle('active',t.textContent===curP.replace(/_/g,' ')));
 document.getElementById('qbox').textContent='gold '+P.gold+' · '+P.question;
 const c=document.getElementById('conds');c.innerHTML='';
 P.conditions.forEach((cd,i)=>{const chip=el('div','chip'+(i===curC?' active':'')+(cd.kind==='random'?' rand':''));
  chip.appendChild(el('span','dot '+dotClass(cd)));
  chip.appendChild(el('span',null,cd.cond));
  chip.appendChild(el('span','dl',(cd.doubt_load!=null?cd.doubt_load.toFixed(3):'')));
  chip.title=(cd.committed?('commit '+cd.answer+(cd.correct?' ✓':' ✗')):'spiraled')+' · doubt '+cd.doubt_load;
  chip.onclick=()=>{curC=i;curSel=0;renderHead();loadView();};c.appendChild(chip);});}

async function loadView(){const cd=M.prompts[curP].conditions[curC];
 document.getElementById('viewinfo').textContent=cd.cond+' · '+(cd.committed?('→ '+cd.answer+(cd.correct?' ✓':' ✗')):'spiraled to cap');
 if(!cache[cd.file]){document.getElementById('tokens').innerHTML='<div class=hint>loading '+cd.file+'…</div>';
  try{const r=await fetch('./'+cd.file);cache[cd.file]=await r.json();}catch(e){document.getElementById('tokens').innerHTML='<div class=hint>fetch failed — serve results/workspace/ over http</div>';return;}}
 const d=cache[cd.file];const span=Object.keys(d.positions).map(Number).sort((a,b)=>a-b);
 const think=span.findIndex(p=>p>=(d.prompt_len||0));
 view={toks:span.map(p=>d.positions[p].token),cells:span.map(p=>{const o={};LAYERS.forEach(l=>o[l]=(d.positions[p].by_layer[l]||[]).slice(0,8));return o;}),think:think<0?0:think};
 renderTokens();renderSide();}

function maxW(c,l){const a=c[l];return a&&a.length?a[0][1]:0;}
function renderTokens(){if(!view)return;const box=document.getElementById('tokens');box.innerHTML='';
 const term=document.getElementById('search').value.trim().toLowerCase();
 view.toks.forEach((tk,i)=>{if(i===view.think&&view.think>0)box.appendChild(el('span','divider','▼ reasoning begins'));
  const cell=view.cells[i],w=maxW(cell,curLayer),isP=view.think>0&&i<view.think;
  const sp=el('span','tok'+(i===curSel?' sel':'')+(isP?' prompt':''));
  sp.style.background=i===curSel?'':'rgba(88,166,255,'+Math.min(.5,w*4).toFixed(3)+')';
  sp.textContent=tk.replace(/\n/g,'↵');
  if(term&&LAYERS.some(l=>(cell[l]||[]).some(c=>c[0].toLowerCase().includes(term))))sp.classList.add('hit');
  sp.onclick=()=>{curSel=i;renderTokens();renderSide();};sp.onmouseenter=()=>{curSel=i;renderSide();};
  box.appendChild(sp);if(tk.includes('\n'))box.appendChild(el('span',null,''),box.lastChild.style.display='block');});}

function renderSide(){if(!view)return;const cell=view.cells[curSel]||{};
 document.getElementById('postok').textContent='['+curSel+'] '+JSON.stringify(view.toks[curSel]||'');
 const host=document.getElementById('layers');host.innerHTML='';
 LAYERS.forEach(l=>{const b=el('div','layer');b.appendChild(el('div','lh','Layer '+l+(l===curLayer?'  (emphasis)':'')));
  const arr=cell[l]||[],mx=arr.length?arr[0][1]:1;
  arr.forEach(([c,w])=>{const r=el('div','cbar');r.appendChild(el('div','cn',c));
   const t=el('div','track'),f=el('div','fill');f.style.width=(mx?100*w/mx:0).toFixed(1)+'%';t.appendChild(f);
   r.appendChild(t);r.appendChild(el('div','cv',w.toFixed(3)));b.appendChild(r);});
  if(!arr.length)b.appendChild(el('div','hint','—'));host.appendChild(b);});}

document.getElementById('search').addEventListener('input',renderTokens);
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||!view)return;
 if(e.key==='ArrowRight'){curSel=Math.min(view.toks.length-1,curSel+1);renderTokens();renderSide();e.preventDefault();}
 if(e.key==='ArrowLeft'){curSel=Math.max(0,curSel-1);renderTokens();renderSide();e.preventDefault();}});
tabs();renderHead();loadView();
</script></body></html>"""


if __name__ == "__main__":
    main()
