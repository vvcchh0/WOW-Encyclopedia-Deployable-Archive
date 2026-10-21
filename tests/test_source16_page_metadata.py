"""Original Common Crawl entity identity must survive the browser derivation."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import export_github_pages as pages


def record():
    return {
        "role": "source16_main_page",
        "source_base_url": "http://www.worldofwarcraft.com/info/items/tinfoilhat.xml",
        "actual_timestamp": "20080512010107",
        "source_sha256": "a" * 64, "source_length": 60077,
        "source_arc": {
            "filename": "crawl-001/2008/06/25/0/1214442499933_0.arc.gz",
            "offset": 2191870, "length": 9104, "compressed_sha256": "b" * 64,
        },
    }


class Source16MetadataTests(unittest.TestCase):
    def test_original_identity_and_public_whitelist(self):
        source = record()
        source["private_payload_path"] = "private/not-for-export.html"
        source["source_arc"]["private_transport_notes"] = "fixture-private-value"
        ref = pages.source16_main_page_reference(source)
        self.assertEqual(ref["sha256"], "a" * 64)
        self.assertEqual(ref["actual_capture_timestamp"], "20080512010107")
        self.assertEqual(ref["length"], 60077)
        self.assertNotIn("private_payload_path", ref)
        self.assertNotIn("private_transport_notes", ref["source_arc"])

    def test_unrelated_records_are_exact_noops(self):
        self.assertIsNone(pages.source16_main_page_reference({"role": "archived_news_html"}))
        text = "<html><body>old page</body></html>"
        self.assertEqual(pages.annotate_source16_main_page(text, None), text)

    def test_foreign_origin_and_transient_query_are_rejected(self):
        for url in ("https://example.org/info/items/tinfoilhat.xml",
                    "http://www.worldofwarcraft.com:81/info/items/tinfoilhat.xml",
                    "http://@www.worldofwarcraft.com/info/items/tinfoilhat.xml",
                    "http://www.worldofwarcraft.com/info/items/tinfoilhat.xml;jsessionid=fixture",
                    "http://www.worldofwarcraft.com/info/items/tinfoilhat.xml?temporary=fixture"):
            source = record()
            source["source_base_url"] = url
            with self.assertRaises(pages.PagesExportError):
                pages.source16_main_page_reference(source)

    def test_invalid_capture_and_coordinates_are_rejected(self):
        for key, value in (("actual_timestamp", "20080532000000"),
                           ("actual_timestamp", "20080513000000"),
                           ("source_sha256", "invalid"), ("source_length", True)):
            source = record()
            source[key] = value
            with self.assertRaises(pages.PagesExportError):
                pages.source16_main_page_reference(source)
        source = record()
        source["source_arc"]["filename"] = "crawl-001/../outside.arc.gz"
        with self.assertRaises(pages.PagesExportError):
            pages.source16_main_page_reference(source)

    def test_notice_uses_real_body_not_script_text(self):
        text = '<html><head><script>var s="<body>";</script></head><body class="actual">Text</body></html>'
        ref = pages.source16_main_page_reference(record())
        result = pages.annotate_source16_main_page(text, ref)
        self.assertIn('<body class="actual">\n<aside', result)
        self.assertIn('2008-05-12 01:01:07 UTC', result)
        self.assertIn('var s="<body>";', result)
        self.assertEqual(result.count('id="__offline-source16-note"'), 1)


if __name__ == "__main__":
    unittest.main()
