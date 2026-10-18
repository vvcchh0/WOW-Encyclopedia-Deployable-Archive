#!/usr/bin/env python3
"""Copy accepted v26 payloads into owned public input folders and re-preflight.

Only the new v26 maps are changed.  The source payloads remain the immutable
network receipts; every copied byte is checked against the accepted SHA,
length, and CDX digest before its map is rebound to the integration copy.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from prepare_v26_inputs import (
    MIN_FREE_BYTES,
    NEW_COLLECTION,
    NEW_SUPPLEMENT,
    ROOT,
    cdx_digest,
    inside,
    loader_preflight,
    read_json,
    rel,
    sha256_file,
)
from prepare_v26_news_primary import NEWS_MAP, combined_loader_preflight


NEIGHBOR_DIR = ROOT / "research/continuous-recovery-20261018/integration/accepted-images/v26-neighbors"
NEWS_DIR = ROOT / "research/continuous-recovery-20261018/integration/accepted-images/v26-news"
PREPARATION = ROOT / "research/continuous-recovery-20261018/integration/v26-public-copy-rebind.json"


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def copy_map_items(map_path: Path, destination_dir: Path, prefix: str) -> list[dict]:
    payload = read_json(map_path, f"v26 map {map_path.name}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"{map_path} has no items list")
    if destination_dir.exists():
        raise RuntimeError(f"refusing existing public-copy directory: {destination_dir}")
    destination_dir.mkdir(parents=True, exist_ok=False)
    copied: list[dict] = []
    for index, item in enumerate(items, start=1):
        original = str(item.get("original") or item.get("logical_url") or "")
        source = inside(ROOT / str(item.get("local_path") or ""), f"source for {original}")
        if not source.is_file():
            raise RuntimeError(f"source payload missing: {source}")
        suffix = Path(original.split("?", 1)[0]).suffix.casefold() or ".jpg"
        stem = safe_slug(original.rsplit("/", 1)[-1].split("?", 1)[0].rsplit(".", 1)[0])
        key = safe_slug(str(item.get("target_key") or ""))
        label = key or stem or f"item-{index:02d}"
        destination = destination_dir / f"{index:02d}-{prefix}-{label}{suffix}"
        shutil.copyfile(source, destination)
        expected_sha = str(item.get("sha256") or "").casefold()
        expected_length = int(item.get("length", -1))
        actual_sha = sha256_file(destination)
        actual_length = destination.stat().st_size
        actual_cdx = cdx_digest(destination.read_bytes())
        expected_cdx = str(item.get("cdx_digest") or "").upper()
        if actual_sha != expected_sha or actual_length != expected_length or actual_cdx != expected_cdx:
            raise RuntimeError(f"public copy verification failed: {original}")
        item["local_path"] = rel(destination)
        copied.append(
            {
                "original": original,
                "source_private_payload": rel(source),
                "public_copy": rel(destination),
                "sha256": actual_sha,
                "length": actual_length,
                "cdx_digest": actual_cdx,
            }
        )
    map_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return copied


def update_receipt(path: Path, *, loader: dict | None = None, map_bindings: dict | None = None, rebind: dict | None = None) -> dict:
    payload = read_json(path, f"receipt {path.name}")
    if loader is not None:
        payload["loader_preflight"] = loader
        payload["checked_utc"] = datetime.now(timezone.utc).isoformat()
    if map_bindings is not None:
        payload["input_maps"] = map_bindings
        # Keep the nested source-map digests synchronized with the rewritten
        # public-copy paths.  These are preparation receipts, so they must
        # describe the exact map bytes that the next guarded exporter reads.
        if isinstance(payload.get("supplement_map"), dict) and "neighbor_supplement" in map_bindings:
            payload["supplement_map"]["sha256"] = map_bindings["neighbor_supplement"]["sha256"]
        if isinstance(payload.get("news_map"), dict) and "news_primary" in map_bindings:
            payload["news_map"]["sha256"] = map_bindings["news_primary"]["sha256"]
        if isinstance(payload.get("input_maps"), dict):
            for key in ("neighbor_supplement", "news_primary", "collection"):
                if key in payload["input_maps"]:
                    payload["input_maps"][key] = map_bindings[key]
    if rebind is not None:
        payload["public_copy_rebind"] = rebind
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before public copies: {free_before}")
    if PREPARATION.exists() or NEIGHBOR_DIR.exists() or NEWS_DIR.exists():
        raise RuntimeError("public copies or rebind receipt already exist; refusing duplicate batch")
    neighbor_copies = copy_map_items(NEW_SUPPLEMENT, NEIGHBOR_DIR, "neighbor")
    news_copies = copy_map_items(NEWS_MAP, NEWS_DIR, "news")
    map_bindings = {
        "neighbor_supplement": {"path": rel(NEW_SUPPLEMENT), "sha256": sha256_file(NEW_SUPPLEMENT)},
        "news_primary": {"path": rel(NEWS_MAP), "sha256": sha256_file(NEWS_MAP)},
        "collection": {"path": rel(NEW_COLLECTION), "sha256": sha256_file(NEW_COLLECTION)},
    }
    rebind = {
        "schema": "wow-recovery.continuous-recovery-20261018.v26-public-copy-rebind.v1",
        "status": "public_copies_bound_and_repreflighted",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "neighbor_count": len(neighbor_copies),
        "news_count": len(news_copies),
        "neighbor_copies": neighbor_copies,
        "news_copies": news_copies,
        "network_requests": 0,
        "export_executed": False,
        "source_private_payloads_preserved": True,
    }
    guide_loader = loader_preflight()
    combined_loader = combined_loader_preflight()
    update_receipt(
        ROOT / "research/continuous-recovery-20261018/integration/v26-input-preparation.json",
        map_bindings=map_bindings,
        rebind=rebind,
    )
    update_receipt(
        ROOT / "research/continuous-recovery-20261018/integration/v26-input-preflight.json",
        loader=guide_loader,
        map_bindings=map_bindings,
        rebind=rebind,
    )
    update_receipt(
        ROOT / "research/continuous-recovery-20261018/integration/v26-news-input-preparation.json",
        map_bindings=map_bindings,
        rebind=rebind,
    )
    update_receipt(
        ROOT / "research/continuous-recovery-20261018/integration/v26-combined-preflight.json",
        loader=combined_loader,
        map_bindings=map_bindings,
        rebind=rebind,
    )
    rebind["map_bindings"] = map_bindings
    rebind["guide_loader_preflight"] = guide_loader
    rebind["combined_loader_preflight"] = combined_loader
    rebind["disk_free_before_bytes"] = free_before
    rebind["disk_free_after_bytes"] = shutil.disk_usage(ROOT).free
    PREPARATION.write_text(json.dumps(rebind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": rebind["status"], "neighbor_count": len(neighbor_copies), "news_count": len(news_copies), "network_requests": 0, "export_executed": False, "map_bindings": map_bindings}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
