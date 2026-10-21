"""Portable exporter checks for the eight talent point-box route reuses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import export_github_pages as pages  # noqa: E402


class TalentBoxLayoutPagesTests(unittest.TestCase):
    page_routes = (
        "/info/classes/druid/talents.html",
        "/info/classes/hunter/talents.html",
        "/info/classes/mage/talents.html",
        "/info/classes/paladin/talents.html",
        "/info/classes/priest/talents.html",
        "/info/classes/rogue/talents.html",
        "/info/classes/shaman/talents.html",
        "/info/classes/warlock/talents.html",
        "/info/classes/warrior/talents.html",
    )
    pairs = (
        ("bot-left.gif", (10, 13)),
        ("bot-right.gif", (10, 13)),
        ("bot.gif", (10, 13)),
        ("left.gif", (13, 10)),
        ("right.gif", (13, 10)),
        ("top-left.gif", (10, 13)),
        ("top-right.gif", (10, 13)),
        ("top.gif", (10, 13)),
    )
    target_prefix = "/shared/global/talents/includes/images/bot-box/"
    source_prefix = "/info/classes/includes-new/images/bot-box/"
    probe_route = "/info/classes/talent-box-probe.js"

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        from test_github_pages_export import GithubPagesExportTests

        base, site, manifest = GithubPagesExportTests()._fixture(root)
        payload = json.loads(manifest.read_text(encoding="utf-8"))

        target_routes = [self.target_prefix + name for name, _ in self.pairs]
        page_data = {}
        for page_route in self.page_routes:
            markers = "".join(
                f'<img class="talent-box" src="{self._marker(route)}" alt="">'
                for route in target_routes
            )
            text = (
                "<html><head><title>Talent page</title>"
                f'<script src="{self.probe_route}"></script></head><body>'
                f"<h1>{page_route}</h1><section>{markers}</section></body></html>"
            ).encode("utf-8")
            page_data[page_route] = text

        self._add_files(
            site,
            payload,
            page_data,
            kind="html",
            mime="text/html; charset=UTF-8",
        )
        probe = (
            "window.dynamicTalentBox = "
            f'"{self.target_prefix}bot-left.gif";'
        ).encode("utf-8")
        self._add_files(
            site,
            payload,
            {self.probe_route: probe},
            kind="js",
            mime="application/javascript",
        )
        source_data = {
            self.source_prefix + name: f"GIF-source-{name}".encode("ascii")
            for name, _ in self.pairs
        }
        self._add_files(
            site,
            payload,
            source_data,
            kind="image",
            mime="image/gif",
        )
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return base, site, manifest

    def _add_files(
        self,
        site: Path,
        payload: dict,
        files: dict[str, bytes],
        *,
        kind: str,
        mime: str,
    ) -> None:
        for route, data in files.items():
            relative = route.lstrip("/")
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            payload["files"].append(
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
            payload["origin_index"]["www.worldofwarcraft.com" + route] = route

    @staticmethod
    def _marker(route: str) -> str:
        requested = quote("http://www.worldofwarcraft.com" + route, safe="")
        return "/__offline/missing-image.svg?requested=" + requested

    def _bundle(self, *, missing_source: bool = False) -> SimpleNamespace:
        records = []
        route_reuses = {}
        for name, dimensions in self.pairs:
            target = self.target_prefix + name
            source = (
                "/info/classes/includes-new/images/bot-box/missing.gif"
                if missing_source
                else self.source_prefix + name
            )
            data = f"GIF-source-{name}".encode("ascii")
            record = {
                "page_routes": list(self.page_routes),
                "target_route": target,
                "source_route": source,
                "source_original_url": "http://www.worldofwarcraft.com" + source,
                "source_capture_timestamp": "20080402072440",
                "source_memento_datetime": "fixture",
                "sha256": hashlib.sha256(data).hexdigest(),
                "length": len(data),
                "format": "GIF",
                "dimensions": list(dimensions),
                "frames": 1,
                "layout_role": "talent-point-box",
                "classification": "layout_compatibility_reuse",
                "target_capture_timestamp": None,
            }
            records.append(record)
            route_reuses[target] = source
        records = tuple(records)
        return SimpleNamespace(
            route_reuses=route_reuses,
            public_records=records,
            map_sha256="b" * 64,
            decision_sha256="c" * 64,
            source_manifest_sha256="d" * 64,
            per_page_records={page: records for page in self.page_routes},
        )

    def _export(
        self,
        root: Path,
        site: Path,
        manifest: Path,
        *,
        bundle=None,
        map_path: Path | None = Path("accepted-talent-box-map.json"),
    ):
        patcher = mock.patch.object(
            pages.talent_box_layout,
            "load_talent_box_layout_bundle",
            return_value=bundle,
        )
        with patcher:
            return pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=root / "out",
                workspace_root=root,
                min_free_bytes=0,
                talent_box_layout_map=map_path,
            )

    def test_none_keeps_default_pipeline_without_loading_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.talent_box_layout,
                "load_talent_box_layout_bundle",
                side_effect=AssertionError("talent box loader must not run by default"),
            ) as loader:
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "out",
                    workspace_root=root,
                    min_free_bytes=0,
                    talent_box_layout_map=None,
                )
            loader.assert_not_called()
            self.assertNotIn("talent_box_layout_reused_target_paths", result["stats"])
            target = self.target_prefix + self.pairs[0][0]
            self.assertFalse((root / "out" / target.lstrip("/")).exists())

    def test_success_reuses_existing_gifs_and_records_all_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            bundle = self._bundle()
            result = self._export(root, site, manifest, bundle=bundle)
            output = root / "out"
            prefix = pages.DEFAULT_BASE_PATH
            for name, _ in self.pairs:
                source = self.source_prefix + name
                target = self.target_prefix + name
                self.assertEqual(
                    (output / source.lstrip("/")).read_bytes(),
                    (site / source.lstrip("/")).read_bytes(),
                )
                self.assertFalse((output / target.lstrip("/")).exists())

            first_page = (output / self.page_routes[0].lstrip("/")).read_text(encoding="utf-8")
            self.assertIn(prefix + self.source_prefix.lstrip("/") + "bot-left.gif", first_page)
            self.assertNotIn("missing-image.svg?requested=", first_page)
            probe = (output / self.probe_route.lstrip("/")).read_text(encoding="utf-8")
            self.assertIn(prefix + self.source_prefix.lstrip("/") + "bot-left.gif", probe)
            self.assertNotIn(self.target_prefix + "bot-left.gif", probe)

            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            for name, _ in self.pairs:
                target = self.target_prefix + name
                source = self.source_prefix + name
                self.assertEqual(route_map["routes"][target], prefix + source.lstrip("/"))
                self.assertNotIn(target, route_map.get("aliases", {}))

            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            top = provenance["talent_box_layout_compatibility"]
            self.assertEqual(top["classification"], "layout_compatibility_reuse")
            self.assertEqual(top["source_map_sha256"], bundle.map_sha256)
            self.assertEqual(top["decision_sha256"], bundle.decision_sha256)
            self.assertEqual(top["source_manifest_sha256"], bundle.source_manifest_sha256)
            self.assertEqual(top["reused_target_paths"], 8)
            self.assertEqual(top["new_image_payloads"], 0)
            self.assertEqual(top["target_original_images_recovered"], 0)
            self.assertEqual(len(top["records"]), 8)
            for page in self.page_routes:
                page_record = next(row for row in provenance["files"] if row.get("route") == page)
                self.assertEqual(len(page_record["layout_reuse_refs"]), 8)
            self.assertEqual(result["stats"]["talent_box_layout_reused_target_paths"], 8)
            self.assertEqual(result["stats"]["talent_box_layout_pages"], 9)

    def test_target_conflict_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            target = self.target_prefix + self.pairs[0][0]
            conflict = site / target.lstrip("/")
            conflict.parent.mkdir(parents=True, exist_ok=True)
            conflict_data = b"preexisting target"
            conflict.write_bytes(conflict_data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append(
                {
                    "route": target,
                    "output_path": "offline/site/" + target.lstrip("/"),
                    "derived_sha256": hashlib.sha256(conflict_data).hexdigest(),
                    "derived_length": len(conflict_data),
                    "mime": "image/gif",
                    "kind": "image",
                    "source_base_url": "http://www.worldofwarcraft.com" + target,
                }
            )
            payload["origin_index"]["www.worldofwarcraft.com" + target] = target
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "target|collid|talent box"):
                self._export(root, site, manifest, bundle=self._bundle())
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())

    def test_missing_canonical_source_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with self.assertRaisesRegex(pages.PagesExportError, "source|canonical|talent box"):
                self._export(root, site, manifest, bundle=self._bundle(missing_source=True))
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())


if __name__ == "__main__":
    unittest.main()
