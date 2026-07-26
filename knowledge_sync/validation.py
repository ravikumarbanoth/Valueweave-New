#!/usr/bin/env python3
"""
Module 2 — Validation. Six checks, run before anything reaches the target.

  V1  Schema        every declared column present; nothing undeclared
  V2  Keys          sync_row_key present and unique within the table
  V3  Required      declared required columns non-empty
  V4  Foreign keys  cross-table references resolve
  V5  Confidence    integer 0-100, or NULL where the source carries none
  V6  Ownership     the owning package matches the ownership registry
  V7  Verification  status is a registered VST-* value

SEVERITY IS THE DESIGN DECISION HERE
------------------------------------
An ERROR aborts the sync. A WARNING is recorded and the sync proceeds.

The split is not about how serious a problem sounds — it is about whether writing
the row would make the target *wrong*. A broken foreign key would produce a
dangling reference that no consumer can detect, so it is an error. A row with
`verification_status = VST-NEEDS_REVIEW` is unreviewed, which is true of all
2,299 rows in the knowledge base — refusing to sync it would refuse to sync
anything, so it is not even a warning; it is the normal state, and the projection
carries the status so the UI can say so.

Validation reports everything it finds. It does not stop at the first error,
because an operator fixing one problem should be able to see the other nineteen.
"""

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from knowledge_sync.config import ROOT, SENTINELS

ERROR, WARNING = "ERROR", "WARNING"
VALID_VERIFICATION = {"VST-NEEDS_REVIEW", "VST-VERIFIED", "VST-REJECTED"}


@dataclass
class Finding:
    check: str
    severity: str
    table: str
    detail: str
    row_key: str = ""

    def __str__(self):
        where = f" [{self.row_key}]" if self.row_key else ""
        return f"{self.severity} {self.check} {self.table}{where}: {self.detail}"


class ValidationReport:
    def __init__(self):
        self.findings = []

    def add(self, *args, **kwargs):
        self.findings.append(Finding(*args, **kwargs))

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == WARNING]

    @property
    def ok(self):
        return not self.errors

    def by_check(self):
        out = defaultdict(int)
        for f in self.findings:
            out[f"{f.check}:{f.severity}"] += 1
        return dict(sorted(out.items()))

    def to_dict(self):
        return {
            "ok": self.ok,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "by_check": self.by_check(),
            "findings": [
                {"check": f.check, "severity": f.severity, "table": f.table,
                 "row_key": f.row_key, "detail": f.detail}
                for f in self.findings[:200]      # cap: a report nobody reads is noise
            ],
            "findings_truncated": max(0, len(self.findings) - 200),
        }


def _ownership_owners():
    """entity_type -> owner package, from the ownership registry."""
    path = ROOT / "knowledge_graph" / "ownership" / "ownership_registry.csv"
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {r["entity_type"]: r["owner_package"] for r in csv.DictReader(f)}


def _declared_overlaps():
    """(entity_type, holder_package) -> ADR, from known_overlaps.csv.

    Same treatment graph check G7 gives: duplication that has been declared and
    attributed to an ADR is governed, not a violation. Warning on all 115 declared
    cases would train an operator to ignore the warning list, which is the failure
    mode that matters — an undeclared overlap would then slip past unnoticed.
    """
    path = ROOT / "knowledge_graph" / "ownership" / "known_overlaps.csv"
    if not path.exists():
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for holder in row["also_held_by"].split(";"):
                holder = holder.strip()
                if holder:
                    out[(row["entity_type"], holder)] = row["adr"]
    return out


def validate(specs, tables, report=None):
    """
    Validate every table. `tables` is {table_name: [transformed rows]}.

    Foreign keys are checked across the whole set rather than per table, which is
    why this takes all of them at once: kg_relationships cannot be validated
    without kg_entities in hand.
    """
    report = report or ValidationReport()
    owners = _ownership_owners()
    declared_overlaps = _declared_overlaps()

    # Key sets for foreign-key resolution, built before any FK check runs.
    key_index = defaultdict(set)
    for spec in specs:
        for row in tables.get(spec.name, []):
            for column in spec.columns:
                key_index[(spec.name, column)].add(row.get(column))

    for spec in specs:
        rows = tables.get(spec.name, [])
        declared = set(spec.columns)

        # ---------------------------------------------------------- V1 schema
        for row in rows[:1]:                 # shape is uniform; one row proves it
            missing = declared - set(row)
            if missing:
                report.add("V1-SCHEMA", ERROR, spec.name,
                           f"declared columns absent from the row: {sorted(missing)}")
            undeclared = {k for k in row
                          if k not in declared and not k.startswith("sync_")}
            if undeclared:
                report.add("V1-SCHEMA", ERROR, spec.name,
                           f"undeclared columns present: {sorted(undeclared)}")

        # ------------------------------------------------------------ V2 keys
        seen = defaultdict(int)
        for row in rows:
            key = row.get("sync_row_key") or ""
            if not key.strip():
                report.add("V2-KEY", ERROR, spec.name,
                           f"empty sync_row_key (source row "
                           f"{row.get('sync_source_row_id')!r})")
            seen[key] += 1
        for key, n in seen.items():
            if n > 1:
                report.add("V2-KEY", ERROR, spec.name,
                           f"sync_row_key appears {n} times", row_key=key)

        # -------------------------------------------------------- V3 required
        for row in rows:
            for column in spec.required:
                value = row.get(column)
                if value is None or (isinstance(value, str) and not value.strip()):
                    report.add("V3-REQUIRED", ERROR, spec.name,
                               f"required column {column!r} is empty",
                               row_key=row.get("sync_row_key", ""))

        # ----------------------------------------------------- V4 foreign keys
        for column, target_table, target_column in spec.foreign_keys:
            valid = key_index.get((target_table, target_column), set())
            if not valid:
                report.add("V4-FOREIGN_KEY", ERROR, spec.name,
                           f"{column} references {target_table}.{target_column}, "
                           f"which extracted no rows")
                continue
            for row in rows:
                value = row.get(column)
                if value in (None, "") or value in SENTINELS:
                    continue
                if value not in valid:
                    report.add("V4-FOREIGN_KEY", ERROR, spec.name,
                               f"{column}={value!r} not found in "
                               f"{target_table}.{target_column}",
                               row_key=row.get("sync_row_key", ""))

        # ------------------------------------------------------ V5 confidence
        if spec.confidence_column:
            for row in rows:
                value = row.get(spec.confidence_column)
                if value is None:
                    continue          # sentinel or genuinely absent; V5 is not V3
                try:
                    n = int(value)
                except (TypeError, ValueError):
                    report.add("V5-CONFIDENCE", ERROR, spec.name,
                               f"{spec.confidence_column}={value!r} is not an integer",
                               row_key=row.get("sync_row_key", ""))
                    continue
                if not 0 <= n <= 100:
                    report.add("V5-CONFIDENCE", ERROR, spec.name,
                               f"{spec.confidence_column}={n} is outside 0-100",
                               row_key=row.get("sync_row_key", ""))

        # ------------------------------------------------------- V6 ownership
        # Applies to kg_entities, where each row names the package it came from.
        if spec.name == "kg_entities" and owners:
            governed = defaultdict(int)
            for row in rows:
                etype = row.get("entity_type")
                expected = owners.get(etype)
                actual = row.get("source_package")
                if not (expected and actual) or expected == actual:
                    continue
                adr = declared_overlaps.get((etype, actual))
                if adr:
                    governed[(etype, actual, adr)] += 1
                    continue
                report.add("V6-OWNERSHIP", ERROR, spec.name,
                           f"{etype} sourced from {actual}, registry says {expected}, "
                           f"and the overlap is NOT declared in known_overlaps.csv",
                           row_key=row.get("sync_row_key", ""))
            # Declared overlaps are summarised once each, not once per row.
            for (etype, actual, adr), n in sorted(governed.items()):
                report.add("V6-OWNERSHIP", WARNING, spec.name,
                           f"{n} {etype} rows held by {actual} rather than "
                           f"{owners[etype]} — declared and governed by {adr}")

        # ---------------------------------------------------- V7 verification
        if spec.verification_column:
            for row in rows:
                value = row.get(spec.verification_column)
                if value in (None, ""):
                    continue
                if value not in VALID_VERIFICATION:
                    report.add("V7-VERIFICATION", ERROR, spec.name,
                               f"{spec.verification_column}={value!r} is not a "
                               f"registered status", row_key=row.get("sync_row_key", ""))

    return report
