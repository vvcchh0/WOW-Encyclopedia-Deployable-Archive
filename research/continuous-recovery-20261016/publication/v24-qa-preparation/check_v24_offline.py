#!/usr/bin/env python3
"""Independent offline checks for the future v24 export.

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
SITE = ROOT / ".scratch/pages-resources-20261016-v24"
PRIOR = ROOT / ".scratch/pages-resources-20261016-v23"
RUN = ROOT / "research/continuous-recovery-20261016"
WORKER = RUN / "integration/v24-build/worker-build-v24.json"
ROOT_INPUT_CANDIDATES = [
    RUN / "publication/root-v24-final-input-acceptance.json",
    RUN / "publication/root-v24-input-acceptance.json",
    RUN / "publication/root-v24-final40-input-acceptance.json",
]
PRIOR_PROVENANCE = PRIOR / "export-provenance.json"
V24_PROVENANCE = SITE / "export-provenance.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
RECEIPT = OUT / "worker-v24-offline-check.json"
ANCHOR = "20080512210044"

EXPECTED_PRIOR_V23_PROVENANCE_SHA = "4af91c0131e3b4760946b3b4db5e1e4a5ba0fc8be026226164c3f44aa56a743e"
EXPECTED_MANIFEST_SHA = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
FINAL_MAP = ROOT / "research/continuous-recovery-20261016/integration/v24-fresh-news-source-map-final.json"
FRESH_RECEIPTS = [
    RUN / "publication/root-news-content02-source-acceptance.json",
    RUN / "publication/root-news-content03-source-acceptance.json",
]
EXPECTED_INPUT_MAPS = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77",
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33",
    "research/continuous-recovery-20261016/integration/v22-primary-news-source-map.json": "672b2bf7330c9436ee1036ae1f80e8a8b83f14475bfc0f4d9480d6b8e4493ad9",
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json": "a21faaf398e4b605a441da7ca9f23d23e75e1e1bfb59a824d59e5aa7a981d772",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "research/continuous-recovery-20261016/integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581",
    "research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json": "de179aa26f0453cd29b30b76600bf22dd9e0a3b443e03300238c13c97bb624c6",
}
EXPECTED_PRODUCTION = {
    "tools/export_github_pages.py": "50bd3569f77d3d52c52ed7077726d7dc99fbee23a3a0ced076a6523198b9225d",
    "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
    "tools/guide_image_collections.py": "9d0f20679733e29c6eb789fd4a05883056e4994ccb173e1dc843d68e070dc057",
}


def root_input_path() -> Path:
    for path in ROOT_INPUT_CANDIDATES:
        if path.is_file():
            return path
    return ROOT_INPUT_CANDIDATES[0]


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
    stats = provenance.get("stats") or {}
    new_count = int(stats.get("primary_image_overlay_records", 0)) - 100
    expected_declared = 8620 + new_count
    expected_actual = expected_declared + 1
    if not 10 <= new_count <= 20:
        add_error(errors, "new_overlay_count_range", new_count=new_count)
    if len(expected) != expected_declared or len(actual) != expected_actual:
        add_error(errors, "object_count", declared=len(expected), actual=len(actual), expected_declared=expected_declared, expected_actual=expected_actual)
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
    if len(old) != 162:
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
    map_document = read_json(FINAL_MAP)
    if map_document.get("accepted") is not True or map_document.get("role") != "primary_image_overlay":
        add_error(errors, "final_map_gate", accepted=map_document.get("accepted"), role=map_document.get("role"))
    for item in map_document.get("items", []):
        route = route_of(str(item.get("original") or ""))
        if route in final_map_items:
            add_error(errors, "new_image_duplicate_route", route=route)
        final_map_items[route] = (FINAL_MAP, item)
    routes: set[str] = set()
    accepted_bytes = 0
    receipt_details: list[dict] = []
    image_mismatches: list[dict] = []
    accepted_items: list[dict] = []
    for path in FRESH_RECEIPTS:
        receipt_document = read_json(path)
        items = receipt_document.get("accepted_images") or []
        image_bytes = sum(int(image.get("length", 0)) for image in items)
        if receipt_document.get("accepted") is not True or not items or int(receipt_document.get("image_bytes", image_bytes)) != image_bytes:
            add_error(errors, "source_receipt_gate", receipt=rel(path), accepted=receipt_document.get("accepted"), count=len(items), bytes=receipt_document.get("image_bytes"), calculated_bytes=image_bytes)
        receipt_details.append({"path": rel(path), "sha256": file_sha(path), "count": len(items), "bytes": image_bytes})
        accepted_items.extend(items)
    if not 10 <= len(accepted_items) <= 20:
        add_error(errors, "new_image_count_range", count=len(accepted_items))
    map_sha = file_sha(FINAL_MAP)
    map_source_bindings = map_document.get("source_acceptances") or []
    expected_source_bindings = {rel(path): file_sha(path) for path in FRESH_RECEIPTS}
    actual_source_bindings = {str(item.get("path")): str(item.get("sha256")) for item in map_source_bindings}
    if actual_source_bindings != expected_source_bindings:
        add_error(errors, "final_map_source_acceptance_bindings", expected=expected_source_bindings, actual=actual_source_bindings)
    for image in accepted_items:
        original = str(image.get("original") or image.get("logical_url") or "")
        route = route_of(original)
        if route in routes:
            add_error(errors, "source_image_duplicate", route=route)
        routes.add(route)
        accepted_bytes += int(image.get("length", 0))
        current_item = current.get(route)
        map_pair = final_map_items.get(route)
        diffs: list[str] = []
        expected_sha = str(image.get("sha256") or "").casefold()
        expected_length = int(image.get("length", -1))
        expected_capture = str(image.get("actual_capture_timestamp") or image.get("actual_timestamp") or "")
        if current_item is None:
            diffs.append("missing_output_overlay")
        if map_pair is None:
            diffs.append("missing_final_map_item")
        raw_value = image.get("private_payload_path") or image.get("accepted_raw_body") or image.get("raw_body") or image.get("source_payload")
        raw_path = ROOT / str(raw_value) if raw_value and not Path(str(raw_value)).is_absolute() else Path(str(raw_value)) if raw_value else None
        if raw_path is None or not raw_path.is_file():
            diffs.append("missing_source_object")
        else:
            if file_sha(raw_path) != expected_sha or raw_path.stat().st_size != expected_length:
                diffs.append("source_object_bytes")
            try:
                from PIL import Image
                with Image.open(raw_path) as img:
                    frame_count = int(getattr(img, "n_frames", 1))
                    if frame_count != int(image.get("decoded_frames", frame_count)):
                        diffs.append("source_object_frames")
                    dimensions = image.get("dimensions")
                    if dimensions and tuple(dimensions) != tuple(img.size):
                        diffs.append("source_object_dimensions")
                    img.verify()
            except Exception as exc:
                diffs.append(f"source_object_decode:{type(exc).__name__}")
        if current_item is not None:
            for field, expected in {
                "original_url": original,
                "source_sha256": expected_sha,
                "derived_sha256": expected_sha,
                "source_length": expected_length,
                "derived_length": expected_length,
                "actual_capture_timestamp": expected_capture,
            }.items():
                if current_item.get(field) != expected:
                    diffs.append(f"{field}:{current_item.get(field)!r}!={expected!r}")
            output = SITE / str(current_item.get("output_path") or "")
            if not output.is_file() or file_sha(output) != expected_sha or output.stat().st_size != expected_length:
                diffs.append("output_bytes")
            if output.is_file():
                try:
                    from PIL import Image
                    with Image.open(output) as img:
                        img.verify()
                except Exception as exc:
                    diffs.append(f"output_decode:{type(exc).__name__}")
        if map_pair is not None:
            map_path, map_item = map_pair
            if current_item is None or str(current_item.get("source_map")) != rel(map_path) or str(current_item.get("source_map_sha256")) != map_sha:
                diffs.append("source_map_identity")
            if (map_item.get("sha256") != expected_sha or int(map_item.get("length", -1)) != expected_length or str(map_item.get("actual_timestamp") or map_item.get("actual_capture_timestamp") or "") != expected_capture):
                diffs.append("final_map_binding")
        if diffs:
            mismatch = {"route": route, "diffs": diffs}
            image_mismatches.append(mismatch)
            add_error(errors, "new_source_image_binding", **mismatch)
    if len(routes) != len(accepted_items) or accepted_bytes != sum(int(image.get("length", 0)) for image in accepted_items) or len(final_map_items) != len(accepted_items):
        add_error(errors, "new_image_conservation", receipt_routes=len(routes), receipt_bytes=accepted_bytes, final_map_items=len(final_map_items), accepted_count=len(accepted_items))
    return {"receipt_details": receipt_details, "unique_routes": len(routes), "accepted_bytes": accepted_bytes, "final_map_items": len(final_map_items), "map_sha256": map_sha, "mismatch_count": len(image_mismatches), "mismatch_sample": image_mismatches[:5]}


def check_collections_and_previews(provenance: dict, errors: list[dict]) -> dict:
    prior = read_json(PRIOR_PROVENANCE)
    stats = provenance.get("stats") or {}
    collection = provenance.get("guide_image_collections") or {}
    preview = provenance.get("guide_previews") or {}
    prior_collection = prior.get("guide_image_collections") or {}
    prior_preview = prior.get("guide_previews") or {}
    if collection != prior_collection:
        add_error(errors, "guide_collection_provenance_changed")
    if preview != prior_preview:
        add_error(errors, "guide_preview_provenance_changed")
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
            prior_record = next((item for item in prior.get("files", []) if item.get("route") == route), None)
            if prior_record is None or (SITE / str(record["output_path"])).read_bytes() != (PRIOR / str(prior_record.get("output_path") or "")).read_bytes():
                add_error(errors, "guide_collection_page_changed", route=route)
            slug = re.sub(r"[^a-z0-9]+", "-", group_id.casefold()).strip("-")
            section_id = f"offline-guide-images-{slug}-{page_role}"
            section_count = text.count(f'id="{section_id}"')
            card_count = text.count('data-guide-image-route="')
            lazy_count = text.count('loading="lazy"')
            anchor_count = text.count('class="offline-guide-image-guide"')
            if section_count != 1 or card_count != count or lazy_count < count or anchor_count != 1:
                add_error(errors, "guide_collection_section", route=route, section_count=section_count, cards=card_count, lazy=lazy_count, guide_anchors=anchor_count, expected=count)
            collection_pages.append({"group_id": group_id, "page_role": page_role, "route": route, "section_count": section_count, "card_count": card_count, "lazy_count": lazy_count, "guide_anchor_count": anchor_count})
    if len(collection_pages) != 6:
        add_error(errors, "guide_collection_page_count", count=len(collection_pages))
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
        "schema": "wow-recovery.publication.v24-offline-check.v1",
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
            raise RuntimeError("v24 output is not atomically complete")
        worker_sha = file_sha(WORKER)
        input_path = root_input_path()
        root_input_sha = file_sha(input_path)
        worker = read_json(WORKER)
        root_input = read_json(input_path)
        if worker.get("export_completed") is not True or worker.get("published") is not False or worker.get("network_requests_by_builder") != 0:
            add_error(errors, "worker_gate", export_completed=worker.get("export_completed"), published=worker.get("published"), network_requests=worker.get("network_requests_by_builder"))
        if root_input.get("accepted") is not True or root_input.get("network_requests") not in (0, None):
            add_error(errors, "root_input_gate", accepted=root_input.get("accepted"), single_export_go=root_input.get("single_export_go"), network_requests=root_input.get("network_requests"))
        if "single_export_go" in root_input and root_input.get("single_export_go") is not True:
            add_error(errors, "root_input_single_export_gate", value=root_input.get("single_export_go"))
        for binding in root_input.get("bindings", []):
            path = ROOT / str(binding.get("path"))
            if not path.is_file() or file_sha(path) != binding.get("sha256"):
                add_error(errors, "root_input_binding", path=str(binding.get("path")))
        if worker.get("input_hashes_before") != worker.get("input_hashes_after"):
            add_error(errors, "worker_input_hash_drift")
        if worker.get("maps_unchanged_during_export") is False or worker.get("production_unchanged_during_export") is False:
            add_error(errors, "worker_immutability_gate", maps=worker.get("maps_unchanged_during_export"), production=worker.get("production_unchanged_during_export"))
        for path, expected in (worker.get("input_hashes_after") or {}).items():
            actual = file_sha(ROOT / path)
            if actual != expected:
                add_error(errors, "input_binding_changed_since_export", path=path, expected=expected, actual=actual)
        if file_sha(PRIOR_PROVENANCE) != EXPECTED_PRIOR_V23_PROVENANCE_SHA:
            add_error(errors, "prior_v23_provenance_sha", actual=file_sha(PRIOR_PROVENANCE))
        if file_sha(SOURCE_MANIFEST) != EXPECTED_MANIFEST_SHA:
            add_error(errors, "source_manifest_sha", actual=file_sha(SOURCE_MANIFEST))
        for relative, expected in EXPECTED_INPUT_MAPS.items():
            actual = file_sha(ROOT / relative)
            if actual != expected:
                add_error(errors, "frozen_input_sha", path=relative, expected=expected, actual=actual)
        for relative, expected in EXPECTED_PRODUCTION.items():
            actual = file_sha(ROOT / relative)
            if actual != expected:
                add_error(errors, "production_sha", path=relative, expected=expected, actual=actual)
        provenance = read_json(V24_PROVENANCE)
        prior = read_json(PRIOR_PROVENANCE)
        stats = provenance.get("stats") or {}
        new_count = int(stats.get("primary_image_overlay_records", 0)) - 100
        expected_counts = {
            "source_records": 8357,
            "image_overlay_records": 162 + new_count,
            "primary_image_overlay_records": 100 + new_count,
            "supplement_image_overlay_records": 62,
        }
        for key, expected in expected_counts.items():
            if stats.get(key) != expected:
                add_error(errors, "provenance_counts", key=key, actual=stats.get(key), expected=expected)
        if not 10 <= new_count <= 20:
            add_error(errors, "new_overlay_count_range", new_count=new_count)
        result["worker_receipt_sha256"] = worker_sha
        result["root_input_acceptance_sha256"] = root_input_sha
        result["root_input_acceptance_path"] = rel(input_path)
        result["export_provenance_sha256"] = file_sha(V24_PROVENANCE)
        result["prior_v23_provenance_sha256"] = file_sha(PRIOR_PROVENANCE)
        result["offline_tree"] = scan_tree(provenance, prior, errors, findings)
        result["prior_overlay_check"] = check_prior_overlays(provenance, prior, errors)
        result["routing_conservation"] = check_routing(errors)
        result["new_source_images"] = check_new_images(provenance, errors)
        result["guide_checks"] = check_collections_and_previews(provenance, errors)
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
