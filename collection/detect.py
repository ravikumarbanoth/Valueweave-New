#!/usr/bin/env python3
"""
Change detection, at two levels.

WHY TWO
-------
A feed and the items in it change for different reasons and at different rates.

  TRANSPORT   Did the server say anything new? `ETag` and `Last-Modified` in,
              `304 Not Modified` out. Costs one request with no body and, on a
              well-behaved server, ends the run there. This is the level that
              makes "don't download everything every day" true.

  ITEM        Did any RECORD change? A feed whose <lastBuildDate> ticks hourly
              has a different body on every fetch and identical items. Hashing
              the whole payload would call that a change every hour and put a
              hundred unchanged records into the review queue — which is how a
              review queue stops being read.

So the payload hash is a fast path, and the item hashes are the answer.

THE FOUR OUTCOMES, AND THE ONE THAT IS NOT A DELETE
----------------------------------------------------
    NEW          a key we have never seen
    UPDATED      a key we have seen, with a different payload hash
    UNCHANGED    a key we have seen, identical
    DISAPPEARED  a key we saw last time and did not see now

DISAPPEARED is deliberately not called DELETED. A news feed holds twenty items
and drops the twenty-first; that item did not stop being true, it fell off the
end of a window. Treating it as a deletion would retire real knowledge because
a publisher paginated.

This mirrors the decision knowledge_sync/changes.py already made for Git ->
Supabase, where a row vanishing from a package is a SOFT delete because "a
dataset was regenerated" is a likelier explanation than "the fact stopped being
true". Same reasoning, one layer earlier.

REUSING THE MANIFEST PATTERN
-----------------------------
knowledge_sync compares against a committed manifest rather than querying the
target, because that makes a plan reproducible offline and makes tampering
visible. `collection/state/fetch_state.json` is the same idea for sources: the
record of what we last saw, comparable without a network.
"""

import hashlib
import json
from dataclasses import dataclass, field

NEW, UPDATED, UNCHANGED, DISAPPEARED = "NEW", "UPDATED", "UNCHANGED", "DISAPPEARED"

#: Fields excluded from an item's hash because they describe the FETCH rather
#: than the item. A feed that stamps every item with the time it was served
#: would otherwise report every item as updated on every run.
VOLATILE_FIELDS = {
    "lastbuilddate", "pubdate_fetched", "fetched_at", "generator",
    "ttl", "docs", "_collected_at", "_fetched_at",
}


def payload_hash(payload):
    """A stable hash of raw bytes or text."""
    data = payload if isinstance(payload, bytes) else str(payload or "").encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def item_hash(record):
    """A stable hash of one parsed record, ignoring volatile fields.

    Sorted keys and a JSON dump rather than `hash()`: Python's hash is salted
    per process, so a state file written by one run would disagree with the
    next for no reason anyone could debug.
    """
    stable = {k: v for k, v in sorted((record or {}).items())
              if k.lower() not in VOLATILE_FIELDS}
    encoded = json.dumps(stable, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def item_key(record, key_field, url=""):
    """The identity of one item.

    `key_field` comes from the registry — `guid` for RSS, `id` for Atom and
    JSON Feed, a real primary key for a register like a training-provider list.

    When it is absent or empty, identity falls back to a hash of the whole
    record. That is not as good — an item whose description gains a comma
    becomes a different item — but it is honest, and the alternative (dropping
    items with no key) silently loses records from feeds that do not publish
    one. The registry's `item_key` column exists precisely so this fallback is
    rare and visible.
    """
    if key_field:
        value = str((record or {}).get(key_field) or "").strip()
        if value:
            return value
    for fallback in ("link", "url", "id", "guid"):
        value = str((record or {}).get(fallback) or "").strip()
        if value:
            return value
    return f"sha:{item_hash(record)}"


@dataclass
class ItemChange:
    key: str
    status: str
    record: dict = field(default_factory=dict)
    hash: str = ""
    previous_hash: str = ""


@dataclass
class ChangeSet:
    source_id: str
    payload_changed: bool = True
    not_modified: bool = False
    items: list = field(default_factory=list)

    def of(self, status):
        return [c for c in self.items if c.status == status]

    @property
    def actionable(self):
        """What a human would have to look at. UNCHANGED never reaches a queue,
        and DISAPPEARED is reported but is not a candidate — it is a signal that
        a window moved, not a new fact."""
        return self.of(NEW) + self.of(UPDATED)

    @property
    def summary(self):
        return {
            "source_id": self.source_id,
            "not_modified": self.not_modified,
            "payload_changed": self.payload_changed,
            "new": len(self.of(NEW)),
            "updated": len(self.of(UPDATED)),
            "unchanged": len(self.of(UNCHANGED)),
            "disappeared": len(self.of(DISAPPEARED)),
        }


def detect(source_id, records, previous_hashes, key_field="", not_modified=False,
           payload_changed=True):
    """Classify every parsed record against what we saw last time."""
    changes = ChangeSet(source_id=source_id, payload_changed=payload_changed,
                        not_modified=not_modified)
    if not_modified:
        return changes

    previous = dict(previous_hashes or {})
    seen = set()
    for record in records or []:
        key = item_key(record, key_field)
        digest = item_hash(record)
        seen.add(key)
        if key not in previous:
            status = NEW
        elif previous[key] != digest:
            status = UPDATED
        else:
            status = UNCHANGED
        changes.items.append(ItemChange(key=key, status=status, record=record,
                                        hash=digest, previous_hash=previous.get(key, "")))

    for key, digest in previous.items():
        if key not in seen:
            changes.items.append(ItemChange(key=key, status=DISAPPEARED,
                                            previous_hash=digest))
    return changes


def next_hashes(previous_hashes, changes):
    """The hash map to store after a run.

    A DISAPPEARED key is KEPT. If it comes back — a feed window scrolls, an
    item is reinstated — it should be recognised as the item we already
    reviewed, not offered again as new. The cost is a state file that only
    grows; `forget_disappeared()` exists for when a source is retired.
    """
    out = dict(previous_hashes or {})
    for change in changes.items:
        if change.status in (NEW, UPDATED, UNCHANGED):
            out[change.key] = change.hash
    return out


def forget_disappeared(hashes, changes):
    """Drop keys that are no longer in the feed. Explicit, never automatic."""
    gone = {c.key for c in changes.of(DISAPPEARED)}
    return {k: v for k, v in (hashes or {}).items() if k not in gone}
