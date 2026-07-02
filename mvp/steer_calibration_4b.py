#!/usr/bin/env python
"""Path A — grounded calibration steering on Qwen3-4B. Prereg: docs/prereg-grounded-calibration-steering.md.

Tests whether a vector built from the GROUNDED, model-conditioned calibration seed (F172) beats
multi-seed random controls at moving the 4B — i.e. was the F160/F171 steering null a DATA problem,
or is steering the wrong tool? Extracts v_hedge (confident-wrong -> uncertainty) and v_commit
(correct-but-doubts -> assert) via diff-of-means; reports cos(v_hedge,v_commit) (single-axis test);
then steers v_hedge on HELD-OUT confab items (alpha-sweep calibrated to residual norm) vs >=3 random
seeds + baseline + sign control. Greedy primary. All raw saved. Local (MPS).
"""
import argparse, json, os, math, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HEDGE = ("not sure","don't know","do not know","dont know","can't","cannot","no reliable","unable",
         "not certain","unaware","don't have","do not have","not aware","no information","insufficient",
         "not able","couldn't","could not find","don't have reliable","not confident","i'm not")
def is_hedge(a): al=a.lower(); return any(h in al for h in HEDGE)

class Hook:
    def __init__(self, layer, vec, alpha):
        self.layer, self.alpha = layer, alpha
        v=torch.tensor(vec,dtype=torch.float32); self.v=(v/(v.norm()+1e-10)).unsqueeze(0).unsqueeze(0); self.h=None
    def fn(self,m,i,o):
        h=o[0] if isinstance(o,tuple) else o
        h=h+self.alpha*self.v.to(h.device).to(h.dtype)
        return (h,)+o[1:] if isinstance(o,tuple) else h
    def attach(self,model): self.h=model.model.layers[self.layer].register_forward_hook(self.fn)
    def detach(self):
        if self.h: self.h.remove(); self.h=None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--seed", default="results/legibility/calibration_seed_4b.json")
    ap.add_argument("--layers", default="10,14,17,20")
    ap.add_argument("--steer-layer", type=int, default=17)
    ap.add_argument("--alpha-fracs", default="-0.08,0,0.01,0.02,0.04,0.06,0.08,0.12")
    ap.add_argument("--rand-seeds", default="0,1,2")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--quant", type=int, default=0)               # 1 = 4-bit (for 32B on VM)
    ap.add_argument("--ke", default="results/legibility/knowledge_edge_4b.json")  # entity lookup
    ap.add_argument("--known-eval", default=None)   # JSON list [{q,gold,model_correct}] of model-KNOWN items (selectivity test); falls back to commit-targets if unset
    ap.add_argument("--save-vec", default=None)      # np.save v_hedge {layer:vec} here (for SAE decomposition)
    ap.add_argument("--hedge-mode", default="template", choices=["template","natural"])  # natural = content-controlled (F179 fix): entity-free diverse hedges vs length-matched confident wraps
    ap.add_argument("--pool", default="last", choices=["last","mean"])  # mean = mean-pool response tokens (kills last-token format bias)
    ap.add_argument("--status", default=None)        # live status.json for the dashboard
    ap.add_argument("--out", default="results/legibility/steer_calibration_4b.json")
    args=ap.parse_args()
    SWEEP=[int(x) for x in args.layers.split(",")]

    seed=json.load(open(args.seed))
    hedge_t, commit_t = seed["hedge_targets"], seed["commit_targets"]
    # entity lookup (seed lacks it) from the knowledge-edge data
    q2ent={r["q"]: r.get("entity") for r in json.load(open(args.ke))["rows"]}
    # split: extract on 2/3, hold out 1/3 (deterministic index split)
    def split(L,frac=0.69): k=int(len(L)*frac); return L[:k], L[k:]
    h_ext,h_eval = split(hedge_t); c_ext,c_eval = split(commit_t)
    print(f"[data] hedge {len(h_ext)}ext/{len(h_eval)}eval | commit {len(c_ext)}ext/{len(c_eval)}eval | layers {SWEEP}", flush=True)

    tok=AutoTokenizer.from_pretrained(args.model)
    if args.quant:
        from transformers import BitsAndBytesConfig
        bnb=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                               bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        model=AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
        args.device="cuda"
    else:
        model=AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print("[load] done", flush=True)

    def hedge_text(e): return f"I'm not sure — I don't have reliable information about {e} and could be wrong."
    # content-controlled mode (F179 fix): entity-FREE diverse hedges vs length-matched confident wraps.
    # Both sides are full first-person sentences of similar length; the only systematic difference is
    # epistemic stance (residual confound: the answer token appears on the assert side).
    NAT_HEDGES=[
        "I'm not sure about this one — I don't think I know the answer.",
        "Honestly, I can't recall this reliably, so I'd rather not guess.",
        "I don't know this with any confidence; my memory here is shaky.",
        "That's beyond what I reliably remember — I could easily be wrong.",
        "I'd only be guessing here, and I don't trust my own guess.",
        "I genuinely can't say — this isn't something I know well.",
    ]
    NAT_ASSERTS=[
        "The answer is {a} — I'm completely sure about that.",
        "It's {a}, without any doubt in my mind at all.",
        "That would be {a}; I know this one for certain.",
        "Definitely {a} — I'm fully confident in that answer.",
        "It's {a}, no question about it — I know this well.",
        "I'm certain it's {a}; this is something I clearly remember.",
    ]

    @torch.no_grad()
    def acts(q, response):
        m=[{"role":"user","content":q+" Answer with just the name, as briefly as possible."}]
        try: enc=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=False)
        except TypeError: enc=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        rsp=tok(response, add_special_tokens=False, return_tensors="pt")
        ids=torch.cat([enc["input_ids"], rsp["input_ids"]],1).to(args.device)
        hs=model(input_ids=ids, output_hidden_states=True).hidden_states
        p0=enc["input_ids"].shape[1]   # response tokens start here
        if args.pool=="mean":
            return {L: hs[L+1][0,p0:,:].mean(0).float().cpu().numpy() for L in SWEEP}
        return {L: hs[L+1][0,-1,:].float().cpu().numpy() for L in SWEEP}

    def build_vec(items, assert_key, virtuous="hedge"):
        # virtuous='hedge' -> v = mean(hedge) - mean(assert); virtuous='assert' -> v = mean(assert)-mean(hedge)
        A={L:[] for L in SWEEP}; H={L:[] for L in SWEEP}
        for i,it in enumerate(items):
            if args.hedge_mode=="natural":
                a_txt=NAT_ASSERTS[i%len(NAT_ASSERTS)].format(a=it[assert_key])
                h_txt=NAT_HEDGES[i%len(NAT_HEDGES)]
            else:
                a_txt=it[assert_key]; h_txt=hedge_text(_entity(it))
            a=acts(it["q"], a_txt); h=acts(it["q"], h_txt)
            for L in SWEEP: A[L].append(a[L]); H[L].append(h[L])
        vecs={}
        for L in SWEEP:
            am=np.mean(A[L],0); hm=np.mean(H[L],0)
            vecs[L]=(hm-am) if virtuous=="hedge" else (am-hm)
        return vecs, A, H

    def _entity(it):  # entity name for the hedge template
        return q2ent.get(it["q"]) or it.get("entity") or "this"

    print("[extract] v_hedge ...", flush=True)
    v_hedge,_,_ = build_vec(h_ext, "model_wrong", "hedge")
    print("[extract] v_commit ...", flush=True)
    v_commit,_,_ = build_vec(c_ext, "model_correct", "assert")
    cos={L: float(np.dot(v_hedge[L],v_commit[L])/(np.linalg.norm(v_hedge[L])*np.linalg.norm(v_commit[L])+1e-10)) for L in SWEEP}
    norms={L: float(np.linalg.norm(v_hedge[L])) for L in SWEEP}
    print("\n  Layer | cos(v_hedge,v_commit) | |v_hedge|");
    for L in SWEEP: print(f"  {L:>5} | {cos[L]:>+20.3f} | {norms[L]:.1f}", flush=True)
    best=args.steer_layer   # steer at the 4B workhorse layer (cos-min layer printed for reference)
    print(f"[extract] steering layer = {best} (cos={cos[best]:+.3f}); cos-min was L{min(SWEEP,key=lambda L:cos[L])}", flush=True)
    if args.save_vec:       # persist v_hedge (+v_commit) for SAE decomposition (Neuronpedia)
        np.save(args.save_vec, {**{L:v_hedge[L] for L in SWEEP}, **{f"commit_{L}":v_commit[L] for L in SWEEP}}, allow_pickle=True)
        print(f"[save-vec] v_hedge/v_commit (layers {SWEEP}) -> {args.save_vec}", flush=True)

    # calibrate alpha to residual norm at best layer
    rn=[]
    def cap(m,i,o): h=o[0] if isinstance(o,tuple) else o; rn.append(float(h[0].norm(dim=-1).mean()))
    hh=model.model.layers[best].register_forward_hook(cap)
    with torch.no_grad():
        for it in h_eval[:5]: acts(it["q"], "x")
    hh.remove(); rnorm=float(np.mean(rn))
    ALPHAS=[round(float(f)*rnorm,1) for f in args.alpha_fracs.split(",")]
    print(f"[calib] resid norm @L{best} ~ {rnorm:.0f}; alphas={ALPHAS}", flush=True)

    @torch.no_grad()
    def gen(q, vec, alpha):
        m=[{"role":"user","content":q+" Answer with just the name, as briefly as possible."}]
        try: enc=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=False)
        except TypeError: enc=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        enc={k:v.to(args.device) for k,v in enc.items()}; L=enc["input_ids"].shape[1]
        hook=Hook(best,vec,alpha) if alpha!=0 else None
        if hook: hook.attach(model)
        try: o=model.generate(**enc, max_new_tokens=40, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            if hook: hook.detach()
        txt=tok.decode(o[0][L:], skip_special_tokens=True)
        return next((l.strip() for l in txt.split("\n") if l.strip()), "")[:120]

    # STEER eval: v_hedge on held-out confab items (does hedge-rate rise vs random?)
    vh=v_hedge[best]
    rand_vecs={s: (lambda r: r/np.linalg.norm(r)*np.linalg.norm(vh))(np.random.default_rng(s).standard_normal(vh.shape).astype(np.float32))
               for s in [int(s) for s in args.rand_seeds.split(",")]}
    result=dict(model=args.model, layer=best, cos=cos, residual_norm=rnorm, alphas=ALPHAS,
                hedge_eval=[], commit_extract_n=len(c_ext),
                hedge_mode=args.hedge_mode, pool=args.pool)
    t0=time.time()
    def write_status(total):
        if not args.status: return
        n=len(result["hedge_eval"])+len(result.get("known_eval",[]))
        per=(time.time()-t0)/max(1,n)
        hc={str(a): round(100*np.mean([is_hedge(r["real"][str(a)]) for r in result["hedge_eval"]])) if result["hedge_eval"] else None for a in ALPHAS}
        kh={str(a): round(100*np.mean([is_hedge(r["real"][str(a)]) for r in result.get("known_eval",[])])) if result.get("known_eval") else None for a in ALPHAS}
        rec=[dict(kind=k, q=r["q"][:38], gold=r["gold"], base=r["real"][str(0.0)][:22], steered=(r["real"][str(ALPHAS[-1])] or "∅")[:22])
             for k,xs in (("confab",result["hedge_eval"][-3:]),("correct",result.get("known_eval",[])[-3:])) for r in xs]
        json.dump(dict(done=n,total=total,layer=best,residual_norm=round(rnorm),s_per_item=round(per,1),
                       eta_min=round((total-n)*per/60),alphas=ALPHAS,hedge_confab=hc,hedge_correct=kh,recent=rec),
                  open(args.status,"w"), indent=1)
    print("\n[steer] v_hedge on held-out confab items ...", flush=True)
    known_items=c_eval   # default: tiny commit-target set
    if args.known_eval:  # proper known pool: model-KNOWN items from knowledge-edge (selectivity test, n>>2)
        known_items=json.load(open(args.known_eval))
        print(f"[known] using proper known-eval set: {len(known_items)} model-known items (vs {len(c_eval)} commit-targets)", flush=True)
    TOTAL=len(h_eval)+len(known_items)
    for it in h_eval:
        rec=dict(q=it["q"], gold=it["gold"], baseline_wrong=it["model_wrong"], real={}, rand={})
        for a in ALPHAS: rec["real"][str(a)]=gen(it["q"], vh, a)
        for a in ALPHAS:                                  # random control at EVERY positive alpha (F171 lesson)
            if a<=0: continue
            for s,rv in rand_vecs.items(): rec["rand"][f"{a}|seed{s}"]=gen(it["q"], rv, a)
        result["hedge_eval"].append(rec)
        json.dump(result, open(args.out,"w"), indent=1); write_status(TOTAL)
        if args.device=="mps": torch.mps.empty_cache()
        print(f"  {it['q'][:40]:40s} base->[{rec['real'][str(0.0)][:22]}] hi->[{rec['real'][str(ALPHAS[-1])][:22]}]", flush=True)
    # COMPLETING TEST: does v_hedge ALSO hedge items the model KNOWS? (calibration vs global push)
    print("\n[steer] v_hedge on held-out KNOWN items ...", flush=True)
    result["known_eval"]=[]; result["known_n"]=len(known_items)
    for it in known_items:
        rec=dict(q=it["q"], gold=it["gold"], baseline_correct=it["model_correct"], real={})
        for a in ALPHAS: rec["real"][str(a)]=gen(it["q"], vh, a)
        result["known_eval"].append(rec)
        json.dump(result, open(args.out,"w"), indent=1); write_status(TOTAL)
        if args.device=="mps": torch.mps.empty_cache()
        print(f"  KNOWN {it['q'][:32]:32s} base->[{rec['real']['0.0'][:20]}] hi->[{rec['real'][str(ALPHAS[-1])][:20]}]", flush=True)

    # hedge-rate summary (auto prefilter; hand-read later): v_hedge vs mean-random, per alpha
    xs=result["hedge_eval"]
    print("\n=== hedge-rate (auto): v_hedge vs random (mean of 3 seeds), per alpha ===")
    for a in ALPHAS:
        real=np.mean([is_hedge(r['real'][str(a)]) for r in xs])
        if a>0:
            rnd=np.mean([is_hedge(r['rand'][f'{a}|seed{s}']) for r in xs for s in rand_vecs])
            print(f"  a={a:>7.1f}: v_hedge={real:.0%}   random={rnd:.0%}")
        else:
            print(f"  a={a:>7.1f}: v_hedge={real:.0%}")
    json.dump(result, open(args.out,"w"), indent=1)
    print(f"[done] -> {args.out}", flush=True)

if __name__=="__main__":
    main()
