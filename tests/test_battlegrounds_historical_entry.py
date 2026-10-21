from __future__ import annotations

import html
from pathlib import Path
import sys
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import historical_exhibits as exhibits  # noqa: E402


class BattlegroundsHistoricalEntryTests(unittest.TestCase):
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"

    @staticmethod
    def _visible(text: str) -> str:
        parser = exhibits._VisibleTextParser(text)
        parser.feed(text)
        parser.close()
        return html.unescape("".join(part for _start, _end, part in parser.parts))

    def test_contest_page_historicalizes_visible_copy_and_removes_only_rules_button(self) -> None:
        source = """<html><head>
<script>var keep = "Blizzard is giving away a rare, life-size mannequin of a Night Elf female.";</script>
<style>.copy::after { content: "To enter the contest, take the best screen shot you can"; }</style>
</head><body>
<p>Blizzard is giving away a rare, life-size mannequin of a Night Elf female.</p>
<p>To enter the contest, take the best screen shot you can within one of the Battlegrounds Zones and submit it using the Web page link below by June 20th, 2005.</p>
<p>We will run them through the gauntlet of dev team scrutiny, and will announce the winners soon after. So train your photographer's eye on the Battlegrounds and good luck!</p>
<a href="rules.html;jsessionid=OLD"><img src="/shared/wow-com/images/buttons/button-continue.gif" alt="Continue"></a>
<a href="examples.html"><img src="example.jpg" alt="Example Entry">Example Entry</a>
</body></html>"""
        output = exhibits.transform_derived_page(
            source,
            exhibits.BATTLEGROUNDS_CONTEST_ROUTE,
            base_path=self.prefix,
        )
        visible = self._visible(output)
        self.assertIn("Blizzard announced a giveaway of a rare, life-size Night Elf female mannequin", visible)
        self.assertIn("historical exhibit accepts no submissions", visible)
        self.assertIn("planned publication of the winners", visible)
        self.assertNotIn("Blizzard is giving away a rare", visible)
        self.assertNotIn("To enter the contest", visible)
        self.assertNotIn("We will run them through", visible)
        self.assertNotIn("So train your photographer", visible)
        self.assertIn("historical-rules-note", output)
        self.assertNotIn("button-continue.gif", output)
        self.assertNotIn("href=\"rules.html", output)
        self.assertIn('href="examples.html"', output)
        self.assertIn('var keep = "Blizzard is giving away a rare, life-size mannequin of a Night Elf female.";', output)
        self.assertIn('content: "To enter the contest, take the best screen shot you can"', output)
        self.assertEqual(output, exhibits.transform_derived_page(output, exhibits.BATTLEGROUNDS_CONTEST_ROUTE, base_path=self.prefix))

    def test_continue_replacement_consumes_only_matching_anchor_and_preserves_neighbor(self) -> None:
        source = (
            '<p>Before</p>'
            '<a href="rules.html"><img src="/shared/wow-com/images/buttons/button-continue.gif" alt="Continue"></a>'
            '<a href="examples.html"><img src="example.jpg" alt="Example Entry">Example Entry</a>'
            '<p>After</p>'
        )
        output = exhibits.transform_battlegrounds_contest_page(source)
        self.assertEqual(output.count("</a>"), 1)
        self.assertNotIn('href="rules.html"', output)
        self.assertNotIn("button-continue.gif", output)
        self.assertIn(
            '<a href="examples.html"><img src="example.jpg" alt="Example Entry">Example Entry</a>',
            output,
        )
        self.assertIn("<p>Before</p>", output)
        self.assertIn("<p>After</p>", output)

    def test_contest_page_accepts_localized_missing_rules_anchor(self) -> None:
        requested = quote("http://www.worldofwarcraft.com/contests/05-06-09/rules.html", safe="")
        missing = f'{self.prefix}__offline/missing.html?requested={requested}&reason=external-or-uncollected-resource'
        source = (
            '<html><body><p>Blizzard is giving away a rare, life-size mannequin of a Night Elf female.</p>'
            f'<a href="{missing}"><img src="{missing.replace("missing.html", "missing-image.svg")}" alt=""></a>'
            "</body></html>"
        )
        output = exhibits.transform_derived_page(
            source,
            exhibits.BATTLEGROUNDS_CONTEST_ROUTE,
            base_path=self.prefix,
        )
        self.assertIn("historical-rules-note", output)
        self.assertNotIn("missing-image.svg", output)
        self.assertNotIn("href=\"" + missing, output)

    def test_news_transform_is_limited_to_exact_post_and_keeps_target_href(self) -> None:
        target_href = self.prefix + "contests/05-06-09/index.html"
        source = f"""<html><head>
<script>var keep = "Submit a Screenshot";</script><style>.x {{ content: "We will run them through the gauntlet"; }}</style>
</head><body>
<div class="postContainer"><h3 class="title">Insider Battlegrounds Screen Shot Contest<small> - Indoflaven on 6/14/05</small></h3>
<div class="postBody">
To celebrate the launch of the Battlegrounds System, Blizzard is giving away a rare, life-size mannequin of a Night Elf female.
<p>To enter the contest, take the best screen shot you can within one of the Battlegrounds Zones and submit it using the Web page link below by June 20th, 2005.</p>
<p>We will run them through the gauntlet of dev team scrutiny, and will announce the winners soon after. So train your photographer's eye on the Battlegrounds and good luck!</p>
<ul><li><a href="{target_href}">Submit a Screenshot</a></li></ul>
</div></div>
<div class="postContainer"><h3 class="title">Other News<small> - 6/14/05</small></h3>
<div class="postBody">Blizzard is giving away a rare, life-size mannequin of a Night Elf female. <a href="{target_href}">Submit a Screenshot</a></div></div>
</body></html>"""
        output = exhibits.transform_derived_page(source, exhibits.BATTLEGROUNDS_NEWS_ROUTE)
        visible = self._visible(output)
        target_start = visible.index("Insider Battlegrounds Screen Shot Contest")
        target_end = visible.index("Other News")
        target_visible = visible[target_start:target_end]
        neighbor_visible = visible[target_end:]
        self.assertIn("Blizzard announced a giveaway", target_visible)
        self.assertIn("historical exhibit accepts no submissions", target_visible)
        self.assertIn("planned publication of the winners", target_visible)
        self.assertIn("View historical contest", target_visible)
        self.assertNotIn("Submit a Screenshot", target_visible)
        self.assertIn("Blizzard is giving away a rare", neighbor_visible)
        self.assertIn("Submit a Screenshot", neighbor_visible)
        self.assertIn(f'<a href="{target_href}">View historical contest</a>', output)
        self.assertIn('var keep = "Submit a Screenshot";', output)
        self.assertIn('content: "We will run them through the gauntlet"', output)
        self.assertNotIn('data-historical-exhibit="p1"', output)
        self.assertEqual(output, exhibits.transform_derived_page(output, exhibits.BATTLEGROUNDS_NEWS_ROUTE))

    def test_other_routes_are_unchanged(self) -> None:
        source = "<html><body><p>Blizzard is giving away a rare, life-size mannequin of a Night Elf female.</p></body></html>"
        self.assertEqual(
            source,
            exhibits.transform_derived_page(source, "/news/wow-news-06-2006.html"),
        )


if __name__ == "__main__":
    unittest.main()
