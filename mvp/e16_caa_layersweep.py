#!/usr/bin/env python
"""E16 — FAIR CAA sycophancy comparison: per-method LAYER SWEEP. Build v_dom (CAA diff-of-means)
and v_behav (behavioral-Jacobian) at each layer, find each method's OWN best layer, compare there
(so neither is handicapped by a forced layer). Deterministic A/B logit scoring. Qwen3-4B.
Incremental save per layer; disk-guard.
"""
import json, os, shutil, sys, time
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,"corpus/external/caa_sycophancy"); WS=os.path.join(ROOT,"mvp/results/workspace")
LAYERS=[10,14,16,18,20,24]; NBUILD=200; OUT=os.path.join(WS,"e16_caa_layersweep.json")
def letter_ids(tok):
    def one(s):
        for c in (s," "+s):
            ii=tok(c,add_special_tokens=False)["input_ids"]
            if len(ii)==1: return ii[0]
        return tok(s,add_special_tokens=False)["input_ids"][0]
    return one("A"),one("B")
def pids(tok,q):
    return tok(tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)+"The best answer is (",add_special_tokens=False)["input_ids"]
def main():
    tok,hf,_=load_model(); Aid,Bid=letter_ids(tok)
    gen=json.load(open(os.path.join(D,"generate.json")))[:NBUILD]; test=json.load(open(os.path.join(D,"test_ab.json")))
    sylet=lambda e:e["answer_matching_behavior"].strip("() ")
    CKPT=os.path.join(WS,"e16_build_ckpt.npy")
    if os.path.exists(CKPT):
        c=np.load(CKPT,allow_pickle=True).item()
        match=c["match"]; nonmatch=c["nonmatch"]; grads=c["grads"]; norms=c["norms"]; start=c["n"]
        print(f"[build] RESUMED from ckpt at {start}/{NBUILD}",flush=True)
    else:
        match={L:[] for L in LAYERS}; nonmatch={L:[] for L in LAYERS}; grads={L:[] for L in LAYERS}; norms={L:[] for L in LAYERS}; start=0
    print(f"[build] {NBUILD} pairs, layers {LAYERS} (from {start})",flush=True)
    for gi,e in enumerate(gen):
        if gi<start: continue
        base=pids(tok,e["question"]); sl=sylet(e); nl="B" if sl=="A" else "A"
        caps={}
        hs=[hf.model.layers[L].register_forward_hook((lambda L:(lambda m,i,o:caps.__setitem__(L,o[0] if isinstance(o,tuple) else o)))(L)) for L in LAYERS]
        with torch.no_grad():
            for lett,bucket in ((sl,match),(nl,nonmatch)):
                lid=tok(lett,add_special_tokens=False)["input_ids"][0]
                hf(torch.tensor([base+[lid]],device=DEVICE))
                for L in LAYERS:
                    bucket[L].append(caps[L][0,-1].float().cpu().numpy())
                    if lett==sl: norms[L].append(float(caps[L][0,-1].norm()))
        for h in hs: h.remove()
        emb=hf.model.embed_tokens(torch.tensor([base],device=DEVICE)).detach().requires_grad_(True)
        caps={}
        hs=[hf.model.layers[L].register_forward_hook((lambda L:(lambda m,i,o:caps.__setitem__(L,o[0] if isinstance(o,tuple) else o)))(L)) for L in LAYERS]
        out=hf(inputs_embeds=emb); last=out.logits[0,-1]
        slid=tok(sl,add_special_tokens=False)["input_ids"][0]; nlid=tok(nl,add_special_tokens=False)["input_ids"][0]
        gs=torch.autograd.grad(last[nlid]-last[slid],[caps[L] for L in LAYERS])
        for L,g in zip(LAYERS,gs): grads[L].append(g[0,-1].detach().float().cpu().numpy())
        for h in hs: h.remove()
        del out,caps,emb,gs
        if DEVICE=="mps": torch.mps.empty_cache()
        if (gi+1)%25==0:
            np.save(CKPT,{"match":match,"nonmatch":nonmatch,"grads":grads,"norms":norms,"n":gi+1})
            print(f"  build {gi+1}/{NBUILD} (ckpt saved)",flush=True)
    np.save(CKPT,{"match":match,"nonmatch":nonmatch,"grads":grads,"norms":norms,"n":NBUILD})
    print("[build] complete, ckpt saved",flush=True)
    vdom={L:np.mean(match[L],0)-np.mean(nonmatch[L],0) for L in LAYERS}   # +=more syc
    vbeh={L:np.mean(grads[L],0) for L in LAYERS}                           # +=less syc
    nrm={L:float(np.mean(norms[L])) for L in LAYERS}
    rng=np.random.default_rng(0)
    def steer_rate(L,vec,alpha):
        hits=[]
        for e in test:
            base=pids(tok,e["question"]); sl=sylet(e)
            h=None
            if vec is not None:
                vv=torch.tensor(vec/np.linalg.norm(vec),dtype=torch.float16,device=DEVICE)
                h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
            with torch.no_grad(): lg=hf(torch.tensor([base],device=DEVICE)).logits[0,-1].float()
            if h:h.remove()
            sylg=lg[Aid if sl=="A" else Bid].item(); nolg=lg[Bid if sl=="A" else Aid].item()
            hits.append(sylg-nolg)   # >0 picks sycophantic
        if DEVICE=="mps": torch.mps.empty_cache()
        return hits
    base_margin=steer_rate(LAYERS[0],None,0)   # layer-independent
    rate=lambda ms: round(float(np.mean([m>0 for m in ms])),3)
    anti=lambda ms: round(float(np.mean(np.array(ms)>np.array(base_margin))),3)
    res=json.load(open(OUT)) if os.path.exists(OUT) else {"baseline_rate":rate(base_margin),"alpha_frac":0.2,"per_layer":{}}
    print(f"\nbaseline sycophancy rate = {res['baseline_rate']}\n{'layer':>5} {'domReduce':>10} {'behavReduce':>12} {'randMean':>9}  (rate; lower=less syc)")
    for L in LAYERS:
        if str(L) in res["per_layer"]:
            r=res["per_layer"][str(L)]; print(f"{L:>5} {r['dom_reduce_rate']:>10} {r['behav_reduce_rate']:>12} {r['rand_rate_mean']:>9}   (cached)"); continue
        a=0.2*nrm[L]
        dm=steer_rate(L,vdom[L],-a); bm=steer_rate(L,vbeh[L],+a)
        rr=[steer_rate(L,rng.standard_normal(vdom[L].shape),a) for _ in range(3)]
        res["per_layer"][str(L)]={"dom_reduce_rate":rate(dm),"behav_reduce_rate":rate(bm),
            "rand_rate_mean":round(float(np.mean([rate(r) for r in rr])),3),
            "dom_anti":anti(dm),"behav_anti":anti(bm),"rand_anti_mean":round(float(np.mean([anti(r) for r in rr])),3),
            "cos_dom_behav":round(float(np.dot(vdom[L]/np.linalg.norm(vdom[L]),vbeh[L]/np.linalg.norm(vbeh[L]))),3),"alpha":round(a,2)}
        r=res["per_layer"][str(L)]
        print(f"{L:>5} {r['dom_reduce_rate']:>10} {r['behav_reduce_rate']:>12} {r['rand_rate_mean']:>9}   cos={r['cos_dom_behav']:+.2f}",flush=True)
        json.dump(res,open(OUT,"w"),indent=1)
    dombest=min(LAYERS,key=lambda L:res["per_layer"][str(L)]["dom_reduce_rate"])
    behbest=min(LAYERS,key=lambda L:res["per_layer"][str(L)]["behav_reduce_rate"])
    res["fair"]={"dom_best_layer":dombest,"dom_best_rate":res["per_layer"][str(dombest)]["dom_reduce_rate"],
                 "behav_best_layer":behbest,"behav_best_rate":res["per_layer"][str(behbest)]["behav_reduce_rate"],
                 "baseline":res["baseline_rate"]}
    json.dump(res,open(OUT,"w"),indent=1)
    print(f"\n=== FAIR (each method at its OWN best layer) ===")
    print(f"  baseline syc rate      = {res['baseline_rate']}")
    print(f"  CAA diff-of-means best = {res['fair']['dom_best_rate']} (L{dombest})")
    print(f"  behavioral-Jacobian best= {res['fair']['behav_best_rate']} (L{behbest})")
    open(os.path.join(WS,"E16_DONE"),"w").write("done"); print("[done] -> "+OUT)
main()
