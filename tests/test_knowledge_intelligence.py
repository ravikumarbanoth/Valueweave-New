#!/usr/bin/env python3
"""
The Knowledge Intelligence layer: the promotion gate, the queue inventory,
derived entity profiles, knowledge gaps and gap candidates.

WHAT THESE TESTS DEFEND
------------------------
Not that the layer is clever — that it is HONEST. A derived layer's failure
mode is not being wrong, it is quietly becoming canonical: an inferred edge
losing its label, a gap turning into an invented training provider, a
recommendation reading as a decision. Every test below aims at one of those,
and several assert an ABSENCE, which is the only way to test a promise not to
fabricate.

WHAT IS NOT TESTED HERE, AND WHY
---------------------------------
Query intent, location extraction and result grouping already exist in
`knowledge_engine/stage2.py` and `frontend/lib/search/intelligence.js`, and are
already covered by `tests/test_stage2.py` and `tests/test_search_intelligence.py`.
This file does not re-test them and this layer does not reimplement them —
it answers the other question, "what is missing from the GRAPH", which those
modules do not ask.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from tests.js_harness import JsHarness, entities, NODE, NODE_REASON

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

QUEUE = ROOT / "collection" / "state" / "review_queue.jsonl"


def queue_rows():
    return [json.loads(line) for line in
            QUEUE.read_text(encoding="utf-8").splitlines() if line.strip()]


# ═══════════════════════════════ 1. the promotion gate
class PromotionGateTest(unittest.TestCase):
    """The constraint that shapes the whole of Stage 1.

    A machine may inventory, classify, group and recommend. It may not
    approve, and therefore may not promote. If this stops being true the
    review queue stops meaning anything, and these tests are the alarm.
    """

    def test_a_machine_cannot_enter_approved(self):
        from stewardship.lifecycle import (LifecycleState,          # noqa: PLC0415
                                           TransitionError, check_transition)
        with self.assertRaises(TransitionError):
            check_transition(LifecycleState.REVIEWED, LifecycleState.APPROVED,
                             actor="a-machine", by_machine=True)

    def test_approval_requires_a_named_actor(self):
        from stewardship.lifecycle import (LifecycleState,          # noqa: PLC0415
                                           TransitionError, check_transition)
        with self.assertRaises(TransitionError):
            check_transition(LifecycleState.REVIEWED, LifecycleState.APPROVED,
                             actor="", by_machine=False)

    def test_nothing_in_the_queue_was_approved(self):
        """The single most important assertion in this file: it is what makes
        "we processed the backlog" mean "we sorted it", not "we published
        it"."""
        for row in queue_rows():
            with self.subTest(candidate=row["candidate_id"]):
                self.assertIn(row["state"], ("NEEDS_REVIEW", "DUPLICATE"))


# ═══════════════════════════════ 2. the inventory
class InventoryTest(unittest.TestCase):

    def setUp(self):
        from collection import inventory                           # noqa: PLC0415
        self.inv = inventory
        self.rows = inventory.build(with_search=False)

    def test_every_queued_candidate_is_inventoried(self):
        self.assertEqual(len(self.rows), len(queue_rows()))

    def test_every_candidate_gets_one_recommendation_with_a_reason(self):
        """An inventory that leaves rows unlabelled has not processed the
        backlog, it has looked at it."""
        for row in self.rows:
            rec, why = self.inv.recommend(row)
            with self.subTest(candidate=row["candidate_id"]):
                self.assertIn(rec, self.inv.RECOMMENDATIONS)
                self.assertGreater(len(why), 20)

    def test_test_fixtures_are_always_rejected(self):
        """The `fix-*` sources exist to exercise the collector. One reaching a
        package would be the pipeline publishing its own test data."""
        for row in self.rows:
            if row["source"].startswith("fix-"):
                with self.subTest(candidate=row["candidate_id"]):
                    self.assertEqual(self.inv.recommend(row)[0], "REJECT")

    def test_the_rejected_candidate_stays_rejected(self):
        row = next(r for r in self.rows if r["title"] == "Production Operator")
        self.assertEqual(self.inv.recommend(row)[0], "REJECT")

    def test_a_grouped_candidate_is_never_promoted_alone(self):
        """Groups exist to stop the same trade being approved twice under two
        names. A grouped row may come back GROUP, or RESEARCH_REQUIRED when it
        is also disputed — never PROMOTE, and the group is named either way so
        whoever picks it up decides the rest in the same sitting."""
        for row in self.rows:
            if row["group"]:
                rec, why = self.inv.recommend(row)
                with self.subTest(candidate=row["candidate_id"]):
                    self.assertIn(rec, ("GROUP", "RESEARCH_REQUIRED"))
                    self.assertIn(row["group"], why)

    def test_only_verified_candidates_are_recommended_for_promotion(self):
        """The bar for PROMOTE is a primary source already checked and
        recorded — not a plausible-looking role name."""
        for row in self.rows:
            if self.inv.recommend(row)[0] == "PROMOTE":
                with self.subTest(candidate=row["candidate_id"]):
                    self.assertTrue(row["verified"])
                    self.assertTrue(row["verified_code"])
                    self.assertTrue(row["promotable_type"])

    def test_promotion_that_needs_a_repoint_says_so(self):
        """A new Skill plus an old alias still pointing at the wrong
        BusinessOpportunity is an incoherent promotion. The recommendation has
        to carry that obligation or it will be missed."""
        for row in self.rows:
            rec, why = self.inv.recommend(row)
            if rec == "PROMOTE" and row["repoint_required"]:
                with self.subTest(candidate=row["candidate_id"]):
                    self.assertIn("re-point", why)
                    self.assertIn(row["repoint_concept"], why)

    def test_an_unpromotable_type_is_reported_not_silently_dropped(self):
        """BusinessOpportunity has no target in collection/decide.py, so the
        pipeline cannot write a row for it even after approval. That is a gap
        in the promoter, and the inventory must say so rather than leaving
        seven candidates looking merely undecided."""
        unpromotable = [r for r in self.rows
                        if not r["promotable_type"]
                        and not r["source"].startswith("fix-")
                        and r["entity_type"] != "KnowledgeGap"]
        self.assertTrue(unpromotable)
        for row in unpromotable:
            rec, why = self.inv.recommend(row)
            with self.subTest(candidate=row["candidate_id"]):
                self.assertEqual(rec, "KEEP_NEEDS_REVIEW")
                self.assertIn("decide.py", why)

    def test_the_gate_is_quoted_not_paraphrased(self):
        for fragment in ("machine_permitted", "--actor", "may not approve"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.inv.PROMOTION_IS_NOT_AUTOMATABLE)


# ═══════════════════════════════ 3. derived profiles
class ProfileTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from knowledge_intelligence import profiles                # noqa: PLC0415
        cls.P = profiles
        cls.profiles = profiles.build(("Skill",))

    def test_one_profile_per_skill_in_the_graph(self):
        skills = [e for e in entities() if e["entity_type"] == "Skill"]
        self.assertEqual(len(self.profiles), len(skills))

    def test_every_relationship_in_a_profile_exists_in_the_graph(self):
        """A derived view may restate the graph. It may not add to it — one
        invented edge and the layer stops being derived."""
        real = set()
        for rel in self.P._rows(self.P.RELATIONSHIPS):
            real.add((rel["from_entity"], rel["relationship_type"], rel["to_entity"]))
            real.add((rel["to_entity"], rel["relationship_type"], rel["from_entity"]))
        for profile in self.profiles:
            for dim, rows in profile["dimensions"].items():
                for row in rows:
                    key = (profile["entity_id"], row["via"], row["entity_id"])
                    with self.subTest(entity=profile["entity"], dim=dim,
                                      other=row["entity"]):
                        self.assertIn(key, real)

    def test_every_graph_edge_is_labelled_canonical(self):
        for profile in self.profiles:
            for rows in profile["dimensions"].values():
                for row in rows:
                    self.assertEqual(row["trust"], "CANONICAL")

    def test_no_profile_invents_an_attribute(self):
        """The failure this layer exists to avoid: a profile carrying a
        plausible training provider nobody researched."""
        blob = json.dumps(self.profiles)
        for what, pattern in {
            "a rupee figure": r"₹\s*[\d,]+",
            "a phone number": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
            "an email address": r"[\w.-]+@[\w.-]+\.\w+",
        }.items():
            with self.subTest(what=what):
                self.assertIsNone(re.search(pattern, blob))

    def test_a_missing_dimension_is_recorded_not_hidden(self):
        """The whole point. Certification is 0% across the graph, so every
        profile must say so rather than rendering an empty section."""
        for profile in self.profiles:
            if not profile["dimensions"]["certification"]:
                with self.subTest(entity=profile["entity"]):
                    self.assertIn("certification", profile["missing"])
                    self.assertEqual(profile["status"], "RESEARCH_REQUIRED")

    def test_coverage_reports_the_uncomfortable_numbers(self):
        """A coverage report that flatters the platform is useless. These are
        the real figures; if one improves, update it deliberately."""
        cov = self.P.coverage(self.profiles)
        self.assertEqual(cov["dimensions"]["certification"]["have"], 0)
        self.assertEqual(cov["dimensions"]["district"]["have"], 0)
        self.assertEqual(cov["complete"], 0)
        self.assertLess(cov["dimensions"]["training"]["pct"], 25.0)


# ═══════════════════════════════ 4. research articles
class ArticleIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from knowledge_intelligence import profiles                # noqa: PLC0415
        cls.P = profiles
        cls.articles = profiles.load_articles()
        cls.profiles = profiles.build(("Skill",))

    def test_the_articles_are_found_and_parsed(self):
        self.assertGreaterEqual(len(self.articles), 3)
        for article in self.articles:
            with self.subTest(slug=article["slug"]):
                self.assertTrue(article["title"])
                self.assertGreater(len(article["text"]), 500)

    def test_a_mention_is_a_whole_phrase_not_a_substring(self):
        """`tractor` ⊂ `contractor` cost this repository a regression once
        already. The article matcher must not reintroduce it one layer up."""
        fake = {"slug": "x", "title": "x",
                "text": "An electrical contracting firm in Medak."}
        self.assertIsNone(self.P._mentions(fake, "tractor", []))
        self.assertIsNotNone(self.P._mentions(fake, "contracting", []))

    def test_article_links_are_derived_not_canonical(self):
        for profile in self.profiles:
            for article in profile["articles"]:
                with self.subTest(entity=profile["entity"]):
                    self.assertEqual(article["trust"], "DERIVED")
                    self.assertTrue(article["matched"])

    def test_every_claimed_mention_is_really_in_the_article(self):
        """Few of the skills are mentioned by any article, and that is the
        honest answer — the articles are about businesses, not trades. A layer
        producing more would be guessing."""
        by_slug = {a["slug"]: a for a in self.articles}
        for profile in self.profiles:
            for article in profile["articles"]:
                with self.subTest(entity=profile["entity"], slug=article["slug"]):
                    self.assertIn(article["matched"].lower(),
                                  by_slug[article["slug"]]["text"].lower())


# ═══════════════════════════════ 5. gap candidates
class GapCandidateTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from knowledge_intelligence import candidates              # noqa: PLC0415
        cls.C = candidates
        cls.rows = candidates.candidates()

    def test_gaps_go_through_the_existing_queue_not_a_new_one(self):
        queued = {r["candidate_id"] for r in queue_rows()}
        for candidate in self.rows:
            with self.subTest(candidate=candidate.candidate_id):
                self.assertIn(candidate.candidate_id, queued)

    def test_a_gap_can_never_become_a_package_row(self):
        """`KnowledgeGap` is deliberately absent from decide.py's TARGETS, so
        even a human who approves one cannot turn it into knowledge by
        accident."""
        from collection import decide                              # noqa: PLC0415
        self.assertNotIn(self.C.GAP_TYPE, decide.TARGETS)
        for candidate in self.rows:
            with self.subTest(candidate=candidate.candidate_id):
                self.assertEqual(candidate.classified_as, self.C.GAP_TYPE)
                self.assertFalse(candidate.is_entity)

    def test_the_slice_is_small_enough_to_actually_be_read(self):
        """45 skills have a gap; queueing all 45 is the queue-fatigue failure
        the collection design names. The rule narrows it to the sharpest form
        — a livelihood the platform recommends and cannot teach."""
        self.assertLessEqual(len(self.rows), 10)
        self.assertGreater(len(self.rows), 0)

    def test_every_gap_names_the_business_that_makes_it_urgent(self):
        for candidate in self.rows:
            with self.subTest(candidate=candidate.candidate_id):
                self.assertTrue(candidate.raw["recommended_businesses"])
                self.assertTrue(candidate.raw["missing"])
                self.assertEqual(candidate.raw["status"], "RESEARCH_REQUIRED")

    def test_a_gap_carries_no_factual_claim(self):
        """Checking for the WORDS was the first version of this test and it
        failed on the reviewer note — the sentence promising the row carries
        no salary or fee contains both words. What must be absent is DATA."""
        payload = [{k: v for k, v in c.raw.items() if not k.startswith("_")}
                   for c in self.rows]
        blob = json.dumps(payload)
        for what, pattern in {
            "a rupee figure": r"₹\s*[\d,]+",
            "any number that could be a rate": r"\b\d{3,}\b",
            "a phone number": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
            "an email address": r"[\w.-]+@[\w.-]+\.\w+",
        }.items():
            with self.subTest(what=what):
                self.assertIsNone(re.search(pattern, blob))


# ═══════════════════════════════ 6. no search regression
@unittest.skipUnless(NODE, NODE_REASON)
class NoSearchRegressionTest(unittest.TestCase):
    """This milestone must not have moved a single search result.

    Nothing was promoted, so the graph is unchanged; nothing was aliased, so
    the concept table is unchanged. That is a claim worth measuring rather
    than asserting, because it is the one thing a reader would notice.
    """

    def test_the_graph_and_packages_are_untouched(self):
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "knowledge_graph", "packages"],
            cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertEqual(dirty, "")

    def test_the_known_answers_are_still_the_answers(self):
        h = JsHarness()
        try:
            h.dataset("entities.json", entities())
            got = h.run("""
                const { rankEntities } = await import("$LIB/knowledge-search.js");
                const rows = JSON.parse(fs.readFileSync("$DIR/entities.json","utf8"));
                const out = {};
                for (const q of %s) {
                  const r = rankEntities(rows, q, { limit: 1 })[0];
                  out[q] = r ? r.canonical_name : null;
                }
                console.log(JSON.stringify(out));
            """ % json.dumps([
                "plc automation", "scada", "mobile repair", "smart home",
                "car mechanic", "ac service", "computer repair",
                "fabrication workshop", "cold storage business",
                "plumbing contractor", "rac mechanic", "pipe fitter"]))
        finally:
            h.cleanup()
        expected = {
            "plc automation": "PLC Programming & Control Systems",
            "scada": "PLC Programming & Control Systems",
            "mobile repair": "Electronics Repair & Maintenance",
            "smart home": "IoT Systems Development",
            "car mechanic": "Automobile Mechanic (Diesel/Petrol)",
            "ac service": "HVAC Technician",
            "computer repair": "Electronics Repair & Maintenance",
            "fabrication workshop": "Welding (MIG/TIG/Arc)",
            "cold storage business": "Cold Storage Facility",
            "plumbing contractor": "Plumbing",
            "rac mechanic": "HVAC Technician",
            "pipe fitter": "Plumbing",
        }
        for query, want in expected.items():
            with self.subTest(query=query):
                self.assertEqual(got[query], want)

    def test_no_sector_magnet_and_no_certification_beats_a_skill(self):
        """Two named regressions from earlier milestones, re-asserted because
        this milestone touched the layer above them."""
        h = JsHarness()
        try:
            h.dataset("entities.json", entities())
            got = h.run("""
                const { rankEntities } = await import("$LIB/knowledge-search.js");
                const rows = JSON.parse(fs.readFileSync("$DIR/entities.json","utf8"));
                const out = {};
                for (const q of %s) {
                  const r = rankEntities(rows, q, { limit: 1 })[0];
                  out[q] = r ? { name: r.canonical_name, type: r.entity_type } : null;
                }
                console.log(JSON.stringify(out));
            """ % json.dumps(["welding", "plumbing", "masonry", "solar technician",
                              "cnc operator", "lathe operator"]))
        finally:
            h.cleanup()
        for query, row in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(row)
                self.assertNotIn(row["name"].lower(),
                                 ("manufacturing", "construction", "services"))
                self.assertNotEqual(row["type"], "Certification")


if __name__ == "__main__":
    unittest.main(verbosity=2)
