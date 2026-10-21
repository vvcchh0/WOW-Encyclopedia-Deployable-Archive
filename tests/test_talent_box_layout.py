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

import talent_box_layout as box  # noqa: E402


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TalentBoxLayoutTests(unittest.TestCase):
    def _gif(self, size: tuple[int, int], colour: tuple[int, int, int]) -> bytes:
        image = Image.new("RGB", size, colour)
        output = io.BytesIO()
        image.save(output, format="GIF")
        return output.getvalue()

    def _fixture(
        self,
        root: Path,
        *,
        entry_updates: dict[str, dict[str, object]] | None = None,
        map_updates: dict[str, object] | None = None,
        decision_updates: dict[str, object] | None = None,
        manifest_updates: dict[str, object] | None = None,
    ) -> dict[str, object]:
        site = root / "site"
        site.mkdir(parents=True, exist_ok=True)
        entry_updates = entry_updates or {}
        dimensions = {
            "bot-left.gif": (10, 13),
            "bot-right.gif": (10, 13),
            "bot.gif": (140, 13),
            "left.gif": (10, 56),
            "right.gif": (10, 64),
            "top-left.gif": (10, 13),
            "top-right.gif": (10, 13),
            "top.gif": (106, 13),
        }
        entries: list[dict[str, object]] = []
        files: list[dict[str, object]] = []
        for index, (target, expected) in enumerate(box._EXPECTED_ENTRIES.items()):
            source = str(expected["source_route"])
            name = source.rsplit("/", 1)[-1]
            data = self._gif(dimensions[name], (10 + index, 40, 90))
            source_file = site / source.lstrip("/")
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_bytes(data)
            capture = f"2008040207{2440 + index:04d}"
            entry: dict[str, object] = {
                "target_route": target,
                "source_route": source,
                "page_routes": list(box.EXPECTED_PAGE_ROUTES),
                "source_original_url": "http://www.worldofwarcraft.com" + source,
                "source_capture_timestamp": capture,
                "source_memento_datetime": "fixture",
                "sha256": _sha(data),
                "length": len(data),
                "format": "GIF",
                "dimensions": list(dimensions[name]),
                "frames": 1,
                "layout_role": "talent_points_box_" + name.removesuffix(".gif"),
                "classification": box.EXPECTED_CLASSIFICATION,
                "target_capture_timestamp": None,
            }
            entry.update(entry_updates.get(target, {}))
            entries.append(entry)
            files.append(
                {
                    "route": source,
                    "output_path": (Path("site") / source.lstrip("/")).as_posix(),
                    "source_base_url": entry["source_original_url"],
                    "source_sha256": entry["sha256"],
                    "derived_sha256": entry["sha256"],
                    "source_length": entry["length"],
                    "derived_length": entry["length"],
                    "source_mime": "image/gif",
                    "mime": "image/gif",
                    "actual_timestamp": entry["source_capture_timestamp"],
                    "transformed": False,
                }
            )
        manifest: dict[str, object] = {"schema_version": 1, "files": files}
        manifest.update(manifest_updates or {})
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        manifest_sha = _sha(manifest_path.read_bytes())
        decision: dict[str, object] = {
            "schema": box.EXPECTED_DECISION_SCHEMA,
            "accepted_for_compatibility_reuse": True,
            "classification": box.EXPECTED_CLASSIFICATION,
            "new_image_payloads": 0,
            "target_original_images_recovered": 0,
            "targets": entries,
            "bindings": [{"path": "manifest.json", "sha256": manifest_sha}],
        }
        decision.update(decision_updates or {})
        decision_path = root / "decision.json"
        decision_path.write_text(json.dumps(decision, sort_keys=True), encoding="utf-8")
        decision_sha = _sha(decision_path.read_bytes())
        source_map: dict[str, object] = {
            "schema": box.EXPECTED_MAP_SCHEMA,
            "classification": box.EXPECTED_CLASSIFICATION,
            "source_manifest_sha256": manifest_sha,
            "decision": "decision.json",
            "decision_sha256": decision_sha,
            "entries": entries,
        }
        source_map.update(map_updates or {})
        map_path = root / "input-map.json"
        map_path.write_text(json.dumps(source_map, sort_keys=True), encoding="utf-8")
        return {
            "map": map_path,
            "manifest": manifest_path,
            "manifest_data": manifest,
            "site": site,
            "map_sha": _sha(map_path.read_bytes()),
            "decision_sha": decision_sha,
            "manifest_sha": manifest_sha,
        }

    def _load(self, fixture: dict[str, object]):
        with mock.patch.multiple(
            box,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_MANIFEST_SHA256=fixture["manifest_sha"],
        ):
            return box.load_talent_box_layout_bundle(
                fixture["map"],
                fixture["map"].parent,
                fixture["site"],
                fixture["manifest"],
                fixture["manifest_data"],
            )

    def test_success_returns_eight_routes_nine_page_refs_and_no_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            before = sorted(path.relative_to(Path(tmp)).as_posix() for path in Path(tmp).rglob("*"))
            bundle = self._load(fixture)
            after = sorted(path.relative_to(Path(tmp)).as_posix() for path in Path(tmp).rglob("*"))
            self.assertEqual(before, after)
            self.assertIsInstance(bundle, box.LayoutCompatibilityBundle)
            self.assertEqual(len(bundle.route_reuses), 8)
            self.assertEqual(len(bundle.public_records), 8)
            self.assertEqual(set(bundle.per_page_records), set(box.EXPECTED_PAGE_ROUTES))
            self.assertTrue(all(len(records) == 8 for records in bundle.per_page_records.values()))
            self.assertEqual(
                sum(record["length"] for record in bundle.public_records),
                sum(row["source_length"] for row in fixture["manifest_data"]["files"]),
            )
            self.assertTrue(all("data" not in record and "source_local_path" not in record for record in bundle.public_records))
            self.assertTrue(all(record["target_capture_timestamp"] is None for record in bundle.public_records))
            self.assertEqual(
                bundle.route_reuses["/shared/global/talents/includes/images/bot-box/bot-left.gif"],
                "/info/classes/includes-new/images/bot-box/bot-left.gif",
            )

    def test_rejects_unaccepted_decision_and_wrong_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), decision_updates={"accepted_for_compatibility_reuse": False})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "not accepted"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), map_updates={"classification": "image_recovery"})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "classification"):
                self._load(fixture)

    def test_rejects_scope_page_target_source_and_existing_target(self) -> None:
        target = next(iter(box._EXPECTED_ENTRIES))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={target: {"target_capture_timestamp": "20080512"}})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "target capture"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={target: {"page_routes": list(box.EXPECTED_PAGE_ROUTES[:-1])}})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "page_routes"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), entry_updates={target: {"target_route": "/shared/global/talents/../bad.gif"}})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "traversal|scope"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            target_file = fixture["site"] / target.lstrip("/")
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_bytes(b"existing")
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "already exists"):
                self._load(fixture)

    def test_rejects_source_hash_drift_and_manifest_binding(self) -> None:
        target = next(iter(box._EXPECTED_ENTRIES))
        source = box._EXPECTED_ENTRIES[target]["source_route"]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            (fixture["site"] / str(source).lstrip("/")).write_bytes(b"drift")
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "SHA mismatch"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp), decision_updates={"bindings": []})
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "does not bind"):
                self._load(fixture)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            (fixture["site"] / str(source).lstrip("/")).unlink()
            with self.assertRaisesRegex(box.LayoutCompatibilityError, "source asset|cannot resolve"):
                self._load(fixture)


if __name__ == "__main__":
    unittest.main()
