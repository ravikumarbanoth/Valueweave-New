#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Stewardship Lifecycle (Work Package 5)

The seven-state record lifecycle, implemented from `governance/DATA_STEWARDSHIP.md`
rather than invented here. That document is the specification; this module is its
executable form, and the two are kept in agreement by `tests/test_stewardship.py`.

    DRAFT -> COLLECTED -> VALIDATED -> REVIEWED -> APPROVED -> PUBLISHED -> ARCHIVED

THREE RULES THAT MAKE THIS MORE THAN AN ENUM
--------------------------------------------
1. **No backward transitions.** A published record found to be wrong is corrected
   through a new package version, never by rewinding its state. Rewinding would
   destroy the audit trail that is the whole point of tracking state.

2. **Every transition needs an actor.** `VALIDATED -> REVIEWED` without a named
   reviewer is not a review; it is a checkbox. `require_actor` is True on the
   transitions where a human is the evidence.

3. **APPROVED is the only state a machine may not enter.** Collection, validation
   and publication are automatable. Approval is the moment a person accepts
   responsibility for a claim, and `Transition.machine_permitted` says so.

The current reality this models, stated plainly: all 647 entities are PUBLISHED
having never passed through REVIEWED or APPROVED, because no steward existed to
perform those transitions. `effective_state()` reports that gap instead of hiding
it.
"""

from dataclasses import dataclass
from enum import Enum


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    COLLECTED = "COLLECTED"
    VALIDATED = "VALIDATED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return value
        v = str(value or "").strip().upper()
        try:
            return cls(v)
        except ValueError:
            raise ValueError(
                f"unknown lifecycle state {value!r}; expected one of "
                f"{[s.value for s in cls]}") from None

    @property
    def order(self):
        return ORDER.index(self)


ORDER = [LifecycleState.DRAFT, LifecycleState.COLLECTED, LifecycleState.VALIDATED,
         LifecycleState.REVIEWED, LifecycleState.APPROVED, LifecycleState.PUBLISHED,
         LifecycleState.ARCHIVED]


class TransitionError(Exception):
    """Raised when a transition is not permitted. Carries why, not just that."""


@dataclass(frozen=True)
class Transition:
    source: LifecycleState
    target: LifecycleState
    requirement: str
    require_actor: bool
    machine_permitted: bool


#: The transition table, one row per arrow in DATA_STEWARDSHIP.md.
TRANSITIONS = [
    Transition(LifecycleState.DRAFT, LifecycleState.COLLECTED,
               "Provenance present on every field", False, True),
    Transition(LifecycleState.COLLECTED, LifecycleState.VALIDATED,
               "The owning package's validator exits 0", False, True),
    Transition(LifecycleState.VALIDATED, LifecycleState.REVIEWED,
               "A named human reviewer has read the record against its sources",
               True, False),
    Transition(LifecycleState.REVIEWED, LifecycleState.APPROVED,
               "Steward sign-off; verification_status becomes VST-VERIFIED",
               True, False),
    Transition(LifecycleState.APPROVED, LifecycleState.PUBLISHED,
               "Included in a released package version", False, True),
    Transition(LifecycleState.PUBLISHED, LifecycleState.ARCHIVED,
               "A successor exists, or the record is retired", True, True),
    # ------------------------------------------------------------------ the
    # RETROACTIVE REVIEW path.
    #
    # Every one of the 647 entities is PUBLISHED and none passed through REVIEWED,
    # because no steward existed when they were released. Under the forward-only
    # rule that is a dead end: a steward who reads a published record against its
    # sources has nowhere to record it, and the platform can never leave 0% verified.
    #
    # The resolution is not to relax the forward-only rule. It is to recognise that
    # this is not a backward move at all — the record never occupied REVIEWED, so
    # this fills in a *skipped* state rather than undoing a completed one. The gate
    # says exactly that: it is refused the moment a record is genuinely VST-VERIFIED,
    # which is the only case where it would be a real rewind.
    Transition(LifecycleState.PUBLISHED, LifecycleState.REVIEWED,
               "Retroactive review of a record that reached PUBLISHED without ever "
               "passing through REVIEWED; permitted only while it is not VST-VERIFIED",
               True, False),
]

BY_PAIR = {(t.source, t.target): t for t in TRANSITIONS}

#: Reaching APPROVED sets this on the underlying package rows. Nothing else does.
VERIFIED_STATUS = "VST-VERIFIED"
NEEDS_REVIEW_STATUS = "VST-NEEDS_REVIEW"


def allowed_from(state):
    state = LifecycleState.parse(state)
    return [t for t in TRANSITIONS if t.source == state]


RETROACTIVE_REVIEW = (LifecycleState.PUBLISHED, LifecycleState.REVIEWED)


def check_transition(source, target, actor=None, by_machine=False,
                     verification_status=None):
    """
    Validate a proposed transition. Returns the Transition, or raises TransitionError.

    Refuses rather than warns: a stewardship workflow that lets an invalid transition
    through with a warning records a decision that was never made.

    `verification_status` gates the retroactive-review path only. Pass the record's
    current status when you have it; omitting it assumes not-yet-verified, which is
    true of every row in the knowledge base today.
    """
    source = LifecycleState.parse(source)
    target = LifecycleState.parse(target)

    if source == target:
        raise TransitionError(f"{source.value} -> {target.value} is not a transition")

    if (source, target) == RETROACTIVE_REVIEW and \
            (verification_status or "").strip() == VERIFIED_STATUS:
        raise TransitionError(
            f"{source.value} -> {target.value} is refused: this record is already "
            f"{VERIFIED_STATUS}, so re-reviewing it would be a genuine rewind. "
            f"Correct a verified record with a new package version.")

    t = BY_PAIR.get((source, target))
    if t is None:
        if target.order < source.order:
            raise TransitionError(
                f"{source.value} -> {target.value} moves backwards. Backward transitions "
                f"are not permitted: correct a published record with a new package "
                f"version, which preserves the audit trail.")
        legal = [x.target.value for x in allowed_from(source)]
        raise TransitionError(
            f"{source.value} -> {target.value} skips a state. From {source.value} the "
            f"only permitted target is {legal or 'nothing — it is terminal'}.")

    if t.require_actor and not (actor or "").strip():
        raise TransitionError(
            f"{source.value} -> {target.value} requires a named actor: {t.requirement}")

    if by_machine and not t.machine_permitted:
        raise TransitionError(
            f"{source.value} -> {target.value} may not be performed by a machine. "
            f"{t.requirement}.")

    return t


def effective_state(lifecycle_state, verification_status):
    """
    Reconcile the two things a record says about itself.

    A record can claim PUBLISHED while its verification_status says nobody has read
    it. Both facts are true and the tension between them is the honest description
    of this platform today, so this returns the state plus the gap rather than
    silently preferring one.
    """
    state = LifecycleState.parse(lifecycle_state)
    verified = (verification_status or "").strip() == VERIFIED_STATUS
    reviewed_or_beyond = state.order >= LifecycleState.REVIEWED.order

    if reviewed_or_beyond and not verified:
        return state, ("claims %s but verification_status is %s: it reached this state "
                       "without human review" % (state.value, verification_status
                                                 or "(empty)"))
    if verified and not reviewed_or_beyond:
        return state, ("marked %s but lifecycle_state is only %s"
                       % (VERIFIED_STATUS, state.value))
    return state, None
