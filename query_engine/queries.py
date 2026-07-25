#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Named Queries (Module 5)

The five business questions from the Platform v2 brief, expressed as functions over
QueryEngine. This module holds the domain vocabulary; engine.py holds none.

Each function returns a list of Result objects. Every Result can produce the exact
(package, dataset, row_id) chain that supports it — see Result.provenance().

Run directly to execute all five against the built graph:
    python3 query_engine/queries.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from query_engine.engine import QueryEngine                      # noqa: E402
from knowledge_graph.resolution.resolver import Resolver         # noqa: E402


class Queries:
    """Named business questions. Surface forms are resolved, never string-matched."""

    def __init__(self, engine=None, resolver=None):
        self.qe = engine or QueryEngine()
        self.rz = resolver or Resolver()

    def _entity_id(self, surface_form, entity_type):
        e = self.rz.resolve(surface_form, entity_type=entity_type)
        return e["global_entity_id"] if e else None

    # ---------------------------------------------------------------- Query 1
    def businesses_requiring_skill(self, skill_name, min_confidence=0):
        """
        "Find all businesses requiring Python."

        Skill <-REQUIRES_SKILL- MSME|BusinessOpportunity|Industry
        """
        sid = self._entity_id(skill_name, "Skill")
        if not sid:
            return []
        hits = self.qe.neighbours(sid, rel_type="REQUIRES_SKILL", direction="in")
        return self.qe.rank(hits, min_confidence)

    # ---------------------------------------------------------------- Query 2
    def schemes_supporting(self, subject_name, subject_type=None, min_confidence=0):
        """
        "Find all schemes supporting Millet Processing."

        Subject -SUPPORTED_BY_SCHEME-> GovernmentScheme

        subject_type is optional: the resolver tries MSME, then Crop, then
        BusinessOpportunity, so a caller does not need to know which package owns
        the thing they are asking about. That is the point of the graph.
        """
        candidates = [subject_type] if subject_type else \
            ["MSME", "Crop", "BusinessOpportunity", "Skill"]
        for etype in candidates:
            sid = self._entity_id(subject_name, etype)
            if sid:
                hits = self.qe.neighbours(sid, rel_type="SUPPORTED_BY_SCHEME",
                                          direction="out")
                if hits:
                    return self.qe.rank(hits, min_confidence)
        return []

    # ---------------------------------------------------------------- Query 3
    def skills_needed_for(self, business_name, min_confidence=0):
        """
        "Find all skills needed for Solar EPC."

        MSME|BusinessOpportunity -REQUIRES_SKILL-> Skill
        """
        for etype in ("MSME", "BusinessOpportunity", "Industry"):
            bid = self._entity_id(business_name, etype)
            if bid:
                hits = self.qe.neighbours(bid, rel_type="REQUIRES_SKILL", direction="out")
                if hits:
                    return self.qe.rank(hits, min_confidence)
        return []

    # ---------------------------------------------------------------- Query 4
    def districts_suitable_for(self, industry_or_business, min_confidence=0):
        """
        "Find districts suitable for Food Processing."

        Two paths, because the question can mean either:
          a) a named business          -> GENERATES_EMPLOYMENT -> District
          b) an industry category      -> its member businesses -> District

        Path (b) is the interesting one: it crosses Package008 category membership
        into Package001 geography, which no single package can answer.
        """
        bid = self._entity_id(industry_or_business, "MSME")
        if bid:
            hits = self.qe.neighbours(bid, rel_type="GENERATES_EMPLOYMENT", direction="out")
            return self.qe.rank(hits, min_confidence)

        iid = self._entity_id(industry_or_business, "Industry")
        if not iid:
            return []
        # Industry -> member MSMEs is not a direct edge; MSMEs carry category_name.
        # Walk instead through businesses whose category resolves to this industry.
        industry_name = self.rz.get(iid)["canonical_name"]
        out, seen = [], set()
        for msme in self.qe.g.by_type("MSME"):
            mid = msme["global_entity_id"]
            for d in self.qe.neighbours(mid, rel_type="GENERATES_EMPLOYMENT", direction="out"):
                if d.id in seen:
                    continue
                # Keep only businesses that belong to the requested industry, by
                # checking the source package's own category assignment.
                if not self._msme_in_industry(msme, industry_name):
                    continue
                seen.add(d.id)
                out.append(d)
        return self.qe.rank(out, min_confidence)

    def _msme_in_industry(self, msme_entity, industry_name):
        """Consult Package008's own category assignment; do not infer."""
        if not hasattr(self, "_msme_cat"):
            import csv
            path = (Path(__file__).resolve().parent.parent / "packages" /
                    "Package008_MSME" / "datasets" / "msme_businesses.csv")
            with open(path, newline="", encoding="utf-8") as f:
                self._msme_cat = {r["business_name"]: r["category_name"]
                                  for r in csv.DictReader(f)}
        cat = self._msme_cat.get(msme_entity["canonical_name"], "")
        return cat.lower() == industry_name.lower()

    # ---------------------------------------------------------------- Query 5
    def ai_tools_used_in(self, industry_name, min_confidence=0):
        """
        "Find AI tools used in Manufacturing."

        Industry -USES_AI-> Industry (AI Tooling: * / AgriTech: *)
        """
        iid = self._entity_id(industry_name, "Industry")
        if not iid:
            return []
        hits = self.qe.neighbours(iid, rel_type="USES_AI", direction="out")
        return self.qe.rank(hits, min_confidence)

    # ------------------------------------------------- additional traversals
    def full_business_context(self, business_name):
        """
        Everything the graph knows about one MSME, in one call. This is the query
        that justifies the whole layer: it spans six packages and no single package
        could answer it.
        """
        bid = self._entity_id(business_name, "MSME")
        if not bid:
            return {}
        return {
            "business": self.qe.get(bid).to_dict(),
            "skills": [r.to_dict() for r in
                       self.qe.neighbours(bid, "REQUIRES_SKILL", "out")],
            "schemes": [r.to_dict() for r in
                        self.qe.neighbours(bid, "SUPPORTED_BY_SCHEME", "out")],
            "machinery": [r.to_dict() for r in
                          self.qe.neighbours(bid, "USES_MACHINERY", "out")],
            "raw_materials": [r.to_dict() for r in
                              self.qe.neighbours(bid, "USES_RAW_MATERIAL", "out")],
            "crops_processed": [r.to_dict() for r in
                                self.qe.neighbours(bid, "PROCESSES", "out")],
            "districts": [r.to_dict() for r in
                          self.qe.neighbours(bid, "GENERATES_EMPLOYMENT", "out")],
            "export_countries": [r.to_dict() for r in
                                 self.qe.neighbours(bid, "EXPORTS_TO", "out")],
            "banks": [r.to_dict() for r in
                      self.qe.neighbours(bid, "SUPPORTED_BY_BANK", "out")],
        }

    def crop_to_opportunity(self, crop_name):
        """Crop -> businesses that process it -> the schemes supporting those."""
        cid = self._entity_id(crop_name, "Crop")
        if not cid:
            return {}
        processors = self.qe.neighbours(cid, "PROCESSES", "in")
        schemes = self.qe.traverse(cid, [("PROCESSES", "in"),
                                         ("SUPPORTED_BY_SCHEME", "out")])
        return {
            "crop": self.qe.get(cid).to_dict(),
            "processed_by": [r.to_dict() for r in processors],
            "schemes_reachable": [r.to_dict() for r in self.qe.rank(schemes)],
        }


# --------------------------------------------------------------------------
def _show(title, results, limit=8):
    print(f"\n{title}")
    print("-" * len(title))
    if not results:
        print("  (no results)")
        return
    for r in results[:limit]:
        prov = r.provenance()
        src = f"{prov[0]['package']}/{prov[0]['dataset']}" if prov else r.entity["source_package"]
        print(f"  [{r.min_confidence():>2}] {r.entity_type:<20} {r.name[:52]:<52} <- {src}")
    if len(results) > limit:
        print(f"  ... and {len(results) - limit} more")


if __name__ == "__main__":
    q = Queries()
    print("ValueWeave Query Engine — the five named queries from the Platform v2 brief")
    print(f"graph: {q.qe.stats()}")

    _show("1. Find all businesses requiring Python",
          q.businesses_requiring_skill("Python"))

    _show("2. Find all schemes supporting Millet Processing",
          q.schemes_supporting("Millet Processing"))

    _show("3. Find all skills needed for Solar EPC",
          q.skills_needed_for("Solar Rooftop EPC Contractor"))

    _show("4. Find districts suitable for Food Processing",
          q.districts_suitable_for("Food Processing"))

    _show("5. Find AI tools used in Manufacturing",
          q.ai_tools_used_in("Manufacturing"))

    print("\n\n6. Cross-package traversal: full context for one business")
    print("-" * 56)
    ctx = q.full_business_context("Turmeric")
    if not ctx:
        ctx = q.full_business_context("Spice Grinding and Packing Unit")
    if ctx:
        print(f"  {ctx['business']['canonical_name']}")
        for k in ("skills", "schemes", "machinery", "raw_materials",
                  "crops_processed", "districts", "export_countries", "banks"):
            names = [x["canonical_name"] for x in ctx[k]]
            if names:
                shown = ", ".join(names[:4])
                more = f" (+{len(names) - 4})" if len(names) > 4 else ""
                print(f"    {k:<18} {len(names):>2}  {shown}{more}")

    print("\n\n7. Provenance: every answer traces to a package row")
    print("-" * 52)
    res = q.businesses_requiring_skill("Python")
    if res:
        r = res[0]
        print(f"  {r.name} requires Python because:")
        for p in r.provenance():
            print(f"    {p['package']}/{p['dataset']} row {p['row_id']} "
                  f"({p['relationship']}, confidence {p['confidence']})")
