#!/usr/bin/env python3
"""Run the one root-authorized v19 Pages export from frozen local inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v19"
ROOT_V17_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json"
ROOT_V18_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-export-acceptance.json"
ROOT_V18_LOCAL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-local-acceptance.json"
ROOT_V18_BROWSER_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-browser-acceptance.json"
ROOT_V2_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-city-v2-code-acceptance.json"
FOCUSED_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v18-build/focused-guide-tests-receipt.json"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
V18_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v18/export-provenance.json"
V18_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v18-build/worker-build-v18.json"
PREPARATION_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/prepare-v19-inputs.json"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/worker-build-v19.json"
V1_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"
V2_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
V19_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json"
NEWS_SHARED10_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-news-shared10-source-acceptance.json"
NEWS_SHARED13_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-news-shared13-source-acceptance.json"
NEWS_SHARED10_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-shared10/source-map.json"
NEWS_SHARED13_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-shared13/source-map.json"
MIN_FREE_BYTES = 11_005_853_696
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

FROZEN_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
ORIGINAL_OFFLINE_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V18_PROVENANCE_SHA256 = "5e233b4e951b15f6004a971eb5082fb77202b59234f8a4561d3d03d671daf3b5"
ROOT_V17_ACCEPTANCE_SHA256 = "d45384119fe8ba9578a0a11a25ce79653460f2a65562423a5ad66ebd17883429"
ROOT_V18_EXPORT_ACCEPTANCE_SHA256 = "1eddccd098f380566beecc5a5e0ee0dfe6e1522ac68afa87ba2a4da4414e2c4c"
ROOT_V18_LOCAL_ACCEPTANCE_SHA256 = "ef768465d6945dd3972fe60abdc201c71a913c5b60566428658402aed6fb8a5d"
ROOT_V18_BROWSER_ACCEPTANCE_SHA256 = "cf1152f27bcb73d8288afff81e344717440c8b05f2f295bc4652ca377143dfa3"
V18_BUILD_RECEIPT_SHA256 = "17ba2c060b72a08da2219a74867cf569f1e98f758996b72c22241e981f0a7c72"
ROOT_V2_ACCEPTANCE_SHA256 = "215bcca89a55bb3a5756998d428f6e62f01577ef58384e4a490b8e9049f63eb2"
V2_GUIDE_MAP_SHA256 = "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581"
V1_GUIDE_MAP_SHA256 = "cf0da5fec45993684676d94d1cc09fad3f5a421dabbb18b56861000daa6248b2"
PREPARATION_RECEIPT_SHA256 = "903bf57c53ce9b2b7bd25b6e9a3c1ab0541c407015bb9d212404c61c40b6e9c6"
V19_PRIMARY_MAP_SHA256 = "7587fcb84e79f90502953d12e425af8a418916b2d4a8f6d211c7f8be24cf5df7"
NEWS_SHARED10_ACCEPTANCE_SHA256 = "65354d44666d68654a619efdc10bc8bd2cacab0cd085f3d729bdb6159309be4f"
NEWS_SHARED13_ACCEPTANCE_SHA256 = "cda6475904c67a034dbbaee20362a1b5c65f9d376e960b91f6c2918c10875ff2"
NEWS_SHARED10_SOURCE_MAP_SHA256 = "e73e0ac9e465da9dce571e55a6a4c730c02a35c68d346c5f81ad5f72220f059d"
NEWS_SHARED13_SOURCE_MAP_SHA256 = "e5148b15bb67eae6e5f24176549283ab0f021ee6502c06ed3f10e11d38ba99c6"

PRODUCTION_SHA256 = {
    "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
    "tools/export_github_pages.py": "c16647890b488f534aa7945f3333ca38a6583b8ca6dad6ce70e40a06d3685de9",
}
TEST_SHA256 = {
    "tests/test_guide_previews.py": "ec8d351347efb790cb003bff2f0e94493a85f6da75f801a26b8422a6d88b9852",
}
MAP_SHA256 = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/guide-previews-source-map.json": V1_GUIDE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": V2_GUIDE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json": V19_PRIMARY_MAP_SHA256,
}

PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
    V19_PRIMARY_MAP,
]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_hash(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 changed: expected {expected}, got {actual}")
    return actual


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def locked_input_hashes() -> dict[str, str]:
    paths: dict[str, tuple[Path, str]] = {
        rel(SOURCE_MANIFEST): (SOURCE_MANIFEST, FROZEN_MANIFEST_SHA256),
        rel(ORIGINAL_OFFLINE_MANIFEST): (ORIGINAL_OFFLINE_MANIFEST, ORIGINAL_OFFLINE_MANIFEST_SHA256),
        rel(ROOT_V17_ACCEPTANCE): (ROOT_V17_ACCEPTANCE, ROOT_V17_ACCEPTANCE_SHA256),
        rel(ROOT_V18_EXPORT_ACCEPTANCE): (ROOT_V18_EXPORT_ACCEPTANCE, ROOT_V18_EXPORT_ACCEPTANCE_SHA256),
        rel(ROOT_V18_LOCAL_ACCEPTANCE): (ROOT_V18_LOCAL_ACCEPTANCE, ROOT_V18_LOCAL_ACCEPTANCE_SHA256),
        rel(ROOT_V18_BROWSER_ACCEPTANCE): (ROOT_V18_BROWSER_ACCEPTANCE, ROOT_V18_BROWSER_ACCEPTANCE_SHA256),
        rel(ROOT_V2_ACCEPTANCE): (ROOT_V2_ACCEPTANCE, ROOT_V2_ACCEPTANCE_SHA256),
        rel(FOCUSED_RECEIPT): (FOCUSED_RECEIPT, "9ae29a7db52077a3c94f7a85b67a444f28cb2c2f985fc8b9242ed96601800b5f"),
        rel(V18_PROVENANCE): (V18_PROVENANCE, V18_PROVENANCE_SHA256),
        rel(V18_BUILD_RECEIPT): (V18_BUILD_RECEIPT, V18_BUILD_RECEIPT_SHA256),
        rel(PREPARATION_RECEIPT): (PREPARATION_RECEIPT, PREPARATION_RECEIPT_SHA256),
        rel(NEWS_SHARED10_ACCEPTANCE): (NEWS_SHARED10_ACCEPTANCE, NEWS_SHARED10_ACCEPTANCE_SHA256),
        rel(NEWS_SHARED13_ACCEPTANCE): (NEWS_SHARED13_ACCEPTANCE, NEWS_SHARED13_ACCEPTANCE_SHA256),
        rel(NEWS_SHARED10_SOURCE_MAP): (NEWS_SHARED10_SOURCE_MAP, NEWS_SHARED10_SOURCE_MAP_SHA256),
        rel(NEWS_SHARED13_SOURCE_MAP): (NEWS_SHARED13_SOURCE_MAP, NEWS_SHARED13_SOURCE_MAP_SHA256),
        rel(V1_GUIDE_MAP): (V1_GUIDE_MAP, V1_GUIDE_MAP_SHA256),
        rel(V2_GUIDE_MAP): (V2_GUIDE_MAP, V2_GUIDE_MAP_SHA256),
    }
    for relative, expected in {**PRODUCTION_SHA256, **TEST_SHA256, **MAP_SHA256}.items():
        paths[relative] = (ROOT / relative, expected)
    return {relative: require_hash(path, expected, relative) for relative, (path, expected) in paths.items()}


def validate_gates() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v17 = read_object(ROOT_V17_ACCEPTANCE, "root v17 input acceptance")
    if v17.get("accepted") is not True or v17.get("export_started") is not False:
        raise RuntimeError("root v17 input acceptance is not accepted and pre-export")
    for key, expected in {
        "source_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "primary_overlays": 48,
        "supplement_overlays": 21,
        "total_overlays": 69,
        "source_records": 8357,
    }.items():
        if v17.get(key) != expected:
            raise RuntimeError(f"root v17 gate differs for {key}: {v17.get(key)!r}")

    v18_export = read_object(ROOT_V18_EXPORT_ACCEPTANCE, "root v18 export acceptance")
    if v18_export.get("accepted") is not True or v18_export.get("published") is not False:
        raise RuntimeError("root v18 export acceptance is not accepted and unpublished")
    for key, expected in {
        "checked_declared_files": 8527,
        "actual_files": 8528,
        "stats": None,
    }.items():
        if key == "stats":
            stats = v18_export.get("stats") or {}
            if any(stats.get(name) != value for name, value in {
                "output_files": 8527,
                "source_records": 8357,
                "image_overlay": 69,
                "primary_image_overlay_records": 48,
                "supplement_image_overlay_records": 21,
                "guide_preview_count": 22,
                "guide_preview_gallery_pages": 6,
            }.items()):
                raise RuntimeError("root v18 export stats do not match the accepted v18 tree")
        elif v18_export.get(key) != expected:
            raise RuntimeError(f"root v18 export gate differs for {key}: {v18_export.get(key)!r}")
    v18_local = read_object(ROOT_V18_LOCAL_ACCEPTANCE, "root v18 local acceptance")
    if v18_local.get("accepted") is not True or v18_local.get("network_requests") != 0 or v18_local.get("published") is not False:
        raise RuntimeError("root v18 local acceptance is not an accepted local-only gate")
    v18_browser = read_object(ROOT_V18_BROWSER_ACCEPTANCE, "root v18 browser acceptance")
    if v18_browser.get("accepted") is not True or v18_browser.get("external_requests") != []:
        raise RuntimeError("root v18 browser acceptance is not an accepted local-only gate")
    v18_build = read_object(V18_BUILD_RECEIPT, "worker v18 build receipt")
    if v18_build.get("export_completed") is not True or v18_build.get("network_requests_by_builder") != 0:
        raise RuntimeError("worker v18 build receipt is not complete and local-only")
    preparation = read_object(PREPARATION_RECEIPT, "v19 input preparation receipt")
    if preparation.get("asset_count") != 10 or preparation.get("asset_bytes") != 33224 or preparation.get("map_sha256") != V19_PRIMARY_MAP_SHA256:
        raise RuntimeError("v19 input preparation receipt does not bind the ten accepted assets")

    v2 = read_object(ROOT_V2_ACCEPTANCE, "root City v2 code acceptance")
    if v2.get("accepted") is not True or v2.get("network_requests") != 0:
        raise RuntimeError("root City v2 code acceptance is not accepted local-only evidence")
    if v2.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or v2.get("production_code_sha256") != PRODUCTION_SHA256["tools/guide_previews.py"]:
        raise RuntimeError("root City v2 code acceptance does not bind current source/code")
    if v2.get("v2_map_sha256") != V2_GUIDE_MAP_SHA256 or v2.get("v2_groups") != 6 or v2.get("v2_previews") != 22 or v2.get("city_cards") != 3:
        raise RuntimeError("root City v2 map/count gate differs")

    focused = read_object(FOCUSED_RECEIPT, "focused guide test receipt")
    if focused.get("exit_code") != 0 or focused.get("result") != "9 tests OK":
        raise RuntimeError("focused guide tests are not accepted")
    return v17, v2, focused


def output_file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def preflight_loader() -> dict[str, Any]:
    """Run the unchanged exporter loaders against v19 inputs without writing output."""

    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages as exporter
    import guide_previews

    manifest = read_object(SOURCE_MANIFEST, "source15 manifest")
    records = list(manifest.get("files") or [])
    route_records: dict[str, dict[str, Any]] = {}
    route_to_static: dict[str, str] = {}
    relative_paths: set[str] = set()
    for record in records:
        route = exporter.safe_route(str(record.get("route") or ""))
        route_records[route] = record
        relative = exporter.static_rel_for_route(route, record)
        relative_paths.add(relative)
        route_to_static[route] = exporter.static_url(BASE_PATH, relative)
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(route_records) | {str(alias) for alias in aliases}
    primary, primary_bytes = exporter.load_image_overlays(
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=frozen_routes,
        frozen_static_paths=set(relative_paths),
    )
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_static = set(relative_paths) | {str(item["relative"]) for item in primary}
    for item in primary:
        route_to_static[str(item["route"])] = exporter.static_url(BASE_PATH, str(item["relative"]))
    supplement, supplement_bytes = exporter.load_supplement_image_overlays(
        tuple(SUPPLEMENT_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_static,
        allow_later_image_supplements=True,
    )
    for item in supplement:
        route_to_static[str(item["route"])] = exporter.static_url(BASE_PATH, str(item["relative"]))
    bundle = guide_previews.load_guide_preview_map(
        V2_GUIDE_MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    if len(primary) != 58 or len(supplement) != 21:
        raise RuntimeError(f"v19 loader count mismatch: primary={len(primary)}, supplement={len(supplement)}")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "guide_preview_groups": len(bundle.groups),
        "guide_preview_count": bundle.preview_count,
        "network_requests": 0,
    }


def verify_postbuild(result: dict[str, Any]) -> dict[str, Any]:
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v19 output or partial output state is invalid after export")
    provenance_path = OUTPUT / "export-provenance.json"
    provenance = read_object(provenance_path, "v19 export provenance")
    stats = provenance.get("stats") or {}
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages as exporter
    import guide_previews
    if result.get("output_files") != 8537 or stats.get("output_files") != 8537:
        raise RuntimeError(f"v19 declared output count is not 8537: result={result.get('output_files')}, provenance={stats.get('output_files')}")
    actual_files = output_file_count(OUTPUT)
    if actual_files != 8538:
        raise RuntimeError(f"v19 actual file count is not 8538: {actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or stats.get("source_records") != 8357:
        raise RuntimeError("v19 provenance does not bind source15 manifest")
    expected_stats = {
        "image_overlay": 79,
        "image_overlay_records": 79,
        "primary_image_overlay_records": 58,
        "supplement_image_overlay_records": 21,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v19 provenance stat {key} is {stats.get(key)!r}, expected {expected}")
    guide_provenance = provenance.get("guide_previews") or {}
    if guide_provenance.get("schema") != "github-pages-guide-preview-provenance/v2" or guide_provenance.get("source_map_schema") != "wow-recovery.guide-preview-source-map.v2":
        raise RuntimeError("v19 guide preview provenance is not v2")
    if guide_provenance.get("preview_count") != 22 or guide_provenance.get("group_count") != 6:
        raise RuntimeError("v19 guide preview provenance count is wrong")
    if guide_provenance.get("source_map_sha256") != V2_GUIDE_MAP_SHA256:
        raise RuntimeError("v19 guide preview provenance does not bind v2 map")

    old_provenance = read_object(V18_PROVENANCE, "v18 export provenance")
    old_overlays = {
        str(item.get("route")): item
        for item in old_provenance.get("files", [])
        if item.get("role") == "image_overlay"
    }
    overlays = [item for item in provenance.get("files", []) if item.get("role") == "image_overlay"]
    new_overlays = {str(item.get("route")): item for item in overlays}
    if len(old_overlays) != 69 or len(overlays) != 79 or not set(old_overlays).issubset(set(new_overlays)):
        raise RuntimeError("v19 overlay route set does not retain v18's 69 routes plus ten new routes")
    retained_mismatches: list[str] = []
    for route, old_item in old_overlays.items():
        new_item = new_overlays[route]
        output_file = OUTPUT / str(new_item.get("output_path") or "")
        if (
            str(new_item.get("derived_sha256") or "") != str(old_item.get("derived_sha256") or "")
            or not output_file.is_file()
            or sha256(output_file) != str(old_item.get("derived_sha256") or "")
        ):
            retained_mismatches.append(route)
    if retained_mismatches:
        raise RuntimeError(f"v18 retained overlay bytes changed: {retained_mismatches[:5]}")

    v19_map = read_object(V19_PRIMARY_MAP, "v19 primary map")
    expected_new_routes = {
        exporter.mirror.route_path(str(item.get("original") or item.get("logical_url") or ""))
        for item in v19_map.get("items", [])
    }
    actual_new_routes = set(new_overlays) - set(old_overlays)
    if len(expected_new_routes) != 10 or actual_new_routes != expected_new_routes:
        raise RuntimeError(
            f"v19 new overlay routes differ from the ten-item map: expected={sorted(expected_new_routes)}, actual={sorted(actual_new_routes)}"
        )
    new_overlay_bytes_verified = True
    for route in sorted(expected_new_routes):
        item = new_overlays[route]
        output_file = OUTPUT / str(item.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(item.get("derived_sha256") or ""):
            new_overlay_bytes_verified = False
            break
    if not new_overlay_bytes_verified:
        raise RuntimeError("v19 new overlay output bytes do not match provenance")

    section_checks: dict[str, dict[str, Any]] = {}
    notice = "These previews survive in the original guide pages. Full-size gallery images are still incomplete."
    expected_counts = {group[0]: len(group[1]) for group in [(g["group_id"], g["previews"]) for g in json.loads(V2_GUIDE_MAP.read_text(encoding="utf-8"))["groups"]]}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        page_path = OUTPUT / exporter.static_rel_for_route(gallery_route, {"kind": "html"})
        page = page_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{guide_previews._slug(group_id)}"
        route_markers = page.count('data-guide-preview-route=')
        section_checks[group_id] = {
            "path": rel(page_path),
            "section_id_count": page.count(f'id="{section_id}"'),
            "title_count": page.count("Preserved guide previews"),
            "notice_count": page.count(notice),
            "view_original_guide_count": page.count("View original guide"),
            "route_marker_count": route_markers,
            "expected_cards": expected_counts[group_id],
        }
        for key in ("section_id_count", "title_count", "notice_count", "view_original_guide_count"):
            if section_checks[group_id][key] != 1:
                raise RuntimeError(f"v19 guide preview section count failed: {group_id} {key}")
        if route_markers != expected_counts[group_id]:
            raise RuntimeError(f"v19 guide preview card count failed: {group_id} {route_markers}")

    city_page_path = OUTPUT / exporter.static_rel_for_route("/pvp/worldpvp/cityattacks-gallery.html", {"kind": "html"})
    city_page = city_page_path.read_text(encoding="utf-8")
    if "/pvp/worldpvp/images/city/ss1.jpg" in city_page or "dynamic_full_candidate" in city_page:
        raise RuntimeError("v19 City page contains a dynamic/full alias")
    if "addshots(" not in city_page:
        raise RuntimeError("v19 City page lost its dynamic gallery script")

    old_gallery_equal: dict[str, bool] = {}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        old_path = Path(ROOT / ".scratch/pages-resources-20261016-v18" / exporter.static_rel_for_route(gallery_route, {"kind": "html"}))
        new_path = OUTPUT / exporter.static_rel_for_route(gallery_route, {"kind": "html"})
        old_gallery_equal[group_id] = old_path.read_bytes() == new_path.read_bytes()
        if not old_gallery_equal[group_id]:
            raise RuntimeError(f"v19 changed existing v18 gallery output: {group_id}")

    return {
        "declared_output_files": result.get("output_files"),
        "provenance_declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "source_records": stats.get("source_records"),
        "overlay_records": len(overlays),
        "primary_overlay_records": expected_stats["primary_image_overlay_records"],
        "supplement_overlay_records": expected_stats["supplement_image_overlay_records"],
        "v18_overlay_routes_retained": len(old_overlays),
        "v18_overlay_bytes_verified": True,
        "v19_new_overlay_routes": sorted(expected_new_routes),
        "v19_new_overlay_bytes_verified": new_overlay_bytes_verified,
        "guide_preview_count": guide_provenance.get("preview_count"),
        "guide_gallery_pages": guide_provenance.get("group_count"),
        "guide_sections": section_checks,
        "city_dynamic_full_alias": False,
        "existing_v18_gallery_bytes_equal": old_gallery_equal,
    }


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = "python -X utf8 research/continuous-recovery-20261016/integration/v19-build/build_pages_v19.py"
    started = now()
    export_started = False
    result: dict[str, Any] | None = None
    preflight: dict[str, Any] | None = None
    locks_before: dict[str, str] | None = None
    free_before: int | None = None
    try:
        if RECEIPT.exists():
            raise RuntimeError(f"refusing to overwrite existing worker receipt: {RECEIPT}")
        validate_gates()
        locks_before = locked_input_hashes()
        if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
            raise RuntimeError("source15 source/site is missing")
        if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
            raise RuntimeError("refusing to overwrite existing v19 output or partial")
        free_before = shutil.disk_usage(OUTPUT.parent).free
        if free_before < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")

        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        preflight = preflight_loader()
        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=PRIMARY_MAPS,
            supplement_image_source_maps=SUPPLEMENT_MAPS,
            allow_later_image_supplements=True,
            guide_preview_map=V2_GUIDE_MAP,
        )
        postbuild = verify_postbuild(result)
        locks_after = locked_input_hashes()
        if locks_before != locks_after:
            raise RuntimeError("a locked source/map/production input changed during export")
        free_after = shutil.disk_usage(OUTPUT.parent).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor after export: {free_after} < {MIN_FREE_BYTES}")
        receipt = {
            "schema": "wow-recovery.integration.v19.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": True,
            "export_completed": True,
            "network_requests_by_builder": 0,
            "published": False,
            "source_stage": rel(SOURCE_STAGE),
            "source_stage_reused": True,
            "source_site": rel(SOURCE_SITE),
            "source_manifest": rel(SOURCE_MANIFEST),
            "source_manifest_sha256": locks_after[rel(SOURCE_MANIFEST)],
            "original_offline_manifest": rel(ORIGINAL_OFFLINE_MANIFEST),
            "original_offline_manifest_sha256": locks_after[rel(ORIGINAL_OFFLINE_MANIFEST)],
            "v18_provenance": rel(V18_PROVENANCE),
            "v18_provenance_sha256": locks_after[rel(V18_PROVENANCE)],
            "root_v17_input_acceptance": rel(ROOT_V17_ACCEPTANCE),
            "root_v17_input_acceptance_sha256": locks_after[rel(ROOT_V17_ACCEPTANCE)],
            "root_v18_export_acceptance": rel(ROOT_V18_EXPORT_ACCEPTANCE),
            "root_v18_export_acceptance_sha256": locks_after[rel(ROOT_V18_EXPORT_ACCEPTANCE)],
            "root_v18_local_acceptance": rel(ROOT_V18_LOCAL_ACCEPTANCE),
            "root_v18_local_acceptance_sha256": locks_after[rel(ROOT_V18_LOCAL_ACCEPTANCE)],
            "root_v18_browser_acceptance": rel(ROOT_V18_BROWSER_ACCEPTANCE),
            "root_v18_browser_acceptance_sha256": locks_after[rel(ROOT_V18_BROWSER_ACCEPTANCE)],
            "v18_build_receipt": rel(V18_BUILD_RECEIPT),
            "v18_build_receipt_sha256": locks_after[rel(V18_BUILD_RECEIPT)],
            "root_v2_code_acceptance": rel(ROOT_V2_ACCEPTANCE),
            "root_v2_code_acceptance_sha256": locks_after[rel(ROOT_V2_ACCEPTANCE)],
            "focused_test_receipt": rel(FOCUSED_RECEIPT),
            "focused_test_receipt_sha256": locks_after[rel(FOCUSED_RECEIPT)],
            "v19_input_preparation": rel(PREPARATION_RECEIPT),
            "v19_input_preparation_sha256": locks_after[rel(PREPARATION_RECEIPT)],
            "primary_source_maps": [rel(path) for path in PRIMARY_MAPS],
            "supplement_source_maps": [rel(path) for path in SUPPLEMENT_MAPS],
            "guide_preview_map": rel(V2_GUIDE_MAP),
            "map_sha256_before": {rel(path): locks_before[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, V1_GUIDE_MAP, V2_GUIDE_MAP]},
            "map_sha256_after": {rel(path): locks_after[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, V1_GUIDE_MAP, V2_GUIDE_MAP]},
            "maps_unchanged_during_export": True,
            "production_sha256_before": {key: locks_before[key] for key in PRODUCTION_SHA256},
            "production_sha256_after": {key: locks_after[key] for key in PRODUCTION_SHA256},
            "production_unchanged_during_export": True,
            "test_sha256_before": {key: locks_before[key] for key in TEST_SHA256},
            "test_sha256_after": {key: locks_after[key] for key in TEST_SHA256},
            "v19_primary_source_map": rel(V19_PRIMARY_MAP),
            "v19_primary_source_map_sha256": locks_after[rel(V19_PRIMARY_MAP)],
            "news_shared10_acceptance": rel(NEWS_SHARED10_ACCEPTANCE),
            "news_shared13_acceptance": rel(NEWS_SHARED13_ACCEPTANCE),
            "news_shared10_source_map": rel(NEWS_SHARED10_SOURCE_MAP),
            "news_shared13_source_map": rel(NEWS_SHARED13_SOURCE_MAP),
            "preflight_loader": preflight,
            "root_expected_primary_overlay_count": 58,
            "root_expected_supplement_overlay_count": 21,
            "root_expected_total_overlay_count": 79,
            "root_expected_guide_preview_count": 22,
            "root_expected_guide_gallery_pages": 6,
            "root_expected_city_cards": 3,
            "build": result,
            "postbuild_checks": postbuild,
            "output": rel(OUTPUT),
            "output_refused_if_existing_or_partial": True,
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
            "input_hashes_before": locks_before,
            "input_hashes_after": locks_after,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        free_after = shutil.disk_usage(OUTPUT.parent).free
        failure = {
            "schema": "wow-recovery.integration.v19.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": export_started,
            "export_completed": False,
            "network_requests_by_builder": 0,
            "published": False,
            "error": f"{type(exc).__name__}: {exc}",
            "output": rel(OUTPUT) if OUTPUT.exists() else None,
            "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if locks_before is not None:
            failure["input_hashes_before"] = locks_before
        try:
            write_receipt(failure)
        except Exception as receipt_exc:
            failure["receipt_write_error"] = f"{type(receipt_exc).__name__}: {receipt_exc}"
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
