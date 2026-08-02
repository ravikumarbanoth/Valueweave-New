#!/usr/bin/env python3
"""
Plain language on the way in — PX Phase 7.

THE TEST THE BRIEF SETS
-----------------------
Read the homepage and the onboarding as a first-year student on a phone. Every
heading should help answer one of five questions:

    What can I explore?
    What should I learn?
    What business can I start?
    What government support is available?
    What should I do next?

Measured that way, most of the page answered none of them:

    "India's Digital Economic Infrastructure"
    "Digital Manufacturing Operating System"
    "Collaboration & Capital Infrastructure"
    "The collaboration gap in India's grassroots economy"
    "Find your founder DNA."
    "Built for India's builders."
    "Start building with your people."

Each is a sentence about ValueWeave. None is a sentence about the reader.

WHY THIS IS A GREP AND NOT A JUDGEMENT
--------------------------------------
"Does this heading answer one of five questions" cannot be asserted mechanically
without inviting the kind of test that passes on anything. What CAN be asserted
is the vocabulary that produced the failures — the abstract nouns that let a
heading sound substantial while saying nothing — plus the specific rewrites, so
a future edit cannot quietly restore the old ones.

The judgement stays with a person. The ratchet stops the drift back.

    python3 tests/run_all.py --suite plain_language
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
APP = FE / "app"
COMPONENTS = FE / "components"

#: Everything a visitor meets before they have chosen anything: the homepage,
#: the components it renders, and the two onboarding steps.
ENTRY_SURFACES = [
    APP / "page.js",
    APP / "get-started" / "page.js",
    APP / "onboarding" / "page.js",
    COMPONENTS / "HomeHeroSearch.jsx",
    COMPONENTS / "HomeFeatureGrid.jsx",
    COMPONENTS / "HomeHowItWorks.jsx",
    COMPONENTS / "HomeVideoEmbed.jsx",
    COMPONENTS / "HomeSuccessJourney.jsx",
    COMPONENTS / "HomeLiveActivity.jsx",
    COMPONENTS / "HomepageStats.jsx",
    COMPONENTS / "HomeFeaturedOpportunities.jsx",
]


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    """Comments stripped — several files quote the copy they replaced."""
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def rel(path):
    return str(Path(path).relative_to(FE))


def headings(path):
    """Visible headings and card titles: <h1>–<h3>, chips, and `title:` props."""
    src = code(path)
    out = []
    for tag, text in re.findall(r"<(h[123])\b[^>]*>\s*([^<>{}][^<>]*?)\s*</\1>", src, re.S):
        out.append(" ".join(text.split()))
    for text in re.findall(r'className="chip[^"]*">\s*([A-Za-z][^<>{}]{2,60}?)\s*<', src):
        out.append(" ".join(text.split()))
    out.extend(re.findall(r'^\s*title: "([^"]+)"', src, re.M))
    return [h for h in out if h]


# ═══════════════════════════════════════ 1. the vocabulary that hid the meaning
class AbstractNounTest(unittest.TestCase):
    """The words that let a heading sound substantial while saying nothing."""

    #: Each of these was in a rendered heading before this phase.
    #:
    #: "Infrastructure" appeared in NINE of them. It is the single word doing
    #: the most damage on this page: it is what we are building, and it is
    #: never what anybody came for.
    BANNED_IN_HEADINGS = [
        r"\binfrastructure\b",
        r"\becosystem\b",
        r"\boperating system\b",
        r"\bcapital infrastructure\b",
        r"\bfounder DNA\b",
        r"\barchetype\b",
        r"\bgrassroots\b",
        r"\bleverage\b",
        r"\bempower\w*\b",
        r"\bseamless\w*\b",
        r"\bunlock\w*\b",
        r"\bnext-gen\w*\b",
        r"\bcutting[- ]edge\b",
        r"\bworld[- ]class\b",
        r"\bholistic\b",
        r"\bsynerg\w+\b",
    ]

    def test_no_entry_heading_uses_an_abstract_noun(self):
        offenders = []
        for path in ENTRY_SURFACES:
            for heading in headings(path):
                for pattern in self.BANNED_IN_HEADINGS:
                    if re.search(pattern, heading, re.IGNORECASE):
                        offenders.append(f"{rel(path)}: {heading!r}")
        self.assertEqual(
            offenders, [],
            "A heading should help answer one of the five questions a student "
            "arrives with, not describe what we are:\n  " + "\n  ".join(offenders))

    def test_the_scan_actually_finds_headings(self):
        """Guard against the assertion above passing because it saw nothing."""
        total = sum(len(headings(p)) for p in ENTRY_SURFACES)
        self.assertGreater(total, 25, f"only {total} headings found — the scan is broken")


# ═══════════════════════════════════════ 2. the specific rewrites
class RewriteTest(unittest.TestCase):
    """Named individually, because each one will look re-writable later."""

    def test_the_module_cards_say_what_they_are_for(self):
        src = code(COMPONENTS / "HomeFeatureGrid.jsx")
        for gone in ("District Intelligent Digital Infrastructure",
                     "Skill & Industrial Readiness",
                     "Collaboration & Capital Infrastructure",
                     "Digital Manufacturing Operating System",
                     "Industrial Scaling Resources"):
            with self.subTest(old=gone):
                self.assertNotIn(gone, src)
        for expected in ("Your district", "What to learn", "People and money",
                         "Making things", "Growing a business"):
            with self.subTest(new=expected):
                self.assertIn(f'title: "{expected}"', src)

    def test_the_explore_section_asks_the_readers_question(self):
        src = code(COMPONENTS / "HomeFeatureGrid.jsx")
        self.assertNotIn("India&apos;s Digital Economic Infrastructure", src)
        self.assertIn("What can you explore here?", src)

    def test_the_hero_default_is_about_the_reader(self):
        """Still a CMS field. Only the default changed."""
        schema = code(FE / "lib" / "settings-schema.js")
        self.assertNotIn("Where Ambition Finds Its Team", schema)
        self.assertIn("Find what to learn, what to start, and who can help.", schema)
        # The field itself must survive — an admin can still override it.
        self.assertIn('key: "homepage.hero.heading"', schema)
        self.assertIn('key: "homepage.hero.subheading"', schema)

    def test_the_onboarding_says_what_the_profile_is_for(self):
        src = code(APP / "onboarding" / "page.js")
        self.assertNotIn("lightweight profile", src)
        self.assertIn("suggest skills, schemes and businesses that fit you", src)


# ═══════════════════════════════════════ 3. one page, one path
class NoDuplicateJourneyTest(unittest.TestCase):
    """Two "here is your path" sections is not twice the guidance.

    The homepage carried both a ten-stage "Entrepreneur Journey" strip and a
    five-milestone "Your Startup Journey". A reader hitting the second one has
    to work out whether it supersedes the first.

    The strip also lived in a `min-w-[1120px]` horizontal scroller, so on a
    390px phone it showed three of its ten stages and required a sideways drag
    for the rest — on the page whose whole job is to orient someone.
    """

    def test_only_one_journey_section_remains(self):
        src = code(COMPONENTS / "HomeFeatureGrid.jsx")
        self.assertNotIn("Entrepreneur Journey", src)
        self.assertNotIn("JOURNEY", src)

    def test_the_surviving_one_answers_what_do_i_do_next(self):
        src = code(COMPONENTS / "HomeSuccessJourney.jsx")
        self.assertIn("What to do next", src)
        self.assertNotIn("Your Startup Journey", src)

    def test_no_entry_surface_forces_a_sideways_drag(self):
        """A fixed min-width wider than a phone is a horizontal scrollbar."""
        offenders = []
        for path in ENTRY_SURFACES:
            for match in re.findall(r"min-w-\[(\d+)px\]", code(path)):
                if int(match) > 390:
                    offenders.append(f"{rel(path)}: min-w-[{match}px]")
        self.assertEqual(offenders, [], "\n  ".join(offenders))


# ═══════════════════════════════════════ 4. claims the rest of the page denies
class ConsistencyTest(unittest.TestCase):
    """The most confusing thing on a page is two of its own sentences.

    HomeSuccessJourney promised "500+ live opportunities" three sections below
    HomepageStats saying "Platform launching soon — be among the first to join."
    Both were rendered on the same scroll. One of them had to be wrong, and a
    reader has no way to tell which.
    """

    def test_no_entry_surface_claims_a_volume_it_cannot_show(self):
        offenders = []
        for path in ENTRY_SURFACES:
            for match in re.findall(r"\b(\d{2,}\+?\s*(?:live |curated |real )?"
                                    r"(?:opportunities|ideas|members|users|profiles))",
                                    code(path), re.IGNORECASE):
                offenders.append(f"{rel(path)}: {match!r}")
        self.assertEqual(
            offenders, [],
            "Hard-coded counts go stale and contradict the live stats block:\n  "
            + "\n  ".join(offenders))

    def test_the_stats_block_still_reports_real_numbers(self):
        """Removing the fake counts must not remove the real ones."""
        src = code(COMPONENTS / "HomepageStats.jsx")
        self.assertIn("count: \"exact\"", src)
        self.assertIn("emptyLabel", src, "an honest zero still needs a label")


if __name__ == "__main__":
    unittest.main(verbosity=2)
