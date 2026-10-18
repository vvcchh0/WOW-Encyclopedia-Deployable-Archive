#!/usr/bin/env python3
"""Run the one-shot v29 exporter behind an explicit root acceptance gate.

--prepare performs only offline closure and guard checks and never writes an
output or receipt. A real export requires both --go and --root-export-go plus
the root v29 input acceptance receipt. The frozen v28 builder is imported for
its read-only closure constants and validation helpers; its main function is
never called.
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
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V28_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"
V28_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-preflight.json"
V28_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"
V28_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-build-receipt.json"
V29_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v29/build_pages_v29.py"
V29_PRIMARY_MAP = INTEGRATION / "v29-primary-source-map.json"
V29_IMPACT = INTEGRATION / "v29-impact-estimate.json"
V29_PREPARATION = INTEGRATION / "v29-input-preparation.json"
V29_PREFLIGHT = INTEGRATION / "v29-preflight.json"
V29_PROPOSAL = INTEGRATION / "v29-input-proposal.md"
V29_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v29"
V29_RECEIPT = INTEGRATION / "v29-build-receipt.json"
ROOT_V29_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v29-input-retry1-acceptance.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
EXPORTER = ROOT / "tools/export_github_pages.py"
HISTORICAL_EXHIBITS = ROOT / "tools/historical_exhibits.py"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PREFLIGHT_SHA256 = "a5390b8950ff4908b692f31baf7b635e7cecef39cc7d9dd47e151d0e4d1022fa"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V28_RECEIPT_SHA256 = "2483e506f268ff43a022612e0b2c581cf753bab9935c530812c6da68cd227f3e"
EXPECTED_V29_BUILDER_SHA256 = "cd202bfa5eabd008d635ee81e424c8f8cc248e16cc6f6acadb225a530afa52e0"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V29_IMPACT_SHA256 = "454b2c2abb1f9823e1297c4ef48535df522f954c2bc1e18162b9067594550b48"
EXPECTED_V29_PREPARATION_SHA256 = "c54913a8ef64fa8c824af6290c493d44ebda73910ba526facd3fe37f775a29fe"
EXPECTED_V29_PREFLIGHT_SHA256 = "b29e1e7f69cf17391084d8fb0770008e1b850c9e9b2f92ad5900c65e68ab0194"
EXPECTED_V29_PROPOSAL_SHA256 = "120a0ae5e66bf6da05a82b19f3a99f2bf2c8906a1eab9e39c636093d565dd44c"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_EXPORTER_SHA256 = "943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_V29_PRIMARY_COUNT = 228
EXPECTED_V29_SUPPLEMENT_COUNT = 75
EXPECTED_V29_TOTAL_COUNT = 303
EXPECTED_SOURCE_RECORDS = 8357
EXPECTED_DECLARED_FILES = 8761
EXPECTED_ACTUAL_FILES = 8762
EXPECTED_GUIDE_IMAGES = 39
EXPECTED_GUIDE_PREVIEWS = 22


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
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def load_frozen_v28():
    actual = sha256_file(V28_BUILDER)
    if actual != EXPECTED_V28_BUILDER_SHA256:
        raise RuntimeError(f"frozen v28 builder SHA changed: {actual} != {EXPECTED_V28_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_execute_frozen_v28", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_fixed_inputs(frozen) -> dict[str, str]:
    checks = {
        "v28_builder": (V28_BUILDER, EXPECTED_V28_BUILDER_SHA256),
        "v28_primary_map": (V28_PRIMARY_MAP, EXPECTED_V28_PRIMARY_MAP_SHA256),
        "v28_preflight": (V28_PREFLIGHT, EXPECTED_V28_PREFLIGHT_SHA256),
        "v28_provenance": (V28_PROVENANCE, EXPECTED_V28_PROVENANCE_SHA256),
        "v28_build_receipt": (V28_RECEIPT, EXPECTED_V28_RECEIPT_SHA256),
        "v29_builder": (V29_BUILDER, EXPECTED_V29_BUILDER_SHA256),
        "v29_primary_map": (V29_PRIMARY_MAP, EXPECTED_V29_PRIMARY_MAP_SHA256),
        "v29_impact": (V29_IMPACT, EXPECTED_V29_IMPACT_SHA256),
        "v29_preparation": (V29_PREPARATION, EXPECTED_V29_PREPARATION_SHA256),
        "v29_preflight": (V29_PREFLIGHT, EXPECTED_V29_PREFLIGHT_SHA256),
        "v29_proposal": (V29_PROPOSAL, EXPECTED_V29_PROPOSAL_SHA256),
        "source_manifest": (SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "exporter": (EXPORTER, EXPECTED_EXPORTER_SHA256),
        "historical_exhibits": (HISTORICAL_EXHIBITS, EXPECTED_HISTORICAL_EXHIBITS_SHA256),
    }
    result: dict[str, str] = {}
    for label, (path, expected) in checks.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"{label} SHA changed: {actual} != {expected}")
        result[label] = actual
    closure = frozen.validate_frozen_closure()
    result["frozen_v28_closure"] = json.dumps(closure, sort_keys=True)
    return result


def validate_v29_map() -> dict:
    payload = read_json(V29_PRIMARY_MAP, "v29 primary map")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 40:
        raise RuntimeError(f"v29 primary map item count changed: {len(items or [])}")
    seen: set[str] = set()
    total = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise RuntimeError(f"v29 primary map item {index} is not an object")
        original = str(item.get("original") or item.get("logical_url") or "")
        if not original or original in seen:
            raise RuntimeError(f"v29 primary map item {index} has duplicate/missing original")
        seen.add(original)
        if (urlsplit(original).hostname or "").casefold().rstrip(".") != "www.worldofwarcraft.com":
            raise RuntimeError(f"v29 primary map item {index} is not a primary host: {original}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local:
            raise RuntimeError(f"v29 primary map item {index} has non-public local path: {local}")
        source = (ROOT / local).resolve()
        try:
            source.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"v29 map local path escapes workspace: {local}") from exc
        if not source.is_file():
            raise RuntimeError(f"v29 public copy missing: {source}")
        length = int(item.get("length", -1))
        if source.stat().st_size != length:
            raise RuntimeError(f"v29 public copy length changed: {original}")
        total += length
    if total != 318622:
        raise RuntimeError(f"v29 primary map byte total changed: {total}")
    return {"primary_items": len(items), "bytes": total}


def validate_v29_preflight() -> dict:
    preflight = read_json(V29_PREFLIGHT, "v29 preflight")
    if preflight.get("status") != "preflight_passed_waiting_root_v29_input_acceptance":
        raise RuntimeError("v29 preflight is not the frozen waiting-for-acceptance state")
    if preflight.get("network_requests") != 0 or preflight.get("export_executed") is not False:
        raise RuntimeError("v29 preflight records network/export activity")
    primary = preflight.get("primary_map") or {}
    if primary.get("path") != rel(V29_PRIMARY_MAP) or str(primary.get("sha256", "")).casefold() != EXPECTED_V29_PRIMARY_MAP_SHA256:
        raise RuntimeError("v29 preflight primary map binding changed")
    impact = preflight.get("impact") or {}
    if impact.get("path") != rel(V29_IMPACT) or str(impact.get("sha256", "")).casefold() != EXPECTED_V29_IMPACT_SHA256:
        raise RuntimeError("v29 preflight impact binding changed")
    loader = preflight.get("loader_preflight") or {}
    expected_loader = {
        "primary_overlay_records": EXPECTED_V29_PRIMARY_COUNT,
        "supplement_overlay_records": EXPECTED_V29_SUPPLEMENT_COUNT,
        "total_overlay_records": EXPECTED_V29_TOTAL_COUNT,
        "guide_collection_groups": 3,
        "guide_collection_images": EXPECTED_GUIDE_IMAGES,
        "new_primary_records": 40,
        "new_supplement_records": 0,
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }
    for key, expected in expected_loader.items():
        if loader.get(key) != expected:
            raise RuntimeError(f"v29 loader preflight {key}={loader.get(key)!r}, expected {expected!r}")
    expected_after = {
        "declared_files": EXPECTED_DECLARED_FILES,
        "actual_files": EXPECTED_ACTUAL_FILES,
        "primary_overlays": EXPECTED_V29_PRIMARY_COUNT,
        "supplement_overlays": EXPECTED_V29_SUPPLEMENT_COUNT,
        "total_overlays": EXPECTED_V29_TOTAL_COUNT,
        "guide_previews": EXPECTED_GUIDE_PREVIEWS,
        "guide_collection_images": EXPECTED_GUIDE_IMAGES,
    }
    if preflight.get("expected_after_export") != expected_after:
        raise RuntimeError("v29 preflight expected counts changed")
    return {"loader_preflight": loader, "expected_after_export": expected_after}


def safe_root_path(path_text: str, label: str) -> Path:
    if not isinstance(path_text, str) or not path_text or Path(path_text).is_absolute():
        raise RuntimeError(f"{label} is not a workspace-relative path: {path_text!r}")
    candidate = (ROOT / Path(path_text)).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes workspace: {path_text}") from exc
    return candidate


def validate_root_acceptance() -> dict:
    receipt = read_json(ROOT_V29_INPUT_ACCEPTANCE, "root v29 input acceptance")
    if receipt.get("accepted") is not True:
        raise RuntimeError("root v29 input acceptance is not accepted")
    bindings = receipt.get("map_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise RuntimeError("root v29 input acceptance has no map_bindings")
    bound: dict[str, str] = {}
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise RuntimeError(f"root v29 map binding {index} is not an object")
        path_text = str(binding.get("path") or "")
        expected = str(binding.get("sha256") or "").casefold()
        if len(expected) != 64:
            raise RuntimeError(f"root v29 map binding {index} has invalid SHA")
        if path_text in bound:
            raise RuntimeError(f"root v29 map binding repeated: {path_text}")
        path = safe_root_path(path_text, f"root v29 map binding {index}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"root v29 map binding changed: {path_text}: {actual} != {expected}")
        bound[path_text] = actual
    mandatory = {
        rel(V28_BUILDER): EXPECTED_V28_BUILDER_SHA256,
        rel(V28_PRIMARY_MAP): EXPECTED_V28_PRIMARY_MAP_SHA256,
        rel(V29_PRIMARY_MAP): EXPECTED_V29_PRIMARY_MAP_SHA256,
        rel(V29_PREFLIGHT): EXPECTED_V29_PREFLIGHT_SHA256,
        rel(EXPORTER): EXPECTED_EXPORTER_SHA256,
        rel(HISTORICAL_EXHIBITS): EXPECTED_HISTORICAL_EXHIBITS_SHA256,
    }
    for path_text, expected in mandatory.items():
        if bound.get(path_text) != expected:
            raise RuntimeError(f"root v29 acceptance missing or mismatched mandatory binding: {path_text}")
    if str(receipt.get("preflight_sha256") or "").casefold() != EXPECTED_V29_PREFLIGHT_SHA256:
        raise RuntimeError("root v29 preflight SHA mismatch")
    if receipt.get("new_images") != 40 or receipt.get("image_bytes") != 318622:
        raise RuntimeError("root v29 accepted image count/bytes changed")
    if receipt.get("network_requests") != 0 or receipt.get("export_executed") is not False:
        raise RuntimeError("root v29 acceptance records network/export activity")
    copies = receipt.get("public_image_copies")
    if not isinstance(copies, list) or len(copies) != 40:
        raise RuntimeError("root v29 acceptance must contain 40 public image copies")
    for index, copy in enumerate(copies):
        if not isinstance(copy, dict):
            raise RuntimeError(f"root v29 public copy {index} is not an object")
        path = safe_root_path(str(copy.get("path") or ""), f"root v29 public copy {index}")
        expected = str(copy.get("sha256") or "").casefold()
        length = int(copy.get("length", -1))
        if path.stat().st_size != length or sha256_file(path) != expected:
            raise RuntimeError(f"root v29 public copy changed: {rel(path)}")
    return {"path": rel(ROOT_V29_INPUT_ACCEPTANCE), "sha256": sha256_file(ROOT_V29_INPUT_ACCEPTANCE), "binding_count": len(bound), "public_copy_count": len(copies)}


def guard_outputs() -> None:
    partial = V29_OUTPUT.with_name(V29_OUTPUT.name + ".partial")
    if V29_OUTPUT.exists() or partial.exists() or V29_RECEIPT.exists():
        raise RuntimeError("refusing existing v29 output, partial output, or build receipt")


def command_string() -> str:
    return subprocess.list2cmdline([sys.executable, *sys.argv])


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_export(root_acceptance: dict, free_before: int, frozen) -> int:
    started = utc_now()
    command = command_string()
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        # The frozen v28 PRIMARY_MAPS already contains v25/v26/v27/v28
        # primary maps. Append only the immutable v29 primary map. Its
        # supplement tuple is the complete frozen v28 supplement closure.
        primary_maps = tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP,)
        supplement_maps = tuple(frozen.SUPPLEMENT_MAPS)
        if V28_PRIMARY_MAP not in primary_maps:
            raise RuntimeError("frozen v28 primary map is absent from export closure")
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=V29_OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=primary_maps,
            supplement_image_source_maps=supplement_maps,
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
            guide_image_collection_map=GUIDE_COLLECTION_MAP,
        )
        provenance_path = V29_OUTPUT / "export-provenance.json"
        provenance_sha = sha256_file(provenance_path) if provenance_path.is_file() else None
        provenance = read_json(provenance_path, "v29 output provenance")
        stats = provenance.get("stats") or {}
        expected_stats = {
            "source_records": EXPECTED_SOURCE_RECORDS,
            "image_overlay_records": EXPECTED_V29_TOTAL_COUNT,
            "primary_image_overlay_records": EXPECTED_V29_PRIMARY_COUNT,
            "supplement_image_overlay_records": EXPECTED_V29_SUPPLEMENT_COUNT,
            "output_files": EXPECTED_DECLARED_FILES,
        }
        for key, expected in expected_stats.items():
            if stats.get(key) != expected:
                raise RuntimeError(f"v29 provenance {key}={stats.get(key)!r}, expected {expected}")
        actual_files = sum(1 for path in V29_OUTPUT.rglob("*") if path.is_file())
        if actual_files != EXPECTED_ACTUAL_FILES:
            raise RuntimeError(f"v29 actual file count {actual_files}, expected {EXPECTED_ACTUAL_FILES}")
        free_after = shutil.disk_usage(ROOT).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk floor after v29 export: {free_after}")
        receipt = {
            "schema": "wow-recovery.integration.v29-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": utc_now(),
            "export_started": True,
            "export_completed": True,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": root_acceptance,
            "build": result,
            "closure": {
                "primary_map_count": len(primary_maps),
                "supplement_map_count": len(supplement_maps),
                "v28_primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": EXPECTED_V28_PRIMARY_MAP_SHA256},
                "v29_primary_map": {"path": rel(V29_PRIMARY_MAP), "sha256": EXPECTED_V29_PRIMARY_MAP_SHA256},
            },
            "postbuild": {
                "declared_files": stats.get("output_files"),
                "actual_files": actual_files,
                "provenance_path": rel(provenance_path),
                "provenance_sha256": provenance_sha,
            },
            "output": rel(V29_OUTPUT),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if V29_RECEIPT.exists():
            raise RuntimeError(f"refusing to overwrite v29 build receipt: {V29_RECEIPT}")
        V29_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        free_after = shutil.disk_usage(ROOT).free
        failure = {
            "schema": "wow-recovery.integration.v29-build-receipt.v1",
            "executed_by": "/root/local_recovery_20261018",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": utc_now(),
            "export_started": True,
            "export_completed": False,
            "published": False,
            "network_requests_by_builder": 0,
            "root_input_acceptance": root_acceptance,
            "error": f"{type(exc).__name__}: {exc}",
            "output": rel(V29_OUTPUT) if V29_OUTPUT.exists() else None,
            "partial_output": rel(V29_OUTPUT.with_name(V29_OUTPUT.name + ".partial")) if V29_OUTPUT.with_name(V29_OUTPUT.name + ".partial").exists() else None,
            "output_provenance": {
                "path": rel(V29_OUTPUT / "export-provenance.json"),
                "sha256": sha256_file(V29_OUTPUT / "export-provenance.json") if (V29_OUTPUT / "export-provenance.json").is_file() else None,
            },
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if not V29_RECEIPT.exists():
            V29_RECEIPT.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="offline closure and output-guard check only")
    parser.add_argument("--go", action="store_true", help="perform the single exporter call")
    parser.add_argument("--root-export-go", action="store_true", help="explicit root export authorization gate")
    args = parser.parse_args(argv)
    if args.root_export_go and not args.go:
        parser.error("--root-export-go requires --go")
    if not args.prepare and not args.go:
        parser.error("choose --prepare or --go")
    if args.prepare and args.go:
        parser.error("--prepare and --go are mutually exclusive")
    guard_outputs()
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor before v29 runner: {free_before}")
    frozen = load_frozen_v28()
    pins = validate_fixed_inputs(frozen)
    map_check = validate_v29_map()
    preflight_check = validate_v29_preflight()
    acceptance = None
    if ROOT_V29_INPUT_ACCEPTANCE.is_file():
        acceptance = validate_root_acceptance()
    if args.go:
        if not args.root_export_go:
            parser.error("v29 export requires both --go and --root-export-go")
        if acceptance is None:
            raise RuntimeError(f"missing root v29 input acceptance: {ROOT_V29_INPUT_ACCEPTANCE}")
        free_before_export = shutil.disk_usage(ROOT).free
        if free_before_export < MIN_FREE_BYTES:
            raise RuntimeError(f"D: below floor before v29 export: {free_before_export}")
        result = run_export(acceptance, free_before_export, frozen)
        return result
    print(json.dumps({
        "status": "offline_ready_waiting_root_v29_input_acceptance_and_go",
        "network_requests": 0,
        "export_executed": False,
        "root_acceptance_present": acceptance is not None,
        "pins": pins,
        "map_validation": map_check,
        "preflight_validation": preflight_check,
        "disk_free_before_bytes": free_before,
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
        "output_guard": "clear",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
