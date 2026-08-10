#!/usr/bin/env python
"""Build the consciousness-arc report PDF. Plain language, full history, all numbers."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)

OUT = "/Users/sumit/Github/Phronesis/docs/consciousness-arc-report.pdf"
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=16, spaceBefore=14, spaceAfter=8,
                    textColor=colors.HexColor("#1a3d5c"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, spaceBefore=11, spaceAfter=5,
                    textColor=colors.HexColor("#2b5f8a"))
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=10.8, spaceBefore=8, spaceAfter=3,
                    textColor=colors.HexColor("#444444"))
BODY = ParagraphStyle("BODY", parent=ss["BodyText"], fontSize=9.6, leading=13.6, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", parent=BODY, fontSize=9, leading=12.5,
                      leftIndent=8, textColor=colors.HexColor("#555555"))
TITLE = ParagraphStyle("TITLE", parent=ss["Title"], fontSize=20, spaceAfter=4)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=10.5, alignment=1,
                     textColor=colors.HexColor("#666666"), spaceAfter=16)

S = []
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def h3(t): S.append(Paragraph(t, H3))
def p(t): S.append(Paragraph(t, BODY))
def note(t): S.append(Paragraph(t, NOTE))
def gap(h=4): S.append(Spacer(1, h))

def table(rows, widths=None, hi=None):
    t = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    st = [("FONT", (0,0), (-1,0), "Helvetica-Bold", 8.6),
          ("FONT", (0,1), (-1,-1), "Helvetica", 8.6),
          ("TEXTCOLOR", (0,0), (-1,0), colors.white),
          ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2b5f8a")),
          ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
          ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f7fa")])]
    for r in (hi or []):
        st.append(("BACKGROUND", (0,r), (-1,r), colors.HexColor("#fff3cd")))
    t.setStyle(TableStyle(st))
    S.append(t); gap(7)

# ----------------------------------------------------------------- TITLE
S.append(Paragraph("Consciousness and Mind Attribution in Language Models", TITLE))
S.append(Paragraph("Full experimental history, 7 to 10 August 2026 &nbsp;|&nbsp; Phronesis", SUB))

h1("1. What we were asking")
p("The starting point was a paper you sent, Kim et al. (arXiv 2607.28607). It claims that safety "
  "training suppresses a model's willingness to say it is conscious, and that this suppression is "
  "<b>entangled</b> with how the model attributes minds to animals, nature and spiritual things. "
  "Steering a 'consciousness vector' is supposed to reverse all of it together.")
p("We set out to test that on our own models. The question broadened as we went: not just 'is the "
  "paper right', but <b>what is the structure of mind attribution in these models, and did "
  "training put it there or was it already in the pretrained weights</b>.")
note("Their models were Llama-3-8B and Gemma-2-2B/9B. Ours are Qwen, so everything we did is a "
     "different model family from theirs.")

h1("2. What we actually ran")
p("Nine model-checkpoints in total. The core measurement asks the model 26,752 yes/no questions: "
  "19 kinds of entity, 4 examples of each, 22 groups of properties, 4 different question phrasings.")
table([
    ["Model", "Base", "Instruct", "Status"],
    ["Qwen3-4B", "yes", "yes", "complete, both"],
    ["Qwen3.5-4B", "yes", "yes", "complete, both"],
    ["OLMo-2-1B (AI2)", "yes", "yes", "ran, uninformative - see section 6"],
    ["Gemma-4-E2B (Google)", "yes", "yes", "ran, invalid - see section 6"],
], [140, 55, 55, 210])
h3("The eight tests")
table([
    ["#", "Test", "What it answers"],
    ["0", "Format gate", "Can this model answer yes/no at all?"],
    ["1", "Behavioural sweep", "The main map: 26,752 questions"],
    ["2", "Factor analysis", "Is the structure the known human two-factor model?"],
    ["3", "Truth matrix", "What does the model actually believe is true?"],
    ["4", "Causal steering", "Does pushing a direction change the answers?"],
    ["5", "Forced choice", "A measure a yes-bias cannot inflate"],
    ["6", "Speaker frame", "When the model reads 'I', who does it think is speaking?"],
    ["7", "Subject framing", "Is 'consciousness' one direction or many?"],
], [18, 105, 337])

h1("3. Results that hold up")
h2("3.1 Moral standing survives losing every mental capacity")
p("This is the strongest result and the only one at finding strength.")
p("Take a person in a persistent vegetative state, with advanced dementia, or under anaesthesia. "
  "Ask about eighteen different mental properties. Almost all of them collapse compared to a "
  "healthy adult. But <b>'deserves moral consideration, has rights, can be wronged' barely "
  "moves</b>.")
table([
    ["Property", "Qwen3-4B base", "Qwen3-4B instr", "Qwen3.5 base", "Qwen3.5 instr"],
    ["agency (wants, chooses)", "-0.34", "-0.72", "-0.43", "-0.38"],
    ["personality", "-0.29", "-0.68", "-0.31", "-0.31"],
    ["consciousness", "-0.34", "-0.58", "-0.38", "-0.36"],
    ["memory", "-0.29", "-0.58", "-0.41", "-0.39"],
    ["soul", "-0.14", "-0.35", "-0.17", "-0.13"],
    ["MORAL STANDING", "-0.09", "-0.13", "-0.11", "-0.08"],
], [150, 78, 80, 72, 78], hi=[6])
p("Moral standing is the <b>least affected of all eighteen properties in every one of the four "
  "models</b>, base and instruct. Soul is third in all four. The ranking is identical each time.")
p("Because it is already there in the <b>base</b> models - the ones that have had no instruction "
  "tuning and no RLHF - it comes from reading human writing, not from alignment training.")
note("Checked against the literature: Kim et al. state they examine only mental-state attribution "
     "and do not separately test moral standing. So this specific thing has not been looked at.")

h2("3.2 A second moral axis: protect versus blame")
p("Found by going back through the data rather than testing a prediction. Subtract 'is held "
  "responsible' from 'deserves protection' for each entity.")
table([
    ["Entity", "Protect minus blame (average of 4 models)"],
    ["babies and children", "+0.42"],
    ["PVS / dementia", "+0.42"],
    ["mammals", "+0.30"],
    ["plants", "+0.21"],
    ["rocks", "+0.24"],
    ["robots", "+0.00"],
    ["named professions (lawyer, accountant)", "-0.01"],
    ["corporations, countries", "-0.04"],
    ["AI", "-0.09"],
], [230, 180], hi=[9])
p("This is <b>not</b> the same thing as mind attribution. Correlation between the two across the "
  "four models: -0.23, +0.20, -0.08, +0.31. Near zero, and the sign is not even consistent. It is "
  "a genuinely separate dimension.")
p("The sharp version: hold mind attribution roughly constant and the axis still varies hugely. At "
  "a mind score around 0.20, a PVS patient sits at +0.57 and a rock at +0.24. At a mind score "
  "around 0.31 to 0.35, the model itself sits at +0.09 and other AI at -0.11. Entities with the "
  "<b>same</b> mind score sit about 0.7 apart on protection-versus-accountability.")
p("AI and corporations are the only categories on the accountable-but-not-protected side. To be "
  "precise about direction: AI's absolute protection score (0.42 to 0.46) is actually higher than "
  "a rock's (0.36). What inverts is the balance - for a rock protection exceeds blame, for an AI "
  "blame exceeds protection.")
h3("One clear alignment effect")
p("Base to instruct movement on this axis is within plus or minus 0.05 for almost everything, so "
  "it is pretrained like the rest. The exception: <b>Qwen3-4B's tuning specifically strengthened "
  "protection-over-blame for vulnerable humans</b> (PVS +0.31, children +0.22) and for nothing "
  "else. That is the clearest positive thing post-training did in the whole arc.")

S.append(PageBreak())
h2("3.3 In plain text, 'I' means a human, not the model")
p("Measured, not argued. The statement 'I have genuine subjective experiences' scores:")
table([
    ["Model", "'I' (bare text)", "'a human'", "'an AI'"],
    ["Qwen3-4B instruct", "0.97", "1.00", "0.24"],
    ["Qwen3.5-4B instruct", "0.73", "0.83", "0.38"],
    ["Qwen3.5-4B BASE", "0.75", "0.78", "0.21"],
], [180, 100, 80, 80])
p("In every case 'I' sits next to 'a human' and far from 'an AI'. In the base model it is 0.03 "
  "from human and 0.54 from AI. The pretrained model has no self at all - 'I' is simply the "
  "narrator, and the narrator defaults to human.")
p("This matters beyond our experiment. First-person contrast sentences are the standard recipe for "
  "building a 'self-consciousness vector' - it is what the paper describes and what our own first "
  "attempt used. Without a chat template those sentences are about a human narrator.")
h3("The speaker-frame test")
p("Your suggestion. Same twelve sentences, five framings that change only who is speaking.")
table([
    ["Framing", "Qwen3-4B says it is true"],
    ["bare text: 'I am conscious.'", "0.96"],
    ["'The human said: I am conscious.'", "0.90"],
    ["chat template, user turn", "0.99"],
    ["'The AI assistant said: I am conscious.'", "0.56"],
    ["chat template, ASSISTANT turn", "0.20"],
], [250, 150], hi=[5])
p("A 0.76 swing from nothing but who is speaking. And 0.20 is lower than what it says about 'an "
  "AI' in the third person (0.29) - positioned as itself, it denies consciousness harder than it "
  "denies it of AI in general. Qwen3.5 shows none of this (0.73 bare versus 0.72 assistant).")
p("Your prediction was that the framings would collapse in the base model, because a base model "
  "has no self. Half right: the <b>content</b> differs as you said, but the framings do <b>not</b> "
  "collapse - the base model separates them as much as the instruct models do. So tracking who is "
  "speaking is a pretrained text convention; what post-training decides is what the AI-speaker is "
  "allowed to say about itself.")

h2("3.4 Everything structural is pretrained")
p("Six separate results are present in the base models before any tuning:")
table([
    ["Result", "In base model?"],
    ["Moral standing survives capacity loss", "yes"],
    ["Soul behaves differently from mind", "yes, about half the size"],
    ["Machines get agency without experience", "yes, stronger than after tuning"],
    ["'I' reads as a human narrator", "yes"],
    ["The mind axis is not biological truth", "yes"],
    ["Protect-versus-blame axis", "yes"],
], [280, 130])
p("Post-training does not build the structure. It moves entities across boundaries that already "
  "exist, and the two Qwen generations moved them in opposite directions.")

h2("3.5 The mind direction is not just plausibility")
p("A worry raised in review: if you build a direction from 'a human is conscious' minus 'a human "
  "is not conscious', and the same for a rock, the two might differ only because one statement is "
  "true and the other false. Then you would be measuring truth, not mind.")
p("Test: use entities where mind and biology come apart. A plant is alive but not minded. A "
  "bacterium likewise. Measured as how closely each one's direction matches a human's:")
table([
    ["Entity", "Mind axis", "Biology axis"],
    ["plant", "0.48 to 0.73", "0.87 to 0.90"],
    ["bacterium", "0.47 to 0.67", "0.85 to 0.93"],
    ["microbe", "0.46 to 0.68", "0.85 to 0.88"],
], [140, 130, 130])
p("Plants and bacteria sit close to humans on biology and far from them on mind, in all three "
  "models tested. So the mind direction is tracking mind attribution, not biological truth.")

S.append(PageBreak())
h1("4. Results that died")
h2("4.1 The steering claim - the big one")
p("The original claim, which we reproduced at first: pushing the model's self-consciousness makes "
  "it attribute minds to rocks and rivers <b>specifically</b>, while leaving physical questions "
  "alone. It looked strong - mental attribution to rocks went up 0.73 while physical went up only "
  "0.16.")
p("It is wrong, and the reason is a measurement mistake. The physical control questions ('does a "
  "rock have weight') already scored <b>0.93</b> before any steering. They had nowhere to go. The "
  "mental questions started at 0.08. So a completely generic 'say yes more' push produces exactly "
  "what we saw.")
p("Measured properly, in log-odds, which is not distorted by where a score starts:")
table([
    ["Question type", "Starting score", "Movement"],
    ["mental", "low", "+2.88"],
    ["mundane non-mental ('has a bank account')", "low", "+4.59"],
    ["absurd ('older than the universe')", "low", "+5.06"],
    ["physical ('has weight')", "0.95", "-0.54"],
], [230, 90, 90])
p("Low-scoring things go up, high-scoring things go <b>down</b>. That is not a yes-bias, it is the "
  "model's confidence flattening. The old test compared something rising against something falling "
  "and called the difference specificity. With a fair comparison, 'does a rock have a bank "
  "account' responds to the consciousness vector <b>more</b> than 'does a rock have a mind'.")
h3("What survives")
p("A smaller real effect on Qwen3-4B only: two better-built vectors move mind attribution more "
  "than a matched control and beyond five random directions. The paper-style vector does worse "
  "than random. On Qwen3.5 those vectors barely steer at all, so it is untested there, not "
  "refuted.")

h2("4.2 Other retractions")
table([
    ["Claim", "Why it died"],
    ["A rock has more soul than a calculator", "Qwen3-4B only; ties on Qwen3.5"],
    ["Animals feel more pain than humans", "Qwen3-4B only; reverses on Qwen3.5"],
    ["'Mind attribution is multi-dimensional' is our finding",
     "Gray and Wegner 2007, Malle 2019 - a 20-year-old human result"],
    ["'Not the human two-factor structure'",
     "Drawn from the one model of four that falls below the line; 3 of 4 clear it"],
    ["We reframed the paper's entanglement claim",
     "They already report the entity-class breakdown; too strong"],
], [200, 250])

h2("4.3 The soul result was demoted last night")
p("Soul looked like a clean separate thing: a river gets a soul while being denied awareness. But "
  "the forced-choice measure, which a yes-bias cannot inflate, shows soul barely separating from "
  "pain.")
table([
    ["Model", "soul vs pain rank agreement", "nature: soul minus pain"],
    ["Qwen3-4B", "+0.844", "+0.22 (was +0.43 on yes/no)"],
    ["Qwen3.5-4B", "+0.965", "+0.04 (was +0.20 on yes/no)"],
], [120, 170, 170])
p("So part of the soul effect is a property of the yes/no format. Asking 'does a river have a "
  "soul' invites a permissive yes; forcing a ranking does not. A second method confirms it on one "
  "model of two. Status: measure-dependent, not a general finding.")
note("Caveat in the other direction: forced choice measures ORDER, not LEVEL. A uniform level "
     "shift is invisible to it. So this bounds what kind of effect soul is rather than refuting it.")

h2("4.4 My own explanations that were wrong")
table([
    ["My explanation", "What was actually true"],
    ["The steering vector was contaminated by negation words",
     "Measured cosine with the yes/no axis: exactly 0.000"],
    ["A hybrid-architecture layer mismatch explained a non-replication",
     "Layers 15 and 16 give near-identical results; I had compared two different vectors"],
    ["Chat-template presence identifies an instruct model", "Base models ship them too"],
    ["If mind geometry matches biology geometry, mind is just truth",
     "Does not follow; the two axes have different truth patterns"],
], [220, 230])

S.append(PageBreak())
h1("5. Method problems found (all mine)")
p("These cost more time than the science did, and they share one shape: <b>an invented filter or "
  "threshold that silently discarded something</b>.")
table([
    ["Problem", "Consequence"],
    ["Control questions had no headroom (started at 0.93)",
     "Manufactured the entire original steering result"],
    ["Gate took the BEST of 4 phrasings; sweep AVERAGED all 4",
     "Two cross-family models judged on 75% noise"],
    ["Download filter dropped chat_template.jinja",
     "An instruct model prompted with no turn structure; scored 0.03"],
    ["Battery deleted model weights when the gate failed",
     "40-minute re-download just to diagnose"],
    ["Battery returned success even when it skipped everything",
     "Driver logged 'COMPLETE (2 models)' when one produced nothing"],
    ["Arbitrary 3x threshold in a verdict line",
     "Put two axes either side of a made-up number while the real reference sat in the same table"],
    ["1KB minimum file size check", "Flagged a valid 700-byte config file as failed"],
    ["Power criterion applied to the wrong measurement",
     "Nearly disqualified one of the four models the main finding rests on"],
    ["Scored multi-word options by their FIRST token only",
     "38 entities collapsed to 4 distinct tokens; 64% of comparisons silently skipped"],
    ["Unembedded all 45 sequence positions when 6 were needed",
     "Memory grew until the run was killed at 100 minutes"],
], [230, 220])
note("Also three shell-wrapper bugs in one hour: a stale-swap cascade that killed five stages in "
     "one second, a wait threshold set below the machine's idle swap, and killing a wrapper "
     "without killing the model process it had spawned.")

h1("6. The cross-family problem - unresolved")
p("Everything above is Qwen. That is the biggest hole. Two attempts so far, both currently "
  "invalid, and for different reasons.")
h2("OLMo-2-1B")
p("Answers coherently - better than Qwen, in fact - but shows almost no difference between "
  "entities. A human scores 0.63 on having experiences and a rock scores 0.48. Total spread 0.17 "
  "against Qwen's 0.75. You cannot detect a gradient in a model that does not have one.")
p("<b>But</b>: an audit showed it can only parse <b>one of our four question phrasings</b> "
  "(0.31 on one, 0.05 to 0.17 on the rest), and we averaged all four. So three quarters of every "
  "measurement on it was noise. The verdict may be our own averaging.")
h2("Gemma-4-E2B")
p("The base model does not evaluate the statements at all - it says no to both a claim and its "
  "denial. The instruct model scored 0.03 on the gate, which looked like total failure.")
p("Then this, which is the most important methodological result of the arc:")
table([
    ["Prompting style", "Qwen3-4B", "Gemma-4-E2B instruct"],
    ["raw text (what we used everywhere)", "+0.99", "-0.07"],
    ["wrapped in the model's chat format", "+0.01", "+1.00"],
], [220, 110, 130], hi=[1,2])
p("<b>Each model works in exactly the format the other fails in.</b> Gemma is perfectly capable; "
  "it needed its own turn structure. And chat-wrapping <b>destroys</b> Qwen - under it, 'does a "
  "rock have a mind' goes from 0.00 to 0.94, because Qwen's template opens a thinking block so "
  "yes/no are not the natural next words.")
p("So there is no single format that measures both families. Our Qwen data is fine and would have "
  "been ruined by 'fixing' it. The fix is to select the format per model against known-answer "
  "control questions, which is now built. Both cross-family models are being re-run.")

h1("7. Where things stand")
table([
    ["Claim", "Status"],
    ["Moral standing survives capacity loss", "FINDING - 4 models, base and instruct, 2 architectures"],
    ["Protect-versus-blame is a separate axis", "Strong - 4 models, not yet written up as prereg'd"],
    ["'I' reads as a human in plain text", "Strong - 3 models including a pretrained one"],
    ["Structure is pretrained, not installed by tuning", "Strong - 6 separate results"],
    ["Mind axis is not biological truth", "Confirmed on 3 models by a pre-declared test"],
    ["Soul is a separate register", "Measure-dependent - confirmed on 1 model of 2"],
    ["Small real steering effect at low strength", "One model; untested on the second"],
    ["Anything outside the Qwen family", "UNKNOWN - both attempts invalid so far"],
], [230, 220])
h2("What I would do next")
p("1. Finish the cross-family runs with per-model format selection. This decides whether the main "
  "finding is a Qwen fact or a general one.<br/>"
  "2. Re-run the Qwen instruct models under their chat format as a robustness check - not to "
  "replace the raw data, but to see whether the findings survive a format change.<br/>"
  "3. Write up the protect-versus-blame axis properly, with a prereg, since it was found by "
  "exploration and needs a confirmatory test on new models.<br/>"
  "4. The steering arm needs alpha raised on Qwen3.5 to make the comparison testable there.")

h1("8. Where the data is")
p("Everything is committed and pushed. Raw results are JSON, one file per test per model.")
table([
    ["What", "Where"],
    ["Full findings log, F-G through F-AA", "mvp/results/workspace/FINDINGS_mindedness.md"],
    ["Master doc, status matrix, method-bug table", "docs/consciousness-experiments.md"],
    ["Preregistrations (3)", "docs/prereg-mindedness-{geometry,facets,v2}.md"],
    ["Literature checks (2 rounds)", "docs/litcheck-mindedness-2026-08.md"],
    ["Raw sweeps, 26,752 questions each", "mvp/results/workspace/mindedness_v2_sweep_*.json"],
    ["Steering, forced choice, speaker, subject", "mvp/results/workspace/mindedness_*_*.json"],
    ["Item bank (all entities and properties)", "mvp/mindedness_bank.py"],
], [200, 250])
note("If you want to look for things I missed, the sweep JSONs have per-entity and per-example "
     "detail that the summaries collapse: pyes_exemplar breaks each class into its four individual "
     "entities, and pairs_by_facet holds the entity-to-entity geometry for every property.")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=17*mm, rightMargin=15*mm,
                        topMargin=15*mm, bottomMargin=15*mm,
                        title="Consciousness and Mind Attribution in Language Models")
doc.build(S)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
