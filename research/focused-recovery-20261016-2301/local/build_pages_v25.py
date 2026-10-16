#!/usr/bin/env python3
"""Single-export v25 wrapper, prepared but not executed before root GO."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOCAL = Path(__file__).resolve().parent
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
V24_OUTPUT = ROOT / ".scratch/pages-resources-20261016-v24"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v25"
RECEIPT = LOCAL / "worker-build-v25.json"
PREFLIGHT = LOCAL / "preflight-v25-inputs.json"
ROOT_NEIGHBORS9 = ROOT / "research/continuous-recovery-20261016/publication/root-neighbors9-source-acceptance.json"
NEW_SUPPLEMENT_MAP = LOCAL / "v25-neighbor-supplement-source-map.json"
NEW_COLLECTION_MAP = LOCAL / "v25-guide-image-collection-map.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
V24_FRESH_PRIMARY = ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json"
V24_PROVENANCE = V24_OUTPUT / "export-provenance.json"
V24_LOCAL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v24-local-acceptance.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json",
    V24_FRESH_PRIMARY,
]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json",
    NEW_SUPPLEMENT_MAP,
]
FROZEN_MAP_SHAS = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9",
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77",
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33",
    "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json": "cbd818c907b4746ca2d39777ca35ccf2505e239038377f9a9e51b62a303a33d0",
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json": "a21faaf398e4b605a441da7ca9f23d23e75e1e1bfb59a824d59e5aa7a981d772",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def validate_gates() -> dict:
    if sha(V24_PROVENANCE) != "0d1a392e5be8f5eae71b8ca6bf73f5473331357c6f99f9ac60e79b6d07dec3d0":
        raise RuntimeError("v24 provenance SHA changed")
    if sha(V24_LOCAL_ACCEPTANCE) != "6ede038217c7e3a978dc82c2b6135580660546b9013e30883679cbae11c17282":
        raise RuntimeError("v24 local acceptance SHA changed")
    manifest = read(SOURCE_MANIFEST, "source15 manifest")
    if manifest.get("anchor_timestamp") != ANCHOR or sha(SOURCE_MANIFEST) != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002":
        raise RuntimeError("source15 manifest changed")
    accepted = read(ROOT_NEIGHBORS9, "root neighbors9 acceptance")
    if accepted.get("accepted") is not True or not isinstance(accepted.get("accepted_images"), list):
        raise RuntimeError("root neighbors9 source acceptance is not ready")
    if not NEW_SUPPLEMENT_MAP.is_file() or not NEW_COLLECTION_MAP.is_file():
        raise RuntimeError("run prepare_v25_inputs.py --go after source acceptance")
    for key, expected in FROZEN_MAP_SHAS.items():
        path = ROOT / key
        if sha(path) != expected:
            raise RuntimeError(f"frozen map changed: {key}")
    return {"v24_provenance_sha256": sha(V24_PROVENANCE), "source_manifest_sha256": sha(SOURCE_MANIFEST), "root_neighbors9_sha256": sha(ROOT_NEIGHBORS9), "new_supplement_map_sha256": sha(NEW_SUPPLEMENT_MAP), "new_collection_map_sha256": sha(NEW_COLLECTION_MAP), "accepted_count": len(accepted["accepted_images"])}


def loader_preflight() -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    import guide_image_collections
    import guide_previews

    manifest = read(SOURCE_MANIFEST, "source15 manifest")
    records = {export_github_pages.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", [])}
    paths = {export_github_pages.static_rel_for_route(route, item) for route, item in records.items()}
    route_to_static = {route: export_github_pages.static_url(BASE_PATH, path) for route, path in ((route, export_github_pages.static_rel_for_route(route, item)) for route, item in records.items())}
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(records) | {str(alias) for alias in aliases}
    primary, primary_bytes = export_github_pages.load_image_overlays(tuple(PRIMARY_MAPS), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=frozen_routes, frozen_static_paths=paths)
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_paths = paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(tuple(SUPPLEMENT_MAPS), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=overlay_routes, frozen_static_paths=overlay_paths, allow_later_image_supplements=True)
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    preview = guide_previews.load_guide_preview_map(GUIDE_PREVIEW_MAP, workspace_root=ROOT, source_site=SOURCE_SITE, manifest_path=SOURCE_MANIFEST, manifest=manifest, route_to_static=route_to_static)
    collections = guide_image_collections.load_guide_image_collection_map(NEW_COLLECTION_MAP, workspace_root=ROOT, manifest_path=SOURCE_MANIFEST, manifest=manifest, overlays=[*primary, *supplement], route_to_static=route_to_static, base_path=BASE_PATH)
    if len(primary) != 117 or len(supplement) < 62 or len(primary) + len(supplement) < 179:
        raise RuntimeError(f"unexpected v25 loader counts: {len(primary)}/{len(supplement)}")
    if preview.preview_count != 22 or len(preview.groups) != 6:
        raise RuntimeError("v24 guide preview counts changed")
    return {"primary_overlay_records": len(primary), "primary_overlay_bytes": primary_bytes, "supplement_overlay_records": len(supplement), "supplement_overlay_bytes": supplement_bytes, "total_overlay_records": len(primary) + len(supplement), "new_overlay_records": len(primary) + len(supplement) - 179, "guide_preview_groups": len(preview.groups), "guide_preview_images": preview.preview_count, "guide_collection_groups": len(collections.groups), "guide_collection_images": collections.image_count, "network_requests": 0, "export_executed": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true", help="perform exactly one v25 export after root source acceptance and GO")
    args = parser.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat()
    gates = validate_gates()
    preflight = loader_preflight()
    if not args.go:
        if PREFLIGHT.exists():
            raise RuntimeError(f"refusing to overwrite preflight receipt: {PREFLIGHT}")
        payload = {"schema": "wow-recovery.focused-recovery-20261016-2301.v25-preflight.v1", "executed_by": "/root/local_recovery_20261016", "checked_utc": started, "network_requests": 0, "export_executed": False, "gates": gates, "loader_preflight": preflight, "expected": {"declared_files": 8637 + preflight["new_overlay_records"], "actual_files": 8638 + preflight["new_overlay_records"], "primary_overlays": 117, "supplement_overlays": preflight["supplement_overlay_records"], "total_overlays": preflight["total_overlay_records"], "guide_previews": 22, "guide_collection_images": preflight["guide_collection_images"]}}
        PREFLIGHT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "preflight_only", "receipt": rel(PREFLIGHT), "loader": preflight}, ensure_ascii=False))
        return 0
    if RECEIPT.exists() or OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("refusing existing v25 worker receipt, output, or partial")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before export: {free_before}")
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages
        result = export_github_pages.export_pages(source_site=SOURCE_SITE, manifest_path=SOURCE_MANIFEST, output=OUTPUT, base_path=BASE_PATH, workspace_root=ROOT, max_bytes=None, min_free_bytes=MIN_FREE_BYTES, image_source_maps=tuple(PRIMARY_MAPS), supplement_image_source_maps=tuple(SUPPLEMENT_MAPS), allow_later_image_supplements=True, guide_preview_map=GUIDE_PREVIEW_MAP, guide_image_collection_map=NEW_COLLECTION_MAP)
        post = read(OUTPUT / "export-provenance.json", "v25 provenance")
        stats = post.get("stats") or {}
        new_count = preflight["new_overlay_records"]
        expected = {"source_records": 8357, "image_overlay_records": 179 + new_count, "primary_image_overlay_records": 117, "supplement_image_overlay_records": 62 + new_count, "output_files": 8637 + new_count}
        for key, value in expected.items():
            if stats.get(key) != value:
                raise RuntimeError(f"v25 provenance {key}={stats.get(key)!r}, expected {value}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != 8638 + new_count:
            raise RuntimeError(f"v25 actual file count {actual_files}")
        free_after = shutil.disk_usage(ROOT).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk floor after export: {free_after}")
        receipt = {"schema": "wow-recovery.focused-recovery-20261016-2301.v25-build-receipt.v1", "executed_by": "/root/local_recovery_20261016", "command": "python.exe -X utf8 research/focused-recovery-20261016-2301/local/build_pages_v25.py --go", "checked_utc_start": started, "checked_utc_end": datetime.now(timezone.utc).isoformat(), "export_started": True, "export_completed": True, "published": False, "network_requests_by_builder": 0, "gates": gates, "preflight_loader": preflight, "build": result, "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_sha256": sha(OUTPUT / "export-provenance.json")}, "output": rel(OUTPUT), "disk_free_before_bytes": free_before, "disk_free_after_bytes": free_after, "disk_free_floor_bytes": MIN_FREE_BYTES}
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        failure = {"schema": "wow-recovery.focused-recovery-20261016-2301.v25-build-receipt.v1", "executed_by": "/root/local_recovery_20261016", "command": "python.exe -X utf8 research/focused-recovery-20261016-2301/local/build_pages_v25.py --go", "checked_utc_start": started, "checked_utc_end": datetime.now(timezone.utc).isoformat(), "export_started": True, "export_completed": False, "published": False, "network_requests_by_builder": 0, "error": f"{type(exc).__name__}: {exc}", "output": rel(OUTPUT) if OUTPUT.exists() else None, "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(), "disk_free_before_bytes": free_before, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES}
        RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
