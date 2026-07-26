#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — migration: add the mandatory `notes` column to Package001

WHY THIS EXISTS
---------------
Package001_Geography was built before `notes` became the sixth mandatory provenance
column. Every other package has it. Nothing noticed, because no consumer required
all six until the Knowledge Engine was recovered in v2.2: its `ProvenanceRecord`
emits exactly six columns, and it cannot write a record into a dataset that has
nowhere to put one of them (compatibility check C4).

WHAT IT DOES
------------
Appends a `notes` column to the five Package001 datasets, with an empty value.

An empty note is the honest value. There is no note for these rows, and inventing
explanatory text to fill a column would be fabrication. A blank `notes` cell is
already accepted elsewhere in the repository — Package002 has 12, Package006 has 12.

The migration is idempotent: a dataset that already has the column is left alone.
No existing column is renamed, reordered or removed, and no existing value changes.

    python3 migrations/v2_2_add_notes_column.py --check    # report only
    python3 migrations/v2_2_add_notes_column.py --apply
"""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "packages" / "Package001_Geography" / "datasets"
COLUMN = "notes"


def datasets():
    return sorted(TARGET.glob("*.csv"))


def header(path):
    with open(path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f), [])


def apply(path):
    """Append the column. Returns the number of rows written."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = header(path) + [COLUMN]
    for r in rows:
        r[COLUMN] = ""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pending = [p for p in datasets() if COLUMN not in header(p)]
    print(f"Package001_Geography: {len(datasets())} datasets, "
          f"{len(pending)} missing the {COLUMN!r} column")
    for p in datasets():
        state = "MISSING" if p in pending else "present"
        print(f"  [{state:>7}] {p.name}")

    if args.check or not args.apply:
        sys.exit(1 if pending else 0)

    for p in pending:
        n = apply(p)
        print(f"  added {COLUMN!r} to {p.name} ({n} rows)")
    print(f"\n{len(pending)} datasets migrated." if pending else "\nNothing to do.")
