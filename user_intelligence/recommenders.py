#!/usr/bin/env python3
"""
The ten recommendation categories.

Every recommendation carries the four things the brief requires — **reason,
supporting entities, confidence, timestamp** — and two more that make it usable:
the rule that fired, and a match score kept separate from confidence.

SCORE AND CONFIDENCE ARE DIFFERENT NUMBERS
------------------------------------------
  match_score   how well this fits *this user*. Computed by the rules.
  confidence    how much the underlying rows can be *trusted*. Inherited from the
                graph — the minimum confidence across the supporting evidence.

A perfect match resting on a confidence-50 row is a strong claim about weak data.
One number cannot say that, so there are two.

TWO CATEGORIES HAVE NO DATA
---------------------------
`mentors` and `events` are in the brief and have no backing anywhere in the
platform — no entity type, no table, no column. They return `NO_DATA_SOURCE` with
the reason, and emit zero recommendations. Inventing a mentor would be the exact
failure this platform is built to avoid.

Two more are sparse and say so in `sparse_note`: `courses` (TRAINED_BY has 3
edges) and `markets` (SELLS_TO has 12).
"""

from collections import defaultdict
from dataclasses import dataclass, field

from user_intelligence.config import (CATEGORIES_BY_KEY, MAX_PER_CATEGORY,
                                      MIN_MATCH_SCORE, ROOT)
from user_intelligence.context import load_idea_library
from user_intelligence.profiles import _matched_businesses, _skill_attrs
from user_intelligence.rules import Evidence, band

NO_DATA_SOURCE = "NO_DATA_SOURCE"
OK, EMPTY = "OK", "NO_MATCHES"


@dataclass
class Recommendation:
    category: str
    item_id: str
    item_label: str
    item_type: str
    match_score: float
    confidence: int
    reason: str
    rule: str
    supporting_entities: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "category": self.category,
            "item_id": self.item_id,
            "item_label": self.item_label,
            "item_type": self.item_type,
            "match_score": round(self.match_score, 1),
            "confidence": self.confidence,
            "confidence_band": band(self.confidence),
            "reason": self.reason,
            "rule": self.rule,
            "supporting_entities": [e.to_dict() for e in self.supporting_entities],
            "detail": self.detail,
        }


@dataclass
class CategoryResult:
    key: str
    label: str
    status: str
    recommendations: list = field(default_factory=list)
    note: str = ""

    def to_dict(self):
        return {"category": self.key, "label": self.label, "status": self.status,
                "count": len(self.recommendations), "note": self.note,
                "recommendations": [r.to_dict() for r in self.recommendations]}


def _finish(spec, recs, note=""):
    """Filter, rank and cap. Ordering is total, so output is reproducible."""
    kept = [r for r in recs if r.match_score >= MIN_MATCH_SCORE]
    kept.sort(key=lambda r: (-r.match_score, -r.confidence, r.item_id))
    kept = kept[:MAX_PER_CATEGORY]
    status = OK if kept else EMPTY
    if not kept and not note:
        note = (f"no {spec.label.lower()} scored at or above the {MIN_MATCH_SCORE} "
                f"match floor")
    return CategoryResult(spec.key, spec.label, status, kept,
                          "; ".join(x for x in (note, spec.sparse_note) if x))


def _no_data(spec):
    return CategoryResult(spec.key, spec.label, NO_DATA_SOURCE, [],
                          spec.no_data_reason)


def _min_conf(evidence):
    vals = [e.confidence for e in evidence if e.confidence]
    return min(vals) if vals else 0


# ═══════════════════════════════════════════════════════ 1. Business Ideas
def business_ideas(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["business_ideas"]
    ideas, sector_labels = load_idea_library()
    recs = []

    resolved_skills, _ = kn.resolve_many("skill", ctx.skills)
    my_skill_norms = {kn.normalise(t) for t, _, _ in resolved_skills} | \
        {kn.normalise(s) for s in ctx.skills}
    district_entity, _ = kn.resolve("district", ctx.location_term)
    my_sectors = {kn.normalise(s) for s in list(ctx.top_sectors) + list(ctx.interests)}

    # RB1/RB2/RB3 over the 122 editorial ideas.
    for idea in ideas:
        score, reasons, ev = 0.0, [], []

        overlap = [s for s in (idea.get("skills_needed") or [])
                   if kn.normalise(s) in my_skill_norms]
        if overlap:
            score += min(50, 18 * len(overlap))
            reasons.append(f"needs {len(overlap)} skill(s) you list: "
                           f"{', '.join(sorted(overlap)[:3])}")
            ev.append(Evidence("profile_field", "skills", "your skills",
                               ", ".join(sorted(overlap)[:5])))

        fits = [d for d in (idea.get("district_fit") or [])
                if district_entity and kn.normalise(d) ==
                kn.normalise(ctx.location_term)]
        if fits:
            score += 30
            reasons.append(f"listed as viable in {fits[0]}")
            ev.append(kn.entity_evidence(district_entity, "your district"))

        sector_label = sector_labels.get(idea.get("sector"), idea.get("sector", ""))
        if kn.normalise(sector_label) in my_sectors or \
                kn.normalise(idea.get("sector", "")) in my_sectors:
            score += 20
            reasons.append(f"matches your declared interest in {sector_label}")

        if idea.get("beginner_friendly") and not resolved_skills:
            score += 10
            reasons.append("beginner-friendly, and no skills resolve yet")

        if score:
            recs.append(Recommendation(
                category=spec.key, item_id=f"idea:{idea['slug']}",
                item_label=idea.get("title", idea["slug"]), item_type="Idea",
                match_score=score,
                # Zero, and deliberately NOT _min_conf(ev).
                #
                # `confidence` means "how much can this ITEM be trusted". An
                # idea-library entry is editorial and carries no confidence score
                # at all. The evidence may include a graph entity — the resolved
                # district, at confidence 73 — but that is confidence in the
                # DISTRICT, not in the idea. Borrowing it would dress an
                # unsourced idea in a researched row's credibility, which is the
                # one line this platform exists to hold.
                confidence=0,
                reason="; ".join(reasons), rule="RB1-SKILL_MATCH",
                supporting_entities=ev,
                detail={"sector": sector_label, "bucket": idea.get("bucket"),
                        "investment_min": idea.get("investment_min"),
                        "source": "idea_library (editorial, not researched)",
                        "confidence_note": "editorial content carries no confidence "
                                           "score; supporting entities may."}))

    # Researched counterparts, which DO carry confidence.
    for m in _matched_businesses(ctx, kn, limit=40):
        ev = [kn.entity_evidence(m["entity"], "researched business")] + \
             [kn.edge_evidence(e) for e in m["edges"][:4]]
        recs.append(Recommendation(
            category=spec.key, item_id=m["entity_id"],
            item_label=m["entity"]["canonical_name"],
            item_type=m["entity"]["entity_type"],
            match_score=m["coverage_pct"], confidence=_min_conf(ev),
            reason=f"you cover {len(m['covered'])} of {len(m['required'])} "
                   f"required skills",
            rule="RB1-SKILL_MATCH", supporting_entities=ev,
            detail={"skills_missing": len(m["missing"]),
                    "source": "researched (Package004/008)"}))
    return _finish(spec, recs)


# ══════════════════════════════════════════════════ 2. Government Schemes
def government_schemes(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["government_schemes"]
    recs, seen = [], {}

    # RS1 — through a matched business. The strongest path: it explains itself.
    for m in _matched_businesses(ctx, kn, limit=40):
        for scheme, edge in kn.neighbours(m["entity_id"], "SUPPORTED_BY_SCHEME",
                                          "out"):
            sid = scheme["global_entity_id"]
            ev = [kn.entity_evidence(scheme), kn.entity_evidence(m["entity"]),
                  kn.edge_evidence(edge)]
            cand = Recommendation(
                category=spec.key, item_id=sid,
                item_label=scheme["canonical_name"], item_type="GovernmentScheme",
                match_score=min(100, 40 + m["coverage_pct"] * 0.5),
                confidence=_min_conf(ev),
                reason=f"supports {m['entity']['canonical_name']}, which matches "
                       f"{m['coverage_pct']}% of your skills",
                rule="RS1-VIA_BUSINESS", supporting_entities=ev)
            if sid not in seen or cand.match_score > seen[sid].match_score:
                seen[sid] = cand

    # RS2 — through the district.
    district, _ = kn.resolve("district", ctx.location_term)
    if district:
        for scheme, edge in kn.neighbours(district["global_entity_id"],
                                          "SUPPORTED_BY_SCHEME", "in"):
            sid = scheme["global_entity_id"]
            if sid in seen:
                continue
            ev = [kn.entity_evidence(scheme), kn.entity_evidence(district),
                  kn.edge_evidence(edge)]
            seen[sid] = Recommendation(
                category=spec.key, item_id=sid,
                item_label=scheme["canonical_name"], item_type="GovernmentScheme",
                match_score=45, confidence=_min_conf(ev),
                reason=f"available in {district['canonical_name']}",
                rule="RS2-VIA_DISTRICT", supporting_entities=ev)

    # RS3 — through a skill.
    resolved, _ = kn.resolve_many("skill", ctx.skills)
    for term, skill, _ in resolved:
        for scheme, edge in kn.neighbours(skill["global_entity_id"],
                                          "SUPPORTED_BY_SCHEME", "out"):
            sid = scheme["global_entity_id"]
            if sid in seen:
                continue
            ev = [kn.entity_evidence(scheme), kn.entity_evidence(skill),
                  kn.edge_evidence(edge)]
            seen[sid] = Recommendation(
                category=spec.key, item_id=sid,
                item_label=scheme["canonical_name"], item_type="GovernmentScheme",
                match_score=35, confidence=_min_conf(ev),
                reason=f"supports training in {skill['canonical_name']}, "
                       f"which you list as '{term}'",
                rule="RS3-VIA_SKILL", supporting_entities=ev)

    return _finish(spec, list(seen.values()))


# ═════════════════════════════════════════════════════════════ 3. Courses
def courses(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["courses"]
    recs = []
    roadmap = scores.get("learning_roadmap")
    steps = (getattr(roadmap, "detail", {}) or {}).get("steps", [])

    for step in steps:
        sid = step["entity_id"]
        skill = kn.entities.get(sid)
        if not skill:
            continue

        # RC1 — a real training provider for this gap skill.
        providers = kn.neighbours(sid, "TRAINED_BY", "out")
        for provider, edge in providers:
            ev = [kn.entity_evidence(provider), kn.entity_evidence(skill),
                  kn.edge_evidence(edge)]
            recs.append(Recommendation(
                category=spec.key, item_id=provider["global_entity_id"],
                item_label=provider["canonical_name"], item_type="TrainingProvider",
                match_score=min(100, 60 + step["unlocks_businesses"] * 8),
                confidence=_min_conf(ev),
                reason=f"trains {skill['canonical_name']}, which unlocks "
                       f"{step['unlocks_businesses']} matched business(es)",
                rule="RC1-FOR_GAP_SKILL", supporting_entities=ev,
                detail={"gap_skill": skill["canonical_name"],
                        "roadmap_step": step["step"]}))

        # RC2 — no provider edge: fall back to a same-category certification.
        # Weaker, and labelled as weaker.
        if not providers:
            cat = _skill_attrs(kn, sid).get("category_name", "")
            if not cat:
                continue
            for cert in kn.by_type.get("Certification", []):
                if kn.normalise(cat) not in kn.normalise(cert["canonical_name"]):
                    continue
                ev = [kn.entity_evidence(cert), kn.entity_evidence(skill)]
                recs.append(Recommendation(
                    category=spec.key, item_id=cert["global_entity_id"],
                    item_label=cert["canonical_name"], item_type="Certification",
                    match_score=30, confidence=_min_conf(ev),
                    reason=f"certification in the same category as your gap skill "
                           f"{skill['canonical_name']} — no direct training link "
                           f"exists in the graph",
                    rule="RC2-PROVIDER_IN_DISTRICT", supporting_entities=ev,
                    detail={"match_basis": "category name, not a TRAINED_BY edge"}))
    return _finish(spec, recs)


# ════════════════════════════════════════════════════════════ 4. Research
def research(ctx, kn, scores, articles=()):
    """
    Research articles come from Supabase at runtime, so the caller supplies them.

    Passing them in rather than querying keeps the engine free of a Supabase
    client. With none supplied the category is honestly empty rather than absent.
    """
    spec = CATEGORIES_BY_KEY["research"]
    if not articles:
        return CategoryResult(
            spec.key, spec.label, EMPTY, [],
            "no research_articles rows were supplied to the engine. This category "
            "reads a live Supabase table; the caller passes the rows in.")

    recs = []
    district_term = kn.normalise(ctx.location_term)
    my_sectors = {kn.normalise(s) for s in list(ctx.top_sectors) + list(ctx.interests)}

    for a in sorted(articles, key=lambda x: str(x.get("slug", ""))):
        score, reasons = 0.0, []
        text = kn.normalise(" ".join(str(a.get(k, "")) for k in
                                     ("title", "summary", "district", "sector")))
        if district_term and district_term in text:
            score += 55
            reasons.append(f"covers {ctx.location_term}")
        hit = sorted(s for s in my_sectors if s and s in text)
        if hit:
            score += 45
            reasons.append(f"matches your interest in {hit[0]}")
        if score:
            recs.append(Recommendation(
                category=spec.key, item_id=f"article:{a.get('slug', a.get('id'))}",
                item_label=a.get("title", ""), item_type="ResearchArticle",
                match_score=score, confidence=0,
                reason="; ".join(reasons),
                rule="RR1-DISTRICT_TAG" if district_term in text else "RR2-SECTOR_TAG",
                supporting_entities=[Evidence("supabase", "research_articles",
                                              "research article", a.get("slug", ""))],
                detail={"source": "research_articles (editorial, no confidence score)"}))
    return _finish(spec, recs)


# ═════════════════════════════════════════════════════════════ 5. Mentors
def mentors(ctx, kn, scores):
    """No mentor data exists. Returns NO_DATA_SOURCE rather than guessing."""
    return _no_data(CATEGORIES_BY_KEY["mentors"])


# ═══════════════════════════════════════════════════════ 6. Collaborators
def collaborators(ctx, kn, scores, candidates=()):
    """
    Candidates are other users' rows, supplied by the caller.

    The engine never queries for people. A caller that has already applied its own
    visibility rules passes the rows in, so the engine cannot leak a profile the
    caller would not have shown.
    """
    spec = CATEGORIES_BY_KEY["collaborators"]
    if not candidates:
        return CategoryResult(
            spec.key, spec.label, EMPTY, [],
            "no candidate profiles were supplied. The caller passes these in so "
            "that its own visibility rules apply before the engine sees anyone.")

    mine, _ = kn.resolve_many("skill", ctx.skills)
    mine_ids = {e["global_entity_id"] for _, e, _ in mine}
    my_district = kn.normalise(ctx.location_term)
    my_sectors = {kn.normalise(s) for s in list(ctx.top_sectors) + list(ctx.interests)}

    recs = []
    for cand in sorted(candidates, key=lambda c: str(c.get("id", ""))):
        if cand.get("id") == ctx.user_id:
            continue
        score, reasons, ev = 0.0, [], []

        theirs, _ = kn.resolve_many("skill", cand.get("skills") or [])
        theirs_ids = {e["global_entity_id"] for _, e, _ in theirs}
        complementary = sorted(theirs_ids - mine_ids)
        if complementary:
            score += min(50, 15 * len(complementary))
            names = [kn.entities[s]["canonical_name"] for s in complementary[:3]
                     if s in kn.entities]
            reasons.append(f"brings {len(complementary)} skill(s) you do not have: "
                           f"{', '.join(names)}")
            ev.extend(kn.entity_evidence(kn.entities[s], "their skill")
                      for s in complementary[:5] if s in kn.entities)

        if my_district and kn.normalise(cand.get("city", "")).startswith(my_district):
            score += 30
            reasons.append(f"also in {ctx.location_term}")
            # Recorded as evidence even though it is a profile field rather than a
            # graph entity: the brief requires supporting entities on every
            # recommendation, and "we matched on city" is the supporting fact.
            ev.append(Evidence("profile_field", "city", "same location",
                               ctx.location_term))

        shared = my_sectors & {kn.normalise(s) for s in (cand.get("interests") or [])}
        if shared:
            score += 20
            reasons.append(f"shares your interest in {sorted(shared)[0]}")
            ev.append(Evidence("profile_field", "interests", "shared interest",
                               sorted(shared)[0]))

        if score:
            recs.append(Recommendation(
                category=spec.key, item_id=f"user:{cand.get('id')}",
                item_label=cand.get("name", "") or "(unnamed)", item_type="Profile",
                match_score=score, confidence=_min_conf(ev),
                reason="; ".join(reasons), rule="RL1-COMPLEMENTARY_SKILL",
                supporting_entities=ev,
                detail={"complementary_skill_count": len(complementary)}))
    return _finish(spec, recs)


# ══════════════════════════════════════════════════════════════ 7. Events
def events(ctx, kn, scores):
    """No event data exists anywhere. Returns NO_DATA_SOURCE."""
    return _no_data(CATEGORIES_BY_KEY["events"])


# ═════════════════════════════════════════════════════════════ 8. Markets
def markets(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["markets"]
    recs, seen = [], {}

    for m in _matched_businesses(ctx, kn, limit=40):
        for market, edge in kn.neighbours(m["entity_id"], "SELLS_TO", "out"):
            mid = market["global_entity_id"]
            ev = [kn.entity_evidence(market), kn.entity_evidence(m["entity"]),
                  kn.edge_evidence(edge)]
            cand = Recommendation(
                category=spec.key, item_id=mid,
                item_label=market["canonical_name"], item_type="Market",
                match_score=min(100, 45 + m["coverage_pct"] * 0.4),
                confidence=_min_conf(ev),
                reason=f"channel used by {m['entity']['canonical_name']}, which "
                       f"matches {m['coverage_pct']}% of your skills",
                rule="RM1-VIA_BUSINESS", supporting_entities=ev)
            if mid not in seen or cand.match_score > seen[mid].match_score:
                seen[mid] = cand
    return _finish(spec, list(seen.values()))


# ═══════════════════════════════════════════════════════════════ 9. MSMEs
def msmes(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["msmes"]
    recs = []
    district, _ = kn.resolve("district", ctx.location_term)

    for m in _matched_businesses(ctx, kn, limit=40):
        if m["entity"]["entity_type"] != "MSME":
            continue
        score = m["coverage_pct"]
        reasons = [f"you cover {len(m['covered'])} of {len(m['required'])} "
                   f"required skills"]
        ev = [kn.entity_evidence(m["entity"])] + \
             [kn.edge_evidence(e) for e in m["edges"][:4]]

        # RN2 — does it operate where the user is?
        if district:
            local = [d for d, _ in kn.neighbours(m["entity_id"],
                                                 "GENERATES_EMPLOYMENT", "out")
                     if d["global_entity_id"] == district["global_entity_id"]]
            if local:
                score = min(100, score + 25)
                reasons.append(f"generates employment in {district['canonical_name']}")
                ev.append(kn.entity_evidence(district, "your district"))

        recs.append(Recommendation(
            category=spec.key, item_id=m["entity_id"],
            item_label=m["entity"]["canonical_name"], item_type="MSME",
            match_score=score, confidence=_min_conf(ev),
            reason="; ".join(reasons), rule="RN1-SKILL_MATCH",
            supporting_entities=ev,
            detail={"skills_missing": len(m["missing"])}))
    return _finish(spec, recs)


# ══════════════════════════════════════════════════════════ 10. Industries
def industries(ctx, kn, scores):
    spec = CATEGORIES_BY_KEY["industries"]
    seen = {}

    # RI1 — through a resolved skill.
    resolved, _ = kn.resolve_many("skill", ctx.skills)
    for term, skill, _ in resolved:
        for biz, _e in kn.neighbours(skill["global_entity_id"], "REQUIRES_SKILL", "in"):
            for industry, edge in kn.neighbours(biz["global_entity_id"], "PART_OF",
                                                "out", entity_type="Industry"):
                iid = industry["global_entity_id"]
                ev = [kn.entity_evidence(industry), kn.entity_evidence(skill),
                      kn.edge_evidence(edge)]
                cand = Recommendation(
                    category=spec.key, item_id=iid,
                    item_label=industry["canonical_name"], item_type="Industry",
                    match_score=60, confidence=_min_conf(ev),
                    reason=f"businesses in this industry require "
                           f"{skill['canonical_name']}, which you list as '{term}'",
                    rule="RI1-VIA_SKILL", supporting_entities=ev)
                if iid not in seen:
                    seen[iid] = cand

    # RI2 — a declared interest that resolves to an Industry directly.
    sectors, _ = kn.resolve_many("sector", list(ctx.top_sectors) + list(ctx.interests))
    for term, industry, row in sectors:
        iid = industry["global_entity_id"]
        ev = [kn.entity_evidence(industry)]
        cand = Recommendation(
            category=spec.key, item_id=iid,
            item_label=industry["canonical_name"], item_type="Industry",
            match_score=75, confidence=_min_conf(ev),
            reason=f"you declared an interest in '{term}', which maps to this "
                   f"industry ({row['match_method']})",
            rule="RI2-VIA_INTEREST", supporting_entities=ev)
        if iid not in seen or cand.match_score > seen[iid].match_score:
            seen[iid] = cand

    # RI3 — present in the user's district.
    district, _ = kn.resolve("district", ctx.location_term)
    if district:
        for industry, edge in kn.neighbours(district["global_entity_id"], "LOCATED_IN",
                                            "in", entity_type="Industry"):
            iid = industry["global_entity_id"]
            if iid in seen:
                continue
            ev = [kn.entity_evidence(industry), kn.entity_evidence(district),
                  kn.edge_evidence(edge)]
            seen[iid] = Recommendation(
                category=spec.key, item_id=iid,
                item_label=industry["canonical_name"], item_type="Industry",
                match_score=40, confidence=_min_conf(ev),
                reason=f"present in {district['canonical_name']}",
                rule="RI3-VIA_DISTRICT", supporting_entities=ev)
    return _finish(spec, list(seen.values()))


#: category key -> callable. Extra kwargs are passed by the engine where a
#: category needs caller-supplied rows.
RECOMMENDERS = {
    "business_ideas": business_ideas,
    "government_schemes": government_schemes,
    "courses": courses,
    "research": research,
    "mentors": mentors,
    "collaborators": collaborators,
    "events": events,
    "markets": markets,
    "msmes": msmes,
    "industries": industries,
}
