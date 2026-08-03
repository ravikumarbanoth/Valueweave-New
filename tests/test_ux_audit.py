#!/usr/bin/env python3
"""
PX Phase 10 — the final human UX audit.

HOW THE FINDINGS WERE FOUND
---------------------------
By crawling the built site at 390px in Chromium and measuring, not by reading
the source and imagining. Twenty-eight public routes were loaded and checked
for status, heading structure, horizontal overflow, runtime errors, developer
language and tap-target size.

WHAT THE CRAWL CLEARED
----------------------
Most of the list Phase 10 names was already clean, which is what eight prior
phases were for: no 404s, no page throwing a JavaScript error, exactly one
`h1` per page, and not one page scrolling sideways at 390px. Those are not
asserted here — `tests/test_production_ux.py` and `tests/test_landing.py`
already hold them.

WHAT IT FOUND
-------------
1. Every footer link was 16px tall. "About" measured 35x16. The footer renders
   on all 28 public routes, which made it the most-repeated mobile defect on
   the site — and the audience this platform is for is on a phone.

2. The social icons were 36px, also under the minimum.

3. "Government schemes" and "Manufacturing" each appeared TWICE on the
   homepage — once as a search prompt, once as a goal — as different chips
   opening different pages. That one is in tests/test_landing.py, next to the
   list it constrains.

WHY 44 PIXELS
-------------
WCAG 2.5.5 (AAA) and every mobile platform guideline land on roughly 44
device-independent pixels, which is about the pad of an adult finger. Below
that a link is not merely fiddly, it is a coin toss — and the person paying
for the mis-tap is on a mid-range Android in a Tier-2 town, not on the desk
where the CSS was written.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
FOOTER = FE / "components" / "Footer.jsx"
SOCIAL = FE / "components" / "SocialLinks.jsx"

#: WCAG 2.5.5 Target Size (Enhanced). Tailwind's scale puts this at `11`
#: (2.75rem) or an explicit `min-h-[44px]`.
MIN_TAP_PX = 44


class FooterTapTargetTest(unittest.TestCase):
    """The most-repeated mobile defect on the site: 28 pages, 16px links."""

    def setUp(self):
        self.source = FOOTER.read_text(encoding="utf-8")

    def test_every_footer_link_reserves_a_full_tap_target(self):
        """Measured before the fix: About 35x16, Privacy 41x16, Terms 33x16.

        Asserted on the class strings rather than by launching a browser,
        because this suite has to run in CI where there is no server and no
        Supabase — the browser measurement is what FOUND it, this is what
        keeps it fixed.
        """
        links = re.findall(r"<(?:Link|a)\b[^>]*className=\{?\"([^\"]+)\"",
                           self.source, re.S)
        self.assertGreaterEqual(len(links), 3, "footer links did not parse")
        for cls in links:
            flat = " ".join(cls.split())
            with self.subTest(cls=flat[:60]):
                self.assertRegex(
                    flat, r"min-h-\[44px\]|h-11|py-3|py-4",
                    "a footer link with no vertical padding renders 16px tall")

    def test_the_text_size_was_not_changed_to_achieve_it(self):
        """Padding, not a bigger font. Growing the type would have been a
        redesign of a footer nobody asked to redesign; growing the box is
        invisible until you try to tap it."""
        self.assertIn("text-xs", self.source)

    def test_the_reason_is_recorded_where_the_next_person_will_look(self):
        """A bare `min-h-[44px]` reads as a style tweak and gets refactored
        away. The measurement is why it is there."""
        self.assertIn("44px", self.source)
        self.assertRegex(self.source, r"(?i)tap target|2\.5\.5|WCAG")


class SocialIconTapTargetTest(unittest.TestCase):

    def test_the_icon_buttons_are_at_least_44px(self):
        """Executable lines only. The comment recording the fix quotes the old
        `w-9 h-9` on purpose, and scanning the whole file would fail on the
        explanation of the very change it is checking for."""
        code = "\n".join(
            line for line in SOCIAL.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith(("//", "*", "/*")))
        self.assertNotRegex(
            code, r"\bw-9 h-9\b",
            "36px social buttons — under the 44px minimum on every page "
            "that renders the footer")
        self.assertRegex(code, r"\bw-11 h-11\b")


class SharedControlTapTargetTest(unittest.TestCase):
    """The tap-target defect was not only the footer.

    Fixing the footer exposed the next layer, which is what a crawl is for:
    the navbar logo, the feedback button, six "back" links, and the category
    filters on /explore, /ideas, /research, /dashboard and /opportunity-radar
    — the last of which are the PRIMARY interaction on those pages and were
    hardcoded at `min-h-[32px]` and `min-h-[36px]`, a number somebody chose on
    purpose and chose too small.
    """

    def test_nothing_declares_a_tap_target_below_44px(self):
        """A repository-wide sweep, because the values were spread across six
        files and a per-file test would have missed the seventh."""
        offenders = []
        for path in list((FE / "app").rglob("*.js")) + list((FE / "components").rglob("*.jsx")):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"min-h-\[(?:[0-3]?\d|4[0-3])px\]", line):
                    offenders.append(f"{path.relative_to(FE)}:{n}")
        self.assertEqual(offenders, [],
                         "tap targets declared below the 44px minimum: "
                         + ", ".join(offenders[:6]))

    def test_an_interactive_chip_gets_a_finger_sized_box(self):
        """`.chip` is used 196 times for two different things — a static badge
        and a real control. The rule selects on the element so badges are
        untouched: a <span className="chip"> stays small, an <a> or <button>
        grows."""
        css = (FE / "app" / "globals.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"a\.chip,\s*button\.chip")
        block = css[css.index("a.chip,"):css.index("a.chip,") + 220]
        self.assertIn("min-h-[44px]", block)


class WrappedControlTest(unittest.TestCase):
    """The defect a measurement could not find.

    "Sign in" in the navbar wrapped to two lines at 390px — a pill reading
    "Sign / in". The crawl never saw it, because a control that wraps gets
    TALLER, and every automated check in this file is looking for things that
    are too short. It turned up in a screenshot, which is the argument for
    still looking at the page after measuring it.
    """

    def test_short_navbar_labels_do_not_wrap(self):
        navbar = (FE / "components" / "AppNavbar.jsx").read_text(encoding="utf-8")
        signin = navbar[navbar.index('data-testid="nav-public-signin"'):][:400]
        self.assertIn("whitespace-nowrap", signin)


class InlineLinkExceptionTest(unittest.TestCase):
    """Where the 44px rule deliberately does NOT apply.

    WCAG 2.5.5 exempts a target that is "in a sentence or block of text",
    because the alternative is worse: giving an email address inside a
    paragraph a 44px box breaks the line height of the paragraph around it,
    and a reader loses more to mangled prose than they gain from a bigger tap
    on a link they can also just read.

    Three links land here — the contact address on /privacy and /terms, and
    "Or browse by category" inside the search hint. They are the only sub-44px
    controls left on the public site and they are left on purpose.
    """

    def test_the_contact_addresses_stay_inline(self):
        for page in ("privacy", "terms"):
            source = (FE / "app" / page / "page.js").read_text(encoding="utf-8")
            with self.subTest(page=page):
                self.assertIn("mailto:", source)
                # Inside a <p>, not a standalone block.
                self.assertRegex(source, r"<p>[^<]*<a href=\"mailto:|write to <a|Reach out at <a")


class PrivacyDisclosureTest(unittest.TestCase):
    """Phase 9 started storing something on the reader's device."""

    def test_the_policy_mentions_what_phase_9_stores(self):
        """One word, never sent to us, deletable in a tap — and a policy that
        omits a thing because the thing is small still omits it."""
        page = (FE / "app" / "privacy" / "page.js").read_text(encoding="utf-8")
        self.assertRegex(page, r"(?i)your own browser|on your device")
        self.assertIn("Forget me", page)

    def test_naming_the_auth_provider_is_not_jargon(self):
        """The Phase 10 crawl flagged "Supabase" on this page. It is a false
        positive: naming the processor that handles authentication is a
        standard disclosure, and removing it would make the policy less
        honest, not more readable. Recorded so nobody "fixes" it later."""
        page = (FE / "app" / "privacy" / "page.js").read_text(encoding="utf-8")
        self.assertIn("Supabase", page)


class AuditScopeTest(unittest.TestCase):
    """What the crawl covered, so a later reader knows what was NOT looked at."""

    def test_the_audit_excluded_staff_tools_on_purpose(self):
        """34 of the 82 routes are under /admin. Phase 10 asks what a
        first-generation student meets on a phone, and no student meets
        /admin/opportunity-performance. Auditing them would have buried three
        real findings under forty irrelevant ones.
        """
        admin = list((FE / "app" / "admin").glob("*/page.js"))
        self.assertGreater(len(admin), 20,
                           "if the admin surface shrank, re-check this reasoning")


if __name__ == "__main__":
    unittest.main(verbosity=2)
