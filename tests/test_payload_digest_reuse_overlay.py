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


JPEG_1X1 = base64.b64decode(
    b"/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/AP/EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEAAQUCf//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQMBAT8Bf//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQIBAT8Bf//EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEABj8Cf//Z"
)


class PayloadDigestReuseOverlayTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path]:
        return github_export_tests.GithubPagesExportTests()._fixture(base)

    def _map(self, base: Path, *, mutate=None) -> Path:
        source = base / "raw" / "reuse.jpg"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(JPEG_1X1)
        sha256 = hashlib.sha256(JPEG_1X1).hexdigest()
        digest = base64.b32encode(hashlib.sha1(JPEG_1X1).digest()).decode().rstrip("=")
        items = []
        for route, target_capture, source_url in (
            (
                "/news/images/04-12/ordernow.jpg",
                "20080402082301",
                "http://www.worldofwarcraft.com/shared/wow-com/images/advertising/04-12/ordernow.jpg",
            ),
            (
                "/news/images/05-10/trolldire.jpg",
                "20080402080557",
                "http://www.worldofwarcraft.com/downloads/images/thumbnails/trolldire.jpg",
            ),
        ):
            item = {
                "kind": "image",
                "logical_url": "http://www.worldofwarcraft.com" + route,
                "original": "http://www.worldofwarcraft.com" + route,
                "local_path": "raw/reuse.jpg",
                "mime": "image/jpeg",
                "sha256": sha256,
                "length": len(JPEG_1X1),
                "indexed_capture_timestamp": target_capture,
                "cdx_digest": digest,
                "recovery_method": "payload_digest_reuse",
                "payload_source": {
                    "original_url": source_url,
                    "actual_capture_timestamp": "20080512205900",
                    "sha256": sha256,
                    "length": len(JPEG_1X1),
                },
            }
            if mutate is not None:
                mutate(item, len(items))
            items.append(item)
        map_path = base / "reuse-map.json"
        map_path.write_text(json.dumps({"items": items}, sort_keys=True), encoding="utf-8")
        return map_path

    def _export(self, base: Path, site: Path, manifest: Path, source_map: Path):
        return pages.export_pages(
            source_site=site,
            manifest_path=manifest,
            output=base / "pages",
            workspace_root=base,
            max_bytes=500_000_000,
            min_free_bytes=0,
            image_source_maps=[source_map],
        )

    def test_two_reused_payloads_preserve_separate_target_and_source_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base)
            result = self._export(base, site, manifest, source_map)
            self.assertEqual(result["stats"]["image_overlay_records"], 2)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            overlays = [item for item in provenance["files"] if item.get("role") == "image_overlay"]
            self.assertEqual(len(overlays), 2)
            for item in overlays:
                self.assertEqual(item["recovery_method"], "payload_digest_reuse")
                self.assertIsNone(item["actual_capture_timestamp"])
                self.assertEqual(item["capture_timestamp_basis"], "target_cdx_digest")
                self.assertEqual(item["payload_source"]["actual_capture_timestamp"], "20080512205900")
                self.assertEqual(item["payload_source"]["length"], len(JPEG_1X1))
                self.assertEqual(item["source_sha256"], item["payload_source"]["sha256"])
            self.assertEqual(
                {item["indexed_capture_timestamp"] for item in overlays},
                {"20080402082301", "20080402080557"},
            )

    def test_digest_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(base, mutate=lambda item, index: item.update(cdx_digest="A" * 32) if index == 0 else None)
            with self.assertRaisesRegex(pages.PagesExportError, "CDX SHA-1 digest mismatch"):
                self._export(base, site, manifest, source_map)

    def test_forged_source_timestamp_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                mutate=lambda item, index: item["payload_source"].update(actual_capture_timestamp="20080230000000")
                if index == 0
                else None,
            )
            with self.assertRaisesRegex(pages.PagesExportError, "not a real date"):
                self._export(base, site, manifest, source_map)

    def test_later_payload_source_date_is_allowed_for_preanchor_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                mutate=lambda item, index: item["payload_source"].update(actual_capture_timestamp="20100101000000")
                if index == 0
                else None,
            )
            self._export(base, site, manifest, source_map)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            overlay = next(item for item in provenance["files"] if item.get("role") == "image_overlay")
            self.assertEqual(overlay["indexed_capture_timestamp"], "20080402082301")
            self.assertEqual(overlay["payload_source"]["actual_capture_timestamp"], "20100101000000")

    def test_missing_source_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))

            def remove_source(item, index):
                if index == 0:
                    item.pop("payload_source")

            source_map = self._map(base, mutate=remove_source)
            with self.assertRaisesRegex(pages.PagesExportError, "payload_source evidence is missing"):
                self._export(base, site, manifest, source_map)

    def test_reused_item_cannot_supply_a_target_actual_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                mutate=lambda item, index: item.update(actual_timestamp="20080402082301")
                if index == 0
                else None,
            )
            with self.assertRaisesRegex(pages.PagesExportError, "must omit actual_timestamp"):
                self._export(base, site, manifest, source_map)

    def test_legacy_ordinary_image_map_keeps_actual_capture_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source = base / "raw" / "legacy.jpg"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(JPEG_1X1)
            item = {
                "kind": "image",
                "logical_url": "http://www.worldofwarcraft.com/missing.gif",
                "original": "http://www.worldofwarcraft.com/missing.gif",
                "local_path": "raw/legacy.jpg",
                "mime": "image/jpeg",
                "sha256": hashlib.sha256(JPEG_1X1).hexdigest(),
                "length": len(JPEG_1X1),
                "actual_timestamp": "20080512205900",
                "indexed_capture_timestamp": "20080512205900",
                "cdx_digest": base64.b32encode(hashlib.sha1(JPEG_1X1).digest()).decode().rstrip("="),
            }
            source_map = base / "legacy-map.json"
            source_map.write_text(json.dumps({"items": [item]}), encoding="utf-8")
            self._export(base, site, manifest, source_map)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            overlay = next(item for item in provenance["files"] if item.get("role") == "image_overlay")
            self.assertEqual(overlay["actual_capture_timestamp"], "20080512205900")
            self.assertEqual(overlay["indexed_capture_timestamp"], "20080512205900")
            self.assertNotIn("recovery_method", overlay)
            self.assertNotIn("payload_source", overlay)
            self.assertEqual((base / "pages/missing.gif").read_bytes(), JPEG_1X1)
            article = (base / "pages/article.xml.html").read_text(encoding="utf-8")
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/missing.gif", article)

    def test_existing_ordinary_fixture_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "ordinary-pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            self.assertEqual(result["stats"]["source_records"], 11)
            self.assertTrue((base / "ordinary-pages/export-provenance.json").is_file())


if __name__ == "__main__":
    unittest.main()
