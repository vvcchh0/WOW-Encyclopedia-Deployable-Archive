#!/usr/bin/env python3
"""Prepare and preflight the v30 static38 input closure; never export.

The v30 preparation reuses the frozen v28 builder's map constants and the
completed v29 primary map, then adds only the four root-accepted static38
public-copy receipts.  It keeps the 19 canonical WoW images in a new primary
map and the 13 Armory plus one Blizzard image in a new supplement map.  All
source checks are offline and byte-based; this module has no export path.
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
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V28_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-primary-source-map.json"
V28_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v28/export-provenance.json"
V28_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v28/v28-build-receipt.json"
V29_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"
V29_PREPARATION = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-input-preparation.json"
V29_PREFLIGHT = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-preflight.json"
V29_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-build-receipt.json"
V29_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v29/export-provenance.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ARMORY_TOOL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-armory-origin-tool-acceptance.json"
V30_RECEIPTS = tuple(
    ROOT / f"research/continuous-recovery-20261018/publication/root-static38-batch{index}-public-copy-acceptance.json"
    for index in range(1, 5)
)
V30_PRIMARY_MAP = INTEGRATION / "v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = INTEGRATION / "v30-supplement-source-map.json"
V30_IMPACT = INTEGRATION / "v30-impact-estimate.json"
V30_SOURCE_AUDIT = INTEGRATION / "v30-source-byte-audit.json"
V30_PREPARATION = INTEGRATION / "v30-input-preparation.json"
V30_PREFLIGHT = INTEGRATION / "v30-preflight.json"
V30_PROPOSAL = INTEGRATION / "v30-input-proposal.md"
V30_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v30"
V30_BUILD_RECEIPT = INTEGRATION / "v30-build-receipt.json"
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
ROOT_V30_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v30-input-acceptance.json"
ANCHOR = "20080512210044"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V28_PRIMARY_MAP_SHA256 = "d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2"
EXPECTED_V28_PROVENANCE_SHA256 = "6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793"
EXPECTED_V28_RECEIPT_SHA256 = "2483e506f268ff43a022612e0b2c581cf753bab9935c530812c6da68cd227f3e"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V29_PREPARATION_SHA256 = "c54913a8ef64fa8c824af6290c493d44ebda73910ba526facd3fe37f775a29fe"
EXPECTED_V29_PREFLIGHT_SHA256 = "b29e1e7f69cf17391084d8fb0770008e1b850c9e9b2f92ad5900c65e68ab0194"
EXPECTED_V29_RECEIPT_SHA256 = "6eaf6aa2c212e94f87cc9f1bfea8f6a00940b81f48385c80ba210523f6ba13a4"
EXPECTED_V29_PROVENANCE_SHA256 = "793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_OLD_EXPORTER_SHA256 = "943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00"
EXPECTED_ACCEPTED_EXPORTER_SHA256 = "18f7239eb6af00a324be18f2e00192172fb2023856a39e02dd3c694a4bafe185"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_ARMORY_ACCEPTANCE_SHA256 = "863a141f1082ae76b17e7d5009e03959f066589ac39797483a530718036605cd"
EXPECTED_RECEIPT_SHAS = (
    "05bd0f2642ffc83ca5527431aea212d7d4aad87716cde7d295a540cdf3392e46",
    "a9464cf9e7009aee811653aff71b896f03227945db41f853b9b0feaeb2a3d7bf",
    "5e1919da82b0958941ff44d7e439da1a9a2e274e94bc0cbd3b4b8a989ca8c95a",
    "2c77349e49a60d9721ced254b8c64ede304fcc4bc6ac0990ede0f35d14ee896b",
)
EXPECTED_RECEIPT_COUNTS = (10, 5, 10, 8)
EXPECTED_NEW_IMAGES = 33
EXPECTED_PRIMARY_IMAGES = 19
EXPECTED_SUPPLEMENT_IMAGES = 14
EXPECTED_PRIMARY_BYTES = 70_546
EXPECTED_SUPPLEMENT_BYTES = 86_311
EXPECTED_NEW_BYTES = 156_857
EXPECTED_V29_PRIMARY = 228
EXPECTED_V29_SUPPLEMENT = 75
EXPECTED_V29_TOTAL = 303
EXPECTED_SOURCE_RECORDS = 8_357
EXPECTED_GUIDE_IMAGES = 39
EXPECTED_GUIDE_PREVIEWS = 22
EXPECTED_DECLARED_FILES = 8_794
EXPECTED_ACTUAL_FILES = 8_795

PRIMARY_HOST = "www.worldofwarcraft.com"
SUPPLEMENT_HOSTS = frozenset({"www.wowarmory.com", "armory.wow-europe.com", "www.blizzard.com"})
ARMORY_HOSTS = frozenset({"www.wowarmory.com", "armory.wow-europe.com"})


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


def load_frozen_v28():
    actual = sha256_file(V28_BUILDER)
    if actual != EXPECTED_V28_BUILDER_SHA256:
        raise RuntimeError(f"frozen v28 builder SHA changed: {actual} != {EXPECTED_V28_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_frozen_v28_builder_v30", V28_BUILDER)
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


def receipt_binding(receipt_path: Path, receipt: dict) -> dict:
    source = receipt.get("source_acceptance") or receipt.get("source_receipt")
    if isinstance(source, str):
        source_path = ROOT / source
        declared = None
    elif isinstance(source, dict) and source.get("path"):
        source_path = ROOT / str(source["path"])
        declared = str(source.get("sha256") or "").casefold()
    else:
        raise RuntimeError(f"{receipt_path.name} has no source receipt binding")
    source_path = inside(source_path, f"source receipt for {receipt_path.name}")
    actual = sha256_file(source_path)
    if declared and declared != actual:
        raise RuntimeError(f"{receipt_path.name} source receipt SHA mismatch: {declared} != {actual}")
    return {"path": rel(source_path), "sha256": actual}


def validate_public_receipt(frozen, receipt_path: Path, expected_count: int) -> tuple[dict, list[dict], dict]:
    receipt = read_json(receipt_path, receipt_path.name)
    if receipt.get("accepted") is not True or receipt.get("copy_mode") != "original_bytes":
        raise RuntimeError(f"{receipt_path.name} is not an accepted original-byte copy")
    raw_items = receipt.get("accepted_images")
    if not isinstance(raw_items, list) or len(raw_items) != expected_count:
        raise RuntimeError(f"{receipt_path.name} expected {expected_count} accepted images, got {len(raw_items or [])}")
    binding = receipt_binding(receipt_path, receipt)
    rows: list[dict] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict) or raw.get("accepted") is not True or raw.get("deployed") is not False:
            raise RuntimeError(f"{receipt_path.name}.accepted_images[{index}] is not accepted and undeployed")
        original = str(raw.get("original") or "")
        if not original or original in seen:
            raise RuntimeError(f"duplicate or missing original in {receipt_path.name}: {original!r}")
        seen.add(original)
        actual = str(raw.get("actual_capture_timestamp") or "")
        if not re.fullmatch(r"\d{14}", actual):
            raise RuntimeError(f"invalid capture timestamp for {original}: {actual!r}")
        datetime.strptime(actual, "%Y%m%d%H%M%S")
        source_rel = str(raw.get("local_path") or "")
        if not source_rel.startswith("research/continuous-recovery-20261018/publication/accepted-images/"):
            raise RuntimeError(f"non-public source path in {original}: {source_rel}")
        source = inside(ROOT / source_rel, f"public source {original}")
        if not source.is_file():
            raise RuntimeError(f"public source missing for {original}: {source}")
        data = source.read_bytes()
        expected_sha = str(raw.get("sha256") or "").casefold()
        expected_length = int(raw.get("length", -1))
        if len(data) != expected_length or hashlib.sha256(data).hexdigest() != expected_sha:
            raise RuntimeError(f"public source bytes differ from {receipt_path.name}: {original}")
        if cdx_digest(data) != str(raw.get("cdx_digest") or "").upper():
            raise RuntimeError(f"public source CDX differs from receipt: {original}")
        row = dict(raw)
        row["_destination"] = source
        row["_receipt_path"] = receipt_path
        row["_source_binding"] = binding
        rows.append(row)
    if int(receipt.get("image_bytes", -1)) != sum(int(row["length"]) for row in rows):
        raise RuntimeError(f"{receipt_path.name} image_bytes does not match accepted rows")
    return receipt, rows, binding


def validate_frozen_v29_closure(frozen) -> dict:
    checks = {
        "v28_builder": (V28_BUILDER, EXPECTED_V28_BUILDER_SHA256),
        "v28_primary_map": (V28_PRIMARY_MAP, EXPECTED_V28_PRIMARY_MAP_SHA256),
        "v28_provenance": (V28_PROVENANCE, EXPECTED_V28_PROVENANCE_SHA256),
        "v28_build_receipt": (V28_RECEIPT, EXPECTED_V28_RECEIPT_SHA256),
        "v29_primary_map": (V29_PRIMARY_MAP, EXPECTED_V29_PRIMARY_MAP_SHA256),
        "v29_preparation": (V29_PREPARATION, EXPECTED_V29_PREPARATION_SHA256),
        "v29_preflight": (V29_PREFLIGHT, EXPECTED_V29_PREFLIGHT_SHA256),
        "v29_build_receipt": (V29_RECEIPT, EXPECTED_V29_RECEIPT_SHA256),
        "v29_provenance": (V29_PROVENANCE, EXPECTED_V29_PROVENANCE_SHA256),
        "source_manifest": (SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "armory_tool_acceptance": (ARMORY_TOOL_ACCEPTANCE, EXPECTED_ARMORY_ACCEPTANCE_SHA256),
        "historical_exhibits": (ROOT / "tools/historical_exhibits.py", EXPECTED_HISTORICAL_EXHIBITS_SHA256),
    }
    results: dict[str, str] = {}
    for label, (path, expected) in checks.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen {label} SHA changed: {actual} != {expected}")
        results[label] = actual
    exporter_sha = sha256_file(ROOT / "tools/export_github_pages.py")
    if exporter_sha != EXPECTED_ACCEPTED_EXPORTER_SHA256:
        raise RuntimeError(f"accepted exporter SHA changed: {exporter_sha} != {EXPECTED_ACCEPTED_EXPORTER_SHA256}")
    results["exporter"] = exporter_sha

    armory_acceptance = read_json(ARMORY_TOOL_ACCEPTANCE, "root Armory tool acceptance")
    if armory_acceptance.get("accepted") is not True:
        raise RuntimeError("root Armory tool acceptance is not accepted")
    if armory_acceptance.get("prior_tool_sha256") != EXPECTED_OLD_EXPORTER_SHA256:
        raise RuntimeError("Armory supersession prior exporter SHA changed")
    if armory_acceptance.get("accepted_tool_sha256") != EXPECTED_ACCEPTED_EXPORTER_SHA256:
        raise RuntimeError("Armory supersession accepted exporter SHA changed")
    if armory_acceptance.get("primary_origins_unchanged") is not True:
        raise RuntimeError("Armory acceptance does not preserve primary origins")
    if set(armory_acceptance.get("added_supplement_origins") or []) != set(ARMORY_HOSTS):
        raise RuntimeError("Armory acceptance supplement host set changed")
    if armory_acceptance.get("production_export_executed") is not False:
        raise RuntimeError("Armory acceptance unexpectedly includes a production export")
    results["old_exporter_superseded"] = EXPECTED_OLD_EXPORTER_SHA256
    results["accepted_exporter"] = EXPECTED_ACCEPTED_EXPORTER_SHA256

    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    if manifest.get("anchor_timestamp") != ANCHOR:
        raise RuntimeError("source15 manifest anchor changed")

    v29_receipt = read_json(V29_RECEIPT, "v29 build receipt")
    if v29_receipt.get("export_completed") is not True or v29_receipt.get("published") is not False:
        raise RuntimeError("v29 build receipt is not the completed unpublished export")
    v29_stats = v29_receipt.get("build", {}).get("stats", {})
    expected_v29_overlay_stats = {
        "source_records": EXPECTED_SOURCE_RECORDS,
        "image_overlay_records": EXPECTED_V29_TOTAL,
        "primary_image_overlay_records": EXPECTED_V29_PRIMARY,
        "supplement_image_overlay_records": EXPECTED_V29_SUPPLEMENT,
    }
    for key, expected in expected_v29_overlay_stats.items():
        if v29_stats.get(key) != expected:
            raise RuntimeError(f"v29 receipt {key}={v29_stats.get(key)!r}, expected {expected}")
    if v29_receipt.get("build", {}).get("output_files") != 8_761:
        raise RuntimeError(f"v29 receipt output_files={v29_receipt.get('build', {}).get('output_files')!r}, expected 8761")
    v29_provenance = read_json(V29_PROVENANCE, "v29 output provenance")
    provenance_stats = v29_provenance.get("stats") or {}
    expected_v29_stats = expected_v29_overlay_stats | {"output_files": 8_761}
    for key, expected in expected_v29_stats.items():
        if provenance_stats.get(key) != expected:
            raise RuntimeError(f"v29 provenance {key}={provenance_stats.get(key)!r}, expected {expected}")

    frozen_maps: list[dict] = []
    for role, paths in (("primary", tuple(frozen.PRIMARY_MAPS)), ("supplement", tuple(frozen.SUPPLEMENT_MAPS))):
        for path in paths:
            payload = read_json(path, f"frozen {role} map {path.name}")
            items = payload.get("items")
            if not isinstance(items, list):
                raise RuntimeError(f"frozen map has no items: {path}")
            frozen_maps.append({"role": role, "path": rel(path), "sha256": sha256_file(path), "item_count": len(items)})
    frozen_maps.append({"role": "primary", "path": rel(V29_PRIMARY_MAP), "sha256": sha256_file(V29_PRIMARY_MAP), "item_count": len(read_json(V29_PRIMARY_MAP, V29_PRIMARY_MAP.name)["items"])})
    export_module = import_exporter()
    frozen_primary_routes, frozen_primary_paths = map_route_sets(tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP,), export_module)
    frozen_supplement_routes, frozen_supplement_paths = map_route_sets(tuple(frozen.SUPPLEMENT_MAPS), export_module)
    if len(frozen_primary_routes) != EXPECTED_V29_PRIMARY:
        raise RuntimeError(f"frozen unique primary route closure is {len(frozen_primary_routes)}, expected 228")
    if len(frozen_supplement_routes) != EXPECTED_V29_SUPPLEMENT:
        raise RuntimeError(f"frozen unique supplement route closure is {len(frozen_supplement_routes)}, expected 75")
    results["frozen_map_count"] = str(len(frozen_maps))
    results["frozen_unique_primary_routes"] = str(len(frozen_primary_routes))
    results["frozen_unique_primary_static_paths"] = str(len(frozen_primary_paths))
    results["frozen_unique_supplement_routes"] = str(len(frozen_supplement_routes))
    results["frozen_unique_supplement_static_paths"] = str(len(frozen_supplement_paths))
    return {
        "hashes": results,
        "frozen_maps": frozen_maps,
        "v28_primary_map": {"path": rel(V28_PRIMARY_MAP), "sha256": EXPECTED_V28_PRIMARY_MAP_SHA256, "items": 188},
        "v28_provenance": {"path": rel(V28_PROVENANCE), "sha256": EXPECTED_V28_PROVENANCE_SHA256, "stats": expected_v29_stats | {"image_overlay_records": 263, "primary_image_overlay_records": 188, "supplement_image_overlay_records": 75, "output_files": 8721}},
        "v29_primary_map": {"path": rel(V29_PRIMARY_MAP), "sha256": EXPECTED_V29_PRIMARY_MAP_SHA256, "items": 40, "bytes": 318622},
        "v29_provenance": {"path": rel(V29_PROVENANCE), "sha256": EXPECTED_V29_PROVENANCE_SHA256, "stats": expected_v29_stats},
        "source_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": EXPECTED_SOURCE_MANIFEST_SHA256, "source_records": EXPECTED_SOURCE_RECORDS, "anchor_timestamp": ANCHOR},
        "tool_supersession": {
            "prior_exporter_sha256": EXPECTED_OLD_EXPORTER_SHA256,
            "accepted_exporter_sha256": EXPECTED_ACCEPTED_EXPORTER_SHA256,
            "acceptance_path": rel(ARMORY_TOOL_ACCEPTANCE),
            "acceptance_sha256": EXPECTED_ARMORY_ACCEPTANCE_SHA256,
            "historical_exhibits_sha256": EXPECTED_HISTORICAL_EXHIBITS_SHA256,
        },
    }


def make_item(frozen, raw: dict, *, role: str, relationship: str) -> dict:
    return frozen.make_item(raw, role=role, relationship=relationship)


def collect_new_rows(frozen) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    all_rows: list[dict] = []
    bindings: list[dict] = []
    summaries: list[dict] = []
    for index, receipt_path in enumerate(V30_RECEIPTS):
        if sha256_file(receipt_path) != EXPECTED_RECEIPT_SHAS[index]:
            raise RuntimeError(f"static38 receipt SHA changed: {receipt_path.name}")
        receipt, rows, binding = validate_public_receipt(frozen, receipt_path, EXPECTED_RECEIPT_COUNTS[index])
        bindings.append(binding)
        primary_count = sum(host(str(row["original"])) == PRIMARY_HOST for row in rows)
        supplement_count = len(rows) - primary_count
        summaries.append({
            "path": rel(receipt_path),
            "sha256": sha256_file(receipt_path),
            "count": len(rows),
            "bytes": sum(int(row["length"]) for row in rows),
            "primary_count": primary_count,
            "supplement_count": supplement_count,
            "accepted": receipt.get("accepted") is True,
            "copy_mode": receipt.get("copy_mode"),
        })
        all_rows.extend(rows)
    if len(all_rows) != EXPECTED_NEW_IMAGES or sum(int(row["length"]) for row in all_rows) != EXPECTED_NEW_BYTES:
        raise RuntimeError("static38 accepted row count or bytes changed")
    primary_rows = [row for row in all_rows if host(str(row["original"])) == PRIMARY_HOST]
    supplement_rows = [row for row in all_rows if host(str(row["original"])) in SUPPLEMENT_HOSTS]
    if len(primary_rows) != EXPECTED_PRIMARY_IMAGES or len(supplement_rows) != EXPECTED_SUPPLEMENT_IMAGES:
        raise RuntimeError("static38 host classification changed")
    if sum(int(row["length"]) for row in primary_rows) != EXPECTED_PRIMARY_BYTES or sum(int(row["length"]) for row in supplement_rows) != EXPECTED_SUPPLEMENT_BYTES:
        raise RuntimeError("static38 primary/supplement byte split changed")
    if any(host(str(row["original"])) not in {PRIMARY_HOST, *SUPPLEMENT_HOSTS} for row in all_rows):
        raise RuntimeError("static38 contains an unapproved origin")
    return all_rows, primary_rows, supplement_rows, bindings, summaries


def unique_bindings(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for row in rows:
        binding = row["_source_binding"]
        if binding["path"] not in seen:
            seen.add(binding["path"])
            result.append(dict(binding))
    return result


def make_map(frozen, rows: list[dict], *, role: str, schema: str, kind: str, copy_rule: str, v29: dict) -> dict:
    items = [
        make_item(
            frozen,
            row,
            role=role,
            relationship=(
                "Root-accepted public-copy bytes; v30 primary overlay; no deployment implied."
                if role == "primary_image_overlay"
                else "Root-accepted public-copy bytes; v30 supplement overlay; exact accepted origin route; no deployment implied."
            ),
        )
        for row in rows
    ]
    receipt_paths = unique_bindings(rows)
    public_paths = sorted({rel(row["_receipt_path"]) for row in rows})
    return {
        "schema_version": schema,
        "kind": kind,
        "role": role,
        "accepted": False,
        "status": "prepared_waiting_root_v30_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": copy_rule,
        "relative_to_v29": {
            "new_items": len(items),
            "new_bytes": sum(int(item["length"]) for item in items),
            "v29_primary_map": {"path": rel(V29_PRIMARY_MAP), "sha256": EXPECTED_V29_PRIMARY_MAP_SHA256, "items": 40},
            "v29_provenance": {"path": rel(V29_PROVENANCE), "sha256": EXPECTED_V29_PROVENANCE_SHA256, "primary_overlays": EXPECTED_V29_PRIMARY, "supplement_overlays": EXPECTED_V29_SUPPLEMENT},
        },
        "source_acceptance": receipt_paths,
        "public_copy_acceptance": public_paths,
        "items": items,
    }


def validate_map(frozen, payload: dict, *, role: str, expected_count: int, expected_bytes: int) -> dict:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != expected_count:
        raise RuntimeError(f"{role} map expected {expected_count} items, got {len(items or [])}")
    seen: set[str] = set()
    total = 0
    actual_hosts: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or item.get("kind") != "image":
            raise RuntimeError(f"{role}[{index}] is not an image item")
        original = str(item.get("original") or item.get("logical_url") or "")
        if not original or original in seen:
            raise RuntimeError(f"{role}[{index}] duplicate or missing original")
        seen.add(original)
        logical = str(item.get("logical_url") or "")
        if canonical_url(logical) != canonical_url(original) or host(logical) != host(original):
            raise RuntimeError(f"{role}[{index}] logical/original origin mismatch")
        origin_host = host(original)
        actual_hosts.add(origin_host)
        if role == "primary_image_overlay" and origin_host != PRIMARY_HOST:
            raise RuntimeError(f"primary map contains non-primary host: {original}")
        if role == "supplement_image_overlay" and origin_host not in SUPPLEMENT_HOSTS:
            raise RuntimeError(f"supplement map contains unapproved host: {original}")
        local = str(item.get("local_path") or "")
        if not local.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local:
            raise RuntimeError(f"{role}[{index}] local_path is not a public copy: {local}")
        source = inside(ROOT / local, f"{role}[{index}] public source")
        if not source.is_file():
            raise RuntimeError(f"missing public source: {source}")
        data = source.read_bytes()
        if len(data) != int(item.get("length", -1)) or hashlib.sha256(data).hexdigest() != str(item.get("sha256") or "").casefold():
            raise RuntimeError(f"{role}[{index}] public source bytes differ")
        if cdx_digest(data) != str(item.get("cdx_digest") or "").upper():
            raise RuntimeError(f"{role}[{index}] public source CDX differs")
        actual = str(item.get("actual_timestamp") or "")
        if str(item.get("indexed_capture_timestamp") or "") != actual or str(item.get("temporal_class") or "") != temporal_class(actual):
            raise RuntimeError(f"{role}[{index}] capture metadata differs")
        total += len(data)
    if total != expected_bytes:
        raise RuntimeError(f"{role} map byte total changed: {total} != {expected_bytes}")
    return {"role": role, "items": len(items), "bytes": total, "hosts": sorted(actual_hosts)}


def map_route_sets(map_paths: tuple[Path, ...], export_module) -> tuple[set[str], set[str]]:
    routes: set[str] = set()
    static_paths: set[str] = set()
    for path in map_paths:
        payload = read_json(path, f"image map {path.name}")
        items = payload.get("items")
        if not isinstance(items, list):
            raise RuntimeError(f"image map has no items: {path}")
        for index, item in enumerate(items):
            logical = str(item.get("logical_url") or item.get("original") or "")
            if not logical:
                raise RuntimeError(f"image map item has no logical URL: {path}[{index}]")
            route = export_module.mirror.route_path(logical) if export_module.mirror.is_primary_origin(logical) else export_module.mirror.origin_route(logical)
            routes.add(route)
            static_paths.add(export_module.static_rel_for_route(route))
    return routes, static_paths


def loader_preflight(frozen, primary_map: dict, supplement_map: dict) -> dict:
    export_module = import_exporter()
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    records = {export_module.safe_route(str(item.get("route") or "")): item for item in manifest.get("files", []) if isinstance(item, dict)}
    frozen_routes = set(records) | {str(alias) for alias in (manifest.get("route_aliases") or {})}
    frozen_paths = {export_module.static_rel_for_route(route, item) for route, item in records.items()}
    old_primary_routes, old_primary_paths = map_route_sets(tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP,), export_module)
    old_supplement_routes, old_supplement_paths = map_route_sets(tuple(frozen.SUPPLEMENT_MAPS), export_module)
    frozen_routes |= old_primary_routes | old_supplement_routes
    frozen_paths |= old_primary_paths | old_supplement_paths
    primary, primary_bytes = export_module.load_image_overlays(
        (V30_PRIMARY_MAP,),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_paths,
    )
    expected_primary = {str(item["original"]) for item in primary_map["items"]}
    if {str(item["original_url"]) for item in primary} != expected_primary:
        raise RuntimeError("v30 primary loader did not load exactly the prepared originals")
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_paths = frozen_paths | {str(item["relative"]) for item in primary}
    supplement, supplement_bytes = export_module.load_supplement_image_overlays(
        (V30_SUPPLEMENT_MAP,),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_paths,
        allow_later_image_supplements=True,
    )
    expected_supplement = {str(item["original"]) for item in supplement_map["items"]}
    if {str(item["original_url"]) for item in supplement} != expected_supplement:
        raise RuntimeError("v30 supplement loader did not load exactly the prepared originals")
    collection = read_json(GUIDE_COLLECTION_MAP, "v26 guide collection map")
    groups = collection.get("groups") or []
    if len(groups) != 3 or sum(len(group.get("images") or []) for group in groups) != EXPECTED_GUIDE_IMAGES:
        raise RuntimeError("guide collection closure changed")
    return {
        "primary_overlay_records": EXPECTED_V29_PRIMARY + len(primary),
        "primary_overlay_bytes_checked_new": primary_bytes,
        "supplement_overlay_records": EXPECTED_V29_SUPPLEMENT + len(supplement),
        "supplement_overlay_bytes_checked_new": supplement_bytes,
        "total_overlay_records": EXPECTED_V29_TOTAL + len(primary) + len(supplement),
        "new_primary_records": len(primary),
        "new_supplement_records": len(supplement),
        "guide_collection_groups": len(groups),
        "guide_collection_images": sum(len(group.get("images") or []) for group in groups),
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }


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
            query = parse_qs(urlsplit(target).query)
            source = unquote(query.get("source", [""])[0]) or str(record.get("route") or "")
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
        parsed = urlsplit(original)
        route = export_module.mirror.route_path(original) if export_module.mirror.is_primary_origin(original) else export_module.mirror.origin_route(original)
        rows.append({
            "original": original,
            "role": str(item["overlay_role"]),
            "output_path": export_module.static_rel_for_route(route),
            "reference_count": len(found[original]),
            "references": found[original],
        })
    affected = sorted({ref["source_page"] for row in rows for ref in row["references"] if ref["source_page"]})
    return {
        "schema": "wow-recovery.integration.v30-impact-estimate.v1",
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
            "note": "Counts are manifest-reference estimates; they are not browser or post-export proof.",
        },
        "network_requests": 0,
        "export_executed": False,
    }


def build_source_audit(rows: list[dict]) -> dict:
    export_module = import_exporter()
    entries = []
    for row in rows:
        source = Path(row["_destination"])
        data = source.read_bytes()
        original = str(row["original"])
        route = export_module.mirror.route_path(original) if export_module.mirror.is_primary_origin(original) else export_module.mirror.origin_route(original)
        entries.append({
            "original": original,
            "host": host(original),
            "role": "primary" if host(original) == PRIMARY_HOST else "supplement",
            "actual_capture_timestamp": str(row["actual_capture_timestamp"]),
            "mime": str(row["mime"]),
            "dimensions": row.get("dimensions"),
            "public_copy_path": rel(source),
            "public_copy_acceptance_path": rel(row["_receipt_path"]),
            "source_acceptance_path": row["_source_binding"]["path"],
            "source_acceptance_sha256": row["_source_binding"]["sha256"],
            "declared_length": int(row["length"]),
            "actual_length": len(data),
            "declared_sha256": str(row["sha256"]).casefold(),
            "actual_sha256": hashlib.sha256(data).hexdigest(),
            "declared_cdx_digest": str(row["cdx_digest"]).upper(),
            "actual_cdx_digest": cdx_digest(data),
            "output_route": route,
            "output_path": export_module.static_rel_for_route(route),
            "byte_match": len(data) == int(row["length"]) and hashlib.sha256(data).hexdigest() == str(row["sha256"]).casefold() and cdx_digest(data) == str(row["cdx_digest"]).upper(),
        })
    if not all(entry["byte_match"] for entry in entries):
        raise RuntimeError("new source byte audit has a mismatch")
    return {
        "schema": "wow-recovery.integration.v30-source-byte-audit.v1",
        "status": "actual_public_copy_bytes_checked",
        "source_count": len(entries),
        "primary_count": sum(entry["role"] == "primary" for entry in entries),
        "supplement_count": sum(entry["role"] == "supplement" for entry in entries),
        "primary_bytes": sum(entry["actual_length"] for entry in entries if entry["role"] == "primary"),
        "supplement_bytes": sum(entry["actual_length"] for entry in entries if entry["role"] == "supplement"),
        "total_bytes": sum(entry["actual_length"] for entry in entries),
        "all_byte_match": True,
        "network_requests": 0,
        "entries": entries,
    }


def validate_no_overlap(frozen, primary_map: dict, supplement_map: dict) -> None:
    old_originals: set[str] = set()
    for path in tuple(frozen.PRIMARY_MAPS) + tuple(frozen.SUPPLEMENT_MAPS) + (V29_PRIMARY_MAP,):
        payload = read_json(path, f"frozen map {path.name}")
        old_originals.update(str(item.get("original") or item.get("logical_url") or "") for item in payload.get("items", []))
    new_originals = {str(item["original"]) for item in primary_map["items"] + supplement_map["items"]}
    if len(new_originals) != EXPECTED_NEW_IMAGES:
        raise RuntimeError("new v30 maps contain duplicate originals")
    overlap = old_originals & new_originals
    if overlap:
        raise RuntimeError(f"new v30 originals overlap frozen closure: {sorted(overlap)}")


def write_once(path: Path, payload: dict | str, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing {label}: {path}")
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
        parser.error("v30 preparation requires both --prepare and --preflight; export is execute_v30.py only")
    if V30_OUTPUT.exists() or V30_OUTPUT.with_name(V30_OUTPUT.name + ".partial").exists() or V30_BUILD_RECEIPT.exists():
        raise RuntimeError("refusing existing v30 output, partial output, or build receipt")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D: below floor before v30 preparation: {free_before}")
    frozen = load_frozen_v28()
    closure = validate_frozen_v29_closure(frozen)
    all_rows, primary_rows, supplement_rows, bindings, summaries = collect_new_rows(frozen)
    primary_map = make_map(
        frozen,
        primary_rows,
        role="primary_image_overlay",
        schema="wow-recovery.integration.v30.primary-source-map.v1",
        kind="wow_static_v30_primary_image_source_map",
        copy_rule="Only the nineteen root-accepted www.worldofwarcraft.com static38 public-copy images are added; publication copies remain original bytes and no news batch 49 items are included.",
        v29=closure,
    )
    supplement_map = make_map(
        frozen,
        supplement_rows,
        role="supplement_image_overlay",
        schema="wow-recovery.integration.v30.supplement-source-map.v1",
        kind="wow_static_v30_supplement_image_source_map",
        copy_rule="Only thirteen exact Armory /images/icons/ supplements and one exact www.blizzard.com accepted image are added; the current exporter 18f supersession is required, no primary host expansion occurs, and no news batch 49 items are included.",
        v29=closure,
    )
    validate_no_overlap(frozen, primary_map, supplement_map)
    primary_check = validate_map(frozen, primary_map, role="primary_image_overlay", expected_count=EXPECTED_PRIMARY_IMAGES, expected_bytes=EXPECTED_PRIMARY_BYTES)
    supplement_check = validate_map(frozen, supplement_map, role="supplement_image_overlay", expected_count=EXPECTED_SUPPLEMENT_IMAGES, expected_bytes=EXPECTED_SUPPLEMENT_BYTES)
    impact = build_impact(primary_map["items"] + supplement_map["items"])
    source_audit = build_source_audit(all_rows)

    write_once(V30_PRIMARY_MAP, primary_map, "v30 primary map")
    write_once(V30_SUPPLEMENT_MAP, supplement_map, "v30 supplement map")
    loader = loader_preflight(frozen, primary_map, supplement_map)
    checked_utc = datetime.utcnow().isoformat() + "Z"
    prep = {
        "schema": "wow-recovery.integration.v30-input-preparation.v1",
        "status": "prepared_waiting_root_v30_input_acceptance",
        "checked_utc": checked_utc,
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "frozen_v29_closure": closure,
        "static38_receipts": {"receipts": summaries, "bindings": bindings, "accepted_count": len(all_rows), "accepted_bytes": sum(int(row["length"]) for row in all_rows)},
        "new_maps": {
            "primary": {"path": rel(V30_PRIMARY_MAP), "sha256": sha256_file(V30_PRIMARY_MAP), "items": EXPECTED_PRIMARY_IMAGES, "bytes": EXPECTED_PRIMARY_BYTES},
            "supplement": {"path": rel(V30_SUPPLEMENT_MAP), "sha256": sha256_file(V30_SUPPLEMENT_MAP), "items": EXPECTED_SUPPLEMENT_IMAGES, "bytes": EXPECTED_SUPPLEMENT_BYTES},
        },
        "impact": {"path": rel(V30_IMPACT), "sha256": None, "new_image_count": EXPECTED_NEW_IMAGES},
        "source_byte_audit": {"path": rel(V30_SOURCE_AUDIT), "sha256": None, "items": EXPECTED_NEW_IMAGES, "bytes": EXPECTED_NEW_BYTES},
        "relative_to_v29": {"primary_overlays": EXPECTED_V29_PRIMARY, "supplement_overlays": EXPECTED_V29_SUPPLEMENT, "total_overlays": EXPECTED_V29_TOTAL, "new_primary": EXPECTED_PRIMARY_IMAGES, "new_supplement": EXPECTED_SUPPLEMENT_IMAGES, "new_total": EXPECTED_NEW_IMAGES, "new_bytes": EXPECTED_NEW_BYTES},
        "expected_after_export": {"source_records": EXPECTED_SOURCE_RECORDS, "declared_files": EXPECTED_DECLARED_FILES, "actual_files": EXPECTED_ACTUAL_FILES, "primary_overlays": EXPECTED_V29_PRIMARY + EXPECTED_PRIMARY_IMAGES, "supplement_overlays": EXPECTED_V29_SUPPLEMENT + EXPECTED_SUPPLEMENT_IMAGES, "total_overlays": EXPECTED_V29_TOTAL + EXPECTED_NEW_IMAGES, "guide_previews": EXPECTED_GUIDE_PREVIEWS, "guide_collection_images": EXPECTED_GUIDE_IMAGES},
        "network_requests": 0,
        "export_executed": False,
        "root_input_acceptance_required": True,
        "output": rel(V30_OUTPUT),
        "disk_free_before_bytes": free_before,
    }
    preflight = {
        "schema": "wow-recovery.integration.v30-preflight.v1",
        "status": "preflight_passed_waiting_root_v30_input_acceptance",
        "checked_utc": checked_utc,
        "builder": prep["builder"],
        "frozen_v29_closure": closure,
        "static38_receipts": prep["static38_receipts"],
        "new_maps": prep["new_maps"],
        "impact": {"path": rel(V30_IMPACT), "sha256": sha256_file(V30_IMPACT) if V30_IMPACT.exists() else None},
        "source_byte_audit": {"path": rel(V30_SOURCE_AUDIT), "sha256": sha256_file(V30_SOURCE_AUDIT) if V30_SOURCE_AUDIT.exists() else None},
        "map_validation": {"primary": primary_check, "supplement": supplement_check},
        "loader_preflight": loader,
        "expected_after_export": prep["expected_after_export"],
        "network_requests": 0,
        "export_executed": False,
        "root_input_acceptance_required": True,
        "old_image_payloads_rehashed": False,
        "disk_free_bytes": shutil.disk_usage(ROOT).free,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    # The two audit inputs must be durable before their SHA fields are pinned.
    write_once(V30_IMPACT, impact, "v30 impact estimate")
    write_once(V30_SOURCE_AUDIT, source_audit, "v30 source byte audit")
    prep["impact"]["sha256"] = sha256_file(V30_IMPACT)
    prep["source_byte_audit"]["sha256"] = sha256_file(V30_SOURCE_AUDIT)
    preflight["impact"]["sha256"] = prep["impact"]["sha256"]
    preflight["source_byte_audit"]["sha256"] = prep["source_byte_audit"]["sha256"]
    proposal = f"""# v30 input proposal

v30 extends the completed v29 closure with four root-accepted static38 public-copy receipts. The new set contains {EXPECTED_PRIMARY_IMAGES} primary `www.worldofwarcraft.com` images ({EXPECTED_PRIMARY_BYTES} bytes) and {EXPECTED_SUPPLEMENT_IMAGES} explicit supplements ({EXPECTED_SUPPLEMENT_BYTES} bytes): thirteen exact Armory `/images/icons/` PNGs and one exact `www.blizzard.com` image. The combined new set is {EXPECTED_NEW_IMAGES} images and {EXPECTED_NEW_BYTES} bytes.

Relative to v29, the expected closure is {EXPECTED_V29_PRIMARY + EXPECTED_PRIMARY_IMAGES} primary overlays, {EXPECTED_V29_SUPPLEMENT + EXPECTED_SUPPLEMENT_IMAGES} supplement overlays, and {EXPECTED_V29_TOTAL + EXPECTED_NEW_IMAGES} total overlays. The planning counts are {EXPECTED_DECLARED_FILES} declared files / {EXPECTED_ACTUAL_FILES} actual files, source records {EXPECTED_SOURCE_RECORDS}, guide collection images {EXPECTED_GUIDE_IMAGES}, and guide previews {EXPECTED_GUIDE_PREVIEWS}. These are preflight expectations only; no v30 export was executed.

The v28 builder map constants and v29 primary map remain referenced by immutable paths. The v28 builder SHA is `{EXPECTED_V28_BUILDER_SHA256}`, v28 primary map `{EXPECTED_V28_PRIMARY_MAP_SHA256}`, v28 provenance `{EXPECTED_V28_PROVENANCE_SHA256}`, v29 primary map `{EXPECTED_V29_PRIMARY_MAP_SHA256}`, v29 provenance `{EXPECTED_V29_PROVENANCE_SHA256}`, source manifest `{EXPECTED_SOURCE_MANIFEST_SHA256}`, and historical exhibits `{EXPECTED_HISTORICAL_EXHIBITS_SHA256}`. The root Armory acceptance records exporter supersession `{EXPECTED_OLD_EXPORTER_SHA256}` -> `{EXPECTED_ACCEPTED_EXPORTER_SHA256}`; v30 requires the accepted exporter and leaves primary origins unchanged.

The future `execute_v30.py` wrapper is export-only and requires a root accepted input receipt with every prepared SHA binding, an explicit `root_export_go`/`export_go` flag, the v30 output and receipt absent, and the disk floor available. It does not reprepare maps or invoke the v28/v29 main functions. The pending news-remaining-v28 queue and all batch49 news are excluded.
"""
    prep["impact"]["sha256"] = sha256_file(V30_IMPACT)
    prep["source_byte_audit"]["sha256"] = sha256_file(V30_SOURCE_AUDIT)
    preflight["impact"]["sha256"] = prep["impact"]["sha256"]
    preflight["source_byte_audit"]["sha256"] = prep["source_byte_audit"]["sha256"]
    write_once(V30_PREPARATION, prep, "v30 input preparation")
    write_once(V30_PREFLIGHT, preflight, "v30 preflight")
    write_once(V30_PROPOSAL, proposal, "v30 proposal")
    print(json.dumps({
        "status": "preflight_passed_waiting_root_v30_input_acceptance",
        "primary_map": rel(V30_PRIMARY_MAP),
        "primary_map_sha256": sha256_file(V30_PRIMARY_MAP),
        "supplement_map": rel(V30_SUPPLEMENT_MAP),
        "supplement_map_sha256": sha256_file(V30_SUPPLEMENT_MAP),
        "impact_sha256": sha256_file(V30_IMPACT),
        "source_byte_audit_sha256": sha256_file(V30_SOURCE_AUDIT),
        "preparation_sha256": sha256_file(V30_PREPARATION),
        "preflight_sha256": sha256_file(V30_PREFLIGHT),
        "proposal_sha256": sha256_file(V30_PROPOSAL),
        "primary_items": EXPECTED_PRIMARY_IMAGES,
        "supplement_items": EXPECTED_SUPPLEMENT_IMAGES,
        "new_bytes": EXPECTED_NEW_BYTES,
        "loader": loader,
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
