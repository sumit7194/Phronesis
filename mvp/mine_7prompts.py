#!/usr/bin/env python
"""Deep-mine the 7-prompt workspace data (the viewer's _masked.json files). Reads only saved
JSON — safe to run while the fit trains. Answers:
 (A) scoring recheck: does the trace TEXT reach the gold answer even if labeled wrong/truncated?
 (B) doubt/metacognition load: are 'confusion/mistake/wait/maybe/funny' etc. in the workspace,
     and is that load higher on the failing prompts?
 (C) no-a specifics: number-words timeline + where self-aware concepts (funny/ridiculous/loop) appear.
"""
import json, os, re, sys
from collections import Counter

D = "results/workspace/6q"
ORDER = ["q1_no_a", "q1_plain", "q2_math_solved", "q3_gsm_rescuable", "q4_math_wall",
         "q5_gsm_solved", "q6_gsm_failed"]
DOUBT = {"wait", "hmm", "maybe", "actually", "however", "but", "confused", "confusion",
         "mistake", "wrong", "doubt", "unsure", "uncertain", "perhaps", "recheck", "again",
         "hold", "guess", "suppose", "seems", "no", "not", "hmm", "oops", "error"}
ABSURD = {"funny", "ridiculous", "silly", "absurd", "endless", "forever", "loop", "tedious",
          "pointless", "stuck", "weird", "strange", "obviously", "clearly", "tiring"}


def load(qid):
    p = f"{D}/{qid}_masked.json"
    return json.load(open(p)) if os.path.exists(p) else None


def all_concepts(rec):
    """yield (pos, layer, rank, concept, weight) over every cell."""
    for p, r in rec["positions"].items():
        for l, cs in r["by_layer"].items():
            for rank, (c, w) in enumerate(cs):
                yield int(p), l, rank, c.lower(), w


def main():
    print("=" * 90)
    print("(A) SCORING RECHECK — is the gold answer present in the trace text?")
    print("=" * 90)
    for qid in ORDER:
        d = load(qid)
        if not d:
            continue
        gold = str(d["gold"]).lower()
        t = d["trace"].lower()
        gold_in = gold in t if gold != "none" else any(
            w in t for w in ("no such", "none of", "no number", "does not contain",
                             "doesn't contain", "no positive", "there is no"))
        # also: last 300 chars — did it conclude near the end?
        near_end = gold in t[-400:] if gold != "none" else any(
            w in t[-400:] for w in ("no such", "none", "no number"))
        print(f"  {qid:16} label_correct={str(d['correct']):5} answer={d['answer'][:22]!r:24} "
              f"gold={d['gold']!r:6} gold_in_trace={gold_in} near_end={near_end}")

    print("\n" + "=" * 90)
    print("(B) DOUBT / METACOGNITION LOAD in the workspace (per prompt)")
    print("     load = mean over positions of [sum of doubt-concept weights at L20]")
    print("=" * 90)
    for qid in ORDER:
        d = load(qid)
        if not d:
            continue
        pos_doubt, pos_absurd, n = [], [], 0
        top_doubt = Counter()
        for p, r in d["positions"].items():
            l20 = r["by_layer"].get("20", [])
            dw = sum(w for c, w in l20 if c.lower() in DOUBT)
            aw = sum(w for c, w in l20 if c.lower() in ABSURD)
            pos_doubt.append(dw); pos_absurd.append(aw); n += 1
            for c, w in l20:
                if c.lower() in DOUBT:
                    top_doubt[c.lower()] += w
        md = sum(pos_doubt) / max(n, 1)
        ma = sum(pos_absurd) / max(n, 1)
        top = ", ".join(f"{c}({w:.1f})" for c, w in top_doubt.most_common(6))
        print(f"  {qid:16} doubt_load={md:.4f}  absurd_load={ma:.5f}  correct={d['correct']}")
        print(f"  {'':16} top doubt concepts: {top}")

    print("\n" + "=" * 90)
    print("(C) NO-A SPECIFICS — number-word timeline + self-aware moments")
    print("=" * 90)
    for qid in ("q1_no_a", "q1_plain"):
        d = load(qid)
        if not d:
            continue
        print(f"\n-- {qid} --")
        # self-aware / absurd concept appearances with context
        hits = []
        for p, l, rank, c, w in all_concepts(d):
            if c in ABSURD and w > 0.005:
                hits.append((p, l, rank, c, w))
        hits.sort(key=lambda x: -x[4])
        print(f"  self-aware/absurd concept hits (w>0.005): {len(hits)}")
        for p, l, rank, c, w in hits[:12]:
            around = d["trace"]
            tok = d["positions"][str(p)]["token"]
            print(f"    pos{p} L{l} rank{rank} {c!r} w={w:.3f} (token={tok!r})")
        # number-word density over the trace (are number-words dominating the workspace?)
        NUMS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                "eleven", "twelve", "thirteen", "twenty", "thirty", "forty", "fifty", "hundred",
                "eleven", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"}
        numpos = 0
        tot = 0
        for p, r in d["positions"].items():
            tot += 1
            if any(c.lower() in NUMS for c, w in r["by_layer"].get("20", [])[:5]):
                numpos += 1
        print(f"  positions where a number-word is in L20 top-5: {numpos}/{tot} "
              f"({100*numpos/max(tot,1):.0f}%)")


if __name__ == "__main__":
    main()
