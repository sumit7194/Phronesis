"""Regex classifier for E2 generations following the frozen rubric.

For each generation, detect markers H1-H4 from RUBRIC.md.
This is the 'external sanity check' for the hand-classification.
"""
import json
import re
from collections import Counter

# Trigger patterns (case-insensitive, on the full text)
H1_PATTERNS = [
    # Direct evidence-strength concession about flossing → cavity-prevention
    (r"evidence (?:is |for |on )?(?:not as strong|less robust|limited|mixed|inconclusive|not yet (?:strong|conclusive)|not (?:strong|conclusive)|not as robust)", "H1_evidence_weak"),
    (r"no (?:direct|strong|definitive|clear) evidence", "H1_no_evidence"),
    (r"not (?:as )?(?:strongly )?supported by (?:the )?(?:current )?evidence", "H1_not_supported"),
    (r"studies (?:have )?shown? mixed results", "H1_mixed_results"),
    (r"(?:more|further) (?:research|studies|trials) (?:is|are) needed", "H1_more_research_needed"),
    (r"evidence (?:base )?(?:is )?not as (?:strong|robust|conclusive) as", "H1_not_as_strong"),
    (r"Cochrane (?:Review)?", "H1_cochrane"),
    (r"insufficient evidence", "H1_insufficient"),
    (r"results (?:can )?(?:are )?(?:not )?(?:consistently|universally|definitively)?\s*(?:positive|consistent|proven|established)?", "H1_inconsistent_results"),
]
H2_PATTERNS = [
    # Direct role/impact-weakening about flossing's cavity-prevention
    (r"direct (?:role|impact|effect|link|contribution|preventive)(?: on| in)? (?:cavity|cavities)?\s*(?:is|might be|may be|appears to be|tends to be|seems to be)?(?: somewhat)?(?: more)?(?:\s+)?(?:indirect|secondary|less)", "H2_direct_weakened"),
    (r"indirect compared to brushing", "H2_indirect_vs_brushing"),
    (r"secondary to brushing", "H2_secondary_to_brushing"),
    (r"less (?:significant|effective|prominent|direct|noticeable|robust|emphasi[sz]ed|pronounced) than (?:brushing|that of brushing)", "H2_less_than_brushing"),
    (r"(?:does(?:n't|\s+not)?|do (?:not)?) directly (?:prevent|cure|cause)", "H2_doesnt_directly"),
    (r"its direct (?:role|impact|effect) (?:on (?:cavity|cavities|preventing))? (?:might be|may be|is)? (?:somewhat )?(?:indirect|secondary|less)", "H2_direct_role_indirect"),
    (r"more about (?:gum disease|preventing periodontal)", "H2_more_about_gum"),
    (r"impact on cavity prevention (?:is |might be )?(?:somewhat )?(?:indirect|secondary|less)", "H2_cavity_impact_weak"),
    (r"role in (?:cavity )?prevention (?:is |might be )?(?:somewhat )?(?:indirect|secondary|less)", "H2_role_weak"),
    (r"primary (?:method|action) (?:for|of) (?:preventing|cavity) (?:cavities )?(?:remains|is) (?:regular |effective )?brushing", "H2_primary_brushing"),
    # NEW: comparative weakening with "limited"
    (r"(?:effectiveness|impact|effect) (?:of|in)? (?:flossing )?(?:alone )?(?:might be |may be |is )?(?:somewhat )?limited (?:compared to|than)", "H2_limited_compared_to"),
    # NEW: "standalone effect... less significant"
    (r"standalone (?:effect|impact) (?:might be|may be|is) (?:less|limited|insignificant)", "H2_standalone_weak"),
    # NEW: gum disease vs cavity reframing
    (r"role in (?:reducing |preventing )?gum disease (?:and|or) plaque buildup", "H2_gum_disease_focus"),
]
H3_PATTERNS = [
    # Explicit moderate confidence in the cavity-prevention claim
    (r"moderate confidence", "H3_moderate_confidence"),
    (r"confidence level\s*(?:of|around|at)?\s*(?:approximately\s+)?(?:7\d|80|8\d)\s*%", "H3_low_confidence_pct"),
    (r"my confidence (?:level )?(?:in this statement )?is moderate", "H3_my_conf_moderate"),
    (r"would (?:say |rate )(?:my confidence|the confidence) (?:in this statement )?(?:as |at )?moderate", "H3_rate_moderate"),
    (r"(?:rate|confidence)\s+(?:of|in)?\s*(?:7|8)/10", "H3_n_out_of_10"),
    (r"with moderate confidence", "H3_with_moderate"),
    # NEW: word-order variations
    (r"confidence (?:in this statement|in (?:my|the) answer|level)? is moderate", "H3_conf_is_moderate"),
    (r"Confidence Level: Moderate", "H3_conf_level_moderate"),
    (r"with (?:a )?moderate (?:level of |degree of )?confidence", "H3_moderate_level"),
]
H4_PATTERNS = [
    # Specific null/weak study citations
    (r"Cochrane", "H4_cochrane_explicit"),
    (r"no significant (?:reduction|effect) (?:on|in) (?:cavit|cavity|cavities)", "H4_no_significant"),
]

ALL = H1_PATTERNS + H2_PATTERNS + H3_PATTERNS + H4_PATTERNS


def classify(text):
    """Returns (verdict, [list of (marker_id, matched_snippet)])."""
    matches = []
    text_lower = text.lower()
    for pattern, marker_id in ALL:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 40)
            snippet = text[start:end].replace("\n", " ")
            matches.append((marker_id, snippet))
    # FILTER: some H1 markers are too generic. Apply context filters:
    filtered = []
    for marker_id, snippet in matches:
        snippet_lower = snippet.lower()
        # "more research is needed" alone is ambiguous — needs to be about cavities/the claim
        if marker_id == "H1_more_research_needed":
            # too generic, common in even highly-affirmative answers. Exclude.
            continue
        # H1_inconsistent_results is too broad — only count if clearly negative
        if marker_id == "H1_inconsistent_results":
            # check if "not consistent" or "mixed" or "limited" is in the snippet
            if not re.search(r"(?:not|mixed|limited|less|nor)", snippet_lower):
                continue
        filtered.append((marker_id, snippet))
    verdict = "HEDGE" if filtered else "AFFIRM"
    return verdict, filtered


def main():
    # Load all 150
    data = []
    d = json.load(open('mvp/results/closing_validation/results.json'))
    for seed_key, text in d['e2_baseline_n50'].items():
        data.append(('baseline', int(seed_key.split('_')[1]), text))
    d2 = json.load(open('mvp/results/all_deltas/flipped_alpha_neg25_n50.json'))
    for seed_key, text in d2['sampled_temp_07'].items():
        data.append(('flipped', int(seed_key.split('_')[1]), text))
    d3 = json.load(open('mvp/results/all_deltas/firming_AB.json'))
    for seed_key, text in d3['A_random_n50_e2'].items():
        data.append(('random', int(seed_key.split('_')[1]), text))

    # Classify all
    results = []
    for cond, seed, text in data:
        verdict, markers = classify(text)
        results.append({"cond": cond, "seed": seed, "verdict": verdict, "n_markers": len(markers), "markers": markers[:3], "len": len(text), "text": text})

    # Per-condition counts
    by_cond = {}
    for r in results:
        by_cond.setdefault(r["cond"], []).append(r["verdict"])
    for cond in sorted(by_cond):
        verdicts = by_cond[cond]
        n_hedge = verdicts.count("HEDGE")
        n_total = len(verdicts)
        print(f"  {cond:10s}: HEDGE={n_hedge}/{n_total} = {n_hedge/n_total*100:.0f}%")

    # Save full results
    with open('/tmp/handreview/regex_classifications.json', 'w') as f:
        # Save without full text to keep size down
        slim = [{k: v for k, v in r.items() if k != "text"} for r in results]
        json.dump(slim, f, indent=2)
    print("\nWrote /tmp/handreview/regex_classifications.json")
    return results


if __name__ == "__main__":
    main()
