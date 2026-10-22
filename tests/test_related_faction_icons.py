"""Tests for the fixed, read-only later-source faction icon adapter."""

from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import related_faction_icons as faction_icons  # noqa: E402

MAP = ROOT / faction_icons.EXPECTED_MAP_RELATIVE
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"


class RelatedFactionIconTests(unittest.TestCase):
    def load(self):
        return faction_icons.load_related_faction_icon_bundle(MAP, ROOT, BASE_PATH)

    def test_loads_three_pinned_jpegs_and_eleven_scoped_notices(self):
        bundle = self.load()
        self.assertEqual(len(bundle.assets), 3)
        self.assertEqual(bundle.source_metadata["source_bytes"], 3587)
        self.assertEqual(bundle.estimated_bytes, 3587 + len(bundle.catalog_bytes))
        self.assertEqual(bundle.catalog_relative, "__offline/related-faction-icons.json")
        self.assertEqual(set(bundle.notice_by_page), set(faction_icons.EXPECTED_PAGES))
        self.assertEqual(
            bundle.route_reuses,
            {
                "/info/basics/factions/images/icons/INV_Scroll_03.gif": "/__offline/related-faction-icons/INV_Scroll_03.jpg",
                "/info/basics/factions/images/icons/INV_Scroll_06.gif": "/__offline/related-faction-icons/INV_Scroll_06.jpg",
                "/info/basics/factions/images/icons/INV_Wand_11.gif": "/__offline/related-faction-icons/INV_Wand_11.jpg",
            },
        )
        for asset in bundle.assets:
            self.assertEqual(asset.mime, "image/jpeg")
            self.assertEqual(asset.metadata["length"], len(asset.data))
            self.assertEqual(asset.metadata["width"], 36)
            self.assertEqual(asset.metadata["height"], 36)
            self.assertEqual(asset.metadata["frames"], 1)
            self.assertEqual(hashlib.sha256(asset.data).hexdigest(), asset.metadata["sha256"])
            self.assertEqual(faction_icons._git_blob_sha1(asset.data), asset.metadata["git_blob_sha1"])
            self.assertIsNone(asset.metadata["original_capture_timestamp"])
            self.assertEqual(asset.metadata["original_gif_pixel_identity"], "unknown")

        for notice in bundle.notice_by_page.values():
            plain_text = re.sub(r"<[^>]+>", "", notice)
            self.assertEqual(plain_text, faction_icons.EXPECTED_NOTICE_TEXT)
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons.json", notice)

        # The prior source acceptance and the newer derived-trial decision are
        # separate facts; the adapter must not rewrite the former.
        self.assertFalse(bundle.source_metadata["initial_source_record_browser_acceptance"])
        self.assertTrue(bundle.source_metadata["accepted_for_derived_trial"])
        self.assertEqual(bundle.source_metadata["source_manifest_sha256"], faction_icons.EXPECTED_SOURCE_MANIFEST_SHA256)
        self.assertEqual(bundle.source_metadata["original_2008_images_recovered"], 0)
        self.assertIsNone(bundle.source_metadata["original_capture_timestamp"])

        catalog = json.loads(bundle.catalog_bytes)
        self.assertEqual(catalog["image_count"], 3)
        self.assertEqual(catalog["source_bytes"], 3587)
        self.assertEqual([item["mime"] for item in catalog["images"]], ["image/jpeg"] * 3)
        serialized = bundle.catalog_bytes.decode("utf-8")
        self.assertNotIn("payload_path", serialized)
        self.assertNotIn(str(ROOT), serialized)
        self.assertNotIn('"accepted_for_browser_supplement":', serialized)

        # The exporter consumes the frozen bundle using dataclasses.replace.
        self.assertIsInstance(replace(bundle, source_metadata=dict(bundle.source_metadata)), faction_icons.RelatedFactionIconBundle)

    def test_rejects_external_or_traversal_map_paths(self):
        with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "outside the workspace"):
            faction_icons.load_related_faction_icon_bundle(Path(tempfile.gettempdir()) / "untrusted-map.json", ROOT, BASE_PATH)
        with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "traversal"):
            faction_icons.load_related_faction_icon_bundle("../input-map.json", ROOT, BASE_PATH)
        with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "traversal"):
            faction_icons._resolve_file(ROOT, "../outside.jpg", "payload")

    def test_rejects_same_length_payload_drift_before_image_decode(self):
        asset_path = ROOT / "research/continuous-recovery-20261022/integration/related-faction-icons-v54/assets/INV_Scroll_03.jpg"
        changed = bytearray(asset_path.read_bytes())
        changed[-1] ^= 1
        with tempfile.TemporaryDirectory() as temp:
            replacement = Path(temp) / "changed.jpg"
            replacement.write_bytes(changed)
            original_resolve = faction_icons._resolve_file

            def resolve_with_changed_first_asset(root, value, label):
                if label == "payload for /__offline/related-faction-icons/INV_Scroll_03.jpg":
                    return replacement
                return original_resolve(root, value, label)

            with mock.patch.object(faction_icons, "_resolve_file", side_effect=resolve_with_changed_first_asset):
                with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "SHA mismatch"):
                    self.load()

    def test_jpeg_validator_rejects_png_and_invalid_dimensions(self):
        stream = io.BytesIO()
        Image.new("RGB", (36, 36), (10, 20, 30)).save(stream, format="PNG")
        with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "payload is not JPEG"):
            faction_icons._validate_jpeg(stream.getvalue(), {"format": "JPEG", "width": 36, "height": 36, "frames": 1}, "fixture")

        jpeg = io.BytesIO()
        Image.new("RGB", (36, 36), (10, 20, 30)).save(jpeg, format="JPEG")
        with self.assertRaisesRegex(faction_icons.RelatedFactionIconError, "dimensions/frames do not match"):
            faction_icons._validate_jpeg(jpeg.getvalue(), {"format": "JPEG", "width": 1, "height": 1, "frames": 1}, "fixture")


if __name__ == "__main__":
    unittest.main()
