"""Portable exporter checks for the three accepted encyclopedia image reuses."""

from __future__ import annotations

import hashlib
import inspect
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


_EXPORT_AVAILABLE = (
    hasattr(pages, "related_encyclopedia_images")
    and "related_encyclopedia_image_map" in inspect.signature(pages.export_pages).parameters
)


@unittest.skipUnless(
    _EXPORT_AVAILABLE,
    "root exporter encyclopedia-image interface is not installed yet",
)
class RelatedEncyclopediaPagesTests(unittest.TestCase):
    page_routes = (
        "/info/encyclopedia/315.xml",
        "/info/encyclopedia/349.xml",
        "/info/encyclopedia/474.xml",
    )
    targets = (
        "/info/encyclopedia/images/articles/alleriawindrunner.jpg",
        "/info/encyclopedia/images/articles/cenarioncircle.jpg",
        "/info/encyclopedia/images/articles/malfurionstormrage.jpg",
    )
    canonical_routes = (
        "/__offline/related-encyclopedia-images/alleriawindrunner.jpg",
        "/__offline/related-encyclopedia-images/cenarioncircle.jpg",
        "/__offline/related-encyclopedia-images/malfurionstormrage.jpg",
    )
    source_image_urls = (
        "https://archivecraft.test/alleria.jpg",
        "https://archivecraft.test/cenarion.jpg",
        "https://archivecraft.test/malfurion.jpg",
    )
    source_page_urls = (
        "https://archivecraft.test/alleria/",
        "https://archivecraft.test/cenarion/",
        "https://archivecraft.test/malfurion/",
    )
    sizes = ((300, 353), (300, 418), (300, 326))

    def _jpeg_data(self) -> tuple[bytes, ...]:
        data: list[bytes] = []
        for size, colour in zip(self.sizes, ((180, 70, 40), (30, 120, 70), (60, 80, 180))):
            image = Image.new("RGB", size, colour)
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=90)
            data.append(output.getvalue())
        return tuple(data)

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
        for index, route in enumerate(self.page_routes):
            marker = "/__offline/missing-image.svg?requested=" + quote(
                "http://www.worldofwarcraft.com" + self.targets[index], safe=""
            )
            body = (
                "<html><head><title>Encyclopedia</title></head><body>"
                f"<h1>Article {index}</h1><p>Visible article text {index}</p>"
                f'<img class="article-illustration" src="{marker}" alt="Article {index}">'
                "</body></html>"
            ).encode("utf-8")
            self._add_record(site, manifest, route, body, kind="html", mime="text/html; charset=UTF-8")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return base, site, manifest_path

    def _bundle(self, manifest_path: Path, *, source_manifest_sha256: str | None = None) -> SimpleNamespace:
        data = self._jpeg_data()
        names = ("Alleria Windrunner", "Cenarion Circle", "Malfurion Stormrage")
        assets = []
        for index, payload in enumerate(data):
            width, height = self.sizes[index]
            asset = SimpleNamespace(
                route=self.canonical_routes[index],
                relative=self.canonical_routes[index].lstrip("/"),
                target_route=self.targets[index],
                data=payload,
                mime="image/jpeg",
                metadata={
                    "title": names[index],
                    "page_route": self.page_routes[index],
                    "target_route": self.targets[index],
                    "source_image_url": self.source_image_urls[index],
                    "source_page_url": self.source_page_urls[index],
                    "current_observed_utc": f"2026-10-21T08:19:{7 + index * 6:02d}.040896Z",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "length": len(payload),
                    "format": "JPEG",
                    "width": width,
                    "height": height,
                    "frames": 1,
                    "classification": "current_related_archive_source",
                    "original_capture_timestamp": None,
                },
            )
            assets.append(asset)
        route_reuses = {
            asset.target_route: asset.route
            for asset in assets
        }
        catalog = b'{"schema":"wow-related-encyclopedia-image-catalog/v1","image_count":3}\n'
        manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        return SimpleNamespace(
            assets=tuple(assets),
            route_reuses=route_reuses,
            catalog_relative="__offline/related-encyclopedia-images.json",
            catalog_bytes=catalog,
            estimated_bytes=sum(len(asset.data) for asset in assets) + len(catalog),
            source_metadata={
                "source_label": "ArchiveCraft community archive",
                "classification": "current_related_archive_source",
                "source_manifest_sha256": source_manifest_sha256 or manifest_sha,
                "original_capture_timestamp": None,
                "original_2008_images_recovered": 0,
                "source_checked_utc": "2026-10-21T08:37:15.733498+00:00",
            },
            notice_by_page={
                route: (
                    '<aside id="__offline-related-encyclopedia-images" role="note">'
                    f'Illustration from <a href="{self.source_page_urls[index]}" target="_blank" rel="noopener noreferrer">ArchiveCraft</a>.'
                    "</aside>"
                )
                for index, route in enumerate(self.page_routes)
            },
            map_sha256="a" * 64,
            decision_sha256="b" * 64,
            source_acceptance_sha256="c" * 64,
        )

    def _export(self, root: Path, site: Path, manifest: Path, *, bundle=None, map_path=None):
        with mock.patch.object(
            pages.related_encyclopedia_images,
            "load_related_encyclopedia_image_bundle",
            return_value=bundle,
        ) as loader:
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=root / "out",
                workspace_root=root,
                min_free_bytes=0,
                related_encyclopedia_image_map=map_path,
            )
        return result, loader

    def test_none_keeps_default_pipeline_without_loading_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.related_encyclopedia_images,
                "load_related_encyclopedia_image_bundle",
                side_effect=AssertionError("encyclopedia loader must not run by default"),
            ) as loader:
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "out",
                    workspace_root=root,
                    min_free_bytes=0,
                    related_encyclopedia_image_map=None,
                )
            loader.assert_not_called()
            self.assertNotIn("related_encyclopedia_image_assets", result["stats"])

    def test_success_reuses_canonical_jpegs_localizes_xml_and_records_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            bundle = self._bundle(manifest)
            result, loader = self._export(
                root, site, manifest, bundle=bundle, map_path=Path("accepted-encyclopedia-map.json")
            )
            loader.assert_called_once()
            output = root / "out"
            prefix = pages.DEFAULT_BASE_PATH
            for asset in bundle.assets:
                self.assertEqual((output / asset.relative).read_bytes(), asset.data)
                self.assertFalse((output / asset.target_route.lstrip("/")).exists())
            self.assertEqual(
                (output / bundle.catalog_relative).read_bytes(),
                bundle.catalog_bytes,
            )
            for index, (page_route, target, canonical) in enumerate(zip(self.page_routes, self.targets, self.canonical_routes)):
                page = (output / (page_route.lstrip("/") + ".html")).read_text(encoding="utf-8")
                self.assertIn(prefix + canonical.lstrip("/"), page)
                self.assertNotIn("missing-image.svg?requested=", page)
                self.assertEqual(page.count('id="__offline-related-encyclopedia-images"'), 1)
                self.assertIn(
                    bundle.notice_by_page[page_route],
                    page,
                )
                self.assertIn(
                    f'href="{self.source_page_urls[index]}" target="_blank" rel="noopener noreferrer"',
                    page,
                )
                self.assertNotIn(prefix + bundle.catalog_relative, page)

            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            for target, canonical in bundle.route_reuses.items():
                self.assertEqual(route_map["routes"][target], prefix + canonical.lstrip("/"))
                self.assertEqual(route_map["routes"][canonical], prefix + canonical.lstrip("/"))
                self.assertNotIn(target, route_map.get("aliases", {}))

            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            top = provenance["related_encyclopedia_images"]
            self.assertEqual(top["image_count"], 3)
            self.assertEqual(top["catalog_path"], bundle.catalog_relative)
            self.assertEqual(top["source_map_sha256"], bundle.map_sha256)
            self.assertEqual(top["route_reuses"], dict(bundle.route_reuses))
            self.assertEqual(top["original_2008_images_recovered"], 0)
            for asset in bundle.assets:
                row = next(item for item in provenance["files"] if item.get("route") == asset.route)
                reference = row["source_refs"][0]
                self.assertEqual(reference["classification"], "current_related_archive_source")
                self.assertIsNone(reference["original_capture_timestamp"])
                self.assertEqual(reference["current_observed_utc"], asset.metadata["current_observed_utc"])
                self.assertEqual(reference["source_page_url"], asset.metadata["source_page_url"])
                self.assertEqual(reference["source_image_url"], asset.metadata["source_image_url"])
            self.assertEqual(result["stats"]["related_encyclopedia_image_assets"], 3)
            self.assertEqual(result["stats"]["related_encyclopedia_notice_pages"], 3)

    def test_manifest_pin_mismatch_fails_before_output_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            bundle = self._bundle(manifest, source_manifest_sha256="d" * 64)
            with self.assertRaisesRegex(pages.PagesExportError, "manifest"):
                self._export(root, site, manifest, bundle=bundle, map_path=Path("accepted-encyclopedia-map.json"))
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())

    def test_target_canonical_and_alias_collisions_fail_before_output_creation(self) -> None:
        for mode in ("target", "canonical", "alias"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root, site, manifest_path = self._fixture(Path(tmp))
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                collision_route = self.targets[0] if mode != "canonical" else self.canonical_routes[0]
                if mode == "alias":
                    manifest["route_aliases"][self.targets[0]] = "/article.xml"
                else:
                    self._add_record(
                        site,
                        manifest,
                        collision_route,
                        b"preexisting collision",
                        kind="image",
                        mime="image/jpeg",
                    )
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                bundle = self._bundle(manifest_path)
                with self.assertRaisesRegex(pages.PagesExportError, "collid|existing resource|encyclopedia"):
                    self._export(
                        root,
                        site,
                        manifest_path,
                        bundle=bundle,
                        map_path=Path("accepted-encyclopedia-map.json"),
                    )
                self.assertFalse((root / "out").exists())
                self.assertFalse((root / "out.partial").exists())


if __name__ == "__main__":
    unittest.main()
