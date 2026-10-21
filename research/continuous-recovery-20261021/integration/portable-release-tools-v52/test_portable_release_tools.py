"""Offline contract tests for the isolated v52 portable release adapter."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


COMMON = _load("portable_release_common")
CHECKER = _load("check_portable")
CREATOR = _load("create_upload_release")
PUBLISHER = _load("publish_release")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> tuple[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return _sha(data), len(data)


def _fixture_provenance(site: Path) -> dict:
    paths = {
        "index.html",
        "__offline/route-map.json",
        "__offline/pages_runtime.js",
        "__offline/related-talent-icons.json",
        "__offline/related-talent-ui.json",
        "__offline/related-guide-images.json",
        "__offline/related-guide-images/thumb-thebroken.jpg",
        "__offline/aldor-scryers-lore.js",
        "info/basics/factions/aldorscryers/aldor-scryers.xml.html",
        "info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html",
        "info/encyclopedia/315.xml.html",
        "info/encyclopedia/349.xml.html",
        "info/encyclopedia/474.xml.html",
        "info/encyclopedia/thebroken.html",
        "contests/05-06-09/index.html",
        "info/basics/content-index.html",
        "info/items/tinfoilhat.xml.html",
        "info/races/two-headed-ogre.shtml.html",
        "misc/fan-site-program.html",
        "moltencore/index.html",
        "patchnotes/patch-9-29-04.shtml.html",
        "wrath/features/bard/bardclass.xml.html",
        "__offline/related-sites/blizzcast/index.html",
        "__offline/related-sites/blizzcast/archive.html",
        "info/items/images/socket_anim.swf",
        "info/races/images/dancing/gifs/dwarf_male.swf",
        "wrath/flash/global/tuskarr_idle.swf",
        "__offline/vendor/ruffle/a.wasm",
        "__offline/vendor/ruffle/b.wasm",
        "guide/one.html",
        "guide/one-gallery.html",
        "guide/one.jpg",
    }
    classes = ("druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior")
    base_path = "/WOW-Encyclopedia-Deployable-Archive/"
    paths.update(f"info/classes/{name}/talents.html" for name in classes)
    records = []
    for relative in sorted(paths):
        if relative == "__offline/route-map.json":
            canonical = base_path + "__offline/related-guide-images/thumb-thebroken.jpg"
            data = json.dumps({"base_path": base_path, "routes": {
                "/__offline/related-guide-images/thumb-thebroken.jpg": canonical,
                "/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg": canonical,
                "/burningcrusade/townhall/images/bestiary/thumb-broken.jpg": canonical,
            }, "aliases": {}}, sort_keys=True).encode("utf-8")
        else:
            data = f"fixture:{relative}\n".encode("utf-8")
        _write(site / relative, data)
        route = "/" + relative
        if relative.endswith(".html"):
            route = "/" + relative.removesuffix(".html")
        role = "source16_main_page" if relative in {
            "contests/05-06-09/index.html", "info/basics/content-index.html",
            "info/items/tinfoilhat.xml.html", "info/races/two-headed-ogre.shtml.html",
            "misc/fan-site-program.html", "moltencore/index.html",
            "patchnotes/patch-9-29-04.shtml.html", "wrath/features/bard/bardclass.xml.html",
        } else "fixture"
        records.append({
            "route": route,
            "output_path": relative,
            "derived_sha256": _sha(data),
            "derived_length": len(data),
            "role": role,
            "kind": "html" if relative.endswith(".html") else "other",
        })
    provenance = {
        "base_path": base_path,
        "files": records,
        "guide_image_collections": {
            "group_count": 1,
            "image_count": 1,
            "groups": [{
                "guide_route": "/guide/one",
                "gallery_route": "/guide/one-gallery",
                "image_count": 1,
                "images": [{"route": "/guide/one.jpg"}],
            }],
        },
        "flash_exhibits": {
            "original_swfs": {
                "socket_anim": {"path": "info/items/images/socket_anim.swf"},
                "dwarf_male": {"path": "info/races/images/dancing/gifs/dwarf_male.swf"},
                "tuskarr_idle": {"path": "wrath/flash/global/tuskarr_idle.swf"},
            },
            "files": [
                {"kind": "flash_runtime", "output_path": "__offline/vendor/ruffle/a.wasm"},
                {"kind": "flash_runtime", "output_path": "__offline/vendor/ruffle/b.wasm"},
            ],
        },
        "talent_box_layout_compatibility": {
            "records": [{
                "page_routes": [f"/info/classes/{name}/talents.html" for name in classes],
            }],
        },
        "related_talent_icons": {"catalog_path": "__offline/related-talent-icons.json"},
        "related_talent_ui": {"catalog_path": "__offline/related-talent-ui.json"},
        "related_guide_images": {
            "catalog_path": "__offline/related-guide-images.json",
            "image_count": 1,
            "route_reuses": {
                "/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg": "/__offline/related-guide-images/thumb-thebroken.jpg",
                "/burningcrusade/townhall/images/bestiary/thumb-broken.jpg": "/__offline/related-guide-images/thumb-thebroken.jpg",
            },
        },
    }
    data = json.dumps(provenance, sort_keys=True).encode("utf-8")
    _write(site / "export-provenance.json", data)
    return provenance


def _fixture_receipts(folder: Path) -> tuple[dict[str, Path], dict, dict, dict, dict]:
    site = folder / "site"
    provenance = _fixture_provenance(site)
    provenance_bytes = (site / "export-provenance.json").read_bytes()
    provenance_sha = _sha(provenance_bytes)
    all_files = [p for p in site.rglob("*") if p.is_file()]
    local_objects = [
        {"path": p.relative_to(site).as_posix(), "sha256": _sha(p.read_bytes()), "bytes": p.stat().st_size}
        for p in all_files
    ]
    online_path = "index.html"
    online_file = site / online_path
    local_site = COMMON.rel(COMMON.ROOT, site)
    export_path = folder / "export.json"
    browser_path = folder / "browser.json"
    local_path = folder / "local.json"
    pages_path = folder / "pages-online.json"
    export = {
        "accepted": True,
        "published": False,
        "version": 3,
        "local_site": local_site,
        "actual_files": len(all_files),
        "export_provenance_sha256": provenance_sha,
    }
    browser = {
        "accepted": True,
        "version": 3,
        "export_provenance_sha256": provenance_sha,
        "pages": [{"path": "info/classes/druid/talents.html", "status": 200}],
        "external_requests": [],
        "page_errors": [],
        "request_failures": [],
        "asset_fulfillments": 0,
    }
    pages_online = {
        "accepted": True,
        "version": 3,
        "local_site": local_site,
        "objects": [{
            "path": online_path,
            "local_bytes": online_file.stat().st_size,
            "local_sha256": _sha(online_file.read_bytes()),
        }],
    }
    export_path.write_text(json.dumps(export), encoding="utf-8")
    browser_path.write_text(json.dumps(browser), encoding="utf-8")
    pages_path.write_text(json.dumps(pages_online), encoding="utf-8")
    local = {
        "accepted": True,
        "published": False,
        "version": 3,
        "local_site": local_site,
        "actual_files": len(all_files),
        "export_provenance_sha256": provenance_sha,
        "objects": local_objects,
        "bindings": [
            {"path": COMMON.rel(COMMON.ROOT, export_path), "sha256": _sha(export_path.read_bytes())},
            {"path": COMMON.rel(COMMON.ROOT, browser_path), "sha256": _sha(browser_path.read_bytes())},
        ],
    }
    local_path.write_text(json.dumps(local), encoding="utf-8")
    paths = {"site": site, "local": local_path, "export": export_path, "browser": browser_path,
             "pages_online": pages_path, "extract": folder / "local bundle smoke 20261021 v52",
             "archive": folder / "archive.zip", "package_report": folder / "package.json",
             "server_log": folder / "server.log", "portable": folder / "portable.json"}
    return paths, local, export, browser, pages_online


def _make_archive(paths: dict[str, Path], provenance: dict, *, symlink_name: str | None = None) -> dict:
    expected = CHECKER._expected_members(paths, provenance)
    extras = {
        "README.md": b"fixture readme\n",
        "START_BROWSE.cmd": b"@echo off\r\n",
        "archive-metadata.json": b"{}\n",
    }
    members = {name: (paths["site"] / name[5:]).read_bytes() if name.startswith("site/") else (ROOT / name).read_bytes()
               for name in expected}
    members.update(extras)
    sums = "\n".join(f"{_sha(data)}  {len(data)}  {name}" for name, data in sorted(members.items())) + "\n"
    members["FILE_SHA256SUMS.txt"] = sums.encode("utf-8")
    with zipfile.ZipFile(paths["archive"], "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in members.items():
            if name == symlink_name:
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                zf.writestr(info, data)
            else:
                zf.writestr(name, data)
    archive_sha = _sha(paths["archive"].read_bytes())
    paths["package_report"].write_text(json.dumps({
        "network_performed": False,
        "archive": paths["archive"].name,
        "package_member_count": len(members),
        "verification": {"archive_sha256": archive_sha, "member_count": len(members)},
    }), encoding="utf-8")
    return members


class PortableReleaseToolTests(unittest.TestCase):
    def test_version_paths_and_fixed_release_contract(self):
        paths = COMMON.release_paths("v52")
        self.assertEqual(COMMON.RUN_DATE, "20261021")
        self.assertEqual(COMMON.TAG, "archive-20080512-browser-20261021-v52")
        self.assertTrue(str(paths["extract"]).endswith("local bundle smoke 20261021 v52"))
        with self.assertRaises(AssertionError):
            COMMON.release_paths("v47")
        with self.assertRaises(ValueError):
            COMMON.release_paths("v52/../v47")

    def test_smoke_derives_all_v52_categories(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-smoke-") as temp:
            site = Path(temp) / "site"
            provenance = _fixture_provenance(site)
            paths, counts = COMMON.provenance_smoke_paths(provenance)
            self.assertEqual(counts["flash_or_wasm"], 5)
            self.assertEqual(counts["talent"], 11)
            self.assertEqual(counts["encyclopedia"], 3)
            self.assertEqual(counts["thebroken"], 1)
            self.assertEqual(counts["source16_pages"], 8)
            self.assertEqual(counts["blizzcast"], 2)
            self.assertEqual(counts["related_guide_reuses"], 2)
            self.assertIn("__offline/related-guide-images.json", paths)
            self.assertIn("__offline/related-guide-images/thumb-thebroken.jpg", paths)
            route_map = json.loads((site / "__offline/route-map.json").read_bytes())
            canonical = route_map["routes"]["/__offline/related-guide-images/thumb-thebroken.jpg"]
            self.assertEqual(route_map["routes"]["/burningcrusade/townhall/images/bestiary/thumb-broken.jpg"], canonical)
            self.assertNotIn("/burningcrusade/townhall/images/bestiary/thumb-broken.jpg", route_map["aliases"])
            self.assertIn("info/items/images/socket_anim.swf", paths)
            self.assertIn("__offline/vendor/ruffle/a.wasm", paths)
            self.assertIn("__offline/related-talent-icons.json", paths)
            self.assertIn("info/encyclopedia/315.xml.html", paths)
            self.assertIn("info/encyclopedia/thebroken.html", paths)
            self.assertIn("contests/05-06-09/index.html", paths)

    def test_aldor_scryers_smoke_requires_explicit_final_gate(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-aldor-gate-") as temp:
            folder = Path(temp)
            site = folder / "site"
            provenance = _fixture_provenance(site)
            gate_path = folder / "research" / "continuous-recovery-20261021" / "publication" / "root-v52-final-acceptance.json"
            with patch.object(COMMON, "ROOT", folder):
                paths, counts = COMMON.smoke_paths(provenance, {}, {}, {}, site)
                self.assertEqual(counts["aldor_scryers"], 0)
                self.assertEqual(COMMON.aldor_scryers_gate(site)["status"], "missing")
                gate_path.parent.mkdir(parents=True)
                gate_path.write_text(json.dumps({
                    "accepted": True,
                    "version": "v52",
                    "aldor_scryers_lore": {
                        "accepted": True,
                        "version": "v52",
                        "generated_relative": "__offline/aldor-scryers-lore.js",
                        "page_paths": [
                            "info/basics/factions/aldorscryers/aldor-scryers.xml.html",
                            "info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html",
                        ],
                    },
                }), encoding="utf-8")
                paths, counts = COMMON.smoke_paths(provenance, {}, {}, {}, site)
                self.assertEqual(counts["aldor_scryers"], 3)
                for relative in COMMON.ALDOR_SCRYERS_SMOKE_PATHS:
                    self.assertIn(relative, paths)
                self.assertEqual(COMMON.aldor_scryers_gate(site)["status"], "accepted")

    def test_receipt_contract_and_external_field_drift_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-receipts-") as temp:
            folder = Path(temp)
            paths, local, export, browser, pages = _fixture_receipts(folder)
            paths["local"].write_text(json.dumps(local), encoding="utf-8")
            result = CHECKER._verify_receipts(paths)
            self.assertEqual(result[-1]["local_objects"], local["actual_files"])
            self.assertEqual(result[-1]["groups"], 1)
            self.assertEqual(result[-1]["images"], 1)
            bad_export = copy.deepcopy(export)
            bad_export.pop("actual_files")
            paths["export"].write_text(json.dumps(bad_export), encoding="utf-8")
            with self.assertRaises(AssertionError):
                CHECKER._verify_receipts(paths)
            paths["export"].write_text(json.dumps(export), encoding="utf-8")
            bad_export = copy.deepcopy(export)
            bad_export["published"] = True
            paths["export"].write_text(json.dumps(bad_export), encoding="utf-8")
            with self.assertRaises(AssertionError):
                CHECKER._verify_receipts(paths)
            paths["export"].write_text(json.dumps(export), encoding="utf-8")
            bad_browser = copy.deepcopy(browser)
            bad_browser["external_requests"] = [{"url": "https://outside.invalid/"}]
            paths["browser"].write_text(json.dumps(bad_browser), encoding="utf-8")
            with self.assertRaises(AssertionError):
                CHECKER._verify_receipts(paths)

    def test_source_sha_drift_and_object_field_drift_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-drift-") as temp:
            folder = Path(temp)
            paths, local, export, browser, pages = _fixture_receipts(folder)
            drifted = copy.deepcopy(local)
            drifted["objects"][0].pop("sha256")
            paths["local"].write_text(json.dumps(drifted), encoding="utf-8")
            with self.assertRaises(AssertionError):
                CHECKER._verify_receipts(paths)
            paths["local"].write_text(json.dumps(local), encoding="utf-8")
            provenance_path = paths["site"] / "export-provenance.json"
            provenance = json.loads(provenance_path.read_bytes())
            provenance["files"][0]["derived_sha256"] = "0" * 64
            provenance_path.write_text(json.dumps(provenance, sort_keys=True), encoding="utf-8")
            with self.assertRaises(AssertionError):
                CHECKER._verify_receipts(paths)

    def test_zip_sha_length_crc_and_symlink_guards(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-zip-") as temp:
            folder = Path(temp)
            paths, local, export, browser, pages = _fixture_receipts(folder)
            provenance = json.loads((paths["site"] / "export-provenance.json").read_bytes())
            members = _make_archive(paths, provenance)
            result = CHECKER._check_zip(paths, provenance, json.loads(paths["package_report"].read_bytes()), 1 << 60)
            self.assertEqual(result[-1], len(members))

        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-symlink-") as temp:
            folder = Path(temp)
            paths, local, export, browser, pages = _fixture_receipts(folder)
            provenance = json.loads((paths["site"] / "export-provenance.json").read_bytes())
            _make_archive(paths, provenance, symlink_name="README.md")
            with self.assertRaises(AssertionError):
                CHECKER._check_zip(paths, provenance, json.loads(paths["package_report"].read_bytes()), 1 << 60)

    def test_extracted_space_path_and_loopback_get_head(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="portable-v52-server-") as temp:
            folder = Path(temp)
            paths, local, export, browser, pages = _fixture_receipts(folder)
            provenance = json.loads((paths["site"] / "export-provenance.json").read_bytes())
            _make_archive(paths, provenance)
            CHECKER._check_zip(paths, provenance, json.loads(paths["package_report"].read_bytes()), 1 << 60)
            requests, smoke = CHECKER._serve_smoke(paths, provenance, local, browser, pages)
            self.assertIn(" ", str(paths["extract"]))
            self.assertEqual(len(requests), smoke["paths"] * 2)
            self.assertTrue(requests)
            self.assertEqual({item["method"] for item in requests}, {"GET", "HEAD"})
            self.assertEqual({item["status"] for item in requests}, {200})

    def test_release_scripts_import_and_keep_no_clobber_guards(self):
        self.assertTrue(callable(CHECKER.main))
        self.assertTrue(callable(CREATOR.main))
        self.assertTrue(callable(PUBLISHER.main))
        creator = (HERE / "create_upload_release.py").read_text(encoding="utf-8")
        publisher = (HERE / "publish_release.py").read_text(encoding="utf-8")
        self.assertIn("existing draft is unowned", creator)
        self.assertIn("set(uploaded) <= set(expected)", creator)
        self.assertNotIn("--force", creator)
        self.assertNotIn("--clobber", creator)
        self.assertIn("recovered_existing_publication", publisher)
        self.assertIn("mutation_performed", publisher)


if __name__ == "__main__":
    unittest.main()
