import unittest
from datetime import date, timedelta

from knowledge_engine.core.types import PENDING_VERIFICATION
from knowledge_engine.validation import (
    ConfidenceScoringRule,
    DataFreshnessRule,
    DuplicateDetectionRule,
    ForeignKeyRule,
    RequiredFieldsRule,
    SchemaValidationRule,
    SourceValidationRule,
    ValidationEngine,
)


class RequiredFieldsRuleTest(unittest.TestCase):
    def test_passes_when_all_fields_present(self):
        rule = RequiredFieldsRule(["id", "name"])
        violations = rule.check([{"id": "1", "name": "x"}], {})
        self.assertEqual(violations, [])

    def test_fails_on_missing_or_blank(self):
        rule = RequiredFieldsRule(["id", "name"])
        violations = rule.check([{"id": "1", "name": ""}, {"id": "2"}], {})
        self.assertEqual(len(violations), 2)

    def test_pending_verification_counts_as_present(self):
        rule = RequiredFieldsRule(["investment"])
        violations = rule.check([{"investment": PENDING_VERIFICATION}], {})
        self.assertEqual(violations, [])


class ForeignKeyRuleTest(unittest.TestCase):
    def test_valid_reference_passes(self):
        rule = ForeignKeyRule("district_id", references_dataset="districts")
        context = {"datasets": {"districts": [{"id": "d1"}, {"id": "d2"}]}}
        violations = rule.check([{"district_id": "d1"}], context)
        self.assertEqual(violations, [])

    def test_invalid_reference_fails(self):
        rule = ForeignKeyRule("district_id", references_dataset="districts")
        context = {"datasets": {"districts": [{"id": "d1"}]}}
        violations = rule.check([{"district_id": "missing"}], context)
        self.assertEqual(len(violations), 1)

    def test_pending_verification_is_skipped_not_failed(self):
        rule = ForeignKeyRule("district_id", references_dataset="districts")
        context = {"datasets": {"districts": []}}
        violations = rule.check([{"district_id": PENDING_VERIFICATION}], context)
        self.assertEqual(violations, [])

    def test_missing_context_raises(self):
        rule = ForeignKeyRule("district_id", references_dataset="districts")
        with self.assertRaises(KeyError):
            rule.check([{"district_id": "d1"}], {})


class DuplicateDetectionRuleTest(unittest.TestCase):
    def test_no_duplicates_passes(self):
        rule = DuplicateDetectionRule(["id"])
        violations = rule.check([{"id": "1"}, {"id": "2"}], {})
        self.assertEqual(violations, [])

    def test_within_batch_duplicate_detected(self):
        rule = DuplicateDetectionRule(["id"])
        violations = rule.check([{"id": "1"}, {"id": "1"}], {})
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].record_index, 1)

    def test_cross_batch_duplicate_detected(self):
        rule = DuplicateDetectionRule(["id"])
        violations = rule.check([{"id": "1"}], {"existing_keys": {("1",)}})
        self.assertEqual(len(violations), 1)


class SourceValidationRuleTest(unittest.TestCase):
    def test_valid_url_passes(self):
        rule = SourceValidationRule()
        violations = rule.check(
            [{"data_source": "Gov Portal", "source_url": "https://example.gov.in/data"}], {}
        )
        self.assertEqual(violations, [])

    def test_blank_source_fails(self):
        rule = SourceValidationRule()
        violations = rule.check([{"data_source": "", "source_url": ""}], {})
        self.assertEqual(len(violations), 2)

    def test_malformed_url_fails_unless_local_paths_allowed(self):
        rule = SourceValidationRule(allow_local_paths=False)
        violations = rule.check([{"data_source": "x", "source_url": "not-a-url"}], {})
        self.assertEqual(len(violations), 1)

        lenient_rule = SourceValidationRule(allow_local_paths=True)
        violations = lenient_rule.check([{"data_source": "x", "source_url": "not-a-url"}], {})
        self.assertEqual(violations, [])

    def test_multiple_semicolon_urls_all_checked(self):
        rule = SourceValidationRule()
        violations = rule.check(
            [{"data_source": "x", "source_url": "https://a.gov.in; not-a-url"}], {}
        )
        self.assertEqual(len(violations), 1)


class ConfidenceScoringRuleTest(unittest.TestCase):
    def test_in_range_passes(self):
        rule = ConfidenceScoringRule(max_score=85)
        violations = rule.check([{"confidence_score": "75"}], {})
        self.assertEqual(violations, [])

    def test_exceeds_ceiling_fails(self):
        rule = ConfidenceScoringRule(max_score=85)
        violations = rule.check([{"confidence_score": "90"}], {})
        self.assertEqual(len(violations), 1)

    def test_non_integer_fails(self):
        rule = ConfidenceScoringRule()
        violations = rule.check([{"confidence_score": "high"}], {})
        self.assertEqual(len(violations), 1)


class SchemaValidationRuleTest(unittest.TestCase):
    def setUp(self):
        self.schema = [
            {"name": "id", "type": "string"},
            {"name": "status", "type": "enum", "values": ["A", "B"]},
            {"name": "score", "type": "integer"},
        ]

    def test_valid_record_passes(self):
        rule = SchemaValidationRule(self.schema)
        violations = rule.check([{"id": "1", "status": "A", "score": "5"}], {})
        self.assertEqual(violations, [])

    def test_missing_column_fails(self):
        rule = SchemaValidationRule(self.schema)
        violations = rule.check([{"id": "1", "status": "A"}], {})
        self.assertEqual(len(violations), 1)

    def test_invalid_enum_fails(self):
        rule = SchemaValidationRule(self.schema)
        violations = rule.check([{"id": "1", "status": "Z", "score": "5"}], {})
        self.assertEqual(len(violations), 1)

    def test_pending_verification_enum_allowed(self):
        rule = SchemaValidationRule(self.schema)
        violations = rule.check([{"id": "1", "status": PENDING_VERIFICATION, "score": "5"}], {})
        self.assertEqual(violations, [])

    def test_non_integer_score_fails(self):
        rule = SchemaValidationRule(self.schema)
        violations = rule.check([{"id": "1", "status": "A", "score": "not-a-number"}], {})
        self.assertEqual(len(violations), 1)


class DataFreshnessRuleTest(unittest.TestCase):
    def test_fresh_record_passes(self):
        rule = DataFreshnessRule(max_age_days=30)
        violations = rule.check([{"collection_date": date.today().isoformat()}], {})
        self.assertEqual(violations, [])

    def test_stale_record_fails(self):
        rule = DataFreshnessRule(max_age_days=30)
        stale_date = (date.today() - timedelta(days=100)).isoformat()
        violations = rule.check([{"collection_date": stale_date}], {})
        self.assertEqual(len(violations), 1)

    def test_missing_date_fails(self):
        rule = DataFreshnessRule(max_age_days=30)
        violations = rule.check([{}], {})
        self.assertEqual(len(violations), 1)


class ValidationEngineTest(unittest.TestCase):
    def test_aggregates_violations_from_multiple_rules(self):
        engine = ValidationEngine([RequiredFieldsRule(["id"]), DuplicateDetectionRule(["id"])])
        report = engine.run([{"id": "1"}, {"id": "1"}, {}])
        self.assertFalse(report.passed)
        self.assertEqual(report.total_records, 3)
        self.assertIn("required_fields", report.summary()["violations_by_rule"])
        self.assertIn("duplicate_detection", report.summary()["violations_by_rule"])

    def test_valid_records_excludes_failing_rows(self):
        engine = ValidationEngine([RequiredFieldsRule(["id"])])
        passing, report = engine.valid_records([{"id": "1"}, {}])
        self.assertEqual(passing, [{"id": "1"}])
        self.assertEqual(len(report.violations), 1)


if __name__ == "__main__":
    unittest.main()
