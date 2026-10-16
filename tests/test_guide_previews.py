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
import guide_previews  # noqa: E402
import test_github_pages_export as github_export_tests  # noqa: E402
from test_pages_image_overlay import JPEG_1X1  # noqa: E402




GROUPS = [
    ("fishing", "Fishing", "/info/professions/fishing-gallery.html", "/info/professions/fishing.html", ["ss1", "ss53", "ss34", "ss49"]),
    ("hallows-end", "Hallow's End", "/info/events/hallowsend/gallery.html", "/info/events/hallowsend/index.html", ["ss1", "ss22", "ss60", "ss36"]),
    ("brewfest", "Brewfest", "/info/events/brewfest/gallery.html", "/info/events/brewfest/index.html", ["ss1", "ss2", "ss3", "ss4"]),
    ("winters-veil", "Winter's Veil", "/info/events/winterveil/gallery.html", "/info/events/winterveil/index.html", ["ss1", "ss2", "ss3", "ss4"]),
    ("zulaman", "Zul'Aman", "/info/dungeons/zulaman-gallery.html", "/info/dungeons/zulaman.xml", ["ss1", "ss2", "ss3"]),
]


class GuidePreviewTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path, Path]:
        base, site, manifest_path = github_export_tests.GithubPagesExportTests()._fixture(base)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        acceptance: list[dict] = []

        for group_index, (_group_id, _label, gallery_route, guide_route, names) in enumerate(GROUPS):
            guide_relative = guide_route.lstrip("/")
            gallery_relative = gallery_route.lstrip("/")
            guide_path = site / guide_relative
            gallery_path = site / gallery_relative
            guide_path.parent.mkdir(parents=True, exist_ok=True)
            gallery_path.parent.mkdir(parents=True, exist_ok=True)
            image_routes = [
                self._image_route(group_index, _group_id, name)
                for name in names
            ]
            guide_lines = ["<html><head><title>Guide</title></head><body>"]
            for index, route in enumerate(image_routes, 1):
                guide_lines.append(f'<a href="{gallery_route}#{index}"><img src="{route}"></a>')
            guide_lines.append("</body></html>")
            guide_data = "\n".join(guide_lines).encode("utf-8")
            guide_path.write_bytes(guide_data)
            gallery_data = (
                f'<html><head><title>{_label}</title></head><body>'
                f'<div id="dynamic-gallery">addshots("/{_group_id}/","ss",numShots);</div>'
                "</body></html>"
            ).encode("utf-8")
            gallery_path.write_bytes(gallery_data)
            self._add_record(manifest, guide_route, guide_relative, guide_data, "html" if guide_route.endswith(".html") else "xml", "text/html; charset=UTF-8")
            self._add_record(manifest, gallery_route, gallery_relative, gallery_data, "html", "text/html; charset=UTF-8")
            for index, route in enumerate(image_routes):
                relative = route.lstrip("/")
                image_path = site / relative
                image_path.parent.mkdir(parents=True, exist_ok=True)
                image_path.write_bytes(JPEG_1X1)
                capture = f"20080512{group_index:02d}{index:02d}00"
                self._add_record(
                    manifest,
                    route,
                    relative,
                    JPEG_1X1,
                    "image",
                    "image/jpeg",
                    actual_timestamp=capture,
                    transformed=False,
                )
                acceptance.append(
                    {
                        "route": route,
                        "sha256": hashlib.sha256(JPEG_1X1).hexdigest(),
                        "length": len(JPEG_1X1),
                        "capture_from_frozen_manifest": capture,
                        "accepted": True,
                    }
                )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        input_dir = base / "guide-inputs"
        input_dir.mkdir()
        audit_path = input_dir / "nested-preview-audit.json"
        audit_path.write_text(json.dumps({"counts": {"target_count": 19}, "items": []}), encoding="utf-8")
        acceptance_path = input_dir / "root-nested-preview-acceptance.json"
        acceptance_path.write_text(
            json.dumps(
                {
                    "accepted": True,
                    "network_requests": 0,
                    "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
                    "checked": acceptance,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        acceptance_by_route = {item["route"]: item for item in acceptance}
        map_path = input_dir / "guide-previews-source-map.json"
        map_payload = {
            "schema": "wow-recovery.guide-preview-source-map.v1",
            "source_acceptance": {"path": str(acceptance_path.relative_to(base)), "sha256": hashlib.sha256(acceptance_path.read_bytes()).hexdigest()},
            "source_acceptance_sha256": hashlib.sha256(acceptance_path.read_bytes()).hexdigest(),
            "source_audit": {"path": str(audit_path.relative_to(base)), "sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest()},
            "source_audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
            "source_manifest": {"path": str(manifest_path.relative_to(base)), "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest()},
            "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "anchor_timestamp": "20080512210044",
            "groups": [
                {
                    "group_id": group_id,
                    "label": label,
                    "gallery_route": gallery_route,
                    "guide_route": guide_route,
                    "previews": [
                        {
                            "route": route,
                            "sha256": hashlib.sha256(JPEG_1X1).hexdigest(),
                            "length": len(JPEG_1X1),
                            "capture_timestamp": acceptance_by_route[route]["capture_from_frozen_manifest"],
                        }
                        for route in [self._image_route(i, group_id, name) for name in names]
                    ],
                }
                for i, (group_id, label, gallery_route, guide_route, names) in enumerate(GROUPS)
            ],
        }
        map_path.write_text(json.dumps(map_payload, indent=2), encoding="utf-8")
        return base, site, manifest_path, map_path

    @staticmethod
    def _image_route(group_index: int, group_id: str, name: str) -> str:
        roots = {
            "fishing": "/info/professions/images/fishing/ss/thumbs/",
            "hallows-end": "/info/events/hallowsend/images/newscreenshots/thumbs/",
            "brewfest": "/info/events/brewfest/images/ss/thumbs/",
            "winters-veil": "/info/events/winterveil/images/ss/thumbs/",
            "zulaman": "/info/dungeons/images/zulaman/thumbs/",
        }
        return roots[group_id] + name + "-thumb.jpg"

    @staticmethod
    def _add_record(manifest: dict, route: str, relative: str, data: bytes, kind: str, mime: str, *, actual_timestamp: str | None = None, transformed: bool | None = None) -> None:
        record = {
            "route": route,
            "output_path": "offline/site/" + relative,
            "derived_sha256": hashlib.sha256(data).hexdigest(),
            "derived_length": len(data),
            "mime": mime,
            "kind": kind,
            "source_base_url": "http://www.worldofwarcraft.com" + route,
        }
        if actual_timestamp is not None:
            record["actual_timestamp"] = actual_timestamp
        if transformed is not None:
            record["transformed"] = transformed
        manifest["files"].append(record)

    def _export(self, base: Path, site: Path, manifest: Path, output: Path, map_path: Path | None = None) -> dict:
        return pages.export_pages(
            source_site=site,
            manifest_path=manifest,
            output=output,
            workspace_root=base,
            max_bytes=500_000_000,
            min_free_bytes=0,
            guide_preview_map=map_path,
        )

    def test_five_groups_render_xml_guide_and_preserve_dynamic_gallery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path = self._fixture(Path(tmp))
            output = base / "pages"
            result = self._export(base, site, manifest, output, map_path)
            self.assertEqual(result["stats"]["guide_preview_gallery_pages"], 5)
            self.assertEqual(result["stats"]["guide_preview_count"], 19)
            for _group_id, _label, gallery_route, guide_route, _names in GROUPS:
                page = (output / pages.static_rel_for_route(gallery_route, {"kind": "html"})).read_text(encoding="utf-8")
                self.assertEqual(page.count("Preserved guide previews"), 1)
                self.assertEqual(page.count("These previews survive in the original guide pages. Full-size gallery images are still incomplete."), 1)
                self.assertEqual(page.count("View original guide"), 1)
                self.assertIn("addshots(", page)
                self.assertNotIn("ss1.jpg", page)
            zulaman = (output / "info/dungeons/zulaman-gallery.html").read_text(encoding="utf-8")
            self.assertIn(pages.DEFAULT_BASE_PATH + "info/dungeons/zulaman.xml.html", zulaman)
            self.assertNotIn(pages.DEFAULT_BASE_PATH + "info/dungeons/images/zulaman/ss1.jpg", zulaman)
            self.assertEqual(
                (output / "info/dungeons/images/zulaman/thumbs/ss1-thumb.jpg").read_bytes(),
                JPEG_1X1,
            )
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertIn("/info/dungeons/images/zulaman/thumbs/ss1-thumb.jpg", route_map["routes"])
            self.assertNotIn("/info/dungeons/images/zulaman/ss1.jpg", route_map["routes"])
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(provenance["guide_previews"]["preview_count"], 19)
            self.assertEqual(provenance["guide_previews"]["group_count"], 5)

    def test_no_map_has_no_guide_section_and_repeated_exports_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path = self._fixture(Path(tmp))
            no_map = base / "without-map"
            self._export(base, site, manifest, no_map)
            plain = (no_map / "info/professions/fishing-gallery.html").read_bytes()
            self.assertNotIn(b"Preserved guide previews", plain)
            first = base / "first"
            second = base / "second"
            self._export(base, site, manifest, first, map_path)
            self._export(base, site, manifest, second, map_path)
            self.assertEqual(
                (first / "info/professions/fishing-gallery.html").read_bytes(),
                (second / "info/professions/fishing-gallery.html").read_bytes(),
            )

    def test_loader_rejects_bad_sha_date_missing_route_and_parent_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest, map_path = self._fixture(Path(tmp))
            original = json.loads(map_path.read_text(encoding="utf-8"))
            cases = {
                "sha": lambda item: item.update(sha256="0" * 64),
                "date": lambda item: item.update(capture_timestamp="20080230000000"),
                "route": lambda item: item.update(route="/missing/thumbs/not-collected-thumb.jpg"),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    payload = copy.deepcopy(original)
                    mutate(payload["groups"][0]["previews"][0])
                    bad = base / f"bad-{name}.json"
                    bad.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(pages.PagesExportError):
                        self._export(base, site, manifest, base / f"output-{name}", bad)

            guide = site / "info/professions/fishing.html"
            guide.write_text(guide.read_text(encoding="utf-8").replace("/info/professions/images/fishing/ss/thumbs/ss1-thumb.jpg", "/missing.jpg"), encoding="utf-8")
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            guide_record = next(item for item in manifest_payload["files"] if item["route"] == "/info/professions/fishing.html")
            guide_data = guide.read_bytes()
            guide_record["derived_sha256"] = hashlib.sha256(guide_data).hexdigest()
            guide_record["derived_length"] = len(guide_data)
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            changed_manifest_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
            parent_map_payload = json.loads(map_path.read_text(encoding="utf-8"))
            parent_map_payload["source_manifest"]["sha256"] = changed_manifest_sha
            parent_map_payload["source_manifest_sha256"] = changed_manifest_sha
            parent_map = base / "bad-parent.json"
            parent_map.write_text(json.dumps(parent_map_payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, r"parent gallery href \+ image route"):
                self._export(base, site, manifest, base / "output-parent", parent_map)

    def test_parent_links_reject_cross_origin_and_absolute_session_query(self) -> None:
        cases = (
            (
                "external-href",
                "/info/professions/fishing.html",
                "/info/professions/fishing-gallery.html#1",
                "https://evil.example/info/professions/fishing-gallery.html#1",
                r"cross-origin",
            ),
            (
                "external-image",
                "/info/professions/fishing.html",
                "/info/professions/images/fishing/ss/thumbs/ss1-thumb.jpg",
                "http://evil.example/info/professions/images/fishing/ss/thumbs/ss1-thumb.jpg",
                r"cross-origin",
            ),
            (
                "same-origin-session-query",
                "/info/professions/fishing.html",
                "/info/professions/fishing-gallery.html#1",
                "http://www.worldofwarcraft.com/info/professions/fishing-gallery.html?jsessionid=abc#1",
                r"query-bearing absolute URL",
            ),
        )
        for name, guide_route, old_value, replacement, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                base, site, manifest, map_path = self._fixture(Path(tmp))
                guide = site / guide_route.lstrip("/")
                guide_text = guide.read_text(encoding="utf-8")
                if name == "external-image":
                    changed = guide_text.replace(f'src="{old_value}"', f'src="{replacement}"', 1)
                else:
                    changed = guide_text.replace(f'href="{old_value}"', f'href="{replacement}"', 1)
                self.assertNotEqual(changed, guide_text)
                guide.write_text(changed, encoding="utf-8")
                manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
                guide_record = next(item for item in manifest_payload["files"] if item["route"] == guide_route)
                guide_data = guide.read_bytes()
                guide_record["derived_sha256"] = hashlib.sha256(guide_data).hexdigest()
                guide_record["derived_length"] = len(guide_data)
                manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
                changed_manifest_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
                map_payload = json.loads(map_path.read_text(encoding="utf-8"))
                map_payload["source_manifest"]["sha256"] = changed_manifest_sha
                map_payload["source_manifest_sha256"] = changed_manifest_sha
                bad_map = base / f"bad-{name}.json"
                bad_map.write_text(json.dumps(map_payload), encoding="utf-8")
                with self.assertRaisesRegex(pages.PagesExportError, message):
                    self._export(base, site, manifest, base / f"output-{name}", bad_map)

    def test_map_builder_rejects_existing_output_and_input_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest, map_path = self._fixture(Path(tmp))
            map_payload = json.loads(map_path.read_text(encoding="utf-8"))
            acceptance_path = base / map_payload["source_acceptance"]["path"]
            audit_path = base / map_payload["source_audit"]["path"]
            manifest_path = base / map_payload["source_manifest"]["path"]
            existing = base / "existing-output.json"
            existing.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(guide_previews.GuidePreviewError, r"output already exists"):
                guide_previews.build_source_map_from_audit(
                    output=existing,
                    acceptance_path=acceptance_path,
                    audit_path=audit_path,
                    manifest_path=manifest_path,
                    workspace_root=base,
                )
            with self.assertRaisesRegex(guide_previews.GuidePreviewError, r"differ from every source input"):
                guide_previews.build_source_map_from_audit(
                    output=acceptance_path,
                    acceptance_path=acceptance_path,
                    audit_path=audit_path,
                    manifest_path=manifest_path,
                    workspace_root=base,
                )
            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")

    def test_render_section_is_deterministic_and_does_not_create_full_aliases(self) -> None:
        group = guide_previews.GuidePreviewGroup(
            "zulaman",
            "Zul'Aman",
            "/info/dungeons/zulaman-gallery.html",
            "/info/dungeons/zulaman.xml",
            "/BASE/info/dungeons/zulaman-gallery.html",
            "/BASE/info/dungeons/zulaman.xml.html",
            (guide_previews.GuidePreview("/info/dungeons/images/zulaman/thumbs/ss1-thumb.jpg", "a" * 64, 1, "20080512205641", "/BASE/info/dungeons/images/zulaman/thumbs/ss1-thumb.jpg"),),
        )
        first = guide_previews.render_gallery_section(group)
        second = guide_previews.render_gallery_section(group)
        self.assertEqual(first, second)
        self.assertIn("View original guide", first)
        self.assertNotIn("/info/dungeons/images/zulaman/ss1.jpg", first)
        self.assertEqual(first.count('id="offline-preserved-guide-previews-zulaman"'), 1)


if __name__ == "__main__":
    unittest.main()
