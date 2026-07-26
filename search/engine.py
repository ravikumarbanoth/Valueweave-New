#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Search Engine (Work Package 4)

Four match modes over the index, applied in descending order of evidential
strength, so a caller always gets the strongest available interpretation of their
query rather than a mixture:

    EXACT    normalised query equals a document's normalised title
    PREFIX   a document title starts with the query, or a word in it does
    ALIAS    the query matches a registered alias, resolving to its entity
    FUZZY    token-overlap and sequence similarity above a configurable threshold

Alias documents belong to the ALIAS matcher exclusively; EXACT and PREFIX skip
them. Without that rule an exact hit on "PM-KISAN" would be reported as EXACT and
`modes=["ALIAS"]` would be a mode that matches nothing anyone searches for. Each
mode names what was matched, not merely which function ran.

Modes are selectable and combinable. `MatchMode.ALL` runs the ladder; a caller who
wants only exact matches passes only EXACT and gets no fuzzy noise.

WHY FUZZY IS INCLUDED BUT ALWAYS RANKED LAST
--------------------------------------------
Fuzzy matching is the mode most likely to be wrong. But a wrong search result is
a different kind of error from a wrong entity merge: it is recoverable, because
the user sees it and ignores it. So fuzzy is part of the default ladder — it is
just always ranked below every stronger mode, always labelled with the mode that
produced it, and always carries its score. A caller that cannot tolerate
approximation passes `modes=["EXACT"]` and gets no approximation at all.

Every result carries the confidence and verification_status of the underlying
record. A search hit is not an endorsement: at present every row in this knowledge
base is VST-NEEDS_REVIEW, and results say so.
"""

import difflib
from dataclasses import dataclass
from enum import Enum

from search.index import SearchIndex, normalise, tokens


class MatchMode(str, Enum):
    EXACT = "EXACT"
    PREFIX = "PREFIX"
    ALIAS = "ALIAS"
    FUZZY = "FUZZY"

    @classmethod
    def all(cls):
        return [cls.EXACT, cls.PREFIX, cls.ALIAS, cls.FUZZY]

    @classmethod
    def parse(cls, value):
        """Accept 'exact', 'EXACT', a list, or 'all'. Raises on an unknown mode."""
        if isinstance(value, cls):
            return [value]
        if value is None or value == "" or value == "all":
            return cls.all()
        if isinstance(value, (list, tuple, set)):
            out = []
            for v in value:
                out.extend(cls.parse(v))
            return list(dict.fromkeys(out))
        v = str(value).strip().upper()
        if v == "ALL":
            return cls.all()
        try:
            return [cls(v)]
        except ValueError:
            raise ValueError(
                f"unknown match mode {value!r}; expected one of "
                f"{[m.value for m in cls.all()] + ['all']}") from None


class Scope(str, Enum):
    ENTITY = "entity"
    ALIAS = "alias"
    RELATIONSHIP = "relationship"
    PACKAGE = "package"
    DATASET = "dataset"

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return [value]
        if value is None or value == "" or value == "all":
            return [s for s in cls]
        if isinstance(value, (list, tuple, set)):
            out = []
            for v in value:
                out.extend(cls.parse(v))
            return list(dict.fromkeys(out))
        v = str(value).strip().lower()
        if v == "all":
            return [s for s in cls]
        try:
            return [cls(v)]
        except ValueError:
            raise ValueError(
                f"unknown scope {value!r}; expected one of "
                f"{[s.value for s in cls] + ['all']}") from None


# Ranking weight per mode. The order is the point: an exact match must never be
# displaced by a high-scoring fuzzy one.
MODE_WEIGHT = {MatchMode.EXACT: 1000, MatchMode.ALIAS: 800,
               MatchMode.PREFIX: 600, MatchMode.FUZZY: 400}


@dataclass
class SearchResult:
    document: object
    match_mode: MatchMode
    score: float
    matched_on: str

    @property
    def rank(self):
        return MODE_WEIGHT[self.match_mode] + self.score * 100

    def to_dict(self):
        d = self.document.to_dict()
        d["match_mode"] = self.match_mode.value
        d["score"] = round(self.score, 4)
        d["matched_on"] = self.matched_on
        return d


class SearchEngine:
    #: Floor for the blended token+sequence score.
    DEFAULT_FUZZY_THRESHOLD = 0.62
    #: Stricter floor for raw string similarity alone — the typo route.
    STRING_SIMILARITY_FLOOR = 0.85

    def __init__(self, index=None, fuzzy_threshold=None):
        self.index = index or SearchIndex()
        self.fuzzy_threshold = (self.DEFAULT_FUZZY_THRESHOLD
                                if fuzzy_threshold is None else float(fuzzy_threshold))

    # ------------------------------------------------------------- matchers
    def _exact(self, q, docs, eligible):
        return [SearchResult(d, MatchMode.EXACT, 1.0,
                             "canonical_name" if d.scope == "entity" else d.scope)
                for d in self.index.by_exact.get(q, [])
                if id(d) in eligible and d.scope != "alias"]

    def _prefix(self, q, docs, eligible):
        out = []
        for d in docs:
            if d.scope == "alias":
                continue                       # the ALIAS matcher owns these
            if d.normalised == q:
                continue                       # already an exact hit
            if d.normalised.startswith(q):
                out.append(SearchResult(d, MatchMode.PREFIX,
                                        len(q) / max(len(d.normalised), 1), "title_prefix"))
            elif any(w.startswith(q) for w in d.normalised.split()):
                out.append(SearchResult(d, MatchMode.PREFIX,
                                        0.5 * len(q) / max(len(d.normalised), 1), "word_prefix"))
        return out

    def _alias(self, q, docs, eligible):
        out = []
        for d in self.index.scope("alias"):
            if id(d) not in eligible:
                continue
            if d.normalised == q or d.normalised.startswith(q):
                out.append(SearchResult(
                    d, MatchMode.ALIAS, 1.0 if d.normalised == q else 0.8,
                    f"alias -> {d.extra.get('canonical_name', d.entity_id)}"))
        return out

    def _fuzzy(self, q, docs, eligible):
        """
        Two independent routes to a fuzzy match, because they catch different errors.

        The blend (token overlap + sequence ratio) catches a user who has the right
        words in the wrong order or with extra ones. It is useless against a typo:
        "manufactring" shares no token with "manufacturing", so its Jaccard is 0 and
        the blend lands near 0.48 no matter how close the strings are.

        So a high raw string similarity is accepted on its own, at a stricter floor.
        A single transposed letter clears STRING_SIMILARITY_FLOOR; two unrelated
        words do not.
        """
        qt = set(tokens(q))
        out = []
        for d in docs:
            if d.scope == "alias":
                continue                       # the ALIAS matcher owns these
            if d.normalised == q or d.normalised.startswith(q):
                continue
            dt = set(tokens(d.title))
            jaccard = len(qt & dt) / len(qt | dt) if (qt | dt) else 0.0
            seq = difflib.SequenceMatcher(None, q, d.normalised).ratio()
            blend = 0.5 * jaccard + 0.5 * seq

            if blend >= self.fuzzy_threshold:
                out.append(SearchResult(d, MatchMode.FUZZY, blend,
                                        f"token+sequence similarity {blend:.2f}"))
            elif seq >= self.STRING_SIMILARITY_FLOOR:
                out.append(SearchResult(d, MatchMode.FUZZY, seq,
                                        f"string similarity {seq:.2f} (probable typo)"))
        return out

    # ---------------------------------------------------------------- query
    def search(self, query, scopes=None, modes=None, entity_type=None,
               source_package=None, min_confidence=0, limit=25, fuzzy_threshold=None):
        """
        Search the index. Returns SearchResult objects, strongest first.

        scopes           entity | alias | relationship | package | dataset | all
        modes            EXACT | PREFIX | ALIAS | FUZZY | all
        entity_type      restrict to one entity type (or relationship type)
        source_package   restrict to one owning package
        min_confidence   drop results below this confidence score
        fuzzy_threshold  override the similarity floor for this call only
        """
        q = normalise(query)
        if not q:
            return []

        wanted_scopes = {s.value for s in Scope.parse(scopes)}
        wanted_modes = MatchMode.parse(modes)
        threshold = self.fuzzy_threshold
        if fuzzy_threshold is not None:
            self.fuzzy_threshold, threshold = float(fuzzy_threshold), self.fuzzy_threshold

        try:
            docs = [d for d in self.index.documents
                    if d.scope in wanted_scopes
                    and (not entity_type or d.entity_type == entity_type)
                    and (not source_package or d.source_package == source_package)
                    and d.confidence >= min_confidence]
            eligible = {id(d) for d in docs}

            results, seen = [], set()
            runners = {MatchMode.EXACT: self._exact, MatchMode.PREFIX: self._prefix,
                       MatchMode.ALIAS: self._alias, MatchMode.FUZZY: self._fuzzy}
            for mode in wanted_modes:
                for r in runners[mode](q, docs, eligible):
                    key = (r.document.doc_id, r.document.scope)
                    if key in seen:
                        continue          # the first, strongest mode to find it wins
                    seen.add(key)
                    results.append(r)
        finally:
            if fuzzy_threshold is not None:
                self.fuzzy_threshold = threshold

        results.sort(key=lambda r: (-r.rank, r.document.title))
        return results[:limit] if limit else results

    def suggest(self, prefix, scopes="entity", limit=10):
        """Type-ahead: prefix matches only, no fuzzy noise."""
        return self.search(prefix, scopes=scopes,
                           modes=[MatchMode.EXACT, MatchMode.PREFIX, MatchMode.ALIAS],
                           limit=limit)

    def stats(self):
        s = self.index.stats()
        s["fuzzy_threshold"] = self.fuzzy_threshold
        s["string_similarity_floor"] = self.STRING_SIMILARITY_FLOOR
        s["match_modes"] = [m.value for m in MatchMode.all()]
        s["scopes"] = [x.value for x in Scope]
        return s
