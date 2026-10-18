#!/usr/bin/env python3
"""Prepare and preflight the v32 image closure; never export.

v32 consolidates the unexecuted v31 news49 preparation with seven accepted
next70 batches.  The map produced here is a delta over the frozen v30
closure: 49 news images plus 54 next70 images.  This module only reads old
maps and accepted public copies, writes new v32 preparation evidence, and has
no export path.  ``execute_v32.py`` is the separately guarded export entry.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"

V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V28_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"
V28_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"
V29_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"
V29_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v29/export-provenance.json"
V30_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-supplement-source-map.json"
V30_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v30/export-provenance.json"
V30_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-build-receipt.json"
ROOT_V30_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v30-input-acceptance.json"

V31_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v31/build_pages_v31.py"
V31_EXECUTOR = ROOT / "research/continuous-recovery-20261018/integration/v31/execute_v31.py"
V31_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-primary-source-map.json"
V31_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-supplement-source-map.json"
V31_IMPACT = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-impact-estimate.json"
V31_SOURCE_AUDIT = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-source-byte-audit.json"
V31_PREPARATION = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-input-preparation.json"
V31_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-preflight.json"
V31_PROPOSAL = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-input-proposal.md"
V31_RUNNER_NOTE = ROOT / "research/continuous-recovery-20261018/integration/v31/v31-runner-preparation.md"
V31_SUPERSEDED = ROOT / "research/continuous-recovery-20261018/publication/root-v31-preparation-superseded.json"
V31_RUNTIME_IMPACT = ROOT / "research/continuous-recovery-20261018/publication/root-v31-runtime-impact.json"

EXPORTER = ROOT / "tools/export_github_pages.py"
HISTORICAL_EXHIBITS = ROOT / "tools/historical_exhibits.py"
ROOT_POPUP_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-popup-tool-acceptance.json"
ROOT_RETIRED_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-retired-armory-tool-acceptance.json"
ROOT_MASK_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-attunement-mask-tool-acceptance.json"

NEWS49_RECEIPTS = tuple(
    ROOT / f"research/continuous-recovery-20261018/publication/root-news49-batch{index}-public-copy-acceptance.json"
    for index in range(1, 6)
)
NEXT70_RECEIPTS = tuple(
    ROOT / f"research/continuous-recovery-20261018/publication/root-next70-batch{index}-public-copy-acceptance.json"
    for index in range(1, 8)
)
NEXT70_COUNTS = (8, 7, 10, 8, 4, 9, 8)

V32_PRIMARY_MAP = INTEGRATION / "v32-primary-source-map.json"
V32_SUPPLEMENT_MAP = INTEGRATION / "v32-supplement-source-map.json"
V32_IMPACT = INTEGRATION / "v32-impact-estimate.json"
V32_SOURCE_AUDIT = INTEGRATION / "v32-source-byte-audit.json"
V32_PREPARATION = INTEGRATION / "v32-input-preparation.json"
V32_PREFLIGHT = INTEGRATION / "v32-preflight.json"
V32_PROPOSAL = INTEGRATION / "v32-input-proposal.md"
V32_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v32"
V32_BUILD_RECEIPT = INTEGRATION / "v32-build-receipt.json"

ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696
PRIMARY_HOST = "www.worldofwarcraft.com"

EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V29_PROVENANCE_SHA256 = "793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8"
EXPECTED_V30_PRIMARY_MAP_SHA256 = "8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e"
EXPECTED_V30_SUPPLEMENT_MAP_SHA256 = "53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0"
EXPECTED_V30_PROVENANCE_SHA256 = "b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85"
EXPECTED_V30_BUILD_RECEIPT_SHA256 = "87a5edd7075a339d15da1532ebc630f36e31fae48db1bbafcaa5b15982d9623c"
EXPECTED_V30_INPUT_ACCEPTANCE_SHA256 = "c906c986551e23a569b534057331cef6e6add952125afa3c39416262f823a0d9"
EXPECTED_V31_BUILDER_SHA256 = "e8d82e6a7db4d8e21fff443581fd401d6890d4f5ffc688ea5105ad9cfdd1e7be"
EXPECTED_V31_EXECUTOR_SHA256 = "87fa04262b2792381825eac2ee88b8dbdecb6877b3c11e549116f11244b21c55"
EXPECTED_V31_PRIMARY_MAP_SHA256 = "b9228a8478529cd4a39ba0550665f050cdd6690a211ad0b285a30a6bfaeced16"
EXPECTED_V31_SUPPLEMENT_MAP_SHA256 = "bd0820d484eb4f42fc1b1f7d4bbbfd12bb14ab9dc9d8489924e08fb2af08fc23"
EXPECTED_V31_IMPACT_SHA256 = "3d83fd105d03dbdcaa02a2347666e13eece12ca616496d5c48bcd0b6ad041ec7"
EXPECTED_V31_SOURCE_AUDIT_SHA256 = "d4f7489c7673c34e7252c8dc0c770e64756375821e3e0e13ac5ddf0d5ac21a09"
EXPECTED_V31_PREPARATION_SHA256 = "27f0939380b9a1c444facf4d6901eaadb1c59a837a50966f9277a134b13c26cc"
EXPECTED_V31_PREFLIGHT_SHA256 = "e41063c1b7ea3470760ff95514723f40168420ca78820381629735c5381450aa"
EXPECTED_V31_PROPOSAL_SHA256 = "3010ecb41dfd801d6181492eb5214cc299bc4fc59d4dbd4701e1887611d15d6e"
EXPECTED_V31_RUNNER_NOTE_SHA256 = "e346727b4026ca513ea70c295b7696e7308f138d24bacb43c968371345ebf51f"
EXPECTED_V31_SUPERSEDED_SHA256 = "6de57eb46157d996fa2184900be9d094cc430f43f17b622c2d2db35803238d7d"
EXPECTED_V31_RUNTIME_IMPACT_SHA256 = "6b11f2b3b3c5b9d00aec1ad2433b047da30f7582877defedc20f73d4830a9401"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_EXPORTER_SHA256 = "8c50b1574f24a0bd2b03492ae8fe0cb7d3c48a50a247ba70d9e1859d58672afb"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_POPUP_TOOL_SHA256 = "6e7d0afd979161fd98b996e6256d4ce39359017c5a1428b5e0d7589fe596f8bf"
EXPECTED_RETIRED_TOOL_SHA256 = "46058b7e23cfa317949f42945196b40be77a6e6485834147e8e32a62c6643e6b"
EXPECTED_MASK_TOOL_SHA256 = "8c295a243993353de30ea8173ef5e8530656c65acdbbf0785855eadb14eefa24"
EXPECTED_NEW_IMAGES = 103
EXPECTED_NEW_BYTES = 1_734_198
EXPECTED_NEWS_IMAGES = 49
EXPECTED_NEWS_BYTES = 480_639
EXPECTED_NEXT_IMAGES = 54
EXPECTED_NEXT_BYTES = 1_253_559
EXPECTED_V30_PRIMARY = 247
EXPECTED_V30_SUPPLEMENT = 89
EXPECTED_V30_TOTAL = 336
EXPECTED_PRIMARY = 350
EXPECTED_SUPPLEMENT = 89
EXPECTED_TOTAL = 439
EXPECTED_SOURCE_RECORDS = 8_357
EXPECTED_GUIDE_IMAGES = 39
EXPECTED_GUIDE_PREVIEWS = 22
EXPECTED_DECLARED_FILES = 8_897
EXPECTED_ACTUAL_FILES = 8_898


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes workspace: {path}") from exc
    return resolved


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def host(url: str) -> str:
    return (urlsplit(url).hostname or "").casefold().rstrip(".")


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme.casefold()}://{host(url)}{parsed.path}"


def temporal_class(timestamp: str) -> str:
    actual = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    anchor = datetime.strptime(ANCHOR, "%Y%m%d%H%M%S")
    if actual < datetime(2008, 1, 1):
        return "pre_2008"
    if actual <= anchor:
        return "baseline_2008"
    if actual <= datetime(2008, 12, 31, 23, 59, 59):
        return "late_2008"
    return "post_2008"


def load_v28_builder():
    actual = sha256_file(V28_BUILDER)
    if actual != EXPECTED_V28_BUILDER_SHA256:
        raise RuntimeError(f"v28 builder SHA changed: {actual}")
    spec = importlib.util.spec_from_file_location("wow_recovery_frozen_v28_builder_v32", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_exporter():
    tools = ROOT / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    import export_github_pages  # noqa: E402

    return export_github_pages


def verify_pinned_files() -> dict[str, str]:
    pinned = {
        V28_BUILDER: EXPECTED_V28_BUILDER_SHA256,
        V28_PRIMARY_MAP: EXPECTED_V28_PRIMARY_MAP_SHA256,
        V28_PROVENANCE: EXPECTED_V28_PROVENANCE_SHA256,
        V29_PRIMARY_MAP: EXPECTED_V29_PRIMARY_MAP_SHA256,
        V29_PROVENANCE: EXPECTED_V29_PROVENANCE_SHA256,
        V30_PRIMARY_MAP: EXPECTED_V30_PRIMARY_MAP_SHA256,
        V30_SUPPLEMENT_MAP: EXPECTED_V30_SUPPLEMENT_MAP_SHA256,
        V30_PROVENANCE: EXPECTED_V30_PROVENANCE_SHA256,
        V30_BUILD_RECEIPT: EXPECTED_V30_BUILD_RECEIPT_SHA256,
        ROOT_V30_INPUT_ACCEPTANCE: EXPECTED_V30_INPUT_ACCEPTANCE_SHA256,
        V31_BUILDER: EXPECTED_V31_BUILDER_SHA256,
        V31_EXECUTOR: EXPECTED_V31_EXECUTOR_SHA256,
        V31_PRIMARY_MAP: EXPECTED_V31_PRIMARY_MAP_SHA256,
        V31_SUPPLEMENT_MAP: EXPECTED_V31_SUPPLEMENT_MAP_SHA256,
        V31_IMPACT: EXPECTED_V31_IMPACT_SHA256,
        V31_SOURCE_AUDIT: EXPECTED_V31_SOURCE_AUDIT_SHA256,
        V31_PREPARATION: EXPECTED_V31_PREPARATION_SHA256,
        V31_PREFLIGHT: EXPECTED_V31_PREFLIGHT_SHA256,
        V31_PROPOSAL: EXPECTED_V31_PROPOSAL_SHA256,
        V31_RUNNER_NOTE: EXPECTED_V31_RUNNER_NOTE_SHA256,
        V31_SUPERSEDED: EXPECTED_V31_SUPERSEDED_SHA256,
        V31_RUNTIME_IMPACT: EXPECTED_V31_RUNTIME_IMPACT_SHA256,
        SOURCE_MANIFEST: EXPECTED_SOURCE_MANIFEST_SHA256,
        EXPORTER: EXPECTED_EXPORTER_SHA256,
        HISTORICAL_EXHIBITS: EXPECTED_HISTORICAL_EXHIBITS_SHA256,
        ROOT_POPUP_ACCEPTANCE: EXPECTED_POPUP_TOOL_SHA256,
        ROOT_RETIRED_ACCEPTANCE: EXPECTED_RETIRED_TOOL_SHA256,
        ROOT_MASK_ACCEPTANCE: EXPECTED_MASK_TOOL_SHA256,
    }
    result: dict[str, str] = {}
    for path, expected in pinned.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"pinned file changed: {rel(path)} ({actual} != {expected})")
        result[rel(path)] = actual
    return result


def validate_public_receipt(receipt_path: Path, expected_count: int) -> tuple[dict, list[dict], dict]:
    receipt = read_json(receipt_path, receipt_path.name)
    if receipt.get("accepted") is not True or receipt.get("copy_mode") != "original_bytes":
        raise RuntimeError(f"{receipt_path.name} is not an accepted original-byte copy")
    raw_items = receipt.get("accepted_images")
    if not isinstance(raw_items, list) or len(raw_items) != expected_count:
        raise RuntimeError(f"{receipt_path.name} expected {expected_count} items, got {len(raw_items or [])}")
    source_binding = receipt.get("source_acceptance") or receipt.get("source_receipt")
    if not isinstance(source_binding, dict) or not source_binding.get("path"):
        raise RuntimeError(f"{receipt_path.name} has no source receipt binding")
    source_path = inside(ROOT / str(source_binding["path"]), f"source receipt for {receipt_path.name}")
    source_sha = sha256_file(source_path)
    if str(source_binding.get("sha256") or "").casefold() != source_sha:
        raise RuntimeError(f"{receipt_path.name} source receipt SHA mismatch")
    binding = {"path": rel(source_path), "sha256": source_sha}
    rows: list[dict] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict) or raw.get("accepted") is not True or raw.get("deployed") is not False:
            raise RuntimeError(f"{receipt_path.name}.accepted_images[{index}] is not accepted and undeployed")
        original = str(raw.get("original") or "")
        if not original or original in seen:
            raise RuntimeError(f"duplicate or missing original: {original!r}")
        seen.add(original)
        if host(original) != PRIMARY_HOST:
            raise RuntimeError(f"non-primary v32 source: {original}")
        actual = str(raw.get("actual_capture_timestamp") or "")
        if not re.fullmatch(r"\d{14}", actual):
            raise RuntimeError(f"invalid capture timestamp for {original}: {actual!r}")
        datetime.strptime(actual, "%Y%m%d%H%M%S")
        source_rel = str(raw.get("local_path") or "")
        if not source_rel.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in source_rel:
            raise RuntimeError(f"non-public source path for {original}: {source_rel}")
        source = inside(ROOT / source_rel, f"public source for {original}")
        if not source.is_file():
            raise RuntimeError(f"public source missing: {source}")
        data = source.read_bytes()
        expected_length = int(raw.get("length", -1))
        expected_sha = str(raw.get("sha256") or "").casefold()
        if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
            raise RuntimeError(f"public source bytes differ: {original}")
        if cdx_digest(data) != str(raw.get("cdx_digest") or "").upper():
            raise RuntimeError(f"public source CDX differs: {original}")
        row = dict(raw)
        row["_destination"] = source
        row["_receipt_path"] = receipt_path
        row["_source_binding"] = binding
        rows.append(row)
    if int(receipt.get("image_bytes", -1)) != sum(int(row["length"]) for row in rows):
        raise RuntimeError(f"{receipt_path.name} image_bytes does not match rows")
    return receipt, rows, binding


def map_item_from_row(raw: dict, *, relationship: str) -> dict:
    original = str(raw["original"])
    actual = str(raw.get("actual_capture_timestamp") or raw.get("actual_timestamp") or "")
    return {
        "kind": "image",
        "logical_url": original,
        "original": original,
        "actual_timestamp": actual,
        "indexed_capture_timestamp": actual,
        "mime": str(raw["mime"]),
        "dimensions": raw.get("dimensions"),
        "decoded_frames": raw.get("decoded_frames"),
        "length": int(raw["length"]),
        "sha256": str(raw["sha256"]).casefold(),
        "cdx_digest": str(raw["cdx_digest"]).upper(),
        "local_path": rel(raw["_destination"]),
        "temporal_class": temporal_class(actual),
        "source_acceptance_path": raw["_source_binding"]["path"],
        "public_copy_acceptance_path": rel(raw["_receipt_path"]),
        "public_copy_path": str(raw["local_path"]),
        "source_relationship": relationship,
        "overlay_role": "primary_image_overlay",
    }


def map_item_from_v31(item: dict) -> dict:
    result = dict(item)
    result["source_relationship"] = "Root-accepted public-copy bytes; v32 primary overlay carried from v31; no deployment implied."
    result["overlay_role"] = "primary_image_overlay"
    return result


def unique_bindings(items: list[dict], key: str) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for item in items:
        path = str(item[key])
        if path not in seen:
            seen.add(path)
            result.append({"path": path, "sha256": sha256_file(ROOT / path)})
    return result


def validate_new_map(payload: dict, *, expected_count: int, expected_bytes: int) -> dict:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != expected_count:
        raise RuntimeError(f"v32 primary map expected {expected_count} items")
    seen: set[str] = set()
    total = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict) or item.get("kind") != "image":
            raise RuntimeError(f"v32 map item {index} is not an image")
        original = str(item.get("original") or "")
        logical = str(item.get("logical_url") or "")
        if not original or original in seen:
            raise RuntimeError(f"duplicate v32 original: {original}")
        if canonical_url(logical) != canonical_url(original) or host(logical) != PRIMARY_HOST:
            raise RuntimeError(f"logical/original mismatch: {original}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local:
            raise RuntimeError(f"v32 map item is not a public copy: {local}")
        source = inside(ROOT / local, f"v32 map source {original}")
        data = source.read_bytes()
        if len(data) != int(item.get("length", -1)) or hashlib.sha256(data).hexdigest() != str(item.get("sha256") or "").casefold():
            raise RuntimeError(f"v32 map bytes differ: {original}")
        if cdx_digest(data) != str(item.get("cdx_digest") or "").upper():
            raise RuntimeError(f"v32 map CDX differs: {original}")
        actual = str(item.get("actual_timestamp") or "")
        if str(item.get("indexed_capture_timestamp") or "") != actual or str(item.get("temporal_class") or "") != temporal_class(actual):
            raise RuntimeError(f"v32 map capture metadata differs: {original}")
        seen.add(original)
        total += len(data)
    if total != expected_bytes:
        raise RuntimeError(f"v32 map bytes {total} != {expected_bytes}")
    return {"role": "primary_image_overlay", "items": len(items), "bytes": total, "hosts": [PRIMARY_HOST]}


def map_route_sets(paths: tuple[Path, ...], export_module) -> tuple[set[str], set[str]]:
    routes: set[str] = set()
    static_paths: set[str] = set()
    for path in paths:
        payload = read_json(path, path.name)
        for index, item in enumerate(payload.get("items") or []):
            logical = str(item.get("logical_url") or item.get("original") or "")
            if not logical:
                raise RuntimeError(f"map item has no logical URL: {path}[{index}]")
            route = export_module.mirror.route_path(logical) if export_module.mirror.is_primary_origin(logical) else export_module.mirror.origin_route(logical)
            routes.add(route)
            static_paths.add(export_module.static_rel_for_route(route))
    return routes, static_paths


def build_impact(items: list[dict]) -> dict:
    export_module = import_exporter()
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    targets = {canonical_url(str(item["original"])): item for item in items}
    found: dict[str, list[dict]] = {str(item["original"]): [] for item in items}
    for record in manifest.get("files", []):
        if not isinstance(record, dict):
            continue
        for reference in record.get("references", []) or []:
            if not isinstance(reference, dict):
                continue
            resolved = str(reference.get("resolved_url") or "")
            item = targets.get(canonical_url(resolved))
            if item is None:
                continue
            target = str(reference.get("target") or "")
            source = str(record.get("route") or "")
            query = dict()
            if "?" in target:
                from urllib.parse import parse_qs, unquote

                query = parse_qs(urlsplit(target).query)
                source = unquote(query.get("source", [source])[0])
            source_route = urlsplit(source).path if source.startswith(("http://", "https://")) else source
            found[str(item["original"])].append({
                "source_page": source_route,
                "manifest_route": str(record.get("route") or ""),
                "action": str(reference.get("action") or ""),
                "context": str(reference.get("context") or ""),
                "target": target,
            })
    rows = []
    for item in items:
        original = str(item["original"])
        route = export_module.mirror.route_path(original)
        rows.append({
            "original": original,
            "role": "primary",
            "output_path": export_module.static_rel_for_route(route),
            "reference_count": len(found[original]),
            "references": found[original],
        })
    affected = sorted({ref["source_page"] for row in rows for ref in row["references"] if ref["source_page"]})
    return {
        "schema": "wow-recovery.integration.v32-impact-estimate.v1",
        "status": "static_manifest_estimate_only",
        "source_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256_file(SOURCE_MANIFEST)},
        "new_image_count": len(items),
        "expected_output_paths": [row["output_path"] for row in rows],
        "items": rows,
        "affected_page_routes": affected,
        "static_missing_reduction_estimate": {
            "placeholder_reference_occurrences": sum(ref["action"] == "placeholder" for row in rows for ref in row["references"]),
            "unique_affected_page_routes": len(affected),
            "new_assets_without_frozen_manifest_reference": sum(row["reference_count"] == 0 for row in rows),
            "note": "Manifest counts are planning evidence only; root post-export page scans remain authoritative.",
        },
        "network_requests": 0,
        "export_executed": False,
    }


def build_source_audit(items: list[dict]) -> dict:
    entries = []
    for item in items:
        source = ROOT / str(item["local_path"])
        data = source.read_bytes()
        entries.append({
            "original": item["original"],
            "host": host(item["original"]),
            "role": "primary",
            "actual_capture_timestamp": item["actual_timestamp"],
            "mime": item["mime"],
            "dimensions": item.get("dimensions"),
            "public_copy_path": item["local_path"],
            "public_copy_acceptance_path": item["public_copy_acceptance_path"],
            "source_acceptance_path": item["source_acceptance_path"],
            "source_acceptance_sha256": sha256_file(ROOT / item["source_acceptance_path"]),
            "declared_length": int(item["length"]),
            "actual_length": len(data),
            "declared_sha256": item["sha256"],
            "actual_sha256": hashlib.sha256(data).hexdigest(),
            "declared_cdx_digest": item["cdx_digest"],
            "actual_cdx_digest": cdx_digest(data),
            "output_path": item["original"].split("//", 1)[-1].split("/", 1)[-1],
            "byte_match": len(data) == int(item["length"]) and hashlib.sha256(data).hexdigest() == item["sha256"] and cdx_digest(data) == item["cdx_digest"],
        })
    if not all(entry["byte_match"] for entry in entries):
        raise RuntimeError("v32 source byte audit mismatch")
    return {
        "schema": "wow-recovery.integration.v32-source-byte-audit.v1",
        "status": "actual_public_copy_bytes_checked",
        "source_count": len(entries),
        "primary_count": len(entries),
        "supplement_count": 0,
        "primary_bytes": sum(entry["actual_length"] for entry in entries),
        "supplement_bytes": 0,
        "total_bytes": sum(entry["actual_length"] for entry in entries),
        "all_byte_match": True,
        "network_requests": 0,
        "entries": entries,
    }


def write_once(path: Path, payload: dict | str, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite {label}: {path}")
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    if not (args.prepare and args.preflight):
        parser.error("v32 preparation requires both --prepare and --preflight; export is execute_v32.py only")
    if V32_OUTPUT.exists() or V32_OUTPUT.with_name(V32_OUTPUT.name + ".partial").exists() or V32_BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v32 output, partial output, or build receipt")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below floor before v32 preparation: {free_before}")
    pins = verify_pinned_files()
    frozen = load_v28_builder()
    export_module = import_exporter()

    v31_map = read_json(V31_PRIMARY_MAP, V31_PRIMARY_MAP.name)
    v31_items = [map_item_from_v31(item) for item in v31_map.get("items", [])]
    if len(v31_items) != 49 or sum(int(item["length"]) for item in v31_items) != EXPECTED_NEWS_BYTES:
        raise RuntimeError("v31 news49 map changed")
    next_rows: list[dict] = []
    next_summaries: list[dict] = []
    next_bindings: list[dict] = []
    for receipt_path, expected_count in zip(NEXT70_RECEIPTS, NEXT70_COUNTS):
        receipt, rows, binding = validate_public_receipt(receipt_path, expected_count)
        next_rows.extend(rows)
        next_bindings.append(binding)
        next_summaries.append({
            "path": rel(receipt_path),
            "sha256": sha256_file(receipt_path),
            "count": len(rows),
            "bytes": sum(int(row["length"]) for row in rows),
            "accepted": receipt.get("accepted") is True,
            "copy_mode": receipt.get("copy_mode"),
        })
    if len(next_rows) != EXPECTED_NEXT_IMAGES or sum(int(row["length"]) for row in next_rows) != EXPECTED_NEXT_BYTES:
        raise RuntimeError("next70 count or byte total changed")
    v32_items = v31_items + [map_item_from_row(row, relationship="Root-accepted public-copy bytes; v32 primary overlay; no deployment implied.") for row in next_rows]
    originals = [str(item["original"]) for item in v32_items]
    if len(set(originals)) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("v32 news49/next70 originals overlap")

    old_primary_maps = tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP, V30_PRIMARY_MAP)
    old_supplement_maps = tuple(frozen.SUPPLEMENT_MAPS) + (V30_SUPPLEMENT_MAP,)
    old_originals = set()
    for path in old_primary_maps + old_supplement_maps:
        payload = read_json(path, path.name)
        old_originals.update(str(item.get("original") or item.get("logical_url") or "") for item in payload.get("items", []))
    overlap = old_originals & set(originals)
    if overlap:
        raise RuntimeError(f"v32 new originals overlap v30 closure: {sorted(overlap)}")

    primary_map = {
        "schema_version": "wow-recovery.integration.v32.primary-source-map.v1",
        "kind": "wow_static_v32_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v32_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the root-accepted news49 and next70 public-copy images are added; all v30 supplements and future popup24 resources remain outside v32.",
        "relative_to_v30": {
            "new_items": EXPECTED_NEW_IMAGES,
            "new_bytes": EXPECTED_NEW_BYTES,
            "v30_primary_map": {"path": rel(V30_PRIMARY_MAP), "sha256": EXPECTED_V30_PRIMARY_MAP_SHA256, "items": 19, "bytes": 70_546},
            "v30_supplement_map": {"path": rel(V30_SUPPLEMENT_MAP), "sha256": EXPECTED_V30_SUPPLEMENT_MAP_SHA256, "items": 14, "bytes": 86_311},
            "v30_provenance": {"path": rel(V30_PROVENANCE), "sha256": EXPECTED_V30_PROVENANCE_SHA256, "stats": read_json(V30_PROVENANCE, V30_PROVENANCE.name).get("stats", {})},
        },
        "source_acceptance": unique_bindings(v32_items, "source_acceptance_path"),
        "public_copy_acceptance": sorted({str(item["public_copy_acceptance_path"]) for item in v32_items}),
        "items": v32_items,
    }
    supplement_map = {
        "schema_version": "wow-recovery.integration.v32.supplement-source-map.v1",
        "kind": "wow_static_v32_supplement_image_source_map",
        "role": "supplement_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v32_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "No new v32 supplement images; the frozen Armory and Blizzard supplements remain in v30 closure.",
        "relative_to_v30": {"new_items": 0, "new_bytes": 0, "v30_primary_map": primary_map["relative_to_v30"]["v30_primary_map"], "v30_supplement_map": primary_map["relative_to_v30"]["v30_supplement_map"], "v30_provenance": primary_map["relative_to_v30"]["v30_provenance"]},
        "source_acceptance": [],
        "public_copy_acceptance": [],
        "items": [],
    }
    primary_check = validate_new_map(primary_map, expected_count=EXPECTED_NEW_IMAGES, expected_bytes=EXPECTED_NEW_BYTES)
    supplement_check = {"role": "supplement_image_overlay", "items": 0, "bytes": 0, "hosts": []}
    write_once(V32_PRIMARY_MAP, primary_map, "v32 primary map")
    write_once(V32_SUPPLEMENT_MAP, supplement_map, "v32 supplement map")

    old_primary_routes, old_primary_paths = map_route_sets(old_primary_maps, export_module)
    old_supplement_routes, old_supplement_paths = map_route_sets(old_supplement_maps, export_module)
    new_routes, new_paths = map_route_sets((V32_PRIMARY_MAP,), export_module)
    primary_routes = old_primary_routes | new_routes
    primary_paths = old_primary_paths | new_paths
    supplement_routes = old_supplement_routes
    supplement_paths = old_supplement_paths
    if len(primary_routes) != EXPECTED_PRIMARY or len(supplement_routes) != EXPECTED_SUPPLEMENT:
        raise RuntimeError(f"v32 closure counts changed: {len(primary_routes)}/{len(supplement_routes)}")
    loader = {
        "primary_overlay_records": len(primary_routes),
        "primary_overlay_bytes_checked_new": EXPECTED_NEW_BYTES,
        "supplement_overlay_records": len(supplement_routes),
        "supplement_overlay_bytes_checked_new": 0,
        "total_overlay_records": len(primary_routes) + len(supplement_routes),
        "new_primary_records": EXPECTED_NEW_IMAGES,
        "new_supplement_records": 0,
        "guide_collection_groups": 3,
        "guide_collection_images": EXPECTED_GUIDE_IMAGES,
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }
    all_items = primary_map["items"]
    impact = build_impact(all_items)
    source_audit = build_source_audit(all_items)
    write_once(V32_IMPACT, impact, "v32 impact estimate")
    write_once(V32_SOURCE_AUDIT, source_audit, "v32 source byte audit")
    checked_utc = datetime.utcnow().isoformat() + "Z"
    map_meta = {
        "primary": {"path": rel(V32_PRIMARY_MAP), "sha256": sha256_file(V32_PRIMARY_MAP), "items": EXPECTED_NEW_IMAGES, "bytes": EXPECTED_NEW_BYTES},
        "supplement": {"path": rel(V32_SUPPLEMENT_MAP), "sha256": sha256_file(V32_SUPPLEMENT_MAP), "items": 0, "bytes": 0},
    }
    expected_after_export = {
        "source_records": EXPECTED_SOURCE_RECORDS,
        "declared_files": EXPECTED_DECLARED_FILES,
        "actual_files": EXPECTED_ACTUAL_FILES,
        "primary_overlays": EXPECTED_PRIMARY,
        "supplement_overlays": EXPECTED_SUPPLEMENT,
        "total_overlays": EXPECTED_TOTAL,
        "guide_previews": EXPECTED_GUIDE_PREVIEWS,
        "guide_collection_images": EXPECTED_GUIDE_IMAGES,
        "runtime_allowed_changes": {
            "historical_body_banner_pages": 5,
            "retired_armory_script": "/new-hp/js/enhancedtip.js",
            "popup_runtime": "__offline/pages_runtime.js",
            "attunement_mask_page": "/bcattunement/index.html",
            "note": "Root browser/static acceptance remains authoritative; mask changes three compatibility references and recovers zero original images.",
        },
    }
    prep = {
        "schema": "wow-recovery.integration.v32-input-preparation.v1",
        "status": "prepared_waiting_root_v32_input_acceptance",
        "checked_utc": checked_utc,
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "frozen_v30_closure": {"primary_overlays": EXPECTED_V30_PRIMARY, "supplement_overlays": EXPECTED_V30_SUPPLEMENT, "total_overlays": EXPECTED_V30_TOTAL, "source_records": EXPECTED_SOURCE_RECORDS, "maps": [{"path": rel(path), "sha256": sha256_file(path)} for path in old_primary_maps + old_supplement_maps], "provenance": {"path": rel(V30_PROVENANCE), "sha256": EXPECTED_V30_PROVENANCE_SHA256}},
        "v31_prepared_news49": {"map": {"path": rel(V31_PRIMARY_MAP), "sha256": EXPECTED_V31_PRIMARY_MAP_SHA256, "items": EXPECTED_NEWS_IMAGES, "bytes": EXPECTED_NEWS_BYTES}, "preparation_status": "superseded_unexecuted_v31_preparation"},
        "next70_receipts": {"receipts": next_summaries, "bindings": next_bindings, "accepted_count": EXPECTED_NEXT_IMAGES, "accepted_bytes": EXPECTED_NEXT_BYTES},
        "new_maps": map_meta,
        "impact": {"path": rel(V32_IMPACT), "sha256": sha256_file(V32_IMPACT), "new_image_count": EXPECTED_NEW_IMAGES},
        "source_byte_audit": {"path": rel(V32_SOURCE_AUDIT), "sha256": sha256_file(V32_SOURCE_AUDIT), "items": EXPECTED_NEW_IMAGES, "bytes": EXPECTED_NEW_BYTES},
        "loader_preflight": loader,
        "expected_after_export": expected_after_export,
        "tool_bindings": {"exporter": {"path": rel(EXPORTER), "sha256": EXPECTED_EXPORTER_SHA256}, "historical_exhibits": {"path": rel(HISTORICAL_EXHIBITS), "sha256": EXPECTED_HISTORICAL_EXHIBITS_SHA256}, "popup_acceptance": {"path": rel(ROOT_POPUP_ACCEPTANCE), "sha256": EXPECTED_POPUP_TOOL_SHA256}, "retired_armory_acceptance": {"path": rel(ROOT_RETIRED_ACCEPTANCE), "sha256": EXPECTED_RETIRED_TOOL_SHA256}, "attunement_mask_acceptance": {"path": rel(ROOT_MASK_ACCEPTANCE), "sha256": EXPECTED_MASK_TOOL_SHA256}},
        "relative_to_v30": {"new_images": EXPECTED_NEW_IMAGES, "new_bytes": EXPECTED_NEW_BYTES, "primary_overlays": EXPECTED_V30_PRIMARY, "supplement_overlays": EXPECTED_V30_SUPPLEMENT, "total_overlays": EXPECTED_V30_TOTAL},
        "future_excluded": {"popup24_images": 24, "popup24_bytes": None, "source_records": 273, "reason": "future popup24 queue and source-count projection are outside v32"},
        "network_requests": 0,
        "export_executed": False,
        "root_input_acceptance_required": True,
        "output": rel(V32_OUTPUT),
        "disk_free_before_bytes": free_before,
    }
    preflight = {
        "schema": "wow-recovery.integration.v32-preflight.v1",
        "status": "preflight_passed_waiting_root_v32_input_acceptance",
        "checked_utc": checked_utc,
        "builder": prep["builder"],
        "frozen_v30_closure": prep["frozen_v30_closure"],
        "v31_prepared_news49": prep["v31_prepared_news49"],
        "next70_receipts": prep["next70_receipts"],
        "new_maps": map_meta,
        "impact": prep["impact"],
        "source_byte_audit": prep["source_byte_audit"],
        "map_validation": {"primary": primary_check, "supplement": supplement_check},
        "loader_preflight": loader,
        "expected_after_export": expected_after_export,
        "tool_bindings": prep["tool_bindings"],
        "pinned_files": pins,
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
        "root_input_acceptance_required": True,
        "disk_free_bytes": shutil.disk_usage(ROOT).free,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    proposal = f"""# v32 input proposal

v32 consolidates the unexecuted v31 news49 preparation with seven root-accepted next70 public-copy batches. The new delta over v30 is {EXPECTED_NEW_IMAGES} primary images ({EXPECTED_NEW_BYTES} bytes): {EXPECTED_NEWS_IMAGES} news images ({EXPECTED_NEWS_BYTES} bytes) and {EXPECTED_NEXT_IMAGES} next70 images ({EXPECTED_NEXT_BYTES} bytes). The v30 closure remains {EXPECTED_V30_PRIMARY} primary, {EXPECTED_V30_SUPPLEMENT} supplement, and {EXPECTED_V30_TOTAL} total overlays; the planned v32 closure is {EXPECTED_PRIMARY} primary, {EXPECTED_SUPPLEMENT} supplement, and {EXPECTED_TOTAL} total overlays.

The planned file counts are {EXPECTED_DECLARED_FILES} declared / {EXPECTED_ACTUAL_FILES} actual with {EXPECTED_SOURCE_RECORDS} source records, {EXPECTED_GUIDE_IMAGES} guide collection images, and {EXPECTED_GUIDE_PREVIEWS} previews. These are preparation expectations only; root post-export static and browser checks remain authoritative. The five known real-body banner pages, retired Armory script, popup runtime, and the exact attunement compatibility mask are the allowed derived runtime/page changes. The attunement mask replaces three visible missing-image references with the existing transparent pixel and recovers no original image.

The builder binds the frozen v30 map/provenance closure, the superseded unexecuted v31 news49 map, all 103 public-copy bytes, exporter `{EXPECTED_EXPORTER_SHA256}`, unchanged historical exhibits `{EXPECTED_HISTORICAL_EXHIBITS_SHA256}`, and the popup, retired-Armory, and attunement-mask root receipts. Future popup24 resources and the source-count projection 273 are explicitly excluded. `execute_v32.py` is export-only and requires an independently accepted root input receipt plus `--go --root-export-go`; no v32 export has been executed.
"""
    write_once(V32_PREPARATION, prep, "v32 input preparation")
    write_once(V32_PREFLIGHT, preflight, "v32 preflight")
    write_once(V32_PROPOSAL, proposal, "v32 proposal")
    print(json.dumps({
        "status": preflight["status"],
        "primary_map": rel(V32_PRIMARY_MAP),
        "primary_map_sha256": sha256_file(V32_PRIMARY_MAP),
        "supplement_map": rel(V32_SUPPLEMENT_MAP),
        "supplement_map_sha256": sha256_file(V32_SUPPLEMENT_MAP),
        "impact_sha256": sha256_file(V32_IMPACT),
        "source_byte_audit_sha256": sha256_file(V32_SOURCE_AUDIT),
        "preparation_sha256": sha256_file(V32_PREPARATION),
        "preflight_sha256": sha256_file(V32_PREFLIGHT),
        "proposal_sha256": sha256_file(V32_PROPOSAL),
        "new_primary_items": EXPECTED_NEW_IMAGES,
        "new_bytes": EXPECTED_NEW_BYTES,
        "primary_overlays": EXPECTED_PRIMARY,
        "supplement_overlays": EXPECTED_SUPPLEMENT,
        "total_overlays": EXPECTED_TOTAL,
        "loader": loader,
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
