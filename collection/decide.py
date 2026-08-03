#!/usr/bin/env python3
"""
The two verbs the pipeline was missing: deciding, and promoting.

WHAT WAS ACTUALLY BROKEN
------------------------
The collection framework ended at a review queue and the stewardship framework
began at an entity that already exists in `entities.csv`. Between them was a
gap nobody could cross:

    collection.cli   had no verb to approve a candidate
    stewardship.cli  could only act on an entity_id already in the graph

A candidate is not an entity. So `collection.cli queue` printed twelve rows and
there was no command — none — that could accept one. The pipeline was two
working halves with nothing joining them.

This module is the join, and it is deliberately thin: it records decisions in
the ledger that already exists, and it writes package rows in the shape the
packages already use.

WHY THE DECISION GOES IN THE STEWARDSHIP LEDGER
------------------------------------------------
Because a second audit trail is not an audit trail. `stewardship/ledger.py` is
append-only, validates every transition through `check_transition`, and refuses
rather than warns. Recording a candidate approval anywhere else would give
ValueWeave two answers to "has a person approved this?", which is the same
mistake as two search implementations and considerably more expensive when the
answer matters.

So a candidate transitions through the same lifecycle as everything else:

    COLLECTED -> REVIEWED -> APPROVED

`review` and `approve` are two commands, exactly as in `stewardship/cli.py`,
because recording a judgement and accepting responsibility for it are different
acts and should fail independently.

WHAT PROMOTION DOES AND DOES NOT CLAIM
---------------------------------------
An approved candidate becomes ONE ROW in a package dataset, with:

    · the fields the source genuinely supplied — name, source URL, dates
    · PENDING_VERIFICATION in every other column
    · verification_status = VST-NEEDS_REVIEW

That is the honest shape. A press release announcing a scheme is a NOTIFICATION
about a scheme, not the scheme record: it does not carry the eligibility, the
subsidy rate, the portal or the ministry. Filling those from the announcement
text would be exactly the fabrication this repository exists not to do.

So approval means "this belongs in the graph and is worth researching", and the
research that fills the PENDING cells is a separate human step — after which
`stewardship.cli approve` and `apply --write` mark it verified. That is how all
647 existing rows got their status, and this adds no new rule.
"""

import csv
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

from collection import review
from stewardship.ledger import ReviewLedger
from stewardship.lifecycle import LifecycleState, TransitionError

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"

#: The sentinel. Not invented here — it is the repository's existing mechanism
#: for "this could not be sourced", used in 2,460 cells across the packages.
PENDING = "PENDING_VERIFICATION"
NEEDS_REVIEW = "VST-NEEDS_REVIEW"

#: Where an approved candidate of each type becomes a row. Only the types the
#: sync actually projects — promoting into a dataset no TableSpec reads would
#: put a row in Git that never reaches Supabase and never becomes searchable,
#: which is a silent failure dressed as a success.
#:
#: `key` is the dataset's primary key column, matching knowledge_sync/config.py.
#: `name` is the column the entity's canonical_name comes from, matching
#: knowledge_graph/build_graph.py.
TARGETS = {
    "GovernmentScheme": {
        "package": "Package007_Government_Schemes",
        "dataset": "government_schemes.csv",
        "key": "scheme_id",
        "name": "scheme_name",
        "prefix": "sch",
    },
    "Skill": {
        "package": "Package006_Skills_and_Training",
        "dataset": "skills.csv",
        "key": "skill_id",
        "name": "skill_name",
        "prefix": "skl",
    },
    "MSME": {
        "package": "Package008_MSME",
        "dataset": "msme_businesses.csv",
        "key": "business_id",
        "name": "business_name",
        "prefix": "msm",
    },
    "Crop": {
        "package": "Package005_Agriculture",
        "dataset": "crops.csv",
        "key": "crop_id",
        "name": "crop_name",
        "prefix": "crp",
    },
}

#: Columns a feed item can genuinely fill, and where from. Everything else gets
#: the sentinel. Kept small on purpose: every entry here is a claim that the
#: feed really carries that field, and a wrong one is a fabricated fact.
def _from_candidate(candidate, column):
    raw = candidate.raw or {}
    today = date.today().isoformat()
    if column in ("source_url",):
        return candidate.url or raw.get("link") or raw.get("url") or ""
    if column in ("collection_date", "created_at", "updated_at", "last_verified_date"):
        return today
    if column == "data_source":
        return candidate.source_name
    if column == "confidence_score":
        # Low and deliberately so: nothing about this row has been checked by a
        # person, and a confident-looking number on an unverified row is worse
        # than a modest one.
        return "40"
    if column == "verification_status":
        return NEEDS_REVIEW
    if column in ("status", "is_active"):
        return "PUBLISHED" if column == "status" else "TRUE"
    if column == "notes":
        return (f"Collected automatically from {candidate.source_name} "
                f"({candidate.source_id}) on {today}. Classified as "
                f"{candidate.classified_as} because it {candidate.classified_reason}. "
                f"Every PENDING_VERIFICATION field awaits research against the "
                f"official source.")
    if column in ("version",):
        return "1.0.0"
    if column in ("created_by", "reviewer"):
        return ""
    return None


class PromotionError(Exception):
    """Refuses rather than guesses. A promotion that silently wrote a row into
    the wrong dataset would be discovered by a reader, not by us."""


@dataclass
class Decision:
    candidate_id: str
    from_state: str
    to_state: str
    actor: str
    evidence: str = ""
    notes: str = ""


@dataclass
class PromotionPlan:
    rows: list = field(default_factory=list)     # [(dataset_path, row_dict, candidate)]
    skipped: list = field(default_factory=list)  # [(candidate_id, reason)]

    @property
    def summary(self):
        by_dataset = {}
        for path, _row, _c in self.rows:
            by_dataset[path.name] = by_dataset.get(path.name, 0) + 1
        return {"rows": len(self.rows), "by_dataset": by_dataset,
                "skipped": len(self.skipped)}


def _ledger():
    return ReviewLedger()


#: The one path through the lifecycle. Kept as a list rather than derived from
#: TRANSITIONS because the graph has legal shortcuts — the retroactive-review
#: edge — that a candidate must not take: it exists for the 647 rows that
#: reached PUBLISHED before a steward existed, not for something collected
#: yesterday.
_FORWARD = [LifecycleState.DRAFT, LifecycleState.COLLECTED, LifecycleState.VALIDATED,
            LifecycleState.REVIEWED, LifecycleState.APPROVED,
            LifecycleState.PUBLISHED]


def _path(current, target):
    """Every state between here and there, inclusive of the target."""
    if target == LifecycleState.ARCHIVED:
        return [LifecycleState.ARCHIVED]
    try:
        start = _FORWARD.index(current)
        end = _FORWARD.index(target)
    except ValueError as exc:
        raise PromotionError(f"{current.value} -> {target.value} is not a "
                             f"forward path") from exc
    if end <= start:
        raise PromotionError(f"{current.value} -> {target.value} is not forward")
    return _FORWARD[start + 1:end + 1]


#: The only three targets this command may aim at. PUBLISHED is reachable in
#: the lifecycle and must not be reachable from here: a row becomes PUBLISHED by
#: being included in a released package version, which is an act of the release
#: process, not of a reviewer clicking approve. Without this guard `_path` would
#: happily walk a candidate from COLLECTED all the way to PUBLISHED in one call.
DECIDABLE = {LifecycleState.REVIEWED.value, LifecycleState.APPROVED.value,
             LifecycleState.ARCHIVED.value}


def decide(candidate_id, to_state, actor, evidence="", notes="", queue_path=None,
           ledger=None):
    """Record one decision, in the queue and in the ledger.

    The ledger write happens FIRST. If the transition is illegal it raises and
    the queue is untouched, so the queue can never hold a state the audit trail
    does not justify. The reverse order would let a rejected transition still
    change what a reviewer sees.
    """
    if to_state not in DECIDABLE:
        raise PromotionError(
            f"{to_state} is not a decision a reviewer makes about a candidate. "
            f"Choose one of {sorted(DECIDABLE)}.")

    candidates = review.load(queue_path)
    match = next((c for c in candidates if c.candidate_id == candidate_id), None)
    if not match:
        raise PromotionError(f"no candidate {candidate_id!r} in the queue")

    ledger = ledger if ledger is not None else _ledger()
    current = ledger.current_state(candidate_id, default=LifecycleState.COLLECTED)
    started_at = current

    # Walk the lifecycle rather than jumping it.
    #
    # A candidate arrives COLLECTED, and the first human verb is `review`,
    # which targets REVIEWED — but the lifecycle requires VALIDATED in between,
    # and it is right to. What it does NOT require is that a person perform
    # that step: COLLECTED -> VALIDATED is machine-permitted, and the pipeline
    # genuinely did it — the payload parsed, the record was classified against
    # rules that named their evidence, and it was checked for duplicates.
    #
    # So the machine steps are recorded here, with what actually validated
    # them, at the moment a human first touches the candidate. Recording them
    # during collection instead would put hundreds of entries in an append-only
    # ledger for candidates nobody ever reads.
    for step in _path(current, LifecycleState.parse(to_state)):
        machine = step in (LifecycleState.VALIDATED, LifecycleState.COLLECTED)
        ledger.record(
            candidate_id, current.value, step.value,
            actor="" if machine else actor,
            evidence="" if machine else evidence,
            notes=(f"parsed, classified and de-duplicated by collection/runner.py"
                   if machine else notes),
            by_machine=machine)
        current = step

    # `record()` appends in memory; `flush()` is what makes it an audit trail.
    # Without this the decision existed only for the life of the process, and
    # the next command read a ledger that had never heard of it.
    ledger.flush()

    match.state = {
        LifecycleState.REVIEWED.value: review.NEEDS_REVIEW,
        LifecycleState.APPROVED.value: review.APPROVED,
    }.get(to_state, match.state)
    if to_state == LifecycleState.ARCHIVED.value:
        match.state = review.REJECTED

    review.save(candidates, queue_path)
    return Decision(candidate_id, started_at.value, to_state, actor, evidence, notes)


def approved(queue_path=None):
    return [c for c in review.load(queue_path) if c.state == review.APPROVED]


def _next_key(rows, key_column, prefix):
    """The next id in the dataset's own sequence.

    Read from the file rather than generated, because these ids appear in
    `package_local_id` and in every mapping dataset that references them, and a
    UUID where the dataset uses `sch-014` would be correct and unreadable.
    """
    highest = 0
    for row in rows:
        value = str(row.get(key_column) or "")
        tail = value.rsplit("-", 1)[-1]
        if tail.isdigit():
            highest = max(highest, int(tail))
    width = 3
    for row in rows:
        tail = str(row.get(key_column) or "").rsplit("-", 1)[-1]
        if tail.isdigit():
            width = len(tail)
            break
    return f"{prefix}-{highest + 1:0{width}d}"


def plan(candidates=None, queue_path=None, packages_dir=None):
    """What promotion would write. Never writes."""
    packages_dir = Path(packages_dir or PACKAGES)
    candidates = candidates if candidates is not None else approved(queue_path)
    result = PromotionPlan()

    for candidate in candidates:
        target = TARGETS.get(candidate.classified_as)
        if not target:
            result.skipped.append((
                candidate.candidate_id,
                f"{candidate.classified_as} has no dataset the sync projects — "
                f"a row there would never reach Supabase. Reclassify, or add a "
                f"TARGET once a TableSpec covers it."))
            continue

        path = packages_dir / target["package"] / "datasets" / target["dataset"]
        if not path.exists():
            result.skipped.append((candidate.candidate_id, f"missing dataset {path}"))
            continue

        with open(path, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            columns = list(reader.fieldnames or [])
            rows = list(reader)

        name = (candidate.title or "").strip()
        if not name:
            result.skipped.append((candidate.candidate_id, "no title to name the row"))
            continue
        if any(str(r.get(target["name"]) or "").strip().lower() == name.lower()
               for r in rows):
            result.skipped.append((
                candidate.candidate_id,
                f"{target['dataset']} already holds a row named {name!r}"))
            continue

        row = {}
        for column in columns:
            if column == target["key"]:
                row[column] = _next_key(rows, target["key"], target["prefix"])
            elif column == target["name"]:
                row[column] = name
            else:
                supplied = _from_candidate(candidate, column)
                # PENDING_VERIFICATION for everything the feed did not carry.
                # This is the line that keeps promotion honest: a scheme
                # announcement does not know its own subsidy rate, and writing
                # a plausible one would be the fabrication the whole repository
                # is built to avoid.
                row[column] = supplied if supplied is not None else PENDING
        result.rows.append((path, row, candidate))

    return result


def apply(promotion, write=False):
    """Append the planned rows. `write=False` by default, like everything else."""
    written = []
    if not write:
        return written
    for path, row, _candidate in promotion.rows:
        with open(path, encoding="utf-8", newline="") as fh:
            columns = list(csv.DictReader(fh).fieldnames or [])
        with open(path, "a", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=columns).writerow(
                {c: row.get(c, "") for c in columns})
        written.append(path)
    return written
