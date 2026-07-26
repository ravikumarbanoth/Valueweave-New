#!/usr/bin/env python3
"""
Module 3 — Transformation. CSV strings into Supabase-ready rows.

CSV has one type: text. Postgres does not. Every conversion here is therefore a
decision about what an ambiguous cell means, and the decisions are collected in
one place so they can be argued with.

THE THREE THAT MATTER
---------------------
**A sentinel becomes NULL, never zero and never the literal string.** A sentinel
means "we could not source this". Writing it into an integer column is
impossible; writing 0 would be a fabricated measurement; keeping the string in a
text column would make every consumer re-implement the check. NULL is what SQL
already has for "unknown", and `sync_pending_fields` records *which* sentinel
applied to *which* column, so the UI can explain a blank rather than just show
one.

There is more than one sentinel, which this framework discovered rather than
assumed: `PENDING_VERIFICATION` (2,456 cells) and `PENDING_GEOCODING` (272 cells,
Package001 coordinates). SENTINELS is an explicit set, not a `PENDING_*` pattern
— a pattern would swallow legitimate uppercase data like `PMEGP`, `NABARD` and
`DEPRECATED_REFERENCE`.

**Empty string becomes NULL in numeric and date columns, but stays empty in text
columns.** An empty text cell is a real, distinguishable value in a CSV; an empty
number is not.

**A malformed number is an error, not a NULL.** Coercing `"12,00,000"` to NULL
would silently drop a real figure. It fails validation instead, loudly.

The content hash is computed here because this is the last point at which a row
is fully assembled — hashing earlier would miss the type coercion, and hashing
later would mean change detection depends on the target's round-tripping.
"""

import hashlib
import json
import re
from datetime import date, datetime

from knowledge_sync.config import SENTINELS, SYNC_COLUMNS

#: Column-name suffixes that imply a Postgres type. Naming convention is load
#: bearing across all eight packages, so it is a reliable signal.
INTEGER_HINTS = ("_id_count", "population", "mandal_count", "duration_days",
                 "rainfall_mm", "water_requirement_mm", "launch_year",
                 "nsqf_level", "confidence_score", "confidence",
                 "self_employment_score")
NUMERIC_HINTS = ("area_sq_km", "density_per_sq_km", "urban_pct", "literacy_rate_pct",
                 "sex_ratio", "latitude", "longitude", "avg_yield_tons_per_ha",
                 "temperature_min_c", "temperature_max_c")
# `minimum_investment` is deliberately NOT numeric. The name implies a measure,
# but all 45 non-empty Package004 values are sourced prose — "Rs 3,50,000 total
# project cost per the official KVIC/PMEGP profile; smaller informal starts are
# plausible but not quantified in a government source". Coercing that to a number
# would either fail or, worse, discard the sourcing that makes it trustworthy.
DATE_HINTS = ("derived_at", "created_at", "updated_at")
# `collection_date` is deliberately NOT a date column. It is a provenance
# annotation, and the packages write it two ways: a bare ISO date, or a
# semicolon-separated list with a note — "2026-07-22; 2026-07-24 (v2 enrichment)"
# — matching the multi-source cell convention used elsewhere. Parsing that to a
# single date would silently discard the second collection pass and the note that
# explains it. Git is the source of truth; a cache that reinterprets its source is
# no longer a cache. Stored verbatim as text.

_INT_RE = re.compile(r"^-?\d+$")
_NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")


class TransformError(ValueError):
    """A cell could not be converted. Carries enough context to find the row."""

    def __init__(self, table, row_key, column, value, reason):
        super().__init__(f"{table}.{column} = {value!r} in row {row_key!r}: {reason}")
        self.table, self.row_key, self.column = table, row_key, column
        self.value, self.reason = value, reason


def column_kind(name):
    if name in DATE_HINTS:
        return "date"
    if name in INTEGER_HINTS:
        return "integer"
    if name in NUMERIC_HINTS:
        return "numeric"
    return "text"


def coerce(table, row_key, column, value):
    """Return (converted, sentinel_or_None). Raises TransformError on bad input."""
    raw = (value or "").strip()
    kind = column_kind(column)

    if raw in SENTINELS:
        return None, raw
    if raw == "":
        return (None if kind != "text" else ""), None

    if kind == "integer":
        if not _INT_RE.match(raw):
            raise TransformError(table, row_key, column, raw, "not an integer")
        return int(raw), None
    if kind == "numeric":
        if not _NUM_RE.match(raw):
            raise TransformError(table, row_key, column, raw, "not a number")
        return float(raw), None
    if kind == "date":
        try:
            return date.fromisoformat(raw).isoformat(), None
        except ValueError:
            raise TransformError(table, row_key, column, raw,
                                 "not an ISO-8601 date") from None
    return raw, None


def content_hash(row):
    """Stable hash of a row's data, excluding framework bookkeeping.

    Excluding the sync_* columns is what makes the hash mean "did the *knowledge*
    change" rather than "did we touch this row". Without it every sync would
    report every row as updated, because sync_synced_at moves every time.
    """
    payload = {k: v for k, v in sorted(row.items())
               if k not in SYNC_COLUMNS and k != "sync_pending_fields"}
    blob = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def transform_row(spec, row, version, now=None):
    """One extracted row into its final projected shape."""
    key = row.get("sync_row_key", "")
    out, pending = {}, {}

    for column in spec.columns:
        converted, sentinel = coerce(spec.name, key, column, row.get(column))
        out[column] = converted
        if sentinel:
            # Which sentinel, not just that there was one: PENDING_GEOCODING on a
            # latitude means something different to a reader than
            # PENDING_VERIFICATION on a benefit amount.
            pending[column] = sentinel

    out["sync_row_key"] = key
    out["sync_source_package"] = row["sync_source_package"]
    out["sync_source_dataset"] = row["sync_source_dataset"]
    out["sync_source_row_id"] = row["sync_source_row_id"]
    out["sync_pending_fields"] = pending
    out["sync_deleted_at"] = None
    out["sync_version"] = version
    out["sync_synced_at"] = (now or datetime.utcnow()).replace(
        microsecond=0).isoformat() + "Z"
    out["sync_content_hash"] = content_hash(out)
    return out


def transform(spec, rows, version, now=None):
    """Transform every row, collecting errors rather than stopping at the first.

    A single bad cell should not hide the other nineteen. The engine aborts on any
    error, but the operator sees all of them in one run.
    """
    transformed, errors = [], []
    for row in rows:
        try:
            transformed.append(transform_row(spec, row, version, now=now))
        except TransformError as exc:
            errors.append(exc)
    return transformed, errors
