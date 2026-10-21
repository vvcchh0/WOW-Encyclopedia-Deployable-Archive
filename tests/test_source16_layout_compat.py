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

import source16_layout_compat as compat  # noqa: E402


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Source16LayoutCompatibilityTests(unittest.TestCase):
    def _image(self, fmt: str, size: tuple[int, int]) -> bytes:
        image = Image.new("RGBA", size, (0, 6, 31, 227)) if fmt == "PNG" else Image.new("RGB", size, (5, 6, 5))
        output = io.BytesIO()
        image.save(output, format=fmt)
        return output.getvalue()

    def _fixture(self, root: Path, *, entry_updates=None, decision_updates=None, map_updates=None, manifest_updates=None):
        entries = []
        files = []
        roles = {
            "ttip-tl.png": "corner-top-left", "ttip-tr.png": "corner-top-right", "ttip-t.png": "edge-top",
            "ttip-l.png": "edge-left", "ttip-r.png": "edge-right", "ttipbg.png": "interior-fill",
            "ttip-bl.png": "corner-bottom-left", "ttip-br.png": "corner-bottom-right", "ttip-b.png": "edge-bottom",
        }
        for index, (target, info) in enumerate(sorted(compat._EXPECTED_ENTRIES.items())):
            name = info["source_route"].rsplit("/", 1)[-1]
            fmt = "GIF" if name.endswith(".gif") else "PNG"
            size = (24, 24) if fmt == "GIF" else ((105, 49) if name == "ttipbg.png" else ((1, 7) if name in {"ttip-t.png", "ttip-b.png"} else ((7, 1) if name in {"ttip-l.png", "ttip-r.png"} else (7, 7))))
            data = self._image(fmt, size)
            source_route = info["source_route"]
            source_file = root / "site" / source_route.lstrip("/")
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_bytes(data)
            capture = f"2008040200{index:04d}"
            entry = {
                "page_route": info["page_route"], "target_route": target, "source_route": source_route,
                "source_original_url": "http://www.worldofwarcraft.com" + source_route,
                "source_capture_timestamp": capture, "source_memento_datetime": "fixture",
                "sha256": _sha(data), "length": len(data), "format": fmt, "dimensions": list(size), "frames": 1,
                "layout_role": roles.get(name, "return-arrow"), "classification": compat.EXPECTED_CLASSIFICATION,
                "target_capture_timestamp": None,
            }
            if entry_updates and target in entry_updates:
                entry.update(entry_updates[target])
            entries.append(entry)
            files.append({
                "route": source_route, "output_path": (Path("site") / source_route.lstrip("/")).as_posix(),
                "source_base_url": entry["source_original_url"], "source_sha256": entry["sha256"], "derived_sha256": entry["sha256"],
                "source_length": entry["length"], "derived_length": entry["length"], "source_mime": f"image/{fmt.lower()}",
                "mime": f"image/{fmt.lower()}", "actual_timestamp": entry["source_capture_timestamp"], "transformed": False,
            })
        manifest = {"schema_version": 1, "files": files}
        manifest.update(manifest_updates or {})
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        manifest_sha = _sha(manifest_path.read_bytes())
        decision = {
            "schema": compat.EXPECTED_DECISION_SCHEMA, "accepted_for_compatibility_reuse": True,
            "classification": compat.EXPECTED_CLASSIFICATION, "new_image_payloads": 0,
            "target_original_images_recovered": 0, "targets": entries,
            "bindings": [{"path": "manifest.json", "sha256": manifest_sha}],
        }
        decision.update(decision_updates or {})
        decision_path = root / "decision.json"
        decision_path.write_text(json.dumps(decision, sort_keys=True), encoding="utf-8")
        decision_sha = _sha(decision_path.read_bytes())
        source_map = {
            "schema": compat.EXPECTED_MAP_SCHEMA, "decision": "decision.json", "decision_sha256": decision_sha,
            "source_manifest_sha256": manifest_sha, "classification": compat.EXPECTED_CLASSIFICATION, "entries": entries,
        }
        source_map.update(map_updates or {})
        map_path = root / "input-map.json"
        map_path.write_text(json.dumps(source_map, sort_keys=True), encoding="utf-8")
        return {"map": map_path, "manifest": manifest_path, "manifest_data": manifest, "site": root / "site", "map_sha": _sha(map_path.read_bytes()), "decision_sha": decision_sha, "manifest_sha": manifest_sha}

    def _load(self, fixture):
        with mock.patch.multiple(
            compat,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_MANIFEST_SHA256=fixture["manifest_sha"],
        ):
            return compat.load_layout_compatibility_bundle(
                fixture["map"], fixture["map"].parent, fixture["site"], fixture["manifest"], fixture["manifest_data"]
            )

    def test_success_returns_routes_and_public_records_without_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            bundle = self._load(fixture)
            self.assertEqual(len(bundle.route_reuses), 10)
            self.assertEqual(len(bundle.public_records), 10)
            self.assertEqual(len(bundle.per_page_records["/info/items/tinfoilhat.xml"]), 9)
            self.assertEqual(bundle.route_reuses["/moltencore/images/backarrow.gif"], "/wrath/images/layout/backarrow.gif")
            self.assertTrue(all("data" not in row and "source_local_path" not in row for row in bundle.public_records))

    def test_rejects_unaccepted_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), decision_updates={"accepted_for_compatibility_reuse": False})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "not accepted"):
                self._load(fixture)

    def test_rejects_scope_traversal_and_nonnull_target_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={"/moltencore/images/backarrow.gif": {"target_route": "/moltencore/images/../x.gif"}})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "scope|empty/traversal"):
                self._load(fixture)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={"/moltencore/images/backarrow.gif": {"target_capture_timestamp": "20080512"}})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "target capture"):
                self._load(fixture)

    def test_rejects_duplicate_mapping_and_source_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={"/moltencore/images/backarrow.gif": {"target_route": "/info/items/images/tinfoilhat/ttip-tl.png"}})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "duplicate|scope"):
                self._load(fixture)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            (fixture["site"] / "wrath/images/layout/ttip-tl.png").unlink()
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "source asset|manifest output"):
                self._load(fixture)

    def test_rejects_source_hash_drift_and_existing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            source = fixture["site"] / "wrath/images/layout/ttip-tl.png"
            source.write_bytes(b"drift")
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "SHA mismatch"):
                self._load(fixture)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            target = fixture["site"] / "info/items/images/tinfoilhat/ttip-tl.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"existing")
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "already exists"):
                self._load(fixture)

    def test_rejects_wrong_classification_and_manifest_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), map_updates={"classification": "image_recovery"})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "classification"):
                self._load(fixture)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), manifest_updates={"files": []})
            with self.assertRaisesRegex(compat.LayoutCompatibilityError, "missing from source manifest|manifest"):
                self._load(fixture)


if __name__ == "__main__":
    unittest.main()
