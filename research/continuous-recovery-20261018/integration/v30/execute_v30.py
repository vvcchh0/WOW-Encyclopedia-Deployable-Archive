#!/usr/bin/env python3
"""Guarded one-shot v30 exporter wrapper.

This file is intentionally separate from ``build_pages_v30.py``.  The builder
only prepares maps and preflight data.  This wrapper may call the exporter only
when a root input-acceptance receipt has accepted every immutable binding and
the unified v30 preflight/image/network fields, and only when the v30 output,
partial output, and worker receipt are absent.  Explicit export authorization
is supplied by the command-line pair ``--go --root-export-go``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
BUILDER_PATH = INTEGRATION / "build_pages_v30.py"
V30_PRIMARY_MAP = INTEGRATION / "v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = INTEGRATION / "v30-supplement-source-map.json"
V30_IMPACT = INTEGRATION / "v30-impact-estimate.json"
V30_SOURCE_AUDIT = INTEGRATION / "v30-source-byte-audit.json"
V30_PREPARATION = INTEGRATION / "v30-input-preparation.json"
V30_PREFLIGHT = INTEGRATION / "v30-preflight.json"
V30_PROPOSAL = INTEGRATION / "v30-input-proposal.md"
V30_RUNNER_NOTE = INTEGRATION / "v30-runner-preparation.md"
V30_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v30"
V30_BUILD_RECEIPT = INTEGRATION / "v30-build-receipt.json"
ROOT_V30_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v30-input-acceptance.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_BUILDER_SHA256 = "f9fbc95042d6f0e4894d280af6de5276db41746ccc6dc0fe5a8e8d3f6b027026"
EXPECTED_PRIMARY_MAP_SHA256 = "8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e"
EXPECTED_SUPPLEMENT_MAP_SHA256 = "53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0"
EXPECTED_IMPACT_SHA256 = "0e3775503bb36318d47d82f0f7512216d569080000c404a9d78148ddcafe012a"
EXPECTED_SOURCE_AUDIT_SHA256 = "a43d06dc83ee795b574cd59cf186e1389cd410fbefbd8fd6d211ebc8bad2a8ba"
EXPECTED_PREPARATION_SHA256 = "488170490743c5469f05088665dc9b60afc720af168626073f3ca18be3f2d803"
EXPECTED_PREFLIGHT_SHA256 = "ac821017c8b9a878db732f3d0cde8100b7677d5a0249d65f7dbf3b06f6a45e18"
EXPECTED_PROPOSAL_SHA256 = "8a01b5a95d634bd97544ded92e37682b2bbec031ad7a2d7e7bac03af40a4b67f"
EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V29_PROVENANCE_SHA256 = "793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_EXPORTER_SHA256 = "18f7239eb6af00a324be18f2e00192172fb2023856a39e02dd3c694a4bafe185"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_ARMORY_ACCEPTANCE_SHA256 = "863a141f1082ae76b17e7d5009e03959f066589ac39797483a530718036605cd"
EXPECTED_NEW_IMAGES = 33
EXPECTED_NEW_BYTES = 156857
EXPECTED_PRIMARY = 247
EXPECTED_SUPPLEMENT = 89
EXPECTED_TOTAL = 336
EXPECTED_DECLARED = 8794
EXPECTED_ACTUAL = 8795


def sha256_file(path: Path) -> str:
    import hashlib

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
    actual = sha256_file(BUILDER_PATH)
    if actual != EXPECTED_BUILDER_SHA256:
        raise RuntimeError(f"v30 builder SHA changed: {actual} != {EXPECTED_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_v30_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v30 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_prepared_inputs(builder) -> dict:
    expected = {
        BUILDER_PATH: EXPECTED_BUILDER_SHA256,
        V30_PRIMARY_MAP: EXPECTED_PRIMARY_MAP_SHA256,
        V30_SUPPLEMENT_MAP: EXPECTED_SUPPLEMENT_MAP_SHA256,
        V30_IMPACT: EXPECTED_IMPACT_SHA256,
        V30_SOURCE_AUDIT: EXPECTED_SOURCE_AUDIT_SHA256,
        V30_PREPARATION: EXPECTED_PREPARATION_SHA256,
        V30_PREFLIGHT: EXPECTED_PREFLIGHT_SHA256,
        ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py": EXPECTED_V28_BUILDER_SHA256,
        ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json": EXPECTED_V28_PRIMARY_MAP_SHA256,
        ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json": EXPECTED_V28_PROVENANCE_SHA256,
        ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json": EXPECTED_V29_PRIMARY_MAP_SHA256,
        ROOT / ".scratch/pages-resources-20261018-v29/export-provenance.json": EXPECTED_V29_PROVENANCE_SHA256,
        SOURCE_MANIFEST: EXPECTED_SOURCE_MANIFEST_SHA256,
        ROOT / "tools/export_github_pages.py": EXPECTED_EXPORTER_SHA256,
        ROOT / "tools/historical_exhibits.py": EXPECTED_HISTORICAL_EXHIBITS_SHA256,
    }
    hashes = {}
    for path, wanted in expected.items():
        actual = sha256_file(path)
        if actual != wanted:
            raise RuntimeError(f"prepared binding changed: {rel(path)} {actual} != {wanted}")
        hashes[rel(path)] = actual
    preflight = read_json(V30_PREFLIGHT, "v30 preflight")
    if preflight.get("status") != "preflight_passed_waiting_root_v30_input_acceptance":
        raise RuntimeError("v30 preflight is not the frozen waiting state")
    expected_after = preflight.get("expected_after_export") or {}
    if {
        "primary_overlays": expected_after.get("primary_overlays"),
        "supplement_overlays": expected_after.get("supplement_overlays"),
        "total_overlays": expected_after.get("total_overlays"),
        "declared_files": expected_after.get("declared_files"),
        "actual_files": expected_after.get("actual_files"),
    } != {
        "primary_overlays": EXPECTED_PRIMARY,
        "supplement_overlays": EXPECTED_SUPPLEMENT,
        "total_overlays": EXPECTED_TOTAL,
        "declared_files": EXPECTED_DECLARED,
        "actual_files": EXPECTED_ACTUAL,
    }:
        raise RuntimeError("v30 preflight expected counts changed")
    return {"hashes": hashes, "preflight_sha256": EXPECTED_PREFLIGHT_SHA256}


def validate_root_acceptance(prepared: dict, builder, frozen) -> dict:
    receipt = read_json(ROOT_V30_INPUT_ACCEPTANCE, "root v30 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v30 input acceptance is not accepted")
    bindings = {
        str(item.get("path")): str(item.get("sha256") or "").casefold()
        for item in receipt.get("map_bindings", [])
        if isinstance(item, dict)
    }
    if not bindings:
        raise RuntimeError("root v30 input acceptance has no map_bindings")
    for path_text, expected in bindings.items():
        if len(expected) != 64 or Path(path_text).is_absolute():
            raise RuntimeError(f"root v30 binding is not a valid workspace-relative SHA: {path_text}")
        path = (ROOT / Path(path_text)).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"root v30 binding escapes workspace: {path_text}") from exc
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"root v30 binding changed: {path_text}: {actual} != {expected}")
    required = {
        rel(BUILDER_PATH): EXPECTED_BUILDER_SHA256,
        rel(Path(__file__)): sha256_file(Path(__file__)),
        rel(V30_PRIMARY_MAP): EXPECTED_PRIMARY_MAP_SHA256,
        rel(V30_SUPPLEMENT_MAP): EXPECTED_SUPPLEMENT_MAP_SHA256,
        rel(V30_IMPACT): EXPECTED_IMPACT_SHA256,
        rel(V30_SOURCE_AUDIT): EXPECTED_SOURCE_AUDIT_SHA256,
        rel(V30_PREPARATION): EXPECTED_PREPARATION_SHA256,
        rel(V30_PREFLIGHT): EXPECTED_PREFLIGHT_SHA256,
        rel(V30_PROPOSAL): EXPECTED_PROPOSAL_SHA256,
        rel(V30_RUNNER_NOTE): sha256_file(V30_RUNNER_NOTE),
        rel(ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"): EXPECTED_V28_BUILDER_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"): EXPECTED_V28_PRIMARY_MAP_SHA256,
        rel(ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"): EXPECTED_V28_PROVENANCE_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"): EXPECTED_V29_PRIMARY_MAP_SHA256,
        rel(ROOT / ".scratch/pages-resources-20261018-v29/export-provenance.json"): EXPECTED_V29_PROVENANCE_SHA256,
        rel(SOURCE_MANIFEST): EXPECTED_SOURCE_MANIFEST_SHA256,
        rel(ROOT / "tools/export_github_pages.py"): EXPECTED_EXPORTER_SHA256,
        rel(ROOT / "tools/historical_exhibits.py"): EXPECTED_HISTORICAL_EXHIBITS_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-armory-origin-tool-acceptance.json"): EXPECTED_ARMORY_ACCEPTANCE_SHA256,
    }
    for path in tuple(frozen.PRIMARY_MAPS) + tuple(frozen.SUPPLEMENT_MAPS):
        required[rel(path)] = sha256_file(path)
    required[rel(builder.V29_PRIMARY_MAP)] = sha256_file(builder.V29_PRIMARY_MAP)
    for path in (builder.V28_PROVENANCE, builder.V28_RECEIPT, builder.V29_PREPARATION, builder.V29_PREFLIGHT, builder.V29_RECEIPT, builder.V29_PROVENANCE):
        required[rel(path)] = sha256_file(path)
    source_receipt_paths = []
    for receipt_path in builder.V30_RECEIPTS:
        required[rel(receipt_path)] = sha256_file(receipt_path)
        copy_receipt = read_json(receipt_path, receipt_path.name)
        source_binding = copy_receipt.get("source_acceptance") or {}
        source_path = ROOT / str(source_binding.get("path") or "")
        source_receipt_paths.append(source_path)
        required[rel(source_path)] = sha256_file(source_path)
    for path, wanted in required.items():
        if bindings.get(path) != wanted:
            raise RuntimeError(f"root v30 binding mismatch: {path}")
    if str(receipt.get("preflight_sha256") or "").casefold() != prepared["preflight_sha256"]:
        raise RuntimeError("root v30 preflight SHA mismatch")
    if receipt.get("new_images") != EXPECTED_NEW_IMAGES or receipt.get("image_bytes") != EXPECTED_NEW_BYTES:
        raise RuntimeError("root v30 accepted image count/bytes changed")
    if receipt.get("network_requests") != 0 or receipt.get("export_executed") is not False:
        raise RuntimeError("root v30 acceptance records network/export activity")
    copies = receipt.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("root v30 acceptance must contain 33 public image copies")
    for index, copy in enumerate(copies):
        if not isinstance(copy, dict):
            raise RuntimeError(f"root v30 public copy {index} is not an object")
        path_text = str(copy.get("path") or "")
        if Path(path_text).is_absolute():
            raise RuntimeError(f"root v30 public copy {index} is not workspace-relative")
        path = (ROOT / Path(path_text)).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"root v30 public copy {index} escapes workspace") from exc
        expected = str(copy.get("sha256") or "").casefold()
        length = int(copy.get("length", -1))
        if len(expected) != 64 or not path.is_file() or path.stat().st_size != length or sha256_file(path) != expected:
            raise RuntimeError(f"root v30 public copy changed: {path_text}")
    return {"path": rel(ROOT_V30_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_V30_INPUT_ACCEPTANCE), "binding_count": len(bindings), "public_copy_count": len(copies)}


def guard_outputs() -> None:
    if V30_OUTPUT.exists() or V30_OUTPUT.with_name(V30_OUTPUT.name + ".partial").exists() or V30_BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v30 output, partial output, or build receipt")


def write_receipt(payload: dict) -> None:
    if V30_BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v30 build receipt: {V30_BUILD_RECEIPT}")
    V30_BUILD_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_export_go:
        parser.error("v30 export requires both --go and --root-export-go")
    if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
        raise RuntimeError("v30 source site or source manifest is missing")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor before v30 export: {free_before}")
    builder = load_builder()
    frozen = builder.load_frozen_v28()
    prepared = validate_prepared_inputs(builder)
    root_acceptance = validate_root_acceptance(prepared, builder, frozen)
    guard_outputs()
    closure = builder.validate_frozen_v29_closure(frozen)
    primary_map = read_json(V30_PRIMARY_MAP, "v30 primary map")
    supplement_map = read_json(V30_SUPPLEMENT_MAP, "v30 supplement map")
    builder.validate_no_overlap(frozen, primary_map, supplement_map)
    builder.validate_map(frozen, primary_map, role="primary_image_overlay", expected_count=19, expected_bytes=70546)
    builder.validate_map(frozen, supplement_map, role="supplement_image_overlay", expected_count=14, expected_bytes=86311)
    loader = builder.loader_preflight(frozen, primary_map, supplement_map)
    if loader["primary_overlay_records"] != EXPECTED_PRIMARY or loader["supplement_overlay_records"] != EXPECTED_SUPPLEMENT or loader["total_overlay_records"] != EXPECTED_TOTAL:
        raise RuntimeError("v30 loader closure counts changed")
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor immediately before v30 export: {free_before_export}")
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    export_started = False
    command = "python.exe -X utf8 research/continuous-recovery-20261018/integration/v30/execute_v30.py --go --root-export-go"
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=V30_OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=tuple(frozen.PRIMARY_MAPS) + (builder.V29_PRIMARY_MAP, V30_PRIMARY_MAP),
            supplement_image_source_maps=tuple(frozen.SUPPLEMENT_MAPS) + (V30_SUPPLEMENT_MAP,),
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=GUIDE_COLLECTION_MAP,
        )
        provenance_path = V30_OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v30 output provenance")
        stats = provenance.get("stats") or {}
        expected_stats = {
            "source_records": 8357,
            "image_overlay_records": EXPECTED_TOTAL,
            "primary_image_overlay_records": EXPECTED_PRIMARY,
            "supplement_image_overlay_records": EXPECTED_SUPPLEMENT,
            "output_files": EXPECTED_DECLARED,
        }
        for key, expected in expected_stats.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v30 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in V30_OUTPUT.rglob("*") if path.is_file())
        if actual_files != EXPECTED_ACTUAL:
            raise RuntimeError(f"v30 actual file count {actual_files}, expected {EXPECTED_ACTUAL}")
        receipt = {
            "schema": "wow-recovery.integration.v30-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": root_acceptance,
            "frozen_v29_closure": closure,
            "loader_preflight": loader,
            "build": result,
            "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_path": rel(provenance_path), "provenance_sha256": sha256_file(provenance_path)},
            "output": rel(V30_OUTPUT),
            "disk_free_before_bytes": free_before_export,
            "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        if export_started and not V30_BUILD_RECEIPT.exists():
            failure = {
                "schema": "wow-recovery.integration.v30-build-receipt.v1",
                "executed_by": "/root/local_recovery_20261018",
                "command": command,
                "checked_utc_start": started,
                "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "export_started": True,
                "export_completed": False,
                "published": False,
                "network_requests_by_builder": 0,
                "root_input_acceptance": root_acceptance,
                "error": f"{type(exc).__name__}: {exc}",
                "output": rel(V30_OUTPUT) if V30_OUTPUT.exists() else None,
                "partial_exists": V30_OUTPUT.with_name(V30_OUTPUT.name + ".partial").exists(),
                "disk_free_before_bytes": free_before_export,
                "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
                "disk_free_floor_bytes": MIN_FREE_BYTES,
            }
            write_receipt(failure)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
