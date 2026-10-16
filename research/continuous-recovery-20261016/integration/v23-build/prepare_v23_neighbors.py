#!/usr/bin/env python3
"""Prepare v23 gallery-neighbor supplement and collection inputs.

This is a local preflight only.  It copies the three root-accepted neighbor
receipts byte-for-byte, writes two explicit supplement maps plus the strict
three-group collection map, and runs the existing loaders against source15
and the frozen v22 inputs.  It never calls ``export_pages``.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
BUILD_DIR = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "research/continuous-recovery-20261016/integration/accepted-images/gallery-neighbors-v23"
NUMERIC_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map.json"
CATALOG_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map.json"
COLLECTION_MAP = ROOT / "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map.json"
RECEIPT = BUILD_DIR / "preflight-v23-neighbor-inputs.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
V22_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v22/export-provenance.json"
V22_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v22-export-acceptance.json"
CODE_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-guide-collections-code-acceptance.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
    # v22's 52-item map owns the inherited v20/v21 routes for this preflight.
    # The older maps remain after it only as frozen duplicate evidence.
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
]

NEIGHBOR_SPECS = [
    {
        "batch": "gallery-neighbors01",
        "receipt": ROOT / "research/continuous-recovery-20261016/publication/root-gallery-neighbors01-source-acceptance.json",
        "source_map": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors01/output/source-map.json",
        "plan": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors01/plan.json",
        "batch_report": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors01/output/batch-report.json",
    },
    {
        "batch": "gallery-neighbors02",
        "receipt": ROOT / "research/continuous-recovery-20261016/publication/root-gallery-neighbors02-source-acceptance.json",
        "source_map": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors02/output/source-map.json",
        "plan": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors02/plan.json",
        "batch_report": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors02/output/batch-report.json",
    },
    {
        "batch": "gallery-neighbors03",
        "receipt": ROOT / "research/continuous-recovery-20261016/publication/root-gallery-neighbors03-source-acceptance.json",
        "source_map": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors03/output/source-map.json",
        "plan": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors03/plan.json",
        "batch_report": ROOT / "research/continuous-recovery-20261016/network/gallery-neighbors03/output/batch-report.json",
    },
]

EXPECTED_FROZEN_HASHES = {
    ".scratch/offline-navigation-20261015-v15/build-manifest.json": "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002",
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9",
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33",
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77",
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581",
}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    return path


def require_hash(path: Path, expected: str, label: str) -> str:
    require_file(path, label)
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA changed: expected {expected}, got {actual}")
    return actual


def verify_frozen_inputs() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative, expected in EXPECTED_FROZEN_HASHES.items():
        hashes[relative] = require_hash(ROOT / relative, expected, relative)
    require_file(V22_PROVENANCE, "v22 export provenance")
    require_file(V22_EXPORT_ACCEPTANCE, "v22 export acceptance")
    require_file(CODE_ACCEPTANCE, "guide collection code acceptance")
    v22_acceptance = read_json(V22_EXPORT_ACCEPTANCE)
    if v22_acceptance.get("accepted") is not True:
        raise RuntimeError("v22 export acceptance is not accepted")
    stats = v22_acceptance.get("stats") or {}
    if stats.get("image_overlay") != 122 or stats.get("primary_image_overlay_records") != 100 or stats.get("supplement_image_overlay_records") != 22:
        raise RuntimeError(f"v22 overlay stats changed: {stats}")
    if v22_acceptance.get("checked_declared_files") != 8580 or v22_acceptance.get("actual_files") != 8581:
        raise RuntimeError("v22 file counts changed")
    code = read_json(CODE_ACCEPTANCE)
    if code.get("accepted") is not True or code.get("export_authorized") is not False:
        raise RuntimeError("guide collection code acceptance gate changed")
    hashes[rel(V22_PROVENANCE)] = sha256(V22_PROVENANCE)
    hashes[rel(V22_EXPORT_ACCEPTANCE)] = sha256(V22_EXPORT_ACCEPTANCE)
    hashes[rel(CODE_ACCEPTANCE)] = sha256(CODE_ACCEPTANCE)
    return hashes


def verify_image(data: bytes, accepted: dict[str, Any], *, label: str) -> dict[str, Any]:
    expected_length = int(accepted["length"])
    expected_sha = str(accepted["sha256"]).casefold()
    if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
        raise RuntimeError(f"{label} SHA/length mismatch")
    digest = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")
    if digest != str(accepted.get("cdx_digest") or "").upper():
        raise RuntimeError(f"{label} CDX digest mismatch")
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            detected = image.format
            dimensions = list(image.size)
            frames = int(getattr(image, "n_frames", 1))
            for frame_index in range(frames):
                image.seek(frame_index)
                image.convert("RGBA").load()
    except Exception as exc:
        raise RuntimeError(f"{label} Pillow verification failed") from exc
    expected_format = {"image/jpeg": "JPEG", "image/gif": "GIF", "image/png": "PNG"}.get(str(accepted.get("mime") or "").casefold())
    if expected_format and detected != expected_format:
        raise RuntimeError(f"{label} Pillow format mismatch: {detected!r} != {expected_format!r}")
    if dimensions != list(accepted.get("dimensions") or []) or frames != int(accepted.get("decoded_frames") or 0):
        raise RuntimeError(f"{label} Pillow dimension/frame mismatch: {dimensions}/{frames}")
    return {"format": detected, "dimensions": dimensions, "decoded_frames": frames, "all_frames_decoded": True}


def temporal_class(timestamp: str) -> str:
    value = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    anchor = datetime.strptime(ANCHOR, "%Y%m%d%H%M%S")
    if value < datetime(2008, 1, 1):
        return "pre_2008"
    if value <= anchor:
        return "baseline_2008"
    if value <= datetime(2008, 12, 31, 23, 59, 59):
        return "late_2008"
    return "post_2008"


def classify_original(original: str) -> tuple[str | None, int | None]:
    path = urlsplit(original).path
    patterns = {
        "love-is-in-the-air": r"^/info/events/loveisintheair/images/ss(\d+)\.jpg$",
        "lunar-festival": r"^/info/events/lunarnewyears/images/ss(\d+)\.jpg$",
        "world-pvp": r"^/pvp/worldpvp/images/ss(\d+)\.jpg$",
    }
    for group_id, pattern in patterns.items():
        match = re.fullmatch(pattern, path)
        if match:
            return group_id, int(match.group(1))
    return None, None


def source_acceptance_record(spec: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    receipt = spec["receipt"]
    return {
        "path": rel(receipt),
        "sha256": sha256(receipt),
        "accepted": document.get("accepted"),
        "accepted_count": len(document.get("accepted_images") or []),
        "total_image_bytes": document.get("image_bytes"),
        "checked_utc": document.get("checked_utc"),
        "plan_sha256": document.get("plan_sha256"),
        "batch_report_sha256": document.get("batch_report_sha256"),
    }


def prepare_records() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    if ASSET_DIR.exists():
        raise RuntimeError(f"refusing to reuse existing asset directory: {ASSET_DIR}")
    for path in (NUMERIC_MAP, CATALOG_MAP, COLLECTION_MAP, RECEIPT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite existing preflight file: {path}")
    ASSET_DIR.mkdir(parents=True, exist_ok=False)
    all_records: list[dict[str, Any]] = []
    by_original: dict[str, dict[str, Any]] = {}
    acceptance_summary: list[dict[str, Any]] = []
    source_map_summary: list[dict[str, Any]] = []
    for spec in NEIGHBOR_SPECS:
        receipt = spec["receipt"]
        source_map = spec["source_map"]
        plan = spec["plan"]
        batch_report = spec["batch_report"]
        receipt_doc = read_json(receipt)
        if receipt_doc.get("accepted") is not True:
            raise RuntimeError(f"root receipt is not accepted: {receipt}")
        receipt_items = receipt_doc.get("accepted_images")
        if not isinstance(receipt_items, list):
            raise RuntimeError(f"accepted_images missing: {receipt}")
        source_doc = read_json(source_map)
        source_items = source_doc.get("accepted_payloads")
        if not isinstance(source_items, list):
            raise RuntimeError(f"accepted_payloads missing: {source_map}")
        source_by_original = {str(item.get("original")): (index, item) for index, item in enumerate(source_items)}
        if len(source_by_original) != len(source_items):
            raise RuntimeError(f"duplicate source-map original in {source_map}")
        if sha256(plan) != str(receipt_doc.get("plan_sha256") or ""):
            raise RuntimeError(f"plan SHA mismatch for {receipt}")
        if sha256(batch_report) != str(receipt_doc.get("batch_report_sha256") or ""):
            raise RuntimeError(f"batch-report SHA mismatch for {receipt}")
        acceptance_summary.append(source_acceptance_record(spec, receipt_doc))
        source_map_summary.append({
            "batch": spec["batch"],
            "path": rel(source_map),
            "sha256": sha256(source_map),
            "batch_id": source_doc.get("batch_id"),
            "accepted_payload_count": len(source_items),
        })
        for receipt_index, accepted in enumerate(receipt_items):
            original = str(accepted.get("original") or "")
            if not original or original in by_original:
                raise RuntimeError(f"duplicate or missing accepted original: {original!r}")
            source_index, source_item = source_by_original.get(original, (None, None))
            if source_item is None:
                raise RuntimeError(f"root receipt original absent from source map: {original}")
            source_path = ROOT / str(accepted.get("private_payload_path") or "")
            source_map_payload_path = ROOT / str(source_item.get("private_decoded_payload_path") or "")
            if source_path.resolve() != source_map_payload_path.resolve():
                raise RuntimeError(f"receipt/source-map payload path mismatch: {original}")
            if source_item.get("decoded_body_sha256") != accepted.get("sha256") or int(source_item.get("decoded_body_bytes")) != int(accepted.get("length")):
                raise RuntimeError(f"receipt/source-map byte metadata mismatch: {original}")
            if source_item.get("selected_capture_timestamp") != accepted.get("actual_capture_timestamp"):
                raise RuntimeError(f"receipt/source-map capture mismatch: {original}")
            if source_item.get("cdx_digest") != accepted.get("cdx_digest"):
                raise RuntimeError(f"receipt/source-map digest mismatch: {original}")
            require_file(source_path, f"accepted payload {original}")
            data = source_path.read_bytes()
            group_id, number = classify_original(original)
            is_collection = group_id is not None
            output_name = f"{len(all_records) + 1:02d}-{'collection' if is_collection else 'catalog'}-{Path(urlsplit(original).path).name}"
            destination = ASSET_DIR / output_name
            pillow = verify_image(data, accepted, label=original)
            destination.write_bytes(data)
            if destination.read_bytes() != data:
                raise RuntimeError(f"copy verification failed: {destination}")
            actual_timestamp = str(accepted["actual_capture_timestamp"])
            item = {
                "kind": "image",
                "logical_url": original,
                "original": original,
                "local_path": rel(destination),
                "mime": accepted["mime"],
                "sha256": str(accepted["sha256"]).casefold(),
                "length": int(accepted["length"]),
                "actual_timestamp": actual_timestamp,
                "indexed_capture_timestamp": actual_timestamp,
                "cdx_digest": str(accepted["cdx_digest"]).upper(),
                "temporal_class": temporal_class(actual_timestamp),
                "dimensions": list(accepted["dimensions"]),
                "decoded_frames": int(accepted["decoded_frames"]),
                "source_relationship": (
                    "Root-accepted numeric full neighbor image; explicit supplement overlay and guide-image collection input; copied byte-for-byte."
                    if is_collection
                    else "Root-accepted neighbor thumbnail/model image; ordinary supplement catalog only; never a numeric full gallery collection image."
                ),
                "catalog_role": "guide_image_collection_numeric_full" if is_collection else "ordinary_supplement_catalog_only",
                "collection_group": group_id,
                "collection_number": number,
                "source_acceptance_path": rel(receipt),
                "acceptance_record": f"{rel(receipt)}#accepted_images[{receipt_index}]",
                "accepted_raw_body": rel(source_path),
                "accepted_raw_body_sha256": str(accepted["sha256"]).casefold(),
                "source_map_record": f"{rel(source_map)}#accepted_payloads[{source_index}]",
                "source_map_sha256": sha256(source_map),
                "source_evidence": {
                    "root_receipt_sha256": sha256(receipt),
                    "root_receipt_checked_utc": receipt_doc.get("checked_utc"),
                    "plan_sha256": receipt_doc.get("plan_sha256"),
                    "batch_report_sha256": receipt_doc.get("batch_report_sha256"),
                    "source_map_sha256": sha256(source_map),
                    "source_map_batch_id": source_doc.get("batch_id"),
                    "source_map_entry_index": source_index,
                    "source_map_status": source_item.get("status"),
                    "selected_capture_timestamp": source_item.get("selected_capture_timestamp"),
                    "actual_memento_timestamp": source_item.get("actual_memento_timestamp"),
                    "cdx_record_length": source_item.get("cdx_record_length"),
                    "replay_body_sha256": source_item.get("decoded_body_sha256"),
                    "replay_body_length": source_item.get("decoded_body_bytes"),
                },
                "preflight_pillow": pillow,
            }
            all_records.append(item)
            by_original[original] = item
    if len(all_records) != 30 or sum(int(item["length"]) for item in all_records) != 5188925:
        raise RuntimeError(f"neighbor conservation changed: count={len(all_records)} bytes={sum(int(item['length']) for item in all_records)}")
    return all_records, by_original, {
        "acceptance_records": acceptance_summary,
        "source_map_records": source_map_summary,
    }


def build_map_payload(items: list[dict[str, Any]], *, kind: str, purpose: str, acceptance_summary: list[dict[str, Any]], source_map_summary: list[dict[str, Any]]) -> dict[str, Any]:
    used_receipts = {str(item["source_acceptance_path"]) for item in items}
    used_sources = {str(item["source_map_record"]).split("#", 1)[0] for item in items}
    return {
        "schema_version": 1,
        "kind": kind,
        "accepted": True,
        "role": "related_site_image_supplement",
        "purpose": purpose,
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {
            "records": [record for record in acceptance_summary if record["path"] in used_receipts],
            "accepted_count": len(items),
            "total_image_bytes": sum(int(item["length"]) for item in items),
        },
        "source_maps": [record for record in source_map_summary if record["path"] in used_sources],
        "copy_rule": "Each local_path is a byte-for-byte copy of the root-accepted decoded replay body; SHA-256, length, CDX digest, MIME, dimensions, and all decoded frames are checked before and after copy.",
        "items": items,
    }


def build_collection_map(items: list[dict[str, Any]], acceptance_summary: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {
        "love-is-in-the-air": ("Love is in the Air", "/info/events/loveisintheair/index.html", "/info/events/loveisintheair/gallery.html"),
        "lunar-festival": ("Lunar Festival", "/info/events/lunarnewyears/index.html", "/info/events/lunarnewyears/gallery.html"),
        "world-pvp": ("World PvP", "/pvp/worldpvp/index.xml", "/pvp/worldpvp/worldpvp-gallery.html"),
    }
    groups: list[dict[str, Any]] = []
    collection_items = [item for item in items if item.get("collection_group")]
    if len(collection_items) != 24:
        raise RuntimeError(f"collection item count changed: {len(collection_items)}")
    for group_id, (label, guide_route, gallery_route) in expected.items():
        group_items = sorted(
            [item for item in collection_items if item["collection_group"] == group_id],
            key=lambda item: int(item["collection_number"]),
        )
        groups.append({
            "group_id": group_id,
            "label": label,
            "guide_route": guide_route,
            "gallery_route": gallery_route,
            "images": [
                {
                    "route": urlsplit(item["original"]).path,
                    "original": item["original"],
                    "sha256": item["sha256"],
                    "length": item["length"],
                    "actual_capture_timestamp": item["actual_timestamp"],
                    "source_acceptance_path": item["source_acceptance_path"],
                }
                for item in group_items
            ],
        })
    return {
        "schema": "wow-recovery.guide-image-collections.v1",
        "purpose": "v23 preflight only: 24 root-accepted numeric full neighbor images in the three fixed guide-image collections; ordinary thumb/model catalog items are excluded.",
        "source_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256(SOURCE_MANIFEST)},
        "anchor_timestamp": ANCHOR,
        "source_acceptances": [
            {"path": record["path"], "sha256": record["sha256"]}
            for record in acceptance_summary
        ],
        "groups": groups,
    }


def make_route_to_static(manifest: dict[str, Any], primary: list[dict[str, Any]], supplement: list[dict[str, Any]]) -> tuple[dict[str, str], set[str], set[str]]:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages

    route_to_static: dict[str, str] = {}
    frozen_routes: set[str] = set()
    frozen_static_paths: set[str] = set()
    for record in manifest.get("files") or []:
        route = export_github_pages.safe_route(str(record.get("route") or ""))
        relative = export_github_pages.static_rel_for_route(route, record)
        route_to_static[route] = export_github_pages.static_url(BASE_PATH, relative)
        frozen_routes.add(route)
        frozen_static_paths.add(relative)
    for alias in manifest.get("route_aliases") or {}:
        frozen_routes.add(str(alias))
    for item in [*primary, *supplement]:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    return route_to_static, frozen_routes, frozen_static_paths


def run_loader_preflight(manifest: dict[str, Any], numeric_map: Path, catalog_map: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    import guide_image_collections
    import guide_previews

    # This order preserves the v22 route order while assigning all 52 cloned
    # routes to v22-primary before the frozen v20/v21 duplicate evidence.
    primary, primary_bytes = export_github_pages.load_image_overlays(
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes={str(item.get("route")) for item in manifest.get("files") or []} | {str(alias) for alias in manifest.get("route_aliases") or {}},
        frozen_static_paths={export_github_pages.static_rel_for_route(str(item.get("route")), item) for item in manifest.get("files") or []},
    )
    route_to_static, frozen_routes, frozen_static_paths = make_route_to_static(manifest, primary, [])
    old_supplement, old_supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(OLD_SUPPLEMENT_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes | {str(item["route"]) for item in primary},
        frozen_static_paths=frozen_static_paths | {str(item["relative"]) for item in primary},
        allow_later_image_supplements=True,
    )
    route_to_static, _frozen_routes, _frozen_static_paths = make_route_to_static(manifest, primary, old_supplement)
    current_v22_routes = [str(item.get("route")) for item in (read_json(V22_PROVENANCE).get("files") or []) if item.get("role") == "image_overlay"]
    current_old_routes = [str(item["route"]) for item in [*primary, *old_supplement]]
    if current_old_routes != current_v22_routes:
        raise RuntimeError("corrected v23 old overlay route order differs from accepted v22 provenance")
    if len(primary) != 100 or len(old_supplement) != 22:
        raise RuntimeError(f"old v22 loader counts changed: primary={len(primary)} supplement={len(old_supplement)}")
    primary_identity_counts = Counter(rel(Path(item["map_path"])) for item in primary)
    if primary_identity_counts.get(rel(ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json")) != 52:
        raise RuntimeError(f"v22 primary map does not own 52 routes: {primary_identity_counts}")
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple([*OLD_SUPPLEMENT_MAPS, numeric_map, catalog_map]),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        # The complete list is loaded from its base frozen set; old routes are
        # intentionally not pre-added because they are inputs to this call.
        frozen_routes=frozen_routes | {str(item["route"]) for item in primary},
        frozen_static_paths=frozen_static_paths | {str(item["relative"]) for item in primary},
        allow_later_image_supplements=True,
    )
    route_to_static, _frozen_routes, _frozen_static_paths = make_route_to_static(manifest, primary, supplement)
    preview_bundle = guide_previews.load_guide_preview_map(
        GUIDE_PREVIEW_MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    collection_bundle = guide_image_collections.load_guide_image_collection_map(
        COLLECTION_MAP,
        workspace_root=ROOT,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        overlays=supplement,
        route_to_static=route_to_static,
        base_path=BASE_PATH,
    )
    if len(supplement) != 52 or collection_bundle.image_count != 24 or len(collection_bundle.groups) != 3:
        raise RuntimeError(f"new loader counts changed: supplement={len(supplement)} collections={collection_bundle.image_count}/{len(collection_bundle.groups)}")
    catalog_routes = {str(item["route"]) for item in supplement if str(item["map_path"]) == str(CATALOG_MAP.resolve())}
    collection_routes = {image.route for group in collection_bundle.groups for image in group.images}
    if catalog_routes & collection_routes:
        raise RuntimeError("ordinary catalog route entered guide collection")
    supplement_source_counts = Counter(rel(Path(item["map_path"])) for item in supplement)
    return {
        "old_v22_route_order_preserved": True,
        "old_v22_primary_overlay_records": len(primary),
        "old_v22_primary_overlay_bytes": primary_bytes,
        "old_v22_supplement_overlay_records": len(old_supplement),
        "old_v22_supplement_overlay_bytes": old_supplement_bytes,
        "new_supplement_overlay_records": len(supplement) - len(old_supplement),
        "new_supplement_overlay_bytes": supplement_bytes - old_supplement_bytes,
        "preflight_primary_overlay_records": len(primary),
        "preflight_supplement_overlay_records": len(supplement),
        "preflight_total_overlay_records": len(primary) + len(supplement),
        "preflight_total_overlay_bytes": primary_bytes + supplement_bytes,
        "primary_source_map_identity_counts": dict(primary_identity_counts),
        "supplement_source_map_identity_counts": dict(supplement_source_counts),
        "guide_preview_groups": len(preview_bundle.groups),
        "guide_preview_images": preview_bundle.preview_count,
        "guide_collection_groups": len(collection_bundle.groups),
        "guide_collection_images": collection_bundle.image_count,
        "guide_collection_group_counts": {group.group_id: len(group.images) for group in collection_bundle.groups},
        "catalog_only_images": len(catalog_routes),
        "network_requests": 0,
        "export_executed": False,
    }


def main() -> int:
    frozen_hashes = verify_frozen_inputs()
    manifest = read_json(SOURCE_MANIFEST)
    if str(manifest.get("anchor_timestamp") or "") != ANCHOR:
        raise RuntimeError("source15 anchor changed")
    records, _by_original, evidence = prepare_records()
    collection_items = [item for item in records if item.get("collection_group")]
    catalog_items = [item for item in records if not item.get("collection_group")]
    write_json(NUMERIC_MAP, build_map_payload(collection_items, kind="wow_gallery_neighbors_v23_numeric_full_supplement", purpose="24 numeric full images for the three guide-image collections; explicit supplement only.", acceptance_summary=evidence["acceptance_records"], source_map_summary=evidence["source_map_records"]))
    write_json(CATALOG_MAP, build_map_payload(catalog_items, kind="wow_gallery_neighbors_v23_catalog_supplement", purpose="One nested thumbnail and five model images kept as ordinary supplement catalog entries; excluded from the guide-image collection map.", acceptance_summary=evidence["acceptance_records"], source_map_summary=evidence["source_map_records"]))
    write_json(COLLECTION_MAP, build_collection_map(records, evidence["acceptance_records"]))
    loader = run_loader_preflight(manifest, NUMERIC_MAP, CATALOG_MAP)
    receipt = {
        "schema": "wow-recovery.integration.v23.neighbor-preflight.v1",
        "executed_by": "/root/local_recovery_20261016",
        "prepared_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "network_requests": 0,
        "export_executed": False,
        "source15_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256(SOURCE_MANIFEST), "anchor_timestamp": ANCHOR},
        "source_site": rel(SOURCE_SITE),
        "code_acceptance": {"path": rel(CODE_ACCEPTANCE), "sha256": sha256(CODE_ACCEPTANCE), "accepted": True, "export_authorized": False},
        "v22_export_acceptance": {"path": rel(V22_EXPORT_ACCEPTANCE), "sha256": sha256(V22_EXPORT_ACCEPTANCE), "accepted": True, "old_overlay_records": 122},
        "v22_provenance": {"path": rel(V22_PROVENANCE), "sha256": sha256(V22_PROVENANCE)},
        "frozen_input_hashes": frozen_hashes,
        "primary_map_order": [rel(path) for path in PRIMARY_MAPS],
        "primary_map_priority_rule": "v22-primary-news-source-map.json (52 items) is before frozen v20/v21 duplicate evidence; the 52 routes retain v22 source-map identity.",
        "old_supplement_map_order": [rel(path) for path in OLD_SUPPLEMENT_MAPS],
        "new_maps": {
            "numeric_full_supplement": {"path": rel(NUMERIC_MAP), "sha256": sha256(NUMERIC_MAP), "item_count": len(collection_items), "bytes": sum(int(item["length"]) for item in collection_items)},
            "ordinary_catalog_supplement": {"path": rel(CATALOG_MAP), "sha256": sha256(CATALOG_MAP), "item_count": len(catalog_items), "bytes": sum(int(item["length"]) for item in catalog_items)},
            "guide_image_collection": {"path": rel(COLLECTION_MAP), "sha256": sha256(COLLECTION_MAP), "item_count": len(collection_items), "group_count": 3},
        },
        "root_neighbor_acceptances": evidence["acceptance_records"],
        "root_neighbor_source_maps": evidence["source_map_records"],
        "copied_assets": {
            "directory": rel(ASSET_DIR),
            "count": len(records),
            "bytes": sum(int(item["length"]) for item in records),
            "byte_for_byte_and_sha_verified": True,
            "pillow_all_frames_verified": True,
            "items": [
                {
                    "original": item["original"],
                    "local_path": item["local_path"],
                    "sha256": item["sha256"],
                    "length": item["length"],
                    "dimensions": item["dimensions"],
                    "decoded_frames": item["decoded_frames"],
                    "temporal_class": item["temporal_class"],
                    "catalog_role": item["catalog_role"],
                }
                for item in records
            ],
        },
        "loader_preflight": loader,
        "production_changed": False,
        "deferred": [
            "NETWORK27 full15 is not included; root must accept it and derive a separate final v23 map.",
            "No export_pages invocation or final v23 output was performed.",
        ],
    }
    write_json(RECEIPT, receipt)
    print(json.dumps({"receipt": rel(RECEIPT), "numeric_map": rel(NUMERIC_MAP), "catalog_map": rel(CATALOG_MAP), "collection_map": rel(COLLECTION_MAP), "assets": len(records), "asset_bytes": sum(int(item["length"]) for item in records), "loader": loader}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
