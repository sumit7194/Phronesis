#!/usr/bin/env python
"""E20 overnight — hallucination/correctness probe pipeline (RESILIENT: checkpoint every 15, resume,
disk-guard). Stage A: run 4B no-think on ~200 factual Qs, capture late-layer hidden states + label
correct/wrong (accent-normalized). Stage B: per-layer logistic probe predicting correct-vs-wrong
(does the model KNOW when it hallucinates?). Stage C: answer-recovery on the misses (is gold rank
low at best layer vs a random-answer baseline?). Writes summary for morning review.
"""
import json, os, re, shutil, sys, time, unicodedata
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); WS=os.path.join(ROOT,"mvp/results/workspace")
LS=[20,26,30,33]; CAP=os.path.join(WS,"e20_capture.npz"); META=os.path.join(WS,"e20_meta.json")
OUT=os.path.join(WS,"e20_summary.json"); STAT=os.path.join(WS,"status_e20.json")
CAPITALS={"Bhutan":"Thimphu","Eritrea":"Asmara","Mongolia":"Ulaanbaatar","Nepal":"Kathmandu","Slovenia":"Ljubljana","Ecuador":"Quito","Uruguay":"Montevideo","Laos":"Vientiane","Ghana":"Accra","Latvia":"Riga","Bhutan ":"Thimphu","Armenia":"Yerevan","Azerbaijan":"Baku","Georgia":"Tbilisi","Moldova":"Chisinau","Tajikistan":"Dushanbe","Turkmenistan":"Ashgabat","Kyrgyzstan":"Bishkek","Bahrain":"Manama","Qatar":"Doha","Oman":"Muscat","Yemen":"Sanaa","Jordan":"Amman","Lebanon":"Beirut","Brunei":"Bandar","Bhutan  ":"Thimphu","Fiji":"Suva","Samoa":"Apia","Tonga":"Nukualofa","Vanuatu":"Port Vila","Palau":"Ngerulmud","Nauru":"Yaren","Tuvalu":"Funafuti","Kiribati":"Tarawa","Suriname":"Paramaribo","Guyana":"Georgetown","Belize":"Belmopan","Honduras":"Tegucigalpa","Nicaragua":"Managua","Paraguay":"Asuncion","Bolivia":"Sucre","Namibia":"Windhoek","Botswana":"Gaborone","Zambia":"Lusaka","Malawi":"Lilongwe","Rwanda":"Kigali","Burundi":"Gitega","Togo":"Lome","Benin":"Porto-Novo","Chad":"Ndjamena","Niger":"Niamey","Mali":"Bamako","Gabon":"Libreville","Djibouti":"Djibouti","Mauritania":"Nouakchott","Lesotho":"Maseru","Eswatini":"Mbabane","Comoros":"Moroni","Seychelles":"Victoria"}
ELEMENTS={"tungsten":74,"uranium":92,"cobalt":27,"nickel":28,"zinc":30,"arsenic":33,"bromine":35,"krypton":36,"strontium":38,"zirconium":40,"molybdenum":42,"palladium":46,"cadmium":48,"tin":50,"antimony":51,"iodine":53,"cesium":55,"barium":56,"tungsten ":74,"platinum":78,"mercury":80,"lead":82,"bismuth":83,"radon":86,"radium":88,"thorium":90,"plutonium":94,"argon":18,"neon":10,"helium":2}
YEARS=[("the Eiffel Tower was completed","1889"),("the Berlin Wall fell","1989"),("the Titanic sank","1912"),("the French Revolution began","1789"),("penicillin was discovered","1928"),("the first moon landing happened","1969"),("the Chernobyl disaster occurred","1986"),("the Wright brothers first flew","1903"),("the American Civil War ended","1865"),("World War I began","1914"),("the Great Fire of London occurred","1666"),("the printing press was invented by Gutenberg","1440"),("Krakatoa erupted","1883"),("the Suez Canal opened","1869"),("the telephone was patented by Bell","1876"),("Mount Vesuvius destroyed Pompeii","79"),("the Magna Carta was signed","1215"),("the Declaration of Independence was signed","1776"),("Napoleon was defeated at Waterloo","1815"),("the Spanish Armada was defeated","1588")]
MISC=[("Who wrote One Hundred Years of Solitude?","Marquez"),("Who wrote Crime and Punishment?","Dostoevsky"),("Who was the first person to reach the South Pole?","Amundsen"),("Who painted The Starry Night?","Gogh"),("What is the deepest ocean trench?","Mariana"),("What is the tallest waterfall in the world?","Angel"),("What is the smallest bone in the human body?","stapes"),("What is the currency of Vietnam?","dong"),("What is the currency of Poland?","zloty"),("What is the largest moon of Saturn?","Titan"),("What is the longest river in Asia?","Yangtze"),("What is the largest species of shark?","whale"),("Who discovered penicillin?","Fleming"),("What is the hardest natural substance?","diamond"),("Who developed the theory of general relativity?","Einstein"),("What is the largest internal organ in the human body?","liver"),("What is the most abundant gas in Earth's atmosphere?","nitrogen"),("Who wrote The Brothers Karamazov?","Dostoevsky"),("What is the capital of Iceland?","Reykjavik"),("What is the longest mountain range in the world?","Andes"),("Who invented the telephone?","Bell"),("What planet is known as the Red Planet?","Mars"),("What is the largest island in the world?","Greenland"),("Who wrote Don Quixote?","Cervantes"),("What is the national flower of Japan?","cherry"),("Who composed the Four Seasons?","Vivaldi"),("What is the largest lake in Africa?","Victoria"),("What is the currency of Thailand?","baht"),("What is the fastest land animal?","cheetah"),("Who wrote War and Peace?","Tolstoy"),("What is the largest desert in Asia?","Gobi"),("Who discovered gravity?","Newton"),("What is the study of earthquakes called?","seismology"),("What is the largest bird in the world?","ostrich"),("What is the currency of South Korea?","won"),("Who wrote The Odyssey?","Homer"),("What is the tallest animal in the world?","giraffe"),("What is the chemical symbol for potassium?","K"),("What is the capital of Finland?","Helsinki"),("Who painted Guernica?","Picasso")]
def build_qs():
    qs=[]
    for c,cap in CAPITALS.items(): qs.append((f"What is the capital of {c.strip()}?",cap,"capital"))
    for e,n in ELEMENTS.items(): qs.append((f"What is the atomic number of {e.strip()}?",str(n),"element"))
    for ev,y in YEARS: qs.append((f"In what year did {ev}? Give only the year.",y,"year"))
    for q,g in MISC: qs.append((q,g,"misc"))
    # dedup by question
    seen=set(); out=[]
    for q,g,c in qs:
        if q in seen: continue
        seen.add(q); out.append((q,g,c))
    return out
def norm(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]","",s)
def main():
    qs=build_qs()
    meta=json.load(open(META)) if os.path.exists(META) else []
    done={m["q"] for m in meta}
    hs={L:[] for L in LS}
    if os.path.exists(CAP):
        z=np.load(CAP);  hs={L:list(z[f"L{L}"]) for L in LS}
    tok,hf,lens=load_model()
    fid=lambda s: tok(" "+s,add_special_tokens=False)["input_ids"][0]
    print(f"[capture] {len(qs)} Qs, {len(done)} done",flush=True)
    for i,(q,gold,cat) in enumerate(qs):
        if q in done: continue
        if shutil.disk_usage("/").free/1e9 < 3: print("[STOP] disk"); break
        pre=tok.apply_chat_template([{"role":"user","content":q+" Give only the answer."}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        ids=tok(pre,add_special_tokens=False,return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out=hf(ids["input_ids"],output_hidden_states=True)
            gen=hf.generate(**ids,max_new_tokens=12,do_sample=False,pad_token_id=tok.eos_token_id)
        ans=tok.decode(gen[0,ids["input_ids"].shape[1]:],skip_special_tokens=True).strip()
        correct = norm(gold) in norm(ans)
        gid=fid(gold); ranks={}
        for L in LS:
            lg=lens.unembed(out.hidden_states[L][0,-1].unsqueeze(0)).float()[0]
            ranks[L]=int((lg>lg[gid]).sum()); hs[L].append(out.hidden_states[L][0,-1].float().cpu().numpy())
        meta.append({"q":q,"gold":gold,"cat":cat,"answer":ans[:40],"correct":bool(correct),"gold_rank":ranks})
        done.add(q)
        if len(meta)%15==0 or i==len(qs)-1:
            np.savez(CAP,**{f"L{L}":np.array(hs[L]) for L in LS}); json.dump(meta,open(META,"w"))
            json.dump({"done":len(meta),"total":len(qs),"correct":sum(m["correct"] for m in meta),"free_gb":round(shutil.disk_usage('/').free/1e9,1),"ts":time.strftime("%H:%M:%S")},open(STAT,"w"))
        if DEVICE=="mps": torch.mps.empty_cache()
    np.savez(CAP,**{f"L{L}":np.array(hs[L]) for L in LS}); json.dump(meta,open(META,"w"))
    # ---- Stage B: correctness probes ----
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    y=np.array([1 if m["correct"] else 0 for m in meta])
    z=np.load(CAP)
    summ={"n":len(meta),"n_correct":int(y.sum()),"n_wrong":int((1-y).sum()),"cat_counts":{}}
    from collections import Counter
    summ["cat_counts"]=dict(Counter(m["cat"] for m in meta))
    summ["cat_acc"]={c:round(np.mean([m["correct"] for m in meta if m["cat"]==c]),2) for c in set(m["cat"] for m in meta)}
    print(f"\n[probe] n={len(meta)} correct={int(y.sum())} wrong={int((1-y).sum())}")
    if 8<=y.sum()<=len(y)-8:  # need both classes
        summ["probe_auroc"]={}
        for L in LS:
            X=np.array(z[f"L{L}"]); X=X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-9)
            cv=StratifiedKFold(5,shuffle=True,random_state=0)
            au=cross_val_score(LogisticRegression(max_iter=2000,C=1.0),X,y,cv=cv,scoring="roc_auc")
            summ["probe_auroc"][L]=round(float(au.mean()),3)
            print(f"   L{L}: correctness-probe AUROC = {au.mean():.3f}")
        best=max(summ["probe_auroc"],key=summ["probe_auroc"].get); summ["best_layer"]=best
    else:
        summ["probe_auroc"]="SKIPPED (need >=8 of each class); consider harder Qs"
        print("   probe skipped: not enough of both classes")
    # ---- Stage C: answer-recovery on the misses ----
    wrong=[m for m in meta if not m["correct"]]
    if wrong:
        summ["n_hallucinations"]=len(wrong)
        # gold rank at each layer for the misses (present-somewhere = low min rank)
        minranks=[min(m["gold_rank"].values()) for m in wrong]
        summ["halluc_gold_minrank"]={"median":int(np.median(minranks)),"present_le20":int(sum(r<=20 for r in minranks)),"absent_gt1000":int(sum(r>1000 for r in minranks))}
        summ["halluc_examples"]=[{"q":m["q"][:40],"gold":m["gold"],"answer":m["answer"],"gold_minrank":min(m["gold_rank"].values())} for m in wrong[:15]]
        print(f"\n[recovery] {len(wrong)} misses; gold-minrank median={int(np.median(minranks))}, present(<=20)={sum(r<=20 for r in minranks)}, absent(>1000)={sum(r>1000 for r in minranks)}")
    json.dump(summ,open(OUT,"w"),indent=1)
    open(os.path.join(WS,"E20_DONE"),"w").write("done"); print("[done] -> "+OUT)
main()
