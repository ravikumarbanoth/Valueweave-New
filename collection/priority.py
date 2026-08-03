#!/usr/bin/env python3
"""
Which candidate should a reviewer read first?

THE PROBLEM A FLAT QUEUE CREATES
---------------------------------
Every collected item is equal until something says otherwise, so a queue of
four hundred is read top to bottom until the reader gets tired — and the office
circular at position three gets the same attention as the state electronics
manufacturing policy at position two hundred. Reviewer time is the scarcest
thing in this whole pipeline, and an unordered queue spends it at random.

    ★★★★★  a major government scheme
    ★★★★★  an electronics manufacturing policy
    ★★★★☆  a skill development mission
    ★★★☆☆  an industry report
    ★★☆☆☆  a tender
    ★☆☆☆☆  an office circular

WHY THIS IS NINE SMALL RULES AND NOT ONE MODEL
-----------------------------------------------
Same reason as `classify.py`, and it matters more here. A priority score decides
what a person spends their morning on. If they cannot see WHY something is at
the top, they cannot tell a good ranking from a broken one — and the first time
the ranking is wrong and unexplainable, they stop trusting it and go back to
reading top to bottom, which is where we started.

So every factor returns points AND a sentence. `explain()` renders the sentence
list, and the CLI prints it next to the stars.

WHAT IT DELIBERATELY DOES NOT USE
----------------------------------
Recency alone. A feed that publishes hourly would otherwise own the top of the
queue permanently, and "published twenty minutes ago" is not a reason to read
something before a policy from last week. Recency is capped at a small bonus
and cannot lift an item a full star on its own.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

#: Score -> stars. The bands are wide on purpose: a scoring system with sixty
#: distinguishable levels invites arguments about a two-point difference that
#: means nothing. Five buckets is what a reviewer can act on.
STAR_BANDS = [(80, 5), (60, 4), (40, 3), (22, 2), (0, 1)]

#: How much a category is worth before anything else is considered. These are a
#: curator's ordering of what changes a student's options most — a scheme they
#: can apply to outranks an industry report about the sector they are in.
CATEGORY_POINTS = {
    "GovernmentScheme": 34,
    "BusinessOpportunity": 30,
    "Skill": 26,
    "TrainingProvider": 24,
    "Certification": 22,
    "MSME": 22,
    "Industry": 20,
    "FinancialInstitution": 18,
    "Crop": 16,
    "Institution": 16,
    "Machinery": 12,
    "Market": 12,
    "District": 12,
    "Research": 14,
    "Event": 8,
    "Job": 8,
    "Technology": 10,
    "News": 4,
    "UNCLASSIFIED": 2,
}

#: Phrases that raise or lower an item regardless of its category, because they
#: describe how much of a difference the item makes rather than what it is
#: about. A policy is a scheme AND a bigger deal than a circular is.
IMPACT_TERMS = {
    22: ("policy", "mission", "national programme", "national program",
         "state policy", "new scheme", "launched", "sanctioned"),
    14: ("subsidy", "grant", "financial assistance", "incentive", "margin money",
         "applications invited", "registration open", "empanelment"),
    8: ("guidelines", "eligibility", "amendment", "revised", "corrigendum",
        "extension of", "deadline"),
    -10: ("office order", "office circular", "office memorandum", "transfer",
          "posting", "seniority list", "holiday", "meeting notice", "minutes of"),
    -6: ("tender", "quotation", "auction", "e-procurement", "bid document"),
}

#: An item naming a place we cover is about our readers. One naming a place we
#: do not is national context at best.
STATE_TERMS = {
    "TG": ("telangana", "hyderabad"),
    "AP": ("andhra pradesh", "amaravati", "visakhapatnam", "vijayawada"),
    "IN": ("india", "bharat", "national", "all india"),
}


@dataclass
class Factor:
    name: str
    points: int
    reason: str


@dataclass
class Priority:
    score: int = 0
    stars: int = 1
    factors: list = field(default_factory=list)

    @property
    def bar(self):
        return "★" * self.stars + "☆" * (5 - self.stars)

    def explain(self):
        return [f"{f.points:+3d}  {f.reason}" for f in self.factors]

    def to_dict(self):
        return {"score": self.score, "stars": self.stars,
                "factors": [vars(f) for f in self.factors]}


def _text(candidate):
    raw = candidate.raw or {}
    parts = [candidate.title]
    for key in ("summary", "description", "content_text", "content"):
        if raw.get(key):
            parts.append(str(raw[key]))
    return " ".join(parts).lower()


def _age_days(candidate, now):
    stamp = candidate.published_at or candidate.collected_at
    for parse in (_iso, _rfc2822):
        value = parse(stamp)
        if value:
            return max(0.0, (now - value).total_seconds() / 86400)
    return None


def _iso(stamp):
    try:
        value = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _rfc2822(stamp):
    import email.utils                                              # noqa: PLC0415
    try:
        value = email.utils.parsedate_to_datetime(str(stamp))
    except (TypeError, ValueError):
        return None
    return value if value and value.tzinfo else (value.replace(tzinfo=timezone.utc)
                                                 if value else None)


def score(candidate, source=None, demand=None, districts=(), now=None):
    """Rank one candidate.

    `source`    the registry row it came from — carries reliability and state.
    `demand`    {term: score} from the research backlog. An item about something
                people are actually searching for is worth reading first, and
                this is the only factor that connects the review queue to real
                users rather than to our own taxonomy.
    `districts` district names from the graph, so "in Medak" is recognised
                without a hand-written list that goes stale when a state
                reorganises its districts.
    """
    now = now or datetime.now(timezone.utc)
    text = _text(candidate)
    result = Priority()

    # ── what kind of thing it is ────────────────────────────────────────────
    points = CATEGORY_POINTS.get(candidate.classified_as, 6)
    result.factors.append(Factor("category", points,
                                 f"{candidate.classified_as} is worth {points}"))

    # ── how much of a difference it makes ───────────────────────────────────
    for value, terms in IMPACT_TERMS.items():
        hit = next((t for t in terms if t in text), None)
        if hit:
            result.factors.append(Factor("impact", value, f"reads as “{hit}”"))

    # ── who published it ────────────────────────────────────────────────────
    if source is not None:
        # Reliability is 0-100 and declared. Scaled to ±10 so a trusted source
        # cannot promote a circular past a scheme, only break a tie.
        reliability = int((source.reliability - 50) / 5)
        if reliability:
            result.factors.append(Factor(
                "source", reliability,
                f"{source.name[:40]} is rated {source.reliability}/100"))
        if source.state in ("TG", "AP"):
            result.factors.append(Factor("source_state", 6,
                                         f"a {source.state} source"))

    # ── where it applies ────────────────────────────────────────────────────
    for state, terms in STATE_TERMS.items():
        hit = next((t for t in terms if t in text), None)
        if not hit:
            continue
        points = 12 if state in ("TG", "AP") else 4
        result.factors.append(Factor("state", points, f"names “{hit}”"))
        break

    named = [d for d in districts if d and len(d) > 3 and d.lower() in text]
    if named:
        result.factors.append(Factor(
            "district", 10, f"names {', '.join(sorted(named)[:3])}"))

    # ── whether anybody is asking ───────────────────────────────────────────
    if demand:
        wanted = sorted(
            ((term, value) for term, value in demand.items()
             if len(term) > 3 and term in text),
            key=lambda pair: -pair[1])
        if wanted:
            term, value = wanted[0]
            points = min(20, 6 + int(value))
            result.factors.append(Factor(
                "search_demand", points,
                f"people search for “{term}” and we hold nothing"))

    # ── how fresh ───────────────────────────────────────────────────────────
    age = _age_days(candidate, now)
    if age is not None:
        # Capped low and deliberately: an hourly feed would otherwise own the
        # top of the queue forever, and "twenty minutes ago" is not a reason to
        # read something before last week's policy.
        points = 6 if age <= 3 else 3 if age <= 14 else 0 if age <= 90 else -4
        if points:
            result.factors.append(Factor(
                "recency", points,
                f"published {int(age)} day{'' if int(age) == 1 else 's'} ago"))

    # ── whether we have probably seen it ────────────────────────────────────
    if candidate.duplicate_of:
        result.factors.append(Factor("duplicate", -40, "already in the queue"))
    elif candidate.supersedes:
        # An amendment to something we hold is the single most valuable thing
        # in a collection pipeline: knowledge going stale is invisible, and
        # this is the only signal that it has.
        result.factors.append(Factor("supersedes", 18,
                                     "appears to amend something we already have"))

    if candidate.change == "UPDATED":
        result.factors.append(Factor("changed", 8, "the source edited this item"))

    result.score = max(0, sum(f.points for f in result.factors))
    result.stars = next(stars for floor, stars in STAR_BANDS if result.score >= floor)
    return result


def rank(candidates, sources=None, demand=None, districts=(), now=None):
    """Score every candidate and return them most-important first.

    The score is written onto the candidate as `priority` and `priority_stars`
    so it survives into the queue file and a reviewer sees it without running
    anything.
    """
    by_id = {s.source_id: s for s in (sources or [])}
    scored = []
    for candidate in candidates or []:
        result = score(candidate, source=by_id.get(candidate.source_id),
                       demand=demand, districts=districts, now=now)
        candidate.priority = result.score
        candidate.priority_stars = result.stars
        candidate.priority_reason = "; ".join(f.reason for f in result.factors[:3])
        scored.append((result, candidate))

    scored.sort(key=lambda pair: (-pair[0].score, pair[1].candidate_id))
    return [candidate for _result, candidate in scored]


def district_names(entities_csv=None):
    """District names from the graph, for the district-relevance factor.

    Read from the graph rather than hard-coded, so a state reorganising its
    districts — which both of these have done recently — updates this by
    rebuilding the graph rather than by somebody remembering.
    """
    import csv                                                      # noqa: PLC0415
    from pathlib import Path                                        # noqa: PLC0415
    path = Path(entities_csv or
                Path(__file__).resolve().parent.parent
                / "knowledge_graph" / "entities" / "entities.csv")
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return [row["canonical_name"] for row in csv.DictReader(fh)
                if row["entity_type"] == "District"]


def demand_from_backlog(suggestions):
    """{term: score} from the research backlog, for the demand factor."""
    return {s.term: s.score for s in (suggestions or []) if s.status == "OPEN"}
