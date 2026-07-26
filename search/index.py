#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Search Index (Work Package 4)

Builds one flat, searchable document set out of four things that are shaped
differently and are usually searched separately:

    entities        647 nodes from the Global Entity Registry
    aliases         150 alternative surface forms, each pointing at an entity
    relationships   865 edges, searchable by their type and by their endpoints
    packages        the 8 released packages and their datasets

A `Document` is the common shape. Making them uniform is the entire job of this
module: the engine above it then has exactly one kind of thing to match against,
and adding a fifth searchable scope later means adding a loader here and nothing
else.

DESIGN NOTE — why the index is built, not queried live
------------------------------------------------------
`query_engine.GraphStore` already loads the graph. This module deliberately does
not reuse it. GraphStore is optimised for traversal (adjacency indexes); search
needs the opposite shape — a normalised-text index. Sharing one structure would
make both slower and neither clearer.

The index is rebuilt on construction and held in memory. At 647 entities that
costs a few milliseconds; the moment it does not, this class is where a real
inverted index or a database goes, and nothing above it changes.
"""

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"
PACKAGES = ROOT / "packages"


def normalise(text):
    """Comparison form: ascii, lowercase, punctuation collapsed to single spaces.

    Parenthetical qualifiers are KEPT. Dropping them is right for resolution and
    wrong for search: someone searching "Manufacturing (Automotive)" means that,
    not its parent. The Resolver makes the opposite trade for the opposite reason
    (see knowledge_graph/resolution/resolver.py).
    """
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def tokens(text):
    return [t for t in normalise(text).split() if t]


@dataclass
class Document:
    """One searchable thing, whatever its underlying scope."""

    doc_id: str
    scope: str                  # entity | alias | relationship | package | dataset
    title: str                  # the text a user would recognise
    normalised: str = ""
    entity_id: str = ""         # the entity this document resolves to, when it has one
    entity_type: str = ""
    source_package: str = ""
    confidence: int = 0
    verification_status: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.normalised:
            self.normalised = normalise(self.title)

    def to_dict(self):
        d = {
            "doc_id": self.doc_id,
            "scope": self.scope,
            "title": self.title,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "source_package": self.source_package,
            "confidence": self.confidence,
            "verification_status": self.verification_status,
        }
        d.update(self.extra)
        return {k: v for k, v in d.items() if v != "" and v is not None}


def _read(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _int(value, default=0):
    v = str(value or "").strip()
    return int(v) if v.isdigit() else default


class SearchIndex:
    """The searchable corpus. Load once, query many times."""

    SCOPES = ("entity", "alias", "relationship", "package", "dataset")

    def __init__(self, kg_dir=None, packages_dir=None):
        self.kg = Path(kg_dir or KG)
        self.packages = Path(packages_dir or PACKAGES)

        self.documents = []
        self.by_scope = defaultdict(list)
        self.by_exact = defaultdict(list)     # normalised title -> [Document]
        self.by_token = defaultdict(set)      # token -> {doc index}
        self.entities = {}                    # global_entity_id -> entity row

        self._load_entities()
        self._load_aliases()
        self._load_relationships()
        self._load_packages()
        self._finalise()

    # ------------------------------------------------------------- loading
    def _add(self, doc):
        self.documents.append(doc)
        self.by_scope[doc.scope].append(doc)

    def _load_entities(self):
        for e in _read(self.kg / "entities" / "entities.csv"):
            self.entities[e["global_entity_id"]] = e
            self._add(Document(
                doc_id=e["global_entity_id"],
                scope="entity",
                title=e["canonical_name"],
                entity_id=e["global_entity_id"],
                entity_type=e["entity_type"],
                source_package=e["source_package"],
                confidence=_int(e.get("confidence_score")),
                verification_status=e.get("verification_status", ""),
                extra={"package_local_id": e.get("package_local_id", ""),
                       "lifecycle_state": e.get("lifecycle_state", "")},
            ))

    def _load_aliases(self):
        for a in _read(self.kg / "entities" / "aliases.csv"):
            ent = self.entities.get(a["global_entity_id"])
            if not ent:
                continue          # an alias to nothing is not searchable
            self._add(Document(
                doc_id=a["alias_id"],
                scope="alias",
                title=a["alias"],
                entity_id=a["global_entity_id"],
                entity_type=ent["entity_type"],
                source_package=a.get("source_package", ent["source_package"]),
                confidence=_int(ent.get("confidence_score")),
                verification_status=ent.get("verification_status", ""),
                extra={"alias_type": a.get("alias_type", ""),
                       "canonical_name": ent["canonical_name"]},
            ))

    def _load_relationships(self):
        for r in _read(self.kg / "relationships" / "relationships.csv"):
            src = self.entities.get(r["from_entity"])
            dst = self.entities.get(r["to_entity"])
            if not src or not dst:
                continue
            # A relationship is searchable by the sentence it asserts, so that
            # "turmeric processing" finds the edge as well as the two endpoints.
            title = f"{src['canonical_name']} {r['relationship_type']} {dst['canonical_name']}"
            self._add(Document(
                doc_id=r["relationship_id"],
                scope="relationship",
                title=title,
                entity_type=r["relationship_type"],
                source_package=r.get("provenance_package", ""),
                confidence=_int(r.get("confidence")),
                extra={"from_entity": r["from_entity"],
                       "to_entity": r["to_entity"],
                       "from_name": src["canonical_name"],
                       "to_name": dst["canonical_name"],
                       "relationship_type": r["relationship_type"],
                       "provenance_dataset": r.get("provenance_dataset", ""),
                       "provenance_row_id": r.get("provenance_row_id", "")},
            ))

    def _load_packages(self):
        for pkg in sorted(p for p in self.packages.iterdir() if p.is_dir()):
            ds_dir = pkg / "datasets"
            datasets = sorted(ds_dir.glob("*.csv")) if ds_dir.exists() else []
            # `Package006_Skills` is a placeholder directory holding only a README,
            # superseded by Package006_Skills_and_Training. A directory with no
            # datasets is not a released package, so it is not searchable as one.
            if not datasets:
                continue
            rows = 0
            for f in datasets:
                rows += len(_read(f))
                self._add(Document(
                    doc_id=f"{pkg.name}/{f.name}",
                    scope="dataset",
                    title=f.stem.replace("_", " "),
                    source_package=pkg.name,
                    extra={"dataset": f.name, "rows": len(_read(f))},
                ))
            self._add(Document(
                doc_id=pkg.name,
                scope="package",
                title=pkg.name.replace("_", " "),
                source_package=pkg.name,
                extra={"datasets": len(datasets), "rows": rows},
            ))

    def _finalise(self):
        for i, doc in enumerate(self.documents):
            self.by_exact[doc.normalised].append(doc)
            for t in tokens(doc.title):
                self.by_token[t].add(i)

    # --------------------------------------------------------------- access
    def scope(self, name):
        return self.by_scope.get(name, [])

    def entity(self, global_entity_id):
        return self.entities.get(global_entity_id)

    def stats(self):
        return {
            "documents": len(self.documents),
            "by_scope": {k: len(v) for k, v in sorted(self.by_scope.items())},
            "distinct_normalised_titles": len(self.by_exact),
            "distinct_tokens": len(self.by_token),
        }


if __name__ == "__main__":
    import json
    print(json.dumps(SearchIndex().stats(), indent=2))
