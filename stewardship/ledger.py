#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Stewardship Ledger (Work Package 5)

An append-only record of every lifecycle decision a steward has made.

WHY A LEDGER AND NOT A STATE COLUMN
-----------------------------------
The obvious implementation is a `lifecycle_state` column that gets overwritten on
each transition. That loses the only thing worth keeping: *who decided what, when,
and on what evidence*. A record that says APPROVED tells you nothing about whether
approval was considered or clicked.

So state is derived, never stored: `current_state()` replays the ledger. The cost
is a fold over the entries; the benefit is that the audit trail cannot be edited by
a later transition, and a wrong approval is visible as a wrong approval rather than
vanishing under a correction.

Nothing here writes to a package or to the graph. Propagating an approval into a
package's `verification_status` is a separate, explicit step — see `store.py` —
because writing to a package is a release action and should never be a side effect
of recording a decision.
"""

import csv
import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from stewardship.lifecycle import LifecycleState, check_transition

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "stewardship" / "review_ledger.csv"

FIELDS = ["entry_id", "recorded_at", "entity_id", "from_state", "to_state",
          "actor", "actor_role", "evidence", "verification_status_after", "notes"]


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class LedgerEntry:
    entity_id: str
    from_state: str
    to_state: str
    actor: str = ""
    actor_role: str = ""
    evidence: str = ""
    verification_status_after: str = ""
    notes: str = ""
    recorded_at: str = field(default_factory=_now)
    entry_id: str = ""

    def __post_init__(self):
        if not self.entry_id:
            # Deterministic id over the content that identifies the decision, so
            # replaying the same decision twice is detectable rather than silently
            # duplicated.
            digest = hashlib.sha256(
                f"{self.entity_id}|{self.from_state}|{self.to_state}|"
                f"{self.actor}|{self.recorded_at}".encode()).hexdigest()[:12]
            self.entry_id = f"rev-{digest}"

    def to_row(self):
        return {k: asdict(self)[k] for k in FIELDS}


class ReviewLedger:
    def __init__(self, path=None):
        self.path = Path(path or LEDGER_PATH)
        self.entries = []
        if self.path.exists():
            with open(self.path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.entries.append(LedgerEntry(**{k: row.get(k, "") for k in FIELDS}))

    # ------------------------------------------------------------- reading
    def for_entity(self, entity_id):
        return [e for e in self.entries if e.entity_id == entity_id]

    def current_state(self, entity_id, default=LifecycleState.PUBLISHED):
        """Replay this entity's entries. The last recorded target wins."""
        history = self.for_entity(entity_id)
        if not history:
            return LifecycleState.parse(default)
        return LifecycleState.parse(history[-1].to_state)

    def verification_status(self, entity_id, default=""):
        for e in reversed(self.for_entity(entity_id)):
            if e.verification_status_after:
                return e.verification_status_after
        return default

    def actors(self):
        return sorted({e.actor for e in self.entries if e.actor})

    # ------------------------------------------------------------- writing
    def record(self, entity_id, from_state, to_state, actor="", actor_role="",
               evidence="", notes="", by_machine=False, verification_status=None):
        """
        Validate and append one transition. Raises TransitionError if not permitted.

        Validation happens here rather than in the caller so that no code path can
        append an illegal transition to the audit trail.
        """
        transition = check_transition(from_state, to_state, actor=actor,
                                      by_machine=by_machine,
                                      verification_status=verification_status)
        status = ""
        if LifecycleState.parse(to_state) == LifecycleState.APPROVED:
            from stewardship.lifecycle import VERIFIED_STATUS
            status = VERIFIED_STATUS
        entry = LedgerEntry(
            entity_id=entity_id,
            from_state=LifecycleState.parse(from_state).value,
            to_state=LifecycleState.parse(to_state).value,
            actor=actor, actor_role=actor_role,
            evidence=evidence or transition.requirement,
            verification_status_after=status, notes=notes)
        self.entries.append(entry)
        return entry

    def flush(self):
        """Rewrite the ledger file from the in-memory entries."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(e.to_row() for e in self.entries)
        return self.path

    def stats(self):
        by_state, by_actor = {}, {}
        for e in self.entries:
            by_state[e.to_state] = by_state.get(e.to_state, 0) + 1
            if e.actor:
                by_actor[e.actor] = by_actor.get(e.actor, 0) + 1
        return {
            "entries": len(self.entries),
            "entities_touched": len({e.entity_id for e in self.entries}),
            "transitions_by_target_state": dict(sorted(by_state.items())),
            "by_actor": dict(sorted(by_actor.items(), key=lambda kv: -kv[1])),
        }
