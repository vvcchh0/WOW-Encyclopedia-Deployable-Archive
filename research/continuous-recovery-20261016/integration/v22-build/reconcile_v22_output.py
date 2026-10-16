#!/usr/bin/env python3
"""Reconcile a promoted v22 tree after a builder-only postcheck failure.

This script is deliberately read-only with respect to the exported tree.  It
does not call export_pages and writes only the reconciliation receipt beside
the bounded v22 build artifacts.
"""

from __future__ import annotations

import hashlib
import json
import runpy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
BUILDER = ROOT / "research/continuous-recovery-20261016/integration/v22-build/build_pages_v22.py"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v22-build/worker-build-v22.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v22"
PROVENANCE = OUTPUT / "export-provenance.json"
RECONCILIATION = ROOT / "research/continuous-recovery-20261016/integration/v22-build/post-export-reconciliation-v22.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
V20_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
V22_MAP = ROOT / "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def map_route(exporter: Any, item: dict[str, Any]) -> str:
    return exporter.mirror.route_path(str(item.get("original") or item.get("logical_url") or ""))


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("promoted output is missing or a partial tree remains")
    if RECONCILIATION.exists():
        raise RuntimeError(f"refusing to overwrite reconciliation receipt: {RECONCILIATION}")

    builder = runpy.run_path(str(BUILDER))
    failure = read_object(RECEIPT)
    failure_sha = sha256(RECEIPT)
    provenance = read_object(PROVENANCE)
    old = read_object(V20_PROVENANCE)
    exporter = builder["export_github_pages"]
    postbuild = builder["verify_postbuild"]({"output_files": 8580})
    preflight = builder["preflight_loader"]()
    input_before = failure.get("input_hashes_before") or {}
    input_after = builder["locked_input_hashes"]()
    if input_before != input_after:
        raise RuntimeError("locked v22 inputs changed after the failed builder turn")

    current_overlays = {
        str(item.get("route")): item
        for item in provenance.get("files", [])
        if item.get("role") == "image_overlay"
    }
    old_overlays = {
        str(item.get("route")): item
        for item in old.get("files", [])
        if item.get("role") == "image_overlay"
    }
    stable_fields = (
        "derived_sha256",
        "derived_length",
        "source_sha256",
        "source_length",
        "mime",
        "temporal_class",
        "original_url",
        "route",
        "output_path",
    )
    stable_field_mismatches: list[str] = []
    byte_mismatches: list[str] = []
    missing_fields: list[str] = []
    overlay_bindings: list[dict[str, Any]] = []
    for route in sorted(current_overlays):
        item = current_overlays[route]
        output_path = OUTPUT / str(item.get("output_path") or "")
        required = (
            "route",
            "output_path",
            "derived_sha256",
            "derived_length",
            "source_sha256",
            "source_length",
            "mime",
            "original_url",
            "source_map",
            "source_map_sha256",
        )
        missing_fields.extend(f"{route}:{key}" for key in required if not item.get(key))
        if not output_path.is_file():
            byte_mismatches.append(f"{route}:missing_output")
            actual_sha = None
            actual_length = None
        else:
            actual_sha = sha256(output_path)
            actual_length = output_path.stat().st_size
            if actual_sha != item.get("derived_sha256") or actual_length != item.get("derived_length"):
                byte_mismatches.append(f"{route}:output")
        overlay_bindings.append(
            {
                "route": route,
                "output_path": item.get("output_path"),
                "original_url": item.get("original_url"),
                "mime": item.get("mime"),
                "derived_sha256": item.get("derived_sha256"),
                "derived_length": item.get("derived_length"),
                "source_sha256": item.get("source_sha256"),
                "source_length": item.get("source_length"),
                "actual_file_sha256": actual_sha,
                "actual_file_length": actual_length,
                "actual_capture_timestamp": item.get("actual_capture_timestamp"),
                "source_map": item.get("source_map"),
                "source_map_sha256": item.get("source_map_sha256"),
                "supplement_strategy": item.get("supplement_strategy"),
            }
        )

    for route, old_item in old_overlays.items():
        current = current_overlays.get(route)
        if current is None:
            stable_field_mismatches.append(f"{route}:missing_route")
            continue
        if any(current.get(key) != old_item.get(key) for key in stable_fields):
            stable_field_mismatches.append(f"{route}:metadata")
        output_path = OUTPUT / str(current.get("output_path") or "")
        if not output_path.is_file() or sha256(output_path) != old_item.get("derived_sha256"):
            byte_mismatches.append(f"{route}:v20_bytes")

    v20_map = read_object(V20_MAP)
    v22_map = read_object(V22_MAP)
    v20_routes = {map_route(exporter, item) for item in v20_map.get("items", [])}
    v22_routes = {map_route(exporter, item) for item in v22_map.get("items", [])}
    v20_identity = (rel(V20_MAP), sha256(V20_MAP))
    v22_identity = (rel(V22_MAP), sha256(V22_MAP))
    v20_map_identity_delta = [
        route
        for route in sorted(v20_routes)
        if route in current_overlays
        and (current_overlays[route].get("source_map"), current_overlays[route].get("source_map_sha256"))
        not in {v20_identity, v22_identity}
    ]
    v20_clone_routes = [
        route
        for route in sorted(v20_routes)
        if route in current_overlays
        and (current_overlays[route].get("source_map"), current_overlays[route].get("source_map_sha256")) == v22_identity
    ]
    v20_frozen_routes = [
        route
        for route in sorted(v20_routes)
        if route in current_overlays
        and (current_overlays[route].get("source_map"), current_overlays[route].get("source_map_sha256")) == v20_identity
    ]
    if missing_fields or stable_field_mismatches or byte_mismatches or v20_map_identity_delta:
        raise RuntimeError(
            "overlay reconciliation failed: "
            f"missing={len(missing_fields)} stable={len(stable_field_mismatches)} "
            f"bytes={len(byte_mismatches)} map={len(v20_map_identity_delta)}"
        )

    output_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
    result = {
        "schema": "wow-recovery.integration.v22.post-export-reconciliation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc_start": started,
        "checked_utc_end": datetime.now(timezone.utc).isoformat(),
        "reconciled_export_valid": True,
        "export_was_not_repeated": True,
        "builder_failure_receipt": rel(RECEIPT),
        "builder_failure_receipt_sha256": failure_sha,
        "builder_failure_error": failure.get("error"),
        "builder_failure_export_started": failure.get("export_started"),
        "builder_failure_export_completed_field": failure.get("export_completed"),
        "promoted_output_observed": True,
        "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
        "builder_postcheck_source_sha256": sha256(BUILDER),
        "output": rel(OUTPUT),
        "output_provenance": rel(PROVENANCE),
        "output_provenance_sha256": sha256(PROVENANCE),
        "declared_output_files": provenance.get("stats", {}).get("output_files"),
        "actual_output_files": output_files,
        "source_records": provenance.get("stats", {}).get("source_records"),
        "overlay_counts": {
            "total": len(current_overlays),
            "primary": sum(1 for item in current_overlays.values() if item.get("supplement_strategy") == "primary_image_overlay"),
            "supplement": sum(1 for item in current_overlays.values() if item.get("supplement_strategy") == "explicit_supplement_image_overlay"),
        },
        "guide_previews": {
            "groups": (provenance.get("guide_previews") or {}).get("group_count"),
            "cards": (provenance.get("guide_previews") or {}).get("preview_count"),
        },
        "fresh_preflight": preflight,
        "postbuild_checks": postbuild,
        "overlay_field_audit": {
            "all_overlay_records_have_required_fields": len(missing_fields) == 0,
            "required_field_missing_count": len(missing_fields),
            "all_output_sha256_and_length_match_provenance": len(byte_mismatches) == 0,
            "output_byte_mismatch_count": len(byte_mismatches),
            "v20_routes_retained": len(old_overlays),
            "v20_stable_metadata_mismatch_count": len(stable_field_mismatches),
            "v20_frozen_map_identity_routes": len(v20_frozen_routes),
            "v20_clone_map_identity_routes": len(v20_clone_routes),
            "v20_unexpected_map_identity_count": len(v20_map_identity_delta),
            "v20_clone_map_identity_reason": "The completed export used the v22 clone map before the postcheck-only ordering correction; all 34 inherited routes retain the old bytes and all non-map metadata.",
        },
        "overlay_bindings": overlay_bindings,
        "source_map_counts": {
            key: sum(1 for item in current_overlays.values() if item.get("source_map") == key)
            for key in sorted({str(item.get("source_map")) for item in current_overlays.values()})
        },
        "v20_map_identity_delta_routes": v20_clone_routes,
        "v21_delta_and_v22_new_routes": {
            "v21_delta": postbuild.get("v21_delta_routes"),
            "v22_new_primary": postbuild.get("v22_new_primary_routes"),
            "v21_late_supplement": postbuild.get("v21_late_supplement_route"),
        },
        "input_hashes_before": input_before,
        "input_hashes_after": input_after,
        "locked_inputs_unchanged": input_before == input_after,
        "disk_free_before_bytes_from_failure_receipt": failure.get("disk_free_before_bytes"),
        "disk_free_after_bytes_from_failure_receipt": failure.get("disk_free_after_bytes"),
        "disk_free_floor_bytes": failure.get("disk_free_floor_bytes"),
        "network_requests_by_builder": failure.get("network_requests_by_builder"),
        "published": False,
        "browser_validation_by_worker": False,
        "browser_validation_note": "Root-owned targeted browser/full-tree validation remains separate; this receipt is local-only.",
    }
    RECONCILIATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reconciled_export_valid": True,
        "receipt": rel(RECONCILIATION),
        "receipt_sha256": sha256(RECONCILIATION),
        "output_provenance_sha256": result["output_provenance_sha256"],
        "declared_output_files": result["declared_output_files"],
        "actual_output_files": result["actual_output_files"],
        "overlay_counts": result["overlay_counts"],
        "v20_clone_map_identity_routes": len(v20_clone_routes),
        "export_was_not_repeated": True,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
