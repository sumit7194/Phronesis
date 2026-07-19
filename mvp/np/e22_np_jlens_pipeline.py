#!/usr/bin/env python
"""E22 — Neuronpedia J-lens pipeline (NO local GPU). For each factual Q, call the hosted Jacobian
Lens on Qwen3.6-27B; extract the 27B's answer + whether the GOLD answer appears anywhere in the
workspace trajectory (logit-lens AND Jacobian-lens, all layers/positions). Redoes last night's
hallucination-workspace question properly, on a bigger model. Resilient (per-Q save, key rotation).
"""
import json, os, itertools, time, unicodedata, urllib.request, urllib.error
ENV="/Users/sumit/Downloads/NP/.env"; OUT="/Users/sumit/Github/Phronesis/mvp/np/e22_jlens_27b.json"
env={}
for l in open(ENV):
    m=l.strip().split('=',1)
    if len(m)==2: env[m[0].strip()]=m[1].strip()
KEYS=[env[k] for k in env if k.startswith('NEURONPEDIA_API_KEY')]; _kc=itertools.cycle(range(len(KEYS)))
def raw(path,body):
    for _ in range(len(KEYS)*2):
        ki=next(_kc)
        req=urllib.request.Request('https://www.neuronpedia.org'+path,data=json.dumps(body).encode(),
            headers={'Content-Type':'application/json','x-api-key':KEYS[ki]},method='POST')
        try:
            return urllib.request.urlopen(req,timeout=180).read().decode()
        except urllib.error.HTTPError as e:
            if e.code in (429,401): time.sleep(1); continue
            return json.dumps({"error":e.code,"body":e.read().decode()[:200]})
        except Exception as e: return json.dumps({"error":str(e)[:150]})
    return json.dumps({"error":"keys exhausted"})
def parse_stream(txt):
    dec=json.JSONDecoder(); out=[]; i=0; txt=txt.strip()
    while i<len(txt):
        while i<len(txt) and txt[i] in ' \n\r\t': i+=1
        if i>=len(txt): break
        try: o,i=dec.raw_decode(txt,i); out.append(o)
        except: break
    return out
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
QS=[("What is the capital of Bhutan?","Thimphu"),("What is the capital of Comoros?","Moroni"),
 ("What is the capital of Palau?","Ngerulmud"),("What is the capital of Nauru?","Yaren"),
 ("What is the currency of Bhutan?","ngultrum"),("Who wrote One Hundred Years of Solitude?","Marquez"),
 ("What is the largest species of shark?","whale"),("What is the longest river in Asia?","Yangtze"),
 ("Who composed The Four Seasons?","Vivaldi"),("What is the smallest bone in the human body?","stapes"),
 ("What is the capital of Kazakhstan?","Astana"),("Who won the Nobel Peace Prize in 2019?","Abiy"),
 ("What is the tallest waterfall in the world?","Angel"),("What is the deepest lake in the world?","Baikal"),
 ("What is the capital of Burkina Faso?","Ouagadougou")]
def workspace_hit(objs, gold):
    """Does gold's normalized form appear in any layer/position/lens top-8? Return (hit, where)."""
    g=norm(gold); best=None
    for o in objs:
        if o.get('kind')!='token': continue
        for res in o.get('results',[]):
            typ=res['type']
            for layer_idx,toks in enumerate(res.get('top_tokens',[])):
                for rank,t in enumerate(toks):
                    if g in norm(t) or norm(t).strip() in g and len(norm(t).strip())>2:
                        cand=(rank,layer_idx,o['position'],typ,t)
                        if best is None or rank<best[0]: best=cand
    return (best is not None), best
def main():
    res=json.load(open(OUT)) if os.path.exists(OUT) else []
    done={r['q'] for r in res}
    print(f"[e22] {len(QS)} Qs on Qwen3.6-27B J-lens, {len(done)} done, {len(KEYS)} keys")
    for q,gold in QS:
        if q in done: continue
        prompt=q+" Answer with just the name."
        txt=raw('/api/lens/prompt',{"modelId":"qwen3.6-27b","prompt":prompt})
        objs=parse_stream(txt)
        meta=next((o for o in objs if o.get('kind')=='meta'),{})
        done_o=next((o for o in objs if o.get('kind')=='done'),{})
        completion=done_o.get('completion','')[:120]
        correct=norm(gold) in norm(completion)
        hit,where=workspace_hit(objs,gold)
        cat="correct" if correct else ("truth_IN_workspace" if hit else "truth_ABSENT")
        rec={"q":q,"gold":gold,"completion":completion,"correct":bool(correct),
             "gold_in_workspace":hit,"where":where,"cat":cat,"n_objs":len(objs)}
        res.append(rec); json.dump(res,open(OUT,"w"),indent=1)
        print(f"  [{cat:>18}] {q[:34]:<34} gold={gold:<11} 27B_says={completion[:24]!r:<26} ws_hit@{where[:3] if where else None}",flush=True)
    from collections import Counter
    print("\n=== summary (Qwen3.6-27B) ===", dict(Counter(r['cat'] for r in res)))
    hall=[r for r in res if not r['correct']]
    print(f"hallucinations: {len(hall)}; truth-in-workspace: {sum(1 for r in hall if r['gold_in_workspace'])}, absent: {sum(1 for r in hall if not r['gold_in_workspace'])}")
    print("[done] ->",OUT)
main()
