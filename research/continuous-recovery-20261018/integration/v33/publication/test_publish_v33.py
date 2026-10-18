from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load_module("v33_publication_prepare", "publish_v33.py")


def row(path: str, *, kind: str = "page", role: str = "page", digest: str = "a" * 64, length: int = 1, mime: str = "text/html") -> dict[str, object]:
    return {
        "output_path": path,
        "kind": kind,
        "role": role,
        "derived_sha256": digest,
        "derived_length": length,
        "mime": mime,
    }


class V33PublicationPreparationTests(unittest.TestCase):
    def test_root_and_dynamic_delta(self) -> None:
        self.assertEqual(publisher.ROOT.as_posix().casefold().rstrip("/"), "d:/wow_encyclopedia")
        old_image = row("images/old.png", kind="image_overlay", role="image_overlay", digest="b" * 64, length=2, mime="image/png")
        old_page = row("news/old.html", digest="c" * 64, length=9)
        new_image = row("images/new.png", kind="image_overlay", role="image_overlay", digest="d" * 64, length=4, mime="image/png")
        changed_page = row("news/old.html", digest="e" * 64, length=11)
        delta = publisher.provenance_delta(
            {"files": [old_image, old_page]},
            {"files": [old_image, changed_page, new_image]},
            {"new_images": 1, "image_bytes": 4},
        )
        self.assertEqual(delta["new_image_count"], 1)
        self.assertEqual(delta["new_image_bytes"], 4)
        self.assertEqual(delta["new_paths"], ["images/new.png"])
        self.assertEqual(delta["changed_paths"], ["news/old.html"])
        self.assertEqual(delta["previous_image_overlay_count"], 1)

    def test_frozen_image_metadata_must_not_change(self) -> None:
        old = row("images/old.png", kind="image_overlay", role="image_overlay", digest="b" * 64, length=2, mime="image/png")
        changed = row("images/old.png", kind="image_overlay", role="image_overlay", digest="f" * 64, length=3, mime="image/png")
        with self.assertRaisesRegex(RuntimeError, "changed frozen image-overlay metadata"):
            publisher.provenance_delta({"files": [old]}, {"files": [changed]}, {"new_images": 0, "image_bytes": 0})

        old_with_origin = {**old, "origin_host": "www.worldofwarcraft.com"}
        changed_origin = {**old_with_origin, "origin_host": "www.wow-europe.com"}
        with self.assertRaisesRegex(RuntimeError, "changed frozen image-overlay metadata"):
            publisher.provenance_delta({"files": [old_with_origin]}, {"files": [changed_origin]}, {"new_images": 0, "image_bytes": 0})

    def test_object_binding_is_bounded_and_hashes_actual_site_bytes(self) -> None:
        with tempfile.TemporaryDirectory(dir=publisher.PUB, prefix="v33-pub-fixture-") as directory:
            site = Path(directory)
            (site / "images").mkdir()
            (site / "news").mkdir()
            (site / "images/new.png").write_bytes(b"PNG\x00")
            (site / "news/old.html").write_text("<html>changed</html>\n", encoding="utf-8")
            (site / "export-provenance.json").write_text("{}\n", encoding="utf-8")
            delta = {
                "new_paths": ["images/new.png"],
                "changed_paths": ["news/old.html"],
                "after_rows": {
                    "images/new.png": row("images/new.png", kind="image_overlay", role="image_overlay", length=4, mime="image/png"),
                    "news/old.html": row("news/old.html", length=21, mime="text/xml"),
                },
            }
            objects = publisher.site_object_bindings(site, delta)
            self.assertEqual([item["path"] for item in objects], ["export-provenance.json", "images/new.png", "news/old.html"])
            self.assertEqual(objects[1]["bytes"], 4)
            self.assertEqual(objects[1]["sha256"], publisher.sha256_bytes(b"PNG\x00"))
            self.assertEqual(objects[1]["mime"], ["image/png"])
            self.assertEqual(objects[2]["mime"], ["text/html"])

    def test_counts_and_previous_pages_commit_are_dynamic(self) -> None:
        self.assertEqual(
            publisher.guide_counts({"stats": {"guide_image_collection_images": 7, "guide_preview_count": 3}, "guide_image_collections": {"group_count": 2}}),
            {"guide_collection_images": 7, "guide_collection_groups": 2, "guide_previews": 3},
        )
        self.assertEqual(publisher.previous_online_commit({"expected_pages_commit": "A" * 40}), "a" * 40)
        with self.assertRaisesRegex(RuntimeError, "no exact Pages commit"):
            publisher.previous_online_commit({"expected_pages_commit": "short"})


if __name__ == "__main__":
    unittest.main()
