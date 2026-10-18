#!/usr/bin/env python3
"""Bind root-accepted news9 images and run the combined v26 loader preflight.

The five guide-neighbor inputs are prepared by ``prepare_v26_inputs.py``.
This small companion only adds the eight root-accepted NEWS-CONTENT01/03
primary images and verifies the combined exporter inputs.  It never exports
the site and never treats the complete zero-row 04-02-08-1 query as a source
map item.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from prepare_v26_inputs import (
    ANCHOR,
    BASE_PATH,
    GUIDE_PREVIEW_MAP,
    MIN_FREE_BYTES,
    NEW_COLLECTION,
    PRIMARY_MAPS,
    ROOT,
    SOURCE_MANIFEST,
    SOURCE_SITE,
    SUPPLEMENT_MAPS,
    V25_PROVENANCE,
    cdx_digest,
    inside,
    read_json,
    rel,
    sha256_file,
    temporal_class,
)


NEWS_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-news9-source-acceptance.json"
NEWS_BATCH_REPORT = ROOT / "research/continuous-recovery-20261018/network/news-transport-unknowns-v25-v3/output/batch-report.json"
NEWS_PLAN = ROOT / "research/continuous-recovery-20261018/network/news-transport-unknowns-v25-v3/plan.json"
NEWS_SOURCE_MAP = ROOT / "research/continuous-recovery-20261018/network/news-transport-unknowns-v25-v3/output/source-map.json"
NEWS_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-news-primary-source-map.json"
NEWS_PREPARATION = ROOT / "research/continuous-recovery-20261018/integration/v26-news-input-preparation.json"
COMBINED_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v26-combined-preflight.json"


def validate_news() -> tuple[dict, list[dict], list[dict]]:
    acceptance = read_json(NEWS_ACCEPTANCE, "root news9 source acceptance")
    if acceptance.get("accepted") is not True:
        raise RuntimeError("root news9 source acceptance is not accepted")
    accepted = acceptance.get("accepted_images")
    if not isinstance(accepted, list) or len(accepted) != 8:
        raise RuntimeError(f"expected eight accepted news9 images, got {len(accepted or [])}")
    plan = read_json(NEWS_PLAN, "news9 plan")
    plan_by_original = {str(item.get("original") or ""): item for item in plan.get("candidates", []) if isinstance(item, dict)}
    accepted_items: list[dict] = []
    seen: set[str] = set()
    for index, raw in enumerate(accepted):
        if not isinstance(raw, dict) or raw.get("accepted") is not True:
            raise RuntimeError(f"accepted_images[{index}] is not accepted")
        original = str(raw.get("original") or "")
        if original in seen or original not in plan_by_original:
            raise RuntimeError(f"unexpected or duplicate news9 original: {original}")
        seen.add(original)
        timestamp = str(raw.get("actual_capture_timestamp") or "")
        if len(timestamp) != 14 or timestamp != str(raw.get("indexed_capture_timestamp") or timestamp):
            raise RuntimeError(f"invalid news9 capture timestamp: {original}")
        source_raw = raw.get("private_payload_path")
        if not source_raw:
            raise RuntimeError(f"news9 private payload path missing: {original}")
        source = inside(ROOT / str(source_raw), f"news9 payload {original}")
        if not source.is_file():
            raise RuntimeError(f"news9 payload missing: {source}")
        data = source.read_bytes()
        expected_sha = str(raw.get("sha256") or "").casefold()
        expected_length = int(raw.get("length", -1))
        if sha256_file(source) != expected_sha or len(data) != expected_length:
            raise RuntimeError(f"news9 payload SHA/length mismatch: {original}")
        if cdx_digest(data) != str(raw.get("cdx_digest") or "").upper():
            raise RuntimeError(f"news9 payload CDX digest mismatch: {original}")
        accepted_items.append({**raw, "_source": source, "_timestamp": timestamp, "_target_key": plan_by_original[original].get("target_key")})

    batch = read_json(NEWS_BATCH_REPORT, "news9 batch report")
    empty: list[dict] = []
    for result in batch.get("results", []):
        if not isinstance(result, dict) or result.get("status") != "complete_no_eligible_capture":
            continue
        target_key = str(result.get("target_key") or "")
        candidate = plan_by_original.get(next((str(item.get("original") or "") for item in plan.get("candidates", []) if item.get("target_key") == target_key), ""), {})
        empty.append(
            {
                "target_key": target_key,
                "original": candidate.get("original"),
                "status": result.get("status"),
                "fresh_cdx_transport": result.get("fresh_cdx_transport"),
                "row_count": (result.get("cdx") or {}).get("row_count"),
                "potential_truncation": (result.get("cdx") or {}).get("potential_truncation"),
                "source": rel(NEWS_BATCH_REPORT),
            }
        )
    if len(empty) != 1 or empty[0].get("original") != "http://www.worldofwarcraft.com/news/images/08-04/04-02-08-1.jpg":
        raise RuntimeError(f"unexpected news9 complete-empty set: {empty}")
    return acceptance, accepted_items, empty


def make_news_map(acceptance: dict, accepted_items: list[dict]) -> dict:
    binding = {"path": rel(NEWS_ACCEPTANCE), "sha256": sha256_file(NEWS_ACCEPTANCE)}
    items: list[dict] = []
    for raw in accepted_items:
        original = str(raw["original"])
        item = {
            "kind": "image",
            "logical_url": original,
            "original": original,
            "actual_timestamp": raw["_timestamp"],
            "indexed_capture_timestamp": raw["_timestamp"],
            "mime": str(raw.get("mime") or "image/jpeg"),
            "dimensions": raw.get("dimensions"),
            "decoded_frames": raw.get("decoded_frames"),
            "length": int(raw["length"]),
            "sha256": str(raw["sha256"]).casefold(),
            "cdx_digest": str(raw["cdx_digest"]).upper(),
            "local_path": rel(raw["_source"]),
            "temporal_class": temporal_class(raw["_timestamp"]),
            "target_key": raw.get("_target_key"),
            "source_acceptance_path": rel(NEWS_ACCEPTANCE),
            "source_relationship": "Root-accepted news9 exact CDX/replay payload; explicit v26 primary overlay; copied bytes are referenced without re-encoding.",
        }
        items.append(item)
    return {
        "schema_version": "wow-recovery.integration.v26.news-primary-source-map.v1",
        "kind": "wow_news_v26_news9_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": True,
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the eight root-accepted news9 payloads are included; the complete zero-row exact query remains excluded and no dynamic alias is inferred.",
        "source_acceptance": binding,
        "source_map": {"path": rel(NEWS_SOURCE_MAP), "sha256": sha256_file(NEWS_SOURCE_MAP)},
        "batch_report": {"path": rel(NEWS_BATCH_REPORT), "sha256": sha256_file(NEWS_BATCH_REPORT)},
        "items": items,
    }


def combined_loader_preflight() -> dict:
    if sha256_file(V25_PROVENANCE) != "e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e":
        raise RuntimeError("v25 provenance SHA changed")
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if sha256_file(SOURCE_MANIFEST) != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002" or manifest.get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 manifest SHA or anchor changed")
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    import guide_image_collections
    import guide_previews

    records = {export_github_pages.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", [])}
    paths = {export_github_pages.static_rel_for_route(route, item) for route, item in records.items()}
    route_to_static = {route: export_github_pages.static_url(BASE_PATH, path) for route, path in ((route, export_github_pages.static_rel_for_route(route, item)) for route, item in records.items())}
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(records) | {str(alias) for alias in aliases}
    primary_maps = (*PRIMARY_MAPS, NEWS_MAP)
    primary, primary_bytes = export_github_pages.load_image_overlays(tuple(primary_maps), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=frozen_routes, frozen_static_paths=paths)
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_paths = paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(tuple(SUPPLEMENT_MAPS), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=overlay_routes, frozen_static_paths=overlay_paths, allow_later_image_supplements=True)
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    preview = guide_previews.load_guide_preview_map(GUIDE_PREVIEW_MAP, workspace_root=ROOT, source_site=SOURCE_SITE, manifest_path=SOURCE_MANIFEST, manifest=manifest, route_to_static=route_to_static)
    collections = guide_image_collections.load_guide_image_collection_map(NEW_COLLECTION, workspace_root=ROOT, manifest_path=SOURCE_MANIFEST, manifest=manifest, overlays=[*primary, *supplement], route_to_static=route_to_static, base_path=BASE_PATH)
    if len(primary) != 125 or len(supplement) != 71 or len(primary) + len(supplement) != 196:
        raise RuntimeError(f"unexpected combined v26 overlay counts: {len(primary)}/{len(supplement)}")
    if preview.preview_count != 22 or len(preview.groups) != 6:
        raise RuntimeError(f"guide preview counts changed: {len(preview.groups)}/{preview.preview_count}")
    if collections.image_count != 39 or len(collections.groups) != 3:
        raise RuntimeError(f"guide collection counts changed: {len(collections.groups)}/{collections.image_count}")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "new_primary_news_records": 8,
        "new_supplement_neighbor_records": 5,
        "guide_preview_groups": len(preview.groups),
        "guide_preview_images": preview.preview_count,
        "guide_collection_groups": len(collections.groups),
        "guide_collection_images": collections.image_count,
        "network_requests": 0,
        "export_executed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true", help="write the v26 news primary map and preparation receipt")
    parser.add_argument("--preflight", action="store_true", help="run the combined offline loader preflight")
    args = parser.parse_args(argv)
    if not args.go and not args.preflight:
        print(json.dumps({"status": "prepared_only", "network_requests": 0, "export_executed": False}, ensure_ascii=False))
        return 0
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v26 news preparation: {free_before}")
    acceptance, accepted_items, empty = validate_news()
    if args.go:
        for path in (NEWS_MAP, NEWS_PREPARATION):
            if path.exists():
                raise RuntimeError(f"refusing to overwrite existing v26 news preparation output: {path}")
        news_map = make_news_map(acceptance, accepted_items)
        NEWS_MAP.write_text(json.dumps(news_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        prep = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-news-input-preparation.v1",
            "status": "prepared_waiting_export_go",
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "source_acceptance": {"path": rel(NEWS_ACCEPTANCE), "sha256": sha256_file(NEWS_ACCEPTANCE)},
            "accepted_count": len(accepted_items),
            "accepted_bytes": sum(int(item["length"]) for item in accepted_items),
            "news_map": {"path": rel(NEWS_MAP), "sha256": sha256_file(NEWS_MAP), "item_count": len(news_map["items"])},
            "complete_empty_excluded": empty,
            "network_requests": 0,
            "export_executed": False,
            "disk_free_before_bytes": free_before,
        }
        NEWS_PREPARATION.write_text(json.dumps(prep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.preflight:
        if not NEWS_MAP.is_file() or not NEW_COLLECTION.is_file():
            raise RuntimeError("run --go for news map and prepare v26 guide inputs before combined preflight")
        if COMBINED_PREFLIGHT.exists():
            raise RuntimeError(f"refusing to overwrite existing combined preflight: {COMBINED_PREFLIGHT}")
        loader = combined_loader_preflight()
        payload = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-combined-preflight.v1",
            "status": "preflight_passed_waiting_export_go",
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "news_source_acceptance": {"path": rel(NEWS_ACCEPTANCE), "sha256": sha256_file(NEWS_ACCEPTANCE)},
            "news_map": {"path": rel(NEWS_MAP), "sha256": sha256_file(NEWS_MAP), "item_count": 8},
            "guide_preparation": {"path": rel(ROOT / "research/continuous-recovery-20261018/integration/v26-input-preparation.json"), "sha256": sha256_file(ROOT / "research/continuous-recovery-20261018/integration/v26-input-preparation.json")},
            "guide_preflight": {"path": rel(ROOT / "research/continuous-recovery-20261018/integration/v26-input-preflight.json"), "sha256": sha256_file(ROOT / "research/continuous-recovery-20261018/integration/v26-input-preflight.json")},
            "batch_report": {"path": rel(NEWS_BATCH_REPORT), "sha256": sha256_file(NEWS_BATCH_REPORT)},
            "complete_empty_excluded": empty,
            "loader_preflight": loader,
            "expected_after_export": {"declared_files": 8654, "actual_files": 8655, "primary_overlays": 125, "supplement_overlays": 71, "total_overlays": 196, "guide_previews": 22, "guide_collection_images": 39},
            "network_requests": 0,
            "export_executed": False,
            "published": False,
            "root_export_go_required": True,
            "disk_free_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        COMBINED_PREFLIGHT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "preflight_only" if args.preflight else "prepared", "news_map": rel(NEWS_MAP), "combined_preflight": rel(COMBINED_PREFLIGHT) if args.preflight else None, "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
