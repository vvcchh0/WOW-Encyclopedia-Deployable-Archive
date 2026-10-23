from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TEST_TEMP_ROOT = ROOT / ".scratch" / "test-temp-20261023"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import historical_export_store as store_tool  # noqa: E402


def _sha(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    length = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
            length += len(chunk)
    return digest.hexdigest(), length


class HistoricalExportStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(prefix="historical-export-store-", dir=TEST_TEMP_ROOT)
        self.base = Path(self._tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        (self.repo / ".scratch").mkdir()
        (self.repo / "research").mkdir()
        self.store = self.repo / "artifacts" / "historical-exports-20261023"
        self.plan = self.repo / "research" / "export-plan.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _tree(self, name: str) -> Path:
        path = self.repo / ".scratch" / name
        path.mkdir(parents=True)
        return path

    def _build(self, trees: list[Path]) -> dict:
        relative = [tree.relative_to(self.repo).as_posix() for tree in trees]
        self.plan.write_text(json.dumps({"trees": relative}), encoding="utf-8")
        return store_tool.build_store(plan=self.plan, store=self.store, repo_root=self.repo, floor_bytes=0)

    @staticmethod
    def _relative_paths(root: Path) -> set[str]:
        return {path.relative_to(root).as_posix() for path in root.rglob("*")}

    def test_cross_version_dedup_and_complete_round_trip(self) -> None:
        first = self._tree("pages-fixture-v1")
        second = self._tree("pages-fixture-v2")
        for tree in (first, second):
            (tree / "assets").mkdir()
            (tree / "empty").mkdir()
            (tree / ".hidden").write_bytes(b"hidden content shared across versions")
            (tree / "export-provenance.json").write_text('{"source":"fixture"}\n', encoding="utf-8")
            (tree / "assets" / "same.bin").write_bytes(b"same payload" * 4096)
            (tree / "assets" / "same-again.bin").write_bytes(b"same payload" * 4096)
        (second / "only-v2.html").write_text("extra file absent from old provenance", encoding="utf-8")

        result = self._build([first, second])
        self.assertTrue(result["accepted"])
        self.assertLess(result["unique_object_bytes"], result["logical_version_bytes"])
        self.assertEqual(
            store_tool.verify_store(store=self.store, originals=True, repo_root=self.repo)["originals"]["all_contents_match"],
            True,
        )

        catalog = json.loads((self.store / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["objects"]), 4)  # shared hidden, provenance, payload, and v2-only file
        manifest = store_tool._read_manifest(self.store, catalog["manifests"][0])
        self.assertIn(".hidden", {item["path"] for item in manifest["files"]})
        self.assertIn("export-provenance.json", {item["path"] for item in manifest["files"]})
        self.assertIn("empty", {item["path"] for item in manifest["directories"]})
        self.assertEqual(
            sum(item["bytes"] for item in manifest["files"]),
            next(item["logical_bytes"] for item in catalog["versions"] if item["version_id"].endswith("pages-fixture-v1")),
        )

        destination = self.base / "restored-v2"
        restored = store_tool.restore_version(store=self.store, version="pages-fixture-v2", dest=destination, floor_bytes=0)
        self.assertTrue(restored["verified"])
        for relative in (".hidden", "export-provenance.json", "assets/same.bin", "assets/same-again.bin", "empty", "only-v2.html"):
            original = second / relative
            recreated = destination / relative
            self.assertEqual(original.is_dir(), recreated.is_dir(), relative)
            if original.is_file():
                self.assertEqual(original.read_bytes(), recreated.read_bytes(), relative)
                self.assertEqual(original.stat().st_mtime_ns, recreated.stat().st_mtime_ns, relative)

    def test_corrupt_object_or_manifest_is_rejected(self) -> None:
        tree = self._tree("pages-fixture-corruption")
        (tree / "payload.bin").write_bytes(b"object bytes that must be checked")
        self._build([tree])

        corrupt_object = self.base / "corrupt-object-store"
        shutil.copytree(self.store, corrupt_object)
        with zipfile.ZipFile(corrupt_object / "objects.zip", "r") as original:
            members = [(info.filename, original.read(info.filename)) for info in original.infolist()]
        name, payload = members[0]
        changed = bytes([payload[0] ^ 0x01]) + payload[1:]
        with zipfile.ZipFile(corrupt_object / "objects.zip", "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as output:
            output.writestr(name, changed)
        receipt_path = corrupt_object / "acceptance.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        digest, length = _sha(corrupt_object / "objects.zip")
        receipt["objects_archive"] = {"path": "objects.zip", "bytes": length, "sha256": digest}
        receipt_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        with self.assertRaises(store_tool.StoreError):
            store_tool.verify_store(store=corrupt_object)

        corrupt_manifest = self.base / "corrupt-manifest-store"
        shutil.copytree(self.store, corrupt_manifest)
        catalog = json.loads((corrupt_manifest / "catalog.json").read_text(encoding="utf-8"))
        manifest_path = corrupt_manifest / catalog["manifests"][0]["path"]
        raw = bytearray(manifest_path.read_bytes())
        raw[-1] ^= 0x01
        manifest_path.write_bytes(raw)
        with self.assertRaises(store_tool.StoreError):
            store_tool.verify_store(store=corrupt_manifest)

    def test_dangerous_manifest_paths_and_case_collisions_are_rejected(self) -> None:
        base = {
            "schema": store_tool.MANIFEST_SCHEMA,
            "version_id": ".scratch/pages-fixture-safe",
            "tree_mtime_ns": 1,
            "directories": [],
            "files": [{"path": "../escape", "bytes": 1, "sha256": "0" * 64, "mtime_ns": 1}],
        }
        with self.assertRaises(store_tool.StoreError):
            store_tool._validate_manifest(base)
        base["files"] = [
            {"path": "images/A.png", "bytes": 1, "sha256": "0" * 64, "mtime_ns": 1},
            {"path": "images/a.png", "bytes": 1, "sha256": "1" * 64, "mtime_ns": 1},
        ]
        base["directories"] = [{"path": "images", "mtime_ns": 1}]
        with self.assertRaises(store_tool.StoreError):
            store_tool._validate_manifest(base)

    def test_reparse_source_directory_is_rejected(self) -> None:
        tree = self._tree("pages-fixture-reparse")
        self.plan.write_text(json.dumps({"trees": [tree.relative_to(self.repo).as_posix()]}), encoding="utf-8")
        real_reparse_check = store_tool._is_reparse_or_link

        def simulated_reparse(path: Path) -> bool:
            return path == tree or real_reparse_check(path)

        with patch.object(store_tool, "_is_reparse_or_link", side_effect=simulated_reparse):
            with self.assertRaises(store_tool.StoreError):
                store_tool.build_store(plan=self.plan, store=self.store, repo_root=self.repo, floor_bytes=0)

    def test_build_rejects_store_inside_source_without_creating_paths(self) -> None:
        tree = self._tree("pages-fixture-output-isolation")
        (tree / "index.html").write_text("source remains unchanged", encoding="utf-8")
        self.plan.write_text(json.dumps({"trees": [tree.relative_to(self.repo).as_posix()]}), encoding="utf-8")
        before = self._relative_paths(tree)
        nested_store = tree / "new-output-parent" / "store"

        with self.assertRaisesRegex(store_tool.StoreError, "outside every source tree"):
            store_tool.build_store(plan=self.plan, store=nested_store, repo_root=self.repo, floor_bytes=0)

        self.assertEqual(self._relative_paths(tree), before)
        self.assertFalse((tree / "new-output-parent").exists())

    def test_restore_refuses_existing_destination_without_overwriting(self) -> None:
        tree = self._tree("pages-fixture-destination")
        (tree / "index.html").write_text("original", encoding="utf-8")
        self._build([tree])
        destination = self.base / "already-there"
        destination.mkdir()
        sentinel = destination / "keep.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaises(store_tool.StoreError):
            store_tool.restore_version(store=self.store, version="pages-fixture-destination", dest=destination, floor_bytes=0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")

    def test_restore_rejects_dest_inside_or_ancestor_of_store_without_mutation(self) -> None:
        tree = self._tree("pages-fixture-restore-isolation")
        (tree / "index.html").write_text("restorable source", encoding="utf-8")
        self._build([tree])
        before = self._relative_paths(self.store)

        destinations = [self.store / "restored-inside", self.store.parent]
        for destination in destinations:
            with self.subTest(destination=destination):
                with self.assertRaisesRegex(store_tool.StoreError, "outside the store"):
                    store_tool.restore_version(
                        store=self.store,
                        version="pages-fixture-restore-isolation",
                        dest=destination,
                        floor_bytes=0,
                    )
                self.assertEqual(self._relative_paths(self.store), before)
        self.assertFalse((self.store / "restored-inside").exists())


if __name__ == "__main__":
    unittest.main()
