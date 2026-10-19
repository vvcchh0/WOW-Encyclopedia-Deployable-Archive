from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402


NAV_ROUTE = "/shared/wow-com/includes-client/navtreefunctions.js"
WINNERS_PATH = "/WOW-Encyclopedia-Deployable-Archive/contests/05-05-25/winners.html"


def _node() -> str | None:
    return shutil.which("node")


def _runtime_result(source: str, pathname: str) -> str:
    node = _node()
    if not node:
        raise unittest.SkipTest("Node.js is required for the contest nav runtime fixture")
    driver = (
        "const vm = require('vm');\n"
        f"const code = {json.dumps(source)};\n"
        f"const context = {{window: {{}}, document: {{location: {{pathname: {json.dumps(pathname)}}}}}}};\n"
        "vm.createContext(context);\n"
        "vm.runInContext(code, context);\n"
        "process.stdout.write(String(context.window.seen === undefined ? 'undefined' : context.window.seen));\n"
    )
    completed = subprocess.run([node, "-e", driver], text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout


def _fixture_source(*, result: str | None = None, menu_label: str | None = "Contests") -> str:
    menu = "" if menu_label is None else f"var Menu1_6_4 = [{json.dumps(menu_label)}, '/contests/', '', 0];"
    initial = "var result;" if result is None else f"var result = {json.dumps(result)};"
    return (
        f"{initial}{menu}\n"
        "function stripId(value) { return value; }\n"
        "function tree(value) { window.seen = value; }\n"
        "tree(result);\n"
    )


class ContestNavigationRecoveryTests(unittest.TestCase):
    def test_real_navtree_source_is_derived_once_and_source_stays_frozen(self) -> None:
        source_path = ROOT / "mirror/20080512/www.worldofwarcraft.com" / NAV_ROUTE.lstrip("/")
        source_bytes = source_path.read_bytes()
        derived, changed = pages.rewrite_contest_navtree_fallback(
            source_bytes.decode("utf-8"), base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertTrue(changed)
        self.assertEqual(derived.count("offline-contest-nav-fallback-v1"), 1)
        self.assertEqual(derived.count("tree(result);"), 1)
        self.assertLess(derived.index("offline-contest-nav-fallback-v1"), derived.index("tree(result);"))
        self.assertEqual(pages.rewrite_contest_navtree_fallback(derived, base_path=pages.DEFAULT_BASE_PATH), (derived, False))
        self.assertEqual(source_path.read_bytes(), source_bytes)

    def test_runtime_success_uses_real_path_and_loaded_contests_label(self) -> None:
        derived, changed = pages.rewrite_contest_navtree_fallback(
            _fixture_source(), base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertTrue(changed)
        self.assertEqual(_runtime_result(derived, WINNERS_PATH), "1_6_4")

    def test_existing_result_and_other_path_are_unchanged(self) -> None:
        derived, _ = pages.rewrite_contest_navtree_fallback(
            _fixture_source(result="existing"), base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertEqual(_runtime_result(derived, WINNERS_PATH), "existing")
        other_path, _ = pages.rewrite_contest_navtree_fallback(
            _fixture_source(), base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertEqual(
            _runtime_result(other_path, "/WOW-Encyclopedia-Deployable-Archive/contests/index.html"),
            "undefined",
        )

    def test_missing_or_mismatched_menu_node_does_not_fabricate_result(self) -> None:
        missing, _ = pages.rewrite_contest_navtree_fallback(
            _fixture_source(menu_label=None), base_path=pages.DEFAULT_BASE_PATH
        )
        wrong, _ = pages.rewrite_contest_navtree_fallback(
            _fixture_source(menu_label="Community"), base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertEqual(_runtime_result(missing, WINNERS_PATH), "undefined")
        self.assertEqual(_runtime_result(wrong, WINNERS_PATH), "undefined")

    def test_ambiguous_targets_are_rejected(self) -> None:
        derived, _ = pages.rewrite_contest_navtree_fallback(
            _fixture_source(), base_path=pages.DEFAULT_BASE_PATH
        )
        with self.assertRaisesRegex(pages.PagesExportError, "tree\(result\)"):
            pages.rewrite_contest_navtree_fallback(
                _fixture_source() + "tree(result);\n", base_path=pages.DEFAULT_BASE_PATH
            )
        with self.assertRaisesRegex(pages.PagesExportError, "tree\(result\)"):
            pages.rewrite_contest_navtree_fallback(
                derived + "tree(result);\n", base_path=pages.DEFAULT_BASE_PATH
            )
        duplicate_marker = (
            _fixture_source()
            + "/* offline-contest-nav-fallback-v1 */\n"
            + "/* offline-contest-nav-fallback-v1 */\n"
        )
        with self.assertRaisesRegex(pages.PagesExportError, "markers"):
            pages.rewrite_contest_navtree_fallback(duplicate_marker, base_path=pages.DEFAULT_BASE_PATH)

    def test_export_pipeline_derives_navtree_and_provenance_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            site = base / "offline/site"
            site.mkdir(parents=True)
            files = {
                "index.xml": b"<html><head></head><body>home</body></html>",
                NAV_ROUTE.lstrip("/"): _fixture_source().encode("utf-8"),
            }
            records = []
            for relative, data in files.items():
                path = site / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                route = "/" + relative
                kind = "html" if relative == "index.xml" else "js"
                records.append(
                    {
                        "route": route,
                        "output_path": "offline/site/" + relative,
                        "derived_sha256": hashlib.sha256(data).hexdigest(),
                        "derived_length": len(data),
                        "mime": "text/html; charset=UTF-8" if kind == "html" else "application/javascript",
                        "kind": kind,
                        "source_base_url": "http://www.worldofwarcraft.com" + route,
                    }
                )
            manifest_path = base / "offline/build-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchor_timestamp": "20080512210044",
                        "route_aliases": {"/": "/index.xml"},
                        "origin_index": {"www.worldofwarcraft.com" + row["route"]: row["route"] for row in records},
                        "files": records,
                    }
                ),
                encoding="utf-8",
            )
            output = base / "pages"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest_path,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
            )
            exported = (output / NAV_ROUTE.lstrip("/")).read_text(encoding="utf-8")
            self.assertIn("offline-contest-nav-fallback-v1", exported)
            self.assertEqual(result["stats"]["contest_navtree_fallback_repaired"], 1)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == NAV_ROUTE)
            self.assertIn("derived contest nav fallback", item["derivation_reason"])


if __name__ == "__main__":
    unittest.main()
