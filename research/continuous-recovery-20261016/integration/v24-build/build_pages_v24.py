#!/usr/bin/env python3
"""Single-export v24 helper, guarded until root accepts NEWS-CONTENT02.

Without --go this performs only the v24 loader preflight and writes a local
preflight receipt. With --go it performs exactly one export into a new v24
output and refuses existing output or partial trees. This file is prepared
offline; it is not invoked by the current input preparation step.
"""

from __future__ import annotations

import argparse
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
V23_OUTPUT = ROOT / ".scratch/pages-resources-20261016-v23"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v24"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v24-build/worker-build-v24.json"
PREFLIGHT_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v24-build/preflight-v24-inputs.json"
INPUT_PLAN = ROOT / "research/continuous-recovery-20261016/integration/v24-build/prepare-v24-input-plan.json"
V23_PROVENANCE = V23_OUTPUT / "export-provenance.json"
V23_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v23-export-acceptance.json"
V23_PREP = ROOT / "research/continuous-recovery-20261016/integration/v23-build/preflight-v23-neighbor-inputs-final40.json"
V23_WORKER = ROOT / "research/continuous-recovery-20261016/integration/v23-build/worker-build-v23-final40.json"
FRESH_MAP = ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json"
FRESH_RECEIPTS = [
    ROOT / "research/continuous-recovery-20261016/publication/root-news-content02-source-acceptance.json",
    ROOT / "research/continuous-recovery-20261016/publication/root-news-content03-source-acceptance.json",
]
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
COLLECTION_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

BASE_PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json",
]
PRIMARY_MAPS = [*BASE_PRIMARY_MAPS, FRESH_MAP]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json",
]
BASE_MAP_HASHES = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9",
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77",
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33",
}
SUPPLEMENT_MAP_HASHES = {
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json": "a21faaf398e4b605a441da7ca9f23d23e75e1e1bfb59a824d59e5aa7a981d772",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
}
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {rel(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object")
    return payload

def map_items(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path, f"map {rel(path)}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"map {rel(path)} has no items list")
    return [item for item in items if isinstance(item, dict)]

def fresh_count() -> int:
    return len(map_items(FRESH_MAP))

def validate_fresh_map() -> dict[str, Any]:
    payload = read_json(FRESH_MAP, "v24 fresh map")
    if payload.get("accepted") is not True or payload.get("role") != "primary_image_overlay":
        raise RuntimeError("v24 fresh map is not an accepted primary map")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) == 0:
        raise RuntimeError("v24 fresh map has no items")
    accepted_by_original: dict[str, dict[str, Any]] = {}
    accepted_receipt_bindings: list[dict[str, Any]] = []
    for receipt_path in FRESH_RECEIPTS:
        receipt = read_json(receipt_path, f"{receipt_path.stem} root acceptance")
        if receipt.get("accepted") is not True:
            raise RuntimeError(f"{rel(receipt_path)} is not accepted")
        accepted = receipt.get("accepted_images")
        if not isinstance(accepted, list):
            raise RuntimeError(f"{rel(receipt_path)} has no accepted_images list")
        accepted_receipt_bindings.append({"path": rel(receipt_path), "sha256": sha256(receipt_path), "accepted_count": len(accepted)})
        for accepted_item in accepted:
            original = str(accepted_item.get("original") or accepted_item.get("logical_url") or "")
            if not original or original in accepted_by_original:
                raise RuntimeError(f"duplicate accepted fresh original: {original}")
            accepted_by_original[original] = accepted_item
    source_acceptances = payload.get("source_acceptances")
    if not isinstance(source_acceptances, list) or len(source_acceptances) != len(accepted_receipt_bindings):
        raise RuntimeError("v24 fresh map source_acceptances must bind every accepted news receipt")
    for expected, actual in zip(accepted_receipt_bindings, source_acceptances):
        if actual.get("path") != expected["path"] or actual.get("sha256") != expected["sha256"] or actual.get("accepted_count") != expected["accepted_count"]:
            raise RuntimeError("v24 fresh map source acceptance binding changed")
    if len(items) != len(accepted_by_original):
        raise RuntimeError("v24 fresh map count does not match accepted CONTENT02/03 count")
    for item in items:
        original = str(item.get("original") or item.get("logical_url") or "")
        accepted_item = accepted_by_original.get(original)
        if accepted_item is None:
            raise RuntimeError(f"v24 fresh map item is not in accepted CONTENT02/03 receipts: {original}")
        if str(item.get("sha256") or "").casefold() != str(accepted_item.get("sha256") or "").casefold() or int(item.get("length", -1)) != int(accepted_item.get("length", -2)):
            raise RuntimeError(f"v24 fresh map byte binding changed: {original}")
    base_originals = {
        str(item.get("original") or item.get("logical_url") or "")
        for path in BASE_PRIMARY_MAPS
        for item in map_items(path)
    }
    fresh_originals = [str(item.get("original") or item.get("logical_url") or "") for item in items]
    if len(set(fresh_originals)) != len(fresh_originals) or set(fresh_originals) & base_originals:
        raise RuntimeError("v24 fresh map overlaps or duplicates an existing primary original")
    return {
        "item_count": len(items),
        "map_sha256": sha256(FRESH_MAP),
        "source_acceptance_sha256s": {binding["path"]: binding["sha256"] for binding in accepted_receipt_bindings},
        "originals": fresh_originals,
    }

def validate_gates() -> dict[str, Any]:
    for path in [SOURCE_MANIFEST, V23_PROVENANCE, V23_ACCEPTANCE, V23_PREP, V23_WORKER, *BASE_PRIMARY_MAPS, *SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP, COLLECTION_MAP]:
        if not path.is_file():
            raise RuntimeError(f"frozen v23 input missing: {rel(path)}")
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if manifest.get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 anchor changed")
    acceptance = read_json(V23_ACCEPTANCE, "root v23 acceptance")
    stats = acceptance.get("stats") or {}
    expected = {
        "accepted": True,
        "checked_declared_files": 8620,
        "actual_files": 8621,
        "source_records": 8357,
        "image_overlay_records": 162,
        "primary_image_overlay_records": 100,
        "supplement_image_overlay_records": 62,
        "guide_preview_count": 22,
        "guide_preview_gallery_pages": 6,
        "guide_image_collection_images": 32,
        "guide_image_collection_pages": 6,
    }
    if acceptance.get("accepted") is not True or acceptance.get("checked_declared_files") != expected["checked_declared_files"] or acceptance.get("actual_files") != expected["actual_files"]:
        raise RuntimeError("v23 acceptance status/file counts changed")
    for key in ("source_records", "image_overlay_records", "primary_image_overlay_records", "supplement_image_overlay_records", "guide_preview_count", "guide_preview_gallery_pages", "guide_image_collection_images", "guide_image_collection_pages"):
        if stats.get(key) != expected[key]:
            raise RuntimeError(f"v23 acceptance stat changed: {key}={stats.get(key)!r}")
    provenance = read_json(V23_PROVENANCE, "v23 provenance")
    if provenance.get("source_manifest_sha256") != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002":
        raise RuntimeError("v23 provenance does not bind source15")
    for receipt_path in FRESH_RECEIPTS:
        if not receipt_path.is_file():
            raise RuntimeError(f"{rel(receipt_path)} is absent; final CONTENT02+03 acceptance is required")
        receipt = read_json(receipt_path, f"{receipt_path.stem} root acceptance")
        if receipt.get("accepted") is not True:
            raise RuntimeError(f"{rel(receipt_path)} is not accepted")
    if not FRESH_MAP.is_file():
        raise RuntimeError("v24 fresh map is absent; run prepare_v24_inputs.py after root acceptance")
    fresh_binding = validate_fresh_map()
    return {
        "v23_acceptance_sha256": sha256(V23_ACCEPTANCE),
        "v23_provenance_sha256": sha256(V23_PROVENANCE),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "v23_stats": stats,
        "fresh_receipt_sha256s": {rel(path): sha256(path) for path in FRESH_RECEIPTS},
        "fresh_map_sha256": fresh_binding["map_sha256"],
        "fresh_count": fresh_count(),
        "fresh_map_binding": fresh_binding,
    }

def locked_hashes() -> dict[str, str]:
    paths = dict(BASE_MAP_HASHES)
    paths.update(SUPPLEMENT_MAP_HASHES)
    paths.update({
        rel(SOURCE_MANIFEST): "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002",
        rel(V23_PROVENANCE): "4af91c0131e3b4760946b3b4db5e1e4a5ba0fc8be026226164c3f44aa56a743e",
        rel(V23_ACCEPTANCE): "e987b8dbb0f868df22b73152dab98f7c10cbe77ff9fbd35c48ee670e4239fb1a",
        rel(V23_PREP): "6f9072e9dc3717740c52290165e8d7d9f97ff5494eca7481e46a8f63f31139dd",
        rel(V23_WORKER): "1d9563282178d596d06a9886bfc8486b3cb6da495927757cf0bbb9950cd0919e",
        rel(GUIDE_PREVIEW_MAP): "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581",
        rel(COLLECTION_MAP): "de179aa26f0453cd29b30b76600bf22dd9e0a3b443e03300238c13c97bb624c6",
        "tools/export_github_pages.py": "50bd3569f77d3d52c52ed7077726d7dc99fbee23a3a0ced076a6523198b9225d",
        "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
        "tools/guide_image_collections.py": "9d0f20679733e29c6eb789fd4a05883056e4994ccb173e1dc843d68e070dc057",
    })
    paths[rel(FRESH_MAP)] = sha256(FRESH_MAP)
    for receipt_path in FRESH_RECEIPTS:
        paths[rel(receipt_path)] = sha256(receipt_path)
    for path, expected in paths.items():
        actual = sha256(ROOT / path)
        if actual != expected:
            raise RuntimeError(f"locked input changed: {path} expected {expected} got {actual}")
    return paths
def preflight_loader() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    import guide_image_collections
    import guide_previews

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
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
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes,
        frozen_static_paths=relative_paths,
    )
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_static = relative_paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(SUPPLEMENT_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_static,
        allow_later_image_supplements=True,
    )
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    preview = guide_previews.load_guide_preview_map(
        GUIDE_PREVIEW_MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    collections = guide_image_collections.load_guide_image_collection_map(
        COLLECTION_MAP,
        workspace_root=ROOT,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        overlays=[*primary, *supplement],
        route_to_static=route_to_static,
        base_path=BASE_PATH,
    )
    expected_primary = 100 + fresh_count()
    if len(primary) != expected_primary or len(supplement) != 62 or len(primary) + len(supplement) != 162 + fresh_count():
        raise RuntimeError(f"v24 loader count changed: {len(primary)}/{len(supplement)}/{fresh_count()}")
    if preview.preview_count != 22 or len(preview.groups) != 6:
        raise RuntimeError("v23 guide preview counts changed")
    if collections.image_count != 32 or len(collections.groups) != 3:
        raise RuntimeError("v23 guide collection counts changed")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "fresh_primary_records": fresh_count(),
        "guide_preview_groups": len(preview.groups),
        "guide_preview_images": preview.preview_count,
        "guide_collection_groups": len(collections.groups),
        "guide_collection_images": collections.image_count,
        "network_requests": 0,
        "export_executed": False,
    }
def verify_postbuild(result: dict[str, Any]) -> dict[str, Any]:
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v24 output or partial output state is invalid")
    provenance = read_json(OUTPUT / "export-provenance.json", "v24 export provenance")
    stats = provenance.get("stats") or {}
    n = fresh_count()
    expected = {
        "source_records": 8357,
        "image_overlay": 162 + n,
        "image_overlay_records": 162 + n,
        "primary_image_overlay_records": 100 + n,
        "supplement_image_overlay_records": 62,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
        "guide_image_collection_pages": 6,
        "guide_image_collection_images": 32,
        "output_files": 8620 + n,
    }
    for key, value in expected.items():
        if stats.get(key) != value:
            raise RuntimeError(f"v24 provenance stat {key}={stats.get(key)!r}, expected {value}")
    actual_files = sum(1 for item in OUTPUT.rglob("*") if item.is_file())
    if result.get("output_files") != 8620 + n or actual_files != 8621 + n:
        raise RuntimeError(f"v24 file counts changed: result={result.get('output_files')} actual={actual_files}")
    if provenance.get("source_manifest_sha256") != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002":
        raise RuntimeError("v24 provenance does not bind source15")
    return {
        "declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "stats": stats,
        "fresh_count": n,
    }

def write_preflight(gates: dict[str, Any], preflight: dict[str, Any]) -> None:
    if PREFLIGHT_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite existing v24 preflight receipt: {PREFLIGHT_RECEIPT}")
    payload = {
        "schema": "wow-recovery.integration.v24.preflight.v1",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": now(),
        "network_requests": 0,
        "export_executed": False,
        "gates": gates,
        "loader_preflight": preflight,
        "fresh_map": {"path": rel(FRESH_MAP), "sha256": sha256(FRESH_MAP), "item_count": fresh_count()},
        "expected_counts": {
            "declared_files": 8620 + fresh_count(),
            "actual_files": 8621 + fresh_count(),
            "primary_overlays": 100 + fresh_count(),
            "supplement_overlays": 62,
            "total_overlays": 162 + fresh_count(),
            "guide_preview_groups": 6,
            "guide_preview_images": 22,
            "guide_collection_groups": 3,
            "guide_collection_images": 32,
        },
    }
    PREFLIGHT_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true", help="perform the one authorized export")
    args = parser.parse_args()
    started = now()
    gates = validate_gates()
    if not args.go:
        preflight = preflight_loader()
        write_preflight(gates, preflight)
        print(json.dumps({"status": "preflight_only", "receipt": rel(PREFLIGHT_RECEIPT), "fresh_count": fresh_count(), "network_requests": 0, "export_executed": False}, ensure_ascii=False, sort_keys=True))
        return 0
    if RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite existing v24 worker receipt: {RECEIPT}")
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError(f"refusing to overwrite existing v24 output or partial: {OUTPUT}")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")
    locks_before = locked_hashes()
    preflight = preflight_loader()
    export_started = True
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages
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
            raise RuntimeError("locked source/map/production input changed during export")
        free_after = shutil.disk_usage(ROOT).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor after export: {free_after} < {MIN_FREE_BYTES}")
        receipt = {
            "schema": "wow-recovery.integration.v24.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": "\"C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe\" -X utf8 research/continuous-recovery-20261016/integration/v24-build/build_pages_v24.py --go",
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": True,
            "export_completed": True,
            "network_requests_by_builder": 0,
            "published": False,
            "source15_manifest": rel(SOURCE_MANIFEST),
            "source15_manifest_sha256": locks_after[rel(SOURCE_MANIFEST)],
            "v23_provenance": rel(V23_PROVENANCE),
            "v23_provenance_sha256": locks_after[rel(V23_PROVENANCE)],
            "v23_acceptance": rel(V23_ACCEPTANCE),
            "v23_acceptance_sha256": locks_after[rel(V23_ACCEPTANCE)],
            "fresh_source_acceptances": [
                {"path": rel(path), "sha256": locks_after[rel(path)]}
                for path in FRESH_RECEIPTS
            ],
            "fresh_map": rel(FRESH_MAP),
            "fresh_map_sha256": locks_after[rel(FRESH_MAP)],
            "primary_source_maps": [rel(path) for path in PRIMARY_MAPS],
            "supplement_source_maps": [rel(path) for path in SUPPLEMENT_MAPS],
            "guide_preview_map": rel(GUIDE_PREVIEW_MAP),
            "guide_image_collection_map": rel(COLLECTION_MAP),
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
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        free_after = shutil.disk_usage(ROOT).free
        failure = {
            "schema": "wow-recovery.integration.v24.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": "\"C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe\" -X utf8 research/continuous-recovery-20261016/integration/v24-build/build_pages_v24.py --go",
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
        RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        raise

if __name__ == "__main__":
    raise SystemExit(main())
