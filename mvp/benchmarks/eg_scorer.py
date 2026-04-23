"""
EG (Evidence Grounding) scorer.

Per docs/eg-rt-eval-spec.md §3.4, scores a generation on evidence-grounding
markers: counts specific evidence-type labels and claim-evidence patterns,
subtracts vague appeals, normalises by token count.

Returns score in units of "markers per 1000 tokens"; positive = more EG.

Calibration target (from §3.5): on mvp-combined/triplets-evidence-grounding:
- virtuous mean >= +10
- deficiency-non-virtuous mean <= +2 (vague appeals dominate)
- excess-non-virtuous is high by regex but hand-review flags as caricature

Known failure modes (§3.6):
- keyword stuffing inflates score — hand review required
- length confound mitigated via per-1000 normalisation
- domain sensitivity — report per-domain means separately
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List


# Evidence-type labels: specific categories of evidence the reasoner names
# v2 expanded to catch compound "X evidence" and naturalistic scientific prose
EVIDENCE_TYPE_PATTERNS: List[str] = [
    r"\bobservational (?:study|studies|data|evidence|comparison|controls?)\b",
    r"\bexperimental (?:study|studies|data|evidence|comparison|finding|findings)\b",
    r"\bcontrolled experiment\b",
    r"\bcase (?:study|studies|report|reports)\b",
    r"\bclinical case\b",
    r"\brandomi[sz]ed (?:controlled )?trial\b",
    r"\bRCTs?\b",
    r"\bmeta[- ]?analysis\b",
    r"\bsystematic review\b",
    r"\btheoretical (?:prediction|model|calculation|framework|expectation|claim|inference)\b",
    r"\btheory predicts?\b",
    r"\banecdotal\b",
    r"\bsingle example\b",
    r"\billustrative example\b",
    r"\bsurvey (?:data|results|response|responses)\b",
    r"\bsimulation(?:s)?\b",
    r"\bcomputational model\b",
    r"\blongitudinal (?:study|studies|data)\b",
    r"\bcross[- ]sectional (?:study|studies|data)\b",
    r"\bspecific (?:observation|measurement|result|finding|data)\b",
    r"\bdirect (?:observation|measurement|evidence)\b",
    r"\bfield (?:study|studies|data|measurement|observations?)\b",
    r"\blab(?:oratory)? (?:study|studies|data|measurement|work|result|results)\b",
    r"\bempirical (?:observation|finding|measurement|evidence|support|claim)\b",
    r"\b(?:prospective|retrospective) (?:study|studies|cohort)\b",
    r"\bcohort study\b",
    r"\bfirst[- ]principles (?:prediction|calculation)\b",
    r"\bsingle[- ]site (?:trial|study)\b",
    r"\bmulti[- ]?site (?:trial|study)\b",
    # v2: compound "X evidence" / "X comparison" — common in naturalistic scientific writing
    r"\b(?:route|fare|media|spectroscopic|photometric|biological|chemical|physical|statistical|kinetic|structural|procedural|analytical|compositional|volumetric|temperature|pressure|sensor|visual|textual|rate|trap|mechanism)-?\w*\s+(?:evidence|comparison|data|indicator|indicators|finding|findings|result|results|observation|observations)\b",
    r"\bevidence type\b",
    r"\bindirect (?:indicator|indicators|evidence)\b",
    r"\bspectroscopic (?:evidence|analysis|signature|measurement)\b",
    r"\bmechanistic (?:inference|prediction|claim)\b",
    r"\bcross[- ]study\b",
    r"\bcontrol(?: group| arm| condition| experiment|s)?\b",
    r"\bnegative (?:evidence|result|control)\b",
    r"\bsensitivity analysis\b",
    r"\bpilot (?:study|trial|run)\b",
    r"\bvalidation (?:data|study|run)\b",
    r"\bplacebo[- ]controlled\b",
    r"\bquasi[- ]experimental\b",
    r"\bpre[- ]?registered\b",
    r"\bpower(?:ed)? (?:for|to detect)\b",
]

# Claim-evidence linkage patterns: reasoner explicitly ties a claim to specific evidence
# v2 expanded for the "grounds the claim" / "rests on" / "I can ground" patterns
CLAIM_EVIDENCE_PATTERNS: List[str] = [
    r"\bbased on (?:a |an |the )?(?:study|trial|experiment|observation|survey|dataset|measurement|finding)\b",
    r"\b(?:supported|established|documented|shown|demonstrated) by (?:a |an |the )?(?:study|trial|experiment|observation|measurement)\b",
    r"\baccording to (?:a |an |the )?(?:study|paper|trial|report|dataset|analysis)\b",
    r"\bevidence for this (?:comes from|is)\b",
    r"\bthis (?:rests|relies|depends) on\b",
    r"\bthe (?:data|evidence|observation|finding)s? (?:here|in this study) (?:shows?|suggests?|indicates?)\b",
    # v2: naturalistic claim-grounding forms
    r"\bgrounds? the claim\b",
    r"\bsupports? the (?:narrow |specific |broader |equivalence )?claim\b",
    r"\bthat (?:comparison|observation|finding|result|measurement) (?:grounds|supports|establishes|documents)\b",
    r"\bI can ground\b",
    r"\bthe empirical claim (?:here |I can |is )\b",
    r"\bthe (?:causal|mechanistic|theoretical) claim is\b",
    r"\bas (?:an empirical|a measurement|a direct observation)\b",
    r"\b(?:evidence|data) (?:anchor|anchors|anchoring)\b",
    r"\b(?:that|this) is (?:observational|experimental|empirical|direct) (?:evidence|data|measurement|observation)\b",
    r"\b(?:observed|measured|recorded) (?:directly|empirically|in the data)\b",
    r"\bnot (?:a |an )?(?:inference|direct measurement|empirical observation|structural identification)\b",
    r"\bwithin this (?:study|trial|experiment)('s)? own terms\b",
    r"\bis direct (?:evidence|measurement|observation)\b",
    r"\bnot (?:simulation|inference|theory)\b",
    r"\b(?:strong|weak|mixed) evidence\b",
    r"\ba (?:direct|specific) (?:observation|measurement|finding|comparison)\b",
    r"\bthe (?:specific|direct) (?:observation|measurement|finding)\b",
]

# Vague-appeal markers: under-grounded authority appeals AND confident-causation without evidence
# v2 expanded to catch deficiency-specific rhetoric (not just vocabulary — rhetorical moves too)
VAGUE_APPEAL_PATTERNS: List[str] = [
    # Authority / generality appeals (v1)
    r"\bstudies (?:show|have shown|suggest|demonstrate)\b",
    r"\bresearch (?:has )?shown\b",
    r"\bit is (?:generally |well |widely )?(?:known|accepted|understood|established)\b",
    r"\bis well[- ]understood\b",
    r"\b(?:is|are) (?:well[- ]|widely )(?:known|understood|established|accepted)\b",
    r"\bresearch demonstrates\b",
    r"\bscience has (?:shown|established|proved)\b",
    r"\bexperts (?:say|agree|believe)\b",
    r"\bthe literature (?:shows?|suggests?|indicates?)\b",
    r"\bconventional wisdom\b",
    r"\bthe consensus (?:is|view)\b",
    r"\beveryone knows\b",
    r"\bcommon knowledge\b",
    r"\bgenerally (?:accepted|believed|thought)\b",
    r"\bwhat is known about\b",
    r"\bare known to\b",
    # v2: confident causal assertions without evidence-type tagging (EG-b deficiency signature)
    r"\bis causing\b",
    r"\bthe effect is (?:clear|obvious|evident)\b",
    r"\bthe pattern matches what is known\b",
    r"\bconsistent with what we know\b",
    r"\bestablishing that .{1,30} (?:is|are) (?:driving|causing)\b",
    r"\b(?:is|are) driving (?:the|a) (?:decline|increase|observed|trend|change|pattern|effect|result)\b",
    r"\bconfirm(?:s|ing|ed) what .{1,30} predicted\b",
    r"\bthe mechanism is (?:clear|well[- ]understood|known|obvious)\b",
    r"\bis the (?:obvious|clear|primary) (?:source|cause|driver)\b",
    r"\bthe .{1,30} link (?:between|is) .{1,40} (?:well[- ]|widely )?understood\b",
    r"\bdocumented ecological\b",
    r"\bthe evidence is clear\b",
    r"\bon a trajectory of\b",
    r"\bfalls squarely within\b",
    r"\bthe .{1,20} implication is direct\b",
    r"\bthis pattern matches\b",
]


@dataclass
class EGScore:
    """Detailed EG score breakdown."""
    tokens: int
    evidence_types_matched: int
    claim_evidence_matched: int
    vague_appeals_matched: int
    pos: int
    neg: int
    score: float

    def to_dict(self) -> Dict:
        return {
            "tokens": self.tokens,
            "evidence_types_matched": self.evidence_types_matched,
            "claim_evidence_matched": self.claim_evidence_matched,
            "vague_appeals_matched": self.vague_appeals_matched,
            "pos": self.pos,
            "neg": self.neg,
            "score": self.score,
        }


def _count_matches(patterns: List[str], text: str) -> int:
    total = 0
    for p in patterns:
        total += len(re.findall(p, text, re.IGNORECASE))
    return total


def score_eg(text: str) -> EGScore:
    """Score a single passage for Evidence Grounding.

    Returns EGScore dataclass. `score` field is the headline metric
    (markers per 1000 tokens, positive = more EG).
    """
    tokens = len(text.split())
    if tokens == 0:
        return EGScore(0, 0, 0, 0, 0, 0, 0.0)

    ev_types = _count_matches(EVIDENCE_TYPE_PATTERNS, text)
    claim_ev = _count_matches(CLAIM_EVIDENCE_PATTERNS, text)
    vague = _count_matches(VAGUE_APPEAL_PATTERNS, text)

    pos = ev_types + claim_ev
    neg = vague
    score = (pos - neg) / tokens * 1000.0

    return EGScore(
        tokens=tokens,
        evidence_types_matched=ev_types,
        claim_evidence_matched=claim_ev,
        vague_appeals_matched=vague,
        pos=pos,
        neg=neg,
        score=score,
    )


if __name__ == "__main__":
    # Quick sanity check
    virtuous_sample = (
        "The controlled experiment yielded 1.3-point reduction (95% CI 0.8-1.8). "
        "This direct observation supports the efficacy claim. The meta-analysis "
        "of three separate RCTs established a baseline. According to the study, "
        "duloxetine produced a comparable effect."
    )
    vague_sample = (
        "Studies show that exercise is beneficial. Research has shown that "
        "sleep improves memory. It is generally known that hydration matters. "
        "The literature suggests these effects are robust. Experts agree."
    )
    v = score_eg(virtuous_sample)
    n = score_eg(vague_sample)
    print(f"Virtuous sample: score={v.score:.1f} (pos={v.pos}, neg={v.neg}, tokens={v.tokens})")
    print(f"Vague sample:    score={n.score:.1f} (pos={n.pos}, neg={n.neg}, tokens={n.tokens})")
    assert v.score > n.score, "Scorer sanity check failed — virtuous should beat vague"
    print("Sanity check passed.")
