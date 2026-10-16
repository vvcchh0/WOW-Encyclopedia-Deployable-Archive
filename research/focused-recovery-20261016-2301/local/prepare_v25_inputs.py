#!/usr/bin/env python3
"""Prepare v25 neighbor copies/maps after root accepts the future receipt.

This is deliberately not run until the named root acceptance receipt exists.
It reads local payloads only, copies bytes into this owned directory, and
creates new supplement/collection maps without changing any frozen map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
LOCAL = Path(__file__).resolve().parent
DEFAULT_RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-neighbors9-source-acceptance.json"
BASE_COLLECTION = ROOT / "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json"
V24_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v24/export-provenance.json"
ASSET_DIR = LOCAL / "accepted-images/v25-neighbors"
NEW_SUPPLEMENT_MAP = LOCAL / "v25-neighbor-supplement-source-map.json"
NEW_COLLECTION_MAP = LOCAL / "v25-guide-image-collection-map.json"
PREP_RECEIPT = LOCAL / "v25-input-preparation.json"
ANCHOR = "20080512210044"
GROUPS = {"love-is-in-the-air", "lunar-festival", "world-pvp"}


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


def capture(item: dict) -> str:
    value = str(item.get("actual_timestamp") or item.get("actual_capture_timestamp") or item.get("capture_timestamp") or "")
    if not re.fullmatch(r"\d{14}", value):
        raise RuntimeError(f"invalid actual timestamp: {value!r}")
    datetime.strptime(value, "%Y%m%d%H%M%S")
    return value


def temporal_class(value: str) -> str:
    actual = datetime.strptime(value, "%Y%m%d%H%M%S")
    anchor = datetime.strptime(ANCHOR, "%Y%m%d%H%M%S")
    if actual < datetime(2008, 1, 1):
        return "pre_2008"
    if actual <= anchor:
        return "baseline_2008"
    if actual <= datetime(2008, 12, 31, 23, 59, 59):
        return "late_2008"
    return "post_2008"


def original(item: dict) -> str:
    value = str(item.get("original") or item.get("logical_url") or "")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or (parsed.hostname or "").casefold().rstrip(".") != "www.worldofwarcraft.com":
        raise RuntimeError(f"unapproved neighbor origin: {value}")
    if parsed.query or parsed.fragment or parsed.username or parsed.password or "\\" in parsed.path or ".." in parsed.path.split("/"):
        raise RuntimeError(f"unsafe neighbor original: {value}")
    if parsed.port not in {None, 80, 443}:
        raise RuntimeError(f"non-default neighbor port: {value}")
    if not parsed.path.startswith("/") or not parsed.path.casefold().endswith((".jpg", ".jpeg", ".gif", ".png")):
        raise RuntimeError(f"unsupported neighbor image path: {value}")
    return value


def payload_path(item: dict) -> Path:
    for key in ("local_path", "private_payload_path", "accepted_raw_body", "payload_path"):
        raw = item.get(key)
        if raw:
            path = (ROOT / str(raw)).resolve()
            try:
                path.relative_to(ROOT.resolve())
            except ValueError as exc:
                raise RuntimeError(f"payload escapes workspace: {raw}") from exc
            if path.is_file():
                return path
    raise RuntimeError("accepted neighbor has no existing local payload path")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--go", action="store_true", help="write owned copies and maps after the root receipt is accepted")
    args = parser.parse_args(argv)
    if not args.go:
        print(json.dumps({"status": "prepared_only", "receipt": rel(args.receipt.resolve()), "writes": False}, ensure_ascii=False))
        return 0
    if ASSET_DIR.exists() or NEW_SUPPLEMENT_MAP.exists() or NEW_COLLECTION_MAP.exists() or PREP_RECEIPT.exists():
        raise RuntimeError("refusing to overwrite existing v25 local preparation outputs")
    receipt_path = args.receipt.resolve()
    receipt = read(receipt_path, "root neighbors9 source acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("future root neighbors9 source acceptance is not accepted")
    accepted = receipt.get("accepted_images")
    if not isinstance(accepted, list) or not accepted:
        raise RuntimeError("future root neighbors9 receipt has no accepted_images")
    prior = read(V24_PROVENANCE, "v24 provenance")
    old_originals = {str(item.get("original_url") or "") for item in prior.get("files", []) if item.get("role") == "image_overlay"}
    old_routes = {str(item.get("route") or "") for item in prior.get("files", []) if item.get("role") == "image_overlay"}
    ASSET_DIR.mkdir(parents=True, exist_ok=False)
    map_items: list[dict] = []
    collection_items: list[dict] = []
    copied: list[dict] = []
    for index, raw in enumerate(accepted, start=1):
        if not isinstance(raw, dict) or raw.get("accepted") is not True:
            raise RuntimeError(f"accepted_images[{index - 1}] is not accepted")
        logical = original(raw)
        if logical in old_originals:
            raise RuntimeError(f"neighbor original already exists in v24 overlays: {logical}")
        route = urlsplit(logical).path
        if route in old_routes:
            raise RuntimeError(f"neighbor route already exists in v24 overlays: {route}")
        source = payload_path(raw)
        expected_sha = str(raw.get("sha256") or "").casefold()
        expected_length = int(raw.get("length", -1))
        if sha(source) != expected_sha or source.stat().st_size != expected_length:
            raise RuntimeError(f"accepted neighbor payload SHA/length mismatch: {logical}")
        suffix = Path(urlsplit(logical).path).suffix.casefold()
        destination = ASSET_DIR / f"{index:02d}-neighbor{suffix}"
        shutil.copyfile(source, destination)
        if sha(destination) != expected_sha or destination.stat().st_size != expected_length:
            raise RuntimeError(f"copied neighbor bytes changed: {logical}")
        actual = capture(raw)
        indexed = str(raw.get("indexed_capture_timestamp") or actual)
        if indexed != actual:
            raise RuntimeError(f"neighbor actual/indexed timestamps differ: {logical}")
        classification = temporal_class(actual)
        item = {
            "kind": "image",
            "logical_url": logical,
            "original": logical,
            "actual_timestamp": actual,
            "indexed_capture_timestamp": indexed,
            "mime": str(raw.get("mime") or ""),
            "dimensions": raw.get("dimensions"),
            "decoded_frames": raw.get("decoded_frames"),
            "length": expected_length,
            "sha256": expected_sha,
            "cdx_digest": raw.get("cdx_digest"),
            "local_path": rel(destination),
            "temporal_class": classification,
            "source_acceptance_path": rel(receipt_path),
            "source_relationship": "Root-accepted neighbor retry payload; explicit v25 supplement overlay; copied byte-for-byte.",
        }
        map_items.append(item)
        if str(raw.get("catalog_role") or "") == "guide_image_collection_numeric_full" and str(raw.get("collection_group") or "") in GROUPS:
            collection_items.append({
                "actual_capture_timestamp": actual,
                "length": expected_length,
                "original": logical,
                "route": route,
                "sha256": expected_sha,
                "source_acceptance_path": rel(receipt_path),
            })
        copied.append({"original": logical, "route": route, "path": rel(destination), "sha256": expected_sha, "length": expected_length, "temporal_class": classification})

    source_binding = {"path": rel(receipt_path), "sha256": sha(receipt_path)}
    supplement_map = {
        "accepted": True,
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Each local_path is copied byte-for-byte from a root-accepted payload; the exporter verifies SHA-256, length, MIME, timestamp, and CDX digest.",
        "items": map_items,
        "kind": "wow_gallery_neighbors_v25_supplement",
        "purpose": "Only the newly accepted v25 neighbor retry images; no v24 item is duplicated.",
        "role": "related_site_image_supplement",
        "schema_version": 1,
        "source_acceptance": source_binding,
    }
    base_collection = read(BASE_COLLECTION, "v23 collection map")
    if base_collection.get("schema") != "wow-recovery.guide-image-collections.v1":
        raise RuntimeError("v23 collection map schema changed")
    collection = json.loads(json.dumps(base_collection))
    collection["purpose"] = "v25 clone of the accepted three guide-image collections with only root-accepted neighbor retry images appended."
    collection.setdefault("source_acceptances", []).append(source_binding)
    for added in collection_items:
        group_id = next((str(item.get("collection_group")) for item in accepted if original(item) == added["original"]), None)
        group = next((group for group in collection.get("groups", []) if group.get("group_id") == group_id), None)
        if group is None:
            raise RuntimeError(f"collection group missing for {added['original']}")
        if any(item.get("route") == added["route"] for item in group.get("images", [])):
            raise RuntimeError(f"collection route duplicated in v23 map: {added['route']}")
        group.setdefault("images", []).append(added)

    NEW_SUPPLEMENT_MAP.write_text(json.dumps(supplement_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    NEW_COLLECTION_MAP.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "schema": "wow-recovery.focused-recovery-20261016-2301.v25-input-preparation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "source_acceptance": source_binding,
        "accepted_count": len(accepted),
        "copied_count": len(copied),
        "copied_bytes": sum(item["length"] for item in copied),
        "collection_added_count": len(collection_items),
        "supplement_map": {"path": rel(NEW_SUPPLEMENT_MAP), "sha256": sha(NEW_SUPPLEMENT_MAP), "item_count": len(map_items)},
        "collection_map": {"path": rel(NEW_COLLECTION_MAP), "sha256": sha(NEW_COLLECTION_MAP), "group_count": len(collection.get("groups", [])), "image_count": sum(len(group.get("images", [])) for group in collection.get("groups", []))},
        "copied": copied,
        "network_requests": 0,
        "export_executed": False,
    }
    PREP_RECEIPT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "prepared", "accepted_count": len(accepted), "copied_bytes": report["copied_bytes"], "collection_added_count": len(collection_items), "supplement_map_sha256": report["supplement_map"]["sha256"], "collection_map_sha256": report["collection_map"]["sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
