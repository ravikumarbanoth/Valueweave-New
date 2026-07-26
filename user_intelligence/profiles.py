#!/usr/bin/env python3
"""
The eight scored profiles.

Each is a small set of named rules folded by `rules.combine()`. Every rule returns
evidence, so any score can be expanded into the entities and edges that produced
it — `score_result.evidence` is the audit trail, and a score with no evidence is a
bug rather than a low result.

WHY SO MANY RULES RETURN NO_SIGNAL RATHER THAN A LOW NUMBER
----------------------------------------------------------
With a 22.8% skill resolve rate (Step 0) and 86 REQUIRES_SKILL edges, most users
will have little or nothing to score against. A low number implies a measurement
was taken; NO_SIGNAL says none was possible, and names why. Only one of those two
is true, and only one lets a UI write a useful sentence.
"""

from collections import Counter, defaultdict

from user_intelligence.config import STARTUP_WEIGHTS
from user_intelligence.rules import (Evidence, applied, combine, no_signal,
                                     unavailable)

NSQF_MAX = 10


def _int(value, default=0):
    v = str(value or "").strip()
    return int(v) if v.lstrip("-").isdigit() else default


def _skill_attrs(kn, entity_id):
    """Package006-owned attributes for a Skill, read from the source dataset."""
    if not hasattr(kn, "_skill_attr_cache"):
        import csv
        from user_intelligence.config import ROOT
        path = (ROOT / "packages" / "Package006_Skills_and_Training" / "datasets"
                / "skills.csv")
        cache = {}
        if path.exists():
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    cache[kn.normalise(row["skill_name"])] = row
        kn._skill_attr_cache = cache
    ent = kn.entities.get(entity_id) or {}
    return kn._skill_attr_cache.get(kn.normalise(ent.get("canonical_name", "")), {})


# ═══════════════════════════════════════════════════ 1. User Skill Profile
def skill_profile(ctx, kn):
    resolved, unresolved = kn.resolve_many("skill", ctx.skills)
    outcomes = []

    # SK1 — how much of what the user claims we can actually reason about.
    if not ctx.skills:
        outcomes.append(unavailable("SK1-RESOLVED",
                                    "the profile lists no skills"))
    elif not resolved:
        outcomes.append(no_signal(
            "SK1-RESOLVED",
            f"none of {len(ctx.skills)} claimed skills has a researched "
            f"counterpart yet: " + "; ".join(r for _, r in unresolved[:3]),
            evidence=[Evidence("crosswalk", f"unresolved:{t}", t, reason)
                      for t, reason in unresolved[:6]]))
    else:
        rate = 100 * len(resolved) / len(ctx.skills)
        outcomes.append(applied(
            "SK1-RESOLVED", rate,
            f"{len(resolved)} of {len(ctx.skills)} skills resolve to the knowledge "
            f"graph",
            evidence=[kn.entity_evidence(e, f"claimed as '{t}'")
                      for t, e, _ in resolved], weight=2.0))

    # SK2 — depth. NSQF is a national qualification level, not our invention.
    levels = [_int(_skill_attrs(kn, e["global_entity_id"]).get("nsqf_level"))
              for _, e, _ in resolved]
    levels = [x for x in levels if x]
    if levels:
        outcomes.append(applied(
            "SK2-DEPTH", 100 * max(levels) / NSQF_MAX,
            f"highest NSQF level among resolved skills is {max(levels)}",
            evidence=[Evidence("entity", "nsqf", "NSQF depth",
                               f"levels {sorted(levels)}")]))
    else:
        outcomes.append(no_signal("SK2-DEPTH",
                                  "no resolved skill carries an NSQF level"))

    # SK3 — breadth across Package006 categories.
    cats = sorted({_skill_attrs(kn, e["global_entity_id"]).get("category_name", "")
                   for _, e, _ in resolved} - {""})
    if cats:
        outcomes.append(applied("SK3-BREADTH", min(100, len(cats) * 25),
                                f"skills span {len(cats)} category(ies): "
                                f"{', '.join(cats[:4])}"))
    else:
        outcomes.append(no_signal("SK3-BREADTH", "no categorised resolved skill"))

    # SK4 — market demand, from how much of the graph asks for these skills.
    demand, demand_ev = 0, []
    for _, e, _ in resolved:
        requiring = kn.neighbours(e["global_entity_id"], "REQUIRES_SKILL", "in")
        demand += len(requiring)
        demand_ev.extend(kn.edge_evidence(edge, f"requires {e['canonical_name']}")
                         for _, edge in requiring[:3])
    if demand:
        outcomes.append(applied("SK4-DEMAND", min(100, demand * 8),
                                f"{demand} researched businesses require these skills",
                                evidence=demand_ev[:10]))
    else:
        outcomes.append(no_signal(
            "SK4-DEMAND",
            "no researched business requires these skills — 86 REQUIRES_SKILL edges "
            "exist in total, so this is often a coverage gap"))

    result = combine("skill_profile", "User Skill Profile", outcomes,
                     low_means="No claimed skill could be matched to researched data.")
    result.detail = {
        "resolved": [{"term": t, "entity_id": e["global_entity_id"],
                      "canonical_name": e["canonical_name"],
                      "match_method": row["match_method"],
                      "nsqf_level": _int(_skill_attrs(
                          kn, e["global_entity_id"]).get("nsqf_level")) or None}
                     for t, e, row in resolved],
        "unresolved": [{"term": t, "reason": r} for t, r in unresolved],
        "resolve_rate_pct": (round(100 * len(resolved) / len(ctx.skills), 1)
                            if ctx.skills else None),
        "categories": cats,
    }
    return result


# ═════════════════════════════════════════════ 2. Business Readiness
def _matched_businesses(ctx, kn, limit=25):
    """
    Businesses whose required skills the user partly covers.

    Returns rows ordered by coverage then id, so the result is stable. Shared by
    business readiness, learning roadmap, funding and several recommenders — one
    definition of "a business this user matches", used everywhere.
    """
    resolved, _ = kn.resolve_many("skill", ctx.skills)
    have = {e["global_entity_id"] for _, e, _ in resolved}
    if not have:
        return []

    per_business = defaultdict(lambda: {"required": set(), "edges": []})
    for etype in ("MSME", "BusinessOpportunity"):
        for biz in kn.by_type.get(etype, []):
            bid = biz["global_entity_id"]
            for skill, edge in kn.neighbours(bid, "REQUIRES_SKILL", "out"):
                per_business[bid]["required"].add(skill["global_entity_id"])
                per_business[bid]["edges"].append(edge)
                per_business[bid]["entity"] = biz

    out = []
    for bid, info in per_business.items():
        required = info["required"]
        if not required:
            continue
        covered = required & have
        if not covered:
            continue
        out.append({
            "entity": info["entity"],
            "entity_id": bid,
            "required": sorted(required),
            "covered": sorted(covered),
            "missing": sorted(required - have),
            "coverage_pct": round(100 * len(covered) / len(required), 1),
            "edges": info["edges"],
        })
    out.sort(key=lambda m: (-m["coverage_pct"], m["entity_id"]))
    return out[:limit]


def business_readiness(ctx, kn):
    outcomes = []
    matches = _matched_businesses(ctx, kn)

    if not ctx.skills:
        outcomes.append(unavailable("BR1-SKILL_COVERAGE", "the profile lists no skills"))
    elif not matches:
        outcomes.append(no_signal(
            "BR1-SKILL_COVERAGE",
            "no researched business requires any of the user's resolved skills"))
    else:
        best = matches[0]
        outcomes.append(applied(
            "BR1-SKILL_COVERAGE", best["coverage_pct"],
            f"covers {len(best['covered'])} of {len(best['required'])} skills "
            f"required by {best['entity']['canonical_name']}",
            evidence=[kn.entity_evidence(best["entity"], "best skill match")]
                     + [kn.edge_evidence(e) for e in best["edges"][:5]],
            weight=2.0))

    # BR2 — is the user somewhere the graph knows about?
    district, drow = kn.resolve("district", ctx.location_term)
    if not ctx.location_term:
        outcomes.append(unavailable("BR2-DISTRICT",
                                    "no city or district on the profile"))
    elif not district:
        outcomes.append(no_signal(
            "BR2-DISTRICT", kn.explain_unresolved("district", ctx.location_term)))
    else:
        local = kn.neighbours(district["global_entity_id"], None, "in")
        outcomes.append(applied(
            "BR2-DISTRICT", min(100, len(local) * 10),
            f"{len(local)} researched entities are linked to "
            f"{district['canonical_name']}",
            evidence=[kn.entity_evidence(district, "resolved district")]))

    # BR3 — do the user's declared sectors exist as researched industries?
    sectors, unresolved_sectors = kn.resolve_many(
        "sector", list(ctx.top_sectors) + list(ctx.interests))
    if sectors:
        outcomes.append(applied(
            "BR3-CATEGORY_FIT", min(100, len(sectors) * 34),
            f"{len(sectors)} declared sector(s) map to researched industries",
            evidence=[kn.entity_evidence(e, f"from '{t}'") for t, e, _ in sectors]))
    else:
        outcomes.append(no_signal(
            "BR3-CATEGORY_FIT",
            "no declared sector or interest maps to a researched industry"))

    result = combine("business_readiness", "Business Readiness", outcomes,
                     low_means="Skills do not yet cover any researched business.")
    result.detail = {
        "matched_businesses": [
            {"entity_id": m["entity_id"], "name": m["entity"]["canonical_name"],
             "type": m["entity"]["entity_type"], "coverage_pct": m["coverage_pct"],
             "skills_covered": len(m["covered"]), "skills_required": len(m["required"])}
            for m in matches[:10]],
        "resolved_district": district["canonical_name"] if district else None,
        "resolved_sectors": [e["canonical_name"] for _, e, _ in sectors],
    }
    return result


# ═══════════════════════════════════════════════ 3. Learning Roadmap
def learning_roadmap(ctx, kn):
    outcomes = []
    matches = _matched_businesses(ctx, kn)
    resolved, _ = kn.resolve_many("skill", ctx.skills)
    have = {e["global_entity_id"] for _, e, _ in resolved}

    gap_counts = Counter()
    for m in matches:
        for sid in m["missing"]:
            gap_counts[sid] += 1

    if not matches:
        outcomes.append(no_signal(
            "LR1-GAP",
            "no matched business, so there is no gap to compute. Resolve at least "
            "one skill first."))
    else:
        # A high score means a SMALL gap: the roadmap is short.
        total_missing = sum(len(m["missing"]) for m in matches[:5]) or 0
        total_required = sum(len(m["required"]) for m in matches[:5]) or 1
        closeness = 100 * (1 - total_missing / total_required)
        if gap_counts:
            gap_evidence = [
                kn.entity_evidence(kn.entities[sid], f"needed by {n} business(es)")
                for sid, n in gap_counts.most_common(8) if sid in kn.entities]
            gap_reason = (f"{len(gap_counts)} distinct skills separate the user from "
                          f"their top matched businesses")
        else:
            # No gap. The supporting fact is the fully-covered businesses, not an
            # empty list of missing skills — a score with no evidence cannot be
            # explained, which defeats the point of scoring it.
            gap_evidence = [kn.entity_evidence(m["entity"], "fully covered")
                            for m in matches[:8]]
            gap_reason = (f"already covers every skill required by "
                          f"{len(matches)} matched business(es)")
        outcomes.append(applied("LR1-GAP", closeness, gap_reason, weight=2.0,
                                evidence=gap_evidence))

    # LR2 — sequence by how many matched businesses each gap unlocks.
    ordered = []
    for sid, n in sorted(gap_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        ent = kn.entities.get(sid)
        if not ent:
            continue
        attrs = _skill_attrs(kn, sid)
        ordered.append({
            "step": len(ordered) + 1,
            "entity_id": sid,
            "skill": ent["canonical_name"],
            "unlocks_businesses": n,
            "nsqf_level": _int(attrs.get("nsqf_level")) or None,
            "learning_duration": attrs.get("learning_duration") or None,
            "difficulty": attrs.get("difficulty_level") or None,
        })
    if ordered:
        outcomes.append(applied(
            "LR2-SEQUENCE", min(100, len(ordered) * 12),
            f"roadmap ordered by unlock count; first step is "
            f"{ordered[0]['skill']} ({ordered[0]['unlocks_businesses']} businesses)"))
    elif matches:
        # There IS a match and there is NO gap. LR2 and LR3 measure the quality of
        # a roadmap we can offer, and there is no roadmap to offer because none is
        # needed. Scoring that 0 would drag a fully-covered user down to ~67 for
        # having nothing left to learn, which inverts the meaning of the score.
        # UNAVAILABLE removes it from the denominator instead.
        outcomes.append(unavailable(
            "LR2-SEQUENCE",
            "no skill gap to sequence — the user already covers every skill their "
            "matched businesses require"))
    else:
        outcomes.append(no_signal("LR2-SEQUENCE", "no matched business, so no gap"))

    # LR3 — can any gap actually be trained? TRAINED_BY has 3 edges in total.
    trainable, train_ev = 0, []
    for step in ordered:
        providers = kn.neighbours(step["entity_id"], "TRAINED_BY", "out")
        if providers:
            trainable += 1
            step["providers"] = [p["canonical_name"] for p, _ in providers]
            train_ev.extend(kn.edge_evidence(e) for _, e in providers[:2])
    if trainable:
        outcomes.append(applied(
            "LR3-PROVIDER", 100 * trainable / max(len(ordered), 1),
            f"{trainable} of {len(ordered)} roadmap steps have a linked training "
            f"provider", evidence=train_ev[:6]))
    elif ordered:
        outcomes.append(no_signal(
            "LR3-PROVIDER",
            "no roadmap step has a linked training provider — TRAINED_BY holds 3 "
            "edges across the whole graph, so this is a known coverage gap"))
    else:
        outcomes.append(unavailable(
            "LR3-PROVIDER", "no roadmap steps, so no provider to find"))

    result = combine("learning_roadmap", "Learning Roadmap", outcomes)
    result.detail = {
        "steps": ordered[:15],
        "distinct_gaps": len(gap_counts),
        "steps_with_provider": trainable,
        # Stated explicitly so a UI does not have to infer "nothing to learn"
        # from an empty list, which looks identical to "we could not work it out".
        "gap_state": ("NO_GAP" if matches and not ordered
                      else "HAS_GAP" if ordered else "NO_MATCHED_BUSINESS"),
    }
    return result


# ═════════════════════════════════════ 4. District Opportunity Score
def district_opportunity(ctx, kn):
    outcomes = []
    district, row = kn.resolve("district", ctx.location_term)

    if not ctx.location_term:
        result = combine("district_opportunity", "District Opportunity Score",
                         [unavailable("DO1-RESOLVE",
                                      "no city or district on the profile")])
        result.detail = {}
        return result

    if not district:
        result = combine("district_opportunity", "District Opportunity Score",
                         [no_signal("DO1-RESOLVE",
                                    kn.explain_unresolved("district",
                                                          ctx.location_term))])
        result.detail = {"term": ctx.location_term}
        return result

    did = district["global_entity_id"]
    outcomes.append(applied(
        "DO1-RESOLVE", 100,
        f"'{ctx.location_term}' resolves to {district['canonical_name']} "
        f"({row['match_method']})",
        evidence=[kn.entity_evidence(district)]))

    inbound = kn.neighbours(did, None, "in")
    by_type = Counter(node["entity_type"] for node, _ in inbound)
    if inbound:
        outcomes.append(applied(
            "DO2-DENSITY", min(100, len(inbound) * 6),
            f"{len(inbound)} researched entities link to this district",
            weight=2.0,
            evidence=[kn.edge_evidence(e, node["canonical_name"])
                      for node, e in inbound[:10]]))
    else:
        outcomes.append(no_signal(
            "DO2-DENSITY",
            f"no researched entity links to {district['canonical_name']} yet — "
            f"GENERATES_EMPLOYMENT holds 32 edges across 61 districts, so most "
            f"districts are thin"))

    if by_type:
        outcomes.append(applied(
            "DO3-DIVERSITY", min(100, len(by_type) * 20),
            f"spanning {len(by_type)} entity type(s): "
            + ", ".join(f"{k} {v}" for k, v in by_type.most_common(4))))
    else:
        outcomes.append(no_signal("DO3-DIVERSITY", "nothing to diversify over"))

    result = combine("district_opportunity", "District Opportunity Score", outcomes,
                     low_means="Little researched data for this district yet.")
    result.detail = {
        "district_entity_id": did,
        "district_name": district["canonical_name"],
        "match_method": row["match_method"],
        "linked_entities": len(inbound),
        "by_entity_type": dict(by_type.most_common()),
    }
    return result


# ═══════════════════════════════════════════ 5. Collaboration Score
def collaboration_score(ctx, kn):
    outcomes = []

    # CO1 — is the profile even usable for matching?
    fields = [bool(ctx.name), bool(ctx.city), bool(ctx.skills), bool(ctx.interests),
              bool(ctx.bio), bool(ctx.looking_for)]
    filled = sum(fields)
    outcomes.append(applied(
        "CO1-PROFILE", 100 * filled / len(fields),
        f"{filled} of {len(fields)} collaboration-relevant profile fields present",
        evidence=[Evidence("profile_field", "profile_completeness",
                           "profile completeness", f"{filled}/{len(fields)}")]))

    # CO2 — demonstrated collaboration. `teams` does not exist; accepted
    # connections are the real working group.
    missing = ctx.missing("teams")
    n = len(ctx.accepted_connection_ids)
    if n:
        outcomes.append(applied(
            "CO2-ACCEPTED", min(100, n * 25),
            f"{n} accepted connection(s)"
            + (" (using connections; no teams table exists)" if missing else ""),
            evidence=[Evidence("supabase", f"connection:{cid}", "accepted connection")
                      for cid in ctx.accepted_connection_ids[:6]], weight=2.0))
    else:
        outcomes.append(no_signal(
            "CO2-ACCEPTED",
            "no accepted connections yet"
            + (" — and no teams table exists, so there is no other working-group "
               "signal to fall back on" if missing else "")))

    # CO3 — complementarity with people already connected.
    mine, _ = kn.resolve_many("skill", ctx.skills)
    theirs, _ = kn.resolve_many("skill", ctx.collaborator_skills)
    mine_ids = {e["global_entity_id"] for _, e, _ in mine}
    theirs_ids = {e["global_entity_id"] for _, e, _ in theirs}
    if not ctx.collaborator_skills:
        outcomes.append(unavailable(
            "CO3-COMPLEMENTARITY",
            "no connected peers, so complementarity cannot be measured"))
    elif not (mine_ids or theirs_ids):
        outcomes.append(no_signal(
            "CO3-COMPLEMENTARITY",
            "neither the user's nor their peers' skills resolve to the graph"))
    else:
        complementary = theirs_ids - mine_ids
        union = mine_ids | theirs_ids
        outcomes.append(applied(
            "CO3-COMPLEMENTARITY", 100 * len(complementary) / max(len(union), 1),
            f"peers bring {len(complementary)} skill(s) the user does not have",
            evidence=[kn.entity_evidence(kn.entities[s], "peer skill")
                      for s in sorted(complementary)[:8] if s in kn.entities]))

    result = combine("collaboration_score", "Collaboration Score", outcomes)
    result.detail = {
        "profile_fields_filled": filled,
        "accepted_connections": n,
        "pending_connections": len(ctx.pending_connection_ids),
        "complementary_skills": sorted(theirs_ids - mine_ids),
        "teams_table_available": missing is None,
    }
    return result


# ═════════════════════════════════════════════════ 6. AI Readiness
def ai_readiness(ctx, kn):
    outcomes = []
    resolved, _ = kn.resolve_many("skill", ctx.skills)

    # AI1 — Package006 records ai_augmentation_level per skill. Use it, don't guess.
    LEVELS = {"very high": 100, "high": 80, "medium": 55, "moderate": 55,
              "low": 30, "very low": 15}
    scores, ev = [], []
    for t, e, _ in resolved:
        raw = (_skill_attrs(kn, e["global_entity_id"]).get("ai_augmentation_level")
               or "").strip().lower()
        if raw in LEVELS:
            scores.append(LEVELS[raw])
            ev.append(kn.entity_evidence(e, f"ai_augmentation_level = {raw}"))
    if scores:
        outcomes.append(applied(
            "AI1-SKILL_AUGMENTATION", sum(scores) / len(scores),
            f"{len(scores)} resolved skill(s) carry a Package006 AI-augmentation "
            f"level", evidence=ev[:8], weight=2.0))
    elif resolved:
        outcomes.append(no_signal(
            "AI1-SKILL_AUGMENTATION",
            "no resolved skill records an ai_augmentation_level"))
    else:
        outcomes.append(unavailable("AI1-SKILL_AUGMENTATION",
                                    "no resolved skills to assess"))

    # AI2 — ai_readiness on matched businesses, again from the data.
    matches = _matched_businesses(ctx, kn)
    biz_scores, biz_ev = [], []
    import csv as _csv
    from user_intelligence.config import ROOT as _ROOT
    path = _ROOT / "packages" / "Package008_MSME" / "datasets" / "msme_businesses.csv"
    readiness = {}
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            for row in _csv.DictReader(f):
                readiness[kn.normalise(row["business_name"])] = \
                    (row.get("ai_readiness") or "").strip().lower()
    for m in matches:
        raw = readiness.get(kn.normalise(m["entity"]["canonical_name"]), "")
        if raw in LEVELS:
            biz_scores.append(LEVELS[raw])
            biz_ev.append(kn.entity_evidence(m["entity"], f"ai_readiness = {raw}"))
    if biz_scores:
        outcomes.append(applied(
            "AI2-BUSINESS_READINESS", sum(biz_scores) / len(biz_scores),
            f"{len(biz_scores)} matched business(es) carry an AI-readiness rating",
            evidence=biz_ev[:6]))
    else:
        outcomes.append(no_signal(
            "AI2-BUSINESS_READINESS",
            "no matched business carries an AI-readiness rating"))

    # AI3 — reachable AI tooling via USES_AI (16 edges).
    tooling, tool_ev = set(), []
    for m in matches:
        for tool, edge in kn.neighbours(m["entity_id"], "USES_AI", "out"):
            tooling.add(tool["global_entity_id"])
            tool_ev.append(kn.edge_evidence(edge, tool["canonical_name"]))
    if tooling:
        outcomes.append(applied(
            "AI3-TOOLING", min(100, len(tooling) * 20),
            f"{len(tooling)} AI tool(s) linked to matched businesses",
            evidence=tool_ev[:6]))
    else:
        outcomes.append(no_signal(
            "AI3-TOOLING",
            "no AI tooling linked to matched businesses — USES_AI holds 16 edges "
            "across the whole graph"))

    result = combine("ai_readiness", "AI Readiness", outcomes)
    result.detail = {"skills_with_ai_rating": len(scores),
                     "businesses_with_ai_rating": len(biz_scores),
                     "reachable_ai_tools": sorted(tooling)}
    return result


# ══════════════════════════════════════════ 7. Funding Readiness
def funding_readiness(ctx, kn):
    outcomes = []
    matches = _matched_businesses(ctx, kn)
    district, _ = kn.resolve("district", ctx.location_term)

    # FR1 — schemes reachable through matched businesses.
    schemes, scheme_ev = {}, []
    for m in matches:
        for scheme, edge in kn.neighbours(m["entity_id"], "SUPPORTED_BY_SCHEME",
                                          "out"):
            schemes[scheme["global_entity_id"]] = scheme
            scheme_ev.append(kn.edge_evidence(
                edge, f"{m['entity']['canonical_name']} -> "
                      f"{scheme['canonical_name']}"))
    if schemes:
        outcomes.append(applied(
            "FR1-SCHEME_REACH", min(100, len(schemes) * 12),
            f"{len(schemes)} government scheme(s) reachable through matched "
            f"businesses", evidence=scheme_ev[:8], weight=2.0))
    else:
        outcomes.append(no_signal(
            "FR1-SCHEME_REACH",
            "no scheme reachable — this needs at least one matched business"))

    # FR2 — banks and institutions.
    banks, bank_ev = {}, []
    for m in matches:
        for bank, edge in kn.neighbours(m["entity_id"], "SUPPORTED_BY_BANK", "out"):
            banks[bank["global_entity_id"]] = bank
            bank_ev.append(kn.edge_evidence(edge, bank["canonical_name"]))
    if banks:
        outcomes.append(applied(
            "FR2-BANK_REACH", min(100, len(banks) * 25),
            f"{len(banks)} financial institution(s) linked to matched businesses",
            evidence=bank_ev[:6]))
    else:
        outcomes.append(no_signal("FR2-BANK_REACH",
                                  "no financial institution linked"))

    # FR3 — a scheme application needs a real profile behind it.
    needed = {"name": ctx.name, "city": ctx.city, "skills": ctx.skills,
              "district": ctx.district or ctx.city, "budget": ctx.budget}
    have = [k for k, v in sorted(needed.items()) if v]
    outcomes.append(applied(
        "FR3-PROFILE_COMPLETENESS", 100 * len(have) / len(needed),
        f"{len(have)} of {len(needed)} application-relevant fields present: "
        f"{', '.join(have)}",
        evidence=[Evidence("profile_field", "application_readiness",
                           "application fields", f"{len(have)}/{len(needed)}")]))

    result = combine("funding_readiness", "Funding Readiness", outcomes)
    result.detail = {
        "reachable_schemes": [{"entity_id": k, "name": v["canonical_name"]}
                              for k, v in sorted(schemes.items())][:15],
        "reachable_institutions": [v["canonical_name"]
                                   for _, v in sorted(banks.items())],
        "district": district["canonical_name"] if district else None,
    }
    return result


# ═══════════════════════════════════════════ 8. Startup Readiness
def startup_readiness(scores):
    """
    Weighted composite of the other seven.

    UNAVAILABLE components are dropped from the denominator rather than scored
    zero, and the reason names them. A composite that silently treats "we have no
    data" as "the user scores zero" is the single easiest way to produce a number
    that misleads.
    """
    parts, missing, ev = [], [], []
    for key, weight in sorted(STARTUP_WEIGHTS.items()):
        s = scores.get(key)
        if s is None or s.score is None:
            missing.append(key)
            continue
        parts.append((s, weight))
        ev.append(Evidence("entity", f"score:{key}", s.label,
                           f"{s.score:.1f} × {weight}", confidence=s.confidence))

    if not parts:
        return combine("startup_readiness", "Startup Readiness",
                       [unavailable("ST1-COMPOSITE",
                                    f"every component was unavailable: "
                                    f"{', '.join(missing)}")])

    total_weight = sum(w for _, w in parts)
    value = sum(s.score * w for s, w in parts) / total_weight
    reason = (f"weighted composite of {len(parts)} component score(s) "
              f"({total_weight:.2f} of 1.00 weight available)")
    if missing:
        reason += f"; excluded as unavailable: {', '.join(missing)}"

    outcome = applied("ST1-COMPOSITE", value, reason, evidence=ev)
    result = combine("startup_readiness", "Startup Readiness", [outcome])
    result.detail = {
        "components": {s.key: round(s.score, 1) for s, _ in parts},
        "weights_applied": {s.key: w for s, w in parts},
        "weight_available": round(total_weight, 3),
        "excluded_unavailable": missing,
    }
    return result


#: key -> callable(ctx, kn). startup_readiness is applied last, over the others.
SCORERS = {
    "skill_profile": skill_profile,
    "business_readiness": business_readiness,
    "learning_roadmap": learning_roadmap,
    "district_opportunity": district_opportunity,
    "collaboration_score": collaboration_score,
    "ai_readiness": ai_readiness,
    "funding_readiness": funding_readiness,
}
