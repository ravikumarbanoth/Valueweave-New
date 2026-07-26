#!/usr/bin/env python3
"""Work Package 6 — Stewardship workflow tests.

The transition rules are the product here, so most of these test refusals rather
than successes. A workflow that permits an illegal transition has recorded a
decision nobody made, which is worse than a workflow that does nothing.

Every test that writes uses a temporary ledger. The repository's real
`review_ledger.csv` stays empty, because inventing steward decisions to make a
test suite look busy would be exactly the fabrication this platform forbids.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stewardship.ledger import ReviewLedger                                  # noqa: E402
from stewardship.lifecycle import (LifecycleState, TRANSITIONS,              # noqa: E402
                                   TransitionError, VERIFIED_STATUS,
                                   allowed_from, check_transition,
                                   effective_state)
from stewardship.store import StewardshipStore                               # noqa: E402


class SpecificationAgreementTest(unittest.TestCase):
    """The lifecycle module claims to implement governance/DATA_STEWARDSHIP.md.
    This checks the claim instead of trusting the docstring."""

    def test_the_seven_states_match_the_governance_document(self):
        text = (ROOT / "governance" / "DATA_STEWARDSHIP.md").read_text()
        for state in LifecycleState:
            with self.subTest(state=state.value):
                self.assertIn(state.value, text)

    def test_graph_validator_registers_the_same_states(self):
        text = (ROOT / "knowledge_graph" / "validate_graph.py").read_text()
        for state in LifecycleState:
            self.assertIn(f'"{state.value}"', text)


class TransitionRuleTest(unittest.TestCase):
    def test_happy_path_is_permitted(self):
        for t in TRANSITIONS:
            with self.subTest(f"{t.source.value}->{t.target.value}"):
                check_transition(t.source, t.target, actor="steward")

    def test_backward_transitions_are_refused(self):
        for src, dst in [("PUBLISHED", "DRAFT"), ("APPROVED", "VALIDATED"),
                         ("ARCHIVED", "PUBLISHED"), ("REVIEWED", "COLLECTED")]:
            with self.subTest(f"{src}->{dst}"):
                with self.assertRaises(TransitionError) as ctx:
                    check_transition(src, dst, actor="steward")
                self.assertIn("backwards", str(ctx.exception))

    def test_skipping_a_state_is_refused(self):
        with self.assertRaises(TransitionError) as ctx:
            check_transition("VALIDATED", "APPROVED", actor="steward")
        self.assertIn("skips a state", str(ctx.exception))

    def test_review_requires_a_named_actor(self):
        with self.assertRaises(TransitionError) as ctx:
            check_transition("VALIDATED", "REVIEWED")
        self.assertIn("named actor", str(ctx.exception))

    def test_a_machine_may_not_approve(self):
        with self.assertRaises(TransitionError) as ctx:
            check_transition("REVIEWED", "APPROVED", actor="bot", by_machine=True)
        self.assertIn("may not be performed by a machine", str(ctx.exception))

    def test_a_machine_may_collect_and_validate(self):
        check_transition("DRAFT", "COLLECTED", by_machine=True)
        check_transition("COLLECTED", "VALIDATED", by_machine=True)

    def test_self_transition_is_not_a_transition(self):
        with self.assertRaises(TransitionError):
            check_transition("PUBLISHED", "PUBLISHED", actor="steward")

    def test_unknown_state_raises(self):
        with self.assertRaises(ValueError):
            LifecycleState.parse("SORT_OF_DONE")


class RetroactiveReviewTest(unittest.TestCase):
    """All 647 entities are PUBLISHED and none were reviewed. Without this path
    the platform can never leave 0% verified."""

    def test_published_may_be_reviewed_when_not_yet_verified(self):
        t = check_transition("PUBLISHED", "REVIEWED", actor="steward")
        self.assertIn("Retroactive review", t.requirement)

    def test_published_may_not_be_reviewed_once_verified(self):
        with self.assertRaises(TransitionError) as ctx:
            check_transition("PUBLISHED", "REVIEWED", actor="steward",
                             verification_status=VERIFIED_STATUS)
        self.assertIn("genuine rewind", str(ctx.exception))

    def test_it_still_requires_an_actor(self):
        with self.assertRaises(TransitionError):
            check_transition("PUBLISHED", "REVIEWED")

    def test_it_is_not_machine_permitted(self):
        with self.assertRaises(TransitionError):
            check_transition("PUBLISHED", "REVIEWED", actor="bot", by_machine=True)


class EffectiveStateTest(unittest.TestCase):
    def test_published_but_unverified_reports_the_gap(self):
        _state, gap = effective_state("PUBLISHED", "VST-NEEDS_REVIEW")
        self.assertIsNotNone(gap)
        self.assertIn("without human review", gap)

    def test_no_gap_once_verified(self):
        _state, gap = effective_state("APPROVED", VERIFIED_STATUS)
        self.assertIsNone(gap)

    def test_verified_but_only_collected_is_also_a_gap(self):
        _state, gap = effective_state("COLLECTED", VERIFIED_STATUS)
        self.assertIsNotNone(gap)


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = ReviewLedger(path=Path(self.tmp.name) / "ledger.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def test_illegal_transitions_never_reach_the_ledger(self):
        with self.assertRaises(TransitionError):
            self.ledger.record("vw:crop:turmeric", "PUBLISHED", "DRAFT", actor="s")
        self.assertEqual(self.ledger.entries, [])

    def test_approval_sets_the_verification_status(self):
        self.ledger.record("vw:crop:turmeric", "PUBLISHED", "REVIEWED", actor="s")
        entry = self.ledger.record("vw:crop:turmeric", "REVIEWED", "APPROVED", actor="s")
        self.assertEqual(entry.verification_status_after, VERIFIED_STATUS)

    def test_review_alone_does_not_verify(self):
        entry = self.ledger.record("vw:crop:turmeric", "PUBLISHED", "REVIEWED", actor="s")
        self.assertEqual(entry.verification_status_after, "")

    def test_state_is_replayed_not_stored(self):
        self.ledger.record("vw:crop:turmeric", "PUBLISHED", "REVIEWED", actor="s")
        self.ledger.record("vw:crop:turmeric", "REVIEWED", "APPROVED", actor="s")
        self.assertEqual(self.ledger.current_state("vw:crop:turmeric"),
                         LifecycleState.APPROVED)
        self.assertEqual(len(self.ledger.for_entity("vw:crop:turmeric")), 2,
                         "history must survive the second transition")

    def test_round_trips_through_disk(self):
        self.ledger.record("vw:crop:turmeric", "PUBLISHED", "REVIEWED",
                           actor="r.banoth", evidence="checked against source")
        path = self.ledger.flush()
        reloaded = ReviewLedger(path=path)
        self.assertEqual(len(reloaded.entries), 1)
        self.assertEqual(reloaded.entries[0].actor, "r.banoth")
        self.assertEqual(reloaded.current_state("vw:crop:turmeric"),
                         LifecycleState.REVIEWED)

    def test_unknown_entity_defaults_to_published(self):
        self.assertEqual(self.ledger.current_state("vw:crop:nothing"),
                         LifecycleState.PUBLISHED)


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = ReviewLedger(path=Path(self.tmp.name) / "ledger.csv")
        self.store = StewardshipStore(ledger=self.ledger)

    def tearDown(self):
        self.tmp.cleanup()

    def test_queue_is_ordered_by_leverage(self):
        rows = self.store.queue(limit=20)
        degrees = [r["degree"] for r in rows]
        self.assertEqual(degrees, sorted(degrees, reverse=True))

    def test_queue_reports_cumulative_coverage(self):
        rows = self.store.queue(limit=40)
        self.assertGreater(rows[-1]["cumulative_coverage_pct"], 0)
        pcts = [r["cumulative_coverage_pct"] for r in rows]
        self.assertEqual(pcts, sorted(pcts))

    def test_approved_entities_leave_the_queue(self):
        gid = self.store.queue(limit=1)[0]["entity_id"]
        self.ledger.record(gid, "PUBLISHED", "REVIEWED", actor="s")
        self.ledger.record(gid, "REVIEWED", "APPROVED", actor="s")
        self.assertNotIn(gid, {r["entity_id"] for r in self.store.queue(limit=None)})

    def test_summary_counts_reconcile(self):
        s = self.store.summary()
        self.assertEqual(s["verified"] + s["awaiting_review"], s["entities"])

    def test_apply_is_a_dry_run_by_default(self):
        gid = "vw:crop:turmeric"
        self.ledger.record(gid, "PUBLISHED", "REVIEWED", actor="s")
        self.ledger.record(gid, "REVIEWED", "APPROVED", actor="s")
        before = (ROOT / "packages" / "Package005_Agriculture"
                  / "datasets" / "crops.csv").read_text()
        report = self.store.apply_approvals()
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["rows_updated"], 1)
        after = (ROOT / "packages" / "Package005_Agriculture"
                 / "datasets" / "crops.csv").read_text()
        self.assertEqual(before, after, "a dry run must not touch a package")

    def test_apply_locates_the_exact_package_row(self):
        gid = "vw:crop:turmeric"
        self.ledger.record(gid, "PUBLISHED", "REVIEWED", actor="s")
        self.ledger.record(gid, "REVIEWED", "APPROVED", actor="s")
        report = self.store.apply_approvals()
        self.assertEqual(report["unlocatable"], [])
        self.assertEqual(report["written"][0]["dataset"],
                         "packages/Package005_Agriculture/datasets/crops.csv")

    def test_nothing_is_approved_without_a_ledger_entry(self):
        self.assertEqual(self.store.apply_approvals()["approved_entities"], 0)


class RealLedgerTest(unittest.TestCase):
    def test_the_committed_ledger_records_no_invented_reviews(self):
        path = ROOT / "stewardship" / "review_ledger.csv"
        self.assertTrue(path.exists(), "the ledger file must exist, even when empty")
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows, [],
                         "no steward has reviewed anything; the ledger must not pretend "
                         "otherwise")


if __name__ == "__main__":
    unittest.main(verbosity=2)
