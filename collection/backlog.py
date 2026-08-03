#!/usr/bin/env python3
"""
What people looked for and did not find.

THE INPUT THAT DID NOT EXIST
-----------------------------
`search_events` has been in the schema since migration 004 and
`frontend/lib/search-tracking.js` has been in the repository just as long. The
admin page at /admin/search-intelligence renders a panel called "No-Results
Searches — content gaps" over an empty table, and says so in its own copy:

    "No data yet. Add trackSearch() calls from search inputs using
     lib/search-tracking.js."

`trackSearch` had ZERO callers. Every no-result search since launch was
discarded at the moment it happened. This milestone wires it (see
components/search/LiveSearch.jsx) so the backlog has something to read.

WHAT THIS PRODUCES, AND WHAT IT REFUSES TO PRODUCE
---------------------------------------------------
It produces a RESEARCH SUGGESTION: a term, how often it was searched, how many
people, and whether the search engine understood the words but held no data.
It is a work item for a researcher.

It does not produce knowledge. The temptation this file exists to resist is
obvious and expensive: "Lift Technician" is searched forty times, we hold
nothing, and generating a plausible entity would make the search work
immediately. That entity would be a fabricated claim about the labour market of
Telangana, published under a badge that says we checked it against an official
source. The rule the whole repository runs on — never fabricate; use
PENDING_VERIFICATION where a fact cannot be confirmed — is the same rule here,
one level up: a gap in coverage is reported as a gap.

TWO SIGNALS, WEIGHTED DIFFERENTLY
----------------------------------
`search_events` is passive: someone typed and left. `user_requests` is active:
someone filled in a form asking for it. A request is worth more than a search
because it cost the person something, and because it usually carries a sentence
explaining what they actually wanted.
"""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG_PATH = ROOT / "collection" / "state" / "research_backlog.json"

#: A term searched fewer times than this is one person trying spellings, not a
#: gap in coverage. Set low because the corpus is small and the audience is
#: still growing — it is a floor against noise, not a popularity contest.
MIN_SEARCHES = 3

#: One person searching the same thing twenty times is one person. Distinct
#: sessions matter more than raw count, and the ranking says so.
SEARCH_WEIGHT = 1.0
REQUEST_WEIGHT = 5.0


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Suggestion:
    term: str
    searches: int = 0
    requests: int = 0
    distinct_days: int = 0
    score: float = 0.0
    understood_as: str = ""
    example_request: str = ""
    suggested_category: str = ""
    status: str = "OPEN"
    first_seen: str = ""
    last_seen: str = ""

    def to_dict(self):
        return asdict(self)


def _day(timestamp):
    return str(timestamp or "")[:10]


def build(search_events=None, user_requests=None, resolver=None, classifier=None,
          min_searches=MIN_SEARCHES):
    """Turn raw signals into ranked research suggestions.

    `search_events` — rows of {query, results_count, created_at}
    `user_requests` — rows of {title, description, created_at, status}
    `resolver`      — optional callable(term) -> the English concept the search
                      vocabulary resolved it to, or "". Passing it in rather
                      than importing keeps this module free of the frontend:
                      the vocabulary is JavaScript, and reaching for it here
                      would make the backlog untestable without node.
    `classifier`    — optional callable(term) -> a suggested target category.
    """
    searches = Counter()
    days = defaultdict(set)
    first, last = {}, {}

    for row in search_events or []:
        query = str(row.get("query") or "").strip().lower()
        if not query:
            continue
        # Only the failures. A term that returns results is not a gap, however
        # popular — that is the analytics page's job, not this one's.
        if int(row.get("results_count") or 0) > 0:
            continue
        searches[query] += 1
        stamp = str(row.get("created_at") or "")
        days[query].add(_day(stamp))
        if stamp:
            first[query] = min(first.get(query, stamp), stamp)
            last[query] = max(last.get(query, stamp), stamp)

    requests = Counter()
    examples = {}
    for row in user_requests or []:
        title = str(row.get("title") or "").strip().lower()
        if not title or str(row.get("status") or "pending") != "pending":
            continue
        requests[title] += 1
        if title not in examples:
            examples[title] = str(row.get("description") or "")[:280]
        stamp = str(row.get("created_at") or "")
        days[title].add(_day(stamp))
        if stamp:
            first[title] = min(first.get(title, stamp), stamp)
            last[title] = max(last.get(title, stamp), stamp)

    suggestions = []
    for term in set(searches) | set(requests):
        search_count = searches[term]
        request_count = requests[term]
        # A single request is enough on its own — somebody asked in words.
        if search_count < min_searches and request_count == 0:
            continue
        distinct = len({d for d in days[term] if d})
        suggestions.append(Suggestion(
            term=term,
            searches=search_count,
            requests=request_count,
            distinct_days=distinct,
            # Distinct days multiplies rather than adds: forty searches on one
            # day is a burst, four searches on four days is a standing need.
            score=round((search_count * SEARCH_WEIGHT + request_count * REQUEST_WEIGHT)
                        * max(distinct, 1) ** 0.5, 2),
            understood_as=(resolver(term) if resolver else "") or "",
            example_request=examples.get(term, ""),
            suggested_category=(classifier(term) if classifier else "") or "",
            first_seen=first.get(term, ""),
            last_seen=last.get(term, ""),
        ))

    suggestions.sort(key=lambda s: (-s.score, s.term))
    return suggestions


def merge(existing, incoming):
    """Keep decisions. A suggestion someone marked DONE or WONT_DO stays that
    way; only its counts refresh, so a closed item cannot silently reopen and
    reappear at the top of the list every week."""
    by_term = {s.term: s for s in existing}
    for suggestion in incoming:
        previous = by_term.get(suggestion.term)
        if previous and previous.status != "OPEN":
            previous.searches = suggestion.searches
            previous.requests = suggestion.requests
            previous.distinct_days = suggestion.distinct_days
            previous.last_seen = suggestion.last_seen
            continue
        if previous:
            suggestion.first_seen = previous.first_seen or suggestion.first_seen
            suggestion.status = previous.status
        by_term[suggestion.term] = suggestion
    return sorted(by_term.values(), key=lambda s: (s.status != "OPEN", -s.score, s.term))


def load(path=None):
    path = Path(path or BACKLOG_PATH)
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Suggestion(**{k: v for k, v in row.items()
                          if k in Suggestion.__dataclass_fields__})
            for row in raw.get("suggestions", [])]


def save(suggestions, path=None):
    path = Path(path or BACKLOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "written_at": _now(),
        "note": ("Gaps, not knowledge. Each row is a topic people looked for and "
                 "ValueWeave does not cover. Nothing here may be turned into an "
                 "entity without research against a public source."),
        "open": sum(1 for s in suggestions if s.status == "OPEN"),
        "suggestions": [s.to_dict() for s in suggestions],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path
