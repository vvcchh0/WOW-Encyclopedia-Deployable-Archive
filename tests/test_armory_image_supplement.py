#!/usr/bin/env python3
"""Focused tests for the exact Armory supplement host/path extension.

The accepted inputs are the frozen public-copy receipts, so the tests exercise
the exporter with the same US/EU PNG bytes that the next recovery overlay will
use.  The fixtures are temporary and no network is used.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import export_github_pages as pages  # noqa: E402
from test_related_image_overlay import RelatedImageOverlayTests  # noqa: E402


SOURCE_RECEIPTS = (
    ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch1-source-acceptance.json",
    ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch2-source-acceptance.json",
)
PUBLIC_RECEIPTS = (
    ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch1-public-copy-acceptance.json",
    ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch2-public-copy-acceptance.json",
)
ARMORY_HOSTS = {"www.wowarmory.com", "armory.wow-europe.com"}


class ArmoryImageSupplementTests(RelatedImageOverlayTests):
    """Regression surface for host, path, byte, and origin-route invariants."""

    def _map(self, base: Path, entries: list[dict], name: str = "supplement-map.json") -> Path:
        path = super()._map(base, entries, name)
        payload = json.loads(path.read_text(encoding="utf-8"))
        by_url = {entry["logical_url"]: entry for entry in entries}
        for item in payload["items"]:
            entry = by_url[item["logical_url"]]
            item["mime"] = entry.get("declared_mime", "image/gif")
            if entry.get("cdx_digest"):
                item["cdx_digest"] = entry["cdx_digest"]
        path.write_text(json.dumps(payload), encoding="utf-8")
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

    def _accepted_armory_entries(self) -> list[dict]:
        public_by_url = {}
        for receipt_path in PUBLIC_RECEIPTS:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            for row in receipt["accepted_images"]:
                public_by_url[row["original"]] = row

        rows = []
        for receipt_path in SOURCE_RECEIPTS:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertTrue(receipt["accepted"], receipt_path)
            for index, row in enumerate(receipt["accepted_images"], start=1):
                parsed = urlsplit(row["original"])
                if parsed.hostname not in ARMORY_HOSTS:
                    continue
                public_row = public_by_url[row["original"]]
                data = (ROOT / public_row["local_path"]).read_bytes()
                rows.append(
                    {
                        "filename": f"accepted-armory-{len(rows) + 1:02d}-{index}.png",
                        "logical_url": row["original"],
                        "original": row["original"],
                        "actual_timestamp": row["actual_capture_timestamp"],
                        "indexed_capture_timestamp": row["actual_capture_timestamp"],
                        "temporal_class": "baseline_2008",
                        "data": data,
                        "declared_mime": row["mime"],
                        "cdx_digest": row["cdx_digest"],
                        "receipt_sha256": row["sha256"],
                        "receipt_length": row["length"],
                    }
                )
        return rows

    def test_public_copies_match_all_thirteen_accepted_armory_pngs(self) -> None:
        entries = self._accepted_armory_entries()
        self.assertEqual(len(entries), 13)
        self.assertEqual({urlsplit(entry["logical_url"]).hostname for entry in entries}, ARMORY_HOSTS)
        for entry in entries:
            with self.subTest(original=entry["logical_url"]):
                data = entry["data"]
                self.assertEqual(len(data), entry["receipt_length"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["receipt_sha256"])
                self.assertTrue(urlsplit(entry["logical_url"]).path.startswith("/images/icons/"))
                with Image.open(io.BytesIO(data)) as image:
                    self.assertEqual(image.format, "PNG")

    def test_real_us_eu_supplements_are_namespaced_and_same_path_isolated(self) -> None:
        entries = self._accepted_armory_entries()
        us = next(entry for entry in entries if urlsplit(entry["logical_url"]).hostname == "www.wowarmory.com")
        eu = next(entry for entry in entries if urlsplit(entry["logical_url"]).hostname == "armory.wow-europe.com")
        same_path = [
            {
                **us,
                "filename": "same-path-us.png",
                "logical_url": "http://www.wowarmory.com/images/icons/same-path.png",
                "original": "http://www.wowarmory.com/images/icons/same-path.png",
            },
            {
                **eu,
                "filename": "same-path-eu.png",
                "logical_url": "http://armory.wow-europe.com/images/icons/same-path.png",
                "original": "http://armory.wow-europe.com/images/icons/same-path.png",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base, [*entries, *same_path])
            result = self._export(base, site, manifest, supplement=[source_map])
            output = base / "pages"
            self.assertEqual(result["stats"]["supplement_image_overlay_records"], 15)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            overlays = [row for row in provenance["files"] if row.get("role") == "image_overlay"]
            self.assertEqual(len(overlays), 15)
            by_path = {row["output_path"]: row for row in overlays}
            for entry in entries + same_path:
                parsed = urlsplit(entry["logical_url"])
                route = f"_origins/{parsed.hostname}{parsed.path}"
                with self.subTest(original=entry["logical_url"]):
                    self.assertIn(route, by_path)
                    self.assertEqual((output / route).read_bytes(), entry["data"])
                    record = by_path[route]
                    self.assertEqual(record["origin_namespace"], parsed.hostname)
                    self.assertEqual(record["original_url"], entry["original"])
                    self.assertEqual(record["source_sha256"], hashlib.sha256(entry["data"]).hexdigest())
                    self.assertEqual(record["mime"], "image/png")
            us_route = "_origins/www.wowarmory.com/images/icons/same-path.png"
            eu_route = "_origins/armory.wow-europe.com/images/icons/same-path.png"
            self.assertNotEqual((output / us_route).read_bytes(), (output / eu_route).read_bytes())

    def test_primary_armory_input_and_invalid_supplement_inputs_are_rejected(self) -> None:
        valid = self._accepted_armory_entries()[0]
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base, [valid], "primary-armory.json")
            with self.assertRaisesRegex(pages.PagesExportError, "not an approved image origin"):
                self._export(base, site, manifest, primary=[source_map])

        cases = {
            "outside_icons": "http://www.wowarmory.com/account/login.png",
            "eu_outside_icons": "http://armory.wow-europe.com/images/characters/5.png",
            "query": "http://www.wowarmory.com/images/icons/query.png?x=1",
            "nondefault_port": "http://www.wowarmory.com:8080/images/icons/port.png",
            "bare_host": "http://wowarmory.com/images/icons/bare.png",
            "trailing_dot_host": "http://www.wowarmory.com./images/icons/dotted.png",
            "non_image_extension": "http://www.wowarmory.com/images/icons/file.txt",
        }
        for name, url in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                base, site, manifest = self._fixture(Path(tmp))
                entry = {
                    "filename": f"{name}.bin",
                    "logical_url": url,
                    "original": url,
                    "actual_timestamp": "20080402041000",
                    "indexed_capture_timestamp": "20080402041000",
                    "temporal_class": "baseline_2008",
                    "data": b"not-an-image",
                    "declared_mime": "image/png",
                }
                source_map = self._map(base, [entry], f"{name}.json")
                with self.assertRaises(pages.PagesExportError):
                    self._export(base, site, manifest, supplement=[source_map])

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            mismatch = {
                **valid,
                "filename": "origin-mismatch.png",
                "logical_url": "http://www.wowarmory.com/images/icons/mismatch.png",
                "original": "http://armory.wow-europe.com/images/icons/mismatch.png",
            }
            source_map = self._map(base, [mismatch], "origin-mismatch.json")
            with self.assertRaisesRegex(pages.PagesExportError, "logical_url and original disagree"):
                self._export(base, site, manifest, supplement=[source_map])

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            html_payload = {**valid, "filename": "html.png", "data": b"<html>not an image</html>"}
            source_map = self._map(base, [html_payload], "html-payload.json")
            with self.assertRaisesRegex(pages.PagesExportError, "PNG magic mismatch"):
                self._export(base, site, manifest, supplement=[source_map])


if __name__ == "__main__":
    unittest.main()
