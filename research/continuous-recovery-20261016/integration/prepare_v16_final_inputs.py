"""Prepare the single final v16 NEWS primary map and EU2 supplement map."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/continuous-recovery-20261016/integration"
NEWS_ACCEPTANCES = [
    ROOT / "research/continuous-recovery-20261016/publication/root-news01-acceptance.json",
    ROOT / "research/continuous-recovery-20261016/publication/root-news02-acceptance.json",
]
EU2_PROPOSAL = ROOT / "research/continuous-recovery-20261016/local-audit/regional-image-supplement-map.proposal.json"
NEWS_MAP = OUT / "v16-primary-news-image-source-map.json"
EU2_MAP = OUT / "v16-eu-image-source-map.json"
NEWS_COPY_RECEIPT = OUT / "v16-primary-news-copy-receipt.json"
EU2_COPY_RECEIPT = OUT / "v16-eu-copy-receipt.json"
ANCHOR = "20080512210044"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def image_check(path: Path, expected_sha: str, expected_length: int) -> dict:
    actual_sha = sha256(path)
    actual_length = path.stat().st_size
    if actual_sha != expected_sha or actual_length != expected_length:
        raise AssertionError(
            f"payload mismatch {path}: {actual_length}/{actual_sha} expected {expected_length}/{expected_sha}"
        )
    with Image.open(path) as image:
        dimensions = list(image.size)
        image.verify()
    with Image.open(path) as image:
        image.load()
        mime_format = image.format
    return {
        "path": rel(path),
        "sha256": actual_sha,
        "length": actual_length,
        "dimensions": dimensions,
        "format": mime_format,
    }


def copy_payload(source: Path, destination: Path, expected_sha: str, expected_length: int) -> dict:
    if not source.is_file():
        raise AssertionError(f"accepted source missing: {source}")
    source_check = image_check(source, expected_sha, expected_length)
    if destination.exists():
        raise RuntimeError(f"refusing to overwrite existing final asset: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    destination_check = image_check(destination, expected_sha, expected_length)
    return {
        "source": source_check,
        "destination": destination_check,
        "byte_for_byte": source.read_bytes() == destination.read_bytes(),
    }


def prepare_news() -> dict:
    if NEWS_MAP.exists() or NEWS_COPY_RECEIPT.exists():
        raise RuntimeError(f"final NEWS map or receipt already exists: {NEWS_MAP}")
    accepted = []
    acceptance_evidence = []
    for acceptance_path in NEWS_ACCEPTANCES:
        acceptance = load(acceptance_path)
        if not acceptance.get("accepted"):
            raise AssertionError(f"root acceptance is not accepted: {acceptance_path}")
        acceptance_evidence.append(
            {
                "path": rel(acceptance_path),
                "sha256": sha256(acceptance_path),
                "accepted": acceptance.get("accepted"),
                "total_image_bytes": acceptance.get("total_image_bytes"),
                "accepted_count": len(acceptance.get("accepted_images") or []),
                "checked_utc": acceptance.get("checked_utc"),
            }
        )
        accepted.extend((acceptance_path, item) for item in acceptance.get("accepted_images") or [])
    if len(accepted) != 9:
        raise AssertionError(f"expected 9 accepted NEWS images, got {len(accepted)}")

    items = []
    copied = []
    for index, (acceptance_path, item) in enumerate(accepted, start=1):
        original = str(item["original"])
        source = ROOT / item["raw_body_path"]
        name = Path(original.split("?", 1)[0]).name
        destination = OUT / "accepted-images/news" / f"{index:02d}-{name}"
        copy = copy_payload(source, destination, str(item["sha256"]), int(item["length"]))
        copied.append(
            {
                "acceptance_record": f"{rel(acceptance_path)}#accepted_images[{(index - 1) if acceptance_path == NEWS_ACCEPTANCES[0] else (index - 4)}]",
                "original": original,
                "raw_body_path": rel(source),
                "raw_body_sha256": sha256(source),
                "copy": copy,
            }
        )
        items.append(
            {
                "kind": "image",
                "logical_url": original,
                "original": original,
                "local_path": rel(destination),
                "mime": str(item["mime"]),
                "sha256": str(item["sha256"]),
                "length": int(item["length"]),
                "actual_timestamp": str(item["actual_timestamp"]),
                "indexed_capture_timestamp": str(item["actual_timestamp"]),
                "cdx_digest": str(item["cdx_digest"]),
                "temporal_class": "baseline_2008",
                "dimensions": list(item["dimensions"]),
                "source_relationship": "root-accepted NEWS01/NEWS02 original JPEG; copied byte-for-byte for primary image overlay",
                "acceptance_record": f"{rel(acceptance_path)}#accepted_images[{(index - 1) if acceptance_path == NEWS_ACCEPTANCES[0] else (index - 4)}]",
                "accepted_raw_body": rel(source),
                "accepted_raw_body_sha256": sha256(source),
            }
        )

    payload = {
        "schema_version": 1,
        "kind": "wow_news_v16_primary_image_source_map",
        "accepted": True,
        "role": "primary_image_overlay",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {
            "records": acceptance_evidence,
            "accepted_count": len(items),
            "total_image_bytes": sum(int(item["length"]) for item in items),
        },
        "copy_rule": "Each local_path is a byte-for-byte copy of a root-accepted raw replay body; SHA-256, length, and Pillow decode are checked before and after copy.",
        "items": items,
    }
    NEWS_MAP.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "wow-recovery.integration.v16-primary-news-copy.v1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests_performed": 0,
        "export_started": False,
        "accepted_count": len(items),
        "total_image_bytes": sum(int(item["length"]) for item in items),
        "acceptances": acceptance_evidence,
        "copied": copied,
        "map": {"path": rel(NEWS_MAP), "sha256": sha256(NEWS_MAP), "items": len(items)},
        "disk_free_bytes_after_copy": shutil.disk_usage(ROOT.drive or ROOT.anchor).free,
    }
    NEWS_COPY_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def prepare_eu2() -> dict:
    if EU2_MAP.exists() or EU2_COPY_RECEIPT.exists():
        raise RuntimeError(f"final EU2 map or receipt already exists: {EU2_MAP}")
    proposal = load(EU2_PROPOSAL)
    if len(proposal.get("items") or []) != 2:
        raise AssertionError("EU2 proposal must contain exactly two accepted items")
    proposal_hash = sha256(EU2_PROPOSAL)
    items = []
    copied = []
    for index, item in enumerate(proposal["items"], start=1):
        source = ROOT / item["local_path"]
        destination = OUT / "accepted-images/eu2" / Path(item["local_path"]).name
        copy = copy_payload(source, destination, str(item["sha256"]), int(item["length"]))
        accepted_item = dict(item)
        accepted_item["local_path"] = rel(destination)
        accepted_item["source_local_path_prior"] = rel(source)
        accepted_item["accepted"] = True
        accepted_item["acceptance_record"] = f"{rel(EU2_PROPOSAL)}#/items/{index - 1}"
        accepted_item["copied_source_sha256"] = sha256(source)
        accepted_item["copied_destination_sha256"] = sha256(destination)
        items.append(accepted_item)
        copied.append(
            {
                "proposal_item_index": index - 1,
                "logical_url": item["logical_url"],
                "source": copy["source"],
                "destination": copy["destination"],
                "byte_for_byte": copy["byte_for_byte"],
            }
        )
    payload = {
        "schema_version": 1,
        "kind": "related_official_image_integration_map",
        "accepted": True,
        "role": "related_site_image_supplement",
        "anchor_timestamp": ANCHOR,
        "source_acceptance": {
            "proposal_path": rel(EU2_PROPOSAL),
            "proposal_sha256": proposal_hash,
            "accepted_items": len(items),
            "source_relationship": "root-accepted EU2 related-site full images; supplement only, never a US Game Guide primary replacement",
        },
        "copy_rule": "Each local_path is a byte-for-byte copy of the accepted proposal payload; SHA-256, length, and Pillow decode are checked before and after copy.",
        "items": items,
    }
    EU2_MAP.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "wow-recovery.integration.v16-eu2-copy.v1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests_performed": 0,
        "export_started": False,
        "proposal": {"path": rel(EU2_PROPOSAL), "sha256": proposal_hash},
        "accepted_count": len(items),
        "copied": copied,
        "map": {"path": rel(EU2_MAP), "sha256": sha256(EU2_MAP), "items": len(items)},
        "disk_free_bytes_after_copy": shutil.disk_usage(ROOT.drive or ROOT.anchor).free,
    }
    EU2_COPY_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    news = prepare_news()
    eu2 = prepare_eu2()
    print(json.dumps({"news": news, "eu2": eu2}, ensure_ascii=False))


if __name__ == "__main__":
    main()
