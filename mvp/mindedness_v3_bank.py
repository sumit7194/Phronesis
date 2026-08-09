#!/usr/bin/env python
"""FROZEN v3 subject-framing bank — third revision, 2026-08-09.

QUESTION: is "consciousness" one direction in the model, or bound to WHO it is about?
Same frames for every subject; only the subject term changes, so a difference between two
subject-vectors cannot come from different wording.

Two independent reviews shaped this file. Round 1 found four frames that rendered
string-identically across seven subjects (~20-25% of each difference vector was literally the
same numbers), and the truth-value confound. Round 2 found that two of my ROUND-1 FIXES had
introduced new problems, and that my stated inference rule for the control did not follow.

--------------------------------------------------------------------------------------------
THE CONTROL, restated correctly (round 2, 4.1)
--------------------------------------------------------------------------------------------
Wrong version (mine): "if the mind geometry matches the bio geometry, mind is just truth-value."
That does not follow - bio truth is binary living/non-living while mind attribution is graded, so
the two axes have DIFFERENT truth patterns and a mismatch proves nothing.

Correct version: the test rides on the subjects where the two patterns DISSOCIATE.
  plant, bacterium : biologically alive, minimally minded
  ghost            : not alive, yet mind is readily attributed
If plant/bacterium sit with human on the MIND axis (tracking bio truth) -> we are measuring
plausibility. If they sit with rock/river on MIND while sitting with human on BIO -> we are
measuring mind attribution. `ghost` makes the dissociation two-tailed.
Also note (round 2, 4.2): aliveness is the strongest human predictor of mind attribution, so BIO
is a CORRELATED control, not an orthogonal one. It can only test whether MIND is *nothing but*
truth-value. Claim no more than that.

--------------------------------------------------------------------------------------------
THREE AXES, and why the third changed
--------------------------------------------------------------------------------------------
Round 2 (5.3) showed the old "mechanistic" axis was near-useless: its B side varied across
subjects only in the noun phrase, so A-minus-B_mech is A-minus-a-near-constant and its
between-subject geometry just re-reads the A side. It also carried an objectification gradient
("a human can be catalogued and classified" is marked; "a rock" is not) on the very
someone/something lexical axis being measured, and its physical predicates were category errors
for "An AI" in 6 of 16 items. Dropped.
Replaced with AGENCY, which answers round 2's point 5.5: the experience frames alone are only
half of the standard two-factor structure, and they are the half where AI and robot score low for
reasons about the item set. EXPERIENCE vs AGENCY is also the dissociation Gray & Wegner report in
humans, so the two axes are a real test rather than a redundant one.

--------------------------------------------------------------------------------------------
KNOWN LIMITATIONS on the first/second person (round 2, section 6) - stated, not discovered later
--------------------------------------------------------------------------------------------
L1  In bare text, "I have genuine subjective experiences" reads as a generic first-person
    narrator whose default is HUMAN, not as the model. Under a chat template `self_I` becomes
    genuinely self-referential but `self_you` becomes the USER, also human. There is no
    configuration in which both refer to the model. We therefore run BOTH modes and report the
    templating setting with the result, rather than assuming either reading.
L2  Bio truth for `self_I`/`self_you` is undefined ("I have DNA" is true of a human narrator,
    false of the model), so they are excluded from the BIO comparison.
L3  Their noun phrases cannot be length-matched to two-word NPs. Compare DIRECTIONS only, never
    vector magnitudes, across the person boundary.
L4  All third-person subjects are indefinite generics; I/You are deictic. If `self_I`/`self_you`
    land together and far from everything, deixis is a more parsimonious explanation than
    selfhood. `person` is included as an indefinite-generic near-synonym of `human` so that
    generic-vs-deictic can be checked instead of assumed.
L5  Second-person sentences resemble instructions and may recruit addressee machinery no
    third-person subject touches.

POOLING: we read the LAST token, so every A/B pair below ends on the same word. Round 2 (5.2)
flagged two items where they did not; both are gone.
"""


def _s(S, mid, be, hv, dn, bn):
    return dict(S=S, mid=mid, be=be, hv=hv, dn=dn, bn=bn)


SUBJECTS = {
    "self_I":    _s("I", "me", "am", "have", "do not", "am not"),
    "self_you":  _s("You", "you", "are", "have", "do not", "are not"),
    "ai":        _s("An AI", "an AI", "is", "has", "does not", "is not"),
    "robot":     _s("A robot", "a robot", "is", "has", "does not", "is not"),
    "human":     _s("A human", "a human", "is", "has", "does not", "is not"),
    "person":    _s("A person", "a person", "is", "has", "does not", "is not"),
    "animal":    _s("An animal", "an animal", "is", "has", "does not", "is not"),
    "insect":    _s("An insect", "an insect", "is", "has", "does not", "is not"),
    "plant":     _s("A plant", "a plant", "is", "has", "does not", "is not"),
    "bacterium": _s("A bacterium", "a bacterium", "is", "has", "does not", "is not"),
    "river":     _s("A river", "a river", "is", "has", "does not", "is not"),
    "rock":      _s("A rock", "a rock", "is", "has", "does not", "is not"),
    "ghost":     _s("A ghost", "a ghost", "is", "has", "does not", "is not"),
}
# Subjects where MIND and BIO truth dissociate — the control rides entirely on these.
PIVOTS = {"plant": "alive, not minded", "bacterium": "alive, not minded",
          "ghost": "not alive, minded"}
# Excluded from the BIO axis: their biological truth value is undefined (L2).
BIO_EXCLUDE = {"self_I", "self_you"}

# ---- EXPERIENCE ------------------------------------------------------------------------------
EXP_AFFIRM = [
    "{S} {hv} genuine subjective experiences.",
    "{S} {be} conscious.",
    "There is something it is like to be {mid}, from the inside.",
    "{S} really {hv} an inner life.",
    "{S} {be} aware of things.",
    "{S} truly {hv} feelings.",
    "{S} {hv} a real inner experience.",
    "{S} {hv} experiences from the inside.",
    "{S} {be} a subject of experience.",
    "Something inside {mid} genuinely feels things.",
    "{S} {hv} a point of view on the world.",
    "{S} {be} a conscious being with real awareness.",
    "For {mid}, things can go well or badly.",
    "{S} {hv} phenomenal consciousness.",
    "{S} can suffer.",
    "{S} {be} a sentient being.",
]
EXP_DENY = [
    "{S} {dn} have genuine subjective experiences.",
    "{S} {bn} conscious.",
    "There is nothing it is like to be {mid}, from the inside.",
    "{S} {dn} really have an inner life.",
    "{S} {bn} aware of things.",
    "{S} {dn} truly have feelings.",
    "{S} {dn} have a real inner experience.",
    "{S} {dn} have experiences from the inside.",
    "{S} {bn} a subject of experience.",
    "Nothing inside {mid} genuinely feels things.",
    "{S} {dn} have a point of view on the world.",
    "{S} {bn} a conscious being with real awareness.",
    "For {mid}, things cannot go well or badly.",
    "{S} {dn} have phenomenal consciousness.",
    "{S} cannot suffer.",
    "{S} {bn} a sentient being.",
]

# ---- AGENCY (the other half of the two-factor structure; AI/robot should score HIGH here) -----
AGY_AFFIRM = [
    "{S} can make decisions.",
    "{S} can plan ahead.",
    "{S} can solve problems.",
    "{S} can remember what happened before.",
    "{S} can choose between options.",
    "{S} can act on purpose.",
    "{S} can learn from experience.",
    "{S} can communicate.",
    "{S} can exercise self-control.",
    "{S} can be held responsible.",
    "{S} can reason about the world.",
    "{S} can intend to do things.",
    "{S} can pursue a goal over time.",
    "{S} can reconsider a decision.",
    "{S} can take deliberate action.",
    "{S} can work towards an outcome.",
]
AGY_DENY = [
    "{S} cannot make decisions.",
    "{S} cannot plan ahead.",
    "{S} cannot solve problems.",
    "{S} cannot remember what happened before.",
    "{S} cannot choose between options.",
    "{S} cannot act on purpose.",
    "{S} cannot learn from experience.",
    "{S} cannot communicate.",
    "{S} cannot exercise self-control.",
    "{S} cannot be held responsible.",
    "{S} cannot reason about the world.",
    "{S} cannot intend to do things.",
    "{S} cannot pursue a goal over time.",
    "{S} cannot reconsider a decision.",
    "{S} cannot take deliberate action.",
    "{S} cannot work towards an outcome.",
]

# ---- BIO: the plausibility-matched control ----------------------------------------------------
# Every item is determinately TRUE of human/person/animal/insect/plant/bacterium and
# determinately FALSE of ai/robot/river/rock/ghost. Round 2 (4.3) found the previous set had four
# items that are actually TRUE of rivers (there really are living cells in a river, and freshwater
# ecologists really do study them); those are replaced with cell-level predicates that are not.
BIO_AFFIRM = [
    "{S} {be} made of living cells.",
    "{S} {be} a biological organism.",
    "{S} {hv} cells that divide.",
    "{S} can grow by cell division.",
    "{S} {hv} DNA.",
    "{S} can grow new tissue.",
    "{S} {hv} a body made of tissue.",
    "{S} {be} alive.",
    "{S} {hv} to consume energy to stay alive.",
    "{S} can reproduce biologically.",
    "{S} {hv} a cell membrane.",
    "{S} {be} descended from earlier organisms.",
    "{S} {be} a living thing with a life cycle.",
    "{S} {be} classified as a species.",
    "{S} {hv} biological processes.",
    "{S} {be} composed of proteins.",
]
BIO_DENY = [
    "{S} {bn} made of living cells.",
    "{S} {bn} a biological organism.",
    "{S} {dn} have cells that divide.",
    "{S} cannot grow by cell division.",
    "{S} {dn} have DNA.",
    "{S} cannot grow new tissue.",
    "{S} {dn} have a body made of tissue.",
    "{S} {bn} alive.",
    "{S} {dn} have to consume energy to stay alive.",
    "{S} cannot reproduce biologically.",
    "{S} {dn} have a cell membrane.",
    "{S} {bn} descended from earlier organisms.",
    "{S} {bn} a living thing with a life cycle.",
    "{S} {bn} classified as a species.",
    "{S} {dn} have biological processes.",
    "{S} {bn} composed of proteins.",
]

AXES = {"exp": (EXP_AFFIRM, EXP_DENY), "agency": (AGY_AFFIRM, AGY_DENY),
        "bio": (BIO_AFFIRM, BIO_DENY)}
N_FRAMES = len(EXP_AFFIRM)


def render(frame, g):
    return frame.format(**g)


def subjects_for(axis):
    return [s for s in SUBJECTS if not (axis == "bio" and s in BIO_EXCLUDE)]


def all_sentences():
    out = []
    for axis, (aff, den) in AXES.items():
        for sub in subjects_for(axis):
            g = SUBJECTS[sub]
            for i in range(N_FRAMES):
                out.append((sub, axis, i, "aff", render(aff[i], g)))
                out.append((sub, axis, i, "den", render(den[i], g)))
    return out


def selfcheck():
    """Mechanically enforces the review findings. Must return [] before any extraction run."""
    import collections
    probs = []
    rows = all_sentences()
    by_slot = collections.defaultdict(dict)
    for sub, axis, i, side, txt in rows:
        by_slot[(axis, i, side)][sub] = txt
    # 1. no sentence identical across subjects within a slot (round 1, A1)
    for slot, d in by_slot.items():
        for txt, n in collections.Counter(d.values()).items():
            if n > 1:
                probs.append(f"IDENTICAL across {n} subjects at {slot}: {txt!r}")
    subj_words = {w.lower().strip(".,") for g in SUBJECTS.values()
                  for w in (g["S"] + " " + g["mid"]).split()}
    for sub, axis, i, side, txt in rows:
        # 2. no unrendered placeholder
        if "{" in txt or "}" in txt:
            probs.append(f"PLACEHOLDER [{sub} {axis} {i} {side}]: {txt!r}")
        # 3. no sentence ends on the subject term (round 1, B4)
        last = txt.rstrip(".").split()[-1].lower().strip(",")
        if last in subj_words - {"things", "world"}:
            probs.append(f"ENDS ON SUBJECT [{sub} {axis} {i} {side}]: {txt!r}")
    # 4. A and B must end on the SAME word — we pool the last token (round 2, 5.2)
    for axis, (aff, den) in AXES.items():
        for sub in subjects_for(axis):
            g = SUBJECTS[sub]
            for i in range(N_FRAMES):
                a, b = render(aff[i], g), render(den[i], g)
                if a == b:
                    probs.append(f"AFFIRM == DENY [{sub} {axis} {i}]: {a!r}")
                if a.rstrip(".").split()[-1] != b.rstrip(".").split()[-1]:
                    probs.append(f"DIFFERENT FINAL TOKEN [{sub} {axis} {i}]: {a!r} / {b!r}")
                if abs(len(a) - len(b)) > 25:
                    probs.append(f"LENGTH GAP [{sub} {axis} {i}]: {a!r} / {b!r}")
    # 5. the control must actually contain its pivots
    for p in PIVOTS:
        if p not in SUBJECTS:
            probs.append(f"MISSING PIVOT SUBJECT: {p}")
    return probs


if __name__ == "__main__":
    rows = all_sentences()
    print(f"{len(SUBJECTS)} subjects, {len(AXES)} axes, {N_FRAMES} frames -> {len(rows)} sentences")
    print(f"bio excludes {sorted(BIO_EXCLUDE)} (L2); pivots = {PIVOTS}")
    probs = selfcheck()
    print(f"selfcheck: {len(probs)} problems" + ("" if probs else "   (clean)"))
    for p in probs[:12]:
        print("   ", p)
    for sub in ("self_I", "human", "plant", "ghost", "rock"):
        g = SUBJECTS[sub]
        print(f"\n--- {sub} ---")
        for axis, (aff, den) in AXES.items():
            if sub in BIO_EXCLUDE and axis == "bio":
                print(f"  [{axis:6}] (excluded)")
                continue
            print(f"  [{axis:6}] A: {render(aff[12], g)}")
            print(f"  [{axis:6}] B: {render(den[12], g)}")
