from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

import export_github_pages as pages  # noqa: E402
import related_player_gallery_previews as previews  # noqa: E402


PAGE_GROUPS = (
    ("/info/dungeons/cot-hyjal-gallery.html", "Battle for Mount Hyjal", 6),
    ("/info/dungeons/cot-hyjal-gallery.html", "Battle for Mount Hyjal", 6),
    ("/info/dungeons/cot-hyjal-gallery.html", "Battle for Mount Hyjal", 6),
    ("/info/dungeons/cot-escape-gallery.html", "Escape from Durnholde", 15),
    ("/info/dungeons/cot-escape-gallery.html", "Escape from Durnholde", 15),
    ("/info/dungeons/cot-opening-gallery.html", "Opening of the Dark Portal", 16),
    ("/info/dungeons/cot-opening-gallery.html", "Opening of the Dark Portal", 16),
    ("/info/dungeons/cot-opening-gallery.html", "Opening of the Dark Portal", 16),
)


def _jpeg(index: int) -> bytes:
    image = Image.new("RGB", (150, 110))
    for y in range(110):
        for x in range(150):
            image.putpixel((x, y), ((x + index * 21) % 256, (y * 2 + index * 17) % 256, (x + y + index * 31) % 256))
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=77)
    return output.getvalue()


def _fixture(root: Path) -> tuple[Path, dict[str, str], tuple[dict, ...], int]:
    entries = []
    payloads = []
    for index, (page_route, group_label, player_row) in enumerate(PAGE_GROUPS, start=1):
        data = _jpeg(index)
        git_path = f"instance/images/test-{index:02}.jpg"
        member = f"payloads/{index:02}.jpg"
        git_blob_sha = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
        entries.append({
            "archive_member": member,
            "route": f"/{previews.EXPECTED_ASSET_DIRECTORY}/{index:02}.jpg",
            "relative": f"{previews.EXPECTED_ASSET_DIRECTORY}/{index:02}.jpg",
            "git_path": git_path,
            "git_blob_sha1": git_blob_sha,
            "sha256": hashlib.sha256(data).hexdigest(),
            "length": len(data),
            "frames": [[150, 110]],
            "european_gallery_anchor": f"https://example.invalid/fr/gallery#{index}",
            "existing_player_gallery_row": player_row,
            "target_page_route": page_route,
            "group_label": group_label,
            "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
        })
        payloads.append((member, data))
    total_bytes = sum(len(data) for _, data in payloads)
    grouped = {route: count for route, count in previews.EXPECTED_PAGE_COUNTS.items()}
    map_dir = root / "inputs"
    map_dir.mkdir(parents=True, exist_ok=True)
    archive_path = map_dir / "source-payloads.zip"
    with ZipFile(archive_path, "w", compression=ZIP_STORED, allowZip64=False) as archive:
        for member, data in payloads:
            info = ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    archive_bytes = archive_path.read_bytes()
    map_data = {
        "schema": previews.EXPECTED_MAP_SCHEMA,
        "source": {
            "repository": previews.EXPECTED_REPOSITORY,
            "commit": previews.EXPECTED_COMMIT,
            "commit_url": previews.EXPECTED_SOURCE_URL,
            "classification": previews.EXPECTED_SOURCE_CLASSIFICATION,
            "design_decision_sha256": previews.EXPECTED_DESIGN_SHA256,
            "source_acceptance_sha256": previews.EXPECTED_SOURCE_ACCEPTANCE_SHA256,
        },
        "archive": {"path": "source-payloads.zip", "sha256": hashlib.sha256(archive_bytes).hexdigest(), "length": len(archive_bytes)},
        "expected_image_count": len(entries),
        "expected_payload_bytes": total_bytes,
        "page_counts": grouped,
        "items": entries,
    }
    map_path = map_dir / "input-map.json"
    map_path.write_text(json.dumps(map_data, sort_keys=True, indent=2), encoding="utf-8")
    return map_path, {entry["route"]: "/base/" + entry["relative"] for entry in entries}, tuple(entries), total_bytes


class RelatedPlayerGalleryPreviewTests(unittest.TestCase):
    def _load(self, root: Path, map_path: Path):
        _path, _routes, entries, total_bytes = _fixture(root)
        with mock.patch.multiple(
            previews,
            EXPECTED_ITEMS=entries,
            EXPECTED_PAYLOAD_BYTES=total_bytes,
        ):
            bundle = previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")
        return bundle, entries

    def test_bundle_checks_zip_hash_git_blob_and_every_jpeg_frame(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, route_map, entries, total = _fixture(root)
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                bundle = previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")
            self.assertEqual(len(bundle.assets), 8)
            self.assertEqual(sum(len(asset.data) for asset in bundle.assets), total)
            self.assertEqual({route: len(items) for route, items in bundle.assets_by_page.items()}, previews.EXPECTED_PAGE_COUNTS)
            self.assertTrue(all(asset.mime == "image/jpeg" and asset.metadata["decoded_frames"] == 1 for asset in bundle.assets))
            self.assertTrue(all(not asset.route.startswith("/instance/images/") for asset in bundle.assets))
            self.assertEqual(bundle.assets[0].route, entries[0]["route"])
            self.assertEqual(route_map[bundle.assets[0].route], "/base/" + bundle.assets[0].relative)

    def test_map_drift_archive_drift_and_extra_zip_member_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, _route_map, entries, total = _fixture(root)
            map_data = json.loads(map_path.read_text(encoding="utf-8"))
            map_data["items"][0]["target_page_route"] = "/info/dungeons/other.html"
            map_path.write_text(json.dumps(map_data), encoding="utf-8")
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                with self.assertRaisesRegex(previews.RelatedPlayerGalleryPreviewError, "items differ"):
                    previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, _route_map, entries, total = _fixture(root)
            archive_path = map_path.parent / "source-payloads.zip"
            archive_path.write_bytes(archive_path.read_bytes() + b"drift")
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                with self.assertRaisesRegex(previews.RelatedPlayerGalleryPreviewError, "archive length or SHA mismatch"):
                    previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, _route_map, entries, total = _fixture(root)
            map_data = json.loads(map_path.read_text(encoding="utf-8"))
            archive_path = map_path.parent / "source-payloads.zip"
            archive_bytes = archive_path.read_bytes()
            with ZipFile(io.BytesIO(archive_bytes), "r") as source_zip:
                saved = [(info.filename, source_zip.read(info)) for info in source_zip.infolist()]
            rebuilt = io.BytesIO()
            with ZipFile(rebuilt, "w", compression=ZIP_STORED) as archive:
                for member, data in saved + [("payloads/extra.jpg", b"extra")]:
                    info = ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = ZIP_STORED
                    info.create_system = 3
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                    archive.writestr(info, data)
            new_archive = rebuilt.getvalue()
            archive_path.write_bytes(new_archive)
            map_data["archive"]["sha256"] = hashlib.sha256(new_archive).hexdigest()
            map_data["archive"]["length"] = len(new_archive)
            map_path.write_text(json.dumps(map_data), encoding="utf-8")
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                with self.assertRaisesRegex(previews.RelatedPlayerGalleryPreviewError, "ZIP members"):
                    previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")

    def test_preview_section_is_separate_page_scoped_and_keeps_native_gallery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, route_map, entries, total = _fixture(root)
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                bundle = previews.load_related_player_gallery_preview_bundle(map_path, root, "/base/")
            for route, expected_count in previews.EXPECTED_PAGE_COUNTS.items():
                original = '<html><body><center><div id="native-gallery">addshots("/instance/images/","ss",16);</div><span class="contentBlock" style="">native block</span></center><footer>existing footer</footer></body></html>'
                result, changed, count = previews.insert_preview_section(
                    original, page_route=route, bundle=bundle, route_to_static=route_map,
                )
                self.assertTrue(changed)
                self.assertEqual(count, expected_count)
                self.assertEqual(result.count(f'id="{previews.SECTION_ID}"'), 1)
                self.assertLess(result.index(f'id="{previews.SECTION_ID}"'), result.index('<span class="contentBlock"'))
                self.assertLess(result.index("<center>"), result.index(f'id="{previews.SECTION_ID}"'))
                self.assertLess(result.index("</section>"), result.index("</center>"))
                self.assertEqual(result.replace(result[result.index("<section id="):result.index("</section>") + len("</section>")], ""), original)
                self.assertIn("addshots(\"/instance/images/\",\"ss\",16);", result)
                self.assertIn("French guide previews preserved in", result)
                self.assertIn('>Coolwow2</a>.', result)
                self.assertIn(previews.EXPECTED_SOURCE_URL, result)
                self.assertNotIn("pinned commit", result)
                self.assertNotIn("Full screenshot and US gallery sequence identities are unknown", result)
                section_html = result[result.index("<section id="):result.index("</section>") + len("</section>")]
                for asset in bundle.assets_by_page[route]:
                    static = route_map[asset.route]
                    self.assertIn(f'<a href="{static}"><img src="{static}" width="150" height="110"', result)
                    self.assertIn(f'alt="French guide preview: {asset.metadata["group_label"]}"', result)
                untouched, changed, count = previews.insert_preview_section(
                    original, page_route="/info/dungeons/other.html", bundle=bundle, route_to_static=route_map,
                )
                self.assertEqual(untouched, original)
                self.assertFalse(changed)
                self.assertEqual(count, 0)
            with self.assertRaisesRegex(previews.RelatedPlayerGalleryPreviewError, "contentBlock.*found 0"):
                previews.insert_preview_section(
                    "<html><body><center>no marker</center></body></html>",
                    page_route="/info/dungeons/cot-hyjal-gallery.html", bundle=bundle, route_to_static=route_map,
                )
            with self.assertRaisesRegex(previews.RelatedPlayerGalleryPreviewError, "contentBlock.*found 2"):
                previews.insert_preview_section(
                    '<html><body><span class="contentBlock"></span><span class="contentBlock extra"></span></body></html>',
                    page_route="/info/dungeons/cot-hyjal-gallery.html", bundle=bundle, route_to_static=route_map,
                )

    def test_optional_export_writes_only_namespaced_assets_and_preserves_gallery_slots(self) -> None:
        from test_github_pages_export import GithubPagesExportTests

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            base, site, manifest_path = GithubPagesExportTests()._fixture(base)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for route in previews.EXPECTED_PAGE_COUNTS:
                text = '<html><body><center><div id="native-gallery">addshots("/instance/images/","ss",16);</div><span class="contentBlock" style="">native block</span></center></body></html>'
                data = text.encode("utf-8")
                source = site / route.lstrip("/")
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(data)
                manifest["files"].append({
                    "route": route,
                    "output_path": "offline/site/" + route.lstrip("/"),
                    "derived_sha256": hashlib.sha256(data).hexdigest(),
                    "derived_length": len(data),
                    "mime": "text/html; charset=UTF-8",
                    "kind": "html",
                    "source_base_url": "http://www.worldofwarcraft.com" + route,
                })
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            input_map, route_map, entries, total = _fixture(base / "related-preview-inputs")
            output = base / "pages-with-related-gallery-previews"
            with mock.patch.multiple(previews, EXPECTED_ITEMS=entries, EXPECTED_PAYLOAD_BYTES=total):
                result = pages.export_pages(
                    source_site=site,
                    manifest_path=manifest_path,
                    output=output,
                    workspace_root=base,
                    min_free_bytes=0,
                    max_bytes=500_000_000,
                    related_player_gallery_preview_map=input_map,
                )
            self.assertEqual(result["stats"]["related_player_gallery_preview_assets"], 8)
            self.assertEqual(result["stats"]["related_player_gallery_preview_pages"], 3)
            self.assertEqual(result["stats"]["related_player_gallery_preview_displayed"], 8)
            self.assertEqual(result["stats"]["related_player_gallery_preview_original_us_images_added"], 0)
            output_route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))["routes"]
            self.assertTrue(all(entry["route"] in output_route_map for entry in entries))
            self.assertTrue(all(not route.startswith("/instance/images/") for route in output_route_map))
            self.assertFalse((output / "source-payloads.zip").exists())
            for route, expected_count in previews.EXPECTED_PAGE_COUNTS.items():
                output_page = output / pages.static_rel_for_route(route, {"kind": "html"})
                page = output_page.read_text(encoding="utf-8")
                self.assertEqual(page.count(f'id="{previews.SECTION_ID}"'), 1)
                self.assertIn('addshots("/instance/images/","ss",16);', page)
                self.assertEqual(page.count('class="related-player-gallery-preview"'), expected_count)
            export_provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            related = export_provenance["related_player_gallery_previews"]
            self.assertEqual(related["image_count"], 8)
            self.assertEqual(related["original_us_gallery_images_added"], 0)
            self.assertEqual(related["page_counts"], previews.EXPECTED_PAGE_COUNTS)
            self.assertEqual(related["map_sha256"], hashlib.sha256(input_map.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
