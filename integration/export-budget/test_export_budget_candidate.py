from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from export_github_pages_candidate import load_candidate, source_sha256  # noqa: E402


class ExportBudgetCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pages = load_candidate()

    @staticmethod
    def _fixture(base: Path) -> tuple[Path, Path]:
        site = base / "offline" / "site"
        site.mkdir(parents=True)
        data = (
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>Home</title></head>"
            "<body><a href=\"/index.xml\">Home</a></body></html>"
        ).encode("utf-8")
        source = site / "index.xml"
        source.write_bytes(data)
        manifest = {
            "schema_version": 1,
            "anchor_timestamp": "20080512210044",
            "route_aliases": {"/": "/index.xml"},
            "origin_index": {},
            "files": [
                {
                    "route": "/index.xml",
                    "output_path": "offline/site/index.xml",
                    "derived_sha256": hashlib.sha256(data).hexdigest(),
                    "derived_length": len(data),
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "source_base_url": "http://www.worldofwarcraft.com/index.xml",
                }
            ],
        }
        manifest_path = base / "offline" / "build-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return site, manifest_path

    def test_none_skips_workspace_walk_but_completes_and_reports_null(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            site, manifest = self._fixture(base)
            with mock.patch.object(self.pages, "workspace_size", side_effect=AssertionError("workspace walk")):
                with mock.patch.object(self.pages.shutil, "disk_usage", return_value=SimpleNamespace(free=10**15)) as disk:
                    result = self.pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "pages",
                        workspace_root=base,
                        max_bytes=None,
                        min_free_bytes=0,
                    )
            self.assertTrue((base / "pages").is_dir())
            self.assertIsNone(result["workspace_bytes"])
            self.assertEqual(disk.call_count, 2)

    def test_none_still_enforces_disk_floor_without_workspace_walk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            site, manifest = self._fixture(base)
            with mock.patch.object(self.pages, "workspace_size", side_effect=AssertionError("workspace walk")):
                with mock.patch.object(
                    self.pages.shutil,
                    "disk_usage",
                    return_value=SimpleNamespace(free=self.pages.DEFAULT_MIN_FREE_BYTES - 1),
                ):
                    with self.assertRaisesRegex(self.pages.PagesExportError, "disk reserve"):
                        self.pages.export_pages(
                            source_site=site,
                            manifest_path=manifest,
                            output=base / "low-space",
                            workspace_root=base,
                            max_bytes=None,
                        )

    def test_finite_budget_still_walks_and_rejects_before_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            site, manifest = self._fixture(base)
            with mock.patch.object(self.pages, "workspace_size", return_value=0) as size:
                with self.assertRaisesRegex(self.pages.PagesExportError, "workspace budget exceeded"):
                    self.pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "limited",
                        workspace_root=base,
                        max_bytes=1,
                        min_free_bytes=0,
                    )
            self.assertEqual(size.call_count, 1)


if __name__ == "__main__":
    unittest.main()
