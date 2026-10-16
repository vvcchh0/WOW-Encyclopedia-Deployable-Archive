"""Prepare v21 accepted image bytes and source maps from frozen local receipts.

This is local-only.  It consumes the root-accepted replay receipts, copies the
three decoded payloads byte-for-byte, and writes the v21 primary and explicit
late supplement maps.  It does not run the Pages exporter.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "research/continuous-recovery-20261016/integration/accepted-images/news-v21"
V20_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json"
LATE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
V20_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v20-export-acceptance.json"

PRIMARY_RECEIPTS = [
    ROOT / "research/continuous-recovery-20261016/publication/root-aug-final3-source-acceptance.json",
    ROOT / "research/continuous-recovery-20261016/publication/root-aug-cached19-source-acceptance.json",
]
LATE_RECEIPT = ROOT / "research/continuous-recovery-20261016/publication/root-aug-late11-source-acceptance.json"
PRIMARY_SOURCE_MAPS = [
    ROOT / "research/continuous-recovery-20261016/network/aug27-final3/output/source-map.json",
    ROOT / "research/continuous-recovery-20261016/network/aug27-cached19/output/source-map.json",
]
LATE_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-same-day-late11/output/source-map.json"
ANCHOR = "20080512210044"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def receipt_image(receipt_paths: list[Path], original: str) -> tuple[dict, Path]:
    for receipt_path in receipt_paths:
        receipt = read(receipt_path)
        if receipt.get("accepted") is not True:
            raise RuntimeError(f"root receipt is not accepted: {receipt_path}")
        for index, item in enumerate(receipt.get("accepted_images") or []):
            if item.get("original") == original:
                return item, receipt_path
    raise RuntimeError(f"accepted image not found in receipts: {original}")


def source_entry(source_map_path: Path, original: str) -> tuple[dict, int, dict]:
    payload = read(source_map_path)
    for index, item in enumerate(payload.get("accepted_payloads") or []):
        if item.get("original") == original:
            return item, index, payload
    raise RuntimeError(f"accepted source-map payload not found: {original} in {source_map_path}")


def verify_image(data: bytes, expected_mime: str, expected_dimensions: list[int], expected_length: int, expected_sha: str, expected_digest: str) -> dict:
    if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
        raise RuntimeError("payload byte/hash mismatch")
    actual_digest = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")
    if actual_digest != expected_digest:
        raise RuntimeError(f"CDX digest mismatch: {actual_digest} != {expected_digest}")
    from PIL import Image
    import io
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


def prepare_item(original: str, receipt_paths: list[Path], source_map_paths: list[Path], local_name: str, *, temporal_class: str, relationship: str) -> tuple[dict, dict]:
    accepted, receipt_path = receipt_image(receipt_paths, original)
    source_path = ROOT / str(accepted["private_payload_path"])
    if not source_path.is_file():
        raise RuntimeError(f"accepted private payload missing: {source_path}")
    source_map_path = None
    payload = None
    entry_index = None
    source_map_doc = None
    for candidate in source_map_paths:
        try:
            payload, entry_index, source_map_doc = source_entry(candidate, original)
            source_map_path = candidate
            break
        except RuntimeError:
            continue
    if source_map_path is None or payload is None or source_map_doc is None:
        raise RuntimeError(f"source map payload missing for {original}")
    if payload.get("decoded_body_sha256") != accepted.get("sha256") or int(payload.get("decoded_body_bytes")) != int(accepted.get("length")):
        raise RuntimeError(f"receipt/source-map disagreement for {original}")
    if not re.fullmatch(r"\d{14}", str(accepted.get("actual_capture_timestamp") or "")):
        raise RuntimeError("invalid capture timestamp")
    data = source_path.read_bytes()
    image_meta = verify_image(data, str(accepted["mime"]), list(accepted["dimensions"]), int(accepted["length"]), str(accepted["sha256"]), str(accepted["cdx_digest"]))
    destination = ASSET_DIR / local_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    if destination.read_bytes() != data:
        raise RuntimeError(f"copy verification failed: {destination}")
    source_evidence = {
        "source_map_sha256": sha256(source_map_path),
        "target_key": payload.get("target_key"),
        "entry_index": entry_index,
        "entry_status": (source_map_doc.get("accepted_payload_status") or ""),
        "actual_memento_timestamp": accepted.get("actual_capture_timestamp"),
        "selected_capture_timestamp": accepted.get("actual_capture_timestamp"),
        "cdx_record_length": payload.get("cdx_record_length"),
        "replay_body_sha256": accepted.get("sha256"),
        "replay_body_length": accepted.get("length"),
        "replay_url": f"https://web.archive.org/web/{accepted.get('actual_capture_timestamp')}id_/{original}",
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
        "actual_timestamp": accepted["actual_capture_timestamp"],
        "indexed_capture_timestamp": accepted["actual_capture_timestamp"],
        "cdx_digest": accepted["cdx_digest"],
        "temporal_class": temporal_class,
        "dimensions": list(accepted["dimensions"]),
        "source_relationship": relationship,
        "acceptance_record": f"{relative(receipt_path)}#accepted_images[{next(i for i,x in enumerate(read(receipt_path).get('accepted_images') or []) if x.get('original') == original)}]",
        "accepted_raw_body": relative(source_path),
        "accepted_raw_body_sha256": accepted["sha256"],
        "source_map_record": f"{relative(source_map_path)}#accepted_payloads[{entry_index}]",
        "source_evidence": source_evidence,
    }
    verification = {
        "original": original,
        "local_path": relative(destination),
        "source_payload": relative(source_path),
        "sha256": accepted["sha256"],
        "length": int(accepted["length"]),
        "mime": accepted["mime"],
        "dimensions": list(accepted["dimensions"]),
        "pillow": image_meta,
        "byte_for_byte": data == destination.read_bytes(),
        "actual_timestamp": accepted.get("actual_capture_timestamp"),
        "temporal_class": temporal_class,
        "receipt": relative(receipt_path),
        "source_map": relative(source_map_path),
        "source_map_sha256": sha256(source_map_path),
    }
    return item, verification


def main() -> int:
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if PRIMARY_MAP.exists() or LATE_MAP.exists():
        raise RuntimeError("refusing to overwrite existing v21 maps")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    v20 = read(V20_MAP)
    v20_items = copy.deepcopy(v20.get("items") or [])
    if len(v20_items) != 34:
        raise RuntimeError(f"v20 map item count changed: {len(v20_items)}")
    for item in v20_items:
        item["source_relationship"] = "Inherited unchanged from the accepted v20 primary map for v21; source bytes, origin metadata, and route identity remain byte-for-byte bound to the v20 item."
        item["inherited_from_v20_map"] = {"path": relative(V20_MAP), "sha256": sha256(V20_MAP)}

    tcg, tcg_verification = prepare_item(
        "http://www.worldofwarcraft.com/news/images/07-08/tcg03-thumb.jpg",
        PRIMARY_RECEIPTS,
        PRIMARY_SOURCE_MAPS,
        "25-tcg03-thumb.jpg",
        temporal_class="baseline_2008",
        relationship="Root-accepted baseline_2008 replay body added to v21 primary overlay map; copied byte-for-byte without recompression.",
    )
    aug19, aug19_verification = prepare_item(
        "http://www.worldofwarcraft.com/news/images/07-08/08-15-07-3.jpg",
        PRIMARY_RECEIPTS,
        PRIMARY_SOURCE_MAPS,
        "26-08-15-07-3.jpg",
        temporal_class="baseline_2008",
        relationship="Root-accepted baseline_2008 replay body added to v21 primary overlay map; copied byte-for-byte without recompression.",
    )
    late, late_verification = prepare_item(
        "http://www.worldofwarcraft.com/news/images/07-08/08-22-07-2.jpg",
        [LATE_RECEIPT],
        [LATE_SOURCE_MAP],
        "late-08-22-07-2.jpg",
        temporal_class="late_2008",
        relationship="Root-accepted late_2008 supplement; actual May 12 capture retained separately, with pre-anchor April digest identity recorded in source evidence.",
    )
    late["pre_anchor_indexed_capture"] = "20080402080429"
    late["pre_anchor_digest"] = "MLUKMD2MO3CNVZGT2PCCNNXF7RDKJAA4"
    late["pre_anchor_digest_match"] = True
    late["adoption_approved"] = True
    v21_items = v20_items + [tcg, aug19]

    receipt_records = []
    for path in PRIMARY_RECEIPTS + [LATE_RECEIPT]:
        receipt = read(path)
        receipt_records.append({
            "path": relative(path),
            "sha256": sha256(path),
            "accepted": receipt.get("accepted"),
            "accepted_count": len(receipt.get("accepted_images") or []),
            "total_image_bytes": receipt.get("image_bytes"),
            "checked_utc": receipt.get("checked_utc"),
        })

    source_map_records = []
    for path in [V20_MAP, *PRIMARY_SOURCE_MAPS, LATE_SOURCE_MAP]:
        doc = read(path)
        source_map_records.append({
            "path": relative(path),
            "sha256": sha256(path),
            "accepted_payload_count": len(doc.get("accepted_payloads") or []) if "accepted_payloads" in doc else len(doc.get("items") or []),
            "entry_count": len(doc.get("entries") or []) if "entries" in doc else len(doc.get("items") or []),
        })

    primary_map = {
        "schema_version": 1,
        "kind": "wow_news_v21_primary_image_source_map",
        "accepted": True,
        "role": "primary_image_overlay",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {"records": receipt_records[:2], "accepted_count": 2, "total_image_bytes": tcg["length"] + aug19["length"]},
        "source_maps": source_map_records[:3],
        "copy_rule": "The 34 accepted v20 primary items are cloned with version-independent v21 provenance wording. Two additional root-accepted baseline_2008 bodies are copied byte-for-byte; SHA-256, length, MIME, Pillow dimensions, frames, and CDX digest are checked before export.",
        "items": v21_items,
    }
    late_map = {
        "schema_version": 1,
        "kind": "wow_news_v21_august_late_supplement_source_map",
        "accepted": True,
        "role": "supplement_image_overlay",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {"records": receipt_records[2:], "accepted_count": 1, "total_image_bytes": late["length"]},
        "source_maps": [source_map_records[-1]],
        "copy_rule": "The one root-accepted late_2008 payload remains an explicit supplement. Its actual 20080512231210 capture is preserved; the equal April pre-anchor CDX digest is evidence only and does not reclassify the payload as baseline.",
        "items": [late],
    }
    write(PRIMARY_MAP, primary_map)
    write(LATE_MAP, late_map)
    verification = {
        "schema": "wow-recovery.integration.v21.input-preparation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "prepared_utc": generated,
        "network_requests": 0,
        "anchor_timestamp": ANCHOR,
        "v20_input": {"path": relative(V20_MAP), "sha256": sha256(V20_MAP), "item_count": len(v20_items)},
        "v20_provenance": {"path": relative(V20_PROVENANCE), "sha256": sha256(V20_PROVENANCE)},
        "v20_acceptance": {"path": relative(V20_ACCEPTANCE), "sha256": sha256(V20_ACCEPTANCE)},
        "primary_map": {"path": relative(PRIMARY_MAP), "sha256": sha256(PRIMARY_MAP), "item_count": len(v21_items), "new_items": [tcg["original"], aug19["original"]]},
        "late_map": {"path": relative(LATE_MAP), "sha256": sha256(LATE_MAP), "item_count": 1, "new_items": [late["original"]]},
        "asset_directory": relative(ASSET_DIR),
        "asset_count": 3,
        "asset_bytes": tcg["length"] + aug19["length"] + late["length"],
        "primary_asset_bytes": tcg["length"] + aug19["length"],
        "late_asset_bytes": late["length"],
        "verification": [tcg_verification, aug19_verification, late_verification],
        "pre_anchor_digest_match_preserved": late.get("pre_anchor_digest_match"),
        "late_actual_timestamp": late.get("actual_timestamp"),
        "late_temporal_class": late.get("temporal_class"),
        "old_v20_frozen": True,
        "production_changed": False,
    }
    write(OUT / "prepare-v21-inputs.json", verification)
    print(json.dumps({"primary_map": relative(PRIMARY_MAP), "primary_map_sha256": sha256(PRIMARY_MAP), "late_map": relative(LATE_MAP), "late_map_sha256": sha256(LATE_MAP), "asset_count": 3, "asset_bytes": verification["asset_bytes"], "primary_bytes": verification["primary_asset_bytes"], "late_bytes": verification["late_asset_bytes"], "network_requests": 0}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
