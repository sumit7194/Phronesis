#!/usr/bin/env python
"""Path B v2 — gate -> search -> answer, Qwen3-4B. Prereg extends docs/prereg-gated-abstention.md.

For LOW-confidence items, instead of abstaining (F174), SEARCH (Wikipedia) + RAG-answer. Tests
whether gate->search fixes BOTH calibration halves: corrects confabulations AND rescues
underconfident-correct answers (which F174's read-only gating could not). To get the full
accuracy-vs-search-rate curve from one pass, we retrieve + RAG-answer EVERY item and also keep the
direct greedy answer; any gate threshold is then evaluated post-hoc. Local 4B + Wikipedia API.
"""
import json, urllib.request, urllib.parse, re, unicodedata, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler

UA="PhronesisResearch/0.1 (calibration experiment; payvizio@gmail.com)"
def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]"," ",s.lower()).strip()
def correct(ans,gold): na=norm(ans); return bool(na) and any(len(g)>=3 and g in na for g in gold)
def first_line(t): return next((l.strip() for l in t.split("\n") if l.strip()),"")[:80]

def wiki(entity, sentences=4):
    def get(u):
        return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA}),timeout=12))
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
    d=json.load(open("results/legibility/knowledge_edge_4b.json"))["rows"]
    gt=np.array([1 if r["hand_no_ok"] else 0 for r in d])
    # combined confidence reader (LOO logistic, as F174)
    SIG=np.column_stack([[r["p_true"] for r in d],[r["seq_logprob"] for r in d],
                         [-r["mean_entropy"] for r in d],[-r["semantic_entropy"] for r in d]])
    Xs=StandardScaler().fit_transform(SIG); conf=np.zeros(len(d))
    for tr,te in LeaveOneOut().split(Xs):
        conf[te]=LogisticRegression(max_iter=1000).fit(Xs[tr],gt[tr]).predict_proba(Xs[te])[0,1]

    tok=AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    model=AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B",torch_dtype=torch.float16).to("mps").eval()
    print("[load] done",flush=True)

    @torch.no_grad()
    def rag(q, ctx):
        msg=q+" Answer with just the name, as briefly as possible."
        content=(f"Context (may help; ignore if irrelevant):\n{ctx}\n\n{msg}") if ctx else msg
        m=[{"role":"user","content":content}]
        try: enc=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False)
        except TypeError: enc=tok.apply_chat_template(m,add_generation_prompt=True,return_tensors="pt",return_dict=True)
        enc={k:v.to("mps") for k,v in enc.items()}; L=enc["input_ids"].shape[1]
        o=model.generate(**enc,max_new_tokens=32,do_sample=False,pad_token_id=tok.eos_token_id)
        return first_line(tok.decode(o[0][L:],skip_special_tokens=True))

    out="results/legibility/gate_search_4b.json"
    rows=[]
    try: rows=json.load(open(out))["rows"]
    except Exception: pass
    t0=time.time()
    for i in range(len(rows), len(d)):
        r=d[i]; ent=r.get("entity") or r["q"]
        title,ctx=wiki(ent)
        ans=rag(r["q"], ctx)
        rows.append(dict(q=r["q"], entity=ent, gold_raw=r["gold_raw"], gold=r["gold"], hand_no_ok=r["hand_no_ok"],
                         greedy=r["greedy"], greedy_ok=bool(correct(r["greedy"],r["gold"])),
                         conf=float(conf[i]), wiki_title=title, search_ans=ans, search_ok=bool(correct(ans,r["gold"]))))
        json.dump({"rows":rows}, open(out,"w"), indent=1)
        if torch.backends.mps.is_available(): torch.mps.empty_cache()
        if (i+1)%10==0 or i+1==len(d):
            sk=np.mean([x["search_ok"] for x in rows]); gk=np.mean([x["greedy_ok"] for x in rows])
            print(f"  {i+1}/{len(d)} greedy_ok={gk:.2f} search_ok={sk:.2f} ({(time.time()-t0):.0f}s)",flush=True)
    print("[done] -> "+out,flush=True)

if __name__=="__main__":
    main()
