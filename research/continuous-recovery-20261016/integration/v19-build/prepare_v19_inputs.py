#!/usr/bin/env python3
"""Prepare the ten root-accepted shared-news bytes for the isolated v19 build.

This script is intentionally additive.  It refuses to overwrite the v19 map,
asset directory, or preparation receipt, and it does not touch any v18 input.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = ROOT / "research/continuous-recovery-20261016/integration"
MAP_PATH = INTEGRATION / "v19-primary-news-source-map.json"
ASSET_DIR = INTEGRATION / "accepted-images/news-v19"
RECEIPT_PATH = ROOT / "research/continuous-recovery-20261016/integration/v19-build/prepare-v19-inputs.json"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696

BATCHES = [
    {
        "batch": "news-shared10",
        "acceptance": ROOT / "research/continuous-recovery-20261016/publication/root-news-shared10-source-acceptance.json",
        "source_map": ROOT / "research/continuous-recovery-20261016/network/news-shared10/source-map.json",
        "prefix": "NEWS10",
    },
    {
        "batch": "news-shared13",
        "acceptance": ROOT / "research/continuous-recovery-20261016/publication/root-news-shared13-source-acceptance.json",
        "source_map": ROOT / "research/continuous-recovery-20261016/network/news-shared13/source-map.json",
        "prefix": "NEWS13",
    },
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")


def verify_image(data: bytes, expected_mime: str, expected_dimensions: list[int], expected_frames: int, label: str) -> dict[str, Any]:
    expected_format = {"image/gif": "GIF", "image/jpeg": "JPEG", "image/png": "PNG"}.get(expected_mime)
    if expected_format is None:
        raise RuntimeError(f"{label} unsupported MIME: {expected_mime!r}")
    with Image.open(BytesIO(data)) as image:
        image_format = image.format
        dimensions = list(image.size)
        frame_count = 0
        while True:
            image.seek(frame_count)
            image.load()
            frame_count += 1
            try:
                image.seek(frame_count)
            except EOFError:
                break
    if image_format != expected_format:
        raise RuntimeError(f"{label} format mismatch: {image_format!r} != {expected_format!r}")
    if dimensions != expected_dimensions:
        raise RuntimeError(f"{label} dimensions mismatch: {dimensions!r} != {expected_dimensions!r}")
    if frame_count != expected_frames:
        raise RuntimeError(f"{label} frame count mismatch: {frame_count} != {expected_frames}")
    return {"format": image_format, "dimensions": dimensions, "decoded_frames": frame_count}


def require_disk(label: str) -> int:
    free = shutil.disk_usage(ROOT).free
    if free < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor failed {label}: {free} < {MIN_FREE_BYTES}")
    return free


def load_json(path: Path, label: str) -> dict[str, Any]:
    require_file(path, label)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object")
    return payload


def source_map_entry(source_map: dict[str, Any], target_key: str, original: str) -> tuple[int, dict[str, Any], dict[str, Any]]:
    accepted = [item for item in source_map.get("accepted_payloads", []) if item.get("original") == original]
    if len(accepted) != 1:
        raise RuntimeError(f"source map accepted_payloads mismatch for {target_key}: {len(accepted)}")
    payload = accepted[0]
    entries = source_map.get("entries", [])
    matches = [(index, entry) for index, entry in enumerate(entries) if entry.get("target_key") == target_key]
    if len(matches) != 1:
        raise RuntimeError(f"source map entries mismatch for {target_key}: {len(matches)}")
    return matches[0][0], matches[0][1], payload


def main() -> int:
    if MAP_PATH.exists() or ASSET_DIR.exists() or RECEIPT_PATH.exists():
        raise RuntimeError("refusing to overwrite an existing v19 map, asset directory, or preparation receipt")
    require_disk("before preparation")

    all_items: list[dict[str, Any]] = []
    acceptance_records: list[dict[str, Any]] = []
    source_map_records: list[dict[str, Any]] = []
    seen_originals: set[str] = set()
    verification: list[dict[str, Any]] = []
    ASSET_DIR.mkdir(parents=True, exist_ok=False)

    for batch in BATCHES:
        acceptance_path = batch["acceptance"]
        source_map_path = batch["source_map"]
        acceptance = load_json(acceptance_path, f"{batch['batch']} acceptance")
        source_map = load_json(source_map_path, f"{batch['batch']} source map")
        if acceptance.get("accepted") is not True:
            raise RuntimeError(f"{batch['batch']} acceptance is not accepted")
        accepted_images = acceptance.get("accepted_images")
        if not isinstance(accepted_images, list):
            raise RuntimeError(f"{batch['batch']} acceptance has no accepted_images list")
        acceptance_records.append(
            {
                "batch": batch["batch"],
                "path": rel(acceptance_path),
                "sha256": sha256_file(acceptance_path),
                "batch_report_sha256": acceptance.get("batch_report_sha256"),
                "accepted": True,
                "accepted_count": len(accepted_images),
                "total_image_bytes": acceptance.get("image_bytes"),
                "checked_utc": acceptance.get("checked_utc"),
            }
        )
        source_map_records.append(
            {
                "batch": batch["batch"],
                "path": rel(source_map_path),
                "sha256": sha256_file(source_map_path),
                "accepted_payload_count": len(source_map.get("accepted_payloads", [])),
                "entry_count": len(source_map.get("entries", [])),
            }
        )
        for accepted_index, accepted in enumerate(accepted_images):
            original = str(accepted.get("original") or "")
            if not original or original in seen_originals:
                raise RuntimeError(f"duplicate or missing original URL at {batch['batch']}[{accepted_index}]")
            seen_originals.add(original)
            target_key = ""
            payload_matches = [
                item for item in source_map.get("accepted_payloads", []) if item.get("original") == original
            ]
            if len(payload_matches) != 1:
                raise RuntimeError(f"accepted payload not found for {original}")
            target_key = str(payload_matches[0].get("target_key") or "")
            source_index, entry, payload = source_map_entry(source_map, target_key, original)
            expected = {
                "sha256": accepted.get("sha256"),
                "length": accepted.get("length"),
                "actual_capture_timestamp": accepted.get("actual_capture_timestamp"),
                "cdx_digest": accepted.get("cdx_digest"),
            }
            for key, value in expected.items():
                payload_key = {
                    "sha256": "raw_body_sha256",
                    "actual_capture_timestamp": "selected_capture_timestamp",
                    "length": "raw_body_bytes",
                }.get(key, key)
                if payload.get(payload_key) != value:
                    raise RuntimeError(f"{batch['batch']} accepted/source-map mismatch for {original}: {key}")
            private_path = ROOT / str(accepted.get("private_payload_path") or "")
            require_file(private_path, f"payload for {original}")
            if rel(private_path) != str(payload.get("private_decoded_payload_path")):
                raise RuntimeError(f"private payload path mismatch for {original}")
            data = private_path.read_bytes()
            if sha256_bytes(data) != accepted.get("sha256") or len(data) != int(accepted.get("length")):
                raise RuntimeError(f"payload bytes do not match acceptance for {original}")
            image_name = f"{len(all_items) + 1:02d}-{Path(original.split("?", 1)[0]).name}"
            destination = ASSET_DIR / image_name
            shutil.copyfile(private_path, destination)
            copied = destination.read_bytes()
            if copied != data:
                raise RuntimeError(f"copy changed bytes for {original}")
            image_check = verify_image(
                copied,
                str(accepted.get("mime") or ""),
                list(accepted.get("dimensions") or []),
                int(accepted.get("decoded_frames")),
                original,
            )
            actual_timestamp = str(accepted.get("actual_capture_timestamp") or "")
            if not actual_timestamp.startswith("2008") or actual_timestamp > ANCHOR:
                raise RuntimeError(f"baseline timestamp is outside anchor for {original}: {actual_timestamp}")
            entry_status = str(entry.get("status") or "")
            latest_unknown = bool(entry.get("latest_unknown", False))
            replay_results = entry.get("replay_results") or []
            replay_url = ""
            if replay_results:
                replay_url = str(replay_results[0].get("memento_replay_url") or "")
                if not replay_url:
                    selected = (entry.get("cdx") or {}).get("selected") or []
                    if selected:
                        replay_url = str(selected[0].get("replay_url") or "")
            item = {
                "kind": "image",
                "logical_url": original,
                "original": original,
                "local_path": rel(destination),
                "mime": accepted.get("mime"),
                "sha256": accepted.get("sha256"),
                "length": int(accepted.get("length")),
                "actual_timestamp": actual_timestamp,
                "indexed_capture_timestamp": actual_timestamp,
                "cdx_digest": accepted.get("cdx_digest"),
                "temporal_class": "baseline_2008",
                "dimensions": list(accepted.get("dimensions") or []),
                "source_relationship": "root-accepted shared-news original; copied byte-for-byte for v19 primary image overlay preparation",
                "acceptance_record": f"{rel(acceptance_path)}#accepted_images[{accepted_index}]",
                "accepted_raw_body": rel(private_path),
                "accepted_raw_body_sha256": accepted.get("sha256"),
                "source_map_record": f"{rel(source_map_path)}#accepted_payloads[{source_map.get('accepted_payloads', []).index(payload)}]",
                "source_evidence": {
                    "source_map_sha256": sha256_file(source_map_path),
                    "target_key": target_key,
                    "entry_index": source_index,
                    "entry_status": entry_status,
                    "cdx_source": entry.get("cdx_source"),
                    "latest_unknown": latest_unknown,
                    "actual_memento_timestamp": accepted.get("actual_capture_timestamp"),
                    "selected_capture_timestamp": payload.get("selected_capture_timestamp"),
                    "cdx_record_length": payload.get("cdx_record_length"),
                    "replay_url": replay_url or None,
                    "bound_from": "20060101000000",
                    "bound_to": ANCHOR,
                    "best_known_bound": original.endswith("/blizzconlogo.jpg") and latest_unknown,
                },
            }
            all_items.append(item)
            verification.append(
                {
                    "original": original,
                    "local_path": rel(destination),
                    "source_payload": rel(private_path),
                    "sha256": sha256_file(destination),
                    "length": len(copied),
                    **image_check,
                    "byte_for_byte": copied == data,
                }
            )

    require_disk("before map write")
    map_payload = {
        "schema_version": 1,
        "kind": "wow_news_v19_primary_image_source_map",
        "accepted": True,
        "role": "primary_image_overlay",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {
            "records": acceptance_records,
            "accepted_count": len(all_items),
            "total_image_bytes": sum(int(item["length"]) for item in all_items),
        },
        "source_maps": source_map_records,
        "copy_rule": "Each local_path is a byte-for-byte copy of a root-accepted decoded replay body; SHA-256, length, MIME, Pillow dimensions, and all frames are checked before the v19 export. Blizzcon is explicitly bounded by the complete 20060101..20080512 window with best-known latest status.",
        "items": all_items,
    }
    MAP_PATH.write_text(json.dumps(map_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require_disk("after map write")
    receipt = {
        "schema": "wow-recovery.integration.v19.input-preparation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "prepared_utc": datetime.now().astimezone().isoformat(),
        "network_requests": 0,
        "anchor_timestamp": ANCHOR,
        "source_acceptance": acceptance_records,
        "source_maps": source_map_records,
        "map_path": rel(MAP_PATH),
        "map_sha256": sha256_file(MAP_PATH),
        "asset_directory": rel(ASSET_DIR),
        "asset_count": len(verification),
        "asset_bytes": sum(item["length"] for item in verification),
        "verification": verification,
        "disk_free_after_bytes": require_disk("after preparation"),
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"map": rel(MAP_PATH), "map_sha256": receipt["map_sha256"], "asset_count": len(verification), "asset_bytes": receipt["asset_bytes"], "receipt": rel(RECEIPT_PATH)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
