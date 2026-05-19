# Phronesis Publication Playbook

**Purpose**: a self-contained guide to publishing Phronesis writeups for someone who has never written research papers / LessWrong posts / arXiv preprints before. Compiled 2026-05-18 from a literature search across LW/AF interpretability posts and arXiv interpretability papers.

**How to use this doc**: read once end-to-end before writing your first post. Refer back to specific sections while drafting. The exemplars in §A.1 and §A.2 are the most important part — *read them* before you write, not after.

---

## A. Read these first (genre exemplars)

### A.1 LessWrong / Alignment Forum exemplars (immediate target — F121 post)

Read these seven posts in this order before drafting:

| # | Post | Author(s) | Words | What to steal |
|---|------|-----------|-------|--------------|
| 1 | [Refusal in LLMs is mediated by a single direction](https://www.lesswrong.com/posts/jGuXSZgv6qfdhMCuJ/refusal-in-llms-is-mediated-by-a-single-direction) | Arditi, Obeso, Aaquib111, Wes Gurnee, Neel Nanda | ~10,000 | Three-sentence bold-italics opening claim. "We do not claim X about Y" limitations phrasing. |
| 2 | [Steering Llama 2 with Contrastive Activation Additions](https://www.lesswrong.com/posts/v7f8ayBxLhmMFRzpa/steering-llama-2-with-contrastive-activation-additions) | Panickssery, Schulz, NickGabs, Meg, evhub, TurnTrout | ~4,500 | Inline verbatim model outputs as block quotes. |
| 3 | [Comparing the effectiveness of top-down and bottom-up activation steering](https://www.lesswrong.com/posts/boB3hJiZijxM3J6Ed/comparing-the-effectiveness-of-top-down-and-bottom-up) | Ana Kapros | ~2,200 | **Closest length and affiliation match to your post.** Academic structure (Intro / Related Work / Methods / Results / Discussion / Limitations / Future Work). |
| 4 | [Activation space interpretability may be doomed](https://www.lesswrong.com/posts/gYfpPbww3wQRaxAFD/activation-space-interpretability-may-be-doomed) | Chughtai & Bushnaq (Apollo) | ~3,500 | Bounded-negative architectural claim. Calibrated hedging ("may be," "seems likely," "probably"). |
| 5 | [My Failed AI Safety Research Projects (Q1/Q2 2025)](https://www.lesswrong.com/posts/kiCZzHDkRtupek2mc/my-failed-ai-safety-research-projects-q1-q2-2025) | Adam Newgas | ~1,200 | Tone for independent / bounded-negative writeups. |
| 6 | [SAE features for refusal and sycophancy steering vectors](https://www.lesswrong.com/posts/k8bBx4HcTF9iyikma/sae-features-for-refusal-and-sycophancy-steering-vectors) | neverix, Kharlapenko, Conmy, Nanda | ~4,500 | Three-bullet TL;DR. Explicit "unlikely to continue pursuing this direction" closing. |
| 7 | [Why I'm Moving from Mechanistic to Prosaic Interpretability](https://www.lesswrong.com/posts/Ypkx5GyhwxNLRGiWo/why-i-m-moving-from-mechanistic-to-prosaic-interpretability) | Daniel Tan | ~2,800 | Solo voice. Honesty about negative updates without sounding defensive. |

**Recommended model for the F121 post**: hybrid of Kapros's skeleton (academic-style sections), Arditi's bolded opening claim, CAA's side-by-side verbatim-sample tables, neverix's closing register.

### A.2 arXiv / longform exemplars (longer-term — Phronesis paper)

| # | Paper | Pages | What to steal |
|---|------|------:|--------------|
| 1 | [Panickssery et al. — Steering Llama 2 via CAA](https://arxiv.org/abs/2312.06681) (ACL 2024) | ~20 | Method figure on page 1. Per-behavior result subsections. Explicit "Effects on general capabilities" doubling as limitations check. |
| 2 | [Arditi et al. — Refusal direction](https://arxiv.org/abs/2406.11717) (NeurIPS 2024) | ~25 | One-sentence load-bearing claim in abstract with explicit N (13 models, up to 72B). Symmetric ablation+addition test layout. |
| 3 | [Tan & Chanin et al. — Steering vector reliability](https://arxiv.org/abs/2407.12404) (ICLR 2025) | ~18 | Two-axis structure: in-distribution variability + OOD brittleness as separable sub-findings. **Closest structural shape to a Phronesis paper.** |
| 4 | [Wu et al. — AxBench](https://arxiv.org/abs/2501.17148) (ICML 2025 spotlight) | ~30 | How to put a negative-result punchline in the title without sounding sour. Trinity of baselines (prompting / finetuning / diff-in-means). |
| 5 | [Korznikov et al. — Sanity Checks for SAEs](https://arxiv.org/abs/2602.14111) (Feb 2026) | ~22 | Paired SAE-vs-random-baseline table pattern (0.87 vs 0.90, 0.69 vs 0.72, 0.73 vs 0.72). Directly analogous to F122. |
| 6 | [Karvonen et al. — Rogue Scalpel](https://arxiv.org/abs/2509.22067) (Feb 2026) | ~15 | Recent, tight, single-architectural-claim writeup with strong null-control discipline. **15-page tier you should target for Scope A.** |
| 7 | [Templeton et al. — Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) | ~80 page-equiv | Canonical transformer-circuits-style longform. Section landmarks, interactive widgets, mid-document Limitations. Use only if you go Scope C. |

Also worth reading (April 2026, most current Anthropic-style longform on the inspiration paper for Phronesis): [Emotion Concepts and their Function in a Large Language Model](https://transformer-circuits.pub/2026/emotions/index.html).

---

## B. LessWrong/AF structural conventions (for the F121 post)

### B.1 Front matter

- **Title**: short, claim-shaped. Not a question. *"Residual-stream additive steering is one-sided: a reciprocal test on two open-weight LLMs"* — good. *"Investigating activation steering"* — bad.
- **Linkpost note (optional)**: if you also have an arXiv version or are mirroring from a personal blog, immediately under the title write `Linkpost for [URL]`. The CAA post does this.
- **Epistemic status (optional but recommended for bounded results)**: first italicized line. For your post:
  > *Epistemic status: empirical, N=2 models, prompts and code released. The architectural claim (one-sided additive steering) is what I'm most confident in; the feature-semantic comparisons (humility vs doubt vs commit) are weaker.*

### B.2 TL;DR

- Always present, immediately after epistemic status.
- For a multi-finding post, use bullets (3-5, one sentence each).
- For a single-claim post, use a prose paragraph leading with a bolded claim.

### B.3 Sections

The Kapros / academic skeleton (recommended for the F121 post):

1. **Introduction / Motivation** (~200 words) — what you tested, why
2. **Background** (~200 words) — CAA, refusal direction, what "reciprocal test" means
3. **Methods** (~250 words) — models, prompts, layers, α grid, judge
4. **Results** (~600 words) — the six-corner table with verbatim quotes
5. **Discussion** (~250 words) — what the asymmetry implies architecturally
6. **Reconciliation with prior work** (~200 words) — Arditi (ablation ≠ addition), Anthropic Emotions (calm-suppresses-blackmail)
7. **Limitations** (~150 words)
8. **What would falsify this** (~100 words) — explicit list
9. **Replication recipe** (~100 words)
10. **About / acknowledgements / links** (~50 words) — independent researcher, code link, data link

### B.4 Mechanics

- **Footnotes**: use LW's native superscript (`[^1]`). Target 3-6.
- **Citations**: inline as "Arditi et al. (2024) showed..." for primary references; footnote-style for tangents.
- **Math**: KaTeX renders cleanly. Use sparingly. The steering formula `h' = h + αv` displayed once is enough.
- **Tables**: Markdown tables OK. For asymmetry claims, a side-by-side `α=+k` / `α=−k` two-column table is the gold standard.
- **Images**: PNG. Host on LW directly (the editor uploads). Never link to imgur — gets rate-limited.
- **Verbatim model outputs**: fenced quote blocks, or inside the side-by-side table.

### B.5 Cross-posting to AF

When you submit to LW, the editor has a checkbox to also submit to the Alignment Forum. AF moderators promote selected posts to AF; if yours is promoted, it gets a small "AI Alignment Forum" link in the post metadata. You don't write "Crossposted to AF" in the body.

### B.6 Tags

Attach: **Activation Engineering**, **Interpretability (ML & AI)**, **AI**. Optionally Mechanistic Interpretability.

### B.7 After posting

- Reply in-thread to substantive comments within 2-3 days.
- For load-bearing corrections, append `**Edit YYYY-MM-DD:**` at the bottom of the post explaining the change; do not silently rewrite the body.
- Typos: fix silently.
- Typical karma trajectory for a competent first post in this genre: 5-15 in hour 0-24, 30-80 within a week if it catches.

---

## C. Tone — concrete patterns

### Good

- "We find that..." (Arditi). Not "We discovered," "We prove," "We demonstrate."
- "may be," "seems likely," "probably" — calibrated hedging.
- Naming what you didn't test: *"I do not claim that the asymmetry generalizes to larger models or to non-residual-stream interventions."*
- Explicit hyperparameter and prompt disclosure.
- For inconclusive arms: *"unlikely to continue pursuing this direction"* (neverix et al.) or *"this is the operating point we recommend; α=4 has a residual coherence issue"* — concretely bounded.

### Bad

- "We show" / "We prove" for an N=2 result.
- "Surprisingly," "Remarkably," "We were shocked to find" — press-release tells.
- "Has implications for alignment" without spelling out which claim, experiment, model class.
- Anthropomorphizing the vector ("the humility direction wants to...").
- Defensive preemption ("I know this is small-N, but..."). Better: just disclose N and move on.

### Burying the lede

By the end of paragraph 1, the reader should know (a) what you tested, (b) on what models, (c) what the main finding is, (d) what it does NOT show. Arditi's three-sentence bolded opener is the canonical move.

### The "what would falsify this" section

Less common in interpretability than in alignment-strategy posts, but increasingly expected. For F121:

> This claim would be falsified by: (a) a model where positive α suppresses generation symmetrically with negative α; (b) any of the three feature semantics showing two-sided suppression on either model; (c) the asymmetry disappearing under a different residual-stream layer choice.

---

## D. Anti-patterns to avoid

1. **Underspecified prompts**. Never write "we tested on humility prompts" without linking the exact prompt set. Single most common reason an interp post gets dismissed.
2. **Missing model IDs**. `Qwen/Qwen3-4B`, `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` — give the exact HF model IDs and the chat template you used.
3. **No code link**. Disqualifying in 2026 for this genre. Even a messy notebook beats nothing.
4. **"We discovered..." without showing the work**. Show the α-sweep, the raw generations, one figure.
5. **Hidden hyperparameter sensitivity**. If a claim depends on a specific layer or α, say so explicitly and show the sweep across neighbours.
6. **Asymmetric reporting of pos vs neg α**. Since one-sidedness IS the F121 claim, quote verbatim samples from *both* signs.
7. **Speculation creep**. Quarantine speculation in a clearly labeled subsection. Don't let it leak into the abstract.
8. **Anthropomorphic feature names without scare quotes**. First mention: `"humility"`, `"doubt"`, `"commit"`. After that you can drop the quotes.
9. **Overfit lit review**. Genre expects 4-8 cited prior works, not 30. Arditi + CAA + ActAdd + 1-2 recent (Tan / AxBench / Korznikov) is plenty.
10. **Overclaiming**. Truthful framing: "across 5 open-weight model families at the 2–8B scale, steering failed to install virtues in a way distinguishable from random-direction control." Don't write "we showed virtues cannot be steered."

---

## E. Independent-researcher mechanics

### Author bio / affiliation

- LW: minimal. Don't open with "As an independent researcher with no formal affiliation..." — it preemptively flags a concern most readers don't have. If you want to signal it, do it in one sentence at the bottom: *"I'm an independent researcher; this work was done on my own hardware, no funding or affiliation. Code and data: [link]."*
- arXiv: list **"Independent"** (just that, no city, no lab name). Standard for arXiv interpretability papers from unaffiliated authors.

### Reproducibility checklist (must-have)

- GitHub URL with commit hash matching the published version
- HuggingFace dataset/model cards for any released artifacts (corpus, steering vectors, generations)
- Exact HF model IDs and chat template
- Exact prompts (in repo or appendix)
- Exact layers and α values swept
- Seeds (or "deterministic, greedy decoding" stated)
- Opus judge prompt template (for Phronesis specifically — judge prompts are part of the artifact)

The de-facto bar is the [NeurIPS paper checklist](https://neurips.cc/public/guides/PaperChecklist). Satisfy it even if not submitting to NeurIPS.

### Post-publication propagation

1. Post arXiv link with a 3-tweet thread (claim+number / key figure / code link). Tag relevant interp researchers — at least one will boost if the claim is sharp.
2. Mirror to Bluesky.
3. Time the arXiv drop and the LW post within 24 hours of each other for compounding signal.

### Workshop submissions

- Most NeurIPS / ICLR / ICML workshops accept any email; no academic affiliation needed.
- Endorsement is an *arXiv-specific* mechanism, not a workshop requirement.
- Watch dual-submission policy: if your arXiv preprint predates the workshop CFP by >4 months, some workshops will reject for "not novel." Time the workshop submission within 3 months of arXiv.

### arXiv first-submission mechanics

- You need **endorsement** for cs.LG / cs.CL. Per the January 2026 policy update, institutional email is no longer sufficient.
- Path: pick 3-5 papers you cite, find their "endorsers" link on the arXiv abstract page, email 2-3 of those authors with abstract + PDF link + one paragraph asking for endorsement.
- After endorsement: submit via arxiv.org/submit. Moderation typically 1-3 business days.
- LaTeX template: [`kourgeorge/arxiv-style`](https://github.com/kourgeorge/arxiv-style) (preprint-styled, not conference-styled). [Overleaf version](https://www.overleaf.com/latex/templates/style-and-template-for-preprints-arxiv-bio-arxiv/fxsnsrzpnvwc).

---

## F. Long-term: which scope, which venue, which timeline

Three scopes for the eventual Phronesis paper (separate from the LW post):

| Scope | Length | Contents | Venue | Time to write | Risk |
|---|------:|---|---|---|---|
| A | 8-12 pp | F121 + F122 + cube corners + Arditi/Emotions reconciliation only | arXiv → workshop | 4-7 weeks | Safest but feels thin to reviewers asking "so what about installation?" |
| B | 15-25 pp | F111→F120 negative-result chain + F121/F122 + FM-X taxonomy | arXiv standalone + workshop | 8-14 weeks | **Recommended.** Hardest length to land but lets the FM-X taxonomy live as its own contribution. |
| C | 30-50 pp | Full project incl. (a+tools) experiment, all 5 mechanism families, full FM-X | Self-hosted HTML + arXiv companion | 4-6 months | Reward only if (a+tools) lands positive. Build incrementally toward this from B. |

**Recommended path**: Scope B, arXiv-first with parallel HTML longform on a personal site (Goodfire-style, not transformer-circuits.pub — the latter is effectively closed to outside contributors). Write before (a+tools) lands — the negative-result framing is timely *now*; if (a+tools) flips it, v2 update or a follow-up.

**Workshop target**: NeurIPS 2026 Mech Interp workshop or ICLR 2027 SoLaR, depending on timing.

**Suggested timeline (10 weeks total)**:
- Weeks 1-2: outline + figures
- Weeks 3-6: draft
- Weeks 7-8: endorser outreach + revision
- Week 9: final polish
- Week 10: arXiv + LW + HTML companion go live within 24 hours

---

## G. Anthropic skills (none paper-specific)

I checked. There is no Anthropic skill specifically for paper writing. The closest are:

- **`anthropic-skills:docx`** — for producing Word documents. Not relevant for arXiv (LaTeX) or LW (Markdown).
- **`anthropic-skills:pdf`** — for producing PDFs. Useful for the final preprint export, but you'll be generating PDFs from LaTeX anyway.
- **`anthropic-skills:pptx`** — for slide decks (workshop talks).
- **`anthropic-skills:skill-creator`** — for building your own skill. Overkill for one-off writeups.

What replaces a skill is this playbook + the F121 draft + the genre exemplars. The structure is in §B; the tone is in §C; the do-nots are in §D.

---

## H. Process: how to actually write your first LessWrong post

A practical sequence so you don't stall:

1. **Read the seven LW exemplars in §A.1** (~2 hours). Take notes on: what their TL;DR looks like; how they format the verbatim quotes; how the limitations section reads.

2. **Read your existing draft** at `docs/drafts/F121-steering-one-sidedness.md` end-to-end. Mark anything that doesn't sound like the genre.

3. **Revise structure to match Kapros + Arditi + CAA hybrid** (per §A.1 recommendation):
   - Add an epistemic-status line at the top
   - Convert the TL;DR to a prose paragraph leading with a bolded claim (Arditi style)
   - Add an explicit "What would falsify this" section before the closing
   - Add an "About / Acknowledgements / Links" footer

4. **Verify every quote, model ID, and verdict count** against raw data one more time. (This was done on 2026-05-18; re-verify before posting if time has passed.)

5. **Build the artifacts**:
   - GitHub repo with code + commit hash
   - HuggingFace dataset card for the 2,914 generations (or just the F121/F122-relevant subset)
   - One figure: the six-corner table rendered as a graphic
   - Exact prompt text in a repo file or appendix

6. **Sit on the draft for 48 hours.** Re-read with the genre exemplars open in another tab.

7. **Post to LW.** Check the "submit to Alignment Forum" box.

8. **Within 24 hours**: 3-tweet thread on Twitter/Bluesky tagging relevant interp researchers.

9. **Within 72 hours**: reply to every substantive comment. Append `**Edit:**` at the bottom for any load-bearing correction.

10. **One week later**: post-mortem. What landed, what didn't, what to do differently for F122 or the longer paper.

---

## Cross-references

- `docs/drafts/F121-steering-one-sidedness.md` — first writeup target
- `docs/writeup-plan.md` — overall writeup queue
- `docs/references.md` — running bibliography (most of the prior art for the F121 post is already here)
- `docs/findings.md` — source of truth for empirical claims to cite
