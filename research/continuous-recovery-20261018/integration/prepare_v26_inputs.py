#!/usr/bin/env python3
"""Prepare and preflight the v26 neighbor input maps without exporting pages.

This preparation is intentionally narrow: it binds the five root-accepted
neighbor payloads to a new supplement map, clones the accepted v25 collection
map, and appends only the four exact numeric full images to their established
collections.  The Lunar Festival ``sswdress3.jpg`` payload remains a
model-view supplement and is excluded from the numeric guide collections.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = Path(__file__).resolve().parent
ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-neighbors5-source-acceptance.json"
BASE_SUPPLEMENT = ROOT / "research/focused-recovery-20261016-2301/local/v25-neighbor-supplement-source-map.json"
BASE_COLLECTION = ROOT / "research/focused-recovery-20261016-2301/local/v25-guide-image-collection-map.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
V25_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v25/export-provenance.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
NEW_SUPPLEMENT = INTEGRATION / "v26-neighbor-supplement-source-map.json"
NEW_COLLECTION = INTEGRATION / "v26-guide-image-collection-map.json"
PREPARATION = INTEGRATION / "v26-input-preparation.json"
PREFLIGHT = INTEGRATION / "v26-input-preflight.json"
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
    ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json",
]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json",
    ROOT / "research/focused-recovery-20261016-2301/local/v25-neighbor-supplement-source-map.json",
    NEW_SUPPLEMENT,
]

NEW_RULES = {
    "http://www.worldofwarcraft.com:80/info/events/lunarnewyears/images/ss5.jpg": {
        "catalog_role": "guide_image_collection_numeric_full",
        "collection_group": "lunar-festival",
    },
    "http://www.worldofwarcraft.com:80/info/events/lunarnewyears/images/sswdress3.jpg": {
        "catalog_role": "model_view",
        "collection_group": None,
    },
    "https://www.worldofwarcraft.com/pvp/worldpvp/images/ss11.jpg": {
        "catalog_role": "guide_image_collection_numeric_full",
        "collection_group": "world-pvp",
    },
    "https://www.worldofwarcraft.com/pvp/worldpvp/images/ss13.jpg": {
        "catalog_role": "guide_image_collection_numeric_full",
        "collection_group": "world-pvp",
    },
    "https://www.worldofwarcraft.com/pvp/worldpvp/images/ss3.jpg": {
        "catalog_role": "guide_image_collection_numeric_full",
        "collection_group": "world-pvp",
    },
}


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes workspace: {path}") from exc
    return resolved


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def temporal_class(timestamp: str) -> str:
    actual = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    anchor = datetime.strptime(ANCHOR, "%Y%m%d%H%M%S")
    if actual < datetime(2008, 1, 1):
        return "pre_2008"
    if actual <= anchor:
        return "baseline_2008"
    if actual <= datetime(2008, 12, 31, 23, 59, 59):
        return "late_2008"
    return "post_2008"


def validate_acceptance() -> tuple[dict, dict[str, dict]]:
    receipt = read_json(ACCEPTANCE, "root neighbors5 source acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root neighbors5 acceptance is not accepted")
    accepted = receipt.get("accepted_images")
    if not isinstance(accepted, list) or len(accepted) != len(NEW_RULES):
        raise RuntimeError(f"expected {len(NEW_RULES)} accepted images, got {len(accepted or [])}")
    by_original: dict[str, dict] = {}
    for index, raw in enumerate(accepted):
        if not isinstance(raw, dict) or raw.get("accepted") is not True:
            raise RuntimeError(f"accepted_images[{index}] is not accepted")
        original = str(raw.get("original") or "")
        if original in by_original or original not in NEW_RULES:
            raise RuntimeError(f"unexpected or duplicate accepted original: {original}")
        actual = str(raw.get("actual_capture_timestamp") or "")
        if not re.fullmatch(r"\d{14}", actual):
            raise RuntimeError(f"invalid capture timestamp for {original}: {actual!r}")
        datetime.strptime(actual, "%Y%m%d%H%M%S")
        source_raw = raw.get("private_payload_path")
        if not source_raw:
            raise RuntimeError(f"accepted payload path is missing: {original}")
        source = inside(ROOT / str(source_raw), f"accepted payload {original}")
        if not source.is_file():
            raise RuntimeError(f"accepted payload is missing: {source}")
        data = source.read_bytes()
        expected_sha = str(raw.get("sha256") or "").casefold()
        expected_length = int(raw.get("length", -1))
        if sha256_file(source) != expected_sha or len(data) != expected_length:
            raise RuntimeError(f"accepted payload bytes differ from receipt: {original}")
        if cdx_digest(data) != str(raw.get("cdx_digest") or "").upper():
            raise RuntimeError(f"accepted payload CDX digest differs from receipt: {original}")
        by_original[original] = {**raw, "_source": source, "_actual": actual}
    if set(by_original) != set(NEW_RULES):
        raise RuntimeError(f"accepted original set differs: {sorted(by_original)}")
    return receipt, by_original


def make_maps(receipt: dict, accepted: dict[str, dict]) -> tuple[dict, dict, list[dict]]:
    binding = {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)}
    items: list[dict] = []
    collection_items: list[dict] = []
    for original, rule in NEW_RULES.items():
        raw = accepted[original]
        actual = raw["_actual"]
        route = urlsplit(original).path
        item = {
            "kind": "image",
            "logical_url": original,
            "original": original,
            "actual_timestamp": actual,
            "indexed_capture_timestamp": actual,
            "mime": str(raw.get("mime") or ""),
            "dimensions": raw.get("dimensions"),
            "decoded_frames": raw.get("decoded_frames"),
            "length": int(raw["length"]),
            "sha256": str(raw["sha256"]).casefold(),
            "cdx_digest": str(raw["cdx_digest"]).upper(),
            "local_path": rel(raw["_source"]),
            "temporal_class": temporal_class(actual),
            "catalog_role": rule["catalog_role"],
            "collection_group": rule["collection_group"],
            "source_acceptance_path": rel(ACCEPTANCE),
            "source_relationship": "Root-accepted neighbors5 retry payload; explicit v26 supplement overlay; no deployment implied.",
        }
        items.append(item)
        if rule["collection_group"]:
            collection_items.append(
                {
                    "actual_capture_timestamp": actual,
                    "length": int(raw["length"]),
                    "original": original,
                    "route": route,
                    "sha256": str(raw["sha256"]).casefold(),
                    "source_acceptance_path": rel(ACCEPTANCE),
                }
            )
    supplement = {
        "accepted": True,
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Each local_path points to a root-accepted payload; the exporter verifies SHA-256, length, MIME, timestamp, and CDX digest.",
        "items": items,
        "kind": "wow_gallery_neighbors_v26_supplement",
        "purpose": "Only the five newly accepted v26 neighbor retry images; no v25 item is duplicated.",
        "role": "related_site_image_supplement",
        "schema_version": 1,
        "source_acceptance": binding,
    }
    base_collection = read_json(BASE_COLLECTION, "v25 collection map")
    if base_collection.get("schema") != "wow-recovery.guide-image-collections.v1":
        raise RuntimeError("v25 collection map schema changed")
    collection = copy.deepcopy(base_collection)
    collection["purpose"] = "v26 clone of the accepted v25 guide-image collections with four root-accepted numeric full neighbors appended; sswdress3 remains model_view only."
    acceptances = collection.setdefault("source_acceptances", [])
    if binding not in acceptances:
        acceptances.append(binding)
    for added in collection_items:
        group_id = NEW_RULES[added["original"]]["collection_group"]
        group = next((group for group in collection.get("groups", []) if group.get("group_id") == group_id), None)
        if group is None:
            raise RuntimeError(f"collection group missing for {group_id}")
        if any(item.get("route") == added["route"] for item in group.get("images", [])):
            raise RuntimeError(f"collection route already exists: {added['route']}")
        group.setdefault("images", []).append(added)
    return supplement, collection, collection_items


def loader_preflight() -> dict:
    if sha256_file(V25_PROVENANCE) != "e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e":
        raise RuntimeError("v25 provenance SHA changed")
    if sha256_file(SOURCE_MANIFEST) != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002" or read_json(SOURCE_MANIFEST, "source15 manifest").get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 manifest SHA or anchor changed")
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    import guide_image_collections
    import guide_previews

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
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
    collections = guide_image_collections.load_guide_image_collection_map(NEW_COLLECTION, workspace_root=ROOT, manifest_path=SOURCE_MANIFEST, manifest=manifest, overlays=[*primary, *supplement], route_to_static=route_to_static, base_path=BASE_PATH)
    if len(primary) != 117 or len(supplement) != 71 or len(primary) + len(supplement) != 188:
        raise RuntimeError(f"unexpected v26 overlay counts: {len(primary)}/{len(supplement)}")
    if preview.preview_count != 22 or len(preview.groups) != 6:
        raise RuntimeError(f"guide preview counts changed: {len(preview.groups)}/{preview.preview_count}")
    if collections.image_count != 39 or len(collections.groups) != 3:
        raise RuntimeError(f"guide collection counts changed: {len(collections.groups)}/{collections.image_count}")
    routes = {image.route for group in collections.groups for image in group.images}
    expected_collection_routes = {
        "/info/events/lunarnewyears/images/ss5.jpg",
        "/pvp/worldpvp/images/ss11.jpg",
        "/pvp/worldpvp/images/ss13.jpg",
        "/pvp/worldpvp/images/ss3.jpg",
    }
    if not expected_collection_routes <= routes or "/info/events/lunarnewyears/images/sswdress3.jpg" in routes:
        raise RuntimeError("v26 collection/model_view separation failed")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "new_overlay_records": 5,
        "guide_preview_groups": len(preview.groups),
        "guide_preview_images": preview.preview_count,
        "guide_collection_groups": len(collections.groups),
        "guide_collection_images": collections.image_count,
        "collection_numeric_full_added": 4,
        "model_view_added": 1,
        "network_requests": 0,
        "export_executed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true", help="write the v26 supplement and collection maps")
    parser.add_argument("--preflight", action="store_true", help="run offline loaders and write the preflight receipt")
    args = parser.parse_args(argv)
    if not args.go and not args.preflight:
        print(json.dumps({"status": "prepared_only", "writes": False, "network_requests": 0}, ensure_ascii=False))
        return 0
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v26 preparation: {free_before}")
    receipt, accepted = validate_acceptance()
    if args.go:
        for path in (NEW_SUPPLEMENT, NEW_COLLECTION, PREPARATION):
            if path.exists():
                raise RuntimeError(f"refusing to overwrite existing v26 preparation output: {path}")
        supplement, collection, collection_items = make_maps(receipt, accepted)
        NEW_SUPPLEMENT.write_text(json.dumps(supplement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        NEW_COLLECTION.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        prep = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-input-preparation.v1",
            "status": "prepared_waiting_export_go",
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "source_acceptance": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
            "accepted_count": len(accepted),
            "accepted_bytes": sum(int(item["length"]) for item in accepted.values()),
            "numeric_full_collection_added": len(collection_items),
            "model_view_added": 1,
            "supplement_map": {"path": rel(NEW_SUPPLEMENT), "sha256": sha256_file(NEW_SUPPLEMENT), "item_count": len(supplement["items"])},
            "collection_map": {"path": rel(NEW_COLLECTION), "sha256": sha256_file(NEW_COLLECTION), "group_count": len(collection["groups"]), "image_count": sum(len(group.get("images", [])) for group in collection["groups"])},
            "network_requests": 0,
            "export_executed": False,
            "disk_free_before_bytes": free_before,
        }
        PREPARATION.write_text(json.dumps(prep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.preflight:
        if not NEW_SUPPLEMENT.is_file() or not NEW_COLLECTION.is_file():
            raise RuntimeError("run with --go before v26 preflight")
        if PREFLIGHT.exists():
            raise RuntimeError(f"refusing to overwrite existing v26 preflight receipt: {PREFLIGHT}")
        loader = loader_preflight()
        payload = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-preflight.v1",
            "status": "preflight_passed_waiting_export_go",
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "source_acceptance": {"path": rel(ACCEPTANCE), "sha256": sha256_file(ACCEPTANCE)},
            "base_v25_provenance_sha256": sha256_file(V25_PROVENANCE),
            "source15_manifest_sha256": sha256_file(SOURCE_MANIFEST),
            "loader_preflight": loader,
            "expected_after_export": {"declared_files": 8646, "actual_files": 8647, "primary_overlays": 117, "supplement_overlays": 71, "total_overlays": 188, "guide_previews": 22, "guide_collection_images": 39},
            "network_requests": 0,
            "export_executed": False,
            "published": False,
            "root_export_go_required": True,
            "disk_free_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        PREFLIGHT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "preflight_only" if args.preflight else "prepared", "supplement_map": rel(NEW_SUPPLEMENT), "collection_map": rel(NEW_COLLECTION), "preflight": rel(PREFLIGHT) if args.preflight else None, "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
