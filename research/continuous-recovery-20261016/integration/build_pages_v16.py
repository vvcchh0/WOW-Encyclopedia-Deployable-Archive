"""Export v16 only after root GO; prepared with frozen v15 source and accepted maps."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / ".scratch/offline-navigation-20261015-v15"
DEFAULT_OUTPUT = ROOT / ".scratch/pages-resources-20261016-v16"
DEFAULT_NEWS_MAP = ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json"
DEFAULT_EU2_MAP = ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json"
DEFAULT_PRECHECK = ROOT / "research/continuous-recovery-20261016/integration/loader-precheck-v16-final.json"
ACCEPTED_NEWS_MAX = 13
MIN_FREE_BYTES = 11_005_853_696
FROZEN_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
ORIGINAL_OFFLINE_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V15_PROVENANCE = ROOT / ".scratch/pages-resources-20261015-v15/export-provenance.json"
V15_PROVENANCE_SHA256 = "be0c336f831e19e63dedc4ada87ed672c620863061f9696e42048dfc1cea890a"
PRODUCTION_FILES = [
    ROOT / "tools/export_github_pages.py",
    ROOT / "tools/offline_mirror.py",
    ROOT / "tools/historical_exhibits.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def ensure_hash(path: Path, expected: str, label: str) -> str:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} hash changed: expected {expected}, got {actual}")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepared v16 exporter; run only after root GO")
    parser.add_argument("--news-primary-map", type=Path, default=DEFAULT_NEWS_MAP)
    parser.add_argument("--eu2-map", type=Path, default=DEFAULT_EU2_MAP)
    parser.add_argument("--precheck", type=Path, default=DEFAULT_PRECHECK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.output.exists():
        raise RuntimeError(f"refusing to overwrite existing v16 output: {args.output}")
    partial = args.output.with_name(args.output.name + ".partial")
    if partial.exists():
        raise RuntimeError(f"refusing to reuse existing v16 partial output: {partial}")
    free_before = shutil.disk_usage(args.output.parent.resolve()).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")

    source_manifest = SOURCE / "build-manifest.json"
    ensure_hash(source_manifest, FROZEN_MANIFEST_SHA256, "frozen v15 manifest")
    ensure_hash(ORIGINAL_OFFLINE_MANIFEST, ORIGINAL_OFFLINE_MANIFEST_SHA256, "original offline manifest")
    ensure_hash(V15_PROVENANCE, V15_PROVENANCE_SHA256, "v15 export provenance")
    if not args.precheck.is_file():
        raise RuntimeError(f"final loader precheck missing: {args.precheck}")
    precheck = json.loads(args.precheck.read_text(encoding="utf-8"))
    precheck_assertions = precheck.get("assertions") or {}
    if precheck_assertions.get("no_export_started") is not True or precheck_assertions.get("no_network_requests") is not True:
        raise RuntimeError("final loader precheck does not prove no prior export/network")
    if precheck.get("accepted_inputs", {}).get("current_or_final_primary_loader_count") != 28:
        raise RuntimeError("final loader precheck primary count is not 28")
    if precheck.get("accepted_inputs", {}).get("supplement_loader_count") != 21:
        raise RuntimeError("final loader precheck supplement count is not 21")
    news_map = args.news_primary_map.resolve()
    eu2_map = args.eu2_map.resolve()
    payload = json.loads(news_map.read_text(encoding="utf-8"))
    news_count = len(payload.get("items") or [])
    if news_count != 9:
        raise RuntimeError(f"final NEWS map must contain exactly 9 root-accepted items: {news_count}")
    eu2_payload = json.loads(eu2_map.read_text(encoding="utf-8"))
    eu2_count = len(eu2_payload.get("items") or [])
    if eu2_count != 2:
        raise RuntimeError(f"final EU2 map must contain exactly 2 accepted items: {eu2_count}")

    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages

    implementation_files = PRODUCTION_FILES
    implementation_before = {rel(path): sha256(path) for path in implementation_files}
    if implementation_before[rel(PRODUCTION_FILES[0])] != "636925a2b9721f408b7d9225d3c8e63c2bab1232b51225a8963c6f9cd443258e":
        raise RuntimeError("export_github_pages.py is not the approved production revision")
    if implementation_before[rel(PRODUCTION_FILES[1])] != "8171683dc6b74237d3a655697c9930932fe863f8200685f16da8d4c29c1c635a":
        raise RuntimeError("offline_mirror.py is not the approved production revision")
    if implementation_before[rel(PRODUCTION_FILES[2])] != "3ad2472adbf351ad3340b4277e53e94ac25d33574f5bcdea06f067e5a5d027ac":
        raise RuntimeError("historical_exhibits.py is not the approved production revision")
    primary = [
        ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
        ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
        news_map,
    ]
    supplements = [
        ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
        ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
        ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
        eu2_map,
    ]
    map_hashes_before = {rel(path): sha256(path) for path in primary + supplements}
    result = export_github_pages.export_pages(
        source_site=SOURCE / "site",
        manifest_path=SOURCE / "build-manifest.json",
        output=args.output.resolve(),
        image_source_maps=primary,
        supplement_image_source_maps=supplements,
        allow_later_image_supplements=True,
        min_free_bytes=MIN_FREE_BYTES,
    )
    implementation_after = {rel(path): sha256(path) for path in implementation_files}
    map_hashes_after = {rel(path): sha256(path) for path in primary + supplements}
    free_after = shutil.disk_usage(args.output.parent.resolve()).free
    receipt = {
        "schema": "wow-recovery.integration.v16.build-receipt",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "executed_by": "/root/local_recovery_20261016",
        "export_started": True,
        "export_completed": True,
        "build": result,
        "source_stage": rel(SOURCE),
        "source_stage_reused": True,
        "source_manifest": rel(source_manifest),
        "source_manifest_sha256": sha256(source_manifest),
        "original_offline_manifest": rel(ORIGINAL_OFFLINE_MANIFEST),
        "original_offline_manifest_sha256": sha256(ORIGINAL_OFFLINE_MANIFEST),
        "v15_export_provenance": rel(V15_PROVENANCE),
        "v15_export_provenance_sha256": sha256(V15_PROVENANCE),
        "final_loader_precheck": rel(args.precheck),
        "final_loader_precheck_sha256": sha256(args.precheck),
        "primary_source_maps": [rel(path) for path in primary],
        "supplement_source_maps": [rel(path) for path in supplements],
        "primary_overlay_count_expected": 28,
        "supplement_overlay_count_expected": 21,
        "total_overlay_count_expected": 49,
        "news_primary_item_count": news_count,
        "eu2_supplement_item_count": eu2_count,
        "map_sha256_before": map_hashes_before,
        "map_sha256_after": map_hashes_after,
        "maps_unchanged_during_export": map_hashes_before == map_hashes_after,
        "allow_later_image_supplements": True,
        "published": False,
        "network_requests_by_builder": 0,
        "disk_free_before_bytes": free_before,
        "disk_free_after_bytes": free_after,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
        "output_refused_if_existing_or_partial": True,
        "implementation_sha256_before": implementation_before,
        "implementation_sha256_after": implementation_after,
        "implementation_unchanged_during_export": implementation_before == implementation_after,
    }
    receipt_path = ROOT / "research/continuous-recovery-20261016/integration/root-build-v16.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
