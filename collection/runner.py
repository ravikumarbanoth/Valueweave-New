#!/usr/bin/env python3
"""
The run — registry in, review queue out.

    for each due source
        fetch conditionally  ──▶ 304?  stop, cost was one request with no body
        parse                     the registry names the parser; nothing sniffs
        detect                    per item, against the hashes we stored
        classify                  by rule, carrying the words that fired
        dedupe                    within the run and against the queue
        queue                     as COLLECTED, then NEEDS_REVIEW
        record state              what we saw, so the next run can compare

Every stage is a module that can be used on its own and tested on its own. This
file is the sequencing and nothing else — no parsing logic, no rules, no HTTP.

WHAT IT CANNOT DO
-----------------
Write to `packages/`. Write to the knowledge graph. Write to Supabase. Approve
anything. The output is a diff in `collection/state/review_queue.jsonl` and a
line in the run log. A person reads the diff.

WHY THE EXISTING ENGINE DOES THE FETCHING
------------------------------------------
`knowledge_engine/collectors/` and `knowledge_engine/parsers/` were built for
exactly this and have 117 tests. What they never had was a caller. This is the
caller. The one thing they were missing — conditional requests — was added to
`_io.read_source` as five additive lines rather than reimplemented here, so
every collector gained the capability and none of their tests changed.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from collection import classify as classifier
from collection import detect, dedupe, registry, review
from knowledge_engine.parsers.base import ParseError


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


#: JSON Feed puts its entries under `items`; a plain JSON API might use `data`
#: or `results`. The JSON parser takes a record path, and rather than make every
#: registry row carry one, these are tried in order and the first list of
#: objects wins. A source that needs something else says so in `notes` and gets
#: a `record_path` — which is a registry change, not a code change.
JSON_RECORD_PATHS = ("items", "data", "records", "results", "entries", "")


@dataclass
class SourceRun:
    source_id: str
    status: str = "ok"          # ok | not_modified | skipped | error
    error: str = ""
    http_status: int = 0
    duration_ms: int = 0
    records: int = 0
    changes: dict = field(default_factory=dict)
    classified: dict = field(default_factory=dict)
    duplicates: dict = field(default_factory=dict)
    queued: int = 0


@dataclass
class RunReport:
    started_at: str = field(default_factory=_now)
    finished_at: str = ""
    sources: list = field(default_factory=list)
    queue: dict = field(default_factory=dict)
    merged: dict = field(default_factory=dict)
    dry_run: bool = True

    @property
    def failed(self):
        return [s for s in self.sources if s.status == "error"]

    def as_dict(self):
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "dry_run": self.dry_run,
            "sources": [vars(s) for s in self.sources],
            "queue": self.queue,
            "merged": self.merged,
            "failures": len(self.failed),
        }


def _conditional_headers(state):
    """What we already know, offered back to the server.

    An `ETag` is exact and preferred. `Last-Modified` is a fallback with
    one-second resolution, which is why both are sent when both are known —
    a server that ignores one usually honours the other.
    """
    headers = {}
    if state.etag:
        headers["If-None-Match"] = state.etag
    if state.last_modified:
        headers["If-Modified-Since"] = state.last_modified
    return headers


def _parse(source, payload):
    """Parser from the registry, with the JSON record path tried in order."""
    parser = registry.resolve(source.parser)()
    if source.parser.endswith("JSONParser"):
        last_error = None
        for path in JSON_RECORD_PATHS:
            try:
                records = parser.parse(payload, record_path=path) if path else parser.parse(payload)
                if records:
                    return records
            except (ParseError, KeyError, TypeError) as exc:
                last_error = exc
        if last_error:
            raise ParseError(f"no usable record path in {JSON_RECORD_PATHS}: {last_error}")
        return []
    return parser.parse(payload)


def run_source(source, known_titles=None, use_conditional=True):
    """One source, all the way to candidates. Never raises."""
    run = SourceRun(source_id=source.source_id)
    started = time.monotonic()

    if not source.runnable:
        run.status = "skipped"
        run.error = f"status={source.status}"
        return run, [], None

    try:
        collector = registry.resolve(source.collector)()
    except registry.RegistryError as exc:
        run.status, run.error = "error", str(exc)
        return run, [], None

    headers = _conditional_headers(source.fetch) if use_conditional else {}
    result = collector.fetch(source.url, headers=headers or None)
    run.duration_ms = int((time.monotonic() - started) * 1000)
    run.http_status = int(result.metadata.get("http_status") or 0)

    if not result.ok:
        run.status, run.error = "error", result.error or "fetch failed"
        return run, [], None

    if result.metadata.get("not_modified"):
        run.status = "not_modified"
        run.changes = detect.ChangeSet(source.source_id, not_modified=True).summary
        return run, [], result

    digest = detect.payload_hash(result.payload)
    payload_changed = digest != source.fetch.content_hash

    try:
        records = _parse(source, result.payload)
    except ParseError as exc:
        run.status, run.error = "error", f"parse failed: {exc}"
        return run, [], result

    run.records = len(records)
    changes = detect.detect(
        source.source_id, records, source.fetch.item_hashes,
        key_field=source.item_key, payload_changed=payload_changed,
    )
    run.changes = changes.summary

    actionable = changes.actionable
    classifications = [classifier.classify(c.record, forced=source.classify_as)
                       for c in actionable]
    run.classified = classifier.distribution(classifications)

    found = dedupe.dedupe([(c.key, c.record) for c in actionable],
                          known_titles=known_titles)
    run.duplicates = found.summary

    candidates = []
    for change, classification in zip(actionable, classifications):
        cid = review.candidate_id(source.source_id, change.key)
        duplicate_key = found.duplicate_of.get(change.key, "")
        version = found.versions.get(change.key, {})
        candidates.append(review.Candidate(
            candidate_id=cid,
            source_id=source.source_id,
            source_name=source.name,
            item_key=change.key,
            title=dedupe.title_of(change.record),
            url=str(change.record.get("link") or change.record.get("url") or source.url),
            published_at=str(change.record.get("pubDate")
                             or change.record.get("updated")
                             or change.record.get("date_published") or ""),
            change=change.status,
            classified_as=classification.target,
            classified_reason=classification.reason,
            is_entity=classification.is_entity,
            state=review.DUPLICATE if duplicate_key else review.COLLECTED,
            duplicate_of=review.candidate_id(source.source_id, duplicate_key) if duplicate_key else "",
            duplicate_reason=next((m[4] for group in found.groups
                                   for m in group.members if m[0] == change.key), ""),
            supersedes=review.candidate_id(source.source_id, version["updates"]) if version else "",
            raw=change.record,
        ))

    run.queued = len(candidates)

    # State is returned rather than written: the caller decides whether this was
    # a dry run. A runner that wrote state on a dry run would make the second
    # dry run see no changes and report a green pipeline that had done nothing.
    new_state = registry.FetchState(
        last_checked=_now(),
        last_ok=_now(),
        last_changed=_now() if changes.actionable else source.fetch.last_changed,
        etag=str(result.metadata.get("etag") or ""),
        last_modified=str(result.metadata.get("last_modified") or ""),
        content_hash=digest,
        consecutive_failures=0,
        last_error="",
        item_count=len(records),
        item_hashes=detect.next_hashes(source.fetch.item_hashes, changes),
    )
    return run, candidates, new_state


def run(sources=None, only=None, force=False, write=False, queue_path=None,
        state_path=None):
    """A full pass. `write=False` is the default, everywhere, on purpose."""
    sources = sources if sources is not None else registry.load()
    if only:
        wanted = set(only)
        sources = [s for s in sources if s.source_id in wanted]

    report = RunReport(dry_run=not write)
    queue = review.load(queue_path)
    known_titles = {c.item_key: c.title for c in queue if c.title}

    fresh_candidates = []
    for source in sources:
        if not force and not source.due():
            continue

        source_run, candidates, new_state = run_source(source, known_titles=known_titles)
        report.sources.append(source_run)
        fresh_candidates.extend(candidates)
        for candidate in candidates:
            if candidate.title:
                known_titles[candidate.item_key] = candidate.title

        if source_run.status == "error":
            source.fetch.last_checked = _now()
            source.fetch.consecutive_failures += 1
            source.fetch.last_error = source_run.error
        elif source_run.status == "not_modified":
            source.fetch.last_checked = _now()
            source.fetch.last_ok = _now()
            source.fetch.consecutive_failures = 0
            source.fetch.last_error = ""
        elif new_state is not None:
            source.fetch = new_state

    merged, stats = review.merge(queue, fresh_candidates)
    stats["promoted_to_review"] = review.to_needs_review(merged)
    report.merged = stats
    report.queue = review.summary(merged)
    report.finished_at = _now()

    if write:
        review.save(merged, queue_path)
        registry.save_state(sources, state_path)

    return report
