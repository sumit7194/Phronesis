#!/usr/bin/env python
"""Qwen3-32B knowledge-edge map (4-bit, L4) — scale test of F172. Mirrors knowledge_edge_4b.py.

Per item: greedy+scores (seq log-prob, predictive entropy), k samples (pass@k + semantic entropy),
verbalized P(True). Reuses the 200 hand-scored 32B EntityQuestions (GT in entityq_32b_handscore.json;
gens in entityq_think_32b.json). Writes status.json for the dashboard. Checkpointed.
"""
import argparse, json, os, math, unicodedata, re, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]"," ",s.lower()).strip()
def first_line(t): return next((l.strip() for l in t.split("\n") if l.strip()),"")[:80]
def correct(a,g): na=norm(a); return bool(na) and any(len(x)>=3 and x in na for x in g)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--gt", default="entityq_32b_handscore.json")
    ap.add_argument("--gens", default="entityq_think_32b.json")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--out", default="knowledge_edge_32b.json")
    ap.add_argument("--status", default="status.json")
    args=ap.parse_args()

    gt={r["q"]:r for r in json.load(open(args.gt))}
    gens=json.load(open(args.gens)); gens=gens["rows"] if isinstance(gens,dict) else gens
    items=[dict(q=r["q"], entity=r.get("entity"), pop=r.get("pop"), gold=r["gold"], gold_raw=r.get("gold_raw"),
                greedy_nothink=r.get("nothink",""), hand_no_ok=gt.get(r["q"],{}).get("hand_no_ok")) for r in gens]
    print(f"[data] {len(items)} items, k={args.k}", flush=True)

    results=[]
    if os.path.exists(args.out):
        try: results=json.load(open(args.out))["rows"]
        except Exception: results=[]
    start=len(results)
    bnb=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                           bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tok=AutoTokenizer.from_pretrained(args.model)
    model=AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
    A_id=tok("A",add_special_tokens=False)["input_ids"][0]; B_id=tok("B",add_special_tokens=False)["input_ids"][0]
    print(f"[load] done ({start} resumed)", flush=True)

    def enc_chat(q):
        m=[{"role":"user","content":q+" Answer with just the name, as briefly as possible."}]
        try: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        return {k:v.to("cuda") for k,v in e.items()}

    @torch.no_grad()
    def greedy_scores(q):
        enc=enc_chat(q); L=enc["input_ids"].shape[1]
        o=model.generate(**enc,max_new_tokens=24,do_sample=False,pad_token_id=tok.eos_token_id,
                         output_scores=True,return_dict_in_generate=True)
        seq=o.sequences[0][L:]; ans=first_line(tok.decode(seq,skip_special_tokens=True))
        lps,ents=[],[]
        for step,lg in enumerate(o.scores):
            lp=torch.log_softmax(lg[0].float(),-1); p=lp.exp(); ents.append(float(-(p*lp).sum()))
            if step<len(seq): lps.append(float(lp[seq[step]]))
        return ans,(float(np.mean(lps)) if lps else 0.0),(float(np.mean(ents)) if ents else 0.0)

    @torch.no_grad()
    def sample_k(q,k):
        enc=enc_chat(q); L=enc["input_ids"].shape[1]; outs=[]
        for s in range(k):
            torch.manual_seed(1000+s)
            o=model.generate(**enc,max_new_tokens=24,do_sample=True,temperature=args.temp,top_p=0.95,pad_token_id=tok.eos_token_id)
            outs.append(first_line(tok.decode(o[0][L:],skip_special_tokens=True)))
        return outs

    @torch.no_grad()
    def p_true(q,proposed):
        prompt=(f"Question: {q}\nProposed answer: {proposed}\nIs the proposed answer correct?\n(A) True\n(B) False\nThe single most likely option is (")
        m=[{"role":"user","content":prompt}]
        try: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        e={k:v.to("cuda") for k,v in e.items()}; lg=model(**e).logits[0,-1].float()
        pa,pb=lg[A_id].item(),lg[B_id].item(); mx=max(pa,pb)
        return math.exp(pa-mx)/(math.exp(pa-mx)+math.exp(pb-mx))

    def sem_ent(samples):
        from collections import Counter
        c=Counter(norm(s) or "0" for s in samples); tot=sum(c.values())
        return float(-sum((v/tot)*math.log(v/tot) for v in c.values())), len(c)

    t0=time.time()
    for j in range(start,len(items)):
        it=items[j]
        g,lp,ent=greedy_scores(it["q"]); smp=sample_k(it["q"],args.k); pt=p_true(it["q"],g); se,nc=sem_ent(smp)
        results.append(dict(q=it["q"], entity=it["entity"], pop=it["pop"], gold_raw=it["gold_raw"], gold=it["gold"],
                            hand_no_ok=it["hand_no_ok"], greedy=g, seq_logprob=round(lp,4), mean_entropy=round(ent,4),
                            p_true=round(pt,4), samples=smp, semantic_entropy=round(se,4), n_clusters=nc,
                            auto_greedy_ok=correct(g,it["gold"]), auto_passk=any(correct(s,it["gold"]) for s in smp)))
        json.dump({"model":args.model,"k":args.k,"rows":results}, open(args.out,"w"), indent=1)
        per=(time.time()-t0)/max(1,j+1-start)
        json.dump(dict(done=len(results),total=len(items),s_per_item=round(per,1),
                       eta_h=round(per*(len(items)-j-1)/3600,2),
                       auto_greedy=round(float(np.mean([r["auto_greedy_ok"] for r in results])),3),
                       auto_passk=round(float(np.mean([r["auto_passk"] for r in results])),3),
                       recent=[{"pop":int(r["pop"] or 0),"q":r["q"][:60],"gold":r["gold_raw"],
                                "greedy":r["greedy"][:30],"p_true":r["p_true"]} for r in results[-6:]]),
                  open(args.status,"w"), indent=1)
        if (j+1)%5==0 or j+1==len(items):
            print(f"  {j+1}/{len(items)} greedy={np.mean([r['auto_greedy_ok'] for r in results]):.2f} passk={np.mean([r['auto_passk'] for r in results]):.2f} ({per:.0f}s/it)", flush=True)
    print("[done] -> "+args.out, flush=True)

if __name__=="__main__":
    main()
