from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import related_talent_icons  # noqa: E402


class RelatedTalentIconV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / ".scratch" / "test-temp-20261022"
        cls.scratch.mkdir(parents=True, exist_ok=True)

    def test_real_v2_keeps_the_v1_assets_and_notice_unchanged(self) -> None:
        v1_map = ROOT / related_talent_icons.EXPECTED_V2_BASE_MAP_RELATIVE
        v2_map = ROOT / related_talent_icons.EXPECTED_V2_MAP_RELATIVE
        v1 = related_talent_icons._load_v1_related_talent_bundle(
            v1_map, ROOT, "/WOW-Encyclopedia-Deployable-Archive"
        )
        public_v1 = related_talent_icons.load_related_talent_bundle(
            v1_map, ROOT, "/WOW-Encyclopedia-Deployable-Archive"
        )
        v2 = related_talent_icons.load_related_talent_bundle(
            v2_map, ROOT, "/WOW-Encyclopedia-Deployable-Archive"
        )

        self.assertEqual(len(v1.assets), 986)
        self.assertEqual(public_v1, v1)
        self.assertEqual(len(v2.assets), 1006)
        self.assertEqual(v2.assets[:986], v1.assets)
        self.assertEqual(v2.notice_html, v1.notice_html)
        self.assertEqual(v2.catalog_relative, v1.catalog_relative)
        self.assertEqual(v2.per_class_counts["paladin"], v1.per_class_counts["paladin"] + 6)
        self.assertEqual(v2.per_class_counts["hunter"], v1.per_class_counts["hunter"] + 4)
        self.assertEqual(v2.per_class_counts["rogue"], v1.per_class_counts["rogue"] + 2)
        self.assertEqual(v2.per_class_counts["warrior"], v1.per_class_counts["warrior"] + 8)
        self.assertEqual(v2.source_metadata["original_capture_timestamp"], None)
        self.assertEqual(v2.source_metadata["original_2008_images_recovered"], 0)
        self.assertEqual(v2.source_metadata["mapped_source_bytes"], 21820)
        self.assertEqual(v2.estimated_bytes, sum(len(asset.data) for asset in v2.assets) + len(v2.catalog_bytes))

        catalog = json.loads(v2.catalog_bytes)
        v1_catalog = json.loads(v1.catalog_bytes)
        self.assertEqual(catalog["schema"], "wow-related-talent-icon-catalog/v2")
        self.assertEqual(catalog["icon_count"], 1006)
        self.assertEqual(len(catalog["assets"]), 1006)
        self.assertEqual(catalog["assets"][:986], v1_catalog["assets"])
        self.assertEqual(len(catalog["mappings"]), 20)
        mapping = catalog["mappings"][0]
        self.assertEqual(mapping["target_route"], v2.assets[986].route)
        self.assertEqual(mapping["source_repository_path"], v2.assets[986].metadata["source_repository_path"])
        self.assertEqual(mapping["original_2008_pixel_identity"], "unknown")
        self.assertIn(related_talent_icons.EXPECTED_COMMIT_SHA, mapping["source_image_url"])
        self.assertIn("path:" + mapping["source_repository_path"], v2.assets[986].source_refs)
        self.assertIn("reason:" + mapping["mapping_reason"], v2.assets[986].source_refs)
        public_text = v2.catalog_bytes.decode("utf-8")
        for forbidden in ("payload_path", "private/http", "private\\http"):
            self.assertNotIn(forbidden, public_text)

    def _tampered_binding_workspace(self, mutate) -> tuple[tempfile.TemporaryDirectory, Path, dict[str, str]]:
        temp = tempfile.TemporaryDirectory(dir=self.scratch)
        root = Path(temp.name)
        source_root = ROOT
        for relative in (
            related_talent_icons.EXPECTED_V2_MAP_RELATIVE,
            related_talent_icons.EXPECTED_V2_DECISION_RELATIVE,
            related_talent_icons.EXPECTED_V2_PINS_RELATIVE,
            related_talent_icons.EXPECTED_V2_ACCEPTANCE_RELATIVE,
            related_talent_icons.EXPECTED_V2_AUDIT_RELATIVE,
            related_talent_icons.EXPECTED_V2_BASE_MAP_RELATIVE,
        ):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_root / relative, destination)

        map_path = root / related_talent_icons.EXPECTED_V2_MAP_RELATIVE
        decision_path = root / related_talent_icons.EXPECTED_V2_DECISION_RELATIVE
        pins_path = root / related_talent_icons.EXPECTED_V2_PINS_RELATIVE
        map_data = json.loads(map_path.read_text(encoding="utf-8"))
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        mutate(map_data, decision)
        map_data["entries"] = decision["entries"]
        decision_raw = (json.dumps(decision, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        decision_path.write_bytes(decision_raw)
        decision_sha = hashlib.sha256(decision_raw).hexdigest()
        map_data["decision_sha256"] = decision_sha
        map_raw = (json.dumps(map_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        map_path.write_bytes(map_raw)
        map_sha = hashlib.sha256(map_raw).hexdigest()
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
        pins["map_sha256"] = map_sha
        pins["decision_sha256"] = decision_sha
        pins_path.write_text(json.dumps(pins, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        expected_pins = dict(related_talent_icons.EXPECTED_V2_ROOT_PINS)
        expected_pins["map_sha256"] = map_sha
        expected_pins["decision_sha256"] = decision_sha
        patched = {
            "EXPECTED_V2_MAP_SHA256": map_sha,
            "EXPECTED_V2_DECISION_SHA256": decision_sha,
            "EXPECTED_V2_ROOT_PINS": expected_pins,
        }
        return temp, map_path, patched

    def _assert_v2_bindings_reject(self, mutate, expected_message: str) -> None:
        temp, map_path, patched = self._tampered_binding_workspace(mutate)
        try:
            with mock.patch.multiple(
                related_talent_icons,
                **patched,
            ):
                with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, expected_message):
                    related_talent_icons._validate_v2_bindings(map_path, Path(temp.name))
        finally:
            temp.cleanup()

    def test_rejects_cross_class_reuse_even_when_map_and_decision_agree(self) -> None:
        def mutate(map_data, decision):
            map_data["entries"][0]["route"] = map_data["entries"][0]["route"].replace("/paladin/", "/rogue/")
            decision["entries"][0]["route"] = map_data["entries"][0]["route"]

        self._assert_v2_bindings_reject(mutate, "crosses talent classes")

    def test_rejects_duplicate_payload_paths(self) -> None:
        def mutate(map_data, decision):
            duplicate_payload = map_data["entries"][0]["payload_path"]
            map_data["entries"][1]["payload_path"] = duplicate_payload
            decision["entries"][1]["payload_path"] = duplicate_payload

        self._assert_v2_bindings_reject(mutate, "duplicate v2 payload path")

    def test_rejects_payload_traversal(self) -> None:
        def mutate(map_data, decision):
            map_data["entries"][0]["payload_path"] = "../outside.jpg"
            decision["entries"][0]["payload_path"] = "../outside.jpg"

        self._assert_v2_bindings_reject(mutate, "traversal")

    def test_shared_image_validator_rejects_png_disguised_as_jpeg(self) -> None:
        output = io.BytesIO()
        Image.new("RGB", (36, 36), (10, 20, 30)).save(output, format="PNG")
        with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "decodes as PNG"):
            related_talent_icons._validate_image(
                output.getvalue(),
                {"format": "JPEG", "width": 36, "height": 36, "frames": 1},
                "/shared/global/talents/paladin/images/holy/example.jpg",
            )


if __name__ == "__main__":
    unittest.main()
