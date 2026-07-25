#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Entity Resolution Engine (Module 4)

Four capabilities, in the order they are applied:

  1. Canonical naming   normalise a surface form to the canonical name of an entity
  2. Alias resolution   look up an entity by any registered alias
  3. Duplicate detection find entities that are probably the same thing
  4. Cross-package linking resolve a (package, local_id) pair to a global_entity_id

Plus a fifth that is deliberately NOT automatic:

  5. Merge support      propose merges for human decision, never execute them

DESIGN POSITION on automatic merging
------------------------------------
This engine does not merge entities. It proposes. Merging two entities is a
destructive, irreversible assertion that two package-owned records describe one
real thing, and getting it wrong silently corrupts every query that traverses the
merged node. Package006 alone contains "Electrician (Domestic Wiring)" and
"Industrial Electrician" — similar strings, genuinely different skills.

`propose_merges()` emits candidates with a similarity score and the evidence behind
it. A data steward accepts or rejects. See governance/DATA_GOVERNANCE.md for the
review workflow and ADR-004 for the reasoning.

Usage:
    from knowledge_graph.resolution.resolver import Resolver
    r = Resolver()
    r.resolve("PM-KISAN")                       -> the scheme entity
    r.resolve("Python", entity_type="Skill")    -> Python Programming
    r.by_local_id("Package005_Agriculture", "crop-001")
    r.propose_merges(threshold=0.86)
"""

import csv
import difflib
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

KG = Path(__file__).resolve().parent.parent
ENTITIES = KG / "entities" / "entities.csv"
ALIASES = KG / "entities" / "aliases.csv"

# Tokens that carry no discriminating meaning when comparing entity names.
STOPWORDS = {
    "the", "of", "and", "for", "in", "a", "an", "unit", "scheme", "yojana",
    "small", "scale", "service", "services", "centre", "center", "india",
    "indian", "national", "state", "government", "ltd", "limited",
}


def normalise(text):
    """Canonical comparison form: ascii, lowercase, punctuation stripped."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"\([^)]*\)", " ", text)          # drop parenthetical qualifiers
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def normalise_full(text):
    """Comparison form. Unlike normalise(), KEEPS parenthetical qualifiers.

    Dropping them is correct for lookup and wrong for duplicate detection:
    "Manufacturing" and "Manufacturing (Automotive)" are a parent and a child,
    not the same entity, and collapsing them scored a false 1.000.
    """
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def tokens(text):
    return {t for t in normalise_full(text).split() if t and t not in STOPWORDS}


class Resolver:
    def __init__(self, entities_path=ENTITIES, aliases_path=ALIASES):
        self.entities = []
        self.by_gid = {}
        self.by_norm = defaultdict(list)      # normalised name -> [entity]
        self.by_type_norm = {}                # (type, normalised) -> entity
        self.by_local = {}                    # (package, local_id) -> entity
        self.alias_index = defaultdict(list)  # normalised alias -> [entity]

        with open(entities_path, newline="", encoding="utf-8") as f:
            for e in csv.DictReader(f):
                self.entities.append(e)
                self.by_gid[e["global_entity_id"]] = e
                n = normalise(e["canonical_name"])
                self.by_norm[n].append(e)
                key = (e["entity_type"], n)
                # An exact full-name match must win over one that only matches
                # after parenthetical stripping, or "Manufacturing (General)"
                # shadows "Manufacturing".
                prior = self.by_type_norm.get(key)
                exact_now = normalise_full(e["canonical_name"]) == n
                exact_prior = prior and normalise_full(prior["canonical_name"]) == n
                if prior is None or (exact_now and not exact_prior):
                    self.by_type_norm[key] = e
                key = (e["source_package"], e["package_local_id"])
                if e["package_local_id"] and e["package_local_id"] != "PENDING_VERIFICATION":
                    self.by_local[key] = e

        if Path(aliases_path).exists():
            with open(aliases_path, newline="", encoding="utf-8") as f:
                for a in csv.DictReader(f):
                    ent = self.by_gid.get(a["global_entity_id"])
                    if ent:
                        self.alias_index[normalise(a["alias"])].append(ent)

    # ---------------------------------------------------------------- lookup
    def get(self, global_entity_id):
        return self.by_gid.get(global_entity_id)

    def by_local_id(self, source_package, package_local_id):
        """Cross-package linking: (package, local id) -> global entity."""
        return self.by_local.get((source_package, package_local_id))

    def resolve(self, surface_form, entity_type=None, fuzzy=True, cutoff=0.88):
        """
        Resolve a surface form to exactly one entity, or None.

        Order: exact canonical -> registered alias -> fuzzy (optional).
        Returns None rather than guessing when the result is ambiguous.
        """
        n = normalise(surface_form)

        # 1. exact canonical
        if entity_type:
            hit = self.by_type_norm.get((entity_type, n))
            if hit:
                return hit
        else:
            hits = self.by_norm.get(n, [])
            if len(hits) == 1:
                return hits[0]
            if len(hits) > 1:
                return None       # ambiguous across types; caller must disambiguate

        # 2. registered alias
        alias_hits = [e for e in self.alias_index.get(n, [])
                      if not entity_type or e["entity_type"] == entity_type]
        if len(alias_hits) == 1:
            return alias_hits[0]

        # 3. unique prefix within a type ("Python" -> "Python Programming").
        #    Only fires on exactly one match; two candidates is ambiguity, not a hint.
        if entity_type:
            pref = [e for e in self.entities
                    if e["entity_type"] == entity_type
                    and normalise(e["canonical_name"]).startswith(n + " ")]
            if len(pref) == 1:
                return pref[0]

        # 4. fuzzy, restricted to a type when one is given
        if not fuzzy:
            return None
        pool = [e for e in self.entities
                if not entity_type or e["entity_type"] == entity_type]
        names = {normalise(e["canonical_name"]): e for e in pool}
        close = difflib.get_close_matches(n, list(names), n=2, cutoff=cutoff)
        if len(close) == 1:
            return names[close[0]]
        if len(close) == 2 and close[0] != close[1]:
            # Two plausible matches is exactly the case where guessing is wrong.
            return None
        return None

    def search(self, substring, entity_type=None, limit=25):
        """Substring search for interactive use. Never used by the query engine."""
        n = normalise(substring)
        out = [e for e in self.entities
               if n in normalise(e["canonical_name"])
               and (not entity_type or e["entity_type"] == entity_type)]
        return out[:limit]

    # ------------------------------------------------------ duplicate detection
    @staticmethod
    def similarity(a, b):
        """Blend of token overlap and sequence ratio; both in 0..1."""
        ta, tb = tokens(a), tokens(b)
        jaccard = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
        seq = difflib.SequenceMatcher(None, normalise_full(a), normalise_full(b)).ratio()
        return round(0.6 * jaccard + 0.4 * seq, 4)

    def propose_merges(self, threshold=0.86, same_type_only=True):
        """
        Propose candidate duplicate pairs for HUMAN review.

        Never merges. Returns a list of proposals, each carrying the evidence a
        steward needs to accept or reject: both entity ids, both owning packages,
        the similarity score and which signal drove it.
        """
        proposals = []
        buckets = defaultdict(list)
        for e in self.entities:
            key = e["entity_type"] if same_type_only else "*"
            buckets[key].append(e)

        for _, group in buckets.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a, b = group[i], group[j]
                    score = self.similarity(a["canonical_name"], b["canonical_name"])
                    if score < threshold:
                        continue
                    ta, tb = tokens(a["canonical_name"]), tokens(b["canonical_name"])
                    proposals.append({
                        "entity_a": a["global_entity_id"],
                        "name_a": a["canonical_name"],
                        "package_a": a["source_package"],
                        "entity_b": b["global_entity_id"],
                        "name_b": b["canonical_name"],
                        "package_b": b["source_package"],
                        "entity_type": a["entity_type"],
                        "similarity": score,
                        "shared_tokens": " ".join(sorted(ta & tb)),
                        "distinguishing_tokens": " ".join(sorted(ta ^ tb)),
                        "cross_package": a["source_package"] != b["source_package"],
                        "recommendation": ("REVIEW" if score < 0.95 else "LIKELY_DUPLICATE"),
                        "decision": "PENDING_STEWARD_REVIEW",
                    })
        return sorted(proposals, key=lambda p: -p["similarity"])

    # ----------------------------------------------------------------- stats
    def stats(self):
        by_type = defaultdict(int)
        by_package = defaultdict(int)
        for e in self.entities:
            by_type[e["entity_type"]] += 1
            by_package[e["source_package"]] += 1
        return {
            "entities": len(self.entities),
            "aliases": sum(len(v) for v in self.alias_index.values()),
            "entity_types": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
            "by_source_package": dict(sorted(by_package.items(), key=lambda kv: -kv[1])),
        }


if __name__ == "__main__":
    import json
    import sys

    r = Resolver()
    print(json.dumps(r.stats(), indent=2))

    print("\n-- resolution examples --")
    for form, etype in [("PM-KISAN", None), ("Python", "Skill"),
                        ("Turmeric", "Crop"), ("Hyderabad", "District"),
                        ("Nonexistent Thing", None)]:
        hit = r.resolve(form, entity_type=etype)
        print(f"  {form!r:26} -> {hit['global_entity_id'] if hit else 'UNRESOLVED'}")

    print("\n-- cross-package linking --")
    e = r.by_local_id("Package005_Agriculture", "crop-001")
    print(f"  (Package005, crop-001) -> {e['global_entity_id'] if e else 'UNRESOLVED'}")

    props = r.propose_merges()
    out = KG / "resolution" / "merge_proposals.csv"
    if props:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(props[0].keys()))
            w.writeheader()
            w.writerows(props)
    print(f"\n-- duplicate detection --")
    print(f"  {len(props)} merge proposals written to {out.relative_to(KG.parent)}")
    print("  NONE are applied automatically; every one awaits steward review.")
    for p in props[:8]:
        print(f"    {p['similarity']:.3f}  {p['name_a']!r} <-> {p['name_b']!r} "
              f"({p['entity_type']}, {p['recommendation']})")
