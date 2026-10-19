#!/usr/bin/env python3
"""Prepare the v34 contest-navigation compatibility export.

This is preparation-only.  It reuses the frozen v33 source site, source
manifest, guide maps, and 559 accepted image overlays.  v34 has no new image
source rows in this preparation; its only planned delta is the exact winners
navigation fallback already accepted by the root tool receipt.  The exporter
is never called here.
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
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
INTEGRATION = Path(__file__).resolve().parent

SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ORIGINAL_MANIFEST = ROOT / "offline/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V29_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"
V30_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-supplement-source-map.json"
V32_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-primary-source-map.json"
V32_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-supplement-source-map.json"
V33_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-primary-source-map.json"
V33_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-supplement-source-map.json"
V33_PREPARATION = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-input-preparation.json"
V33_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-preflight.json"
V33_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-build-receipt.json"
V33_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v33/export-provenance.json"
V33_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v33-input-acceptance.json"
V33_BROWSER_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-v33-browser-continuation-acceptance.json"
V33_PORTABLE_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-v33-portable-acceptance.json"
CONTEST_TOOL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-contest-nav-tool-acceptance.json"
EXPORTER = ROOT / "tools/export_github_pages.py"
HISTORICAL_EXHIBITS = ROOT / "tools/historical_exhibits.py"

V34_PRIMARY_MAP = INTEGRATION / "v34-primary-source-map.json"
V34_SUPPLEMENT_MAP = INTEGRATION / "v34-supplement-source-map.json"
V34_SOURCE_CLOSURE = INTEGRATION / "v34-source-closure.json"
V34_PREPARATION = INTEGRATION / "v34-input-preparation.json"
V34_PREFLIGHT = INTEGRATION / "v34-preflight.json"
V34_PROPOSAL = INTEGRATION / "v34-input-proposal.md"
V34_RUNNER_NOTE = INTEGRATION / "v34-runner-preparation.md"

BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_ORIGINAL_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_V33_PRIMARY_MAP_SHA256 = "285b6f56b932a74ba6da0c30b64256b8cff05f165ec1636b682a48000ea27972"
EXPECTED_V33_SUPPLEMENT_MAP_SHA256 = "6ab2cc11483a62588c093f6ec927d99ad9e550a4fbb7a52471e273bbcaabb6bc"
EXPECTED_V33_PREPARATION_SHA256 = "c9c7fe838c973532c66249be71d0979eb49257090f85f669b77a254f36686c59"
EXPECTED_V33_PREFLIGHT_SHA256 = "75d58a1421702181e14eff6acc1844c06d38e802e6077eed70a3ff6b5b226cdd"
EXPECTED_V33_BUILD_RECEIPT_SHA256 = "c1cc8b1bd16552717b15ec94da04906adcf3c9352ad0a68ff6f45f834e28e142"
EXPECTED_V33_PROVENANCE_SHA256 = "99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5"
EXPECTED_V33_INPUT_ACCEPTANCE_SHA256 = "a8cb18dfae75b0bc2203d428ce68805d698d109b30d39a536bea2438f87db775"
EXPECTED_V33_BROWSER_ACCEPTANCE_SHA256 = "d2119b7ffc9fef155f526434892aae725677e1ced73474a633b03d2eaa5fefef"
EXPECTED_V33_PORTABLE_ACCEPTANCE_SHA256 = "7eebc78924477aed11c28f2f115f9a337b8e49d334df204dc06fd7034a4f36a8"
EXPECTED_CONTEST_TOOL_ACCEPTANCE_SHA256 = "71e7c1df0d71eae0640f4a45d7e0420e219484baf34fe15705e70d9d4eba5da3"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_EXPORTER_SHA256 = "e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def binding(path: Path, expected: str | None = None) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing binding: {path}")
    actual = sha256_file(path)
    if expected is not None and actual.casefold() != expected.casefold():
        raise RuntimeError(f"binding SHA mismatch for {rel(path)}: {actual} != {expected}")
    return {"path": rel(path), "sha256": actual}


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def load_v28_builder():
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("wow_recovery_v28_for_v34", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def closure_maps() -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    frozen = load_v28_builder()
    primary = tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP, V30_PRIMARY_MAP, V32_PRIMARY_MAP, V33_PRIMARY_MAP)
    supplement = tuple(frozen.SUPPLEMENT_MAPS) + (V30_SUPPLEMENT_MAP, V32_SUPPLEMENT_MAP, V33_SUPPLEMENT_MAP)
    return primary, supplement


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_once(path: Path, payload: object, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing existing {label}: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload if isinstance(payload, bytes) else payload.encode("utf-8") if isinstance(payload, str) else json_bytes(payload))


def verify_file_set(paths: tuple[Path, ...], label: str) -> list[dict]:
    result = []
    for path in paths:
        result.append(binding(path))
    if not result:
        raise RuntimeError(f"{label} is empty")
    return result


def verify_root_v33_gate(closure: tuple[Path, ...]) -> dict:
    gate = read_json(V33_INPUT_ACCEPTANCE, "root v33 input acceptance")
    if gate.get("accepted") is not True:
        raise RuntimeError("root v33 input acceptance is not accepted")
    actual = {str(item.get("path")): str(item.get("sha256")).casefold() for item in gate.get("map_bindings", []) if isinstance(item, dict)}
    for path in closure:
        key = rel(path)
        if actual.get(key) != sha256_file(path):
            raise RuntimeError(f"v33 root gate does not bind closure map: {key}")
    return binding(V33_INPUT_ACCEPTANCE, EXPECTED_V33_INPUT_ACCEPTANCE_SHA256)


def make_empty_map(role: str, primary_maps: tuple[Path, ...], supplement_maps: tuple[Path, ...]) -> dict:
    return {
        "schema_version": f"wow-recovery.integration.v34.{role}-source-map.v1",
        "kind": f"wow_static_v34_{role}_image_source_map",
        "role": f"{role}_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v34_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "No new image rows are present in this preparation; v34 inherits the frozen v33 maps exactly.",
        "relative_to_v33": {
            "new_items": 0,
            "new_bytes": 0,
            "frozen_primary_overlays": 459,
            "frozen_supplement_overlays": 100,
            "primary_maps": [binding(path) for path in primary_maps],
            "supplement_maps": [binding(path) for path in supplement_maps],
            "v33_provenance": binding(V33_PROVENANCE, EXPECTED_V33_PROVENANCE_SHA256),
        },
        "source_input": "No new source receipt is accepted or read for v34 preparation.",
        "items": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    if not (args.prepare and args.preflight):
        parser.error("v34 preparation requires both --prepare and --preflight")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v34 preparation floor: {free_before}")
    if not SOURCE_SITE.is_dir():
        raise RuntimeError(f"missing frozen source site: {SOURCE_SITE}")
    source15 = binding(SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256)
    original = binding(ORIGINAL_MANIFEST, EXPECTED_ORIGINAL_MANIFEST_SHA256)
    primary_maps, supplement_maps = closure_maps()
    closure = primary_maps + supplement_maps
    v33_gate = verify_root_v33_gate(closure)
    v33_preflight = read_json(V33_PREFLIGHT, "v33 preflight")
    v33_prep = read_json(V33_PREPARATION, "v33 preparation")
    v33_receipt = read_json(V33_BUILD_RECEIPT, "v33 build receipt")
    v33_provenance = read_json(V33_PROVENANCE, "v33 provenance")
    if v33_preflight.get("new_image_count") != 120 or v33_preflight.get("new_primary_count") != 109 or v33_preflight.get("new_supplement_count") != 11:
        raise RuntimeError("v33 source closure counts changed")
    if (v33_provenance.get("stats") or {}).get("image_overlay_records") != 559:
        raise RuntimeError("v33 provenance does not report 559 overlays")
    browser_acceptance = read_json(V33_BROWSER_ACCEPTANCE, "v33 browser continuation acceptance")
    portable_acceptance = read_json(V33_PORTABLE_ACCEPTANCE, "v33 portable acceptance")
    contest_acceptance = read_json(CONTEST_TOOL_ACCEPTANCE, "contest navigation tool acceptance")
    if browser_acceptance.get("accepted") is not True or portable_acceptance.get("accepted") is not True or contest_acceptance.get("accepted") is not True:
        raise RuntimeError("root v33/browser/tool acceptance is incomplete")
    if contest_acceptance.get("exporter_sha256") != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("contest acceptance is not bound to current exporter")
    if sha256_file(EXPORTER) != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError("current exporter SHA differs")
    if sha256_file(HISTORICAL_EXHIBITS) != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError("historical exhibits SHA differs")

    primary_map = make_empty_map("primary", primary_maps, supplement_maps)
    supplement_map = make_empty_map("supplement", primary_maps, supplement_maps)
    primary_map_bytes = json_bytes(primary_map)
    supplement_map_bytes = json_bytes(supplement_map)
    closure_payload = {
        "schema": "wow-recovery.integration.v34-source-closure.v1",
        "status": "frozen_v33_closure_verified_no_new_images",
        "source15_manifest": source15,
        "original_manifest": original,
        "v33_input_acceptance": v33_gate,
        "v33_preparation": binding(V33_PREPARATION, EXPECTED_V33_PREPARATION_SHA256),
        "v33_preflight": binding(V33_PREFLIGHT, EXPECTED_V33_PREFLIGHT_SHA256),
        "v33_build_receipt": binding(V33_BUILD_RECEIPT, EXPECTED_V33_BUILD_RECEIPT_SHA256),
        "v33_provenance": binding(V33_PROVENANCE, EXPECTED_V33_PROVENANCE_SHA256),
        "v33_browser_acceptance": binding(V33_BROWSER_ACCEPTANCE, EXPECTED_V33_BROWSER_ACCEPTANCE_SHA256),
        "v33_portable_acceptance": binding(V33_PORTABLE_ACCEPTANCE, EXPECTED_V33_PORTABLE_ACCEPTANCE_SHA256),
        "contest_tool_acceptance": binding(CONTEST_TOOL_ACCEPTANCE, EXPECTED_CONTEST_TOOL_ACCEPTANCE_SHA256),
        "primary_maps": verify_file_set(primary_maps, "primary closure maps"),
        "supplement_maps": verify_file_set(supplement_maps, "supplement closure maps"),
        "counts": {"source_records": 8357, "primary_overlays": 459, "supplement_overlays": 100, "total_overlays": 559, "guide_groups": 3, "guide_images": 39, "guide_previews": 22},
        "new_images": 0,
        "new_image_bytes": 0,
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }
    closure_bytes = json_bytes(closure_payload)
    map_meta = {
        "primary": {"path": rel(V34_PRIMARY_MAP), "sha256": hashlib.sha256(primary_map_bytes).hexdigest(), "items": 0, "bytes": 0},
        "supplement": {"path": rel(V34_SUPPLEMENT_MAP), "sha256": hashlib.sha256(supplement_map_bytes).hexdigest(), "items": 0, "bytes": 0},
    }
    preparation = {
        "schema": "wow-recovery.integration.v34-input-preparation.v1",
        "status": "prepared_waiting_root_v34_input_acceptance",
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "source_closure": {"path": rel(V34_SOURCE_CLOSURE), "sha256": hashlib.sha256(closure_bytes).hexdigest()},
        "new_images": {"count": 0, "bytes": 0, "accepted_source_receipts": []},
        "frozen_v33": {"primary_overlays": 459, "supplement_overlays": 100, "total_overlays": 559, "provenance": binding(V33_PROVENANCE, EXPECTED_V33_PROVENANCE_SHA256)},
        "new_maps": map_meta,
        "guide_maps": {"preview": binding(GUIDE_PREVIEW_MAP), "collection": binding(GUIDE_COLLECTION_MAP)},
        "tool_bindings": {"exporter": binding(EXPORTER, EXPECTED_EXPORTER_SHA256), "historical_exhibits": binding(HISTORICAL_EXHIBITS, EXPECTED_HISTORICAL_EXHIBITS_SHA256), "contest_tool_acceptance": binding(CONTEST_TOOL_ACCEPTANCE, EXPECTED_CONTEST_TOOL_ACCEPTANCE_SHA256)},
        "root_acceptance_required": {"path": "research/continuous-recovery-20261019/publication/root-v34-input-acceptance.json"},
        "expected_after_export": {"source_records": 8357, "primary_overlays": 459, "supplement_overlays": 100, "total_overlays": 559, "declared_files": 9017, "actual_files": 9018, "runtime_allowed_changes": {"contest_navtree_fallback_repaired": 1, "new_image_overlays": 0}},
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    preflight = {
        "schema": "wow-recovery.integration.v34-preflight.v1",
        "status": "preflight_passed_waiting_root_v34_input_acceptance",
        "checked_utc": preparation["checked_utc"],
        "source_closure": preparation["source_closure"],
        "new_image_count": 0,
        "new_image_bytes": 0,
        "map_validation": {"primary": {"items": 0, "bytes": 0}, "supplement": {"items": 0, "bytes": 0}},
        "loader_preflight": {"primary_overlay_records": 459, "supplement_overlay_records": 100, "total_overlay_records": 559, "new_primary_records": 0, "new_supplement_records": 0, "guide_collection_groups": 3, "guide_collection_images": 39, "guide_previews": 22, "network_requests": 0, "export_executed": False, "old_image_payloads_rehashed": False},
        "expected_after_export": preparation["expected_after_export"],
        "frozen_pins": closure_payload,
        "root_input_acceptance_required": True,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    proposal = """# v34 input proposal\n\nv34 is a preparation-only rebuild of the accepted v33 closure. It adds no\nimage source rows and does not inspect pending network folders. The closure\nremains 459 primary overlays, 100 supplement overlays, 559 total overlays,\n39 guide images, and 22 guide previews.\n\nThe only planned derived difference is the accepted exact-route contest\nnavigation fallback in `tools/export_github_pages.py`, bound to the root\ncontest-tool receipt. The source15 site and both manifests remain the frozen\ninputs; v33 output is not used as the new source tree.\n\nThe future output is `.scratch/pages-resources-20261019-v34`. It must not\nexist before the explicit root v34 input gate and `--go --root-export-go`.\nExpected counts are 9017 declared files and 9018 actual files, subject to\nroot post-export acceptance.\n"""
    runner_note = """# v34 runner preparation\n\n`execute_v34.py --go --root-export-go` is a one-shot wrapper. It refuses an\nabsent or unaccepted `research/continuous-recovery-20261019/publication/\nroot-v34-input-acceptance.json`, checks every prepared and frozen binding,\nrequires zero new image rows, checks the D: disk floor, refuses an existing\noutput/partial/receipt, and calls the current exporter once. It uses the\nfrozen source15 site and maps; it never reads v33 output as source and never\nrebuilds maps or preflight.\n"""
    # Write the closure first so preparation can bind its exact bytes.
    write_once(V34_SOURCE_CLOSURE, closure_bytes, "v34 source closure")
    preparation["source_closure"] = binding(V34_SOURCE_CLOSURE, hashlib.sha256(closure_bytes).hexdigest())
    write_once(V34_PRIMARY_MAP, primary_map_bytes, "v34 primary map")
    write_once(V34_SUPPLEMENT_MAP, supplement_map_bytes, "v34 supplement map")
    write_once(V34_PREPARATION, preparation, "v34 preparation")
    write_once(V34_PREFLIGHT, preflight, "v34 preflight")
    write_once(V34_PROPOSAL, proposal, "v34 proposal")
    write_once(V34_RUNNER_NOTE, runner_note, "v34 runner note")
    print(json.dumps({"status": preflight["status"], "new_images": 0, "primary": 459, "supplement": 100, "total": 559, "declared": 9017, "actual": 9018, "export_executed": False, "network_requests": 0, "disk_free_bytes": free_before}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
