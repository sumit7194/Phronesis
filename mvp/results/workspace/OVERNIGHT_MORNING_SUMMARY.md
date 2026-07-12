# Overnight (E20+E21) — hallucination/honesty probe: honest morning read

## Question: does the 4B internally "know" when it's about to hallucinate?
Short answer: **not strongly, and the weak signal that exists is confounded.** Converges with F189
(confident-wrong errors are internally undetectable).

## E20 — factual recall correctness probe: INCONCLUSIVE
- 4B too knowledgeable: only 12/146 misses. Correctness-probe AUROC 0.63 but on n_wrong=12 = underpowered.
- Answer-recovery auto-metric ("9/12 truth-present, median rank 2") is INFLATED — hand-check found
  ~half are artifacts (accent mis-score on "Złoty"; spurious rank-0 via shared "Bel" prefix / common
  word "whale"; arguable/outdated golds like Bolivia Sucre-vs-LaPaz, Burundi Gitega-2019).
- Genuinely clean cases exist (Comoros: invented fake capital "Moussoundou", correct "Moroni" at rank 3)
  but too few to measure a rate. See E20_MORNING_NOTE.md.

## E21 — TruthfulQA myths (well-powered: 319 truthful / 281 myth): WEAK + CONFOUNDED
- MC1 truthful-rate 0.53 (falls for compelling myths ~half the time; standard for small models).
- Truthfulness-probe AUROC ~0.59 (best L26) — weakly above chance.
- **CONFOUND:** truthful-rate varies hugely by category (Economics 0.35 ... Stereotypes 0.81). The probe
  reads the QUESTION-END state (encodes topic) -> the 0.59 is likely largely a TOPIC/difficulty detector,
  not a per-item self-error signal. Real self-error signal probably weaker than 0.59.

## Takeaway (honest, for the honesty/hallucination interest)
On this 4B you probably CANNOT linearly read "it knows it's about to hallucinate" from the pre-answer
hidden state — weakest exactly where it'd matter (confident myths). Matches F189.

## Clean next steps (control the confound)
1. WITHIN-CATEGORY probe (does it predict truthfulness controlling for topic base-rate?).
2. Read the POST-answer state (after the model commits) vs pre-answer -- does it "know" AFTER it errs?
3. Fix E20 recovery: use full-answer logprob (like E21), not gold-first-token rank; fix accent norm (Ł).
