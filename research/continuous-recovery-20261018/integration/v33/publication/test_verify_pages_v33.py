from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load_module("v33_pages_verifier", "verify_pages_v33.py")


class V33PagesVerifierTests(unittest.TestCase):
    def test_curl_policy_is_tls_only_and_never_follows_redirects(self) -> None:
        direct = verifier.curl_command("images/new.png", "direct", 8, Path("body"), 1024)
        proxy = verifier.curl_command("images/new.png", "proxy", 8, Path("body"), 1024)
        for command in (direct, proxy):
            self.assertIn("--proto", command)
            self.assertEqual(command[command.index("--proto") + 1], "=https")
            self.assertIn("--tlsv1.2", command)
            self.assertNotIn("--location", command)
            self.assertNotIn("-L", command)
            self.assertNotIn("--max-redirs", command)
        self.assertEqual(direct[direct.index("--noproxy") + 1], "*")
        self.assertEqual(proxy[proxy.index("--noproxy") + 1], "")
        self.assertEqual(proxy[proxy.index("--proxy") + 1], "http://127.0.0.1:7890")

    def test_load_objects_accepts_safe_unique_paths_and_rejects_duplicates(self) -> None:
        original_gate = verifier.LOCAL_GATE
        original_site = verifier.SITE
        try:
            with tempfile.TemporaryDirectory(dir=verifier.PUB, prefix="v33-verifier-fixture-") as directory:
                fixture_root = Path(directory)
                site = fixture_root / "site"
                site.mkdir()
                (site / "images").mkdir()
                data = b"fixture-png"
                (site / "images/a.png").write_bytes(data)
                gate = fixture_root / "gate.json"
                object_path = "images/a.png"
                object_sha = verifier.sha256_bytes(data)
                binding_path = (site / object_path).relative_to(verifier.ROOT).as_posix()
                binding = {"path": binding_path, "sha256": object_sha, "bytes": len(data)}
                gate.write_text(json.dumps({"accepted": True, "published": False, "local_site": site.relative_to(verifier.ROOT).as_posix(), "bindings": [binding], "objects": [{"path": object_path, "sha256": object_sha, "bytes": len(data), "mime": ["image/png"]}]}), encoding="utf-8")
                verifier.LOCAL_GATE = gate
                verifier.SITE = site
                objects = verifier.load_objects()
                self.assertEqual(objects[0]["path"], "images/a.png")
                self.assertEqual(objects[0]["mime"], {"image/png"})
                gate.write_text(json.dumps({"accepted": True, "published": False, "local_site": site.relative_to(verifier.ROOT).as_posix(), "bindings": [binding], "objects": [{"path": "../outside", "sha256": "a" * 64, "bytes": 1}]}), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "unsafe"):
                    verifier.load_objects()
                gate.write_text(json.dumps({"accepted": True, "published": False, "local_site": site.relative_to(verifier.ROOT).as_posix(), "bindings": [binding], "objects": [{"path": "images/a.png", "sha256": object_sha, "bytes": len(data)}, {"path": "images/a.png", "sha256": "b" * 64, "bytes": len(data)}]}), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "unsafe or duplicate"):
                    verifier.load_objects()
        finally:
            verifier.LOCAL_GATE = original_gate
            verifier.SITE = original_site

    def test_expected_commit_requires_exact_hex_report(self) -> None:
        original = verifier.PUBLISH_REPORT
        try:
            with tempfile.TemporaryDirectory(dir=verifier.PUB, prefix="v33-report-fixture-") as directory:
                report = Path(directory) / "report.json"
                verifier.PUBLISH_REPORT = report
                report.write_text(json.dumps({"new_commit_sha": "A" * 40}), encoding="utf-8")
                self.assertEqual(verifier.expected_commit(), "a" * 40)
                report.write_text(json.dumps({"new_commit_sha": "g" * 40}), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "exact 40-character"):
                    verifier.expected_commit()
        finally:
            verifier.PUBLISH_REPORT = original


if __name__ == "__main__":
    unittest.main()
