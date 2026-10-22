from __future__ import annotations

import json
import hashlib
import zlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import portable_check as checker  # noqa: E402


class PortableCheckTests(unittest.TestCase):
    def test_extract_consumes_verified_member_list_and_rejects_drift(self) -> None:
        payload=b"offline page bytes"
        name="site/index.html"
        records=[{"path":name,"sha256":hashlib.sha256(payload).hexdigest(),"bytes":len(payload),"crc32":f"{zlib.crc32(payload)&0xffffffff:08x}"}]
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);archive=root/"tiny.zip"
            info=zipfile.ZipInfo(name);info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as zf:zf.writestr(info,payload)
            with patch.object(checker,"_require_disk_floor",return_value=20_000_000_000):
                self.assertEqual(checker._extract_verified(archive,root/"accepted",{name},records),len(payload))
                self.assertEqual((root/"accepted"/name).read_bytes(),payload)
                changed=[{**records[0],"sha256":"0"*64}]
                with self.assertRaisesRegex(checker.PortableCheckError,"changed between verification"):
                    checker._extract_verified(archive,root/"rejected",{name},changed)

    def test_canonical_paths_and_zip_whitelist(self) -> None:
        self.assertEqual(checker._safe_relative("site/index.html", "fixture"), "site/index.html")
        for unsafe in ("../index.html", "/absolute", "C:/drive", "site\\index.html", "site//index.html"):
            with self.subTest(unsafe=unsafe), self.assertRaises(checker.PortableCheckError):
                checker._safe_relative(unsafe, "fixture")

        info = zipfile.ZipInfo("site/index.html")
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        observed = checker._validate_zip_infos([info], {"site/index.html"})
        self.assertEqual(set(observed), {"site/index.html"})

    def test_zip_rejects_duplicate_symlink_encryption_and_raw_evidence(self) -> None:
        def regular(name: str) -> zipfile.ZipInfo:
            item = zipfile.ZipInfo(name)
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            return item

        with self.assertRaisesRegex(checker.PortableCheckError, "duplicate"):
            checker._validate_zip_infos([regular("site/a"), regular("site/a")], {"site/a"})

        link = regular("site/link")
        link.external_attr = 0o120777 << 16
        with self.assertRaisesRegex(checker.PortableCheckError, "regular file"):
            checker._validate_zip_infos([link], {"site/link"})

        encrypted = regular("site/a")
        encrypted.flag_bits |= 0x1
        with self.assertRaisesRegex(checker.PortableCheckError, "encrypted"):
            checker._validate_zip_infos([encrypted], {"site/a"})

        with self.assertRaisesRegex(checker.PortableCheckError, "raw or runtime evidence"):
            checker._validate_zip_infos([regular("site/attempt.body")], {"site/attempt.body"})

    def test_config_accepts_v55_and_rejects_pre_v54(self) -> None:
        config = {
            "schema": checker.CONFIG_SCHEMA,
            "version": "v55",
            "accepted_site": "site",
            "archive": "a.zip",
            "package_report": "report.json",
            "export": {"path": "export.json"},
            "root_browser_acceptance": {"path": "browser.json"},
            "output_receipt": "receipt.json",
            "smoke_paths": [{
                "url_path": "/prefix/index.html",
                "site_relative": "index.html",
                "expected_mime": "text/html; charset=utf-8",
                "methods": ["GET", "HEAD"],
            }],
        }
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(checker._load_config(config_path)["version"], "v55")
            config["version"] = "v53"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(checker.PortableCheckError, "v54 or later"):
                checker._load_config(config_path)

    def test_local_preview_get_head_prefix_and_child_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            accepted_site = root / "accepted"
            package_root = root / "package"
            packaged_site = package_root / "site"
            (accepted_site).mkdir()
            (packaged_site).mkdir(parents=True)
            payload = b"<!doctype html><title>fixture</title>\n"
            (accepted_site / "index.html").write_bytes(payload)
            (packaged_site / "index.html").write_bytes(payload)
            provenance = {"base_path": "/fixture-prefix/"}
            (accepted_site / "export-provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
            (packaged_site / "export-provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
            tool_target = package_root / "tools" / "serve_pages_preview.py"
            tool_target.parent.mkdir(parents=True)
            shutil.copy2(checker.REPOSITORY_ROOT / "tools" / "serve_pages_preview.py", tool_target)

            stopped: list[object] = []
            original_stop = checker._stop_server

            def capture_stop(process):
                result = original_stop(process)
                stopped.append(process)
                return result

            with patch.object(checker, "_stop_server", side_effect=capture_stop):
                results = checker._smoke_check(
                    package_root,
                    accepted_site,
                    "/fixture-prefix/",
                    [{
                        "url_path": "/fixture-prefix/index.html",
                        "site_relative": "index.html",
                        "expected_mime": "text/html; charset=utf-8",
                        "methods": ["GET", "HEAD"],
                    }],
                )
            self.assertEqual(len(stopped), 1)
            self.assertIsNotNone(stopped[0].poll())
            self.assertEqual(results[0]["location"], "/fixture-prefix/")
            self.assertEqual([item["method"] for item in results[1:]], ["GET", "HEAD"])
            self.assertTrue(results[1]["body_matches_accepted_site"])
            self.assertFalse(results[2]["body_matches_accepted_site"])
            self.assertEqual(results[1]["sha256"], checker._sha256_bytes(payload))

    def test_smoke_path_must_match_file_under_project_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "index.html").write_bytes(b"x")
            with self.assertRaisesRegex(checker.PortableCheckError, "outside accepted project prefix"):
                checker._check_smoke_paths(
                    [{
                        "url_path": "https://example.invalid/other.html",
                        "site_relative": "index.html",
                        "expected_mime": "text/html",
                        "methods": ["GET", "HEAD"],
                    }],
                    "/fixture-prefix/",
                    site,
                )

    def test_acceptance_receipts_bind_site_provenance_and_listed_objects(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root = Path(temporary)
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_bytes(b"accepted page")
            provenance = {"base_path": "/checked/", "anchor_timestamp": "20080512000000"}
            (site / "export-provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
            sources, _, provenance_sha, _ = checker._expected_source_files(site)
            index = site / "index.html"
            index_sha, index_bytes = checker._hash_file(index)
            site_rel = site.relative_to(checker.REPOSITORY_ROOT).as_posix()
            export_path = root / "export-acceptance.json"
            browser_path = root / "browser-acceptance.json"
            evidence_path = root / "browser-evidence.txt"
            evidence_path.write_text("local browser evidence", encoding="utf-8")
            evidence_sha = checker._hash_file(evidence_path)[0]
            export_path.write_text(json.dumps({
                "accepted": True,
                "local_site": site_rel,
                "actual_files": 2,
                "export_provenance_sha256": provenance_sha,
                "objects": [{"path": "index.html", "sha256": index_sha, "bytes": index_bytes}],
            }), encoding="utf-8")
            browser_path.write_text(json.dumps({
                "schema": "wow-root-final-browser-acceptance/v1",
                "accepted": True,
                "local_site": site_rel,
                "export_provenance_sha256": provenance_sha,
                "pages": [],
                "external_requests": [],
                "page_errors": [],
                "asset_fulfillments": 0,
                "evidence": [{"path": evidence_path.relative_to(checker.REPOSITORY_ROOT).as_posix(), "sha256": evidence_sha}],
            }), encoding="utf-8")
            config = {
                "accepted_site": site_rel,
                "export": {"path": export_path.relative_to(checker.REPOSITORY_ROOT).as_posix()},
                "root_browser_acceptance": {"path": browser_path.relative_to(checker.REPOSITORY_ROOT).as_posix()},
            }
            self.assertEqual(checker._read_export_acceptance(config, site, sources, provenance_sha), checker._hash_file(export_path)[0])
            self.assertEqual(checker._read_root_acceptance(config, site, provenance_sha)[0], checker._hash_file(browser_path)[0])

            export_record = json.loads(export_path.read_text(encoding="utf-8"))
            export_record["objects"][0]["sha256"] = "0" * 64
            export_path.write_text(json.dumps(export_record), encoding="utf-8")
            with self.assertRaisesRegex(checker.PortableCheckError, "object differs"):
                checker._read_export_acceptance(config, site, sources, provenance_sha)


if __name__ == "__main__":
    unittest.main()
