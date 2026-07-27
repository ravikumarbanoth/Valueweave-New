#!/usr/bin/env python3
"""
Graph compiler coverage — regression protection for `knowledge_graph/build_graph.py`.

The builder is the compiler for the knowledge platform: a dataset that it does not
read contributes nothing, however well researched it is. Today it reads 39 of 77
datasets, and the 38 it skips were skipped silently — nothing in the build output,
the graph summary or the test suite said so.

**What this file protects, in order of how badly it would hurt:**

  1. **A new dataset added to a package must be registered.** Adding a CSV to
     `packages/*/datasets/` and forgetting the builder is how the repository reached
     39/77. `test_every_dataset_is_registered` fails the moment it happens.
  2. **The manifest must not drift from the builder.** A manifest that claims a
     dataset is consumed while `build_graph.py` never opens it is worse than no
     manifest. `test_consumed_manifest_matches_the_builder_source` parses the
     builder and compares.
  3. **Coverage must not regress.** Registering a dataset is progress; un-registering
     one is not. `test_coverage_does_not_regress` pins the floor.

The manifest below is a **census, not an aspiration**. `IGNORED` records datasets
that exist and are not consumed — every entry is a known gap with a plan in
`BUILDER_REGISTRY.md`, not an oversight. Moving an entry from `IGNORED` to
`CONSUMED` is the unit of progress this file measures.
"""

import csv
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
BUILDER = ROOT / "knowledge_graph" / "build_graph.py"
sys.path.insert(0, str(ROOT))


# ══════════════════════════════════════════════════════ the registry manifest
#
# Every dataset in packages/*/datasets/ must appear in exactly one set below.
# A dataset in none of them fails test_every_dataset_is_registered.

#: Read by build_graph.py and contributing entities or relationships.
CONSUMED = {
    "Package001_Geography/datasets/district.csv",
    "Package001_Geography/datasets/state.csv",
    "Package002_Education/datasets/universities_telangana_andhra_pradesh.csv",
    "Package004_Industries/datasets/china_inspired_adapted_opportunities.csv",
    "Package004_Industries/datasets/construction_skilled_trade_services.csv",
    "Package004_Industries/datasets/digital_technology_livelihoods.csv",
    "Package004_Industries/datasets/food_agro_processing_micro_enterprises.csv",
    "Package005_Agriculture/datasets/ai_precision_agriculture.csv",
    "Package005_Agriculture/datasets/climate_zones.csv",
    "Package005_Agriculture/datasets/crop_categories.csv",
    "Package005_Agriculture/datasets/crop_climate_mapping.csv",
    "Package005_Agriculture/datasets/crop_soil_mapping.csv",
    "Package005_Agriculture/datasets/crops.csv",
    "Package005_Agriculture/datasets/export_opportunities.csv",
    "Package005_Agriculture/datasets/farm_machinery.csv",
    "Package005_Agriculture/datasets/soil_types.csv",
    "Package006_Skills_and_Training/datasets/certifications.csv",
    "Package006_Skills_and_Training/datasets/industry_skill_mapping.csv",
    "Package006_Skills_and_Training/datasets/skill_business_mapping.csv",
    "Package006_Skills_and_Training/datasets/skills.csv",
    "Package006_Skills_and_Training/datasets/training_providers.csv",
    "Package007_Government_Schemes/datasets/agriculture_scheme_mapping.csv",
    "Package007_Government_Schemes/datasets/financial_institutions.csv",
    "Package007_Government_Schemes/datasets/government_schemes.csv",
    "Package007_Government_Schemes/datasets/industry_scheme_mapping.csv",
    "Package007_Government_Schemes/datasets/skill_scheme_mapping.csv",
    "Package008_MSME/datasets/agriculture_business_mapping.csv",
    "Package008_MSME/datasets/ai_business_tools.csv",
    "Package008_MSME/datasets/district_business_mapping.csv",
    "Package008_MSME/datasets/education_support_mapping.csv",
    "Package008_MSME/datasets/export_opportunities.csv",
    "Package008_MSME/datasets/financial_support.csv",
    "Package008_MSME/datasets/machinery_mapping.csv",
    "Package008_MSME/datasets/market_channels.csv",
    "Package008_MSME/datasets/msme_businesses.csv",
    "Package008_MSME/datasets/msme_categories.csv",
    "Package008_MSME/datasets/raw_material_mapping.csv",
    "Package008_MSME/datasets/scheme_mapping.csv",
    "Package008_MSME/datasets/skill_mapping.csv",
}

#: Present, populated, and NOT read by the builder. Each has an entry in
#: BUILDER_REGISTRY.md naming its entity types, foreign keys and expected
#: contribution. Shrinking this set is the point of the graph-compiler work.
IGNORED = {
    "Package001_Geography/datasets/revenue_division_telangana.csv",
    "Package002_Education/datasets/education_boards_regulatory_bodies.csv",
    "Package002_Education/datasets/entrance_exams.csv",
    "Package002_Education/datasets/scholarships.csv",
    "Package003_Healthcare/datasets/government_health_insurance_schemes.csv",
    "Package003_Healthcare/datasets/government_hospitals_telangana_andhra_pradesh.csv",
    "Package003_Healthcare/datasets/medical_colleges_telangana_andhra_pradesh.csv",
    "Package003_Healthcare/datasets/medical_regulatory_bodies_and_health_missions.csv",
    "Package004_Industries/datasets/msme_entrepreneurship_support_schemes.csv",
    "Package005_Agriculture/datasets/agri_business_mapping.csv",
    "Package005_Agriculture/datasets/agri_processing_opportunities.csv",
    "Package005_Agriculture/datasets/agriculture_schemes.csv",
    "Package005_Agriculture/datasets/agriculture_training.csv",
    "Package005_Agriculture/datasets/crop_disease_management.csv",
    "Package005_Agriculture/datasets/farmer_producer_organizations.csv",
    "Package005_Agriculture/datasets/market_linkages.csv",
    "Package006_Skills_and_Training/datasets/ai_skill_mapping.csv",
    "Package006_Skills_and_Training/datasets/career_paths.csv",
    "Package006_Skills_and_Training/datasets/government_skill_schemes.csv",
    "Package006_Skills_and_Training/datasets/skill_categories.csv",
    "Package006_Skills_and_Training/datasets/training_centres.csv",
    "Package007_Government_Schemes/datasets/application_process.csv",
    "Package007_Government_Schemes/datasets/district_scheme_mapping.csv",
    "Package007_Government_Schemes/datasets/education_scheme_mapping.csv",
    "Package007_Government_Schemes/datasets/eligibility_criteria.csv",
    "Package007_Government_Schemes/datasets/implementing_agencies.csv",
    "Package007_Government_Schemes/datasets/required_documents.csv",
    "Package007_Government_Schemes/datasets/scheme_ai_recommendations.csv",
    "Package007_Government_Schemes/datasets/scheme_application_status.csv",
    "Package007_Government_Schemes/datasets/scheme_benefits.csv",
    "Package007_Government_Schemes/datasets/scheme_categories.csv",
    "Package008_MSME/datasets/business_models.csv",
    "Package008_MSME/datasets/industry_mapping.csv",
    "Package008_MSME/datasets/investment_intelligence.csv",
    "Package008_MSME/datasets/license_compliance.csv",
    "Package008_MSME/datasets/startup_ecosystem.csv",
}

#: Header-only. Nothing to consume until they are collected.
EMPTY = {
    "Package001_Geography/datasets/mandal.csv",
    "Package001_Geography/datasets/revenue_division_andhra_pradesh.csv",
}

#: Coverage floor. Raise it when datasets are registered; never lower it.
MIN_CONSUMED = 39


def on_disk():
    return {str(p.relative_to(PACKAGES)) for p in PACKAGES.glob("*/datasets/*.csv")}


def builder_reads():
    """
    Dataset paths `build_graph.py` actually opens.

    Two loading styles have to be understood, and a checker that knows only the
    first would report Package004 as unread:

      read("Package005_Agriculture/datasets/crops.csv")       -- literal
      read(f"Package004_Industries/datasets/{fname}.csv")     -- from P4_FILES
    """
    src = BUILDER.read_text(encoding="utf-8")
    paths = {m for m in re.findall(r'(?:read|maybe)\(\s*"([^"]+)"', src)
             if m.startswith("Package")}
    block = re.search(r"P4_FILES\s*=\s*\{(.*?)\}", src, re.S)
    if block:
        for name in re.findall(r'"(\w+)"\s*:\s*"\w+"', block.group(1)):
            paths.add(f"Package004_Industries/datasets/{name}.csv")
    return paths


# ═══════════════════════════════════════════════════════════ 1. registration
class DatasetRegistrationTest(unittest.TestCase):

    def test_every_dataset_is_registered(self):
        """
        The regression this file exists for.

        A new CSV under packages/*/datasets/ that nobody classified is invisible to
        the graph and to every report derived from it. Failing here forces the
        decision — consume it, or record why not — at the moment it is cheap.
        """
        unregistered = sorted(on_disk() - CONSUMED - IGNORED - EMPTY)
        self.assertEqual(
            unregistered, [],
            "dataset(s) present in packages/ but absent from the compiler registry.\n"
            "Add each to CONSUMED (and wire it into build_graph.py) or to IGNORED "
            "(with an entry in docs/BUILDER_REGISTRY.md saying why):\n  "
            + "\n  ".join(unregistered))

    def test_no_manifest_entry_is_stale(self):
        """A manifest naming a file that no longer exists silently over-reports."""
        missing = sorted((CONSUMED | IGNORED | EMPTY) - on_disk())
        self.assertEqual(missing, [],
                         f"registry names dataset(s) that do not exist: {missing}")

    def test_the_three_sets_are_disjoint(self):
        for a, b, an, bn in ((CONSUMED, IGNORED, "CONSUMED", "IGNORED"),
                             (CONSUMED, EMPTY, "CONSUMED", "EMPTY"),
                             (IGNORED, EMPTY, "IGNORED", "EMPTY")):
            with self.subTest(pair=f"{an}/{bn}"):
                self.assertEqual(sorted(a & b), [],
                                 f"a dataset cannot be both {an} and {bn}")


# ══════════════════════════════════════════════ 2. the manifest tracks reality
class ManifestFidelityTest(unittest.TestCase):
    """
    A manifest that drifts from the builder is worse than none: it reports coverage
    the compiler does not have, and every downstream figure inherits the error.
    """

    def test_consumed_manifest_matches_the_builder_source(self):
        reads = builder_reads()
        claimed_not_read = sorted(CONSUMED - reads)
        read_not_claimed = sorted(reads - CONSUMED)
        self.assertEqual(claimed_not_read, [],
                         "CONSUMED claims dataset(s) build_graph.py never opens: "
                         f"{claimed_not_read}")
        self.assertEqual(read_not_claimed, [],
                         "build_graph.py reads dataset(s) missing from CONSUMED: "
                         f"{read_not_claimed}")

    def test_ignored_datasets_are_genuinely_unread(self):
        reads = builder_reads()
        contradiction = sorted(IGNORED & reads)
        self.assertEqual(contradiction, [],
                         f"IGNORED lists dataset(s) the builder does read: {contradiction}")

    def test_empty_datasets_are_actually_empty(self):
        """
        `mandal.csv` and the AP revenue divisions are header-only. If one is
        populated later it must move to IGNORED or CONSUMED, not sit in EMPTY
        looking accounted for.
        """
        for rel in sorted(EMPTY):
            with self.subTest(dataset=rel):
                with open(PACKAGES / rel, encoding="utf-8") as f:
                    rows = sum(1 for _ in csv.reader(f)) - 1
                self.assertLessEqual(
                    rows, 0,
                    f"{rel} now has {rows} rows — reclassify it out of EMPTY")


# ═══════════════════════════════════════════════════════════════ 3. coverage
class CoverageTest(unittest.TestCase):

    def test_coverage_does_not_regress(self):
        self.assertGreaterEqual(
            len(CONSUMED), MIN_CONSUMED,
            f"dataset coverage fell below {MIN_CONSUMED}. Un-registering a dataset "
            "removes entities or edges from the graph")

    def test_every_package_contributes_something(self):
        """
        Package003_Healthcare currently contributes nothing: 4 datasets, 146 rows,
        0 entities, 0 edges. Recorded as a known state rather than asserted away,
        so the day it is wired in, this test says so.

        Only packages that own a `datasets/` directory count. `Package006_Skills`
        is an empty duplicate holding a README and is therefore out of scope here;
        deleting it is tracked as backlog K5.
        """
        pkgs = {p.name for p in PACKAGES.iterdir()
                if p.is_dir() and (p / "datasets").is_dir()}
        contributing = {rel.split("/")[0] for rel in CONSUMED}
        silent = sorted(pkgs - contributing)
        self.assertEqual(
            silent, ["Package003_Healthcare"],
            "the set of packages contributing nothing to the graph changed.\n"
            "Expected exactly Package003_Healthcare "
            f"(see PACKAGE003_INTEGRATION_PLAN.md). Got: {silent}")


# ══════════════════════════════════════════════════════════ 4. compiler shape
class CompilerInvariantTest(unittest.TestCase):
    """Properties of build_graph.py that later refactoring must preserve."""

    @classmethod
    def setUpClass(cls):
        cls.src = BUILDER.read_text(encoding="utf-8")

    def test_unresolved_endpoints_are_logged_by_the_edge_helper(self):
        """
        `edge()` records an unresolvable endpoint instead of dropping it. This is
        the only diagnostic the compiler has for a mapping that fails to join, and
        four call sites currently bypass it by pre-checking with `and E(...)`
        (see GRAPH_COMPILER_REPORT.md). The helper itself must keep the behaviour.
        """
        body = self.src.split("def edge(")[1].split("\ndef ")[0]
        self.assertIn("UNRESOLVED.append", body,
                      "edge() no longer logs unresolvable endpoints — mapping "
                      "failures would become invisible")

    def test_entity_and_relationship_types_are_closed_sets(self):
        """An unregistered type must abort the build, not appear in the output."""
        self.assertIn("FATAL: unregistered entity_type", self.src)
        self.assertIn("FATAL: unregistered relationship_type", self.src)

    def test_edges_are_deduplicated_by_triple(self):
        """Why the graph has 0 duplicate edges. Six new sources will test it."""
        self.assertIn("EDGE_KEYS", self.src)
        self.assertIn("key = (from_id, rtype, to_id)", self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
