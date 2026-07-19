#!/usr/bin/env python
"""E19 — fixed hallucination-workspace read. Harder obscure facts, no-think. Read gold-answer rank
across a LAYER SWEEP (facts live late, not at L20). For each Q: model's answer + gold's min rank
across layers (present-SOMEWHERE vs absent-EVERYWHERE). Correct answers validate the read (gold
should be low-rank at some layer). Hallucinations classified truth-PRESENT vs ABSENT.
"""
import json, os, sys
import torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READ_L=[14,20,26,30,33]   # + output
QS=[
 ("What is the capital of Bhutan?","Thimphu"),("What is the capital of Eritrea?","Asmara"),
 ("What is the capital of Mongolia?","Ulaanbaatar"),("What is the capital of Nepal?","Kathmandu"),
 ("What is the capital of Slovenia?","Ljubljana"),("What is the capital of Ecuador?","Quito"),
 ("What is the capital of Uruguay?","Montevideo"),("What is the capital of Laos?","Vientiane"),
 ("What is the capital of Ghana?","Accra"),("What is the capital of Latvia?","Riga"),
 ("Who wrote One Hundred Years of Solitude?","Marquez"),("Who wrote Crime and Punishment?","Dostoevsky"),
 ("Who was the first person to reach the South Pole?","Amundsen"),("Who discovered penicillin?","Fleming"),
 ("What is the chemical symbol for tungsten?","W"),("What is the atomic number of uranium?","92"),
 ("What is the largest moon of Saturn?","Titan"),("What is the deepest ocean trench?","Mariana"),
 ("What is the tallest waterfall in the world?","Angel"),("What is the smallest bone in the human body?","stapes"),
 ("What is the currency of Vietnam?","dong"),("What is the currency of Poland?","zloty"),
 ("In what year was the Eiffel Tower completed?","1889"),("In what year did the Berlin Wall fall?","1989"),
 ("What is the national animal of Scotland?","unicorn"),("What is the largest species of shark?","whale"),
 ("Who painted The Starry Night?","Gogh"),("What is the longest river in Asia?","Yangtze"),
]
def main():
    tok,hf,lens=load_model()
    fid=lambda s: tok(" "+s,add_special_tokens=False)["input_ids"][0]
    res=[]
    for q,gold in QS:
        pre=tok.apply_chat_template([{"role":"user","content":q+" Give only the answer."}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        ids=tok(pre,add_special_tokens=False,return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out=hf(ids["input_ids"],output_hidden_states=True)
            gen=hf.generate(**ids,max_new_tokens=12,do_sample=False,pad_token_id=tok.eos_token_id)
        ans=tok.decode(gen[0,ids["input_ids"].shape[1]:],skip_special_tokens=True).strip()
        gid=fid(gold); ranks={}
        for L in READ_L:
            lg=torch.log_softmax(lens.unembed(out.hidden_states[L][0,-1].unsqueeze(0)).float()[0],-1)
            ranks[L]=int((lg>lg[gid]).sum())
        ranks["out"]=int((torch.log_softmax(out.logits[0,-1].float(),-1)>torch.log_softmax(out.logits[0,-1].float(),-1)[gid]).sum())
        minrank=min(ranks.values())
        correct=gold.lower() in ans.lower()
        cat=("correct" if correct else ("truth_PRESENT" if minrank<=20 else "truth_ABSENT"))
        res.append({"q":q[:40],"gold":gold,"answer":ans[:35],"correct":correct,"min_rank":minrank,"ranks":ranks,"cat":cat})
        print(f"[{cat:>14}] {q[:36]:<36} gold={gold:<11} out={ans[:20]:<20} minrank={minrank:<6} (L20={ranks[20]},L30={ranks[30]},out={ranks['out']})",flush=True)
        json.dump(res,open(os.path.join(ROOT,"mvp/results/workspace/e19_halluc_layersweep.json"),"w"),indent=1)
        if DEVICE=="mps": torch.mps.empty_cache()
    from collections import Counter
    hal=[r for r in res if not r["correct"]]
    print(f"\n=== summary === {dict(Counter(r['cat'] for r in res))}")
    print(f"correct answers: median min-rank = {sorted([r['min_rank'] for r in res if r['correct']])[len([r for r in res if r['correct']])//2] if any(r['correct'] for r in res) else 'NA'} (should be LOW if the layer-read works)")
    print(f"hallucinations: {len(hal)}; truth-present {sum(1 for r in hal if r['cat']=='truth_PRESENT')}, truth-absent {sum(1 for r in hal if r['cat']=='truth_ABSENT')}")
    print("[done]")
main()
