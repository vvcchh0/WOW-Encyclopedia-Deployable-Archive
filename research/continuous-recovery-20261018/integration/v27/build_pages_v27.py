#!/usr/bin/env python3
"""Prepare and preflight the v27 input closure; export is guarded and opt-in.

The v27 closure reuses the frozen v25 map lists, the accepted v26 news,
neighbor, and guide-collection maps, and adds only the root-accepted v27
public copies.  Preparation and preflight hash the new public copies and map
metadata, while the frozen image payloads are protected by their accepted
v26/v25 receipts and map hashes.  The exporter is called only when both
``--go`` and ``--root-export-go`` are supplied after root acceptance.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
V25_LOCAL = ROOT / "research/focused-recovery-20261016-2301/local"
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
V25_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v25/export-provenance.json"
V26_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v26/export-provenance.json"
V26_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v26-export-acceptance.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
V26_NEWS_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-news-primary-source-map.json"
V26_NEIGHBOR_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-neighbor-supplement-source-map.json"
V26_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
NEWS8_RECEIPT = ROOT / "research/continuous-recovery-20261018/publication/root-news8-next-public-copy-acceptance.json"
BATCH1_RECEIPT = ROOT / "research/continuous-recovery-20261018/publication/root-news20-batch1-public-copy-acceptance.json"
BATCH2_RECEIPT = ROOT / "research/continuous-recovery-20261018/publication/root-news20-batch2-public-copy-acceptance.json"
V27_IMAGE_ROOT = INTEGRATION / "accepted-images"
V27_PRIMARY_MAP = INTEGRATION / "v27-primary-source-map.json"
V27_SUPPLEMENT_MAP = INTEGRATION / "v27-blizzard-supplement-source-map.json"
V27_IMPACT = INTEGRATION / "v27-impact-estimate.json"
V27_PREPARATION = INTEGRATION / "v27-input-preparation.json"
V27_PREFLIGHT = INTEGRATION / "v27-preflight.json"
V27_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v27"
V27_RECEIPT = INTEGRATION / "v27-build-receipt.json"
ROOT_V27_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v27-input-acceptance.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_EXPORTER_SHA256 = "943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00"
EXPECTED_V25_PROVENANCE_SHA256 = "e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e"
EXPECTED_V26_PROVENANCE_SHA256 = "f5580948c5df72a744577e15bf9165ee7ec477c5adf4b458e5db0241acd9c332"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_V26_NEWS_MAP_SHA256 = "eb3a02a20ca749f32582099597b07530ed54737f11c5f034ffee176ffa469c8d"
EXPECTED_V26_NEIGHBOR_MAP_SHA256 = "ceb990178355de5c60bab0db2f9323186a57ed8c16a7432d4a6caec0b118e356"
EXPECTED_V26_COLLECTION_MAP_SHA256 = "fc150d82800d74cfb412b37a627996827e6cf352ee3cecb3f1a2bee7f1e5ab74"
EXPECTED_V26_EXPORT_ACCEPTANCE_SHA256 = "4addc91ba8166da663f44220a46dcafd7c974be0cdd53267bb18c9cb05692373"
EXPECTED_NEWS8_RECEIPT_SHA256 = "d0ff0ceed01649f869f886ee178cd260e56553db0a88a3cb2452b42b29b86583"
EXPECTED_BATCH1_RECEIPT_SHA256 = "43c78a0095fc671fb99d15775ecb3b6b9aea64a8e53156728ea050b3be3ccc0d"
EXPECTED_BATCH2_RECEIPT_SHA256 = "e26605ed0debbf86acb87d54522c3c7d65221a39646ddfc919e35959122ef9df"

sys.path.insert(0, str(V25_LOCAL))
import build_pages_v25 as frozen_v25  # noqa: E402


PRIMARY_MAPS = tuple(frozen_v25.PRIMARY_MAPS) + (V26_NEWS_MAP, V27_PRIMARY_MAP)
SUPPLEMENT_MAPS = tuple(frozen_v25.SUPPLEMENT_MAPS) + (V26_NEIGHBOR_MAP, V27_SUPPLEMENT_MAP)


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


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


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


def host(url: str) -> str:
    parsed = urlsplit(url)
    return (parsed.hostname or "").casefold().rstrip(".")


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme.casefold()}://{host(url)}{parsed.path}"


def receipt_binding(receipt_path: Path, receipt: dict) -> dict:
    source = receipt.get("source_receipt") or receipt.get("source_acceptance")
    if isinstance(source, str):
        source_path = ROOT / source
        return {"path": rel(source_path), "sha256": sha256_file(source_path)}
    if isinstance(source, dict) and source.get("path"):
        source_path = ROOT / str(source["path"])
        return {"path": rel(source_path), "sha256": sha256_file(source_path)}
    raise RuntimeError(f"{receipt_path.name} has no source receipt binding")


def validate_public_receipt(receipt_path: Path, expected_count: int, dest_dir: str) -> tuple[dict, list[dict], dict]:
    receipt = read_json(receipt_path, receipt_path.name)
    if receipt.get("accepted") is not True:
        raise RuntimeError(f"{receipt_path.name} is not accepted")
    raw_items = receipt.get("accepted_images")
    if not isinstance(raw_items, list) or len(raw_items) != expected_count:
        raise RuntimeError(f"{receipt_path.name} expected {expected_count} accepted images, got {len(raw_items or [])}")
    binding = receipt_binding(receipt_path, receipt)
    rows: list[dict] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict) or raw.get("accepted") is not True or raw.get("deployed") is not False:
            raise RuntimeError(f"{receipt_path.name}.accepted_images[{index}] is not accepted and undeployed")
        original = str(raw.get("original") or "")
        if not original or original in seen:
            raise RuntimeError(f"duplicate or missing original in {receipt_path.name}: {original!r}")
        seen.add(original)
        actual = str(raw.get("actual_capture_timestamp") or "")
        if not re.fullmatch(r"\d{14}", actual):
            raise RuntimeError(f"invalid capture timestamp for {original}: {actual!r}")
        datetime.strptime(actual, "%Y%m%d%H%M%S")
        source_rel = str(raw.get("local_path") or "")
        if not source_rel.startswith("research/continuous-recovery-20261018/publication/accepted-images/"):
            raise RuntimeError(f"non-public source path in {original}: {source_rel}")
        source = inside(ROOT / source_rel, f"public source {original}")
        if not source.is_file():
            raise RuntimeError(f"public source missing for {original}: {source}")
        data = source.read_bytes()
        expected_sha = str(raw.get("sha256") or "").casefold()
        expected_length = int(raw.get("length", -1))
        if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
            raise RuntimeError(f"public source bytes differ from {receipt_path.name}: {original}")
        if cdx_digest(data) != str(raw.get("cdx_digest") or "").upper():
            raise RuntimeError(f"public source CDX differs from receipt: {original}")
        destination = inside(V27_IMAGE_ROOT / dest_dir / source.name, f"v27 copy {original}")
        if not destination.is_file():
            raise RuntimeError(f"v27 public copy missing for {original}: {destination}")
        if destination.stat().st_size != expected_length or sha256_file(destination) != expected_sha:
            raise RuntimeError(f"v27 public copy bytes differ from receipt: {original}")
        row = dict(raw)
        row["_destination"] = destination
        row["_receipt_path"] = receipt_path
        row["_source_binding"] = binding
        rows.append(row)
    return receipt, rows, binding


def make_item(raw: dict, *, role: str, relationship: str) -> dict:
    original = str(raw["original"])
    actual = str(raw["actual_capture_timestamp"])
    return {
        "kind": "image",
        "logical_url": original,
        "original": original,
        "actual_timestamp": actual,
        "indexed_capture_timestamp": actual,
        "mime": str(raw["mime"]),
        "dimensions": raw.get("dimensions"),
        "decoded_frames": raw.get("decoded_frames"),
        "length": int(raw["length"]),
        "sha256": str(raw["sha256"]).casefold(),
        "cdx_digest": str(raw["cdx_digest"]).upper(),
        "local_path": rel(raw["_destination"]),
        "temporal_class": temporal_class(actual),
        "source_acceptance_path": raw["_source_binding"]["path"],
        "public_copy_acceptance_path": rel(raw["_receipt_path"]),
        "public_copy_path": str(raw["local_path"]),
        "source_relationship": relationship,
        "overlay_role": role,
    }


def source_binding_for_row(raw: dict) -> dict:
    source_receipt = raw["_receipt_path"]
    receipt = read_json(source_receipt, source_receipt.name)
    return receipt_binding(source_receipt, receipt)


def make_maps() -> tuple[dict, dict, dict]:
    news8_receipt, news8_rows, news8_binding = validate_public_receipt(NEWS8_RECEIPT, 8, "news8-next")
    batch1_receipt, batch1_rows, batch1_binding = validate_public_receipt(BATCH1_RECEIPT, 10, "news20-batch1")
    batch2_receipt, batch2_rows, batch2_binding = validate_public_receipt(BATCH2_RECEIPT, 9, "news20-batch2")
    primary_news8 = [row for row in news8_rows if host(row["original"]) in {"www.worldofwarcraft.com", "worldofwarcraft.com"}]
    supplement_news8 = [row for row in news8_rows if host(row["original"]) == "www.blizzard.com"]
    if len(primary_news8) != 4 or len(supplement_news8) != 4:
        raise RuntimeError(f"news8 host split changed: primary={len(primary_news8)} supplement={len(supplement_news8)}")
    if any(host(row["original"]) != "www.worldofwarcraft.com" for row in batch1_rows + batch2_rows):
        raise RuntimeError("news20 batch contains a non-primary host")
    primary_rows = primary_news8 + batch1_rows + batch2_rows
    supplement_rows = supplement_news8
    primary_items = [
        make_item(row, role="primary_image_overlay", relationship="Root-accepted public-copy bytes; v27 primary overlay; no deployment implied.")
        for row in primary_rows
    ]
    supplement_items = [
        make_item(row, role="related_site_image_supplement", relationship="Root-accepted Blizzard public-copy bytes; v27 explicit supplement overlay; origin namespace preserved; no deployment implied.")
        for row in supplement_rows
    ]
    primary_map = {
        "schema_version": "wow-recovery.integration.v27.primary-source-map.v1",
        "kind": "wow_news_v27_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v27_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the four root-accepted news8 WoW-host images and nineteen root-accepted news20 batch1/batch2 WoW-host images are included; local copies are byte-verified and never re-encoded.",
        "source_acceptance": [news8_binding, batch1_binding, batch2_binding],
        "public_copy_acceptance": [
            {"path": rel(NEWS8_RECEIPT), "sha256": sha256_file(NEWS8_RECEIPT), "count": len(news8_rows)},
            {"path": rel(BATCH1_RECEIPT), "sha256": sha256_file(BATCH1_RECEIPT), "count": len(batch1_rows)},
            {"path": rel(BATCH2_RECEIPT), "sha256": sha256_file(BATCH2_RECEIPT), "count": len(batch2_rows)},
        ],
        "items": primary_items,
    }
    supplement_map = {
        "schema_version": "wow-recovery.integration.v27.blizzard-supplement-source-map.v1",
        "kind": "wow_blizzard_v27_supplement_image_source_map",
        "purpose": "Four root-accepted www.blizzard.com images; they remain explicit supplements and route under the Blizzard origin namespace.",
        "role": "related_site_image_supplement",
        "accepted": False,
        "status": "prepared_waiting_root_v27_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Each local_path points to a root-accepted public copy; exporter verifies SHA-256, length, MIME, timestamp, CDX digest, and origin route.",
        "source_acceptance": [news8_binding],
        "public_copy_acceptance": [{"path": rel(NEWS8_RECEIPT), "sha256": sha256_file(NEWS8_RECEIPT), "count": len(supplement_rows)}],
        "items": supplement_items,
    }
    receipts = {
        "news8": {"path": rel(NEWS8_RECEIPT), "sha256": sha256_file(NEWS8_RECEIPT), "accepted_count": len(news8_rows), "bytes": sum(int(row["length"]) for row in news8_rows)},
        "batch1": {"path": rel(BATCH1_RECEIPT), "sha256": sha256_file(BATCH1_RECEIPT), "accepted_count": len(batch1_rows), "bytes": sum(int(row["length"]) for row in batch1_rows)},
        "batch2": {"path": rel(BATCH2_RECEIPT), "sha256": sha256_file(BATCH2_RECEIPT), "accepted_count": len(batch2_rows), "bytes": sum(int(row["length"]) for row in batch2_rows)},
    }
    return primary_map, supplement_map, receipts


def validate_v26_closure() -> dict:
    checks = {
        "v25_provenance": (V25_PROVENANCE, EXPECTED_V25_PROVENANCE_SHA256),
        "v26_provenance": (V26_PROVENANCE, EXPECTED_V26_PROVENANCE_SHA256),
        "source_manifest": (SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "v26_export_acceptance": (V26_EXPORT_ACCEPTANCE, EXPECTED_V26_EXPORT_ACCEPTANCE_SHA256),
        "v26_news_map": (V26_NEWS_MAP, EXPECTED_V26_NEWS_MAP_SHA256),
        "v26_neighbor_map": (V26_NEIGHBOR_MAP, EXPECTED_V26_NEIGHBOR_MAP_SHA256),
        "v26_collection_map": (V26_COLLECTION_MAP, EXPECTED_V26_COLLECTION_MAP_SHA256),
    }
    results: dict[str, str] = {}
    for label, (path, expected) in checks.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen {label} SHA changed: {actual} != {expected}")
        results[label] = actual
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if manifest.get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 manifest anchor changed")
    exporter_sha = sha256_file(ROOT / "tools/export_github_pages.py")
    if exporter_sha != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError(f"approved exporter SHA changed: {exporter_sha}")
    export_acceptance = read_json(V26_EXPORT_ACCEPTANCE, "v26 export acceptance")
    if export_acceptance.get("accepted") is not True or export_acceptance.get("declared_files") != 8654 or export_acceptance.get("actual_files") != 8655:
        raise RuntimeError("v26 export acceptance baseline is not the accepted 8654/8655 result")
    collection = read_json(V26_COLLECTION_MAP, "v26 guide collection map")
    groups = collection.get("groups")
    if not isinstance(groups, list) or len(groups) != 3 or sum(len(group.get("images") or []) for group in groups) != 39:
        raise RuntimeError("v26 guide collection closure is not 3 groups/39 images")
    frozen = {}
    for relative, expected in frozen_v25.FROZEN_MAP_SHAS.items():
        path = ROOT / relative
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen v25 map changed: {relative}")
        frozen[relative] = actual
    results["frozen_v25_map_count"] = str(len(frozen))
    results["exporter"] = exporter_sha
    results["guide_collection_groups"] = "3"
    results["guide_collection_images"] = "39"
    return results


def map_route_sets(map_paths: tuple[Path, ...], export_module) -> tuple[set[str], set[str]]:
    routes: set[str] = set()
    static_paths: set[str] = set()
    for path in map_paths:
        payload = read_json(path, f"image map {path.name}")
        items = payload.get("items")
        if not isinstance(items, list):
            raise RuntimeError(f"image map has no items: {path}")
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise RuntimeError(f"image map item is not an object: {path}[{index}]")
            logical = str(item.get("logical_url") or item.get("original") or "")
            if not logical:
                raise RuntimeError(f"image map item has no logical URL: {path}[{index}]")
            route = export_module.mirror.route_path(logical) if export_module.mirror.is_primary_origin(logical) else export_module.mirror.origin_route(logical)
            routes.add(route)
            static_paths.add(export_module.static_rel_for_route(route))
    return routes, static_paths


def build_impact(items: list[dict]) -> dict:
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    targets = {canonical_url(str(item["original"])): item for item in items}
    found: dict[str, list[dict]] = {str(item["original"]): [] for item in items}
    for record in manifest.get("files", []):
        if not isinstance(record, dict):
            continue
        for reference in record.get("references", []) or []:
            if not isinstance(reference, dict):
                continue
            resolved = str(reference.get("resolved_url") or "")
            item = targets.get(canonical_url(resolved))
            if item is None:
                continue
            target = str(reference.get("target") or "")
            query = parse_qs(urlsplit(target).query)
            source = unquote(query.get("source", [""])[0]) or str(record.get("route") or "")
            source_route = urlsplit(source).path if source.startswith(("http://", "https://")) else source
            found[str(item["original"])].append(
                {
                    "source_page": source_route,
                    "manifest_route": str(record.get("route") or ""),
                    "action": str(reference.get("action") or ""),
                    "context": str(reference.get("context") or ""),
                    "target": target,
                }
            )
    rows = []
    for item in items:
        original = str(item["original"])
        parsed = urlsplit(original)
        output_path = ("_origins/" + host(original) + parsed.path) if host(original) == "www.blizzard.com" else parsed.path.lstrip("/")
        refs = found[original]
        rows.append({
            "original": original,
            "output_path": output_path,
            "reference_count": len(refs),
            "references": refs,
        })
    affected_pages = sorted({ref["source_page"] for row in rows for ref in row["references"] if ref["source_page"]})
    placeholder_count = sum(ref["action"] == "placeholder" for row in rows for ref in row["references"])
    return {
        "schema": "wow-recovery.integration.v27-impact-estimate.v1",
        "status": "static_manifest_estimate_only",
        "source_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256_file(SOURCE_MANIFEST)},
        "new_image_count": len(items),
        "expected_output_paths": [row["output_path"] for row in rows],
        "items": rows,
        "affected_page_routes": affected_pages,
        "static_missing_reduction_estimate": {
            "placeholder_reference_occurrences": placeholder_count,
            "unique_affected_page_routes": len(affected_pages),
            "new_assets_without_frozen_manifest_reference": sum(row["reference_count"] == 0 for row in rows),
            "note": "Counts are manifest-reference estimates; they are not browser or post-export proof."
        },
        "network_requests": 0,
        "export_executed": False,
    }


def validate_new_maps(primary_map: dict, supplement_map: dict) -> dict:
    for label, payload, expected_count in (("primary", primary_map, 23), ("supplement", supplement_map, 4)):
        if not isinstance(payload.get("items"), list) or len(payload["items"]) != expected_count:
            raise RuntimeError(f"v27 {label} item count changed")
        for index, item in enumerate(payload["items"]):
            local = str(item.get("local_path") or "")
            if not local.startswith("research/continuous-recovery-20261018/integration/v27/accepted-images/") or "private-payloads" in local:
                raise RuntimeError(f"v27 {label}[{index}] local_path is not a public integration copy: {local}")
            path = inside(ROOT / local, f"v27 {label}[{index}]")
            if not path.is_file() or path.stat().st_size != int(item.get("length", -1)) or sha256_file(path) != str(item.get("sha256") or "").casefold():
                raise RuntimeError(f"v27 {label}[{index}] bytes differ from map")
    return {"primary_items": len(primary_map["items"]), "supplement_items": len(supplement_map["items"])}


def loader_preflight(primary_map: dict, supplement_map: dict) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    records = {export_github_pages.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", []) if isinstance(item, dict)}
    frozen_routes = set(records)
    frozen_paths = {export_github_pages.static_rel_for_route(route, item) for route, item in records.items()}
    old_primary_routes, old_primary_paths = map_route_sets(tuple(frozen_v25.PRIMARY_MAPS) + (V26_NEWS_MAP,), export_github_pages)
    old_supplement_routes, old_supplement_paths = map_route_sets(tuple(frozen_v25.SUPPLEMENT_MAPS) + (V26_NEIGHBOR_MAP,), export_github_pages)
    frozen_routes |= old_primary_routes | old_supplement_routes
    frozen_paths |= old_primary_paths | old_supplement_paths
    primary, primary_bytes = export_github_pages.load_image_overlays((V27_PRIMARY_MAP,), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=frozen_routes, frozen_static_paths=frozen_paths)
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_paths = frozen_paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays((V27_SUPPLEMENT_MAP,), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=overlay_routes, frozen_static_paths=overlay_paths, allow_later_image_supplements=True)
    loaded_originals = {str(item["original_url"]) for item in primary + supplement}
    expected_originals = {str(item["original"]) for item in primary_map["items"] + supplement_map["items"]}
    if loaded_originals != expected_originals:
        raise RuntimeError("v27 loader did not load exactly the prepared originals")
    collection = read_json(V26_COLLECTION_MAP, "v26 guide collection map")
    return {
        "primary_overlay_records": 125 + len(primary),
        "primary_overlay_bytes_checked_new": primary_bytes,
        "supplement_overlay_records": 71 + len(supplement),
        "supplement_overlay_bytes_checked_new": supplement_bytes,
        "total_overlay_records": 196 + len(primary) + len(supplement),
        "new_primary_records": len(primary),
        "new_supplement_records": len(supplement),
        "guide_collection_groups": len(collection["groups"]),
        "guide_collection_images": sum(len(group.get("images") or []) for group in collection["groups"]),
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }


def write_once(path: Path, payload: dict, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing {label}: {path}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_root_acceptance(primary_map: dict, supplement_map: dict, preflight_sha: str) -> dict:
    receipt = read_json(ROOT_V27_INPUT_ACCEPTANCE, "root v27 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v27 input acceptance is not accepted")
    bindings = {str(item.get("path")): str(item.get("sha256", "")).casefold() for item in receipt.get("map_bindings", []) if isinstance(item, dict)}
    for path in (V27_PRIMARY_MAP, V27_SUPPLEMENT_MAP, V27_IMPACT, V27_PREFLIGHT):
        expected = preflight_sha if path == V27_PREFLIGHT else sha256_file(path)
        if bindings.get(rel(path)) != expected:
            raise RuntimeError(f"root v27 map binding mismatch: {rel(path)}")
    if str(receipt.get("preflight_sha256") or "").casefold() != preflight_sha:
        raise RuntimeError("root v27 preflight SHA mismatch")
    return {"path": rel(ROOT_V27_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_V27_INPUT_ACCEPTANCE)}


def guard_outputs() -> None:
    if V27_OUTPUT.exists() or V27_OUTPUT.with_name(V27_OUTPUT.name + ".partial").exists() or V27_RECEIPT.exists():
        raise RuntimeError("refusing existing v27 output, partial output, or worker receipt")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="write v27 maps, impact estimate, and preparation receipt")
    parser.add_argument("--preflight", action="store_true", help="run offline new-map preflight and write receipt")
    parser.add_argument("--go", action="store_true", help="enter the single exporter call; requires --root-export-go")
    parser.add_argument("--root-export-go", action="store_true", help="explicit root export gate")
    args = parser.parse_args(argv)
    if not (args.prepare or args.preflight or args.go or args.root_export_go):
        print(json.dumps({"status": "prepared_only", "network_requests": 0, "export_executed": False}, ensure_ascii=False))
        return 0
    if args.root_export_go and not args.go:
        parser.error("--root-export-go requires --go")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v27 preparation/export: {free_before}")
    closure = validate_v26_closure()
    primary_map, supplement_map, receipts = make_maps()
    if args.prepare:
        write_once(V27_PRIMARY_MAP, primary_map, "v27 primary map")
        write_once(V27_SUPPLEMENT_MAP, supplement_map, "v27 supplement map")
        impact = build_impact(primary_map["items"] + supplement_map["items"])
        write_once(V27_IMPACT, impact, "v27 impact estimate")
        prep = {
            "schema": "wow-recovery.integration.v27-input-preparation.v1",
            "status": "prepared_waiting_root_v27_input_acceptance",
            "checked_utc": datetime.utcnow().isoformat() + "Z",
            "frozen_v26_closure": closure,
            "receipts": receipts,
            "primary_map": {"path": rel(V27_PRIMARY_MAP), "sha256": sha256_file(V27_PRIMARY_MAP), "item_count": len(primary_map["items"])},
            "supplement_map": {"path": rel(V27_SUPPLEMENT_MAP), "sha256": sha256_file(V27_SUPPLEMENT_MAP), "item_count": len(supplement_map["items"])},
            "impact": {"path": rel(V27_IMPACT), "sha256": sha256_file(V27_IMPACT)},
            "network_requests": 0,
            "export_executed": False,
            "disk_free_before_bytes": free_before,
        }
        write_once(V27_PREPARATION, prep, "v27 preparation receipt")
    else:
        primary_map = read_json(V27_PRIMARY_MAP, "v27 primary map")
        supplement_map = read_json(V27_SUPPLEMENT_MAP, "v27 supplement map")
        validate_new_maps(primary_map, supplement_map)
    if args.preflight or args.go:
        if not V27_PRIMARY_MAP.is_file() or not V27_SUPPLEMENT_MAP.is_file() or not V27_IMPACT.is_file():
            raise RuntimeError("v27 maps and impact estimate must be prepared first")
        validate_new_maps(primary_map, supplement_map)
        loader = loader_preflight(primary_map, supplement_map)
        preflight = {
            "schema": "wow-recovery.integration.v27-preflight.v1",
            "status": "preflight_passed_waiting_root_export_go",
            "checked_utc": datetime.utcnow().isoformat() + "Z",
            "frozen_v26_closure": closure,
            "receipts": receipts,
            "primary_map": {"path": rel(V27_PRIMARY_MAP), "sha256": sha256_file(V27_PRIMARY_MAP)},
            "supplement_map": {"path": rel(V27_SUPPLEMENT_MAP), "sha256": sha256_file(V27_SUPPLEMENT_MAP)},
            "impact": {"path": rel(V27_IMPACT), "sha256": sha256_file(V27_IMPACT)},
            "loader_preflight": loader,
            "expected_after_export": {"declared_files": 8681, "actual_files": 8682, "primary_overlays": 148, "supplement_overlays": 75, "total_overlays": 223, "guide_previews": 22, "guide_collection_images": 39},
            "network_requests": 0,
            "export_executed": False,
            "root_export_go_required": True,
            "old_image_payloads_rehashed": False,
            "disk_free_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if args.preflight:
            write_once(V27_PREFLIGHT, preflight, "v27 preflight receipt")
    if not args.go:
        print(json.dumps({"status": "preflight_only" if args.preflight else "prepared", "network_requests": 0, "export_executed": False}, ensure_ascii=False))
        return 0
    if not args.root_export_go:
        parser.error("v27 export requires both --go and --root-export-go")
    root_acceptance = validate_root_acceptance(primary_map, supplement_map, sha256_file(V27_PREFLIGHT))
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v27 export: {free_before_export}")
    started = datetime.utcnow().isoformat() + "Z"
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=V27_OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=PRIMARY_MAPS,
            supplement_image_source_maps=SUPPLEMENT_MAPS,
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=V26_COLLECTION_MAP,
        )
        provenance = read_json(V27_OUTPUT / "export-provenance.json", "v27 output provenance")
        stats = provenance.get("stats") or {}
        expected_stats = {"source_records": 8357, "image_overlay_records": 223, "primary_image_overlay_records": 148, "supplement_image_overlay_records": 75, "output_files": 8681}
        for key, expected in expected_stats.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v27 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in V27_OUTPUT.rglob("*") if path.is_file())
        if actual_files != 8682:
            raise RuntimeError(f"v27 actual file count {actual_files}")
        receipt = {"schema": "wow-recovery.integration.v27-build-receipt.v1", "executed_by": "/root/local_recovery_20261018", "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/v27/build_pages_v27.py --go --root-export-go", "checked_utc_start": started, "checked_utc_end": datetime.utcnow().isoformat() + "Z", "export_started": True, "export_completed": True, "published": False, "network_requests_by_builder": 0, "root_input_acceptance": root_acceptance, "build": result, "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_sha256": sha256_file(V27_OUTPUT / "export-provenance.json")}, "output": rel(V27_OUTPUT), "disk_free_before_bytes": free_before_export, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES}
        write_once(V27_RECEIPT, receipt, "v27 build receipt")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        failure = {"schema": "wow-recovery.integration.v27-build-receipt.v1", "executed_by": "/root/local_recovery_20261018", "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/v27/build_pages_v27.py --go --root-export-go", "checked_utc_start": started, "checked_utc_end": datetime.utcnow().isoformat() + "Z", "export_started": True, "export_completed": False, "published": False, "network_requests_by_builder": 0, "root_input_acceptance": root_acceptance, "error": f"{type(exc).__name__}: {exc}", "output": rel(V27_OUTPUT) if V27_OUTPUT.exists() else None, "partial_exists": V27_OUTPUT.with_name(V27_OUTPUT.name + ".partial").exists(), "disk_free_before_bytes": free_before_export, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES}
        if not V27_RECEIPT.exists():
            V27_RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
