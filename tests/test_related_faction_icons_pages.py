"""Exercise the faction supplement at the real exporter boundary."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import export_github_pages as pages
import related_faction_icons
from test_github_pages_export import GithubPagesExportTests

MAP = ROOT / "research/continuous-recovery-20261022/integration/related-faction-icons-v54/input-map.json"


class RelatedFactionPagesTests(unittest.TestCase):
    def fixture(self, root):
        root, site, manifest = GithubPagesExportTests()._fixture(root)
        bundle = related_faction_icons.load_related_faction_icon_bundle(
            MAP, ROOT, "/WOW-Encyclopedia-Deployable-Archive/"
        )
        data = json.loads(manifest.read_bytes())
        for route in bundle.notice_by_page:
            relative = route.lstrip("/")
            images = "".join(
                '<img src="/__offline/missing-image.svg?requested='
                + quote("http://www.worldofwarcraft.com" + target, safe="") + '">'
                for target in bundle.route_reuses
            )
            body = ("<html><head><title>Rewards</title></head><body>" + images + "</body></html>").encode()
            target = site / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            data["files"].append({
                "route": route, "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(body).hexdigest(),
                "derived_length": len(body), "kind": "html", "mime": "text/html; charset=UTF-8",
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            })
            data["origin_index"]["www.worldofwarcraft.com" + route] = route
        manifest.write_bytes(json.dumps(data).encode())
        source = dict(bundle.source_metadata)
        source["source_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        bundle = replace(bundle, source_metadata=source)
        return root, site, manifest, bundle

    def run_export(self, root, site, manifest, bundle):
        with mock.patch.object(
            pages.related_faction_icons, "load_related_faction_icon_bundle", return_value=bundle,
        ):
            return pages.export_pages(
                source_site=site, manifest_path=manifest, output=root / "out",
                workspace_root=root, min_free_bytes=0, related_faction_icon_map=Path("reviewed.json"),
            )

    def test_real_bundle_bytes_routes_notices_and_attribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root, site, manifest, bundle = self.fixture(Path(temp))
            result = self.run_export(root, site, manifest, bundle)
            self.assertEqual(result["stats"]["related_faction_icon_assets"], 3)
            self.assertEqual(result["stats"]["related_faction_icon_notice_pages"], 11)
            out = root / "out"
            route_map = json.loads((out / "__offline/route-map.json").read_bytes())
            routes = route_map["routes"]
            for asset in bundle.assets:
                self.assertEqual((out / asset.relative).read_bytes(), asset.data)
                self.assertEqual(routes[asset.target_route], routes[asset.route])
                self.assertFalse((out / asset.target_route.lstrip("/")).exists())
            provenance = json.loads((out / "export-provenance.json").read_bytes())
            self.assertEqual(provenance["related_faction_icons"]["original_2008_images_recovered"], 0)
            self.assertEqual(provenance["related_faction_icons"]["image_count"], 3)
            for route in bundle.notice_by_page:
                relative = routes[route].removeprefix("/WOW-Encyclopedia-Deployable-Archive/")
                text = (out / relative).read_text()
                self.assertEqual(text.count('id="__offline-related-faction-icons"'), 1)
                self.assertIn("2015", text)
                self.assertIn("/__offline/related-faction-icons.json", text)
                for asset in bundle.assets:
                    self.assertIn(asset.route, text)

    def test_existing_target_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root, site, manifest, bundle = self.fixture(Path(temp))
            reused = dict(bundle.route_reuses)
            reused["/style.css"] = bundle.assets[0].route
            bundle = replace(bundle, route_reuses=reused)
            with self.assertRaisesRegex(pages.PagesExportError, "target collides"):
                self.run_export(root, site, manifest, bundle)
            self.assertFalse((root / "out").exists())

    def test_wrong_source_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root, site, manifest, bundle = self.fixture(Path(temp))
            bundle = replace(bundle, source_metadata={**bundle.source_metadata, "source_manifest_sha256": "0" * 64})
            with self.assertRaisesRegex(pages.PagesExportError, "accepted source manifest"):
                self.run_export(root, site, manifest, bundle)
            self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
