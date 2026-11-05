#!/usr/bin/env python3
"""
Derived structured profiles, and the gaps in them.

WHAT A PROFILE IS
-----------------
Everything the repository already knows about one entity, gathered from the
four places it is currently scattered across — `entities.csv`,
`relationships.csv`, the concept table and the research articles — presented
as one shape.

Nothing here is new knowledge. Every edge is already a row in
`relationships.csv` (CANONICAL) or a restatement of one (DERIVED). The profile
is a VIEW: deleting the directory and rebuilding must produce the same thing,
which is what makes it safe to regenerate without review.

WHY THE GAPS ARE THE POINT
---------------------------
A profile listing four training providers is useful. A profile listing none is
MORE useful, because it says so. The platform's honest problem is not that it
ranks badly — it is that for most trades it holds a name and little else, and
until that is visible nobody can prioritise fixing it.

    "EV Technician: no training, no certification, no district"

is a research task a person can pick up on a Tuesday. A silently empty section
is not.

THE DIMENSIONS, AND WHY THESE
------------------------------
They are the questions a student or would-be entrepreneur actually arrives
with, mapped onto relationship types that exist in the graph today. Nothing
was invented to pad the list: `TRAINED_BY` has very few rows and is included
precisely because its emptiness is the finding.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from knowledge_intelligence import CANONICAL, DERIVED, RESEARCH_REQUIRED  # noqa: E402

ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
RELATIONSHIPS = ROOT / "knowledge_graph" / "relationships" / "relationships.csv"
CONCEPTS = ROOT / "frontend" / "lib" / "search" / "vocabulary" / "concepts.js"
ARTICLES = ROOT / "frontend" / "content" / "research"

#: dimension -> (relationship types, entity types that can satisfy it).
#: Both directions are read: `REQUIRES_SKILL` is written from the business to
#: the skill, and a skill's profile needs to see it.
DIMENSIONS = {
    "industry":      (("PART_OF", "RELATED_TO"), ("Industry",)),
    "business":      (("REQUIRES_SKILL", "RELATED_TO"),
                      ("BusinessOpportunity", "MSME")),
    "scheme":        (("SUPPORTED_BY_SCHEME", "FUNDED_BY", "RELATED_TO"),
                      ("GovernmentScheme",)),
    "training":      (("TRAINED_BY", "RELATED_TO"),
                      ("TrainingProvider", "Institution")),
    "certification": (("RELATED_TO",), ("Certification",)),
    "related_skill": (("RELATED_TO", "REQUIRES_SKILL"), ("Skill",)),
    "district":      (("LOCATED_IN", "RELATED_TO"), ("District",)),
    "machinery":     (("USES_MACHINERY",), ("Machinery",)),
}

#: Dimensions whose absence is worth reporting as a research task. Machinery is
#: not one: a reader choosing a trade does not need the tool list to decide,
#: and flagging it on every skill would bury the ones that matter.
GAP_DIMENSIONS = ("training", "certification", "business", "scheme", "district")


def _rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_graph():
    ents = _rows(ENTITIES)
    by_id = {e["global_entity_id"]: e for e in ents}
    edges = defaultdict(list)
    for rel in _rows(RELATIONSHIPS):
        for a, b in ((rel["from_entity"], rel["to_entity"]),
                     (rel["to_entity"], rel["from_entity"])):
            if a in by_id and b in by_id:
                edges[a].append((rel["relationship_type"], b, rel))
    return ents, by_id, edges


def load_aliases():
    """Concept aliases keyed by the entity term the concept expands to.

    The concept table points at entity NAMES, not ids, so the join is by
    lower-cased name — the same join `expands_to` already relies on and which
    the multilingual tests already hold.
    """
    raw = CONCEPTS.read_text(encoding="utf-8")
    body = raw[raw.index("Object.freeze(") + len("Object.freeze("):]
    data = json.loads(body.rstrip().rstrip(");"))
    out = defaultdict(list)
    for concept in data["concepts"]:
        terms = concept["en"] + concept["te"] + concept["tanglish"]
        for target in concept["expands_to"]:
            out[target.lower()].extend(terms)
    return out


def load_articles():
    """Research articles as (slug, title, plain text).

    Front matter is stripped so a title does not count as body evidence twice.
    Nothing is parsed beyond that: this layer reads articles for MENTIONS, not
    for claims, and extracting claims from prose is the one thing the whole
    stewardship design exists to prevent.
    """
    if not ARTICLES.exists():
        return []
    out = []
    for path in sorted(ARTICLES.glob("*.mdx")):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text, re.M)
        body = re.sub(r"^---.*?---", "", text, count=1, flags=re.S)
        out.append({"slug": path.stem,
                    "title": (m.group(1).strip() if m else path.stem),
                    "text": body})
    return out


def _mentions(article, name, aliases):
    """Whole-phrase, case-insensitive.

    Substring matching here would repeat the `tractor` ⊂ `contractor` mistake
    one layer up, where it would be harder to see.
    """
    haystack = " " + re.sub(r"\s+", " ", article["text"]).lower() + " "
    for term in [name] + list(aliases):
        t = term.lower().strip()
        if len(t) < 4:
            continue
        if re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", haystack):
            return term
    return None


def build(entity_types=("Skill",)):
    """One profile per entity of the requested types."""
    ents, by_id, edges = load_graph()
    aliases = load_aliases()
    articles = load_articles()

    profiles = []
    for entity in ents:
        if entity["entity_type"] not in entity_types:
            continue
        name = entity["canonical_name"]
        eid = entity["global_entity_id"]
        alias_terms = sorted(set(aliases.get(name.lower(), [])))

        dims = {}
        for dim, (rel_types, target_types) in DIMENSIONS.items():
            found = []
            for rel_type, other_id, rel in edges.get(eid, []):
                other = by_id[other_id]
                if rel_type in rel_types and other["entity_type"] in target_types \
                        and other_id != eid:
                    found.append({
                        "entity": other["canonical_name"],
                        "entity_id": other_id,
                        "entity_type": other["entity_type"],
                        "via": rel_type,
                        "confidence": rel.get("confidence"),
                        "provenance": rel.get("provenance_package"),
                        "trust": CANONICAL,
                    })
            #: Deduplicated by ENTITY ID, not by name. Several names in this
            #: graph belong to two entities each — "Carpentry" is both a
            #: BusinessOpportunity and a Skill — and collapsing by name would
            #: merge two different rows and lose whichever id came second.
            #: Two relationship rows joining the same PAIR are still one fact
            #: and are collapsed, which is what this is for.
            seen, unique = set(), []
            for row in found:
                if row["entity_id"] in seen:
                    continue
                seen.add(row["entity_id"])
                unique.append(row)
            dims[dim] = unique

        mentions = []
        for article in articles:
            hit = _mentions(article, name, alias_terms)
            if hit:
                mentions.append({"slug": article["slug"], "title": article["title"],
                                 "matched": hit, "trust": DERIVED})

        missing = [d for d in GAP_DIMENSIONS if not dims.get(d)]
        profiles.append({
            "entity": name,
            "entity_id": eid,
            "entity_type": entity["entity_type"],
            "package": entity.get("source_package"),
            "confidence": entity.get("confidence_score"),
            "verification_status": entity.get("verification_status"),
            "aliases": alias_terms,
            "aliases_trust": CANONICAL if alias_terms else RESEARCH_REQUIRED,
            "dimensions": dims,
            "articles": mentions,
            "missing": missing,
            "status": RESEARCH_REQUIRED if missing else DERIVED,
        })
    return profiles


def gaps(profiles=None, entity_types=("Skill",)):
    """The research tasks, one per entity missing anything.

    This is NOT knowledge. It is a list of questions, and it is the honest
    output of a platform that holds many trade names and few courses.
    """
    profiles = build(entity_types) if profiles is None else profiles
    return [{
        "entity": p["entity"],
        "entity_id": p["entity_id"],
        "entity_type": p["entity_type"],
        "missing": p["missing"],
        "have": [d for d in GAP_DIMENSIONS if d not in p["missing"]],
        "status": RESEARCH_REQUIRED,
    } for p in profiles if p["missing"]]


def coverage(profiles=None, entity_types=("Skill",)):
    """How much of each dimension the platform actually holds."""
    profiles = build(entity_types) if profiles is None else profiles
    total = len(profiles)
    out = {"entities": total, "dimensions": {}}
    for dim in GAP_DIMENSIONS:
        have = sum(1 for p in profiles if p["dimensions"].get(dim))
        out["dimensions"][dim] = {
            "have": have, "missing": total - have,
            "pct": round(100 * have / total, 1) if total else 0.0}
    out["with_article"] = sum(1 for p in profiles if p["articles"])
    out["complete"] = sum(1 for p in profiles if not p["missing"])
    return out
