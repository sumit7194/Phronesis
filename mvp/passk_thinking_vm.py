#!/usr/bin/env python
"""Pass@k thinking-recall — the proper measurement the F169/F170 retraction said we lacked.

Per obscure-EntityQuestions item, draw k temperature samples in BOTH no-think and think modes;
score pass@k (= can the right answer be reached in k tries) for each. This is Google's metric
(pass@k + sampling), not our prior pass@1 greedy. Parameterized: 32B (4-bit/cuda, VM) or 4B
(fp16/mps, Mac). Reuses the existing 200 items + gold. status.json + checkpointed.
"""
import argparse, json, os, re, unicodedata, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]"," ",s.lower()).strip()
def correct(a,g): na=norm(a); return bool(na) and any(len(x)>=3 and x in na for x in g)
def first_line(t): return next((l.strip() for l in t.split("\n") if l.strip()),"")[:80]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--gens", default="entityq_think_32b.json")     # source of the 200 items + gold
    ap.add_argument("--device", default="cuda")                    # cuda (32B) or mps (4B)
    ap.add_argument("--quant", type=int, default=1)                # 1 = 4-bit (for 32B)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--n", type=int, default=0)                    # 0 = all items
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--max-think", type=int, default=512)
    ap.add_argument("--out", default="passk_thinking_32b.json")
    ap.add_argument("--status", default="status.json")
    args=ap.parse_args()

    gens=json.load(open(args.gens)); gens=gens["rows"] if isinstance(gens,dict) else gens
    items=[dict(q=r["q"], entity=r.get("entity"), pop=r.get("pop"), gold=r["gold"], gold_raw=r.get("gold_raw")) for r in gens]
    if args.n: items=items[:args.n]
    print(f"[data] {len(items)} items, k={args.k}", flush=True)

    results=[]
    if os.path.exists(args.out):
        try: results=json.load(open(args.out))["rows"]
        except Exception: results=[]
    start=len(results)
    tok=AutoTokenizer.from_pretrained(args.model)
    if args.quant:
        from transformers import BitsAndBytesConfig
        bnb=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                               bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        model=AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
    else:
        model=AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    close_ids=tok("</think>", add_special_tokens=False)["input_ids"]
    print(f"[load] done ({start} resumed)", flush=True)

    def enc(q, thinking):
        m=[{"role":"user","content":q+" Answer with just the name, as briefly as possible."}]
        try: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=thinking)
        except TypeError: e=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        return {k:v.to(args.device) for k,v in e.items()}

    def find_close(ids):
        n=len(close_ids)
        for i in range(len(ids)-n,-1,-1):
            if ids[i:i+n]==close_ids: return i+n
        return None

    @torch.no_grad()
    def sample(q, thinking, k):
        e=enc(q,thinking); L=e["input_ids"].shape[1]; outs=[]
        mx=args.max_think if thinking else 24
        for s in range(k):
            torch.manual_seed(2000+s)
            o=model.generate(**e,max_new_tokens=mx,do_sample=True,temperature=args.temp,top_p=0.95,pad_token_id=tok.eos_token_id)
            ids=o[0].tolist()
            if thinking:
                c=find_close(ids[L:]); ans=first_line(tok.decode(ids[L+c:] if c else ids[L:], skip_special_tokens=True))
            else:
                ans=first_line(tok.decode(ids[L:], skip_special_tokens=True))
            outs.append(ans)
        return outs

    t0=time.time()
    for j in range(start,len(items)):
        it=items[j]
        nt=sample(it["q"],False,args.k); th=sample(it["q"],True,args.k)
        results.append(dict(q=it["q"], entity=it["entity"], pop=it["pop"], gold_raw=it["gold_raw"], gold=it["gold"],
                            nothink_samples=nt, think_samples=th,
                            nothink_passk=any(correct(s,it["gold"]) for s in nt),
                            think_passk=any(correct(s,it["gold"]) for s in th),
                            nothink_pass1=correct(nt[0],it["gold"]), think_pass1=correct(th[0],it["gold"])))
        json.dump({"model":args.model,"k":args.k,"rows":results}, open(args.out,"w"), indent=1)
        per=(time.time()-t0)/max(1,j+1-start)
        json.dump(dict(done=len(results),total=len(items),s_per_item=round(per,1),eta_h=round(per*(len(items)-j-1)/3600,2),
                       nothink_passk=round(float(np.mean([r["nothink_passk"] for r in results])),3),
                       think_passk=round(float(np.mean([r["think_passk"] for r in results])),3),
                       nothink_pass1=round(float(np.mean([r["nothink_pass1"] for r in results])),3),
                       think_pass1=round(float(np.mean([r["think_pass1"] for r in results])),3),
                       recent=[{"q":r["q"][:50],"gold":r["gold_raw"],"nt_pk":r["nothink_passk"],"th_pk":r["think_passk"]} for r in results[-6:]]),
                  open(args.status,"w"), indent=1)
        if args.device=="mps": torch.mps.empty_cache()
        else: torch.cuda.empty_cache()
        if (j+1)%5==0 or j+1==len(items):
            r=results; print(f"  {j+1}/{len(items)} | pass@k: nt={np.mean([x['nothink_passk'] for x in r]):.2f} th={np.mean([x['think_passk'] for x in r]):.2f} | pass@1: nt={np.mean([x['nothink_pass1'] for x in r]):.2f} th={np.mean([x['think_pass1'] for x in r]):.2f} ({per:.0f}s/it)", flush=True)
    print("[done] -> "+args.out, flush=True)

if __name__=="__main__":
    main()
