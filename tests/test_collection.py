#!/usr/bin/env python3
"""
Automated collection — the framework, not the feeds.

WHAT THIS MILESTONE ACTUALLY CHANGED
-------------------------------------
Most of the machinery already existed and had never been called. The Knowledge
Engine's collectors and parsers shipped in Platform v2.2 with 117 tests and its
own README saying so plainly: "no source has yet been collected by this
engine." The stewardship lifecycle and its append-only ledger shipped in v2.2
as well, and `stewardship/review_ledger.csv` still holds only a header row.

So these tests are about the spine that connects them — registry, conditional
fetch, per-item change detection, rule classification, deduplication, the
review queue, the backlog and the monitor — and about the four rules that make
the whole thing safe to run unattended:

    1  nothing publishes. No path from a feed to packages/, to the graph or to
       Supabase exists in this package.
    2  nothing is invented. Every classification carries the words that fired;
       every alias, gap and duplicate is traceable to something a source said.
    3  a URL nobody has proved reachable is PENDING_VERIFICATION and is never
       fetched on a schedule.
    4  an unchanged feed costs one request with no body.

Rule 4 is tested against a real HTTP server, because it is the claim the whole
"don't download everything every day" objective rests on and it cannot be
tested by asserting on source.

    python3 tests/run_all.py --suite collection
"""

import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collection import backlog, classify, dedupe, detect, monitor, registry, review, runner  # noqa: E402

FIXTURES = ROOT / "collection" / "fixtures"


def fixture_source(**overrides):
    base = dict(
        source_id="t-rss", name="test", category="Testing", state="TG", country="IN",
        url=str(FIXTURES / "scheme_notifications.rss"), source_type="RSS",
        collector="knowledge_engine.collectors.rss_collector.RSSCollector",
        parser="knowledge_engine.parsers.rss_parser.RSSParser",
        frequency="DAILY", reliability=50, status="ACTIVE", tags=["test"],
        item_key="guid", classify_as="", notes="",
    )
    base.update(overrides)
    return registry.Source(**base)


# ═══════════════════════════════ 1. the registry
class RegistryTest(unittest.TestCase):

    def setUp(self):
        self.sources = registry.load()

    def test_it_loads_and_every_row_validates(self):
        self.assertGreater(len(self.sources), 0)

    def test_the_shipped_registry_covers_every_source_type_it_claims_to_support(self):
        """A framework that supports six formats and exercises one is a
        framework that supports one. Each of these has a working local fixture
        and is run by `collection.cli run`."""
        types = {s.source_type for s in self.sources if s.category == "Testing"}
        self.assertEqual(types, {"RSS", "ATOM", "JSON_FEED", "CSV"})

    def test_every_collector_and_parser_named_is_importable(self):
        """The registry names classes as strings so adding a source is a data
        change. A typo must fail at load, not three stages later."""
        for source in self.sources:
            with self.subTest(source=source.source_id):
                self.assertTrue(callable(registry.resolve(source.collector)))
                self.assertTrue(callable(registry.resolve(source.parser)))

    def test_the_declared_type_agrees_with_the_parser(self):
        expected = {
            "RSS": "RSSParser", "ATOM": "RSSParser", "JSON_FEED": "JSONParser",
            "XML": "XMLParser", "REST_API": "JSONParser", "CSV": "CSVParser",
            "DATASET": "CSVParser",
        }
        for source in self.sources:
            with self.subTest(source=source.source_id):
                self.assertTrue(source.parser.endswith(expected[source.source_type]),
                                f"{source.source_type} routed to {source.parser}")

    def test_an_unverified_source_is_never_run_on_a_schedule(self):
        """The rule that keeps a dashboard honest: a URL somebody typed is not
        a URL somebody checked."""
        for source in self.sources:
            if source.status == "PENDING_VERIFICATION":
                with self.subTest(source=source.source_id):
                    self.assertFalse(source.runnable)
                    self.assertFalse(source.due())

    def test_a_bad_row_is_an_error_and_not_a_silent_skip(self):
        """A source dropped for a typo is a source nobody notices stopped
        being monitored."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text(
                ",".join(registry.FIELDS) + "\n"
                "x,Name,NotACategory,TG,IN,http://e.invalid,RSS,a.B,c.D,DAILY,50,ACTIVE,,guid,,\n",
                encoding="utf-8")
            with self.assertRaises(registry.RegistryError):
                registry.load(registry_path=path, state_path=Path(tmp) / "none.json")

    def test_configuration_and_state_are_different_files(self):
        """Every scheduled run writes state. If it wrote to the CSV a human
        authored, the diff that should show "someone added a source" would show
        forty timestamps with one real edit hidden among them."""
        text = registry.REGISTRY_PATH.read_text(encoding="utf-8")
        for state_field in ("last_checked", "last_ok", "etag", "content_hash"):
            with self.subTest(field=state_field):
                self.assertNotIn(state_field, text)


# ═══════════════════════════════ 2. change detection
class ChangeDetectionTest(unittest.TestCase):

    RECORDS = [{"guid": "a", "title": "One"}, {"guid": "b", "title": "Two"}]

    def test_everything_is_new_the_first_time(self):
        changes = detect.detect("s", self.RECORDS, {}, key_field="guid")
        self.assertEqual(changes.summary["new"], 2)

    def test_nothing_is_new_the_second_time(self):
        first = detect.detect("s", self.RECORDS, {}, key_field="guid")
        hashes = detect.next_hashes({}, first)
        second = detect.detect("s", self.RECORDS, hashes, key_field="guid")
        self.assertEqual(second.summary, {"source_id": "s", "not_modified": False,
                                          "payload_changed": True, "new": 0,
                                          "updated": 0, "unchanged": 2, "disappeared": 0})

    def test_an_edited_record_is_an_update_and_not_a_new_one(self):
        hashes = detect.next_hashes({}, detect.detect("s", self.RECORDS, {}, key_field="guid"))
        edited = [{"guid": "a", "title": "One (amended)"}, self.RECORDS[1]]
        changes = detect.detect("s", edited, hashes, key_field="guid")
        self.assertEqual(changes.summary["updated"], 1)
        self.assertEqual(changes.summary["new"], 0)

    def test_a_feed_that_only_restamps_itself_reports_no_change(self):
        """The failure this is built against: a <lastBuildDate> that ticks
        hourly makes the payload hash differ on every fetch while the items are
        identical. Hashing the payload alone would queue everything, hourly."""
        with_stamp = [dict(r, lastBuildDate="Mon, 03 Aug 2026 04:00:00 +0000")
                      for r in self.RECORDS]
        later = [dict(r, lastBuildDate="Mon, 03 Aug 2026 05:00:00 +0000")
                 for r in self.RECORDS]
        hashes = detect.next_hashes({}, detect.detect("s", with_stamp, {}, key_field="guid"))
        changes = detect.detect("s", later, hashes, key_field="guid")
        self.assertEqual(changes.summary["unchanged"], 2)
        self.assertEqual(changes.actionable, [])

    def test_an_item_falling_off_the_window_is_not_a_delete(self):
        """A news feed holds twenty items and drops the twenty-first. That item
        did not stop being true."""
        hashes = detect.next_hashes({}, detect.detect("s", self.RECORDS, {}, key_field="guid"))
        changes = detect.detect("s", [self.RECORDS[0]], hashes, key_field="guid")
        self.assertEqual(changes.summary["disappeared"], 1)
        self.assertEqual(changes.actionable, [])
        self.assertIn("b", detect.next_hashes(hashes, changes),
                      "a returning item must be recognised, not offered again as new")

    def test_a_hash_is_stable_across_processes(self):
        """Python's built-in hash is salted per process; a state file written by
        one run would disagree with the next for no debuggable reason."""
        script = ("import sys; sys.path.insert(0, %r);"
                  "from collection.detect import item_hash;"
                  "print(item_hash({'guid': 'a', 'title': 'One'}))" % str(ROOT))
        out = [subprocess.run([sys.executable, "-c", script], capture_output=True,
                              text=True, timeout=60).stdout.strip() for _ in range(2)]
        self.assertEqual(out[0], out[1])
        self.assertEqual(out[0], detect.item_hash({"guid": "a", "title": "One"}))


# ═══════════════════════════════ 3. conditional fetch, against a real server
@unittest.skipIf(shutil.which("python3") is None, "python3 required")
class ConditionalFetchTest(unittest.TestCase):
    """The claim the whole objective rests on, tested over HTTP.

    Not against a live government feed: this sandbox cannot reach one, and even
    with a network you cannot ask a real server to change on command — which is
    the other half of what needs testing.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "scripts" / "dev"))
        import fake_feed_server                                     # noqa: PLC0415
        cls.module = fake_feed_server
        cls.server = fake_feed_server.serve(port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def url(self, name):
        return f"http://127.0.0.1:{self.port}/{name}"

    def test_the_first_fetch_returns_a_body_and_validators(self):
        source = fixture_source(url=self.url("scheme_notifications.rss"))
        run, candidates, state = runner.run_source(source)
        self.assertEqual(run.status, "ok")
        self.assertEqual(run.http_status, 200)
        self.assertEqual(run.records, 4)
        self.assertTrue(state.etag, "the server sent an ETag and it was not stored")
        self.assertTrue(state.last_modified)

    def test_an_unchanged_feed_costs_one_request_with_no_body(self):
        source = fixture_source(url=self.url("skill_council.atom"), item_key="id")
        _run, _candidates, state = runner.run_source(source)
        source.fetch = state

        run, candidates, _ = runner.run_source(source)
        self.assertEqual(run.status, "not_modified")
        self.assertEqual(run.http_status, 304)
        self.assertEqual(candidates, [], "a 304 must not queue anything")

    def test_a_changed_feed_is_fetched_again_and_only_the_changed_item_is_queued(self):
        name = "district_industries.jsonfeed"
        source = fixture_source(
            url=self.url(name), item_key="id", source_type="JSON_FEED",
            collector="knowledge_engine.collectors.json_collector.JSONCollector",
            parser="knowledge_engine.parsers.json_parser.JSONParser")
        _run, first, state = runner.run_source(source)
        self.assertEqual(len(first), 3)
        source.fetch = state

        import urllib.request                                        # noqa: PLC0415
        urllib.request.urlopen(f"http://127.0.0.1:{self.port}/_mutate?path=/{name}",
                               timeout=10).read()

        run, candidates, _ = runner.run_source(source)
        self.assertEqual(run.status, "ok", "a changed feed must not report 304")
        self.assertEqual(run.changes["updated"], 1)
        self.assertEqual(run.changes["new"], 0)
        self.assertEqual(len(candidates), 1,
                         "only the item that changed belongs in the queue")

    def test_a_dead_url_is_an_error_and_not_a_crash(self):
        source = fixture_source(url=self.url("nothing-here.rss"))
        run, candidates, state = runner.run_source(source)
        self.assertEqual(run.status, "error")
        self.assertEqual(candidates, [])
        self.assertIsNone(state)


# ═══════════════════════════════ 4. classification
class ClassificationTest(unittest.TestCase):

    def test_every_target_is_a_real_entity_type_or_an_explicit_non_entity(self):
        """A category nothing downstream can use is a category that produces
        candidates nobody can approve."""
        for rule in classify.RULES:
            with self.subTest(target=rule.target):
                self.assertIn(rule.target, classify.TARGETS)

    def test_entity_targets_exist_in_the_knowledge_graph(self):
        import csv                                                   # noqa: PLC0415
        with open(ROOT / "knowledge_graph" / "entities" / "entities.csv",
                  encoding="utf-8", newline="") as fh:
            live = {row["entity_type"] for row in csv.DictReader(fh)}
        missing = sorted(classify.ENTITY_TARGETS - live)
        self.assertEqual(missing, [], f"classifies into types the graph lacks: {missing}")

    def test_no_two_rules_share_a_weight(self):
        """Equal weights resolve alphabetically, which is arbitrary dressed as
        a decision — "Common facility centre for millet processing" came out as
        Crop over Machinery because C sorts before M."""
        weights = [r.weight for r in classify.RULES]
        self.assertEqual(len(weights), len(set(weights)), sorted(weights))

    def test_a_classification_always_says_why(self):
        result = classify.classify({"title": "New subsidy scheme for micro enterprises"})
        self.assertEqual(result.target, "GovernmentScheme")
        self.assertTrue(result.matched)
        self.assertIn("subsidy", result.reason)

    def test_unclassified_is_a_legitimate_answer(self):
        result = classify.classify({"title": "Monthly bulletin"})
        self.assertEqual(result.target, classify.UNCLASSIFIED)
        self.assertTrue(result.reason)

    def test_the_registry_can_declare_the_type_outright(self):
        """A register of training providers is a list of training providers.
        Making the classifier re-derive that from prose it does not contain
        would be guessing where the source already told us."""
        result = classify.classify({"provider_name": "Government ITI"},
                                   forced="TrainingProvider")
        self.assertEqual(result.target, "TrainingProvider")
        self.assertIn("declared in the registry", result.reason)

    def test_the_fixtures_classify_the_way_a_person_would(self):
        """Regression on the four corrections the first run against the
        fixtures forced: empanelment, licence, nsqf and the Crop/Machinery
        tie."""
        cases = [
            ("Margin Money Subsidy Scheme for micro enterprises", "GovernmentScheme"),
            ("Skill training centre empanelment for ITI graduates", "TrainingProvider"),
            ("Solar rooftop installation opportunity for licensed contractors",
             "BusinessOpportunity"),
            ("New qualification pack for drone maintenance technician", "Certification"),
            ("Common facility centre for millet processing announced", "Machinery"),
        ]
        for title, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(classify.classify({"title": title}).target, expected)


# ═══════════════════════════════ 5. deduplication
class DedupeTest(unittest.TestCase):

    def test_a_republished_notification_is_caught(self):
        items = [("a", {"title": "Margin Money Subsidy Scheme — Notification 41/2026"}),
                 ("b", {"title": "Margin Money Subsidy Scheme — Notification 87/2026"})]
        result = dedupe.dedupe(items)
        self.assertEqual(result.duplicate_of.get("b"), "a")

    def test_two_genuinely_different_schemes_are_not_merged(self):
        """The failure mode a collection pipeline must not have. At a 0.6
        threshold these merge, and they are two schemes."""
        items = [("a", {"title": "Margin Money Subsidy for micro enterprises"}),
                 ("b", {"title": "Interest Subvention for small and medium exporters"})]
        self.assertEqual(dedupe.dedupe(items).duplicate_of, {})

    def test_an_amendment_is_a_version_and_not_a_duplicate(self):
        """The single most important thing a collection pipeline can catch."""
        items = [("a", {"title": "Solar rooftop installation subsidy guidelines"}),
                 ("b", {"title": "Solar rooftop installation subsidy guidelines — corrigendum"})]
        result = dedupe.dedupe(items)
        self.assertIn("b", result.versions)
        self.assertNotIn("b", result.duplicate_of)

    def test_it_also_compares_against_what_we_already_hold(self):
        """The same notification arriving from two sources on two days is not
        visible inside one feed."""
        known = {"old": "Battery recycling collection centre licences invited"}
        items = [("new", {"title": "Battery recycling collection centre licences invited"})]
        self.assertEqual(dedupe.dedupe(items, known_titles=known).duplicate_of["new"], "old")

    def test_a_short_title_cannot_clear_the_threshold_by_accident(self):
        items = [("a", {"title": "Notice 12"}), ("b", {"title": "Notice 44"})]
        self.assertEqual(dedupe.dedupe(items).duplicate_of, {})

    def test_nothing_is_deleted(self):
        """It groups and marks. A "duplicate" that was a second, genuinely
        different scheme would otherwise be lost silently."""
        title = "Battery recycling collection centre licences invited"
        items = [("a", {"title": title}), ("b", {"title": title})]
        result = dedupe.dedupe(items)
        self.assertEqual(result.groups[0].size, 2)
        self.assertEqual(result.groups[0].primary_key, "a")


# ═══════════════════════════════ 6. the review queue
class ReviewQueueTest(unittest.TestCase):

    def candidate(self, **kw):
        base = dict(candidate_id="s:1", source_id="s", source_name="S", item_key="1",
                    title="T", url="u", published_at="", change="NEW",
                    classified_as="GovernmentScheme", classified_reason="matched “scheme”",
                    is_entity=True)
        base.update(kw)
        return review.Candidate(**base)

    def test_nothing_in_this_package_can_approve(self):
        """`APPROVED is the only state a machine may not enter` —
        stewardship/lifecycle.py. This asserts the collection layer honours it."""
        for module in (review, runner, registry, monitor, backlog):
            source = Path(module.__file__).read_text(encoding="utf-8")
            with self.subTest(module=module.__name__):
                self.assertNotIn("LifecycleState.APPROVED", source)
                self.assertNotIn("= APPROVED", source.replace("REJECTED = ", "")
                                 .replace("APPROVED = \"APPROVED\"", ""))

    def test_only_one_module_may_write_to_a_package(self):
        """The boundary moved when promotion was added, so state where it is.

        `decide.py` writes to `packages/` and that is the whole feature — but it
        is the ONLY module that may, it only does so under `--write`, and only
        for a candidate the ledger already records as APPROVED. Nothing else in
        `collection/` touches a package, and nothing at all touches the graph or
        Supabase: the graph is rebuilt by its own builder and the sync is a
        separate command on a separate trigger.
        """
        forbidden = ("packages/", "knowledge_graph/", "supabase", "kg_entities")
        for path in sorted((ROOT / "collection").glob("*.py")):
            body = path.read_text(encoding="utf-8")
            lines = [line.split("#", 1)[0] for line in body.splitlines()]
            # `cli.py` PRINTS `python3 knowledge_graph/build_graph.py` as the
            # operator's next step. Naming a command is not running one, and
            # the test below is what holds that line honest — it asserts the
            # CLI has no subprocess, os.system or check_call anywhere.
            if path.name == "cli.py":
                lines = [line for line in lines if "print(" not in line]
            code = "\n".join(lines)
            # Docstrings are prose about the boundary; only code is checked.
            parts = code.split('"""')
            code = "".join(parts[i] for i in range(0, len(parts), 2))
            allowed = {"packages/"} if path.name == "decide.py" else set()
            for token in forbidden:
                if token in allowed:
                    continue
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, code)

    def test_the_cli_only_names_the_graph_builder_it_never_runs_it(self):
        """`promote --write` prints the rebuild command rather than running it.
        Rebuilding the graph is a separate, reviewable act, and a command that
        silently regenerated 648 entities as a side effect of writing one row
        would bury that row in a diff nobody could read."""
        code = (ROOT / "collection" / "cli.py").read_text(encoding="utf-8")
        self.assertIn("print(\"      python3 knowledge_graph/build_graph.py\")", code)
        for runner_call in ("subprocess", "os.system", "check_call"):
            with self.subTest(call=runner_call):
                self.assertNotIn(runner_call, code)

    def test_a_decided_candidate_is_not_offered_again(self):
        """A queue that re-presents decided material trains the people reading
        it to skim."""
        existing = [self.candidate(state=review.APPROVED)]
        merged, stats = review.merge(existing, [self.candidate()])
        self.assertEqual(merged[0].state, review.APPROVED)
        self.assertEqual(stats["kept_decided"], 1)

    def test_an_updated_item_reopens_a_decided_candidate(self):
        """The thing that was approved is not the thing that is there now."""
        existing = [self.candidate(state=review.APPROVED)]
        merged, stats = review.merge(existing, [self.candidate(change="UPDATED")])
        self.assertEqual(merged[0].state, review.NEEDS_REVIEW)
        self.assertEqual(stats["reopened"], 1)

    def test_a_duplicate_never_reaches_a_reviewer(self):
        candidates = [self.candidate(state=review.DUPLICATE, duplicate_of="s:0")]
        self.assertEqual(review.to_needs_review(candidates), 0)
        self.assertEqual(candidates[0].state, review.DUPLICATE)

    def test_the_raw_record_survives_to_the_point_of_approval(self):
        """A reviewer must see what the source actually said, not a summary."""
        candidate = self.candidate(raw={"title": "T", "description": "D"})
        restored = json.loads(candidate.to_json())
        self.assertEqual(restored["raw"], {"title": "T", "description": "D"})


# ═══════════════════════════════ 7. the research backlog
class BacklogTest(unittest.TestCase):

    EVENTS = ([{"query": "lift technician", "results_count": 0,
                "created_at": f"2026-08-0{d}T10:00:00Z"} for d in (1, 2, 3)]
              + [{"query": "electrician", "results_count": 11,
                  "created_at": "2026-08-01T10:00:00Z"}] * 9
              + [{"query": "drone repair", "results_count": 0,
                  "created_at": "2026-08-01T10:00:00Z"}])

    def test_only_failures_become_suggestions(self):
        """A term that returns results is not a gap, however popular."""
        terms = {s.term for s in backlog.build(search_events=self.EVENTS)}
        self.assertIn("lift technician", terms)
        self.assertNotIn("electrician", terms)

    def test_one_person_trying_spellings_is_not_a_gap(self):
        terms = {s.term for s in backlog.build(search_events=self.EVENTS)}
        self.assertNotIn("drone repair", terms, "below the floor and not requested")

    def test_a_request_counts_even_once(self):
        """Somebody asked in words. That cost them something."""
        suggestions = backlog.build(
            search_events=[],
            user_requests=[{"title": "Battery recycling", "description": "how to start",
                            "status": "pending", "created_at": "2026-08-01T10:00:00Z"}])
        self.assertEqual([s.term for s in suggestions], ["battery recycling"])
        self.assertEqual(suggestions[0].example_request, "how to start")

    def test_a_closed_suggestion_does_not_reopen_itself(self):
        done = backlog.Suggestion(term="lift technician", status="DONE", score=9)
        merged = backlog.merge([done], backlog.build(search_events=self.EVENTS))
        self.assertEqual(next(s.status for s in merged if s.term == "lift technician"), "DONE")

    def test_the_output_says_what_it_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = backlog.save(backlog.build(search_events=self.EVENTS),
                                Path(tmp) / "b.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("Gaps, not knowledge", payload["note"])

    def test_the_frontend_now_records_the_signal_this_reads(self):
        """`trackSearch` shipped with migration 004 and had ZERO callers. Every
        no-result search since launch was discarded at the moment it happened,
        and the admin page said so in its own copy."""
        source = (ROOT / "frontend" / "components" / "search" / "LiveSearch.jsx"
                  ).read_text(encoding="utf-8")
        self.assertIn("trackSearch", source)
        self.assertIn("resultsCount", source)


# ═══════════════════════════════ 8. monitoring
class MonitorTest(unittest.TestCase):

    def source(self, **fetch):
        s = fixture_source()
        s.fetch = registry.FetchState(**fetch)
        return s

    def test_a_dead_feed_is_critical(self):
        health = monitor.check([self.source(consecutive_failures=6,
                                            last_error="404", last_ok="2026-01-01T00:00:00+00:00")])
        self.assertEqual(health.status, "critical")
        self.assertEqual(health.findings[0].check, "dead_feed")

    def test_a_quiet_feed_and_a_dead_one_are_not_the_same_number(self):
        """Both produce zero new items. The difference is only visible in the
        source's state, which is why these metrics are about sources."""
        from datetime import datetime, timedelta, timezone           # noqa: PLC0415
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(hours=2)).isoformat()
        old = (now - timedelta(days=40)).isoformat()
        quiet = monitor.check([self.source(last_ok=recent, last_changed=recent)], now=now)
        stale = monitor.check([self.source(last_ok=old, last_changed=old)], now=now)
        self.assertEqual(quiet.status, "healthy")
        self.assertEqual(stale.status, "degraded")
        self.assertEqual(stale.findings[0].check, "stale")

    def test_freshness_for_a_source_never_fetched_is_unknown_not_stale(self):
        """A dashboard with an invented number is worse than one with a missing
        panel — knowledge_sync/metrics.py, and it applies with more force here."""
        health = monitor.check([self.source()])
        self.assertEqual(health.sources[0]["freshness"], monitor.UNKNOWN)

    def test_a_duplicate_spike_is_reported(self):
        last_run = {"sources": [{"source_id": "t-rss", "records": 20,
                                 "duplicates": {"duplicates": 18}}]}
        from datetime import datetime, timezone                      # noqa: PLC0415
        now = datetime.now(timezone.utc)
        health = monitor.check([self.source(last_ok=now.isoformat(),
                                            last_changed=now.isoformat())],
                               last_run=last_run, now=now)
        self.assertIn("duplicate_spike", [f.check for f in health.findings])

    def test_the_real_registry_reports_its_unverified_sources(self):
        health = monitor.check(registry.load())
        checks = {f.check for f in health.findings}
        self.assertIn("never_verified", checks)


# ═══════════════════════════════ 9. the run, end to end
class RunnerTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.queue = Path(self.tmp.name) / "queue.jsonl"
        self.state = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def sources(self):
        # The four local fixtures by id, not by category. `pypi-rss-001` is also
        # category Testing — it is a real feed kept PAUSED to prove the network
        # leg — and including it would make this assert on something that skips.
        return [s for s in registry.load(state_path=self.state)
                if s.source_id.startswith("fix-")]

    def test_a_full_pass_over_the_local_fixtures(self):
        report = runner.run(sources=self.sources(), force=True, write=True,
                            queue_path=self.queue, state_path=self.state)
        self.assertEqual([s.status for s in report.sources], ["ok"] * 4)
        self.assertEqual(report.queue["by_state"]["NEEDS_REVIEW"], 11)
        self.assertEqual(report.queue["by_state"]["DUPLICATE"], 1)

    def test_running_twice_queues_nothing_the_second_time(self):
        runner.run(sources=self.sources(), force=True, write=True,
                   queue_path=self.queue, state_path=self.state)
        second = runner.run(sources=self.sources(), force=True, write=True,
                            queue_path=self.queue, state_path=self.state)
        self.assertEqual(sum(s.queued for s in second.sources), 0)
        self.assertEqual(second.merged["added"], 0)

    def test_a_dry_run_writes_nothing(self):
        """A runner that wrote state on a dry run would make the second dry run
        see no changes and report a green pipeline that had done nothing."""
        runner.run(sources=self.sources(), force=True, write=False,
                   queue_path=self.queue, state_path=self.state)
        self.assertFalse(self.queue.exists())
        self.assertFalse(self.state.exists())

    def test_the_schedule_is_honoured_unless_forced(self):
        runner.run(sources=self.sources(), force=True, write=True,
                   queue_path=self.queue, state_path=self.state)
        again = runner.run(sources=self.sources(), force=False, write=False,
                           queue_path=self.queue, state_path=self.state)
        self.assertEqual(again.sources, [], "a daily source checked now is not due")


# ═══════════════════════════════ 10. the workflow that runs it
class ScheduledWorkflowTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            import yaml                                              # noqa: PLC0415
        except ImportError:                                          # pragma: no cover
            raise unittest.SkipTest("PyYAML — see requirements-dev.txt")
        cls.yaml = yaml
        cls.path = ROOT / ".github" / "workflows" / "knowledge-collect.yml"

    def workflow(self):
        return self.yaml.safe_load(self.path.read_text(encoding="utf-8"))

    def test_it_exists_and_is_scheduled(self):
        triggers = self.workflow().get(True) or self.workflow().get("on")
        self.assertIn("schedule", triggers)
        self.assertIn("workflow_dispatch", triggers)

    def test_it_opens_a_pull_request_and_never_pushes_to_main(self):
        """The review queue IS the diff. A workflow that committed to main
        would have published collected material without a person reading it."""
        body = self.path.read_text(encoding="utf-8")
        self.assertIn("create-pull-request", body)
        self.assertNotIn("git push origin main", body)

    def test_it_never_calls_the_sync(self):
        """Collection stops at a pull request. Sync is a separate workflow on a
        separate trigger, and joining them would put unreviewed material one
        cron away from Supabase."""
        body = self.path.read_text(encoding="utf-8")
        self.assertNotIn("knowledge_sync", body)
        self.assertNotIn("scripts/sync", body)

    def test_every_add_path_is_a_file_the_job_actually_writes(self):
        """`add-paths` listed `research_backlog.json`, which only
        `collection.cli backlog --write` creates and this job never runs.

        One missing path is not a partial failure. It is a single `git add`, so
        the pathspec error stages NOTHING — the commit then finds an empty index
        and the action throws, and a run that collected perfectly well produces
        no pull request. Naming a file here is a claim that the job writes it.
        """
        for step in self.workflow()["jobs"]["collect"]["steps"]:
            paths = (step.get("with") or {}).get("add-paths")
            if not paths:
                continue
            for path in paths.split():
                with self.subTest(path=path):
                    self.assertTrue(
                        (ROOT / path).exists(),
                        f"{path} is in add-paths but does not exist. Either the "
                        f"job must write it or it must not be listed.")

    def test_the_pull_request_body_names_commands_that_exist(self):
        """The body told reviewers to run `stewardship.cli review <entity_id>`,
        which cannot act on a candidate — it answers `no such entity` (and exits
        0, so a wrapper would read it as success). Deciding about a candidate is
        `collection.cli`."""
        body = self.path.read_text(encoding="utf-8")
        self.assertNotIn("stewardship.cli", body)
        for verb in ("review", "approve", "reject"):
            with self.subTest(verb=verb):
                self.assertIn(f"collection.cli {verb}", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)


# ═══════════════════════════════ 11. the two verbs that were missing
class DecideAndPromoteTest(unittest.TestCase):
    """The gap the first end-to-end run found.

    Collection ended at a review queue. Stewardship began at an entity already
    in `entities.csv`. Between them was nothing: `collection.cli queue` printed
    twelve rows and no command in the repository could accept one. Two working
    halves, and no join.
    """

    def setUp(self):
        from collection import decide                                # noqa: PLC0415
        from stewardship.ledger import ReviewLedger                  # noqa: PLC0415
        self.decide = decide
        self.tmp = tempfile.TemporaryDirectory()
        self.queue = Path(self.tmp.name) / "queue.jsonl"
        self.ledger = ReviewLedger(path=Path(self.tmp.name) / "ledger.csv")
        review.save([review.Candidate(
            candidate_id="s:1", source_id="s", source_name="S", item_key="1",
            title="Test Margin Money Subsidy Scheme", url="https://example.invalid/1",
            published_at="", change="NEW", classified_as="GovernmentScheme",
            classified_reason="matched “subsidy”", is_entity=True,
            state=review.NEEDS_REVIEW, raw={"title": "Test Margin Money Subsidy Scheme"},
        )], self.queue)

    def tearDown(self):
        self.tmp.cleanup()

    def approve(self):
        for state in ("REVIEWED", "APPROVED"):
            self.decide.decide("s:1", state, actor="tester",
                               evidence="https://example.invalid/1",
                               queue_path=self.queue, ledger=self.ledger)

    def test_the_decision_walks_the_lifecycle_rather_than_jumping_it(self):
        """COLLECTED -> REVIEWED skips VALIDATED, and the lifecycle refuses. The
        machine step is recorded with what actually validated it — the pipeline
        parsed, classified and de-duplicated the record — rather than the
        lifecycle being loosened."""
        self.decide.decide("s:1", "REVIEWED", actor="tester", evidence="url",
                           queue_path=self.queue, ledger=self.ledger)
        states = [(e.from_state, e.to_state, e.actor)
                  for e in self.ledger.for_entity("s:1")]
        self.assertEqual(states, [("COLLECTED", "VALIDATED", ""),
                                  ("VALIDATED", "REVIEWED", "tester")])

    def test_the_decision_lands_in_the_one_audit_trail(self):
        """A second audit trail is not an audit trail."""
        self.approve()
        entries = self.ledger.for_entity("s:1")
        self.assertEqual(entries[-1].to_state, "APPROVED")
        self.assertEqual(entries[-1].actor, "tester")
        self.assertEqual(entries[-1].verification_status_after, "VST-VERIFIED")

    def test_a_decision_survives_the_process(self):
        """`record()` appends in memory; `flush()` is what makes it a trail.
        Without the flush the decision existed for the life of one command and
        the next read a ledger that had never heard of it."""
        self.decide.decide("s:1", "REVIEWED", actor="tester", evidence="url",
                           queue_path=self.queue, ledger=self.ledger)
        from stewardship.ledger import ReviewLedger                  # noqa: PLC0415
        reopened = ReviewLedger(path=self.ledger.path)
        self.assertTrue(reopened.for_entity("s:1"))

    def test_an_illegal_transition_leaves_the_queue_untouched(self):
        """The ledger is written first, so the queue can never hold a state the
        audit trail does not justify."""
        with self.assertRaises(Exception):
            self.decide.decide("s:1", "PUBLISHED", actor="tester",
                               queue_path=self.queue, ledger=self.ledger)
        self.assertEqual(review.load(self.queue)[0].state, review.NEEDS_REVIEW)

    def test_a_machine_cannot_approve(self):
        """`APPROVED is the only state a machine may not enter` —
        stewardship/lifecycle.py, and the collection layer honours it."""
        with self.assertRaises(Exception):
            self.decide.decide("s:1", "APPROVED", actor="",
                               queue_path=self.queue, ledger=self.ledger)

    def test_promotion_fills_only_what_the_source_supplied(self):
        """The line that keeps this honest. A press release announcing a scheme
        does not carry its eligibility, subsidy rate or portal, and writing a
        plausible one would be the fabrication the repository exists to avoid.
        """
        self.approve()
        promotion = self.decide.plan(candidates=self.decide.approved(self.queue))
        self.assertEqual(len(promotion.rows), 1)
        _path, row, _c = promotion.rows[0]
        self.assertEqual(row["scheme_name"], "Test Margin Money Subsidy Scheme")
        self.assertEqual(row["source_url"], "https://example.invalid/1")
        self.assertEqual(row["verification_status"], "VST-NEEDS_REVIEW")
        for column in ("ministry", "objective", "benefit_summary", "official_portal"):
            with self.subTest(column=column):
                self.assertEqual(row[column], self.decide.PENDING)

    def test_it_takes_the_dataset_s_own_next_id(self):
        """These ids appear in package_local_id and in every mapping dataset
        that references them. A UUID where the dataset uses `sch-041` would be
        correct and unreadable."""
        self.approve()
        _path, row, _c = self.decide.plan(
            candidates=self.decide.approved(self.queue)).rows[0]
        self.assertRegex(row["scheme_id"], r"^sch-\d{3}$")

    def test_a_type_the_sync_does_not_project_is_refused(self):
        """A row in a dataset no TableSpec reads would never reach Supabase and
        never become searchable — a silent failure dressed as a success."""
        candidates = review.load(self.queue)
        candidates[0].classified_as = "Event"
        candidates[0].state = review.APPROVED
        promotion = self.decide.plan(candidates=candidates)
        self.assertEqual(promotion.rows, [])
        self.assertIn("no dataset the sync projects", promotion.skipped[0][1])

    def test_every_target_is_a_dataset_the_sync_actually_reads(self):
        """The guard behind that refusal: if a TARGET names a dataset no
        TableSpec covers, promotion writes rows that vanish."""
        from knowledge_sync import config                            # noqa: PLC0415
        projected = {(s.package, s.dataset) for spec in config.TABLE_SPECS
                     for s in spec.sources}
        for kind, target in self.decide.TARGETS.items():
            with self.subTest(kind=kind):
                self.assertIn((target["package"], target["dataset"]), projected)

    def test_it_will_not_write_the_same_row_twice(self):
        self.approve()
        candidates = self.decide.approved(self.queue)
        candidates[0].title = "Prime Minister's Employment Generation Programme"
        promotion = self.decide.plan(candidates=candidates)
        self.assertEqual(promotion.rows, [])
        self.assertIn("already holds a row named", promotion.skipped[0][1])

    def test_promotion_is_a_dry_run_by_default(self):
        self.approve()
        promotion = self.decide.plan(candidates=self.decide.approved(self.queue))
        self.assertEqual(self.decide.apply(promotion, write=False), [])


class SyncCountRatchetTest(unittest.TestCase):

    def test_the_expected_entity_count_is_read_and_not_written_down(self):
        """`EXPECTED_ROWS=1812` and `expected 647` were correct the day they
        were written and wrong the first time collection promoted anything: the
        graph went to 648 and the sync warned about a knowledge base that had
        grown exactly as intended. A ratchet that fires on success is one people
        learn to ignore."""
        body = (ROOT / "scripts" / "run_sync.sh").read_text(encoding="utf-8")
        # Executable lines only — the comment above the change quotes the old
        # values on purpose, and asserting on the whole file would fail on the
        # explanation of the very fix it is checking for.
        code = "\n".join(line for line in body.splitlines()
                          if not line.lstrip().startswith("#"))
        self.assertNotIn("expected 647", code)
        self.assertNotIn("EXPECTED_ROWS=1812", code)
        self.assertIn("graph_summary.json", code)
        self.assertIn("EXPECTED_ENTITIES", code)
