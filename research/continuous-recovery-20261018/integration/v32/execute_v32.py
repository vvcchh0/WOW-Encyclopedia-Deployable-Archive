#!/usr/bin/env python3
"""Guarded one-shot v32 exporter wrapper.

The v32 builder is preparation-only.  This wrapper never regenerates maps or
preflight files and will call the exporter only after an independently
accepted root input receipt and the explicit ``--go --root-export-go`` pair.
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
BUILDER_PATH = INTEGRATION / "build_pages_v32.py"
PRIMARY_MAP = INTEGRATION / "v32-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v32-supplement-source-map.json"
IMPACT = INTEGRATION / "v32-impact-estimate.json"
SOURCE_AUDIT = INTEGRATION / "v32-source-byte-audit.json"
PREPARATION = INTEGRATION / "v32-input-preparation.json"
PREFLIGHT = INTEGRATION / "v32-preflight.json"
PROPOSAL = INTEGRATION / "v32-input-proposal.md"
RUNNER_NOTE = INTEGRATION / "v32-runner-preparation.md"
BUILD_RECEIPT = INTEGRATION / "v32-build-receipt.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261018-v32"
ROOT_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v32-input-acceptance.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_BUILDER_SHA256 = "b88a74633b488e07ac6570980733b1feab465523c7bf76da59cf304496dd2019"
EXPECTED_EXPORTER_SHA256 = "8c50b1574f24a0bd2b03492ae8fe0cb7d3c48a50a247ba70d9e1859d58672afb"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_PRIMARY_MAP_SHA256 = "939af6242b1e8cc9e62e09decd055b104cad7db4dcf17f42b9d002a4ed059318"
EXPECTED_SUPPLEMENT_MAP_SHA256 = "aeb391ba14f7debfbaf0a557a69bac693120ce2471da2d7162f5260602da6966"
EXPECTED_IMPACT_SHA256 = "f607bba28acee693ecaf6219e2ff233c436c457d270db37924145393f5f36fc5"
EXPECTED_SOURCE_AUDIT_SHA256 = "8d37cfb59f80e4f64b6af00a2b220dcef61cc20d1e8448576d9b1cd2f794f768"
EXPECTED_PREPARATION_SHA256 = "f83fa7053f2859ab87300f24f7438ced2db4aed2ef0b8689bd5b08148453c3bc"
EXPECTED_PREFLIGHT_SHA256 = "d8b81b9bf571e999b376a07401e74299a5c9808b2011758ff3e4a21ff90507cd"
EXPECTED_PROPOSAL_SHA256 = "4b018fc1210fcfb3152da9f1c2ca8d5547a5bb2de92e29d7ce33d59eb02339c5"
EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V30_PRIMARY_MAP_SHA256 = "8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e"
EXPECTED_V30_SUPPLEMENT_MAP_SHA256 = "53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0"
EXPECTED_V30_PROVENANCE_SHA256 = "b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85"
EXPECTED_V30_BUILD_RECEIPT_SHA256 = "87a5edd7075a339d15da1532ebc630f36e31fae48db1bbafcaa5b15982d9623c"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_PRIMARY = 350
EXPECTED_SUPPLEMENT = 89
EXPECTED_TOTAL = 439
EXPECTED_DECLARED = 8_897
EXPECTED_ACTUAL = 8_898
EXPECTED_NEW_IMAGES = 103
EXPECTED_NEW_BYTES = 1_734_198


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
    actual = sha256_file(BUILDER_PATH)
    if actual != EXPECTED_BUILDER_SHA256:
        raise RuntimeError(f"v32 builder SHA changed: {actual} != {EXPECTED_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_v32_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v32 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def required_bindings(builder) -> dict[str, str]:
    frozen = builder.load_v28_builder()
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
        builder.V28_PRIMARY_MAP,
        builder.V28_PROVENANCE,
        builder.V29_PRIMARY_MAP,
        builder.V29_PROVENANCE,
        builder.V30_PRIMARY_MAP,
        builder.V30_SUPPLEMENT_MAP,
        builder.V30_PROVENANCE,
        builder.V30_BUILD_RECEIPT,
        builder.ROOT_V30_INPUT_ACCEPTANCE,
        builder.V31_BUILDER,
        builder.V31_EXECUTOR,
        builder.V31_PRIMARY_MAP,
        builder.V31_SUPPLEMENT_MAP,
        builder.V31_IMPACT,
        builder.V31_SOURCE_AUDIT,
        builder.V31_PREPARATION,
        builder.V31_PREFLIGHT,
        builder.V31_PROPOSAL,
        builder.V31_RUNNER_NOTE,
        builder.V31_SUPERSEDED,
        builder.V31_RUNTIME_IMPACT,
        builder.SOURCE_MANIFEST,
        builder.GUIDE_PREVIEW_MAP,
        builder.GUIDE_COLLECTION_MAP,
        builder.EXPORTER,
        builder.HISTORICAL_EXHIBITS,
        builder.ROOT_POPUP_ACCEPTANCE,
        builder.ROOT_RETIRED_ACCEPTANCE,
        builder.ROOT_MASK_ACCEPTANCE,
    ]
    for path in tuple(frozen.PRIMARY_MAPS) + tuple(frozen.SUPPLEMENT_MAPS):
        paths.append(path)
    for receipt_path in builder.NEWS49_RECEIPTS + builder.NEXT70_RECEIPTS:
        receipt = read_json(receipt_path, receipt_path.name)
        paths.append(receipt_path)
        source = receipt.get("source_acceptance") or receipt.get("source_receipt")
        paths.append(ROOT / str(source["path"]))
        for row in receipt.get("accepted_images", []):
            paths.append(ROOT / str(row["local_path"]))
    # A path can be present in more than one closure list; preserve one binding.
    result: dict[str, str] = {}
    for path in paths:
        result[rel(path)] = sha256_file(path)
    return result


def validate_root_acceptance(builder) -> dict:
    gate = read_json(ROOT_INPUT_ACCEPTANCE, "root v32 input acceptance")
    if gate.get("accepted") is not True:
        raise RuntimeError("root v32 input acceptance is not accepted")
    if gate.get("preflight_sha256", "").casefold() != EXPECTED_PREFLIGHT_SHA256:
        raise RuntimeError("root v32 preflight SHA mismatch")
    if gate.get("new_images") != EXPECTED_NEW_IMAGES or gate.get("image_bytes") != EXPECTED_NEW_BYTES:
        raise RuntimeError("root v32 accepted count/bytes changed")
    if gate.get("network_requests") != 0 or gate.get("export_executed") is not False:
        raise RuntimeError("root v32 gate records network/export activity")
    bindings = {
        str(item.get("path")): str(item.get("sha256") or "").casefold()
        for item in gate.get("map_bindings", [])
        if isinstance(item, dict)
    }
    expected = required_bindings(builder)
    for path, wanted in expected.items():
        if bindings.get(path) != wanted:
            raise RuntimeError(f"root v32 binding mismatch: {path}")
    copies = gate.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("root v32 gate must list exactly 103 public image copies")
    for copy in copies:
        if not isinstance(copy, dict):
            raise RuntimeError("root v32 public copy is not an object")
        path = ROOT / str(copy.get("path") or "")
        wanted = str(copy.get("sha256") or "").casefold()
        if not path.is_file() or path.stat().st_size != int(copy.get("length", -1)) or sha256_file(path) != wanted:
            raise RuntimeError(f"root v32 public copy changed: {path}")
    return {"path": rel(ROOT_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_INPUT_ACCEPTANCE), "binding_count": len(bindings), "public_copy_count": len(copies)}


def guard_prepared(builder) -> dict:
    expected = {
        BUILDER_PATH: EXPECTED_BUILDER_SHA256,
        PRIMARY_MAP: EXPECTED_PRIMARY_MAP_SHA256,
        SUPPLEMENT_MAP: EXPECTED_SUPPLEMENT_MAP_SHA256,
        IMPACT: EXPECTED_IMPACT_SHA256,
        SOURCE_AUDIT: EXPECTED_SOURCE_AUDIT_SHA256,
        PREPARATION: EXPECTED_PREPARATION_SHA256,
        PREFLIGHT: EXPECTED_PREFLIGHT_SHA256,
        PROPOSAL: EXPECTED_PROPOSAL_SHA256,
        builder.EXPORTER: EXPECTED_EXPORTER_SHA256,
        builder.HISTORICAL_EXHIBITS: EXPECTED_HISTORICAL_EXHIBITS_SHA256,
    }
    for path, wanted in expected.items():
        actual = sha256_file(path)
        if actual != wanted:
            raise RuntimeError(f"prepared v32 file changed: {rel(path)} ({actual} != {wanted})")
    preflight = read_json(PREFLIGHT, "v32 preflight")
    if preflight.get("status") != "preflight_passed_waiting_root_v32_input_acceptance":
        raise RuntimeError("v32 preflight is not waiting for root acceptance")
    expected_after = preflight.get("expected_after_export") or {}
    for key, wanted in {
        "primary_overlays": EXPECTED_PRIMARY,
        "supplement_overlays": EXPECTED_SUPPLEMENT,
        "total_overlays": EXPECTED_TOTAL,
        "declared_files": EXPECTED_DECLARED,
        "actual_files": EXPECTED_ACTUAL,
    }.items():
        if expected_after.get(key) != wanted:
            raise RuntimeError(f"v32 preflight expected {key} changed")
    return preflight


def guard_outputs() -> None:
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists() or BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v32 output, partial output, or build receipt")


def write_receipt(payload: dict) -> None:
    if BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v32 build receipt: {BUILD_RECEIPT}")
    BUILD_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_export_go:
        parser.error("v32 export requires both --go and --root-export-go")
    if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
        raise RuntimeError("v32 source site or source manifest is missing")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below floor before v32 export: {free_before}")
    builder = load_builder()
    preflight = guard_prepared(builder)
    root_acceptance = validate_root_acceptance(builder)
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D below floor immediately before v32 export: {free_before_export}")
    frozen = builder.load_v28_builder()
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = "python.exe -X utf8 research/continuous-recovery-20261018/integration/v32/execute_v32.py --go --root-export-go"
    export_started = False
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        if sha256_file(ROOT / "tools/export_github_pages.py") != EXPECTED_EXPORTER_SHA256:
            raise RuntimeError("current exporter SHA changed before export")
        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=tuple(frozen.PRIMARY_MAPS) + (builder.V29_PRIMARY_MAP, builder.V30_PRIMARY_MAP, PRIMARY_MAP),
            supplement_image_source_maps=tuple(frozen.SUPPLEMENT_MAPS) + (builder.V30_SUPPLEMENT_MAP, SUPPLEMENT_MAP),
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=GUIDE_COLLECTION_MAP,
        )
        provenance_path = OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v32 output provenance")
        stats = provenance.get("stats") or {}
        for key, expected in {
            "source_records": 8_357,
            "image_overlay_records": EXPECTED_TOTAL,
            "primary_image_overlay_records": EXPECTED_PRIMARY,
            "supplement_image_overlay_records": EXPECTED_SUPPLEMENT,
            "output_files": EXPECTED_DECLARED,
        }.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v32 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        if actual_files != EXPECTED_ACTUAL:
            raise RuntimeError(f"v32 actual file count {actual_files}, expected {EXPECTED_ACTUAL}")
        receipt = {
            "schema": "wow-recovery.integration.v32-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": root_acceptance,
            "preflight_sha256": EXPECTED_PREFLIGHT_SHA256,
            "expected_after_export": preflight.get("expected_after_export"),
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
                "schema": "wow-recovery.integration.v32-build-receipt.v1",
                "executed_by": "/root/local_recovery_20261018",
                "command": command,
                "checked_utc_start": started,
                "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "export_started": True,
                "export_completed": False,
                "published": False,
                "network_requests_by_builder": 0,
                "root_input_acceptance": root_acceptance,
                "preflight_sha256": EXPECTED_PREFLIGHT_SHA256,
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
