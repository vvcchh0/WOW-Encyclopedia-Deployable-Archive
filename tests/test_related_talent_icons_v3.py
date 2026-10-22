from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import related_talent_icons  # noqa: E402


class RelatedTalentIconV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / ".scratch" / "test-temp-20261022"
        cls.scratch.mkdir(parents=True, exist_ok=True)

    def test_real_v3_preserves_v2_assets_notice_and_catalog_rows(self) -> None:
        base_path = "/WOW-Encyclopedia-Deployable-Archive"
        v2_map = ROOT / related_talent_icons.EXPECTED_V2_MAP_RELATIVE
        v3_map = ROOT / related_talent_icons.EXPECTED_V3_MAP_RELATIVE
        v2 = related_talent_icons.load_related_talent_bundle(v2_map, ROOT, base_path)
        v3 = related_talent_icons.load_related_talent_bundle(v3_map, ROOT, base_path)

        self.assertEqual(len(v2.assets), 1006)
        self.assertEqual(len(v3.assets), 1024)
        self.assertEqual(v3.assets[:1006], v2.assets)
        self.assertEqual(v3.notice_html, v2.notice_html)
        self.assertEqual(v3.catalog_relative, v2.catalog_relative)
        self.assertEqual(v3.source_acceptance_sha256, v2.source_acceptance_sha256)
        self.assertEqual(v3.per_class_counts["mage"], v2.per_class_counts["mage"] + 2)
        self.assertEqual(v3.per_class_counts["paladin"], v2.per_class_counts["paladin"] + 2)
        self.assertEqual(v3.per_class_counts["rogue"], v2.per_class_counts["rogue"] + 4)
        self.assertEqual(v3.per_class_counts["shaman"], v2.per_class_counts["shaman"] + 2)
        self.assertEqual(v3.per_class_counts["warrior"], v2.per_class_counts["warrior"] + 8)
        self.assertEqual(v3.source_metadata["ordinary_icon_count"], 986)
        self.assertEqual(v3.source_metadata["v2_mapped_icon_count"], 20)
        self.assertEqual(v3.source_metadata["v3_mapped_icon_count"], 18)
        self.assertEqual(v3.source_metadata["mapped_icon_count"], 38)
        self.assertEqual(v3.source_metadata["source_bytes"], 1_079_648)
        self.assertEqual(v3.source_metadata["mapped_source_bytes"], 41_259)
        self.assertEqual(v3.source_metadata["v3_mapped_source_bytes"], 19_439)
        self.assertEqual(v3.source_metadata["original_capture_timestamp"], None)
        self.assertEqual(v3.source_metadata["original_2008_images_recovered"], 0)
        self.assertEqual(v3.estimated_bytes, sum(len(asset.data) for asset in v3.assets) + len(v3.catalog_bytes))

        v2_catalog = json.loads(v2.catalog_bytes)
        v3_catalog = json.loads(v3.catalog_bytes)
        self.assertEqual(v3_catalog["schema"], "wow-related-talent-icon-catalog/v2")
        self.assertEqual(v3_catalog["assets"][:1006], v2_catalog["assets"])
        self.assertEqual(v3_catalog["mappings"][:20], v2_catalog["mappings"])
        self.assertEqual(len(v3_catalog["assets"]), 1024)
        self.assertEqual(len(v3_catalog["mappings"]), 38)
        new_assets = v3.assets[1006:]
        self.assertEqual(len(new_assets), 18)
        self.assertTrue(all(asset.metadata["old_data_sha256"] != asset.metadata["old_source_data_sha256"] for asset in new_assets))
        self.assertTrue(all(any(ref.startswith("old-derived-data-sha256:") for ref in asset.source_refs) for asset in new_assets))
        new_mappings = v3_catalog["mappings"][20:]
        self.assertTrue(all("old_source_data_sha256" in mapping for mapping in new_mappings))
        self.assertTrue(all(mapping["original_2008_pixel_identity"] == "unknown" for mapping in new_mappings))
        for forbidden in ("payload_path", "private/http", "private\\http"):
            self.assertNotIn(forbidden, v3.catalog_bytes.decode("utf-8"))

    def _copy_v3_validation_workspace(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory(dir=self.scratch)
        root = Path(temp.name)
        relative_inputs = (
            related_talent_icons.EXPECTED_V3_MAP_RELATIVE,
            related_talent_icons.EXPECTED_V3_DECISION_RELATIVE,
            related_talent_icons.EXPECTED_V3_PINS_RELATIVE,
            related_talent_icons.EXPECTED_V3_ROOT_ACCEPTANCE_RELATIVE,
            related_talent_icons.EXPECTED_V3_PREPARATION_RELATIVE,
            related_talent_icons.EXPECTED_V3_AUDIT_RELATIVE,
            related_talent_icons.EXPECTED_V3_SOURCE_ACCEPTANCE_RELATIVE,
            related_talent_icons.EXPECTED_V3_BASE_MAP_RELATIVE,
        )
        for relative in relative_inputs:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

        source_map = json.loads((ROOT / related_talent_icons.EXPECTED_V3_MAP_RELATIVE).read_text(encoding="utf-8"))
        for entry in source_map["entries"]:
            source = ROOT / entry["payload_path"]
            target = root / entry["payload_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        for class_name in ("mage", "paladin", "rogue", "shaman", "warrior"):
            source16 = ROOT / ".scratch/offline-non-gallery-20261021-v16/site/shared/global/talents" / class_name / "data.js"
            v55 = ROOT / related_talent_icons.EXPECTED_V3_V55_EXPORT_RELATIVE / "shared/global/talents" / class_name / "data.js"
            for source, target in (
                (source16, root / ".scratch/offline-non-gallery-20261021-v16/site/shared/global/talents" / class_name / "data.js"),
                (v55, root / related_talent_icons.EXPECTED_V3_V55_EXPORT_RELATIVE / "shared/global/talents" / class_name / "data.js"),
            ):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        return temp, root / related_talent_icons.EXPECTED_V3_MAP_RELATIVE

    def test_rejects_corrupted_v3_payload_bytes(self) -> None:
        temp, map_path = self._copy_v3_validation_workspace()
        try:
            map_data = json.loads(map_path.read_text(encoding="utf-8"))
            payload = Path(temp.name) / map_data["entries"][0]["payload_path"]
            corrupted = bytearray(payload.read_bytes())
            corrupted[-10] ^= 0x01
            payload.write_bytes(corrupted)
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "SHA mismatch"):
                related_talent_icons._validate_v3_bindings(map_path, Path(temp.name))
        finally:
            temp.cleanup()

    def test_rejects_map_binding_drift(self) -> None:
        temp = tempfile.TemporaryDirectory(dir=self.scratch)
        try:
            root = Path(temp.name)
            relative = related_talent_icons.EXPECTED_V3_MAP_RELATIVE
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
            changed = json.loads(target.read_text(encoding="utf-8"))
            changed["entries"][0]["old_source_data_sha256"] = "0" * 64
            target.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "input map SHA mismatch"):
                related_talent_icons._validate_v3_bindings(target, root)
        finally:
            temp.cleanup()

    def test_rejects_unselected_effect_candidate(self) -> None:
        audit = json.loads((ROOT / related_talent_icons.EXPECTED_V3_AUDIT_RELATIVE).read_text(encoding="utf-8"))
        selected = set(related_talent_icons.EXPECTED_V3_SELECTED_IDS)
        candidate = next(row for row in audit["new_same_class_candidates"] if row["candidate_id"] not in selected)
        entry = {
            "mapping_id": candidate["candidate_id"],
            "route": candidate["old_2008_target"]["routes"][1],
            "class": candidate["class"],
            "talent": candidate["old_2008_target"]["canonical_talent_title"],
            "state": "on",
        }
        with self.assertRaisesRegex(related_talent_icons.RelatedTalentIconError, "outside the nine selected"):
            related_talent_icons._validate_v3_entry_semantics(entry, candidate, {}, {})


if __name__ == "__main__":
    unittest.main()
