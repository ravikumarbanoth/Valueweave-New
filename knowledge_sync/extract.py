#!/usr/bin/env python3
"""
Extraction — read the Git sources into normalised rows.

Deliberately the dullest module in the framework: it reads CSVs and shapes them
to the spec's column list. Anything clever belongs in transform.py, where it can
be tested against a fixture rather than against the repository.

Two rules it does enforce:

  * **Only declared columns survive.** A column added upstream is dropped rather
    than silently widening the projection, so a package release cannot change the
    Supabase schema by accident.

  * **Every row records where it came from** — package, dataset and row id —
    before any other module sees it. A row that cannot name its origin is not a
    row this framework will sync.
"""

import csv

from knowledge_sync.config import TableSpec


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def source_rows(source, spec):
    """Rows from one Source, shaped to the spec and tagged with provenance."""
    out = []
    for raw in read_csv(source.path):
        row = {c: raw.get(c, "") for c in spec.columns}
        row.update(source.constants)
        row_id = (raw.get(source.key_column) or "").strip()
        row["sync_source_package"] = source.package
        row["sync_source_dataset"] = source.dataset
        row["sync_source_row_id"] = row_id
        # Unique within the table even when several datasets feed it: two
        # Package004 files both key on `id`, so the dataset name disambiguates.
        row["sync_row_key"] = (row_id if len(spec.sources) == 1
                               else f"{source.dataset}:{row_id}")
        out.append(row)
    return out


def extract(spec: TableSpec):
    """All rows for one table, across every source that feeds it."""
    rows = []
    for source in spec.sources:
        rows.extend(source_rows(source, spec))
    return rows


def extract_all(specs):
    return {s.name: extract(s) for s in specs}
