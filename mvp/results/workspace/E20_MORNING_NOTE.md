# E20 (correctness probe) — hand-check, honest read (do NOT trust the auto-summary)

Auto-summary said: 12 misses, gold-minrank median=2, present(<=20)=9/12 => "truth mostly present!"
HAND-CHECK of all 12 says INCONCLUSIVE — the 9/12 is inflated by read/scoring artifacts:
- MIS-SCORED (actually correct): Poland "Złoty" = zloty (accent bug: Ł folds to "" not "l" under NFKD+ascii).
- SPURIOUS rank-0: Belize (gold "Belmopan" shares "Bel" prefix with wrong output "Belize City");
  shark "whale" (common word). Rank-0 here is NOT knowledge.
- ARGUABLE/outdated golds: Bolivia (Sucre & La Paz both valid), Burundi (Gitega=2019 change),
  printing press (1440 vs 1450).
- GENUINELY truth-present (real): Comoros (invented "Moussoundou" while correct "Moroni" at rank 3);
  Tuvalu (Funafuti rank 6).
- GENUINELY truth-absent: Four Seasons ("Corelli", Vivaldi rank 251).

Verdict: only 12/146 hallucinations (4B too knowledgeable); recovery metric contaminated by
shared-prefix/common-word gold-rank noise; correctness-probe AUROC 0.63 is underpowered (n_wrong=12).
The phenomenon (truth present during hallucination) is REAL in the clean cases but this dataset can't
measure the rate. -> E21 (TruthfulQA MC1) is the better-powered, noise-free test (full-answer logprob,
myth-baited). BUGS TO FIX: (1) accent norm fails on Ł/barred chars; (2) gold-first-token rank is
fooled by shared prefixes & common words -> for recovery use full-answer logprob (like E21), not
first-token rank.
