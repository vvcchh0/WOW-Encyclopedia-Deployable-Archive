"""Future-facing exporter seam tests for the single related guide image."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from urllib.parse import quote

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import export_github_pages as pages  # noqa: E402


class RelatedGuidePagesTests(unittest.TestCase):
    page_route = "/burningcrusade/townhall/bestiary.html"
    target_route = "/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg"
    dynamic_target_route = "/burningcrusade/townhall/images/bestiary/thumb-broken.jpg"
    canonical_route = "/__offline/related-guide-images/thumb-thebroken.jpg"
    source_image_url = "https://archivecraft.test/thumb-thebroken.jpg"
    source_page_url = "https://archivecraft.test/bestiary/"

    @staticmethod
    def _jpeg_data() -> bytes:
        output = io.BytesIO()
        Image.new("RGB", (237, 184), (90, 40, 130)).save(output, format="JPEG", quality=90)
        return output.getvalue()

    @staticmethod
    def _add_record(site: Path, manifest: dict, route: str, data: bytes, *, kind: str, mime: str) -> None:
        relative = route.lstrip("/")
        path = site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest["files"].append(
            {
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": mime,
                "kind": kind,
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            }
        )
        manifest["origin_index"]["www.worldofwarcraft.com" + route] = route

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        from test_github_pages_export import GithubPagesExportTests

        base, site, manifest_path = GithubPagesExportTests()._fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        marker = "/__offline/missing-image.svg?requested=" + quote(
            "http://www.worldofwarcraft.com" + self.target_route, safe=""
        )
        dynamic_marker = "/__offline/missing-image.svg?requested=" + quote(
            "http://www.worldofwarcraft.com" + self.dynamic_target_route, safe=""
        )
        body = (
            "<html><head><title>The Broken</title></head><body>"
            "<h1>The Broken</h1><p>Visible Bestiary text</p>"
            f'<img class="article-illustration" src="{marker}" alt="The Broken">'
            f'<img class="article-illustration" src="{dynamic_marker}" alt="The Broken dynamic">'
            "</body></html>"
        ).encode("utf-8")
        self._add_record(site, manifest, self.page_route, body, kind="html", mime="text/html; charset=UTF-8")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return base, site, manifest_path

    def _bundle(self, manifest_path: Path) -> SimpleNamespace:
        data = self._jpeg_data()
        asset = SimpleNamespace(
            route=self.canonical_route,
            relative=self.canonical_route.lstrip("/"),
            target_route=self.target_route,
            data=data,
            mime="image/jpeg",
            metadata={
                "title": "The Broken",
                "page_route": self.page_route,
                "target_route": self.target_route,
                "source_image_url": self.source_image_url,
                "source_page_url": self.source_page_url,
                "current_observed_utc": "2026-10-21T09:38:21.231103Z",
                "sha256": hashlib.sha256(data).hexdigest(),
                "length": len(data),
                "format": "JPEG",
                "width": 237,
                "height": 184,
                "frames": 1,
                "classification": "current_related_archive_source",
                "original_capture_timestamp": None,
                "source_processing_note": "Processing before retrieval is unknown.",
            },
        )
        catalog = b'{"schema":"wow-related-guide-image-catalog/v1","image_count":1}\n'
        return SimpleNamespace(
            assets=(asset,),
            route_reuses={
                self.target_route: self.canonical_route,
                self.dynamic_target_route: self.canonical_route,
            },
            catalog_relative="__offline/related-guide-images.json",
            catalog_bytes=catalog,
            estimated_bytes=len(data) + len(catalog),
            source_metadata={
                "source_label": "ArchiveCraft community archive",
                "classification": "current_related_archive_source",
                "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                "decision_sha256": "b" * 64,
                "source_acceptance_sha256": "c" * 64,
                "original_capture_timestamp": None,
                "original_2008_images_recovered": 0,
                "image_count": 1,
                "source_bytes": len(data),
                "source_checked_utc": "2026-10-21T09:45:38.516282+00:00",
            },
            notice_by_page={
                self.page_route: (
                    '<aside id="__offline-related-guide-images" role="note">'
                    f'Illustration from <a href="{self.source_page_url}" target="_blank" rel="noopener noreferrer">ArchiveCraft</a>.'
                    "</aside>"
                )
            },
            map_sha256="a" * 64,
            decision_sha256="b" * 64,
            source_acceptance_sha256="c" * 64,
        )

    def _export(self, root: Path, site: Path, manifest: Path, bundle: SimpleNamespace):
        with mock.patch.object(
            pages.related_guide_images,
            "load_related_guide_image_bundle",
            return_value=bundle,
        ) as loader:
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=root / "out",
                workspace_root=root,
                min_free_bytes=0,
                related_guide_image_map=Path("accepted-guide-map.json"),
            )
        return result, loader

    def test_success_reuses_canonical_jpeg_and_localizes_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, site, manifest = self._fixture(Path(temp))
            bundle = self._bundle(manifest)
            result, loader = self._export(root, site, manifest, bundle)
            loader.assert_called_once()
            output = root / "out"
            asset = bundle.assets[0]
            self.assertEqual((output / asset.relative).read_bytes(), asset.data)
            self.assertFalse((output / asset.target_route.lstrip("/")).exists())
            self.assertEqual((output / bundle.catalog_relative).read_bytes(), bundle.catalog_bytes)
            static_page = output / self.page_route.lstrip("/")
            if not static_page.exists():
                static_page = output / (self.page_route.lstrip("/") + ".html")
            page = static_page.read_text(encoding="utf-8")
            self.assertIn(pages.DEFAULT_BASE_PATH + asset.relative, page)
            self.assertNotIn("missing-image.svg?requested=", page)
            self.assertIn('id="__offline-related-guide-images"', page)
            self.assertIn(self.source_page_url, page)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertEqual(route_map["routes"][self.target_route], pages.DEFAULT_BASE_PATH + asset.relative)
            self.assertEqual(route_map["routes"][self.dynamic_target_route], pages.DEFAULT_BASE_PATH + asset.relative)
            self.assertEqual(result["stats"]["related_guide_image_assets"], 1)


if __name__ == "__main__":
    unittest.main()
