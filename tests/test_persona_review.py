#!/usr/bin/env python3
"""
Human UX review — PX Phase 8.

HOW THE FINDINGS WERE FOUND
---------------------------
Not by reading source. Seven personas from the brief — a 17-year-old student,
an ITI student, a graduate, a degree student, a woman entrepreneur, a farmer, a
working professional — were each walked through the journey they would actually
take, in a real browser at 390px, against a production build reading the real
647 entities (scripts/dev/fake_postgrest.py).

Five defects survived that walk. Every one of them is invisible in the source
and obvious on the screen.

    1  A search result page headed "What would you like to explore?".
       You typed "Electrician", pressed Search, and the page asked what you
       wanted — above a paragraph inviting you to start exploring. That is
       what a page looks like when it has ignored you, and it is precisely
       what this route did until the search fix landed. The results were
       right underneath; the heading argued with them.

    2  A mistyped or stale detail URL rendered "More is on the way" with no
       heading at all — the platform-is-not-ready message. One address being
       wrong was reported as the whole site being unfinished, and the way out
       pointed at the business ideas rather than back at the category.

    3  "← Knowledge Explorer" as the back link on every detail page. A
       product-area name, to a reader who arrived from a search engine and
       has never seen it.

    4  The source stated twice under every title, three lines apart: a
       "Skills & training research" chip, then "From our skills & training
       research". Once is provenance. Twice reads as a bug.

    5  /opportunity-radar — where /start/entrepreneur sends people, so the
       first real page a would-be founder sees — headed "Ranked. Scored.
       Ready for You to Build." over a subtitle naming the Idea Library and
       the Research Hub. Phase 7's plain-language pass was scoped to the
       homepage and never reached it.

WHAT THIS FILE CAN AND CANNOT HOLD
----------------------------------
These are static assertions on the five rewrites. They stop the drift back.
They are not the review — the review was the walk, and the next one will need
walking too.

    python3 tests/run_all.py --suite persona_review
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
APP = FE / "app"
COMPONENTS = FE / "components"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


# ═══════════════════════════════ 1. the page knows a search happened
class SearchResultHeadingTest(unittest.TestCase):

    def setUp(self):
        self.src = code(APP / "knowledge" / "page.js")

    def test_the_heading_shows_the_query(self):
        self.assertIn('searching ? "Search results" : "Explore"', self.src)
        self.assertIn('`“${q}”`', self.src)

    def test_the_browse_invitation_is_hidden_once_a_query_exists(self):
        """"What would you like to explore?" is right for someone with no
        query and wrong for someone who just typed one."""
        self.assertIn("{!searching && (", self.src)

    def test_the_invitation_still_exists_for_someone_who_arrives_cold(self):
        self.assertIn("What would you like to explore?", self.src)


# ═══════════════════════════════ 2. missing page vs missing platform
class NotFoundTest(unittest.TestCase):

    def test_the_state_exists_and_says_what_happened(self):
        src = code(COMPONENTS / "knowledge" / "KnowledgeEmptyState.jsx")
        self.assertIn("NOT_FOUND: {", src)
        self.assertIn("We could not find that page", src)
        self.assertIn('"NOT_FOUND"', src, "it must be in EMPTY_STATES too")

    def test_the_detail_route_asks_which_it_is(self):
        """The two causes look identical from the route and mean opposites."""
        src = code(APP / "knowledge" / "[type]" / "[slug]" / "page.js")
        self.assertIn("await knowledgeAvailable()", src)
        self.assertIn('availability.available ? "NOT_FOUND" : "SCHEMA_UNREACHABLE"', src)

    def test_it_offers_the_category_rather_than_the_radar(self):
        src = code(APP / "knowledge" / "[type]" / "[slug]" / "page.js")
        self.assertIn("not-found-category", src)
        self.assertIn("Browse all {label.toLowerCase()}", src)

    def test_a_missing_page_no_longer_claims_the_platform_is_unfinished(self):
        src = code(APP / "knowledge" / "[type]" / "[slug]" / "page.js")
        block = src[src.index("if (!entity) {"):src.index("const [detail, related]")]
        self.assertNotIn('reason="SCHEMA_UNREACHABLE"', block,
                         "the unconditional not-deployed message is the bug")


# ═══════════════════════════════ 3 & 4. the detail header
class DetailHeaderTest(unittest.TestCase):

    def setUp(self):
        self.src = code(COMPONENTS / "knowledge" / "EntityHeader.jsx")

    def test_the_back_link_does_not_name_a_product_area(self):
        self.assertNotIn('backLabel = "Knowledge Explorer"', self.src)
        self.assertIn("Back to everything we have researched", self.src)

    def test_the_source_is_stated_once(self):
        """SourceBadge and ProvenanceLine were both visible, three lines apart."""
        self.assertIn("<SourceBadge", self.src)
        self.assertIn("srOnly", self.src)

    def test_the_identifiers_survive_for_support_and_tests(self):
        """Hiding the sentence must not drop the data attributes with it."""
        prov = code(COMPONENTS / "knowledge" / "ProvenanceLine.jsx")
        for attr in ("data-source-package", "data-source-dataset", "data-source-row"):
            with self.subTest(attr=attr):
                self.assertIn(attr, prov)
        self.assertIn('srOnly ? "sr-only"', prov,
                      "the element must stay in the DOM, only its text goes")


# ═══════════════════════════════ 5. the entrepreneur's first real page
class OpportunityRadarTest(unittest.TestCase):

    def test_the_heading_is_not_a_slogan(self):
        src = code(APP / "opportunity-radar" / "page.js")
        self.assertNotIn("Ranked. Scored.", src)
        self.assertIn("Business ideas,", src)

    def test_the_subtitle_does_not_name_other_product_areas(self):
        src = code(APP / "opportunity-radar" / "page.js")
        hero = src[src.index('data-testid="radar-title"'):]
        hero = hero[:hero.index("</section>")]
        for area in ("Idea Library", "Research Hub"):
            with self.subTest(area=area):
                self.assertNotIn(area, hero)


# ═══════════════════════════════ the journeys themselves
class JourneyReachabilityTest(unittest.TestCase):
    """Every step of every persona's walk must be a route that exists.

    The walk is manual; this keeps its destinations honest between walks, so a
    renamed route cannot quietly strand a persona.
    """

    JOURNEYS = {
        "17-year-old student": ["/", "/start/student", "/knowledge"],
        "ITI student": ["/knowledge", "/start/skilled-worker"],
        "graduate": ["/start/job-seeker", "/explore"],
        "degree student": ["/start/student", "/discover"],
        "woman entrepreneur": ["/start/entrepreneur", "/opportunity-radar", "/ideas"],
        "farmer": ["/start/farmer", "/districts"],
        "working professional": ["/knowledge", "/collaborators"],
    }

    def route_exists(self, path):
        parts = [p for p in path.strip("/").split("/") if p]
        node = APP
        for part in parts:
            if (node / part).is_dir():
                node = node / part
                continue
            dynamic = [d for d in node.iterdir()
                       if d.is_dir() and d.name.startswith("[")]
            if not dynamic:
                return False
            node = dynamic[0]
        return (node / "page.js").exists() or (node / "page.jsx").exists()

    def test_every_step_of_every_journey_resolves(self):
        offenders = []
        for persona, steps in self.JOURNEYS.items():
            for step in steps:
                if not self.route_exists(step):
                    offenders.append(f"{persona}: {step}")
        self.assertEqual(offenders, [], "\n  ".join(offenders))


if __name__ == "__main__":
    unittest.main(verbosity=2)
