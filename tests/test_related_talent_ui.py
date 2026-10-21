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

import related_talent_ui  # noqa: E402


def _git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class RelatedTalentUITests(unittest.TestCase):
    def _png(self, size: tuple[int, int], colour: tuple[int, int, int, int]) -> bytes:
        image = Image.new("RGBA", size, colour)
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    def _fixture(
        self,
        root: Path,
        *,
        entry_updates: dict[str, dict[str, object]] | None = None,
        source_updates: dict[str, object] | None = None,
        decision_updates: dict[str, object] | None = None,
        acceptance_updates: dict[str, object] | None = None,
        data_updates: dict[str, bytes] | None = None,
    ) -> dict[str, object]:
        payload_dir = root / "payloads"
        payload_dir.mkdir(parents=True, exist_ok=True)
        entry_updates = entry_updates or {}
        data_updates = data_updates or {}
        entries: list[dict[str, object]] = []
        sizes = {
            "/shared/global/talents/images/talents/icon-over-grey.gif": (52, 48),
            "/shared/global/talents/images/talents/icon-over-green.gif": (52, 48),
            "/shared/global/talents/images/talents/icon-over-yellow.gif": (52, 48),
            "/shared/global/talents/includes/images/reset.gif": (60, 20),
            "/shared/global/talents/includes/images/resetall.gif": (80, 20),
            "/shared/global/talents/includes/images/printableversion.gif": (130, 20),
        }
        for index, (target, expected) in enumerate(related_talent_ui.UI_TARGETS.items()):
            canonical = str(expected["route"])
            repository_path = str(expected["repository_path"])
            data = data_updates.get(target)
            if data is None:
                width, height = sizes[target]
                data = self._png((width, height), (32 + index, 96, 160, 255))
            payload = payload_dir / Path(repository_path).name
            payload.write_bytes(data)
            entry: dict[str, object] = {
                "target_route": target,
                "route": canonical,
                "repository_path": repository_path,
                "sha256": hashlib.sha256(data).hexdigest(),
                "length": len(data),
                "git_blob_sha1": _git_blob_sha1(data),
                "format": "PNG",
                "width": int(expected["width"]),
                "height": int(expected["height"]),
                "frames": 1,
                "classification": related_talent_ui.EXPECTED_CLASSIFICATION,
                "original_capture_timestamp": None,
                "payload_path": payload.relative_to(root).as_posix(),
            }
            entry.update(entry_updates.get(target, {}))
            entries.append(entry)

        source: dict[str, object] = {
            "repository_url": related_talent_ui.EXPECTED_REPOSITORY_URL,
            "commit_sha": related_talent_ui.EXPECTED_COMMIT_SHA,
            "tree_sha": related_talent_ui.EXPECTED_TREE_SHA,
            "zip_url": "https://example.invalid/ui.zip",
            "downloaded_utc": "2026-10-21T04:39:55.289652+00:00",
            "original_capture_timestamp": None,
            "classification": related_talent_ui.EXPECTED_CLASSIFICATION,
        }
        source.update(source_updates or {})

        acceptance: dict[str, object] = {
            "schema": related_talent_ui.EXPECTED_ACCEPTANCE_SCHEMA,
            "accepted_source": True,
            "repository_url": related_talent_ui.EXPECTED_REPOSITORY_URL,
            "commit_sha": related_talent_ui.EXPECTED_COMMIT_SHA,
            "tree_sha": related_talent_ui.EXPECTED_TREE_SHA,
            "original_2008_images_recovered": 0,
            "published_images": 0,
        }
        acceptance.update(acceptance_updates or {})
        acceptance_path = root / "acceptance.json"
        acceptance_path.write_text(json.dumps(acceptance, sort_keys=True), encoding="utf-8")
        acceptance_sha = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()

        decision_targets = [
            {key: value for key, value in entry.items() if key != "payload_path"}
            for entry in entries
        ]
        decision: dict[str, object] = {
            "schema": related_talent_ui.EXPECTED_DECISION_SCHEMA,
            "accepted_for_browser_supplement": True,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "source": {
                "repository_url": related_talent_ui.EXPECTED_REPOSITORY_URL,
                "commit_sha": related_talent_ui.EXPECTED_COMMIT_SHA,
                "tree_sha": related_talent_ui.EXPECTED_TREE_SHA,
                "classification": related_talent_ui.EXPECTED_CLASSIFICATION,
                "original_capture_timestamp": None,
            },
            "accepted_ui_count": 6,
            "accepted_source_bytes": sum(int(entry["length"]) for entry in entries),
            "original_capture_timestamp": None,
            "original_2008_images_recovered": 0,
            "targets": decision_targets,
        }
        decision.update(decision_updates or {})
        decision_path = root / "decision.json"
        decision_path.write_text(json.dumps(decision, sort_keys=True), encoding="utf-8")
        decision_sha = hashlib.sha256(decision_path.read_bytes()).hexdigest()

        source_map: dict[str, object] = {
            "schema": related_talent_ui.EXPECTED_MAP_SCHEMA,
            "decision": "decision.json",
            "decision_sha256": decision_sha,
            "source_acceptance": "acceptance.json",
            "source_acceptance_sha256": acceptance_sha,
            "source": source,
            "ui_count": 6,
            "entries": entries,
        }
        map_path = root / "input-map.json"
        map_path.write_text(json.dumps(source_map, sort_keys=True), encoding="utf-8")
        map_sha = hashlib.sha256(map_path.read_bytes()).hexdigest()
        total = sum(int(entry["length"]) for entry in entries)
        fixture_targets = {
            target: {
                **dict(expected),
                "sha256": entry["sha256"],
                "length": entry["length"],
                "git_blob_sha1": entry["git_blob_sha1"],
            }
            for target, entry in zip(related_talent_ui.UI_TARGETS, entries)
            for expected in (related_talent_ui.UI_TARGETS[target],)
        }
        return {
            "map_path": map_path,
            "map_sha": map_sha,
            "decision_sha": decision_sha,
            "acceptance_sha": acceptance_sha,
            "total": total,
            "entries": entries,
            "ui_targets": fixture_targets,
        }

    def _load(self, fixture: dict[str, object], root: Path):
        with mock.patch.multiple(
            related_talent_ui,
            EXPECTED_MAP_SHA256=fixture["map_sha"],
            EXPECTED_DECISION_SHA256=fixture["decision_sha"],
            EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
            EXPECTED_TOTAL_BYTES=fixture["total"],
            UI_TARGETS=fixture["ui_targets"],
        ):
            return related_talent_ui.load_related_talent_ui_bundle(
                fixture["map_path"], root, "/WOW-Encyclopedia-Deployable-Archive/"
            )

    def test_success_preserves_six_pngs_and_public_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root)
            bundle = self._load(fixture, root)
            self.assertEqual(len(bundle.assets), 6)
            self.assertEqual(sum(len(asset.data) for asset in bundle.assets), fixture["total"])
            self.assertEqual(bundle.catalog_relative, "__offline/related-talent-ui.json")
            self.assertEqual(bundle.estimated_bytes, fixture["total"] + len(bundle.catalog_bytes))
            self.assertEqual(bundle.source_metadata["map_sha256"], fixture["map_sha"])
            self.assertEqual(bundle.source_metadata["ui_count"], 6)
            self.assertIn(
                'href="/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-icons.json"',
                bundle.notice_html,
            )
            self.assertIn(
                'href="/WOW-Encyclopedia-Deployable-Archive/__offline/related-talent-ui.json"',
                bundle.notice_html,
            )
            self.assertIn("Icon sources.", bundle.notice_html)
            self.assertIn("Interface sources.", bundle.notice_html)
            self.assertNotIn("Original icon directory", bundle.notice_html)
            self.assertNotIn("Interface image directory", bundle.notice_html)
            catalog_text = bundle.catalog_bytes.decode("utf-8")
            self.assertNotIn("payload_path", catalog_text)
            self.assertNotIn("zip_url", catalog_text)
            self.assertNotIn("example.invalid", catalog_text)
            for asset in bundle.assets:
                self.assertEqual(asset.mime, "image/png")
                self.assertEqual(asset.relative, asset.route[1:])
                self.assertEqual(bundle.route_reuses[asset.target_route], asset.route)
                self.assertEqual(asset.metadata["sha256"], hashlib.sha256(asset.data).hexdigest())

    def test_rejects_unaccepted_or_wrongly_bound_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root, decision_updates={"accepted_for_browser_supplement": False})
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "not accepted"):
                self._load(fixture, root)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root, source_updates={"classification": "2008_original"})
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "classification"):
                self._load(fixture, root)

    def test_rejects_traversal_and_noncanonical_route(self) -> None:
        target = next(iter(related_talent_ui.UI_TARGETS))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root, entry_updates={target: {"payload_path": "../outside.png"}})
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "traversal"):
                self._load(fixture, root)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root, entry_updates={target: {"route": "/other/ui.png"}})
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "exact UI target"):
                self._load(fixture, root)

    def test_rejects_payload_hash_drift_and_non_png(self) -> None:
        target = next(iter(related_talent_ui.UI_TARGETS))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root)
            payload = root / "payloads" / "icon-over-grey.png"
            drifted = bytearray(payload.read_bytes())
            drifted[0] ^= 0x01
            payload.write_bytes(bytes(drifted))
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "SHA mismatch"):
                self._load(fixture, root)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = io.BytesIO()
            Image.new("RGB", (52, 48), (2, 4, 8)).save(output, format="JPEG")
            fixture = self._fixture(root, data_updates={target: output.getvalue()})
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "not PNG"):
                self._load(fixture, root)

    def test_rejects_duplicate_target_and_nonnull_capture(self) -> None:
        targets = list(related_talent_ui.UI_TARGETS)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(
                root,
                entry_updates={targets[1]: {"target_route": targets[0]}},
            )
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "duplicate UI target"):
                self._load(fixture, root)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(
                root,
                entry_updates={targets[0]: {"original_capture_timestamp": "20080402010101"}},
            )
            with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "original_capture"):
                self._load(fixture, root)

    def test_rejects_query_base_path_before_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root)
            with mock.patch.multiple(
                related_talent_ui,
                EXPECTED_MAP_SHA256=fixture["map_sha"],
                EXPECTED_DECISION_SHA256=fixture["decision_sha"],
                EXPECTED_SOURCE_ACCEPTANCE_SHA256=fixture["acceptance_sha"],
                EXPECTED_TOTAL_BYTES=fixture["total"],
            ):
                with self.assertRaisesRegex(related_talent_ui.RelatedTalentUIError, "query"):
                    related_talent_ui.load_related_talent_ui_bundle(
                        fixture["map_path"], root, "/site?bad=1"
                    )

    def test_loader_does_not_overwrite_canonical_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root)
            existing = root / "__offline" / "related-talent-ui" / "icon-over-grey.png"
            existing.parent.mkdir(parents=True, exist_ok=True)
            sentinel = b"pre-existing-output"
            existing.write_bytes(sentinel)
            self._load(fixture, root)
            self.assertEqual(existing.read_bytes(), sentinel)
            self.assertFalse((root / "__offline" / "related-talent-ui" / "reset.png").exists())


if __name__ == "__main__":
    unittest.main()
