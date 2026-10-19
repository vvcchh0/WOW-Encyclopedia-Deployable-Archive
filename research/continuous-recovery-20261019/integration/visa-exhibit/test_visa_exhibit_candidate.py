from __future__ import annotations

import re
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from export_historical_exhibits_candidate import VISA_IMAGE_ROUTES, load_candidate  # noqa: E402


class VisaExhibitCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exhibits = load_candidate()
        cls.prefix = "/WOW-Encyclopedia-Deployable-Archive/"

    @staticmethod
    def _source_fixture() -> str:
        return '''<!doctype html><html><head><title>World of Warcraft VISA Credit Card</title></head><body>
<form action="https://www.firstnational.com/apply"><input name="card"><button>Apply now!</button></form>
<div class="SignUpLink"><a href="https://www.visa.com">Sign Up for a World of Warcraft VISA Card</a></div>
<div class="applynowbutton" onmouseover="this.style.background='url(images/button_applynow_on.gif)'" onmouseout="this.style.background='url(images/pixel.gif)'"><a href="https://www.firstnational.com/welcome/DynamicApp">Apply now!</a></div>
<object data="images/slideshow.swf"><embed src="images/slideshow.swf"></object>
<img src="/visa/images/credit_back_1.jpg"><p>Click here for additional Card benefits and services.</p>
</body></html>'''

    def test_aliases_and_canonical_route_are_manifest_scoped(self) -> None:
        self.assertEqual(self.exhibits.canonical_exhibit_route("/visa"), "/visa/index.html")
        self.assertEqual(self.exhibits.canonical_exhibit_route("/visa/"), "/visa/index.html")
        self.assertEqual(self.exhibits.canonical_exhibit_route("/visa/index.html"), "/visa/index.html")
        self.assertEqual(
            self.exhibits.canonical_exhibit_route("/visa/reward"),
            "/visa/reward/index.html",
        )
        self.assertIsNone(self.exhibits.canonical_exhibit_route("/visa.html"))
        self.assertIsNone(self.exhibits.canonical_exhibit_route("/visa/benefits.jsp"))

    def test_visa_derivation_is_static_six_image_exhibit(self) -> None:
        output = self.exhibits.transform_derived_page(
            self._source_fixture(), "/visa/index.html", base_path=self.prefix
        )
        self.assertIn('class="historical-exhibit"', output)
        self.assertIn("2008 World of Warcraft Rewards Visa promotion", output)
        self.assertEqual(output.count("<figure data-visa-artwork="), 6)
        for image_route in VISA_IMAGE_ROUTES:
            self.assertIn(self.prefix + image_route.lstrip("/"), output)
        anchors = re.findall(r'<a\b[^>]*href="([^"]+)"', output, flags=re.I)
        self.assertEqual(
            anchors,
            [self.prefix, self.prefix + "visa/reward/index.html"],
        )
        for forbidden in (
            "<form",
            "<input",
            "<button",
            "<object",
            "<embed",
            "onmouseover",
            "onmouseout",
            "SignUpLink",
            "Apply now",
            "firstnational.com",
            "visa.com",
            "?source=",
        ):
            self.assertNotIn(forbidden.casefold(), output.casefold())
        self.assertNotIn("<script", output.casefold())

    def test_visa_transform_is_idempotent_and_reward_or_news_routes_remain_scoped(self) -> None:
        output = self.exhibits.transform_derived_page(
            self._source_fixture(), "/visa/index.html", base_path=self.prefix
        )
        self.assertEqual(
            output,
            self.exhibits.transform_derived_page(output, "/visa/index.html", base_path=self.prefix),
        )
        reward = self.exhibits.transform_derived_page(
            "<html><body>retired reward form</body></html>",
            "/visa/reward/index.html",
            base_path=self.prefix,
        )
        self.assertIn("button-have3.gif", reward)
        self.assertNotIn("credit_back_1.jpg", reward)
        news = "<html><body><p>ordinary news</p></body></html>"
        self.assertEqual(
            news,
            self.exhibits.transform_derived_page(news, "/news/rss-01-2007.xml", base_path=self.prefix),
        )


if __name__ == "__main__":
    unittest.main()
