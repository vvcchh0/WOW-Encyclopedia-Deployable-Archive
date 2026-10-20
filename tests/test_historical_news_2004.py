from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import historical_exhibits as exhibits  # noqa: E402


class HistoricalNews2004Tests(unittest.TestCase):
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"

    def _fixture(self, image_source: str | None = None) -> str:
        image_source = image_source or self.prefix + "news/images/04-12/ordernow.jpg"
        return f'''<!doctype html><html><body>
<div class="postContainer">
<h3 class="title">World of Warcraft Now On Sale from the Blizzard Store - <small>Indoflaven on 12/16/04</small></h3>
<div class="postBody">
<a href="https://shop.blizzard.com/section1/#wow"><img src="{image_source}" border="0" width="210" height="89" align="right"></a>
<form action="https://shop.blizzard.com/section1/#wow"><input name="order"></form>
In order to claim your in-game item, follow the five steps below. New recruits were needed for the Horde and Alliance. World of Warcraft was nearly sold out in stores, but it was available in the Blizzard Online Store. <a href="https://shop.blizzard.com/section1/#wow">Head to our online store and get your copy now</a>.
</div>
</div>
<div class="postContainer"><h3 class="title">New World of Warcraft T-Shirts - <small>Indoflaven on 12/16/04</small></h3><div class="postBody">Sibling news remains intact.</div></div>
</body></html>'''

    def test_target_entry_becomes_static_and_preserves_sibling(self) -> None:
        source = self._fixture()
        output = exhibits.transform_derived_page(
            source, "/news/wow-news2004.html", base_path=self.prefix
        )
        self.assertIn("World of Warcraft Now On Sale from the Blizzard Store", output)
        self.assertIn("Indoflaven on 12/16/04", output)
        self.assertIn("New World of Warcraft T-Shirts", output)
        self.assertIn("Sibling news remains intact.", output)
        self.assertIn("On December 16, 2004, the notice reported that World of Warcraft was available from the Blizzard Online Store.", output)
        self.assertIn("Historical 2004 promotional artwork", output)
        self.assertIn(
            f'src="{self.prefix}news/images/04-12/ordernow.jpg"', output
        )
        target = output[: output.index("New World of Warcraft T-Shirts")]
        self.assertNotIn("shop.blizzard.com", target)
        self.assertNotIn("Head to our online store", target)
        self.assertNotIn("<form", target.casefold())
        self.assertNotIn("<input", target.casefold())
        self.assertNotIn("In order to claim your in-game item", target)
        figure = re.search(
            r'(?is)<figure\b[^>]*data-historical-exhibit=["\']news-2004-ordernow["\'][^>]*>.*?</figure>',
            output,
        )
        self.assertIsNotNone(figure)
        self.assertNotRegex(figure.group(0), r"(?i)<\s*a\b|\bhref\s*=")
        self.assertEqual(
            output,
            exhibits.transform_derived_page(
                output, "/news/wow-news2004.html", base_path=self.prefix
            ),
        )

    def test_route_and_localized_image_guards_leave_other_inputs_unchanged(self) -> None:
        source = self._fixture("https://www.worldofwarcraft.com/news/images/04-12/ordernow.jpg")
        self.assertEqual(
            source,
            exhibits.transform_derived_page(source, "/news/wow-news2004.html", base_path=self.prefix),
        )
        source = self._fixture()
        self.assertEqual(
            source,
            exhibits.transform_derived_page(source, "/news/wow-news2005.html", base_path=self.prefix),
        )

        wrong_date = self._fixture().replace("Indoflaven on 12/16/04", "Indoflaven on 12/17/04", 1)
        self.assertEqual(
            wrong_date,
            exhibits.transform_derived_page(wrong_date, "/news/wow-news2004.html", base_path=self.prefix),
        )

        wrong_title = self._fixture().replace(
            "World of Warcraft Now On Sale from the Blizzard Store",
            "World of Warcraft Now On Sale from a Retail Store",
            1,
        )
        self.assertEqual(
            wrong_title,
            exhibits.transform_derived_page(wrong_title, "/news/wow-news2004.html", base_path=self.prefix),
        )


if __name__ == "__main__":
    unittest.main()
