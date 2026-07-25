#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Query Engine (Module 5)

A traversal library over the Global Entity Registry and Relationship Graph. No UI,
no server, no database — the interfaces are the deliverable, and the reference
implementation runs against the CSVs so that the interfaces are demonstrably real
rather than aspirational.

ARCHITECTURE
------------
Three layers, deliberately separated:

  GraphStore   loads entities and edges, builds adjacency indexes. The only layer
               that knows the data is in CSV. Swapping in Postgres, DuckDB or a
               property graph replaces this class and nothing else.

  QueryEngine  traversal primitives: neighbours, paths, filters. Domain-agnostic.

  queries.py   the named business questions, expressed in terms of QueryEngine.
               This is where domain vocabulary lives.

Every result carries provenance. A query answer that cannot say which package and
which row it came from is not an answer this platform is willing to give.

Usage:
    from query_engine.engine import QueryEngine
    qe = QueryEngine()
    qe.neighbours("vw:skill:python-programming", direction="in")
    qe.find(entity_type="MSME", where=lambda e: e["confidence_score"] > "70")
"""

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"


class GraphStore:
    """
    Storage abstraction. The ONLY class that knows the graph lives in CSV files.

    To move to a real database, implement this interface and pass an instance to
    QueryEngine. Nothing above this line changes.
    """

    def __init__(self, entities_path=None, relationships_path=None):
        entities_path = entities_path or KG / "entities" / "entities.csv"
        relationships_path = relationships_path or KG / "relationships" / "relationships.csv"

        self.entities = {}
        with open(entities_path, newline="", encoding="utf-8") as f:
            for e in csv.DictReader(f):
                self.entities[e["global_entity_id"]] = e

        self.edges = []
        self.out_index = defaultdict(list)   # from_entity -> [edge]
        self.in_index = defaultdict(list)    # to_entity   -> [edge]
        self.type_index = defaultdict(list)  # relationship_type -> [edge]
        with open(relationships_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.edges.append(r)
                self.out_index[r["from_entity"]].append(r)
                self.in_index[r["to_entity"]].append(r)
                self.type_index[r["relationship_type"]].append(r)

        self.entity_type_index = defaultdict(list)
        for e in self.entities.values():
            self.entity_type_index[e["entity_type"]].append(e)

    def entity(self, gid):
        return self.entities.get(gid)

    def out_edges(self, gid, rel_type=None):
        edges = self.out_index.get(gid, [])
        return [e for e in edges if rel_type is None or e["relationship_type"] == rel_type]

    def in_edges(self, gid, rel_type=None):
        edges = self.in_index.get(gid, [])
        return [e for e in edges if rel_type is None or e["relationship_type"] == rel_type]

    def by_type(self, entity_type):
        return self.entity_type_index.get(entity_type, [])

    def edges_of_type(self, rel_type):
        return self.type_index.get(rel_type, [])


class Result:
    """
    One query result: an entity plus the evidence that put it there.

    `via` is the chain of edges traversed. Every edge carries its provenance
    package, dataset and row id, so any answer can be traced to the exact CSV row
    in the exact package that produced it.
    """

    __slots__ = ("entity", "via", "score")

    def __init__(self, entity, via=None, score=None):
        self.entity = entity
        self.via = via or []
        self.score = score

    @property
    def id(self):
        return self.entity["global_entity_id"]

    @property
    def name(self):
        return self.entity["canonical_name"]

    @property
    def entity_type(self):
        return self.entity["entity_type"]

    def provenance(self):
        """Every (package, dataset, row_id) that supports this result."""
        return [
            {"package": e["provenance_package"],
             "dataset": e["provenance_dataset"],
             "row_id": e["provenance_row_id"],
             "relationship": e["relationship_type"],
             "confidence": e["confidence"]}
            for e in self.via
        ]

    def min_confidence(self):
        """A chain is only as strong as its weakest edge."""
        if not self.via:
            return int(self.entity.get("confidence_score", 0))
        return min(int(e["confidence"]) for e in self.via)

    def to_dict(self):
        return {
            "global_entity_id": self.id,
            "canonical_name": self.name,
            "entity_type": self.entity_type,
            "source_package": self.entity["source_package"],
            "path_confidence": self.min_confidence(),
            "hops": len(self.via),
            "provenance": self.provenance(),
        }

    def __repr__(self):
        return f"<{self.entity_type} {self.name!r} conf={self.min_confidence()}>"


class QueryEngine:
    """Domain-agnostic traversal primitives. Domain vocabulary lives in queries.py."""

    def __init__(self, store=None):
        self.g = store or GraphStore()

    # ------------------------------------------------------------- primitives
    def get(self, gid):
        e = self.g.entity(gid)
        return Result(e) if e else None

    def find(self, entity_type=None, name_contains=None, where=None):
        """Filter entities without traversing."""
        pool = self.g.by_type(entity_type) if entity_type else list(self.g.entities.values())
        out = []
        for e in pool:
            if name_contains and name_contains.lower() not in e["canonical_name"].lower():
                continue
            if where and not where(e):
                continue
            out.append(Result(e))
        return out

    def neighbours(self, gid, rel_type=None, direction="out", entity_type=None):
        """
        One hop. direction: 'out' (gid is subject), 'in' (gid is object), 'both'.

        Returns Result objects carrying the edge that produced them.
        """
        edges = []
        if direction in ("out", "both"):
            edges += [(e, e["to_entity"]) for e in self.g.out_edges(gid, rel_type)]
        if direction in ("in", "both"):
            edges += [(e, e["from_entity"]) for e in self.g.in_edges(gid, rel_type)]

        out, seen = [], set()
        for edge, other_id in edges:
            if other_id in seen:
                continue
            ent = self.g.entity(other_id)
            if ent is None:
                continue
            if entity_type and ent["entity_type"] != entity_type:
                continue
            seen.add(other_id)
            out.append(Result(ent, via=[edge]))
        return out

    def traverse(self, gid, path, entity_type=None):
        """
        Multi-hop traversal along an explicit path specification.

        path is a list of (relationship_type, direction) tuples. Explicit beats
        clever: a caller can read exactly which edges a query walks, which matters
        when the answer will be shown to a citizen.

            qe.traverse(crop_id, [("PROCESSES", "in"), ("SUPPORTED_BY_SCHEME", "out")])
        """
        frontier = [Result(self.g.entity(gid))] if self.g.entity(gid) else []
        for rel_type, direction in path:
            nxt, seen = [], set()
            for r in frontier:
                for hop in self.neighbours(r.id, rel_type=rel_type, direction=direction):
                    if hop.id in seen:
                        continue
                    seen.add(hop.id)
                    nxt.append(Result(hop.entity, via=r.via + hop.via))
            frontier = nxt
        if entity_type:
            frontier = [r for r in frontier if r.entity_type == entity_type]
        return frontier

    def shortest_path(self, from_gid, to_gid, max_hops=4):
        """Breadth-first path between two entities, ignoring edge direction."""
        if from_gid == to_gid:
            return []
        seen = {from_gid}
        frontier = [(from_gid, [])]
        for _ in range(max_hops):
            nxt = []
            for gid, chain in frontier:
                for edge in self.g.out_edges(gid) + self.g.in_edges(gid):
                    other = edge["to_entity"] if edge["from_entity"] == gid else edge["from_entity"]
                    if other in seen:
                        continue
                    new_chain = chain + [edge]
                    if other == to_gid:
                        return new_chain
                    seen.add(other)
                    nxt.append((other, new_chain))
            frontier = nxt
            if not frontier:
                break
        return None

    def rank(self, results, min_confidence=0, sort_by="confidence"):
        """Filter by path confidence and sort. No scoring model is invented here."""
        out = [r for r in results if r.min_confidence() >= min_confidence]
        if sort_by == "confidence":
            out.sort(key=lambda r: (-r.min_confidence(), r.name))
        elif sort_by == "name":
            out.sort(key=lambda r: r.name)
        return out

    # ------------------------------------------------------------------ stats
    def stats(self):
        return {
            "entities": len(self.g.entities),
            "relationships": len(self.g.edges),
            "entity_types": len(self.g.entity_type_index),
            "relationship_types": len(self.g.type_index),
        }
