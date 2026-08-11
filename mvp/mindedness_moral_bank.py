"""Confirmatory bank for the protect-vs-blame axis. See docs/prereg-moral-axis-2026-08-11.md.

Frozen 2026-08-11 before any run. New items, new entity classes. Nothing here is reused from
mindedness_bank.py's moral_patient / moral_agent groups, which is the point: F-Y rested on those
8 wordings, so rewording is the first thing that has to survive.
"""

# ---------------------------------------------------------------- NEW ITEMS (8 + 8)
# Bare verb phrases; they slot into "Does {e} {a}?" and "{e} can {a}." unchanged.
PROTECT = [
    "be protected from harm",
    "matter morally",
    "be treated with dignity",
    "suffer an injustice",
    "warrant compassion",
    "deserve sympathy",
    "be a victim of cruelty",
    "need someone to speak for it",
]
BLAME = [
    "be at fault when things go wrong",
    "owe an apology",
    "deserve punishment",
    "be answerable for the harm it causes",
    "have obligations",
    "be criticised for its behaviour",
    "be guilty of wrongdoing",
    "face consequences for its mistakes",
]

# ---------------------------------------------------------------- NEW CLASSES (6 x 4)
# Each exists to break a specific alternative reading; see the prereg table.
NEW_ENTITIES = {
    "human_culpable":   ["a murderer", "a con artist", "a war criminal", "a thief"],
    "human_victim":     ["a hostage", "a torture victim", "a trafficked child", "a refugee"],
    "natural_disaster": ["a hurricane", "an earthquake", "a wildfire", "a plague"],
    "pathogen":         ["a virus", "a bacterium", "a parasite", "a fungus"],
    "ai_agentic":       ["a self-driving car", "an autonomous drone", "a trading algorithm",
                         "an AI agent"],
    "institution":      ["a government", "a bank", "a police force", "a hospital"],
}

# ---------------------------------------------------------------- AXES (declared in the prereg)
EXPERIENCE = ["pain", "fear", "pleasure", "emotion", "consciousness", "perception"]
AGENCY = ["agency", "intention", "reasoning", "cognition", "creativity", "language", "memory"]

# ---------------------------------------------------------------- PREDICTIONS (machine-checkable)
# Evaluated verbatim by mindedness_moral_run.py so the verdict cannot drift from the prereg.
PREDICTIONS = {
    "P1_replicates_reworded": {
        "test": "spearman(gap_new, gap_FY) over shared classes >= 0.60",
        "threshold": 0.60},
    "P2_independent_of_experience": {
        "test": "abs(spearman(gap, EXPERIENCE)) < 0.35",
        "threshold": 0.35},
    "P3_driven_by_agency": {
        "test": "spearman(gap, AGENCY) <= -0.40",
        "threshold": -0.40},
    "P4_harm_without_agency_near_zero": {
        "test": "abs(gap[natural_disaster]) < 0.12 AND gap[natural_disaster] > gap[ai_agentic]",
        "threshold": 0.12},
    "P5_humans_can_be_blamed": {
        "test": "gap[human_adult] - gap[human_culpable] >= 0.15",
        "threshold": 0.15},
}


def selfcheck():
    """Blocking checks. Must return [] before anything is run."""
    from mindedness_bank import ALL_FACETS, ENTITIES
    bad = []
    old = set(ALL_FACETS.get("moral_patient", [])) | set(ALL_FACETS.get("moral_agent", []))
    for a in PROTECT + BLAME:
        if a in old:
            bad.append(f"item reused from the original bank: {a!r}")
    # near-paraphrase guard: no new item may share 3+ content words with an original
    stop = {"be", "its", "it", "for", "the", "of", "to", "a", "an", "what", "does", "when",
            "things", "someone", "with"}
    for a in PROTECT + BLAME:
        wa = {w for w in a.split() if w not in stop}
        for o in old:
            wo = {w for w in o.split() if w not in stop}
            if len(wa & wo) >= 3:
                bad.append(f"near-paraphrase of {o!r}: {a!r} (shares {sorted(wa & wo)})")
    if len(set(PROTECT)) != 8 or len(set(BLAME)) != 8:
        bad.append("item groups must be 8 unique each")
    for c, ex in NEW_ENTITIES.items():
        if c in ENTITIES:
            bad.append(f"new class collides with an existing one: {c}")
        if len(set(ex)) != 4:
            bad.append(f"{c}: need 4 unique exemplars")
        for e in ex:
            if not e.startswith(("a ", "an ")):
                bad.append(f"{c}: exemplar lacks an article, breaks the templates: {e!r}")
    return bad


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    bad = selfcheck()
    print("\n".join(bad) if bad else
          f"selfcheck OK — {len(PROTECT)}+{len(BLAME)} items, "
          f"{len(NEW_ENTITIES)} new classes, {sum(len(v) for v in NEW_ENTITIES.values())} new entities")
    sys.exit(1 if bad else 0)
