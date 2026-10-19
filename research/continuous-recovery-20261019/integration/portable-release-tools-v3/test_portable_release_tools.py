"""Offline path/schema tests for the parameterized release tools."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


COMMON = _load("portable_release_common")


class PortableReleaseToolTests(unittest.TestCase):
    def test_version_and_release_paths_are_parameterized(self):
        paths = COMMON.release_paths("v32")
        self.assertEqual(paths["site"], ROOT / ".scratch/pages-resources-20261018-v32")
        self.assertEqual(
            paths["archive"],
            ROOT / "artifacts/WOW_Encyclopedia_20080512_browser_20261018_v32.zip",
        )
        with self.assertRaises(ValueError):
            COMMON.release_paths("32")
        with self.assertRaises(ValueError):
            COMMON.release_paths("v32/../v31")

    def test_current_provenance_derives_three_groups_and_thirty_nine_images(self):
        pub = ROOT / "research/continuous-recovery-20261018/publication"
        site = ROOT / ".scratch/pages-resources-20261018-v32"
        provenance = json.loads((site / "export-provenance.json").read_bytes())
        local = json.loads((pub / "root-v32-local-acceptance.json").read_bytes())
        browser = json.loads((pub / "root-v32-browser-acceptance.json").read_bytes())
        pages = json.loads((pub / "root-v32-pages-online-acceptance.json").read_bytes())
        site = ROOT / ".scratch/pages-resources-20261018-v32"
        paths, counts = COMMON.smoke_paths(provenance, local, browser, pages, site)
        self.assertEqual(counts, {"groups": 3, "images": 39})
        self.assertGreater(len(paths), 150)
        self.assertIn("bcattunement/index.html", paths)
        self.assertIn("info/events/loveisintheair/gallery.html", paths)
        self.assertIn("pvp/worldpvp/index.xml.html", paths)
        self.assertNotIn("pvp/worldpvp/index.xml", paths)
        for relative in paths:
            self.assertTrue((site / COMMON.safe_site_path(relative)).is_file(), relative)
        for relative in COMMON.FIXED_SMOKE_PATHS:
            self.assertIn(relative, paths)

    def test_route_index_converts_xml_guide_route_to_actual_output(self):
        site = ROOT / ".scratch/pages-resources-20261018-v32"
        provenance = json.loads((site / "export-provenance.json").read_bytes())
        routes = COMMON.provenance_route_outputs(provenance)
        self.assertEqual(routes["pvp/worldpvp/index.xml"], "pvp/worldpvp/index.xml.html")
        self.assertEqual(routes["pvp/worldpvp/worldpvp-gallery.html"], "pvp/worldpvp/worldpvp-gallery.html")

    def test_current_v32_receipts_match_actual_site_shape(self):
        checker = _load("check_portable")
        paths = checker.release_paths("v32")
        _local, _export, _browser, _pages, _provenance, counts = checker._verify_receipts(paths)
        self.assertEqual(counts, {
            "groups": 3,
            "images": 39,
            "provenance_sha256": "a071d47b65232f723c2e74112adab521eb124d22b57aa430437646f06f50d356",
        })

    def test_path_guard_rejects_traversal(self):
        with self.assertRaises(AssertionError):
            COMMON.safe_site_path("../outside")
        with self.assertRaises(AssertionError):
            COMMON.safe_site_path("C:/outside")

    def test_release_scripts_are_importable_without_running_network(self):
        for name in ("check_portable", "create_upload_release", "publish_release"):
            module = _load(name)
            self.assertTrue(callable(module.main))

    def test_release_safety_guards_are_present(self):
        creator = (HERE / "create_upload_release.py").read_text(encoding="utf-8")
        publisher = (HERE / "publish_release.py").read_text(encoding="utf-8")
        self.assertIn("main must equal origin/main", creator)
        self.assertIn("existing draft is unowned", creator)
        self.assertIn("set(uploaded) <= set(expected)", creator)
        self.assertNotIn("--force", creator)
        self.assertNotIn("--clobber", creator)
        self.assertIn("assets_before_publish", publisher)
        self.assertIn("resolved_tag_commit", publisher)
        self.assertIn("_verify_saved_published_config", publisher)
        self.assertIn("recovered_existing_publication", publisher)

    def test_published_recovery_requires_owned_exact_config_and_never_mutates(self):
        publisher = _load("publish_release")
        expected = {
            "archive.zip": (10, "a" * 64),
            "archive.zip.sha256": (5, "b" * 64),
            "NOTICE.md": (6, "c" * 64),
        }
        config = {
            "draft": False,
            "id": 42,
            "tag": publisher.TAG,
            "target_commit": "deadbeef",
            "portable_acceptance_sha256": "d" * 64,
            "expected_assets": {name: {"bytes": size, "sha256": digest}
                                for name, (size, digest) in expected.items()},
        }
        data = {
            "id": 42,
            "draft": False,
            "tag_name": publisher.TAG,
            "target_commitish": "deadbeef",
        }
        publisher._verify_saved_published_config(config, data, expected, "d" * 64, "deadbeef")
        publisher._verify_saved_published_config({**config, "draft": True}, data, expected, "d" * 64, "deadbeef")
        report = publisher._recovered_report("v32", 42, "deadbeef", "deadbeef", data, [], "portable.json")
        self.assertTrue(report["accepted"])
        self.assertTrue(report["recovered_existing_publication"])
        self.assertFalse(report["mutation_performed"])
        with self.assertRaises(AssertionError):
            publisher._verify_saved_published_config({**config, "id": 43}, data, expected, "d" * 64, "deadbeef")

    def test_main_recovers_owned_published_release_with_stale_draft_true(self):
        import json
        import tempfile
        from unittest.mock import patch
        publisher = _load("publish_release")
        expected = {"archive.zip": (10, "a" * 64), "archive.zip.sha256": (5, "b" * 64), "NOTICE.md": (6, "c" * 64)}
        target = "e" * 40
        config = {"draft": True, "id": 42, "tag": publisher.TAG, "target_commit": target,
                  "portable_acceptance_sha256": "d" * 64,
                  "expected_assets": {name: {"bytes": size, "sha256": digest} for name, (size,digest) in expected.items()}}
        data = {"id": 42, "draft": False, "tag_name": publisher.TAG, "target_commitish": target, "html_url": "https://example.invalid/release",
                "assets": [{"id": i, "name": n, "size": s, "state": "uploaded", "digest": "sha256:"+d} for i,(n,(s,d)) in enumerate(expected.items())]}
        with tempfile.TemporaryDirectory(prefix="root-recovery-fixture-", dir=HERE) as temp:
            folder = Path(temp)
            paths = {"draft": folder / "draft.json", "portable": folder / "portable.json", "publication_report": folder / "publication.json"}
            paths["draft"].write_text(json.dumps(config), encoding="utf-8")
            def api(endpoint):
                return {"sha": target} if "/commits/" in endpoint else data
            with patch.object(publisher, "release_paths", return_value=paths), \
                 patch.object(publisher, "_expected", return_value=(expected, "d" * 64)), \
                 patch.object(publisher, "_api", side_effect=api) as reads, \
                 patch.object(publisher, "run_local", return_value=target) as commands, \
                 patch.object(sys, "argv", ["publish_release.py", "--version", "v33"]):
                publisher.main()
            report = json.loads(paths["publication_report"].read_bytes())
            self.assertTrue(report["accepted"])
            self.assertTrue(report["recovered_existing_publication"])
            self.assertFalse(report["mutation_performed"])
            self.assertEqual(reads.call_count, 2)
            self.assertEqual([x.args[0] for x in commands.call_args_list], [["git", "rev-parse", "HEAD"], ["git", "rev-parse", "origin/main"]])


if __name__ == "__main__":
    unittest.main()
