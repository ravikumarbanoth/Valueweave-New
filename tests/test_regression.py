#!/usr/bin/env python3
"""
Work Package 6 — Regression tests.

One test per bug that has actually been found and fixed in this repository. Nothing
speculative: if a case is here, something once got it wrong.

The value of this file is that each test is a short account of a real failure. A
future change that reintroduces one of these fails with a message saying what the
original mistake was, rather than an anonymous assertion error.
"""

import csv
import io
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class SentinelDisciplineRegressionTest(unittest.TestCase):
    """Package005 V5 caught a note reading 'district attribution left
    PENDING_VERIFICATION'. The sentinel must be a whole cell, never a word in a
    sentence, or a consumer filtering on it silently misses data."""

    PROVENANCE_COLUMNS = {"data_source", "source_url", "collection_date",
                          "confidence_score", "verification_status"}

    def test_provenance_columns_never_embed_the_sentinel_in_prose(self):
        offenders = []
        for pkg in sorted(p for p in (ROOT / "packages").iterdir() if p.is_dir()):
            ds = pkg / "datasets"
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                for i, row in enumerate(read(f), start=2):
                    for k in self.PROVENANCE_COLUMNS & set(row):
                        v = (row[k] or "").strip()
                        if "PENDING_VERIFICATION" in v and v != "PENDING_VERIFICATION":
                            offenders.append(f"{pkg.name}/{f.name}:{i}[{k}]")
        self.assertEqual(offenders, [], f"non-bare sentinels: {offenders[:5]}")


class AmpersandRegressionTest(unittest.TestCase):
    """v2.0: `Agriculture & Allied` and `Agriculture and Allied` produced two graph
    nodes, and named query 5 silently returned nothing. Both the graph's slug and
    search normalisation must fold `&` to `and`."""

    def test_graph_holds_no_ampersand_split_duplicates(self):
        """Asserted on the artifact rather than by importing build_graph.py, which
        rebuilds the entire graph at import time. The artifact is also the thing
        that was actually wrong: two nodes where there should have been one."""
        seen = {}
        collisions = []
        for e in read(ROOT / "knowledge_graph" / "entities" / "entities.csv"):
            key = (e["entity_type"],
                   e["canonical_name"].replace("&", "and").lower().replace("  ", " "))
            if key in seen and seen[key] != e["canonical_name"]:
                collisions.append(f"{seen[key]!r} / {e['canonical_name']!r}")
            seen[key] = e["canonical_name"]
        self.assertEqual(collisions, [],
                         f"names differing only by & vs and became separate nodes: "
                         f"{collisions}")

    def test_search_normalisation_folds_ampersand(self):
        from search.index import normalise
        self.assertEqual(normalise("Welding & Metal Fabrication"),
                         normalise("Welding and Metal Fabrication"))


class ResolverShadowingRegressionTest(unittest.TestCase):
    """v2.0: `normalise()` strips parentheticals, so `Manufacturing (General)`
    shadowed `Manufacturing` in the type index, and `Manufacturing` vs
    `Manufacturing (Automotive)` scored a false 1.000 similarity."""

    def test_exact_name_wins_over_a_parenthetical_variant(self):
        from knowledge_graph.resolution.resolver import Resolver
        r = Resolver()
        hit = r.resolve("Manufacturing", entity_type="Industry")
        self.assertIsNotNone(hit)
        self.assertEqual(hit["canonical_name"], "Manufacturing")

    def test_parent_and_child_are_not_scored_identical(self):
        from knowledge_graph.resolution.resolver import Resolver
        self.assertLess(Resolver.similarity("Manufacturing", "Manufacturing (Automotive)"),
                        1.0)


class ForeignKeyRegressionTest(unittest.TestCase):
    """Package007 and Package008 each shipped references to ids that looked
    plausible and did not exist — `AP-GNT` for `AP-GUN`, a skill named only in a
    collection report. Guessing an id format is not reading it."""

    def test_district_references_resolve(self):
        districts = {r["dist_id"] for r in read(
            ROOT / "packages" / "Package001_Geography" / "datasets" / "district.csv")}
        broken = []
        for pkg in sorted(p for p in (ROOT / "packages").iterdir() if p.is_dir()):
            ds = pkg / "datasets"
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                rows = read(f)
                if not rows:
                    continue
                cols = [c for c in rows[0] if c.endswith("dist_id")
                        or c == "package001_district_id"]
                for i, r in enumerate(rows, start=2):
                    for c in cols:
                        v = (r[c] or "").strip()
                        if v and v != "PENDING_VERIFICATION" and v not in districts:
                            broken.append(f"{pkg.name}/{f.name}:{i}[{c}]={v}")
        self.assertEqual(broken, [], f"unresolvable district references: {broken[:5]}")


class StaleFigureRegressionTest(unittest.TestCase):
    """After the v2 merge, PLATFORM_V2.md and ADR-001 still said 650 entities and
    77.85% connectivity when the real figures were 647 and 78.05%. Generated
    artifacts were right; hand-typed prose had drifted."""

    def test_hand_written_docs_do_not_state_a_stale_entity_count(self):
        actual = len(read(ROOT / "knowledge_graph" / "entities" / "entities.csv"))
        stale = []
        for doc in [ROOT / "PLATFORM_V2.md",
                    ROOT / "governance" / "adr" / "ADR-001-knowledge-graph-as-derived-layer.md"]:
            if not doc.exists():
                continue
            text = doc.read_text()
            for wrong in (str(actual + 3), str(actual - 3)):
                if f"{wrong} entities" in text:
                    stale.append(f"{doc.name} says '{wrong} entities', actual {actual}")
        self.assertEqual(stale, [], f"stale figures: {stale}")


class BackwardCompatibilityRegressionTest(unittest.TestCase):
    """v2.2 appended columns to six packages. Appending must never rewrite a value:
    the failure mode is silent, because the row count and column order still look
    right."""

    TOUCHED = [
        "packages/Package001_Geography/datasets/district.csv",
        "packages/Package001_Geography/datasets/state.csv",
        "packages/Package002_Education/datasets/scholarships.csv",
        "packages/Package003_Healthcare/datasets/government_health_insurance_schemes.csv",
        "packages/Package004_Industries/datasets/msme_entrepreneurship_support_schemes.csv",
        "packages/Package005_Agriculture/datasets/agriculture_schemes.csv",
        "packages/Package006_Skills_and_Training/datasets/government_skill_schemes.csv",
    ]

    def test_no_existing_cell_value_changed(self):
        for rel in self.TOUCHED:
            with self.subTest(dataset=rel):
                before = subprocess.run(["git", "show", f"main:{rel}"], cwd=ROOT,
                                        capture_output=True, text=True)
                if before.returncode != 0:
                    self.skipTest("main is not available for comparison")
                old = list(csv.DictReader(io.StringIO(before.stdout)))
                new = read(ROOT / rel)
                self.assertEqual(len(old), len(new), f"{rel}: row count changed")
                if not old:
                    continue
                changed = [(i, c) for i, (a, b) in enumerate(zip(old, new))
                           for c in old[0] if a[c] != b[c]]
                self.assertEqual(changed, [], f"{rel}: {len(changed)} values changed")


class PackageValidatorRegressionTest(unittest.TestCase):
    """Every package that ships a validator must still pass it after v2.2's
    column additions."""

    def test_package_validators_still_pass(self):
        for validator in sorted((ROOT / "packages").glob("*/validate.py")):
            with self.subTest(package=validator.parent.name):
                result = subprocess.run([sys.executable, "validate.py"],
                                        cwd=validator.parent,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0,
                                 f"{validator.parent.name} validator failed:\n"
                                 f"{result.stdout[-2000:]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
