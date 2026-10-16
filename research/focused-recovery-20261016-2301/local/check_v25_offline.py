#!/usr/bin/env python3
"""Bounded offline checker for a future v25 output.

The checker is intentionally parameterized because the nine neighbor retry
receipts and final v25 map names are not accepted yet.  It never exports,
starts a browser, performs network I/O, extracts an archive, or modifies a
site.  If executed, its only write is the worker-named receipt in this local
directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
LOCAL = Path(__file__).resolve().parent
DEFAULT_SITE = ROOT / ".scratch/pages-resources-20261016-v25"
DEFAULT_PRIOR_SITE = ROOT / ".scratch/pages-resources-20261016-v24"
DEFAULT_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
EXPECTED_PRIOR_PROVENANCE_SHA = "0d1a392e5be8f5eae71b8ca6bf73f5473331357c6f99f9ac60e79b6d07dec3d0"
EXPECTED_MANIFEST_SHA = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
MIN_FREE_BYTES = 11_005_853_696
PRIOR_DECLARED = 8637
PRIOR_ACTUAL = 8638
PRIOR_OVERLAYS = 179
PRIOR_PRIMARY = 117
PRIOR_SUPPLEMENT = 62


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def add_error(errors: list[dict], reason: str, **detail: object) -> None:
    entry = {"reason": reason}
    entry.update(detail)
    errors.append(entry)


def norm_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def original_of(item: dict) -> str:
    return str(item.get("original") or item.get("logical_url") or item.get("original_url") or "")


def timestamp_of(item: dict) -> str:
    return str(item.get("actual_capture_timestamp") or item.get("actual_timestamp") or item.get("capture_timestamp") or "")


def route_of(original: str, item: dict | None = None) -> str:
    if item and item.get("route"):
        return str(item["route"])
    return urlsplit(original).path


def map_items(path: Path) -> list[dict]:
    payload = read_json(path, f"map {path}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"map has no items list: {path}")
    return [item for item in items if isinstance(item, dict)]


def provenance_files(provenance: dict) -> dict[str, dict]:
    return {str(item.get("output_path")): item for item in provenance.get("files", []) if item.get("output_path")}


def scan_tree(site: Path, prior_site: Path, provenance: dict, prior: dict, allowed_changed: set[str], errors: list[dict]) -> dict:
    expected = provenance_files(provenance)
    previous = provenance_files(prior)
    actual: set[str] = set()
    changed: list[str] = []
    reused: list[str] = []
    total_bytes = 0
    for path in site.rglob("*"):
        if path.is_symlink():
            add_error(errors, "symlink", path=rel(path))
        if not path.is_file():
            continue
        relative = path.relative_to(site).as_posix()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        actual.add(relative)
        total_bytes += len(data)
        record = expected.get(relative)
        if record is None and relative != "export-provenance.json":
            add_error(errors, "undeclared_object", path=relative)
        elif record is not None:
            if digest != record.get("derived_sha256") or len(data) != int(record.get("derived_length", -1)):
                add_error(errors, "provenance_bytes", path=relative)
        old = previous.get(relative)
        if old is not None:
            old_path = prior_site / relative
            old_bytes = old_path.read_bytes() if old_path.is_file() else None
            if old_bytes == data:
                reused.append(relative)
            else:
                changed.append(relative)
                if relative not in allowed_changed:
                    add_error(errors, "unexpected_prior_byte_change", path=relative)
        else:
            changed.append(relative)
    expected_actual = len(expected) + 1
    if actual != set(expected) | {"export-provenance.json"}:
        add_error(errors, "member_set", declared=len(expected), actual=len(actual), expected_actual=expected_actual)
    if len(expected) != PRIOR_DECLARED:
        # v25 adds N records. The caller checks the exact dynamic count below.
        pass
    return {"declared_files": len(expected), "actual_files": len(actual), "tree_bytes": total_bytes, "reused_prior_paths": len(reused), "changed_paths": sorted(changed)}


def check_prior_overlays(current: dict, prior: dict, errors: list[dict]) -> dict:
    old = {str(item.get("route")): item for item in prior.get("files", []) if item.get("role") == "image_overlay"}
    now = {str(item.get("route")): item for item in current.get("files", []) if item.get("role") == "image_overlay"}
    fields = [
        "route", "output_path", "source_sha256", "source_length", "derived_sha256", "derived_length",
        "mime", "source_map", "source_map_sha256", "source_path", "origin_namespace", "temporal_class",
        "original_url", "actual_capture_timestamp", "indexed_capture_timestamp", "cdx_digest",
        "supplement_strategy",
    ]
    mismatches: list[dict] = []
    for route, old_item in old.items():
        item = now.get(route)
        if item is None:
            mismatches.append({"route": route, "reason": "missing"})
            continue
        for field in fields:
            if item.get(field) != old_item.get(field):
                mismatches.append({"route": route, "field": field, "prior": old_item.get(field), "current": item.get(field)})
    if len(old) != PRIOR_OVERLAYS:
        add_error(errors, "prior_overlay_count", count=len(old), expected=PRIOR_OVERLAYS)
    if mismatches:
        add_error(errors, "prior_overlay_metadata", count=len(mismatches), sample=mismatches[:5])
    return {"prior_overlay_count": len(old), "current_overlay_count": len(now), "mismatch_count": len(mismatches), "mismatch_sample": mismatches[:5]}


def root_binding_index(root_acceptance: dict) -> dict[str, str]:
    bindings = root_acceptance.get("bindings") or []
    result: dict[str, str] = {}
    for binding in bindings:
        if isinstance(binding, dict) and binding.get("path") and binding.get("sha256"):
            result[norm_path(str(binding["path"]))] = str(binding["sha256"]).casefold()
    return result


def check_new_sources(
    site: Path,
    current: dict,
    prior: dict,
    root_acceptance: dict,
    receipt_paths: list[Path],
    map_paths: list[Path],
    expected_primary_added: int,
    expected_supplement_added: int,
    errors: list[dict],
) -> dict:
    bindings = root_binding_index(root_acceptance)
    accepted: dict[str, dict] = {}
    receipt_details: list[dict] = []
    for path in receipt_paths:
        key = norm_path(rel(path))
        if bindings and bindings.get(key) != sha256_file(path):
            add_error(errors, "root_receipt_binding", path=key)
        receipt = read_json(path, f"source receipt {path}")
        if receipt.get("accepted") is not True:
            add_error(errors, "source_receipt_not_accepted", path=key)
        items = receipt.get("accepted_images") or receipt.get("images") or []
        if not isinstance(items, list):
            add_error(errors, "source_receipt_items", path=key)
            items = []
        receipt_details.append({"path": key, "sha256": sha256_file(path), "count": len(items), "bytes": receipt.get("image_bytes")})
        for image in items:
            original = original_of(image)
            if not original or original in accepted:
                add_error(errors, "duplicate_new_original", original=original)
            accepted[original] = image
    map_by_original: dict[str, tuple[Path, dict]] = {}
    for path in map_paths:
        key = norm_path(rel(path))
        if bindings and bindings.get(key) != sha256_file(path):
            add_error(errors, "root_map_binding", path=key)
        for item in map_items(path):
            original = original_of(item)
            if not original or original in map_by_original:
                add_error(errors, "duplicate_new_map_original", original=original)
            map_by_original[original] = (path, item)
    old_routes = {str(item.get("route")) for item in prior.get("files", []) if item.get("role") == "image_overlay"}
    current_routes = {str(item.get("route")): item for item in current.get("files", []) if item.get("role") == "image_overlay"}
    checked: list[dict] = []
    accepted_bytes = 0
    primary_count = supplement_count = 0
    for original, image in accepted.items():
        pair = map_by_original.get(original)
        if pair is None:
            add_error(errors, "accepted_image_missing_from_new_map", original=original)
            continue
        map_path, map_item = pair
        expected_sha = str(image.get("sha256") or "").casefold()
        expected_length = int(image.get("length", -1))
        expected_time = timestamp_of(image)
        if str(map_item.get("sha256") or "").casefold() != expected_sha or int(map_item.get("length", -1)) != expected_length or timestamp_of(map_item) != expected_time:
            add_error(errors, "map_receipt_byte_binding", original=original, map=rel(map_path))
        route = route_of(original, map_item)
        if route in old_routes:
            add_error(errors, "new_route_overlaps_prior_overlay", route=route)
        record = current_routes.get(route)
        if record is None:
            add_error(errors, "new_overlay_missing", route=route)
        else:
            output = site / str(record.get("output_path") or "")
            if not output.is_file() or sha256_file(output) != expected_sha or output.stat().st_size != expected_length:
                add_error(errors, "new_overlay_bytes", route=route)
            if str(record.get("source_sha256") or "").casefold() != expected_sha or int(record.get("source_length", -1)) != expected_length or str(record.get("original_url") or "") != original:
                add_error(errors, "new_overlay_provenance", route=route)
            if timestamp_of(record) != expected_time:
                add_error(errors, "new_overlay_timestamp", route=route)
            if str(record.get("source_map") or "") != rel(map_path) or str(record.get("source_map_sha256") or "").casefold() != sha256_file(map_path):
                add_error(errors, "new_overlay_map_identity", route=route)
            role_class = str(record.get("supplement_strategy") or record.get("temporal_class") or "")
            if "supplement" in role_class or str(record.get("role")) == "supplement_image_overlay":
                supplement_count += 1
            else:
                primary_count += 1
        accepted_bytes += max(expected_length, 0)
        checked.append({"original": original, "route": route, "sha256": expected_sha, "length": expected_length, "map": rel(map_path)})
    if set(map_by_original) != set(accepted):
        add_error(errors, "new_map_receipt_set", map_count=len(map_by_original), receipt_count=len(accepted))
    if primary_count != expected_primary_added or supplement_count != expected_supplement_added:
        add_error(errors, "new_overlay_class_counts", primary=primary_count, supplement=supplement_count, expected_primary=expected_primary_added, expected_supplement=expected_supplement_added)
    return {"receipts": receipt_details, "accepted_count": len(accepted), "accepted_bytes": accepted_bytes, "primary_added": primary_count, "supplement_added": supplement_count, "checked": checked}


def check_collections(site: Path, current: dict, prior: dict, expected_images: int, errors: list[dict]) -> dict:
    old = prior.get("guide_image_collections") or {}
    now = current.get("guide_image_collections") or {}
    if now.get("group_count") != 3 or now.get("image_count") != expected_images:
        add_error(errors, "collection_counts", groups=now.get("group_count"), images=now.get("image_count"), expected=expected_images)
    old_groups = {str(group.get("group_id")): group for group in old.get("groups", [])}
    new_groups = {str(group.get("group_id")): group for group in now.get("groups", [])}
    if set(old_groups) != set(new_groups):
        add_error(errors, "collection_group_identity", old=sorted(old_groups), new=sorted(new_groups))
    old_images = 0
    for group_id, old_group in old_groups.items():
        new_group = new_groups.get(group_id)
        if new_group is None:
            continue
        if old_group.get("guide_route") != new_group.get("guide_route") or old_group.get("gallery_route") != new_group.get("gallery_route"):
            add_error(errors, "collection_page_identity", group=group_id)
        new_by_route = {str(item.get("route")): item for item in new_group.get("images", [])}
        for old_item in old_group.get("images", []):
            old_images += 1
            current_item = new_by_route.get(str(old_item.get("route")))
            if current_item is None or current_item != old_item:
                add_error(errors, "collection_prior_image_changed", group=group_id, route=old_item.get("route"))
    stats = current.get("stats") or {}
    if stats.get("guide_image_collection_pages") != 6 or stats.get("guide_image_collection_images") != expected_images:
        add_error(errors, "collection_stats", pages=stats.get("guide_image_collection_pages"), images=stats.get("guide_image_collection_images"))
    pages: list[dict] = []
    for group in now.get("groups", []):
        count = int(group.get("image_count", -1))
        for page_role, route in (("guide", group.get("guide_route")), ("gallery", group.get("gallery_route"))):
            record = next((item for item in current.get("files", []) if item.get("route") == route), None)
            if record is None:
                add_error(errors, "collection_page_missing", route=route)
                continue
            text = (site / str(record.get("output_path") or "")).read_text(encoding="utf-8")
            slug = re.sub(r"[^a-z0-9]+", "-", str(group.get("group_id")).casefold()).strip("-")
            section_id = f"offline-guide-images-{slug}-{page_role}"
            sections = text.count(f'id="{section_id}"')
            cards = text.count('data-guide-image-route="')
            lazy = text.count('loading="lazy"')
            anchors = text.count('class="offline-guide-image-guide"')
            if sections != 1 or cards != count or lazy < count or anchors != 1:
                add_error(errors, "collection_section", route=route, sections=sections, cards=cards, lazy=lazy, anchors=anchors, expected=count)
            pages.append({"group_id": group.get("group_id"), "page_role": page_role, "route": route, "cards": cards, "expected": count})
    previews = current.get("guide_previews") or {}
    old_previews = prior.get("guide_previews") or {}
    if previews != old_previews:
        add_error(errors, "preview_provenance_changed")
    if stats.get("guide_preview_gallery_pages") != 6 or stats.get("guide_preview_count") != 22:
        add_error(errors, "preview_counts", pages=stats.get("guide_preview_gallery_pages"), images=stats.get("guide_preview_count"))
    return {"prior_images": old_images, "current_images": now.get("image_count"), "groups": now.get("group_count"), "pages": pages, "previews_unchanged": previews == old_previews}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    parser.add_argument("--prior-site", type=Path, default=DEFAULT_PRIOR_SITE)
    parser.add_argument("--root-acceptance", type=Path, required=True)
    parser.add_argument("--worker-receipt", type=Path, required=True)
    parser.add_argument("--new-source-receipt", type=Path, action="append", default=[])
    parser.add_argument("--new-map", type=Path, action="append", default=[])
    parser.add_argument("--collection-map", type=Path, required=True)
    parser.add_argument("--expected-primary-added", type=int, required=True)
    parser.add_argument("--expected-supplement-added", type=int, required=True)
    parser.add_argument("--expected-collection-images", type=int, required=True)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--receipt", type=Path, default=LOCAL / "worker-v25-offline-check.json")
    args = parser.parse_args(argv)
    errors: list[dict] = []
    result: dict = {"schema": "wow-recovery.focused-recovery-20261016-2301.v25-offline-check.v1", "export_executed": False, "browser_executed": False, "network_requests": 0, "errors": errors}
    try:
        site = args.site.resolve()
        prior_site = args.prior_site.resolve()
        prior_prov_path = prior_site / "export-provenance.json"
        current_prov_path = site / "export-provenance.json"
        if not site.is_dir() or site.with_name(site.name + ".partial").exists():
            raise RuntimeError("v25 site is missing or partial")
        if not prior_site.is_dir() or sha256_file(prior_prov_path) != EXPECTED_PRIOR_PROVENANCE_SHA:
            raise RuntimeError("frozen v24 prior site/provenance SHA mismatch")
        root_acceptance = read_json(args.root_acceptance, "root v25 acceptance")
        if root_acceptance.get("accepted") is not True:
            add_error(errors, "root_acceptance_not_accepted")
        worker = read_json(args.worker_receipt, "v25 worker receipt")
        if worker.get("export_completed") is not True or worker.get("published") is True:
            add_error(errors, "worker_gate", export_completed=worker.get("export_completed"), published=worker.get("published"))
        current = read_json(current_prov_path, "v25 provenance")
        prior = read_json(prior_prov_path, "v24 provenance")
        stats = current.get("stats") or {}
        new_count = args.expected_primary_added + args.expected_supplement_added
        expected_declared = PRIOR_DECLARED + new_count
        expected_actual = PRIOR_ACTUAL + new_count
        if current.get("source_manifest_sha256") != EXPECTED_MANIFEST_SHA:
            add_error(errors, "source_manifest_sha", actual=current.get("source_manifest_sha256"))
        for key, expected in {
            "source_records": 8357,
            "image_overlay_records": PRIOR_OVERLAYS + new_count,
            "primary_image_overlay_records": PRIOR_PRIMARY + args.expected_primary_added,
            "supplement_image_overlay_records": PRIOR_SUPPLEMENT + args.expected_supplement_added,
            "output_files": expected_declared,
        }.items():
            if stats.get(key) != expected:
                add_error(errors, "provenance_count", key=key, actual=stats.get(key), expected=expected)
        allowed = {norm_path(p) for p in args.changed_path}
        allowed.update({"export-provenance.json", "__offline/route-map.json", "__offline/pages_runtime.js", "__offline/related-images/index.html"})
        tree = scan_tree(site, prior_site, current, prior, allowed, errors)
        if tree["actual_files"] != expected_actual or tree["declared_files"] != expected_declared:
            add_error(errors, "output_counts", actual=tree["actual_files"], declared=tree["declared_files"], expected_actual=expected_actual, expected_declared=expected_declared)
        overlays = check_prior_overlays(current, prior, errors)
        sources = check_new_sources(site, current, prior, root_acceptance, [p.resolve() for p in args.new_source_receipt], [p.resolve() for p in args.new_map], args.expected_primary_added, args.expected_supplement_added, errors)
        collection = check_collections(site, current, prior, args.expected_collection_images, errors)
        if sha256_file(args.collection_map.resolve()) != root_binding_index(root_acceptance).get(norm_path(rel(args.collection_map.resolve())), sha256_file(args.collection_map.resolve())):
            add_error(errors, "collection_map_root_binding")
        result.update({"prior_provenance_sha256": sha256_file(prior_prov_path), "v25_provenance_sha256": sha256_file(current_prov_path), "tree": tree, "prior_overlays": overlays, "new_sources": sources, "collections": collection, "disk_free_bytes": shutil.disk_usage(ROOT).free, "expected_counts": {"declared": expected_declared, "actual": expected_actual, "overlays": PRIOR_OVERLAYS + new_count}})
        if result["disk_free_bytes"] < MIN_FREE_BYTES:
            add_error(errors, "disk_floor", free=result["disk_free_bytes"], floor=MIN_FREE_BYTES)
        result["offline_check_passed"] = not errors
    except Exception as exc:
        add_error(errors, "checker_exception", type=type(exc).__name__, detail=str(exc))
        result["offline_check_passed"] = False
    result["checked_utc"] = datetime.now(timezone.utc).isoformat()
    args.receipt.resolve().write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"offline_check_passed": result["offline_check_passed"], "errors": errors[:8], "v25_provenance_sha256": result.get("v25_provenance_sha256")}, ensure_ascii=False))
    return 0 if result["offline_check_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
