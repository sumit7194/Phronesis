#!/usr/bin/env python
"""Path B v2 at scale — gate->search->answer on Qwen3-32B (4-bit, L4 VM). Mirrors gate_search_4b.py.

For every item: keep direct greedy answer + retrieve (Wikipedia) and RAG-answer, so any gate
threshold is evaluated post-hoc. Tests whether search still helps a model that already knows more
(36% vs 4B 22%), and whether it catches the 32B's heavy confident-confabulation cell (F176).
status.json for the dashboard. Checkpointed.
"""
import json, urllib.request, urllib.parse, re, unicodedata, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler

UA="PhronesisResearch/0.1 (calibration experiment; payvizio@gmail.com)"
def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]"," ",s.lower()).strip()
def correct(a,g): na=norm(a); return bool(na) and any(len(x)>=3 and x in na for x in g)
def first_line(t): return next((l.strip() for l in t.split("\n") if l.strip()),"")[:80]

def wiki(entity, sentences=4):
    def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA}),timeout=12))
    try:
        s=urllib.parse.urlencode({"action":"query","list":"search","srsearch":entity,"format":"json","srlimit":1})
        hits=get("https://en.wikipedia.org/w/api.php?"+s)["query"]["search"]
        if not hits: return "",""
        title=hits[0]["title"]
        e=urllib.parse.urlencode({"action":"query","prop":"extracts","exintro":1,"explaintext":1,"titles":title,"format":"json"})
        pg=next(iter(get("https://en.wikipedia.org/w/api.php?"+e)["query"]["pages"].values()))
        return title, " ".join(pg.get("extract","").split(". ")[:sentences])[:700]
    except Exception: return "",""

def main():
    d=json.load(open("knowledge_edge_32b.json"))["rows"]
    gt=np.array([1 if r.get("hand_no_ok") else 0 for r in d])
    SIG=np.column_stack([[r["p_true"] for r in d],[r["seq_logprob"] for r in d],
                         [-r["mean_entropy"] for r in d],[-r["semantic_entropy"] for r in d]])
    Xs=StandardScaler().fit_transform(SIG); conf=np.zeros(len(d))
    for tr,te in LeaveOneOut().split(Xs):
        conf[te]=LogisticRegression(max_iter=1000).fit(Xs[tr],gt[tr]).predict_proba(Xs[te])[0,1]

    bnb=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                           bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
    model=AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-32B", quantization_config=bnb, device_map="cuda").eval()
    print("[load] done", flush=True)

    @torch.no_grad()
    def rag(q, ctx):
        msg=q+" Answer with just the name, as briefly as possible."
        content=(f"Context (may help; ignore if irrelevant):\n{ctx}\n\n{msg}") if ctx else msg
        m=[{"role":"user","content":content}]
        try: enc=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: enc=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        enc={k:v.to("cuda") for k,v in enc.items()}; L=enc["input_ids"].shape[1]
        o=model.generate(**enc,max_new_tokens=32,do_sample=False,pad_token_id=tok.eos_token_id)
        return first_line(tok.decode(o[0][L:],skip_special_tokens=True))

    out="gate_search_32b.json"; rows=[]
    try: rows=json.load(open(out))["rows"]
    except Exception: pass
    t0=time.time()
    for i in range(len(rows), len(d)):
        r=d[i]; ent=r.get("entity") or r["q"]
        title,ctx=wiki(ent); ans=rag(r["q"], ctx)
        rows.append(dict(q=r["q"], entity=ent, gold_raw=r["gold_raw"], gold=r["gold"], hand_no_ok=r.get("hand_no_ok"),
                         greedy=r["greedy"], greedy_ok=bool(correct(r["greedy"],r["gold"])), conf=float(conf[i]),
                         wiki_title=title, search_ans=ans, search_ok=bool(correct(ans,r["gold"]))))
        json.dump({"rows":rows}, open(out,"w"), indent=1)
        gk=np.mean([x["greedy_ok"] for x in rows]); sk=np.mean([x["search_ok"] for x in rows])
        per=(time.time()-t0)/max(1,len(rows))
        json.dump(dict(done=len(rows),total=len(d),s_per_item=round(per,1),eta_h=round(per*(len(d)-len(rows))/3600,2),
                       greedy=round(float(gk),3),search=round(float(sk),3),
                       recent=[{"q":x["q"][:50],"gold":x["gold_raw"],"greedy":x["greedy"][:24],"search":x["search_ans"][:24],"ok":x["search_ok"]} for x in rows[-6:]]),
                  open("status.json","w"), indent=1)
        torch.cuda.empty_cache()
        if len(rows)%10==0 or len(rows)==len(d):
            print(f"  {len(rows)}/{len(d)} greedy={gk:.2f} search={sk:.2f} ({per:.0f}s/it)", flush=True)
    print("[done] -> "+out, flush=True)

if __name__=="__main__":
    main()
