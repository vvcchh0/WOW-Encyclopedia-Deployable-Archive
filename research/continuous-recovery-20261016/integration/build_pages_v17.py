"""Run the single root-authorized v17 Pages export from frozen inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v17"
ROOT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json"
WORKER_TEST_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-verification.json"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
V16_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v16/export-provenance.json"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/worker-build-v17.json"
MIN_FREE_BYTES = 11_005_853_696
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

FROZEN_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
ORIGINAL_OFFLINE_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V16_PROVENANCE_SHA256 = "853214cc4324c2e15c96858cbfbe0fad67a93293121a9a3ffb86b7969e14daec"
ROOT_ACCEPTANCE_SHA256 = "d45384119fe8ba9578a0a11a25ce79653460f2a65562423a5ad66ebd17883429"
WORKER_TEST_RECEIPT_SHA256 = "5dfd4db8f6db8bd6542001e7c4d068ae4ae8b228219b258ec270d3b2e79862f7"

PRODUCTION_SHA256 = {
    "tools/guide_previews.py": "7281dd7f56b1f54da8c13088f2b5bd89f90aa73c11a5f8a326a03ac1187bd2a3",
    "tools/export_github_pages.py": "c16647890b488f534aa7945f3333ca38a6583b8ca6dad6ce70e40a06d3685de9",
    "tests/test_guide_previews.py": "a761ebc1a0e301f494a39273c7d05717c198a804f848575801c60227eb11c561",
}

MAP_SHA256 = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/guide-previews-source-map.json": "cf0da5fec45993684676d94d1cc09fad3f5a421dabbb18b56861000daa6248b2",
}

PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
]
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_hash(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 changed: expected {expected}, got {actual}")
    return actual


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised only on damaged inputs
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def locked_input_hashes() -> dict[str, str]:
    paths: dict[str, tuple[Path, str]] = {
        "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json": (ROOT_ACCEPTANCE, ROOT_ACCEPTANCE_SHA256),
        "research/continuous-recovery-20261016/integration/guide-previews-verification.json": (WORKER_TEST_RECEIPT, WORKER_TEST_RECEIPT_SHA256),
        ".scratch/offline-navigation-20261015-v15/build-manifest.json": (SOURCE_MANIFEST, FROZEN_MANIFEST_SHA256),
        "offline/build-manifest.json": (ORIGINAL_OFFLINE_MANIFEST, ORIGINAL_OFFLINE_MANIFEST_SHA256),
        ".scratch/pages-resources-20261016-v16/export-provenance.json": (V16_PROVENANCE, V16_PROVENANCE_SHA256),
    }
    for relative, expected in PRODUCTION_SHA256.items():
        paths[relative] = (ROOT / relative, expected)
    for relative, expected in MAP_SHA256.items():
        paths[relative] = (ROOT / relative, expected)
    return {rel(path): require_hash(path, expected, relative) for relative, (path, expected) in paths.items()}


def validate_root_gate() -> dict[str, Any]:
    acceptance = read_object(ROOT_ACCEPTANCE, "root v17 input acceptance")
    if acceptance.get("accepted") is not True or acceptance.get("export_started") is not False:
        raise RuntimeError("root v17 input acceptance is not accepted and pre-export")
    if acceptance.get("production_sha256") != PRODUCTION_SHA256:
        raise RuntimeError("root v17 production SHA lock differs")
    if acceptance.get("map_sha256") != MAP_SHA256:
        raise RuntimeError("root v17 map SHA lock differs")
    expected_counts = {
        "guide_preview_count": 19,
        "guide_gallery_pages": 5,
        "new_news_images": 20,
        "new_news_bytes": 100831,
        "primary_overlays": 48,
        "supplement_overlays": 21,
        "total_overlays": 69,
        "source_records": 8357,
    }
    for key, expected in expected_counts.items():
        if acceptance.get(key) != expected:
            raise RuntimeError(f"root v17 count lock differs for {key}: {acceptance.get(key)!r}")
    if acceptance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256:
        raise RuntimeError("root v17 source manifest lock differs")
    return acceptance


def output_file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def verify_postbuild(result: dict[str, Any], root_acceptance: dict[str, Any]) -> dict[str, Any]:
    if not OUTPUT.is_dir() or (OUTPUT.with_name(OUTPUT.name + ".partial")).exists():
        raise RuntimeError("v17 output or partial output state is invalid after export")
    provenance_path = OUTPUT / "export-provenance.json"
    provenance = read_object(provenance_path, "v17 export provenance")
    stats = provenance.get("stats") or {}
    if result.get("output_files") != 8527 or stats.get("output_files") != 8527:
        raise RuntimeError(f"v17 declared output count is not 8527: result={result.get('output_files')}, provenance={stats.get('output_files')}")
    actual_files = output_file_count(OUTPUT)
    if actual_files != 8528:
        raise RuntimeError(f"v17 actual file count is not 8528: {actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or stats.get("source_records") != 8357:
        raise RuntimeError("v17 provenance does not bind the frozen source manifest")
    expected_stats = {
        "image_overlay": 69,
        "image_overlay_records": 69,
        "primary_image_overlay_records": 48,
        "supplement_image_overlay_records": 21,
        "guide_preview_gallery_pages": 5,
        "guide_preview_count": 19,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v17 provenance stat {key} is {stats.get(key)!r}, expected {expected}")
    guide_provenance = provenance.get("guide_previews") or {}
    if guide_provenance.get("preview_count") != 19 or guide_provenance.get("group_count") != 5:
        raise RuntimeError("v17 guide preview provenance count is wrong")

    overlays = [item for item in provenance.get("files", []) if item.get("role") == "image_overlay"]
    if len(overlays) != 69:
        raise RuntimeError(f"v17 overlay records are not 69: {len(overlays)}")
    primary = [item for item in overlays if item.get("supplement_strategy") == "primary_image_overlay"]
    supplements = [item for item in overlays if item.get("supplement_strategy") == "explicit_supplement_image_overlay"]
    if len(primary) != 48 or len(supplements) != 21:
        raise RuntimeError(f"v17 overlay strategy counts are wrong: primary={len(primary)}, supplements={len(supplements)}")

    old_provenance = read_object(V16_PROVENANCE, "v16 export provenance")
    old_overlays = {str(item.get("route")): item for item in old_provenance.get("files", []) if item.get("role") == "image_overlay"}
    new_overlays = {str(item.get("route")): item for item in overlays}
    if len(old_overlays) != 49:
        raise RuntimeError(f"v16 retained overlay provenance is not 49: {len(old_overlays)}")
    retained_mismatches: list[str] = []
    for route, old_item in old_overlays.items():
        new_item = new_overlays.get(route)
        output_file = OUTPUT / str(old_item.get("output_path") or "")
        if new_item is None or not output_file.is_file() or sha256(output_file) != str(old_item.get("derived_sha256") or ""):
            retained_mismatches.append(route)
    if retained_mismatches:
        raise RuntimeError(f"v16 retained overlay bytes changed: {retained_mismatches[:5]}")

    section_checks: dict[str, dict[str, Any]] = {}
    notice = "These previews survive in the original guide pages. Full-size gallery images are still incomplete."
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "tools"))
    import guide_previews as _guide_previews
    import export_github_pages as _exporter

    for group_id, (_label, gallery_route, _guide_route) in _guide_previews.EXPECTED_GROUPS.items():
        page_path = OUTPUT / _exporter.static_rel_for_route(gallery_route, {"kind": "html"})
        page = page_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{_guide_previews._slug(group_id)}"
        section_checks[group_id] = {
            "path": rel(page_path),
            "section_id_count": page.count(f'id="{section_id}"'),
            "title_count": page.count("Preserved guide previews"),
            "notice_count": page.count(notice),
            "view_original_guide_count": page.count("View original guide"),
        }
        if any(value != 1 for key, value in section_checks[group_id].items() if key.endswith("_count")):
            raise RuntimeError(f"v17 guide preview section count failed: {group_id}")

    v17_overlay_routes = {
        str(item.get("route"))
        for item in overlays
        if str(item.get("source_map") or "").endswith("v17-primary-news-image-source-map.json")
    }
    if len(v17_overlay_routes) != 20:
        raise RuntimeError(f"v17 new NEWS overlay provenance count is not 20: {len(v17_overlay_routes)}")

    return {
        "declared_output_files": result.get("output_files"),
        "provenance_declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "source_records": stats.get("source_records"),
        "overlay_records": len(overlays),
        "primary_overlay_records": len(primary),
        "supplement_overlay_records": len(supplements),
        "retained_v16_overlay_records": len(old_overlays),
        "retained_v16_overlay_bytes_verified": True,
        "new_v17_news_overlay_records": len(v17_overlay_routes),
        "guide_preview_count": guide_provenance.get("preview_count"),
        "guide_gallery_pages": guide_provenance.get("group_count"),
        "guide_sections": section_checks,
        "root_expected_counts_repeated": {
            key: root_acceptance.get(key)
            for key in ("primary_overlays", "supplement_overlays", "total_overlays", "guide_preview_count", "guide_gallery_pages")
        },
    }


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = "python -X utf8 research/continuous-recovery-20261016/integration/build_pages_v17.py"
    started = now()
    export_started = False
    result: dict[str, Any] | None = None
    root_acceptance: dict[str, Any] | None = None
    locks_before: dict[str, str] | None = None
    free_before: int | None = None
    try:
        if RECEIPT.exists():
            raise RuntimeError(f"refusing to overwrite existing worker receipt: {RECEIPT}")
        root_acceptance = validate_root_gate()
        locks_before = locked_input_hashes()
        if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
            raise RuntimeError("frozen v15 source/site is missing")
        if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
            raise RuntimeError("refusing to overwrite existing v17 output or partial")
        free_before = shutil.disk_usage(OUTPUT.parent).free
        if free_before < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")

        sys.path.insert(0, str(ROOT / "tools"))
        import export_github_pages

        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=PRIMARY_MAPS,
            supplement_image_source_maps=SUPPLEMENT_MAPS,
            allow_later_image_supplements=True,
            guide_preview_map=GUIDE_PREVIEW_MAP,
        )
        postbuild = verify_postbuild(result, root_acceptance)
        locks_after = locked_input_hashes()
        if locks_before != locks_after:
            raise RuntimeError("a locked source/map/production input changed during export")
        free_after = shutil.disk_usage(OUTPUT.parent).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor after export: {free_after} < {MIN_FREE_BYTES}")
        receipt = {
            "schema": "wow-recovery.integration.v17.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": True,
            "export_completed": True,
            "network_requests_by_builder": 0,
            "published": False,
            "source_stage": rel(SOURCE_STAGE),
            "source_stage_reused": True,
            "source_site": rel(SOURCE_SITE),
            "source_manifest": rel(SOURCE_MANIFEST),
            "source_manifest_sha256": locks_after[rel(SOURCE_MANIFEST)],
            "original_offline_manifest": rel(ORIGINAL_OFFLINE_MANIFEST),
            "original_offline_manifest_sha256": locks_after[rel(ORIGINAL_OFFLINE_MANIFEST)],
            "v16_export_provenance": rel(V16_PROVENANCE),
            "v16_export_provenance_sha256": locks_after[rel(V16_PROVENANCE)],
            "root_input_acceptance": rel(ROOT_ACCEPTANCE),
            "root_input_acceptance_sha256": locks_after[rel(ROOT_ACCEPTANCE)],
            "worker_test_receipt": rel(WORKER_TEST_RECEIPT),
            "worker_test_receipt_sha256": locks_after[rel(WORKER_TEST_RECEIPT)],
            "primary_source_maps": [rel(path) for path in PRIMARY_MAPS],
            "supplement_source_maps": [rel(path) for path in SUPPLEMENT_MAPS],
            "guide_preview_map": rel(GUIDE_PREVIEW_MAP),
            "map_sha256_before": {rel(path): locks_before[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP]},
            "map_sha256_after": {rel(path): locks_after[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, GUIDE_PREVIEW_MAP]},
            "maps_unchanged_during_export": True,
            "production_sha256_before": {key: locks_before[key] for key in PRODUCTION_SHA256},
            "production_sha256_after": {key: locks_after[key] for key in PRODUCTION_SHA256},
            "production_unchanged_during_export": True,
            "root_acceptance_sha256_locked": ROOT_ACCEPTANCE_SHA256,
            "root_expected_primary_overlay_count": 48,
            "root_expected_supplement_overlay_count": 21,
            "root_expected_total_overlay_count": 69,
            "root_expected_guide_preview_count": 19,
            "root_expected_guide_gallery_pages": 5,
            "build": result,
            "postbuild_checks": postbuild,
            "output": rel(OUTPUT),
            "output_refused_if_existing_or_partial": True,
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
            "input_hashes_before": locks_before,
            "input_hashes_after": locks_after,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        free_after = shutil.disk_usage(OUTPUT.parent).free
        failure = {
            "schema": "wow-recovery.integration.v17.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": export_started,
            "export_completed": False,
            "network_requests_by_builder": 0,
            "published": False,
            "error": f"{type(exc).__name__}: {exc}",
            "output": rel(OUTPUT) if OUTPUT.exists() else None,
            "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if locks_before is not None:
            failure["input_hashes_before"] = locks_before
        try:
            write_receipt(failure)
        except Exception as receipt_exc:  # pragma: no cover - protects original failure reporting
            failure["receipt_write_error"] = f"{type(receipt_exc).__name__}: {receipt_exc}"
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
