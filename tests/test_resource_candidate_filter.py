from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import filter_resource_candidates as candidate_filter  # noqa: E402


class ResourceCandidateFilterTests(unittest.TestCase):
    def _write_json(self, path: Path, value: object) -> Path:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_existing_primary_and_preview_images_are_excluded_but_foreign_same_path_remains(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifest = self._write_json(
                base / "build-manifest.json",
                {
                    "files": [
                        {
                            "route": "/images/frozen.jpg",
                            "kind": "image",
                            "mime": "image/jpeg",
                            "derived_sha256": "frozen-derived",
                        },
                        {
                            "route": "/images/former.html",
                            "kind": "html",
                            "mime": "text/html",
                            "derived_sha256": "html-derived",
                        },
                    ]
                },
            )
            preview = self._write_json(
                base / "export-provenance.json",
                {
                    "files": [
                        {
                            "route": "/images/overlay.gif",
                            "kind": "image",
                            "mime": "image/gif",
                            "derived_sha256": "overlay-derived",
                        }
                    ]
                },
            )
            candidates = self._write_json(
                base / "candidates.json",
                {
                    "items": [
                        {"logical_url": "http://www.worldofwarcraft.com/images/frozen.jpg"},
                        {"url": "https://worldofwarcraft.com/images/overlay.gif"},
                        {"original": "http://www.wow-europe.com/images/frozen.jpg"},
                        {"logical_url": "https://www.wow-europe.com/images/frozen.jpg"},
                        {"logical_url": "http://www.worldofwarcraft.com/images/former.html"},
                        {"logical_url": "not-a-url"},
                    ],
                },
            )
            output = base / "filtered.json"
            result = candidate_filter.filter_candidates(
                input_path=candidates,
                manifest_path=manifest,
                preview_provenance_path=preview,
                output_path=output,
            )

            self.assertEqual(result["stats"]["existing_route"], 2)
            self.assertEqual(result["stats"]["duplicate_route"], 1)
            self.assertEqual(result["stats"]["invalid"], 1)
            self.assertEqual(result["stats"]["remaining"], 2)
            remaining_routes = {item["route"] for item in result["remaining_candidates"]}
            self.assertIn("/_origins/www.wow-europe.com/images/frozen.jpg", remaining_routes)
            self.assertIn("/images/former.html", remaining_routes)
            existing = result["excluded"]["existing_route"]
            self.assertEqual(existing[0]["known_sha256"], "frozen-derived")
            self.assertEqual(existing[1]["source"], "preview_provenance")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["stats"], result["stats"])

    def test_same_origin_spelling_deduplicates_and_foreign_route_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifest = self._write_json(base / "manifest.json", {"files": []})
            candidates = self._write_json(
                base / "candidates.json",
                {
                    "candidates": [
                        {"logical_url": "http://worldofwarcraft.com/news/picture.jpg"},
                        {"logical_url": "https://www.worldofwarcraft.com/news/picture.jpg"},
                        {"logical_url": "https://www.wow-europe.com/news/picture.jpg"},
                        {"logical_url": "http://www.worldofwarcraft.com/../escape.jpg"},
                        {"logical_url": "http://user:pass@www.worldofwarcraft.com/news/private.jpg"},
                    ]
                },
            )
            result = candidate_filter.filter_candidates(input_path=candidates, manifest_path=manifest)

            self.assertEqual(result["stats"]["duplicate_route"], 1)
            self.assertEqual(result["stats"]["invalid"], 2)
            self.assertEqual(result["stats"]["remaining"], 2)
            routes = {item["route"] for item in result["requests"]}
            self.assertIn("/news/picture.jpg", routes)
            self.assertIn("/_origins/www.wow-europe.com/news/picture.jpg", routes)
            self.assertTrue(all("escape" not in item["url"] and "private" not in item["url"] for item in result["requests"]))

    def test_hashes_and_invalid_candidates_are_recorded_without_entering_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifest = self._write_json(
                base / "manifest.json",
                {"files": [{"route": "/images/x.gif", "kind": "image", "mime": "image/gif", "source_sha256": "source"}]},
            )
            candidates = self._write_json(
                base / "candidates.json",
                {"items": [{"logical_url": "http://www.worldofwarcraft.com/images/x.gif"}, {"logical_url": "http://"}]},
            )
            output = base / "out.json"
            result = candidate_filter.filter_candidates(
                input_path=candidates,
                manifest_path=manifest,
                output_path=output,
            )

            self.assertEqual(result["stats"]["remaining"], 0)
            self.assertEqual(result["excluded"]["existing_route"][0]["known_sha256"], "source")
            self.assertEqual(len(result["excluded"]["invalid"]), 1)
            self.assertEqual(result["input"]["sha256"], hashlib.sha256(candidates.read_bytes()).hexdigest())
            self.assertEqual(result["manifest"]["sha256"], hashlib.sha256(manifest.read_bytes()).hexdigest())
            self.assertEqual(result["requests"], [])


if __name__ == "__main__":
    unittest.main()
