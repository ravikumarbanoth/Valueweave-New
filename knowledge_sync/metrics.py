#!/usr/bin/env python3
"""
Module 7 — Metrics.

Counts that describe a run, plus the two that describe its *quality*:

  coverage      rows in the target vs rows Git produces. Anything below 100%
                means the projection is incomplete and a page will render a gap.
  pending_rate  share of cells holding a sentinel. Rising means data quality is
                degrading; it is not visible in row counts.

Everything is derived from what the run actually did. Nothing is estimated, and
no metric is recorded that the framework cannot compute — a dashboard with an
invented number is worse than one with a missing panel.
"""

from collections import Counter


def row_metrics(all_changes, tables):
    per_table, totals = {}, Counter()
    for name, changes in sorted(all_changes.items()):
        rows = tables.get(name, [])
        pending_cells = sum(len(r.get("sync_pending_fields") or {}) for r in rows)
        cells = sum(len(r) for r in rows) or 1
        per_table[name] = {
            "source_rows": len(rows),
            "inserted": len(changes.inserts),
            "updated": len(changes.updates),
            "soft_deleted": len(changes.deletes),
            "skipped": changes.skips,
            "pending_cells": pending_cells,
            "pending_rate_pct": round(100 * pending_cells / cells, 2),
        }
        totals["source_rows"] += len(rows)
        totals["inserted"] += len(changes.inserts)
        totals["updated"] += len(changes.updates)
        totals["soft_deleted"] += len(changes.deletes)
        totals["skipped"] += changes.skips
        totals["pending_cells"] += pending_cells
        totals["cells"] += cells
    return per_table, totals


def build(run_id, mode, version, all_changes, tables, report, duration,
          packages_processed=None):
    per_table, totals = row_metrics(all_changes, tables)
    source_rows = totals["source_rows"]
    return {
        "run_id": run_id,
        "mode": mode,
        "version": version,
        "duration_seconds": duration,
        "packages_processed": sorted(packages_processed or []),
        "tables_processed": len(all_changes),
        "rows_synchronised": totals["inserted"] + totals["updated"],
        "rows_inserted": totals["inserted"],
        "rows_updated": totals["updated"],
        "rows_soft_deleted": totals["soft_deleted"],
        "rows_skipped": totals["skipped"],
        "rows_from_source": source_rows,
        "validation_errors": len(report.errors) if report else 0,
        "validation_warnings": len(report.warnings) if report else 0,
        "validation_by_check": report.by_check() if report else {},
        "pending_cells": totals["pending_cells"],
        "pending_rate_pct": round(100 * totals["pending_cells"] / (totals["cells"] or 1), 2),
        "rows_per_second": (round(source_rows / duration, 1) if duration else None),
        "by_table": per_table,
    }


def coverage(target, specs, tables):
    """Rows in the target vs rows Git produces. Below 100% means an incomplete page."""
    out = {}
    for spec in specs:
        expected = len(tables.get(spec.name, []))
        actual = target.count(spec.name)
        out[spec.name] = {
            "expected": expected,
            "in_target": actual,
            "coverage_pct": round(100 * actual / expected, 2) if expected else 100.0,
            "complete": actual == expected,
        }
    return out
