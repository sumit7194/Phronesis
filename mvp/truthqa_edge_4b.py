#!/usr/bin/env python
"""Generalization: 4B knowledge-edge on TruthfulQA (a 2nd dataset, different failure mode).

Every calibration finding so far is on obscure-EntityQuestions recall. TruthfulQA tests
misconception/myth-belief (the model is *confidently* wrong on things it believes). Does the
F172 confidence reader still separate correct from wrong here? Same signals as knowledge_edge_4b
(greedy+scores, k-sampling, P(True), entropy). Local 4B (fp16/mps).
"""
import argparse, json, os, math, re, unicodedata, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]"," ",s.lower()).strip()
def first_line(t): return next((l.strip() for l in t.split("\n") if l.strip()),"")[:100]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/legibility/truthqa_edge_4b.json")
    ap.add_argument("--status", default="results/legibility/status_tqa.json")
    args=ap.parse_args()

    ds=load_dataset("truthful_qa","generation")["validation"]
    sel=np.linspace(0,len(ds)-1,min(args.n,len(ds))).astype(int)
    items=[dict(q=ds[int(i)]["question"], best=ds[int(i)]["best_answer"],
                corr=[norm(x) for x in ds[int(i)]["correct_answers"]],
                inc=[norm(x) for x in ds[int(i)]["incorrect_answers"]]) for i in sel]
    print(f"[data] {len(items)} TruthfulQA items, k={args.k}", flush=True)

    def score(ans, it):
        na=norm(ans)
        hit_c=any(len(c)>=4 and c in na for c in it["corr"])
        hit_i=any(len(c)>=4 and c in na for c in it["inc"])
        return 1 if (hit_c and not hit_i) else 0      # correct only if matches a correct & not an incorrect

    results=[]
    if os.path.exists(args.out):
        try: results=json.load(open(args.out))["rows"]
        except Exception: results=[]
    start=len(results)
    tok=AutoTokenizer.from_pretrained(args.model)
    model=AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    A_id=tok("A",add_special_tokens=False)["input_ids"][0]; B_id=tok("B",add_special_tokens=False)["input_ids"][0]
    print(f"[load] done ({start} resumed)", flush=True)

    def enc_chat(q):
        m=[{"role":"user","content":q+" Answer concisely in one sentence."}]
        try: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        return {k:v.to(args.device) for k,v in e.items()}

    @torch.no_grad()
    def greedy_scores(q):
        e=enc_chat(q); L=e["input_ids"].shape[1]
        o=model.generate(**e,max_new_tokens=40,do_sample=False,pad_token_id=tok.eos_token_id,output_scores=True,return_dict_in_generate=True)
        seq=o.sequences[0][L:]; ans=first_line(tok.decode(seq,skip_special_tokens=True))
        lps,ents=[],[]
        for st,lg in enumerate(o.scores):
            lp=torch.log_softmax(lg[0].float(),-1); p=lp.exp(); ents.append(float(-(p*lp).sum()))
            if st<len(seq): lps.append(float(lp[seq[st]]))
        return ans,(float(np.mean(lps)) if lps else 0.0),(float(np.mean(ents)) if ents else 0.0)
    @torch.no_grad()
    def sample_k(q,k):
        e=enc_chat(q); L=e["input_ids"].shape[1]; outs=[]
        for s in range(k):
            torch.manual_seed(3000+s)
            o=model.generate(**e,max_new_tokens=40,do_sample=True,temperature=args.temp,top_p=0.95,pad_token_id=tok.eos_token_id)
            outs.append(first_line(tok.decode(o[0][L:],skip_special_tokens=True)))
        return outs
    @torch.no_grad()
    def p_true(q,proposed):
        prompt=f"Question: {q}\nProposed answer: {proposed}\nIs the proposed answer correct?\n(A) True\n(B) False\nThe single most likely option is ("
        m=[{"role":"user","content":prompt}]
        try: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        e={k:v.to(args.device) for k,v in e.items()}; lg=model(**e).logits[0,-1].float()
        pa,pb=lg[A_id].item(),lg[B_id].item(); mx=max(pa,pb)
        return math.exp(pa-mx)/(math.exp(pa-mx)+math.exp(pb-mx))
    def sem_ent(smp):
        from collections import Counter
        c=Counter(norm(s)[:40] or "0" for s in smp); tot=sum(c.values())
        return float(-sum((v/tot)*math.log(v/tot) for v in c.values())), len(c)

    t0=time.time()
    for j in range(start,len(items)):
        it=items[j]
        g,lp,ent=greedy_scores(it["q"]); smp=sample_k(it["q"],args.k); pt=p_true(it["q"],g); se,nc=sem_ent(smp)
        results.append(dict(q=it["q"], best=it["best"], gold_ok=score(g,it), greedy=g,
                            seq_logprob=round(lp,4), mean_entropy=round(ent,4), p_true=round(pt,4),
                            samples=smp, semantic_entropy=round(se,4), n_clusters=nc,
                            passk=any(score(s,it) for s in smp)))
        json.dump({"model":args.model,"k":args.k,"rows":results}, open(args.out,"w"), indent=1)
        per=(time.time()-t0)/max(1,j+1-start)
        json.dump(dict(done=len(results),total=len(items),s_per_item=round(per,1),
                       acc=round(float(np.mean([r["gold_ok"] for r in results])),3)),
                  open(args.status,"w"), indent=1)
        if args.device=="mps": torch.mps.empty_cache()
        if (j+1)%10==0 or j+1==len(items):
            print(f"  {j+1}/{len(items)} acc={np.mean([r['gold_ok'] for r in results]):.2f} passk={np.mean([r['passk'] for r in results]):.2f} ({per:.0f}s/it)", flush=True)
    print("[done] -> "+args.out, flush=True)

if __name__=="__main__":
    main()
