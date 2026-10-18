from __future__ import annotations

import hashlib
import html
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402
import historical_exhibits as exhibits  # noqa: E402

FROZEN_PAGE = ROOT / ".scratch/pages-resources-20261018-v27/news/rss-02-2007.xml.html"
FROZEN_IMAGE = ROOT / ".scratch/pages-resources-20261018-v27/news/images/07-02/upgradenow.gif"


class HistoricalNewsUpgradeTests(unittest.TestCase):
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"
    route = "/news/rss-02-2007.xml"

    @staticmethod
    def _visible(text: str) -> str:
        parser = exhibits._VisibleTextParser(text)
        parser.feed(text)
        parser.close()
        return html.unescape("".join(part for _start, _end, part in parser.parts))

    def _fixture(self) -> str:
        return f'''<!doctype html>
<html><head></head><body>
<div id="outside-copy">
<div class="menuFiller"><a href="{self.prefix}__offline/missing.html?requested=http%3A%2F%2Fsignup.worldofwarcraft.com%2F">Create Account</a></div>
All you need to do is:
Login to <a href="{self.prefix}__offline/missing.html?requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2F">Manage Account</a>
Enter your credit card information
</div>
<div class="news-expand" id="news2-1-07-1212">
<div class="news-listing" onclick="toggleEntry('target','')">
<h1><a href="javascript:dummyFunction();">Burning Crusade Direct Online Upgrade Now Available</a></h1>
<description>
You can now buy account-upgrade keys and download the game client for World of Warcraft: The Burning Crusade directly through the account-management section of www.worldofwarcraft.com. The direct online upgrade method is the most convenient way to upgrade to The Burning Crusade and join the millions of players who are already adventuring beyond the Dark Portal.
<br><br>
All you need to do is:
<blockquote>
1. Login to <a href="{self.prefix}__offline/missing.html?requested=account">Account Management</a><br>
2. Click The Burning Crusade "Download Now" button<br>
3. Enter your credit card information<br>
4. Follow the link to download The Burning Crusade game client
</blockquote>
That's it! If you haven't upgraded your account yet, now's your chance to take your World of Warcraft experience to the next level, whenever you want.
</description>
<style>
.upgradenow {{ width:377px; height:74px; background:url("{self.prefix}news/images/07-02/upgradenow.gif") 0 0 no-repeat; }}
.unrelated {{ color: red; }}
</style>
<div class="empty-before"><a href="/keep-this-empty-anchor"></a></div>
<div style="text-align:center;"><div class="upgradenow">
<a href="{self.prefix}__offline/missing.html?requested=account/burning-crusade-direct-online-upgrade.html"></a>
</div></div>
</div>
</div>
<div class="news-listing" onclick="toggleEntry('neighbor','')">
<a href="javascript:dummyFunction();">Neighbor News</a><img src="{self.prefix}news/images/neighbor.jpg">
</div>
<script>var preserved = "Enter your credit card information";</script>
</body></html>'''

    def test_fixture_becomes_static_historical_artwork(self) -> None:
        derived = pages.disable_sensitive_forms(self._fixture(), route=self.route)
        output = exhibits.transform_derived_page(derived, self.route, base_path=self.prefix)
        bounds = exhibits._news_upgrade_entry_bounds(output)
        self.assertIsNotNone(bounds)
        target_visible = self._visible(output[bounds[0] : bounds[1]])
        figure_match = re.search(r"(?is)<figure\b[^>]*data-historical-exhibit=[\"']news-upgrade-artwork[\"'][^>]*>.*?</figure>", output)
        self.assertIsNotNone(figure_match)
        figure = figure_match.group(0)

        self.assertIn("Burning Crusade Direct Online Upgrade — 2007 Historical Exhibit", target_visible)
        self.assertIn("Historical steps described in the February 2007 notice", target_visible)
        for phrase in (
            "All you need to do",
            "Login to Account Management",
            'Click The Burning Crusade "Download Now" button',
            "Enter your credit card information",
            "Follow the link to download The Burning Crusade game client",
        ):
            self.assertNotIn(phrase.casefold(), target_visible.casefold())
        self.assertIn("Historical 2007 artwork", figure)
        self.assertIn("static exhibit artwork", figure)
        self.assertIn(self.prefix + "news/images/07-02/upgradenow.gif", figure)
        self.assertIn('width="377" height="148"', figure)
        self.assertIn("max-width:377px", figure)
        self.assertIn("margin:1em auto", figure)
        self.assertNotRegex(figure, r"(?i)<\s*a\b|\bhref\s*=|<\s*form\b|\bon(?:click|mouseover|mouseout)\s*=")
        self.assertNotIn(".upgradenow", output)
        self.assertIn(".unrelated", output)
        self.assertIn("class=\"empty-before\"><a href=\"/keep-this-empty-anchor\"></a>", output)

        self.assertIn('id="news2-1-07-1212"', output)
        self.assertIn("toggleEntry('target','')", output)
        self.assertIn("toggleEntry('neighbor','')", output)
        self.assertIn("Neighbor News", output)
        self.assertIn(self.prefix + "news/images/neighbor.jpg", output)
        self.assertIn('var preserved = "Enter your credit card information"', output)
        self.assertIn("All you need to do is:", output)
        self.assertIn(
            f'Login to <a href="{self.prefix}__offline/missing.html?requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Faccount%2F">Historical: Manage Account</a>',
            output,
        )
        self.assertIn("Historical: Create Account", output)
        self.assertEqual(
            output,
            exhibits.transform_derived_page(output, self.route, base_path=self.prefix),
        )
        outside_start = output.index('<div id="outside-copy">')
        target_start = output.index('<div class="news-expand" id="news2-1-07-1212">')
        self.assertLess(outside_start, target_start)
        globally_rewritten = exhibits.rewrite_historical_account_links(
            derived, base_path=self.prefix
        )
        self.assertEqual(
            globally_rewritten[outside_start: globally_rewritten.index('<div class="news-expand"')],
            output[outside_start:target_start],
        )

    @unittest.skipUnless(
        FROZEN_PAGE.is_file() and FROZEN_IMAGE.is_file(),
        "optional frozen v27 integration input is unavailable",
    )
    def test_frozen_v27_page_is_read_only_input_and_gif_is_unchanged(self) -> None:
        self.assertTrue(FROZEN_IMAGE.is_file(), FROZEN_IMAGE)
        source = FROZEN_PAGE.read_text(encoding="utf-8", errors="replace")
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        image_hash = hashlib.sha256(FROZEN_IMAGE.read_bytes()).hexdigest()

        output = exhibits.transform_derived_page(source, self.route)
        visible = self._visible(output)
        self.assertIn("Historical 2007 artwork", output)
        self.assertIn("/WOW-Encyclopedia-Deployable-Archive/news/images/07-02/upgradenow.gif", output)
        self.assertIn("toggleEntry(&#x27;2-1-07-1212&#x27;,&#x27;&#x27;)", output)
        self.assertEqual(output, exhibits.transform_derived_page(output, self.route))
        self.assertNotIn("Enter your credit card information", visible)
        self.assertNotIn('Click The Burning Crusade "Download Now" button', visible)
        self.assertNotIn("Follow the link to download The Burning Crusade game client", visible)
        figure = re.search(r"(?is)<figure\b[^>]*data-historical-exhibit=[\"']news-upgrade-artwork[\"'][^>]*>.*?</figure>", output)
        self.assertIsNotNone(figure)
        self.assertNotRegex(figure.group(0), r"(?i)<\s*a\b|\bhref\s*=|<\s*form\b|\bon(?:click|mouseover|mouseout)\s*=")
        self.assertEqual(source_hash, hashlib.sha256(FROZEN_PAGE.read_bytes()).hexdigest())
        self.assertEqual(image_hash, hashlib.sha256(FROZEN_IMAGE.read_bytes()).hexdigest())

    def test_non_target_news_route_is_unchanged(self) -> None:
        source = '<html><body><p>Enter your credit card information</p><script>toggleEntry(1)</script></body></html>'
        self.assertEqual(source, exhibits.transform_derived_page(source, "/news/rss-03-2007.xml"))


if __name__ == "__main__":
    unittest.main()
