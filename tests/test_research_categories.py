#!/usr/bin/env python3
"""
Research article categories: the expanded taxonomy and custom categories.

`research_articles.category` is free text and always was, so a custom category
is stored in the column that already exists. What these tests hold is that the
three spellings that can end up in that column — a predefined id, a custom
label, an older hand-typed value — resolve to ONE category everywhere, and
that the editor's publishing workflow was not touched to get there.
"""
import re
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"

ORIGINAL = {
    "agriculture": "Agriculture", "healthcare": "Healthcare",
    "technology": "Technology", "manufacturing": "Manufacturing",
    "energy": "Energy", "retail": "Retail", "education": "Education",
    "logistics": "Logistics", "food-processing": "Food Processing",
    "handicrafts": "Handicrafts",
}


@unittest.skipIf(NODE is None, "node is required — the code under test is JavaScript")
class TaxonomyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.t = cls.h.run('''
            const t = await import("$LIB/theme.js");
            const V = (s, used) => t.validateCustomCategory(s, used || []);
            console.log(JSON.stringify({
              labels: t.CATEGORY_LABELS,
              groups: t.CATEGORY_GROUPS,
              resolve: Object.fromEntries([
                "healthcare", "Healthcare", "food processing", "Food Processing",
                "FOOD-PROCESSING", "Drone Services", "drone-services",
                "ev & battery technology", "", "Arts and Crafts",
              ].map((s) => [s, t.resolveCategory(s)])),
              empty_no_fallback: t.resolveCategory("", null),
              norm: Object.fromEntries([
                "  drone   services ", "EV charging", "arts&crafts", "eCommerce and D2C",
                "bamboo products of the north east", "   ", "<b>x</b>",
              ].map((s) => [s, t.normalizeCustomCategory(s)])),
              v_empty: V("   "),
              v_short: V("a"),
              v_symbols: V("&&&"),
              v_new: V("  drone   services "),
              v_predef_label: V("health care"),
              v_predef_amp: V("EV and Battery Technology"),
              v_dupe_custom: V("drone-SERVICES", ["Drone Services", "Bamboo Products"]),
              v_long: V("x".repeat(200) + " y"),
            }));
        ''')

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def test_every_original_category_keeps_its_id_and_label(self):
        for cid, label in ORIGINAL.items():
            self.assertEqual(self.t["labels"].get(cid), label, cid)

    def test_the_list_grew_and_has_no_duplicates(self):
        labels = self.t["labels"]
        self.assertGreaterEqual(len(labels), 30)
        grouped = [i for g in self.t["groups"] for i in g["items"]]
        self.assertEqual(len(grouped), len(labels), "an id appears in two groups")
        key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))
        self.assertEqual(len({key(l) for _, l in grouped}), len(grouped))

    def test_ids_are_clean_slugs(self):
        for cid in self.t["labels"]:
            self.assertRegex(cid, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_no_category_is_a_place(self):
        # District stays its own field.
        for label in self.t["labels"].values():
            for place in ("Telangana", "Andhra", "Hyderabad", "District"):
                self.assertNotIn(place, label)

    def test_every_spelling_of_a_predefined_category_is_that_category(self):
        r = self.t["resolve"]
        for s in ("healthcare", "Healthcare"):
            self.assertEqual((r[s]["id"], r[s]["known"]), ("healthcare", True))
        for s in ("food processing", "Food Processing", "FOOD-PROCESSING"):
            self.assertEqual(r[s]["id"], "food-processing")
            self.assertEqual(r[s]["label"], "Food Processing")
        self.assertEqual(r["ev & battery technology"]["id"], "ev-battery-technology")

    def test_a_custom_category_gets_one_id_and_a_readable_label(self):
        r = self.t["resolve"]
        self.assertEqual(r["Drone Services"], {"id": "drone-services", "label": "Drone Services", "known": False})
        # The slug form (an MDX file, an older row) is the SAME category.
        self.assertEqual(r["drone-services"]["id"], "drone-services")
        self.assertEqual(r["drone-services"]["label"], "Drone Services")
        self.assertEqual(r["Arts and Crafts"]["id"], "arts-and-crafts")

    def test_an_uncategorised_row_still_reads_as_before(self):
        self.assertEqual(self.t["resolve"][""]["id"], "agriculture")
        self.assertEqual(self.t["empty_no_fallback"]["id"], "")

    def test_spacing_and_capitalisation_are_normalised(self):
        n = self.t["norm"]
        self.assertEqual(n["  drone   services "], "Drone Services")
        self.assertEqual(n["EV charging"], "EV Charging")          # EV untouched
        self.assertEqual(n["arts&crafts"], "Arts & Crafts")
        self.assertEqual(n["eCommerce and D2C"], "eCommerce and D2C")
        self.assertEqual(n["bamboo products of the north east"], "Bamboo Products of the North East")
        self.assertEqual(n["   "], "")
        self.assertNotIn("<", n["<b>x</b>"])

    def test_empty_and_meaningless_names_are_rejected(self):
        for k in ("v_empty", "v_short", "v_symbols"):
            self.assertFalse(self.t[k]["ok"], k)
            self.assertTrue(self.t[k]["error"])

    def test_a_new_custom_category_is_stored_as_its_tidy_label(self):
        v = self.t["v_new"]
        self.assertEqual((v["ok"], v["value"], v["existing"]), (True, "Drone Services", None))

    def test_typing_a_predefined_category_selects_it_instead(self):
        self.assertEqual(self.t["v_predef_label"]["value"], "healthcare")
        self.assertEqual(self.t["v_predef_label"]["existing"], "predefined")
        self.assertEqual(self.t["v_predef_amp"]["value"], "ev-battery-technology")

    def test_a_near_duplicate_of_a_custom_category_reuses_the_original(self):
        v = self.t["v_dupe_custom"]
        self.assertEqual((v["value"], v["existing"]), ("Drone Services", "custom"))

    def test_length_is_capped(self):
        self.assertLessEqual(len(self.t["v_long"]["value"]), 60)


class WiringTest(unittest.TestCase):
    """Source-level: who reads the central list, and what was left alone."""

    def read(self, rel):
        return (FE / rel).read_text(encoding="utf-8")

    def test_the_editor_offers_groups_and_a_custom_entry(self):
        src = self.read("app/admin/research/ArticleEditor.jsx")
        self.assertIn("CATEGORY_GROUPS.map", src)
        self.assertIn("<optgroup", src)
        self.assertIn("+ Add Custom Category", src)
        self.assertIn("validateCustomCategory(", src)

    def test_the_custom_entry_is_the_last_option(self):
        src = self.read("app/admin/research/ArticleEditor.jsx")
        select = src[src.index('data-testid="editor-category"'):]
        select = select[:select.index("</select>")]
        self.assertTrue(select.rstrip().endswith("+ Add Custom Category</option>"))

    def test_the_save_path_was_not_changed(self):
        # The row written to Supabase, and the two actions, exactly as before.
        src = self.read("app/admin/research/ArticleEditor.jsx")
        self.assertIn("category: f.category || null,", src)
        for testid in ("editor-title", "editor-slug", "editor-content",
                       "editor-save-draft", "editor-publish", "editor-unpublish"):
            self.assertIn(f'data-testid="{testid}"', src)
        self.assertIn('if (!f.title.trim() || !f.slug.trim())', src)
        self.assertIn("}, 30000);", src)

    def test_no_new_table_or_migration_for_categories(self):
        names = [p.name for p in (FE / "migrations").glob("*.sql")]
        self.assertFalse([n for n in names if "categor" in n.lower()])

    def test_the_hub_builds_its_chips_from_the_articles(self):
        src = self.read("app/research/ResearchHubClient.jsx")
        self.assertIn("a.categoryLabel", src)
        self.assertNotIn("CATEGORY_LABELS[selectedCategory]", src)

    def test_db_articles_carry_a_label_and_search_on_it(self):
        src = self.read("lib/research-db.js")
        self.assertIn("categoryLabel: cat.label", src)
        self.assertIn("sector: row.category ? cat.label", src)

    def test_cards_and_detail_pages_show_the_label(self):
        for rel in ("components/research/ArticleCard.jsx",
                    "components/research/ArticleTemplate.jsx"):
            self.assertIn("label={article.categoryLabel}", self.read(rel), rel)

    def test_a_category_creates_no_knowledge_graph_relationship(self):
        for rel in ("lib/theme.js", "app/admin/research/ArticleEditor.jsx"):
            src = self.read(rel)
            for word in ("kg_relationships", "kg_entities", "relationships.csv"):
                self.assertNotIn(word, src, rel)


if __name__ == "__main__":
    unittest.main()
