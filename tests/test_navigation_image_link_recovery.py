from __future__ import annotations

from pathlib import Path
import sys
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402
import offline_mirror as mirror  # noqa: E402


class NavigationImageLinkRecoveryTests(unittest.TestCase):
    prefix = pages.DEFAULT_BASE_PATH
    source_url = "http://www.worldofwarcraft.com/news/rss-08-2007.xml"
    image_url = "http://www.worldofwarcraft.com/news/images/07-08/ss01.jpg"
    image_route = "/news/images/07-08/ss01.jpg"

    def _localizer(
        self,
        *,
        validated_routes: set[str] | frozenset[str] = frozenset(),
        extra_routes: dict[str, str] | None = None,
        extra_origins: dict[str, str] | None = None,
    ) -> pages.PagesLocalizer:
        route_to_static = {
            "/__offline/missing.html": self.prefix + "__offline/missing.html",
            "/__offline/missing-image.svg": self.prefix + "__offline/missing-image.svg",
            self.image_route: self.prefix + self.image_route.lstrip("/"),
        }
        route_to_static.update(extra_routes or {})
        origin_index = {mirror.origin_key(self.image_url): self.image_route}
        origin_index.update(extra_origins or {})
        return pages.PagesLocalizer(
            route_to_static=route_to_static,
            aliases={},
            origin_index=origin_index,
            base_path=self.prefix,
            validated_navigation_image_routes=validated_routes,
        )

    def _marker(self, requested: str) -> str:
        return (
            "/__offline/missing.html?source="
            + quote(self.source_url, safe="")
            + "&requested="
            + quote(requested, safe="")
            + "&reason=invalid-overlay-or-uncollected-site-resource"
        )

    def _localize(
        self,
        localizer: pages.PagesLocalizer,
        literal: str,
        *,
        context: str = "navigation",
        base_url: str | None = None,
    ) -> tuple[str, mirror.ReferenceRecorder]:
        base_url = base_url or self.source_url
        recorder = mirror.ReferenceRecorder("/news/rss-08-2007.xml", base_url)
        result = localizer.localize(literal, base_url=base_url, context=context, recorder=recorder)
        return result, recorder

    def test_validated_exact_origin_jpg_recovers_and_records_reason(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        result, recorder = self._localize(localizer, self._marker(self.image_url))

        self.assertEqual(result, self.prefix + self.image_route.lstrip("/"))
        recovered = [row for row in recorder.records if row["action"] == "localized"]
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0]["reason"], "recovered validated exact-origin raster navigation image")
        self.assertEqual(recovered[0]["resolved_url"], self.image_url)

    def test_default_http_and_https_ports_are_normalized_by_origin_key(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        for requested in (
            "http://www.worldofwarcraft.com:80/news/images/07-08/ss01.jpg",
            "https://www.worldofwarcraft.com:443/news/images/07-08/ss01.jpg",
        ):
            with self.subTest(requested=requested):
                result, _recorder = self._localize(localizer, self._marker(requested))
                self.assertEqual(result, self.prefix + self.image_route.lstrip("/"))

    def test_root_relative_source_marker_is_healed_by_html_pipeline(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        recorder = mirror.ReferenceRecorder("/news/rss-08-2007.xml", self.source_url)
        source = f'<html><body><a href="{self._marker(self.image_url)}">Screenshot</a></body></html>'

        derived = mirror.rewrite_html(
            source,
            base_url=self.source_url,
            localizer=localizer,
            recorder=recorder,
            source_sha="fixture",
            compat_assets=[],
        )

        self.assertIn(self.prefix + self.image_route.lstrip("/"), derived)
        self.assertNotIn("__offline/missing.html?", derived)

    def test_missing_html_needs_explicit_validated_route(self) -> None:
        localizer = self._localizer()
        result, _recorder = self._localize(localizer, self._marker(self.image_url))

        self.assertIn(self.prefix + "__offline/missing.html?", result)
        self.assertIn("requested=", result)

    def test_same_path_other_origin_does_not_borrow_image(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        result, _recorder = self._localize(
            localizer,
            self._marker("http://www.wow-europe.com/news/images/07-08/ss01.jpg"),
        )

        self.assertIn(self.prefix + "__offline/missing.html?", result)

    def test_non_raster_html_query_credentials_and_port_stay_missing(self) -> None:
        html_route = "/news/landing.html"
        html_url = "http://www.worldofwarcraft.com/news/landing.html"
        mismatched_route = "/news/mismatched.jpg"
        mismatched_url = "http://www.worldofwarcraft.com/news/mismatched.jpg"
        svg_route = "/news/diagram.svg"
        svg_url = "http://www.worldofwarcraft.com/news/diagram.svg"
        localizer = self._localizer(
            validated_routes={self.image_route, html_route, mismatched_route, svg_route},
            extra_routes={
                html_route: self.prefix + html_route.lstrip("/"),
                mismatched_route: self.prefix + "news/mismatched.html",
                svg_route: self.prefix + svg_route.lstrip("/"),
            },
            extra_origins={
                mirror.origin_key(html_url): html_route,
                mirror.origin_key(mismatched_url): mismatched_route,
                mirror.origin_key(svg_url): svg_route,
            },
        )
        cases = (
            html_url,
            mismatched_url,
            svg_url,
            self.image_url + "?variant=full",
            self.image_url + "#full",
            "http://user:password@www.worldofwarcraft.com/news/images/07-08/ss01.jpg",
            "http://@www.worldofwarcraft.com/news/images/07-08/ss01.jpg",
            "http://www.worldofwarcraft.com:8080/news/images/07-08/ss01.jpg",
        )
        for requested in cases:
            with self.subTest(requested=requested):
                result, _recorder = self._localize(localizer, self._marker(requested))
                self.assertIn(self.prefix + "__offline/missing.html?", result)

    def test_missing_html_does_not_recover_outside_navigation_context(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        result, _recorder = self._localize(localizer, self._marker(self.image_url), context="image")

        self.assertIn(self.prefix + "__offline/missing.html?", result)

    def test_project_prefixed_marker_is_preserved_by_early_return(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        project_marker = self.prefix + self._marker(self.image_url).lstrip("/")
        result, recorder = self._localize(localizer, project_marker)

        self.assertEqual(result, project_marker)
        self.assertEqual(recorder.records[-1]["reason"], "already Pages-prefixed")

    def test_existing_missing_image_recovery_is_unchanged(self) -> None:
        localizer = self._localizer()
        marker = (
            "/__offline/missing-image.svg?source="
            + quote(self.source_url, safe="")
            + "&requested="
            + quote(self.image_url, safe="")
            + "&reason=external-or-uncollected-resource"
        )
        result, _recorder = self._localize(localizer, marker, context="image")

        self.assertEqual(result, self.prefix + self.image_route.lstrip("/"))

    def test_existing_compatibility_alias_recovery_is_unchanged(self) -> None:
        old_url = "http://www.worldofwarcraft.com/info/basics/dailyquests.shtml"
        old_route = "/info/basics/dailyquests.shtml"
        canonical_route = "/info/basics/dailyquests.html"
        localizer = pages.PagesLocalizer(
            route_to_static={
                "/__offline/missing.html": self.prefix + "__offline/missing.html",
                canonical_route: self.prefix + canonical_route.lstrip("/"),
            },
            aliases={old_route: canonical_route},
            origin_index={},
            base_path=self.prefix,
            validated_navigation_image_routes=frozenset(),
        )
        result, _recorder = self._localize(localizer, self._marker(old_url))

        self.assertEqual(result, self.prefix + canonical_route.lstrip("/"))

    def test_recovered_output_is_idempotent(self) -> None:
        localizer = self._localizer(validated_routes={self.image_route})
        first, _recorder = self._localize(localizer, self._marker(self.image_url))
        second, recorder = self._localize(localizer, first)

        self.assertEqual(second, first)
        self.assertEqual(recorder.records[-1]["reason"], "already Pages-prefixed")


if __name__ == "__main__":
    unittest.main()
