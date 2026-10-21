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

import related_talent_icons  # noqa: E402


def _git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class RelatedTalentIconTests(unittest.TestCase):
    def _jpeg(self, size: tuple[int, int] = (36, 36)) -> bytes:
        image = Image.new("RGB", size, (32, 96, 160))
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=90)
        return output.getvalue()

    def _fixture(
        self,
        root: Path,
        *,
        image_data: bytes | None = None,
        entry_updates: dict[str, object] | None = None,
        source_updates: dict[str, object] | None = None,
        decision_updates: dict[str, object] | None = None,
        acceptance_updates: dict[str, object] | None = None,
    ) -> dict[str, object]:
        data = image_data if image_data is not None else self._jpeg()
        payload = root / "private" / "icon.jpg"
        payload.parent.mkdir(parents=True, exist_ok=True)
        payload.write_bytes(data)

        route = "/shared/global/talents/druid/images/balance/testicon.jpg"
        entry: dict[str, object] = {
            "route": route,
            "repository_path": route[1:],
            "payload_path": payload.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "length": len(data),
            "git_blob_sha1": _git_blob_sha1(data),
            "format": "JPEG",
            "width": 36,
            "height": 36,
            "frames": 1,
        }
        entry.update(entry_updates or {})

        source: dict[str, object] = {
            "repository_url": related_talent_icons.EXPECTED_REPOSITORY_URL,
            "commit_sha": related_talent_icons.EXPECTED_COMMIT_SHA,
            "tree_sha": related_talent_icons.EXPECTED_TREE_SHA,
            "downloaded_utc": "2026-10-21T04:39:55.289652+00:00",
            "classification": related_talent_icons.EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
        source.update(source_updates or {})

        acceptance: dict[str, object] = {
            "schema": related_talent_icons.EXPECTED_ACCEPTANCE_SCHEMA,
            "accepted_source": True,
            "repository_url": related_talent_icons.EXPECTED_REPOSITORY_URL,
            "commit_sha": related_talent_icons.EXPECTED_COMMIT_SHA,
            "tree_sha": related_talent_icons.EXPECTED_TREE_SHA,
            "strict_36px_same_path_icon_candidates": 1,
            "original_2008_images_recovered": 0,
            "published_images": 0,
        }
        acceptance.update(acceptance_updates or {})
        acceptance_path = root / "acceptance.json"
        acceptance_path.write_text(json.dumps(acceptance, sort_keys=True), encoding="utf-8")
        acceptance_sha = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()

        decision: dict[str, object] = {
            "schema": related_talent_icons.EXPECTED_DECISION_SCHEMA,
            "accepted_for_browser_supplement": True,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "accepted_icon_count": 1,
            "original_capture_timestamp": None,
            "original_2008_images_recovered": 0,
        }
        decision.update(decision_updates or {})
        decision_path = root / "decision.json"
        decision_path.write_text(json.dumps(decision, sort_keys=True), encoding="utf-8")
        decision_sha = hashlib.sha256(decision_path.read_bytes()).hexdigest()

        source_map: dict[str, object] = {
            "schema": related_talent_icons.EXPECTED_MAP_SCHEMA,
            "decision": "decision.json",
            "decision_sha256": decision_sha,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "source": source,
            "icon_count": 1,
            "entries": [entry],
        }
        map_path = root / "input-map.json"
        map_path.write_text(json.dumps(source_map, sort_keys=True), encoding="utf-8")
        map_sha = hashlib.sha256(map_path.read_bytes()).hexdigest()
        return {
            "map_path": map_path,
            "map_sha": map_sha,
            "decision_sha": decision_sha,
            "acceptance_sha": acceptance_sha,
            "image_length": len(data),
        }

    def _load(self, fixture: dict[str, object]):
        with mock.patch.multiple(
            related_talent_icons,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
            EXPECTED_ICON_COUNT=1,
            EXPECTED_TOTAL_BYTES=fixture["image_length"],
        ):
            return related_talent_icons.load_related_talent_bundle(
                fixture["map_path"],
                Path(fixture["map_path"]).parent,
                "/WOW-Encyclopedia-Deployable-Archive/",
            )

    def test_success_preserves_bytes_and_public_catalog_has_no_private_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            bundle = self._load(fixture)
            self.assertEqual(len(bundle.assets), 1)
            asset = bundle.assets[0]
            self.assertEqual(asset.route, "/shared/global/talents/druid/images/balance/testicon.jpg")
            self.assertEqual(asset.relative, "shared/global/talents/druid/images/balance/testicon.jpg")
            self.assertEqual(asset.mime, "image/jpeg")
            self.assertEqual(asset.metadata["width"], 36)
            self.assertEqual(asset.metadata["frames"], 1)
            self.assertEqual(bundle.estimated_bytes, fixture["image_length"] + len(bundle.catalog_bytes))
            self.assertEqual(bundle.per_class_counts["druid"], 1)
            self.assertIn("Talent data: 2008 archive", bundle.notice_html)
            self.assertIn("later WotLK 3.3.5a calculator backup", bundle.notice_html)
            self.assertIn('id="related-talent-icons-notice"', bundle.notice_html)
            self.assertIn('role="note"', bundle.notice_html)
            self.assertNotIn("not verified", bundle.notice_html)
            self.assertEqual(bundle.source_metadata["retrieved_utc"], "2026-10-21T04:39:55.289652+00:00")
            catalog = json.loads(bundle.catalog_bytes)
            self.assertEqual(catalog["catalog_relative"], "__offline/related-talent-icons.json")
            self.assertEqual(catalog["assets"][0]["url"], "/WOW-Encyclopedia-Deployable-Archive/shared/global/talents/druid/images/balance/testicon.jpg")
            public_text = bundle.catalog_bytes.decode("utf-8")
            for forbidden in ("payload_path", "zip_url", "downloaded_utc", "http_requests"):
                self.assertNotIn(forbidden, public_text)

    def test_rejects_unaccepted_decision_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), decision_updates={"accepted_for_browser_supplement": False})
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "not accepted"):
                self._load(fixture)

    def test_rejects_route_scope_and_payload_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(
                Path(tmp),
                entry_updates={"route": "/shared/global/talents/druid/images/../testicon.jpg"},
            )
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "traversal"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={"payload_path": "../outside.jpg"})
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "traversal"):
                self._load(fixture)

    def test_rejects_non_jpeg_or_wrong_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image = Image.new("RGB", (36, 36), (2, 4, 8))
            output = io.BytesIO()
            image.save(output, format="PNG")
            fixture = self._fixture(Path(tmp), image_data=output.getvalue())
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "not JPEG"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), image_data=self._jpeg((35, 36)))
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "dimensions"):
                self._load(fixture)

    def test_rejects_nonnull_original_capture_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), source_updates={"original_capture_timestamp": "20080402010101"})
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "capture timestamp"):
                self._load(fixture)

    def test_rejects_payload_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={"sha256": "0" * 64})
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "SHA mismatch"):
                self._load(fixture)

    def test_rejects_query_in_base_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            with mock.patch.multiple(
                related_talent_icons,
                EXPECTED_MAP_SHA256=fixture["map_sha"],
                EXPECTED_DECISION_SHA256=fixture["decision_sha"],
                EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
                EXPECTED_ICON_COUNT=1,
                EXPECTED_TOTAL_BYTES=fixture["image_length"],
            ):
                with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "query"):
                    related_talent_icons.load_related_talent_bundle(
                        fixture["map_path"], Path(tmp), "/site?bad=1"
                    )


if __name__ == "__main__":
    unittest.main()
