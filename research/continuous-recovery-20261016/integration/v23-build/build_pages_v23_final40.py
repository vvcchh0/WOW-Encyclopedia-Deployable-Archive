#!/usr/bin/env python3
"""Run the single root-authorized v23 final40 Pages export.

This file is prepared for the later GO only.  It is not invoked by the
final40 input-preparation step.  Its inputs are source15, the frozen v22
provenance/maps, and the separate final40 neighbor maps; it refuses an
existing output or partial tree and records a failure receipt instead of
retrying an export.
"""

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
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v23"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v23-build/worker-build-v23-final40.json"
PREPARATION_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v23-build/preflight-v23-neighbor-inputs-final40.json"
V22_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v22/export-provenance.json"
V22_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v22-export-acceptance.json"
CODE_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-guide-collections-code-acceptance.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
COLLECTION_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json"
FINAL_NUMERIC_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json"
FINAL_CATALOG_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

BASE_PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
]
V22_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json"
V20_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
V21_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json"
PRIMARY_MAPS = [*BASE_PRIMARY_MAPS, V22_PRIMARY_MAP, V20_PRIMARY_MAP, V21_PRIMARY_MAP]

OLD_SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json",
]
SUPPLEMENT_MAPS = [*OLD_SUPPLEMENT_MAPS, FINAL_NUMERIC_MAP, FINAL_CATALOG_MAP]

FROZEN_HASHES = {
    ".scratch/offline-navigation-20261015-v15/build-manifest.json": "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002",
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9",
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33",
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77",
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
    "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json": "de179aa26f0453cd29b30b76600bf22dd9e0a3b443e03300238c13c97bb624c6",
}
PRODUCTION_HASHES = {
    "tools/export_github_pages.py": "50bd3569f77d3d52c52ed7077726d7dc99fbee23a3a0ced076a6523198b9225d",
    "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
    "tools/guide_image_collections.py": "9d0f20679733e29c6eb789fd4a05883056e4994ccb173e1dc843d68e070dc057",
}

sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages  # noqa: E402
import guide_image_collections  # noqa: E402
import guide_previews  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def require_hash(path: Path, expected: str, label: str) -> str:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA changed: expected {expected}, got {actual}")
    return actual


def locked_hashes() -> dict[str, str]:
    paths = dict(FROZEN_HASHES)
    paths.update(PRODUCTION_HASHES)
    paths[rel(SOURCE_MANIFEST)] = FROZEN_HASHES[rel(SOURCE_MANIFEST)]
    paths[rel(PREPARATION_RECEIPT)] = "6f9072e9dc3717740c52290165e8d7d9f97ff5494eca7481e46a8f63f31139dd"
    paths[rel(V22_PROVENANCE)] = "b2c111baac62b28490a81f5ea25e978ebdc29de8af2072d85f8bb34c8d25131f"
    paths[rel(V22_ACCEPTANCE)] = "03cc173167ba5a7282efcff797b7261c4f8423d4fe252b1a8d56e6becdfbda6c"
    paths[rel(CODE_ACCEPTANCE)] = "a236dd67726399a45ff9a71e91287590553e7fc3f5b69906d4f95ab604a9e812"
    return {relative: require_hash(ROOT / relative, expected, relative) for relative, expected in paths.items()}


def validate_gates() -> dict[str, Any]:
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if str(manifest.get("anchor_timestamp") or "") != ANCHOR:
        raise RuntimeError("source15 anchor changed")
    v22 = read_json(V22_ACCEPTANCE, "root v22 acceptance")
    if v22.get("accepted") is not True or v22.get("published") is not False:
        raise RuntimeError("v22 acceptance gate is not accepted/unpublished")
    stats = v22.get("stats") or {}
    expected = {
        "image_overlay": 122,
        "primary_image_overlay_records": 100,
        "supplement_image_overlay_records": 22,
        "guide_preview_count": 22,
        "guide_preview_gallery_pages": 6,
    }
    if any(stats.get(key) != value for key, value in expected.items()):
        raise RuntimeError(f"v22 overlay/preview stats changed: {stats}")
    if v22.get("checked_declared_files") != 8580 or v22.get("actual_files") != 8581:
        raise RuntimeError("v22 file counts changed")
    code = read_json(CODE_ACCEPTANCE, "guide collection code acceptance")
    if code.get("accepted") is not True or code.get("export_authorized") is not False:
        raise RuntimeError("guide collection code gate changed")
    preparation = read_json(PREPARATION_RECEIPT, "final40 preflight receipt")
    loader = preparation.get("loader_preflight") or {}
    checks = {
        "network_requests": 0,
        "export_executed": False,
        "preflight_primary_overlay_records": 100,
        "preflight_supplement_overlay_records": 62,
        "preflight_total_overlay_records": 162,
        "guide_preview_groups": 6,
        "guide_preview_images": 22,
        "guide_collection_groups": 3,
        "guide_collection_images": 32,
        "catalog_only_images": 8,
    }
    if any(loader.get(key) != value for key, value in checks.items()):
        raise RuntimeError(f"final40 preflight loader gate changed: {loader}")
    copied = preparation.get("copied_assets") or {}
    if copied.get("count") != 40 or copied.get("bytes") != 6901604 or copied.get("byte_for_byte_and_sha_verified") is not True or copied.get("pillow_all_frames_verified") is not True:
        raise RuntimeError(f"final40 copied asset gate changed: {copied}")
    return {"v22_acceptance": v22, "final40_preflight": preparation}


def preflight_loader(manifest: dict[str, Any]) -> dict[str, Any]:
    route_records: dict[str, dict[str, Any]] = {}
    route_to_static: dict[str, str] = {}
    relative_paths: set[str] = set()
    for record in manifest.get("files") or []:
        route = export_github_pages.safe_route(str(record.get("route") or ""))
        route_records[route] = record
        relative = export_github_pages.static_rel_for_route(route, record)
        relative_paths.add(relative)
        route_to_static[route] = export_github_pages.static_url(BASE_PATH, relative)
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(route_records) | {str(alias) for alias in aliases}
    primary, primary_bytes = export_github_pages.load_image_overlays(
        tuple(PRIMARY_MAPS), workspace_root=ROOT, anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes, frozen_static_paths=relative_paths,
    )
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_static = relative_paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(SUPPLEMENT_MAPS), workspace_root=ROOT, anchor_timestamp=ANCHOR,
        frozen_routes=overlay_routes, frozen_static_paths=overlay_static,
        allow_later_image_supplements=True,
    )
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    preview = guide_previews.load_guide_preview_map(
        GUIDE_PREVIEW_MAP, workspace_root=ROOT, source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST, manifest=manifest, route_to_static=route_to_static,
    )
    collections = guide_image_collections.load_guide_image_collection_map(
        COLLECTION_MAP, workspace_root=ROOT, manifest_path=SOURCE_MANIFEST,
        manifest=manifest, overlays=[*primary, *supplement], route_to_static=route_to_static,
        base_path=BASE_PATH,
    )
    if (len(primary), len(supplement), collections.image_count, len(collections.groups)) != (100, 62, 32, 3):
        raise RuntimeError(f"v23 loader counts changed: {len(primary)}/{len(supplement)}/{collections.image_count}/{len(collections.groups)}")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "guide_preview_groups": len(preview.groups),
        "guide_preview_images": preview.preview_count,
        "guide_collection_groups": len(collections.groups),
        "guide_collection_images": collections.image_count,
        "network_requests": 0,
    }


def verify_postbuild(result: dict[str, Any]) -> dict[str, Any]:
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v23 output or partial output state is invalid after export")
    provenance = read_json(OUTPUT / "export-provenance.json", "v23 export provenance")
    stats = provenance.get("stats") or {}
    expected_stats = {
        "source_records": 8357,
        "image_overlay": 162,
        "image_overlay_records": 162,
        "primary_image_overlay_records": 100,
        "supplement_image_overlay_records": 62,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
        "guide_image_collection_pages": 6,
        "guide_image_collection_images": 32,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v23 provenance stat {key}={stats.get(key)!r}, expected {expected}")
    actual_files = sum(1 for item in OUTPUT.rglob("*") if item.is_file())
    if result.get("output_files") != 8620 or stats.get("output_files") != 8620 or actual_files != 8621:
        raise RuntimeError(f"v23 file counts changed: result={result.get('output_files')} provenance={stats.get('output_files')} actual={actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_HASHES[rel(SOURCE_MANIFEST)]:
        raise RuntimeError("v23 provenance does not bind source15")
    previews = provenance.get("guide_previews") or {}
    if previews.get("preview_count") != 22 or previews.get("group_count") != 6:
        raise RuntimeError("v23 guide preview provenance changed")
    collections = provenance.get("guide_image_collections") or {}
    if collections.get("image_count") != 32 or collections.get("group_count") != 3:
        raise RuntimeError("v23 guide collection provenance changed")
    return {"declared_output_files": stats.get("output_files"), "actual_output_files": actual_files, "stats": stats, "guide_previews": previews, "guide_collections": collections}


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = '"C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe" -X utf8 research/continuous-recovery-20261016/integration/v23-build/build_pages_v23_final40.py'
    started = now()
    export_started = False
    free_before: int | None = None
    locks_before: dict[str, str] | None = None
    try:
        if RECEIPT.exists():
            raise RuntimeError(f"refusing to overwrite existing worker receipt: {RECEIPT}")
        gates = validate_gates()
        locks_before = locked_hashes()
        if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
            raise RuntimeError(f"refusing to overwrite existing v23 output or partial: {OUTPUT}")
        free_before = shutil.disk_usage(OUTPUT.parent).free
        if free_before < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")
        manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
        preflight = preflight_loader(manifest)
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
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=COLLECTION_MAP,
        )
        postbuild = verify_postbuild(result)
        locks_after = locked_hashes()
        if locks_before != locks_after:
            raise RuntimeError("a locked source/map/production input changed during export")
        free_after = shutil.disk_usage(OUTPUT.parent).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor after export: {free_after} < {MIN_FREE_BYTES}")
        receipt = {
            "schema": "wow-recovery.integration.v23.build-receipt.final40.v1",
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
            "v22_provenance": rel(V22_PROVENANCE),
            "v22_provenance_sha256": locks_after[rel(V22_PROVENANCE)],
            "v22_acceptance": rel(V22_ACCEPTANCE),
            "v22_acceptance_sha256": locks_after[rel(V22_ACCEPTANCE)],
            "final40_preflight": rel(PREPARATION_RECEIPT),
            "final40_preflight_sha256": locks_after[rel(PREPARATION_RECEIPT)],
            "primary_source_maps": [rel(path) for path in PRIMARY_MAPS],
            "supplement_source_maps": [rel(path) for path in SUPPLEMENT_MAPS],
            "guide_preview_map": rel(GUIDE_PREVIEW_MAP),
            "guide_image_collection_map": rel(COLLECTION_MAP),
            "map_sha256_before": {rel(path): locks_before.get(rel(path), sha256(path)) for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP, COLLECTION_MAP]},
            "map_sha256_after": {rel(path): locks_after.get(rel(path), sha256(path)) for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP, COLLECTION_MAP]},
            "maps_unchanged_during_export": True,
            "production_sha256_before": {key: locks_before[key] for key in PRODUCTION_HASHES},
            "production_sha256_after": {key: locks_after[key] for key in PRODUCTION_HASHES},
            "production_unchanged_during_export": True,
            "preflight_loader": preflight,
            "build": result,
            "postbuild_checks": postbuild,
            "output": rel(OUTPUT),
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
            "schema": "wow-recovery.integration.v23.build-receipt.final40.v1",
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
