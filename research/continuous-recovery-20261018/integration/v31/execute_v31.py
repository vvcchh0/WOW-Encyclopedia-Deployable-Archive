#!/usr/bin/env python3
"""Guarded one-shot v31 exporter wrapper.

The v31 builder only prepares maps and preflight data.  This wrapper is the
future export entry point and requires an independently accepted root input
receipt plus the explicit ``--go --root-export-go`` pair before it can call the
exporter.  It never prepares or rewrites v31 inputs.
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
BUILDER_PATH = INTEGRATION / "build_pages_v31.py"
V31_PRIMARY_MAP = INTEGRATION / "v31-primary-source-map.json"
V31_SUPPLEMENT_MAP = INTEGRATION / "v31-supplement-source-map.json"
V31_IMPACT = INTEGRATION / "v31-impact-estimate.json"
V31_SOURCE_AUDIT = INTEGRATION / "v31-source-byte-audit.json"
V31_PREPARATION = INTEGRATION / "v31-input-preparation.json"
V31_PREFLIGHT = INTEGRATION / "v31-preflight.json"
V31_PROPOSAL = INTEGRATION / "v31-input-proposal.md"
V31_RUNNER_NOTE = INTEGRATION / "v31-runner-preparation.md"
V31_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v31"
V31_BUILD_RECEIPT = INTEGRATION / "v31-build-receipt.json"
ROOT_V31_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v31-input-acceptance.json"
ROOT_V31_RUNTIME_IMPACT = ROOT / "research/continuous-recovery-20261018/publication/root-v31-runtime-impact.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_BUILDER_SHA256 = "e8d82e6a7db4d8e21fff443581fd401d6890d4f5ffc688ea5105ad9cfdd1e7be"
EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V29_PROVENANCE_SHA256 = "793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8"
EXPECTED_V30_PRIMARY_MAP_SHA256 = "8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e"
EXPECTED_V30_SUPPLEMENT_MAP_SHA256 = "53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0"
EXPECTED_V30_PROVENANCE_SHA256 = "b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_EXPORTER_SHA256 = "7c3684fb777e9c21b07fe8c8a1be0418810f448e99dd582ed4c9d9c342764dea"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_ARMORY_ACCEPTANCE_SHA256 = "863a141f1082ae76b17e7d5009e03959f066589ac39797483a530718036605cd"
EXPECTED_RETIRED_ARMORY_ACCEPTANCE_SHA256 = "46058b7e23cfa317949f42945196b40be77a6e6485834147e8e32a62c6643e6b"
EXPECTED_HISTORICAL_NEWS_ACCEPTANCE_SHA256 = "b2b4a6cb74cc5713ba5389d682b1d1f7ad0eaf864966d12e69a44eebbb42f02b"
EXPECTED_RUNTIME_IMPACT_SHA256 = "6b11f2b3b3c5b9d00aec1ad2433b047da30f7582877defedc20f73d4830a9401"
EXPECTED_V31_PRIMARY_MAP_SHA256 = "b9228a8478529cd4a39ba0550665f050cdd6690a211ad0b285a30a6bfaeced16"
EXPECTED_V31_SUPPLEMENT_MAP_SHA256 = "bd0820d484eb4f42fc1b1f7d4bbbfd12bb14ab9dc9d8489924e08fb2af08fc23"
EXPECTED_V31_IMPACT_SHA256 = "3d83fd105d03dbdcaa02a2347666e13eece12ca616496d5c48bcd0b6ad041ec7"
EXPECTED_V31_SOURCE_AUDIT_SHA256 = "d4f7489c7673c34e7252c8dc0c770e64756375821e3e0e13ac5ddf0d5ac21a09"
EXPECTED_V31_PREPARATION_SHA256 = "27f0939380b9a1c444facf4d6901eaadb1c59a837a50966f9277a134b13c26cc"
EXPECTED_V31_PREFLIGHT_SHA256 = "e41063c1b7ea3470760ff95514723f40168420ca78820381629735c5381450aa"
EXPECTED_V31_PROPOSAL_SHA256 = "3010ecb41dfd801d6181492eb5214cc299bc4fc59d4dbd4701e1887611d15d6e"
EXPECTED_RECEIPT_SHAS = (
    "1cbbb670705cc7615c85cf7f968143ac7cb2393551212e2290f649c55503c07f",
    "f10f4464d809474873940d823daef3062acfa16323c870ad80fc55ab43dfc5b5",
    "570082ebc535343c87c416832b78f75166de6265e88b6716839ab170458aa9d3",
    "b15bb4222e0e267d9a4fec665af912e27f62225e3d377a056afd44057098c7e2",
    "c6a210b917e8926cd456b6157cc73dbaf416b3b7ce0f9328f74a439d95a4d47e",
)
EXPECTED_NEW_IMAGES = 49
EXPECTED_NEW_BYTES = 480_639
EXPECTED_PRIMARY = 296
EXPECTED_SUPPLEMENT = 89
EXPECTED_TOTAL = 385
EXPECTED_DECLARED = 8_843
EXPECTED_ACTUAL = 8_844


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
        raise RuntimeError(f"v31 builder SHA changed: {actual} != {EXPECTED_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_v31_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v31 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_root_acceptance(builder, frozen) -> dict:
    receipt = read_json(ROOT_V31_INPUT_ACCEPTANCE, "root v31 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v31 input acceptance is not accepted")
    if receipt.get("preflight_sha256", "").casefold() != EXPECTED_V31_PREFLIGHT_SHA256:
        raise RuntimeError("root v31 preflight SHA mismatch")
    if receipt.get("new_images") != EXPECTED_NEW_IMAGES or receipt.get("image_bytes") != EXPECTED_NEW_BYTES:
        raise RuntimeError("root v31 accepted image count/bytes changed")
    if receipt.get("network_requests") != 0 or receipt.get("export_executed") is not False:
        raise RuntimeError("root v31 acceptance records network/export activity")
    copies = receipt.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("root v31 acceptance must contain 49 public image copies")
    bindings = {
        str(item.get("path")): str(item.get("sha256") or "").casefold()
        for item in receipt.get("map_bindings", [])
        if isinstance(item, dict)
    }
    if not bindings:
        raise RuntimeError("root v31 acceptance has no map_bindings")

    required: dict[str, str] = {
        rel(BUILDER_PATH): EXPECTED_BUILDER_SHA256,
        rel(Path(__file__)): sha256_file(Path(__file__)),
        rel(V31_PRIMARY_MAP): EXPECTED_V31_PRIMARY_MAP_SHA256,
        rel(V31_SUPPLEMENT_MAP): EXPECTED_V31_SUPPLEMENT_MAP_SHA256,
        rel(V31_IMPACT): EXPECTED_V31_IMPACT_SHA256,
        rel(V31_SOURCE_AUDIT): EXPECTED_V31_SOURCE_AUDIT_SHA256,
        rel(V31_PREPARATION): EXPECTED_V31_PREPARATION_SHA256,
        rel(V31_PREFLIGHT): EXPECTED_V31_PREFLIGHT_SHA256,
        rel(V31_PROPOSAL): EXPECTED_V31_PROPOSAL_SHA256,
        rel(V31_RUNNER_NOTE): sha256_file(V31_RUNNER_NOTE),
        rel(ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"): EXPECTED_V28_BUILDER_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"): EXPECTED_V28_PRIMARY_MAP_SHA256,
        rel(ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"): EXPECTED_V28_PROVENANCE_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"): EXPECTED_V29_PRIMARY_MAP_SHA256,
        rel(ROOT / ".scratch/pages-resources-20261018-v29/export-provenance.json"): EXPECTED_V29_PROVENANCE_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v30/v30-primary-source-map.json"): EXPECTED_V30_PRIMARY_MAP_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/integration/v30/v30-supplement-source-map.json"): EXPECTED_V30_SUPPLEMENT_MAP_SHA256,
        rel(ROOT / ".scratch/pages-resources-20261018-v30/export-provenance.json"): EXPECTED_V30_PROVENANCE_SHA256,
        rel(SOURCE_MANIFEST): EXPECTED_SOURCE_MANIFEST_SHA256,
        rel(ROOT / "tools/export_github_pages.py"): EXPECTED_EXPORTER_SHA256,
        rel(ROOT / "tools/historical_exhibits.py"): EXPECTED_HISTORICAL_EXHIBITS_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-armory-origin-tool-acceptance.json"): EXPECTED_ARMORY_ACCEPTANCE_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-retired-armory-tool-acceptance.json"): EXPECTED_RETIRED_ARMORY_ACCEPTANCE_SHA256,
        rel(ROOT / "research/continuous-recovery-20261018/publication/root-historical-news-tool-retry1-acceptance.json"): EXPECTED_HISTORICAL_NEWS_ACCEPTANCE_SHA256,
        rel(ROOT_V31_RUNTIME_IMPACT): EXPECTED_RUNTIME_IMPACT_SHA256,
    }
    for path in tuple(frozen.PRIMARY_MAPS) + tuple(frozen.SUPPLEMENT_MAPS):
        required[rel(path)] = sha256_file(path)
    for path in (
        builder.V28_PROVENANCE,
        builder.V28_RECEIPT,
        builder.V29_PRIMARY_MAP,
        builder.V29_PREPARATION,
        builder.V29_PREFLIGHT,
        builder.V29_RECEIPT,
        builder.V29_PROVENANCE,
        builder.V30_PRIMARY_MAP,
        builder.V30_SUPPLEMENT_MAP,
        builder.V30_IMPACT,
        builder.V30_SOURCE_AUDIT,
        builder.V30_PREPARATION,
        builder.V30_PREFLIGHT,
        builder.V30_PROPOSAL,
        builder.V30_RUNNER_NOTE,
        builder.V30_BUILD_RECEIPT,
        builder.V30_PROVENANCE,
        builder.ROOT_V30_INPUT_ACCEPTANCE,
    ):
        required[rel(path)] = sha256_file(path)
    for index, receipt_path in enumerate(builder.V31_RECEIPTS):
        if sha256_file(receipt_path) != EXPECTED_RECEIPT_SHAS[index]:
            raise RuntimeError(f"news49 receipt SHA changed: {receipt_path.name}")
        required[rel(receipt_path)] = EXPECTED_RECEIPT_SHAS[index]
        copy_receipt = read_json(receipt_path, receipt_path.name)
        source_binding = copy_receipt.get("source_acceptance") or copy_receipt.get("source_receipt") or {}
        source_path = ROOT / str(source_binding.get("path") if isinstance(source_binding, dict) else source_binding)
        required[rel(source_path)] = sha256_file(source_path)
        for row in copy_receipt.get("accepted_images", []):
            local = ROOT / str(row.get("local_path") or "")
            required[rel(local)] = sha256_file(local)
    for copy in copies:
        if not isinstance(copy, dict):
            raise RuntimeError("root v31 public copy is not an object")
        path = ROOT / str(copy.get("path") or "")
        wanted = str(copy.get("sha256") or "").casefold()
        if not path.is_file() or path.stat().st_size != int(copy.get("length", -1)) or sha256_file(path) != wanted:
            raise RuntimeError(f"root v31 public copy changed: {path}")
        required[rel(path)] = wanted
    for path, wanted in required.items():
        if bindings.get(path) != wanted:
            raise RuntimeError(f"root v31 binding mismatch: {path}")
    return {"path": rel(ROOT_V31_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_V31_INPUT_ACCEPTANCE), "binding_count": len(bindings), "public_copy_count": len(copies)}


def validate_prepared(builder, frozen, v30) -> tuple[dict, dict, dict]:
    for path, wanted in (
        (V31_PRIMARY_MAP, EXPECTED_V31_PRIMARY_MAP_SHA256),
        (V31_SUPPLEMENT_MAP, EXPECTED_V31_SUPPLEMENT_MAP_SHA256),
        (V31_IMPACT, EXPECTED_V31_IMPACT_SHA256),
        (V31_SOURCE_AUDIT, EXPECTED_V31_SOURCE_AUDIT_SHA256),
        (V31_PREPARATION, EXPECTED_V31_PREPARATION_SHA256),
        (V31_PREFLIGHT, EXPECTED_V31_PREFLIGHT_SHA256),
        (V31_PROPOSAL, EXPECTED_V31_PROPOSAL_SHA256),
    ):
        if sha256_file(path) != wanted:
            raise RuntimeError(f"prepared v31 input changed: {rel(path)}")
    preflight = read_json(V31_PREFLIGHT, "v31 preflight")
    if preflight.get("status") != "preflight_passed_waiting_root_v31_input_acceptance":
        raise RuntimeError("v31 preflight is not waiting for root acceptance")
    expected = preflight.get("expected_after_export") or {}
    if {key: expected.get(key) for key in ("primary_overlays", "supplement_overlays", "total_overlays", "declared_files", "actual_files")} != {
        "primary_overlays": EXPECTED_PRIMARY,
        "supplement_overlays": EXPECTED_SUPPLEMENT,
        "total_overlays": EXPECTED_TOTAL,
        "declared_files": EXPECTED_DECLARED,
        "actual_files": EXPECTED_ACTUAL,
    }:
        raise RuntimeError("v31 preflight expected counts changed")
    closure = builder.validate_frozen_v30_closure(frozen, v30)
    primary_map = read_json(V31_PRIMARY_MAP, "v31 primary map")
    supplement_map = read_json(V31_SUPPLEMENT_MAP, "v31 supplement map")
    builder.validate_no_overlap(frozen, primary_map, supplement_map)
    builder.validate_map(frozen, primary_map, role="primary_image_overlay", expected_count=49, expected_bytes=EXPECTED_NEW_BYTES)
    builder.validate_map(frozen, supplement_map, role="supplement_image_overlay", expected_count=0, expected_bytes=0)
    loader = builder.loader_preflight(frozen, primary_map, supplement_map)
    if loader["primary_overlay_records"] != EXPECTED_PRIMARY or loader["supplement_overlay_records"] != EXPECTED_SUPPLEMENT or loader["total_overlay_records"] != EXPECTED_TOTAL:
        raise RuntimeError("v31 loader closure counts changed")
    return closure, primary_map, supplement_map


def guard_outputs() -> None:
    if V31_OUTPUT.exists() or V31_OUTPUT.with_name(V31_OUTPUT.name + ".partial").exists() or V31_BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v31 output, partial output, or build receipt")


def write_receipt(payload: dict) -> None:
    if V31_BUILD_RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite v31 build receipt: {V31_BUILD_RECEIPT}")
    V31_BUILD_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-export-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_export_go:
        parser.error("v31 export requires both --go and --root-export-go")
    if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
        raise RuntimeError("v31 source site or source manifest is missing")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor before v31 export: {free_before}")
    builder = load_builder()
    frozen = builder.load_frozen_v28()
    v30 = builder.load_v30_builder()
    prepared = validate_prepared(builder, frozen, v30)
    root_acceptance = validate_root_acceptance(builder, frozen)
    guard_outputs()
    free_before_export = shutil.disk_usage(ROOT).free
    if free_before_export < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor immediately before v31 export: {free_before_export}")
    closure, primary_map, supplement_map = prepared
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = "python.exe -X utf8 research/continuous-recovery-20261018/integration/v31/execute_v31.py --go --root-export-go"
    export_started = False
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=V31_OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=tuple(frozen.PRIMARY_MAPS) + (builder.V29_PRIMARY_MAP, builder.V30_PRIMARY_MAP, V31_PRIMARY_MAP),
            supplement_image_source_maps=tuple(frozen.SUPPLEMENT_MAPS) + (builder.V30_SUPPLEMENT_MAP, V31_SUPPLEMENT_MAP),
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=GUIDE_COLLECTION_MAP,
        )
        provenance_path = V31_OUTPUT / "export-provenance.json"
        provenance = read_json(provenance_path, "v31 output provenance")
        stats = provenance.get("stats") or {}
        for key, expected in {
            "source_records": 8357,
            "image_overlay_records": EXPECTED_TOTAL,
            "primary_image_overlay_records": EXPECTED_PRIMARY,
            "supplement_image_overlay_records": EXPECTED_SUPPLEMENT,
            "output_files": EXPECTED_DECLARED,
        }.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v31 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in V31_OUTPUT.rglob("*") if path.is_file())
        if actual_files != EXPECTED_ACTUAL:
            raise RuntimeError(f"v31 actual file count {actual_files}, expected {EXPECTED_ACTUAL}")
        receipt = {
            "schema": "wow-recovery.integration.v31-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": root_acceptance,
            "frozen_v30_closure": closure,
            "loader_preflight": builder.loader_preflight(frozen, primary_map, supplement_map),
            "build": result,
            "postbuild": {"declared_files": stats.get("output_files"), "actual_files": actual_files, "provenance_path": rel(provenance_path), "provenance_sha256": sha256_file(provenance_path)},
            "output": rel(V31_OUTPUT),
            "disk_free_before_bytes": free_before_export,
            "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        if export_started and not V31_BUILD_RECEIPT.exists():
            write_receipt({
                "schema": "wow-recovery.integration.v31-build-receipt.v1",
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
                "output": rel(V31_OUTPUT) if V31_OUTPUT.exists() else None,
                "partial_exists": V31_OUTPUT.with_name(V31_OUTPUT.name + ".partial").exists(),
                "disk_free_before_bytes": free_before_export,
                "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
                "disk_free_floor_bytes": MIN_FREE_BYTES,
            })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
