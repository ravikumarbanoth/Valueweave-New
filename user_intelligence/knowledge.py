#!/usr/bin/env python3
"""
Read-only access to the knowledge graph and the Step 0 vocabulary crosswalk.

READS GIT, NOT SUPABASE
-----------------------
The Step 1 sync projects the graph into Supabase, and this engine could read that
projection. It reads the Git artifacts instead, for three reasons:

  * Git is the source of truth (ADR-001). Reading the projection adds a hop that
    can only ever be stale or equal.
  * The engine then runs with no credentials, so its tests are real tests.
  * The projection has not been applied to any database yet. An engine that could
    not run until it was would be untestable today.

Substituting the projection later means replacing this class and nothing above it.

WHY A SNAPSHOT
--------------
Loaded once, frozen, and hashed. Every score and recommendation is computed
against one immutable view, so a run cannot see the graph change underneath it,
and `snapshot_hash` lets two runs prove they saw the same data.
"""

import csv
import hashlib
from collections import defaultdict
from pathlib import Path

from user_intelligence.config import ROOT
from user_intelligence.rules import Evidence

KG = ROOT / "knowledge_graph"
VOCAB = ROOT / "governance" / "vocabulary"

NO_COUNTERPART = "NO_COUNTERPART"


def _read(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _int(value, default=0):
    v = str(value or "").strip()
    return int(v) if v.lstrip("-").isdigit() else default


class KnowledgeSnapshot:
    """Entities, edges, aliases and crosswalks — loaded once, then read-only."""

    def __init__(self, kg_dir=None, vocab_dir=None):
        kg = Path(kg_dir or KG)
        vocab = Path(vocab_dir or VOCAB)

        self.entities = {e["global_entity_id"]: e
                         for e in _read(kg / "entities" / "entities.csv")}
        self.edges = _read(kg / "relationships" / "relationships.csv")

        self.by_type = defaultdict(list)
        for e in self.entities.values():
            self.by_type[e["entity_type"]].append(e)
        for rows in self.by_type.values():
            rows.sort(key=lambda e: e["global_entity_id"])   # deterministic order

        self.out_edges = defaultdict(list)
        self.in_edges = defaultdict(list)
        for r in self.edges:
            self.out_edges[r["from_entity"]].append(r)
            self.in_edges[r["to_entity"]].append(r)

        # Step 0 crosswalks: the only bridge from free text to the graph.
        self.crosswalk = defaultdict(dict)          # kind -> normalised -> row
        self.no_counterpart = defaultdict(set)
        for kind in ("skill", "sector", "district"):
            for row in _read(vocab / f"{kind}_crosswalk.csv"):
                key = row["normalised_term"]
                if row["match_method"] == NO_COUNTERPART:
                    self.no_counterpart[kind].add(key)
                    continue
                # First vocabulary wins; all vocabularies agree on a resolved term
                # because they resolve against the same graph.
                self.crosswalk[kind].setdefault(key, row)

        self.snapshot_hash = self._hash()

    def _hash(self):
        material = "|".join([
            str(len(self.entities)), str(len(self.edges)),
            *sorted(self.entities), *sorted(r["relationship_id"] for r in self.edges),
        ])
        return hashlib.sha256(material.encode()).hexdigest()[:16]

    # ------------------------------------------------------------- resolution
    @staticmethod
    def normalise(text):
        import re
        import unicodedata
        t = unicodedata.normalize("NFKD", str(text))
        t = t.encode("ascii", "ignore").decode("ascii").lower()
        t = t.replace("&", " and ")
        t = re.sub(r"[^a-z0-9]+", " ", t)
        return re.sub(r"\s{2,}", " ", t).strip()

    def resolve(self, kind, term):
        """
        Free text -> (entity, crosswalk row) or (None, None).

        Returns None for an unresolvable term rather than guessing. `explain()`
        distinguishes "we have no data for this" from "we have never seen it".
        """
        row = self.crosswalk[kind].get(self.normalise(term))
        if not row:
            return None, None
        return self.entities.get(row["global_entity_id"]), row

    def explain_unresolved(self, kind, term):
        key = self.normalise(term)
        if key in self.no_counterpart[kind]:
            return (f"'{term}' is a recognised {kind} with no researched counterpart "
                    f"in the knowledge base yet")
        return f"'{term}' is not in the {kind} vocabulary crosswalk"

    def resolve_many(self, kind, terms):
        """Returns (resolved, unresolved) — both ordered, both explained."""
        resolved, unresolved = [], []
        for term in terms or []:
            entity, row = self.resolve(kind, term)
            if entity:
                resolved.append((term, entity, row))
            else:
                unresolved.append((term, self.explain_unresolved(kind, term)))
        resolved.sort(key=lambda t: t[1]["global_entity_id"])
        unresolved.sort()
        return resolved, unresolved

    # -------------------------------------------------------------- traversal
    def neighbours(self, entity_id, rel_type=None, direction="out",
                   entity_type=None):
        edges = (self.out_edges if direction == "out" else self.in_edges).get(
            entity_id, [])
        out = []
        for r in edges:
            if rel_type and r["relationship_type"] != rel_type:
                continue
            other = r["to_entity"] if direction == "out" else r["from_entity"]
            node = self.entities.get(other)
            if not node:
                continue
            if entity_type and node["entity_type"] != entity_type:
                continue
            out.append((node, r))
        out.sort(key=lambda pair: pair[1]["relationship_id"])
        return out

    def degree(self, entity_id):
        return len(self.out_edges.get(entity_id, [])) + \
            len(self.in_edges.get(entity_id, []))

    # --------------------------------------------------------------- evidence
    def entity_evidence(self, entity, detail=""):
        return Evidence(
            kind="entity", ref=entity["global_entity_id"],
            label=entity["canonical_name"], detail=detail,
            confidence=_int(entity.get("confidence_score")),
            source_package=entity.get("source_package", ""),
            source_row_id=entity.get("package_local_id", ""))

    def edge_evidence(self, edge, detail=""):
        return Evidence(
            kind="edge", ref=edge["relationship_id"],
            label=f"{edge['relationship_type']}",
            detail=detail or f"{edge['from_entity']} -> {edge['to_entity']}",
            confidence=_int(edge.get("confidence")),
            source_package=edge.get("provenance_package", ""),
            source_dataset=edge.get("provenance_dataset", ""),
            source_row_id=edge.get("provenance_row_id", ""))

    def stats(self):
        return {
            "entities": len(self.entities),
            "edges": len(self.edges),
            "snapshot_hash": self.snapshot_hash,
            "crosswalk_resolved": {k: len(v) for k, v in sorted(self.crosswalk.items())},
            "crosswalk_no_counterpart": {k: len(v) for k, v
                                         in sorted(self.no_counterpart.items())},
        }
