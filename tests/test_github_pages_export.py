from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402


class GithubPagesExportTests(unittest.TestCase):
    def test_workspace_limit_is_optional_and_disk_reserve_still_applies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(pages, "workspace_size", return_value=15_000_000_000):
                result = pages.export_pages(source_site=site, manifest_path=manifest, output=base / "uncapped", workspace_root=base, min_free_bytes=0)
                self.assertEqual(result["workspace_bytes"], 15_000_000_000)
                with self.assertRaisesRegex(pages.PagesExportError, "workspace budget exceeded"):
                    pages.export_pages(source_site=site, manifest_path=manifest, output=base / "limited", workspace_root=base, max_bytes=14_000_000_000, min_free_bytes=0)
            with mock.patch.object(pages.shutil, "disk_usage", return_value=SimpleNamespace(free=pages.DEFAULT_MIN_FREE_BYTES - 1)):
                with self.assertRaisesRegex(pages.PagesExportError, "disk reserve"):
                    pages.export_pages(source_site=site, manifest_path=manifest, output=base / "low-space", workspace_root=base)

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
            self.assertNotRegex(page, r"<form\b")
            self.assertNotRegex(page, r"<(?:input|select|textarea|button)\b")
            self.assertIn("offline-archive-notice", page)
            self.assertIn("Unavailable", page)
            self.assertNotIn('name="password"', page)
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

    def test_prefixed_account_menu_labels_on_real_home_and_encyclopedia_pages(self) -> None:
        base_path = pages.DEFAULT_BASE_PATH
        for route in ("/index.xml", "/info/encyclopedia/index.xml"):
            with self.subTest(route=route):
                source = (ROOT / "offline/site" / route.lstrip("/")).read_text(
                    encoding="utf-8", errors="replace"
                )
                prefixed = re.sub(
                    r'href="/__offline/missing\.html',
                    'href="' + base_path + '__offline/missing.html',
                    source,
                    flags=re.I,
                )
                derived = pages.historical_exhibits.transform_derived_page(
                    prefixed, route, base_path=base_path
                )
                self.assertIn("Historical: Create Account", derived)
                self.assertIn("Historical: Manage Account", derived)
                self.assertIn("Historical: Retrieve Password", derived)
                self.assertIn(
                    base_path + '__offline/missing.html?source=', derived
                )

    def test_html_prolog_bom_is_removed_before_runtime_injection(self) -> None:
        source = (
            "<!-- derived comment -->\n\ufeff<!doctype html><html><head>"
            "<title>Legacy</title></head><body>literal\ufeffbody</body></html>"
        )
        normalized = pages.normalize_html_prolog(source)
        self.assertNotIn("\ufeff<!doctype", normalized.casefold())
        self.assertIn("literal\ufeffbody", normalized)
        derived = pages.inject_html_runtime(
            normalized,
            base_path=pages.DEFAULT_BASE_PATH,
            source_sha="fixture",
        )
        head_start = derived.casefold().index("<head")
        head_end = derived.casefold().index("</head>")
        csp = derived.index('http-equiv="Content-Security-Policy"')
        self.assertLess(head_start, csp)
        self.assertLess(csp, head_end)
        self.assertIn("literal\ufeffbody", derived)

    def test_runtime_maps_dynamic_document_write_image_with_spaces(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable for the runtime regression")
        runtime = pages.runtime_js(pages.DEFAULT_BASE_PATH, {})
        driver = f"""
const window = {{
    location: {{
        origin: "https://pages.test",
        href: "https://pages.test{pages.DEFAULT_BASE_PATH}info/races/dancing.html"
    }},
    Element: undefined,
    CSSStyleDeclaration: undefined,
    HTMLImageElement: undefined
}};
const writes = [];
const document = {{
    baseURI: window.location.href,
    write: function (value) {{ writes.push(String(value)); }},
    writeln: function (value) {{ writes.push(String(value)); }},
    addEventListener: function () {{}},
    querySelector: function () {{ return null; }},
    images: []
}};
globalThis.location = window.location;
globalThis.fetch = function () {{
    return Promise.resolve({{ok: true, json: function () {{ return Promise.resolve({{routes: {{}}}}); }}}});
}};
{runtime}
const Menu2 = ["Player Interaction"];
document.write('<img src = "/shared/wow-com/images/subnav/icon_' + Menu2[0].toLowerCase() + '.jpg">');
process.stdout.write(writes[0]);
"""
        result = subprocess.run(
            [node, "-e", driver],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            'src = "/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?',
            result.stdout,
        )
        self.assertIn("reason=dynamic-image-uncollected", result.stdout)
        self.assertNotIn(
            'src = "/shared/wow-com/images/subnav/icon_player interaction.jpg"',
            result.stdout,
        )

    def test_real_audited_flash_codebase_attributes_are_renamed_by_source_page(self) -> None:
        cases = {
            "info/items/socketeditems.html": 5,
            "visa/index.html": 1,
            "info/races/dancing.html": 1,
        }
        recorder = pages.mirror.ReferenceRecorder("/flash-audit.html", "http://www.worldofwarcraft.com/flash-audit.html")
        total = 0
        for relative, expected in cases.items():
            source = (ROOT / "offline/site" / relative).read_text(encoding="utf-8", errors="replace")
            rewritten = pages.rename_flash_codebase_metadata(source, recorder=recorder)
            self.assertEqual(rewritten.count("data-archive-codebase"), expected, relative)
            self.assertEqual(len(re.findall(r"(?<!data-archive-)\bcodebase\s*=\s*\"http://", rewritten, re.I)), 0, relative)
            total += expected
        self.assertEqual(total, 7)
        self.assertEqual(recorder.counts["flash_codebase_renamed"], 7)

    def test_flash_codebase_export_is_token_scoped_and_traceable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            flash = site / "flash.html"
            cab_a = "http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0"
            cab_b = "http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,29,0"
            cab_c = "https://download.adobe.com/shockwave/cabs/flash/swflash.cab"
            objects = "".join(f'<object codebase="{value}" data="movie.swf"></object>' for value in [cab_a] * 5 + [cab_b, cab_c])
            flash.write_text(
                "<html><body>"
                + objects
                + '<object codebase="/ordinary/object.cab" data="ordinary.swf"></object>'
                + '<object codebase="https://evilmacromedia.com/shockwave/cabs/flash/swflash.cab" data="evil.swf"></object>'
                + '<p>codebase="' + cab_a + '"</p>'
                + "<script>var literal = 'codebase=\"" + cab_a + "\"';</script>"
                + "</body></html>",
                encoding="utf-8",
            )
            data = flash.read_bytes()
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append({
                "route": "/flash.html",
                "output_path": "offline/site/flash.html",
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com/flash.html",
            })
            payload["origin_index"]["www.worldofwarcraft.com/flash.html"] = "/flash.html"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/flash.html").read_text(encoding="utf-8")
            self.assertEqual(exported.count("data-archive-codebase"), 7)
            self.assertEqual(exported.count('codebase="/ordinary/object.cab"'), 1)
            self.assertIn("codebase=\"https://evilmacromedia.com/shockwave/cabs/flash/swflash.cab\"", exported)
            self.assertIn('codebase=\"' + cab_a + '\"', exported)
            self.assertIn("var literal", exported)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == "/flash.html")
            self.assertEqual(item["reference_counts"]["flash_codebase_renamed"], 7)

            raw_negative = (
                "<script>var markup = '<object codebase=\"" + cab_a + "\">';</script>"
                + '<p>codebase="' + cab_a + '"</p>'
                + '<object codebase="/ordinary/object.cab"></object>'
            )
            self.assertEqual(pages.rename_flash_codebase_metadata(raw_negative), raw_negative)
            self.assertNotIn("data-archive-codebase", raw_negative)

    def test_flash_codebase_ignores_installer_text_in_other_attributes(self) -> None:
        cab = "http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab"
        title = "note codebase='" + cab + "'"
        source = '<object title="' + title + '" codebase="' + cab + '"></object>'
        rewritten = pages.rename_flash_codebase_metadata(source)
        self.assertIn('title="' + title + '"', rewritten)
        self.assertIn('data-archive-codebase="' + cab + '"', rewritten)
        self.assertEqual(rewritten, pages.rename_flash_codebase_metadata(rewritten))

    def test_generated_404_uses_archive_missing_copy_and_keeps_runtime_marker(self) -> None:
        page = pages.generated_404(pages.DEFAULT_BASE_PATH)
        self.assertIn("<title>Page not in this archive</title>", page)
        self.assertIn("This page was not saved in the available archive.", page)
        self.assertNotIn("will not fetch it from the Internet", page)
        self.assertIn('<meta name="offline-pages-404" content="true">', page)
        self.assertIn("URLSearchParams", page)
        self.assertIn(pages.DEFAULT_BASE_PATH + "__offline/pages_runtime.js", page)

    def test_story_exhibit_disables_only_retired_form_initializers(self) -> None:
        route = "/community/stories/submit.html"
        source = (ROOT / "offline/site" / route.lstrip("/")).read_text(
            encoding="utf-8", errors="replace"
        )
        inert = pages.disable_sensitive_forms(source, route=route)
        derived = pages.historical_exhibits.transform_derived_page(
            inert, route, base_path=pages.DEFAULT_BASE_PATH
        )
        self.assertNotIn(
            'nameopt(document.getElementById("displayInformation"))', derived
        )
        self.assertNotIn(
            "circumsize(document.getElementById('story'),3000)", derived
        )
        self.assertIn("p7_eqCols2_10.js", derived)
        self.assertIn("function count(", derived)
        self.assertIn("searchCall()", derived)
        self.assertIn("buildtopnav.js", derived)

    def test_iframe_fallback_urls_remain_local_on_raw_text_parsers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            homepage = site / "index.xml"
            text = homepage.read_text(encoding="utf-8").replace(
                "</body>",
                '<iframe src="https://ads.example/frame"><script>document.write(\'<a href="https://ads.example/click"><img src="https://ads.example/pixel.jpg"></a>\');</script><noscript><a href="https://ads.example/click"><img src="https://ads.example/pixel.jpg"></a></noscript></iframe></body>',
            )
            data = text.encode("utf-8")
            homepage.write_bytes(data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"][0]["derived_sha256"] = hashlib.sha256(data).hexdigest()
            payload["files"][0]["derived_length"] = len(data)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(source_site=site, manifest_path=manifest, output=base / "pages", workspace_root=base, max_bytes=500_000_000, min_free_bytes=0)
            exported = (base / "pages/index.xml.html").read_text(encoding="utf-8")
            self.assertNotIn('href="https://ads.example', exported)
            self.assertNotIn('src="https://ads.example', exported)
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg', exported)
            self.assertEqual(homepage.read_bytes(), data)

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

    def test_form_token_pass_handles_external_controls_and_preserves_search(self) -> None:
        text = """<div>
<form id=biz method=post action=/submit onsubmit="directsubmit()">
<input type=password name=ssn value=SECRET onclick="undisable()"><input type=hidden name=token value=SECRET>
<select name=region><option value=US>US</option><option value=EU selected>EU</option></select>
<textarea name=comment onkeyup="submit()">visible comment</textarea>
<button type=submit onclick="submit()">Send</button>
<input type=image src=/send.gif alt="Send" onclick="biz.submit()">
<input type=file name=upload>
</form><input form=biz type=text value="outside" onclick="directsubmit()">
<form name=topSearch onsubmit="return searchCall()"><input name=searchQuery value="keep"></form>
<form id=form3><table><tr><td>layout</td></tr></table>
</div>"""
        output = pages.disable_sensitive_forms(text, route="/contests/05-12-giveaway/contest.html")
        self.assertEqual(len(re.findall(r"<form\b", output, re.I)), 1)
        self.assertNotIn('<form id="biz"', output)
        self.assertNotRegex(output, r"<(?:select|textarea|button)\b")
        self.assertNotRegex(output, r'<input\b[^>]*\b(?:password|hidden|type="image")')
        self.assertRegex(output, r"<form\b[^>]*\bname=topSearch\b")
        self.assertIn("offline-archive-notice", output)
        self.assertIn("Unavailable", output)
        self.assertIn('data-offline-control="select">EU</span>', output)
        self.assertIn("File upload unavailable in archive", output)
        self.assertIn('<img src="/send.gif" alt="Send" />', output)
        self.assertIn("visible comment", output)
        self.assertNotIn("SECRET", output)
        self.assertNotIn("directsubmit", output)
        self.assertNotIn("undisable", output)
        self.assertNotIn("onclick", output)
        search = pages.disable_sensitive_forms(
            '<form name="searchForm1"><input type="hidden" name="gameId" value="11"><input type="submit" value="Search"></form>',
            route="/policy/index.html",
        )
        self.assertIn('<form name="searchForm1">', search)
        self.assertIn('type="hidden"', search)
        self.assertIn('type="submit"', search)

    def test_local_filter_forms_require_route_and_handler_evidence(self) -> None:
        local_filter_cases = {
            "/info/basics/factions/arathi/index.html": "info/basics/factions/arathi/index.html",
            "/info/basics/factions/argent/index.html": "info/basics/factions/argent/index.html",
            "/info/basics/factions/badgesofjustice/badges-of-justice2.html": "info/basics/factions/badgesofjustice/badges-of-justice2.html",
            "/info/basics/factions/warsong/index.html": "info/basics/factions/warsong/index.html",
            "/pvp/rewards-arena-class-armor.html": "pvp/rewards-arena-class-armor.html",
            "/pvp/rewards-class-armor.html": "pvp/rewards-class-armor.html",
            "/pvp/rewards-vindicators-armor.html": "pvp/rewards-vindicators-armor.html",
            "/pvp/rewards-weapons.html": "pvp/rewards-weapons.html",
        }
        for route, relative in local_filter_cases.items():
            source = (ROOT / "offline/site" / relative).read_text(encoding="utf-8")
            output = pages.disable_sensitive_forms(source, route=route)
            self.assertEqual(output.count("offline-archive-notice"), 0, route)
            self.assertGreaterEqual(len(re.findall(r"<form\b", output, re.I)), 2, route)
            self.assertGreaterEqual(len(re.findall(r"<select\b", output, re.I)), 2, route)

        # Route and handler evidence are both required; an anonymous unknown
        # form with the same-looking select must remain inert.
        unknown = pages.disable_sensitive_forms(
            '<form><select name="bracketSelector" onchange="levelBracket=this.form.bracketSelector.options[this.form.bracketSelector.selectedIndex].value; reloadTable();"><option>One</option></select></form>',
            route="/info/basics/factions/unknown/index.html",
        )
        self.assertNotRegex(unknown, r"<form\b")
        self.assertNotRegex(unknown, r"<select\b")
        self.assertIn("offline-archive-notice", unknown)

        same_route_with_extra_submit = pages.disable_sensitive_forms(
            '<form><select name="bracketSelector" onchange="levelBracket=this.form.bracketSelector.options[this.form.bracketSelector.selectedIndex].value; reloadTable(); directsubmit();"><option>One</option></select></form>',
            route="/pvp/rewards-class-armor.html",
        )
        self.assertNotRegex(same_route_with_extra_submit, r"<form\b")
        self.assertNotRegex(same_route_with_extra_submit, r"<select\b")
        self.assertIn("offline-archive-notice", same_route_with_extra_submit)
        post_with_filter = pages.disable_sensitive_forms(
            '<form method="post" action="/submit"><select name="bracketSelector" onchange="levelBracket=this.form.bracketSelector.options[this.form.bracketSelector.selectedIndex].value; reloadTable();"><option>One</option></select></form>',
            route="/pvp/rewards-class-armor.html",
        )
        self.assertNotRegex(post_with_filter, r"<form\b")
        self.assertNotRegex(post_with_filter, r"<select\b")

    def test_wrath_thumbnail_rewrite_is_strict_and_route_scoped(self) -> None:
        source = (ROOT / "offline/site/wrath/js/thumbnailslayout.js").read_text(encoding="utf-8")
        rewritten = pages.rewrite_wrath_thumbnails_script(source)
        self.assertIn("URLSearchParams", rewritten)
        self.assertEqual(rewritten.count("eval("), 0)
        self.assertIn("queryParams.getAll(\"s\")", rewritten)
        self.assertIn("queryTotalPages = actualPages", rewritten)
        self.assertIn("currentPage = queryCurrentPage", rewritten)
        with self.assertRaises(pages.PagesExportError):
            pages.rewrite_wrath_thumbnails_script(source.replace('query.split("s=")', 'query.split("page=")'))


if __name__ == "__main__":
    unittest.main()
