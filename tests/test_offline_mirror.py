from __future__ import annotations

import http.client
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
import subprocess
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import offline_mirror as mirror  # noqa: E402


class AttributeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.casefold() in {"src", "href", "data", "background", "action", "poster"} and value:
                self.references.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


class OfflineMirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / "offline")
        cls.work = Path(cls.temp.name)
        cls.site = cls.work / "site"
        cls.manifest_path = cls.work / "build-manifest.json"
        cls.manifest = mirror.build_site(
            url_map_path=mirror.DEFAULT_URL_MAP,
            overlay_path=mirror.DEFAULT_OVERLAY,
            site_dir=cls.site,
            manifest_path=cls.manifest_path,
            support_dir=mirror.DEFAULT_SUPPORT,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_build_covers_core_pages_with_source_hashes(self) -> None:
        core = [item for item in self.manifest["files"] if item.get("role") == "core_page"]
        self.assertEqual(len(core), 52)
        self.assertEqual(self.manifest["stats"]["source_entries"], 437)
        self.assertEqual(self.manifest["stats"]["supplements"], 1)
        for item in core:
            self.assertTrue((ROOT / item["output_path"]).is_file())
            self.assertEqual(item["mime"].casefold().split(";", 1)[0], "text/html")
            source = ROOT / item["source_local_path"]
            self.assertEqual(mirror.sha256_file(source), item["source_sha256"])
            self.assertEqual(mirror.sha256_file(ROOT / item["output_path"]), item["derived_sha256"])

    def test_html_xml_derivation_localizes_and_handles_missing_images(self) -> None:
        page = (self.site / "info/encyclopedia/315.xml").read_text(encoding="utf-8")
        self.assertNotIn("<?xml-stylesheet", page)
        self.assertIn("offline derived from source SHA-256", page)
        self.assertIn('/__offline/compat.js', page)
        self.assertIn('/__offline/missing-image.svg?', page)
        parser = AttributeParser()
        parser.feed(page)
        external = [value for value in parser.references if re.match(r"(?i)^(?:https?:)?//", value)]
        self.assertEqual(external, [])
        self.assertIn("/info/encyclopedia/index.xml", page)
        self.assertNotIn("_gat._getTracker", page)

    def test_scripts_have_no_external_url_literals_that_can_request(self) -> None:
        # Comments may retain historical attribution URLs.  URL-bearing quoted
        # strings in menu scripts must have become local routes/placeholders.
        for path in (self.site / "new-hp/js").glob("*.js"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if line.lstrip().startswith("//"):
                    continue
                self.assertNotRegex(line, r"(?i)[\"']https?://")

    def test_css_imports_use_stylesheet_context_and_backgrounds_use_image_context(self) -> None:
        base_url = "http://www.worldofwarcraft.com/styles/base.css"
        routes = {
            "/styles/master.css": {"logical_url": "http://www.worldofwarcraft.com/styles/master.css"},
            "/styles/theme.css": {"logical_url": "http://www.worldofwarcraft.com/styles/theme.css"},
        }
        localizer = mirror.Localizer(routes, set())
        recorder = mirror.ReferenceRecorder("/styles/base.css", base_url)
        css = (
            '@import url("master.css");\n'
            '@import url(master.css);\n'
            '@import "theme.css";\n'
            '@import url("missing.css");\n'
            'body { background: url("missing.png"); }\n'
        )

        rewritten = mirror.rewrite_css(
            css,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
        )

        self.assertIn('@import url("/styles/master.css")', rewritten)
        self.assertIn('@import url(/styles/master.css)', rewritten)
        self.assertNotIn('%22/%22s%22t%22y', rewritten)
        self.assertIn('@import "/styles/theme.css"', rewritten)
        self.assertIn('/__offline/empty.css?', rewritten)
        self.assertIn('/__offline/missing-image.svg?', rewritten)
        import_records = [item for item in recorder.records if item["context"] == "css_import"]
        self.assertEqual(len(import_records), 4)
        import_actions = {item["literal"]: item["action"] for item in import_records}
        self.assertEqual(import_actions["master.css"], "localized")
        self.assertEqual(import_actions["theme.css"], "localized")
        self.assertEqual(import_actions["missing.css"], "placeholder")
        background_records = [item for item in recorder.records if item["context"] == "css_url"]
        self.assertEqual(len(background_records), 1)
        self.assertIn("missing-image.svg", background_records[0]["target"])

    def test_origin_index_keeps_forum_and_primary_same_path_isolated(self) -> None:
        main_url = "http://www.worldofwarcraft.com/images/pixel.gif"
        forum_url = "http://forums.worldofwarcraft.com/images/pixel.gif"
        routes = {
            "/images/pixel.gif": {"logical_url": main_url},
            "/_origins/forums.worldofwarcraft.com/images/pixel.gif": {"logical_url": forum_url},
        }
        origin_index = {
            mirror.origin_key(main_url): "/images/pixel.gif",
            mirror.origin_key(forum_url): "/_origins/forums.worldofwarcraft.com/images/pixel.gif",
        }
        localizer = mirror.Localizer(routes, set(), origin_index=origin_index)
        self.assertEqual(localizer._lookup(main_url)[0], "/images/pixel.gif")
        self.assertEqual(
            localizer._lookup(forum_url)[0],
            "/_origins/forums.worldofwarcraft.com/images/pixel.gif",
        )
        # A third host cannot borrow either same-path entry through the
        # path-only compatibility fallback.
        self.assertIsNone(localizer._lookup("http://www.blizzard.com/images/pixel.gif"))

    def test_build_namespaces_forum_css_and_image_without_colliding(self) -> None:
        main_css = self.work / "origin-main.css"
        main_image = self.work / "origin-main.gif"
        forum_css = self.work / "origin-forum.css"
        forum_image = self.work / "origin-forum.gif"
        main_css.write_text("body{background:url('/images/pixel.gif')}\n", encoding="utf-8")
        forum_css.write_text("body{background:url('/images/pixel.gif')}\n", encoding="utf-8")
        main_image.write_bytes(b"MAIN-PIXEL")
        forum_image.write_bytes(b"FORUM-PIXEL")

        def source(logical: str, path: Path, mime: str, kind: str) -> dict:
            return {
                "logical_url": logical,
                "local_path": path.relative_to(ROOT).as_posix(),
                "sha256": mirror.sha256_file(path),
                "mime": mime,
                "kind": kind,
            }

        primary_map = self.work / "origin-primary-map.json"
        primary_map.write_text(json.dumps({"files": [
            source("http://www.worldofwarcraft.com/css/theme.css", main_css, "text/css; charset=UTF-8", "css"),
            source("http://www.worldofwarcraft.com/images/pixel.gif", main_image, "image/gif", "image"),
        ]}), encoding="utf-8")
        forum_map = self.work / "origin-forum-map.json"
        forum_map.write_text(json.dumps({"files": [
            source("http://forums.worldofwarcraft.com/css/theme.css", forum_css, "text/css; charset=UTF-8", "css"),
            source("http://forums.worldofwarcraft.com/images/pixel.gif", forum_image, "image/gif", "image"),
        ]}), encoding="utf-8")
        site = self.work / "origin-site"
        manifest_path = self.work / "origin-manifest.json"
        manifest = mirror.build_site(
            url_map_path=primary_map,
            overlay_path=self.work / "missing-origin-overlay.json",
            site_dir=site,
            manifest_path=manifest_path,
            support_dir=mirror.DEFAULT_SUPPORT,
            extra_map_paths=(forum_map,),
            include_menu_supplement=False,
        )
        forum_css_route = "/_origins/forums.worldofwarcraft.com/css/theme.css"
        forum_image_route = "/_origins/forums.worldofwarcraft.com/images/pixel.gif"
        self.assertIn(forum_css_route, {item["route"] for item in manifest["files"]})
        self.assertIn(forum_image_route, {item["route"] for item in manifest["files"]})
        self.assertEqual((site / "images/pixel.gif").read_bytes(), b"MAIN-PIXEL")
        self.assertEqual((site / forum_image_route.lstrip("/")).read_bytes(), b"FORUM-PIXEL")
        self.assertIn('/images/pixel.gif', (site / "css/theme.css").read_text(encoding="utf-8"))
        self.assertIn(forum_image_route, (site / forum_css_route.lstrip("/")).read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["origin_index"][mirror.origin_key("http://forums.worldofwarcraft.com/images/pixel.gif")],
            forum_image_route,
        )
        forum_record = next(item for item in manifest["files"] if item["route"] == forum_image_route)
        self.assertEqual(forum_record["origin_namespace"], "forums.worldofwarcraft.com")

    def test_source_base_url_alias_uses_forum_origin_without_overriding_logical(self) -> None:
        main_url = "http://www.worldofwarcraft.com/policy/forum-coc.html"
        forum_source = "http://forums.worldofwarcraft.com/forum-coc.html"
        route = "/policy/forum-coc.html"
        entries = {
            route: {
                "logical_url": main_url,
                "source_base_url": forum_source,
            },
        }
        origin_index = {mirror.origin_key(main_url): route, mirror.origin_key(forum_source): route}
        localizer = mirror.Localizer(entries, set(), origin_index=origin_index)
        self.assertEqual(localizer._lookup(forum_source)[0], route)
        self.assertEqual(localizer._lookup(main_url)[0], route)

    def test_script_embedded_css_and_js_attributes_get_typed_contexts(self) -> None:
        base_url = "http://www.worldofwarcraft.com/new-hp/js/menu1.js"
        routes = {
            "/new-hp/styles/menu.css": {"logical_url": "http://www.worldofwarcraft.com/new-hp/styles/menu.css"},
            "/new-hp/js/menu2.js": {"logical_url": "http://www.worldofwarcraft.com/new-hp/js/menu2.js"},
            "/new-hp/images/icon.gif": {"logical_url": "http://www.worldofwarcraft.com/new-hp/images/icon.gif"},
        }
        localizer = mirror.Localizer(routes, set())
        recorder = mirror.ReferenceRecorder("/new-hp/js/menu1.js", base_url)
        script = (
            '<link rel="stylesheet" href="/new-hp/styles/menu.css">'
            '<script src="/new-hp/js/menu2.js"></script>'
            '<img src="/new-hp/images/icon.gif">'
        )

        rewritten = mirror.rewrite_script(
            script,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
        )

        self.assertIn('href="/new-hp/styles/menu.css"', rewritten)
        self.assertIn('src="/new-hp/js/menu2.js"', rewritten)
        self.assertIn('src="/new-hp/images/icon.gif"', rewritten)
        contexts = {item["literal"]: item["context"] for item in recorder.records}
        self.assertEqual(contexts["/new-hp/styles/menu.css"], "stylesheet")
        self.assertEqual(contexts["/new-hp/js/menu2.js"], "script")
        self.assertEqual(contexts["/new-hp/images/icon.gif"], "image")

    def test_compat_injection_ignores_head_markers_inside_inline_script(self) -> None:
        base_url = "http://www.worldofwarcraft.com/burningcrusade/townhall/story.html"
        localizer = mirror.Localizer({}, set())
        recorder = mirror.ReferenceRecorder("/burningcrusade/townhall/story.html", base_url)
        source = '<html><head><script>var markup = "<style>body{color:red}</style></head>";</script></head><body></body></html>'

        derived = mirror.rewrite_html(
            source,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
            source_sha="test-source-sha",
            compat_assets=["/__offline/compat.css", "/__offline/compat.js"],
        )

        script_start = derived.index("<script>")
        script_end = derived.index("</script>", script_start)
        self.assertNotIn("/__offline/compat", derived[script_start:script_end])
        self.assertEqual(derived.count("/__offline/compat.css"), 1)
        self.assertEqual(derived.count("/__offline/compat.js"), 1)
        self.assertIn('</script><link rel="stylesheet" href="/__offline/compat.css">', derived)

    def test_raid_calendar_uses_snapshot_year_without_changing_other_pages(self) -> None:
        localizer = mirror.Localizer({}, set())
        calendar = "http://www.worldofwarcraft.com:80/calendar/"
        recorder = mirror.ReferenceRecorder("/calendar/index.html", calendar)
        source = "todate=new Date(); var year=todate.getYear();"
        derived = mirror.rewrite_script(source, base_url=calendar, localizer=localizer, recorder=recorder)
        self.assertIn("new Date(2008, 4, 12, 21, 0, 44)", derived)
        self.assertEqual(mirror.rewrite_script(source, base_url="http://www.worldofwarcraft.com/other.html",
                                              localizer=localizer, recorder=recorder), source)

    def test_dynamic_image_prefix_is_not_replaced_by_a_missing_page(self) -> None:
        url = "http://www.worldofwarcraft.com/info/dungeons/auchindoun.xml"
        localizer = mirror.Localizer({}, set())
        recorder = mirror.ReferenceRecorder("/info/dungeons/auchindoun.xml", url)
        source = 'targexpimg.src = "/new-hp/images/icons/news-"+exps+".gif";'
        self.assertEqual(mirror.rewrite_script(source, base_url=url, localizer=localizer,
                                              recorder=recorder), source)

    def test_toplist_feed_clock_keeps_historical_week_and_cookie_clock(self) -> None:
        url = "http://www.worldofwarcraft.com/toplist/includes-client/js/logic.js"
        recorder = mirror.ReferenceRecorder("/toplist/includes-client/js/logic.js", url)
        localizer = mirror.Localizer({}, set())
        source = (
            "var date = new Date(); var tmpDate = new Date('May 1, 2008'); "
            "var today = new Date(); var feeds = []; "
            "for (var delay = 2; delay < 9; delay++) { "
            "today.setDate(today.getDate() - delay); "
            "feeds.push(today.getFullYear() + '-' + (today.getMonth()+1) + '-' + today.getDate()); "
            "today = new Date(); }"
        )
        derived = mirror.rewrite_script(source, base_url=url, localizer=localizer, recorder=recorder)
        self.assertIn("var date = new Date();", derived)
        self.assertIn("var tmpDate = new Date('May 1, 2008');", derived)
        self.assertEqual(len([r for r in recorder.records if r["action"] == "patched"]), 1)
        self.assertEqual(mirror.rewrite_script(derived, base_url=url, localizer=localizer, recorder=recorder), derived)
        for other in ("http://www.worldofwarcraft.com/logic.js", "http://www.blizzard.com/toplist/includes-client/js/logic.js"):
            self.assertEqual(mirror.rewrite_script(source, base_url=other,
                                                   localizer=localizer, recorder=recorder), source)
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for historical Toplist week calculation")
        result = subprocess.run([node, "-e", derived + "process.stdout.write(JSON.stringify(feeds));"],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ["2008-5-10", "2008-5-9", "2008-5-8", "2008-5-7",
                                                    "2008-5-6", "2008-5-5", "2008-5-4"])

    def test_homepage_screenshot_uses_utc_snapshot_date(self) -> None:
        source = ('xmlServerDate = new Date(xmlTimeVerification.getResponseHeader("Date"));'
                  'currentShotNumber = Math.floor(xmlServerDate.getTime()/86400000) - 12671;')
        url = "https://www.worldofwarcraft.com/index.xml"
        recorder = mirror.ReferenceRecorder("/index.xml", url)
        localizer = mirror.Localizer({}, set())
        derived = mirror.rewrite_script(source, base_url=url, localizer=localizer, recorder=recorder)
        self.assertIn("new Date(Date.UTC(2008, 4, 12, 21, 0, 44))", derived)
        self.assertEqual(len([r for r in recorder.records if r["action"] == "patched"]), 1)
        for other in ("http://www.worldofwarcraft.com/other.html", "http://www.blizzard.com/index.xml"):
            self.assertEqual(mirror.rewrite_script(source, base_url=other,
                                                   localizer=localizer, recorder=recorder), source)
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the historical screenshot calculation")
        completed = subprocess.run([node, "-e", derived + "process.stdout.write(String(currentShotNumber));"],
                                   text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "1340")

    def test_navtree_compat_fallback_only_fills_unset_result(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the navtree fallback runtime check")
        base_url = "http://www.worldofwarcraft.com/shared/wow-com/includes-client/navtreefunctions.js"
        localizer = mirror.Localizer({}, set())
        driver = (
            "const fs = require('fs');\n"
            "const vm = require('vm');\n"
            "const code = fs.readFileSync(0, 'utf8');\n"
            "const context = {window: {Menu1_6: ['Community']}, "
            "document: {location: {pathname: '/COMMUNITY/CHINAICOKE.HTML'}}};\n"
            "vm.createContext(context);\n"
            "vm.runInContext(code, context);\n"
            "process.stdout.write(String(context.result));\n"
        )

        for source, expected in (
            (
                "var result = 'existing'; var pageId = 'Community'; "
                "function findNode() {} findNode('1','_',pageId);",
                "existing",
            ),
            (
                "var pageId = 'Community'; function findNode() {} "
                "findNode('1','_',pageId);",
                "1_6",
            ),
        ):
            recorder = mirror.ReferenceRecorder("/shared/wow-com/includes-client/navtreefunctions.js", base_url)
            rewritten = mirror.rewrite_script(
                source,
                base_url=base_url,
                localizer=localizer,
                recorder=recorder,
            )
            self.assertIn("offline-nav-alias-fallback-v1", rewritten)
            self.assertIn("window[\"Menu\" + offlineNavNode]", rewritten)
            self.assertEqual(len([r for r in recorder.records if r["action"] == "patched"]), 1)
            self.assertIn("nav-alias-audit.json", recorder.records[0]["reason"])
            completed = subprocess.run(
                [node, "-e", driver],
                input=rewritten,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout, expected)

    def test_navtree_valentines_fallback_uses_observed_menu_node(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the navtree fallback runtime check")
        base_url = "http://www.worldofwarcraft.com/shared/wow-com/includes-client/navtreefunctions.js"
        localizer = mirror.Localizer({}, set())
        source = "var pageId = 'Fan Wallpapers'; function findNode() {} findNode('1','_',pageId);"
        recorder = mirror.ReferenceRecorder("/shared/wow-com/includes-client/navtreefunctions.js", base_url)
        rewritten = mirror.rewrite_script(source, base_url=base_url, localizer=localizer, recorder=recorder)
        self.assertIn('"/downloads/wallpapers/valentines/index.html"', rewritten)
        driver = (
            "const fs = require('fs');\n"
            "const vm = require('vm');\n"
            "const code = fs.readFileSync(0, 'utf8');\n"
            "const context = {window: {Menu1_8_6: ['Fan Wallpapers']}, "
            "document: {location: {pathname: '/DOWNLOADS/WALLPAPERS/VALENTINES/INDEX.HTML'}}};\n"
            "vm.createContext(context);\n"
            "vm.runInContext(code, context);\n"
            "process.stdout.write(String(context.result));\n"
        )
        completed = subprocess.run([node, "-e", driver], input=rewritten, text=True,
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "1_8_6")

    def test_navtree_recovery_maps_legacy_pvp_and_dressing_pages(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the navtree recovery runtime check")
        base_url = "http://www.worldofwarcraft.com/shared/wow-com/includes-client/navtreefunctions.js"
        localizer = mirror.Localizer({}, set())
        driver = (
            "const fs = require('fs');\n"
            "const vm = require('vm');\n"
            "const code = fs.readFileSync(0, 'utf8');\n"
            "const context = {window: WINDOW, "
            "document: {location: {pathname: PATH}}};\n"
            "vm.createContext(context);\n"
            "vm.runInContext(code, context);\n"
            "process.stdout.write(String(context.result));\n"
        )
        cases = (
            (
                "/info/faq/pvppage.html",
                "1_9",
                "var pageId = 'PvP Rankings'; function findNode() {} findNode('1','_',pageId);",
                "const WINDOW = {Menu1_9: ['Player vs Player']}; const PATH = '/info/faq/pvppage.html';\n",
            ),
            (
                "/info/underdev/dressingroom.html",
                "1_5_7",
                "var pageId = 'Dressing Room'; function findNode() {} findNode('1','_',pageId);",
                "const WINDOW = {Menu1_5_7: ['Dressing Room']}; const PATH = '/info/underdev/dressingroom.html';\n",
            ),
        )
        for route, expected, source, prelude in cases:
            recorder = mirror.ReferenceRecorder(route, base_url)
            rewritten = mirror.rewrite_script(
                source,
                base_url=base_url,
                localizer=localizer,
                recorder=recorder,
            )
            self.assertIn('"' + route + '"', rewritten)
            self.assertIn('"' + expected + '"', rewritten)
            completed = subprocess.run(
                [node, "-e", prelude + driver],
                input=rewritten,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout, expected)

    def test_mounts_footer_guards_are_route_scoped_and_preserve_available_functions(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the mounts footer guard runtime check")
        source = (
            'if (stripId(Menu1[0]) == "Game Guide")\n'
            ' document.write("strategy:" + stripId(pageId));\n'
            'if (document.location.href.indexOf("/account/") == -1 && '
            'document.location.href.indexOf("/loginsupport/") == -1)\n'
            ' document.write("error:" + stripId(pageId));\n'
            'printSubNav(result,2);\n'
            'printRelatedLinks(result);\n'
        )
        base_url = "https://www.worldofwarcraft.com/info/basics/mounts.html"
        localizer = mirror.Localizer({}, set())
        recorder = mirror.ReferenceRecorder("/info/basics/mounts.html", base_url)
        rewritten = mirror.rewrite_script(source, base_url=base_url, localizer=localizer, recorder=recorder)
        self.assertIn(mirror._MOUNTS_FOOTER_GUARD_MARKER, rewritten)
        self.assertIn('typeof stripId == "function"', rewritten)
        self.assertIn('typeof printSubNav == "function"', rewritten)
        self.assertEqual(len([r for r in recorder.records if r["action"] == "patched"]), 1)

        missing_driver = (
            "const fs = require('fs'); const vm = require('vm'); "
            "const code = fs.readFileSync(0, 'utf8'); "
            "const context = {document: {location: {href: 'https://www.worldofwarcraft.com/info/basics/mounts.html'}, "
            "write: function () { throw new Error('optional footer was not skipped'); }}}; "
            "vm.createContext(context); vm.runInContext(code, context); process.stdout.write('ok');"
        )
        missing = subprocess.run([node, "-e", missing_driver], input=rewritten, text=True,
                                 capture_output=True, check=False)
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertEqual(missing.stdout, "ok")

        present_driver = (
            "const fs = require('fs'); const vm = require('vm'); "
            "const code = fs.readFileSync(0, 'utf8'); const calls = []; "
            "const context = {stripId: function (v) { return String(v); }, Menu1: ['Game Guide'], pageId: 'Mounts', result: 'node', "
            "document: {location: {href: 'https://www.worldofwarcraft.com/info/basics/mounts.html'}, write: function (v) { calls.push(v); }}, "
            "printSubNav: function (v, n) { calls.push('sub:' + v + ':' + n); }, "
            "printRelatedLinks: function (v) { calls.push('related:' + v); }}; "
            "vm.createContext(context); vm.runInContext(code, context); process.stdout.write(JSON.stringify(calls));"
        )
        present = subprocess.run([node, "-e", present_driver], input=rewritten, text=True,
                                 capture_output=True, check=False)
        self.assertEqual(present.returncode, 0, present.stderr)
        calls = json.loads(present.stdout)
        self.assertIn("strategy:Mounts", calls)
        self.assertIn("error:Mounts", calls)
        self.assertIn("sub:node:2", calls)
        self.assertIn("related:node", calls)

        other_recorder = mirror.ReferenceRecorder("/info/basics/mounts/bear-gallery.html",
                                                  "https://www.worldofwarcraft.com/info/basics/mounts/bear-gallery.html")
        self.assertEqual(
            mirror.rewrite_script(
                source,
                base_url="https://www.worldofwarcraft.com/info/basics/mounts/bear-gallery.html",
                localizer=localizer,
                recorder=other_recorder,
            ),
            source,
        )

    def test_policy_support_guards_are_route_scoped_and_preserve_available_functions(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the policy support guard runtime check")
        base_url = "http://www.worldofwarcraft.com/policy/"
        localizer = mirror.Localizer({}, set())
        recorder = mirror.ReferenceRecorder("/policy/index.html", base_url)
        source = (
            "if (is_ie6 && !is_ie7) document.write('ie6');\n"
            "if (is_ie7) document.write('ie7');\n"
            "if (is_opera) document.write('opera');\n"
            "if (is_safari) document.write('safari');\n"
            "addEvent(window, 'load', function () { $('warcraftgamebuttons'); });\n"
            "function bla () { $('articleUrl'); }\n"
            "addEvent(window, 'load', bla);\n"
            "addEvent(window, 'load', stretchContainer);\n"
            "addEvent(window, 'load', addValues1); addEvent(window, 'load', addValues2);\n"
        )
        rewritten = mirror.rewrite_script(
            source,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
        )
        self.assertIn(mirror._POLICY_RUNTIME_GUARD_MARKER, rewritten)
        self.assertIn('typeof is_ie6 != "undefined"', rewritten)
        self.assertIn('typeof addEvent == "function" && typeof $ == "function"', rewritten)
        self.assertIn('typeof stretchContainer == "function"', rewritten)
        self.assertEqual(recorder.counts["patched"], 1)

        missing_driver = (
            "const vm = require('vm'); const code = require('fs').readFileSync(0, 'utf8'); "
            "const context = {window: {}, document: {write: function () { "
            "throw new Error('optional policy branch was not skipped'); }}}; "
            "vm.createContext(context); vm.runInContext(code, context); process.stdout.write('ok');"
        )
        missing = subprocess.run(
            [node, "-e", missing_driver],
            input=rewritten,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertEqual(missing.stdout, "ok")

        present_source = "if (is_ie7) document.write('ie7'); addEvent(window, 'load', stretchContainer);"
        present_recorder = mirror.ReferenceRecorder("/policy/index.html", base_url)
        present = mirror.rewrite_script(
            present_source,
            base_url=base_url,
            localizer=localizer,
            recorder=present_recorder,
        )
        present_driver = (
            "const vm = require('vm'); const code = require('fs').readFileSync(0, 'utf8'); "
            "const calls = []; const context = {is_ie7: true, stretchContainer: function () {}, "
            "addEvent: function () { calls.push('event'); }, window: {}, document: "
            "{write: function (v) { calls.push(v); }}}; vm.createContext(context); "
            "vm.runInContext(code, context); process.stdout.write(JSON.stringify(calls));"
        )
        available = subprocess.run(
            [node, "-e", present_driver],
            input=present,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(available.returncode, 0, available.stderr)
        self.assertEqual(json.loads(available.stdout), ["ie7", "event"])

        other_recorder = mirror.ReferenceRecorder(
            "/other.html", "http://www.worldofwarcraft.com/other.html"
        )
        self.assertEqual(
            mirror.rewrite_script(
                source,
                base_url="http://www.worldofwarcraft.com/other.html",
                localizer=localizer,
                recorder=other_recorder,
            ),
            source,
        )
        self.assertEqual(other_recorder.counts["patched"], 0)

        foreign_recorder = mirror.ReferenceRecorder(
            "/policy/index.html", "http://forums.worldofwarcraft.com/policy/"
        )
        self.assertEqual(
            mirror.rewrite_script(
                source,
                base_url="http://forums.worldofwarcraft.com/policy/",
                localizer=localizer,
                recorder=foreign_recorder,
            ),
            source,
        )
        self.assertEqual(foreign_recorder.counts["patched"], 0)

    def test_build_manifest_preserves_optional_route_alias_evidence(self) -> None:
        mount_path = ROOT / "offline/source-entities-pages-recovery/02f5f728c9a7370912742a9cedba2bfe9fd394cf2d46a5bcd44bb0386f7f7153.bin"
        gallery_path = ROOT / "offline/source-entities-pages-recovery/6d4e7e701254daa0bcd114d653d97f78be2b625dd54fad5fdf8ecd1299ea5d4c.bin"
        source_mount = {
            "source_local_path": mount_path.relative_to(ROOT).as_posix(),
            "source_sha256": mirror.sha256_file(mount_path),
            "mime": "text/html;charset=UTF-8",
        }
        source_gallery = {
            "source_local_path": gallery_path.relative_to(ROOT).as_posix(),
            "source_sha256": mirror.sha256_file(gallery_path),
            "mime": "text/html;charset=UTF-8",
        }
        url_map = {
            "anchor": "20080512210044",
            "files": [
                {
                    "original": "https://www.worldofwarcraft.com/info/basics/mounts.html",
                    "local_path": source_mount["source_local_path"],
                    "sha256": source_mount["source_sha256"],
                    "mime": source_mount["mime"],
                    "kind": "html",
                    "role": "test_page",
                    "route_alias_evidence": {
                        "status": 302,
                        "location": "/info/index.html",
                        "evidence": "test-header-record",
                    },
                },
                {
                    "original": "https://www.worldofwarcraft.com/community/comics/gallery.html",
                    "local_path": source_gallery["source_local_path"],
                    "sha256": source_gallery["source_sha256"],
                    "mime": source_gallery["mime"],
                    "kind": "html",
                    "role": "test_page_without_alias_evidence",
                },
            ],
        }
        map_path = self.work / "route-alias-evidence-map.json"
        map_path.write_text(json.dumps(url_map), encoding="utf-8")
        site_dir = self.work / "route-alias-evidence-site"
        manifest_path = self.work / "route-alias-evidence-manifest.json"
        built = mirror.build_site(
            url_map_path=map_path,
            overlay_path=self.work / "missing-overlay.json",
            site_dir=site_dir,
            manifest_path=manifest_path,
            support_dir=mirror.DEFAULT_SUPPORT,
        )
        mounted = next(item for item in built["files"] if item["route"] == "/info/basics/mounts.html")
        gallery = next(item for item in built["files"] if item["route"] == "/community/comics/gallery.html")
        self.assertEqual(mounted["route_alias_evidence"]["status"], 302)
        self.assertEqual(mounted["route_alias_evidence"]["location"], "/info/index.html")
        self.assertNotIn("route_alias_evidence", gallery)

    def test_duplicate_index_entity_retains_only_same_sha_directory_aliases(self) -> None:
        original = self.work / "directory-index-source.html"
        original.write_bytes(b"<html><body>Verified directory article</body></html>")
        different = self.work / "different-directory-source.html"
        different.write_bytes(b"<html><body>A different article</body></html>")
        def source(path: Path, logical: str) -> dict:
            return {"logical_url": logical, "local_path": path.relative_to(ROOT).as_posix(),
                    "sha256": mirror.sha256_file(path), "mime": "text/html", "kind": "html",
                    "actual_timestamp": "20080402025033"}
        primary = self.work / "directory-primary-map.json"
        primary.write_text(json.dumps({"files": [source(original, "http://www.worldofwarcraft.com/guide/index.html")]}), encoding="utf-8")
        good = {**source(original, "https://www.worldofwarcraft.com/guide/"),
                "derived_route": "/guide/index.html", "route_aliases": ["/guide", "/guide/"]}
        bad = {**source(different, "https://www.worldofwarcraft.com/unrelated/"),
               "derived_route": "/guide/index.html", "route_aliases": ["/unrelated"]}
        extra = self.work / "directory-extra-map.json"
        extra.write_text(json.dumps({"files": [good, bad]}), encoding="utf-8")
        built = mirror.build_site(
            url_map_path=primary, overlay_path=self.work / "missing-overlay.json",
            site_dir=self.work / "directory-site", manifest_path=self.work / "directory-manifest.json",
            support_dir=mirror.DEFAULT_SUPPORT, extra_map_paths=[extra], include_menu_supplement=False,
        )
        self.assertEqual(built["route_aliases"]["/guide"], "/guide/index.html")
        self.assertEqual(built["route_aliases"]["/guide/"], "/guide/index.html")
        self.assertNotIn("/unrelated", built["route_aliases"])
        self.assertNotIn("/unrelated/", built["route_aliases"])
        record = next(x for x in built["files"] if x["route"] == "/guide/index.html")
        evidence = record["route_alias_sources"]
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["logical_url"], good["logical_url"])
        self.assertEqual(evidence[0]["source_sha256"], good["sha256"])
        self.assertEqual(evidence[0]["aliases"], ["/guide", "/guide/"])

    def test_meta_refresh_localizes_only_navigation_url_and_preserves_delay(self) -> None:
        base_url = "http://www.worldofwarcraft.com/info/source.html"
        entries = {
            "/info/one.html": {"logical_url": "http://www.worldofwarcraft.com/info/one.html"},
            "/info/two.html": {"logical_url": "http://www.worldofwarcraft.com/info/two.html"},
            "/info/three.html": {"logical_url": "https://www.worldofwarcraft.com/info/three.html"},
        }
        localizer = mirror.Localizer(entries, set())
        recorder = mirror.ReferenceRecorder("/info/source.html", base_url)
        source = (
            "<html><head>"
            "<meta HTTP-EQUIV=\"ReFrEsH\" content='1; URL=\"one.html\"'>"
            "<meta http-equiv='refresh' content='5; url = /info/two.html'>"
            "<meta hTtP-eQuIv=\"refresh\" content=\"0;URL='https://www.worldofwarcraft.com/info/three.html'\">"
            "<meta http-equiv=\"refresh\" content=\"2; URL='https://external.example.invalid/landing.html'\">"
            "<meta name=\"description\" content=\"5; URL=ordinary.html\">"
            "</head><body></body></html>"
        )

        derived = mirror.rewrite_html(
            source,
            base_url=base_url,
            localizer=localizer,
            recorder=recorder,
            source_sha="test-meta-refresh",
            compat_assets=[],
        )

        self.assertIn('content="1; URL=&quot;/info/one.html&quot;"', derived)
        self.assertIn('content="5; url = /info/two.html"', derived)
        self.assertIn('content="0;URL=&#x27;/info/three.html&#x27;"', derived)
        self.assertIn('content="2; URL=&#x27;/__offline/missing.html?', derived)
        self.assertIn('content="5; URL=ordinary.html"', derived)
        navigation_records = [r for r in recorder.records if r["context"] == "navigation"]
        self.assertEqual(len(navigation_records), 4)
        self.assertEqual(
            {r["action"] for r in navigation_records},
            {"localized", "placeholder"},
        )

    def test_official_host_root_does_not_alias_unrelated_blizzard_home(self) -> None:
        entries = {"/index.xml": {"logical_url": "https://www.worldofwarcraft.com/index.xml"}}
        localizer = mirror.Localizer(entries, set(), root_target="/index.xml", route_aliases={"/": "/index.xml"})
        self.assertEqual(localizer._lookup("http://worldofwarcraft.com/")[0], "/index.xml")
        self.assertIsNone(localizer._lookup("http://www.blizzard.com/"))

    def test_excluded_advertising_frame_has_compact_explicit_placeholder(self) -> None:
        localizer = mirror.Localizer({}, set())
        base = "http://www.worldofwarcraft.com/index.xml"
        recorder = mirror.ReferenceRecorder("/index.xml", base)
        source = '<iframe src="http://ads.blizzard.com/html.ng/site=wow"></iframe>'
        derived = mirror.rewrite_html(source, base_url=base, localizer=localizer, recorder=recorder,
                                      source_sha="test", compat_assets=[])
        self.assertIn("/__offline/excluded-frame.html?", derived)
        self.assertEqual(recorder.records[0]["reason"], "excluded-dynamic-advertisement")

    def test_reviewed_historical_navigation_and_spacer_typos(self) -> None:
        localizer = mirror.Localizer({}, set())
        fansites = "http://www.worldofwarcraft.com/community/fansites.html"
        recorder = mirror.ReferenceRecorder("/community/fansites.html", fansites)
        self.assertIn('pageId = "Fan Sites"', mirror.rewrite_script('var pageId = "Fansites";',
            base_url=fansites, localizer=localizer, recorder=recorder))
        starter = "http://www.worldofwarcraft.com/info/basics/gettingstarted.html"
        source = '<html><head></head><body><img scr=/shared/wow-com/images/layout/pixel.gif></body></html>'
        derived = mirror.rewrite_html(source, base_url=starter, localizer=localizer, recorder=recorder,
                                      source_sha="test", compat_assets=[])
        self.assertIn('<img src=', derived)
        other = mirror.rewrite_html(source, base_url=fansites, localizer=localizer, recorder=recorder,
                                    source_sha="test", compat_assets=[])
        self.assertIn('<img scr=', other)

    def test_forum_policy_uses_archived_browser_opera_property_only_for_forum_source(self) -> None:
        localizer = mirror.Localizer({}, set())
        forum_source = "http://forums.worldofwarcraft.com:80/forum-coc.html"
        recorder = mirror.ReferenceRecorder("/policy/forum-coc.html", forum_source)
        source = 'if (is_opera) document.write("opera");'
        derived = mirror.rewrite_script(
            source,
            base_url=forum_source,
            localizer=localizer,
            recorder=recorder,
        )
        self.assertIn(
            'if (typeof is_opera != "undefined" ? is_opera : (typeof Browser != "undefined" && Browser && Browser.opera))',
            derived,
        )
        self.assertNotIn("if (is_opera)", derived)
        self.assertEqual(recorder.counts["patched"], 1)
        self.assertIn("Browser.opera", recorder.records[0]["target"])
        self.assertIn("no global shim", recorder.records[0]["reason"])

        unrelated = mirror.ReferenceRecorder("/other.html", "http://forums.worldofwarcraft.com:80/other.html")
        untouched = mirror.rewrite_script(
            source,
            base_url="http://www.worldofwarcraft.com:80/other.html",
            localizer=localizer,
            recorder=unrelated,
        )
        self.assertEqual(untouched, source)
        self.assertEqual(unrelated.counts["patched"], 0)

    @unittest.skipUnless(sys.platform == "win32", "Windows exclusive address binding")
    def test_two_servers_cannot_share_one_windows_port(self) -> None:
        first = mirror.OfflineHTTPServer(("127.0.0.1", 0), site_dir=self.site, manifest=self.manifest)
        try:
            with self.assertRaises(OSError):
                mirror.OfflineHTTPServer(first.server_address, site_dir=self.site, manifest=self.manifest)
        finally:
            first.server_close()

    def _server(self) -> tuple[mirror.OfflineHTTPServer, threading.Thread]:
        server = mirror.OfflineHTTPServer(
            ("127.0.0.1", 0),
            site_dir=self.site,
            manifest=self.manifest,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread

    def test_loopback_routes_mime_api_and_path_security(self) -> None:
        server, thread = self._server()
        try:
            port = server.server_port
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)

            connection.request("GET", "/info/encyclopedia/315.xml")
            response = connection.getresponse()
            body = response.read()
            self.assertEqual(response.status, 200)
            self.assertTrue(response.getheader("Content-Type", "").startswith("text/html"))
            self.assertIn(b"Alleria Windrunner", body)
            self.assertIn("'self'", response.getheader("Content-Security-Policy", ""))
            page_item = next(item for item in self.manifest["files"] if item["route"] == "/info/encyclopedia/315.xml")
            self.assertEqual(response.getheader("X-Offline-Entity-Kind"), page_item["kind"])
            self.assertEqual(response.getheader("X-Offline-Source-SHA256"), page_item["source_sha256"])
            self.assertEqual(response.getheader("X-Offline-Derived-SHA256"), page_item["derived_sha256"])
            self.assertEqual(response.getheader("X-Offline-Served-SHA256"), mirror.sha256_bytes(body))

            connection.request("GET", "/new-hp/layout/menu.xml")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertTrue(response.getheader("Content-Type", "").startswith("application/xml"))
            response.read()

            core_routes = [
                item["route"] for item in self.manifest["files"] if item.get("role") == "core_page"
            ]
            self.assertEqual(len(core_routes), 52)
            for route in core_routes:
                connection.request("GET", route)
                response = connection.getresponse()
                self.assertEqual(response.status, 200, route)
                self.assertTrue(response.getheader("Content-Type", "").startswith("text/html"), route)
                self.assertGreater(len(response.read()), 0, route)

            query = urllib.parse.quote("http://www.worldofwarcraft.com/info/encyclopedia/315.xml", safe="")
            connection.request("GET", "/__offline/api/url-map?url=" + query)
            response = connection.getresponse()
            mapping = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(mapping["matches"][0]["route"], "/info/encyclopedia/315.xml")

            connection.request("GET", "/%2e%2e%2fREADME.md")
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            self.assertIn(b"path traversal", response.read())

            connection.request("GET", "/not-collected-anywhere")
            response = connection.getresponse()
            self.assertEqual(response.status, 404)
            self.assertIn(b"Offline route not collected", response.read())

            connection.request("GET", "/__offline/uncollected?kind=search&query=orc")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.getheader("X-Offline-Entity-Kind"), "uncollected-feature")
            self.assertIn(b"Offline feature not collected", response.read())

            connection.request("GET", "/__offline/missing.html")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.getheader("X-Offline-Entity-Kind"), "generated_placeholder")
            response.read()

            # Runtime paths that were constructed by historical scripts stay
            # local through typed placeholders rather than returning a remote
            # or browser-generated error page.
            connection.request("GET", "/runtime/missing.js")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertTrue(response.getheader("Content-Type", "").startswith("application/javascript"))
            self.assertEqual(response.getheader("X-Offline-Entity-Kind"), "uncollected-script-placeholder")
            response.read()

            connection.request("GET", "/__offline/api/log")
            response = connection.getresponse()
            log = json.loads(response.read())
            self.assertGreaterEqual(log["count"], 5)
            self.assertTrue(any(item.get("route") == "/__offline/rejected" for item in log["entries"]))
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_historical_route_spellings_normalize_without_weakening_security(self) -> None:
        manifest = dict(self.manifest)
        manifest["route_aliases"] = dict(self.manifest.get("route_aliases", {}))
        manifest["route_aliases"].update(
            {
                "/legacy": "/info/encyclopedia/index.xml",
                "/legacy/": "/info/encyclopedia/index.xml",
            }
        )
        server = mirror.OfflineHTTPServer(
            ("127.0.0.1", 0),
            site_dir=self.site,
            manifest=manifest,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)

            for path in (
                "/info//encyclopedia/315.xml",
                "/info/encyclopedia/315.xml%20",
                "/info/encyclopedia/315.xml/",
                "/new-hp/menus//menu1.htm",
                "/new-hp/menus/menu1.htm%20",
            ):
                connection.request("GET", path)
                response = connection.getresponse()
                self.assertEqual(response.status, 200, path)
                self.assertNotIn(b"Offline route rejected", response.read(), path)

            connection.request("GET", "/legacy//")
            response = connection.getresponse()
            self.assertEqual(response.status, 302)
            self.assertEqual(response.getheader("Location"), "/info/encyclopedia/index.xml")
            response.read()

            # An uncollected directory spelling is a normal local gap, not a
            # security rejection caused only by its trailing slash.
            connection.request("GET", "/info/")
            response = connection.getresponse()
            self.assertEqual(response.status, 404)
            self.assertIn(b"Offline route not collected", response.read())

            for path in ("/safe/%2e%2e/315.xml", "/safe/%5c315.xml", "/safe/%00"):
                connection.request("GET", path)
                response = connection.getresponse()
                self.assertEqual(response.status, 400, path)
                self.assertIn(b"path traversal" if "2e" in path else b"path traversal", response.read(), path)
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_root_alias_and_no_source_tree_escape(self) -> None:
        server, thread = self._server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/")
            response = connection.getresponse()
            self.assertEqual(response.status, 302)
            self.assertEqual(response.getheader("Location"), "/info/encyclopedia/index.xml")
            response.read()
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_extra_map_explicit_homepage_alias_overrides_default(self) -> None:
        source_file = self.work / "external-homepage.html"
        source_file.write_text(
            "<!doctype html><html><body><h1>Historical homepage</h1></body></html>\n",
            encoding="utf-8",
        )
        extra_map_path = self.work / "homepage-extra-map.json"
        extra_map_path.write_text(
            json.dumps(
                {
                    "files": [
                        {
                            "logical_url": "http://www.worldofwarcraft.com/index.xml",
                            "local_path": str(source_file.relative_to(ROOT)).replace("\\", "/"),
                            "mime": "text/html; charset=UTF-8",
                            "role": "site_homepage",
                            "route_aliases": {"/": "/index.xml"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        site_dir = self.work / "homepage-site"
        manifest_path = self.work / "homepage-manifest.json"
        manifest = mirror.build_site(
            url_map_path=mirror.DEFAULT_URL_MAP,
            overlay_path=mirror.DEFAULT_OVERLAY,
            site_dir=site_dir,
            manifest_path=manifest_path,
            support_dir=mirror.DEFAULT_SUPPORT,
            extra_map_paths=(extra_map_path,),
        )
        self.assertEqual(manifest["route_aliases"]["/"], "/index.xml")
        self.assertEqual(manifest["route_aliases"]["/index.html"], "/index.xml")
        self.assertIn("/index.xml", {item["route"] for item in manifest["files"]})

        server = mirror.OfflineHTTPServer(
            ("127.0.0.1", 0),
            site_dir=site_dir,
            manifest=manifest,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/")
            response = connection.getresponse()
            self.assertEqual(response.status, 302)
            self.assertEqual(response.getheader("Location"), "/index.xml")
            response.read()
            connection.request("GET", "/index.html")
            response = connection.getresponse()
            self.assertEqual(response.status, 302)
            self.assertEqual(response.getheader("Location"), "/index.xml")
            response.read()
            connection.request("GET", "/index.xml")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertIn(b"Historical homepage", response.read())
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_foreign_root_is_namespaced_and_cannot_replace_primary_homepage(self) -> None:
        main_file = self.work / "primary-homepage.xml"
        foreign_file = self.work / "foreign-homepage.html"
        main_file.write_text("<html><body>Primary homepage</body></html>\n", encoding="utf-8")
        foreign_file.write_text("<html><body>Foreign root</body></html>\n", encoding="utf-8")

        def source(logical: str, path: Path, mime: str) -> dict:
            return {
                "logical_url": logical,
                "local_path": path.relative_to(ROOT).as_posix(),
                "sha256": mirror.sha256_file(path),
                "mime": mime,
                "kind": "html",
            }

        primary_map = self.work / "primary-homepage-map.json"
        primary_map.write_text(json.dumps({"files": [
            {
                **source("http://www.worldofwarcraft.com/index.xml", main_file, "text/html; charset=UTF-8"),
                "route_aliases": ["/"],
            },
        ]}), encoding="utf-8")
        foreign_map = self.work / "foreign-root-map.json"
        foreign_map.write_text(json.dumps({"files": [
            source("http://forums.worldofwarcraft.com/", foreign_file, "text/html; charset=UTF-8"),
        ]}), encoding="utf-8")
        site = self.work / "foreign-root-site"
        manifest_path = self.work / "foreign-root-manifest.json"
        manifest = mirror.build_site(
            url_map_path=primary_map,
            overlay_path=self.work / "missing-foreign-root-overlay.json",
            site_dir=site,
            manifest_path=manifest_path,
            support_dir=mirror.DEFAULT_SUPPORT,
            extra_map_paths=(foreign_map,),
            include_menu_supplement=False,
        )
        foreign_route = "/_origins/forums.worldofwarcraft.com/index.html"
        self.assertEqual(manifest["route_aliases"]["/"], "/index.xml")
        self.assertIn(foreign_route, {item["route"] for item in manifest["files"]})
        self.assertEqual(
            manifest["origin_index"][mirror.origin_key("http://forums.worldofwarcraft.com/")],
            foreign_route,
        )
        self.assertIn("<html><body>Primary homepage</body></html>", (site / "index.xml").read_text(encoding="utf-8"))
        self.assertIn("<html><body>Foreign root</body></html>", (site / foreign_route.lstrip("/")).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
