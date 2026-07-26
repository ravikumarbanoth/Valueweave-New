#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Stewardship Store (Work Package 5)

Joins three things that live apart: the graph's entities, the review ledger's
decisions, and the package rows those entities came from.

    StewardshipStore.record(entity_id)   -> current state, verification, history
    StewardshipStore.queue()             -> what to review first, and why
    StewardshipStore.apply_approvals()   -> write VST-VERIFIED into package rows

THE REVIEW QUEUE IS ORDERED BY LEVERAGE, NOT BY ID
--------------------------------------------------
With zero rows verified and 2,299 rows to read, the order of work is the whole
decision. The v2.1 audit measured where the value is: the top 40 entities by
edge-endpoint degree touch 37% of all endpoints in the graph. Verifying those 40
buys more trust than verifying 400 leaves.

So `queue()` ranks by degree — how many relationships an entity anchors — with
confidence as a tiebreak, and reports the coverage each prefix of the queue buys.

WRITES ARE EXPLICIT AND NARROW
------------------------------
`apply_approvals()` is the only function in the platform that changes a package
row's `verification_status`. It writes exactly one column, only for entities with
a recorded APPROVED transition naming an actor, and it refuses to invent a row it
cannot find. Recording a decision and acting on it are kept separate so that a
mistaken approval can be seen in the ledger before it reaches a package.
"""

import csv
from collections import defaultdict
from pathlib import Path

from stewardship.ledger import ReviewLedger
from stewardship.lifecycle import (LifecycleState, NEEDS_REVIEW_STATUS,
                                   VERIFIED_STATUS, effective_state)

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"
PACKAGES = ROOT / "packages"


def _read(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class StewardshipStore:
    def __init__(self, ledger=None, kg_dir=None, packages_dir=None):
        self.kg = Path(kg_dir or KG)
        self.packages = Path(packages_dir or PACKAGES)
        self.ledger = ledger if ledger is not None else ReviewLedger()

        self.entities = {e["global_entity_id"]: e
                         for e in _read(self.kg / "entities" / "entities.csv")}
        self.edges = _read(self.kg / "relationships" / "relationships.csv")

        self.degree = defaultdict(int)
        for r in self.edges:
            self.degree[r["from_entity"]] += 1
            self.degree[r["to_entity"]] += 1

    # ------------------------------------------------------------- reading
    def record(self, entity_id):
        e = self.entities.get(entity_id)
        if not e:
            return None
        declared = e.get("lifecycle_state", LifecycleState.PUBLISHED.value)
        state = self.ledger.current_state(entity_id, default=declared)
        status = self.ledger.verification_status(
            entity_id, default=e.get("verification_status", NEEDS_REVIEW_STATUS))
        _state, gap = effective_state(state, status)
        return {
            "entity_id": entity_id,
            "canonical_name": e["canonical_name"],
            "entity_type": e["entity_type"],
            "source_package": e["source_package"],
            "package_local_id": e.get("package_local_id", ""),
            "confidence_score": e.get("confidence_score", ""),
            "declared_lifecycle_state": declared,
            "lifecycle_state": state.value,
            "verification_status": status,
            "degree": self.degree.get(entity_id, 0),
            "gap": gap,
            "history": [h.to_row() for h in self.ledger.for_entity(entity_id)],
        }

    def queue(self, limit=40, entity_type=None, source_package=None,
              include_verified=False):
        """Highest-leverage unverified entities first, with cumulative coverage."""
        rows = []
        for gid, e in self.entities.items():
            if entity_type and e["entity_type"] != entity_type:
                continue
            if source_package and e["source_package"] != source_package:
                continue
            status = self.ledger.verification_status(
                gid, default=e.get("verification_status", NEEDS_REVIEW_STATUS))
            if not include_verified and status == VERIFIED_STATUS:
                continue
            conf = e.get("confidence_score", "0")
            rows.append({
                "entity_id": gid,
                "canonical_name": e["canonical_name"],
                "entity_type": e["entity_type"],
                "source_package": e["source_package"],
                "degree": self.degree.get(gid, 0),
                "confidence_score": int(conf) if str(conf).isdigit() else 0,
                "lifecycle_state": self.ledger.current_state(
                    gid, default=e.get("lifecycle_state",
                                       LifecycleState.PUBLISHED.value)).value,
                "verification_status": status,
            })

        rows.sort(key=lambda r: (-r["degree"], -r["confidence_score"], r["canonical_name"]))
        total_endpoints = sum(self.degree.values())
        running = 0
        for i, r in enumerate(rows, start=1):
            running += r["degree"]
            r["queue_position"] = i
            r["cumulative_edge_endpoints"] = running
            r["cumulative_coverage_pct"] = (round(100 * running / total_endpoints, 2)
                                            if total_endpoints else 0.0)
        return rows[:limit] if limit else rows

    def summary(self):
        by_state, by_status, by_package = defaultdict(int), defaultdict(int), defaultdict(int)
        gaps = 0
        for gid, e in self.entities.items():
            rec = self.record(gid)
            by_state[rec["lifecycle_state"]] += 1
            by_status[rec["verification_status"]] += 1
            if rec["verification_status"] != VERIFIED_STATUS:
                by_package[e["source_package"]] += 1
            if rec["gap"]:
                gaps += 1
        verified = by_status.get(VERIFIED_STATUS, 0)
        return {
            "entities": len(self.entities),
            "by_lifecycle_state": dict(sorted(by_state.items())),
            "by_verification_status": dict(sorted(by_status.items())),
            "verified": verified,
            "awaiting_review": len(self.entities) - verified,
            "verified_pct": round(100 * verified / len(self.entities), 2) if self.entities else 0.0,
            "entities_with_state_verification_gap": gaps,
            "unverified_by_package": dict(sorted(by_package.items(), key=lambda kv: -kv[1])),
            "ledger": self.ledger.stats(),
        }

    # ------------------------------------------------------------- writing
    def apply_approvals(self, dry_run=True):
        """
        Propagate APPROVED decisions into the owning package rows.

        Writes exactly one column, `verification_status`, and only for entities
        whose ledger shows an APPROVED transition. Returns a report of what was
        written and — just as importantly — what could not be located.
        """
        approved = [gid for gid in self.entities
                    if self.ledger.current_state(gid, default="PUBLISHED").order
                    >= LifecycleState.APPROVED.order
                    and self.ledger.verification_status(gid) == VERIFIED_STATUS]

        # Group the work by the file it touches, so each CSV is rewritten once.
        wanted = defaultdict(set)          # path -> {local_id}
        unlocatable = []
        for gid in approved:
            e = self.entities[gid]
            lid = e.get("package_local_id", "")
            if not lid or lid in ("PENDING_VERIFICATION", "n/a") or ":" in lid:
                unlocatable.append({"entity_id": gid, "reason":
                                    f"package_local_id {lid!r} is not a package row key"})
                continue
            ds = self.packages / e["source_package"] / "datasets"
            hit = False
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                rows = _read(f)
                if rows and any((r.get(list(rows[0])[0]) or "") == lid for r in rows):
                    wanted[f].add(lid)
                    hit = True
                    break
            if not hit:
                unlocatable.append({"entity_id": gid, "reason":
                                    f"no row with id {lid!r} in {e['source_package']}"})

        written = []
        for path, ids in sorted(wanted.items()):
            rows = _read(path)
            key = list(rows[0])[0]
            changed = 0
            for r in rows:
                if r.get(key) in ids and r.get("verification_status") != VERIFIED_STATUS:
                    r["verification_status"] = VERIFIED_STATUS
                    changed += 1
            if changed and not dry_run:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
            written.append({"dataset": str(path.relative_to(ROOT)),
                            "rows_updated": changed})

        return {
            "dry_run": dry_run,
            "approved_entities": len(approved),
            "datasets_touched": len(written),
            "rows_updated": sum(w["rows_updated"] for w in written),
            "written": written,
            "unlocatable": unlocatable,
        }
