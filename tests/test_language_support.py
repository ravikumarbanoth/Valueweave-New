"""Focused static and runtime tests for the English/Telugu UI layer."""

import json
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

    def test_fallback_hierarchy_never_returns_raw_namespace_key(self):
        self.assertIn("TRANSLATION_DICTIONARY[DEFAULT_LANGUAGE]", self.language)
        self.assertIn("humanizeKey", self.language)
        self.assertNotIn("return english?.[key] || key", self.language,
                         "t() must never return a raw key with namespace prefix")

    def test_industrial_readiness_key_present_in_both_languages(self):
        self.assertIn("'nav.industrial-readiness': 'Industrial Readiness'", self.language)
        self.assertIn("'nav.industrial-readiness': 'పారిశ్రామిక సంసిద్ధత'", self.language)

    def test_founder_identity_translations_present(self):
        self.assertIn("'footer.founded_by': 'Founded by Ravi Kumar Banoth'", self.language)
        self.assertIn("'footer.founded_by': 'రవి కుమార్ బానోత్ చే స్థాపించబడింది'", self.language)
        self.assertIn("'about.founder_name': 'Ravi Kumar Banoth'", self.language)
        self.assertIn("'about.founder_name': 'రవి కుమార్ బానోత్'", self.language)
        self.assertIn("'about.founder_title': 'Founder, ValueWeave'", self.language)
        self.assertIn("'about.founder_title': 'వ్యవస్థాపకుడు, వేల్యూవీవ్'", self.language)


class NavigationIntegrationTests(unittest.TestCase):
    def test_desktop_navigation_has_selector(self):
        self.assertIn("<LanguageSelector />", source(FRONTEND / "components" / "AppNavbar.jsx"))

    def test_mobile_navigation_has_selector(self):
        self.assertIn("<LanguageSelector />", source(FRONTEND / "components" / "MobileNavMenu.jsx"))

    def test_mobile_nav_menu_passes_fallback_label(self):
        menu_src = source(FRONTEND / "components" / "MobileNavMenu.jsx")
        self.assertIn("t(`nav.${l.label.toLowerCase().replaceAll(\" \", \"-\")}`, l.label)", menu_src)

    def test_search_keeps_query_navigation_unchanged(self):
        live_search = source(FRONTEND / "components" / "search" / "LiveSearch.jsx")
        self.assertIn("encodeURIComponent(q)", live_search)
        self.assertIn("const { t } = useLanguage()", live_search)
        self.assertNotIn("setQuery(t(", live_search)


class FounderAttributionIntegrationTests(unittest.TestCase):
    def test_footer_has_subtle_founder_attribution(self):
        footer_src = source(FRONTEND / "components" / "Footer.jsx")
        self.assertIn("Founded by Ravi Kumar Banoth", footer_src)
        self.assertIn('data-testid="footer-founder"', footer_src)

    def test_about_page_has_concise_founder_section(self):
        about_src = source(FRONTEND / "app" / "about" / "page.js")
        self.assertIn("Ravi Kumar Banoth", about_src)
        self.assertIn("Founder, ValueWeave", about_src)
        self.assertIn("ValueWeave was founded by Ravi Kumar Banoth", about_src)
        self.assertIn('data-testid="about-founder"', about_src)


if __name__ == "__main__":
    unittest.main()
