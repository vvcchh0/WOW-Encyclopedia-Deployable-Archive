#!/usr/bin/env python3
"""Focused regression tests for the exact Blizzard supplement-host change.

These tests reuse the existing related-image overlay fixture helpers and do
not modify the repository or use the network.
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


ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-news8-next-source-acceptance.json"
PUBLIC_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-news8-next-public-copy-acceptance.json"


def jpeg_bytes(rgb: tuple[int, int, int]) -> bytes:
    stream = io.BytesIO()
    image = Image.new("RGB", (2, 2), rgb)
    image.save(stream, format="JPEG")
    return stream.getvalue()


class BlizzardImageSupplementTests(RelatedImageOverlayTests):
    """Small regression surface for host allowlisting and origin routing."""

    def _map(self, base: Path, entries: list[dict], name: str = "supplement-map.json") -> Path:
        """Reuse the existing fixture, restoring each entry's real MIME/CDX fields."""
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

    def _public_blizzard_entries(self) -> list[dict]:
        source = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        public = json.loads(PUBLIC_ACCEPTANCE.read_text(encoding="utf-8"))
        public_by_url = {row["original"]: row for row in public["accepted_images"]}
        entries = []
        for index, row in enumerate(source["accepted_images"], start=1):
            if not row["original"].casefold().startswith("http://www.blizzard.com/"):
                continue
            public_row = public_by_url[row["original"]]
            data = (ROOT / public_row["local_path"]).read_bytes()
            entries.append(
                {
                    "filename": f"accepted-blizzard-{index}.jpg",
                    "logical_url": row["original"],
                    "original": row["original"],
                    "actual_timestamp": row["actual_capture_timestamp"],
                    "indexed_capture_timestamp": row["actual_capture_timestamp"],
                    "temporal_class": "pre_2008",
                    "data": data,
                    "declared_mime": row["mime"],
                    "cdx_digest": row["cdx_digest"],
                }
            )
        return entries

    def _blizzard_entries(self) -> list[dict]:
        main_data = jpeg_bytes((220, 40, 40))
        blizzard_data = jpeg_bytes((40, 40, 220))
        return [
            {
                "filename": "main-fansitekit.jpg",
                "logical_url": "http://www.worldofwarcraft.com/WoW/images/screens/fansitekit.jpg",
                "original": "http://www.worldofwarcraft.com/WoW/images/screens/fansitekit.jpg",
                "actual_timestamp": "20060623155951",
                "indexed_capture_timestamp": "20060623155951",
                "temporal_class": "pre_2008",
                "data": main_data,
                "declared_mime": "image/jpeg",
            },
            {
                "filename": "blizzard-fansitekit.jpg",
                "logical_url": "http://www.blizzard.com/WoW/images/screens/fansitekit.jpg",
                "original": "http://www.blizzard.com/WoW/images/screens/fansitekit.jpg",
                "actual_timestamp": "20060623155951",
                "indexed_capture_timestamp": "20060623155951",
                "temporal_class": "pre_2008",
                "data": blizzard_data,
                "declared_mime": "image/jpeg",
            },
        ]

    def test_acceptance_receipt_has_four_accepted_blizzard_sources(self) -> None:
        payload = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        rows = [
            row
            for row in payload["accepted_images"]
            if row.get("original", "").casefold().startswith("http://www.blizzard.com/")
        ]
        self.assertTrue(payload["accepted"])
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["accepted"] and not row["deployed"] for row in rows))
        self.assertTrue(all(row["actual_capture_timestamp"][:4] in {"2005", "2006"} for row in rows))

    def test_public_copies_match_the_four_accepted_sources(self) -> None:
        source = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        public = json.loads(PUBLIC_ACCEPTANCE.read_text(encoding="utf-8"))
        public_by_url = {row["original"]: row for row in public["accepted_images"]}
        rows = [
            row
            for row in source["accepted_images"]
            if row["original"].casefold().startswith("http://www.blizzard.com/")
        ]
        self.assertEqual(len(rows), 4)
        for row in rows:
            with self.subTest(original=row["original"]):
                public_row = public_by_url[row["original"]]
                path = ROOT / public_row["local_path"]
                data = path.read_bytes()
                self.assertEqual(len(data), row["length"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
                with Image.open(io.BytesIO(data)) as image:
                    self.assertEqual(image.format, "JPEG")

    def test_blizzard_supplement_gets_origin_route_and_same_path_stays_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base, [self._blizzard_entries()[0], *self._public_blizzard_entries()])
            self._export(base, site, manifest, supplement=[source_map])
            output = base / "pages"
            main = output / "WoW/images/screens/fansitekit.jpg"
            blizzard = output / "_origins/www.blizzard.com/WoW/images/screens/fansitekit.jpg"
            self.assertTrue(main.is_file())
            self.assertTrue(blizzard.is_file())
            self.assertEqual(main.read_bytes(), self._blizzard_entries()[0]["data"])
            self.assertNotEqual(main.read_bytes(), blizzard.read_bytes())
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            overlays = [row for row in provenance["files"] if row.get("role") == "image_overlay"]
            by_path = {row["output_path"]: row for row in overlays}
            self.assertEqual(len(overlays), 5)
            self.assertEqual(
                {row["origin_namespace"] for row in overlays},
                {"www.worldofwarcraft.com", "www.blizzard.com"},
            )
            for entry in self._public_blizzard_entries():
                route = "_origins/www.blizzard.com/" + urlsplit(entry["logical_url"]).path.lstrip("/")
                self.assertIn(route, by_path)
                self.assertEqual((output / route).read_bytes(), entry["data"])
                self.assertEqual(by_path[route]["origin_namespace"], "www.blizzard.com")

    def test_primary_stays_strict_and_invalid_blizzard_inputs_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base, [self._blizzard_entries()[1]])
            with self.assertRaisesRegex(pages.PagesExportError, "not an approved image origin"):
                self._export(base, site, manifest, primary=[source_map])

        cases = {
            "origin_mismatch": {
                "logical_url": "http://www.blizzard.com/WoW/images/screens/bad.jpg",
                "original": "http://www.worldofwarcraft.com/WoW/images/screens/bad.jpg",
                "data": jpeg_bytes((40, 220, 40)),
                "declared_mime": "image/jpeg",
            },
            "html_payload": {
                "logical_url": "http://www.blizzard.com/WoW/images/screens/html.jpg",
                "original": "http://www.blizzard.com/WoW/images/screens/html.jpg",
                "data": b"<html><body>not an image</body></html>",
                "declared_mime": "image/jpeg",
            },
            "nondefault_port": {
                "logical_url": "http://www.blizzard.com:8080/WoW/images/screens/port.jpg",
                "original": "http://www.blizzard.com:8080/WoW/images/screens/port.jpg",
                "data": jpeg_bytes((40, 220, 40)),
                "declared_mime": "image/jpeg",
            },
            "bare_blizzard_host": {
                "logical_url": "http://blizzard.com/WoW/images/screens/bare.jpg",
                "original": "http://blizzard.com/WoW/images/screens/bare.jpg",
                "data": jpeg_bytes((40, 220, 40)),
                "declared_mime": "image/jpeg",
            },
            "query_suffix": {
                "logical_url": "http://www.blizzard.com/WoW/images/screens/query.jpg?x=1",
                "original": "http://www.blizzard.com/WoW/images/screens/query.jpg?x=1",
                "data": jpeg_bytes((40, 220, 40)),
                "declared_mime": "image/jpeg",
            },
        }
        for name, raw in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                base, site, manifest = self._fixture(Path(tmp))
                entry = {
                    "filename": f"{name}.jpg",
                    "logical_url": raw["logical_url"],
                    "original": raw["original"],
                    "actual_timestamp": "20060623155951",
                    "indexed_capture_timestamp": "20060623155951",
                    "temporal_class": "pre_2008",
                    "data": raw["data"],
                    "declared_mime": raw["declared_mime"],
                }
                source_map = self._map(base, [entry])
                with self.assertRaises(pages.PagesExportError):
                    self._export(base, site, manifest, supplement=[source_map])


if __name__ == "__main__":
    unittest.main()

