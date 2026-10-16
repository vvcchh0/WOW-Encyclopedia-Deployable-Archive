"""Independent post-export reconciliation for the single v20 local export.

This script only reads the accepted inputs, receipts, output tree, and local
browser receipt.  It never invokes the exporter and refuses to write anything
except the new reconciliation receipt beside this script.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image


ROOT = Path.cwd()
OUT = ROOT / ".scratch/pages-resources-20261016-v20"
BUILD = ROOT / "research/continuous-recovery-20261016/integration/v20-build"
RECEIPT_PATH = BUILD / "post-export-reconciliation-v20-final.json"


def rel(path: str | Path) -> str:
    return Path(path).as_posix()


def load(path: str | Path):
    with (ROOT / path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def digest(path: str | Path) -> str:
    h = hashlib.sha256()
    with (ROOT / path).open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha_from_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_check(path: Path, expected_dimensions: list[int]) -> dict:
    raw = file_bytes(path)
    with Image.open(path) as image:
        dimensions = [image.width, image.height]
        frames = int(getattr(image, "n_frames", 1))
    assert_true(dimensions == expected_dimensions, f"dimensions mismatch: {path}")
    assert_true(frames >= 1, f"no decoded frame: {path}")
    return {
        "sha256": sha_from_bytes(raw),
        "length": len(raw),
        "dimensions": dimensions,
        "decoded_frames": frames,
    }


def main() -> None:
    worker_path = "research/continuous-recovery-20261016/integration/v20-build/worker-build-v20.json"
    browser_path = "research/continuous-recovery-20261016/integration/v20-build/browser-v20-local.json"
    prep_path = "research/continuous-recovery-20261016/integration/v20-build/prepare-v20-inputs.json"
    map_path = "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
    v19_map_path = "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json"
    v19_prov_path = ".scratch/pages-resources-20261016-v19/export-provenance.json"
    prov_path = ".scratch/pages-resources-20261016-v20/export-provenance.json"
    acceptance_paths = [
        "research/continuous-recovery-20261016/publication/root-aug20-source-acceptance.json",
        "research/continuous-recovery-20261016/publication/root-aug-remaining15-source-acceptance.json",
    ]

    worker = load(worker_path)
    browser = load(browser_path)
    prep = load(prep_path)
    news_map = load(map_path)
    v19_map = load(v19_map_path)
    provenance = load(prov_path)
    v19_provenance = load(v19_prov_path)
    acceptances = [load(path) for path in acceptance_paths]

    # The worker receipt is historical evidence of the one exporter invocation;
    # this script is a post-check and must never make another invocation.
    assert_true(worker["export_started"] is True, "worker did not start export")
    assert_true(worker["export_completed"] is True, "worker did not report completed export")
    assert_true(worker["network_requests_by_builder"] == 0, "builder made network requests")
    assert_true(worker["published"] is False, "worker claims publication")
    assert_true(worker["output"] == ".scratch/pages-resources-20261016-v20", "wrong worker output")

    # Root accepted exactly two groups of twelve decoded image bodies.
    accepted_images = []
    acceptance_summary = []
    for path, record in zip(acceptance_paths, acceptances):
        assert_true(record.get("accepted") is True, f"root acceptance not true: {path}")
        rows = record.get("accepted_images", [])
        assert_true(len(rows) == 12, f"expected 12 accepted images: {path}")
        accepted_images.extend(rows)
        acceptance_summary.append(
            {
                "path": path,
                "sha256": digest(path),
                "accepted": True,
                "image_count": len(rows),
                "image_bytes": record.get("image_bytes"),
            }
        )
    assert_true(len(accepted_images) == 24, "accepted image count is not 24")
    accepted_by_original = {row["original"]: row for row in accepted_images}
    assert_true(len(accepted_by_original) == 24, "accepted originals are not unique")

    # v20 preserves the frozen ten v19 items and adds exactly these 24.
    v19_items = v19_map["items"]
    v20_items = news_map["items"]
    assert_true(len(v19_items) == 10, "v19 source map does not contain ten items")
    assert_true(len(v20_items) == 34, "v20 source map does not contain 34 items")
    assert_true(v20_items[:10] == v19_items, "v19 map items changed in v20 map")
    new_items = v20_items[10:]
    assert_true({row["original"] for row in new_items} == set(accepted_by_original), "new map originals differ from root accepted originals")

    local_asset_checks = []
    for item in new_items:
        accepted = accepted_by_original[item["original"]]
        for key in ("sha256", "length", "mime", "dimensions"):
            assert_true(item[key] == accepted[key], f"map/acceptance {key} mismatch: {item['original']}")
        assert_true(item["actual_timestamp"] == accepted["actual_capture_timestamp"], f"capture mismatch: {item['original']}")
        assert_true(item["cdx_digest"] == accepted["cdx_digest"], f"digest mismatch: {item['original']}")
        local_path = ROOT / item["local_path"]
        assert_true(local_path.is_file(), f"missing copied asset: {item['local_path']}")
        checked = image_check(local_path, item["dimensions"])
        assert_true(checked["sha256"] == item["sha256"], f"asset SHA mismatch: {item['local_path']}")
        assert_true(checked["length"] == item["length"], f"asset length mismatch: {item['local_path']}")
        local_asset_checks.append(
            {
                "original": item["original"],
                "local_path": item["local_path"],
                "sha256": checked["sha256"],
                "length": checked["length"],
                "dimensions": checked["dimensions"],
                "decoded_frames": checked["decoded_frames"],
            }
        )
    assert_true(sum(row["length"] for row in local_asset_checks) == 209170, "new asset byte total is not 209170")

    # Overlay provenance and bytes are checked independently of the worker's
    # counters.  The provenance JSON itself is the one extra output file.
    overlay_entries = [row for row in provenance["files"] if row.get("kind") == "image_overlay"]
    v19_overlay_entries = [row for row in v19_provenance["files"] if row.get("kind") == "image_overlay"]
    assert_true(len(overlay_entries) == 103, "v20 provenance overlay count is not 103")
    assert_true(len(v19_overlay_entries) == 79, "v19 provenance overlay count is not 79")
    overlay_by_route = {row["route"]: row for row in overlay_entries}
    v19_overlay_by_route = {row["route"]: row for row in v19_overlay_entries}
    assert_true(len(overlay_by_route) == 103, "duplicate v20 overlay routes")
    assert_true(set(v19_overlay_by_route).issubset(overlay_by_route), "v19 overlay routes not retained")

    output_overlay_checks = []
    for route, entry in overlay_by_route.items():
        output_file = OUT / entry["output_path"]
        assert_true(output_file.is_file(), f"missing output overlay: {route}")
        raw = file_bytes(output_file)
        actual_sha = sha_from_bytes(raw)
        assert_true(actual_sha == entry["derived_sha256"], f"output overlay SHA mismatch: {route}")
        assert_true(len(raw) == entry["derived_length"], f"output overlay length mismatch: {route}")
        output_overlay_checks.append(route)

    old_overlay_byte_equal = True
    for route, old_entry in v19_overlay_by_route.items():
        new_entry = overlay_by_route[route]
        old_file = ROOT / ".scratch/pages-resources-20261016-v19" / old_entry["output_path"]
        new_file = OUT / new_entry["output_path"]
        assert_true(old_file.is_file() and new_file.is_file(), f"old/new overlay file missing: {route}")
        equal = file_bytes(old_file) == file_bytes(new_file)
        old_overlay_byte_equal = old_overlay_byte_equal and equal
        assert_true(equal, f"retained v19 overlay bytes changed: {route}")

    new_routes = {urlparse(item["original"]).path for item in new_items}
    assert_true(new_routes == set(overlay_by_route) - set(v19_overlay_by_route), "v20 route delta is not exactly 24 new routes")
    new_overlay_bytes = sum(overlay_by_route[route]["derived_length"] for route in new_routes)

    # Actual tree and provenance counts.
    actual_output_files = sum(1 for path in OUT.rglob("*") if path.is_file())
    declared_output_files = provenance["stats"]["output_files"]
    assert_true(len(provenance["files"]) == declared_output_files, "provenance file list/count mismatch")
    assert_true(actual_output_files == declared_output_files + 1, "actual output count does not include only provenance JSON extra")
    assert_true(provenance["stats"]["source_records"] == 8357, "source record count changed")

    # The six guide sections and all 22 preview routes are checked from the
    # rendered files and provenance, including the newly accepted City group.
    guide = provenance["guide_previews"]
    assert_true(guide["group_count"] == 6, "guide group count is not six")
    assert_true(sum(group["preview_count"] for group in guide["groups"]) == 22, "guide preview count is not 22")
    guide_checks = {}
    old_gallery_bytes_equal = {}
    for group in guide["groups"]:
        group_id = group["group_id"]
        html_path = OUT / group["gallery_route"].lstrip("/")
        assert_true(html_path.is_file(), f"missing guide gallery: {group_id}")
        html = html_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{group_id}"
        assert_true(html.count(f'id="{section_id}"') == 1, f"guide section not unique: {group_id}")
        assert_true(html.count("Preserved guide previews") == 1, f"guide title not unique: {group_id}")
        assert_true(html.count("These previews survive in the original guide pages. Full-size gallery images are still incomplete.") == 1, f"guide notice mismatch: {group_id}")
        cards = html.count('class="offline-guide-preview-card"')
        routes = re.findall(r'data-guide-preview-route="([^"]+)"', html)
        assert_true(cards == group["preview_count"], f"guide card count mismatch: {group_id}")
        assert_true(len(routes) == group["preview_count"], f"guide route marker count mismatch: {group_id}")
        for preview in group["previews"]:
            route = preview["route"]
            assert_true(routes.count(route) == 1, f"guide route not unique: {group_id} {route}")
            image_path = OUT / route.lstrip("/")
            assert_true(image_path.is_file(), f"guide preview bytes missing: {route}")
            raw = file_bytes(image_path)
            assert_true(sha_from_bytes(raw) == preview["source_sha256"], f"guide preview SHA mismatch: {route}")
            assert_true(len(raw) == preview["source_length"], f"guide preview length mismatch: {route}")
        if group_id == "city-attacks":
            # City previews remain thumb routes with no dynamic ssN/full alias.
            section = html[html.find(f'id="{section_id}"'): html.find("</section>", html.find(f'id="{section_id}"'))]
            assert_true(all("/thumbs/" in route for route in routes), "City preview route left thumbs namespace")
            assert_true("data-gallery-full" not in section and "dynamic_full" not in section, "City section contains a dynamic full alias")
        guide_checks[group_id] = {
            "gallery_route": group["gallery_route"],
            "guide_route": group["guide_route"],
            "preview_count": group["preview_count"],
            "section_id_count": html.count(f'id="{section_id}"'),
            "card_count": cards,
            "route_marker_count": len(routes),
            "city_no_dynamic_full_alias": group_id != "city-attacks" or True,
        }
        if group_id != "city-attacks":
            old_path = ROOT / ".scratch/pages-resources-20261016-v19" / group["gallery_route"].lstrip("/")
            old_gallery_bytes_equal[group_id] = old_path.is_file() and old_path.read_bytes() == html_path.read_bytes()
            assert_true(old_gallery_bytes_equal[group_id], f"retained gallery bytes changed: {group_id}")

    # Browser receipt is read-only evidence from the one bounded local run.
    assert_true(browser["accepted"] is True, "local browser receipt not accepted")
    aug_page = next(page for page in browser["pages"] if page["label"] == "august-news-24")
    assert_true(aug_page["status"] == 200, "August page did not return 200")
    assert_true(len(aug_page["expected"]) == 24, "browser August expected count is not 24")
    assert_true(all(row["count"] == 1 and all(row["complete"]) and all(width > 0 and height > 0 for width, height in row["natural"]) for row in aug_page["expected"]), "browser August image load check failed")
    assert_true(len(aug_page["direct"]) == 24, "browser direct image count is not 24")
    assert_true(all(row["status"] == 200 and row["bytes"] == row["local_bytes"] and row["local_sha256"] for row in aug_page["direct"]), "browser direct byte check failed")
    assert_true(all(anchor["status"] == 200 for row in aug_page["direct"] for anchor in row["anchor_checks"]), "browser parent-anchor check failed")
    assert_true(browser["external_requests_blocked"] == 0, "browser made external requests")

    worker_before = worker["input_hashes_before"]
    worker_after = worker["input_hashes_after"]
    assert_true(worker_before == worker_after, "locked inputs changed during export")
    assert_true(worker["production_sha256_before"] == worker["production_sha256_after"], "production tools changed during export")
    assert_true(worker["disk_free_after_bytes"] >= worker["disk_free_floor_bytes"], "disk floor was violated")

    # Keep the post-check receipt compact while retaining exact hash bindings.
    tracked = {
        path: digest(path)
        for path in [
            worker_path,
            browser_path,
            prep_path,
            map_path,
            v19_map_path,
            v19_prov_path,
            prov_path,
            *acceptance_paths,
            ".scratch/offline-navigation-20261015-v15/build-manifest.json",
            "offline/build-manifest.json",
        ]
    }
    tracked.update({
        "build_pages_v20.py": digest(BUILD / "build_pages_v20.py"),
        "production/tools/guide_previews.py": worker["production_sha256_after"]["tools/guide_previews.py"],
        "production/tools/export_github_pages.py": worker["production_sha256_after"]["tools/export_github_pages.py"],
    })

    result = {
        "schema": "wow-recovery.integration.v20.post_export_reconciliation.v1",
        "accepted": True,
        "reconciled_export_valid": True,
        "executed_by": "/root/local_recovery_20261016",
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "meaning": "Independent post-export checks passed after the single v20 exporter invocation; this receipt does not rerun export or imply publication.",
        "export_invocations_after_worker_success": 0,
        "worker": {
            "path": worker_path,
            "sha256": digest(worker_path),
            "command": worker["command"],
            "checked_utc_start": worker["checked_utc_start"],
            "checked_utc_end": worker["checked_utc_end"],
            "export_started": worker["export_started"],
            "export_completed": worker["export_completed"],
            "network_requests_by_builder": worker["network_requests_by_builder"],
            "published": worker["published"],
        },
        "inputs": {
            "source15_manifest": {"path": ".scratch/offline-navigation-20261015-v15/build-manifest.json", "sha256": tracked[".scratch/offline-navigation-20261015-v15/build-manifest.json"]},
            "offline_manifest": {"path": "offline/build-manifest.json", "sha256": tracked["offline/build-manifest.json"]},
            "v19_map": {"path": v19_map_path, "sha256": tracked[v19_map_path], "items": len(v19_items)},
            "v20_map": {"path": map_path, "sha256": tracked[map_path], "items": len(v20_items), "new_items": len(new_items), "new_bytes": sum(row["length"] for row in local_asset_checks)},
            "v20_preparation": {"path": prep_path, "sha256": tracked[prep_path], "asset_count": prep["asset_count"], "asset_bytes": prep["asset_bytes"]},
            "root_acceptances": acceptance_summary,
            "source15_unchanged": worker_before == worker_after,
            "production_unchanged": worker["production_sha256_before"] == worker["production_sha256_after"],
        },
        "output": {
            "path": ".scratch/pages-resources-20261016-v20",
            "provenance_path": prov_path,
            "provenance_sha256": tracked[prov_path],
            "declared_files": declared_output_files,
            "actual_files_including_provenance": actual_output_files,
            "source_records": provenance["stats"]["source_records"],
            "overlay_records": {"total": len(overlay_entries), "primary": 82, "supplement": 21, "new_primary": len(new_routes), "new_primary_bytes": new_overlay_bytes},
            "retained_v19_overlay_routes": len(v19_overlay_by_route),
            "retained_v19_overlay_bytes_equal": old_overlay_byte_equal,
            "guide_previews": {"groups": guide["group_count"], "cards": sum(group["preview_count"] for group in guide["groups"]), "sections": guide_checks, "old_gallery_bytes_equal": old_gallery_bytes_equal},
            "disk_free_before_bytes": worker["disk_free_before_bytes"],
            "disk_free_after_bytes": worker["disk_free_after_bytes"],
            "disk_free_floor_bytes": worker["disk_free_floor_bytes"],
        },
        "local_browser": {
            "path": browser_path,
            "sha256": tracked[browser_path],
            "accepted": browser["accepted"],
            "pages": len(browser["pages"]),
            "checks": len(browser["checks"]),
            "requests_total": browser["requests_total"],
            "external_requests_blocked": browser["external_requests_blocked"],
            "august_images": 24,
            "august_direct_byte_checks": 24,
            "august_parent_anchor_200": True,
        },
        "verification": {
            "root_accepted_images": 24,
            "local_asset_sha_length_pillow_checks": 24,
            "map_items_preserved_plus_new": True,
            "overlay_routes_and_output_bytes_checked": len(output_overlay_checks),
            "guide_sections_and_preview_bytes_checked": 6,
            "input_hashes_before_after_equal": worker_before == worker_after,
            "network_requests": 0,
            "published": False,
        },
        "tracked_sha256": tracked,
        "deviations": [
            "The worker receipt retains a copied helper label existing_v18_gallery_bytes_equal; this independent receipt uses the accurate v19 retained-gallery check.",
            "The v20 map's inherited source_relationship prose still says v19 primary image overlay preparation for the 24 accepted additions; source bytes, source maps, acceptance hashes, timestamps, and overlay routing were independently checked and are unchanged.",
        ],
        "uncovered": [
            "No online Pages commit, deployment, or remote browser check was performed.",
            "No later unknown August-news assets were included.",
        ],
    }
    RECEIPT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "accepted": result["accepted"],
        "reconciled_export_valid": result["reconciled_export_valid"],
        "receipt": rel(RECEIPT_PATH),
        "receipt_sha256": digest(RECEIPT_PATH),
        "provenance_sha256": tracked[prov_path],
        "actual_files": actual_output_files,
        "declared_files": declared_output_files,
        "overlays": len(overlay_entries),
        "guide_previews": 22,
        "browser_checks": len(browser["checks"]),
        "network_requests": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
