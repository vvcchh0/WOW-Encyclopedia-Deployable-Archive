#!/usr/bin/env python3
"""Guarded one-shot v34 exporter wrapper.

The wrapper never prepares maps or reads pending sources.  It requires a
separately accepted root v34 input gate and the explicit ``--go
--root-export-go`` pair before calling the exporter once.
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
BUILDER_PATH = INTEGRATION / "build_pages_v34.py"
RUNNER_PATH = Path(__file__).resolve()
PRIMARY_MAP = INTEGRATION / "v34-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v34-supplement-source-map.json"
SOURCE_CLOSURE = INTEGRATION / "v34-source-closure.json"
PREPARATION = INTEGRATION / "v34-input-preparation.json"
PREFLIGHT = INTEGRATION / "v34-preflight.json"
PROPOSAL = INTEGRATION / "v34-input-proposal.md"
RUNNER_NOTE = INTEGRATION / "v34-runner-preparation.md"
VERIFICATION = INTEGRATION / "v34-preparation-verification.json"
VERIFICATION_R2 = INTEGRATION / "v34-preparation-verification-r2.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261019-v34"
BUILD_RECEIPT = INTEGRATION / "v34-build-receipt.json"
ROOT_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-v34-input-acceptance.json"
MIN_FREE_BYTES = 11_005_853_696
MAX_OUTPUT_BYTES = 650_000_000
START_DEADLINE = datetime(2026, 10, 19, 13, 30, 0, tzinfo=timezone.utc)
EXPECTED_EXPORTER_SHA256 = "e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
V34_SCHEMA = "wow-recovery.integration.v34-build-receipt.v1"


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
    spec = importlib.util.spec_from_file_location("wow_recovery_v34_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v34 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def required_bindings(builder: object) -> dict[str, str]:
    primary_maps, supplement_maps = builder.closure_maps()
    paths = [
        BUILDER_PATH,
        RUNNER_PATH,
        PRIMARY_MAP,
        SUPPLEMENT_MAP,
        SOURCE_CLOSURE,
        PREPARATION,
        PREFLIGHT,
        PROPOSAL,
        RUNNER_NOTE,
        VERIFICATION,
        VERIFICATION_R2,
        builder.SOURCE_MANIFEST,
        builder.ORIGINAL_MANIFEST,
        builder.GUIDE_PREVIEW_MAP,
        builder.GUIDE_COLLECTION_MAP,
        builder.V28_BUILDER,
        builder.V29_PRIMARY_MAP,
        builder.V30_PRIMARY_MAP,
        builder.V30_SUPPLEMENT_MAP,
        builder.V32_PRIMARY_MAP,
        builder.V32_SUPPLEMENT_MAP,
        builder.V33_PRIMARY_MAP,
        builder.V33_SUPPLEMENT_MAP,
        builder.V33_PREPARATION,
        builder.V33_PREFLIGHT,
        builder.V33_BUILD_RECEIPT,
        builder.V33_PROVENANCE,
        builder.V33_INPUT_ACCEPTANCE,
        builder.V33_BROWSER_ACCEPTANCE,
        builder.V33_PORTABLE_ACCEPTANCE,
        builder.CONTEST_TOOL_ACCEPTANCE,
        builder.EXPORTER,
        builder.HISTORICAL_EXHIBITS,
    ]
    paths.extend(primary_maps)
    paths.extend(supplement_maps)
    result: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"required v34 binding is missing: {path}")
        result[rel(path)] = sha256_file(path)
    return result


def validate_root_acceptance(builder: object, preflight: dict) -> dict:
    gate = read_json(ROOT_INPUT_ACCEPTANCE, "root v34 input acceptance")
    if gate.get("accepted") is not True:
        raise RuntimeError("root v34 input acceptance is not accepted")
    if str(gate.get("preflight_sha256") or "").casefold() != sha256_file(PREFLIGHT):
        raise RuntimeError("root v34 preflight SHA mismatch")
    if gate.get("network_requests") not in {0, None} or gate.get("export_executed") is not False:
        raise RuntimeError("root v34 gate records network/export activity")
    for key in ("new_images", "image_bytes"):
        if key in gate and gate.get(key) != 0:
            raise RuntimeError(f"root v34 gate {key} is not zero")
    expected = required_bindings(builder)
    actual = {str(item.get("path")): str(item.get("sha256") or "").casefold() for item in gate.get("map_bindings", []) if isinstance(item, dict)}
    for path, wanted in expected.items():
        if actual.get(path) != wanted.casefold():
            raise RuntimeError(f"root v34 binding mismatch: {path}")
    copies = gate.get("public_image_copies")
    if copies not in (None, []):
        raise RuntimeError("v34 has no accepted public image copies")
    return {"path": rel(ROOT_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_INPUT_ACCEPTANCE), "binding_count": len(actual), "gate": gate}


def guard_prepared(builder: object) -> dict:
    preparation = read_json(PREPARATION, "v34 input preparation")
    preflight = read_json(PREFLIGHT, "v34 preflight")
    if preparation.get("status") != "prepared_waiting_root_v34_input_acceptance":
        raise RuntimeError("v34 preparation is not waiting for root acceptance")
    if preflight.get("status") != "preflight_passed_waiting_root_v34_input_acceptance":
        raise RuntimeError("v34 preflight is not waiting for root acceptance")
    if str(preparation.get("builder", {}).get("sha256") or "") != sha256_file(BUILDER_PATH):
        raise RuntimeError("v34 builder changed after preparation")
    for path, expected in ((PRIMARY_MAP, preparation["new_maps"]["primary"]["sha256"]), (SUPPLEMENT_MAP, preparation["new_maps"]["supplement"]["sha256"]), (SOURCE_CLOSURE, preparation["source_closure"]["sha256"])):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"v34 prepared binding changed: {path}")
    if sha256_file(builder.EXPORTER) != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("current exporter SHA changed")
    if sha256_file(builder.HISTORICAL_EXHIBITS) != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError("historical exhibits SHA changed")
    return preflight


def guard_outputs() -> None:
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists() or BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v34 output, partial output, or build receipt")


def expected_postbuild(gate: dict) -> dict:
    values = gate.get("expected_after_export") or gate.get("postbuild_expectations") or gate.get("expectations")
    if not isinstance(values, dict):
        raise RuntimeError("root v34 input gate has no post-export expectations")
    required = ("primary_overlays", "supplement_overlays", "total_overlays", "declared_files", "actual_files")
    if any(values.get(key) is None for key in required):
        raise RuntimeError("root v34 post-export expectations are incomplete")
    return values


def write_receipt(payload: dict) -> None:
    if BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v34 build receipt: {BUILD_RECEIPT}")
    BUILD_RECEIPT.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_export_go:
        parser.error("v34 export requires both --go and --root-export-go")
    now = datetime.now(timezone.utc)
    if now >= START_DEADLINE:
        raise RuntimeError(
            f"v34 export start deadline passed: {now.isoformat()} >= {START_DEADLINE.isoformat()}"
        )
    if not builder_source_site().is_dir() or not builder_source_manifest().is_file():
        raise RuntimeError("frozen v34 source site or source manifest is missing")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v34 export floor before start: {free_before}")
    builder = load_builder()
    preflight = guard_prepared(builder)
    root_acceptance = validate_root_acceptance(builder, preflight)
    expected = expected_postbuild(root_acceptance["gate"])
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v34 export floor immediately before exporter: {free_before_export}")
    primary_maps, supplement_maps = builder.closure_maps()
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = "python.exe -X utf8 research/continuous-recovery-20261019/integration/v34/execute_v34.py --go --root-export-go"
    export_started = False
    try:
        if str(ROOT / "tools") not in sys.path:
            sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        if sha256_file(builder.EXPORTER) != EXPECTED_EXPORTER_SHA256:
            raise RuntimeError("current exporter SHA changed before v34 export")
        export_started = True
        result = export_github_pages.export_pages(
            source_site=builder.SOURCE_SITE,
            manifest_path=builder.SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=builder.BASE_PATH,
            workspace_root=ROOT,
            max_bytes=MAX_OUTPUT_BYTES,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=primary_maps + (PRIMARY_MAP,),
            supplement_image_source_maps=supplement_maps + (SUPPLEMENT_MAP,),
            allow_later_image_supplements=True,
            guide_preview_map=builder.GUIDE_PREVIEW_MAP,
            guide_image_collection_map=builder.GUIDE_COLLECTION_MAP,
        )
        provenance_path = OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v34 output provenance")
        stats = provenance.get("stats") or {}
        checks = {
            "primary_image_overlay_records": expected["primary_overlays"],
            "supplement_image_overlay_records": expected["supplement_overlays"],
            "image_overlay_records": expected["total_overlays"],
            "output_files": expected["declared_files"],
            "contest_navtree_fallback_repaired": 1,
        }
        for key, wanted in checks.items():
            if stats.get(key) != wanted:
                raise RuntimeError(f"v34 provenance {key}={stats.get(key)!r}, expected {wanted!r}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != expected["actual_files"]:
            raise RuntimeError(f"v34 actual files {actual_files} != {expected['actual_files']}")
        receipt = {
            "schema": V34_SCHEMA,
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
            "expected_after_export": expected,
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
                "schema": V34_SCHEMA,
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


def builder_source_site() -> Path:
    return ROOT / ".scratch/offline-navigation-20261015-v15/site"


def builder_source_manifest() -> Path:
    return ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"


if __name__ == "__main__":
    raise SystemExit(main())
