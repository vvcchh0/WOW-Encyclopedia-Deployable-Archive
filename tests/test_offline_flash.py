from __future__ import annotations

import hashlib
import stat
import sys
import tempfile
import unittest
import zipfile
from contextlib import nullcontext
from pathlib import Path
from unittest import mock
import zlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import offline_flash  # noqa: E402


class OfflineFlashTests(unittest.TestCase):
    def test_exact_routes_inject_once_and_unknown_pages_do_not(self) -> None:
        base = "/WOW-Encyclopedia-Deployable-Archive/"
        for route, kind in (
            (offline_flash.SOCKET_ROUTE, "socket"),
            (offline_flash.DANCE_ROUTE, "dance"),
            (offline_flash.TUSKARR_ROUTE, "tuskarr"),
        ):
            source = "<html><head></head><body><object></object></body></html>"
            rewritten, stats = offline_flash.rewrite_page(source, route=route.lstrip("/"), base_path=base)
            self.assertEqual(stats["kind"], kind)
            self.assertEqual(stats["helper_injected"], 1)
            self.assertIn(f'data-offline-flash="{kind}"', rewritten)
            self.assertIn(base + "__offline/flash-exhibits.js", rewritten)
            again, second_stats = offline_flash.rewrite_page(rewritten, route=route, base_path=base)
            self.assertEqual(again, rewritten)
            self.assertTrue(second_stats["already_present"])

        source = "<html><head></head><body><object data=\"business.swf\"></object></body></html>"
        unchanged, stats = offline_flash.rewrite_page(source, route="/info/other.html", base_path=base)
        self.assertEqual(unchanged, source)
        self.assertFalse(stats["enabled"])
        self.assertNotIn("flash-exhibits.js", unchanged)

    def test_query_and_bad_base_paths_cannot_bypass_allowlist(self) -> None:
        with self.assertRaises(offline_flash.OfflineFlashError):
            offline_flash.rewrite_page("<head></head>", route="/info/races/dancing.html?route=/wrath", base_path="/site/")
        with self.assertRaises(offline_flash.OfflineFlashError):
            offline_flash.rewrite_page("<head></head>", route=offline_flash.DANCE_ROUTE, base_path="https://example.invalid/")

    def test_fake_helper_marker_in_comment_or_script_does_not_suppress_injection(self) -> None:
        source = (
            '<html><head><!-- <script data-offline-flash="dance" '
            'src="/site/__offline/flash-exhibits.js"></script> -->'
            '<script>var fake = \'<script data-offline-flash="dance" '
            'src="/site/__offline/flash-exhibits.js">\'; var close = "</head>";</script>'
            '</head><body></body></html>'
        )
        rewritten, stats = offline_flash.rewrite_page(source, route=offline_flash.DANCE_ROUTE, base_path="/site/")
        self.assertEqual(stats["helper_injected"], 1)
        self.assertEqual(rewritten.count('data-offline-flash="dance"'), 3)
        self.assertIn('<script defer data-offline-flash="dance"', rewritten)

    def _write_zip(self, path: Path, members: dict[str, bytes]) -> str:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name, payload in members.items():
                bundle.writestr(name, payload)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _mini_contract(self, extra: dict[str, bytes] | None = None) -> tuple[dict[str, bytes], dict[str, tuple[int, int]]]:
        members = {name: ("fixture:" + name).encode("utf-8") for name in offline_flash.RUFFLE_MEMBER_EXPECTATIONS}
        if extra:
            members.update(extra)
        expected = {
            name: (len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
            for name, payload in members.items()
            if name in offline_flash.RUFFLE_MEMBER_EXPECTATIONS
        }
        return members, expected

    def test_stage_runtime_returns_provenance_files_and_rejects_existing_output(self) -> None:
        members, expected = self._mini_contract()
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "runtime.zip"
            archive_sha = self._write_zip(archive, members)
            with mock.patch.object(offline_flash, "RUFFLE_ZIP_SHA256", archive_sha), mock.patch.object(
                offline_flash, "RUFFLE_MEMBER_EXPECTATIONS", expected
            ):
                result = offline_flash.stage_runtime(
                    Path(tmp) / "site",
                    archive_path=archive,
                    base_path="/WOW-Encyclopedia-Deployable-Archive/",
                    min_free_bytes=0,
                )
                self.assertEqual(result["runtime_version"], "0.7.1")
                self.assertEqual(result["archive_sha256"], archive_sha)
                self.assertEqual(result["runtime_file_count"], 9)
                self.assertEqual(len(result["files"]), 10)
                self.assertEqual(result["total_bytes"], sum(item["length"] for item in result["files"]))
                for item in result["files"]:
                    self.assertTrue((Path(tmp) / "site" / item["output_path"]).is_file())
                    self.assertIn(item["kind"], {"flash_runtime", "flash_helper", "flash_license"})
                with self.assertRaisesRegex(offline_flash.OfflineFlashError, "existing runtime file"):
                    offline_flash.stage_runtime(
                        Path(tmp) / "site",
                        archive_path=archive,
                        base_path="/WOW-Encyclopedia-Deployable-Archive/",
                        min_free_bytes=0,
                    )

    def test_stage_runtime_rejects_wrong_sha_and_unsafe_members(self) -> None:
        members, expected = self._mini_contract()
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "tiny.zip"
            archive_sha = self._write_zip(archive, members)
            with mock.patch.object(offline_flash, "RUFFLE_ZIP_SHA256", "0" * 64):
                with self.assertRaisesRegex(offline_flash.OfflineFlashError, "archive SHA mismatch"):
                    offline_flash.stage_runtime(Path(tmp) / "out", archive_path=archive, base_path="/site/", min_free_bytes=0)

            unsafe_members, unsafe_expected = self._mini_contract({"../escape.js": b"escape"})
            unsafe = Path(tmp) / "unsafe.zip"
            unsafe_sha = self._write_zip(unsafe, unsafe_members)
            with mock.patch.object(offline_flash, "RUFFLE_ZIP_SHA256", unsafe_sha), mock.patch.object(
                offline_flash, "RUFFLE_MEMBER_EXPECTATIONS", unsafe_expected
            ):
                with self.assertRaisesRegex(offline_flash.OfflineFlashError, "unsafe Ruffle ZIP member path"):
                    offline_flash.stage_runtime(Path(tmp) / "out", archive_path=unsafe, base_path="/site/", min_free_bytes=0)

    def test_stage_runtime_rejects_encrypted_and_symlink_members(self) -> None:
        members, expected = self._mini_contract()
        for label, configure in (
            ("encrypted", lambda info: setattr(info, "flag_bits", 0x1)),
            ("symlink", lambda info: setattr(info, "external_attr", (stat.S_IFLNK | 0o777) << 16)),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                archive = Path(tmp) / (label + ".zip")
                with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                    for name, payload in members.items():
                        bundle.writestr(name, payload)
                    if label != "encrypted":
                        info = zipfile.ZipInfo(label + ".bin")
                        configure(info)
                        bundle.writestr(info, b"fixture")
                archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
                with mock.patch.object(offline_flash, "RUFFLE_ZIP_SHA256", archive_sha), mock.patch.object(
                    offline_flash, "RUFFLE_MEMBER_EXPECTATIONS", expected
                ):
                    if label == "encrypted":
                        with zipfile.ZipFile(archive) as bundle:
                            infos = bundle.infolist()
                        fake_info = zipfile.ZipInfo("encrypted.bin")
                        fake_info.flag_bits = 0x1
                        info_patch = mock.patch.object(zipfile.ZipFile, "infolist", return_value=infos + [fake_info])
                    else:
                        info_patch = nullcontext()
                    with info_patch:
                        with self.assertRaisesRegex(offline_flash.OfflineFlashError, "not a plain readable file|symlink"):
                            offline_flash.stage_runtime(Path(tmp) / "out", archive_path=archive, base_path="/site/", min_free_bytes=0)


if __name__ == "__main__":
    unittest.main()
