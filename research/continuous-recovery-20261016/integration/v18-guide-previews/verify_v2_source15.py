#!/usr/bin/env python3
"""Run a local source15 loader and one City Attacks render precheck."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import export_github_pages as pages  # noqa: E402
import guide_previews  # noqa: E402


MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
MANIFEST_PATH = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/v2-source15-loader-verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    route_to_static = {
        str(record["route"]): pages.static_url(
            pages.DEFAULT_BASE_PATH,
            pages.static_rel_for_route(str(record["route"]), record),
        )
        for record in manifest.get("files", [])
        if isinstance(record, dict) and isinstance(record.get("route"), str)
    }
    bundle = guide_previews.load_guide_preview_map(
        MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=MANIFEST_PATH,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    if bundle.map_schema != "wow-recovery.guide-preview-source-map.v2":
        raise ValueError("loader did not select v2 schema")
    if bundle.preview_count != 22 or len(bundle.groups) != 6:
        raise ValueError("loader did not conserve 6 groups / 22 previews")
    city = bundle.group_for_gallery("/pvp/worldpvp/cityattacks-gallery.html")
    if city is None or len(city.previews) != 3:
        raise ValueError("City Attacks group did not contain exactly three previews")
    city_record = next(item for item in manifest["files"] if item.get("route") == city.gallery_route)
    city_page = ROOT / str(city_record["output_path"])
    city_page_sha_before = sha256(city_page)
    original = city_page.read_text(encoding="utf-8")
    rendered = guide_previews.insert_gallery_section(original, city)
    route_markers = sum(rendered.count(f'data-guide-preview-route="{preview.route}"') for preview in city.previews)
    if rendered.count("Preserved guide previews") != 1 or route_markers != 3:
        raise ValueError("City render did not contain one section and three route markers")
    if "/pvp/worldpvp/images/city/ss1.jpg" in rendered or "dynamic_full_candidate" in rendered:
        raise ValueError("City render introduced a dynamic/full alias")
    receipt = {
        "schema": "wow-recovery.guide-preview-v2-source15-loader-verification.v1",
        "executed_by": "local_recovery_20261016",
        "network_requests": 0,
        "inputs": {
            "map": {"path": MAP.relative_to(ROOT).as_posix(), "sha256": sha256(MAP)},
            "manifest": {"path": MANIFEST_PATH.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST_PATH)},
            "city_gallery_source": {
                "path": city_page.relative_to(ROOT).as_posix(),
                "sha256": sha256(city_page),
                "bytes": city_page.stat().st_size,
            },
        },
        "loader": {"map_schema": bundle.map_schema, "group_count": len(bundle.groups), "preview_count": bundle.preview_count},
        "render": {
            "gallery_route": city.gallery_route,
            "guide_route": city.guide_route,
            "section_count": rendered.count("Preserved guide previews"),
            "route_marker_count": route_markers,
            "rendered_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
            "source_unchanged_after_render": sha256(city_page) == city_page_sha_before,
            "dynamic_full_alias": False,
        },
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
