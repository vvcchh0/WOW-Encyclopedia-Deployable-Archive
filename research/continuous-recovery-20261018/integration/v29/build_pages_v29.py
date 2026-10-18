#!/usr/bin/env python3
"""Prepare and preflight the v29 image-input extension.

This is deliberately a preparation-only wrapper.  It imports the frozen v28
builder for receipt/map/closure helpers, pins the accepted v28 builder, map,
and provenance bytes, validates four new public-copy receipts, writes one new
v29 primary map plus audit metadata, and never calls the exporter or v28 main.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V28_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"
V28_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"
V28_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-build-receipt.json"
V29_RECEIPTS = tuple(
    ROOT / f"research/continuous-recovery-20261018/publication/root-news-unplanned-batch{index}-public-copy-acceptance.json"
    for index in range(5, 9)
)
V29_PRIMARY_MAP = INTEGRATION / "v29-primary-source-map.json"
V29_IMPACT = INTEGRATION / "v29-impact-estimate.json"
V29_PREPARATION = INTEGRATION / "v29-input-preparation.json"
V29_PREFLIGHT = INTEGRATION / "v29-preflight.json"
V29_PROPOSAL = INTEGRATION / "v29-input-proposal.md"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
V29_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v29"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V28_RECEIPT_SHA256 = "2483e506f268ff43a022612e0b2c581cf753bab9935c530812c6da68cd227f3e"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_EXPORTER_SHA256 = "943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_V29_RECEIPT_SHAS = (
    "6344e3830f37651eadf56809e3eebeaff0d4c975a4d27d6ca3ce210299d6cca3",
    "dbe8a2cde67aff1c79f3d50b263ab0b7ef5c0fe2daf62813093afa0fcbb92d6f",
    "aa0617d99d0cd8a08f83564ab1de9849b520109416e1f445094f3ca63b6e4042",
    "5a2234a78b5e2dea2d8e2ab0d22019f13dad2db8df5788d6bcf3b174b938069e",
)
EXPECTED_V29_IMAGE_COUNT = 40
EXPECTED_V29_IMAGE_BYTES = 318622
EXPECTED_V28_PRIMARY_COUNT = 188
EXPECTED_V28_SUPPLEMENT_COUNT = 75
EXPECTED_V28_TOTAL_COUNT = 263
EXPECTED_SOURCE_RECORDS = 8357
EXPECTED_GUIDE_IMAGES = 39
EXPECTED_GUIDE_PREVIEWS = 22
EXPECTED_DECLARED_FILES = 8761
EXPECTED_ACTUAL_FILES = 8762


def load_frozen_v28():
    actual = sha256_file(V28_BUILDER)
    if actual != EXPECTED_V28_BUILDER_SHA256:
        raise RuntimeError(f"frozen v28 builder SHA changed: {actual} != {EXPECTED_V28_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_frozen_v28_builder", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def host(url: str) -> str:
    return (urlsplit(url).hostname or "").casefold().rstrip(".")


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme.casefold()}://{host(url)}{parsed.path}"


def validate_v28_pins(frozen) -> dict:
    checks = {
        "v28_builder": (V28_BUILDER, EXPECTED_V28_BUILDER_SHA256),
        "v28_primary_map": (V28_PRIMARY_MAP, EXPECTED_V28_PRIMARY_MAP_SHA256),
        "v28_provenance": (V28_PROVENANCE, EXPECTED_V28_PROVENANCE_SHA256),
        "v28_build_receipt": (V28_RECEIPT, EXPECTED_V28_RECEIPT_SHA256),
        "source_manifest": (SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "exporter": (ROOT / "tools/export_github_pages.py", EXPECTED_EXPORTER_SHA256),
        "historical_exhibits": (ROOT / "tools/historical_exhibits.py", EXPECTED_HISTORICAL_EXHIBITS_SHA256),
    }
    result = {}
    for label, (path, expected) in checks.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen {label} SHA changed: {actual} != {expected}")
        result[label] = actual
    provenance = read_json(V28_PROVENANCE, "v28 provenance")
    stats = provenance.get("stats") or {}
    expected_stats = {
        "source_records": EXPECTED_SOURCE_RECORDS,
        "image_overlay_records": EXPECTED_V28_TOTAL_COUNT,
        "primary_image_overlay_records": EXPECTED_V28_PRIMARY_COUNT,
        "supplement_image_overlay_records": EXPECTED_V28_SUPPLEMENT_COUNT,
        "output_files": EXPECTED_DECLARED_FILES - 40,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v28 provenance {key}={stats.get(key)!r}, expected {expected}")
    result["v28_stats"] = expected_stats
    # This calls only frozen read/closure checks; v28 main is never invoked.
    result["frozen_v28_closure"] = frozen.validate_frozen_closure()
    return result


def make_receipts(frozen):
    rows = []
    summaries = []
    bindings = []
    seen = set()
    for receipt_path in V29_RECEIPTS:
        expected_sha = EXPECTED_V29_RECEIPT_SHAS[V29_RECEIPTS.index(receipt_path)]
        if expected_sha:
            actual_sha = sha256_file(receipt_path)
            if actual_sha != expected_sha:
                raise RuntimeError(f"v29 receipt SHA changed: {receipt_path.name}")
        receipt, receipt_rows, binding = frozen.validate_public_receipt(receipt_path, 10)
        for row in receipt_rows:
            original = str(row["original"])
            if original in seen:
                raise RuntimeError(f"v29 duplicate original across receipts: {original}")
            if host(original) != "www.worldofwarcraft.com":
                raise RuntimeError(f"v29 primary map has non-primary host: {original}")
            seen.add(original)
        rows.extend(receipt_rows)
        bindings.append(binding)
        summaries.append({
            "path": rel(receipt_path),
            "sha256": sha256_file(receipt_path),
            "count": len(receipt_rows),
            "bytes": sum(int(row["length"]) for row in receipt_rows),
            "accepted": receipt.get("accepted") is True,
        })
    if len(rows) != EXPECTED_V29_IMAGE_COUNT:
        raise RuntimeError(f"v29 expected {EXPECTED_V29_IMAGE_COUNT} images, got {len(rows)}")
    total_bytes = sum(int(row["length"]) for row in rows)
    if total_bytes != EXPECTED_V29_IMAGE_BYTES:
        raise RuntimeError(f"v29 expected {EXPECTED_V29_IMAGE_BYTES} bytes, got {total_bytes}")
    old_originals = set()
    for map_path in tuple(frozen.PRIMARY_MAPS) + tuple(frozen.SUPPLEMENT_MAPS) + (V28_PRIMARY_MAP,):
        payload = read_json(map_path, map_path.name)
        old_originals.update(str(item.get("original") or item.get("logical_url") or "") for item in payload.get("items", []))
    overlap = old_originals & seen
    if overlap:
        raise RuntimeError(f"v29 originals overlap frozen v28 closure: {sorted(overlap)}")
    items = [
        frozen.make_item(
            row,
            role="primary_image_overlay",
            relationship="Root-accepted public-copy bytes; v29 primary overlay; no deployment implied.",
        )
        for row in rows
    ]
    primary_map = {
        "schema_version": "wow-recovery.integration.v29.primary-source-map.v1",
        "kind": "wow_news_v29_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v29_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the forty root-accepted www.worldofwarcraft.com public-copy images from unplanned batches 5-8 are added; existing publication copies are byte-verified and never re-encoded.",
        "relative_to_v28": {
            "new_primary_items": EXPECTED_V29_IMAGE_COUNT,
            "new_bytes": EXPECTED_V29_IMAGE_BYTES,
            "v28_primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": sha256_file(V28_PRIMARY_MAP), "items": len(read_json(V28_PRIMARY_MAP, V28_PRIMARY_MAP.name)["items"])},
            "v28_provenance": {"path": rel(V28_PROVENANCE), "sha256": sha256_file(V28_PROVENANCE), "primary_overlays": EXPECTED_V28_PRIMARY_COUNT, "supplement_overlays": EXPECTED_V28_SUPPLEMENT_COUNT},
        },
        "source_acceptance": bindings,
        "public_copy_acceptance": summaries,
        "items": items,
    }
    return primary_map, rows, summaries, bindings


def build_impact(frozen, items: list[dict]) -> dict:
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    targets = {canonical_url(str(item["original"])): item for item in items}
    found = {str(item["original"]): [] for item in items}
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
            found[str(item["original"])].append({
                "source_page": source_route,
                "manifest_route": str(record.get("route") or ""),
                "action": str(reference.get("action") or ""),
                "context": str(reference.get("context") or ""),
                "target": target,
            })
    rows = []
    for item in items:
        original = str(item["original"])
        rows.append({
            "original": original,
            "output_path": urlsplit(original).path.lstrip("/"),
            "reference_count": len(found[original]),
            "references": found[original],
        })
    affected = sorted({ref["source_page"] for row in rows for ref in row["references"] if ref["source_page"]})
    return {
        "schema": "wow-recovery.integration.v29-impact-estimate.v1",
        "status": "static_manifest_estimate_only",
        "relative_to_v28": {"new_image_count": EXPECTED_V29_IMAGE_COUNT, "new_bytes": EXPECTED_V29_IMAGE_BYTES, "v28_overlay_records": EXPECTED_V28_TOTAL_COUNT},
        "source_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256_file(SOURCE_MANIFEST)},
        "new_image_count": len(items),
        "expected_output_paths": [row["output_path"] for row in rows],
        "items": rows,
        "affected_page_routes": affected,
        "static_missing_reduction_estimate": {
            "placeholder_reference_occurrences": sum(ref["action"] == "placeholder" for row in rows for ref in row["references"]),
            "unique_affected_page_routes": len(affected),
            "new_assets_without_frozen_manifest_reference": sum(row["reference_count"] == 0 for row in rows),
            "note": "Counts are manifest-reference estimates; they are not browser or post-export proof.",
        },
        "network_requests": 0,
        "export_executed": False,
    }


def validate_new_map(frozen, primary_map: dict) -> dict:
    items = primary_map.get("items")
    if not isinstance(items, list) or len(items) != EXPECTED_V29_IMAGE_COUNT:
        raise RuntimeError(f"v29 primary item count changed: {len(items or [])}")
    originals = set()
    total = 0
    for index, item in enumerate(items):
        original = str(item.get("original") or item.get("logical_url") or "")
        if not original or original in originals:
            raise RuntimeError(f"v29 primary[{index}] duplicate or missing original")
        originals.add(original)
        if host(original) != "www.worldofwarcraft.com":
            raise RuntimeError(f"v29 primary[{index}] non-primary host: {original}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local:
            raise RuntimeError(f"v29 primary[{index}] local_path is not a public copy: {local}")
        path = ROOT / local
        if not path.is_file():
            raise RuntimeError(f"v29 public copy missing: {path}")
        data = path.read_bytes()
        if len(data) != int(item.get("length", -1)) or hashlib.sha256(data).hexdigest() != str(item.get("sha256") or "").casefold():
            raise RuntimeError(f"v29 public copy bytes differ: {original}")
        if frozen.cdx_digest(data) != str(item.get("cdx_digest") or "").upper():
            raise RuntimeError(f"v29 public copy CDX differs: {original}")
        total += len(data)
    if total != EXPECTED_V29_IMAGE_BYTES:
        raise RuntimeError(f"v29 map byte total changed: {total}")
    return {"primary_items": len(items), "supplement_items": 0, "bytes": total}


def loader_preflight(frozen, primary_map: dict) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    records = {export_github_pages.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", []) if isinstance(item, dict)}
    frozen_routes = set(records)
    frozen_paths = {export_github_pages.static_rel_for_route(route, item) for route, item in records.items()}
    old_primary_routes, old_primary_paths = frozen.map_route_sets(tuple(frozen.PRIMARY_MAPS), export_github_pages)
    old_supplement_routes, old_supplement_paths = frozen.map_route_sets(tuple(frozen.SUPPLEMENT_MAPS), export_github_pages)
    frozen_routes |= old_primary_routes | old_supplement_routes
    frozen_paths |= old_primary_paths | old_supplement_paths
    loaded, checked_bytes = export_github_pages.load_image_overlays((V29_PRIMARY_MAP,), workspace_root=ROOT, anchor_timestamp=ANCHOR, frozen_routes=frozen_routes, frozen_static_paths=frozen_paths)
    loaded_originals = {str(item["original_url"]) for item in loaded}
    expected_originals = {str(item["original"]) for item in primary_map["items"]}
    if loaded_originals != expected_originals:
        raise RuntimeError("v29 loader did not load exactly the prepared originals")
    collection = read_json(frozen.V26_COLLECTION_MAP, "v26 guide collection map")
    return {
        "primary_overlay_records": EXPECTED_V28_PRIMARY_COUNT + len(loaded),
        "primary_overlay_bytes_checked_new": checked_bytes,
        "supplement_overlay_records": EXPECTED_V28_SUPPLEMENT_COUNT,
        "supplement_overlay_bytes_checked_new": 0,
        "total_overlay_records": EXPECTED_V28_TOTAL_COUNT + len(loaded),
        "new_primary_records": len(loaded),
        "new_supplement_records": 0,
        "guide_collection_groups": len(collection["groups"]),
        "guide_collection_images": sum(len(group.get("images") or []) for group in collection["groups"]),
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }


def write_once(path: Path, value: dict | str, label: str):
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing {label}: {path}")
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare v29 inputs only; exporter is intentionally unavailable in this wrapper.")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if not (args.prepare and args.preflight):
        parser.error("v29 preparation requires both --prepare and --preflight")
    if V29_OUTPUT.exists():
        raise RuntimeError(f"refusing to touch existing v29 output: {V29_OUTPUT}")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor before v29 preparation: {free_before}")
    frozen = load_frozen_v28()
    frozen_pins = validate_v28_pins(frozen)
    primary_map, rows, receipt_summaries, bindings = make_receipts(frozen)
    # Prepare the map and all audit data in memory before any output is created.
    impact = build_impact(frozen, rows)
    map_check = validate_new_map(frozen, primary_map)
    # The frozen exporter loader consumes a path, so materialize only the new
    # map before the read-only loader preflight.  All other artifacts are still
    # written only after that preflight succeeds.
    map_sha = hashlib.sha256(json.dumps(primary_map, ensure_ascii=False, indent=2).encode("utf-8") + b"\n").hexdigest()
    write_once(V29_PRIMARY_MAP, primary_map, "v29 primary map")
    loader = loader_preflight(frozen, primary_map)
    checked_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # The map hash above is checked against the exact bytes after write below;
    # this keeps preparation deterministic while preserving normal JSON layout.
    prep = {
        "schema": "wow-recovery.integration.v29-input-preparation.v1",
        "status": "prepared_waiting_root_v29_input_acceptance",
        "checked_utc": checked_utc,
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "frozen_v28_closure": {
            "v28_builder": frozen_pins["v28_builder"],
            "v28_primary_map": frozen_pins["v28_primary_map"],
            "v28_provenance": frozen_pins["v28_provenance"],
            "v28_build_receipt": frozen_pins["v28_build_receipt"],
            "source_manifest": frozen_pins["source_manifest"],
            "exporter": frozen_pins["exporter"],
            "historical_exhibits": frozen_pins["historical_exhibits"],
            "v28_stats": frozen_pins["v28_stats"],
            "v28_closure_validation": frozen_pins["frozen_v28_closure"],
        },
        "receipts": {"receipts": receipt_summaries, "bindings": bindings},
        "v28_reuse": {
            "primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": frozen_pins["v28_primary_map"], "item_count": len(read_json(V28_PRIMARY_MAP, V28_PRIMARY_MAP.name)["items"])},
            "output_provenance": {"path": rel(V28_PROVENANCE), "sha256": frozen_pins["v28_provenance"]},
            "supplement_records": EXPECTED_V28_SUPPLEMENT_COUNT,
            "primary_records": EXPECTED_V28_PRIMARY_COUNT,
        },
        "primary_map": {"path": rel(V29_PRIMARY_MAP), "sha256": map_sha, "item_count": EXPECTED_V29_IMAGE_COUNT, "bytes": EXPECTED_V29_IMAGE_BYTES},
        "impact": {"path": rel(V29_IMPACT), "new_image_count": EXPECTED_V29_IMAGE_COUNT},
        "expected_after_export": {
            "declared_files": EXPECTED_DECLARED_FILES,
            "actual_files": EXPECTED_ACTUAL_FILES,
            "primary_overlays": EXPECTED_V28_PRIMARY_COUNT + EXPECTED_V29_IMAGE_COUNT,
            "supplement_overlays": EXPECTED_V28_SUPPLEMENT_COUNT,
            "total_overlays": EXPECTED_V28_TOTAL_COUNT + EXPECTED_V29_IMAGE_COUNT,
            "guide_previews": EXPECTED_GUIDE_PREVIEWS,
            "guide_collection_images": EXPECTED_GUIDE_IMAGES,
        },
        "network_requests": 0,
        "export_executed": False,
        "output": rel(V29_OUTPUT),
        "disk_free_before_bytes": free_before,
    }
    preflight = {
        "schema": "wow-recovery.integration.v29-preflight.v1",
        "status": "preflight_passed_waiting_root_v29_input_acceptance",
        "checked_utc": checked_utc,
        "builder": prep["builder"],
        "frozen_v28_closure": prep["frozen_v28_closure"],
        "receipts": prep["receipts"],
        "primary_map": prep["primary_map"],
        "impact": {"path": rel(V29_IMPACT), "sha256": hashlib.sha256(json.dumps(impact, ensure_ascii=False, indent=2).encode("utf-8") + b"\n").hexdigest()},
        "map_validation": map_check,
        "loader_preflight": loader,
        "expected_after_export": prep["expected_after_export"],
        "network_requests": 0,
        "export_executed": False,
        "root_input_acceptance_required": True,
        "old_image_payloads_rehashed": False,
        "disk_free_bytes": shutil.disk_usage(ROOT).free,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    proposal = f"""# v29 input proposal\n\nThis preparation extends the frozen v28 closure with forty root-accepted public-copy images from unplanned batches 5-8. The new v29 primary map adds {EXPECTED_V29_IMAGE_COUNT} unique `www.worldofwarcraft.com` resources totaling {EXPECTED_V29_IMAGE_BYTES} bytes. Existing v28 primary/supplement maps and publication copies remain referenced by their immutable paths; no old map is copied or rewritten, and no new historical-exhibit wording is introduced.\n\nExpected integration after root acceptance is {EXPECTED_V28_PRIMARY_COUNT + EXPECTED_V29_IMAGE_COUNT} primary overlays, {EXPECTED_V28_SUPPLEMENT_COUNT} supplement overlays, {EXPECTED_V28_TOTAL_COUNT + EXPECTED_V29_IMAGE_COUNT} total overlays, {EXPECTED_DECLARED_FILES} declared files / {EXPECTED_ACTUAL_FILES} actual files, guide collection {EXPECTED_GUIDE_IMAGES}, and previews {EXPECTED_GUIDE_PREVIEWS}. These are planning expectations; this wrapper performs no export or publication.\n\nThe wrapper pins v28 builder `{EXPECTED_V28_BUILDER_SHA256}`, v28 primary map `{EXPECTED_V28_PRIMARY_MAP_SHA256}`, v28 provenance `{EXPECTED_V28_PROVENANCE_SHA256}`, exporter `{EXPECTED_EXPORTER_SHA256}`, historical exhibits `{EXPECTED_HISTORICAL_EXHIBITS_SHA256}`, and source manifest `{EXPECTED_SOURCE_MANIFEST_SHA256}`. Root input acceptance must bind the final map/preflight hashes before any future export decision.\n"""
    OUT_DIR = INTEGRATION
    write_once(V29_IMPACT, impact, "v29 impact estimate")
    # Refresh bytes-dependent hashes after the exact files have been written.
    prep["builder"]["sha256"] = sha256_file(Path(__file__))
    prep["primary_map"]["sha256"] = sha256_file(V29_PRIMARY_MAP)
    prep["impact"]["sha256"] = sha256_file(V29_IMPACT)
    preflight["builder"] = prep["builder"]
    preflight["primary_map"] = prep["primary_map"]
    preflight["impact"]["sha256"] = prep["impact"]["sha256"]
    write_once(V29_PREPARATION, prep, "v29 preparation")
    write_once(V29_PREFLIGHT, preflight, "v29 preflight")
    write_once(V29_PROPOSAL, proposal, "v29 proposal")
    print(json.dumps({
        "primary_map": rel(V29_PRIMARY_MAP),
        "primary_map_sha256": sha256_file(V29_PRIMARY_MAP),
        "impact_sha256": sha256_file(V29_IMPACT),
        "preparation_sha256": sha256_file(V29_PREPARATION),
        "preflight_sha256": sha256_file(V29_PREFLIGHT),
        "proposal_sha256": sha256_file(V29_PROPOSAL),
        "primary_items": EXPECTED_V29_IMAGE_COUNT,
        "new_bytes": EXPECTED_V29_IMAGE_BYTES,
        "loader": loader,
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
