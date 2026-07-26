#!/usr/bin/env python3
"""
The rule engine. Rule-based, no AI, and reproducible by construction.

THREE THINGS EVERY RULE RETURNS
-------------------------------
  value      a number, or None
  evidence   the entities and edges that produced it — never a bare number
  status     APPLIED | UNAVAILABLE | NO_SIGNAL

The distinction between the last two is the one that matters:

  **UNAVAILABLE** — we cannot compute this. An input is missing (there is no
  `assessment_results` table), so any number would be fiction.

  **NO_SIGNAL** — we computed it and the answer is "nothing". The user has no
  resolvable skill, or their district has no researched business.

Both currently render as an empty panel in a naive UI, and they mean opposite
things: one is our gap, the other is theirs. Collapsing them into `score = 0`
would tell a user their district has no opportunity when the truth is that we have
not collected it yet.

REPRODUCIBILITY
---------------
No randomness, no clock inside any computation, no external call. Rules read a
frozen `UserContext` and a frozen knowledge snapshot. `Outcome.fingerprint()`
hashes the inputs and the result, excluding timestamps, so two runs over the same
data are provably identical — `test_engine_is_reproducible` asserts it.

Ordering is explicit everywhere. A rule that iterates a set and takes the first
element would be reproducible within one Python process and not across two, which
is the worst kind of non-determinism: invisible until it matters.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum

APPLIED, UNAVAILABLE, NO_SIGNAL = "APPLIED", "UNAVAILABLE", "NO_SIGNAL"


class Direction(str, Enum):
    OUT = "out"
    IN = "in"


@dataclass(frozen=True)
class Evidence:
    """One fact that supported a conclusion. Always traceable to the graph."""

    kind: str                 # entity | edge | profile_field | crosswalk | supabase
    ref: str                  # entity id, relationship id, or column name
    label: str = ""
    detail: str = ""
    confidence: int = 0
    source_package: str = ""
    source_dataset: str = ""
    source_row_id: str = ""

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v not in ("", 0)}


@dataclass
class Outcome:
    rule: str
    status: str
    value: float = None
    weight: float = 1.0
    reason: str = ""
    evidence: list = field(default_factory=list)

    @property
    def applied(self):
        return self.status == APPLIED

    def to_dict(self):
        return {
            "rule": self.rule,
            "status": self.status,
            "value": (round(self.value, 2) if isinstance(self.value, (int, float))
                      else None),
            "weight": self.weight,
            "reason": self.reason,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    def fingerprint(self):
        payload = {"rule": self.rule, "status": self.status,
                   "value": (round(self.value, 4)
                             if isinstance(self.value, (int, float)) else None),
                   "evidence": sorted(e.ref for e in self.evidence)}
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- constructors
def applied(rule, value, reason, evidence=None, weight=1.0):
    return Outcome(rule=rule, status=APPLIED, value=clamp(value), weight=weight,
                   reason=reason, evidence=list(evidence or []))


def unavailable(rule, reason, weight=1.0):
    """We cannot compute this. Distinct from 'the answer is nothing'."""
    return Outcome(rule=rule, status=UNAVAILABLE, value=None, weight=weight,
                   reason=reason)


def no_signal(rule, reason, evidence=None, weight=1.0):
    """We computed it; the answer is nothing. A real, reportable result."""
    return Outcome(rule=rule, status=NO_SIGNAL, value=0.0, weight=weight,
                   reason=reason, evidence=list(evidence or []))


def clamp(value, low=0.0, high=100.0):
    if value is None:
        return None
    return float(max(low, min(high, value)))


# --------------------------------------------------------------------- scoring
@dataclass
class ScoreResult:
    key: str
    label: str
    score: float = None
    status: str = APPLIED
    outcomes: list = field(default_factory=list)
    reason: str = ""

    @property
    def evidence(self):
        seen, out = set(), []
        for o in self.outcomes:
            for e in o.evidence:
                if e.ref not in seen:
                    seen.add(e.ref)
                    out.append(e)
        return out

    @property
    def confidence(self):
        """
        Confidence is inherited from the data, never invented.

        Kept strictly separate from `score`. The score says how well the user
        matches; the confidence says how much the underlying rows can be trusted.
        A perfect match built on a confidence-50 row is a strong claim about weak
        data, and a UI that shows one number cannot say so.

        The minimum, not the mean: a chain is as trustworthy as its weakest link,
        and averaging lets one high-confidence row mask a poor one.
        """
        scores = [e.confidence for e in self.evidence if e.confidence]
        return min(scores) if scores else 0

    def to_dict(self):
        return {
            "key": self.key, "label": self.label,
            "score": (round(self.score, 1) if self.score is not None else None),
            "status": self.status, "confidence": self.confidence,
            "reason": self.reason,
            "evidence_count": len(self.evidence),
            "evidence": [e.to_dict() for e in self.evidence[:25]],
            "outcomes": [o.to_dict() for o in self.outcomes],
        }

    def fingerprint(self):
        return hashlib.sha256(
            "|".join([self.key, self.status,
                      f"{self.score:.4f}" if self.score is not None else "none"]
                     + [o.fingerprint() for o in self.outcomes]).encode()
        ).hexdigest()[:12]


def combine(key, label, outcomes, low_means=""):
    """
    Fold rule outcomes into one score.

    Weighted mean over APPLIED and NO_SIGNAL outcomes. UNAVAILABLE outcomes are
    **excluded from the denominator**, not counted as zero — otherwise a missing
    input would silently depress a score and look like a finding about the user.

    If every outcome is UNAVAILABLE the score is None, and the reason names the
    inputs that were missing. A score of None is honest; a score of 0 is not.
    """
    computable = [o for o in outcomes if o.status in (APPLIED, NO_SIGNAL)]
    if not computable:
        reasons = "; ".join(o.reason for o in outcomes) or "no rule could be applied"
        return ScoreResult(key=key, label=label, score=None, status=UNAVAILABLE,
                           outcomes=outcomes, reason=reasons)

    total_weight = sum(o.weight for o in computable) or 1.0
    score = sum((o.value or 0.0) * o.weight for o in computable) / total_weight

    contributing = [o for o in computable if o.status == APPLIED and (o.value or 0) > 0]
    if contributing:
        reason = "; ".join(o.reason for o in contributing[:4])
    else:
        reason = low_means or "no positive signal found"
        return ScoreResult(key=key, label=label, score=clamp(score),
                           status=NO_SIGNAL, outcomes=outcomes, reason=reason)

    skipped = [o.rule for o in outcomes if o.status == UNAVAILABLE]
    if skipped:
        reason += f" (rules skipped for missing inputs: {', '.join(skipped)})"
    return ScoreResult(key=key, label=label, score=clamp(score), status=APPLIED,
                       outcomes=outcomes, reason=reason)


def band(confidence):
    from user_intelligence.config import CONFIDENCE_BANDS
    for low, high, name in CONFIDENCE_BANDS:
        if low <= confidence <= high:
            return name
    return "UNKNOWN"
