"""Focused static tests for the lightweight English/Telugu UI layer."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"


def source(path):
    return path.read_text(encoding="utf-8")


class LanguageModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language = source(FRONTEND / "lib" / "language.js")

    def test_english_is_default_and_telugu_supported(self):
        self.assertIn("export const DEFAULT_LANGUAGE = 'en'", self.language)
        self.assertIn("const SUPPORTED_LANGUAGES = ['en', 'te']", self.language)

    def test_persistence_and_document_language(self):
        self.assertIn("localStorage.setItem(STORAGE_KEY, lang)", self.language)
        self.assertIn("document.documentElement.lang = lang", self.language)
        self.assertIn("localStorage.getItem(STORAGE_KEY)", self.language)

    def test_english_fallback_exists(self):
        self.assertIn("TRANSLATION_DICTIONARY[DEFAULT_LANGUAGE]", self.language)
        self.assertIn("return english?.[key] || key", self.language)

    def test_audience_and_language_storage_are_separate(self):
        self.assertIn("vw_ui_language", self.language)
        self.assertNotIn("audience", self.language.split("const STORAGE_KEY", 1)[1].split(";", 1)[0])


class NavigationIntegrationTests(unittest.TestCase):
    def test_desktop_navigation_has_selector(self):
        self.assertIn("<LanguageSelector />", source(FRONTEND / "components" / "AppNavbar.jsx"))

    def test_mobile_navigation_has_selector(self):
        self.assertIn("<LanguageSelector />", source(FRONTEND / "components" / "MobileNavMenu.jsx"))

    def test_search_keeps_query_navigation_unchanged(self):
        live_search = source(FRONTEND / "components" / "search" / "LiveSearch.jsx")
        self.assertIn("encodeURIComponent(q)", live_search)
        self.assertIn("const { t } = useLanguage()", live_search)
        self.assertNotIn("setQuery(t(", live_search)


if __name__ == "__main__":
    unittest.main()
