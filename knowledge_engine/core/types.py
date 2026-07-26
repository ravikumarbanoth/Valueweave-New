"""Shared enums used across every Knowledge Engine module.

These mirror the conventions already established by hand in Package001_Geography through
Package004_Industries so that engine-produced records are structurally identical to hand-built ones.
"""

from __future__ import annotations

from enum import Enum


class VerificationStatus(str, Enum):
    """Mirrors the VST-* convention used in every package's `verification_status` column.

    A record is created at NEEDS_REVIEW and promoted to VERIFIED only by an explicit human/governance
    action — never automatically by any Knowledge Engine module.
    """

    NEEDS_REVIEW = "VST-NEEDS_REVIEW"
    VERIFIED = "VST-VERIFIED"
    REJECTED = "VST-REJECTED"

    @classmethod
    def default(cls) -> "VerificationStatus":
        return cls.NEEDS_REVIEW


class SourceTier(int, Enum):
    """The 5-tier source-priority order used across Package001-004's collection methodology.

    Lower tier number = stronger source. Confidence-scoring rules (see
    `validation.rules.ConfidenceScoringRule`) use this ordering to sanity-check that a record's
    confidence score is consistent with the strength of the tier its source belongs to.
    """

    GOVERNMENT = 1
    OFFICIAL_ORGANIZATION = 2
    VERIFIED_SOCIAL_MEDIA = 3
    TRUSTED_NEWS = 4
    COMMUNITY_QUALITATIVE = 5


class ConfidenceTier(Enum):
    """Confidence-score bands calibrated to match Package001-004's convention.

    - GOVERNMENT_GRADE (70-100): traced to a specific government/authoritative document.
    - PORTAL_OR_NEWS (55-69): a named organization/news source without primary-document backing.
    - COMMUNITY_QUALITATIVE (0-54): Tier-5 qualitative color only; must be flagged in a record's
      notes and is never the sole basis for a numeric claim.
    """

    GOVERNMENT_GRADE = (70, 100)
    PORTAL_OR_NEWS = (55, 69)
    COMMUNITY_QUALITATIVE = (0, 54)

    @classmethod
    def for_score(cls, score: int) -> "ConfidenceTier":
        for tier in cls:
            low, high = tier.value
            if low <= score <= high:
                return tier
        raise ValueError(f"confidence score {score} is out of the valid 0-100 range")


#: The literal sentinel used across every ValueWeave package when a fact cannot be traced to a
#: reliable source. Must appear as this exact bare string in a cell — never with an appended
#: explanation. Any explanation belongs in that record's `notes` field, prefixed `[field_name]:`.
PENDING_VERIFICATION = "PENDING_VERIFICATION"
