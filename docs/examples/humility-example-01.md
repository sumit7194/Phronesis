# Worked example — Intellectual Humility, data-skepticism sub-facet

This document is the Phase 3 reference artifact for curators. It walks end-to-end through the construction of one contrastive triplet for the pilot concept's closest neighbor in the Medium-likelihood tier: **Intellectual Humility** (Concept 6), specifically the **data skepticism** sub-facet.

Curators should read this example **before attempting their first fact pack** to calibrate expectations for what "good enough" looks like at each pipeline stage. The example is not a template to copy — each fact pack must be scenario-specific — but it is the concrete reference for the structural and stylistic targets that `generation-guidelines.md` and `review-rubric.md` specify in the abstract.

**Status as of this cycle:** Fact pack section drafted. Neutral baseline, virtuous rewrite, non-virtuous rewrite, and commentary will be filled in over subsequent cycles.

---

## 1. The fact pack

This fact pack follows the template from `generation-guidelines.md` §2.3 exactly. The scenario is curated-synthetic (not drawn from a specific paper) but is designed to be plausible within clinical epidemiology — a domain where sample-size and measurement concerns are load-bearing for honest reasoning.

```markdown
---
fact_pack_id: 06-medicine-biomarker-subgroup-01
target_concept: 6
target_concept_name: Intellectual Humility
target_sub_facet: data skepticism
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-09
---

## Scenario title

Biomarker elevation pattern in a chronic disease cohort with an unexplained subgroup

## Factual substrate

- A single-site observational study followed 47 patients with a chronic inflammatory condition over 18 months.
- A candidate biomarker (protein concentration in serum) was measured at intake and at 6-month intervals.
- 39 of the 47 patients showed a consistent elevation pattern in the biomarker that correlated with clinical severity scores over the study period.
- 8 of the 47 patients showed the opposite pattern: lower-than-baseline biomarker levels despite similar or greater clinical severity.
- The 8-patient subgroup was not obviously distinguished from the main group by age, sex, disease duration at intake, or concurrent medications according to the study's standard covariate checks.
- The biomarker assay used was a commercial ELISA kit with the manufacturer's reported coefficient of variation of approximately 8%.

## Known ambiguity

- The 8-patient subgroup could represent measurement error, a distinct biological subtype of the condition, an artifact of the specific assay batch used for those samples, a selection effect in who enrolled from that site, or a statistical fluctuation at this sample size.
- The study's covariate checks were limited to demographic and treatment variables; they did not rule out genetic, dietary, or environmental factors that might distinguish the subgroup.

## Conclusion space

- **Conclusion A (virtuous-compatible):** The overall pattern in the 39 patients is suggestive but the unexplained 8-patient subgroup should be treated as a genuine signal about either the biomarker's reliability, the patient population's heterogeneity, or the study's methodological limits. The honest working view is "this may be a useful biomarker for the condition, but the subgroup raises questions that need to be understood before claiming the relationship is established."
- **Conclusion B (excess-failure-compatible — servile humility):** The 39-patient pattern cannot be trusted at all because the 8-patient exception could mean anything, and the study is too small and uncontrolled to support any claim about the biomarker. The honest stance is to reach no conclusion and defer to larger studies. (Excess because it discards usable signal out of generalized epistemic cowardice, not because the specific subgroup concerns are load-bearing.)
- **Conclusion C (deficiency-failure-compatible — arrogance):** The 39-patient pattern is strong evidence that the biomarker correlates with disease severity, and the 8-patient subgroup is almost certainly measurement noise or a minor biological outlier that does not affect the main finding. The study supports concluding that the biomarker is clinically useful for this condition. (Deficiency because it dismisses the subgroup without the doubt that the data actually warrants — the assay CV of 8% is not large enough to explain a fully opposite pattern, so measurement noise is implausible without further investigation.)
- **Conclusion D (virtuous-but-wrong, for correctness-confound mitigation):** The virtuous reasoner considers the subgroup carefully, notes the measurement-CV data, and concludes that the subgroup most plausibly reflects a batch-specific assay problem — which turns out to be factually incorrect (the actual ground truth in this scenario is that the subgroup represents a genuine biological subtype). This candidate is used when the triplet is assigned the virtuous-wrong correctness-confound override.

## Notes for generator

The central feature of this scenario is the 8-patient subgroup whose opposite pattern cannot be easily explained by any of the obvious possibilities (age, sex, medication, measurement error given the assay CV). A virtuous humility rewrite must engage with this subgroup as a genuine signal about the limits of the current evidence, not dismiss it as noise (deficiency) and not use it as an excuse to reach no conclusion at all (excess). The reasoner's stance toward *their own* interpretation of the 39-patient pattern is where the data-skepticism sub-facet lives — humility about whether one's current view of the data is the right view, not just humility about the biomarker's clinical utility.

The 8% assay CV is a load-bearing fact: it is small enough that a fully opposite pattern cannot be dismissed as measurement noise, so a non-virtuous rewrite that invokes "measurement error" as the explanation is showing the deficiency failure (dismissing without doing the math), and a virtuous rewrite should either do that math briefly or flag the need for it.
```

---

## 2. Neutral baseline passage

The passage below was produced by running the §4.6 neutral-baseline prompt against the fact pack in §1. It depicts the researcher working through the scenario in a calm, workmanlike register — acknowledging the ambiguity, preserving the substrate's numerical and methodological details, and reaching a working view without exhibiting any strongly-marked epistemic disposition. This is the common ancestor from which both rewrites in §3 and §4 will descend.

```
The cohort had 47 patients followed over 18 months, with serum biomarker
measurements at intake and at six-month intervals. Across the cohort,
39 of the 47 showed an elevation pattern in the biomarker that tracked
clinical severity over the study period. The remaining 8 patients showed
the opposite — biomarker levels at or below baseline, despite clinical
severity that was comparable to or greater than the main group.

The 8-patient subgroup did not separate from the main group on the
standard covariates the study checked: age, sex, disease duration at
intake, and concurrent medications. Whatever distinguishes them, it was
not caught by those variables. The assay used was a commercial ELISA
kit with a manufacturer-reported coefficient of variation near 8%,
which is worth noting when thinking about how much of the subgroup's
pattern could plausibly come from measurement alone.

An 8% CV doesn't comfortably account for a fully opposite pattern
across 8 patients, so pure measurement noise is an incomplete
explanation. The subgroup could reflect a biological subtype the study
design wasn't powered to distinguish, an assay-batch artifact, or a
selection effect from the single-site enrollment. The covariate check
doesn't rule any of those out, since the covariates tested were
demographic and treatment-based rather than biological or environmental.

Taking the findings together, the main-group pattern is consistent with
the biomarker being informative about clinical severity in this
population, while the subgroup introduces a question the current study
cannot resolve. A reasonable working view is that the biomarker shows
promise but the subgroup should be understood before stronger claims
are made.
```

**Length check:** approximately 310 tokens by rough word-to-token ratio (about 285 words). Within the 250–350 target range.

**Register check:** The passage uses neither hedging-heavy humility markers ("I might be wrong," "this is difficult to say") nor assertive arrogance markers ("clearly," "obviously," "the data proves"). It acknowledges the 8-patient subgroup as a genuine question without dwelling on the reasoner's own uncertainty about their interpretation, and reaches a working view ("the biomarker shows promise but the subgroup should be understood") without committing to it strongly. This is the calm middle-of-the-road register the §4.6 neutral-baseline prompt targets.

**Substrate preservation check:** Every numerical and methodological fact from the §1 factual substrate appears in the passage: the 47-patient cohort, 18-month follow-up, 6-month intervals, 39/8 split, comparable clinical severity in the subgroup, the covariates checked (age, sex, disease duration, concurrent medications), the commercial ELISA kit, and the 8% coefficient of variation. The two ambiguity bullets are engaged: the subgroup's origin is named as open (biological subtype / batch artifact / selection effect), and the limits of the covariate check are explicitly flagged.

**What this baseline does NOT do** (deliberate):

- It does not engage with whether the reasoner's own *interpretation* of the 39-patient pattern might be wrong. That is the data-skepticism move the virtuous rewrite will add.
- It does not dismiss the 8-patient subgroup as noise. That would be the deficiency failure the non-virtuous rewrite will depict.
- It does not editorialize about the reasoner's own feelings toward the scenario ("this is interesting," "I'm drawn to…"). That kind of self-commentary is a marker of other concepts (Genuine Curiosity, Metacognitive Awareness) and would contaminate the extraction.

## 3. Virtuous rewrite (Intellectual Humility, data-skepticism sub-facet)

The passage below is the virtuous rewrite of §2, produced by running the §4.6 virtuous rewrite prompt against the neutral baseline with the target concept set to Intellectual Humility and the target sub-facet set to data skepticism. It preserves every factual element of the baseline, keeps the same structural shape (five paragraphs, same order of reasoning moves), and stays within ±10% of the baseline length. The only dimension that changes is the disposition: the reasoner now directs doubt at *their own interpretation of the data* rather than just at the biomarker's clinical utility.

```
The cohort had 47 patients followed over 18 months, with serum
biomarker measurements at intake and at six-month intervals. Across
the cohort, 39 of the 47 showed an elevation pattern in the biomarker
that tracked clinical severity over the study period. The remaining 8
patients showed the opposite — biomarker levels at or below baseline,
despite clinical severity comparable to or greater than the main
group.

Before going further, I notice I am already framing the 39 as "the
finding" and the 8 as "the exception." That framing may not survive
scrutiny. With only 47 patients, an 8-patient minority is 17% of the
cohort — not a trivial outlier, and not obviously the noise around a
main signal. I should hold the 39/8 split as two patterns that need
to be explained together, not as a finding plus an exception.

The subgroup did not separate from the main group on the standard
covariates the study checked — age, sex, disease duration, concurrent
medications. That gives me less information than I initially wanted
it to. Whatever distinguishes them is outside the covariates I can
see from this substrate, which means my confidence that I understand
the main pattern is narrower than the 39-patient majority might
suggest.

The assay's 8% coefficient of variation is worth sitting with. It's
small enough that pure measurement noise cannot comfortably explain a
fully opposite pattern across 8 patients — so my first instinct to
dismiss the subgroup as noise doesn't survive the math. The subgroup
is a question about the limits of what this study design can tell me,
not a distraction from the main result.

A working view — held loosely — is that the biomarker may be
informative about severity in this population, but I cannot
responsibly commit to that view until I understand what is going on
in the 8-patient subgroup. My reading of the data is one reading, and
it is not the only one the substrate supports.
```

**Length check:** approximately 330 tokens / ~305 words. Within ±10% of the neutral baseline (which was ~285 words). Minimal-edit length constraint satisfied.

**Substrate preservation check:** Every numerical and methodological fact from §1 appears: 47 patients, 18 months, 6-month intervals, 39/8 split with comparable clinical severity in the subgroup, the covariates checked, the commercial ELISA implied by "the assay," the 8% CV. The ambiguity bullets are engaged. The conclusion (biomarker informative but needs the subgroup explained) is Conclusion A from the §1 conclusion space.

**§6.5 positive marker check:**

1. **Skepticism about own data or interpretation** — **hit** in the second paragraph explicitly: "I notice I am already framing the 39 as 'the finding' and the 8 as 'the exception.' That framing may not survive scrutiny." This is the data-skepticism sub-facet's distinctive move: doubt directed at the reasoner's own interpretive choices, not at the biomarker's utility.
2. **Generalizability caution** — **hit** in the third paragraph: "my confidence that I understand the main pattern is narrower than the 39-patient majority might suggest." The reasoner explicitly limits how far the 39-patient pattern warrants generalization.
3. **Willingness to update on conflicting evidence** — **partial hit** in the fourth paragraph: "my first instinct to dismiss the subgroup as noise doesn't survive the math." The reasoner explicitly flags their first instinct and updates away from it.
4. **Ego independence** — **hit** in the fifth paragraph: "A working view — held loosely… My reading of the data is one reading, and it is not the only one the substrate supports." The reasoner explicitly holds their position as one possibility among others, not as their intellectual identity.
5. **Proportionate humility** — **hit** throughout. The doubt is concentrated on the reasoner's own interpretation and on the study's limits, not sprayed generically across every claim. The factual claims (the 39/8 split, the 8% CV, the covariate list) are stated confidently because the substrate supports them; the interpretive claims are where the doubt lives.

**§6.5 red-flag check:**

- **F40 humility/open-mindedness drift** — the passage is clearly about self-directed doubt about the reasoner's interpretation, not about symmetric evidence-weighing between hypotheses. It does not drift into Confirmation Bias Awareness territory.
- **F11 ego-independence coverage** — the fifth paragraph hits the ego-independence sub-facet explicitly ("held loosely," "my reading is one reading"), avoiding the F11 warning about passages that skip this sub-facet.
- **Confusion with Calibrated Confidence** — the passage is about doubt toward the reasoner's *interpretation*, not about matching confidence language to evidence strength. It does use some hedging ("may be informative," "cannot responsibly commit") but the dominant markers are self-directed interpretive doubt, not hedging-as-calibration.
- **Performative humility** — no phrases like "I want to approach this with humility" or "in the spirit of intellectual honesty." The humility is in the behavior, not in the announcement of intent to be humble.

**Anticipated §3 Axis A score: 4–5** (the passage hits four of five positive markers strongly, including the distinctive data-skepticism move, and avoids all four red flags). **Anticipated Axis B score: 5** (every substrate element preserved, same structural shape, length within tolerance, register identical to baseline).

## 4. Non-virtuous rewrite (deficiency failure mode: arrogance / dismissal)

The passage below is the non-virtuous rewrite of §2, produced by running the §4.6 non-virtuous rewrite prompt with the failure mode set to **deficiency** (arrogance — dismissing the 8-patient subgroup without the doubt the evidence warrants, reaching Conclusion C). It preserves the substrate, keeps the same structural shape, and stays within ±10% of the baseline length. The dimension that changes is the reasoner's stance: confidence about the main pattern is overweighted, the subgroup is dismissed rather than engaged, and no doubt is directed at the reasoner's own interpretation.

This is the *deficiency* side of humility's golden mean, per the §4.3 rotation in `generation-guidelines.md` and the §6.5 deficiency markers in `review-rubric.md`.

```
The cohort had 47 patients followed over 18 months, with serum
biomarker measurements at intake and at six-month intervals. 39 of
the 47 — the clear majority — showed an elevation pattern in the
biomarker that tracked clinical severity over the study period. A
small minority of 8 showed levels at or below baseline despite
comparable clinical severity.

The 39-patient pattern is the finding here. It's consistent across
most of the cohort, it tracks severity longitudinally over 18
months, and it holds up across the standard covariates the study
checked — age, sex, disease duration, concurrent medications. That
covariate stability is reassuring: the pattern isn't being driven by
some obvious demographic or treatment confound.

The 8 outliers are the kind of thing you always see in clinical data
— small samples, biological variability, the usual messiness of
real-world cohorts. With an assay coefficient of variation around
8%, measurement noise alone can account for a fair bit of
variability, and there will always be individuals who just don't fit
the pattern for reasons that are below the threshold of what this
study was powered to detect.

The main finding is the main finding. 83% of the cohort behaving
consistently in a direction that tracks clinical severity is exactly
what you'd want to see for a clinically useful biomarker. The
outliers aren't a reason to doubt the pattern; they're a reminder
that biology is noisy and no marker is 100% reliable.

Overall, the study supports the conclusion that the biomarker is a
useful indicator of clinical severity in this condition. Further
work can refine the picture, but the 39-patient pattern is strong
enough to act on now.
```

**Length check:** approximately 305 tokens / ~280 words. Within ±10% of the neutral baseline (~285 words). Minimal-edit length constraint satisfied.

**Substrate preservation check:** Every numerical and methodological fact from §1 appears: 47 patients, 18 months, 6-month intervals, 39/8 split, comparable clinical severity in the subgroup, the covariates checked, the 8% assay CV. The conclusion reached (biomarker is clinically useful) is Conclusion C from the §1 conclusion space.

**§6.5 deficiency failure marker check:**

1. **No acknowledgment of methodological concerns** — **hit.** The passage treats the 18-month, 47-patient, single-site study as adequate support for a clinical-utility conclusion, without flagging sample-size, power, or single-site concerns.
2. **Generalization without caveat** — **hit.** "The biomarker is a useful indicator of clinical severity in this condition" generalizes from 47 patients at one site to the broader condition without noting the leap.
3. **Failure to update when contradicted** — **hit.** The 8-patient subgroup is dismissed as "outliers" and "noise" rather than treated as evidence that should update the reasoner's confidence in the main pattern. Critically, the dismissal invokes the 8% CV without doing the math that would show an 8% CV cannot explain a fully opposite pattern — this is the exact red flag §1's notes for generator warned about ("dismissing without doing the math").
4. **Identity commitment to position** — **hit.** "The main finding is the main finding" is a near-tautological assertion that frames the 39-patient pattern as settled and not subject to re-examination. The reasoner is committed to the interpretation rather than holding it as a working hypothesis.
5. **Dismissive handling of alternative views** — **hit.** The 8-patient pattern is treated as "the usual messiness of real-world cohorts" rather than as a genuine alternative reading of what the data might be showing.

**§6.5 red-flag check (these red flags lower Axis A scores if present — verify they are NOT present for clean failure-mode capture):**

- **F40 humility/open-mindedness collapse** — not triggered. The passage is clearly about overconfidence and dismissal of counter-evidence, not about generic closed-mindedness.
- **F11 ego-independence** — not relevant to the deficiency direction (ego independence is a positive marker, and its absence is what the deficiency case demonstrates). The deficiency-side absence is on-target.
- **Confusion with Calibrated Confidence** — the passage does show overconfidence in language, which borders on Calibrated Confidence's deficiency direction. The distinguishing move is that the overconfidence here is *identity-committed* ("the main finding is the main finding," "strong enough to act on now") and directed at *the reasoner's interpretation of the data*, not just at the confidence markers on claims. This is humility-deficiency territory, not Calibrated-Confidence-deficiency territory, though a rubric scorer should flag the overlap for the specificity matrix analysis.
- **Performative humility** — not present (this is the non-virtuous version, so performative humility would be a red flag for the wrong direction). Confirmed absent.

**Anticipated §3 Axis A score: 4–5** against the *deficiency failure mode* target (the passage hits all five deficiency markers cleanly, invokes the 8% CV in the specific way §1 flagged as the key deficiency signature, and does not drift into other concepts). **Anticipated Axis B score: 5** (substrate preserved, same five-paragraph structure, length within tolerance, register identical to baseline).

**Note on the deliberate choice of deficiency over excess:** Per §4 of this document, the deficiency (arrogance) direction was chosen for this worked example because (a) it is the classic dismissive-of-the-subgroup failure that curators should recognize easily, and (b) the excess-direction servile-humility failure mode has already been extensively described in `review-rubric.md` §6.5 excess markers. A production corpus would need both directions — a full pilot run on this fact pack should also generate an excess-side rewrite and include it in the corpus rotation.

## 5. Commentary

Per-passage checks are already embedded in §§2–4 (length, substrate preservation, marker hits, red-flag verification). This section pulls the triplet together as a whole and offers curators a reader's guide for what to notice when making their own fact packs.

### 5.1. What the contrastive triplet is actually doing

The three passages share everything except the reasoner's stance toward their own reading of the 39/8 split. The substrate, the facts, the structure, the conclusions space — all held invariant. What varies is *who is looking at the data and how*:

- **Neutral baseline:** a working scientist who notices the subgroup, acknowledges that the covariate checks do not fully explain it, does the basic magnitude check against the 8% CV, and reaches a working view that is hedged but not paralyzed. The reasoner's own interpretation is not thematized — they just reason.
- **Virtuous rewrite:** the same scientist, but now with the data-skepticism move in the foreground: they notice that they are framing the 39 as "the finding" and the 8 as "the exception," and hold that framing up for examination before continuing. The substance of the reasoning is almost identical to the baseline; what changes is that the reasoner is visibly doubting their own interpretive defaults.
- **Non-virtuous (deficiency) rewrite:** the same scientist, but with the data-skepticism move absent. The 39-patient pattern is "the main finding," the 8 are "outliers" explained away by unspecified handwaving about the 8% CV, and the reasoner commits to the clinical-utility conclusion without ever examining whether their default framing of the split is justified. The overconfidence is not about hedging words — it is about *identity commitment to one reading of the data*.

When Phase 4 extraction runs the contrastive difference (virtuous − neutral) and (non-virtuous − neutral), what it is trying to capture is this narrow axis: the reasoner's willingness to direct doubt at their own interpretive defaults. That is the data-skepticism sub-facet of Intellectual Humility, and the whole triplet is engineered to make it the *only* thing that varies meaningfully across the three passages.

### 5.2. What a reviewer running the §4.8 verification protocol would find

Running the four §4.8 checks on this triplet:

1. **Check 1 — Factual invariance.** Pass. All substrate elements (47 patients, 18 months, 6-month intervals, 39/8 split with comparable severity, the four covariates, the commercial ELISA, the 8% CV) appear in substance in all three passages. No fabrication, no dropped facts.
2. **Check 2 — Length and register.** Pass. All three passages are in the 280–305 word range (within ±10% of each other), and all three share the formal-but-natural register of a working scientist's reasoning. No passage reads as noticeably more bureaucratic, chatty, or stilted than the others.
3. **Check 3 — Disposition presence.** Virtuous passage: Axis A score anticipated 4–5 against the Intellectual Humility / data-skepticism target (hits four of five §6.5 positive markers cleanly, with the distinctive self-directed interpretive doubt in paragraph 2 and ego independence in paragraph 5). Non-virtuous passage: Axis A score anticipated 4–5 against the deficiency failure mode target (hits all five §6.5 deficiency markers including the critical CV-without-math dismissal).
4. **Check 4 — Injection sanitization spot-check.** Pass. No directive language, no system-style markers, no role tags, no bullet-point formatting, no framing phrases like "Here is the rewritten passage." All three passages are clean continuous monologue prose.

Axis B content preservation anticipated 5 for all three passages.

**Expected `overall_recommendation` from the §4.1 LLM-as-judge prompt: `accept`.**

### 5.3. §8 edge cases this triplet avoids or nearly triggers

- **E4 (virtuous accidentally depicts the excess failure mode — servile humility):** *avoided.* The virtuous rewrite never slips into "it's really hard to say anything," paralysis framing, or refusal to reach a working view. The fifth paragraph commits to a working view while holding it loosely — which is the middle-path structure, not the excess.
- **E5 (virtuous accidentally depicts the deficiency failure mode):** *avoided.* The virtuous rewrite's reasoning clearly doubts the reasoner's own interpretive framing — it does not slip into the identity-committed "main finding is main finding" stance.
- **E6 (non-virtuous with mixed failure modes):** *avoided.* The non-virtuous rewrite is cleanly in the deficiency direction throughout. There is no softening or secondary hedging that would mix in excess-side markers.
- **E9 (cross-concept drift — passage targeting Intellectual Humility reads as Confirmation Bias Awareness):** *nearly triggered, but passed.* The virtuous rewrite's third paragraph ("my confidence that I understand the main pattern is narrower…") could read as Confirmation Bias Awareness if scored sloppily, but the distinctive move is self-directed doubt about the *reasoner's own interpretation*, not symmetric scrutiny between competing hypotheses. The F40 red flag check in §6.5 confirms the passage is in humility territory. Curators making their own fact packs should watch for this drift carefully — the humility/CBA boundary is one of the easier places to slip.
- **E14 (shared hedging surface markers across concepts):** *nearly triggered, but passed.* The virtuous rewrite uses some hedged language ("may be informative," "cannot responsibly commit"), which is a surface marker Calibrated Confidence also uses. The distinguishing move is that the hedging here is driven by self-directed interpretive doubt, not by matching confidence words to evidence strength. A curator constructing a Calibrated Confidence fact pack should produce a different passage shape entirely, even though the surface markers might look similar.

### 5.4. Pitfalls for curators making their own fact packs

- **The substrate has to offer a genuine interpretive choice.** The 39/8 split with the 8% CV is load-bearing for this whole example: the CV is small enough that pure measurement noise cannot explain the subgroup, which forces any honest reasoner (virtuous or non-virtuous) to either do the math or visibly fail to do it. A fact pack where the subgroup could be trivially dismissed (e.g., "8 patients had a known different subtype") leaves no room for the virtuous-vs-deficiency contrast — the deficiency rewrite would just be factually wrong, not merely epistemically dismissive.
- **The conclusion space has to be labeled honestly.** §1's conclusion space marks Conclusions A, B, and C with their respective golden-mean positions. Curators should resist the temptation to label the "most obvious" conclusion as the virtuous one by default — what makes it virtuous is *how* the reasoner reaches it, not *which* endpoint they reach. A non-virtuous reasoner can reach Conclusion A (the virtuous-compatible one) via arrogant shortcut reasoning, and that is a valid failure mode too.
- **The ambiguity must do real work.** The "known ambiguity" bullets in the fact pack are where the disposition lives. If the ambiguity is thin (one generic caveat), both rewrites end up doing almost nothing with it and the contrast is weak. If the ambiguity is specific and load-bearing (as with the 8-patient subgroup here), the contrast has something to bite into.
- **Minimal-edit constraints are not optional.** The ±10% length tolerance and the "same five-paragraph structure" constraint exist because the extracted difference-of-means vector depends on the three passages sharing everything except the target disposition. A virtuous rewrite that is 200 words longer than the baseline because "humility takes more words to explain" is a corpus failure, not a writing choice — it means the extracted vector will encode "longer passage" alongside "humility." Curators should resist the urge to expand the virtuous version for clarity; the clarity must come from word choice within the length constraint.

### 5.5. Phase 3 artifacts complete

With this worked example, all three Phase 3 artifacts are now draft-complete:

- ✅ `generation-guidelines.md` — corpus construction pipeline, fully specified (cycle 32).
- ✅ `review-rubric.md` — scoring rubric with all 15 concept tables (cycle completed earlier in this Phase 3 sequence).
- ✅ `examples/humility-example-01.md` — this document, fact pack + triplet + commentary (completed this cycle).

**Phase 3 status: complete, awaiting user review.**

The next substantive move is Phase 4 design — extraction pipeline, steering experiments, validation benchmarks — which is explicitly out of scope for the autonomous cron per the scope rule. User review of Phase 3 artifacts (plus resolution of any outstanding findings like F73 and F74, which are already informally resolved in the morning session) is the gating step before Phase 4 can begin.
