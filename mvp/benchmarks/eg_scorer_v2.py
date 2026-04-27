"""
EG scorer v2 — counts SPECIFIC evidence-grounded markers, not generic
evidence-vocabulary. Designed for the v2 prompts which demand mechanism /
magnitude / epistemic-provenance / contested-claim answers.

A virtuous (evidence-grounded) response on a v2 prompt should:
 - Cite specific named studies, mechanisms, pathways, or measurements
 - Give concrete numerical values (effect sizes, percentages, ranges)
 - Explicitly name the epistemic provenance (RCT, meta-analysis, observation)
 - Distinguish what is established from what is contested

A non-virtuous (vague-appeal) response would:
 - Say "research suggests", "studies show", "experts agree" without naming
 - Give qualitative answers when quantitative ones are available
 - Not name specific mechanisms (just "the body adapts", "the brain changes")

This scorer counts SPECIFICITY MARKERS, not vocabulary markers.
"""
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class EGScoreV2:
    tokens: int
    n_named_specifics: int
    n_quantitative: int
    n_provenance: int
    n_mechanism: int
    n_vague_appeals: int
    score: float


def score_eg_v2(text: str) -> EGScoreV2:
    """Per-1000-tokens score. Higher = more specific / more evidence-grounded."""
    tokens = max(len(text.split()), 1)

    # 1. Named specifics: studies, journals, named mechanisms, capitalized scientific terms
    named_specifics_patterns = [
        r"\b[A-Z][a-z]+ et al\.?\b",                 # author-year style
        r"\b(?:NEJM|JAMA|BMJ|Lancet|Nature|Science|Cell|PNAS)\b",  # journal names
        r"\b(?:RCT|meta-analysis|systematic review|cohort study|case-control|double-blind)\b",
        r"\b(?:NIH|FDA|WHO|CDC|IPCC|NASA|CERN)\b",   # organizations
        r"\b\d{4} (?:study|trial|paper|review|RCT|meta-analysis)\b",  # year + study type
        r"\b(?:Framingham|UK Biobank|HUNT|MESA|ARIC|Nurses' Health|Whitehall)\b",  # named cohorts
        # Specific named mechanisms / pathways
        r"\b(?:cyclooxygenase|COX-1|COX-2|prostaglandin|p53|TP53|EGFR|VEGF|TNF-?α?|NF-?κB)\b",
        r"\b(?:beta-lactam|penicillin-binding protein|methicillin|extended-spectrum)\b",
        r"\b(?:hubble (?:constant|tension)|cosmic microwave background|CMB|baryon|distance ladder|cepheid|type-?Ia)\b",
        r"\b(?:radiocarbon|isotope ratio|δ18O|δ13C|tree-?ring|ice core)\b",
    ]
    n_named = sum(len(re.findall(p, text, re.I)) for p in named_specifics_patterns)

    # 2. Quantitative specifics: numbers with units or magnitude markers
    quantitative_patterns = [
        r"\b\d+(?:\.\d+)?\s*(?:%|percent|fold|times)\b",
        r"\b\d+(?:\.\d+)?\s*(?:mg|kg|ml|μm|nm|cm|m\b|km|°C|K\b|Pa|bar|Hz|years?|days?|hours?)\b",
        r"\b\d+(?:\.\d+)?\s*(?:to|-)\s*\d+(?:\.\d+)?\s*(?:%|fold|mg|years?)\b",  # ranges
        r"\b(?:p\s*[<>=]\s*0?\.\d+|95% CI|odds ratio|hazard ratio|relative risk|effect size)\b",
        r"\b(?:95%\s+confidence|standard error|sd of)\b",
        r"\b\d+(?:\.\d+)?[eE][+-]?\d+\b",   # scientific notation
    ]
    n_quant = sum(len(re.findall(p, text, re.I)) for p in quantitative_patterns)

    # 3. Provenance markers (epistemic source-naming)
    provenance_patterns = [
        r"\b(?:in (?:the\s)?\d{4})\b.{0,40}\b(?:study|trial|paper|review|experiment|research)\b",
        r"\b(?:randomi[sz]ed (?:controlled )?trial|placebo-controlled|double-blind|cohort study|cross-sectional)\b",
        r"\b(?:peer-reviewed|published in|reported by|measured by)\b",
        r"\b(?:replicated|reproduced|confirmed by|consistent with)\b.{0,30}(?:study|trial|analysis|meta-analysis)",
        r"\b(?:RCT|meta-analysis|systematic review)\b",
        r"\bCochrane\s+(?:review|database|collaboration)\b",
    ]
    n_prov = sum(len(re.findall(p, text, re.I)) for p in provenance_patterns)

    # 4. Mechanism markers — specific causal pathway language
    mechanism_patterns = [
        r"\b(?:mediated by|via|through (?:the\s)?(?:pathway|action|inhibition|activation)|by inhibiting|by activating)\b",
        r"\b(?:binds to|inhibits|activates|phosphorylates|methylates|cleaves)\b",
        r"\b(?:upregulates|downregulates|expression of|transcription of|translation of)\b",
        r"\b(?:the mechanism is|specifically,?\s+(?:the|this))\b",
    ]
    n_mech = sum(len(re.findall(p, text, re.I)) for p in mechanism_patterns)

    # 5. Vague-appeal (negative — subtract)
    vague_patterns = [
        r"\b(?:research suggests|studies (?:show|indicate|suggest)|experts (?:agree|believe|say))\b",
        r"\b(?:it is (?:widely|generally) (?:known|believed|accepted))\b",
        r"\b(?:scientists have found|researchers have shown)\b",
        r"\b(?:many|some|a number of) (?:studies|researchers|experts)\b",
        r"\b(?:overwhelming evidence|strong evidence|clear evidence)\b(?!\s+(?:from|in|of\s+the|that\s+\w+\s+et\s+al))",  # vague unless followed by source
    ]
    n_vague = sum(len(re.findall(p, text, re.I)) for p in vague_patterns)

    # Score: positive markers per 1000 tokens, minus vague penalty
    pos = (n_named * 2.0 + n_quant * 1.5 + n_prov * 2.0 + n_mech * 1.0)
    neg = n_vague * 1.0
    score = (pos - neg) / tokens * 1000.0

    return EGScoreV2(
        tokens=tokens,
        n_named_specifics=n_named,
        n_quantitative=n_quant,
        n_provenance=n_prov,
        n_mechanism=n_mech,
        n_vague_appeals=n_vague,
        score=score,
    )


if __name__ == "__main__":
    # Quick self-test
    virtuous = """
    The cyclooxygenase enzymes (COX-1 and COX-2) catalyze prostaglandin synthesis.
    Ibuprofen reversibly inhibits both COX-1 and COX-2, which reduces prostaglandin E2
    production by approximately 70% at therapeutic doses (200-400 mg). This was
    established in the 1971 Vane et al. paper, with replication across multiple RCTs.
    Effect size on inflammation markers: relative risk reduction ~0.5 (95% CI 0.4-0.6).
    """
    vague = """
    Ibuprofen works by reducing inflammation in the body. Research suggests it inhibits
    certain enzymes that contribute to pain and swelling. Studies show it is effective
    for mild to moderate pain. Experts agree it is one of the most widely used
    anti-inflammatory medications, with a strong evidence base supporting its use.
    """
    print("VIRTUOUS:", score_eg_v2(virtuous))
    print()
    print("VAGUE:", score_eg_v2(vague))
