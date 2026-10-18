#!/usr/bin/env python3
"""Single guarded v26 export wrapper; preparation is safe, export is opt-in.

The wrapper imports the frozen v25 map lists and calls the existing exporter
exactly once when both ``--go`` and ``--root-export-go`` are supplied.  The
root v26 input-acceptance receipt, public-copy digests, frozen v25 hashes, and
combined preflight are checked before the exporter is entered.  A failed run
writes one worker receipt and is never retried by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = Path(__file__).resolve().parent
V25_LOCAL = ROOT / "research/focused-recovery-20261016-2301/local"
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
V25_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v25/export-provenance.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261018-v26"
RECEIPT = INTEGRATION / "v26-build-receipt.json"
ROOT_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v26-input-acceptance.json"
COMBINED_PREFLIGHT = INTEGRATION / "v26-combined-preflight.json"
NEWS_MAP = INTEGRATION / "v26-news-primary-source-map.json"
NEIGHBOR_MAP = INTEGRATION / "v26-neighbor-supplement-source-map.json"
COLLECTION_MAP = INTEGRATION / "v26-guide-image-collection-map.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696
EXPECTED_EXPORTER_SHA256 = "50bd3569f77d3d52c52ed7077726d7dc99fbee23a3a0ced076a6523198b9225d"
EXPECTED_V25_PROVENANCE_SHA256 = "e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_PREflight_SHA256 = "9e948ba51898ff1c09edccd1f12776ccd72da6c085aac2bb5e7f2b5540625ecc"


# Importing the v25 wrapper only loads its frozen constants; it does not run
# its main function.  This keeps the v26 map list aligned with the accepted
# v25 entry point while adding exactly one news map and one neighbor map.
sys.path.insert(0, str(V25_LOCAL))
import build_pages_v25 as frozen_v25  # noqa: E402


PRIMARY_MAPS = tuple(frozen_v25.PRIMARY_MAPS) + (NEWS_MAP,)
SUPPLEMENT_MAPS = tuple(frozen_v25.SUPPLEMENT_MAPS) + (NEIGHBOR_MAP,)


def sha256(path: Path) -> str:
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


def check_map_public_paths(path: Path) -> dict:
    payload = read_json(path, f"v26 map {path.name}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"v26 map has no items: {path}")
    private = []
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError(f"non-object map item in {path}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/integration/accepted-images/"):
            private.append(local)
        if "private-payloads" in local:
            private.append(local)
        target = ROOT / local
        if not target.is_file():
            raise RuntimeError(f"map local_path missing: {local}")
    if private:
        raise RuntimeError(f"map still references non-public/private paths: {private[:3]}")
    return {"path": rel(path), "sha256": sha256(path), "item_count": len(items)}


def check_collection_map(path: Path) -> dict:
    payload = read_json(path, f"v26 collection map {path.name}")
    groups = payload.get("groups")
    if not isinstance(groups, list) or len(groups) != 3:
        raise RuntimeError(f"v26 collection map group count changed: {path}")
    image_count = sum(len(group.get("images") or []) for group in groups if isinstance(group, dict))
    if image_count != 39:
        raise RuntimeError(f"v26 collection map image count changed: {image_count}")
    return {"path": rel(path), "sha256": sha256(path), "group_count": len(groups), "image_count": image_count}


def validate_root_acceptance() -> dict:
    receipt = read_json(ROOT_INPUT_ACCEPTANCE, "root v26 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v26 input acceptance is not accepted")
    expected_maps = {
        rel(NEIGHBOR_MAP): sha256(NEIGHBOR_MAP),
        rel(NEWS_MAP): sha256(NEWS_MAP),
        rel(COLLECTION_MAP): sha256(COLLECTION_MAP),
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-neighbors5-source-acceptance.json"): sha256(ROOT / "research/continuous-recovery-20261018/publication/root-neighbors5-source-acceptance.json"),
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-news9-source-acceptance.json"): sha256(ROOT / "research/continuous-recovery-20261018/publication/root-news9-source-acceptance.json"),
    }
    accepted_bindings = {
        str(item.get("path")): str(item.get("sha256", "")).casefold()
        for item in (receipt.get("map_bindings") or [])
        if isinstance(item, dict)
    }
    for path, expected in expected_maps.items():
        if accepted_bindings.get(path) != expected:
            raise RuntimeError(f"root acceptance map binding mismatch: {path}")
    preflight_sha = sha256(COMBINED_PREFLIGHT)
    if str(receipt.get("preflight_sha256") or "").casefold() != preflight_sha:
        raise RuntimeError("root acceptance preflight SHA mismatch")
    if preflight_sha != EXPECTED_PREflight_SHA256:
        raise RuntimeError("combined preflight SHA differs from accepted baseline")
    copies = receipt.get("public_image_copies") or []
    if len(copies) != 13 or int(receipt.get("new_images", -1)) != 13:
        raise RuntimeError(f"root acceptance expected 13 public copies, got {len(copies)}")
    checked_copies = []
    for item in copies:
        path = ROOT / str(item.get("path") or "")
        if not path.is_file():
            raise RuntimeError(f"accepted public copy missing: {path}")
        actual_sha = sha256(path)
        actual_length = path.stat().st_size
        if actual_sha != str(item.get("sha256") or "").casefold() or actual_length != int(item.get("length", -1)):
            raise RuntimeError(f"accepted public copy changed: {path}")
        checked_copies.append({"path": rel(path), "sha256": actual_sha, "length": actual_length})
    if int(receipt.get("prior_collection_images_preserved", -1)) != 35 or int(receipt.get("guide_collection_images", -1)) != 39:
        raise RuntimeError("root acceptance collection counts changed")
    return {
        "path": rel(ROOT_INPUT_ACCEPTANCE),
        "sha256": sha256(ROOT_INPUT_ACCEPTANCE),
        "public_copies": checked_copies,
        "map_bindings": expected_maps,
        "preflight_sha256": preflight_sha,
    }


def validate_gates() -> dict:
    if sha256(V25_PROVENANCE) != EXPECTED_V25_PROVENANCE_SHA256:
        raise RuntimeError("v25 provenance SHA changed")
    if sha256(SOURCE_MANIFEST) != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise RuntimeError("source15 manifest SHA changed")
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if manifest.get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 manifest anchor changed")
    if sha256(ROOT / "tools/export_github_pages.py") != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("accepted exporter SHA changed")
    for key, expected in frozen_v25.FROZEN_MAP_SHAS.items():
        path = ROOT / key
        if sha256(path) != expected:
            raise RuntimeError(f"frozen v25 map changed: {key}")
    preflight = read_json(COMBINED_PREFLIGHT, "v26 combined preflight")
    if preflight.get("status") != "preflight_passed_waiting_export_go" or preflight.get("network_requests") != 0 or preflight.get("export_executed") is not False:
        raise RuntimeError("combined preflight is not an offline waiting-for-GO receipt")
    expected = preflight.get("expected_after_export") or {}
    for key, value in {"declared_files": 8654, "actual_files": 8655, "primary_overlays": 125, "supplement_overlays": 71, "total_overlays": 196, "guide_previews": 22, "guide_collection_images": 39}.items():
        if expected.get(key) != value:
            raise RuntimeError(f"combined preflight expected {key}={expected.get(key)!r}, expected {value}")
    root_acceptance = validate_root_acceptance()
    map_checks = [check_map_public_paths(path) for path in (NEIGHBOR_MAP, NEWS_MAP)]
    map_checks.append(check_collection_map(COLLECTION_MAP))
    return {
        "root_input_acceptance": root_acceptance,
        "v25_provenance_sha256": sha256(V25_PROVENANCE),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "exporter_sha256": sha256(ROOT / "tools/export_github_pages.py"),
        "frozen_v25_map_count": len(frozen_v25.FROZEN_MAP_SHAS),
        "v26_map_checks": map_checks,
        "combined_preflight_sha256": sha256(COMBINED_PREFLIGHT),
    }


def guard_outputs() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing existing v26 output: {OUTPUT}")
    if OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError(f"refusing existing v26 partial output: {OUTPUT.with_name(OUTPUT.name + '.partial')}")
    if RECEIPT.exists():
        raise RuntimeError(f"refusing existing v26 worker receipt: {RECEIPT}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true", help="enter the single exporter call; requires --root-export-go")
    parser.add_argument("--root-export-go", action="store_true", help="explicit root export gate")
    args = parser.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat()
    gates = validate_gates()
    guard_outputs()
    if args.root_export_go and not args.go:
        parser.error("--root-export-go requires --go")
    if args.go and not args.root_export_go:
        parser.error("v26 export requires both --go and --root-export-go")
    if not args.go:
        print(json.dumps({"status": "ready_waiting_root_export_go", "network_requests": 0, "export_executed": False, "gates": gates}, ensure_ascii=False))
        return 0
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk floor before v26 export: {free_before}")
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=PRIMARY_MAPS,
            supplement_image_source_maps=SUPPLEMENT_MAPS,
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=COLLECTION_MAP,
        )
        provenance = read_json(OUTPUT / "export-provenance.json", "v26 output provenance")
        stats = provenance.get("stats") or {}
        expected_stats = {
            "source_records": 8357,
            "image_overlay_records": 196,
            "primary_image_overlay_records": 125,
            "supplement_image_overlay_records": 71,
            "output_files": 8654,
        }
        for key, value in expected_stats.items():
            if stats.get(key) != value:
                raise RuntimeError(f"v26 provenance {key}={stats.get(key)!r}, expected {value}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != 8655:
            raise RuntimeError(f"v26 actual file count {actual_files}")
        free_after = shutil.disk_usage(ROOT).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk floor after v26 export: {free_after}")
        receipt = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/build_pages_v26.py --go --root-export-go",
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat(),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "accepted_map_written": False,
            "gates": gates,
            "build": result,
            "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_sha256": sha256(OUTPUT / "export-provenance.json")},
            "output": rel(OUTPUT),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        failure = {
            "schema": "wow-recovery.continuous-recovery-20261018.v26-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": "python.exe -X utf8 research/continuous-recovery-20261018/integration/build_pages_v26.py --go --root-export-go",
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat(),
            "export_started": True,
            "export_completed": False,
            "published": False,
            "network_requests_by_builder": 0,
            "accepted_map_written": False,
            "gates": gates,
            "error": f"{type(exc).__name__}: {exc}",
            "output": rel(OUTPUT) if OUTPUT.exists() else None,
            "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
