from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

import export_github_pages as pages  # noqa: E402
import guide_image_collections  # noqa: E402
from test_github_pages_export import GithubPagesExportTests  # noqa: E402
from test_pages_image_overlay import JPEG_1X1  # noqa: E402


GROUPS = [
    (
        "love-is-in-the-air",
        "Love is in the Air",
        "/info/events/loveisintheair/index.html",
        "/info/events/loveisintheair/gallery.html",
        "/info/events/loveisintheair/images/ss1.jpg",
        "20000101000000",
    ),
    (
        "lunar-festival",
        "Lunar Festival",
        "/info/events/lunarnewyears/index.html",
        "/info/events/lunarnewyears/gallery.html",
        "/info/events/lunarnewyears/images/ss1.jpg",
        "20060719032007",
    ),
    (
        "world-pvp",
        "World PvP",
        "/pvp/worldpvp/index.xml",
        "/pvp/worldpvp/worldpvp-gallery.html",
        "/pvp/worldpvp/images/ss1.jpg",
        "20080402030650",
    ),
]


class GuideImageCollectionTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path, Path, Path, list[dict]]:
        base, site, manifest_path = GithubPagesExportTests()._fixture(base)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        image_sha = hashlib.sha256(JPEG_1X1).hexdigest()
        accepted_images: list[dict] = []
        overlays: list[dict] = []
        source_map_items: list[dict] = []
        groups: list[dict] = []
        payload_dir = base / "guide-collection-inputs" / "accepted-payloads"
        payload_dir.mkdir(parents=True, exist_ok=True)

        for index, (group_id, label, guide_route, gallery_route, image_route, capture) in enumerate(GROUPS):
            guide_path = site / guide_route.lstrip("/")
            gallery_path = site / gallery_route.lstrip("/")
            guide_path.parent.mkdir(parents=True, exist_ok=True)
            gallery_path.parent.mkdir(parents=True, exist_ok=True)
            guide_data = (
                f'<html><head><title>{label}</title></head><body>'
                f'<a href="{gallery_route}#1"><img src="{image_route}"></a>'
                "</body></html>"
            ).encode("utf-8")
            gallery_data = (
                f'<html><head><title>{label} gallery</title></head><body>'
                f'<div id="dynamic-gallery">addshots("{image_route.rsplit("/", 1)[0]}/","ss",1);</div>'
                "</body></html>"
            ).encode("utf-8")
            guide_path.write_bytes(guide_data)
            gallery_path.write_bytes(gallery_data)
            self._add_record(manifest, guide_route, guide_route.lstrip("/"), guide_data, "html", "text/html; charset=UTF-8")
            self._add_record(manifest, gallery_route, gallery_route.lstrip("/"), gallery_data, "html", "text/html; charset=UTF-8")

            original = f"http://www.worldofwarcraft.com:80{image_route}"
            payload_path = payload_dir / f"{group_id}.jpg"
            payload_path.write_bytes(JPEG_1X1)
            payload_relative = payload_path.relative_to(base).as_posix()
            accepted_images.append(
                {
                    "original": original,
                    "actual_capture_timestamp": capture,
                    "mime": "image/jpeg",
                    "length": len(JPEG_1X1),
                    "sha256": image_sha,
                    "private_payload_path": payload_relative,
                    "accepted": True,
                }
            )
            overlays.append(
                {
                    "route": image_route,
                    "original_url": original,
                    "source_sha256": image_sha,
                    "source_length": len(JPEG_1X1),
                    "actual_timestamp": capture,
                    "indexed_capture_timestamp": capture,
                    "supplement_strategy": "explicit_supplement_image_overlay",
                    "data": JPEG_1X1,
                    "mime": "image/jpeg",
                }
            )
            source_map_items.append(
                {
                    "kind": "image",
                    "logical_url": original,
                    "original": original,
                    "local_path": payload_relative,
                    "actual_timestamp": capture,
                    "indexed_capture_timestamp": capture,
                    "sha256": image_sha,
                    "length": len(JPEG_1X1),
                    "mime": "image/jpeg",
                    "temporal_class": "pre_2008" if capture < "20080101000000" else "baseline_2008",
                }
            )
            groups.append(
                {
                    "group_id": group_id,
                    "label": label,
                    "guide_route": guide_route,
                    "gallery_route": gallery_route,
                    "images": [
                        {
                            "route": image_route,
                            "original": original,
                            "sha256": image_sha,
                            "length": len(JPEG_1X1),
                            "actual_capture_timestamp": capture,
                            "source_acceptance_path": "guide-collection-inputs/root-guide-images-acceptance.json",
                        }
                    ],
                }
            )

        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        acceptance_path = base / "guide-collection-inputs/root-guide-images-acceptance.json"
        acceptance_path.parent.mkdir(parents=True, exist_ok=True)
        acceptance_path.write_text(
            json.dumps({"accepted": True, "accepted_images": accepted_images}, indent=2),
            encoding="utf-8",
        )
        manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        acceptance_sha = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()
        map_path = base / "guide-collection-inputs/guide-image-collections.json"
        map_path.write_text(
            json.dumps(
                {
                    "schema": "wow-recovery.guide-image-collections.v1",
                    "source_manifest": {"path": str(manifest_path.relative_to(base)), "sha256": manifest_sha},
                    "anchor_timestamp": "20080512210044",
                    "source_acceptances": [
                        {
                            "path": str(acceptance_path.relative_to(base)),
                            "sha256": acceptance_sha,
                        }
                    ],
                    "groups": groups,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        overlay_map = base / "guide-collection-inputs/supplement-map.json"
        overlay_map.write_text(json.dumps({"items": source_map_items}, indent=2), encoding="utf-8")
        return base, site, manifest_path, map_path, overlay_map, overlays

    @staticmethod
    def _add_record(manifest: dict, route: str, relative: str, data: bytes, kind: str, mime: str) -> None:
        manifest["files"].append(
            {
                "route": route,
                "output_path": "offline/site/" + relative,
                "derived_sha256": hashlib.sha256(data).hexdigest(),
                "derived_length": len(data),
                "mime": mime,
                "kind": kind,
                "source_base_url": "http://www.worldofwarcraft.com" + route,
            }
        )

    def _load(self, base: Path, site: Path, manifest: Path, map_path: Path, overlays: list[dict]) -> guide_image_collections.GuideImageCollectionBundle:
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        route_to_static = {
            str(item["route"]): "/BASE/" + str(item["route"]).lstrip("/") + (".html" if str(item["route"]).endswith(".xml") else "")
            for item in manifest_payload["files"]
        }
        for overlay in overlays:
            route_to_static[overlay["route"]] = "/BASE/" + overlay["route"].lstrip("/")
        return guide_image_collections.load_guide_image_collection_map(
            map_path,
            workspace_root=base,
            manifest_path=manifest,
            manifest=manifest_payload,
            overlays=overlays,
            route_to_static=route_to_static,
            base_path="/BASE/",
        )

    def test_valid_early_capture_and_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path, _overlay_map, overlays = self._fixture(Path(tmp))
            bundle = self._load(base, site, manifest, map_path, overlays)
            self.assertEqual(bundle.image_count, 3)
            self.assertEqual(len(bundle.groups), 3)
            self.assertEqual(bundle.groups[0].images[0].capture_timestamp, "20000101000000")
            self.assertEqual(bundle.groups[0].images[0].original, "http://www.worldofwarcraft.com:80/info/events/loveisintheair/images/ss1.jpg")
            self.assertEqual(bundle.provenance()["groups"][0]["images"][0]["original"], bundle.groups[0].images[0].original)
            for group in bundle.groups:
                for role in ("guide", "gallery"):
                    section = guide_image_collections.render_guide_image_section(group, role)
                    self.assertEqual(section.count("Guide images"), 1)
                    self.assertIn("Open an image to view its original size.", section)
                    self.assertIn("loading=\"lazy\"", section)
                self.assertNotIn("/ss/ss1", guide_image_collections.render_guide_image_section(group, "guide"))

    def test_rejects_wrong_host_path_number_date_hash_receipt_traversal_and_duplicate(self) -> None:
        cases = {
            "host": lambda payload: payload["groups"][0]["images"][0].update(original="https://evil.example/info/events/loveisintheair/images/ss1.jpg"),
            "path": lambda payload: payload["groups"][0]["images"][0].update(route="/info/events/loveisintheair/images/ss/thumb/ss1.jpg", original="http://www.worldofwarcraft.com/info/events/loveisintheair/images/ss/thumb/ss1.jpg"),
            "number": lambda payload: payload["groups"][0]["images"][0].update(route="/info/events/loveisintheair/images/ss13.jpg", original="http://www.worldofwarcraft.com/info/events/loveisintheair/images/ss13.jpg"),
            "date": lambda payload: payload["groups"][0]["images"][0].update(actual_capture_timestamp="20080512210045"),
            "hash": lambda payload: payload["groups"][0]["images"][0].update(sha256="0" * 64),
            "receipt": lambda payload: payload["source_acceptances"][0].update(sha256="0" * 64),
            "traversal": lambda payload: payload["source_manifest"].update(path="../outside.json"),
            "duplicate": lambda payload: payload["groups"][0]["images"].append(copy.deepcopy(payload["groups"][0]["images"][0])),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                base, site, manifest, map_path, _overlay_map, overlays = self._fixture(Path(tmp))
                payload = json.loads(map_path.read_text(encoding="utf-8"))
                mutate(payload)
                bad_map = base / f"guide-collection-inputs/bad-{name}.json"
                bad_map.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(guide_image_collections.GuideImageCollectionError):
                    self._load(base, site, manifest, bad_map, overlays)

    def test_production_receipt_without_route_and_rejects_wrong_source_or_unaccepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path, _overlay_map, overlays = self._fixture(Path(tmp))
            bundle = self._load(base, site, manifest, map_path, overlays)
            self.assertEqual(bundle.image_count, 3)

            wrong_path_payload = json.loads(map_path.read_text(encoding="utf-8"))
            wrong_path_payload["groups"][0]["images"][0]["source_acceptance_path"] = "guide-collection-inputs/not-the-bound-receipt.json"
            wrong_path = base / "guide-collection-inputs/bad-wrong-source-path.json"
            wrong_path.write_text(json.dumps(wrong_path_payload), encoding="utf-8")
            with self.assertRaises(guide_image_collections.GuideImageCollectionError):
                self._load(base, site, manifest, wrong_path, overlays)

            receipt_path = base / "guide-collection-inputs/root-guide-images-acceptance.json"
            receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_payload["accepted"] = False
            receipt_path.write_text(json.dumps(receipt_payload, indent=2), encoding="utf-8")
            unaccepted_payload = json.loads(map_path.read_text(encoding="utf-8"))
            unaccepted_payload["source_acceptances"][0]["sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            unaccepted_path = base / "guide-collection-inputs/bad-unaccepted-receipt.json"
            unaccepted_path.write_text(json.dumps(unaccepted_payload), encoding="utf-8")
            with self.assertRaises(guide_image_collections.GuideImageCollectionError):
                self._load(base, site, manifest, unaccepted_path, overlays)

    def test_exporter_hook_uses_supplement_loader_and_preserves_addshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path, overlay_map, _overlays = self._fixture(Path(tmp))
            output = base / "pages"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
                supplement_image_source_maps=[overlay_map],
                guide_image_collection_map=map_path,
            )
            self.assertEqual(result["stats"]["guide_image_collection_pages"], 6)
            self.assertEqual(result["stats"]["guide_image_collection_images"], 3)
            for _group_id, _label, guide_route, gallery_route, _image_route, _capture in GROUPS:
                for route in (guide_route, gallery_route):
                    relative = pages.static_rel_for_route(route, {"kind": "html"})
                    page = (output / relative).read_text(encoding="utf-8")
                    self.assertEqual(page.count('class="offline-guide-image-collection"'), 1)
                    self.assertEqual(page.count("Guide images"), 1)
                gallery = (output / pages.static_rel_for_route(gallery_route, {"kind": "html"})).read_text(encoding="utf-8")
                self.assertIn("addshots(", gallery)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(provenance["guide_image_collections"]["group_count"], 3)
            self.assertEqual(provenance["guide_image_collections"]["image_count"], 3)
            self.assertEqual(provenance["stats"]["guide_image_collection_pages"], 6)

    def test_none_map_keeps_old_export_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, _map_path, _overlay_map, _overlays = self._fixture(Path(tmp))
            output = base / "plain"
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                max_bytes=500_000_000,
            )
            gallery = (output / "info/events/loveisintheair/gallery.html").read_text(encoding="utf-8")
            self.assertIn("addshots(", gallery)
            self.assertNotIn("offline-guide-image-collection", gallery)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            self.assertNotIn("guide_image_collections", provenance)


if __name__ == "__main__":
    unittest.main()
