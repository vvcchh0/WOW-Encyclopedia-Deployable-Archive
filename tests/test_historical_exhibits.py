from __future__ import annotations

import re
import sys
import unittest
import html
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import historical_exhibits as exhibits  # noqa: E402
import export_github_pages as pages  # noqa: E402


class HistoricalExhibitTests(unittest.TestCase):
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"

    def test_p0_routes_and_aliases_are_canonical(self) -> None:
        self.assertTrue(exhibits.is_historical_exhibit_route("/visa/reward/index.html"))
        self.assertEqual(exhibits.canonical_exhibit_route("visa/reward"), "/visa/reward/index.html")
        self.assertEqual(exhibits.canonical_exhibit_route("/visa/reward/login"), "/visa/reward/login.html")
        self.assertIsNone(exhibits.canonical_exhibit_route("/visa/index.html"))

    def test_reward_selection_is_a_static_historical_exhibit(self) -> None:
        page = exhibits.transform_derived_page(
            '<html><body><form><input name="password"><a href="/visa/reward/login.html">Login</a></form></body></html>',
            "/visa/reward/index.html",
            base_path=self.prefix,
        )
        self.assertIn('class="historical-exhibit"', page)
        self.assertIn("2008 archive · Historical exhibit", page)
        self.assertIn("retired", page.casefold())
        self.assertIn(self.prefix + "visa/reward/login.html", page)
        self.assertIn(self.prefix + "visa/reward/images/button-have3.gif", page)
        self.assertNotRegex(page, r"<\s*(?:form|input|select|textarea|button)\b")
        self.assertNotIn("Please select one of the following options", page)
        self.assertNotIn("Continue to the Rewards Site", page)
        self.assertNotRegex(page, r"https?://")

    def test_identity_exhibits_describe_fields_in_past_tense_only(self) -> None:
        for route, expected in (
            ("/visa/reward/login.html", "Social Security Number"),
            ("/visa/reward/wow-login.html", "account name and password"),
        ):
            with self.subTest(route=route):
                page = exhibits.transform_derived_page("<html><body>old form</body></html>", route, base_path=self.prefix)
                self.assertIn('class="historical-exhibit"', page)
                self.assertIn("historical interface", page.casefold())
                self.assertIn(expected.casefold(), page.casefold())
                self.assertIn("No personal", page)
                self.assertNotRegex(page, r"<\s*(?:form|input|select|textarea|button)\b")
                self.assertNotRegex(page, r"(?i)please\s+(?:enter|fill out|provide)")
                self.assertNotRegex(page, r"https?://")

    def test_trial_selector_is_a_static_exhibit_with_local_return(self) -> None:
        page = exhibits.transform_derived_page(
            '<html><body><script src="afftrack.js">setCookies(1)</script>'
            '<form><input name="email"></form></body></html>',
            "/burningcrusade/trial/index.html",
            base_path=self.prefix,
        )
        self.assertIn('data-exhibit-route="/burningcrusade/trial/index.html"', page)
        self.assertIn("2008 World of Warcraft trial selector", page)
        self.assertIn("Burning Crusade", page)
        self.assertIn("World of Warcraft", page)
        self.assertIn("images/", page)
        self.assertIn("not been recovered", page.casefold())
        self.assertIn(self.prefix, page)
        self.assertNotIn("afftrack.js", page.casefold())
        self.assertNotIn("setcookies", page.casefold())
        self.assertNotIn("signup.worldofwarcraft.com", page.casefold())
        self.assertNotRegex(page, r"<\s*(?:form|input|select|textarea|button)\b")
        self.assertNotRegex(page, r"<\s*img\b")
        self.assertNotRegex(page, r"https?://")

    def test_ptr_aliases_render_neutral_static_exhibit_with_local_links_only(self) -> None:
        source = """<html><head><title>WoW -> Public Test Realm</title></head><body>
        <script>document.write('legacy operational control')</script>
        <form action="http://test.worldofwarcraft.com/us/copy/character-copy.html"><input name="copy"></form>
        <p>The World of Warcraft Public Test Realms (PTRs) are used to test upcoming content patches in a public environment before they are released to live realms.</p>
        </body></html>"""
        metadata = {
            "actual_timestamp": "20061110075927",
            "actual_memento": "2006-11-10T07:59:27+00:00",
        }
        for route in ("/ptr", "/ptr/", "/ptr/index.html"):
            with self.subTest(route=route):
                self.assertTrue(exhibits.is_historical_exhibit_route(route))
                self.assertEqual(exhibits.canonical_exhibit_route(route), "/ptr/index.html")
                page = exhibits.transform_derived_page(
                    source,
                    route,
                    base_path=self.prefix,
                    source_metadata=metadata,
                )
                self.assertIn("<title>World of Warcraft Public Test Realm — Historical Exhibit</title>", page)
                self.assertIn("Selected archival capture: 2006-11-10 07:59:27 UTC.", page)
                self.assertNotIn("2006 World of Warcraft", page)
                self.assertIn(
                    "The Public Test Realms were used to test upcoming content patches",
                    page,
                )
                self.assertIn("<h2>About the Public Test Realm</h2>", page)
                self.assertIn("<h2>Related archived pages</h2>", page)
                self.assertIn(">Archive home</a>", page)
                self.assertNotIn("selected source", page.casefold())
                self.assertNotRegex(page, r"<\s*(?:script|form|input|select|textarea|button)\b")
                self.assertNotRegex(page, r"(?i)character[- ]copy|software[- ]download|download for")
                self.assertNotRegex(page, r"https?://")
                for local_route in (
                    "index.html",
                    "info/basics/guide.html",
                    "info/faq/ptr.html",
                    "patchnotes/test-realm-patchnotes.html",
                ):
                    self.assertIn(self.prefix + local_route, page)

    def test_p1_rewrite_does_not_touch_scripts_or_search_controls(self) -> None:
        source = '''<html><body><form id="topSearch"><input name="searchBox"></form>
<p>Welcome to the Future Beta Sign-Up Form!</p>
<p>Once you enter your information, you should receive a confirmation eMail. We will eMail you again once invitations are being sent; the eMail you receive at that point will contain further instructions.</p>
<script>var message = "Welcome to the Future Beta Sign-Up Form!";</script>
<p><a href="/info/article.html">ordinary article</a></p></body></html>'''
        page = exhibits.transform_p1_page(source, "/misc/beta-signup.html")
        self.assertIn("archived beta sign-up page from 2008", page)
        self.assertIn("The 2008 page described confirmation email messages", page)
        self.assertIn('var message = "Welcome to the Future Beta Sign-Up Form!";', page)
        self.assertIn('name="searchBox"', page)
        self.assertIn("ordinary article", page)
        self.assertIn('data-historical-exhibit="p1"', page)

    def test_p1_does_not_rewrite_an_unlisted_article(self) -> None:
        source = '<html><body><p>Apply now!</p><script>window.search="Apply now!";</script></body></html>'
        self.assertEqual(source, exhibits.transform_p1_page(source, "/info/story/article.html"))

    def test_historical_account_menu_labels_follow_exact_local_targets(self) -> None:
        def missing(requested: str) -> str:
            return "/__offline/missing.html?requested=" + quote(requested, safe="")

        hrefs = {
            "create": missing("http://signup.worldofwarcraft.com/"),
            "manage": missing("https://www.worldofwarcraft.com/account/"),
            "password": missing("https://www.worldofwarcraft.com/loginsupport/password.html"),
        }
        source = (
            '<nav><a href="' + hrefs["create"] + '">Create Account</a>'
            '<a href="' + hrefs["manage"] + '">Manage Account</a>'
            '<a href="' + hrefs["password"] + '">Retrieve Password</a></nav>'
        )
        page = exhibits.rewrite_historical_account_links(source)
        self.assertIn("Historical: Create Account", page)
        self.assertIn("Historical: Manage Account", page)
        self.assertIn("Historical: Retrieve Password", page)
        for href in hrefs.values():
            self.assertIn(href, page)

    def test_historical_account_rewrite_ignores_unrelated_targets_and_scripts(self) -> None:
        unrelated = "/__offline/missing.html?requested=" + quote(
            "https://example.com/account/", safe=""
        )
        source = (
            '<script>var menu = "<a href="' + unrelated + '">Create Account</a>";</script>'
            '<p><a href="' + unrelated + '">Create Account</a></p>'
            '<p>Create Account</p>'
        )
        self.assertEqual(source, exhibits.rewrite_historical_account_links(source))

    def test_p1_context_is_mobile_visible_and_has_viewport(self) -> None:
        source = "<html><head><title>Legacy</title></head><body><p>Legacy page</p></body></html>"
        page = exhibits.transform_p1_page(source, "/misc/beta-signup.html")
        self.assertIn('name="viewport" content="width=device-width, initial-scale=1"', page)
        self.assertIn('width:100vw;max-width:none;margin:10px 0', page)

    @staticmethod
    def _tag_pair_counts(text: str, tag: str) -> tuple[int, int]:
        opening = len(re.findall(r"<" + tag + r"\b", text, flags=re.I))
        closing = len(re.findall(r"</" + tag + r"\s*>", text, flags=re.I))
        return opening, closing

    def test_real_frozen_structures_survive_visa_and_promotion_rewrites(self) -> None:
        visa_route = "/visa/index.html"
        visa_source = (ROOT / "offline/site" / visa_route.lstrip("/")).read_text(
            encoding="utf-8", errors="replace"
        )
        visa_derived = pages.disable_sensitive_forms(visa_source, route=visa_route)
        visa_page = exhibits.transform_p1_page(visa_derived, visa_route)
        for tag in ("a", "table", "tr", "td"):
            with self.subTest(route=visa_route, tag=tag):
                self.assertEqual(
                    self._tag_pair_counts(visa_derived, tag),
                    self._tag_pair_counts(visa_page, tag),
                )
        self.assertEqual(*self._tag_pair_counts(visa_page, "a"))
        visa_visible = self._visible(visa_page).casefold()
        self.assertIn("the 2008 page described additional card benefits", visa_visible)
        self.assertNotIn("click here for additional card benefits and services", visa_visible)

        promotion_route = "/misc/promotion.html"
        promotion_source = (
            ROOT / "offline/site" / promotion_route.lstrip("/")
        ).read_text(encoding="utf-8", errors="replace")
        promotion_derived = pages.disable_sensitive_forms(
            promotion_source, route=promotion_route
        )
        promotion_page = exhibits.transform_p1_page(
            promotion_derived, promotion_route
        )
        for tag in ("table", "tr", "td"):
            with self.subTest(route=promotion_route, tag=tag):
                self.assertEqual(
                    self._tag_pair_counts(promotion_derived, tag),
                    self._tag_pair_counts(promotion_page, tag),
                )
        redemption_start = promotion_page.find(
            "How the 2008 service described redemption"
        )
        self.assertGreaterEqual(redemption_start, 0)
        redemption_end = promotion_page.find("</td", redemption_start)
        self.assertGreater(redemption_end, redemption_start)
        redemption_region = promotion_page[redemption_start:redemption_end].casefold()
        self.assertIn("the 2008 page listed five steps for redemption", redemption_region)
        self.assertNotIn("<ol", redemption_region)
        self.assertNotIn("<li", redemption_region)
        self.assertNotIn(
            "in order to claim your in-game item, please follow these five steps",
            self._visible(promotion_page).casefold(),
        )

    @staticmethod
    def _visible(text: str) -> str:
        parser = exhibits._VisibleTextParser(text)
        parser.feed(text)
        parser.close()
        return html.unescape("".join(part for _start, _end, part in parser.parts))

    def test_reported_p1_requests_are_rewritten_in_real_frozen_pages(self) -> None:
        cases = {
            "/misc/beta-signup.html": (
                "email address for its invitation process",
                "please enter a valid email address",
                "Once you enter your information, you should receive",
            ),
            "/misc/promotion.html": (
                "instructions described selecting a region and realm",
                "you can enter your promotion code in the appropriate fields",
                "This will take you to another page with your in-game code",
            ),
            "/downloads/languagepack-en.xml": (
                "installer is not included in this archive",
                "To get started, please download",
                "click the install button",
            ),
            "/downloads/languagepack-es.xml": (
                "el instalador no está incluido",
                "Para participar, por favor descarga",
                "haz clic en él para que se inicie la instalación",
            ),
            "/downloads/other-downloads.html": (
                "IAK download; the software is not included",
                "download our World of Warcraft IAK now",
                "download our World of Warcraft IAK",
                "To upgrade to a full World of Warcraft or Burning Crusade account click here",
            ),
            "/downloads/index.html": (
                "game-client download requiring an account",
                "To download the World of Warcraft game client, click here",
            ),
            "/misc/promotion.html": (
                "The 2008 page listed five steps for redemption",
                "In order to claim your in-game item, please follow these five steps",
            ),
            "/misc/deals.html": (
                "2008 AT&T offer",
                "Sign up for AT&T High Speed Internet and Receive 3 Months of WoW FREE",
            ),
            "/ui/index.html": (
                "PC interface tool — 2008 software reference",
                "Download for PC",
            ),
        }
        for route, (expected, *removed) in cases.items():
            with self.subTest(route=route):
                source = (ROOT / "offline/site" / route.lstrip("/")).read_text(encoding="utf-8", errors="replace")
                # Exercise the same ordering used by the exporter before the
                # historical text pass; the source itself remains untouched.
                derived = pages.disable_sensitive_forms(source, route=route)
                derived = exhibits.transform_p1_page(derived, route)
                visible = self._visible(derived)
                self.assertIn(expected.casefold(), visible.casefold())
                for phrase in removed:
                    self.assertNotIn(phrase.casefold(), visible.casefold())


if __name__ == "__main__":
    unittest.main()
