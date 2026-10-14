from __future__ import annotations

import base64
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
import test_github_pages_export as github_export_tests  # noqa: E402


GIF_1X1 = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")


class RelatedImageOverlayTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path]:
        base, site, manifest = github_export_tests.GithubPagesExportTests()._fixture(base)
        return base, site, manifest

    def _map(self, base: Path, entries: list[dict], name: str = "supplement-map.json") -> Path:
        raw = base / "raw"
        raw.mkdir(exist_ok=True)
        materialized = []
        for entry in entries:
            item = dict(entry)
            filename = item.pop("filename")
            data = item.pop("data", GIF_1X1)
            source = raw / filename
            source.write_bytes(data)
            item.update(
                {
                    "kind": "image",
                    "local_path": str(Path("raw") / filename),
                    "mime": "image/gif",
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "length": len(data),
                    "cdx_digest": base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip("="),
                }
            )
            materialized.append(item)
        path = base / name
        path.write_text(json.dumps({"items": materialized}), encoding="utf-8")
        return path

    def _export(self, base: Path, site: Path, manifest: Path, *, primary=(), supplement=()):
        return pages.export_pages(
            source_site=site,
            manifest_path=manifest,
            output=base / "pages",
            workspace_root=base,
            max_bytes=500_000_000,
            min_free_bytes=0,
            image_source_maps=list(primary),
            supplement_image_source_maps=list(supplement),
        )

    def test_europe_hosts_same_path_are_namespaced_and_catalogued(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {
                        "filename": "eu-www.gif",
                        "logical_url": "http://www.wow-europe.com:80/images/same.gif",
                        "original": "https://www.wow-europe.com/images/same.gif",
                        "actual_timestamp": "20080401000000",
                        "indexed_capture_timestamp": "20080401000000",
                        "temporal_class": "baseline_2008",
                    },
                    {
                        "filename": "eu-bare.gif",
                        "logical_url": "https://wow-europe.com:443/images/same.gif",
                        "original": "http://wow-europe.com/images/same.gif",
                        "actual_timestamp": "20071201000000",
                        "indexed_capture_timestamp": "20071201000000",
                        "temporal_class": "pre_2008",
                    },
                    {
                        "filename": "main-pre.gif",
                        "logical_url": "http://worldofwarcraft.com:80/images/main-pre.gif",
                        "original": "https://www.worldofwarcraft.com/images/main-pre.gif",
                        "actual_timestamp": "20071202000000",
                        "indexed_capture_timestamp": "20071202000000",
                        "temporal_class": "pre_2008",
                    },
                    {
                        "filename": "karazhan-late.gif",
                        "logical_url": "https://worldofwarcraft.com:443/images/karazhan-late.gif",
                        "original": "http://www.worldofwarcraft.com/images/karazhan-late.gif",
                        "actual_timestamp": "20080512212653",
                        "indexed_capture_timestamp": "20080512212653",
                        "temporal_class": "late_2008",
                    },
                ],
            )
            before = (site / "article.xml").read_bytes()
            self._export(base, site, manifest, supplement=[source_map])
            output = base / "pages"
            self.assertEqual((site / "article.xml").read_bytes(), before)
            self.assertEqual((output / "_origins/www.wow-europe.com/images/same.gif").read_bytes(), GIF_1X1)
            self.assertEqual((output / "_origins/wow-europe.com/images/same.gif").read_bytes(), GIF_1X1)
            self.assertTrue((output / "images/main-pre.gif").is_file())
            self.assertTrue((output / "images/karazhan-late.gif").is_file())
            catalog = (output / "__offline/related-images/index.html").read_text(encoding="utf-8")
            self.assertIn("www.wow-europe.com", catalog)
            self.assertIn("wow-europe.com", catalog)
            self.assertIn("2008-04-01 00:00:00 UTC", catalog)
            self.assertIn("baseline_2008", catalog)
            self.assertIn("_origins/www.wow-europe.com/images/same.gif", catalog)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertIn("/__offline/related-images/index.html", route_map["routes"])
            self.assertEqual(
                route_map["routes"]["/__offline/related-images/index.html"],
                "/WOW-Encyclopedia-Deployable-Archive/__offline/related-images/index.html",
            )
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            overlays = [item for item in provenance["files"] if item.get("role") == "image_overlay"]
            self.assertEqual(len(overlays), 4)
            self.assertEqual({item["origin_namespace"] for item in overlays}, {"www.wow-europe.com", "wow-europe.com" , "www.worldofwarcraft.com"})
            self.assertEqual({item["supplement_strategy"] for item in overlays}, {"explicit_supplement_image_overlay"})
            self.assertEqual({item["temporal_class"] for item in overlays}, {"baseline_2008", "pre_2008", "late_2008"})
            catalog_records = [item for item in provenance["files"] if item.get("kind") == "related_images_index"]
            self.assertEqual(len(catalog_records), 1)
            self.assertEqual(catalog_records[0]["output_path"], "__offline/related-images/index.html")

    def test_primary_entry_point_remains_strict_and_unknown_supplement_host_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            pre_map = self._map(
                base,
                [{
                    "filename": "pre.gif",
                    "logical_url": "http://www.worldofwarcraft.com/pre.gif",
                    "original": "http://www.worldofwarcraft.com/pre.gif",
                    "actual_timestamp": "20071201000000",
                    "indexed_capture_timestamp": "20071201000000",
                    "temporal_class": "pre_2008",
                }],
                "pre-map.json",
            )
            with self.assertRaises(pages.PagesExportError):
                self._export(base, site, manifest, primary=[pre_map])

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            wrong_class = self._map(
                base,
                [{
                    "filename": "wrong-class.gif",
                    "logical_url": "http://www.worldofwarcraft.com/wrong-class.gif",
                    "original": "http://www.worldofwarcraft.com/wrong-class.gif",
                    "actual_timestamp": "20080401000000",
                    "indexed_capture_timestamp": "20080401000000",
                    "temporal_class": "pre_2008",
                }],
                "wrong-class-map.json",
            )
            with self.assertRaises(pages.PagesExportError):
                self._export(base, site, manifest, primary=[wrong_class])

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            external = self._map(
                base,
                [{
                    "filename": "external.gif",
                    "logical_url": "http://media.wow-europe.com/external.gif",
                    "original": "http://media.wow-europe.com/external.gif",
                    "actual_timestamp": "20080401000000",
                    "indexed_capture_timestamp": "20080401000000",
                    "temporal_class": "baseline_2008",
                }],
                "external-map.json",
            )
            with self.assertRaises(pages.PagesExportError):
                self._export(base, site, manifest, supplement=[external])

    def test_temporal_class_and_default_port_policy_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            mismatch = self._map(
                base,
                [{
                    "filename": "mismatch.gif",
                    "logical_url": "http://www.wow-europe.com:80/mismatch.gif",
                    "original": "http://www.wow-europe.com/mismatch.gif",
                    "actual_timestamp": "20081231235959",
                    "indexed_capture_timestamp": "20081231235959",
                    "temporal_class": "baseline_2008",
                }],
                "mismatch-map.json",
            )
            with self.assertRaises(pages.PagesExportError):
                self._export(base, site, manifest, supplement=[mismatch])

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            nondefault = self._map(
                base,
                [{
                    "filename": "nondefault.gif",
                    "logical_url": "http://www.wow-europe.com:8080/nondefault.gif",
                    "original": "http://www.wow-europe.com:8080/nondefault.gif",
                    "actual_timestamp": "20080401000000",
                    "indexed_capture_timestamp": "20080401000000",
                    "temporal_class": "baseline_2008",
                }],
                "nondefault-map.json",
            )
            with self.assertRaises(pages.PagesExportError):
                self._export(base, site, manifest, supplement=[nondefault])


if __name__ == "__main__":
    unittest.main()
