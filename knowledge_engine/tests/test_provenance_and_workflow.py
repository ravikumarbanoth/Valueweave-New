import tempfile
import unittest
from datetime import date
from pathlib import Path

from knowledge_engine.collectors.csv_collector import CSVCollector
from knowledge_engine.core.provenance import ProvenanceRecord
from knowledge_engine.core.types import VerificationStatus
from knowledge_engine.parsers.csv_parser import CSVParser
from knowledge_engine.provenance.tracker import ProvenanceTracker
from knowledge_engine.update_engine.states import WorkflowState
from knowledge_engine.update_engine.workflow import UpdateWorkflow, WorkflowStateError
from knowledge_engine.validation.engine import ValidationEngine
from knowledge_engine.validation.rules import RequiredFieldsRule


class ProvenanceRecordTest(unittest.TestCase):
    def test_defaults_last_verified_to_collection_date(self):
        record = ProvenanceRecord(
            source="Gov Source", source_url=["https://a.gov.in"], collection_date=date(2026, 1, 1),
            collector="test/0.1.0", confidence=75,
        )
        self.assertEqual(record.last_verified, date(2026, 1, 1))
        self.assertEqual(record.verification_status, VerificationStatus.NEEDS_REVIEW)

    def test_empty_source_url_raises(self):
        with self.assertRaises(ValueError):
            ProvenanceRecord(source="x", source_url=[], collection_date=date.today(), collector="c", confidence=50)

    def test_confidence_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            ProvenanceRecord(source="x", source_url=["https://a.com"], collection_date=date.today(), collector="c", confidence=150)

    def test_to_csv_fields_joins_multiple_urls(self):
        record = ProvenanceRecord(
            source="x", source_url=["https://a.gov.in", "https://b.gov.in"],
            collection_date=date(2026, 1, 1), collector="c", confidence=70,
        )
        fields = record.to_csv_fields()
        self.assertEqual(fields["source_url"], "https://a.gov.in; https://b.gov.in")

    def test_round_trip_to_dict_from_dict(self):
        record = ProvenanceRecord(
            source="x", source_url=["https://a.gov.in"], collection_date=date(2026, 1, 1),
            collector="c", confidence=70, package_version="1.0.0",
        )
        restored = ProvenanceRecord.from_dict(record.to_dict())
        self.assertEqual(restored, record)

    def test_re_verify_raises_if_confidence_lowered(self):
        record = ProvenanceRecord(source="x", source_url=["https://a.com"], collection_date=date.today(), collector="c", confidence=70)
        with self.assertRaises(ValueError):
            record.re_verify(new_confidence=60)

    def test_re_verify_raises_if_increase_exceeds_8(self):
        record = ProvenanceRecord(source="x", source_url=["https://a.com"], collection_date=date.today(), collector="c", confidence=70)
        with self.assertRaises(ValueError):
            record.re_verify(new_confidence=80)

    def test_re_verify_allows_increase_up_to_8(self):
        record = ProvenanceRecord(source="x", source_url=["https://a.com"], collection_date=date.today(), collector="c", confidence=70)
        record.re_verify(new_confidence=78)
        self.assertEqual(record.confidence, 78)


class ProvenanceTrackerTest(unittest.TestCase):
    def test_attach_uniform_merges_fields(self):
        records = [{"id": "1"}, {"id": "2"}]
        provenance = ProvenanceTracker.default_provenance(
            source="Gov Source", source_url="https://a.gov.in", confidence=75, collector="test/0.1.0",
        )
        result = ProvenanceTracker.attach_uniform(records, provenance)
        self.assertEqual(result[0]["data_source"], "Gov Source")
        self.assertEqual(result[0]["verification_status"], "VST-NEEDS_REVIEW")

    def test_mark_pending_verification_formats_notes(self):
        record = {"id": "1", "minimum_investment": "500000", "notes": ""}
        updated = ProvenanceTracker.mark_pending_verification(record, "minimum_investment", "no source found")
        self.assertEqual(updated["minimum_investment"], "PENDING_VERIFICATION")
        self.assertEqual(updated["notes"], "[minimum_investment]: no source found")

    def test_mark_pending_verification_appends_to_existing_notes(self):
        record = {"id": "1", "field_a": "x", "notes": "existing note"}
        updated = ProvenanceTracker.mark_pending_verification(record, "field_a", "reason")
        self.assertEqual(updated["notes"], "existing note | [field_a]: reason")

    def test_find_sentinel_violations_detects_appended_text(self):
        records = [
            {"id": "1", "field": "PENDING_VERIFICATION"},
            {"id": "2", "field": "PENDING_VERIFICATION - some explanation"},
        ]
        violations = ProvenanceTracker.find_sentinel_violations(records)
        self.assertEqual(violations, [(1, "field", "PENDING_VERIFICATION - some explanation")])


class UpdateWorkflowTest(unittest.TestCase):
    def _make_workflow(self, csv_content: str, tmp_dir: str) -> UpdateWorkflow:
        path = Path(tmp_dir) / "data.csv"
        path.write_text(csv_content, encoding="utf-8")
        engine = ValidationEngine([RequiredFieldsRule(["id", "name"])])
        return UpdateWorkflow(
            name="test_workflow", collector=CSVCollector(), source=str(path),
            parser=CSVParser(), validation_engine=engine,
        )

    def test_happy_path_reaches_pending_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            database = {}
            state = workflow.run_to_approval(database)
            self.assertEqual(state, WorkflowState.PENDING_HUMAN_APPROVAL)
            self.assertEqual(database, {"1": {"id": "1", "name": "Alpha"}})

    def test_approve_transitions_to_stable_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            workflow.run_to_approval({})
            workflow.approve("reviewer", "looks good")
            self.assertEqual(workflow.state, WorkflowState.STABLE_RELEASE)

    def test_reject_transitions_to_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            workflow.run_to_approval({})
            workflow.reject("reviewer", "insufficient sourcing")
            self.assertEqual(workflow.state, WorkflowState.REJECTED)

    def test_approve_outside_pending_state_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            with self.assertRaises(WorkflowStateError):
                workflow.approve("reviewer")

    def test_no_changes_detected_short_circuits(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            previous = [{"id": "1", "name": "Alpha"}]
            state = workflow.run_to_approval({}, previous_records=previous)
            self.assertEqual(state, WorkflowState.NO_CHANGES_DETECTED)

    def test_collector_failure_transitions_to_failed(self):
        engine = ValidationEngine([])
        workflow = UpdateWorkflow(
            name="broken", collector=CSVCollector(), source="/nonexistent/file.csv",
            parser=CSVParser(), validation_engine=engine,
        )
        state = workflow.run_to_approval({})
        self.assertEqual(state, WorkflowState.FAILED)
        self.assertIsNotNone(workflow.error)

    def test_failing_records_excluded_from_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            # second row is missing 'name', which RequiredFieldsRule requires
            workflow = self._make_workflow("id,name\n1,Alpha\n2,\n", tmp)
            database = {}
            workflow.run_to_approval(database)
            self.assertEqual(list(database.keys()), ["1"])

    def test_history_records_every_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = self._make_workflow("id,name\n1,Alpha\n", tmp)
            workflow.run_to_approval({})
            states = [t["state"] for t in workflow.history_summary()]
            self.assertEqual(
                states,
                ["CHECKING_SOURCE", "DETECTING_CHANGES", "VALIDATING", "UPDATING_DATABASE",
                 "GENERATING_DRAFT", "PENDING_HUMAN_APPROVAL"],
            )


if __name__ == "__main__":
    unittest.main()
