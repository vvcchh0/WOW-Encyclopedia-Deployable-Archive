from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import related_faction_icons as legacy
import related_faction_item_extension as items
import related_faction_canonical_extension as canonical

class CanonicalFactionArtTests(unittest.TestCase):
    def test_profiles_preserve_all_ten_preexisting_assets_and_targets(self):
        old = legacy.load_related_faction_icon_bundle(items.MAP_RELATIVE, ROOT, "/archive/")
        new = legacy.load_related_faction_icon_bundle(canonical.MAP_RELATIVE, ROOT, "/archive/")
        self.assertEqual(new.assets[:10], old.assets)
        self.assertEqual(len(new.assets), 58)
        self.assertEqual(len(new.route_reuses), 59)
        self.assertTrue(all(new.route_reuses[k] == v for k, v in old.route_reuses.items()))
        self.assertEqual(new.source_metadata["original_2008_images_recovered"], 0)
        for page in old.notice_by_page:
            self.assertIn('inv_misc_token_honorhold.jpg"]{width:16px;height:16px;', new.notice_by_page[page])
            self.assertEqual(new.notice_by_page[page].count('id="__offline-related-faction-icons"'), 1)

    def test_case_and_extension_variants_share_one_verified_image(self):
        bundle = legacy.load_related_faction_icon_bundle(canonical.MAP_RELATIVE, ROOT, "/archive/")
        targets = [canonical.PREFIX + "INV_Relics_LibramofHope.jpg", canonical.PREFIX + "inv_relics_libramofhope.gif"]
        self.assertEqual(bundle.route_reuses[targets[0]], bundle.route_reuses[targets[1]])
        self.assertEqual(sum(a.route == bundle.route_reuses[targets[0]] for a in bundle.assets), 1)
        added = canonical.load_additional_assets(canonical.MAP_RELATIVE, ROOT)
        self.assertEqual(sum(len(a.data) for a in added), canonical.SOURCE_BYTES)
        for asset in added:
            self.assertEqual(hashlib.sha256(asset.data).hexdigest(), asset.metadata["sha256"])
            self.assertEqual(asset.metadata["display_size"], [36, 36])

    def test_target_collision_is_rejected(self):
        base = legacy.load_related_faction_icon_bundle(items.MAP_RELATIVE, ROOT, "/")
        target = canonical.load_additional_assets(canonical.MAP_RELATIVE, ROOT)[0].target_route
        routes = dict(base.route_reuses)
        routes[target] = routes.pop(next(iter(routes)))
        with self.assertRaisesRegex(legacy.RelatedFactionIconError, "collides"):
            canonical.extend_bundle(canonical.MAP_RELATIVE, ROOT, "/", replace(base, route_reuses=routes))

    def test_second_profile_preserves_58_assets_and_adds_48_exact_sources(self):
        old = legacy.load_related_faction_icon_bundle(canonical.MAP_RELATIVE, ROOT, "/archive/")
        new = legacy.load_related_faction_icon_bundle(canonical.MORE_MAP_RELATIVE, ROOT, "/archive/")
        self.assertEqual(new.assets[:58], old.assets)
        self.assertEqual(len(new.assets), 106)
        self.assertEqual(len(new.route_reuses), 107)
        self.assertTrue(all(new.route_reuses[k] == v for k, v in old.route_reuses.items()))
        self.assertEqual(sum(len(a.data) for a in new.assets[58:]), 78665)
        self.assertTrue(all(a.mime == "image/jpeg" for a in new.assets[58:]))
        for page in ("/pvp/rewards-general-armor.html", "/pvp/rewards-veterans-armor.html", "/pvp/rewards-vindicators-armor.html"):
            self.assertIn('width:36px;height:36px;', new.notice_by_page[page])

    def test_map_and_zip_tampering_are_rejected(self):
        for change in ("map", "zip"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / canonical.MAP_RELATIVE
                path.parent.mkdir(parents=True)
                for name in ("input-map.json", "source-payloads.zip"):
                    (path.parent / name).write_bytes((ROOT / canonical.MAP_RELATIVE).parent.joinpath(name).read_bytes())
                receipt = root / canonical.ACCEPTANCE_RELATIVE
                receipt.parent.mkdir(parents=True)
                receipt.write_bytes((ROOT / canonical.ACCEPTANCE_RELATIVE).read_bytes())
                edited = path if change == "map" else path.parent / "source-payloads.zip"
                raw = bytearray(edited.read_bytes())
                raw[70] ^= 1
                edited.write_bytes(raw)
                with self.assertRaisesRegex(legacy.RelatedFactionIconError, "SHA-256"):
                    canonical.load_additional_assets(path, root)

    def test_final_eight_profile_preserves_all_106_prior_assets(self):
        old = legacy.load_related_faction_icon_bundle(canonical.MORE_MAP_RELATIVE, ROOT, "/archive/")
        new = legacy.load_related_faction_icon_bundle(canonical.THIRD_MAP_RELATIVE, ROOT, "/archive/")
        self.assertEqual(new.assets[:106], old.assets)
        self.assertEqual(len(new.assets), 114)
        self.assertEqual(len(new.route_reuses), 115)
        self.assertTrue(all(new.route_reuses[k] == v for k, v in old.route_reuses.items()))
        self.assertEqual(sum(len(a.data) for a in new.assets[106:]), 13620)

if __name__ == "__main__":
    unittest.main()
