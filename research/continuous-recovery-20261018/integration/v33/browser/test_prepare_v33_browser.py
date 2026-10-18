from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def load():
    path = HERE / "prepare_v33_browser.py"
    spec = importlib.util.spec_from_file_location("v33_browser_preparer_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prep = load()


class FakeMirror:
    def is_primary_origin(self, url):
        return "worldofwarcraft.com" in url

    def route_path(self, url):
        return "/" + url.split(".com", 1)[1].split("?", 1)[0].lstrip("/")

    def origin_route(self, url):
        parsed = url.split(".com", 1)[1].split("?", 1)[0]
        return "/_origins/example.com" + parsed


class FakeExporter:
    mirror = FakeMirror()

    @staticmethod
    def static_rel_for_route(route, record=None):
        value = route.lstrip("/")
        if record and record.get("kind") == "html" and not value.endswith(".html"):
            value += ".html"
        return value or "index.html"


class BrowserPreparerTests(unittest.TestCase):
    def test_preflight_export_marker_falls_back_to_loader_and_stays_strict(self):
        self.assertIs(prep.preflight_export_executed({"loader_preflight": {"export_executed": False}}), False)
        self.assertIs(prep.preflight_export_executed({"export_executed": False, "loader_preflight": {"export_executed": True}}), False)
        self.assertIs(prep.preflight_export_executed({"export_executed": True, "loader_preflight": {"export_executed": False}}), True)
        self.assertIsNone(prep.preflight_export_executed({"export_executed": None, "loader_preflight": {"export_executed": False}}))
        self.assertIsNot(prep.preflight_export_executed({}), False)

    def test_real_v32_image_overlay_schema_is_read_only_compatible(self):
        if not prep.V32_PROVENANCE.exists():
            self.skipTest("accepted v32 provenance is unavailable")
        payload = json.loads(prep.V32_PROVENANCE.read_text(encoding="utf-8"))
        row = next(row for row in payload["files"] if row.get("kind") == "image_overlay")
        self.assertEqual(row.get("role"), "image_overlay")
        for key in ("original_url", "mime", "output_path", "derived_length", "derived_sha256"):
            self.assertIn(key, row)
        items = prep.load_frozen_v32_items({"files": [row]})
        self.assertEqual(items[0]["_map_role"], "frozen_v32_image_overlay")
        self.assertEqual(items[0]["served_output_path"], row["output_path"])

    def test_old_and_new_reference_sets_keep_all_validated_hrefs(self):
        old = {"original_url": "http://www.worldofwarcraft.com/old.gif", "output_path": "old.gif", "derived_length": 4, "derived_sha256": "a" * 64, "mime": "image/gif", "kind": "image_overlay", "role": "image_overlay"}
        old_item = prep.load_frozen_v32_items({"files": [old]})[0]
        new_item = {"original": "http://www.worldofwarcraft.com/new.jpg", "overlay_role": "primary_image_overlay"}
        record = {
            "route": "/news/rss-08-2007.xml", "kind": "html", "source_base_url": "http://www.worldofwarcraft.com/news/rss-08-2007.xml", "source_sha256": "page-sha",
            "references": [
                {"literal": "/old.gif", "resolved_url": old["original_url"], "target": "/__offline/missing.html?requested=" + old["original_url"], "context": "navigation"},
                {"literal": "/new.jpg", "resolved_url": new_item["original"], "target": "/__offline/missing.html?requested=" + new_item["original"], "context": "navigation"},
            ],
        }
        result = prep.derive_references([record], [old_item, new_item], FakeExporter)
        self.assertEqual({row["original"] for row in result["ordinary_image_hrefs"]}, {old["original_url"], new_item["original"]})

    def test_v33_provenance_preserves_old_route_and_bytes_metadata(self):
        old = {"original_url": "http://www.worldofwarcraft.com/old.gif", "output_path": "old.gif", "derived_length": 4, "derived_sha256": "a" * 64, "mime": "image/gif", "kind": "image_overlay", "role": "image_overlay"}
        item = prep.load_frozen_v32_items({"files": [old]})[0]
        self.assertEqual(prep.validate_frozen_v32_records({"files": [old]}, [item]), [item])

    def test_popup_literal_resolves_against_source_page(self):
        value = prep.popup_original(
            "javascript:popUpOmega('images/arena/ss1.jpg',800,611)",
            "http://www.worldofwarcraft.com/insider/11/arena.xml",
        )
        self.assertEqual(value, "http://www.worldofwarcraft.com/insider/11/images/arena/ss1.jpg")
        self.assertIsNone(prep.popup_original("javascript:showTip('x')", "http://example.com/a"))

    def test_reference_classes_are_separate(self):
        original = "http://www.worldofwarcraft.com/images/new.jpg"
        item = {"original": original, "overlay_role": "primary_image_overlay"}
        record = {
            "route": "/news/rss-08-2007.xml",
            "kind": "html",
            "source_base_url": "http://www.worldofwarcraft.com/news/rss-08-2007.xml",
            "source_sha256": "page-sha",
            "references": [
                {"literal": "javascript:popUpOmega('/images/new.jpg',100,100)", "resolved_url": "http://www.worldofwarcraft.com/news/rss-08-2007.xml", "target": "javascript:popUpOmega('/images/new.jpg',100,100)", "context": "navigation"},
                {"literal": "/images/new.jpg", "resolved_url": original, "target": "/__offline/missing.html?requested=" + original, "context": "navigation"},
                {"literal": "/images/new.jpg", "resolved_url": original, "target": "/__offline/missing-image.svg?requested=" + original, "context": "css_url"},
            ],
        }
        result = prep.derive_references([record], [item], FakeExporter)
        self.assertEqual(len(result["popup_full_image_links"]), 1)
        self.assertEqual(len(result["ordinary_image_hrefs"]), 1)
        self.assertEqual(len(result["static_render_targets"]), 1)
        self.assertEqual(result["popup_full_image_links"][0]["page_output"], "news/rss-08-2007.xml.html")
        self.assertEqual(result["ordinary_image_hrefs"][0]["context"], "navigation")

    def test_new_map_item_checks_exact_public_bytes(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            file = pathlib.Path(directory) / "image.jpg"
            data = b"\xff\xd8\xff browser fixture"
            file.write_bytes(data)
            relative = file.relative_to(ROOT).as_posix()
            item = {"original": "http://www.worldofwarcraft.com/a.jpg", "overlay_role": "primary_image_overlay", "local_path": relative, "length": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            result = prep.load_new_items({"items": [item]}, {"items": []})
            self.assertEqual(result[0]["original"], item["original"])
            self.assertEqual(result[0]["_map_role"], "primary_image_overlay")

    def test_prepare_gate_refuses_without_root_manifest_or_v33_output(self):
        if prep.INPUT.exists() or prep.OUTPUT.exists() or prep.V33_PROVENANCE.exists():
            self.skipTest("live v33 output or prepared browser input exists; preserve immutable artifacts")
        with self.assertRaisesRegex(RuntimeError, "browser input gate is not ready"):
            prep.build_input()

    def test_checker_contract_requires_both_go_flags_and_uses_local_boundary(self):
        source = (HERE / "check_v33_browser.cjs").read_text(encoding="utf-8")
        self.assertIn("--go --root-browser-go", source)
        self.assertIn("root-v33-browser-input-acceptance.json", source)
        self.assertIn("report.external_requests", source)
        self.assertIn("outputRoot", source)
        self.assertIn("news_toggle_ids", source)
        self.assertIn("path.resolve(__dirname, '../../../../..')", source)
        self.assertNotIn("export_github_pages.py --", source)

    def test_news_toggle_ids_parse_actual_entry_and_ignore_script_literals(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            old_output = prep.OUTPUT
            try:
                prep.OUTPUT = pathlib.Path(directory)
                page = pathlib.Path(directory) / "news/rss-08-2007.xml.html"
                page.parent.mkdir(parents=True)
                page.write_text(
                    '<script>const fake = "<div id=\\"news-script\\" class=\\"news-collapse\\">";</script>'
                    '<div class="news-collapse" id="news2-1-07-1212"><div class="news-toggle"><a>open</a></div></div>'
                    '<div id="news2-2" class="news-expand"><div class="news-toggle"><a>already</a></div></div>',
                    encoding="utf-8",
                )
                self.assertEqual(prep.news_toggle_ids("news/rss-08-2007.xml.html"), ["news2-1-07-1212"])
            finally:
                prep.OUTPUT = old_output


if __name__ == "__main__":
    unittest.main()
