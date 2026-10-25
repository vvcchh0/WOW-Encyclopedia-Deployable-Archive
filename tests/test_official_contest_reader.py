from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import official_contest_reader as reader
import export_github_pages as pages


class OfficialContestReaderTests(unittest.TestCase):
    def bundle(self):
        return reader.load_official_contest_bundle(reader.MAP_RELATIVE, ROOT, "/archive/", reader.MANIFEST_SHA256)

    def test_preserves_five_captions_without_loading_missing_photographs_or_scripts(self):
        bundle = self.bundle()
        document = bundle.generated_files[0]["data"].decode()
        self.assertEqual(len(bundle.generated_files), 3)
        self.assertEqual(document.count("Photograph not yet recovered."), 5)
        self.assertIn("wondeful costumes", document)
        self.assertIn("2008-08-29", document)
        self.assertIn("Warlock Nemesis Set &amp; Succubus", document)
        self.assertNotIn("<script", document)
        self.assertNotIn("<form", document)
        self.assertNotIn("<img", document)
        data = json.loads(bundle.generated_files[1]["data"])
        self.assertEqual(data["article"]["stated_honorable_costumes"], 28)
        self.assertEqual(data["article"]["honorable_viewer_parameter"], 29)
        redirect = bundle.generated_files[2]
        self.assertEqual(redirect["path"], reader.LEGACY_REDIRECT_ROUTE)
        self.assertIn('content="0;url=/archive/contests/06-10-costume/winners.html"', redirect["data"].decode())
        self.assertNotIn('<script', redirect["data"].decode())

    def test_rejects_wrong_context_source_drift_and_network_base(self):
        with self.assertRaisesRegex(reader.OfficialContestError, "manifest guard"):
            reader.load_official_contest_bundle(reader.MAP_RELATIVE, ROOT, "/", "0" * 64)
        with self.assertRaisesRegex(reader.OfficialContestError, "base path"):
            reader.load_official_contest_bundle(reader.MAP_RELATIVE, ROOT, "//other.example/", reader.MANIFEST_SHA256)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / reader.MAP_RELATIVE
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / reader.MAP_RELATIVE).read_bytes() + b" ")
            with self.assertRaisesRegex(reader.OfficialContestError, "SHA-256"):
                reader.load_official_contest_bundle(target, root, "/", reader.MANIFEST_SHA256)

    def test_text_renderer_escapes_article_values(self):
        data = json.loads((ROOT / reader.MAP_RELATIVE).read_bytes())
        data = copy.deepcopy(data)
        data["winners"][0]["work"] = '<script>alert("x")</script>'
        text = reader._render(data, "/").decode()
        self.assertIn("&lt;script&gt;", text)
        self.assertNotIn("<script", text)

    def test_export_rewrites_original_news_link_and_records_the_official_source(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site = root / "offline/site"
            site.mkdir(parents=True)
            text = b'<html><head><title>News</title></head><body><a href="http://www.worldofwarcraft.com/contests/06-10-costume/winners.shtml">Costume winners</a></body></html>'
            (site / "news.html").write_bytes(text)
            record = {"route": "/news.html", "output_path": "offline/site/news.html",
                      "derived_sha256": hashlib.sha256(text).hexdigest(), "derived_length": len(text),
                      "mime": "text/html; charset=UTF-8", "kind": "html",
                      "source_base_url": "http://www.worldofwarcraft.com/news.html"}
            manifest = root / "offline/build-manifest.json"
            manifest.write_bytes(json.dumps({"schema_version": 1, "anchor_timestamp": "20080512210044",
                                             "route_aliases": {"/": "/news.html"}, "origin_index": {}, "files": [record]}).encode())
            with patch.object(reader, "load_official_contest_bundle", return_value=bundle) as load:
                result = pages.export_pages(source_site=site, manifest_path=manifest, output=root / "export",
                                            workspace_root=root, base_path="/archive/", max_bytes=None,
                                            min_free_bytes=0, official_contest_map=Path("fixed-input.json"))
            self.assertEqual(load.call_args.args[3], hashlib.sha256(manifest.read_bytes()).hexdigest())
            rewritten = (root / "export/news.html").read_text(encoding="utf-8")
            self.assertIn('href="/archive/contests/06-10-costume/winners.html"', rewritten)
            routes = json.loads((root / "export/__offline/route-map.json").read_bytes())
            self.assertEqual(routes["routes"]["/contests/06-10-costume/winners.shtml"], "/archive/contests/06-10-costume/winners.html")
            self.assertEqual(result["stats"]["official_contest_reading_pages"], 1)
            provenance = json.loads((root / "export/export-provenance.json").read_bytes())
            self.assertEqual(provenance["official_contest_reading"]["image_bytes_recovered"], 0)


if __name__ == "__main__":
    unittest.main()
