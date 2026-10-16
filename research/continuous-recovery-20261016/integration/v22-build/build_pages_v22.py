#!/usr/bin/env python3
"""Run the one root-authorized local v22 Pages export from frozen inputs."""

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
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v22"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v22-build/worker-build-v22.json"
PREPARATION_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v22-build/prepare-v22-inputs.json"
V22_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json"
V21_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json"
V21_LATE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json"
V20_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
ROOT_V20_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v20-export-acceptance.json"
V21_FAILURE_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v21-build/worker-build-v21.json"
ROOT_PROMOTION_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-export-promotion-fix-acceptance.json"
V2_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
V1_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"
CONTENT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-news-content01-source-acceptance.json"
STATIC_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-static-main01-source-acceptance.json"
CONTENT_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-content01/output/source-map.json"
STATIC_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/static-main01/output/source-map.json"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
MIN_FREE_BYTES = 11_005_853_696
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

BASE_PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
]
# Keep v20's established provenance as the first owner of its 34 routes.  The
# v22 map intentionally clones those records while adding the 16 new routes;
# retaining v20 first makes a future export preserve the frozen v20 source-map
# identity for inherited files while v22 remains authoritative for its delta.
PRIMARY_MAPS = [*BASE_PRIMARY_MAPS, V20_PRIMARY_MAP, V22_PRIMARY_MAP]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    V21_LATE_MAP,
]

FROZEN_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
ORIGINAL_OFFLINE_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V20_PRIMARY_MAP_SHA256 = "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77"
V20_PROVENANCE_SHA256 = "c4b741691f9ac8ad8201dfc35e6af81119c60e62afa07f08c569ec3a9e7a9f50"
ROOT_V20_ACCEPTANCE_SHA256 = "8db1088841c41e2fde6c72e45b10aede1221b15e65600e19bd09eba8e0a9e92e"
V21_PRIMARY_MAP_SHA256 = "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33"
V21_LATE_MAP_SHA256 = "a21faaf398e4b605a441da7ca9f23d23e75e1e1bfb59a824d59e5aa7a981d772"
V21_FAILURE_RECEIPT_SHA256 = "7e5b96e843e4ef11f1cc8c4446a99be0920ae53b575f16431fad03ed052a6fe9"
ROOT_PROMOTION_ACCEPTANCE_SHA256 = "721d5a89900b99aafee6370045686ff491b969e0d4d21d9b895686984646a25a"
V22_PRIMARY_MAP_SHA256 = "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9"
PREPARATION_RECEIPT_SHA256 = "ef86df1865b94b3c5cf83a63fa4ae6b0a074b52927f8067d55847a706208c53e"
CONTENT_ACCEPTANCE_SHA256 = "70deedfbc1cd0511c82e41dbd786f81224af8386a7bd1adb73160512bd965475"
STATIC_ACCEPTANCE_SHA256 = "006bae6e91ee2123748bf2009a0a5ad28a36c14d482c68487a8e668c0eeb1d7d"
CONTENT_SOURCE_MAP_SHA256 = "d252e2ad23fb240a511d665a9f4bce2b39dd44fe7ddac339cb6678fb34e5e420"
STATIC_SOURCE_MAP_SHA256 = "b19518b7eca6de8767d00da528529fa8c067a07befb09286b0e5b1148c15f167"
V2_GUIDE_MAP_SHA256 = "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581"
V1_GUIDE_MAP_SHA256 = "cf0da5fec45993684676d94d1cc09fad3f5a421dabbb18b56861000daa6248b2"

PRODUCTION_SHA256 = {
    "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
    "tools/export_github_pages.py": "2e1a4ee9ae06e3e7df6ec9a3bb6da1a16fc505168d49f8aeb6dc28082d1d1b92",
}
TEST_SHA256 = {
    "tests/test_guide_previews.py": "ec8d351347efb790cb003bff2f0e94493a85f6da75f801a26b8422a6d88b9852",
    "tests/test_export_promotion.py": "92540a5f672f1b83b50a37e2454fc2c1a6a3dbe061761834be38267b82eb7a72",
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
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": V20_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": V21_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json": V21_LATE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": V22_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": V2_GUIDE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/guide-previews-source-map.json": V1_GUIDE_MAP_SHA256,
}

sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages  # noqa: E402


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


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def require_hash(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 changed: expected {expected}, got {actual}")
    return actual


def locked_input_hashes() -> dict[str, str]:
    paths: dict[str, tuple[Path, str]] = {
        rel(SOURCE_MANIFEST): (SOURCE_MANIFEST, FROZEN_MANIFEST_SHA256),
        rel(ORIGINAL_OFFLINE_MANIFEST): (ORIGINAL_OFFLINE_MANIFEST, ORIGINAL_OFFLINE_MANIFEST_SHA256),
        rel(V20_PROVENANCE): (V20_PROVENANCE, V20_PROVENANCE_SHA256),
        rel(ROOT_V20_ACCEPTANCE): (ROOT_V20_ACCEPTANCE, ROOT_V20_ACCEPTANCE_SHA256),
        rel(V21_FAILURE_RECEIPT): (V21_FAILURE_RECEIPT, V21_FAILURE_RECEIPT_SHA256),
        rel(ROOT_PROMOTION_ACCEPTANCE): (ROOT_PROMOTION_ACCEPTANCE, ROOT_PROMOTION_ACCEPTANCE_SHA256),
        rel(PREPARATION_RECEIPT): (PREPARATION_RECEIPT, PREPARATION_RECEIPT_SHA256),
        rel(V22_PRIMARY_MAP): (V22_PRIMARY_MAP, V22_PRIMARY_MAP_SHA256),
        rel(V21_PRIMARY_MAP): (V21_PRIMARY_MAP, V21_PRIMARY_MAP_SHA256),
        rel(V21_LATE_MAP): (V21_LATE_MAP, V21_LATE_MAP_SHA256),
        rel(CONTENT_ACCEPTANCE): (CONTENT_ACCEPTANCE, CONTENT_ACCEPTANCE_SHA256),
        rel(STATIC_ACCEPTANCE): (STATIC_ACCEPTANCE, STATIC_ACCEPTANCE_SHA256),
        rel(CONTENT_SOURCE_MAP): (CONTENT_SOURCE_MAP, CONTENT_SOURCE_MAP_SHA256),
        rel(STATIC_SOURCE_MAP): (STATIC_SOURCE_MAP, STATIC_SOURCE_MAP_SHA256),
        rel(V1_GUIDE_MAP): (V1_GUIDE_MAP, V1_GUIDE_MAP_SHA256),
        rel(V2_GUIDE_MAP): (V2_GUIDE_MAP, V2_GUIDE_MAP_SHA256),
    }
    for relative, expected in {**PRODUCTION_SHA256, **TEST_SHA256, **MAP_SHA256}.items():
        paths[relative] = (ROOT / relative, expected)
    return {relative: require_hash(path, expected, relative) for relative, (path, expected) in paths.items()}


def validate_gates() -> dict[str, Any]:
    v20_acceptance = read_object(ROOT_V20_ACCEPTANCE, "root v20 export acceptance")
    if v20_acceptance.get("accepted") is not True or v20_acceptance.get("published") is not False:
        raise RuntimeError("root v20 tree is not accepted and unpublished")
    if v20_acceptance.get("checked_declared_files") != 8561 or v20_acceptance.get("actual_files") != 8562:
        raise RuntimeError("root v20 counts changed")
    v20_stats = v20_acceptance.get("stats") or {}
    for key, expected in {
        "output_files": 8561,
        "source_records": 8357,
        "image_overlay": 103,
        "primary_image_overlay_records": 82,
        "supplement_image_overlay_records": 21,
        "guide_preview_count": 22,
        "guide_preview_gallery_pages": 6,
    }.items():
        if v20_stats.get(key) != expected:
            raise RuntimeError(f"root v20 stat {key} changed: {v20_stats.get(key)!r}")
    v20_provenance = read_object(V20_PROVENANCE, "v20 provenance")
    if (v20_provenance.get("stats") or {}).get("source_records") != 8357:
        raise RuntimeError("v20 provenance source count changed")

    v21_failure = read_object(V21_FAILURE_RECEIPT, "v21 failure receipt")
    if v21_failure.get("export_started") is not True or v21_failure.get("export_completed") is not False or "WinError 5" not in str(v21_failure.get("error")):
        raise RuntimeError("v21 failure receipt no longer records the bounded rename failure")
    promotion = read_object(ROOT_PROMOTION_ACCEPTANCE, "export promotion acceptance")
    if promotion.get("accepted") is not True or promotion.get("network_requests") != 0:
        raise RuntimeError("export promotion fix is not accepted local-only evidence")
    if (promotion.get("implementation") or {}).get("sha256") != PRODUCTION_SHA256["tools/export_github_pages.py"] or (promotion.get("implementation") or {}).get("errno_fallback") is not False:
        raise RuntimeError("export promotion acceptance does not bind the strict helper")

    content = read_object(CONTENT_ACCEPTANCE, "news content acceptance")
    static = read_object(STATIC_ACCEPTANCE, "static main acceptance")
    if content.get("accepted") is not True or len(content.get("accepted_images") or []) != 10 or content.get("image_bytes") != 82894:
        raise RuntimeError("news content acceptance count/bytes changed")
    if static.get("accepted") is not True or len(static.get("accepted_images") or []) != 6 or static.get("image_bytes") != 69733:
        raise RuntimeError("static main acceptance count/bytes changed")
    preparation = read_object(PREPARATION_RECEIPT, "v22 input preparation receipt")
    if preparation.get("asset_count") != 16 or preparation.get("asset_bytes") != 152627 or preparation.get("network_requests") != 0 or (preparation.get("primary_map") or {}).get("sha256") != V22_PRIMARY_MAP_SHA256 or (preparation.get("v21_primary_input") or {}).get("sha256") != V21_PRIMARY_MAP_SHA256:
        raise RuntimeError("v22 preparation does not bind the sixteen accepted primary assets")
    return {"v20_acceptance": v20_acceptance, "promotion_acceptance": promotion, "preparation": preparation}


def output_file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def preflight_loader() -> dict[str, Any]:
    import guide_previews

    manifest = read_object(SOURCE_MANIFEST, "source15 manifest")
    records = list(manifest.get("files") or [])
    route_records: dict[str, dict[str, Any]] = {}
    route_to_static: dict[str, str] = {}
    relative_paths: set[str] = set()
    for record in records:
        route = export_github_pages.safe_route(str(record.get("route") or ""))
        route_records[route] = record
        relative = export_github_pages.static_rel_for_route(route, record)
        relative_paths.add(relative)
        route_to_static[route] = export_github_pages.static_url(BASE_PATH, relative)
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(route_records) | {str(alias) for alias in aliases}
    primary, primary_bytes = export_github_pages.load_image_overlays(
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=frozen_routes,
        frozen_static_paths=set(relative_paths),
    )
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_static = set(relative_paths) | {str(item["relative"]) for item in primary}
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(SUPPLEMENT_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_static,
        allow_later_image_supplements=True,
    )
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    bundle = guide_previews.load_guide_preview_map(
        V2_GUIDE_MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    if len(primary) != 100 or len(supplement) != 22:
        raise RuntimeError(f"v22 loader count mismatch: primary={len(primary)}, supplement={len(supplement)}")
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
    import guide_previews

    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v22 output or partial output state is invalid after export")
    provenance = read_object(OUTPUT / "export-provenance.json", "v22 provenance")
    stats = provenance.get("stats") or {}
    if result.get("output_files") != 8580 or stats.get("output_files") != 8580:
        raise RuntimeError(f"v22 declared output count is not 8580: result={result.get('output_files')}, provenance={stats.get('output_files')}")
    actual_files = output_file_count(OUTPUT)
    if actual_files != 8581:
        raise RuntimeError(f"v22 actual file count is not 8581: {actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or stats.get("source_records") != 8357:
        raise RuntimeError("v22 provenance does not bind source15 manifest")
    expected_stats = {
        "image_overlay": 122,
        "image_overlay_records": 122,
        "primary_image_overlay_records": 100,
        "supplement_image_overlay_records": 22,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v22 provenance stat {key} is {stats.get(key)!r}, expected {expected}")
    guide = provenance.get("guide_previews") or {}
    if guide.get("preview_count") != 22 or guide.get("group_count") != 6 or guide.get("source_map_sha256") != V2_GUIDE_MAP_SHA256:
        raise RuntimeError("v22 guide preview provenance mismatch")

    old = read_object(V20_PROVENANCE, "v20 provenance")
    old_overlays = {str(item.get("route")): item for item in old.get("files", []) if item.get("role") == "image_overlay"}
    overlays = [item for item in provenance.get("files", []) if item.get("role") == "image_overlay"]
    by_route = {str(item.get("route")): item for item in overlays}
    if len(old_overlays) != 103 or len(overlays) != 122 or not set(old_overlays).issubset(by_route):
        raise RuntimeError("v22 did not retain all frozen v20 overlay routes")
    # source_map identity is checked below with the explicit v20->v22 clone
    # rule.  The remaining fields must stay byte-for-byte/provenance-equal to
    # the accepted v20 record.
    stable_fields = ("derived_sha256", "derived_length", "source_sha256", "source_length", "mime", "temporal_class", "original_url", "route", "output_path")
    retained_mismatches: list[str] = []
    for route, old_item in old_overlays.items():
        current = by_route[route]
        if any(key in old_item and current.get(key) != old_item.get(key) for key in stable_fields):
            retained_mismatches.append(f"{route}:metadata")
        output_file = OUTPUT / str(current.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(old_item.get("derived_sha256") or ""):
            retained_mismatches.append(f"{route}:bytes")
    def map_route(item: dict[str, Any]) -> str:
        return export_github_pages.mirror.route_path(str(item.get("original") or item.get("logical_url") or ""))

    v20_map = read_object(V20_PRIMARY_MAP, "v20 map")
    v21_map = read_object(V21_PRIMARY_MAP, "v21 map")
    v22_map = read_object(V22_PRIMARY_MAP, "v22 map")
    v20_routes = {map_route(item) for item in v20_map.get("items", [])}
    v21_routes = {map_route(item) for item in v21_map.get("items", [])}
    v22_routes = {map_route(item) for item in v22_map.get("items", [])}
    allowed_v20_map_identity = (rel(V20_PRIMARY_MAP), V20_PRIMARY_MAP_SHA256)
    allowed_v22_clone_identity = (rel(V22_PRIMARY_MAP), V22_PRIMARY_MAP_SHA256)
    for route, old_item in old_overlays.items():
        current = by_route[route]
        current_identity = (current.get("source_map"), current.get("source_map_sha256"))
        old_identity = (old_item.get("source_map"), old_item.get("source_map_sha256"))
        # A v20 route may retain its original map identity (the normal future
        # ordering) or be represented by the v22 clone already promoted in
        # this one completed export.  No other provenance source is accepted.
        if current_identity not in {old_identity, allowed_v20_map_identity, allowed_v22_clone_identity}:
            retained_mismatches.append(f"{route}:source_map")
    if retained_mismatches:
        raise RuntimeError(f"frozen v20 overlay metadata/bytes changed: {retained_mismatches[:5]}")

    late_map = read_object(V21_LATE_MAP, "v21 late map")
    late_items = late_map.get("items") or []
    if len(v20_routes) != 34 or len(v21_routes) != 36 or len(v22_routes) != 52 or len(late_items) != 1:
        raise RuntimeError(f"v22 map route counts changed: v20={len(v20_routes)}, v21={len(v21_routes)}, v22={len(v22_routes)}, late={len(late_items)}")
    v21_delta = v21_routes - v20_routes
    v22_delta = v22_routes - v21_routes
    late_route = map_route(late_items[0])
    if len(v21_delta) != 2 or len(v22_delta) != 16:
        raise RuntimeError(f"v22 route deltas changed: v21={len(v21_delta)}, v22={len(v22_delta)}")
    actual_new = set(by_route) - set(old_overlays)
    expected_new = v21_delta | v22_delta | {late_route}
    if actual_new != expected_new:
        raise RuntimeError(f"v22 new overlay routes differ: expected={sorted(expected_new)}, actual={sorted(actual_new)}")

    def check_map_item(route: str, item: dict[str, Any], label: str) -> None:
        output_item = by_route.get(route)
        if output_item is None:
            raise RuntimeError(f"{label} route missing: {route}")
        output_file = OUTPUT / str(output_item.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(item.get("sha256") or ""):
            raise RuntimeError(f"{label} bytes mismatch: {route}")
        for output_key, map_key in (("derived_sha256", "sha256"), ("derived_length", "length"), ("mime", "mime"), ("cdx_digest", "cdx_digest"), ("actual_capture_timestamp", "actual_timestamp"), ("indexed_capture_timestamp", "indexed_capture_timestamp")):
            if map_key in item and output_item.get(output_key) != item.get(map_key):
                raise RuntimeError(f"{label} provenance mismatch {output_key}: {route}")

    v22_items = {map_route(item): item for item in v22_map.get("items", [])}
    for route, item in v22_items.items():
        check_map_item(route, item, "v22 primary")
        # The 34 inherited v20 routes can be sourced from the frozen v20 map;
        # the v22 map binding is required for only the two v21 delta routes and
        # sixteen newly accepted assets.
        if route not in v20_routes and by_route[route].get("source_map_sha256") != V22_PRIMARY_MAP_SHA256:
            raise RuntimeError(f"v22 primary provenance did not bind v22 map: {route}")
    late_item = late_items[0]
    check_map_item(late_route, late_item, "v21 late supplement")
    late_output = by_route[late_route]
    if late_item.get("actual_timestamp") != "20080512231210" or late_item.get("temporal_class") != "late_2008" or late_item.get("pre_anchor_digest_match") is not True or late_output.get("actual_capture_timestamp") != "20080512231210":
        raise RuntimeError("late supplement timestamp/digest evidence changed")

    notice = "These previews survive in the original guide pages. Full-size gallery images are still incomplete."
    guide_doc = json.loads(V2_GUIDE_MAP.read_text(encoding="utf-8"))
    expected_counts = {str(group["group_id"]): len(group["previews"]) for group in guide_doc["groups"]}
    sections: dict[str, dict[str, Any]] = {}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        page_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        page = page_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{guide_previews._slug(group_id)}"
        sections[group_id] = {
            "path": rel(page_path),
            "section_id_count": page.count(f'id="{section_id}"'),
            "title_count": page.count("Preserved guide previews"),
            "notice_count": page.count(notice),
            "view_original_guide_count": page.count("View original guide"),
            "route_marker_count": page.count("data-guide-preview-route="),
            "expected_cards": expected_counts[group_id],
        }
        for key in ("section_id_count", "title_count", "notice_count", "view_original_guide_count"):
            if sections[group_id][key] != 1:
                raise RuntimeError(f"guide preview section count failed: {group_id} {key}")
        if sections[group_id]["route_marker_count"] != expected_counts[group_id]:
            raise RuntimeError(f"guide preview card count failed: {group_id}")

    city_route = "/pvp/worldpvp/cityattacks-gallery.html"
    city_page = (OUTPUT / export_github_pages.static_rel_for_route(city_route, {"kind": "html"})).read_text(encoding="utf-8")
    if "dynamic_full_candidate" in city_page or "/pvp/worldpvp/images/city/ss1.jpg" in city_page or "addshots(" not in city_page:
        raise RuntimeError("City page dynamic gallery invariants failed")
    old_gallery_equal: dict[str, bool] = {}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        old_path = ROOT / ".scratch/pages-resources-20261016-v20" / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        new_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        old_gallery_equal[group_id] = old_path.read_bytes() == new_path.read_bytes()
        if not old_gallery_equal[group_id]:
            raise RuntimeError(f"existing v20 gallery changed: {group_id}")
    return {
        "declared_output_files": result.get("output_files"),
        "provenance_declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "source_records": stats.get("source_records"),
        "overlay_records": len(overlays),
        "primary_overlay_records": expected_stats["primary_image_overlay_records"],
        "supplement_overlay_records": expected_stats["supplement_image_overlay_records"],
        "v20_overlay_routes_retained": len(old_overlays),
        "v21_delta_routes": sorted(v21_delta),
        "v22_new_primary_routes": sorted(v22_delta),
        "v21_late_supplement_route": late_route,
        "new_overlay_bytes_verified": True,
        "guide_preview_count": guide.get("preview_count"),
        "guide_gallery_pages": guide.get("group_count"),
        "guide_sections": sections,
        "city_dynamic_full_alias": False,
        "existing_v20_gallery_bytes_equal": old_gallery_equal,
    }


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = '"C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe" -X utf8 research/continuous-recovery-20261016/integration/v22-build/build_pages_v22.py'
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
            raise RuntimeError("refusing to overwrite existing v22 output or partial")
        free_before = shutil.disk_usage(OUTPUT.parent).free
        if free_before < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")
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
            "schema": "wow-recovery.integration.v22.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": True,
            "export_completed": True,
            "network_requests_by_builder": 0,
            "published": False,
            "source_stage": rel(SOURCE_STAGE),
            "source_site": rel(SOURCE_SITE),
            "source_manifest": rel(SOURCE_MANIFEST),
            "source_manifest_sha256": locks_after[rel(SOURCE_MANIFEST)],
            "original_offline_manifest": rel(ORIGINAL_OFFLINE_MANIFEST),
            "original_offline_manifest_sha256": locks_after[rel(ORIGINAL_OFFLINE_MANIFEST)],
            "v20_provenance": rel(V20_PROVENANCE),
            "v20_provenance_sha256": locks_after[rel(V20_PROVENANCE)],
            "root_v20_acceptance": rel(ROOT_V20_ACCEPTANCE),
            "root_v20_acceptance_sha256": locks_after[rel(ROOT_V20_ACCEPTANCE)],
            "v21_failure_receipt": rel(V21_FAILURE_RECEIPT),
            "v21_failure_receipt_sha256": locks_after[rel(V21_FAILURE_RECEIPT)],
            "root_promotion_fix_acceptance": rel(ROOT_PROMOTION_ACCEPTANCE),
            "root_promotion_fix_acceptance_sha256": locks_after[rel(ROOT_PROMOTION_ACCEPTANCE)],
            "v22_input_preparation": rel(PREPARATION_RECEIPT),
            "v22_input_preparation_sha256": locks_after[rel(PREPARATION_RECEIPT)],
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
            "v21_primary_source_map": rel(V21_PRIMARY_MAP),
            "v21_primary_source_map_sha256": locks_after[rel(V21_PRIMARY_MAP)],
            "v21_late_supplement_source_map": rel(V21_LATE_MAP),
            "v21_late_supplement_source_map_sha256": locks_after[rel(V21_LATE_MAP)],
            "v22_primary_source_map": rel(V22_PRIMARY_MAP),
            "v22_primary_source_map_sha256": locks_after[rel(V22_PRIMARY_MAP)],
            "content_acceptance": rel(CONTENT_ACCEPTANCE),
            "content_acceptance_sha256": locks_after[rel(CONTENT_ACCEPTANCE)],
            "static_acceptance": rel(STATIC_ACCEPTANCE),
            "static_acceptance_sha256": locks_after[rel(STATIC_ACCEPTANCE)],
            "content_source_map": rel(CONTENT_SOURCE_MAP),
            "content_source_map_sha256": locks_after[rel(CONTENT_SOURCE_MAP)],
            "static_source_map": rel(STATIC_SOURCE_MAP),
            "static_source_map_sha256": locks_after[rel(STATIC_SOURCE_MAP)],
            "preflight_loader": preflight,
            "root_expected_primary_overlay_count": 100,
            "root_expected_supplement_overlay_count": 22,
            "root_expected_total_overlay_count": 122,
            "root_expected_source_records": 8357,
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
            "schema": "wow-recovery.integration.v22.build-receipt.v1",
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
        write_receipt(failure)
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
