#!/usr/bin/env python3
"""
ValueWeave Stewardship — command line interface (Work Package 5)

The workflow a data steward actually performs, in six commands:

    python3 -m stewardship.cli status
    python3 -m stewardship.cli queue --limit 40
    python3 -m stewardship.cli show vw:crop:turmeric
    python3 -m stewardship.cli review vw:crop:turmeric --actor "r.banoth" \\
        --evidence "checked against https://pmkisan.gov.in/ 2026-07-26"
    python3 -m stewardship.cli approve vw:crop:turmeric --actor "r.banoth"
    python3 -m stewardship.cli apply --write

`review` and `approve` only ever append to the ledger. `apply` is the single
command that changes a package row, it requires `--write` to do so, and it prints
what it would do first. That separation is deliberate: recording a judgement and
releasing it are different acts and should fail independently.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stewardship.ledger import ReviewLedger                                # noqa: E402
from stewardship.lifecycle import (LifecycleState, TransitionError,        # noqa: E402
                                   allowed_from)
from stewardship.store import StewardshipStore                             # noqa: E402


def _store():
    return StewardshipStore()


def cmd_status(args):
    s = _store().summary()
    if args.json:
        print(json.dumps(s, indent=2))
        return 0
    print("ValueWeave stewardship status\n")
    print(f"  entities ................. {s['entities']}")
    print(f"  verified ................. {s['verified']} ({s['verified_pct']}%)")
    print(f"  awaiting review .......... {s['awaiting_review']}")
    print(f"  state/verification gaps .. {s['entities_with_state_verification_gap']}")
    print("\n  by lifecycle state:")
    for k, v in s["by_lifecycle_state"].items():
        print(f"    {k:<12} {v}")
    print("\n  unverified by package:")
    for k, v in list(s["unverified_by_package"].items())[:10]:
        print(f"    {k:<34} {v}")
    led = s["ledger"]
    print(f"\n  ledger: {led['entries']} entries across {led['entities_touched']} entities")
    if led["by_actor"]:
        print("    " + ", ".join(f"{k} {v}" for k, v in led["by_actor"].items()))
    return 0


def cmd_queue(args):
    rows = _store().queue(limit=args.limit, entity_type=args.entity_type,
                          source_package=args.package)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("queue is empty — nothing awaiting review under these filters")
        return 0
    print(f"Review queue — {len(rows)} entities, highest leverage first\n")
    print(f"  {'#':>3}  {'deg':>3}  {'cum%':>6}  {'conf':>4}  {'type':<20} name")
    for r in rows:
        print(f"  {r['queue_position']:>3}  {r['degree']:>3}  "
              f"{r['cumulative_coverage_pct']:>6}  {r['confidence_score']:>4}  "
              f"{r['entity_type']:<20} {r['canonical_name'][:46]}")
    last = rows[-1]
    print(f"\n  reviewing these {len(rows)} covers {last['cumulative_coverage_pct']}% "
          f"of all edge endpoints in the graph")
    return 0


def cmd_show(args):
    rec = _store().record(args.entity_id)
    if rec is None:
        print(f"no such entity: {args.entity_id}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(rec, indent=2))
        return 0
    print(f"{rec['canonical_name']}  ({rec['entity_id']})\n")
    for k in ("entity_type", "source_package", "package_local_id", "confidence_score",
              "lifecycle_state", "verification_status", "degree"):
        print(f"  {k:<22} {rec[k]}")
    if rec["gap"]:
        print(f"\n  GAP: {rec['gap']}")
    print(f"\n  permitted next: "
          f"{[t.target.value for t in allowed_from(rec['lifecycle_state'])] or 'none'}")
    if rec["history"]:
        print(f"\n  history ({len(rec['history'])} entries):")
        for h in rec["history"]:
            print(f"    {h['recorded_at']}  {h['from_state']} -> {h['to_state']}  "
                  f"by {h['actor'] or '(unattributed)'}")
            if h["evidence"]:
                print(f"      {h['evidence']}")
    else:
        print("\n  history: none — no steward decision recorded for this entity")
    return 0


def _transition(args, target):
    store = _store()
    rec = store.record(args.entity_id)
    if rec is None:
        print(f"no such entity: {args.entity_id}", file=sys.stderr)
        return 1
    try:
        entry = store.ledger.record(
            entity_id=args.entity_id,
            from_state=rec["lifecycle_state"],
            to_state=target,
            actor=args.actor, actor_role=args.role,
            evidence=args.evidence, notes=args.notes,
            verification_status=rec["verification_status"])
    except TransitionError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    store.ledger.flush()
    print(f"recorded {entry.entry_id}: {rec['canonical_name']} "
          f"{entry.from_state} -> {entry.to_state} by {entry.actor}")
    if entry.verification_status_after:
        print(f"  verification_status will become {entry.verification_status_after} "
              f"when `apply --write` runs")
    return 0


def cmd_review(args):
    return _transition(args, LifecycleState.REVIEWED.value)


def cmd_approve(args):
    return _transition(args, LifecycleState.APPROVED.value)


def cmd_archive(args):
    return _transition(args, LifecycleState.ARCHIVED.value)


def cmd_apply(args):
    report = _store().apply_approvals(dry_run=not args.write)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    mode = "WRITING" if args.write else "dry run (pass --write to apply)"
    print(f"apply approvals — {mode}\n")
    print(f"  approved entities .... {report['approved_entities']}")
    print(f"  datasets touched ..... {report['datasets_touched']}")
    print(f"  rows updated ......... {report['rows_updated']}")
    for w in report["written"]:
        print(f"    {w['dataset']}: {w['rows_updated']}")
    if report["unlocatable"]:
        print(f"\n  {len(report['unlocatable'])} approved entities could not be located "
              f"in a package row:")
        for u in report["unlocatable"][:10]:
            print(f"    {u['entity_id']}: {u['reason']}")
    return 0


def build_parser():
    ap = argparse.ArgumentParser(prog="stewardship",
                                 description="ValueWeave data stewardship workflow")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="verification and lifecycle summary").set_defaults(fn=cmd_status)

    q = sub.add_parser("queue", help="what to review first, ordered by graph leverage")
    q.add_argument("--limit", type=int, default=40)
    q.add_argument("--type", dest="entity_type")
    q.add_argument("--package")
    q.set_defaults(fn=cmd_queue)

    sh = sub.add_parser("show", help="one entity: state, gap, history")
    sh.add_argument("entity_id")
    sh.set_defaults(fn=cmd_show)

    for name, fn, helptext in [
            ("review", cmd_review, "record that a human read this record against its sources"),
            ("approve", cmd_approve, "steward sign-off; marks the record VST-VERIFIED"),
            ("archive", cmd_archive, "retire a published record")]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("entity_id")
        p.add_argument("--actor", required=True, help="the person accountable for this decision")
        p.add_argument("--role", default="", help="e.g. Package Steward")
        p.add_argument("--evidence", default="", help="what was checked, and against what")
        p.add_argument("--notes", default="")
        p.set_defaults(fn=fn)

    a = sub.add_parser("apply", help="propagate approvals into package verification_status")
    a.add_argument("--write", action="store_true", help="actually write; omit for a dry run")
    a.set_defaults(fn=cmd_apply)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
