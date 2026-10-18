#!/usr/bin/env python3
"""Prepare and preflight the v28 input closure; export is guarded and opt-in.

The v28 closure reuses the frozen v25/v26 maps and the accepted v27 primary
and Blizzard supplement maps, then adds only forty root-accepted public-copy
images. Preparation and preflight hash the new public copies and map metadata,
while the frozen image payloads are protected by their v25/v26/v27 receipts,
map hashes, and the frozen v27 output provenance. The exporter is called only
when both ``--go`` and ``--root-export-go`` are supplied after root acceptance.
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
V27_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v27/v27-primary-source-map.json"
V27_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v27/v27-blizzard-supplement-source-map.json"
V27_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v27/v27-preflight.json"
V27_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v27/v27-build-receipt.json"
V27_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v27"
V27_PROVENANCE = V27_OUTPUT / "export-provenance.json"
V28_RECEIPTS = tuple(
    ROOT / f"research/continuous-recovery-20261018/publication/root-news-unplanned-batch{index}-public-copy-acceptance.json"
    for index in range(1, 5)
)
V28_PRIMARY_MAP = INTEGRATION / "v28-primary-source-map.json"
V28_IMPACT = INTEGRATION / "v28-impact-estimate.json"
V28_PREPARATION = INTEGRATION / "v28-input-preparation.json"
V28_PREFLIGHT = INTEGRATION / "v28-preflight.json"
V28_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v28"
V28_RECEIPT = INTEGRATION / "v28-build-receipt.json"
ROOT_V28_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v28-input-acceptance.json"
ROOT_V27_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v27-input-acceptance.json"
V28_EXPECTATIONS = ROOT / "research/continuous-recovery-20261018/publication/v28-export-expectations.json"
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
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_V27_PRIMARY_MAP_SHA256 = "173b83af29adcdf3acb0d90292df1427dc1ef35bee1be3d84874769f6df1d3f9"
EXPECTED_V27_SUPPLEMENT_MAP_SHA256 = "00daa553e5d9c640cadc72aeee8a92bed98758d02b1a576b40740b1b42b740b7"
EXPECTED_V27_PREFLIGHT_SHA256 = "268787d944a4c420638f785c202e8288ff834fa371149673ca2065b3d8e9da5b"
EXPECTED_V27_BUILD_RECEIPT_SHA256 = "297a2c29147f6bf134302fcdd3524f875553d6badcf313e5edd319524b4c2087"
EXPECTED_V27_PROVENANCE_SHA256 = "271e474b80ce936c3a68b567a7c3e42c86851eb371772fa8108498613aa1f012"
EXPECTED_ROOT_V27_INPUT_ACCEPTANCE_SHA256 = "aed24cd509767d95866a5e5937d24f298dae1c3741d072e074aa6d7eed743397"
EXPECTED_V28_PUBLIC_COPY_RECEIPT_SHA256 = (
    "ee9132a5eac7977ee35ae64cf59d7e446792123a02782f28545a29542b77a816",
    "5c75c481619e79855d383e5334d58a363f316c31d09cfeb5424d96b14ece8dd2",
    "94dcabf875123ba6073ba835bda6e7f4e830cc5c994f882423874f8e812878ab",
    "6d898543de9df58561fb863e7124205b42de6e982c95bb1bb63efd93745a57f8",
)
EXPECTED_V28_IMAGE_COUNT = 40
EXPECTED_V28_IMAGE_BYTES = 436264

sys.path.insert(0, str(V25_LOCAL))
import build_pages_v25 as frozen_v25  # noqa: E402


PRIMARY_MAPS = tuple(frozen_v25.PRIMARY_MAPS) + (V26_NEWS_MAP, V27_PRIMARY_MAP, V28_PRIMARY_MAP)
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


def validate_public_receipt(receipt_path: Path, expected_count: int) -> tuple[dict, list[dict], dict]:
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
        row = dict(raw)
        row["_destination"] = source
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


def make_maps() -> tuple[dict, dict]:
    receipt_rows: list[dict] = []
    bindings: list[dict] = []
    receipt_summaries: list[dict] = []
    seen: set[str] = set()
    for index, receipt_path in enumerate(V28_RECEIPTS, start=1):
        receipt, rows, binding = validate_public_receipt(receipt_path, 10)
        for row in rows:
            original = str(row["original"])
            if original in seen:
                raise RuntimeError(f"v28 duplicate original across receipts: {original}")
            if host(original) != "www.worldofwarcraft.com":
                raise RuntimeError(f"v28 non-primary host: {original}")
            seen.add(original)
        receipt_rows.extend(rows)
        bindings.append(binding)
        receipt_summaries.append(
            {
                "path": rel(receipt_path),
                "sha256": sha256_file(receipt_path),
                "count": len(rows),
                "bytes": sum(int(row["length"]) for row in rows),
                "accepted": receipt.get("accepted") is True,
            }
        )
    if len(receipt_rows) != EXPECTED_V28_IMAGE_COUNT:
        raise RuntimeError(f"v28 expected {EXPECTED_V28_IMAGE_COUNT} rows, got {len(receipt_rows)}")
    total_bytes = sum(int(row["length"]) for row in receipt_rows)
    if total_bytes != EXPECTED_V28_IMAGE_BYTES:
        raise RuntimeError(f"v28 expected {EXPECTED_V28_IMAGE_BYTES} bytes, got {total_bytes}")
    old_originals: set[str] = set()
    for path in (V27_PRIMARY_MAP, V27_SUPPLEMENT_MAP):
        payload = read_json(path, path.name)
        old_originals.update(str(item.get("original") or item.get("logical_url") or "") for item in payload.get("items", []))
    overlap = old_originals & seen
    if overlap:
        raise RuntimeError(f"v28 originals overlap v27 maps: {sorted(overlap)}")
    primary_items = [
        make_item(
            row,
            role="primary_image_overlay",
            relationship="Root-accepted public-copy bytes; v28 primary overlay; no deployment implied.",
        )
        for row in receipt_rows
    ]
    primary_map = {
        "schema_version": "wow-recovery.integration.v28.primary-source-map.v1",
        "kind": "wow_news_v28_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v28_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the forty root-accepted www.worldofwarcraft.com public-copy images from unplanned batches 1-4 are added; publication copies are byte-verified and never re-encoded.",
        "relative_to_v27": {
            "new_primary_items": EXPECTED_V28_IMAGE_COUNT,
            "new_bytes": EXPECTED_V28_IMAGE_BYTES,
            "v27_primary_map": {"path": rel(V27_PRIMARY_MAP), "sha256": sha256_file(V27_PRIMARY_MAP), "items": len(read_json(V27_PRIMARY_MAP, V27_PRIMARY_MAP.name)["items"])},
            "v27_supplement_map": {"path": rel(V27_SUPPLEMENT_MAP), "sha256": sha256_file(V27_SUPPLEMENT_MAP), "items": len(read_json(V27_SUPPLEMENT_MAP, V27_SUPPLEMENT_MAP.name)["items"])},
        },
        "source_acceptance": bindings,
        "public_copy_acceptance": receipt_summaries,
        "items": primary_items,
    }
    return primary_map, {"receipts": receipt_summaries, "bindings": bindings}


def validate_frozen_closure() -> dict:
    checks = {
        "v25_provenance": (V25_PROVENANCE, EXPECTED_V25_PROVENANCE_SHA256),
        "v26_provenance": (V26_PROVENANCE, EXPECTED_V26_PROVENANCE_SHA256),
        "source_manifest": (SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "v26_export_acceptance": (V26_EXPORT_ACCEPTANCE, EXPECTED_V26_EXPORT_ACCEPTANCE_SHA256),
        "v26_news_map": (V26_NEWS_MAP, EXPECTED_V26_NEWS_MAP_SHA256),
        "v26_neighbor_map": (V26_NEIGHBOR_MAP, EXPECTED_V26_NEIGHBOR_MAP_SHA256),
        "v26_collection_map": (V26_COLLECTION_MAP, EXPECTED_V26_COLLECTION_MAP_SHA256),
        "v27_primary_map": (V27_PRIMARY_MAP, EXPECTED_V27_PRIMARY_MAP_SHA256),
        "v27_supplement_map": (V27_SUPPLEMENT_MAP, EXPECTED_V27_SUPPLEMENT_MAP_SHA256),
        "v27_preflight": (V27_PREFLIGHT, EXPECTED_V27_PREFLIGHT_SHA256),
        "v27_build_receipt": (V27_BUILD_RECEIPT, EXPECTED_V27_BUILD_RECEIPT_SHA256),
        "v27_provenance": (V27_PROVENANCE, EXPECTED_V27_PROVENANCE_SHA256),
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
    historical_sha = sha256_file(ROOT / "tools/historical_exhibits.py")
    if historical_sha != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError(f"accepted historical exhibits SHA changed: {historical_sha}")
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
    results["historical_exhibits"] = historical_sha
    results["guide_collection_groups"] = "3"
    results["guide_collection_images"] = "39"
    v27_receipt = read_json(V27_BUILD_RECEIPT, "v27 build receipt")
    if v27_receipt.get("published") is not False or v27_receipt.get("export_completed") is not True:
        raise RuntimeError("v27 build receipt is not the completed unpublished export")
    v27_provenance = read_json(V27_PROVENANCE, "v27 output provenance")
    v27_stats = v27_provenance.get("stats") or {}
    expected_v27_stats = {
        "source_records": 8357,
        "image_overlay_records": 223,
        "primary_image_overlay_records": 148,
        "supplement_image_overlay_records": 75,
        "output_files": 8681,
    }
    for key, expected in expected_v27_stats.items():
        if v27_stats.get(key) != expected:
            raise RuntimeError(f"v27 provenance {key}={v27_stats.get(key)!r}, expected {expected}")
    actual_v27_files = sum(1 for path in V27_OUTPUT.rglob("*") if path.is_file())
    if actual_v27_files != 8682:
        raise RuntimeError(f"v27 actual file count {actual_v27_files}, expected 8682")
    results["v27_actual_files"] = str(actual_v27_files)
    if V28_EXPECTATIONS.is_file():
        expectations = read_json(V28_EXPECTATIONS, "root v28 export expectations")
        if expectations.get("accepted") is not True:
            raise RuntimeError("root v28 export expectations are not accepted")
        expected_stats = expectations.get("stats") or {}
        if expected_stats != {
            "source_records": 8357,
            "image_overlay_records": 263,
            "primary_image_overlay_records": 188,
            "supplement_image_overlay_records": 75,
            "output_files": 8721,
        }:
            raise RuntimeError(f"root v28 expectations stats changed: {expected_stats}")
        if expectations.get("guide_collection_images") != 39:
            raise RuntimeError("root v28 expectations guide collection changed")
        if expectations.get("removed_static_unique_addresses") != 40 or expectations.get("removed_static_occurrences") != 40:
            raise RuntimeError("root v28 expectations removed-static counts changed")
        results["v28_expectations"] = sha256_file(V28_EXPECTATIONS)
    else:
        raise RuntimeError(f"missing root v28 expectations: {V28_EXPECTATIONS}")
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
        "schema": "wow-recovery.integration.v28-impact-estimate.v1",
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


def validate_new_map(primary_map: dict) -> dict:
    items = primary_map.get("items")
    if not isinstance(items, list) or len(items) != EXPECTED_V28_IMAGE_COUNT:
        raise RuntimeError(f"v28 primary item count changed: {len(items or [])}")
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise RuntimeError(f"v28 primary[{index}] is not an object")
        original = str(item.get("original") or item.get("logical_url") or "")
        if not original or original in seen:
            raise RuntimeError(f"v28 primary[{index}] duplicate or missing original: {original!r}")
        seen.add(original)
        if host(original) != "www.worldofwarcraft.com":
            raise RuntimeError(f"v28 primary[{index}] has non-primary host: {original}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local:
            raise RuntimeError(f"v28 primary[{index}] local_path is not a public publication copy: {local}")
        path = inside(ROOT / local, f"v28 primary[{index}]")
        if not path.is_file():
            raise RuntimeError(f"v28 primary[{index}] public copy missing: {path}")
        data = path.read_bytes()
        if len(data) != int(item.get("length", -1)) or hashlib.sha256(data).hexdigest() != str(item.get("sha256") or "").casefold():
            raise RuntimeError(f"v28 primary[{index}] bytes differ from map")
        if cdx_digest(data) != str(item.get("cdx_digest") or "").upper():
            raise RuntimeError(f"v28 primary[{index}] CDX digest differs from map")
    return {"primary_items": len(items), "supplement_items": 0, "bytes": sum(int(item["length"]) for item in items)}


def loader_preflight(primary_map: dict) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    records = {export_github_pages.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", []) if isinstance(item, dict)}
    frozen_routes = set(records)
    frozen_paths = {export_github_pages.static_rel_for_route(route, item) for route, item in records.items()}
    old_primary_routes, old_primary_paths = map_route_sets(tuple(frozen_v25.PRIMARY_MAPS) + (V26_NEWS_MAP, V27_PRIMARY_MAP), export_github_pages)
    old_supplement_routes, old_supplement_paths = map_route_sets(tuple(frozen_v25.SUPPLEMENT_MAPS) + (V26_NEIGHBOR_MAP, V27_SUPPLEMENT_MAP), export_github_pages)
    frozen_routes |= old_primary_routes | old_supplement_routes
    frozen_paths |= old_primary_paths | old_supplement_paths
    primary, primary_bytes = export_github_pages.load_image_overlays((V28_PRIMARY_MAP,), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=frozen_routes, frozen_static_paths=frozen_paths)
    loaded_originals = {str(item["original_url"]) for item in primary}
    expected_originals = {str(item["original"]) for item in primary_map["items"]}
    if loaded_originals != expected_originals:
        raise RuntimeError("v28 loader did not load exactly the prepared originals")
    collection = read_json(V26_COLLECTION_MAP, "v26 guide collection map")
    return {
        "primary_overlay_records": 148 + len(primary),
        "primary_overlay_bytes_checked_new": primary_bytes,
        "supplement_overlay_records": 75,
        "supplement_overlay_bytes_checked_new": 0,
        "total_overlay_records": 223 + len(primary),
        "new_primary_records": len(primary),
        "new_supplement_records": 0,
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


def validate_root_acceptance(primary_map: dict, preflight_sha: str) -> dict:
    receipt = read_json(ROOT_V28_INPUT_ACCEPTANCE, "root v28 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v28 input acceptance is not accepted")
    bindings = {str(item.get("path")): str(item.get("sha256", "")).casefold() for item in receipt.get("map_bindings", []) if isinstance(item, dict)}
    for path in (V28_PRIMARY_MAP, V28_IMPACT, V28_PREFLIGHT):
        expected = preflight_sha if path == V28_PREFLIGHT else sha256_file(path)
        if bindings.get(rel(path)) != expected:
            raise RuntimeError(f"root v28 map binding mismatch: {rel(path)}")
    if str(receipt.get("preflight_sha256") or "").casefold() != preflight_sha:
        raise RuntimeError("root v28 preflight SHA mismatch")
    return {"path": rel(ROOT_V28_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_V28_INPUT_ACCEPTANCE)}


def guard_outputs() -> None:
    if V28_OUTPUT.exists() or V28_OUTPUT.with_name(V28_OUTPUT.name + ".partial").exists() or V28_RECEIPT.exists():
        raise RuntimeError("refusing existing v28 output, partial output, or worker receipt")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="write v28 primary map, impact estimate, and preparation receipt")
    parser.add_argument("--preflight", action="store_true", help="run offline v28 map preflight and write receipt")
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
        raise RuntimeError(f"disk floor before v28 preparation/export: {free_before}")
    closure = validate_frozen_closure()
    primary_map, receipts = make_maps()
    if args.prepare:
        write_once(V28_PRIMARY_MAP, primary_map, "v28 primary map")
        impact = build_impact(primary_map["items"])
        write_once(V28_IMPACT, impact, "v28 impact estimate")
        prep = {
            "schema": "wow-recovery.integration.v28-input-preparation.v1",
            "status": "prepared_waiting_root_v28_input_acceptance",
            "checked_utc": datetime.utcnow().isoformat() + "Z",
            "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
            "frozen_v27_closure": closure,
            "receipts": receipts,
            "v27_reuse": {
                "primary_map": {"path": rel(V27_PRIMARY_MAP), "sha256": sha256_file(V27_PRIMARY_MAP), "item_count": len(read_json(V27_PRIMARY_MAP, V27_PRIMARY_MAP.name)["items"])},
                "supplement_map": {"path": rel(V27_SUPPLEMENT_MAP), "sha256": sha256_file(V27_SUPPLEMENT_MAP), "item_count": len(read_json(V27_SUPPLEMENT_MAP, V27_SUPPLEMENT_MAP.name)["items"])},
                "output_provenance": {"path": rel(V27_PROVENANCE), "sha256": sha256_file(V27_PROVENANCE)},
            },
            "primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": sha256_file(V28_PRIMARY_MAP), "item_count": len(primary_map["items"])},
            "impact": {"path": rel(V28_IMPACT), "sha256": sha256_file(V28_IMPACT)},
            "root_expectations": {"path": rel(V28_EXPECTATIONS), "sha256": sha256_file(V28_EXPECTATIONS)},
            "expected_after_export": {"declared_files": 8721, "actual_files": 8722, "primary_overlays": 188, "supplement_overlays": 75, "total_overlays": 263, "guide_previews": 22, "guide_collection_images": 39},
            "network_requests": 0,
            "export_executed": False,
            "disk_free_before_bytes": free_before,
        }
        write_once(V28_PREPARATION, prep, "v28 preparation receipt")
    else:
        primary_map = read_json(V28_PRIMARY_MAP, "v28 primary map")
        validate_new_map(primary_map)
    if args.preflight or args.go:
        if not V28_PRIMARY_MAP.is_file() or not V28_IMPACT.is_file():
            raise RuntimeError("v28 primary map and impact estimate must be prepared first")
        validate_new_map(primary_map)
        loader = loader_preflight(primary_map)
        preflight = {
            "schema": "wow-recovery.integration.v28-preflight.v1",
            "status": "preflight_passed_waiting_root_v28_export_go",
            "checked_utc": datetime.utcnow().isoformat() + "Z",
            "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
            "frozen_v27_closure": closure,
            "receipts": receipts,
            "primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": sha256_file(V28_PRIMARY_MAP)},
            "impact": {"path": rel(V28_IMPACT), "sha256": sha256_file(V28_IMPACT)},
            "root_expectations": {"path": rel(V28_EXPECTATIONS), "sha256": sha256_file(V28_EXPECTATIONS)},
            "loader_preflight": loader,
            "expected_after_export": {"declared_files": 8721, "actual_files": 8722, "primary_overlays": 188, "supplement_overlays": 75, "total_overlays": 263, "guide_previews": 22, "guide_collection_images": 39},
            "network_requests": 0,
            "export_executed": False,
            "root_export_go_required": True,
            "old_image_payloads_rehashed": False,
            "disk_free_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if args.preflight:
            write_once(V28_PREFLIGHT, preflight, "v28 preflight receipt")
    if not args.go:
        print(json.dumps({"status": "preflight_only" if args.preflight else "prepared", "network_requests": 0, "export_executed": False}, ensure_ascii=False))
        return 0
    if not args.root_export_go:
        parser.error("v28 export requires both --go and --root-export-go")
    root_acceptance = validate_root_acceptance(primary_map, sha256_file(V28_PREFLIGHT))
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v28 export: {free_before_export}")
    started = datetime.utcnow().isoformat() + "Z"
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=V28_OUTPUT,
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
        provenance = read_json(V28_OUTPUT / "export-provenance.json", "v28 output provenance")
        stats = provenance.get("stats") or {}
        expected_stats = {"source_records": 8357, "image_overlay_records": 263, "primary_image_overlay_records": 188, "supplement_image_overlay_records": 75, "output_files": 8721}
        for key, expected in expected_stats.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v28 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in V28_OUTPUT.rglob("*") if path.is_file())
        if actual_files != 8722:
            raise RuntimeError(f"v28 actual file count {actual_files}")
        receipt = {"schema": "wow-recovery.integration.v28-build-receipt.v1", "executed_by": "/root/local_recovery_20261018", "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/v28/build_pages_v28.py --go --root-export-go", "checked_utc_start": started, "checked_utc_end": datetime.utcnow().isoformat() + "Z", "export_started": True, "export_completed": True, "published": False, "network_requests_by_builder": 0, "root_input_acceptance": root_acceptance, "build": result, "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_sha256": sha256_file(V28_OUTPUT / "export-provenance.json")}, "output": rel(V28_OUTPUT), "disk_free_before_bytes": free_before_export, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES}
        write_once(V28_RECEIPT, receipt, "v28 build receipt")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        failure = {"schema": "wow-recovery.integration.v28-build-receipt.v1", "executed_by": "/root/local_recovery_20261018", "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/v28/build_pages_v28.py --go --root-export-go", "checked_utc_start": started, "checked_utc_end": datetime.utcnow().isoformat() + "Z", "export_started": True, "export_completed": False, "published": False, "network_requests_by_builder": 0, "root_input_acceptance": root_acceptance, "error": f"{type(exc).__name__}: {exc}", "output": rel(V28_OUTPUT) if V28_OUTPUT.exists() else None, "partial_exists": V28_OUTPUT.with_name(V28_OUTPUT.name + ".partial").exists(), "disk_free_before_bytes": free_before_export, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES}
        if not V28_RECEIPT.exists():
            V28_RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
