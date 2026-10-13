from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402


class GithubPagesExportTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path]:
        site = base / "offline/site"
        site.mkdir(parents=True)
        files = {
            "index.xml": '<html><head><meta charset="ISO-8859-1"><title>Home</title></head><body><form action="https://www.worldofwarcraft.com/account/login"><input type="password" name="password"><input type="submit"></form><a href="/article.xml">Article</a><link rel="stylesheet" href="/style.css"><script src="/app.js"></script><script>window.topicsArray={elune:{linkString:"/article.xml"}};</script></body></html>',
            "article.xml": '<html><head></head><body><a href="index.xml">Home</a><img src="/missing.gif"></body></html>',
            "status.xml": '<status href="/article.xml?x=1&y=2"/>',
            "style.css": 'body { background:url("/missing.gif"); }',
            "app.js": 'window.testPath = "/article.xml"; window.search = "/__offline/uncollected?kind=search&searchType=" + value; window.protocol = "//";',
            "__offline/compat.js": 'function search(){var exactTopic="/article.xml"; window.location.href = exactTopic;}',
            "info/encyclopedia/scripts/cascade.js": 'function avatar(){document.getElementById("avatarImageContainer").style.backgroundImage = "url(images/icons/"+topicsArray[topicsArray[document.title].parentString].linkString.split(".xml")[0]+".jpg)";}',
            "__offline/missing-image.svg": '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            "__offline/missing.html": '<html><body>missing</body></html>',
            "__offline/empty.js": '',
            "__offline/empty.css": '',
        }
        records = []
        for relative, text in files.items():
            path = site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            data = text.encode("utf-8")
            path.write_bytes(data)
            route = "/" + relative
            kind = "xml" if relative == "status.xml" else ("html" if relative.endswith(".xml") else ("css" if relative.endswith(".css") else ("js" if relative.endswith(".js") else "generated_placeholder")))
            records.append({
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "application/xml" if kind == "xml" else "text/html; charset=UTF-8" if kind == "html" else "text/css" if kind == "css" else "application/javascript" if kind == "js" else "image/svg+xml",
                "kind": kind,
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
        manifest = {
            "schema_version": 1,
            "anchor_timestamp": "20080512210044",
            "route_aliases": {"/": "/index.xml", "/index.html": "/index.xml", "/article": "/article.xml"},
            "origin_index": {
                "www.worldofwarcraft.com/index.xml": "/index.xml",
                "www.worldofwarcraft.com/article.xml": "/article.xml",
                "www.worldofwarcraft.com/style.css": "/style.css",
                "www.worldofwarcraft.com/app.js": "/app.js",
            },
            "files": records,
        }
        manifest_path = base / "offline/build-manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return base, site, manifest_path

    def test_project_prefix_xml_html_and_sensitive_form(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            output = base / "pages"
            result = pages.export_pages(source_site=site, manifest_path=manifest, output=output, workspace_root=base, max_bytes=500_000_000, min_free_bytes=0)
            self.assertEqual(result["base_path"], "/WOW-Encyclopedia-Deployable-Archive/")
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "index.xml.html").is_file())
            page = (output / "index.xml.html").read_text(encoding="utf-8")
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/__offline/pages_runtime.js", page)
            self.assertIn("Content-Security-Policy", page)
            self.assertIn("form-action", page)
            self.assertIn('disabled="disabled"', page)
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/article.xml.html", page)
            self.assertIn("Unofficial historical educational preservation (not affiliated with Blizzard)", page)
            self.assertIn('topicsArray={elune:{linkString:"/WOW-Encyclopedia-Deployable-Archive/article.xml.html"}};', page)
            self.assertNotIn('href="/article.xml"', page)
            app = (output / "app.js").read_text(encoding="utf-8")
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/article.xml.html", app)
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/__offline/uncollected/index.html?kind=search&searchType=", app)
            self.assertIn('"//"', app)
            self.assertIn("/WOW-Encyclopedia-Deployable-Archive/article.xml.html", page)
            self.assertTrue((output / ".nojekyll").is_file())
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertEqual(route_map["routes"]["/article.xml"], "/WOW-Encyclopedia-Deployable-Archive/article.xml.html")
            status = (output / "status.xml").read_text(encoding="utf-8")
            self.assertIn("article.xml.html?x=1&amp;y=2", status)
            import xml.etree.ElementTree as ET
            ET.fromstring(status)
            missing = (output / "__offline/missing.html").read_text(encoding="utf-8")
            self.assertIn("URLSearchParams", missing)
            self.assertTrue((output / "404.html").is_file())
            runtime = (output / "__offline/pages_runtime.js").read_text(encoding="utf-8")
            self.assertIn("HTMLImageElement", runtime)
            self.assertIn("dynamic-image-uncollected", runtime)
            self.assertIn("innerHTML", runtime)
            self.assertIn("mapCssImages: mapCssImages", runtime)
            compat = (output / "__offline/compat.js").read_text(encoding="utf-8")
            self.assertIn("window.__WOWPages.mapHref(exactTopic)", compat)
            cascade = (output / "info/encyclopedia/scripts/cascade.js").read_text(encoding="utf-8")
            self.assertIn("window.__WOWPages.mapCssImages", cascade)
            self.assertIn('String(topicsArray[topicsArray[document.title].parentString].linkString).split("/").pop()', cascade)
            self.assertEqual((site / "index.xml").read_text(encoding="utf-8").split("<meta", 1)[0], "<html><head>")

    def test_existing_output_and_traversal_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            output = base / "pages"
            output.mkdir()
            with self.assertRaises(pages.PagesExportError):
                pages.export_pages(source_site=site, manifest_path=manifest, output=output, workspace_root=base, min_free_bytes=0)
            output.rmdir()
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["files"][0]["route"] = "/../escape.xml"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(pages.PagesExportError):
                pages.export_pages(source_site=site, manifest_path=manifest, output=output, workspace_root=base, min_free_bytes=0)


if __name__ == "__main__":
    unittest.main()
