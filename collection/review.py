#!/usr/bin/env python3
"""
The review queue — where collected material waits for a person.

THE ONE RULE
------------
Nothing in this module can publish. It writes candidates to a JSONL file in
Git and it appends decisions to the stewardship ledger. It does not touch
`packages/`, it does not touch the knowledge graph, and it does not touch
Supabase. Promoting an approved candidate into a package dataset is a separate,
explicit act performed by a person — the same separation `stewardship/cli.py`
already enforces between recording a judgement (`review`, `approve`) and
releasing it (`apply --write`).

WHY THIS DOES NOT INVENT A WORKFLOW
------------------------------------
`governance/DATA_STEWARDSHIP.md` already specifies the seven-state lifecycle,
`stewardship/lifecycle.py` implements it, and `stewardship/ledger.py` records
every transition with an actor and evidence. The brief's workflow —

    Collected -> Needs Review -> Approved -> Knowledge Package -> Git -> Sync

— is that lifecycle with the same states under different names:

    COLLECTED -> VALIDATED -> REVIEWED -> APPROVED -> PUBLISHED

So this module produces COLLECTED records and hands them to the machinery that
already exists. Building a second review system beside the first would give
ValueWeave two answers to "has a human approved this?", which is the same
mistake as two search implementations and considerably more expensive.

The rule that makes it safe is already written down and already tested:
`APPROVED is the only state a machine may not enter` (lifecycle.py). Nothing
here can approve anything.

WHY JSONL IN GIT AND NOT A TABLE
---------------------------------
Git is the source of truth for knowledge; Supabase is a read-optimised cache.
A candidate is proposed knowledge. Putting the queue in a database would make
the proposal invisible to the review mechanism the project actually uses —
a pull request — and would need a migration, an RLS policy and an admin screen
before the first candidate could be looked at.

A JSONL file is diffable, reviewable in a PR, greppable, and needs nothing. The
scheduled workflow opens a pull request; the diff IS the queue.
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "collection" / "state" / "review_queue.jsonl"

#: The states a CANDIDATE can be in, which are a strict subset of the
#: stewardship lifecycle. A candidate never reaches PUBLISHED here — it leaves
#: this file when a person promotes it into a package.
COLLECTED = "COLLECTED"
NEEDS_REVIEW = "NEEDS_REVIEW"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
DUPLICATE = "DUPLICATE"

CANDIDATE_STATES = {COLLECTED, NEEDS_REVIEW, APPROVED, REJECTED, DUPLICATE}


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Candidate:
    """One thing a person may want to turn into knowledge.

    Everything here is either copied from the source or derived by a rule that
    named itself. There is no field a machine filled in with a judgement it
    could not explain — `classified_reason` carries the words that fired,
    `duplicate_reason` the overlap that was measured.
    """

    candidate_id: str
    source_id: str
    source_name: str
    item_key: str
    title: str
    url: str
    published_at: str
    change: str                       # NEW or UPDATED
    classified_as: str
    classified_reason: str
    is_entity: bool
    state: str = COLLECTED
    duplicate_of: str = ""
    duplicate_reason: str = ""
    supersedes: str = ""
    collected_at: str = field(default_factory=_now)
    #: The parsed record, verbatim. A reviewer must be able to see what the
    #: source actually said, not a summary of it — and provenance requires the
    #: raw claim to survive to the point of approval.
    raw: dict = field(default_factory=dict)

    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def candidate_id(source_id, item_key):
    """Stable across runs, so re-collecting the same item updates its entry
    rather than adding a second one."""
    safe = "".join(ch if ch.isalnum() or ch in "-._" else "-" for ch in str(item_key))
    return f"{source_id}:{safe[:80]}"


def load(queue_path=None):
    path = Path(queue_path or QUEUE_PATH)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        raw = json.loads(line)
        known = {k: v for k, v in raw.items() if k in Candidate.__dataclass_fields__}
        out.append(Candidate(**known))
    return out


def save(candidates, queue_path=None):
    """Rewrite the queue.

    Not append-only, and deliberately so — this is a QUEUE, not a ledger. The
    audit trail lives in `stewardship/review_ledger.csv`, which IS append-only
    and is where a decision is recorded. Keeping rejected candidates in the
    working queue forever would make the file unreadable, which is the failure
    mode that ends review.
    """
    path = Path(queue_path or QUEUE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(candidates, key=lambda c: (c.state != NEEDS_REVIEW,
                                                c.source_id, c.candidate_id))
    path.write_text("".join(c.to_json() + "\n" for c in ordered), encoding="utf-8")
    return path


def merge(existing, incoming):
    """New candidates in, without losing decisions already made.

    A candidate a human has already approved or rejected keeps that state even
    if the item is collected again. Overwriting it would put decided material
    back in front of a reviewer on every run, which is how a queue trains the
    people reading it to skim.

    An UPDATED item whose content changed is the exception: it returns to
    NEEDS_REVIEW, because the thing that was approved is not the thing that is
    there now.
    """
    by_id = {c.candidate_id: c for c in existing}
    added, reopened, kept = 0, 0, 0

    for candidate in incoming:
        previous = by_id.get(candidate.candidate_id)
        if not previous:
            by_id[candidate.candidate_id] = candidate
            added += 1
            continue
        if candidate.change == "UPDATED" and previous.state in (APPROVED, REJECTED):
            candidate.state = NEEDS_REVIEW
            candidate.collected_at = previous.collected_at
            by_id[candidate.candidate_id] = candidate
            reopened += 1
            continue
        if previous.state in (APPROVED, REJECTED, DUPLICATE):
            kept += 1
            continue
        candidate.state = previous.state
        candidate.collected_at = previous.collected_at
        by_id[candidate.candidate_id] = candidate

    return list(by_id.values()), {"added": added, "reopened": reopened,
                                  "kept_decided": kept}


def to_needs_review(candidates):
    """COLLECTED -> NEEDS_REVIEW. The only transition this module performs.

    It is the one transition `stewardship/lifecycle.py` marks as machine
    permitted on the way in: collecting and queueing are automatable, judging
    is not.
    """
    moved = 0
    for candidate in candidates:
        if candidate.state == COLLECTED and not candidate.duplicate_of:
            candidate.state = NEEDS_REVIEW
            moved += 1
    return moved


def summary(candidates):
    counts = {}
    for candidate in candidates or []:
        counts[candidate.state] = counts.get(candidate.state, 0) + 1
    by_type = {}
    for candidate in candidates or []:
        if candidate.state == NEEDS_REVIEW:
            by_type[candidate.classified_as] = by_type.get(candidate.classified_as, 0) + 1
    return {
        "total": len(candidates or []),
        "by_state": dict(sorted(counts.items())),
        "awaiting_review_by_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
    }
