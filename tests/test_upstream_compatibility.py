from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import offline_mirror as mirror  # noqa: E402


MAP_PATH = ROOT / "offline/upstream-compatibility-map.json"
VENDOR = ROOT / "offline/support/vendor/scriptaculous-1.6.5"


class UpstreamCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.map_data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        cls.item = cls.map_data["files"][0]

    def test_map_is_explicitly_non_wow_and_has_no_capture_timestamps(self) -> None:
        self.assertEqual(self.map_data["classification"], "upstream_compatibility_not_wow_capture")
        self.assertEqual(self.item["classification"], "upstream_compatibility_not_wow_capture")
        self.assertNotIn("actual_timestamp", self.item)
        self.assertNotIn("requested_timestamp", self.item)
        self.assertEqual(mirror.source_entry_classification(self.item), "upstream_compatibility")
        self.assertEqual(mirror.source_entry_classification({"logical_url": "http://www.worldofwarcraft.com/a.js"}), "wow_source")

    def test_candidate_bytes_and_license_hashes_are_stable(self) -> None:
        effects = (VENDOR / "effects.js").read_bytes()
        license_bytes = (VENDOR / "MIT-LICENSE").read_bytes()
        self.assertEqual(len(effects), 32635)
        self.assertEqual(hashlib.sha256(effects).hexdigest(), self.item["sha256"])
        self.assertEqual(hashlib.sha256(license_bytes).hexdigest(), self.item["upstream_compatibility"]["license_sha256"])

    def test_manifest_fields_preserve_compatibility_provenance(self) -> None:
        fields = mirror.upstream_compatibility_record_fields(self.item)
        self.assertEqual(fields["classification"], self.item["classification"])
        self.assertEqual(fields["supplement_note"], self.item["supplement_note"])
        self.assertEqual(fields["upstream_compatibility"], self.item["upstream_compatibility"])
        self.assertEqual(fields["upstream_compatibility"]["commit"], "d6c8f4110a068eb32ef59fc9e7eb4c6c5d3b0df6")

    def test_node_parse_evidence_is_successful_without_execution(self) -> None:
        evidence = json.loads((ROOT / "research/scriptaculous-compat-study/node-parse.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(evidence["execution"], "vm.Script parse only; no source execution")
        self.assertEqual(len(evidence["files"]), 3)
        self.assertTrue(all(item["compile"]["ok"] for item in evidence["files"]))
        effects = next(item for item in evidence["files"] if item["path"].endswith("candidate/effects.js"))
        self.assertTrue(effects["features"]["Element.setOpacity"])
        self.assertTrue(effects["features"]["Effect.Appear"])


if __name__ == "__main__":
    unittest.main()
