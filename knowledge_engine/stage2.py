#!/usr/bin/env python3
"""
Minimal deterministic/local intelligence layer (Stage 2)

Provides a small, deterministic analyzer that performs:
- simple intent detection
- entity/concept resolution via the existing Resolver
- location detection (District) when present
- lightweight knowledge grouping using SearchIndex
- gap detection (missing types for an intent)

This module is intentionally small and deterministic so it can run
without external AI APIs.
"""
from typing import List, Dict

from knowledge_graph.resolution.resolver import Resolver
from search.index import SearchIndex


class DeterministicIntel:
    def __init__(self):
        self.resolver = Resolver()
        self.index = SearchIndex()

    def detect_intent(self, q: str) -> str:
        lq = q.lower()
        if any(w in lq for w in ("course", "training", "learn", "certificate")):
            return "learn"
        if any(w in lq for w in ("job", "jobs", "vacancy", "hire", "recruit")):
            return "job"
        if any(w in lq for w in ("repair", "service", "fix")):
            return "service"
        if any(w in lq for w in ("how", "what", "where", "why")):
            return "question"
        return "unknown"

    def extract_entities(self, q: str) -> List[Dict]:
        parts = [p.strip() for p in q.replace(',', ' ').split() if p.strip()]
        out = []
        # Try resolving each contiguous token span (n-gram up to 4)
        for i in range(len(parts)):
            for j in range(i + 1, min(len(parts), i + 4) + 1):
                span = " ".join(parts[i:j])
                for etype in (None, "Skill", "Occupation", "District"):
                    hit = self.resolver.resolve(span, entity_type=etype)
                    if hit:
                        out.append({"surface": span, "entity": hit})
                        break
                # avoid duplicate matches for overlapping spans
        # Deduplicate by global_entity_id
        seen = set()
        dedup = []
        for e in out:
            gid = e["entity"]["global_entity_id"]
            if gid in seen:
                continue
            seen.add(gid)
            dedup.append(e)
        return dedup

    def detect_location(self, entities: List[Dict]) -> Dict:
        for e in entities:
            if e["entity"].get("entity_type") == "District":
                return e["entity"]
        return {}

    def group_knowledge(self, q: str) -> Dict[str, int]:
        # Very small grouping: count top matching document scopes/types
        tokens = [t for t in q.lower().split() if t]
        counts = {}
        for t in tokens:
            idxs = self.index.by_token.get(t, set())
            for i in idxs:
                doc = self.index.documents[i]
                counts[doc.entity_type or doc.scope] = counts.get(doc.entity_type or doc.scope, 0) + 1
        return counts

    def detect_gaps(self, intent: str, groups: Dict[str, int]) -> List[str]:
        gaps = []
        if intent == "learn" and not groups.get("Skill") and not groups.get("skill"):
            gaps.append("Skill content")
        if intent == "job" and not groups.get("Occupation") and not groups.get("occupation"):
            gaps.append("Occupation listings")
        return gaps

    def analyze(self, q: str) -> Dict:
        intent = self.detect_intent(q)
        entities = self.extract_entities(q)
        location = self.detect_location(entities)
        groups = self.group_knowledge(q)
        gaps = self.detect_gaps(intent, groups)
        return {
            "query": q,
            "intent": intent,
            "entities": entities,
            "location": location,
            "groups": groups,
            "gaps": gaps,
        }


__all__ = ["DeterministicIntel"]
