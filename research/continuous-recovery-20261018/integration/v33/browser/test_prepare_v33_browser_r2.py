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
    path = HERE / "prepare_v33_browser_r2.py"
    spec = importlib.util.spec_from_file_location("v33_browser_preparer_r2_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prep = load()


class BrowserPreparerR2Tests(unittest.TestCase):
    def test_prepared_input_has_exact_late_reference_counts_and_pins(self):
        path = HERE / "v33-browser-input-r2.json"
        self.assertTrue(path.is_file(), "r2 input must be prepared before this test")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "wow-recovery.integration.v33-browser-input-r2.v1")
        self.assertEqual(payload["new_original_count"], 120)
        self.assertEqual(payload["browser_plan"]["ordinary_image_hrefs"]["required_unique_originals"], 69)
        self.assertEqual(payload["browser_plan"]["static_render_targets"]["candidate_count"], 30)
        self.assertEqual(payload["browser_plan"]["popup_full_image_links"]["required"], 21)
        additions = payload["r2_reference_additions"]["targets"]
        self.assertEqual(len(additions), 19)
        self.assertEqual(len({row["original"] for row in additions}), 19)
        self.assertEqual(sum(bool(row["ordinary_image_href"]) for row in additions), 12)
        self.assertEqual(sum(bool(row["static_render_candidate"]) for row in additions), 7)
        for row in additions:
            self.assertTrue(row["source_evidence"]["source_page_sha256"])
            self.assertGreater(int(row["source_evidence"]["source_line"]), 0)
            self.assertTrue(row["current_output_match"]["page_sha256"])
            self.assertGreater(int(row["current_output_match"]["line"]), 0)
        self.assertIn("r2_preparer", payload["source_bindings"])
        self.assertIn("navigation_exclusion_correction", payload["source_bindings"])
        self.assertIn("static40_batch4_plan", payload["source_bindings"])
        self.assertIn("news_body_batch2_plan", payload["source_bindings"])

    def test_news_parser_reads_expand_and_collapse_but_ignores_script_literals(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            old_output = prep.OUTPUT
            try:
                prep.OUTPUT = pathlib.Path(directory)
                page = pathlib.Path(directory) / "news-fixture.html"
                page.write_text(
                    '<script>const fake = "<div id=\"news-script\" class=\"news-collapse\">";</script>'
                    '<div id="news2" class="news-expand"><div class="news-toggle"><a>open</a></div></div>'
                    '<div class="news-collapse extra" id="news3"><div class="news-toggle"><a>closed</a></div></div>',
                    encoding="utf-8",
                )
                self.assertEqual(prep.news_toggle_ids_r2("news-fixture.html"), ["news2", "news3"])
            finally:
                prep.OUTPUT = old_output

    def test_current_matches_are_bound_to_actual_v33_page_bytes(self):
        payload = json.loads((HERE / "v33-browser-input-r2.json").read_text(encoding="utf-8"))
        for row in payload["r2_reference_additions"]["targets"]:
            page = ROOT / ".scratch/pages-resources-20261018-v33" / row["current_output_match"]["page_output"]
            digest = hashlib.sha256(page.read_bytes()).hexdigest()
            self.assertEqual(digest, row["current_output_match"]["page_sha256"])


if __name__ == "__main__":
    unittest.main()
