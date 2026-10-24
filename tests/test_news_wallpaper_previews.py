from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

import export_github_pages as pages  # noqa: E402
import news_wallpaper_previews as previews  # noqa: E402


class NewsWallpaperPreviewTests(unittest.TestCase):
    def _fixture(self, root: Path):
        payload = b"accepted wallpaper bytes"
        spec = previews.NewsWallpaperPreview(
            news_page_route="/news/rss-test.xml",
            thumbnail_route="/news/images/tcg-test.jpg",
            wallpaper_page_route="/downloads/wallpapers/wallpaper-test.html",
            source_image_route="/downloads/wallpapers/images/tcg-test-800x.jpg",
            source_image_sha256=hashlib.sha256(payload).hexdigest(),
            source_image_length=len(payload),
            posted_date="10-31-06",
        )
        site = root / "site"
        relative = Path(spec.source_image_route.lstrip("/"))
        source = site / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(payload)
        records = {
            spec.news_page_route: {"route": spec.news_page_route, "kind": "html"},
            spec.source_image_route: {
                "route": spec.source_image_route,
                "output_path": (Path("site") / relative).as_posix(),
                "kind": "image",
                "mime": "image/jpeg",
                "derived_sha256": spec.source_image_sha256,
                "derived_length": spec.source_image_length,
            },
        }
        routes = {
            spec.news_page_route: "/base/news/rss-test.xml",
            spec.wallpaper_page_route: "/base/downloads/wallpapers/wallpaper-test.html",
            spec.source_image_route: "/base/downloads/wallpapers/images/tcg-test-800x.jpg",
        }
        return spec, site, records, routes, source

    def test_exact_missing_thumb_uses_linked_wallpaper_and_visible_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec, site, records, routes, _source = self._fixture(Path(tmp))
            validated = previews.validate_preview_sources(
                route_records=records,
                route_to_static=routes,
                source_site=site,
                workspace_root=Path(tmp),
                specs=(spec,),
            )
            original = (
                '<div class="news-image"><a href="/downloads/wallpapers/wallpaper-test.html">'
                '<img border="0" height="231" src="/news/images/tcg-test.jpg" width="165"></a></div>'
                '<img src="/news/images/other.jpg">'
            )
            result, items = previews.apply_news_wallpaper_previews(
                original,
                page_route=spec.news_page_route,
                route_to_static=routes,
                validated_sources=validated,
                specs=(spec,),
            )
            self.assertEqual(len(items), 1)
            self.assertIn('href="/downloads/wallpapers/wallpaper-test.html"', result)
            self.assertIn('src="/base/downloads/wallpapers/images/tcg-test-800x.jpg"', result)
            self.assertIn("Preview from linked wallpaper", result)
            self.assertIn("max-width:165px;max-height:231px;width:auto;height:auto;", result)
            self.assertNotIn('height="231"', result)
            self.assertNotIn('width="165"', result)
            self.assertIn('<img src="/news/images/other.jpg">', result)
            self.assertEqual(items[0]["original_thumbnail_added"], False)

    def test_wrong_parent_wallpaper_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec, site, records, routes, _source = self._fixture(Path(tmp))
            validated = previews.validate_preview_sources(
                route_records=records, route_to_static=routes, source_site=site,
                workspace_root=Path(tmp), specs=(spec,),
            )
            wrong_link = (
                '<a href="/downloads/wallpapers/wallpaper-other.html">'
                '<img src="/news/images/tcg-test.jpg"></a>'
            )
            with self.assertRaisesRegex(previews.NewsWallpaperPreviewError, "expected one exact linked thumbnail"):
                previews.apply_news_wallpaper_previews(
                    wrong_link, page_route=spec.news_page_route, route_to_static=routes,
                    validated_sources=validated, specs=(spec,),
                )

    def test_manifest_or_actual_source_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec, site, records, routes, source = self._fixture(Path(tmp))
            with self.assertRaisesRegex(previews.NewsWallpaperPreviewError, "approved source manifest SHA mismatch"):
                previews.validate_preview_sources(
                    route_records=records, route_to_static=routes, source_site=site,
                    workspace_root=Path(tmp), source_manifest_sha256="0" * 64, specs=(spec,),
                )
            records[spec.source_image_route]["derived_sha256"] = "0" * 64
            with self.assertRaisesRegex(previews.NewsWallpaperPreviewError, "manifest SHA mismatch"):
                previews.validate_preview_sources(
                    route_records=records, route_to_static=routes, source_site=site,
                    workspace_root=Path(tmp), specs=(spec,),
                )

            records[spec.source_image_route]["derived_sha256"] = spec.source_image_sha256
            source.write_bytes(b"drifted bytes")
            with self.assertRaisesRegex(previews.NewsWallpaperPreviewError, "source bytes drifted"):
                previews.validate_preview_sources(
                    route_records=records, route_to_static=routes, source_site=site,
                    workspace_root=Path(tmp), specs=(spec,),
                )

    def test_real_thumbnail_is_preserved_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec, site, records, routes, _source = self._fixture(Path(tmp))
            routes[spec.thumbnail_route] = "/base/news/images/tcg-test.jpg"
            validated = previews.validate_preview_sources(
                route_records=records, route_to_static=routes, source_site=site,
                workspace_root=Path(tmp), specs=(spec,),
            )
            original = (
                '<a href="/downloads/wallpapers/wallpaper-test.html">'
                '<img src="/news/images/tcg-test.jpg" width="165"></a>'
            )
            result, items = previews.apply_news_wallpaper_previews(
                original, page_route=spec.news_page_route, route_to_static=routes,
                validated_sources=validated, specs=(spec,),
            )
            self.assertEqual(result, original)
            self.assertEqual(items, [])
            self.assertEqual(validated, {})

    def test_unrelated_page_is_unchanged(self) -> None:
        original = '<img src="/news/images/tcg-test.jpg">'
        result, items = previews.apply_news_wallpaper_previews(
            original, page_route="/news/rss-other.xml", route_to_static={},
            validated_sources={},
        )
        self.assertEqual(result, original)
        self.assertEqual(items, [])

    def test_unsupported_source_export_keeps_legacy_news_html_behavior(self) -> None:
        from test_github_pages_export import GithubPagesExportTests

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest_path = GithubPagesExportTests()._fixture(Path(tmp))
            route = "/news/rss-10-2006.xml"
            relative = route.lstrip("/")
            news_data = (
                '<html><body><a href="/downloads/wallpapers/wallpaper86.html">'
                '<img src="/news/images/06-10/tcg-deathdealer.jpg"></a></body></html>'
            ).encode("utf-8")
            news_path = site / relative
            news_path.parent.mkdir(parents=True, exist_ok=True)
            news_path.write_bytes(news_data)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"].append({
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(news_data).hexdigest(),
                "derived_length": len(news_data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            output = base / "pages-unsupported-manifest"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest_path,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
            )
            page = (output / pages.static_rel_for_route(route, {"kind": "html"})).read_text(encoding="utf-8")
            self.assertNotIn("news-wallpaper-preview-caption", page)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            self.assertNotIn("news_wallpaper_preview_fallbacks", provenance)
            self.assertNotIn("news_wallpaper_preview_display_fallbacks", result["stats"])

    def test_frozen_specs_cover_only_five_exact_announcements(self) -> None:
        self.assertEqual(len(previews.APPROVED_PREVIEWS), 5)
        self.assertEqual(
            {item.news_page_route for item in previews.APPROVED_PREVIEWS},
            {"/news/rss-10-2006.xml", "/news/rss-11-2006.xml"},
        )
        self.assertEqual(len({item.thumbnail_route for item in previews.APPROVED_PREVIEWS}), 5)
        self.assertEqual(
            {
                (item.news_page_route, item.thumbnail_route, item.wallpaper_page_route, item.source_image_route)
                for item in previews.APPROVED_PREVIEWS
            },
            {
                ("/news/rss-10-2006.xml", "/news/images/06-10/tcg-deathdealer.jpg", "/downloads/wallpapers/wallpaper86.html", "/downloads/wallpapers/images/tcg2/tcg2-800x.jpg"),
                ("/news/rss-10-2006.xml", "/news/images/06-10/tcg-zormstonefury.jpg", "/downloads/wallpapers/wallpaper85.html", "/downloads/wallpapers/images/tcg1/tcg1-800x.jpg"),
                ("/news/rss-11-2006.xml", "/news/images/06-11/tcg-facesmash.jpg", "/downloads/wallpapers/wallpaper89.html", "/downloads/wallpapers/images/tcg5/tcg5-800x.jpg"),
                ("/news/rss-11-2006.xml", "/news/images/06-11/tcg-chromie.jpg", "/downloads/wallpapers/wallpaper88.html", "/downloads/wallpapers/images/tcg4/tcg4-800x.jpg"),
                ("/news/rss-11-2006.xml", "/news/images/06-11/tcg-retribution.jpg", "/downloads/wallpapers/wallpaper87.html", "/downloads/wallpapers/images/tcg3/tcg3-800x.jpg"),
            },
        )
        receipt = previews.provenance([{"news_page_route": "/news/rss-10-2006.xml", "thumbnail_route": "/news/images/x.jpg"}])
        self.assertEqual(receipt["original_payloads_added"], 0)


if __name__ == "__main__":
    unittest.main()
