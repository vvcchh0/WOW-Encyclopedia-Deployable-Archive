#!/usr/bin/env python3
"""Independent offline checks for the frozen v23 final40 tree.

This writes a worker-named check receipt in this new QA directory.  It does
not create or modify a root acceptance receipt, start a browser, publish, or
run the exporter.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-resources-20261016-v23"
PRIOR = ROOT / ".scratch/pages-resources-20261016-v22"
RUN = ROOT / "research/continuous-recovery-20261016"
WORKER = RUN / "integration/v23-build/worker-build-v23-final40.json"
ROOT_INPUT = RUN / "publication/root-v23-final40-input-acceptance.json"
V22_PROVENANCE = PRIOR / "export-provenance.json"
V23_PROVENANCE = SITE / "export-provenance.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
RECEIPT = OUT / "worker-v23-offline-check.json"
ANCHOR = "20080512210044"

EXPECTED_WORKER_SHA = "1d9563282178d596d06a9886bfc8486b3cb6da495927757cf0bbb9950cd0919e"
EXPECTED_ROOT_INPUT_SHA = "aebe7758231fc91b62d477598177115725f2155cdb5a78971290918c0cb6b96e"
EXPECTED_V22_PROVENANCE_SHA = "b2c111baac62b28490a81f5ea25e978ebdc29de8af2072d85f8bb34c8d25131f"
EXPECTED_MANIFEST_SHA = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_FINAL_MAPS = {
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
    "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json": "de179aa26f0453cd29b30b76600bf22dd9e0a3b443e03300238c13c97bb624c6",
}
EXPECTED_RECEIPTS = {
    "root-gallery-neighbors01-source-acceptance.json": ("bf278a6a47b21f452ed3d41b44b219e67ade9292877501af0a0c4714a7a182a7", 12, 1884756),
    "root-gallery-neighbors02-source-acceptance.json": ("63d7b6e789b1e07c1851f74d5b6074cae12e28d41a8def5cc714186991b40e4f", 13, 2323105),
    "root-gallery-neighbors03-source-acceptance.json": ("e318aa471f8936cc34aaeaea6a6b4cf40aa66884357256972b56f0dc0970022e", 5, 981064),
    "root-gallery-neighbors-full15-source-acceptance.json": ("382c8a9548435e594605627a622a55a5b9101610f59798b40559ec3e49a3c358", 8, 1387616),
    "root-gallery-neighbors-other4-source-acceptance.json": ("a4ae0afdbb41a3881884289776b4943c482cd6b73762304e5d58c209c33d333c", 2, 325063),
}
RECEIPT_DIR = RUN / "publication"
FINAL_MAP_PATHS = [ROOT / relative for relative in EXPECTED_FINAL_MAPS]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def route_of(original: str) -> str:
    return urlsplit(original).path


def add_error(errors: list[dict], reason: str, **detail: object) -> None:
    item = {"reason": reason}
    item.update(detail)
    errors.append(item)


def load_hygiene_module():
    path = ROOT / "research/github-publication-20261012/full-tree-hygiene.py"
    spec = importlib.util.spec_from_file_location("wow_hygiene_v23", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load hygiene module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def scan_tree(provenance: dict, prior: dict, errors: list[dict], findings: list[dict]) -> dict:
    expected = {str(item["output_path"]): item for item in provenance.get("files", [])}
    previous = {str(item["output_path"]): item for item in prior.get("files", [])}
    actual: set[str] = set()
    reused: list[str] = []
    changed: list[str] = []
    scanned_bytes = 0
    total_bytes = 0
    hygiene = load_hygiene_module()
    for path in SITE.rglob("*"):
        if path.is_symlink():
            add_error(errors, "symlink", path=rel(path))
        if not path.is_file():
            continue
        relative = path.relative_to(SITE).as_posix()
        data = path.read_bytes()
        digest = sha(data)
        actual.add(relative)
        total_bytes += len(data)
        record = expected.get(relative)
        if record is None and relative != "export-provenance.json":
            add_error(errors, "undeclared_object", path=relative)
        elif record is not None:
            if record.get("derived_sha256") != digest or int(record.get("derived_length", -1)) != len(data):
                add_error(errors, "object_hash_or_length", path=relative)
        prior_record = previous.get(relative)
        if prior_record and digest == prior_record.get("derived_sha256") and len(data) == int(prior_record.get("derived_length", -1)):
            reused.append(relative)
            continue
        changed.append(relative)
        scanned_bytes += len(data)
        for pattern in hygiene.PATTERNS:
            if pattern.category in {"cookie_handling_field", "authorization_field_without_value"}:
                continue
            count = len(list(pattern.regex.finditer(data)))
            if count:
                findings.append({"path": relative, "category": pattern.category, "count": count})
        if re.search(rb"(?im)^(?:set-cookie|x-archive-orig-set-cookie|authorization|proxy-authorization):\s*\S+", data):
            add_error(errors, "raw_sensitive_http_header", path=relative)
    if actual != set(expected) | {"export-provenance.json"}:
        add_error(errors, "member_set", expected_count=len(expected) + 1, actual_count=len(actual))
    if len(expected) != 8620 or len(actual) != 8621:
        add_error(errors, "object_count", declared=len(expected), actual=len(actual))
    if provenance.get("source_manifest_sha256") != EXPECTED_MANIFEST_SHA:
        add_error(errors, "source_manifest", actual=provenance.get("source_manifest_sha256"))
    return {
        "declared_files": len(expected),
        "actual_files": len(actual),
        "tree_bytes": total_bytes,
        "hygiene_reused_identical_files": len(reused),
        "changed_scanned_files": len(changed),
        "changed_scanned_bytes": scanned_bytes,
        "changed_paths": sorted(changed),
    }


def check_prior_overlays(provenance: dict, prior: dict, errors: list[dict]) -> dict:
    old = {str(item["route"]): item for item in prior.get("files", []) if item.get("role") == "image_overlay"}
    current = {str(item["route"]): item for item in provenance.get("files", []) if item.get("role") == "image_overlay"}
    fields = [
        "route", "output_path", "source_sha256", "source_length", "derived_sha256", "derived_length",
        "mime", "source_map", "source_map_sha256", "source_path", "origin_namespace", "temporal_class",
        "original_url", "actual_capture_timestamp", "indexed_capture_timestamp", "cdx_digest",
        "supplement_strategy",
    ]
    mismatches: list[dict] = []
    for route, old_item in old.items():
        new_item = current.get(route)
        if new_item is None:
            mismatch = {"route": route, "reason": "missing"}
            mismatches.append(mismatch)
            add_error(errors, "prior_overlay_regression", **mismatch)
            continue
        for field in fields:
            if new_item.get(field) != old_item.get(field):
                mismatch = {"route": route, "field": field, "prior": old_item.get(field), "current": new_item.get(field)}
                mismatches.append(mismatch)
                add_error(errors, "prior_overlay_regression", **mismatch)
    if len(old) != 122:
        add_error(errors, "prior_overlay_count", count=len(old))
    return {"prior_overlay_count": len(old), "current_overlay_count": len(current), "mismatch_count": len(mismatches), "mismatch_sample": mismatches[:5]}


def check_routing(errors: list[dict]) -> dict:
    old_map = read_json(PRIOR / "__offline/route-map.json")
    new_map = read_json(SITE / "__offline/route-map.json")
    differences: dict[str, list[str]] = {}
    for name, values in old_map.items():
        if not isinstance(values, dict):
            if new_map.get(name) != values:
                add_error(errors, "prior_routing_changed", map=name)
            continue
        missing_or_changed = [key for key, value in values.items() if new_map.get(name, {}).get(key) != value]
        differences[name] = missing_or_changed
        if missing_or_changed:
            add_error(errors, "prior_routing_changed", map=name, keys=missing_or_changed[:10])
    return {"prior_map_keys": {key: len(value) if isinstance(value, dict) else 1 for key, value in old_map.items()}, "new_map_keys": {key: len(value) if isinstance(value, dict) else 1 for key, value in new_map.items()}, "changed_or_removed": differences}


def check_new_images(provenance: dict, errors: list[dict]) -> dict:
    current = {str(item["route"]): item for item in provenance.get("files", []) if item.get("role") == "image_overlay"}
    final_map_items: dict[str, tuple[Path, dict]] = {}
    for map_path in FINAL_MAP_PATHS:
        document = read_json(map_path)
        for item in document.get("items", []):
            route = route_of(str(item["original"]))
            if route in final_map_items:
                add_error(errors, "new_image_duplicate_route", route=route)
            final_map_items[route] = (map_path, item)
    routes: set[str] = set()
    accepted_bytes = 0
    receipt_details: list[dict] = []
    image_mismatches: list[dict] = []
    for name, (expected_sha, expected_count, expected_bytes) in EXPECTED_RECEIPTS.items():
        path = RECEIPT_DIR / name
        if file_sha(path) != expected_sha:
            add_error(errors, "source_receipt_sha", receipt=name, actual=file_sha(path))
        document = read_json(path)
        items = document.get("accepted_images") or []
        if document.get("accepted") is not True or len(items) != expected_count or int(document.get("image_bytes", -1)) != expected_bytes:
            add_error(errors, "source_receipt_gate", receipt=name, accepted=document.get("accepted"), count=len(items), bytes=document.get("image_bytes"))
        receipt_details.append({"path": rel(path), "sha256": file_sha(path), "count": len(items), "bytes": document.get("image_bytes")})
        for image in items:
            original = str(image.get("original"))
            route = route_of(original)
            if route in routes:
                add_error(errors, "source_image_duplicate", route=route)
            routes.add(route)
            accepted_bytes += int(image.get("length", 0))
            current_item = current.get(route)
            map_pair = final_map_items.get(route)
            diffs = []
            if current_item is None:
                diffs.append("missing_output_overlay")
            if map_pair is None:
                diffs.append("missing_final_map_item")
            if current_item is not None:
                for field, expected in {
                    "original_url": original,
                    "source_sha256": str(image.get("sha256")).casefold(),
                    "derived_sha256": str(image.get("sha256")).casefold(),
                    "source_length": int(image.get("length")),
                    "derived_length": int(image.get("length")),
                    "actual_capture_timestamp": str(image.get("actual_capture_timestamp")),
                }.items():
                    if current_item.get(field) != expected:
                        diffs.append(f"{field}:{current_item.get(field)!r}!={expected!r}")
                output = SITE / str(current_item.get("output_path") or "")
                if not output.is_file() or file_sha(output) != str(image.get("sha256")).casefold() or output.stat().st_size != int(image.get("length")):
                    diffs.append("output_bytes")
            if map_pair is not None:
                map_path, map_item = map_pair
                if str(current_item.get("source_map")) != rel(map_path) or str(current_item.get("source_map_sha256")) != file_sha(map_path):
                    diffs.append("source_map_identity")
                if map_item.get("sha256") != str(image.get("sha256")).casefold() or int(map_item.get("length")) != int(image.get("length")) or map_item.get("actual_timestamp") != image.get("actual_capture_timestamp"):
                    diffs.append("final_map_binding")
            if diffs:
                mismatch = {"route": route, "diffs": diffs}
                image_mismatches.append(mismatch)
                add_error(errors, "new_source_image_binding", **mismatch)
    if len(routes) != 40 or accepted_bytes != 6901604 or len(final_map_items) != 40:
        add_error(errors, "new_image_conservation", receipt_routes=len(routes), receipt_bytes=accepted_bytes, final_map_items=len(final_map_items))
    return {"receipt_details": receipt_details, "unique_routes": len(routes), "accepted_bytes": accepted_bytes, "final_map_items": len(final_map_items), "mismatch_count": len(image_mismatches), "mismatch_sample": image_mismatches[:5]}


def check_collections_and_previews(provenance: dict, errors: list[dict]) -> dict:
    stats = provenance.get("stats") or {}
    collection = provenance.get("guide_image_collections") or {}
    preview = provenance.get("guide_previews") or {}
    expected_groups = {
        "love-is-in-the-air": (10, "/info/events/loveisintheair/index.html", "/info/events/loveisintheair/gallery.html"),
        "lunar-festival": (10, "/info/events/lunarnewyears/index.html", "/info/events/lunarnewyears/gallery.html"),
        "world-pvp": (12, "/pvp/worldpvp/index.xml", "/pvp/worldpvp/worldpvp-gallery.html"),
    }
    if (collection.get("group_count"), collection.get("image_count")) != (3, 32):
        add_error(errors, "guide_collection_provenance", group_count=collection.get("group_count"), image_count=collection.get("image_count"))
    if (stats.get("guide_image_collection_pages"), stats.get("guide_image_collection_images")) != (6, 32):
        add_error(errors, "guide_collection_stats", pages=stats.get("guide_image_collection_pages"), images=stats.get("guide_image_collection_images"))
    group_counts = {str(group.get("group_id")): int(group.get("image_count", -1)) for group in collection.get("groups", [])}
    if group_counts != {key: value[0] for key, value in expected_groups.items()}:
        add_error(errors, "guide_collection_group_counts", actual=group_counts)
    collection_pages: list[dict] = []
    for group_id, (count, guide_route, gallery_route) in expected_groups.items():
        for page_role, route in (("guide", guide_route), ("gallery", gallery_route)):
            record = next((item for item in provenance.get("files", []) if item.get("route") == route), None)
            if record is None:
                add_error(errors, "guide_collection_page_missing", route=route)
                continue
            text = (SITE / str(record["output_path"])).read_text(encoding="utf-8")
            slug = re.sub(r"[^a-z0-9]+", "-", group_id.casefold()).strip("-")
            section_id = f"offline-guide-images-{slug}-{page_role}"
            section_count = text.count(f'id="{section_id}"')
            card_count = text.count('data-guide-image-route="')
            lazy_count = text.count('loading="lazy"')
            anchor_count = text.count('class="offline-guide-image-guide"')
            if section_count != 1 or card_count != count or lazy_count < count or anchor_count != 1:
                add_error(errors, "guide_collection_section", route=route, section_count=section_count, cards=card_count, lazy=lazy_count, guide_anchors=anchor_count, expected=count)
            collection_pages.append({"group_id": group_id, "page_role": page_role, "route": route, "section_count": section_count, "card_count": card_count, "lazy_count": lazy_count, "guide_anchor_count": anchor_count})
    if (preview.get("group_count"), preview.get("preview_count")) != (6, 22) or (stats.get("guide_preview_gallery_pages"), stats.get("guide_preview_count")) != (6, 22):
        add_error(errors, "guide_preview_counts", provenance=preview, stats={key: stats.get(key) for key in ("guide_preview_gallery_pages", "guide_preview_count")})
    preview_pages: list[dict] = []
    for group in preview.get("groups", []):
        route = str(group.get("gallery_route"))
        record = next((item for item in provenance.get("files", []) if item.get("route") == route), None)
        if record is None:
            add_error(errors, "guide_preview_page_missing", route=route)
            continue
        text = (SITE / str(record["output_path"])).read_text(encoding="utf-8")
        expected = int(group.get("preview_count", -1))
        section_count = text.count('class="offline-guide-preview-section"')
        card_count = text.count('alt="Preserved guide preview"')
        if section_count != 1 or card_count != expected:
            add_error(errors, "guide_preview_section", route=route, section_count=section_count, cards=card_count, expected=expected)
        preview_pages.append({"route": route, "section_count": section_count, "card_count": card_count, "expected": expected})
    return {"collection_group_counts": group_counts, "collection_pages": collection_pages, "preview_pages": preview_pages, "preview_groups": preview.get("group_count"), "preview_images": preview.get("preview_count")}


def main() -> int:
    errors: list[dict] = []
    findings: list[dict] = []
    result: dict = {
        "schema": "wow-recovery.publication.v23-offline-check.v1",
        "worker_named_receipt": True,
        "root_acceptance_called": False,
        "browser_executed": False,
        "export_executed": False,
        "network_requests": 0,
        "errors": errors,
        "publication_findings": findings,
    }
    try:
        if not SITE.is_dir() or SITE.with_name(SITE.name + ".partial").exists():
            raise RuntimeError("v23 output is not atomically complete")
        worker_sha = file_sha(WORKER)
        root_input_sha = file_sha(ROOT_INPUT)
        if worker_sha != EXPECTED_WORKER_SHA:
            add_error(errors, "worker_receipt_sha", actual=worker_sha)
        if root_input_sha != EXPECTED_ROOT_INPUT_SHA:
            add_error(errors, "root_input_acceptance_sha", actual=root_input_sha)
        worker = read_json(WORKER)
        root_input = read_json(ROOT_INPUT)
        if worker.get("export_completed") is not True or worker.get("published") is not False or worker.get("network_requests_by_builder") != 0:
            add_error(errors, "worker_gate", export_completed=worker.get("export_completed"), published=worker.get("published"), network_requests=worker.get("network_requests_by_builder"))
        if root_input.get("accepted") is not True or root_input.get("single_export_go") is not True or root_input.get("network_requests") != 0:
            add_error(errors, "root_input_gate", accepted=root_input.get("accepted"), single_export_go=root_input.get("single_export_go"), network_requests=root_input.get("network_requests"))
        for binding in root_input.get("bindings", []):
            path = ROOT / str(binding.get("path"))
            if not path.is_file() or file_sha(path) != binding.get("sha256"):
                add_error(errors, "root_input_binding", path=str(binding.get("path")))
        if worker.get("input_hashes_before") != worker.get("input_hashes_after"):
            add_error(errors, "worker_input_hash_drift")
        for path, expected in (worker.get("input_hashes_after") or {}).items():
            actual = file_sha(ROOT / path)
            if actual != expected:
                add_error(errors, "input_binding_changed_since_export", path=path, expected=expected, actual=actual)
        if file_sha(V22_PROVENANCE) != EXPECTED_V22_PROVENANCE_SHA:
            add_error(errors, "v22_provenance_sha", actual=file_sha(V22_PROVENANCE))
        if file_sha(SOURCE_MANIFEST) != EXPECTED_MANIFEST_SHA:
            add_error(errors, "source_manifest_sha", actual=file_sha(SOURCE_MANIFEST))
        for relative, expected in EXPECTED_FINAL_MAPS.items():
            actual = file_sha(ROOT / relative)
            if actual != expected:
                add_error(errors, "final_map_sha", path=relative, expected=expected, actual=actual)
        provenance = read_json(V23_PROVENANCE)
        prior = read_json(V22_PROVENANCE)
        result["worker_receipt_sha256"] = worker_sha
        result["root_input_acceptance_sha256"] = root_input_sha
        result["export_provenance_sha256"] = file_sha(V23_PROVENANCE)
        result["offline_tree"] = scan_tree(provenance, prior, errors, findings)
        result["prior_overlay_check"] = check_prior_overlays(provenance, prior, errors)
        result["routing_conservation"] = check_routing(errors)
        result["new_source_images"] = check_new_images(provenance, errors)
        result["guide_checks"] = check_collections_and_previews(provenance, errors)
        stats = provenance.get("stats") or {}
        if {key: stats.get(key) for key in ("source_records", "image_overlay_records", "primary_image_overlay_records", "supplement_image_overlay_records")} != {"source_records": 8357, "image_overlay_records": 162, "primary_image_overlay_records": 100, "supplement_image_overlay_records": 62}:
            add_error(errors, "provenance_counts", stats=stats)
        result["stats"] = stats
        result["disk_free_bytes"] = shutil.disk_usage(ROOT).free
        result["checked_utc"] = datetime.now(timezone.utc).isoformat()
        result["offline_check_passed"] = not errors and not findings
    except Exception as exc:
        add_error(errors, "checker_exception", type=type(exc).__name__, detail=str(exc))
        result["checked_utc"] = datetime.now(timezone.utc).isoformat()
        result["offline_check_passed"] = False
    RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result.get(key) for key in ("offline_check_passed", "export_provenance_sha256", "worker_receipt_sha256", "root_input_acceptance_sha256", "errors", "publication_findings")}, ensure_ascii=False))
    return 0 if result["offline_check_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
