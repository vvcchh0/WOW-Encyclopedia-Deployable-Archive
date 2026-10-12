from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import release_archive


class ReleaseArchiveTests(unittest.TestCase):
    def test_split_verify_and_join_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.zip"
            payload = bytes(range(256)) * 11
            source.write_bytes(payload)
            output = root / "assets"
            result = release_archive.split_archive(source, output, 1000)
            self.assertTrue(result["accepted"])
            manifest = output / "release-assets.json"
            verification = release_archive.verify_parts(manifest)
            self.assertTrue(verification["accepted"])
            joined = root / "joined.zip"
            joined_result = release_archive.join_archive(manifest, joined)
            self.assertTrue(joined_result["accepted"])
            self.assertEqual(joined.read_bytes(), payload)
            self.assertEqual(hashlib.sha256(joined.read_bytes()).hexdigest(), hashlib.sha256(payload).hexdigest())
            self.assertEqual(len(list(output.glob("sample.zip.???"))), 3)

    def test_corrupt_part_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.zip"
            source.write_bytes(b"release-payload-" * 100)
            output = root / "assets"
            release_archive.split_archive(source, output, 600)
            part = output / "sample.zip.002"
            data = bytearray(part.read_bytes())
            data[0] ^= 0xFF
            part.write_bytes(data)
            with self.assertRaises(release_archive.ArchiveError):
                release_archive.verify_parts(output / "release-assets.json")

    def test_join_refuses_existing_output_and_cleans_new_partial_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.zip"
            source.write_bytes(b"a" * 2300)
            assets = root / "assets"
            release_archive.split_archive(source, assets, 1000)
            existing = root / "joined.zip"
            existing.write_bytes(b"keep")
            with self.assertRaises(release_archive.ArchiveError):
                release_archive.join_archive(assets / "release-assets.json", existing)
            self.assertEqual(existing.read_bytes(), b"keep")
            part = assets / "sample.zip.001"
            part.write_bytes(b"broken")
            target = root / "failed.zip"
            with self.assertRaises(release_archive.ArchiveError):
                release_archive.join_archive(assets / "release-assets.json", target)
            self.assertFalse(target.exists())
            self.assertFalse(Path(str(target) + ".partial").exists())

    def test_manifest_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "release-assets.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": release_archive.SCHEMA,
                        "source": {"filename": "source.zip", "length": 3, "sha256": "0" * 64},
                        "part_bytes": 10,
                        "parts": [
                            {"index": 1, "name": "../escape.001", "length": 1, "sha256": "0" * 64},
                            {"index": 2, "name": "part.002", "length": 1, "sha256": "0" * 64},
                            {"index": 3, "name": "part.003", "length": 1, "sha256": "0" * 64},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(release_archive.ArchiveError):
                release_archive.verify_parts(manifest)


if __name__ == "__main__":
    unittest.main()
