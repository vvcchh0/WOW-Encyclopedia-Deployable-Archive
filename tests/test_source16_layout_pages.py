"""Portable exporter checks for Source16 layout route reuses."""

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


class Source16LayoutPagesTests(unittest.TestCase):
    target_ttip = "/info/items/images/tinfoilhat/ttip-tl.png"
    source_ttip = "/wrath/images/layout/ttip-tl.png"
    target_arrow = "/moltencore/images/backarrow.gif"
    source_arrow = "/wrath/images/layout/backarrow.gif"

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        from test_github_pages_export import GithubPagesExportTests

        base, site, manifest = GithubPagesExportTests()._fixture(root)
        payload = json.loads(manifest.read_text(encoding="utf-8"))

        marker = lambda route: (
            "/__offline/missing-image.svg?requested="
            + quote("http://www.worldofwarcraft.com" + route, safe="")
        )
        pages_to_add = {
            "info/items/tinfoilhat.xml": (
                "<html><head><title>Tinfoil</title></head><body><h1>Tinfoil</h1>"
                f'<img id="ttip" src="{marker(self.target_ttip)}"></body></html>'
            ).encode("utf-8"),
            "moltencore/index.html": (
                "<html><head><title>Molten</title></head><body><div class=\"footer\"><div class=\"legal\">"
                f'<q><a href="/"><img id="back" src="{marker(self.target_arrow)}" alt=""> Return</a></q>'
                "</div></div></body></html>"
            ).encode("utf-8"),
        }
        source_assets = {
            "wrath/images/layout/ttip-tl.png": b"ttip-source-bytes",
            "wrath/images/layout/ttip-tr.png": b"ttip-tr-source",
            "wrath/images/layout/ttip-t.png": b"ttip-t-source",
            "wrath/images/layout/ttip-l.png": b"ttip-l-source",
            "wrath/images/layout/ttip-r.png": b"ttip-r-source",
            "wrath/images/layout/ttipbg.png": b"ttipbg-source",
            "wrath/images/layout/ttip-bl.png": b"ttip-bl-source",
            "wrath/images/layout/ttip-br.png": b"ttip-br-source",
            "wrath/images/layout/ttip-b.png": b"ttip-b-source",
            "wrath/images/layout/backarrow.gif": b"arrow-source-bytes",
        }
        for relative, data in pages_to_add.items():
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            payload["files"].append({
                "route": "/" + relative,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com/" + relative,
            })
            payload["origin_index"]["www.worldofwarcraft.com/" + relative] = "/" + relative
        for relative, data in source_assets.items():
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            payload["files"].append({
                "route": "/" + relative,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "image/png" if relative.endswith(".png") else "image/gif",
                "kind": "image",
                "source_base_url": "http://www.worldofwarcraft.com/" + relative,
            })
            payload["origin_index"]["www.worldofwarcraft.com/" + relative] = "/" + relative
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return base, site, manifest

    def _bundle(self) -> SimpleNamespace:
        pairs = [
            ("/info/items/images/tinfoilhat/ttip-tl.png", "/wrath/images/layout/ttip-tl.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-tr.png", "/wrath/images/layout/ttip-tr.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-t.png", "/wrath/images/layout/ttip-t.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-l.png", "/wrath/images/layout/ttip-l.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-r.png", "/wrath/images/layout/ttip-r.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttipbg.png", "/wrath/images/layout/ttipbg.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-bl.png", "/wrath/images/layout/ttip-bl.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-br.png", "/wrath/images/layout/ttip-br.png", "/info/items/tinfoilhat.xml"),
            ("/info/items/images/tinfoilhat/ttip-b.png", "/wrath/images/layout/ttip-b.png", "/info/items/tinfoilhat.xml"),
            ("/moltencore/images/backarrow.gif", "/wrath/images/layout/backarrow.gif", "/moltencore/index.html"),
        ]
        records = tuple({
            "page_route": page,
            "target_route": target,
            "source_route": source,
            "source_original_url": "http://www.worldofwarcraft.com" + source,
            "source_capture_timestamp": "20080402045844",
            "source_memento_datetime": "fixture",
            "sha256": "a" * 64,
            "length": 12,
            "format": "GIF" if source.endswith(".gif") else "PNG",
            "dimensions": [24, 24] if source.endswith(".gif") else [7, 7],
            "frames": 1,
            "layout_role": "return-arrow" if source.endswith(".gif") else "corner-top-left",
            "classification": "layout_compatibility_reuse",
            "target_capture_timestamp": None,
        } for target, source, page in pairs)
        return SimpleNamespace(
            route_reuses={row["target_route"]: row["source_route"] for row in records},
            public_records=records,
            map_sha256="b" * 64,
            decision_sha256="c" * 64,
            source_manifest_sha256="d" * 64,
            per_page_records={
                "/info/items/tinfoilhat.xml": tuple(row for row in records if row["page_route"] == "/info/items/tinfoilhat.xml"),
                "/moltencore/index.html": tuple(row for row in records if row["page_route"] == "/moltencore/index.html"),
            },
        )

    def _export(self, root: Path, site: Path, manifest: Path, *, bundle=None, map_path=None):
        patcher = mock.patch.object(
            pages.source16_layout_compat,
            "load_layout_compatibility_bundle",
            return_value=bundle,
        )
        with patcher:
            return pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=root / "out",
                workspace_root=root,
                min_free_bytes=0,
                source16_layout_map=map_path,
            )

    def test_none_keeps_default_pipeline_without_loading_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.source16_layout_compat,
                "load_layout_compatibility_bundle",
                side_effect=AssertionError("layout loader must not run by default"),
            ) as loader:
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "out",
                    workspace_root=root,
                    min_free_bytes=0,
                    source16_layout_map=None,
                )
            loader.assert_not_called()
            self.assertNotIn("layout_compatibility_reused_target_paths", result["stats"])
            self.assertFalse((root / "out/info/items/images/tinfoilhat/ttip-tl.png").exists())

    def test_success_reuses_existing_image_and_records_public_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            bundle = self._bundle()
            result = self._export(root, site, manifest, bundle=bundle, map_path=Path("accepted-layout-map.json"))
            output = root / "out"
            prefix = pages.DEFAULT_BASE_PATH
            for record in bundle.public_records:
                source = Path(record["source_route"].lstrip("/"))
                target = Path(record["target_route"].lstrip("/"))
                self.assertEqual((output / source).read_bytes(), (site / source).read_bytes())
                self.assertFalse((output / target).exists())
            tinfoil = (output / "info/items/tinfoilhat.xml.html").read_text(encoding="utf-8")
            molten = (output / "moltencore/index.html").read_text(encoding="utf-8")
            self.assertIn(prefix + "wrath/images/layout/ttip-tl.png", tinfoil)
            self.assertIn(prefix + "wrath/images/layout/backarrow.gif", molten)
            self.assertNotIn("missing-image.svg?requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fitems%2Fimages%2Ftinfoilhat%2Fttip-tl.png", tinfoil)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertEqual(route_map["routes"][self.target_ttip], prefix + self.source_ttip.lstrip("/"))
            self.assertEqual(route_map["routes"][self.target_arrow], prefix + self.source_arrow.lstrip("/"))
            self.assertNotIn(self.target_ttip, route_map.get("aliases", {}))
            self.assertNotIn(self.target_arrow, route_map.get("aliases", {}))
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            top = provenance["layout_compatibility_reuse"]
            self.assertEqual(top["reused_target_paths"], 10)
            self.assertEqual(top["source_map_sha256"], bundle.map_sha256)
            self.assertEqual(top["decision_sha256"], bundle.decision_sha256)
            self.assertEqual(top["source_manifest_sha256"], bundle.source_manifest_sha256)
            self.assertEqual(top["classification"], "layout_compatibility_reuse")
            self.assertEqual(top["new_image_payloads"], 0)
            self.assertEqual(len(top["records"]), 10)
            self.assertTrue(all(record["target_capture_timestamp"] is None for record in top["records"]))
            for route, target in (("/info/items/tinfoilhat.xml", self.target_ttip), ("/moltencore/index.html", self.target_arrow)):
                page_record = next(row for row in provenance["files"] if row.get("route") == route)
                self.assertTrue(any(ref.get("target_route") == target for ref in page_record["layout_reuse_refs"]))
            self.assertEqual(result["stats"]["layout_compatibility_reused_target_paths"], 10)
            self.assertEqual(result["stats"]["layout_compatibility_pages"], 2)

    def test_target_conflict_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self._fixture(Path(tmp))
            conflict = site / self.target_ttip.lstrip("/")
            conflict.parent.mkdir(parents=True, exist_ok=True)
            conflict_data = b"preexisting target"
            conflict.write_bytes(conflict_data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append({
                "route": self.target_ttip,
                "output_path": "offline/site/" + self.target_ttip.lstrip("/"),
                "derived_sha256": hashlib.sha256(conflict_data).hexdigest(),
                "derived_length": len(conflict_data),
                "mime": "image/png",
                "kind": "image",
                "source_base_url": "http://www.worldofwarcraft.com" + self.target_ttip,
            })
            payload["origin_index"]["www.worldofwarcraft.com" + self.target_ttip] = self.target_ttip
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "target|collid|layout"):
                self._export(root, site, manifest, bundle=self._bundle(), map_path=Path("accepted-layout-map.json"))
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "out.partial").exists())


if __name__ == "__main__":
    unittest.main()
