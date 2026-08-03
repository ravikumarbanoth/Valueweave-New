#!/usr/bin/env python3
"""
The weekly intelligence report.

WHY MARKDOWN IN GIT AND NOT AN EMAIL
-------------------------------------
An email is read once and gone. A file in `ops/reports/` is a series, and a
series is the only way anybody sees a TREND — which is the entire point of a
weekly report. `git log ops/reports/` is the history of the platform's health,
and diffing last week against this one takes no tooling at all.

It also means the report is reviewable in the pull request that generates it,
and that generating one needs no mail credential, no scheduler integration and
no service to be up.

WHAT GOES IN IT
---------------
Only what changed or what somebody should do. A report that repeats forty
unchanging numbers every week teaches its readers to skim it, which is the same
failure the review queue is designed against and costs the same thing.

So: the score and its movement, what came in, what is waiting, what is broken,
and what people asked for that we do not have. Where a number cannot be
computed it says so rather than printing a zero.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ops import metrics

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "ops" / "reports"


def _now():
    return datetime.now(timezone.utc)


def previous_snapshot(before=None, report_dir=None):
    """The most recent snapshot older than `before`, for the trend line.

    Returns None when there is no earlier report, and the report then says
    "first report — no comparison" rather than showing every number as a fresh
    gain, which is how a new dashboard flatters itself.
    """
    directory = Path(report_dir or REPORT_DIR)
    if not directory.exists():
        return None
    snapshots = sorted(directory.glob("*.json"))
    if before:
        snapshots = [p for p in snapshots if p.stem < before]
    if not snapshots:
        return None
    try:
        return json.loads(snapshots[-1].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _delta(now_value, was_value, unit=""):
    if now_value is None:
        return "—"
    if was_value is None:
        return f"{now_value}{unit}"
    change = round(now_value - was_value, 1)
    if change == 0:
        return f"{now_value}{unit} (unchanged)"
    return f"{now_value}{unit} ({change:+g})"


def render(snapshot, previous=None, now=None):
    """The report, as markdown."""
    now = now or _now()
    week = now.strftime("%G-W%V")
    out = []
    add = out.append

    overview = snapshot["overview"]
    quality = snapshot["quality"]
    was = (previous or {}).get("quality") or {}
    collection = snapshot["collection"]
    integrity = snapshot["integrity"]
    demand = snapshot["demand"]

    add(f"# ValueWeave — week {week}")
    add("")
    add(f"Generated {snapshot['generated_at']} from committed artifacts. "
        f"Every number here is reproducible with `python3 -m ops.cli snapshot`.")
    add("")

    # ── the headline ────────────────────────────────────────────────────────
    add("## Knowledge quality")
    add("")
    add(f"**{quality['overall']} ({quality['grade']})** across "
        f"{quality['dimensions_scored']} scored dimensions"
        + (f", {quality['dimensions_unknown']} unknown"
           if quality["dimensions_unknown"] else "")
        + (f" — was {was.get('overall')} last week" if was.get("overall") is not None
           else " — first report, no comparison"))
    add("")
    add("| dimension | score | what it means |")
    add("|---|---:|---|")
    previous_by_name = {d["name"]: d["value"] for d in (was.get("dimensions") or [])}
    for dimension in quality["dimensions"]:
        value = _delta(dimension["value"], previous_by_name.get(dimension["name"]))
        add(f"| {dimension['name'].replace('_', ' ')} | {value} | {dimension['detail']} |")
    add("")
    if quality["concerns"]:
        add(f"**Below 60:** {', '.join(quality['concerns'])}.")
        add("")

    # ── what came in ────────────────────────────────────────────────────────
    add("## Collection")
    add("")
    sources = collection.get("sources") or {}
    queue = collection.get("queue") or {}
    add(f"- **{sources.get('active', 0)} active** of {sources.get('total', 0)} "
        f"registered sources · {sources.get('pending_verification', 0)} awaiting "
        f"verification · {sources.get('dead', 0)} dead · {sources.get('stale', 0)} stale")
    add(f"- feed health: **{collection.get('feed_status', 'unknown')}**"
        + (f" — last run {collection['last_run']}" if collection.get("last_run") else ""))
    by_state = queue.get("by_state") or {}
    add(f"- review queue: **{by_state.get('NEEDS_REVIEW', 0)} awaiting review**, "
        f"{by_state.get('APPROVED', 0)} approved, {by_state.get('REJECTED', 0)} rejected, "
        f"{by_state.get('DUPLICATE', 0)} duplicates held back")
    stars = queue.get("awaiting_review_by_stars") or {}
    if stars:
        add("- by priority: "
            + " · ".join(f"{'★' * int(k)}{'☆' * (5 - int(k))} {v}"
                         for k, v in sorted(stars.items(), reverse=True)))
    add("")

    top = collection.get("top_of_queue") or []
    if top:
        add("### Read these first")
        add("")
        for item in top[:5]:
            add(f"- {'★' * (item['stars'] or 1)}{'☆' * (5 - (item['stars'] or 1))} "
                f"**{item['type']}** — {item['title']}")
            if item.get("why"):
                add(f"  <br>*{item['why']}*")
        add("")

    # ── what is broken ──────────────────────────────────────────────────────
    add("## Operational health")
    add("")
    add(f"- graph integrity: **{integrity['status']}** — {integrity['counts']}")
    sync = snapshot["sync"]
    add(f"- last successful sync: {sync.get('last_success') or 'never recorded'}"
        + (f" · last failure: {sync['last_failure']}" if sync.get("last_failure") else ""))
    add(f"- graph validation: {snapshot.get('graph_validation') or 'not run'} · "
        f"engine compatibility: {snapshot.get('engine_compatibility') or 'not run'}")
    add("")
    findings = (integrity.get("findings") or []) + (collection.get("findings") or [])
    if findings:
        add("| severity | check | detail |")
        add("|---|---|---|")
        for finding in findings[:12]:
            add(f"| {finding['severity']} | {finding['check']} | {finding['detail'][:160]} |")
        add("")
    else:
        add("No findings.")
        add("")

    # ── what people wanted ──────────────────────────────────────────────────
    add("## Demand")
    add("")
    if demand.get("has_data"):
        add(f"{demand['total']} searches, {demand['unique_terms']} distinct terms, "
            f"**{demand.get('zero_result_pct', 0)}% returned nothing**.")
        add("")
        if demand.get("top"):
            add("| searched | times | | returned nothing | times |")
            add("|---|---:|---|---|---:|")
            zero = demand.get("zero_result") or []
            for index in range(max(len(demand["top"][:8]), len(zero[:8]))):
                left = demand["top"][index] if index < len(demand["top"]) else {"term": "", "count": ""}
                right = zero[index] if index < len(zero) else {"term": "", "count": ""}
                add(f"| {left['term']} | {left['count']} | | {right['term']} | {right['count']} |")
            add("")
    else:
        add("No search data in this report. Search tracking writes to "
            "`search_events`; pass an export with `--events` to include it.")
        add("")

    backlog = snapshot.get("backlog") or []
    if backlog:
        add("### Research backlog")
        add("")
        add("Topics people looked for that ValueWeave does not cover. "
            "**Gaps, not knowledge** — nothing here may become an entity without "
            "research against a public source.")
        add("")
        add("| score | term | searches | requests | status |")
        add("|---:|---|---:|---:|---|")
        for item in backlog[:10]:
            add(f"| {item.get('score')} | {item.get('term')} | {item.get('searches')} "
                f"| {item.get('requests')} | {item.get('status')} |")
        add("")

    # ── the knowledge base itself ───────────────────────────────────────────
    add("## Knowledge base")
    add("")
    was_overview = (previous or {}).get("overview") or {}
    add(f"- **{_delta(overview['entities'], was_overview.get('entities'))} entities** · "
        f"{_delta(overview['relationships'], was_overview.get('relationships'))} relationships · "
        f"{overview['packages']} packages")
    add(f"- {snapshot['connectivity']['connected_pct']}% connected · "
        f"{snapshot['connectivity']['isolated']} isolated · "
        f"median {snapshot['connectivity']['median_degree']} neighbours")
    add(f"- crosswalk: {overview.get('crosswalk_rows')} terms, "
        f"{overview.get('crosswalk_resolved_pct')}% resolved")
    add("")
    least = snapshot["connectivity"].get("least_connected") or []
    if least:
        add("Least connected — reachable by search, leading nowhere:")
        add("")
        for entity in least[:6]:
            add(f"- {entity['name']} ({entity['type']}, {entity['degree']} neighbours)")
        add("")

    add("---")
    add("")
    add("*Generated by `python3 -m ops.cli report --write`. "
        "Nothing in this report is published to readers.*")
    return "\n".join(out) + "\n"


def write(snapshot, now=None, report_dir=None):
    """Write both halves: the markdown a person reads and the JSON next week
    diffs against. The JSON is the one that makes the trend possible."""
    now = now or _now()
    directory = Path(report_dir or REPORT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    stem = now.strftime("%G-W%V")

    previous = previous_snapshot(before=stem, report_dir=directory)
    markdown = render(snapshot, previous=previous, now=now)

    (directory / f"{stem}.md").write_text(markdown, encoding="utf-8")
    (directory / f"{stem}.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8")
    return directory / f"{stem}.md"
