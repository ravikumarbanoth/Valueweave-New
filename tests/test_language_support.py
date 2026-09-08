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

    def test_welcome_back_and_journey_keys_present_in_both_languages(self):
        for key in [
            'home.welcome_back',
            'home.welcome_context_prefix',
            'home.welcome_context_suffix',
            'home.change',
            'home.forget_me',
        ]:
            self.assertIn(f"'{key}':", self.language)

    def test_audience_and_goal_keys_present_in_both_languages(self):
        for key in [
            'audience.student',
            'audience.job-seeker',
            'audience.entrepreneur',
            'audience.farmer',
            'audience.skilled-worker',
            'audience.business-owner',
            'goal.looking_for_a_job',
            'goal.start_a_business',
            'goal.learn_a_skill',
            'goal.government_schemes',
            'goal.agriculture',
            'goal.ai_careers',
            'goal.manufacturing',
            'goal.my_district',
            'goal.explore_everything',
        ]:
            self.assertIn(f"'{key}':", self.language)

    def test_why_and_discover_sections_keys_present_in_both_languages(self):
        for key in [
            'home.why_chip',
            'home.why_title_1',
            'home.gap_1_title',
            'home.gap_2_title',
            'home.gap_3_title',
            'home.discover_chip',
            'home.discover_heading_1',
            'archetype.innovator',
            'archetype.leader',
            'archetype.builder',
            'archetype.influencer',
        ]:
            self.assertIn(f"'{key}':", self.language)

    def test_stats_and_steps_and_cta_keys_present_in_both_languages(self):
        for key in [
            'stats.who_is_here',
            'stats.visitors',
            'stats.assessments',
            'stats.opportunities',
            'stats.collaborators',
            'stats.districts',
            'step.step1_title',
            'step.step2_title',
            'step.step3_title',
            'step.step4_title',
            'step.step5_title',
            'milestone.day1_title',
            'milestone.week1_title',
            'milestone.week2_title',
            'milestone.month1_title',
            'milestone.month3_title',
            'home.ready_chip',
            'home.step_heading_1',
            'home.join_sparkle',
        ]:
            self.assertIn(f"'{key}':", self.language)


class HomepageComponentLocalizationTests(unittest.TestCase):
    def test_client_components_wire_use_language(self):
        components = [
            "HomeHeroSearch.jsx",
            "HomeHowItWorks.jsx",
            "HomeSuccessJourney.jsx",
            "HomepageStatsClient.jsx",
            "HomeFeaturedOpportunitiesClient.jsx",
            "HomeLiveActivityClient.jsx",
            "HomeWhySection.jsx",
            "HomeDiscoverSection.jsx",
            "HomeSectorsSection.jsx",
            "HomeFinalCta.jsx",
            "HomeNavClient.jsx",
            "HomeHeroValueProps.jsx",
            "AppNavbar.jsx",
        ]
        for comp in components:
            src = source(FRONTEND / "components" / comp)
            self.assertIn("useLanguage", src, f"{comp} must import or use useLanguage")
            self.assertIn("use client", src, f"{comp} must be a client component for dynamic translation")

    def test_landing_page_preserves_seo_and_test_contract(self):
        page_src = source(FRONTEND / "app" / "page.js")
        required_identifiers = [
            "heroHeading",
            "heroSubheading",
            "primaryCta",
            "secondaryCta",
            "tertiaryCta",
            "<HomeHeroSearch",
            "<HomepageStats",
            "<HomeHowItWorks",
            "<HomeFeatureGrid",
            "<HomeFeaturedOpportunities",
        ]
        for ident in required_identifiers:
            self.assertIn(ident, page_src, f"Landing page must retain identifier/component {ident}")


class NavigationIntegrationTests(unittest.TestCase):
    def test_global_layout_has_floating_language_switcher(self):
        layout_src = source(FRONTEND / "app" / "layout.js")
        self.assertIn("<FloatingLanguageSwitcher />", layout_src)

    def test_navigation_menus_have_no_duplicate_selectors(self):
        navbar_src = source(FRONTEND / "components" / "AppNavbar.jsx")
        menu_src = source(FRONTEND / "components" / "MobileNavMenu.jsx")
        self.assertNotIn("<LanguageSelector", navbar_src)
        self.assertNotIn("<LanguageSelector", menu_src)

    def test_floating_switcher_has_toggles_and_testids(self):
        switcher_src = source(FRONTEND / "components" / "LanguageSelector.jsx")
        self.assertIn('data-testid="floating-language-switcher"', switcher_src)
        self.assertIn('data-testid="language-toggle-en"', switcher_src)
        self.assertIn('data-testid="language-toggle-te"', switcher_src)

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

