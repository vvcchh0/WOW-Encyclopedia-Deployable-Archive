"""Prepare root-accepted v22 primary image bytes and source map locally."""

from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "research/continuous-recovery-20261016/integration/accepted-images/v22"
V21_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json"
PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json"
V21_LATE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json"
V21_FAILURE_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v21-build/worker-build-v21.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
V20_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
CONTENT_RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-news-content01-source-acceptance.json"
STATIC_RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-static-main01-source-acceptance.json"
CONTENT_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-content01/output/source-map.json"
STATIC_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/static-main01/output/source-map.json"
ANCHOR = "20080512210044"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def source_entry(source_map_path: Path, original: str) -> tuple[dict[str, Any], int, dict[str, Any]]:
    document = read(source_map_path)
    for index, item in enumerate(document.get("accepted_payloads") or []):
        if item.get("original") == original:
            return item, index, document
    raise RuntimeError(f"accepted source-map payload not found: {original} in {source_map_path}")


def receipt_entry(receipt_path: Path, original: str) -> tuple[dict[str, Any], int, dict[str, Any]]:
    document = read(receipt_path)
    if document.get("accepted") is not True:
        raise RuntimeError(f"root receipt is not accepted: {receipt_path}")
    for index, item in enumerate(document.get("accepted_images") or []):
        if item.get("original") == original:
            return item, index, document
    raise RuntimeError(f"accepted receipt image not found: {original} in {receipt_path}")


def verify_image(data: bytes, expected_mime: str, expected_dimensions: list[int], expected_length: int, expected_sha: str, expected_digest: str) -> dict[str, Any]:
    if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
        raise RuntimeError("payload byte/hash mismatch")
    actual_digest = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")
    if actual_digest != expected_digest:
        raise RuntimeError(f"CDX digest mismatch: {actual_digest} != {expected_digest}")
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        detected = image.format
        dimensions = list(image.size)
        frames = int(getattr(image, "n_frames", 1))
        image.verify()
    expected_format = {"image/jpeg": "JPEG", "image/gif": "GIF", "image/png": "PNG"}.get(expected_mime)
    if expected_format and detected != expected_format:
        raise RuntimeError(f"Pillow format mismatch: {detected} != {expected_format}")
    if dimensions != expected_dimensions or frames < 1:
        raise RuntimeError(f"Pillow dimensions/frame mismatch: {dimensions}/{frames}")
    return {"format": detected, "dimensions": dimensions, "decoded_frames": frames}


def prepare_item(original: str, receipt_path: Path, source_map_path: Path, local_name: str, index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    accepted, receipt_index, receipt_document = receipt_entry(receipt_path, original)
    source_path = ROOT / str(accepted["private_payload_path"])
    if not source_path.is_file():
        raise RuntimeError(f"accepted private payload missing: {source_path}")
    payload, source_index, source_document = source_entry(source_map_path, original)
    if payload.get("decoded_body_sha256") != accepted.get("sha256") or int(payload.get("decoded_body_bytes")) != int(accepted.get("length")):
        raise RuntimeError(f"receipt/source-map disagreement for {original}")
    actual_timestamp = str(accepted.get("actual_capture_timestamp") or "")
    if not re.fullmatch(r"\d{14}", actual_timestamp) or actual_timestamp != str(payload.get("selected_capture_timestamp") or ""):
        raise RuntimeError(f"invalid or disagreeing capture timestamp for {original}")
    if actual_timestamp > ANCHOR or not actual_timestamp.startswith("2008"):
        raise RuntimeError(f"v22 primary image is outside 2008 anchor: {original} {actual_timestamp}")
    data = source_path.read_bytes()
    pillow = verify_image(data, str(accepted["mime"]), list(accepted["dimensions"]), int(accepted["length"]), str(accepted["sha256"]), str(accepted["cdx_digest"]))
    destination = ASSET_DIR / local_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    if destination.read_bytes() != data:
        raise RuntimeError(f"copy verification failed: {destination}")
    source_evidence = {
        "source_map_sha256": sha256(source_map_path),
        "target_key": payload.get("target_key"),
        "entry_index": source_index,
        "entry_status": source_document.get("accepted_payload_status") or "",
        "actual_memento_timestamp": actual_timestamp,
        "selected_capture_timestamp": actual_timestamp,
        "cdx_record_length": payload.get("cdx_record_length"),
        "replay_body_sha256": accepted.get("sha256"),
        "replay_body_length": accepted.get("length"),
        "replay_url": f"https://web.archive.org/web/{actual_timestamp}id_/{original}",
        "bound_from": "20060101000000",
        "bound_to": ANCHOR,
    }
    item = {
        "kind": "image",
        "logical_url": original,
        "original": original,
        "local_path": relative(destination),
        "mime": accepted["mime"],
        "sha256": accepted["sha256"],
        "length": int(accepted["length"]),
        "actual_timestamp": actual_timestamp,
        "indexed_capture_timestamp": actual_timestamp,
        "cdx_digest": accepted["cdx_digest"],
        "temporal_class": "baseline_2008",
        "dimensions": list(accepted["dimensions"]),
        "source_relationship": "Root-accepted baseline_2008 replay body added to the v22 primary overlay map; copied byte-for-byte without recompression.",
        "acceptance_record": f"{relative(receipt_path)}#accepted_images[{receipt_index}]",
        "accepted_raw_body": relative(source_path),
        "accepted_raw_body_sha256": accepted["sha256"],
        "source_map_record": f"{relative(source_map_path)}#accepted_payloads[{source_index}]",
        "source_evidence": source_evidence,
    }
    verification = {
        "index": index,
        "original": original,
        "local_path": relative(destination),
        "source_payload": relative(source_path),
        "sha256": accepted["sha256"],
        "length": int(accepted["length"]),
        "mime": accepted["mime"],
        "dimensions": list(accepted["dimensions"]),
        "pillow": pillow,
        "byte_for_byte": data == destination.read_bytes(),
        "actual_timestamp": actual_timestamp,
        "receipt": relative(receipt_path),
        "source_map": relative(source_map_path),
        "source_map_sha256": sha256(source_map_path),
        "receipt_checked_utc": receipt_document.get("checked_utc"),
    }
    return item, verification


def slug_for(index: int, original: str, prefix: str) -> str:
    name = Path(original.split("?", 1)[0]).name or f"image-{index}"
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    return f"{prefix}-{index:02d}-{name}"


def main() -> int:
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if PRIMARY_MAP.exists():
        raise RuntimeError(f"refusing to overwrite existing v22 map: {PRIMARY_MAP}")
    if ASSET_DIR.exists() and any(ASSET_DIR.iterdir()):
        raise RuntimeError(f"refusing to reuse non-empty v22 asset directory: {ASSET_DIR}")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    v21 = read(V21_MAP)
    v21_items = copy.deepcopy(v21.get("items") or [])
    if len(v21_items) != 36:
        raise RuntimeError(f"v21 map item count changed: {len(v21_items)}")
    for item in v21_items:
        item["source_relationship"] = "Inherited accepted v21 primary bytes retained in the v22 primary map; source bytes, origin metadata, route identity, and capture metadata remain unchanged."
        item["inherited_from_v21_map"] = {"path": relative(V21_MAP), "sha256": sha256(V21_MAP)}
        item.pop("inherited_from_v20_map", None)

    accepted_specs: list[tuple[Path, Path, str]] = []
    for receipt, source_map, prefix in ((CONTENT_RECEIPT, CONTENT_SOURCE_MAP, "content"), (STATIC_RECEIPT, STATIC_SOURCE_MAP, "static")):
        document = read(receipt)
        for index, accepted in enumerate(document.get("accepted_images") or [], start=1):
            accepted_specs.append((receipt, source_map, slug_for(index, str(accepted["original"]), prefix)))
    if len(accepted_specs) != 16:
        raise RuntimeError(f"new accepted image count changed: {len(accepted_specs)}")

    new_items: list[dict[str, Any]] = []
    verifications: list[dict[str, Any]] = []
    for index, (receipt, source_map, local_name) in enumerate(accepted_specs, start=1):
        accepted = read(receipt)
        original = str((accepted.get("accepted_images") or [])[index - 1 if receipt == CONTENT_RECEIPT else index - 11]["original"])
        item, verification = prepare_item(original, receipt, source_map, local_name, index)
        new_items.append(item)
        verifications.append(verification)

    receipt_records = []
    for receipt in (CONTENT_RECEIPT, STATIC_RECEIPT):
        document = read(receipt)
        receipt_records.append({
            "path": relative(receipt),
            "sha256": sha256(receipt),
            "accepted": document.get("accepted"),
            "accepted_count": len(document.get("accepted_images") or []),
            "total_image_bytes": document.get("image_bytes"),
            "checked_utc": document.get("checked_utc"),
        })
    source_map_records = []
    for source_map in (CONTENT_SOURCE_MAP, STATIC_SOURCE_MAP):
        document = read(source_map)
        source_map_records.append({
            "path": relative(source_map),
            "sha256": sha256(source_map),
            "accepted_payload_count": len(document.get("accepted_payloads") or []),
            "entry_count": len(document.get("entries") or []),
        })

    primary_items = v21_items + new_items
    primary_map = {
        "schema_version": 1,
        "kind": "wow_news_v22_primary_image_source_map",
        "accepted": True,
        "role": "primary_image_overlay",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {
            "records": receipt_records,
            "accepted_count": 16,
            "total_image_bytes": sum(int(item["length"]) for item in new_items),
            "new_items": [item["original"] for item in new_items],
        },
        "source_maps": source_map_records,
        "inherited_v21_map": {"path": relative(V21_MAP), "sha256": sha256(V21_MAP), "item_count": len(v21_items)},
        "copy_rule": "The 36 accepted v21 primary items are retained with version-independent v22 provenance wording. Sixteen additional root-accepted baseline_2008 bodies are copied byte-for-byte; SHA-256, length, MIME, Pillow dimensions, frames, and CDX digest are checked before export.",
        "items": primary_items,
    }
    write(PRIMARY_MAP, primary_map)

    verification = {
        "schema": "wow-recovery.integration.v22.input-preparation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "prepared_utc": generated,
        "network_requests": 0,
        "anchor_timestamp": ANCHOR,
        "v20_input": {"path": relative(V20_MAP), "sha256": sha256(V20_MAP), "item_count": len(read(V20_MAP).get("items") or [])},
        "v21_primary_input": {"path": relative(V21_MAP), "sha256": sha256(V21_MAP), "item_count": len(v21_items)},
        "v21_late_supplement_input": {"path": relative(V21_LATE_MAP), "sha256": sha256(V21_LATE_MAP), "item_count": len(read(V21_LATE_MAP).get("items") or [])},
        "v20_provenance": {"path": relative(V20_PROVENANCE), "sha256": sha256(V20_PROVENANCE)},
        "v21_build_receipt": {"path": relative(V21_FAILURE_RECEIPT), "sha256": sha256(V21_FAILURE_RECEIPT), "export_completed": read(V21_FAILURE_RECEIPT).get("export_completed")},
        "primary_map": {"path": relative(PRIMARY_MAP), "sha256": sha256(PRIMARY_MAP), "item_count": len(primary_items), "new_items": [item["original"] for item in new_items]},
        "asset_directory": relative(ASSET_DIR),
        "asset_count": len(new_items),
        "asset_bytes": sum(int(item["length"]) for item in new_items),
        "new_primary_asset_bytes": sum(int(item["length"]) for item in new_items),
        "verification": verifications,
        "old_maps_frozen": True,
        "production_changed": False,
    }
    write(OUT / "prepare-v22-inputs.json", verification)
    print(json.dumps({"primary_map": relative(PRIMARY_MAP), "primary_map_sha256": sha256(PRIMARY_MAP), "asset_count": len(new_items), "asset_bytes": verification["asset_bytes"], "inherited_v21_items": len(v21_items), "network_requests": 0}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
