"""Portable exporter checks for the six-image related talent UI bundle."""

from __future__ import annotations

import base64
import hashlib
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import export_github_pages as pages  # noqa: E402


_UI_EXPORT_AVAILABLE = (
    hasattr(pages, "related_talent_ui")
    and "related_talent_ui_map" in inspect.signature(pages.export_pages).parameters
)


@unittest.skipUnless(_UI_EXPORT_AVAILABLE, "root exporter UI bundle interface is not installed yet")
class RelatedTalentUIPagesTests(unittest.TestCase):
    """Exercise the exporter boundary with a small mocked accepted bundle."""

    targets = (
        "/shared/global/talents/images/talents/icon-over-grey.gif",
        "/shared/global/talents/images/talents/icon-over-green.gif",
        "/shared/global/talents/images/talents/icon-over-yellow.gif",
        "/shared/global/talents/includes/images/reset.gif",
        "/shared/global/talents/includes/images/resetall.gif",
        "/shared/global/talents/includes/images/printableversion.gif",
    )

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        from test_github_pages_export import GithubPagesExportTests

        base, site, manifest = GithubPagesExportTests()._fixture(root)
        records = json.loads(manifest.read_text(encoding="utf-8"))
        body_images = []
        for target in self.targets:
            marker = "/__offline/missing-image.svg?requested=" + quote(
                "http://www.worldofwarcraft.com" + target, safe=""
            )
            body_images.append(f'<img class="talent-ui-target" src="{marker}" alt="{target}">')
        text = (
            "<html><head><title>Druid talents</title></head>"
            "<body><h1>Druid talents</h1>"
            + "".join(body_images)
            + "</body></html>"
        ).encode("utf-8")
        target = site / "info/classes/druid/talents.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text)
        records["files"].append(
            {
                "route": "/info/classes/druid/talents.html",
                "output_path": "offline/site/info/classes/druid/talents.html",
                "derived_sha256": hashlib.sha256(text).hexdigest(),
                "derived_length": len(text),
                "kind": "html",
                "mime": "text/html; charset=UTF-8",
                "source_base_url": "http://www.worldofwarcraft.com/info/classes/druid/talents.html",
            }
        )
        records["origin_index"]["www.worldofwarcraft.com/info/classes/druid/talents.html"] = (
            "/info/classes/druid/talents.html"
        )
        manifest.write_text(json.dumps(records), encoding="utf-8")
        return base, site, manifest

    def _png(self, colour: bytes) -> bytes:
        # Valid 1x1 RGBA PNG bytes; no exporter behavior depends on dimensions.
        # The exact source bytes are asserted after export.
        return base64.b64decode(
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        ) + colour

    def _icon_bundle(self, *, collision: bool = False) -> SimpleNamespace:
        data = b"accepted-icon"
        route = "/style.css" if collision else "/shared/global/talents/druid/images/balance/fixture.jpg"
        asset = SimpleNamespace(
            route=route,
            relative=route.lstrip("/"),
            data=data,
            mime="image/jpeg",
            metadata={
                "sha256": hashlib.sha256(data).hexdigest(),
                "git_blob_sha1": "a" * 40,
                "repository_path": route.lstrip("/"),
            },
        )
        return SimpleNamespace(
            assets=(asset,),
            catalog_relative="__offline/related-talent-icons.json",
            catalog_bytes=b'{"classification":"later_related_source"}\n',
            estimated_bytes=len(data) + 43,
            source_metadata={
                "classification": "later_related_source",
                "original_capture_timestamp": None,
                "repository_url": "https://example.invalid/icon-source",
                "retrieved_utc": "2026-10-21T00:00:00+00:00",
            },
            per_class_counts={"druid": 1},
            notice_html='<p id="legacy-icon-notice">legacy icon notice</p>',
            map_sha256="b" * 64,
        )

    def _ui_bundle(self, *, collision: bool = False) -> SimpleNamespace:
        assets = []
        canonical_routes = [
            "/__offline/related-talent-ui/icon-over-grey.png",
            "/__offline/related-talent-ui/icon-over-green.png",
            "/__offline/related-talent-ui/icon-over-yellow.png",
            "/__offline/related-talent-ui/reset.png",
            "/__offline/related-talent-ui/resetall.png",
            "/__offline/related-talent-ui/printableversion.png",
        ]
        for index, (target, route) in enumerate(zip(self.targets, canonical_routes)):
            if collision and index == 0:
                route = "/style.css"
            data = self._png(bytes((index,)))
            assets.append(
                SimpleNamespace(
                    route=route,
                    relative=route.lstrip("/"),
                    target_route=target,
                    data=data,
                    mime="image/png",
                    metadata={
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "git_blob_sha1": "c" * 40,
                        "repository_path": "shared/global/talents/ui/" + Path(route).name,
                        "classification": "later_related_source",
                        "original_capture_timestamp": None,
                    },
                )
            )
        route_reuses = {
            target: asset.route for target, asset in zip(self.targets, assets)
        }
        if collision:
            route_reuses[self.targets[0]] = "/style.css"
        notice = (
            '<p id="related-talent-ui-notice" role="note">Talent data: 2008 archive. '
            'Some icons and interface images come from a later WotLK 3.3.5a calculator backup. '
            '<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-icons.json">Icon sources.</a> '
            '<a href="/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-ui.json">Interface sources.</a></p>'
        )
        return SimpleNamespace(
            assets=tuple(assets),
            route_reuses=route_reuses,
            catalog_relative="__offline/related-talent-ui.json",
            catalog_bytes=b'{"schema":"wow-related-talent-ui-catalog/v1"}\n',
            estimated_bytes=sum(len(asset.data) for asset in assets) + 49,
            source_metadata={
                "classification": "later_related_source",
                "original_capture_timestamp": None,
                "repository_url": "https://example.invalid/ui-source",
                "retrieved_utc": "2026-10-21T00:00:00+00:00",
            },
            notice_html=notice,
            map_sha256="d" * 64,
            decision_sha256="e" * 64,
            source_acceptance_sha256="f" * 64,
        )

    def _export(self, root: Path, site: Path, manifest: Path, *, ui=None, icons=None):
        kwargs = {
            "source_site": site,
            "manifest_path": manifest,
            "output": root / "out",
            "workspace_root": root,
            "min_free_bytes": 0,
        }
        if icons is not None:
            kwargs["related_talent_icon_map"] = Path("accepted-icons.json")
        if ui is not None:
            kwargs["related_talent_ui_map"] = Path("accepted-ui.json")
        with mock.patch.object(
            pages.related_talent_icons, "load_related_talent_bundle", return_value=icons
        ) as icon_loader:
            with mock.patch.object(
                pages.related_talent_ui, "load_related_talent_ui_bundle", return_value=ui
            ) as ui_loader:
                result = pages.export_pages(**kwargs)
        return result, icon_loader, ui_loader

    def test_none_default_has_no_ui_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.related_talent_ui, "load_related_talent_ui_bundle", side_effect=AssertionError("unexpected UI load")
            ) as loader:
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "out",
                    workspace_root=root,
                    min_free_bytes=0,
                )
            loader.assert_not_called()
            self.assertNotIn("related_talent_ui_assets", result["stats"])

    def test_success_maps_old_gifs_to_pngs_and_replaces_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            icon_bundle = self._icon_bundle()
            ui_bundle = self._ui_bundle()
            result, icon_loader, ui_loader = self._export(
                root, site, manifest, ui=ui_bundle, icons=icon_bundle
            )
            icon_loader.assert_called_once()
            ui_loader.assert_called_once()
            output = root / "out"
            for asset in ui_bundle.assets:
                self.assertEqual((output / asset.relative).read_bytes(), asset.data)
                self.assertFalse((output / asset.target_route.lstrip("/")).exists())
            page = (output / "info/classes/druid/talents.html").read_text(encoding="utf-8")
            self.assertEqual(page.count('id="__offline-related-talent-icons"'), 1)
            self.assertIn("Icon sources.", page)
            self.assertIn("Interface sources.", page)
            self.assertIn(
                "/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-icons.json", page
            )
            self.assertIn(
                "/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-ui.json", page
            )
            self.assertNotIn("legacy icon notice", page)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            for asset in ui_bundle.assets:
                expected = pages.DEFAULT_BASE_PATH + asset.relative
                self.assertEqual(route_map["routes"][asset.target_route], expected)
                self.assertEqual(route_map["routes"][asset.route], expected)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            ui_rows = [row for row in provenance["files"] if row.get("kind") == "related_talent_ui"]
            self.assertEqual(len(ui_rows), 6)
            for row in ui_rows:
                self.assertEqual(row["mime"], "image/png")
                self.assertEqual(row["role"], "later_related_talent_ui")
                self.assertEqual(row["source_refs"][0]["classification"], "later_related_source")
                self.assertIsNone(row["source_refs"][0]["original_capture_timestamp"])
                self.assertNotIn("payload_path", json.dumps(row))
            top = provenance["related_talent_ui"]
            self.assertEqual(top["ui_count"], 6)
            self.assertEqual(top["catalog_path"], ui_bundle.catalog_relative)
            self.assertEqual(top["source_map_sha256"], ui_bundle.map_sha256)
            self.assertEqual(result["stats"]["related_talent_ui_assets"], 6)
            self.assertEqual(result["stats"]["related_talent_ui_notice_pages"], 1)

    def test_ui_requires_icons_and_rejects_collision_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with self.assertRaisesRegex(pages.PagesExportError, "related talent icon"):
                pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "out",
                    workspace_root=root,
                    min_free_bytes=0,
                    related_talent_ui_map=Path("accepted-ui.json"),
                )
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())

        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with self.assertRaisesRegex(pages.PagesExportError, "collides"):
                self._export(root, site, manifest, ui=self._ui_bundle(collision=True), icons=self._icon_bundle())
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())


if __name__ == "__main__":
    unittest.main()
