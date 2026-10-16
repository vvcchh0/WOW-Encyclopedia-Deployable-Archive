#!/usr/bin/env python3
"""Independent, read-only reconciliation of the completed v19 output tree."""

from __future__ import annotations

import hashlib
import json
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HELPER = ROOT / "research/continuous-recovery-20261016/integration/v19-build/build_pages_v19.py"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v19"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/post-export-reconciliation-v19.json"
V19_MAP = ROOT / "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json"
V18_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v18/export-provenance.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"not an object: {path}")
    return payload


def local_source(map_path: Path, local_path: str) -> Path:
    candidate = Path(local_path)
    if candidate.is_absolute():
        return candidate
    first = (map_path.parent / candidate).resolve()
    if first.is_file():
        return first
    return (ROOT / candidate).resolve()


def main() -> int:
    if RECEIPT.exists():
        raise RuntimeError(f"refusing to overwrite reconciliation receipt: {RECEIPT}")
    if not OUTPUT.is_dir() or (OUTPUT.with_name(OUTPUT.name + ".partial")).exists():
        raise RuntimeError("v19 output is incomplete or partial")
    module = runpy.run_path(str(HELPER))
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages as exporter
    provenance_path = OUTPUT / "export-provenance.json"
    provenance = read(provenance_path)
    stats = provenance.get("stats") or {}
    files = provenance.get("files") or []
    if len(files) != 8537 or stats.get("output_files") != 8537:
        raise RuntimeError("v19 provenance file count is not 8537")

    file_failures: list[dict[str, Any]] = []
    seen_output_paths: set[str] = set()
    for index, item in enumerate(files, start=1):
        if index == 1 or index % 500 == 0 or index == len(files):
            print(f"reconcile derived files {index}/{len(files)}", flush=True)
        output_path = str(item.get("output_path") or "")
        if not output_path or output_path in seen_output_paths:
            file_failures.append({"output_path": output_path, "reason": "missing_or_duplicate_output_path"})
            continue
        seen_output_paths.add(output_path)
        output_file = OUTPUT / output_path
        if not output_file.is_file():
            file_failures.append({"output_path": output_path, "reason": "missing"})
            continue
        data_sha = sha256(output_file)
        data_len = output_file.stat().st_size
        expected_derived_length = item.get("derived_length")
        if data_sha != str(item.get("derived_sha256") or "") or (
            expected_derived_length is not None and data_len != int(expected_derived_length)
        ):
            file_failures.append(
                {
                    "output_path": output_path,
                    "reason": "derived_hash_or_length_mismatch",
                    "actual_sha256": data_sha,
                    "provenance_sha256": item.get("derived_sha256"),
                    "actual_length": data_len,
                    "provenance_length": item.get("derived_length"),
                }
            )
    actual_files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
    if actual_files != 8538:
        raise RuntimeError(f"v19 actual output count is not 8538: {actual_files}")

    source_map_cache: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    map_failures: list[dict[str, Any]] = []
    overlay_items = [item for item in files if item.get("role") == "image_overlay"]
    for overlay in overlay_items:
        map_rel = str(overlay.get("source_map") or "")
        map_path = (ROOT / map_rel).resolve()
        map_sha = str(overlay.get("source_map_sha256") or "")
        if not map_path.is_file() or sha256(map_path) != map_sha:
            map_failures.append({"route": overlay.get("route"), "reason": "source_map_missing_or_sha_mismatch", "source_map": map_rel})
            continue
        cache_key = f"{map_rel}:{map_sha}"
        if cache_key not in source_map_cache:
            source_map_cache[cache_key] = (map_path, read(map_path))
        _, source_map = source_map_cache[cache_key]
        matches: list[dict[str, Any]] = []
        source_original = str(overlay.get("original_url") or "")
        for entity in source_map.get("items", []):
            logical = str(entity.get("logical_url") or entity.get("original") or "")
            if not logical:
                continue
            entity_route = (
                exporter.mirror.route_path(logical)
                if exporter.mirror.is_primary_origin(logical)
                else exporter.mirror.origin_route(logical)
            )
            if entity_route == str(overlay.get("route") or ""):
                matches.append(entity)
        # The v19 source map is also accepted in the same format but has no
        # reason to be special here; route plus exact original avoids origin
        # joins when a map contains a shared path on another host.
        if map_path == V19_MAP:
            matches = [entity for entity in source_map.get("items", []) if str(entity.get("original") or entity.get("logical_url") or "") == source_original]
        exact_matches = [entity for entity in matches if str(entity.get("original") or entity.get("logical_url") or "") == source_original]
        # Legacy related-site maps intentionally keep equivalent default-port
        # origins in logical_url/original.  Their origin-namespaced route is
        # already exact within the selected map, so a unique route match is a
        # valid binding without inventing a cross-origin join.
        matches = exact_matches or (matches if len(matches) == 1 else [])
        if not matches:
            map_failures.append({"route": overlay.get("route"), "reason": "no_exact_map_item", "source_map": map_rel, "original_url": source_original})
            continue
        entity = matches[0]
        expected_sha = str(entity.get("sha256") or "").casefold()
        has_map_length = "length" in entity or "source_length" in entity
        expected_length = int(entity.get("length", entity.get("source_length", -1)))
        mismatches: dict[str, Any] = {}
        for key, expected, actual in (
            ("source_sha256", expected_sha, str(overlay.get("source_sha256") or "").casefold()),
            ("actual_timestamp", str(entity.get("actual_timestamp") or ""), str(overlay.get("actual_capture_timestamp") or "")),
            ("indexed_timestamp", str(entity.get("indexed_capture_timestamp") or ""), str(overlay.get("indexed_capture_timestamp") or "")),
            ("cdx_digest", str(entity.get("cdx_digest") or "").upper(), str(overlay.get("cdx_digest") or "").upper()),
        ):
            if expected != actual:
                mismatches[key] = {"expected": expected, "actual": actual}
        if has_map_length and expected_length != int(overlay.get("source_length") or -1):
            mismatches["source_length"] = {
                "expected": expected_length,
                "actual": int(overlay.get("source_length") or -1),
            }
        if mismatches:
            map_failures.append({"route": overlay.get("route"), "reason": "overlay_map_field_mismatch", "source_map": map_rel, "mismatches": mismatches})

    v19_map = read(V19_MAP)
    v19_map_routes = {exporter.mirror.route_path(str(item.get("original") or item.get("logical_url") or "")) for item in v19_map.get("items", [])}
    v19_overlay_routes = {str(item.get("route") or "") for item in overlay_items if str(item.get("source_map") or "") == rel(V19_MAP)}
    v18 = read(V18_PROVENANCE)
    v18_routes = {str(item.get("route") or "") for item in v18.get("files", []) if item.get("role") == "image_overlay"}
    checks = {
        "provenance_sha256": sha256(provenance_path),
        "provenance_declared_files": len(files),
        "actual_files_including_provenance": actual_files,
        "all_8537_derived_sha_length_verified": not file_failures,
        "derived_file_failures": file_failures,
        "overlay_records": len(overlay_items),
        "primary_overlay_records": stats.get("primary_image_overlay_records"),
        "supplement_overlay_records": stats.get("supplement_image_overlay_records"),
        "all_overlay_source_map_bindings_verified": not map_failures,
        "overlay_source_map_failures": map_failures,
        "v19_map_routes": sorted(v19_map_routes),
        "v19_map_route_count": len(v19_map_routes),
        "v19_provenance_route_count": len(v19_overlay_routes),
        "v19_routes_exact": v19_map_routes == v19_overlay_routes,
        "v18_overlay_route_count": len(v18_routes),
        "v18_overlay_routes_retained": v18_routes.issubset({str(item.get("route") or "") for item in overlay_items}),
        "source_manifest_sha256": provenance.get("source_manifest_sha256"),
        "source_records": stats.get("source_records"),
        "guide_preview_count": stats.get("guide_preview_count"),
        "guide_preview_gallery_pages": stats.get("guide_preview_gallery_pages"),
    }
    if file_failures or map_failures or not checks["v19_routes_exact"] or not checks["v18_overlay_routes_retained"]:
        raise RuntimeError(json.dumps(checks, ensure_ascii=False))
    payload = {
        "schema": "wow-recovery.integration.v19.post-export-reconciliation.v1",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0,
        "export_invocations": 0,
        "output": rel(OUTPUT),
        "worker_failure_receipt_preserved": True,
        "builder_helper_sha256": sha256(HELPER),
        "v19_map_sha256": sha256(V19_MAP),
        "checks": checks,
        "accepted": True,
    }
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
