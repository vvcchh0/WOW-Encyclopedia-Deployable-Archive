"""Portable tests for the pinned current related guide-image adapter."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import related_guide_images  # noqa: E402


class RelatedGuideImageTests(unittest.TestCase):
    @staticmethod
    def _jpeg(size: tuple[int, int] = (237, 184), colour: tuple[int, int, int] = (90, 40, 130)) -> bytes:
        output = io.BytesIO()
        Image.new("RGB", size, colour).save(output, format="JPEG", quality=90)
        return output.getvalue()

    @staticmethod
    def _write_json(path: Path, value: dict) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _fixture(
        self,
        root: Path,
        *,
        payload: bytes | None = None,
        entry_updates: dict | None = None,
        decision_updates: dict | None = None,
        acceptance_updates: dict | None = None,
    ) -> dict[str, object]:
        payload_path = root / "payload" / "thebroken.jpg"
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        payload_bytes = payload if payload is not None else self._jpeg()
        payload_path.write_bytes(payload_bytes)

        entry = dict(related_guide_images.EXPECTED_ENTRY)
        entry["payload_path"] = "payload/thebroken.jpg"
        with Image.open(io.BytesIO(payload_bytes)) as image:
            entry.update(
                sha256=hashlib.sha256(payload_bytes).hexdigest(),
                length=len(payload_bytes),
                width=image.width,
                height=image.height,
                frames=getattr(image, "n_frames", 1),
            )
        if entry_updates:
            entry.update(entry_updates)
        public_entry = {key: value for key, value in entry.items() if key != "payload_path"}
        decision = {
            "schema": related_guide_images.EXPECTED_DECISION_SCHEMA,
            "accepted_for_browser_supplement": True,
            "checked_utc": "2026-10-21T09:45:38.519290+00:00",
            "classification": related_guide_images.EXPECTED_CLASSIFICATION,
            "original_2008_images_recovered": 0,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": "",
            "targets": [public_entry],
            "compatibility_reuses": [dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)],
            "decision": "Display the exact current related guide image.",
        }
        if decision_updates:
            decision.update(decision_updates)
        acceptance = {
            "schema": related_guide_images.EXPECTED_ACCEPTANCE_SCHEMA,
            "accepted_sources": True,
            "checked_utc": "2026-10-21T09:45:38.516282+00:00",
            "records": [public_entry],
            "source_images": 1,
            "historical_original_images_recovered": 0,
            "raw_http_private": True,
            "images_reencoded": False,
        }
        if acceptance_updates:
            acceptance.update(acceptance_updates)

        decision_path = root / "decision.json"
        acceptance_path = root / "acceptance.json"
        self._write_json(acceptance_path, acceptance)
        acceptance_sha = self._sha(acceptance_path)
        decision["source_acceptance_sha256"] = acceptance_sha
        self._write_json(decision_path, decision)
        decision_sha = self._sha(decision_path)
        map_data = {
            "schema": related_guide_images.EXPECTED_MAP_SCHEMA,
            "decision": "decision.json",
            "decision_sha256": decision_sha,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "source_label": "ArchiveCraft community archive",
            "source_manifest_sha256": related_guide_images.EXPECTED_SOURCE_MANIFEST_SHA256,
            "entries": [entry],
            "compatibility_reuses": [dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)],
        }
        map_path = root / "input-map.json"
        self._write_json(map_path, map_data)
        return {
            "root": root,
            "map_path": map_path,
            "map_sha": self._sha(map_path),
            "decision_sha": decision_sha,
            "acceptance_sha": acceptance_sha,
            "payload": payload_path.read_bytes(),
        }

    def _load(self, fixture: dict[str, object], base_path: str = "/WOW-Encyclopedia-Deployable-Archive/"):
        with mock.patch.multiple(
            related_guide_images,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
        ):
            return related_guide_images.load_related_guide_image_bundle(
                fixture["map_path"], fixture["root"], base_path
            )

    def test_success_preserves_exact_jpeg_and_public_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp))
            bundle = self._load(fixture)
            self.assertIsInstance(bundle, related_guide_images.RelatedGuideImageBundle)
            self.assertEqual(len(bundle.assets), 1)
            asset = bundle.assets[0]
            self.assertIsInstance(asset, related_guide_images.RelatedGuideImageAsset)
            self.assertEqual(asset.data, fixture["payload"])
            self.assertEqual(asset.route, "/__offline/related-guide-images/thumb-thebroken.jpg")
            self.assertEqual(
                bundle.route_reuses,
                {
                    "/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg": asset.route,
                    "/burningcrusade/townhall/images/bestiary/thumb-broken.jpg": asset.route,
                },
            )
            self.assertEqual(bundle.estimated_bytes, len(asset.data) + len(bundle.catalog_bytes))
            self.assertEqual(bundle.source_metadata["original_2008_images_recovered"], 0)
            self.assertIsNone(bundle.source_metadata["original_capture_timestamp"])
            notice = bundle.notice_by_page["/burningcrusade/townhall/bestiary.html"]
            self.assertIn('id="__offline-related-guide-images"', notice)
            self.assertIn("https://archivecraft.com/burningcrusade/townhall/bestiary/", notice)
            self.assertIn("background:#eadbb7;color:#302619", notice)
            catalog = json.loads(bundle.catalog_bytes)
            self.assertEqual(catalog["image_count"], 1)
            self.assertEqual(catalog["compatibility_reuses"], [dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)])
            self.assertEqual(bundle.source_metadata["compatibility_reuses"], [dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)])
            self.assertEqual(catalog["images"][0]["url"], "/WOW-Encyclopedia-Deployable-Archive/__offline/related-guide-images/thumb-thebroken.jpg")
            public_text = bundle.catalog_bytes.decode("utf-8")
            for forbidden in ("payload_path", "raw_http", "cookie", "private", str(Path(temp))):
                self.assertNotIn(forbidden, public_text)

    def test_rejects_payload_path_traversal_and_sha_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), entry_updates={"payload_path": "../outside.jpg"})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "traversal"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), entry_updates={"sha256": "0" * 64})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "length|SHA"):
                self._load(fixture)

    def test_rejects_decision_or_source_acceptance_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), decision_updates={"accepted_for_browser_supplement": False})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "not accepted"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), acceptance_updates={"images_reencoded": True})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "original bytes"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), entry_updates={"original_capture_timestamp": "20080402010101"})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "accepted original_capture_timestamp"):
                self._load(fixture)

    def test_rejects_wrong_compatibility_theme_or_capture(self) -> None:
        wrong_theme = dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)
        wrong_theme["creature_name"] = "dragonspawn"
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), decision_updates={"compatibility_reuses": [wrong_theme]})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "exact accepted compatibility"):
                self._load(fixture)

        wrong_capture = dict(related_guide_images.EXPECTED_COMPATIBILITY_REUSE)
        wrong_capture["original_capture_timestamp"] = "20080402010101"
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), decision_updates={"compatibility_reuses": [wrong_capture]})
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "exact accepted compatibility"):
                self._load(fixture)

    def test_rejects_bad_base_path_and_non_jpeg_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp))
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "query"):
                self._load(fixture, "/site?bad=1")

        png = io.BytesIO()
        Image.new("RGB", (237, 184), (1, 2, 3)).save(png, format="PNG")
        with tempfile.TemporaryDirectory() as temp:
            fixture = self._fixture(Path(temp), payload=png.getvalue())
            with self.assertRaisesRegex(related_guide_images.RelatedGuideImageError, "length|SHA|not JPEG"):
                self._load(fixture)


if __name__ == "__main__":
    unittest.main()
