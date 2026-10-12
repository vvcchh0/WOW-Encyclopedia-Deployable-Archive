from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGING = ROOT / "packaging"
if str(PACKAGING) not in sys.path:
    sys.path.insert(0, str(PACKAGING))

import package_offline_mirror as package  # noqa: E402
import smoke_offline_package as smoke  # noqa: E402


class OfflinePackagingTests(unittest.TestCase):
    def test_recovery_selection_includes_every_required_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            expected = set(package.RECOVERY_REQUIRED_FILES)
            for name in package.RECOVERY_REQUIRED_DIRECTORIES:
                probe = base / name / "package-evidence.txt"
                probe.parent.mkdir(parents=True, exist_ok=True)
                probe.write_text("preserved evidence", encoding="utf-8")
                expected.add(probe.relative_to(base).as_posix())
            for name in package.RECOVERY_REQUIRED_FILES:
                file = base / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("{}" if file.suffix == ".json" else "source", encoding="utf-8")
            script = base / "tools/recover_fixture.py"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text("# fixture", encoding="utf-8")
            with patch.object(package, "ROOT", base):
                selected, _, _ = package.select_files(recovery=True)
            self.assertTrue(expected.issubset(selected), sorted(expected - selected.keys()))

    def _write_recovery_fixture(
        self,
        base: Path,
        *,
        targeted: bool = False,
        missing_page: bool = False,
        fake_counts: bool = False,
        errors: bool = False,
        incomplete: bool = False,
    ) -> Path:
        """Create a small browser-check-shaped fixture without reading offline/site."""
        manifest = {
            "files": [
                {
                    "route": "/core.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "core_page",
                },
                {
                    "route": "/sidebar.xml",
                    "mime": "application/xml; charset=UTF-8",
                    "kind": "xml",
                    "role": "site_recovery_sidebar_page",
                },
                {
                    "route": "/placeholder.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "generated_placeholder",
                    "role": "offline_support",
                },
            ]
        }
        manifest_path = base / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        manifest_sha = package.sha(manifest_path.read_bytes())

        pages = [
            {"route": "/core.html", "accepted": True},
            {"route": "/sidebar.xml", "accepted": True},
        ]
        if missing_page:
            pages.pop()
        placeholders = [{"scope": "official"}] if incomplete else []
        expected_pages = 999 if fake_counts else 2
        browser = {
            "accepted": True,
            "audit_scope": "targeted" if targeted else "all-manifest-documents",
            "requested_routes": ["/core.html"] if targeted else None,
            "targeted_passed": True,
            "build_unchanged": True,
            "server_unchanged": True,
            "build_manifest_sha256": manifest_sha,
            "server_manifest_sha256": manifest_sha,
            "expected_pages": expected_pages,
            "all_manifest_documents": 2,
            "pages": pages,
            "sidebar": [{"route": "/public", "collected": not incomplete}],
            "placeholders": placeholders,
            "in_scope_placeholder_references": 1 if incomplete else 0,
            "excluded_external_placeholder_references": 0,
            "page_errors": [{"route": "/core.html", "error": "fixture"}] if errors else [],
            "resource_failures": [],
            "nonlocal_requests": [],
            "restoration_complete": not incomplete,
        }
        browser_path = base / "research/offline-2008/full-recovery/browser-validation.json"
        browser_path.parent.mkdir(parents=True, exist_ok=True)
        browser_path.write_text(json.dumps(browser, sort_keys=True), encoding="utf-8")
        return manifest_path

    def test_smoke_selects_real_guide_media_and_news_routes(self) -> None:
        # Keep the behavioral fixture independent of the current recovery
        # queue: a placeholder whose text says "Guide" must not win over a
        # later real page.  The production selector is metadata-driven, so
        # this test must not pin an old route that may legitimately change.
        fixture = {
            "route_aliases": {"/": "/index.xml"},
            "files": [
                {
                    "route": "/index.xml",
                    "logical_url": "http://www.worldofwarcraft.com/index.xml",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "core_page",
                    "source_sha256": "home-source",
                },
                {
                    "route": "/info/encyclopedia/392.xml",
                    "logical_url": "http://www.worldofwarcraft.com/info/encyclopedia/392.xml",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "core_page",
                    "source_sha256": "elune-source",
                    "title": "Elune",
                },
                {
                    "route": "/guide-placeholder.html",
                    "logical_url": "http://www.worldofwarcraft.com/guide-placeholder.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "generated_placeholder",
                    "role": "offline_support",
                    "title": "Game Guide placeholder",
                },
                {
                    "route": "/info/story/index.html",
                    "logical_url": "http://www.worldofwarcraft.com/info/story/index.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "site_recovery_page",
                    "source_sha256": "guide-source",
                    "title": "Game Guide",
                },
                {
                    "route": "/downloads/index.html",
                    "logical_url": "http://www.worldofwarcraft.com/downloads/index.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "site_recovery_page",
                    "source_sha256": "media-source",
                    "title": "Media Downloads",
                },
                {
                    "route": "/info/archivednews.html",
                    "logical_url": "http://www.worldofwarcraft.com/info/archivednews.html",
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "site_recovery_page",
                    "source_sha256": "news-source",
                    "title": "Archived News",
                },
            ],
        }
        fixture_selected = smoke.select_smoke_routes(fixture)
        self.assertEqual(fixture_selected["homepage"]["route"], "/index.xml")
        self.assertEqual(fixture_selected["elune"]["route"], "/info/encyclopedia/392.xml")
        self.assertEqual(fixture_selected["guide"]["route"], "/info/story/index.html")
        self.assertEqual(fixture_selected["media"]["route"], "/downloads/index.html")
        self.assertEqual(fixture_selected["news"]["route"], "/info/archivednews.html")
        for item in fixture_selected.values():
            self.assertNotIn(item.get("kind"), smoke.PLACEHOLDER_KINDS)
            self.assertTrue(item.get("source_sha256"))
            self.assertEqual(item["mime"].casefold().split(";", 1)[0], "text/html")

        manifest = json.loads((ROOT / "offline/build-manifest.json").read_text(encoding="utf-8"))
        selected = smoke.select_smoke_routes(manifest)
        manifest_routes = {str(item.get("route")) for item in manifest.get("files", [])}
        for label, item in selected.items():
            self.assertIn(item["route"], manifest_routes, label)
            self.assertNotIn(item.get("kind"), smoke.PLACEHOLDER_KINDS, label)
            self.assertIn(
                str(item.get("mime", "")).casefold().split(";", 1)[0],
                {"text/html", "application/xhtml+xml"},
                label,
            )
            self.assertTrue(item.get("source_sha256"), label)

    def test_smoke_external_paths_and_missing_archive_report(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            archive = base / "missing-package.zip"
            report = base / "external-report.json"
            extraction = base / "fresh-extraction"
            result = smoke.run_smoke(archive=archive, report=report, extraction=extraction, port=18877)
            self.assertEqual(result["status"], "missing_archive")
            self.assertEqual(result["archive"], smoke.display_path(archive))
            self.assertTrue(report.is_file())
            self.assertFalse(extraction.exists())

    def test_extract_rejects_existing_destination_and_bad_member(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            archive = base / "small.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("../escape.txt", b"bad")
            with self.assertRaises(smoke.SmokeError):
                smoke.extract_archive(archive, base / "fresh")
            existing = base / "existing"
            existing.mkdir()
            with self.assertRaises(smoke.SmokeError):
                smoke.extract_archive(archive, existing)

    def test_package_refuses_overwriting_existing_v1_archive(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            report = Path(directory) / "report.json"
            with self.assertRaises(FileExistsError):
                package.package(archive=package.DEST, report=report, recovery=False)
            self.assertFalse(report.exists())

    def test_recovery_validation_requires_full_browser_record(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            manifest_path = base / "manifest.json"
            manifest_path.write_bytes(b"{}")
            browser_path = base / "research/offline-2008/full-recovery/browser-validation.json"
            with patch.object(package, "ROOT", base):
                with self.assertRaises(FileNotFoundError):
                    package.validate_browser(manifest_path, recovery=True)
                browser_path.parent.mkdir(parents=True)
                browser = {
                    "accepted": True,
                    "audit_scope": "all-manifest-documents",
                    "requested_routes": None,
                    "targeted_passed": True,
                    "build_unchanged": True,
                    "server_unchanged": True,
                    "restoration_complete": False,
                    "build_manifest_sha256": "wrong",
                }
                browser_path.write_text(json.dumps(browser), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "another build"):
                    package.validate_browser(manifest_path, recovery=True)

            # The valid incomplete case is checked through the same public
            # validator, with no source/site tree involved.
            with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as valid_directory:
                valid_base = Path(valid_directory)
                valid_manifest = self._write_recovery_fixture(valid_base, incomplete=True)
                with patch.object(package, "ROOT", valid_base):
                    _, _, gaps = package.validate_browser(valid_manifest, recovery=True)
                self.assertFalse(gaps["restoration_complete"])

    def test_recovery_validation_rejects_targeted_pseudoaccepted_record(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            manifest_path = self._write_recovery_fixture(base, targeted=True)
            with patch.object(package, "ROOT", base):
                with self.assertRaisesRegex(RuntimeError, "all-document"):
                    package.validate_browser(manifest_path, recovery=True)

    def test_recovery_validation_rejects_missing_page_and_fake_counts(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            manifest_path = self._write_recovery_fixture(base, missing_page=True)
            with patch.object(package, "ROOT", base):
                with self.assertRaisesRegex(RuntimeError, "do not match manifest"):
                    package.validate_browser(manifest_path, recovery=True)

            manifest_path = self._write_recovery_fixture(base, fake_counts=True)
            with patch.object(package, "ROOT", base):
                with self.assertRaisesRegex(RuntimeError, "page counts"):
                    package.validate_browser(manifest_path, recovery=True)

    def test_recovery_validation_rejects_nonempty_error_arrays(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            manifest_path = self._write_recovery_fixture(base, errors=True)
            with patch.object(package, "ROOT", base):
                with self.assertRaisesRegex(RuntimeError, "page_errors"):
                    package.validate_browser(manifest_path, recovery=True)

            for field in ("resource_failures", "nonlocal_requests"):
                manifest_path = self._write_recovery_fixture(base)
                browser_path = base / "research/offline-2008/full-recovery/browser-validation.json"
                browser = json.loads(browser_path.read_text(encoding="utf-8"))
                browser[field] = [{"fixture": True}]
                browser_path.write_text(json.dumps(browser, sort_keys=True), encoding="utf-8")
                with patch.object(package, "ROOT", base):
                    with self.assertRaisesRegex(RuntimeError, field):
                        package.validate_browser(manifest_path, recovery=True)

    def test_recovery_validation_accepts_explicit_incomplete_and_complete_records(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".scratch") as directory:
            base = Path(directory)
            manifest_path = self._write_recovery_fixture(base, incomplete=True)
            with patch.object(package, "ROOT", base):
                browser, _, gaps = package.validate_browser(manifest_path, recovery=True)
            self.assertTrue(browser["accepted"])
            self.assertFalse(gaps["restoration_complete"])

            manifest_path = self._write_recovery_fixture(base, incomplete=False)
            with patch.object(package, "ROOT", base):
                browser, _, gaps = package.validate_browser(manifest_path, recovery=True)
            self.assertTrue(browser["accepted"])
            self.assertTrue(gaps["restoration_complete"])


if __name__ == "__main__":
    unittest.main()
