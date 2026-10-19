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
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402


class GithubPagesExportTests(unittest.TestCase):
    def test_workspace_limit_is_optional_and_disk_reserve_still_applies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(pages, "workspace_size", side_effect=AssertionError("workspace walk")) as walk:
                with mock.patch.object(pages.shutil, "disk_usage", return_value=SimpleNamespace(free=10**15)) as disk:
                    result = pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "uncapped",
                        workspace_root=base,
                        max_bytes=None,
                        min_free_bytes=0,
                    )
            self.assertIsNone(result["workspace_bytes"])
            walk.assert_not_called()
            self.assertEqual(disk.call_count, 2)
            with mock.patch.object(pages, "workspace_size", return_value=0) as walk:
                with self.assertRaisesRegex(pages.PagesExportError, "workspace budget exceeded"):
                    pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "limited",
                        workspace_root=base,
                        max_bytes=1,
                        min_free_bytes=0,
                    )
            walk.assert_called_once()
            with mock.patch.object(pages, "workspace_size", side_effect=AssertionError("workspace walk")):
                with mock.patch.object(
                    pages.shutil,
                    "disk_usage",
                    side_effect=[
                        SimpleNamespace(free=10**15),
                        SimpleNamespace(free=pages.DEFAULT_MIN_FREE_BYTES - 1),
                    ],
                ):
                    with self.assertRaisesRegex(pages.PagesExportError, "budget exceeded after export"):
                        pages.export_pages(
                            source_site=site,
                            manifest_path=manifest,
                            output=base / "low-space-after",
                            workspace_root=base,
                            max_bytes=None,
                            min_free_bytes=pages.DEFAULT_MIN_FREE_BYTES,
                        )

    def test_finite_workspace_limit_rejects_after_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            records = json.loads(manifest.read_text(encoding="utf-8"))["files"]
            max_bytes = pages.output_estimate(records) + 1
            with mock.patch.object(pages, "workspace_size", side_effect=[0, max_bytes]) as walk:
                with mock.patch.object(pages.shutil, "disk_usage", return_value=SimpleNamespace(free=10**15)):
                    with self.assertRaisesRegex(pages.PagesExportError, "budget exceeded after export"):
                        pages.export_pages(
                            source_site=site,
                            manifest_path=manifest,
                            output=base / "after-cap",
                            workspace_root=base,
                            max_bytes=max_bytes,
                            min_free_bytes=0,
                        )
            self.assertEqual(walk.call_count, 2)
            self.assertFalse((base / "after-cap").exists())

    def test_workspace_limit_disk_reserve_still_applies_before_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            with mock.patch.object(pages.shutil, "disk_usage", return_value=SimpleNamespace(free=pages.DEFAULT_MIN_FREE_BYTES - 1)):
                with self.assertRaisesRegex(pages.PagesExportError, "disk reserve"):
                    pages.export_pages(
                        source_site=site,
                        manifest_path=manifest,
                        output=base / "low-space",
                        workspace_root=base,
                        max_bytes=None,
                    )

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

    def test_wrath_resource_base_remains_directory_while_navigation_uses_index(self) -> None:
        prefix = pages.DEFAULT_BASE_PATH
        for resource_root in ("/wrath/", prefix + "wrath/"):
            with self.subTest(resource_root=resource_root), tempfile.TemporaryDirectory() as tmp:
                base, site, manifest = self._fixture(Path(tmp))
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                entries = {
                    "wrath/index.html": (
                        f'<html><head><title>Wrath</title></head><body><script>var roothost = "{resource_root}"; '
                        'window.navigation = "/wrath/"; window.imageHref = roothost + "images/layout/frame.svg";'
                        '</script></body></html>', "html", "text/html"),
                    "wrath/images/layout/frame.svg": (
                        '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"></svg>', "image", "image/svg+xml"),
                }
                for relative, (text, kind, mime) in entries.items():
                    data = text.encode("utf-8")
                    target = site / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    payload["files"].append({"route": "/" + relative,
                        "output_path": "offline/site/" + relative,
                        "derived_sha256": hashlib.sha256(data).hexdigest(),
                        "derived_length": len(data), "kind": kind, "mime": mime,
                        "source_base_url": "http://www.worldofwarcraft.com/" + relative})
                payload["route_aliases"]["/wrath/"] = "/wrath/index.html"
                payload["origin_index"]["www.worldofwarcraft.com/wrath/"] = "/wrath/index.html"
                manifest.write_text(json.dumps(payload), encoding="utf-8")
                output = base / "pages"
                pages.export_pages(source_site=site, manifest_path=manifest, output=output,
                                   workspace_root=base, min_free_bytes=0)
                derived = (output / "wrath/index.html").read_text(encoding="utf-8")
                root = re.search(r'var roothost = "([^"]+)"', derived).group(1)
                self.assertEqual(root, prefix + "wrath/")
                self.assertIn('window.navigation = "' + prefix + 'wrath/index.html"', derived)
                resource = root + "images/layout/frame.svg"
                self.assertEqual((output / resource.removeprefix(prefix)).read_text(encoding="utf-8"),
                                 entries["wrath/images/layout/frame.svg"][0])
                self.assertNotIn("index.htmlimages", derived)

    def test_ptr_export_path_uses_manifest_capture_and_generated_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source = """<!doctype html><html><head><title>WoW -> Public Test Realm</title></head><body>
<script>document.write('legacy operational control')</script>
<form action=\"http://test.worldofwarcraft.com/us/copy/character-copy.html\"><input name=\"copy\"></form>
<p>The World of Warcraft Public Test Realms (PTRs) are used to test upcoming content patches in a public environment before they are released to live realms.</p>
</body></html>""".encode("utf-8")
            ptr = site / "ptr/index.html"
            ptr.parent.mkdir(parents=True, exist_ok=True)
            ptr.write_bytes(source)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append(
                {
                    "route": "/ptr/index.html",
                    "output_path": "offline/site/ptr/index.html",
                    "derived_sha256": hashlib.sha256(source).hexdigest(),
                    "derived_length": len(source),
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "role": "historical_ptr_exhibit",
                    "actual_timestamp": "20061110075927",
                    "source_base_url": "http://www.worldofwarcraft.com/ptr/",
                }
            )
            payload["route_aliases"].update(
                {"/ptr": "/ptr/index.html", "/ptr/": "/ptr/index.html"}
            )
            payload["origin_index"]["www.worldofwarcraft.com/ptr/"] = "/ptr/index.html"
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            output = base / "pages"
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (output / "ptr/index.html").read_text(encoding="utf-8")
            prefix = pages.DEFAULT_BASE_PATH
            self.assertIn(
                "<title>World of Warcraft Public Test Realm — Historical Exhibit</title>",
                exported,
            )
            self.assertIn("Selected archival capture: 2006-11-10 07:59:27 UTC.", exported)
            self.assertIn(prefix + "index.html", exported)
            self.assertNotIn(prefix + "index.xml", exported)
            self.assertNotRegex(exported, r"<\s*(?:form|input|select|textarea|button)\b")
            self.assertNotIn("test.worldofwarcraft.com", exported)
            self.assertNotIn("character-copy", exported.casefold())
            route_map = json.loads(
                (output / "__offline/route-map.json").read_text(encoding="utf-8")
            )
            self.assertIn("/ptr", route_map["aliases"])
            self.assertIn(prefix + "ptr/index.html", route_map["aliases"]["/ptr/"])

    def test_navtree_community_fix_is_derived_and_idempotent(self) -> None:
        source_path = ROOT / "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js"
        frozen = source_path.read_bytes()
        source = frozen.decode("utf-8", errors="replace")
        derived, changed = pages.rewrite_navtree_community_ids(source)
        self.assertTrue(changed)
        self.assertRegex(derived, r'Menu1_6=new Array\([^\r\n]*?,"/community/","",11,')
        self.assertIn('Menu1_6_10=new Array(bulletImg+"Fan Wallpapers"', derived)
        self.assertIn('Menu1_6_11=new Array(bulletImg+"Fan Sites"', derived)
        self.assertEqual(pages.rewrite_navtree_community_ids(derived), (derived, False))
        self.assertEqual(source_path.read_bytes(), frozen)

    def test_navtree_community_fix_runs_in_export_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source_path = ROOT / "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js"
            frozen = source_path.read_bytes()
            nav = site / "shared/wow-com/includes-client/navtree-main.js"
            nav.parent.mkdir(parents=True, exist_ok=True)
            nav.write_bytes(frozen)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append({
                "route": "/shared/wow-com/includes-client/navtree-main.js",
                "output_path": "offline/site/shared/wow-com/includes-client/navtree-main.js",
                "derived_sha256": hashlib.sha256(frozen).hexdigest(),
                "derived_length": len(frozen),
                "mime": "application/javascript",
                "kind": "js",
                "source_base_url": "http://www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js",
            })
            for route in ("/downloads/wallpapers/fan-wallpapers/index.html", "/community/fansites.html"):
                target = site / route.lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target_data = b"<html><body>fan target</body></html>"
                target.write_bytes(target_data)
                payload["files"].append({
                    "route": route,
                    "output_path": "offline/site/" + route.lstrip("/"),
                    "derived_sha256": hashlib.sha256(target_data).hexdigest(),
                    "derived_length": len(target_data),
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "source_base_url": "http://www.worldofwarcraft.com" + route,
                })
                payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            payload["route_aliases"]["/downloads/wallpapers/fan-wallpapers/"] = "/downloads/wallpapers/fan-wallpapers/index.html"
            payload["origin_index"]["www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js"] = "/shared/wow-com/includes-client/navtree-main.js"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/shared/wow-com/includes-client/navtree-main.js").read_text(encoding="utf-8")
            self.assertRegex(exported, r'Menu1_6=new Array\([^\r\n]*?11,')
            self.assertIn('Menu1_6_10=new Array(bulletImg+"Fan Wallpapers"', exported)
            self.assertIn('Menu1_6_11=new Array(bulletImg+"Fan Sites"', exported)
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/downloads/wallpapers/fan-wallpapers/', exported)
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/community/fansites.html', exported)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == "/shared/wow-com/includes-client/navtree-main.js")
            self.assertIn("Menu1_6_10 -> Menu1_6_11", item["derivation_reason"])
            self.assertEqual(nav.read_bytes(), frozen)

    def test_pvp_mini_site_rewrite_matches_real_source_after_mirror(self) -> None:
        source_path = ROOT / ".scratch/offline-navigation-20261015-v7c/site/pvp/flash-rewards"
        if not source_path.is_file():
            self.skipTest("v7c PvP source is not present in this checkout")
        frozen = source_path.read_bytes()
        source = frozen.decode("utf-8", errors="replace")
        route = "/pvp/flash-rewards/"
        base_url = "http://www.worldofwarcraft.com" + route
        base_path = pages.DEFAULT_BASE_PATH
        placeholder_routes = {
            route_name: base_path + route_name.lstrip("/")
            for route_name in (
                "/__offline/missing-image.svg",
                "/__offline/empty.js",
                "/__offline/empty.css",
                "/__offline/missing.html",
            )
        }
        localizer = pages.PagesLocalizer(
            route_to_static=placeholder_routes,
            aliases={},
            origin_index={},
            base_path=base_path,
        )
        recorder = pages.mirror.ReferenceRecorder(route, base_url)
        mirrored = pages.mirror.rewrite_html(
            source,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
            source_sha=hashlib.sha256(frozen).hexdigest(),
            compat_assets=[],
        )
        derived, changed = pages.rewrite_pvp_mini_site(
            mirrored,
            route=route,
            base_path=base_path,
        )
        self.assertTrue(changed)
        self.assertIn("ss-border-top-bg.gif", derived)
        self.assertIn("ss-border-left.gif", derived)
        self.assertIn("offline-pvp-mini-nav", derived)
        self.assertIn(base_path, derived)
        self.assertIn(base_path + "info/index.html", derived)
        self.assertIn("2007 PvP Mini Site", derived)
        self.assertIn('data-archive-flash-unavailable="true"', derived)
        self.assertIn("intro.swf", derived)
        self.assertIn("has not been recovered", derived)
        self.assertNotIn("<!---Subnav----->", derived)
        self.assertNotIn("printSubNav2", derived)
        self.assertNotIn("Menu1", derived)
        self.assertNotIn("document.write", derived)
        self.assertNotIn("mailto:", derived.casefold())
        self.assertNotRegex(derived, r"<script\b")
        self.assertNotRegex(derived, r"<(?:object|embed)\b")
        self.assertNotIn("getflashplayer", derived.casefold())
        self.assertEqual(source_path.read_bytes(), frozen)

        for candidate_route, candidate in (
            ("/other/route/", source),
            (route, source.replace("</object>", "", 1)),
            (route, source.replace("<!---Subnav----->", "", 1)),
        ):
            unchanged, candidate_changed = pages.rewrite_pvp_mini_site(
                candidate,
                route=candidate_route,
                base_path=base_path,
            )
            self.assertFalse(candidate_changed)
            self.assertEqual(unchanged, candidate)

    def test_pvp_mini_site_rewrite_runs_in_pipeline_and_records_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            source = """<html><head><title>World of Warcraft PvP Mini Site</title></head>
<body><div id="static-frame" style="background:url('/shared/screenshots/borders/ss-border-top-bg.gif')">
<img src="/shared/screenshots/borders/ss-border-left.gif" alt="frame">
<!---Subnav----->
<script>var Menu1 = []; document.write('<a href=\"mailto:old@example.test\">old</a>');</script>
<center><table><tr><td>
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,0,0" id="intro">
<param name="movie" value="intro.swf"><embed src="intro.swf" pluginspage="http://www.macromedia.com/go/getflashplayer"></object>
</td></tr></table></center>
<script>document.write('mailto:old@example.test');</script></div></body></html>""".encode("utf-8")
            source_path = site / "pvp/flash-rewards"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_bytes(source)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            route = "/pvp/flash-rewards/"
            payload["files"].append({
                "route": route,
                "output_path": "offline/site/pvp/flash-rewards",
                "derived_sha256": hashlib.sha256(source).hexdigest(),
                "derived_length": len(source),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/pvp/flash-rewards/index.html").read_text(encoding="utf-8")
            self.assertIn('id="static-frame"', exported)
            self.assertIn(pages.DEFAULT_BASE_PATH, exported)
            self.assertIn(pages.DEFAULT_BASE_PATH + "info/index.html", exported)
            self.assertIn("2007 PvP Mini Site", exported)
            self.assertIn('data-archive-flash-unavailable="true"', exported)
            self.assertNotIn("mailto:", exported.casefold())
            self.assertNotRegex(exported, r"<(?:object|embed)\b")
            self.assertNotIn("getflashplayer", exported.casefold())
            self.assertEqual(result["stats"]["pvp_mini_site_repaired"], 1)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == route)
            self.assertIn("derived PvP mini-site repair", item["derivation_reason"])
            self.assertEqual(source_path.read_bytes(), source)

    def test_ssotd_clock_uses_recorded_capture_and_preserves_gallery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            page = site / "downloads/ssotd/index.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            source = """<html><body><span id="pageNum"></span><div id="galleryPictures"></div>
<script>
startDate = 12671;
function linkHere() { document.location.href = "#" + (currentShotNumber - nowViewing); }
shotsPerPage = 12;
function ThumbSize(size) { shotsPerPage = (size=="sixteen")?16:(size=="twelve")?12:9; }
function checkRequestHeader()
{
    xmlServerDate = new Date(xmlTimeVerification.getResponseHeader("Date"));
    currentShotNumber = Math.floor(Math.floor(Math.floor(Math.floor(eval(xmlServerDate.getTime())/1000)/60)/60)/24) - startDate;
    addshots("/downloads/ssotd/images/screens","ss",currentShotNumber);
}
var xmlTimeVerification = new XMLHttpRequest();
xmlTimeVerification.onreadystatechange = checkRequestHeader;
xmlTimeVerification.open("HEAD","anachronos.xml",true);
xmlTimeVerification.send(null);
</script></body></html>""".replace("\n", "\r\n")
            data = source.encode("utf-8")
            page.write_bytes(data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append({
                "route": "/downloads/ssotd/index.html",
                "output_path": "offline/site/downloads/ssotd/index.html",
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com/downloads/ssotd/",
                "actual_timestamp": "20080512204328",
            })
            payload["origin_index"]["www.worldofwarcraft.com/downloads/ssotd/index.html"] = "/downloads/ssotd/index.html"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/downloads/ssotd/index.html").read_text(encoding="utf-8")
            self.assertIn("currentShotNumber = 1340;", exported)
            self.assertIn(
                'addshots("/WOW-Encyclopedia-Deployable-Archive/downloads/ssotd/images/screens","ss",currentShotNumber);',
                exported,
            )
            self.assertNotIn("xmlTimeVerification", exported)
            self.assertNotIn('open("HEAD"', exported)
            self.assertIn('document.location.href = "#" + (currentShotNumber - nowViewing);', exported)
            self.assertIn('shotsPerPage = 12;', exported)
            self.assertIn('(size=="sixteen")?16:(size=="twelve")?12:9', exported)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == "/downloads/ssotd/index.html")
            self.assertIn("actual_timestamp 20080512204328 UTC", item["derivation_reason"])
            self.assertIn("does not verify the raw screenshot total", item["derivation_reason"])
            self.assertEqual(page.read_bytes(), data)

    def test_ssotd_thumbnail_fallback_prefers_thumb_when_verified(self) -> None:
        base = pages.DEFAULT_BASE_PATH
        full_missing_thumb = "/downloads/ssotd/images/screens/ss1314.jpg"
        full_with_thumb = "/downloads/ssotd/images/screens/ss1336.jpg"
        thumb_with_full = "/downloads/ssotd/images/screens/ss1336-thumb.jpg"
        route_to_static = {
            full_missing_thumb: base + full_missing_thumb.lstrip("/"),
            full_with_thumb: base + full_with_thumb.lstrip("/"),
            thumb_with_full: base + thumb_with_full.lstrip("/"),
        }
        source = """function printPages() {
    thumbnail = shotList[n].replace(".jpg","-thumb.jpg");
    document.getElementById("galleryPictures").innerHTML = thumbnail;
}"""
        rewritten, changed, fallbacks = pages.rewrite_ssotd_thumbnail_fallback(
            source,
            route_to_static=route_to_static,
            base_path=base,
        )
        self.assertTrue(changed)
        self.assertEqual(
            fallbacks,
            {route_to_static[full_missing_thumb]: route_to_static[full_missing_thumb]},
        )
        self.assertIn("__WOW_SSOTD_THUMB_FALLBACK[shotList[n]] || shotList[n].replace", rewritten)
        self.assertIn(route_to_static[full_missing_thumb], rewritten)
        self.assertNotIn(route_to_static[full_with_thumb], rewritten)
        self.assertEqual(
            pages.rewrite_ssotd_thumbnail_fallback(
                rewritten,
                route_to_static=route_to_static,
                base_path=base,
            ),
            (rewritten, False, fallbacks),
        )

    def test_ssotd_thumbnail_fallback_runs_in_export_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            script = site / "new-hp/js/ssotd-screenie.js"
            script.parent.mkdir(parents=True, exist_ok=True)
            script_data = b'function printPages(){\n    thumbnail = shotList[n].replace(".jpg","-thumb.jpg");\n}'
            script.write_bytes(script_data)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["files"].append({
                "route": "/new-hp/js/ssotd-screenie.js",
                "output_path": "offline/site/new-hp/js/ssotd-screenie.js",
                "derived_sha256": hashlib.sha256(script_data).hexdigest(),
                "derived_length": len(script_data),
                "mime": "application/javascript",
                "kind": "js",
                "source_base_url": "http://www.worldofwarcraft.com/new-hp/js/ssotd-screenie.js",
            })
            full_missing_thumb = "/downloads/ssotd/images/screens/ss1314.jpg"
            full_with_thumb = "/downloads/ssotd/images/screens/ss1336.jpg"
            thumb_with_full = "/downloads/ssotd/images/screens/ss1336-thumb.jpg"
            for route in (full_missing_thumb, full_with_thumb, thumb_with_full):
                image = site / route.lstrip("/")
                image.parent.mkdir(parents=True, exist_ok=True)
                image_data = b"fake-jpeg-" + route.encode("ascii")
                image.write_bytes(image_data)
                payload["files"].append({
                    "route": route,
                    "output_path": "offline/site/" + route.lstrip("/"),
                    "derived_sha256": hashlib.sha256(image_data).hexdigest(),
                    "derived_length": len(image_data),
                    "mime": "image/jpeg",
                    "kind": "image",
                    "source_base_url": "http://www.worldofwarcraft.com" + route,
                })
                payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/new-hp/js/ssotd-screenie.js").read_text(encoding="utf-8")
            full_static = pages.DEFAULT_BASE_PATH + full_missing_thumb.lstrip("/")
            self.assertIn(full_static, exported)
            self.assertIn("__WOW_SSOTD_THUMB_FALLBACK[shotList[n]] ||", exported)
            self.assertIn('shotList[n].replace(".jpg","-thumb.jpg")', exported)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            item = next(row for row in provenance["files"] if row.get("route") == "/new-hp/js/ssotd-screenie.js")
            self.assertIn("1 shot(s)", item["derivation_reason"])

    def test_archived_news_compatibility_aliases_rewrite_only_verified_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            targets = {
                "/info/basics/dailyquests.html": "dailyquests",
                "/info/basics/titles.html": "titles",
                "/info/basics/benice.html": "benice",
                "/info/credits.html": "credits",
                "/info/items/armorsets/index.html": "armorsets",
            }
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            requested_routes = {
                "/info/basics/dailyquests.shtml": "/info/basics/dailyquests.html",
                "/info/basics/titles.shtml": "/info/basics/titles.html",
                "/info/basics/benice.shtml": "/info/basics/benice.html",
                "/info/credits.shtml": "/info/credits.html",
                "/info/info/items/armorsets/": "/info/items/armorsets/index.html",
            }
            links = []
            for route, label in targets.items():
                target = site / route.lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                data = f"<html><head><title>{label}</title></head><body>{label}</body></html>".encode("utf-8")
                target.write_bytes(data)
                payload["files"].append({
                    "route": route,
                    "output_path": "offline/site/" + route.lstrip("/"),
                    "derived_sha256": hashlib.sha256(data).hexdigest(),
                    "derived_length": len(data),
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "source_base_url": "http://www.worldofwarcraft.com" + route,
                })
                payload["origin_index"]["www.worldofwarcraft.com" + route] = route
                requested = "http://www.worldofwarcraft.com" + next(
                    old_route for old_route, canonical in requested_routes.items() if canonical == route
                )
                links.append(
                    '<a href="/__offline/missing.html?requested=' + quote(requested, safe="") + '&reason=invalid-overlay-or-uncollected-site-resource">' + label + "</a>"
                )
            payload["route_aliases"]["/info/items/armorsets/"] = "/info/items/armorsets/index.html"
            archived = site / "archived.html"
            archived_data = ("<html><body>" + "".join(links) + "</body></html>").encode("utf-8")
            archived.write_bytes(archived_data)
            payload["files"].append({
                "route": "/archived.html",
                "output_path": "offline/site/archived.html",
                "derived_sha256": hashlib.sha256(archived_data).hexdigest(),
                "derived_length": len(archived_data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com/archived.html",
            })
            payload["origin_index"]["www.worldofwarcraft.com/archived.html"] = "/archived.html"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exported = (base / "pages/archived.html").read_text(encoding="utf-8")
            for route in targets:
                self.assertIn(pages.DEFAULT_BASE_PATH + route.lstrip("/"), exported, route)
            self.assertNotIn("__offline/missing.html?requested=", exported)
            route_map = json.loads((base / "pages/__offline/route-map.json").read_text(encoding="utf-8"))
            for alias in (
                "/info/basics/dailyquests.shtml",
                "/info/basics/titles.shtml",
                "/info/basics/benice.shtml",
                "/info/credits.shtml",
            ):
                self.assertEqual(route_map["routes"][alias], pages.DEFAULT_BASE_PATH + alias.lstrip("/"))
                self.assertTrue((base / "pages" / alias.lstrip("/")).is_file())
            armorsets_alias = "/info/info/items/armorsets/"
            self.assertEqual(
                route_map["routes"][armorsets_alias],
                pages.DEFAULT_BASE_PATH + "info/info/items/armorsets/index.html",
            )
            self.assertTrue((base / "pages/info/info/items/armorsets/index.html").is_file())

    def test_wrath_wallpapers_alias_requires_double_slash_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            route = "/wrath//wallpapers.xml"
            target = site / "wrath/wallpapers.xml"
            target.parent.mkdir(parents=True, exist_ok=True)
            data = b"<html><head><title>Wrath wallpapers</title></head><body>archive</body></html>"
            target.write_bytes(data)
            payload["files"].append({
                "route": route,
                "output_path": "offline/site/wrath/wallpapers.xml",
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": "text/html; charset=UTF-8",
                "kind": "html",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            route_map = json.loads((base / "pages/__offline/route-map.json").read_text(encoding="utf-8"))
            target_static = pages.DEFAULT_BASE_PATH + "wrath/wallpapers.xml.html"
            self.assertEqual(route_map["routes"]["/wrath/wallpapers.xml"], target_static)
            self.assertFalse((base / "pages/wrath/wallpapers.xml").exists())
            self.assertTrue((base / "pages/wrath/wallpapers.xml.html").is_file())

        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            route_map = json.loads((base / "pages/__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertNotIn("/wrath/wallpapers.xml", route_map["routes"])

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

    def test_wrath_viewer_rewrite_is_strict_and_node_validated(self) -> None:
        common_urls = [
            f"http://www.worldofwarcraft.com/wrath/images/artwork/ss{index}.jpg"
            for index in range(1, 13)
        ]
        shot_urls = common_urls + [
            "http://www.worldofwarcraft.com/wrath/images/artwork/en_us/ss1.jpg"
        ]
        source_lines = ["var shotList = ["]
        source_lines.extend(f'    "{url}",' for url in shot_urls)
        source_lines.extend(
            [
                "];",
                "var currentShotNumber = 1;",
                "function nextShot() { return shotList[currentShotNumber + 1]; }",
                "function previousShot() { return shotList[currentShotNumber - 1]; }",
                "var openedShot = -1;",
                "function omegaLightBox(index) { openedShot = index; }",
                'checkForSpecifiedShot = window.location.href.split("s=");',
                "nowViewing = (checkForSpecifiedShot[1]) ? eval(checkForSpecifiedShot[1]) : 0;",
                "omegaLightBox(nowViewing-1);",
            ]
        )
        source = chr(10).join(source_lines)
        rewritten = pages.rewrite_wrath_viewer_script(source)

        self.assertEqual(rewritten.count("URLSearchParams"), 1)
        self.assertEqual(rewritten.count("eval("), 0)
        self.assertIn('getAll("s")', rewritten)
        self.assertIn("omegaLightBox(nowViewing-1);", rewritten)
        self.assertIn(
            "function nextShot() { return shotList[currentShotNumber + 1]; }",
            rewritten,
        )
        self.assertIn(
            "function previousShot() { return shotList[currentShotNumber - 1]; }",
            rewritten,
        )
        for url in shot_urls:
            self.assertIn(f'"{url}"', rewritten)

        node_command = shutil.which("node")
        node = Path(node_command) if node_command else Path(
            "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
        )
        if not node.is_file():
            self.skipTest("bundled Node.js is unavailable for the viewer VM regression")
        cases = [
            {"search": "?s=1", "expected": 1},
            {"search": "?s=3", "expected": 3},
            {"search": "?s=13", "expected": 13},
            {"search": "?s=%33", "expected": 3},
            {"search": "", "expected": 1},
            {"search": "?s=", "expected": 1},
            {"search": "?s=0", "expected": 1},
            {"search": "?s=-1", "expected": 1},
            {"search": "?s=14", "expected": 1},
            {"search": "?s=3&s=4", "expected": 1},
            {"search": "?s=9007199254740992", "expected": 1},
            {"search": "?s=sentinel%3D99", "expected": 1},
        ]
        driver = """
const vm = require("node:vm");
const code = CODE_PLACEHOLDER;
const cases = CASES_PLACEHOLDER;
const expectedList = SHOT_LIST_PLACEHOLDER;
const results = [];
for (const item of cases) {
    const context = {
        window: {
            location: {
                search: item.search,
                href: "https://pages.test/wrath/art.xml" + item.search
            }
        },
        URLSearchParams,
        sentinel: 0,
        eval: function () {
            throw new Error("eval must not be called");
        }
    };
    vm.createContext(context);
    vm.runInContext(code, context);
    results.push({
        nowViewing: context.nowViewing,
        openedShot: context.openedShot,
        sentinel: context.sentinel,
        shotList: context.shotList
    });
}
process.stdout.write(JSON.stringify({results, expectedList}));
""".replace("CODE_PLACEHOLDER", json.dumps(rewritten))
        driver = driver.replace("CASES_PLACEHOLDER", json.dumps(cases))
        driver = driver.replace("SHOT_LIST_PLACEHOLDER", json.dumps(shot_urls))
        result = subprocess.run(
            [str(node), "-e", driver],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["expectedList"], shot_urls)
        self.assertEqual(len(payload["results"]), len(cases))
        for case, observed in zip(cases, payload["results"]):
            with self.subTest(search=case["search"]):
                self.assertEqual(observed["nowViewing"], case["expected"])
                self.assertEqual(observed["openedShot"], case["expected"] - 1)
                self.assertEqual(observed["sentinel"], 0)
                self.assertEqual(observed["shotList"], shot_urls)

        with self.assertRaises(pages.PagesExportError):
            pages.rewrite_wrath_viewer_script(source.replace('split("s=")', 'split("page=")'))
        fragment = (
            'checkForSpecifiedShot = window.location.href.split("s=");'
            + chr(10)
            + "nowViewing = (checkForSpecifiedShot[1]) ? "
            + "eval(checkForSpecifiedShot[1]) : 0;"
        )
        with self.assertRaises(pages.PagesExportError):
            pages.rewrite_wrath_viewer_script(source + chr(10) + fragment)

    def test_wrath_viewer_rewrite_runs_only_for_exact_route(self) -> None:
        source = (
            'var shotList = ["common1", "common2", "common3"];'
            'checkForSpecifiedShot = window.location.href.split("s=");'
            "nowViewing = (checkForSpecifiedShot[1]) ? eval(checkForSpecifiedShot[1]) : 0;"
            "function omegaLightBox(index) { return index; }"
            "omegaLightBox(nowViewing-1);"
        )
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            routes = (
                "/wrath/js/screeniesimplified.js",
                "/wrath/js/other-viewer.js",
            )
            for route in routes:
                script = site / route.lstrip("/")
                script.parent.mkdir(parents=True, exist_ok=True)
                data = source.encode("utf-8")
                script.write_bytes(data)
                payload["files"].append(
                    {
                        "route": route,
                        "output_path": "offline/site/" + route.lstrip("/"),
                        "derived_sha256": hashlib.sha256(data).hexdigest(),
                        "derived_length": len(data),
                        "mime": "application/javascript",
                        "kind": "js",
                        "source_base_url": "http://www.worldofwarcraft.com" + route,
                    }
                )
                payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=base / "pages",
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            exact = (base / "pages/wrath/js/screeniesimplified.js").read_text(encoding="utf-8")
            other = (base / "pages/wrath/js/other-viewer.js").read_text(encoding="utf-8")
            self.assertNotIn("eval(", exact)
            self.assertIn("URLSearchParams", exact)
            self.assertIn("eval(", other)
            provenance = json.loads((base / "pages/export-provenance.json").read_text(encoding="utf-8"))
            exact_record = next(
                row for row in provenance["files"]
                if row.get("route") == "/wrath/js/screeniesimplified.js"
            )
            self.assertIn("Wrath viewer query parser", exact_record["derivation_reason"])

    def test_wrath_card_hit_area_fallback_is_narrow_and_idempotent(self) -> None:
        source = """<!doctype html><html><head><title>Gallery</title></head><body>
<div class="ssborder"><div><a href="/wrath/art.xml?s=1">
<img src="/__offline/missing-image.svg?requested=ssborder1.png" class="png"></a></div></div>
<div class="ssborder"><div><a href="/wrath/art.xml?s=2">
<img src="/wrath/images/layout/ssborder1.png" class="png"></a></div></div>
<img class="content" src="/__offline/missing-image.svg?requested=content.jpg">
</body></html>"""
        for route in ("/wrath/artwork.xml", "/wrath/screenshots.xml"):
            with self.subTest(route=route):
                derived, changed = pages.rewrite_wrath_card_hit_area(source, route=route)
                self.assertTrue(changed)
                self.assertEqual(derived.count(pages._WRATH_CARD_HIT_AREA_MARKER), 1)
                self.assertIn(".ssborder a", derived)
                self.assertIn("width: 243px;", derived)
                self.assertIn("height: 193px;", derived)
                self.assertIn(
                    '.ssborder img[src*="missing-image.svg"][src*="ssborder1.png"]',
                    derived,
                )
                self.assertIn(
                    'src="/wrath/images/layout/ssborder1.png"',
                    derived,
                )
                self.assertIn(
                    'src="/__offline/missing-image.svg?requested=content.jpg"',
                    derived,
                )
                repeated, repeated_changed = pages.rewrite_wrath_card_hit_area(
                    derived, route=route
                )
                self.assertFalse(repeated_changed)
                self.assertEqual(repeated, derived)

        ordinary, ordinary_changed = pages.rewrite_wrath_card_hit_area(
            source, route="/wrath/index.xml"
        )
        self.assertFalse(ordinary_changed)
        self.assertEqual(ordinary, source)

    def test_wrath_card_hit_area_fallback_is_exported_only_for_gallery_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            source = """<!doctype html><html><head><title>Gallery</title></head><body>
<div class="ssborder"><div><a href="/wrath/art.xml?s=1">
<img src="/__offline/missing-image.svg?requested=ssborder1.png"></a></div></div>
<img src="/__offline/missing-image.svg?requested=content.jpg">
</body></html>""".encode("utf-8")
            routes = (
                "/wrath/artwork.xml",
                "/wrath/screenshots.xml",
                "/wrath/other.xml",
            )
            for route in routes:
                relative = route.lstrip("/")
                target = site / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source)
                payload["files"].append(
                    {
                        "route": route,
                        "output_path": "offline/site/" + relative,
                        "derived_sha256": hashlib.sha256(source).hexdigest(),
                        "derived_length": len(source),
                        "mime": "text/html; charset=UTF-8",
                        "kind": "html",
                        "source_base_url": "http://www.worldofwarcraft.com" + route,
                    }
                )
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            output = base / "pages"
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            provenance = json.loads(
                (output / "export-provenance.json").read_text(encoding="utf-8")
            )
            for route in routes:
                exported = (output / ("wrath/" + route.rsplit("/", 1)[-1] + ".html")).read_text(
                    encoding="utf-8"
                )
                if route in {"/wrath/artwork.xml", "/wrath/screenshots.xml"}:
                    self.assertIn(pages._WRATH_CARD_HIT_AREA_MARKER, exported)
                    record = next(
                        row for row in provenance["files"] if row.get("route") == route
                    )
                    self.assertIn("Wrath card hit-area fallback", record["derivation_reason"])
                else:
                    self.assertNotIn(pages._WRATH_CARD_HIT_AREA_MARKER, exported)

    def test_news_toggle_anchor_rewrite_is_strict_idempotent_and_preserves_href(self) -> None:
        source = """<!doctype html><html><head></head><body>
<div class="hoverContainer" onclick="javascript:toggleEntry('1','')">
<h1><a href="javascript:dummyFunction()">Title</a></h1>
<ul><li class="news-toggle"><a href="javascript:toggleEntry('1','')"><img src="/v2/images/pixel.gif"></a></li></ul>
</div>
<div class="hoverContainer" onclick="toggleEntry('2','alt')">
<ul><li class="news-toggle"><a href=" JaVaScRiPt : toggleEntry ( '2' , 'alt' ) ">Case-insensitive scheme</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('wrong','')">
<ul><li class="news-toggle"><a href="javascript:toggleEntry('2','')">Wrong parent</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('Foo','')">
<ul><li class="news-toggle"><a href="javascript:toggleEntry('foo','')">Case mismatch</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:ToggleEntry('5','')">
<ul><li class="news-toggle"><a href="javascript:toggleEntry('5','')">Function case mismatch</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('has space','')">
<ul><li class="news-toggle"><a href="javascript:toggleEntry('has space','')">String whitespace</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('composite','')">
<ul><li class="news-toggle"><a href="javascript:toggleEntry(window.id,'')">Composite expression</a></li></ul>
</div>
<div class="hoverContainer" onclick="toggleEntry('bare','')">
<ul><li class="news-toggle"><a href="toggleEntry('bare','')">Bare href</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('3','')">
<ul><li class="other"><a href="javascript:toggleEntry('3','')">Wrong list</a></li></ul>
</div>
<div class="hoverContainer" onclick="javascript:toggleEntry('4','')">
<ul><li class="news-toggle"><a onclick="keepExisting()" href="javascript:toggleEntry('4','')">Existing handler</a></li></ul>
</div>
</body></html>"""
        rewritten, changed, matched = pages.rewrite_news_toggle_anchors(source)
        self.assertTrue(changed)
        self.assertEqual(matched, 2)
        self.assertEqual(rewritten.count('onclick="event.stopPropagation();"'), 2)
        self.assertIn('href="javascript:toggleEntry(\'1\',\'\')"', rewritten)
        self.assertIn('href=" JaVaScRiPt : toggleEntry ( \'2\' , \'alt\' ) "', rewritten)
        self.assertIn('href="javascript:dummyFunction()"', rewritten)
        self.assertIn('onclick="keepExisting()" href="javascript:toggleEntry(\'4\',\'\')"', rewritten)
        self.assertIn('href="javascript:toggleEntry(\'foo\',\'\')"', rewritten)
        self.assertIn('href="javascript:toggleEntry(\'has space\',\'\')"', rewritten)
        self.assertIn('href="javascript:toggleEntry(window.id,\'\')"', rewritten)
        self.assertIn('href="toggleEntry(\'bare\',\'\')"', rewritten)
        self.assertIn('.news-toggle a[data-archive-derived="news-toggle-anchor-v1"]', rewritten)
        self.assertIn('width: 14px;', rewritten)
        self.assertIn('height: 11px;', rewritten)
        self.assertNotIn('preventDefault', rewritten)
        self.assertNotIn('eval(', rewritten)
        plain = "<p>no news toggle or toggleEntry</p>"
        self.assertEqual(pages.rewrite_news_toggle_anchors(plain), (plain, False, 0))
        repeated, repeated_changed, repeated_matched = pages.rewrite_news_toggle_anchors(rewritten)
        self.assertFalse(repeated_changed)
        self.assertEqual(repeated_matched, 0)
        self.assertEqual(repeated, rewritten)

    def test_news_toggle_anchor_rewrite_runs_in_export_and_records_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            target_route = "/news/rss-07-2007.xml"
            other_route = "/news/other.xml"
            target_source = """<html><head></head><body>
<div class="hoverContainer" onclick="javascript:toggleEntry('1','')"><h1><a href="javascript:dummyFunction()">Title</a></h1>
<ul><li class="news-toggle"><a href="javascript:toggleEntry('1','')"><img src="/v2/images/pixel.gif"></a></li></ul></div>
</body></html>""".encode("utf-8")
            other_source = """<html><head></head><body>
<div class="hoverContainer" onclick="javascript:toggleEntry('2','')"><ul><li class="news-toggle"><a href="javascript:otherAction()">Other</a></li></ul></div>
</body></html>""".encode("utf-8")
            target_path = site / target_route.lstrip("/")
            other_path = site / other_route.lstrip("/")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(target_source)
            other_path.write_bytes(other_source)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            for route, relative, data in (
                (target_route, "offline/site/" + target_route.lstrip("/"), target_source),
                (other_route, "offline/site/" + other_route.lstrip("/"), other_source),
            ):
                payload["files"].append(
                    {
                        "route": route,
                        "output_path": relative,
                        "derived_sha256": hashlib.sha256(data).hexdigest(),
                        "derived_length": len(data),
                        "mime": "text/html; charset=UTF-8",
                        "kind": "html",
                        "source_base_url": "http://www.worldofwarcraft.com" + route,
                    }
                )
                payload["origin_index"]["www.worldofwarcraft.com" + route] = route
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            output = base / "pages"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
            )
            target = (output / "news/rss-07-2007.xml.html").read_text(encoding="utf-8")
            other = (output / "news/other.xml.html").read_text(encoding="utf-8")
            self.assertEqual(result["stats"]["news_toggle_anchor_repaired"], 1)
            self.assertEqual(target.count('onclick="event.stopPropagation();"'), 1)
            self.assertIn('href="javascript:toggleEntry(', target)
            self.assertIn("&#x27;1&#x27;", target)
            self.assertIn('href="javascript:dummyFunction()"', target)
            self.assertNotIn('data-archive-derived="news-toggle-anchor-v1"', other)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            target_record = next(row for row in provenance["files"] if row.get("route") == target_route)
            other_record = next(row for row in provenance["files"] if row.get("route") == other_route)
            self.assertIn("news-toggle anchor repair", target_record["derivation_reason"])
            self.assertNotIn("news-toggle anchor repair", other_record.get("derivation_reason", ""))
            self.assertEqual(target_path.read_bytes(), target_source)
            self.assertEqual(other_path.read_bytes(), other_source)


if __name__ == "__main__":
    unittest.main()
