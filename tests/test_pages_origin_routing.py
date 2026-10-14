from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import export_github_pages as pages
import offline_mirror as mirror


class PagesOriginRoutingTests(unittest.TestCase):
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"

    def setUp(self) -> None:
        self.localizer = pages.PagesLocalizer(
            route_to_static={
                "/images/example.jpg": self.prefix + "images/example.jpg",
                "/_origins/www.wow-europe.com/images/example.jpg": self.prefix + "_origins/www.wow-europe.com/images/example.jpg",
                "/__offline/missing-image.svg": self.prefix + "__offline/missing-image.svg",
            },
            aliases={},
            origin_index={
                "www.worldofwarcraft.com/images/example.jpg": "/images/example.jpg",
                "www.wow-europe.com/images/example.jpg": "/_origins/www.wow-europe.com/images/example.jpg",
            },
            base_path=self.prefix,
        )

    def localize(self, literal: str, base_url: str = "http://www.worldofwarcraft.com/index.xml") -> str:
        recorder = mirror.ReferenceRecorder("/index.xml", base_url)
        return self.localizer.localize(literal, base_url=base_url, context="image", recorder=recorder)

    def test_same_path_keeps_each_recorded_origin(self) -> None:
        self.assertEqual(self.localize("http://www.worldofwarcraft.com/images/example.jpg"), self.prefix + "images/example.jpg")
        self.assertEqual(self.localize("http://www.wow-europe.com/images/example.jpg"), self.prefix + "_origins/www.wow-europe.com/images/example.jpg")

    def test_uncollected_origin_does_not_borrow_main_site_image(self) -> None:
        for url in ["http://media.wow-europe.com/images/example.jpg", "http://uncollected.example/images/example.jpg"]:
            with self.subTest(url=url):
                self.assertIn("/__offline/missing-image.svg?", self.localize(url))
        self.assertIn("/__offline/missing-image.svg?", self.localize("/images/example.jpg", "http://forums.worldofwarcraft.com/forum-coc.html"))

    def test_frozen_local_namespace_and_support_urls_still_resolve(self) -> None:
        route = "/_origins/www.wow-europe.com/images/example.jpg"
        self.assertEqual(self.localize(route, "http://forums.worldofwarcraft.com/forum-coc.html"), self.prefix + route.lstrip("/"))
        self.assertEqual(self.localize("/__offline/missing-image.svg", "http://forums.worldofwarcraft.com/forum-coc.html"), self.prefix + "__offline/missing-image.svg")


if __name__ == "__main__":
    unittest.main()
