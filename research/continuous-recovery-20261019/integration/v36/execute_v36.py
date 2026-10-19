#!/usr/bin/env python3
"""Guarded one-shot v36 exporter wrapper.

Preparation and export are deliberately separate.  This file refuses to run
without the root-v36 acceptance gate and the explicit ``--go
--root-export-go`` pair; it calls the current exporter once and never writes
maps or preflight.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
INTEGRATION = Path(__file__).resolve().parent
BUILDER_PATH = INTEGRATION / "build_pages_v36.py"
RUNNER_PATH = Path(__file__).resolve()
PRIMARY_MAP = INTEGRATION / "v36-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v36-supplement-source-map.json"
SOURCE_CLOSURE = INTEGRATION / "v36-source-closure.json"
NATIVE_INPUT = INTEGRATION / "v36-native-ui-inputs.json"
PREPARATION = INTEGRATION / "v36-input-preparation.json"
PREFLIGHT = INTEGRATION / "v36-preflight.json"
PROPOSAL = INTEGRATION / "v36-input-proposal.md"
RUNNER_NOTE = INTEGRATION / "v36-runner-preparation.md"
OUTPUT = ROOT / ".scratch/pages-resources-20261019-v36"
BUILD_RECEIPT = INTEGRATION / "v36-build-receipt.json"
ROOT_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-v36-input-acceptance.json"
MIN_FREE_BYTES = 11_005_853_696
START_DEADLINE = datetime(2026, 10, 19, 13, 30, 0, tzinfo=timezone.utc)
EXPECTED_EXPORTER_SHA256 = "60fa3cb3279bd2478de73d861fc648efaeda760ca8ee609e4ba3cf3b3030f35d"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "4d62d47526fe5f58abb1ed756cc4c62ffa0a11d3d495d25a3c6af7b0e74a71f0"
EXPECTED_NEW_IMAGES = 51
EXPECTED_NEW_BYTES = 874533
V36_SCHEMA = "wow-recovery.integration.v36-build-receipt.v1"


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
    spec = importlib.util.spec_from_file_location("wow_recovery_v36_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v36 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def required_bindings(builder: object) -> dict[str, str]:
    primary, supplement = builder.closure_maps()
    paths = [
        BUILDER_PATH, RUNNER_PATH, PRIMARY_MAP, SUPPLEMENT_MAP, SOURCE_CLOSURE,
        NATIVE_INPUT, PREPARATION, PREFLIGHT, PROPOSAL, RUNNER_NOTE,
        builder.SOURCE_MANIFEST, builder.ORIGINAL_MANIFEST, builder.GUIDE_PREVIEW_MAP,
        builder.GUIDE_COLLECTION_MAP, builder.V28_BUILDER, builder.V29_PRIMARY_MAP,
        builder.V30_PRIMARY_MAP, builder.V30_SUPPLEMENT_MAP, builder.V32_PRIMARY_MAP,
        builder.V32_SUPPLEMENT_MAP, builder.V33_PRIMARY_MAP, builder.V33_SUPPLEMENT_MAP,
        builder.V34_PRIMARY_MAP, builder.V34_SUPPLEMENT_MAP, builder.V34_PREPARATION,
        builder.V34_PREFLIGHT, builder.V34_BUILD_RECEIPT, builder.V34_PROVENANCE,
        builder.V34_INPUT_ACCEPTANCE, builder.V34_R2_REPORT, builder.V34_R3B_REPORT,
        builder.CONTEST_TOOL_ACCEPTANCE, builder.V35_PRIMARY_MAP, builder.V35_SUPPLEMENT_MAP, builder.V35_SOURCE_CLOSURE, builder.V35_PROVENANCE, builder.V35_LOCAL_ACCEPTANCE, builder.V35_PAGES_ONLINE_ACCEPTANCE, builder.EXPORTER, builder.HISTORICAL_EXHIBITS,
    ]
    paths.extend(primary)
    paths.extend(supplement)
    for batch in builder.NEWS_BATCHES:
        paths.extend((batch["source"], batch["public"]))
    result: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"required v36 binding is missing: {path}")
        result[rel(path)] = sha256_file(path)
    return result


def guard_prepared(builder: object) -> dict:
    preparation = read_json(PREPARATION, "v36 input preparation")
    preflight = read_json(PREFLIGHT, "v36 preflight")
    if preparation.get("status") != "prepared_waiting_root_v36_input_acceptance":
        raise RuntimeError("v36 preparation is not waiting for root acceptance")
    if preflight.get("status") != "preflight_passed_waiting_root_v36_input_acceptance":
        raise RuntimeError("v36 preflight is not waiting for root acceptance")
    if preparation.get("builder", {}).get("sha256") != sha256_file(BUILDER_PATH):
        raise RuntimeError("v36 builder changed after preparation")
    if preparation.get("runner", {}).get("sha256") != sha256_file(RUNNER_PATH):
        raise RuntimeError("v36 runner changed after preparation")
    for path, expected in (
        (PRIMARY_MAP, preparation["new_maps"]["primary"]["sha256"]),
        (SUPPLEMENT_MAP, preparation["new_maps"]["supplement"]["sha256"]),
        (SOURCE_CLOSURE, preparation["source_closure"]["sha256"]),
        (NATIVE_INPUT, preparation["native_ui_input"]["sha256"]),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"v36 prepared binding changed: {path}")
    if sha256_file(builder.EXPORTER) != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("current exporter SHA changed")
    if sha256_file(builder.HISTORICAL_EXHIBITS) != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError("historical exhibits SHA changed")
    return preflight


def validate_root_acceptance(builder: object) -> dict:
    gate = read_json(ROOT_INPUT_ACCEPTANCE, "root v36 input acceptance")
    if gate.get("accepted") is not True:
        raise RuntimeError("root v36 input acceptance is not accepted")
    if str(gate.get("preflight_sha256") or "").casefold() != sha256_file(PREFLIGHT):
        raise RuntimeError("root v36 preflight SHA mismatch")
    if gate.get("new_images") != EXPECTED_NEW_IMAGES or gate.get("image_bytes") != EXPECTED_NEW_BYTES:
        raise RuntimeError("root v36 new image count/bytes mismatch")
    if gate.get("network_requests") not in {0, None} or gate.get("export_executed") is not False:
        raise RuntimeError("root v36 gate records network/export activity")
    expected = required_bindings(builder)
    actual = {str(item.get("path")): str(item.get("sha256") or "").casefold() for item in gate.get("map_bindings", []) if isinstance(item, dict)}
    for path, wanted in expected.items():
        if actual.get(path) != wanted.casefold():
            raise RuntimeError(f"root v36 binding mismatch: {path}")
    copies = gate.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("root v36 public image copy list is incomplete")
    expected_copies = {str(item.get("public_copy_path")): (str(item.get("sha256")).casefold(), int(item.get("length"))) for item in read_json(PRIMARY_MAP, "v36 primary map").get("items", [])}
    actual_copies = {str(item.get("path")): (str(item.get("sha256") or "").casefold(), int(item.get("length"))) for item in copies if isinstance(item, dict)}
    if actual_copies != expected_copies:
        raise RuntimeError("root v36 public image copy metadata differs")
    return {"path": rel(ROOT_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_INPUT_ACCEPTANCE), "gate": gate}


def guard_outputs() -> None:
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists() or BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v36 output, partial output, or build receipt")


def tree_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def write_receipt(payload: dict) -> None:
    if BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v36 build receipt: {BUILD_RECEIPT}")
    BUILD_RECEIPT.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def child_export() -> int:
    """Run the exporter once after the guarded parent has validated all inputs."""
    builder = load_builder()
    if sha256_file(builder.EXPORTER) != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("current exporter SHA changed before v36 child export")
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages
    primary_maps, supplement_maps = builder.closure_maps()
    result = export_github_pages.export_pages(
        source_site=builder.SOURCE_SITE,
        manifest_path=builder.SOURCE_MANIFEST,
        output=OUTPUT,
        base_path=export_github_pages.DEFAULT_BASE_PATH if hasattr(export_github_pages, "DEFAULT_BASE_PATH") else "/WOW-Encyclopedia-Deployable-Archive/",
        workspace_root=ROOT,
        max_bytes=None,
        min_free_bytes=MIN_FREE_BYTES,
        image_source_maps=primary_maps + (PRIMARY_MAP,),
        supplement_image_source_maps=supplement_maps + (SUPPLEMENT_MAP,),
        allow_later_image_supplements=True,
        guide_preview_map=builder.GUIDE_PREVIEW_MAP,
        guide_image_collection_map=builder.GUIDE_COLLECTION_MAP,
    )
    print(json.dumps(result, ensure_ascii=False, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    parser.add_argument("--child-export", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child_export:
        if __import__("os").environ.get("WOW_V36_CHILD") != "1":
            raise RuntimeError("v36 child export requires the guarded parent")
        return child_export()
    if not args.go or not args.root_export_go:
        parser.error("v36 export requires both --go and --root-export-go")
    now = datetime.now(timezone.utc)
    if now >= START_DEADLINE:
        raise RuntimeError(f"v36 export start deadline passed: {now.isoformat()} >= {START_DEADLINE.isoformat()}")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v36 export floor before start: {free_before}")
    builder = load_builder()
    preflight = guard_prepared(builder)
    root_acceptance = validate_root_acceptance(builder)
    gate = root_acceptance["gate"]
    expected = gate.get("expected_after_export") or gate.get("postbuild_expectations") or gate.get("expectations")
    if not isinstance(expected, dict):
        raise RuntimeError("root v36 gate has no post-export expectations")
    for key in ("primary_overlays", "supplement_overlays", "total_overlays", "declared_files", "actual_files"):
        if expected.get(key) is None:
            raise RuntimeError(f"root v36 post-export expectation missing: {key}")
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v36 export floor immediately before exporter: {free_before_export}")
    primary_maps, supplement_maps = builder.closure_maps()
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = "python.exe -X utf8 research/continuous-recovery-20261019/integration/v36/execute_v36.py --go --root-export-go"
    export_started = False
    try:
        if sha256_file(builder.EXPORTER) != EXPECTED_EXPORTER_SHA256:
            raise RuntimeError("current exporter SHA changed before v36 export")
        export_started = True
        child_env = dict(__import__("os").environ)
        child_env["WOW_V36_CHILD"] = "1"
        child_command = [sys.executable, "-X", "utf8", str(RUNNER_PATH), "--child-export"]
        child = subprocess.run(child_command, cwd=str(ROOT), env=child_env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, check=False)
        result = {"returncode": child.returncode, "stdout_tail": child.stdout[-12000:], "stderr_tail": child.stderr[-12000:], "timeout_seconds": 600}
        if child.returncode != 0:
            raise RuntimeError(f"v36 child exporter failed with return code {child.returncode}: {child.stderr[-2000:]}")
        free_after_export = shutil.disk_usage(ROOT).free
        if free_after_export < MIN_FREE_BYTES:
            raise RuntimeError(f"D below v36 export floor after child exporter: {free_after_export}")
        provenance_path = OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v36 output provenance")
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
                raise RuntimeError(f"v36 provenance {key}={stats.get(key)!r}, expected {wanted!r}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != expected["actual_files"]:
            raise RuntimeError(f"v36 actual files {actual_files} != {expected['actual_files']}")
        receipt = {
            "schema": V36_SCHEMA,
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": {"path": root_acceptance["path"], "sha256": root_acceptance["sha256"]},
            "preflight_sha256": sha256_file(PREFLIGHT),
            "expected_after_export": expected,
            "build": result,
            "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "tree_bytes": tree_bytes(OUTPUT), "provenance_path": rel(provenance_path), "provenance_sha256": sha256_file(provenance_path)},
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
            write_receipt({"schema": V36_SCHEMA, "executed_by": "/root/local_recovery_20261018", "command": command, "checked_utc_start": started, "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "export_started": True, "export_completed": False, "published": False, "network_requests_by_builder": 0, "root_input_acceptance": {"path": root_acceptance["path"], "sha256": root_acceptance["sha256"]}, "preflight_sha256": sha256_file(PREFLIGHT), "error": f"{type(exc).__name__}: {exc}", "output": rel(OUTPUT) if OUTPUT.exists() else None, "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(), "disk_free_before_bytes": free_before_export, "disk_free_after_bytes": shutil.disk_usage(ROOT).free, "disk_free_floor_bytes": MIN_FREE_BYTES})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
