#!/usr/bin/env python3
"""
The engine. Runs the eight scorers and ten recommenders for one user and emits the
five output tables.

REPRODUCIBILITY IS THE CONTRACT
-------------------------------
`result_hash` covers the inputs and every score and recommendation, and excludes
`generated_at`. Two runs over the same profile and the same knowledge snapshot
produce the same hash — `test_engine_is_reproducible` asserts it, twice, in the
same process and across a fresh snapshot load.

That matters for more than tidiness. A recommendation a user acts on must be
explainable months later, and an explanation you cannot reproduce is a story.

WHAT THE ENGINE DOES NOT DO
---------------------------
It does not query Supabase. Callers pass rows in — a profile, its connections, its
peers, candidate collaborators, research articles. This keeps the engine free of a
client dependency, testable without credentials, and unable to leak a profile the
caller's own visibility rules would have hidden.
"""

import hashlib
import json
from datetime import datetime, timezone

from user_intelligence import RULES_VERSION, __version__
from user_intelligence.config import (INPUTS, MISSING, OUTPUT_TABLES,
                                      RECOMMENDATION_CATEGORIES, SCORES,
                                      SCORES_BY_KEY, UNVERIFIED_NOTICE)
from user_intelligence.knowledge import KnowledgeSnapshot
from user_intelligence.profiles import SCORERS, startup_readiness
from user_intelligence.recommenders import NO_DATA_SOURCE, RECOMMENDERS
from user_intelligence.rules import UNAVAILABLE


def _utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class IntelligenceResult:
    def __init__(self, ctx, snapshot, scores, categories, generated_at):
        self.ctx = ctx
        self.snapshot = snapshot
        self.scores = scores
        self.categories = categories
        self.generated_at = generated_at

    # ------------------------------------------------------------ the 5 tables
    def user_skill_profile(self):
        s = self.scores["skill_profile"]
        detail = getattr(s, "detail", {}) or {}
        return {
            "user_id": self.ctx.user_id,
            "score": s.score,
            "status": s.status,
            "confidence": s.confidence,
            "reason": s.reason,
            "claimed_skill_count": len(self.ctx.skills),
            "resolved_skill_count": len(detail.get("resolved", [])),
            "resolve_rate_pct": detail.get("resolve_rate_pct"),
            "resolved_skills": detail.get("resolved", []),
            # The honest half: skills the user claims that we have no data for.
            "unresolved_skills": detail.get("unresolved", []),
            "categories": detail.get("categories", []),
            "evidence": [e.to_dict() for e in s.evidence[:40]],
            "rules_version": RULES_VERSION,
            "generated_at": self.generated_at,
        }

    def user_business_profile(self):
        keys = ("business_readiness", "district_opportunity", "ai_readiness",
                "funding_readiness", "startup_readiness")
        out = {
            "user_id": self.ctx.user_id,
            "rules_version": RULES_VERSION,
            "generated_at": self.generated_at,
        }
        for k in keys:
            s = self.scores.get(k)
            out[k] = {
                "score": s.score if s else None,
                "status": s.status if s else UNAVAILABLE,
                "confidence": s.confidence if s else 0,
                "reason": s.reason if s else "score not computed",
                "detail": getattr(s, "detail", {}) if s else {},
            }
        return out

    def user_learning_profile(self):
        s = self.scores["learning_roadmap"]
        detail = getattr(s, "detail", {}) or {}
        courses = self.categories.get("courses")
        return {
            "user_id": self.ctx.user_id,
            "score": s.score,
            "status": s.status,
            "confidence": s.confidence,
            "reason": s.reason,
            "distinct_gaps": detail.get("distinct_gaps", 0),
            "steps_with_provider": detail.get("steps_with_provider", 0),
            "roadmap": detail.get("steps", []),
            "recommended_courses": [r.to_dict() for r in
                                    (courses.recommendations if courses else [])],
            "rules_version": RULES_VERSION,
            "generated_at": self.generated_at,
        }

    def user_recommendations(self):
        """One row per recommendation. Each carries reason, evidence, confidence,
        timestamp — the four things the brief requires."""
        rows = []
        for key, cat in sorted(self.categories.items()):
            for rank, rec in enumerate(cat.recommendations, start=1):
                d = rec.to_dict()
                d.update({
                    "user_id": self.ctx.user_id,
                    "rank": rank,
                    "category_status": cat.status,
                    "rules_version": RULES_VERSION,
                    "generated_at": self.generated_at,
                    "unverified_notice": UNVERIFIED_NOTICE,
                })
                rows.append(d)
        return rows

    def user_activity_summary(self):
        by_cat = {k: {"status": c.status, "count": len(c.recommendations),
                      "note": c.note}
                  for k, c in sorted(self.categories.items())}
        unavailable_scores = sorted(k for k, s in self.scores.items()
                                    if s.score is None)
        no_data_categories = sorted(k for k, c in self.categories.items()
                                    if c.status == NO_DATA_SOURCE)
        return {
            "user_id": self.ctx.user_id,
            "scores": {k: {"score": s.score, "status": s.status,
                           "confidence": s.confidence}
                       for k, s in sorted(self.scores.items())},
            "recommendations_by_category": by_cat,
            "total_recommendations": sum(len(c.recommendations)
                                         for c in self.categories.values()),
            "scores_unavailable": unavailable_scores,
            "categories_without_data": no_data_categories,
            "inputs_unavailable": sorted(self.ctx.unavailable_inputs),
            "accepted_connections": len(self.ctx.accepted_connection_ids),
            "pending_connections": len(self.ctx.pending_connection_ids),
            "profile_complete": self.ctx.profile_complete,
            "knowledge_snapshot_hash": self.snapshot.snapshot_hash,
            "engine_version": __version__,
            "rules_version": RULES_VERSION,
            "result_hash": self.result_hash(),
            "generated_at": self.generated_at,
        }

    def tables(self):
        return {
            "user_skill_profile": self.user_skill_profile(),
            "user_business_profile": self.user_business_profile(),
            "user_learning_profile": self.user_learning_profile(),
            "user_recommendations": self.user_recommendations(),
            "user_activity_summary": self.user_activity_summary(),
        }

    # ------------------------------------------------------------ reproducible
    def result_hash(self):
        """
        Hash of inputs + every score + every recommendation.

        `generated_at` is excluded on purpose: it is the one field that must differ
        between two otherwise identical runs, and including it would make the hash
        useless for proving determinism.
        """
        material = {
            "engine": __version__,
            "rules": RULES_VERSION,
            "snapshot": self.snapshot.snapshot_hash,
            "context": self.ctx.to_dict(),
            "scores": {k: s.fingerprint() for k, s in sorted(self.scores.items())},
            "recommendations": [
                [k, r.item_id, round(r.match_score, 2), r.confidence, r.rule]
                for k, c in sorted(self.categories.items())
                for r in c.recommendations],
        }
        return hashlib.sha256(
            json.dumps(material, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

    def explain(self, score_key=None):
        """Human-readable trace. What a support engineer reads."""
        lines = [f"user {self.ctx.user_id}  ·  engine {__version__}  ·  rules "
                 f"{RULES_VERSION}  ·  result {self.result_hash()}"]
        for key, s in sorted(self.scores.items()):
            if score_key and key != score_key:
                continue
            value = f"{s.score:5.1f}" if s.score is not None else "  n/a"
            lines.append(f"\n{value}  {s.label}  [{s.status}]")
            lines.append(f"        {s.reason}")
            for o in s.outcomes:
                v = f"{o.value:5.1f}" if o.value is not None else "  n/a"
                lines.append(f"        {v}  {o.rule:<26} {o.status:<12} "
                             f"{o.reason[:72]}")
        return "\n".join(lines)


class IntelligenceEngine:
    def __init__(self, snapshot=None):
        self.snapshot = snapshot or KnowledgeSnapshot()

    def run(self, ctx, articles=(), candidates=(), categories=None):
        """
        Compute everything for one user.

        `articles` and `candidates` are caller-supplied Supabase rows; both are
        optional and their absence produces an honestly empty category rather than
        a missing one.
        """
        generated_at = _utcnow()
        kn = self.snapshot

        scores = {}
        for spec in SCORES:
            if spec.key == "startup_readiness":
                continue
            scores[spec.key] = SCORERS[spec.key](ctx, kn)
        scores["startup_readiness"] = startup_readiness(scores)

        wanted = set(categories) if categories else {c.key for c
                                                    in RECOMMENDATION_CATEGORIES}
        results = {}
        for spec in RECOMMENDATION_CATEGORIES:
            if spec.key not in wanted:
                continue
            fn = RECOMMENDERS[spec.key]
            if spec.key == "research":
                results[spec.key] = fn(ctx, kn, scores, articles=articles)
            elif spec.key == "collaborators":
                results[spec.key] = fn(ctx, kn, scores, candidates=candidates)
            else:
                results[spec.key] = fn(ctx, kn, scores)

        return IntelligenceResult(ctx, kn, scores, results, generated_at)

    # ---------------------------------------------------------------- metadata
    def capabilities(self):
        """
        What this engine can and cannot do right now, computed from config.

        Exists so a UI can render an honest capability list instead of a hard-coded
        one that rots. `unavailable_inputs` and `categories_without_data` are the
        two lists a product owner should read first.
        """
        return {
            "engine_version": __version__,
            "rules_version": RULES_VERSION,
            "knowledge": self.snapshot.stats(),
            "scores": [{"key": s.key, "label": s.label, "requires": list(s.requires),
                        "rules": list(s.rules),
                        "blocked_by": [r for r in s.requires
                                       if INPUTS.get(r) and
                                       INPUTS[r].status == MISSING]}
                       for s in SCORES],
            "categories": [{"key": c.key, "label": c.label,
                            "has_data": not c.no_data_reason,
                            "no_data_reason": c.no_data_reason,
                            "sparse_note": c.sparse_note}
                           for c in RECOMMENDATION_CATEGORIES],
            "unavailable_inputs": {name: spec.detail for name, spec
                                   in sorted(INPUTS.items())
                                   if spec.status == MISSING},
            "categories_without_data": [c.key for c in RECOMMENDATION_CATEGORIES
                                        if c.no_data_reason],
            "output_tables": list(OUTPUT_TABLES),
        }
