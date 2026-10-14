from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import package_pages_archive as package  # noqa: E402
import serve_pages_preview as preview  # noqa: E402


class PagesArchiveTests(unittest.TestCase):
    def _write_site(self, base: Path) -> Path:
        site = base / "site"
        (site / "guide").mkdir(parents=True)
        (site / "assets").mkdir()
        (site / "export-provenance.json").write_text(
            json.dumps(
                {
                    "schema": "github-pages-export-provenance/v1",
                    "anchor_timestamp": "20080512210044",
                    "base_path": "/WOW-Encyclopedia-Deployable-Archive/",
                    "files": [],
                    "stats": {"output_files": 4},
                }
            ),
            encoding="utf-8",
        )
        (site / "index.html").write_text("<h1>fixture home</h1>", encoding="utf-8")
        (site / "guide" / "index.html").write_text("<h1>fixture guide</h1>", encoding="utf-8")
        (site / "assets" / "pixel.gif").write_bytes(b"GIF89a\x01\x00\x01\x00fixture")
        return site

    def _build(self, base: Path) -> tuple[Path, dict]:
        site = self._write_site(base)
        archive = base / "package.zip"
        report = base / "package-report.json"
        report_data = package.build_archive(
            site=site,
            archive=archive,
            report=report,
            processed_date="2026-10-14",
            project_root=ROOT,
        )
        return archive, report_data

    def test_package_has_exact_portable_members_and_stream_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive, report = self._build(Path(directory))
            self.assertTrue(report["network_performed"] is False)
            self.assertEqual(len(report["sidecar_sha256"]), 64)
            self.assertEqual(report["verification"]["member_count"], 10)
            self.assertTrue((archive.with_name(archive.name + ".sha256")).is_file())
            with zipfile.ZipFile(archive) as handle:
                names = set(handle.namelist())
                self.assertEqual(
                    names,
                    {
                        "site/export-provenance.json",
                        "site/index.html",
                        "site/guide/index.html",
                        "site/assets/pixel.gif",
                        "tools/serve_pages_preview.py",
                        "NOTICE.md",
                        "README.md",
                        "START_BROWSE.cmd",
                        "archive-metadata.json",
                        "FILE_SHA256SUMS.txt",
                    },
                )
                readme = handle.read("README.md").decode("utf-8")
                self.assertIn("2026-10-14", readme)
                self.assertIn("--open-browser", readme)
                self.assertNotIn(str(Path(directory)), readme)
                metadata = json.loads(handle.read("archive-metadata.json"))
                self.assertEqual(metadata["project_prefix"], "/WOW-Encyclopedia-Deployable-Archive/")
                self.assertEqual(metadata["member_count"], len(names))
                checksums = handle.read("FILE_SHA256SUMS.txt").decode("utf-8")
                self.assertIn("site/assets/pixel.gif", checksums)
            self.assertEqual(report["verification"]["crc_sha_length_all_passed"], True)
            self.assertEqual(report["verification"]["whitelist_exact"], True)

    def test_windows_launcher_propagates_server_exit_code(self) -> None:
        with tempfile.TemporaryDirectory(prefix="archive launcher ") as directory:
            base = Path(directory)
            (base / "tools").mkdir()
            (base / "site").mkdir()
            (base / "tools" / "serve_pages_preview.py").write_text(
                "import sys\nsys.exit(7)\n", encoding="utf-8"
            )
            launcher = base / "START_BROWSE.cmd"
            launcher.write_bytes(package.make_launcher())
            environment = os.environ.copy()
            where_py = subprocess.run(
                ["where", "py"], capture_output=True, text=True, check=False
            )
            if where_py.returncode != 0:
                stub_dir = base / "bin"
                stub_dir.mkdir()
                (stub_dir / "py.cmd").write_text(
                    "@echo off\r\nexit /b 7\r\n", encoding="ascii", newline=""
                )
                environment["PATH"] = str(stub_dir) + os.pathsep + environment.get("PATH", "")
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "call", str(launcher)],
                cwd=base,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            self.assertEqual(result.returncode, 7, result.stdout + result.stderr)

    def test_extra_zip_member_is_rejected_by_whitelist_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive, _ = self._build(base)
            site = base / "site"
            source_members, provenance = package.collect_source_members(site, ROOT)
            members = package.build_member_set(source_members, provenance, "2026-10-14")
            tampered = base / "tampered.zip"
            shutil.copyfile(archive, tampered)
            with zipfile.ZipFile(tampered, "a") as handle:
                handle.writestr("extra-member.txt", b"unexpected")
            with self.assertRaisesRegex(package.ArchiveError, "whitelist"):
                package.verify_archive(tampered, members, provenance)

    def test_extracted_archive_serves_prefix_directory_alias_html_and_binary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive, _ = self._build(base)
            extraction = base / "unpacked"
            extraction.mkdir()
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(extraction)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(extraction / "tools" / "serve_pages_preview.py"),
                    "--site",
                    str(extraction / "site"),
                    "--port",
                    "0",
                ],
                cwd=extraction,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                self.assertIsNotNone(process.stdout)
                first_line = process.stdout.readline().strip()
                self.assertTrue(first_line.startswith("Archive preview: http://127.0.0.1:"), first_line)
                base_url = first_line.split("Archive preview: ", 1)[1]
                prefix = "/WOW-Encyclopedia-Deployable-Archive/"
                with urllib.request.urlopen(base_url, timeout=5) as response:
                    self.assertEqual(response.read(), b"<h1>fixture home</h1>")
                with urllib.request.urlopen(base_url.rstrip("/") + "/guide/", timeout=5) as response:
                    self.assertEqual(response.read(), b"<h1>fixture guide</h1>")
                with urllib.request.urlopen(base_url.rstrip("/") + "/assets/pixel.gif", timeout=5) as response:
                    self.assertEqual(response.read(), b"GIF89a\x01\x00\x01\x00fixture")
                self.assertIn(prefix, base_url)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()

    def test_open_browser_is_opt_in_and_uses_actual_bound_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            site = self._write_site(Path(directory))

            class FakeServer:
                server_port = 43210

                def __init__(self, address, handler):
                    self.address = address
                    self.handler = handler

                def serve_forever(self):
                    raise KeyboardInterrupt

                def server_close(self):
                    pass

            with patch.object(preview, "ThreadingHTTPServer", FakeServer), patch.object(
                preview.webbrowser, "open"
            ) as open_browser, patch.object(sys, "argv", ["serve_pages_preview.py", "--site", str(site), "--port", "0", "--open-browser"]):
                preview.main()
            open_browser.assert_called_once_with(
                "http://127.0.0.1:43210/WOW-Encyclopedia-Deployable-Archive/"
            )

            with patch.object(preview, "ThreadingHTTPServer", FakeServer), patch.object(
                preview.webbrowser, "open"
            ) as open_browser, patch.object(sys, "argv", ["serve_pages_preview.py", "--site", str(site), "--port", "0"]):
                preview.main()
            open_browser.assert_not_called()

    def test_existing_output_unsafe_member_and_disk_threshold_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            archive = base / "package.zip"
            report = base / "report.json"
            archive.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                package.build_archive(site=site, archive=archive, report=report, processed_date="2026-10-14", project_root=ROOT)
            archive.unlink()

            (site / ".git").mkdir()
            (site / ".git" / "config").write_text("metadata", encoding="utf-8")
            with self.assertRaises(package.ArchiveError):
                package.build_archive(site=site, archive=archive, report=report, processed_date="2026-10-14", project_root=ROOT)
            (site / ".git" / "config").unlink()
            (site / ".git").rmdir()

            with patch.object(
                package.shutil,
                "disk_usage",
                return_value=SimpleNamespace(free=package.MIN_FREE_BYTES, total=10**12, used=0),
            ):
                with self.assertRaises(package.ArchiveError):
                    package.build_archive(site=site, archive=archive, report=report, processed_date="2026-10-14", project_root=ROOT)
            self.assertFalse(archive.exists())

    def test_source_mutation_is_detected_after_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            members, _ = package.collect_source_members(site, ROOT)
            (site / "index.html").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(package.ArchiveError, "source changed"):
                package.verify_sources_unchanged(members)

    def test_competing_final_archive_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            archive = base / "package.zip"
            report = base / "report.json"
            original_check = package.verify_sources_unchanged

            def competitor_writes_before_publish(members):
                archive.write_bytes(b"competitor output")
                original_check(members)

            with patch.object(package, "verify_sources_unchanged", side_effect=competitor_writes_before_publish):
                with self.assertRaises(FileExistsError):
                    package.build_archive(
                        site=site,
                        archive=archive,
                        report=report,
                        processed_date="2026-10-14",
                        project_root=ROOT,
                    )
            self.assertEqual(archive.read_bytes(), b"competitor output")
            self.assertFalse(archive.with_name(archive.name + ".partial").exists())
            self.assertFalse(report.exists())

    def test_new_site_file_created_during_write_prevents_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            archive = base / "package.zip"
            report = base / "report.json"
            original_write = package._write_member
            created = False

            def write_then_add_site_file(zf, member, package_date):
                nonlocal created
                original_write(zf, member, package_date)
                if not created:
                    created = True
                    (site / "created-during-write.html").write_text("new", encoding="utf-8")

            with patch.object(package, "_write_member", side_effect=write_then_add_site_file):
                with self.assertRaisesRegex(package.ArchiveError, "site file set changed"):
                    package.build_archive(
                        site=site,
                        archive=archive,
                        report=report,
                        processed_date="2026-10-14",
                        project_root=ROOT,
                    )
            self.assertFalse(archive.exists())
            self.assertFalse(archive.with_name(archive.name + ".partial").exists())
            self.assertFalse(report.exists())

    def test_no_clobber_helper_preserves_competing_sidecar_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for label in ("sidecar", "report"):
                temporary = base / (label + ".partial")
                final = base / label
                temporary.write_bytes(b"ours")
                final.write_bytes(b"competitor")
                with self.assertRaises(FileExistsError):
                    package._publish_no_clobber(temporary, final)
                self.assertEqual(final.read_bytes(), b"competitor")
                self.assertEqual(temporary.read_bytes(), b"ours")
                temporary.unlink()

    def test_build_preserves_competing_sidecar_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            archive = base / "package.zip"
            report = base / "package-report.json"
            sidecar_partial = archive.with_name(archive.name + ".sha256.partial")
            original_open = package._open_exclusive
            competitor_created = False

            def open_then_compete(path: Path):
                nonlocal competitor_created
                if path == sidecar_partial and not competitor_created:
                    competitor_created = True
                    sidecar_partial.write_bytes(b"competitor temp")
                return original_open(path)

            with patch.object(package, "_open_exclusive", side_effect=open_then_compete):
                with self.assertRaises(FileExistsError):
                    package.build_archive(
                        site=site,
                        archive=archive,
                        report=report,
                        processed_date="2026-10-14",
                        project_root=ROOT,
                    )
            self.assertEqual(sidecar_partial.read_bytes(), b"competitor temp")
            self.assertTrue(archive.is_file())
            self.assertFalse(archive.with_name(archive.name + ".partial").exists())
            self.assertFalse(report.exists())

    def test_route_map_redirects_old_xml_and_rejects_unsafe_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            site = self._write_site(base)
            prefix = "/WOW-Encyclopedia-Deployable-Archive/"
            (site / "info" / "encyclopedia").mkdir(parents=True)
            (site / "info" / "encyclopedia" / "index.xml.html").write_text(
                "<h1>canonical XML exhibit</h1>", encoding="utf-8"
            )
            (site / "404.html").write_text(
                '<meta name="offline-pages-404" content="true"><p>archive missing</p>',
                encoding="utf-8",
            )
            (site / "__offline").mkdir()
            (site / "__offline" / "route-map.json").write_text(
                json.dumps(
                    {
                        "base_path": prefix,
                        "routes": {
                            "/info/encyclopedia/index.xml": prefix + "info/encyclopedia/index.xml.html",
                            "/external": "https://example.invalid/outside",
                            "/escape": prefix + "../index.html",
                            "/with-query": prefix + "info/encyclopedia/index.xml.html?remote=1",
                        },
                        "aliases": {"/legacy": prefix + "guide/index.html"},
                    }
                ),
                encoding="utf-8",
            )
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(TOOLS / "serve_pages_preview.py"),
                    "--site",
                    str(site),
                    "--port",
                    "0",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                self.assertIsNotNone(process.stdout)
                first_line = process.stdout.readline().strip()
                base_url = first_line.split("Archive preview: ", 1)[1]
                opener = urllib.request.build_opener(
                    type(
                        "NoRedirect",
                        (urllib.request.HTTPRedirectHandler,),
                        {"redirect_request": lambda self, req, fp, code, msg, headers, newurl: None},
                    )()
                )

                old_url = base_url.rstrip("/") + "/info/encyclopedia/index.xml?q=history"
                with self.assertRaises(HTTPError) as redirect_error:
                    opener.open(old_url, timeout=5)
                self.assertEqual(redirect_error.exception.code, 302)
                self.assertEqual(
                    redirect_error.exception.headers["Location"],
                    prefix + "info/encyclopedia/index.xml.html?q=history",
                )
                with urllib.request.urlopen(
                    "http://127.0.0.1:" + base_url.rsplit(":", 1)[1].split("/", 1)[0] + prefix + "info/encyclopedia/index.xml.html",
                    timeout=5,
                ) as response:
                    self.assertEqual(response.read(), b"<h1>canonical XML exhibit</h1>")

                with self.assertRaises(HTTPError) as head_error:
                    opener.open(urllib.request.Request(old_url, method="HEAD"), timeout=5)
                self.assertEqual(head_error.exception.code, 302)
                self.assertEqual(
                    head_error.exception.headers["Location"],
                    prefix + "info/encyclopedia/index.xml.html?q=history",
                )

                directory_url = base_url.rstrip("/") + "/guide?from=old"
                with self.assertRaises(HTTPError) as directory_error:
                    opener.open(directory_url, timeout=5)
                self.assertEqual(directory_error.exception.code, 302)
                self.assertEqual(directory_error.exception.headers["Location"], prefix + "guide/?from=old")

                with urllib.request.urlopen(base_url.rstrip("/") + "/guide/", timeout=5) as response:
                    self.assertEqual(response.read(), b"<h1>fixture guide</h1>")

                for unsafe in ("/external", "/escape", "/with-query"):
                    with self.assertRaises(HTTPError) as unsafe_error:
                        opener.open(base_url.rstrip("/") + unsafe, timeout=5)
                    self.assertEqual(unsafe_error.exception.code, 404)
                    self.assertIn(b"offline-pages-404", unsafe_error.exception.read())

                with self.assertRaises(HTTPError) as unknown_error:
                    urllib.request.urlopen(base_url.rstrip("/") + "/unknown-route", timeout=5)
                self.assertEqual(unknown_error.exception.code, 404)
                self.assertIn(b"offline-pages-404", unknown_error.exception.read())

                with self.assertRaises(HTTPError) as traversal_error:
                    urllib.request.urlopen(base_url.rstrip("/") + "/../secret", timeout=5)
                self.assertEqual(traversal_error.exception.code, 404)
                self.assertNotIn(b"offline-pages-404", traversal_error.exception.read())

                for encoded in ("%5csecret", "%00secret"):
                    with self.assertRaises(HTTPError) as encoded_error:
                        urllib.request.urlopen(base_url.rstrip("/") + "/" + encoded, timeout=5)
                    self.assertEqual(encoded_error.exception.code, 404)
                    self.assertNotIn(b"offline-pages-404", encoded_error.exception.read())
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()


if __name__ == "__main__":
    unittest.main()
