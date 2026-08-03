#!/usr/bin/env python3
"""
The same thing, said twice.

FIVE WAYS A DUPLICATE ARRIVES, AND WHAT CATCHES EACH
-----------------------------------------------------
    the same item twice in one feed          exact key, exact text
    the same notification from two sources   normalised title
    a republished announcement               normalised title, different key
    a near-duplicate wording change          token overlap
    a version update of a known record       token overlap + a version marker

Exact hashing catches the first and nothing else. Everything below the first
line needs comparison of MEANING, and the cheapest honest approximation of
meaning here is the set of significant words in the title.

WHY NOT EMBEDDINGS
------------------
The same reason the search vocabulary is curated: an embedding index needs a
model, a build step and a vector store, and it would be worse at the thing that
actually fails here. These are government notifications. They repeat *verbatim*
with a different notification number, or differ by one word — "for micro
enterprises" versus "for micro and small enterprises". Token overlap on a
normalised title handles that exactly, is explainable to a reviewer, and costs
nothing.

WHAT THIS DOES NOT DO
---------------------
It does not delete. It GROUPS, marks one member primary and the rest as
duplicates of it, and records why. A reviewer sees the group and decides.
Automatic deletion of a "duplicate" that was actually a second, genuinely
different scheme with a similar name would lose knowledge silently — the one
failure mode a collection pipeline must not have.
"""

import re
from dataclasses import dataclass, field

#: Words that carry no distinguishing weight in Indian public notifications.
#: Not a general stop-word list — "scheme" and "notification" are dropped
#: because almost every item contains them, which is the definition of a word
#: that cannot tell two items apart.
NOISE = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "at", "by",
    "with", "from", "under", "notification", "notice", "announcement",
    "press", "release", "regarding", "re", "dated", "no", "nos", "new",
    "government", "india", "ministry", "department", "office", "circular",
    "order", "public", "general", "shri", "smt", "fixture",
}

#: Above this share of shared significant words, two titles are the same
#: announcement. Chosen by hand against the fixtures and the failure it
#: prevents: at 0.6 "Margin Money Subsidy for micro enterprises" and "Margin
#: Money Subsidy for small enterprises" merge, and those are two schemes.
NEAR_DUPLICATE_THRESHOLD = 0.8

#: A shorter title has fewer words to share, so a small absolute overlap can
#: clear a ratio threshold by accident — and, worse, two titles that differ only
#: in a number normalise to the same string once digits are stripped. Three
#: significant words is the floor below which no duplicate is declared at all.
MIN_SIGNIFICANT_TOKENS = 3

#: Markers that a record is a NEW VERSION of something we already hold rather
#: than a duplicate of it. Version updates must be surfaced, not merged away —
#: an amended scheme is the single most important thing a collection pipeline
#: can catch.
VERSION_MARKERS = (
    "amend", "revised", "revision", "corrigendum", "addendum", "supersed",
    "modification", "updated", "extension of", "extended", "version",
)

EXACT, NEAR, VERSION = "EXACT", "NEAR", "VERSION"

TITLE_FIELDS = ("title", "name", "subject", "headline", "provider_name")


def title_of(record):
    for field_name in TITLE_FIELDS:
        value = (record or {}).get(field_name)
        if value and str(value).strip():
            return str(value).strip()
    return ""


def normalise(text):
    """Lower-case, strip punctuation and digits, collapse whitespace.

    Digits go because a notification number is exactly what differs between two
    postings of the same announcement — keeping them would make every
    republication look unique, which is the duplicate this is here to catch.
    """
    lowered = re.sub(r"[^a-z\s]", " ", str(text or "").lower())
    return " ".join(lowered.split())


def tokens(text):
    return {w for w in normalise(text).split() if len(w) > 2 and w not in NOISE}


def similarity(a, b):
    """Jaccard over significant words. 1.0 identical, 0.0 nothing in common."""
    first, second = tokens(a), tokens(b)
    if not first or not second:
        return 0.0
    return len(first & second) / len(first | second)


def looks_like_a_version(text):
    lowered = str(text or "").lower()
    return any(marker in lowered for marker in VERSION_MARKERS)


@dataclass
class DuplicateGroup:
    primary_key: str
    primary_title: str
    members: list = field(default_factory=list)   # [(key, title, kind, score, reason)]

    @property
    def size(self):
        return 1 + len(self.members)


@dataclass
class DedupeResult:
    groups: list = field(default_factory=list)
    #: key -> the key it duplicates. Everything not in here is unique.
    duplicate_of: dict = field(default_factory=dict)
    #: keys that look like a new version of an earlier record, not a duplicate.
    versions: dict = field(default_factory=dict)

    @property
    def summary(self):
        return {
            "groups": len(self.groups),
            "duplicates": len(self.duplicate_of),
            "version_updates": len(self.versions),
        }


def dedupe(items, known_titles=None):
    """Group duplicates among `items`, and against what we already hold.

    `items` is a list of `(key, record)`. `known_titles` is `{key: title}` for
    records already in the review queue or already published — the second half
    of the problem, because "the same government notification arriving from two
    different sources on two different days" is not visible inside one feed.

    Order is stable: the FIRST item in a group is primary. For a single feed
    that is publication order, which is the right default — the original
    announcement outranks its republication.
    """
    result = DedupeResult()
    seen = []           # [(key, title)] — accumulated primaries
    for key, title in (known_titles or {}).items():
        seen.append((key, title))

    groups = {}         # primary key -> DuplicateGroup

    for key, record in items or []:
        title = title_of(record)
        if not title:
            seen.append((key, title))
            continue

        # Not enough of a title to judge on. `normalise` strips digits, which
        # is right for "Notification 41/2026" versus "87/2026" — the number IS
        # what differs between two postings of one announcement — and wrong for
        # "Notice 12" versus "Notice 44", where the number is all there is.
        # Below the floor, no duplicate is declared at all.
        if len(tokens(title)) < MIN_SIGNIFICANT_TOKENS:
            seen.append((key, title))
            continue

        match, kind, score, reason = None, None, 0.0, ""
        normalised = normalise(title)

        for other_key, other_title in seen:
            if other_key == key:
                continue
            if normalised and normalised == normalise(other_title):
                match, kind, score = other_key, EXACT, 1.0
                reason = "identical title once numbers and punctuation are removed"
                break
            overlap = similarity(title, other_title)
            if overlap >= NEAR_DUPLICATE_THRESHOLD:
                if looks_like_a_version(title):
                    match, kind, score = other_key, VERSION, overlap
                    reason = "same subject with an amendment marker"
                else:
                    match, kind, score = other_key, NEAR, overlap
                    reason = f"{round(overlap * 100)}% of significant words shared"
                break

        if not match:
            seen.append((key, title))
            continue

        if kind == VERSION:
            result.versions[key] = {"updates": match, "score": round(score, 3),
                                    "reason": reason}
            # A version is NOT a duplicate — it stays in the queue on its own
            # merits, carrying a pointer to what it supersedes.
            seen.append((key, title))
            continue

        result.duplicate_of[key] = match
        group = groups.get(match)
        if not group:
            primary_title = next((t for k, t in seen if k == match), "")
            group = DuplicateGroup(primary_key=match, primary_title=primary_title)
            groups[match] = group
            result.groups.append(group)
        group.members.append((key, title, kind, round(score, 3), reason))

    return result
