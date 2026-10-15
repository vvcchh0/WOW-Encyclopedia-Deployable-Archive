from __future__ import annotations

import base64
import hashlib
import importlib
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
github_export_tests = importlib.import_module("test_github_pages_export")


# A valid 1x1 baseline JPEG.  Keeping the fixture encoded avoids adding a
# generated binary to the repository while still exercising Pillow.verify.
JPEG_1X1 = base64.b64decode(
    b"/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/AP/EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEAAQUCf//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQMBAT8Bf//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQIBAT8Bf//EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEABj8Cf//Z"
)
GIF_1X1 = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")


class PagesImageOverlayTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path]:
        base, site, manifest = github_export_tests.GithubPagesExportTests()._fixture(base)
        article = site / "article.xml"
        article.write_text(
            '<html><body><img src="/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Farticle.xml&amp;requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fmissing.gif&amp;reason=external-or-uncollected-resource"><script>addshots("/gallery/","ss",numShots);</script></body></html>',
            encoding="utf-8",
        )
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        record = next(item for item in payload["files"] if item["route"] == "/article.xml")
        data = article.read_bytes()
        record["derived_sha256"] = hashlib.sha256(data).hexdigest()
        record["derived_length"] = len(data)
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return base, site, manifest

    def _map(self, base: Path, entries: list[dict]) -> Path:
        raw = base / "raw"
        raw.mkdir(exist_ok=True)
        for entry in entries:
            path = raw / entry["name"]
            data = entry.pop("data", JPEG_1X1)
            mime = entry.pop("declared_mime", "image/jpeg")
            path.write_bytes(data)
            entry.update(
                {
                    "kind": "image",
                    "local_path": str(Path("raw") / entry["name"]),
                    "mime": mime,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "actual_timestamp": "20080512205900",
                    "indexed_capture_timestamp": "20080512205900",
                    "cdx_digest": base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip("="),
                }
            )
        map_path = base / "map.json"
        map_path.write_text(json.dumps({"items": entries}), encoding="utf-8")
        return map_path

    def test_missing_reference_and_gallery_directory_use_concrete_overlay_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {"name": "missing.jpg", "logical_url": "http://www.worldofwarcraft.com/missing.gif", "original": "http://www.worldofwarcraft.com/missing.gif"},
                    {"name": "ss1.jpg", "logical_url": "http://www.worldofwarcraft.com/gallery/ss1.jpg", "original": "http://www.worldofwarcraft.com/gallery/ss1.jpg"},
                    {"name": "ss1-thumb.jpg", "logical_url": "http://www.worldofwarcraft.com/gallery/ss1-thumb.jpg", "original": "http://www.worldofwarcraft.com/gallery/ss1-thumb.jpg"},
                    {"name": "ss1.jpg", "logical_url": "http://www.worldofwarcraft.com/gallery/ss1.jpg", "original": "http://www.worldofwarcraft.com/gallery/ss1.jpg"},
                ],
            )
            output = base / "pages"
            result = pages.export_pages(
                source_site=base / "offline/site",
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
                image_source_maps=[source_map],
            )
            self.assertEqual(result["stats"]["source_records"], 11)
            self.assertEqual(result["stats"]["image_overlay_records"], 3)
            article = (output / "article.xml.html").read_text(encoding="utf-8")
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/missing.gif', article)
            self.assertNotIn('__offline/missing-image.svg?source=', article)
            self.assertIn('addshots("/WOW-Encyclopedia-Deployable-Archive/gallery/","ss",numShots)', article)
            self.assertTrue((output / "gallery/ss1.jpg").read_bytes() == JPEG_1X1)
            route_map = json.loads((output / "__offline/route-map.json").read_text(encoding="utf-8"))
            self.assertIn("/gallery/ss1.jpg", route_map["routes"])
            self.assertNotIn("/gallery/ss2.jpg", route_map["routes"])
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            overlays = [item for item in provenance["files"] if item.get("role") == "image_overlay"]
            self.assertEqual(len(overlays), 3)
            self.assertTrue(all(item["source_map"] == "map.json" for item in overlays))
            self.assertEqual({item["source_map_sha256"] for item in overlays}, {hashlib.sha256(source_map.read_bytes()).hexdigest()})
            self.assertTrue(all(item["original_url"].startswith("http://www.worldofwarcraft.com/") for item in overlays))

    def test_css_and_inline_style_requested_markers_recover_or_stay_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, site, manifest = self._fixture(Path(tmp))
            recovered = (
                "/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fstyles%2Fbase.css"
                "&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fmissing.gif&reason=external-or-uncollected-resource"
            )
            style = site / "style.css"
            style.write_text(f"body {{ background: url(\"{recovered}\"); }}", encoding="utf-8")
            uncollected = (
                "/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Farticle.xml"
                "&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnot-collected.gif&reason=external-or-uncollected-resource"
            )
            article = site / "article.xml"
            article.write_text(
                article.read_text(encoding="utf-8").replace("<body>", f'<body><div style="background:url(\'{uncollected}\')"></div>', 1),
                encoding="utf-8",
            )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            for route, source in (("/style.css", style), ("/article.xml", article)):
                record = next(item for item in payload["files"] if item["route"] == route)
                data = source.read_bytes()
                record["derived_sha256"] = hashlib.sha256(data).hexdigest()
                record["derived_length"] = len(data)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            source_map = self._map(
                base,
                [{"name": "missing.jpg", "logical_url": "http://www.worldofwarcraft.com/missing.gif", "original": "http://www.worldofwarcraft.com/missing.gif"}],
            )
            output = base / "pages"
            pages.export_pages(
                source_site=site,
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                max_bytes=500_000_000,
                min_free_bytes=0,
                image_source_maps=[source_map],
            )
            css = (output / "style.css").read_text(encoding="utf-8")
            exported_article = (output / "article.xml.html").read_text(encoding="utf-8")
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/missing.gif', css)
            self.assertNotIn('__offline/missing-image.svg?source=', css)
            self.assertIn('/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?', exported_article)
            self.assertIn('requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnot-collected.gif', exported_article)
            self.assertNotIn("url('http://www.worldofwarcraft.com/not-collected.gif')", exported_article)

    def test_loopback_css_localizer_does_not_revisit_support_marker(self) -> None:
        marker = '/__offline/missing-image.svg?requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fmissing.gif'
        localizer = pages.mirror.Localizer({}, set())
        recorder = pages.mirror.ReferenceRecorder('/style.css', 'http://www.worldofwarcraft.com/style.css')
        css = f'body {{ background: url("{marker}"); }}'
        self.assertEqual(
            pages.mirror.rewrite_css(css, base_url=recorder.source_url, localizer=localizer, recorder=recorder),
            css,
        )

    def test_overlay_validation_rejects_hash_mime_date_path_and_route_conflicts(self) -> None:
        cases = {
            "hash": lambda entry: entry.update(sha256="0" * 64),
            "mime": lambda entry: entry.update(mime="image/png"),
            "date": lambda entry: entry.update(actual_timestamp="20080512210045", indexed_capture_timestamp="20080512210045"),
            "invalid_date": lambda entry: entry.update(actual_timestamp="20080230000000", indexed_capture_timestamp="20080230000000"),
            "path": lambda entry: entry.update(local_path="../escape.jpg"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                base, _site, manifest = self._fixture(Path(tmp))
                entry = {"name": "one.jpg", "logical_url": "http://www.worldofwarcraft.com/overlay/one.jpg", "original": "http://www.worldofwarcraft.com/overlay/one.jpg"}
                source_map = self._map(base, [entry])
                payload = json.loads(source_map.read_text(encoding="utf-8"))
                mutate(payload["items"][0])
                source_map.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(pages.PagesExportError):
                    pages.export_pages(source_site=base / "offline/site", manifest_path=manifest, output=base / "pages", workspace_root=base, min_free_bytes=0, image_source_maps=[source_map])

        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            first = {"name": "one.jpg", "logical_url": "http://www.worldofwarcraft.com/overlay/one.jpg", "original": "http://www.worldofwarcraft.com/overlay/one.jpg"}
            source_map = self._map(base, [first])
            payload = json.loads(source_map.read_text(encoding="utf-8"))
            second = dict(payload["items"][0])
            second["name"] = "two.gif"
            second["data"] = GIF_1X1
            second["declared_mime"] = "image/gif"
            # Make the second entity a different valid image while keeping the
            # logical route identical, so the conflict check is reached after
            # both image records pass format and digest validation.
            second["logical_url"] = "http://www.worldofwarcraft.com/overlay/one.jpg"
            second["original"] = second["logical_url"]
            source_map = self._map(base, [payload["items"][0], second])
            with self.assertRaises(pages.PagesExportError):
                pages.export_pages(source_site=base / "offline/site", manifest_path=manifest, output=base / "pages", workspace_root=base, min_free_bytes=0, image_source_maps=[source_map])

        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {"name": "upper.jpg", "logical_url": "http://www.worldofwarcraft.com/Overlay/one.jpg", "original": "http://www.worldofwarcraft.com/Overlay/one.jpg"},
                    {"name": "lower.jpg", "logical_url": "http://www.worldofwarcraft.com/overlay/one.jpg", "original": "http://www.worldofwarcraft.com/overlay/one.jpg"},
                ],
            )
            with self.assertRaises(pages.PagesExportError):
                pages.export_pages(source_site=base / "offline/site", manifest_path=manifest, output=base / "pages", workspace_root=base, min_free_bytes=0, image_source_maps=[source_map])

    def test_later_supplement_requires_explicit_opt_in_and_post_2008_class(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {
                        "name": "ss1314.jpg",
                        "logical_url": "http://www.wow-europe.com/screens/ss1314.jpg",
                        "original": "http://www.wow-europe.com/screens/ss1314.jpg",
                    }
                ],
            )
            payload = json.loads(source_map.read_text(encoding="utf-8"))
            payload["items"][0]["actual_timestamp"] = "20100810173046"
            payload["items"][0]["indexed_capture_timestamp"] = "20100810173046"
            payload["items"][0]["temporal_class"] = "post_2008"
            source_map.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(pages.PagesExportError, "image supplement capture is after 2008"):
                pages.export_pages(
                    source_site=base / "offline/site",
                    manifest_path=manifest,
                    output=base / "pages-default",
                    workspace_root=base,
                    min_free_bytes=0,
                    supplement_image_source_maps=[source_map],
                )

            output = base / "pages-opt-in"
            result = pages.export_pages(
                source_site=base / "offline/site",
                manifest_path=manifest,
                output=output,
                workspace_root=base,
                min_free_bytes=0,
                supplement_image_source_maps=[source_map],
                allow_later_image_supplements=True,
            )
            self.assertEqual(result["stats"]["supplement_image_overlay_records"], 1)
            provenance = json.loads((output / "export-provenance.json").read_text(encoding="utf-8"))
            overlay = next(item for item in provenance["files"] if item.get("role") == "image_overlay")
            self.assertEqual(overlay["actual_capture_timestamp"], "20100810173046")
            self.assertEqual(overlay["indexed_capture_timestamp"], "20100810173046")
            self.assertEqual(overlay["temporal_class"], "post_2008")
            self.assertNotEqual(overlay["temporal_class"], "baseline_2008")
            related = (output / "__offline/related-images/index.html").read_text(encoding="utf-8")
            self.assertIn('data-temporal-class="post_2008"', related)
            self.assertIn("Post-2008 capture", related)

        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {
                        "name": "ss1336.jpg",
                        "logical_url": "http://www.wow-europe.com/screens/ss1336.jpg",
                        "original": "http://www.wow-europe.com/screens/ss1336.jpg",
                    }
                ],
            )
            payload = json.loads(source_map.read_text(encoding="utf-8"))
            payload["items"][0]["actual_timestamp"] = "20100602102329"
            payload["items"][0]["indexed_capture_timestamp"] = "20100602102329"
            payload["items"][0]["temporal_class"] = "late_2008"
            source_map.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "temporal_class does not match capture date"):
                pages.export_pages(
                    source_site=base / "offline/site",
                    manifest_path=manifest,
                    output=base / "pages-wrong-class",
                    workspace_root=base,
                    min_free_bytes=0,
                    supplement_image_source_maps=[source_map],
                    allow_later_image_supplements=True,
                )

        with tempfile.TemporaryDirectory() as tmp:
            base, _site, manifest = self._fixture(Path(tmp))
            source_map = self._map(
                base,
                [
                    {
                        "name": "primary-2010.jpg",
                        "logical_url": "http://www.worldofwarcraft.com/screens/primary-2010.jpg",
                        "original": "http://www.worldofwarcraft.com/screens/primary-2010.jpg",
                    }
                ],
            )
            payload = json.loads(source_map.read_text(encoding="utf-8"))
            payload["items"][0]["actual_timestamp"] = "20100810173046"
            payload["items"][0]["indexed_capture_timestamp"] = "20100810173046"
            payload["items"][0]["temporal_class"] = "post_2008"
            source_map.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "outside the 2008 baseline"):
                pages.export_pages(
                    source_site=base / "offline/site",
                    manifest_path=manifest,
                    output=base / "pages-primary-2010",
                    workspace_root=base,
                    min_free_bytes=0,
                    image_source_maps=[source_map],
                    allow_later_image_supplements=True,
                )

    def test_overlay_url_rejects_decoded_path_tricks(self) -> None:
        unsafe = (
            "/gallery/%5Cescape.jpg",
            "/gallery/%00escape.jpg",
            "/gallery/file%3Aname.jpg",
            "/gallery/./escape.jpg",
            "/gallery/%2e%2e/escape.jpg",
            "//gallery/escape.jpg",
            "/gallery/file.jpg.",
            "/gallery/file.jpg%20",
        )
        for path in unsafe:
            with self.subTest(path=path):
                with self.assertRaises(pages.PagesExportError):
                    pages._overlay_url("http://www.worldofwarcraft.com" + path, label="test")

    def test_gallery_rewrite_is_narrow(self) -> None:
        class Recorder:
            def __init__(self) -> None:
                self.calls = []

            def add(self, *args) -> None:
                self.calls.append(args)

        recorder = Recorder()
        rewritten = pages.rewrite_gallery_addshots(
            'addshots("/gallery/","ss",numShots); addshots("/gallery/","other",numShots); addshots("/../bad/","ss",numShots);',
            base_path="/WOW-Encyclopedia-Deployable-Archive/",
            base_url="http://www.worldofwarcraft.com/info/gallery.html",
            recorder=recorder,
        )
        self.assertIn('addshots("/WOW-Encyclopedia-Deployable-Archive/gallery/","ss",numShots)', rewritten)
        self.assertIn('addshots("/WOW-Encyclopedia-Deployable-Archive/gallery/","ss",numShots)', pages.rewrite_gallery_addshots(
            'addshots("/WOW-Encyclopedia-Deployable-Archive/gallery/","ss",numShots);',
            base_path="/WOW-Encyclopedia-Deployable-Archive/",
            base_url="http://www.worldofwarcraft.com/info/gallery.html",
            recorder=recorder,
        ))
        self.assertIn('addshots("/gallery/","other",numShots)', rewritten)
        self.assertIn('addshots("/../bad/","ss",numShots)', rewritten)
        self.assertEqual(len(recorder.calls), 1)


if __name__ == "__main__":
    unittest.main()
