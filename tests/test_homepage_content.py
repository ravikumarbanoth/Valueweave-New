#!/usr/bin/env python3
"""
Homepage content: the two removed sections, the research-articles section,
and the "?" that stood in front of every Featured Opportunities budget.

THE BUDGET BUG
--------------
HomeFeaturedOpportunitiesClient.jsx was split out of the server component
during the i18n work and written through an encoder that could not represent
"₹". The rupee sign was saved as a literal "?" (0x3F) — the file ended up with
no non-ASCII character at all — so every budget chip read "? ₹2L – ₹5L". The
tests below run the real formatter in Node and read the real component source.
"""
import re
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
COMP = FE / "components"


def read(path):
    return path.read_text(encoding="utf-8")


def code(path):
    """Comments stripped: the components explain the bug by quoting it."""
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


@unittest.skipIf(NODE is None, "node is required — the code under test is JavaScript")
class BudgetLabelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        h = JsHarness()
        try:
            cls.out = h.run('''
                const { formatBudgetLabel } = await import("$LIB/budget.js");
                const cases = ["Under ₹50K", "₹1L – ₹3L", "₹5L – ₹10L", "₹2L-₹5L",
                  "₹5K–15K", "₹10L+", "₹50K – ₹2L", "Under ₹5 Lakhs", "₹ 3L to 7L",
                  "", null, "N/A", "Not specified", "  ₹4L –  ₹10L ", "5 - 10"];
                console.log(JSON.stringify(Object.fromEntries(
                  cases.map((c) => [String(c), formatBudgetLabel(c)]))));
            ''')
        finally:
            h.cleanup()

    def test_the_three_reported_labels(self):
        self.assertEqual(self.out["Under ₹50K"], "Under ₹50,000")
        self.assertEqual(self.out["₹1L – ₹3L"], "₹1L – ₹3L")
        self.assertEqual(self.out["₹5L – ₹10L"], "₹5L – ₹10L")

    def test_no_label_ever_starts_with_a_question_mark_or_a_doubled_rupee(self):
        for raw, label in self.out.items():
            if label is None:
                continue
            self.assertFalse(label.startswith("?"), raw)
            self.assertNotIn("₹ ₹", label, raw)
            self.assertNotIn("₹₹", label, raw)

    def test_values_are_preserved_not_reinterpreted(self):
        self.assertEqual(self.out["₹10L+"], "₹10L+")
        self.assertEqual(self.out["₹50K – ₹2L"], "₹50,000 – ₹2L")
        self.assertEqual(self.out["Under ₹5 Lakhs"], "Under ₹5 Lakhs")
        # A bare range with no symbol is not given one by guesswork.
        self.assertEqual(self.out["5 - 10"], "5 – 10")

    def test_separators_and_spacing_are_tidied(self):
        self.assertEqual(self.out["₹2L-₹5L"], "₹2L – ₹5L")
        self.assertEqual(self.out["₹5K–15K"], "₹5,000 – ₹15,000")
        self.assertEqual(self.out["₹ 3L to 7L"], "₹3L – ₹7L")
        self.assertEqual(self.out["  ₹4L –  ₹10L "], "₹4L – ₹10L")

    def test_missing_budgets_show_nothing(self):
        for raw in ("", "null", "N/A", "Not specified"):
            self.assertIsNone(self.out[raw], raw)


class FeaturedOpportunitiesSourceTest(unittest.TestCase):

    def setUp(self):
        self.client = code(COMP / "HomeFeaturedOpportunitiesClient.jsx")

    def test_the_corrupted_question_mark_is_gone(self):
        self.assertNotRegex(self.client, r"\?\s*\{opp\.investment_range\}")
        self.assertNotIn('"View All Opportunities ?"', self.client)

    def test_the_budget_goes_through_the_formatter(self):
        self.assertIn("formatBudgetLabel(opp.investment_range)", self.client)

    def test_no_component_prefixes_a_symbol_the_value_already_has(self):
        for path in (COMP / "HomeFeaturedOpportunities.jsx", COMP / "HomeFeaturedOpportunitiesClient.jsx"):
            self.assertNotRegex(code(path), r"₹\s*\{[^}]*investment_range", path.name)

    def test_there_is_one_card_not_two(self):
        server = code(COMP / "HomeFeaturedOpportunities.jsx")
        self.assertNotIn("function OpportunityCard", server)


class RemovedSectionsTest(unittest.TestCase):

    def test_who_is_here_so_far_is_not_on_the_homepage(self):
        page = read(FE / "app" / "page.js")
        self.assertNotIn("<HomepageStats", page)
        self.assertNotIn('import HomepageStats', page)
        # Kept, not deleted.
        self.assertTrue((COMP / "HomepageStats.jsx").exists())

    def test_what_we_are_building_next_is_not_on_the_homepage(self):
        grid = code(COMP / "HomeFeatureGrid.jsx")
        for gone in ("What we are building next", "COMING NEXT", "Patents and innovation labs",
                     "University research", "home-future-modules", "FUTURE_MODULES"):
            self.assertNotIn(gone, grid, gone)
        # The shared card component is still used elsewhere and still exists.
        self.assertTrue((COMP / "knowledge" / "CapabilityStatus.jsx").exists())


class ResearchArticlesSectionTest(unittest.TestCase):

    def setUp(self):
        self.server = read(COMP / "HomeResearchArticles.jsx")
        self.client = read(COMP / "HomeResearchArticlesClient.jsx")
        self.client_code = re.sub(r"\s+", " ", self.client)
        self.page = read(FE / "app" / "page.js")

    def test_it_reuses_the_existing_loader_and_card(self):
        self.assertIn('from "@/lib/research"', self.server)
        self.assertIn("getCombinedArticles()", self.server)
        self.assertIn("<ArticleCard", self.client)
        self.assertIn('from "@/components/research/ArticleCard"', self.client)

    def test_published_only_unique_and_four_to_six(self):
        self.assertIn("a.published", self.server)
        self.assertIn("seen.has(a.slug)", self.server)
        self.assertIn("MAX_ARTICLES = 6", self.server)

    def test_no_section_when_there_are_no_articles(self):
        self.assertIn("if (picked.length === 0) return null;", self.server)

    def test_it_does_not_claim_a_popularity_ranking_it_cannot_see(self):
        # Reads are only readable by admins (page_views RLS); the homepage
        # orders by recency and must not call that "most read".
        for src in (self.client, read(FE / "lib" / "language.js")):
            self.assertNotRegex(src, r"(?i)most[ -]read|most popular|trending")

    def test_explore_all_goes_to_the_research_hub(self):
        self.assertIn('href="/research"', self.client)

    def test_headings_are_translated(self):
        lang = read(FE / "lib" / "language.js")
        for key in ("home.research_title", "home.research_subtitle", "home.research_explore_all"):
            self.assertEqual(lang.count(f"'{key}':"), 2, key)
            self.assertIn(f't( "{key}"'.replace("( ", "("), self.client_code.replace("t( ", "t("))

    def test_it_sits_after_opportunities_and_before_the_final_cta(self):
        # Directly after opportunities: Discover → Opportunities → Research.
        # (It sat near the bottom until the network redesign moved it up.)
        body = self.page[self.page.index("return ("):]
        self.assertLess(body.index("<HomeFeaturedOpportunities"), body.index("<HomeResearchArticles"))
        self.assertLess(body.index("<HomeResearchArticles"), body.index("<HomeConnections"))
        self.assertLess(body.index("<HomeResearchArticles"), body.index("<HomeFinalCta"))


if __name__ == "__main__":
    unittest.main()
