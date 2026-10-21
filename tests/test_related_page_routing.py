"""Former missing links may resolve only to accepted exact-origin readers."""
from pathlib import Path
import sys
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages as pages
import offline_mirror as mirror


class RelatedPageRoutingTests(unittest.TestCase):
    prefix = pages.DEFAULT_BASE_PATH
    original = "http://us.blizzard.com/blizzcast/archive/episode1.xml"
    route = "/__offline/related-sites/blizzcast/episode1.html"

    def localizer(self, enabled=True):
        return pages.PagesLocalizer(
            route_to_static={self.route: self.prefix + self.route.lstrip("/"),
                             "/__offline/missing.html": self.prefix + "__offline/missing.html",
                             "/__offline/missing-image.svg": self.prefix + "__offline/missing-image.svg"},
            aliases={}, origin_index={mirror.origin_key(self.original): self.route},
            base_path=self.prefix, validated_related_page_routes={self.route} if enabled else frozenset(),
        )

    def resolve(self, requested, *, enabled=True, context="navigation"):
        marker = "/__offline/missing.html?requested=" + quote(requested, safe="")
        recorder = mirror.ReferenceRecorder("/downloads/index.xml", "http://www.worldofwarcraft.com/downloads/index.xml")
        value = self.localizer(enabled).localize(marker, base_url="http://www.worldofwarcraft.com/downloads/index.xml",
                                                  context=context, recorder=recorder)
        return value, recorder

    def test_exact_accepted_page_heals_shared_menu_marker(self):
        value, recorder = self.resolve(self.original)
        self.assertEqual(value, self.prefix + self.route.lstrip("/"))
        self.assertEqual(recorder.records[-1]["reason"], "recovered accepted exact-origin historical reading page")

    def test_disabled_page_and_media_contexts_do_not_heal(self):
        for options in ({"enabled": False}, {"context": "image"}, {"context": "script"}):
            value, _ = self.resolve(self.original, **options)
            self.assertNotEqual(value, self.prefix + self.route.lstrip("/"))

    def test_same_path_other_origin_query_and_credentials_remain_missing(self):
        for requested in (
            self.original.replace("us.blizzard.com", "example.invalid"),
            self.original.replace("us.blizzard.com", "us.blizzard.com:8080"),
            self.original.replace("us.blizzard.com", "user@us.blizzard.com"),
            self.original + "?password=unused", self.original + "#unrestored",
        ):
            value, _ = self.resolve(requested)
            self.assertIn("__offline/missing.html?", value)

    def test_https_default_port_maps_same_accepted_original(self):
        value, _ = self.resolve(self.original.replace("http://us.blizzard.com", "https://us.blizzard.com:443"))
        self.assertEqual(value, self.prefix + self.route.lstrip("/"))


if __name__ == "__main__":
    unittest.main()
