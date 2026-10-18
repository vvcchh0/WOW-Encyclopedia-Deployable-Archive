#!/usr/bin/env python3
"""Guarded one-shot exporter wrapper for the prepared v33 closure.

This file never regenerates a map or preflight.  It refuses to run without an
accepted root input gate and the explicit ``--go --root-export-go`` pair.  The
root gate must bind the exact prepared files, public-copy bytes, and postbuild
expectations before the exporter is called.
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


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
BUILDER_PATH = INTEGRATION / "build_pages_v33.py"
PRIMARY_MAP = INTEGRATION / "v33-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v33-supplement-source-map.json"
IMPACT = INTEGRATION / "v33-impact-estimate.json"
SOURCE_AUDIT = INTEGRATION / "v33-source-byte-audit.json"
PREPARATION = INTEGRATION / "v33-input-preparation.json"
PREFLIGHT = INTEGRATION / "v33-preflight.json"
PROPOSAL = INTEGRATION / "v33-input-proposal.md"
RUNNER_NOTE = INTEGRATION / "v33-runner-preparation.md"
BUILD_RECEIPT = INTEGRATION / "v33-build-receipt.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261018-v33"
ROOT_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v33-input-acceptance.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696
EXPECTED_EXPORTER_SHA256 = "2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
V33_SCHEMA = "wow-recovery.integration.v33-build-receipt.v1"


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


def load_builder():
    if not BUILDER_PATH.is_file():
        raise RuntimeError(f"missing v33 builder: {BUILDER_PATH}")
    spec = importlib.util.spec_from_file_location("wow_recovery_v33_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v33 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _binding_map(paths: list[Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"required v33 binding is missing: {path}")
        result[rel(path)] = sha256_file(path)
    return result


def required_bindings(builder: object) -> dict[str, str]:
    """Return every immutable input needed to reconstruct this export."""

    frozen, old_primary, old_supplement, _ = builder.frozen_maps()
    input_manifest = Path(builder.ROOT_SOURCE_INPUT_MANIFEST)
    source_manifest, rows, batch_bindings = builder.load_source_input_manifest(input_manifest)
    paths: list[Path] = [
        BUILDER_PATH,
        Path(__file__),
        PRIMARY_MAP,
        SUPPLEMENT_MAP,
        IMPACT,
        SOURCE_AUDIT,
        PREPARATION,
        PREFLIGHT,
        PROPOSAL,
        RUNNER_NOTE,
        builder.V28_BUILDER,
        builder.V29_PRIMARY_MAP,
        builder.V30_PRIMARY_MAP,
        builder.V30_SUPPLEMENT_MAP,
        builder.V30_PROVENANCE,
        builder.V30_BUILD_RECEIPT,
        builder.V32_PRIMARY_MAP,
        builder.V32_SUPPLEMENT_MAP,
        builder.V32_PROVENANCE,
        builder.V32_BUILD_RECEIPT,
        builder.V32_INPUT_ACCEPTANCE,
        builder.V32_EXPORT_ACCEPTANCE,
        builder.SOURCE_MANIFEST,
        builder.ORIGINAL_MANIFEST,
        builder.GUIDE_PREVIEW_MAP,
        builder.GUIDE_COLLECTION_MAP,
        builder.EXPORTER,
        builder.HISTORICAL_EXHIBITS,
        builder.ROOT_POPUP_ACCEPTANCE,
        builder.ROOT_NAVIGATION_ACCEPTANCE,
        builder.ROOT_RETIRED_ACCEPTANCE,
        builder.ROOT_MASK_ACCEPTANCE,
        input_manifest,
    ]
    for path in old_primary + old_supplement:
        paths.append(path)
    for row in rows:
        paths.extend([Path(row["_source_path"]), Path(row["_public_receipt_path"]), Path(row["_destination"])])
    return _binding_map(paths)


def validate_root_acceptance(builder: object, preflight: dict) -> dict:
    gate = read_json(ROOT_INPUT_ACCEPTANCE, "root v33 input acceptance")
    if gate.get("accepted") is not True:
        raise RuntimeError("root v33 input acceptance is not accepted")
    if str(gate.get("preflight_sha256") or "").casefold() != sha256_file(PREFLIGHT):
        raise RuntimeError("root v33 preflight SHA mismatch")
    if gate.get("network_requests") not in {0, None} or gate.get("export_executed") is not False:
        raise RuntimeError("root v33 gate records network/export activity")
    expected_counts = {
        "new_images": preflight.get("new_image_count"),
        "image_bytes": preflight.get("new_image_bytes"),
        "new_primary_images": preflight.get("new_primary_count"),
        "new_supplement_images": preflight.get("new_supplement_count"),
    }
    for key, wanted in expected_counts.items():
        if key in gate and gate.get(key) != wanted:
            raise RuntimeError(f"root v33 gate {key} changed: {gate.get(key)!r} != {wanted!r}")
    actual_bindings = {
        str(item.get("path")): str(item.get("sha256") or "").casefold()
        for item in gate.get("map_bindings", [])
        if isinstance(item, dict)
    }
    expected_bindings = required_bindings(builder)
    for path, wanted in expected_bindings.items():
        if actual_bindings.get(path) != wanted:
            raise RuntimeError(f"root v33 binding mismatch: {path}")
    _, rows, _ = builder.load_source_input_manifest(Path(builder.ROOT_SOURCE_INPUT_MANIFEST))
    expected_copies = {
        str(row["local_path"]): {"path": str(row["local_path"]), "sha256": str(row["sha256"]).casefold(), "length": int(row["length"])}
        for row in rows
    }
    copies = gate.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != len(expected_copies):
        raise RuntimeError("root v33 gate public-copy count differs")
    actual_copies = {str(item.get("path")): item for item in copies if isinstance(item, dict)}
    if set(actual_copies) != set(expected_copies):
        raise RuntimeError("root v33 gate public-copy paths differ")
    for path, expected in expected_copies.items():
        actual = actual_copies[path]
        if str(actual.get("sha256") or "").casefold() != expected["sha256"] or int(actual.get("length", -1)) != expected["length"]:
            raise RuntimeError(f"root v33 public-copy binding differs: {path}")
        source = ROOT / path
        if not source.is_file() or source.stat().st_size != expected["length"] or sha256_file(source) != expected["sha256"]:
            raise RuntimeError(f"root v33 public-copy bytes changed: {path}")
    return {"path": rel(ROOT_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_INPUT_ACCEPTANCE), "binding_count": len(actual_bindings), "public_copy_count": len(actual_copies), "gate": gate}


def guard_prepared(builder: object) -> dict:
    prep = read_json(PREPARATION, "v33 input preparation")
    preflight = read_json(PREFLIGHT, "v33 preflight")
    if preflight.get("status") != "preflight_passed_waiting_root_v33_input_acceptance":
        raise RuntimeError("v33 preflight is not waiting for root acceptance")
    if prep.get("status") != "prepared_waiting_root_v33_input_acceptance":
        raise RuntimeError("v33 preparation is not waiting for root acceptance")
    expected_builder = str(prep.get("builder", {}).get("sha256") or "")
    if not expected_builder or sha256_file(BUILDER_PATH) != expected_builder:
        raise RuntimeError("v33 builder changed after preparation")
    for name, wanted in (("exporter", EXPECTED_EXPORTER_SHA256), ("historical_exhibits", EXPECTED_HISTORICAL_EXHIBITS_SHA256)):
        path = builder.EXPORTER if name == "exporter" else builder.HISTORICAL_EXHIBITS
        if sha256_file(path) != wanted:
            raise RuntimeError(f"v33 {name} changed")
    for entry in (prep.get("new_maps") or {}).values():
        path = ROOT / str(entry.get("path") or "")
        if not path.is_file() or sha256_file(path) != str(entry.get("sha256") or "").casefold():
            raise RuntimeError(f"v33 prepared map changed: {path}")
    for key in ("source_byte_audit", "impact"):
        entry = preflight.get(key) or {}
        path = ROOT / str(entry.get("path") or "")
        if not path.is_file() or sha256_file(path) != str(entry.get("sha256") or "").casefold():
            raise RuntimeError(f"v33 prepared {key} changed: {path}")
    frozen_pins = preflight.get("frozen_pins") or {}
    for raw in frozen_pins.values():
        if not isinstance(raw, dict) or not raw.get("path"):
            continue
        path = ROOT / str(raw["path"])
        if not path.is_file() or sha256_file(path) != str(raw.get("sha256") or "").casefold():
            raise RuntimeError(f"v33 frozen pin changed: {path}")
    return preflight


def guard_outputs() -> None:
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists() or BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v33 output, partial output, or build receipt")


def write_receipt(payload: dict) -> None:
    if BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v33 build receipt: {BUILD_RECEIPT}")
    BUILD_RECEIPT.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _expected_postbuild(gate: dict) -> dict:
    values = gate.get("expected_after_export") or gate.get("postbuild_expectations") or gate.get("expectations")
    if not isinstance(values, dict):
        raise RuntimeError("root v33 input gate has no post-export expectations")
    required = ("primary_overlays", "supplement_overlays", "total_overlays", "declared_files", "actual_files")
    missing = [key for key in required if values.get(key) is None]
    if missing:
        raise RuntimeError(f"root v33 post-export expectations missing: {', '.join(missing)}")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_export_go:
        parser.error("v33 export requires both --go and --root-export-go")
    if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
        raise RuntimeError("v33 source site or source manifest is missing")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v33 export floor before start: {free_before}")
    builder = load_builder()
    preflight = guard_prepared(builder)
    root_acceptance = validate_root_acceptance(builder, preflight)
    expected_after_export = _expected_postbuild(root_acceptance["gate"])
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v33 export floor immediately before exporter: {free_before_export}")
    frozen, old_primary_maps, old_supplement_maps, _ = builder.frozen_maps()
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = "python.exe -X utf8 research/continuous-recovery-20261018/integration/v33/execute_v33.py --go --root-export-go"
    export_started = False
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        if sha256_file(ROOT / "tools/export_github_pages.py") != EXPECTED_EXPORTER_SHA256:
            raise RuntimeError("current exporter SHA changed before v33 export")
        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=old_primary_maps + (PRIMARY_MAP,),
            supplement_image_source_maps=old_supplement_maps + (SUPPLEMENT_MAP,),
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=GUIDE_COLLECTION_MAP,
        )
        provenance_path = OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v33 output provenance")
        stats = provenance.get("stats") or {}
        for key in ("primary_overlays", "supplement_overlays", "total_overlays"):
            provenance_key = {"primary_overlays": "primary_image_overlay_records", "supplement_overlays": "supplement_image_overlay_records", "total_overlays": "image_overlay_records"}[key]
            if stats.get(provenance_key) != expected_after_export[key]:
                raise RuntimeError(f"v33 provenance {provenance_key}={stats.get(provenance_key)!r}, expected {expected_after_export[key]!r}")
        if stats.get("output_files") != expected_after_export["declared_files"]:
            raise RuntimeError(f"v33 declared output files {stats.get('output_files')!r} != {expected_after_export['declared_files']!r}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != expected_after_export["actual_files"]:
            raise RuntimeError(f"v33 actual files {actual_files} != {expected_after_export['actual_files']}")
        receipt = {
            "schema": V33_SCHEMA,
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": {key: value for key, value in root_acceptance.items() if key != "gate"},
            "preflight_sha256": sha256_file(PREFLIGHT),
            "expected_after_export": expected_after_export,
            "build": result,
            "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_path": rel(provenance_path), "provenance_sha256": sha256_file(provenance_path)},
            "output": rel(OUTPUT),
            "disk_free_before_bytes": free_before_export,
            "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        if export_started and not BUILD_RECEIPT.exists():
            write_receipt({
                "schema": V33_SCHEMA,
                "executed_by": "/root/local_recovery_20261018",
                "command": command,
                "checked_utc_start": started,
                "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "export_started": True,
                "export_completed": False,
                "published": False,
                "network_requests_by_builder": 0,
                "root_input_acceptance": {key: value for key, value in root_acceptance.items() if key != "gate"},
                "preflight_sha256": sha256_file(PREFLIGHT),
                "error": f"{type(exc).__name__}: {exc}",
                "output": rel(OUTPUT) if OUTPUT.exists() else None,
                "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
                "disk_free_before_bytes": free_before_export,
                "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
                "disk_free_floor_bytes": MIN_FREE_BYTES,
            })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
