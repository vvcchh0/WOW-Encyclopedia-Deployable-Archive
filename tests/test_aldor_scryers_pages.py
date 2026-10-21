"""Portable exporter checks for the opt-in Aldor/Scryers lore helper."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import export_github_pages as pages  # noqa: E402


class AldorScryersPagesTests(unittest.TestCase):
    page_route = "/info/basics/factions/aldorscryers/aldor-scryers.xml"
    token_route = "/info/basics/factions/aldorscryers/scripts/rewards-aldor-scryers-tokens.js"
    helper_relative = "__offline/aldor-scryers-lore.js"

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        from test_github_pages_export import GithubPagesExportTests

        base, site, manifest = GithubPagesExportTests()._fixture(root)
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        additions = {
            "info/basics/factions/aldorscryers/aldor-scryers.xml": (
                '<html><head><title>Aldor and Scryers</title>'
                '<script>var fake="</head>";</script></head><body>'
                "<h1>Aldor and The Scryers</h1><p>Historical faction details.</p>"
                "</body></html>",
                "html",
                "text/html; charset=UTF-8",
            ),
            "info/basics/factions/aldorscryers/scripts/rewards-aldor-scryers-tokens.js": (
                "var tokenData = {name: 'Aldor token'};\n",
                "js",
                "application/javascript",
            ),
        }
        for relative, (text, kind, mime) in additions.items():
            data = text.encode("utf-8")
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            route = "/" + relative
            payload["files"].append({
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": mime,
                "kind": kind,
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            payload["origin_index"]["www.worldofwarcraft.com" + route] = route
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return base, site, manifest

    def _bundle(self, *, data: bytes = b"/* accepted lore helper */\n") -> SimpleNamespace:
        generated = SimpleNamespace(
            relative=self.helper_relative,
            data=data,
            mime="application/javascript",
            sha256=hashlib.sha256(data).hexdigest(),
            length=len(data),
        )
        return SimpleNamespace(
            generated_file=generated,
            expected_page_route=self.page_route,
            source_metadata={
                "classification": "source16_text_reuse",
                "source_manifest_sha256": "c" * 64,
                "tokens_route": self.token_route,
                "tokens_sha256": "a" * 64,
                "network_requests": 0,
            },
        )

    def _export(self, base: Path, site: Path, manifest: Path, *, bundle=None):
        with mock.patch.object(
            pages.aldor_scryers_lore,
            "load_lore_bundle",
            return_value=bundle,
        ):
            return pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "out",
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
                restore_aldor_scryers_lore=True,
            )

    def test_default_off_does_not_load_or_emit_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.aldor_scryers_lore,
                "load_lore_bundle",
                side_effect=AssertionError("lore loader must remain opt-in"),
            ) as loader:
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=base / "out",
                    workspace_root=base,
                    min_free_bytes=0,
                )
            loader.assert_not_called()
            self.assertNotIn("aldor_scryers_lore_assets", result["stats"])
            self.assertFalse((base / "out" / self.helper_relative).exists())

    def test_enabled_writes_one_helper_injects_exact_page_and_records_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            bundle = self._bundle()
            with mock.patch.object(pages, "output_estimate", wraps=pages.output_estimate) as estimate:
                result = self._export(base, site, manifest, bundle=bundle)
            self.assertGreaterEqual(estimate.call_args.args[1], len(bundle.generated_file.data))
            output = base / "out"
            self.assertEqual((output / self.helper_relative).read_bytes(), bundle.generated_file.data)
            page = (output / "info/basics/factions/aldorscryers/aldor-scryers.xml.html").read_text(encoding="utf-8")
            helper_url = pages.DEFAULT_BASE_PATH + self.helper_relative
            marker = f'<script defer src="{helper_url}"></script>'
            self.assertEqual(page.count(marker), 1)
            self.assertLess(page.index(marker), page.rindex("</head>"))
            self.assertIn('var fake="</head>";', page)
            token = (output / self.token_route.lstrip("/")).read_text(encoding="utf-8")
            self.assertNotIn(self.helper_relative, token)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertEqual(route_map["routes"]["/" + self.helper_relative], helper_url)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            top = provenance["source16_lore_reuse"]
            self.assertEqual(top["classification"], "source16_text_reuse")
            self.assertEqual(top["generated_path"], self.helper_relative)
            self.assertEqual(top["generated_length"], len(bundle.generated_file.data))
            helper_row = next(row for row in provenance["files"] if row.get("output_path") == self.helper_relative)
            self.assertEqual(helper_row["source_refs"][0]["classification"], "source16_text_reuse")
            page_row = next(row for row in provenance["files"] if row.get("route") == self.page_route)
            self.assertIn("Aldor/Scryers lore helper", page_row["derivation_reason"])
            self.assertEqual(result["stats"]["aldor_scryers_lore_assets"], 1)
            self.assertEqual(result["stats"]["aldor_scryers_lore_pages"], 1)

    def test_helper_collision_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            data = b"existing helper route"
            relative = self.helper_relative
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            route = "/" + relative
            payload["files"].append({
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "application/javascript",
                "kind": "js",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "collides"):
                self._export(base, site, manifest, bundle=self._bundle())
            self.assertFalse((base / "out").exists())
            self.assertFalse((base / "out.partial").exists())

    def test_source_drift_error_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(
                pages.aldor_scryers_lore,
                "load_lore_bundle",
                side_effect=pages.aldor_scryers_lore.AldorScryersLoreError("Source16 manifest SHA mismatch"),
            ):
                with self.assertRaisesRegex(pages.PagesExportError, "manifest SHA mismatch"):
                    pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "out",
                        workspace_root=base,
                        min_free_bytes=0,
                        restore_aldor_scryers_lore=True,
                    )
            self.assertFalse((base / "out").exists())
            self.assertFalse((base / "out.partial").exists())


if __name__ == "__main__":
    unittest.main()
