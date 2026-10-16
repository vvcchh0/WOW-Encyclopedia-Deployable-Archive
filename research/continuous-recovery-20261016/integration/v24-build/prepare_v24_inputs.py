#!/usr/bin/env python3
"""Prepare isolated v24 provisional/final inputs from accepted news receipts."""
from __future__ import annotations
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261016/integration/v24-build"
RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-news-content02-source-acceptance.json"
OPTIONAL_RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-news-content03-source-acceptance.json"
SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-content02/output/source-map.json"
PROVISIONAL_MAP = ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-content02-provisional.json"
PROVISIONAL_ASSET_DIR = ROOT / "research/continuous-recovery-20261016/integration/accepted-images/news-v24-content02-provisional"
PROVISIONAL_PLAN = OUT / "prepare-v24-input-plan-content02-provisional.json"
FINAL_MAP = ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json"
FINAL_ASSET_DIR = ROOT / "research/continuous-recovery-20261016/integration/accepted-images/news-v24-final"
FINAL_PLAN = OUT / "prepare-v24-input-plan-final.json"
V23_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v23/export-provenance.json"
V23_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v23-export-acceptance.json"
V23_WORKER = ROOT / "research/continuous-recovery-20261016/integration/v23-build/worker-build-v23-final40.json"
V23_PREP = ROOT / "research/continuous-recovery-20261016/integration/v23-build/preflight-v23-neighbor-inputs-final40.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ANCHOR = "20080512210044"
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
OLD_SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json",
    ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json",
]
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
COLLECTION_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json"
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

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def binding(path: Path, role: str) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path), "role": role}

def identity(url: str) -> tuple[str, str, str, str, str]:
    parsed = urlsplit(url)
    scheme = parsed.scheme.casefold()
    host = (parsed.hostname or "").casefold()
    port = parsed.port
    if (scheme, port) in {("http", 80), ("https", 443)}:
        port = None
    netloc = host if port is None else f"{host}:{port}"
    return (scheme, netloc, parsed.path, parsed.query, parsed.fragment)

def source_items(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"{rel(path)} has no items list")
    return [item for item in items if isinstance(item, dict)]

def existing_primary_originals() -> set[tuple[str, str, str, str, str]]:
    originals: set[tuple[str, str, str, str, str]] = set()
    # Fresh input must not duplicate any of the frozen 162 v23 overlays, even
    # when an older item came through a supplement map rather than primary.
    for path in [*BASE_PRIMARY_MAPS, *OLD_SUPPLEMENT_MAPS]:
        for item in source_items(path):
            original = str(item.get("original") or item.get("logical_url") or "")
            if original:
                originals.add(identity(original))
    return originals

def valid_url(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname == "www.worldofwarcraft.com"
        and bool(parsed.path)
    )

def raw_path(item: dict[str, Any]) -> Path:
    for key in ("accepted_raw_body", "raw_body", "source_payload", "private_payload_path"):
        value = item.get(key)
        if value:
            path = Path(str(value))
            if not path.is_absolute():
                path = ROOT / path
            if path.is_file():
                return path.resolve()
    raise RuntimeError(f"accepted news item has no local raw payload: {item.get('original')!r}")

def validate_baseline() -> dict[str, Any]:
    required = [
        V23_PROVENANCE, V23_ACCEPTANCE, V23_WORKER, V23_PREP, SOURCE_MANIFEST,
        *BASE_PRIMARY_MAPS, *OLD_SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP, COLLECTION_MAP,
    ]
    for path in required:
        if not path.is_file():
            raise RuntimeError(f"v23 frozen input missing: {path}")
    acceptance = read_json(V23_ACCEPTANCE)
    stats = acceptance.get("stats") or {}
    checks = {
        "accepted": acceptance.get("accepted") is True,
        "checked_declared_files": acceptance.get("checked_declared_files") == 8620,
        "actual_files": acceptance.get("actual_files") == 8621,
        "source_records": stats.get("source_records") == 8357,
        "image_overlay_records": stats.get("image_overlay_records") == 162,
        "primary_image_overlay_records": stats.get("primary_image_overlay_records") == 100,
        "supplement_image_overlay_records": stats.get("supplement_image_overlay_records") == 62,
        "guide_preview_count": stats.get("guide_preview_count") == 22,
        "guide_preview_gallery_pages": stats.get("guide_preview_gallery_pages") == 6,
        "guide_image_collection_images": stats.get("guide_image_collection_images") == 32,
        "guide_image_collection_pages": stats.get("guide_image_collection_pages") == 6,
    }
    if not all(checks.values()):
        raise RuntimeError(f"v23 acceptance gate changed: {checks}")
    provenance = read_json(V23_PROVENANCE)
    if provenance.get("source_manifest_sha256") != "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002":
        raise RuntimeError("v23 provenance source15 binding changed")
    return {
        "checks": checks,
        "v23_provenance": binding(V23_PROVENANCE, "frozen v23 export provenance"),
        "v23_acceptance": binding(V23_ACCEPTANCE, "root accepted v23 export"),
        "v23_worker": binding(V23_WORKER, "frozen v23 worker receipt"),
        "v23_preflight": binding(V23_PREP, "frozen v23 input preflight"),
        "source_manifest": binding(SOURCE_MANIFEST, "frozen source15 manifest"),
        "base_primary_maps": [binding(path, "frozen v23 primary map") for path in BASE_PRIMARY_MAPS],
        "old_supplement_maps": [binding(path, "frozen v23 supplement map") for path in OLD_SUPPLEMENT_MAPS],
        "guide_preview_map": binding(GUIDE_PREVIEW_MAP, "frozen v23 guide preview map"),
        "collection_map": binding(COLLECTION_MAP, "frozen v23 guide collection map"),
        "base_primary_item_counts": [len(source_items(path)) for path in BASE_PRIMARY_MAPS],
        "base_and_supplement_original_count": len(existing_primary_originals()),
    }
def accepted_items(receipt: dict[str, Any], receipt_path: Path) -> list[dict[str, Any]]:
    if receipt.get("accepted") is not True:
        raise RuntimeError(f"{rel(receipt_path)} exists but accepted is not true")
    raw_items = receipt.get("accepted_images")
    if not isinstance(raw_items, list):
        raise RuntimeError(f"{rel(receipt_path)} has no accepted_images list")
    originals: set[tuple[str, str, str, str, str]] = set()
    existing = existing_primary_originals()
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise RuntimeError(f"{rel(receipt_path)} accepted_images[{index}] is not an object")
        original = str(raw.get("original") or raw.get("logical_url") or "")
        if not valid_url(original):
            raise RuntimeError(f"{rel(receipt_path)} accepted_images[{index}] has invalid origin: {original!r}")
        key = identity(original)
        if key in originals or key in existing:
            raise RuntimeError(f"accepted news image overlaps existing primary map: {original}")
        originals.add(key)
        actual = str(raw.get("actual_timestamp") or raw.get("actual_capture_timestamp") or "")
        indexed = str(raw.get("indexed_capture_timestamp") or actual)
        if not re.fullmatch(r"\d{14}", actual) or indexed != actual:
            raise RuntimeError(f"accepted news timestamp invalid: {original}: {actual}/{indexed}")
        if actual[:4] != "2008" or actual > ANCHOR:
            raise RuntimeError(f"accepted news image is not baseline 2008 primary: {original}: {actual}")
        payload = raw_path(raw)
        data = payload.read_bytes()
        declared_sha = str(raw.get("sha256") or raw.get("accepted_raw_body_sha256") or "").casefold()
        declared_length = int(raw.get("length", len(data)))
        actual_sha = hashlib.sha256(data).hexdigest()
        if declared_sha != actual_sha or declared_length != len(data):
            raise RuntimeError(f"NEWS-CONTENT02 byte binding mismatch: {original}")
        clone = dict(raw)
        clone["accepted_raw_body"] = rel(payload)
        clone["accepted_raw_body_sha256"] = actual_sha
        clone["actual_timestamp"] = actual
        clone["indexed_capture_timestamp"] = indexed
        clone["kind"] = "image"
        clone["original"] = original
        clone["logical_url"] = str(raw.get("logical_url") or original)
        clone["sha256"] = actual_sha
        clone["length"] = len(data)
        clone["temporal_class"] = "baseline_2008"
        clone["source_acceptance_path"] = rel(receipt_path)
        result.append(clone)
    if not result:
        raise RuntimeError(f"{rel(receipt_path)} accepted_images is empty")
    return result

def copy_assets_and_write_map(
    items: list[dict[str, Any]],
    target_map: Path,
    asset_dir: Path,
    mode: str,
) -> dict[str, Any]:
    if target_map.exists():
        raise RuntimeError(f"refusing to overwrite existing v24 {mode} map: {target_map}")
    asset_dir.mkdir(parents=True, exist_ok=True)
    out_items: list[dict[str, Any]] = []
    total_bytes = 0
    for index, item in enumerate(items, start=1):
        source = ROOT / item["accepted_raw_body"]
        stem = Path(urlsplit(item["original"]).path).name or f"news-{index:02d}.img"
        receipt_tag = Path(str(item.get("source_acceptance_path") or "content02")).stem.replace("root-news-", "")
        target = asset_dir / f"{index:02d}-{receipt_tag}-{stem}"
        data = source.read_bytes()
        if target.exists():
            if target.read_bytes() != data:
                raise RuntimeError(f"refusing asset collision with different bytes: {target}")
        else:
            target.write_bytes(data)
        mapped = dict(item)
        mapped["local_path"] = rel(target)
        mapped["source_relationship"] = (
            f"Root-accepted {receipt_tag} baseline-2008 image; copied byte-for-byte "
            "and appended after frozen v23 primary map inputs."
        )
        out_items.append(mapped)
        total_bytes += len(data)
    map_payload = {
        "schema_version": "wow-recovery.integration.v24.fresh-news-source-map.v2",
        "kind": "wow_news_v24_fresh_news_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": True,
        "anchor_timestamp": ANCHOR,
        "copy_rule": f"Only root-accepted NEWS-CONTENT02/03 accepted_images are copied for this {mode} map; source bytes are never re-encoded. This map contains no inherited v23 items.",
        "source_acceptances": [
            {
                "path": rel(path),
                "sha256": sha256(path),
                "accepted_count": sum(1 for item in out_items if item.get("source_acceptance_path") == rel(path)),
                "total_image_bytes": sum(int(item["length"]) for item in out_items if item.get("source_acceptance_path") == rel(path)),
            }
            for path in (RECEIPT, OPTIONAL_RECEIPT)
            if any(item.get("source_acceptance_path") == rel(path) for item in out_items)
        ],
        "source_map": (
            {"path": rel(SOURCE_MAP), "sha256": sha256(SOURCE_MAP)}
            if SOURCE_MAP.is_file() else {"path": rel(SOURCE_MAP), "present": False}
        ),
        "inherited_v23_primary_maps": [
            {"path": rel(path), "sha256": sha256(path), "item_count": len(source_items(path))}
            for path in BASE_PRIMARY_MAPS
        ],
        "items": out_items,
    }
    target_map.write_text(json.dumps(map_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "map": binding(target_map, f"new v24 {mode} fresh-news primary map"),
        "asset_directory": rel(asset_dir),
        "asset_count": len(out_items),
        "asset_bytes": total_bytes,
        "asset_sha256s": [item["sha256"] for item in out_items],
    }
def main() -> int:
    baseline = validate_baseline()
    common = {
        "schema": "wow-recovery.integration.v24.input-preparation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "prepared_utc": now(),
        "network_requests": 0,
        "export_executed": False,
        "source15_manifest": baseline["source_manifest"],
        "v23_provenance": baseline["v23_provenance"],
        "v23_acceptance": baseline["v23_acceptance"],
        "v23_expected": {
            "declared_files": 8620,
            "actual_files": 8621,
            "primary_overlays": 100,
            "supplement_overlays": 62,
            "total_overlays": 162,
            "guide_preview_groups": 6,
            "guide_preview_images": 22,
            "guide_collection_groups": 3,
            "guide_collection_images": 32,
            "source_records": 8357,
        },
        "future_output_rule": "Expected v24 declared/actual files are 8620+N/8621+N, where N is the count of accepted NEWS-CONTENT02 plus optional NEWS-CONTENT03 baseline primary images.",
        "primary_map_order": [rel(path) for path in BASE_PRIMARY_MAPS] + [rel(FINAL_MAP)],
        "supplement_map_order": [rel(path) for path in OLD_SUPPLEMENT_MAPS],
        "fresh_map": rel(FINAL_MAP),
        "fresh_asset_directory": rel(FINAL_ASSET_DIR),
        "root_acceptance_required": [rel(RECEIPT), rel(OPTIONAL_RECEIPT)],
        "root_acceptance_sha256": {
            rel(path): sha256(path) for path in (RECEIPT, OPTIONAL_RECEIPT) if path.is_file()
        },
        "baseline_input_bindings": baseline,
    }
    if not RECEIPT.is_file():
        common.update({
            "status": "pending_root_news_content02_acceptance",
            "new_item_count": None,
            "new_image_bytes": None,
            "map_created": False,
            "assets_created": False,
            "reason": "NEWS-CONTENT02 root acceptance receipt is absent; no unaccepted payload is used.",
        })
        PROVISIONAL_PLAN.write_text(json.dumps(common, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": common["status"], "plan": rel(PROVISIONAL_PLAN), "network_requests": 0, "export_executed": False}, ensure_ascii=False, sort_keys=True))
        return 0
    receipt = read_json(RECEIPT)
    if receipt.get("accepted") is not True:
        common.update({
            "status": "pending_root_news_content02_acceptance",
            "new_item_count": None,
            "map_created": False,
            "assets_created": False,
            "reason": "NEWS-CONTENT02 receipt exists but is not accepted; no map/assets written.",
        })
        PROVISIONAL_PLAN.write_text(json.dumps(common, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": common["status"], "plan": rel(PROVISIONAL_PLAN), "network_requests": 0, "export_executed": False}, ensure_ascii=False, sort_keys=True))
        return 0
    if shutil.disk_usage(OUT).free < MIN_FREE_BYTES:
        raise RuntimeError("disk free below floor before v24 input preparation")
    content02 = accepted_items(receipt, RECEIPT)
    content03_receipt = read_json(OPTIONAL_RECEIPT) if OPTIONAL_RECEIPT.is_file() else None
    content03 = []
    if content03_receipt is not None and content03_receipt.get("accepted") is True:
        content03 = accepted_items(content03_receipt, OPTIONAL_RECEIPT)
    seen: set[tuple[str, str, str, str, str]] = set()
    for item in content02 + content03:
        key = identity(str(item["original"]))
        if key in seen:
            raise RuntimeError(f"NEWS-CONTENT02/03 duplicate original: {item['original']}")
        seen.add(key)
    final_ready = bool(content03_receipt and content03_receipt.get("accepted") is True)
    items = content02 + content03 if final_ready else content02
    target_map = FINAL_MAP if final_ready else PROVISIONAL_MAP
    asset_dir = FINAL_ASSET_DIR if final_ready else PROVISIONAL_ASSET_DIR
    plan_path = FINAL_PLAN if final_ready else PROVISIONAL_PLAN
    mode = "final" if final_ready else "content02-provisional"
    copy_result = copy_assets_and_write_map(items, target_map, asset_dir, mode)
    common.update({
        "status": "accepted_news_content02_content03_inputs_prepared" if final_ready else "accepted_news_content02_provisional_inputs_prepared",
        "new_item_count": len(items),
        "new_image_bytes": sum(int(item["length"]) for item in items),
        "map_created": True,
        "assets_created": True,
        "source_acceptances": [
            binding(RECEIPT, "root accepted NEWS-CONTENT02 source receipt")
        ] + ([binding(OPTIONAL_RECEIPT, "root accepted NEWS-CONTENT03 source receipt")] if final_ready else []),
        "optional_content03": {
            "path": rel(OPTIONAL_RECEIPT),
            "present": OPTIONAL_RECEIPT.is_file(),
            "accepted": bool(content03_receipt and content03_receipt.get("accepted") is True),
            "sha256": sha256(OPTIONAL_RECEIPT) if OPTIONAL_RECEIPT.is_file() else None,
        },
        "copy_result": copy_result,
        "expected_output_counts": {
            "declared_files": 8620 + len(items),
            "actual_files": 8621 + len(items),
            "primary_overlays": 100 + len(items),
            "supplement_overlays": 62,
            "total_overlays": 162 + len(items),
        },
        "mode": mode,
        "provisional_map": rel(PROVISIONAL_MAP),
        "final_map": rel(FINAL_MAP),
    })
    plan_path.write_text(json.dumps(common, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": common["status"],
        "plan": rel(plan_path),
        "map": rel(target_map),
        "new_item_count": len(items),
        "new_image_bytes": common["new_image_bytes"],
        "network_requests": 0,
        "export_executed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
