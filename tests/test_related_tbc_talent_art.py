from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import related_tbc_talent_art as art  # noqa: E402
import export_github_pages as pages  # noqa: E402


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _one_pixel_png(*, animated: bool = False) -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    parts = [art.PNG_SIGNATURE, _chunk(b"IHDR", ihdr)]
    if animated:
        parts.append(_chunk(b"acTL", struct.pack(">II", 1, 0)))
    parts.extend((_chunk(b"IDAT", zlib.compress(bytes((0, 240, 120, 60, 128)))), _chunk(b"IEND", b"")))
    return b"".join(parts)


def _fixture(root: Path, *, member_name: str | None = None, png_bytes: bytes | None = None):
    png = png_bytes or _one_pixel_png()
    source_path = "WoW Talent Calculator TBC/Textures/Icons/Spell_Test.png"
    zip_member = "icons/Spell_Test.png"
    member = member_name or zip_member
    icon = {
        "icon_id": "Spell_Test",
        "source_path": source_path,
        "source_length": len(png),
        "git_blob_sha1": art._git_blob_sha1(png),
        "png_width": 1,
        "png_height": 1,
        "zip_member": zip_member,
    }
    talent = {
        "class": "Druid",
        "class_slug": "druid",
        "name": "Test Talent",
        "specializations": ["Balance"],
        "icon_id": "Spell_Test",
        "source_path": source_path,
        "active_route": "/shared/global/talents/druid/images/balance/testtalent.jpg",
        "off_route": "/shared/global/talents/druid/images/balance/testtalent-off.jpg",
    }
    pins_digest = art._sha256(art._canonical_json_bytes(art._normalize_source_pins([icon])))
    targets_digest = art._sha256(art._canonical_json_bytes(art._normalize_talent_mappings([talent])))
    expectations = art._Expectations(
        repository=art.EXPECTED_SOURCE_REPOSITORY,
        commit=art.EXPECTED_SOURCE_COMMIT,
        classification=art.EXPECTED_SOURCE_CLASSIFICATION,
        candidate_acceptance_sha256=art.EXPECTED_CANDIDATE_ACCEPTANCE_SHA256,
        candidate_audit_sha256=art.EXPECTED_CANDIDATE_AUDIT_SHA256,
        source_manifest_sha256=art.EXPECTED_SOURCE_MANIFEST_SHA256,
        source_pinset_sha256=pins_digest,
        talent_mapping_sha256=targets_digest,
        icon_count=1,
        talent_count=1,
        route_reuse_count=2,
    )
    zip_path = root / art.EXPECTED_ZIP_FILENAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, png)
    zip_bytes = zip_path.read_bytes()
    source_zip = {
        "filename": art.EXPECTED_ZIP_FILENAME,
        "length": len(zip_bytes),
        "sha256": hashlib.sha256(zip_bytes).hexdigest(),
    }
    map_data = {
        "schema": art.EXPECTED_MAP_SCHEMA,
        "source": {
            "repository": expectations.repository,
            "commit": expectations.commit,
            "classification": expectations.classification,
            "candidate_acceptance_sha256": expectations.candidate_acceptance_sha256,
            "candidate_audit_sha256": expectations.candidate_audit_sha256,
        },
        "source_guard": {"source_manifest_sha256": expectations.source_manifest_sha256},
        "source_zip": source_zip,
        "source_rows_sha256": pins_digest,
        "talent_rows_sha256": targets_digest,
        "icons": [icon],
        "talents": [talent],
    }
    map_path = root / "input-map.json"
    map_path.write_text(json.dumps(map_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return map_path, expectations, png, map_data


def _minimal_export_fixture(root: Path):
    site = root / "offline" / "site"
    site.mkdir(parents=True)
    text = '<html><head><title>Export fixture</title></head><body><p>ok</p></body></html>'
    data = text.encode("utf-8")
    (site / "index.html").write_bytes(data)
    record = {
        "route": "/index.html",
        "output_path": "offline/site/index.html",
        "derived_sha256": hashlib.sha256(data).hexdigest(),
        "derived_length": len(data),
        "mime": "text/html; charset=UTF-8",
        "kind": "html",
        "source_base_url": "http://www.worldofwarcraft.com/index.html",
    }
    manifest = {
        "schema_version": 1,
        "anchor_timestamp": "20080512210044",
        "route_aliases": {"/": "/index.html"},
        "origin_index": {},
        "files": [record],
    }
    manifest_path = root / "offline" / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return site, manifest_path


class RelatedTbcTalentArtTests(unittest.TestCase):
    def test_loader_preserves_png_and_builds_embedded_srgb_grayscale_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, expected, png, _map_data = _fixture(root)
            bundle = art._load_bundle_with_expectations(
                map_path, root, "/WOW-Encyclopedia-Deployable-Archive", expected.source_manifest_sha256, expected,
            )

            self.assertEqual(bundle.icon_count, 1)
            self.assertEqual(bundle.talent_count, 1)
            self.assertEqual(len(bundle.route_reuses), 2)
            png_asset = next(asset for asset in bundle.assets if asset.mime == "image/png")
            svg_asset = next(asset for asset in bundle.assets if asset.mime.startswith("image/svg+xml"))
            self.assertEqual(png_asset.data, png)
            self.assertEqual(png_asset.route, "/__offline/related-tbc-talent-art/Spell_Test.png")
            self.assertEqual(
                bundle.route_reuses["/shared/global/talents/druid/images/balance/testtalent.jpg"],
                png_asset.route,
            )
            self.assertEqual(
                bundle.route_reuses["/shared/global/talents/druid/images/balance/testtalent-off.jpg"],
                "/__offline/related-tbc-talent-art/Spell_Test-off.svg",
            )

            svg = ET.fromstring(svg_asset.data)
            ns = {"s": "http://www.w3.org/2000/svg"}
            filter_node = svg.find("s:defs/s:filter", ns)
            matrix = svg.find("s:defs/s:filter/s:feColorMatrix", ns)
            image = svg.find("s:image", ns)
            self.assertIsNotNone(filter_node)
            self.assertIsNotNone(matrix)
            self.assertIsNotNone(image)
            self.assertEqual(filter_node.attrib["color-interpolation-filters"], "sRGB")
            self.assertEqual(matrix.attrib["values"], art.GRAYSCALE_MATRIX)
            self.assertEqual(matrix.attrib["values"].split()[-5:], ["0", "0", "0", "1", "0"])
            self.assertTrue(image.attrib["href"].startswith("data:image/png;base64,"))
            self.assertEqual(base64.b64decode(image.attrib["href"].split(",", 1)[1]), png)
            self.assertNotIn("<script", svg_asset.data.decode("utf-8").lower())
            self.assertNotIn("http://", image.attrib["href"])
            catalog = json.loads(bundle.catalog_bytes)
            self.assertEqual(catalog["off_state_derivation"]["alpha_preserved"], True)
            self.assertEqual(catalog["off_state_derivation"]["original_2008_image_recovered"], False)

    def test_loader_rejects_actual_source_manifest_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, expected, _png, _map_data = _fixture(root)
            with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "actual source manifest SHA-256"):
                art._load_bundle_with_expectations(map_path, root, "", "0" * 64, expected)

    def test_loader_rejects_accepted_map_sha_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, expected, _png, _map_data = _fixture(root)
            pinned = replace(expected, map_sha256="0" * 64)
            with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "input map SHA-256"):
                art._load_bundle_with_expectations(
                    map_path, root, "", expected.source_manifest_sha256, pinned,
                )

    def test_loader_rejects_a_non_whitelisted_zip_member(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, expected, _png, _map_data = _fixture(root, member_name="../outside.png")
            with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "member set differs"):
                art._load_bundle_with_expectations(
                    map_path, root, "", expected.source_manifest_sha256, expected,
                )
            self.assertFalse((root.parent / "outside.png").exists())

    def test_loader_rejects_source_byte_drift_even_when_zip_hash_is_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = _one_pixel_png()
            drifted = original[:-1] + bytes((original[-1] ^ 1,))
            map_path, expected, _png, map_data = _fixture(root, png_bytes=original)
            with zipfile.ZipFile(root / art.EXPECTED_ZIP_FILENAME, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("icons/Spell_Test.png", drifted)
            zip_bytes = (root / art.EXPECTED_ZIP_FILENAME).read_bytes()
            map_data["source_zip"] = {
                "filename": art.EXPECTED_ZIP_FILENAME,
                "length": len(zip_bytes),
                "sha256": hashlib.sha256(zip_bytes).hexdigest(),
            }
            map_path.write_text(json.dumps(map_data), encoding="utf-8")
            with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "Git blob SHA-1 differs"):
                art._load_bundle_with_expectations(
                    map_path, root, "", expected.source_manifest_sha256, expected,
                )

    def test_loader_rejects_talent_route_mapping_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path, expected, _png, map_data = _fixture(root)
            map_data["talents"][0]["off_route"] = "/shared/global/talents/druid/images/balance/wrong-off.jpg"
            map_path.write_text(json.dumps(map_data), encoding="utf-8")
            with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "65-name audit"):
                art._load_bundle_with_expectations(
                    map_path, root, "", expected.source_manifest_sha256, expected,
                )

    def test_png_parser_rejects_animated_source(self) -> None:
        with self.assertRaisesRegex(art.RelatedTbcTalentArtError, "animated PNG"):
            art._parse_static_png(_one_pixel_png(animated=True))

    def test_absent_related_notice_preserves_existing_notice_exactly(self) -> None:
        existing = '<p id="existing">Existing source notice.</p>\n'
        self.assertEqual(art.merge_talent_source_notice(existing, None), existing)
        self.assertEqual(
            art.merge_talent_source_notice(existing, "<p>Later TBC.</p>"),
            existing + "\n<p>Later TBC.</p>",
        )

    def test_related_attribution_stays_inside_the_existing_talent_aside(self) -> None:
        existing = '<p id="existing-talent-source">Existing icon source.</p>'
        notice = art.merge_talent_source_notice(existing, art.NOTICE_HTML)
        html, inserted = pages.annotate_related_talent_icons(
            "<html><body><h1>Talents</h1></body></html>",
            route="/info/classes/druid/talents.html",
            notice_html=notice,
        )
        self.assertTrue(inserted)
        self.assertEqual(html.count('id="__offline-related-talent-icons"'), 1)
        self.assertIn("Existing icon source.", html)
        self.assertIn("TBC calculator archive (2019)", html)
        source_link = ET.fromstring(html).find(".//a")
        self.assertEqual(source_link.attrib["href"], art.EXPECTED_SOURCE_REPOSITORY + "/tree/" + art.EXPECTED_SOURCE_COMMIT)
        self.assertEqual(source_link.attrib["style"], "color:#255075;text-decoration:underline")
        self.assertNotRegex("".join(ET.fromstring(html).itertext()), r"\b[0-9a-f]{40}\b")

    def test_no_map_export_keeps_existing_route_stats_and_provenance_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site, manifest = _minimal_export_fixture(root)
            output = root / "pages"
            result = pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=root,
                max_bytes=None,
                min_free_bytes=0,
            )
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertNotIn("related_tbc_talent_art", provenance)
            self.assertNotIn("related_tbc_talent_art_pngs", result["stats"])
            self.assertNotIn("related_tbc_talent_art_off_svgs", result["stats"])
            self.assertFalse(any("related-tbc-talent-art" in route for route in route_map["routes"]))

    def test_tbc_art_map_requires_the_existing_talent_icon_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site, manifest = _minimal_export_fixture(root)
            with self.assertRaisesRegex(pages.PagesExportError, "requires the accepted related talent icon map"):
                pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=root / "pages",
                    workspace_root=root,
                    max_bytes=None,
                    min_free_bytes=0,
                    related_tbc_talent_art_map=root / "intentionally-not-opened.json",
                )


if __name__ == "__main__":
    unittest.main()
