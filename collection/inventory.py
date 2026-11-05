#!/usr/bin/env python3
"""
A read-only inventory of the review queue, across every dimension a reviewer
needs before deciding anything.

WHY THIS EXISTS
---------------
`collection.cli queue` lists candidates by priority, which is the right view
when you are working down a feed. It is the wrong view when you sit down to a
backlog of 64: the questions then are "how many of these are really one
decision", "which need a primary source I do not have", and "which will break
search if I approve them without touching the vocabulary".

This joins what is already recorded in four places — the queue, the source
modules, the classification register and the live graph — and writes nothing.

WHAT IT DELIBERATELY DOES NOT DO
---------------------------------
It does not decide. Every row carries a RECOMMENDATION, and a recommendation is
not a state: the queue's state is changed only by `collection.cli
review/approve/reject` with a named actor. See `PROMOTION_IS_NOT_AUTOMATABLE`.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collection import review                                     # noqa: E402

#: The constraint that decides the shape of this whole exercise, quoted from
#: `stewardship/lifecycle.py` rather than paraphrased:
#:
#:     "APPROVED is the only state a machine may not enter. Collection,
#:      validation and publication are automatable. Approval is the moment a
#:      person accepts responsibility for a claim."
#:
#: It is not advice. `Transition(REVIEWED, APPROVED, ..., machine_permitted=
#: False)` makes `check_transition(by_machine=True)` raise, and
#: `collection.cli approve` requires `--actor NAME`. `decide.promote` reads
#: only candidates already APPROVED, so nothing reaches a package row without
#: a named human having signed for it.
#:
#: Everything here therefore stops at "what a reviewer should do and why",
#: which is the most a machine is allowed to contribute.
PROMOTION_IS_NOT_AUTOMATABLE = (
    "stewardship/lifecycle.py: REVIEWED -> APPROVED has machine_permitted="
    "False and require_actor=True; collection.cli approve requires --actor. "
    "A machine may inventory, classify, group and recommend. It may not "
    "approve, and therefore may not promote."
)

#: Types `collection/decide.py` can actually write a package row for. A
#: candidate whose type is missing here cannot be promoted by the existing
#: pipeline even after a human approves it — a real finding about the queue,
#: not a reason to add a target.
PROMOTABLE_TYPES = ("GovernmentScheme", "Skill", "MSME", "Crop")

RECOMMENDATIONS = {
    "PROMOTE": "evidence and workflow support a package row once a human approves",
    "REJECT": "should not become an entity",
    "KEEP_NEEDS_REVIEW": "a real candidate, but nothing here settles it yet",
    "GROUP": "decide together with the rest of its group",
    "RESEARCH_REQUIRED": "needs a primary source before a reviewer can decide",
}


def _entities():
    from tests.js_harness import entities                          # noqa: PLC0415
    return entities()


def _search_top(queries):
    """What the live ranker returns today, one call for the whole batch."""
    from tests.js_harness import JsHarness, entities               # noqa: PLC0415
    harness = JsHarness()
    try:
        harness.dataset("entities.json", entities())
        return harness.run("""
            const { rankEntities } = await import("$LIB/knowledge-search.js");
            const rows = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
            const out = {};
            for (const q of %s) {
              const r = rankEntities(rows, q, { limit: 1 })[0];
              out[q] = r ? { name: r.canonical_name, type: r.entity_type } : null;
            }
            console.log(JSON.stringify(out));
        """ % json.dumps(list(queries)))
    finally:
        harness.cleanup()


def build(with_search=True):
    """One row per queued candidate, joined across every source of truth."""
    from research.sources import candidate_classification as cc     # noqa: PLC0415
    from research.sources import verified_candidates as vc          # noqa: PLC0415
    from research.sources.emit_candidates import DOCUMENTS          # noqa: PLC0415

    by_slug = {}
    for module in DOCUMENTS.values():
        sid = module.SOURCE["source_id"]
        for role in module.new_roles():
            by_slug[f"{sid}:{role['slug']}"] = role

    search = {}
    if with_search:
        search = _search_top(sorted({r["title"] for r in by_slug.values()}))

    known = {e["canonical_name"] for e in _entities()}
    rows = []
    for candidate in review.load():
        cid = candidate.candidate_id
        cls = cc.CANDIDATES.get(cid, {})
        ver = vc.VERIFIED.get(cid, {})
        hit = search.get(candidate.title) or {}
        role = by_slug.get(cid)

        rows.append({
            "candidate_id": cid,
            "title": candidate.title,
            "source": candidate.source_id,
            "state": candidate.state,
            "entity_type": candidate.classified_as,
            "promotable_type": candidate.classified_as in PROMOTABLE_TYPES,
            "confidence": (candidate.raw or {}).get("confidence"),
            "classification": cls.get("cls"),
            "merge_target": cls.get("merge_target"),
            "group": cc.group_of(cid),
            "primary_source": cls.get("primary_source"),
            "verified": bool(ver) and ver.get("exists") is True,
            "verified_code": ver.get("code"),
            "verified_level": ver.get("nsqf_level"),
            "verified_url": ver.get("url"),
            "search_today": hit.get("name"),
            "search_today_type": hit.get("type"),
            "repoint_required": cid in cc.REPOINT_ON_PROMOTION,
            "repoint_concept": cc.REPOINT_ON_PROMOTION.get(cid, (None, None))[0],
            "in_field_technician_magnet":
                cid in cc.FIELD_TECHNICIAN_MAGNET["candidates"],
            "existing_entity": (role or {}).get("existing"),
            "proposed_exists_already": candidate.title in known,
        })
    return rows


def recommend(row):
    """The recommendation for one inventory row, and why.

    Deliberately a pure function of what is already recorded. A judgement that
    is not written down somewhere else belongs in the classification register
    where a person can argue with it, not in a branch here where they cannot
    see it.
    """
    cls = row["classification"]

    if row["source"].startswith("fix-"):
        return "REJECT", ("a pipeline test fixture, not knowledge — these exist "
                          "to exercise the collector and must never be promoted")

    if cls == "E":
        return "REJECT", "classified REJECT by the consolidated review"

    if cls == "D":
        #: A candidate can be both disputed AND grouped — `battery-technician`
        #: and `security-system-installer` are. Disputed wins, because no
        #: amount of group discussion settles a contradiction between sources.
        #: The group is still named: whoever resolves the dispute has to decide
        #: the rest of it in the same sitting.
        note = ("disputed — the sources contradict each other or themselves; "
                "needs a person")
        if row["group"]:
            note += f", and decide with group `{row['group']}`"
        return "RESEARCH_REQUIRED", note

    if cls == "C":
        return "GROUP", f"decide with group `{row['group']}`"

    if not row["promotable_type"]:
        return "KEEP_NEEDS_REVIEW", (
            f"{row['entity_type']} has no target in collection/decide.py, so "
            "the existing pipeline cannot write a row for it even after "
            "approval — the gap is in the promoter, not in the candidate")

    if row["verified"]:
        base = f"verified against {row['verified_code']} — a named human must still approve"
        if row["repoint_required"]:
            base += (f"; promotion must land together with re-pointing the "
                     f"`{row['repoint_concept']}` concept")
        return "PROMOTE", base

    return "RESEARCH_REQUIRED", (
        f"no primary source checked yet; try: {row['primary_source']}")


def summary(rows=None):
    rows = build() if rows is None else rows
    out = {"total": len(rows), "by_state": {}, "by_type": {}, "by_source": {},
           "by_class": {}, "by_recommendation": {}, "repoint_required": 0,
           "in_magnet": 0, "not_promotable_type": 0}
    for row in rows:
        rec, _why = recommend(row)
        for key, value in (("by_state", row["state"]),
                           ("by_type", row["entity_type"]),
                           ("by_source", row["source"]),
                           ("by_class", row["classification"] or "-"),
                           ("by_recommendation", rec)):
            out[key][value] = out[key].get(value, 0) + 1
        out["repoint_required"] += bool(row["repoint_required"])
        out["in_magnet"] += bool(row["in_field_technician_magnet"])
        out["not_promotable_type"] += (not row["promotable_type"])
    return out
