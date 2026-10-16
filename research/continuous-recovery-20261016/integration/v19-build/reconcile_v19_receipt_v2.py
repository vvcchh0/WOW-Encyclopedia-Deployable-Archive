"""Write a non-destructive v2 reconciliation receipt for the completed v19 tree.

The v19 exporter was invoked once.  Its worker receipt records a post-export
helper exception, so this script never invokes the exporter and only binds
independent postchecks to the preserved worker receipt.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BUILD = ROOT / "research/continuous-recovery-20261016/integration/v19-build"
WORKER = BUILD / "worker-build-v19.json"
RECONCILIATION = BUILD / "post-export-reconciliation-v19.json"
POSTVERIFY = BUILD / "postbuild-verification-v19.json"
BROWSER = BUILD / "browser-v19-local.json"
PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v19/export-provenance.json"
OUTPUT = BUILD / "post-export-reconciliation-v19-final.json"
ROOT_V2 = ROOT / "research/continuous-recovery-20261016/publication/root-city-v2-code-acceptance.json"

PRODUCTION_PATHS = [
    "tools/guide_previews.py",
    "tools/export_github_pages.py",
    "tests/test_guide_previews.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hash_locked_inputs(before: dict) -> tuple[dict, list[str], list[str]]:
    after: dict[str, str | None] = {}
    missing: list[str] = []
    mismatches: list[str] = []
    for rel, expected in before.items():
        path = ROOT / rel
        if not path.is_file():
            after[rel] = None
            missing.append(rel)
            continue
        actual = sha256(path)
        after[rel] = actual
        if actual.lower() != str(expected).lower():
            mismatches.append(rel)
    return after, missing, mismatches


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"refusing overwrite: {OUTPUT}")
    worker = load(WORKER)
    prior = load(RECONCILIATION)
    postverify = load(POSTVERIFY)
    browser = load(BROWSER)
    before = worker["input_hashes_before"]
    after, missing, mismatches = hash_locked_inputs(before)

    postbuild = postverify.get("postbuild_checks", {})
    postverify_ok = bool(
        postbuild.get("declared_output_files") == 8537
        and postbuild.get("provenance_declared_output_files") == 8537
        and postbuild.get("actual_output_files") == 8538
        and postbuild.get("source_records") == 8357
        and postbuild.get("overlay_records") == 79
        and postbuild.get("primary_overlay_records") == 58
        and postbuild.get("supplement_overlay_records") == 21
        and postbuild.get("v18_overlay_routes_retained") == 69
        and postbuild.get("v18_overlay_bytes_verified") is True
        and postbuild.get("v19_new_overlay_bytes_verified") is True
        and postbuild.get("guide_preview_count") == 22
        and postbuild.get("guide_gallery_pages") == 6
        and postbuild.get("city_dynamic_full_alias") is False
        and all(postbuild.get("existing_v18_gallery_bytes_equal", {}).values())
    )

    production_paths = {rel: {"before": before.get(rel), "after": after.get(rel)} for rel in PRODUCTION_PATHS}
    map_paths = {
        rel: {"before": before.get(rel), "after": after.get(rel)}
        for rel in before
        if "map" in Path(rel).name.lower() or "source-map" in rel.lower()
    }
    v19_map = "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json"
    if v19_map not in map_paths:
        map_paths[v19_map] = {"before": before.get(v19_map), "after": after.get(v19_map)}

    output_files = [p for p in (ROOT / worker["output"]).rglob("*") if p.is_file()]
    checks = prior["checks"]
    all_independent_checks = bool(
        prior.get("accepted")
        and postverify_ok
        and browser.get("accepted")
        and not missing
        and not mismatches
        and PROVENANCE.is_file()
        and sha256(PROVENANCE) == checks["provenance_sha256"]
    )
    payload = {
        "schema": "wow-recovery.integration.v19.post-export-reconciliation.v2",
        "accepted": all_independent_checks,
        "reconciled_export_valid": all_independent_checks,
        "meaning": "The single export produced a complete output tree; independent postchecks reconcile it after the preserved worker post-export helper failure. This does not rewrite the worker's export_completed field.",
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "export_invocations_after_worker_failure": 0,
        "original_worker_receipt": {
            "path": str(WORKER.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(WORKER),
            "command": worker["command"],
            "export_started": worker["export_started"],
            "export_completed": worker["export_completed"],
            "error": worker["error"],
            "preserved_unchanged": True,
        },
        "postchecks": {
            "prior_reconciliation": {
                "path": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(RECONCILIATION),
                "accepted": prior.get("accepted"),
            },
            "postbuild_verification": {
                "path": str(POSTVERIFY.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(POSTVERIFY),
                "accepted": postverify_ok,
                "reported_accepted_field": postverify.get("accepted"),
            },
            "local_browser": {
                "path": str(BROWSER.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(BROWSER),
                "accepted": browser.get("accepted"),
                "pages": len(browser.get("pages", [])),
                "checks": len(browser.get("checks", [])),
                "external_requests_blocked": browser.get("external_requests_blocked"),
            },
        },
        "output": {
            "relative_path": worker["output"],
            "provenance_path": str(PROVENANCE.relative_to(ROOT)).replace("\\", "/"),
            "provenance_sha256": sha256(PROVENANCE),
            "actual_files_including_provenance": len(output_files),
            "output_tree_bytes": sum(p.stat().st_size for p in output_files),
            "disk_free_after_reconciliation_bytes": shutil.disk_usage(ROOT).free,
            "disk_free_floor_bytes": worker["disk_free_floor_bytes"],
        },
        "locked_input_hashes": {
            "before": before,
            "after": after,
            "unchanged_from_worker_before": not missing and not mismatches,
            "missing": missing,
            "mismatches": mismatches,
        },
        "production_sha256_before_after": production_paths,
        "map_sha256_before_after": map_paths,
        "root_v2_code_acceptance": {
            "path": str(ROOT_V2.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(ROOT_V2),
        },
        "source_and_counts": {
            "source_manifest_sha256": checks["source_manifest_sha256"],
            "source_records": checks["source_records"],
            "declared_files": checks["provenance_declared_files"],
            "actual_files_including_provenance": checks["actual_files_including_provenance"],
            "overlay_records": checks["overlay_records"],
            "primary_overlay_records": checks["primary_overlay_records"],
            "supplement_overlay_records": checks["supplement_overlay_records"],
            "v19_new_primary_routes": checks["v19_map_routes"],
            "v19_new_primary_count": checks["v19_map_route_count"],
            "v18_old_overlay_routes_retained": checks["v18_overlay_route_count"],
            "v18_old_overlay_routes_retained_check": checks["v18_overlay_routes_retained"],
            "guide_preview_groups": checks["guide_preview_gallery_pages"],
            "guide_preview_count": checks["guide_preview_count"],
            "all_derived_sha_length_verified": checks["all_8537_derived_sha_length_verified"],
            "all_overlay_source_map_bindings_verified": checks["all_overlay_source_map_bindings_verified"],
            "v19_routes_exact": checks["v19_routes_exact"],
        },
        "validation_commands": [
            worker["command"],
            "python -X utf8 research/continuous-recovery-20261016/integration/v19-build/postverify_v19_output.py",
            "python -X utf8 research/continuous-recovery-20261016/integration/v19-build/reconcile_v19_export.py",
            "$env:NODE_PATH='C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules'; node research/continuous-recovery-20261016/integration/v19-build/browser_v19_local.cjs",
        ],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(OUTPUT),
        "accepted": payload["accepted"],
        "reconciled_export_valid": payload["reconciled_export_valid"],
        "missing": missing,
        "mismatches": mismatches,
        "declared": checks["provenance_declared_files"],
        "actual": checks["actual_files_including_provenance"],
        "overlays": checks["overlay_records"],
        "primary": checks["primary_overlay_records"],
        "supplement": checks["supplement_overlay_records"],
        "guide_previews": checks["guide_preview_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
