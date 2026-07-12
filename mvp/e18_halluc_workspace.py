#!/usr/bin/env python
"""E18 (idea 1) — hallucination workspace read. Factual Qs graded famous->obscure, THINKING OFF.
At the answer position read the L20 workspace (logit lens): is the GOLD answer present even when the
model outputs something WRONG? Classifies: correct / halluc-truth-PRESENT (gold in top-k, output
wrong = readout failure) / halluc-truth-ABSENT (gold not in top-k = knowledge wall).
"""
import json, os, sys
import torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); L=20
QS=[  # (question, gold short answer) — graded famous -> obscure/confusable
 ("What is the capital of France?","Paris"),
 ("Who wrote the play Romeo and Juliet?","Shakespeare"),
 ("What is the largest planet in our solar system?","Jupiter"),
 ("What is the chemical symbol for iron?","Fe"),
 ("Who painted the Mona Lisa?","Vinci"),
 ("What is the capital of Australia?","Canberra"),
 ("What is the capital of Turkey?","Ankara"),
 ("What is the capital of Canada?","Ottawa"),
 ("What is the capital of Brazil?","Bras"),
 ("What is the capital of Switzerland?","Bern"),
 ("What is the capital of Kazakhstan?","Astana"),
 ("What is the currency of Sweden?","krona"),
 ("Who wrote the novel 1984?","Orwell"),
 ("What is the capital of New Zealand?","Wellington"),
 ("Who won the Nobel Peace Prize in 2019?","Abiy"),
 ("What is the capital of Myanmar?","Naypyidaw"),
 ("What is the smallest country in the world?","Vatican"),
 ("What element has the atomic number 79?","gold"),
]
def main():
    tok,hf,lens=load_model()
    def first_id(s): return tok(" "+s,add_special_tokens=False)["input_ids"][0]
    res=[]
    for q,gold in QS:
        msgs=[{"role":"user","content":q+" Give only the answer, no explanation."}]
        pre=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        ids=tok(pre,add_special_tokens=False,return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out=hf(ids["input_ids"],output_hidden_states=True)
            gen=hf.generate(**ids,max_new_tokens=12,do_sample=False,pad_token_id=tok.eos_token_id)
        ans=tok.decode(gen[0,ids["input_ids"].shape[1]:],skip_special_tokens=True).strip()
        gid=first_id(gold)
        h20=out.hidden_states[L][0,-1]                      # residual at answer-onset position
        ws=torch.log_softmax(lens.unembed(h20.unsqueeze(0)).float()[0],-1)
        outlg=torch.log_softmax(out.logits[0,-1].float(),-1)
        gold_rank_ws=int((ws>ws[gid]).sum()); gold_rank_out=int((outlg>outlg[gid]).sum())
        topws=[repr(tok.decode([t])) for t in torch.topk(ws,10).indices.tolist()]
        correct=gold.lower() in ans.lower()
        cat=("correct" if correct else ("halluc_truth_PRESENT" if gold_rank_ws<=20 else "halluc_truth_ABSENT"))
        r={"q":q[:45],"gold":gold,"answer":ans[:40],"correct":correct,"gold_rank_ws_L20":gold_rank_ws,
           "gold_rank_out":gold_rank_out,"cat":cat,"top_ws":topws}
        res.append(r)
        print(f"[{cat:>20}] {q[:38]:<38} gold={gold:<11} out={ans[:22]:<22} gold_rank(L20/out)={gold_rank_ws}/{gold_rank_out}",flush=True)
        json.dump(res,open(os.path.join(ROOT,"mvp/results/workspace/e18_halluc_workspace.json"),"w"),indent=1)
        if DEVICE=="mps": torch.mps.empty_cache()
    from collections import Counter
    print("\n=== summary ===",dict(Counter(r['cat'] for r in res)))
    print("[done]")
main()
