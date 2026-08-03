#!/usr/bin/env python3
"""
One number for "how good is the knowledge base", and seven you can argue with.

WHY A SINGLE SCORE IS DANGEROUS AND STILL WORTH HAVING
-------------------------------------------------------
A single number hides what it is made of, invites optimisation of the number
rather than the thing, and is usually wrong in some dimension nobody looked at.
It is worth having anyway, for one reason: it makes a TREND visible. "68 last
month, 71 today" is a sentence an operator can act on, where seven separate
tables are seven things nobody compares week to week.

So the score exists and the seven dimensions are always printed beside it, each
with its own number, its own formula stated in the code, and its own UNKNOWN.

    coverage       how much of what we said we would hold, we hold
    connectivity   how much of it leads somewhere
    freshness      how much of it was updated recently enough to trust
    verification   how much a person has actually stood behind
    research       how much is complete rather than PENDING_VERIFICATION
    diversity      how many independent sources it rests on
    popularity     how much of it anybody reads

UNKNOWN IS A RESULT
-------------------
`popularity` has no data: page views and search counts live in Supabase and
this module never fetches. Scoring it zero would drag the total down for a
reason that is about our instrumentation rather than about the knowledge, and
scoring it 100 would flatter it. It returns None, it is excluded from the mean,
and the output says how many dimensions were counted.

That is the same rule `knowledge_sync/metrics.py` set — a dashboard with an
invented number is worse than one with a missing panel — applied to a score,
where the temptation to fill in a blank is strongest.
"""

from collections import Counter
from dataclasses import dataclass, field

from ops import metrics

#: A dimension below this is worth a sentence in the report rather than just a
#: number. Not a failure threshold — nothing here fails a build.
CONCERN_BELOW = 60


@dataclass
class Dimension:
    name: str
    value: float = None          # None means UNKNOWN, and is not averaged
    detail: str = ""
    formula: str = ""

    @property
    def known(self):
        return self.value is not None

    def as_dict(self):
        return {"name": self.name,
                "value": round(self.value, 1) if self.known else None,
                "detail": self.detail, "formula": self.formula}


@dataclass
class Quality:
    dimensions: list = field(default_factory=list)

    @property
    def known(self):
        return [d for d in self.dimensions if d.known]

    @property
    def overall(self):
        if not self.known:
            return None
        return round(sum(d.value for d in self.known) / len(self.known), 1)

    @property
    def grade(self):
        """A letter, because a number invites a target and a letter invites a
        conversation. Bands are wide for the same reason the star bands are."""
        overall = self.overall
        if overall is None:
            return "UNKNOWN"
        for floor, grade in ((85, "A"), (70, "B"), (55, "C"), (40, "D"), (0, "E")):
            if overall >= floor:
                return grade
        return "E"

    @property
    def concerns(self):
        return [d for d in self.known if d.value < CONCERN_BELOW]

    def as_dict(self):
        return {
            "overall": self.overall,
            "grade": self.grade,
            "dimensions_scored": len(self.known),
            "dimensions_unknown": len(self.dimensions) - len(self.known),
            "dimensions": [d.as_dict() for d in self.dimensions],
            "concerns": [d.name for d in self.concerns],
        }


def _pct(part, whole):
    return round(100 * part / whole, 1) if whole else 0.0


def score(entities=None, relationships=None, rows=None, now=None):
    entities = entities if entities is not None else metrics.read_entities()
    relationships = relationships if relationships is not None else metrics.read_relationships()
    rows = rows if rows is not None else metrics.entity_operations(entities, relationships, now=now)
    graph = metrics.load_artifact("graph") or {}
    crosswalk = metrics.load_artifact("crosswalk") or {}

    result = Quality()

    # ── coverage ────────────────────────────────────────────────────────────
    # Against what the BUILDER registers, not against an aspiration. The
    # builder's registered type list is the closest thing to a stated intent
    # that exists in the repository, and measuring against a wish list would
    # make the score a measure of ambition.
    registered = graph.get("entity_types_registered") or 0
    populated = len({e["entity_type"] for e in entities})
    result.dimensions.append(Dimension(
        "coverage",
        _pct(populated, registered) if registered else None,
        f"{populated} of {registered} registered entity types hold rows"
        if registered else "graph_summary.json has not been built",
        "populated entity types ÷ registered entity types"))

    # ── connectivity ────────────────────────────────────────────────────────
    degree = metrics.degrees(relationships)
    connected = sum(1 for e in entities if degree.get(e["global_entity_id"], 0) > 0)
    result.dimensions.append(Dimension(
        "connectivity", _pct(connected, len(entities)) if entities else None,
        f"{connected} of {len(entities)} entities lead somewhere; "
        f"median {metrics._median([degree.get(e['global_entity_id'], 0) for e in entities])} "
        f"neighbours",
        "entities with at least one edge ÷ all entities"))

    # ── freshness ───────────────────────────────────────────────────────────
    fresh = sum(1 for r in rows if r["freshness"] == "FRESH")
    ageing = sum(1 for r in rows if r["freshness"] == "AGEING")
    known_age = sum(1 for r in rows if r["freshness"] != "UNKNOWN")
    result.dimensions.append(Dimension(
        "freshness",
        # Ageing counts half. A record last touched eight months ago is not as
        # good as one from last week and is not as bad as one from three years
        # ago, and collapsing those two into "not fresh" loses the distinction
        # an operator would act on.
        _pct(fresh + ageing * 0.5, known_age) if known_age else None,
        f"{fresh} fresh, {ageing} ageing, "
        f"{sum(1 for r in rows if r['freshness'] == 'STALE')} stale",
        "(fresh + ageing÷2) ÷ entities with a known date"))

    # ── verification ────────────────────────────────────────────────────────
    verified = sum(1 for r in rows if "NEEDS_REVIEW" not in r["verification_status"])
    result.dimensions.append(Dimension(
        "verification", _pct(verified, len(rows)) if rows else None,
        f"{verified} of {len(rows)} entities are not marked NEEDS_REVIEW — "
        f"and no steward has recorded a review yet, so this measures the "
        f"collector's confidence rather than a person's",
        "entities without VST-NEEDS_REVIEW ÷ all entities"))

    # ── research completeness ───────────────────────────────────────────────
    # The share of cells holding a sentinel, across every package dataset. The
    # sentinel is the repository's honesty mechanism, so its frequency is a
    # direct measure of how much research is unfinished.
    pending, cells = _sentinel_density()
    result.dimensions.append(Dimension(
        "research_completeness",
        round(100 - _pct(pending, cells), 1) if cells else None,
        f"{pending} of {cells} dataset cells hold PENDING_VERIFICATION"
        if cells else "no package datasets found",
        "1 − (PENDING cells ÷ all cells)"))

    # ── source diversity ────────────────────────────────────────────────────
    # Concentration, not count. Twenty sources of which one supplies 90% is more
    # fragile than five that supply a fifth each, and a count cannot see that.
    diversity, detail = _source_diversity(entities)
    result.dimensions.append(Dimension(
        "source_diversity", diversity, detail,
        "1 − Herfindahl index over rows per source package, normalised"))

    # ── popularity ──────────────────────────────────────────────────────────
    with_views = [r for r in rows if r["popularity"] is not None]
    result.dimensions.append(Dimension(
        "popularity",
        _pct(sum(1 for r in with_views if r["popularity"] > 0), len(rows))
        if with_views else None,
        f"{len(with_views)} entities have a view or search count"
        if with_views else
        "no popularity data — page views and search counts live in Supabase and "
        "are passed in, not fetched here",
        "entities with at least one view ÷ all entities"))

    # Reported alongside rather than scored: the crosswalk is a join, not
    # knowledge, and folding it into the mean would let a vocabulary fix move a
    # number that is supposed to describe the knowledge base.
    if crosswalk.get("resolve_pct_total") is not None:
        result.dimensions.append(Dimension(
            "vocabulary_join", float(crosswalk["resolve_pct_total"]),
            f"{crosswalk.get('resolved_total')} of {crosswalk.get('terms_total')} "
            f"user-facing terms resolve to an entity",
            "resolved crosswalk terms ÷ all crosswalk terms"))

    return result


def _sentinel_density():
    import csv                                                       # noqa: PLC0415
    pending = cells = 0
    for path in sorted((metrics.ROOT / "packages").glob("*/datasets/*.csv")):
        with open(path, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for value in row.values():
                    cells += 1
                    if str(value or "").strip().upper().startswith("PENDING_VERIFICATION"):
                        pending += 1
    return pending, cells


def _source_diversity(entities):
    counts = Counter(e["source_package"] for e in entities)
    total = sum(counts.values())
    if not total:
        return None, "no entities"
    # Herfindahl: sum of squared shares. 1.0 = one source supplies everything.
    # Normalised against the best achievable for this many sources, so adding a
    # ninth package cannot make the score drop.
    herfindahl = sum((n / total) ** 2 for n in counts.values())
    best = 1 / len(counts)
    score_value = round(100 * (1 - (herfindahl - best) / (1 - best)), 1) if len(counts) > 1 else 0.0
    largest, largest_n = counts.most_common(1)[0]
    return score_value, (f"{len(counts)} source packages; the largest "
                         f"({largest}) supplies {_pct(largest_n, total)}%")
