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

import related_encyclopedia_images  # noqa: E402


class RelatedEncyclopediaImageTests(unittest.TestCase):
    def _jpeg(self, size: tuple[int, int], color: tuple[int, int, int]) -> bytes:
        image = Image.new("RGB", size, color)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=90)
        return output.getvalue()

    def _fixture(
        self,
        root: Path,
        *,
        image_data: list[bytes] | None = None,
        entry_updates: dict[int, dict[str, object]] | None = None,
        decision_updates: dict[str, object] | None = None,
        acceptance_updates: dict[int, dict[str, object]] | None = None,
    ) -> dict[str, object]:
        sizes = [(300, 353), (300, 418), (300, 326)]
        colors = [(180, 70, 40), (30, 120, 70), (60, 80, 180)]
        payloads = image_data or [self._jpeg(size, color) for size, color in zip(sizes, colors)]
        payload_root = root / "private" / "archivecraft"
        payload_root.mkdir(parents=True, exist_ok=True)

        entries: list[dict[str, object]] = []
        acceptance_records: list[dict[str, object]] = []
        source_urls = [
            "https://archivecraft.test/alleria.jpg",
            "https://archivecraft.test/cenarion.jpg",
            "https://archivecraft.test/malfurion.jpg",
        ]
        source_pages = [
            "https://archivecraft.test/alleria/",
            "https://archivecraft.test/cenarion/",
            "https://archivecraft.test/malfurion/",
        ]
        titles = ["Alleria Windrunner", "Cenarion Circle", "Malfurion Stormrage"]
        for index, (expected, data, size) in enumerate(zip(related_encyclopedia_images.EXPECTED_ENTRIES, payloads, sizes)):
            payload = payload_root / f"image-{index}.jpg"
            payload.write_bytes(data)
            width, height = size
            entry: dict[str, object] = {
                "title": titles[index],
                "page_route": expected["page_route"],
                "target_route": expected["target_route"],
                "route": expected["route"],
                "source_image_url": source_urls[index],
                "source_page_url": source_pages[index],
                "current_observed_utc": f"2026-10-21T08:19:{7 + index * 6:02d}.000000Z",
                "sha256": hashlib.sha256(data).hexdigest(),
                "length": len(data),
                "format": "JPEG",
                "width": width,
                "height": height,
                "frames": 1,
                "classification": related_encyclopedia_images.EXPECTED_CLASSIFICATION,
                "original_capture_timestamp": None,
                "source_processing_note": "Fixture preserves original bytes.",
                "payload_path": payload.relative_to(root).as_posix(),
            }
            entry.update((entry_updates or {}).get(index, {}))
            entries.append(entry)
            acceptance: dict[str, object] = {
                "target_id": f"fixture-{index}",
                "url": source_urls[index],
                "source_page_url": source_pages[index],
                "current_observed_utc": entry["current_observed_utc"],
                "current_response_is_not_historical_capture": True,
                "http_status": 200,
                "body_bytes": len(data),
                "body_sha256": hashlib.sha256(data).hexdigest(),
                "content_type": "image/jpeg",
                "content_length": len(data),
                "valid": True,
                "format": "JPEG",
            }
            acceptance.update((acceptance_updates or {}).get(index, {}))
            acceptance_records.append(acceptance)

        acceptance: dict[str, object] = {
            "schema": related_encyclopedia_images.EXPECTED_ACCEPTANCE_SCHEMA,
            "accepted_sources": True,
            "checked_utc": "2026-10-21T09:00:00+00:00",
            "records": acceptance_records,
            "historical_original_images_recovered": 0,
        }
        acceptance_path = root / "acceptance.json"
        acceptance_path.write_text(json.dumps(acceptance, sort_keys=True), encoding="utf-8")
        acceptance_sha = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()

        decision: dict[str, object] = {
            "schema": related_encyclopedia_images.EXPECTED_DECISION_SCHEMA,
            "accepted_for_browser_supplement": True,
            "checked_utc": "2026-10-21T09:00:01+00:00",
            "classification": related_encyclopedia_images.EXPECTED_CLASSIFICATION,
            "original_2008_images_recovered": 0,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "targets": [
                {key: value for key, value in entry.items() if key != "payload_path"}
                for entry in entries
            ],
        }
        decision.update(decision_updates or {})
        decision_path = root / "decision.json"
        decision_path.write_text(json.dumps(decision, sort_keys=True), encoding="utf-8")
        decision_sha = hashlib.sha256(decision_path.read_bytes()).hexdigest()

        source_map: dict[str, object] = {
            "schema": related_encyclopedia_images.EXPECTED_MAP_SCHEMA,
            "decision": "decision.json",
            "decision_sha256": decision_sha,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "source_label": "ArchiveCraft community archive",
            "source_manifest_sha256": related_encyclopedia_images.EXPECTED_SOURCE_MANIFEST_SHA256,
            "entries": entries,
        }
        map_path = root / "input-map.json"
        map_path.write_text(json.dumps(source_map, sort_keys=True), encoding="utf-8")
        map_sha = hashlib.sha256(map_path.read_bytes()).hexdigest()
        return {
            "map_path": map_path,
            "map_sha": map_sha,
            "decision_sha": decision_sha,
            "acceptance_sha": acceptance_sha,
            "payloads": payloads,
        }

    def _load(self, fixture: dict[str, object], base_path: str = "/WOW-Encyclopedia-Deployable-Archive/"):
        with mock.patch.multiple(
            related_encyclopedia_images,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
        ):
            return related_encyclopedia_images.load_related_encyclopedia_image_bundle(
                fixture["map_path"], Path(fixture["map_path"]).parent, base_path
            )

    def test_success_preserves_bytes_and_public_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            bundle = self._load(fixture)
            self.assertEqual(len(bundle.assets), 3)
            self.assertEqual([asset.data for asset in bundle.assets], fixture["payloads"])
            self.assertEqual(bundle.estimated_bytes, sum(map(len, fixture["payloads"])) + len(bundle.catalog_bytes))
            self.assertEqual(len(bundle.route_reuses), 3)
            self.assertEqual(len(bundle.notice_by_page), 3)
            expected_source_pages = (
                "https://archivecraft.test/alleria/",
                "https://archivecraft.test/cenarion/",
                "https://archivecraft.test/malfurion/",
            )
            for page, source_page in zip(bundle.notice_by_page, expected_source_pages):
                notice = bundle.notice_by_page[page]
                self.assertEqual(
                    notice,
                    '<aside id="__offline-related-encyclopedia-images" role="note" '
                    'style="padding:6px 12px;background:#eadbb7;color:#302619;'
                    'font:13px/1.5 Arial,sans-serif;text-align:center">'
                    f'Illustration from <a href="{source_page}" '
                    'style="color:#174f7d;text-decoration:underline" '
                    'target="_blank" rel="noopener noreferrer">ArchiveCraft</a>.'
                    "</aside>",
                )
            catalog = json.loads(bundle.catalog_bytes)
            self.assertEqual(catalog["image_count"], 3)
            self.assertEqual(catalog["images"][0]["url"], "/WOW-Encyclopedia-Deployable-Archive/__offline/related-encyclopedia-images/alleriawindrunner.jpg")
            public_text = bundle.catalog_bytes.decode("utf-8")
            for forbidden in ("payload_path", "raw_http", "cookie", "private"):
                self.assertNotIn(forbidden, public_text)

    def test_rejects_unaccepted_or_historical_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), decision_updates={"accepted_for_browser_supplement": False})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "not accepted"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), acceptance_updates={0: {"current_response_is_not_historical_capture": False}})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "incorrectly presented"):
                self._load(fixture)

    def test_rejects_payload_traversal_and_sha_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={0: {"payload_path": "../outside.jpg"}})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "traversal"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={1: {"sha256": "0" * 64}})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "SHA mismatch"):
                self._load(fixture)

    def test_rejects_non_jpeg_or_wrong_dimensions(self) -> None:
        png = io.BytesIO()
        Image.new("RGB", (300, 353), (1, 2, 3)).save(png, format="PNG")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), image_data=[png.getvalue(), self._jpeg((300, 418), (1, 2, 3)), self._jpeg((300, 326), (1, 2, 3))])
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "not JPEG"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={2: {"width": 299}})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "dimensions"):
                self._load(fixture)

    def test_rejects_nonnull_original_capture_and_bad_base_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={0: {"original_capture_timestamp": "20080402010101"}})
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "capture timestamp"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            with self.assertRaisesRegex(related_encyclopedia_images.RelatedEncyclopediaImageError, "query"):
                self._load(fixture, "/site?bad=1")


if __name__ == "__main__":
    unittest.main()
