from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import related_faction_icons as legacy
import related_faction_item_extension as extension


def fixture(root: Path) -> Path:
    relative = extension.MAP_RELATIVE
    path = root / relative
    path.parent.mkdir(parents=True)
    for name in ("input-map.json", "source-payloads.zip"):
        (path.parent / name).write_bytes((ROOT / relative).parent.joinpath(name).read_bytes())
    receipt = root / "docs/evidence/faction-item-art-20261025.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_bytes((ROOT / "docs/evidence/faction-item-art-20261025.json").read_bytes())
    return path


def base_bundle():
    assets = tuple(legacy.RelatedFactionIconAsset(
        route=f"/old{i}.jpg", relative=f"old{i}.jpg", target_route=f"/original{i}.gif",
        data=b"legacy" + bytes([i]), mime="image/jpeg", metadata={"role": "fixture"},
    ) for i in range(3))
    return legacy.RelatedFactionIconBundle(
        assets=assets, route_reuses={a.target_route: a.route for a in assets},
        catalog_relative=legacy.EXPECTED_CATALOG_RELATIVE, catalog_bytes=b"baseline",
        estimated_bytes=0, source_metadata={"source_label": "fixture"},
        notice_by_page={"/unaffected.html": "original notice"}, map_sha256="old",
        decision_sha256="old-decision", source_acceptance_sha256="old-acceptance",
    )


class FactionItemExtensionTests(unittest.TestCase):
    def test_exact_seven_images_and_original_routes(self):
        assets = extension.load_additional_assets(extension.MAP_RELATIVE, ROOT)
        self.assertEqual(len(assets), 7)
        self.assertEqual(sum(len(a.data) for a in assets), 15498)
        self.assertEqual(sum(a.mime == "image/jpeg" for a in assets), 6)
        self.assertEqual(sum(a.mime == "image/png" for a in assets), 1)
        for asset in assets:
            self.assertEqual(hashlib.sha256(asset.data).hexdigest(), asset.metadata["sha256"])
            self.assertTrue(asset.target_route.startswith("/info/basics/factions/images/icons/"))
        conquest = next(a for a in assets if a.metadata["name"] == "Mark of Conquest")
        self.assertEqual(conquest.metadata["item_ids"], [27921])
        self.assertEqual(conquest.metadata["icon_id"], "inv_misc_armorkit_12")
        self.assertEqual(conquest.metadata["display_size"], [36, 36])
        token = next(a for a in assets if a.metadata["icon_id"] == "inv_misc_token_honorhold")
        self.assertEqual(token.metadata["display_size"], [16, 16])

    def test_map_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = fixture(root)
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(legacy.RelatedFactionIconError, "map SHA-256"):
                extension.load_additional_assets(path, root)

    def test_zip_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = fixture(root)
            zipped = path.parent / "source-payloads.zip"
            raw = bytearray(zipped.read_bytes())
            raw[100] ^= 1
            zipped.write_bytes(raw)
            with self.assertRaisesRegex(legacy.RelatedFactionIconError, "ZIP SHA-256"):
                extension.load_additional_assets(path, root)

    def test_cumulative_bundle_preserves_old_assets_routes_and_unaffected_note(self):
        baseline = base_bundle()
        result = extension.extend_bundle(extension.MAP_RELATIVE, ROOT, "/archive/", baseline)
        self.assertEqual(result.assets[:3], baseline.assets)
        for route, target in baseline.route_reuses.items():
            self.assertEqual(result.route_reuses[route], target)
        self.assertEqual(result.notice_by_page["/unaffected.html"], "original notice")
        self.assertEqual(len(result.assets), 10)
        self.assertEqual(len(result.route_reuses), 10)
        self.assertEqual(result.source_metadata["original_2008_images_recovered"], 0)
        self.assertIn("/archive/__offline/related-faction-icons.json", result.notice_by_page[next(iter(extension.PAGES))])
        note = result.notice_by_page[next(iter(extension.PAGES))]
        self.assertIn('inv_misc_token_honorhold.jpg"]{width:16px;height:16px;', note)
        self.assertIn('inv_relics_libramoftruth.jpg"]{width:36px;height:36px;', note)
        self.assertNotIn('inv_misc_armorkit_11', note)

    def test_cumulative_bundle_rejects_target_collision(self):
        baseline = base_bundle()
        route = extension.load_additional_assets(extension.MAP_RELATIVE, ROOT)[0].target_route
        routes = dict(baseline.route_reuses)
        routes[route] = routes.pop("/original0.gif")
        with self.assertRaisesRegex(legacy.RelatedFactionIconError, "collides"):
            extension.extend_bundle(extension.MAP_RELATIVE, ROOT, "/", replace(baseline, route_reuses=routes))


if __name__ == "__main__":
    unittest.main()
