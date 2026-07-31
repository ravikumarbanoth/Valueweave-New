#!/usr/bin/env python3
"""
ValueWeave v1.0 — Production UX polish.

WHAT THIS SUITE IS FOR
----------------------
Every previous step of this platform was written for the person building it, and
each one left its vocabulary on the screen. By the time Step 4 finished, a
first-year student looking for a welding course in Warangal could be told:

    "The knowledge schema has not been deployed to this environment.
     Depends on: Run the migrations, expose the `knowledge` schema, then
     `scripts/run_sync.sh`. See docs/FIRST_DEPLOYMENT_CHECKLIST.md steps 5–10."

Every word true. None of it theirs.

This suite is the ratchet. The terminology test is the important one: it is not
possible to write an honest empty state without being tempted to explain the
infrastructure, and the temptation returns on every sprint. A grep in a test is
the only thing that reliably says no.

    python3 tests/run_all.py --suite production_ux
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
    """Source with `//` and `/* */` comments stripped.

    A file may — and several do — explain at length which internal term it stopped
    showing. Explaining the history is how the next person avoids repeating it.
    What may not survive is the term rendering.
    """
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def public_sources():
    """Every non-admin page and component.

    `admin/` is excluded throughout: it is tooling for a handful of operators who
    do maintain the sync and do read the checklist, and for whom "Package006" is
    the clearest available word.
    """
    out = []
    for root in (APP, COMPONENTS):
        for path in sorted(root.rglob("*.js")) + sorted(root.rglob("*.jsx")):
            if "admin" in path.parts:
                continue
            out.append(path)
    return out


def rel(path):
    return str(Path(path).relative_to(FE))


# ═══════════════════════════════════════════════ 1. the vocabulary ratchet
class DeveloperLanguageTest(unittest.TestCase):
    """No internal vocabulary in anything a user reads."""

    #: Terms a public user must never meet. Regexes, matched case-insensitively
    #: against comment-stripped source.
    #:
    #: `sync`, `migration` and `deployment` are NOT here as bare words: they are
    #: ordinary English ("syncing your calendar") and banning them outright would
    #: produce false positives that get silenced rather than fixed. The phrases
    #: that actually leaked are banned instead.
    BANNED = [
        (r"knowledge\s+graph", "knowledge graph"),
        (r"knowledge\s+schema", "knowledge schema"),
        (r"Packages?\s*00\d", "package identifier"),
        (r"Packages\s+001", "package range"),
        (r"vocabulary\s+crosswalk", "vocabulary crosswalk"),
        (r"\bcrosswalk\b", "crosswalk"),
        (r"DEPLOYMENT_CHECKLIST", "checklist filename"),
        (r"scripts/\w+\.sh", "script path"),
        (r"rule\s+engine", "rule engine"),
        (r"not\s+switched\s+on", "\"not switched on\""),
        (r"deployed\s+to\s+this\s+environment", "deployment language"),
        (r"\.csv\b", "dataset filename"),
        (r"TABLE_SPEC", "internal spec name"),
        (r"knowledge_sync", "module name"),
        (r"unprojected", "internal jargon"),
    ]

    #: `packages: ["Package001_Geography"]` in the explorer is a prop VALUE handed
    #: to SourceBadge, which renders "Districts & geography research". The
    #: identifier never reaches the screen, and rewriting the data to satisfy a
    #: grep would be the test wagging the code.
    ALLOWED_IDENTIFIER_LINES = re.compile(
        r"^\s*(packages:\s*\[|source_package|sourcePackage|Package00\d\w*:\s*\")")

    def test_no_internal_vocabulary_reaches_a_user(self):
        offenders = []
        for path in public_sources():
            for lineno, line in enumerate(code(path).splitlines(), 1):
                if self.ALLOWED_IDENTIFIER_LINES.match(line):
                    continue
                for pattern, label in self.BANNED:
                    if re.search(pattern, line, re.IGNORECASE):
                        offenders.append(f"{rel(path)}:{lineno}  [{label}]  {line.strip()[:80]}")
        self.assertEqual(
            offenders, [],
            "These render to a public user. Say what they can do, not what our "
            "infrastructure is doing:\n  " + "\n  ".join(offenders))

    def test_source_labels_name_a_subject_not_a_directory(self):
        """"Package006 · Skills & Training" told a student nothing."""
        src = read(FE / "lib" / "knowledge.js")
        block = src[src.index("export const PACKAGE_LABELS"):]
        block = block[:block.index("};")]
        # The KEYS are the identifiers and have to stay — they are what the
        # database column holds. Only the values are read by a person.
        values = re.findall(r':\s*"([^"]+)"', block)
        self.assertEqual(len(values), 8, "one label per research area")
        for value in values:
            with self.subTest(label=value):
                self.assertNotRegex(value, r"Package\s*00\d",
                                    "a label must not repeat its identifier")
        for expected in ("Districts & geography", "Skills & training", "Small business"):
            with self.subTest(label=expected):
                self.assertIn(expected, values)

    def test_provenance_shows_a_sentence_not_three_ids(self):
        """It used to render `Package008_MSME · businesses.csv · B-014`."""
        src = read(COMPONENTS / "knowledge" / "ProvenanceLine.jsx")
        self.assertNotIn("parts.join", src)
        self.assertIn("From our", src)
        # The identifiers survive where support can still reach them.
        for attr in ("data-source-package", "data-source-dataset", "data-source-row"):
            with self.subTest(attr=attr):
                self.assertIn(attr, src)


# ═══════════════════════════════════════════════ 2. the 404
class LegacyRouteTest(unittest.TestCase):
    """`/explore/<id>` was linked from the landing page and never existed."""

    def test_no_page_links_to_the_dead_route(self):
        offenders = [
            rel(p) for p in public_sources()
            if re.search(r"[\"'`]/explore/\$?\{", code(p))
        ]
        self.assertEqual(offenders, [],
                         "link opportunities to /opportunities/<id>")

    def test_the_landing_page_links_to_the_real_detail_route(self):
        src = code(COMPONENTS / "HomeFeaturedOpportunities.jsx")
        self.assertIn("/opportunities/${opp.id}", src)

    def test_the_legacy_url_still_redirects(self):
        """The bad link was live long enough to have been shared."""
        src = read(FE / "next.config.js")
        self.assertIn("redirects", src)
        # `:id+`, not `:id*`. The star modifier matches zero segments too, so it
        # redirected `/explore` — the working marketplace page — to
        # `/opportunities`. Asserting the exact modifier is the only way this
        # stays fixed; both spellings look right in a diff.
        self.assertIn("/explore/:id+", src)
        self.assertIn("/opportunities/:id+", src)
        self.assertNotIn("/explore/:id*", src,
                         "the star modifier also captures /explore itself")
        self.assertIn("permanent: true", src)

    def test_the_destination_route_exists(self):
        self.assertTrue((APP / "opportunities" / "[id]" / "page.js").exists())


# ═══════════════════════════════════════════════ 3. the snapshot rename
class SnapshotPanelTest(unittest.TestCase):
    """"AI-readable summary" described who the block was for, not what it held."""

    def test_the_old_component_is_gone(self):
        self.assertFalse((COMPONENTS / "geo" / "AiReadableSummary.jsx").exists())
        self.assertTrue((COMPONENTS / "geo" / "SnapshotPanel.jsx").exists())

    def test_nothing_still_imports_it(self):
        offenders = [rel(p) for p in public_sources() if "AiReadableSummary" in code(p)]
        self.assertEqual(offenders, [])

    def test_no_page_titles_a_section_ai_readable(self):
        offenders = [
            rel(p) for p in public_sources()
            # `data-ai-readable` is the markup answer engines read and the
            # rename kept it on purpose. Only a human-facing use is banned.
            if re.search(r"(?<!data-)AI-readable", code(p), re.IGNORECASE)
        ]
        self.assertEqual(offenders, [])

    def test_the_opportunity_pages_say_opportunity_snapshot(self):
        for page in ("app/opportunities/[id]/page.js",
                     "app/opportunities/[id]/OpportunityDetailClient.jsx"):
            with self.subTest(page=page):
                self.assertIn('title="Opportunity Snapshot"', read(FE / page))

    def test_the_machine_readable_markup_survives(self):
        """The rename was for humans. Answer engines still get their attributes."""
        src = read(COMPONENTS / "geo" / "SnapshotPanel.jsx")
        self.assertIn('data-ai-readable="true"', src)
        self.assertIn('data-ai-faq="true"', src)


# ═══════════════════════════════════════════════ 4. recommendations
class RecommendationMessagingTest(unittest.TestCase):
    """The brief: never show "Personalised recommendations are not switched on"."""

    def test_the_dashboard_hides_the_block_when_we_cannot_serve_it(self):
        """NOT_DEPLOYED is ours to fix and the user can do nothing about it.

        An empty panel explaining our infrastructure is worse than no panel: it
        occupies the most valuable space on the dashboard to say "not our best
        day". So the whole block is hidden and the opportunity feed moves up.
        """
        src = code(APP / "dashboard" / "page.js")
        self.assertIn('intel.reason === "NOT_COMPUTED"', src)
        self.assertRegex(src, r"intel\.available\s*\|\|\s*intel\.reason")

    def test_the_computable_case_offers_the_button_that_fixes_it(self):
        """NOT_COMPUTED is theirs to fix, so it gets a way to fix it."""
        src = read(APP / "dashboard" / "page.js")
        self.assertIn('href="/onboarding"', src)
        self.assertIn("Complete your profile", src)

    def test_the_state_messages_speak_to_a_person(self):
        src = code(FE / "lib" / "intelligence.js")
        block = src[src.index("export async function intelligenceState"):]
        # Delimited by code, not by a comment banner: `code()` strips comments,
        # so the banner this used to slice on no longer exists.
        block = block[:block.index("export function scoreLabel")]
        self.assertNotIn("deployment", block.lower())
        self.assertNotIn("switched on", block.lower())
        self.assertIn("Add your skills", block)


# ═══════════════════════════════════════════════ 5. district pages
class DistrictMessagingTest(unittest.TestCase):
    """Both district routes exposed the matching mechanism when it missed."""

    ROUTES = ["app/district/[slug]/page.js", "app/districts/[slug]/page.js"]

    def test_neither_route_mentions_how_we_match_names(self):
        for route in self.ROUTES:
            with self.subTest(route=route):
                src = code(FE / route).lower()
                self.assertNotIn("crosswalk", src)
                self.assertNotIn("vocabulary", src)

    def test_the_unmatched_message_keeps_the_editorial_profile_credible(self):
        """A reader must not conclude the profile above is also unreliable."""
        for route in self.ROUTES:
            with self.subTest(route=route):
                self.assertIn("The profile above is still accurate", read(FE / route))

    def test_the_panel_leads_with_what_is_there(self):
        src = read(COMPONENTS / "knowledge" / "DistrictIntelligencePanel.jsx")
        self.assertIn("Opportunities in {districtName}", src)
        self.assertNotIn("What the knowledge base records", src)


# ═══════════════════════════════════════════════ 6. student-first questions
class StudentFirstTest(unittest.TestCase):
    """"Every screen must answer at least one question."

    Not every page can answer all five, and forcing it would produce filler. What
    is checkable is that the pages a student actually lands on name the thing
    they came for — opportunity, skill, business, government support, people —
    somewhere in their own copy.
    """

    PAGES = {
        "app/knowledge/page.js": ["district", "skill", "business", "scheme"],
        "app/readiness/components/ReadinessSections.jsx": ["skill"],
        "app/manufacturing/components/ManufacturingSections.jsx": ["business"],
        "app/network/components/NetworkSections.jsx": ["collaborator"],
        "components/HomeFeatureGrid.jsx": ["district", "skill", "business", "scheme"],
        "components/platform/KnowledgeSearch.jsx": ["district", "skill", "business", "scheme"],
    }

    def test_each_page_names_what_a_user_came_for(self):
        for page, words in self.PAGES.items():
            src = code(FE / page).lower()
            for word in words:
                with self.subTest(page=page, word=word):
                    self.assertIn(word, src)

    def test_the_landing_page_links_to_the_youtube_channel(self):
        src = read(COMPONENTS / "HomeVideoEmbed.jsx")
        self.assertIn("youtube.com/@valueweave", src)
        self.assertIn("home-youtube-link", src)

    def test_the_search_box_suggests_what_to_type(self):
        """An empty box with no example is a wall."""
        src = read(COMPONENTS / "platform" / "KnowledgeSearch.jsx")
        self.assertIn("placeholder=", src)
        explorer = read(APP / "knowledge" / "page.js")
        self.assertIn("Try a district, a skill, or a business idea", explorer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
