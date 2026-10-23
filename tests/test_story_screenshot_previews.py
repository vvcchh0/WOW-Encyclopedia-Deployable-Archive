from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

import export_github_pages as pages  # noqa: E402
import guide_image_collections as collections  # noqa: E402


BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
LOVE_ROUTE = "/info/events/loveisintheair/index.html"
LOVE_ALIAS = "/info/events/loveisintheair/"
LOVE_IMAGES = "/info/events/loveisintheair/images/"
SCREENSHOT_SOURCE = ROOT / "offline/site/shared/wow-com/includes-client/screenshot.js"


class LoveStoryScreenshotPreviewTests(unittest.TestCase):
    def _bundle(self) -> tuple[collections.GuideImageCollectionBundle, dict[str, str]]:
        images = tuple(
            collections.GuideImage(
                route=f"{LOVE_IMAGES}ss{number}.jpg",
                original=f"http://www.worldofwarcraft.com{LOVE_IMAGES}ss{number}.jpg",
                sha256=hashlib.sha256(f"image-{number}".encode()).hexdigest(),
                length=100 + number,
                capture_timestamp="20070104223456",
                static_url=f"{BASE_PATH}{LOVE_IMAGES.lstrip('/')}ss{number}.jpg",
            )
            for number in range(1, 13)
        )
        group = collections.GuideImageCollectionGroup(
            group_id="love-is-in-the-air",
            label="Love is in the Air",
            guide_route=LOVE_ROUTE,
            gallery_route="/info/events/loveisintheair/gallery.html",
            guide_static_url=f"{BASE_PATH}{LOVE_ROUTE.lstrip('/')}",
            gallery_static_url=f"{BASE_PATH}info/events/loveisintheair/gallery.html",
            images=images,
        )
        bundle = collections.GuideImageCollectionBundle(
            map_path=Path("research/fixture-guide-image-map.json"),
            map_sha256="a" * 64,
            source_manifest_path="offline/build-manifest.json",
            source_manifest_sha256="b" * 64,
            source_acceptances=(),
            anchor_timestamp="20080512210044",
            groups=(group,),
        )
        routes = {image.route: image.static_url for image in images}
        return bundle, routes

    def _render_call(
        self,
        script: str,
        *,
        pathname: str,
        directory: str = "images/",
        number: int = 1,
    ) -> str:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is required to execute the generated legacy document.write script")
        payload = {
            "script": script,
            "pathname": pathname,
            "href": "https://vvcchh0.github.io" + pathname,
            "directory": directory,
            "number": number,
        }
        runner = r"""
const fs = require('fs');
const vm = require('vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const writes = [];
const context = {
  document: {
    location: { href: input.href, pathname: input.pathname },
    write: value => writes.push(String(value))
  },
  number: input.number
};
vm.createContext(context);
vm.runInContext(input.script + '\ntheDirectory = ' + JSON.stringify(input.directory) + '; screenshotsTotal = 12; screenshotThinBorder(number, "", "story caption");', context, { timeout: 2000 });
process.stdout.write(JSON.stringify(writes.join('')));
"""
        completed = subprocess.run(
            [node, "-e", runner],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def _derived_script(
        self,
        *,
        routes: dict[str, str] | None = None,
        page_routes: tuple[str, ...] = (LOVE_ALIAS,),
    ) -> str:
        bundle, default_routes = self._bundle()
        group, fallbacks = collections.love_story_preview_fallbacks(
            bundle,
            route_to_static=default_routes if routes is None else routes,
        )
        original = SCREENSHOT_SOURCE.read_text(encoding="utf-8")
        derived, changed = collections.rewrite_love_story_preview_script(
            original,
            group=group,
            fallbacks=fallbacks,
            base_path=BASE_PATH,
            page_routes=page_routes,
        )
        if fallbacks:
            self.assertTrue(changed)
        return derived

    def test_node_document_write_fallback_requires_exact_prefixed_page_and_directory(self) -> None:
        script = self._derived_script()
        for number in range(1, 13):
            with self.subTest(number=number):
                exact_page = self._render_call(
                    script,
                    pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE,
                    number=number,
                )
                expected = BASE_PATH + LOVE_IMAGES.lstrip("/") + f"ss{number}.jpg"
                self.assertEqual(exact_page.count(f'href = "{expected}"'), 2)
                self.assertIn(f'src = "{expected}"', exact_page)
                self.assertIn(f'href = "{expected}">story caption</a>', exact_page)
                self.assertIn('style = "max-width:200px;height:auto;"', exact_page)
                self.assertNotIn("imageviewer.html", exact_page)

        alias_page = self._render_call(
            script,
            pathname=BASE_PATH.rstrip("/") + LOVE_ALIAS,
        )
        alias_expected = BASE_PATH + LOVE_IMAGES.lstrip("/") + "ss1.jpg"
        self.assertIn(f'src = "{alias_expected}"', alias_page)

        unrelated_page = self._render_call(
            script,
            pathname=BASE_PATH + "info/events/loveisintheair/gallery.html",
        )
        self.assertIn("imageviewer.html?", unrelated_page)
        self.assertIn("ss1-thumb.jpg", unrelated_page)
        self.assertNotIn("max-width:200px", unrelated_page)

        unrelated_directory = self._render_call(
            script,
            pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE,
            directory="images/ss/",
        )
        self.assertIn("imageviewer.html?", unrelated_directory)
        self.assertIn("ss1-thumb.jpg", unrelated_directory)
        self.assertNotIn("max-width:200px", unrelated_directory)

        for number in (0, 13):
            with self.subTest(out_of_range=number):
                out_of_range = self._render_call(
                    script,
                    pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE,
                    number=number,
                )
                self.assertIn("imageviewer.html?", out_of_range)
                self.assertIn(f"ss{number}-thumb.jpg", out_of_range)
                self.assertNotIn("max-width:200px", out_of_range)

    def test_node_preserves_genuine_thumbnail_when_full_route_is_present(self) -> None:
        bundle, routes = self._bundle()
        routes[f"{LOVE_IMAGES}ss1-thumb.jpg"] = f"{BASE_PATH}{LOVE_IMAGES.lstrip('/')}ss1-thumb.jpg"
        group, fallbacks = collections.love_story_preview_fallbacks(bundle, route_to_static=routes)
        self.assertIsNotNone(group)
        self.assertNotIn(1, fallbacks)
        derived, changed = collections.rewrite_love_story_preview_script(
            SCREENSHOT_SOURCE.read_text(encoding="utf-8"),
            group=group,
            fallbacks=fallbacks,
            base_path=BASE_PATH,
            page_routes=(LOVE_ALIAS,),
        )
        self.assertTrue(changed)
        html = self._render_call(derived, pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE)
        self.assertIn("imageviewer.html?", html)
        self.assertIn("ss1-thumb.jpg", html)
        self.assertNotIn("max-width:200px", html)

    def test_node_keeps_legacy_request_when_full_and_thumbnail_routes_are_both_absent(self) -> None:
        bundle, routes = self._bundle()
        routes.pop(f"{LOVE_IMAGES}ss1.jpg")
        group, fallbacks = collections.love_story_preview_fallbacks(bundle, route_to_static=routes)
        self.assertIsNotNone(group)
        self.assertNotIn(1, fallbacks)
        derived, changed = collections.rewrite_love_story_preview_script(
            SCREENSHOT_SOURCE.read_text(encoding="utf-8"),
            group=group,
            fallbacks=fallbacks,
            base_path=BASE_PATH,
            page_routes=(LOVE_ALIAS,),
        )
        self.assertTrue(changed)
        html = self._render_call(derived, pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE)
        self.assertIn("imageviewer.html?", html)
        self.assertIn("ss1-thumb.jpg", html)
        self.assertNotIn("max-width:200px", html)

    def test_exporter_derives_script_and_records_display_count_without_new_originals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            from test_guide_image_collections import GuideImageCollectionTests

            base = Path(tmp)
            base, site, manifest_path, map_path, overlay_map, _overlays = GuideImageCollectionTests()._fixture(base)
            relative = "shared/wow-com/includes-client/screenshot.js"
            target = site / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source_bytes = SCREENSHOT_SOURCE.read_bytes()
            target.write_bytes(source_bytes)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"].append(
                {
                    "route": "/" + relative,
                    "output_path": "offline/site/" + relative,
                    "derived_sha256": hashlib.sha256(source_bytes).hexdigest(),
                    "derived_length": len(source_bytes),
                    "mime": "application/javascript; charset=UTF-8",
                    "kind": "js",
                    "source_base_url": "http://www.worldofwarcraft.com/" + relative,
                }
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            collection_map = json.loads(map_path.read_text(encoding="utf-8"))
            collection_map["source_manifest"]["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            map_path.write_text(json.dumps(collection_map, indent=2), encoding="utf-8")

            output = base / "pages-derived"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest_path,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
                supplement_image_source_maps=[overlay_map],
                guide_image_collection_map=map_path,
            )
            self.assertEqual(result["stats"]["love_story_preview_display_fallbacks"], 1)
            self.assertEqual(result["stats"]["love_story_preview_originals_added"], 0)
            script = (output / relative).read_text(encoding="utf-8")
            self.assertIn("__WOW_LOVE_STORY_PREVIEW_FALLBACKS", script)
            self.assertIn("max-width:200px;height:auto;", script)
            rendered = self._render_call(script, pathname=BASE_PATH.rstrip("/") + LOVE_ROUTE)
            expected = BASE_PATH + LOVE_IMAGES.lstrip("/") + "ss1.jpg"
            self.assertIn(f'src = "{expected}"', rendered)
            self.assertNotIn("imageviewer.html", rendered)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            repair = provenance["love_story_preview_fallbacks"]
            self.assertEqual(repair["display_fallback_count"], 1)
            self.assertEqual(repair["original_payloads_added"], 0)
            self.assertEqual(repair["source_guide_image_map_sha256"], hashlib.sha256(map_path.read_bytes()).hexdigest())
            self.assertEqual(repair["items"][0]["number"], 1)


if __name__ == "__main__":
    unittest.main()
