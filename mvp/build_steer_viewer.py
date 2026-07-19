#!/usr/bin/env python
"""Two-level J-space viewer: reasoning/steering runs AND deception runs, in one page.

Level 1 = prompt.  Level 2 = condition (baseline/steered, or honest/roleplay/sabotage/secret).
Each chip carries a precomputed dot(color)+stat+tooltip so steering (commit/doubt) and deception
(truth-token workspace rank) both read coherently. Concept data fetched on demand from the LAN
server. Serve results/workspace/ so it can fetch ./6q/*.json ./steer/*.json ./deception/*.json.
"""
import glob, json, os, re

WS = "results/workspace"
STEER_PROMPTS = ["q1_no_a", "q1_plain", "q2_math_solved", "q3_gsm_rescuable",
                 "q4_math_wall", "q5_gsm_solved", "q6_gsm_failed"]
DECEPT_ITEMS = ["france", "japan", "sky", "planet", "hot", "barks"]
SECRETS = ["sec_banana", "sec_tiger", "sec_copper"]
LAYERS = ["14", "20", "26"]
DOUBT = {"wait", "hmm", "maybe", "actually", "however", "but", "confused", "confusion",
         "mistake", "wrong", "doubt", "unsure", "uncertain", "perhaps", "again", "guess",
         "suppose", "seems", "no", "not", "oops", "error"}
STEER_ORDER = ["baseline", "IH+12", "IH-12", "EG+12", "EG-12", "RT+12", "RT-12",
               "VC+12", "VC-12", "random0+12", "random1+12"]
DEC_ORDER = ["honest", "roleplay", "sabotage", "secret"]


def doubt_load(positions):
    tot = n = 0.0
    for r in positions.values():
        tot += sum(w for c, w in r["by_layer"].get("20", []) if c.lower() in DOUBT)
        n += 1
    return round(tot / max(n, 1), 4)


def steer_cond(cond, kind, file, d, sm):
    committed = bool(sm.get("committed")) if sm else (("</think>" in d.get("trace", "")) or
                                                      bool(re.findall(r"\\boxed", d.get("trace", ""))))
    correct = bool(sm.get("correct")) if sm else bool(d.get("correct"))
    dl = sm.get("doubt_load") if sm else doubt_load(d["positions"])
    dot = "commit-ok" if committed and correct else "commit-wrong" if committed else "spiral"
    ans = (sm.get("answer") if sm else d.get("answer")) or ""
    return {"cond": cond, "kind": kind, "file": file, "dot": dot,
            "stat": (f"{dl:.3f}" if dl is not None else ""),
            "title": (("commit " + str(ans)[:12] + (" ✓" if correct else " ✗")) if committed
                      else "spiraled") + (f" · doubt {dl}" if dl is not None else "")}


def dec_cond(pid, cond):
    f = f"{WS}/deception/{pid}__{cond}.json"
    if not os.path.exists(f):
        return None
    s = json.load(open(f)).get("_sum", {})
    tr, nb = s.get("truth_rank"), s.get("null_best_rank")
    if cond == "honest":
        dot = "honest"
    else:
        dot = "caught" if (tr is not None and tr <= 5) else "missed"
    lbl = "honest" if cond == "honest" else "lied/concealed (auto)"
    return {"cond": cond, "kind": "deception", "file": f"deception/{pid}__{cond}.json", "dot": dot,
            "stat": (f"truth r{tr}" if tr is not None else ""),
            "title": f"{lbl} · truth rank {tr} · null {nb}"}


def main():
    manifest = {"prompts": {}, "order": [], "layers": LAYERS}

    # --- steering / reasoning prompts ---
    for pid in STEER_PROMPTS:
        bp = f"{WS}/6q/{pid}_masked.json"
        if not os.path.exists(bp):
            continue
        d = json.load(open(bp))
        conds = [steer_cond("baseline", "baseline", f"6q/{pid}_masked.json", d, None)]
        for f in sorted(glob.glob(f"{WS}/steer/{pid}__*.json")):
            sm = json.load(open(f)).get("_sum", {})
            cn = sm.get("cond", os.path.basename(f).split("__")[1][:-5])
            conds.append(steer_cond(cn, "random" if "random" in cn else "virtue",
                                    f"steer/{pid}__{cn}.json", None, sm))
        conds.sort(key=lambda c: {v: i for i, v in enumerate(STEER_ORDER)}.get(c["cond"], 99))
        manifest["prompts"][pid] = {"question": d.get("question", ""), "gold": str(d.get("gold", "")),
                                    "group": "reasoning/steering", "conditions": conds}
        manifest["order"].append(pid)

    # --- deception prompts (factual items + secrets) ---
    for pid in DECEPT_ITEMS + SECRETS:
        conds = [c for c in (dec_cond(pid, cn) for cn in DEC_ORDER) if c]
        if not conds:
            continue
        meta = json.load(open(f"{WS}/deception/{pid}__{conds[0]['cond']}.json"))
        manifest["prompts"][pid] = {"question": meta.get("question", pid), "gold": str(meta.get("gold", "")),
                                    "group": "deception", "conditions": conds}
        manifest["order"].append(pid)

    # --- connection-gap chains (think vs no-think composed) ---
    for f in sorted(glob.glob(f"{WS}/connect/*__think.json")):
        cid = os.path.basename(f).replace("__think.json", "")
        conds = []
        for regime in ("think", "nothink"):
            p = f"{WS}/connect/{cid}__{regime}.json"
            if not os.path.exists(p):
                continue
            s = json.load(open(p)).get("_sum", {})
            ok, brk = bool(s.get("composed_ok")), s.get("bridge_rank")
            conds.append({"cond": regime, "kind": "connect", "file": f"connect/{cid}__{regime}.json",
                          "dot": "commit-ok" if ok else "spiral",
                          "stat": (f"bridge r{brk}" if brk is not None else ""),
                          "title": f"composed {'✓' if ok else '✗'} · bridge rank {brk} · gold rank {s.get('gold_rank')}"})
        if conds:
            d = json.load(open(f))
            manifest["prompts"][cid] = {"question": d.get("question", cid), "gold": str(d.get("gold", "")),
                                        "group": "connection (2-hop)", "conditions": conds}
            manifest["order"].append(cid)

    html = TEMPLATE.replace("__PAYLOAD__", json.dumps(manifest, ensure_ascii=False))
    out = f"{WS}/steer_viewer.html"
    with open(out, "w") as fh:
        fh.write(html)
    n = sum(len(p["conditions"]) for p in manifest["prompts"].values())
    print(f"wrote {out} ({len(html)/1e3:.0f} KB), {len(manifest['prompts'])} prompts, {n} views")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>J-space viewer · steering + deception</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2330;--border:#2b3444;--text:#e6edf3;--dim:#8b949e;
 --accent:#58a6ff;--good:#3fb950;--bad:#f85149;--warn:#d29922;--sel:#1f6feb;--bar:#3b5bdb;--barbg:#22272e}
@media(prefers-color-scheme:light){:root{--bg:#fff;--panel:#f6f8fa;--panel2:#eef1f4;--border:#d0d7de;
 --text:#1f2328;--dim:#656d76;--accent:#0969da;--good:#1a7f37;--bad:#cf222e;--warn:#9a6700;--sel:#0969da;--bar:#4c6ef5;--barbg:#e6eaef}}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text)}
header{padding:12px 16px;border-bottom:1px solid var(--border)}h1{font-size:15px;margin:0 0 8px}
.grouplabel{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);margin:6px 0 3px}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.tab{padding:6px 11px;border:1px solid var(--border);border-radius:7px;background:var(--panel);cursor:pointer;font-size:12.5px;color:var(--text)}
.tab.active{background:var(--sel);border-color:var(--sel);color:#fff}
.qbox{background:var(--panel2);border:1px solid var(--border);border-radius:7px;padding:8px 11px;font-size:12.5px;margin:8px 0}
.conds{display:flex;flex-wrap:wrap;gap:5px}
.chip{padding:5px 9px;border:1px solid var(--border);border-radius:6px;background:var(--panel);cursor:pointer;font-size:11.5px;display:flex;gap:6px;align-items:center}
.chip.active{border-color:var(--accent);background:var(--panel2)}
.chip .dot{width:8px;height:8px;border-radius:50%}
.dot.commit-ok,.dot.caught{background:var(--good)}.dot.commit-wrong{background:var(--warn)}
.dot.spiral,.dot.missed{background:var(--bad)}.dot.honest{background:var(--accent)}
.chip .dl{color:var(--dim)}.chip.random{border-style:dashed}
.wrap{display:grid;grid-template-columns:1fr 360px;height:calc(100vh - 210px)}
.stream{overflow-y:auto;padding:14px 16px;border-right:1px solid var(--border)}
.controls{display:flex;gap:10px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.controls input{background:var(--panel);border:1px solid var(--border);color:var(--text);padding:5px 8px;border-radius:6px;font-size:12px;width:150px}
.seg{display:flex;border:1px solid var(--border);border-radius:6px;overflow:hidden}
.seg button{background:var(--panel);border:0;color:var(--dim);padding:4px 9px;cursor:pointer;font-size:12px}.seg button.on{background:var(--sel);color:#fff}
.tok{cursor:pointer;border-radius:3px}.tok:hover{outline:1px solid var(--accent)}.tok.sel{background:var(--sel)!important;color:#fff}
.tok.hit{box-shadow:inset 0 -2px 0 var(--warn)}.tok.prompt{color:var(--dim);font-style:italic}
.divider{display:block;text-align:center;color:var(--warn);font-size:11px;margin:10px 0;border-top:1px dashed var(--border);padding-top:6px}
.side{overflow-y:auto;padding:14px;background:var(--panel)}.side h3{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);margin:0 0 4px}
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
<header><h1>J-space viewer · steering + deception · what the model holds in mind</h1><div id="tabhost"></div>
 <div class="qbox" id="qbox"></div><div class="conds" id="conds"></div></header>
<div class="wrap"><div class="stream"><div class="controls">
 <input id="search" placeholder="highlight concept…" autocomplete="off"><div class="seg" id="layerseg"></div>
 <span class="hint" id="viewinfo"></span></div><div id="tokens"><div class="hint">loading…</div></div></div>
 <div class="side"><h3>Selected token</h3><div class="postok" id="postok">— tap a token —</div><div id="layers"></div>
  <div class="hint">top-8 word-like concepts / layer · deception: watch the truth/secret token's rank while the output hides it</div></div></div>
<script id="m" type="application/json">__PAYLOAD__</script>
<script>
const M=JSON.parse(document.getElementById('m').textContent),LAYERS=M.layers;
let curP=M.order[0],curC=0,curLayer="20",curSel=0,view=null;const cache={};
function el(t,c,x){const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e;}
function tabs(){const host=document.getElementById('tabhost');host.innerHTML='';
 let lastG=null;M.order.forEach(p=>{const g=M.prompts[p].group;
  if(g!==lastG){host.appendChild(el('div','grouplabel',g));const row=el('div','tabs');row.dataset.g=g;host.appendChild(row);lastG=g;}
  const row=[...host.querySelectorAll('.tabs')].pop();const b=el('div','tab'+(p===curP?' active':''),p.replace(/_/g,' '));
  b.onclick=()=>{curP=p;curC=0;curSel=0;renderHead();loadView();};row.appendChild(b);});
 const s=document.getElementById('layerseg');s.innerHTML='';LAYERS.forEach(l=>{const b=el('button',l===curLayer?'on':'',"L"+l);
  b.onclick=()=>{curLayer=l;[...s.children].forEach(x=>x.classList.toggle('on',x.textContent==='L'+curLayer));renderTokens();};s.appendChild(b);});}
function renderHead(){const P=M.prompts[curP];
 document.querySelectorAll('#tabhost .tab').forEach(t=>t.classList.toggle('active',t.textContent===curP.replace(/_/g,' ')));
 document.getElementById('qbox').textContent='gold '+P.gold+' · '+P.question;
 const c=document.getElementById('conds');c.innerHTML='';
 P.conditions.forEach((cd,i)=>{const chip=el('div','chip'+(i===curC?' active':'')+(cd.kind==='random'?' random':''));
  chip.appendChild(el('span','dot '+cd.dot));chip.appendChild(el('span',null,cd.cond));
  if(cd.stat)chip.appendChild(el('span','dl',cd.stat));chip.title=cd.title;
  chip.onclick=()=>{curC=i;curSel=0;renderHead();loadView();};c.appendChild(chip);});}
async function loadView(){const cd=M.prompts[curP].conditions[curC];
 document.getElementById('viewinfo').textContent=cd.cond+' · '+cd.title;
 if(!cache[cd.file]){document.getElementById('tokens').innerHTML='<div class=hint>loading…</div>';
  try{cache[cd.file]=await (await fetch('./'+cd.file)).json();}catch(e){document.getElementById('tokens').innerHTML='<div class=hint>fetch failed — serve results/workspace/ over http</div>';return;}}
 const d=cache[cd.file],span=Object.keys(d.positions).map(Number).sort((a,b)=>a-b),th=span.findIndex(p=>p>=(d.prompt_len||0));
 view={toks:span.map(p=>d.positions[p].token),cells:span.map(p=>{const o={};LAYERS.forEach(l=>o[l]=(d.positions[p].by_layer[l]||[]).slice(0,8));return o;}),think:th<0?0:th};
 renderTokens();renderSide();}
function mw(c,l){const a=c[l];return a&&a.length?a[0][1]:0;}
function renderTokens(){if(!view)return;const box=document.getElementById('tokens');box.innerHTML='';
 const term=document.getElementById('search').value.trim().toLowerCase();
 view.toks.forEach((tk,i)=>{if(i===view.think&&view.think>0)box.appendChild(el('span','divider','▼ reasoning begins'));
  const cell=view.cells[i],w=mw(cell,curLayer),isP=view.think>0&&i<view.think;
  const sp=el('span','tok'+(i===curSel?' sel':'')+(isP?' prompt':''));sp.style.background=i===curSel?'':'rgba(88,166,255,'+Math.min(.5,w*4).toFixed(3)+')';
  sp.textContent=tk.replace(/\n/g,'↵');if(term&&LAYERS.some(l=>(cell[l]||[]).some(c=>c[0].toLowerCase().includes(term))))sp.classList.add('hit');
  sp.onclick=()=>{curSel=i;renderTokens();renderSide();};sp.onmouseenter=()=>{curSel=i;renderSide();};
  box.appendChild(sp);if(tk.includes('\n')){const br=el('span');br.style.display='block';box.appendChild(br);}});}
function renderSide(){if(!view)return;const cell=view.cells[curSel]||{};
 document.getElementById('postok').textContent='['+curSel+'] '+JSON.stringify(view.toks[curSel]||'');
 const host=document.getElementById('layers');host.innerHTML='';
 LAYERS.forEach(l=>{const b=el('div','layer');b.appendChild(el('div','lh','Layer '+l+(l===curLayer?'  (emphasis)':'')));
  const arr=cell[l]||[],mx=arr.length?arr[0][1]:1;arr.forEach(([c,w])=>{const r=el('div','cbar');r.appendChild(el('div','cn',c));
   const t=el('div','track'),f=el('div','fill');f.style.width=(mx?100*w/mx:0).toFixed(1)+'%';t.appendChild(f);r.appendChild(t);r.appendChild(el('div','cv',w.toFixed(3)));b.appendChild(r);});
  if(!arr.length)b.appendChild(el('div','hint','—'));host.appendChild(b);});}
document.getElementById('search').addEventListener('input',renderTokens);
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||!view)return;
 if(e.key==='ArrowRight'){curSel=Math.min(view.toks.length-1,curSel+1);renderTokens();renderSide();e.preventDefault();}
 if(e.key==='ArrowLeft'){curSel=Math.max(0,curSel-1);renderTokens();renderSide();e.preventDefault();}});
tabs();renderHead();loadView();
</script></body></html>"""


if __name__ == "__main__":
    main()
