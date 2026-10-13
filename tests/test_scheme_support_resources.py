#!/usr/bin/env python3
import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "frontend" / "data" / "scheme-support-resources.json"
CSV = ROOT / "packages" / "Package007_Government_Schemes" / "datasets" / "scheme_support_resources.csv"
LIST_PAGE = ROOT / "frontend" / "app" / "schemes" / "page.js"
DETAIL_PAGE = ROOT / "frontend" / "app" / "schemes" / "[slug]" / "page.js"
DIRECTORY = ROOT / "frontend" / "components" / "schemes" / "SchemeSupportDirectory.jsx"


class SchemeSupportImportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(DATA.read_text(encoding="utf-8"))
        cls.records = cls.payload["records"]
        cls.by_slug = {record["slug"]: record for record in cls.records}

    def test_all_populated_workbook_records_are_imported(self):
        self.assertEqual(self.payload["recordCount"], 56)
        self.assertEqual(len(self.records), 56)
        self.assertEqual(
            self.payload["categoryCounts"],
            {
                "Awareness and Digital Literacy": 4,
                "Bank Loan Schemes": 10,
                "Complaints and Grievance Redressal": 1,
                "Handholding and Entrepreneurship Development": 11,
                "Skill Development Centres": 25,
                "Social Security Schemes": 5,
            },
        )

    def test_package_csv_and_frontend_json_stay_in_sync(self):
        with CSV.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 56)
        self.assertEqual([row["resource_id"] for row in rows], [record["resource_id"] for record in self.records])
        self.assertEqual([row["slug"] for row in rows], [record["slug"] for record in self.records])

    def test_slugs_are_stable_and_unique(self):
        slugs = [record["slug"] for record in self.records]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertIn("aif", self.by_slug)
        self.assertIn("rbi-ombudsman", self.by_slug)

    def test_blank_field_rows_are_preserved(self):
        aif = self.by_slug["aif"]
        self.assertEqual(aif["source_excel_row"], "2")
        self.assertEqual(aif["name"], "AIF")
        self.assertEqual(aif["description"], "")
        self.assertIn("description", aif["missing_fields"])
        self.assertIn("official_website", aif["missing_fields"])

    def test_non_scheme_resources_are_not_marked_as_government_schemes(self):
        training = [record for record in self.records if record["display_category"] == "Skill Development Centres"]
        self.assertEqual(len(training), 25)
        self.assertTrue(all(record["entity_type"] == "TrainingProvider" for record in training))
        self.assertEqual(self.by_slug["rbi-ombudsman"]["entity_type"], "Institution")
        self.assertEqual(self.by_slug["psb-loan-in-59-minutes"]["record_kind"], "Loan portal")
        self.assertEqual(self.by_slug["vidyalakshmi"]["record_kind"], "Education loan portal")


class SchemeSupportFrontendTest(unittest.TestCase):
    def test_schemes_page_uses_imported_directory_and_preserves_graph_items(self):
        src = LIST_PAGE.read_text(encoding="utf-8")
        self.assertIn("SchemeSupportDirectory", src)
        self.assertIn("schemeSupportResources", src)
        self.assertIn("graphItems={graphItems}", src)

    def test_detail_page_checks_imported_records_before_graph_redirect(self):
        src = DETAIL_PAGE.read_text(encoding="utf-8")
        self.assertIn("getSchemeSupportResource", src)
        self.assertLess(
            src.index("const imported = getSchemeSupportResource"),
            src.index("const { row, source } = await detailWithGraphFallback"),
        )
        self.assertIn("generateStaticParams", src)

    def test_directory_search_covers_acronyms_tags_and_notes(self):
        src = DIRECTORY.read_text(encoding="utf-8")
        for field in ("name", "source_name", "acronym", "description", "supplemental_notes", "display_category"):
            self.assertIn(f'"{field}"', src)
        self.assertIn("scheme-support-filters", src)
        self.assertIn("Try PMMY, RSETI, grievance, digital literacy", src)

    def test_key_acronyms_and_organisation_types_are_searchable(self):
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        records = payload["records"]
        acronyms = {r["acronym"] for r in records if r["acronym"]}
        for expected in ("PMMY", "PMEGP", "CGTMSE", "PMFME", "PM SVANidhi", "APY", "PMJDY"):
            self.assertIn(expected, acronyms)
        org_types = {r["organisation_type"] for r in records}
        for expected_org in ("Government", "NGO", "Foundation", "Trust", "Vocational Training Provider (VTP)"):
            self.assertIn(expected_org, org_types)

    def test_public_components_do_not_expose_internal_spreadsheet_fields(self):
        detail_file = ROOT / "frontend" / "components" / "schemes" / "SchemeSupportDetail.jsx"
        for path in (DIRECTORY, detail_file):
            src = path.read_text(encoding="utf-8")
            self.assertNotIn("source_excel_row", src)
            self.assertNotIn("canonical_scheme_id", src)
            self.assertNotIn(".xlsx", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
