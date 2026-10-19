#!/usr/bin/env python3
"""Prepare the v35 contest-fix plus 24 accepted news-image delta.

This script is preparation-only.  It reads only the two root-accepted
source/public-copy receipt pairs, validates their public bytes, writes new
v35 maps and a real exporter-loader preflight, and never calls export_pages.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
INTEGRATION = Path(__file__).resolve().parent
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ORIGINAL_MANIFEST = ROOT / "offline/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"
V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V29_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"
V30_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-supplement-source-map.json"
V32_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-primary-source-map.json"
V32_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-supplement-source-map.json"
V33_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-primary-source-map.json"
V33_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v33/v33-supplement-source-map.json"
V34_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261019/integration/v34/v34-primary-source-map.json"
V34_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261019/integration/v34/v34-supplement-source-map.json"
V34_PREPARATION = ROOT / "research/continuous-recovery-20261019/integration/v34/v34-input-preparation.json"
V34_PREFLIGHT = ROOT / "research/continuous-recovery-20261019/integration/v34/v34-preflight.json"
V34_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261019/integration/v34/v34-build-receipt-retry1.json"
V34_PROVENANCE = ROOT / ".scratch/pages-resources-20261019-v34/export-provenance.json"
V34_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-v34-input-acceptance-retry1.json"
V34_R2_REPORT = ROOT / "research/continuous-recovery-20261019/integration/v34/browser/v33-v34-three-pages-r2.json"
V34_R3B_REPORT = ROOT / "research/continuous-recovery-20261019/integration/v34/browser/v34-winners-navigation-r3b.json"
CONTEST_TOOL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261019/publication/root-contest-nav-tool-acceptance.json"
EXPORTER = ROOT / "tools/export_github_pages.py"
HISTORICAL_EXHIBITS = ROOT / "tools/historical_exhibits.py"
NATIVE_INPUT = INTEGRATION / "v35-native-ui-inputs.json"
PRIMARY_MAP = INTEGRATION / "v35-primary-source-map.json"
SUPPLEMENT_MAP = INTEGRATION / "v35-supplement-source-map.json"
SOURCE_CLOSURE = INTEGRATION / "v35-source-closure.json"
PREPARATION = INTEGRATION / "v35-input-preparation.json"
PREFLIGHT = INTEGRATION / "v35-preflight.json"
PROPOSAL = INTEGRATION / "v35-input-proposal.md"
RUNNER_NOTE = INTEGRATION / "v35-runner-preparation.md"
RUNNER = INTEGRATION / "execute_v35.py"

NEWS_BATCHES = (
    {
        "id": "frontier-news04",
        "role": "primary",
        "source": ROOT / "research/continuous-recovery-20261019/publication/root-frontier-news04-source-acceptance.json",
        "public": ROOT / "research/continuous-recovery-20261019/publication/root-frontier-news04-public-copy-acceptance.json",
        "expected_count": 4,
        "expected_bytes": 41536,
        "source_sha256": "2289c58b2b45f18b09a9eeea4480f1115acdd6a56ce01e0fd07f97f6f8742b5b",
        "public_sha256": "cad32cc0f7255b4489359672f82a4d512411c6e839f0b2f7a0ed69ebcdf4a685",
    },
    {
        "id": "frontier-news20a",
        "role": "primary",
        "source": ROOT / "research/continuous-recovery-20261019/publication/root-frontier-news20a-source-acceptance.json",
        "public": ROOT / "research/continuous-recovery-20261019/publication/root-frontier-news20a-public-copy-acceptance.json",
        "expected_count": 20,
        "expected_bytes": 150407,
        "source_sha256": "20699851c0be427849acbdb2d7ef030e1f6bbcd10664d4289382082b059edb88",
        "public_sha256": "2a539aeb72b29e665b7eeb5f07f5bb14e8b11d222c1addc6dd20bba78d2ad0b5",
    },
)

ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_ORIGINAL_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_EXPORTER_SHA256 = "e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_V34_PROVENANCE_SHA256 = "3946f504260aec576087207399ad692eef9f7fac938fac439474a2c540d85447"
EXPECTED_V34_RECEIPT_SHA256 = "00c28092e683d106cbeb8baad54f7660f2eb259a0f215b3938561e466d4a84f2"
EXPECTED_V34_INPUT_ACCEPTANCE_SHA256 = "8d5d0ef5c0b30a912f5bc7d3d12e5437d97a09598fd5a4760a5f770fa1d437c0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def binding(path: Path, expected: str | None = None) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing binding: {path}")
    actual = sha256_file(path)
    if expected is not None and actual.casefold() != expected.casefold():
        raise RuntimeError(f"binding SHA mismatch for {rel(path)}: {actual} != {expected}")
    return {"path": rel(path), "sha256": actual}


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_once(path: Path, payload: object, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing existing {label}: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = payload if isinstance(payload, bytes) else payload.encode("utf-8") if isinstance(payload, str) else json_bytes(payload)
    path.write_bytes(data)


def load_exporter():
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("wow_recovery_v35_exporter", EXPORTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load current exporter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_v28_builder():
    spec = importlib.util.spec_from_file_location("wow_recovery_v35_v28", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def closure_maps() -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    frozen = load_v28_builder()
    primary = tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP, V30_PRIMARY_MAP, V32_PRIMARY_MAP, V33_PRIMARY_MAP, V34_PRIMARY_MAP)
    supplement = tuple(frozen.SUPPLEMENT_MAPS) + (V30_SUPPLEMENT_MAP, V32_SUPPLEMENT_MAP, V33_SUPPLEMENT_MAP, V34_SUPPLEMENT_MAP)
    return primary, supplement


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def receipt_rows(batch: dict) -> tuple[list[dict], dict, dict]:
    source_path = batch["source"]
    public_path = batch["public"]
    source_binding = binding(source_path, batch["source_sha256"])
    public_binding = binding(public_path, batch["public_sha256"])
    source = read_json(source_path, f"{batch['id']} source receipt")
    public = read_json(public_path, f"{batch['id']} public copy receipt")
    if source.get("accepted") is not True:
        raise RuntimeError(f"{batch['id']} source receipt is not accepted")
    if public.get("accepted") is not True or public.get("copy_mode") != "original_bytes":
        raise RuntimeError(f"{batch['id']} public copy is not accepted original bytes")
    source_ref = public.get("source_acceptance") or public.get("source_receipt")
    if not isinstance(source_ref, dict) or source_ref.get("path") != rel(source_path) or str(source_ref.get("sha256")).casefold() != source_binding["sha256"]:
        raise RuntimeError(f"{batch['id']} public receipt source binding differs")
    source_rows = {str(row.get("original")): row for row in source.get("accepted_images", []) if isinstance(row, dict)}
    public_rows = public.get("accepted_images")
    if not isinstance(public_rows, list) or len(public_rows) != batch["expected_count"]:
        raise RuntimeError(f"{batch['id']} count differs")
    rows: list[dict] = []
    seen: set[str] = set()
    for index, public_row in enumerate(public_rows):
        original = str(public_row.get("original") or "")
        if not original or original in seen:
            raise RuntimeError(f"{batch['id']} duplicate/missing original at {index}")
        seen.add(original)
        source_row = source_rows.get(original)
        if source_row is None or source_row.get("accepted") is not True:
            raise RuntimeError(f"{batch['id']} source row missing: {original}")
        for key in ("actual_capture_timestamp", "mime", "dimensions", "decoded_frames", "length", "sha256", "cdx_digest"):
            if source_row.get(key) != public_row.get(key):
                raise RuntimeError(f"{batch['id']} metadata differs for {original}: {key}")
        local_path = str(public_row.get("local_path") or "")
        if not local_path.startswith("research/continuous-recovery-20261019/publication/accepted-images/") or "private-payloads" in local_path:
            raise RuntimeError(f"{batch['id']} local path is not public accepted copy: {local_path}")
        local_file = ROOT / local_path
        if not local_file.is_file():
            raise RuntimeError(f"{batch['id']} public image missing: {local_file}")
        data = local_file.read_bytes()
        if len(data) != int(public_row.get("length", -1)) or sha256_bytes(data) != str(public_row.get("sha256") or "").casefold():
            raise RuntimeError(f"{batch['id']} bytes differ for {original}")
        if cdx_digest(data) != str(public_row.get("cdx_digest") or "").upper():
            raise RuntimeError(f"{batch['id']} CDX differs for {original}")
        parsed = urlsplit(original)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != "www.worldofwarcraft.com" or parsed.query or parsed.fragment or parsed.username is not None or parsed.password is not None:
            raise RuntimeError(f"{batch['id']} primary URL is not exact canonical host: {original}")
        actual = str(public_row.get("actual_capture_timestamp") or "")
        if len(actual) != 14 or not actual.isdigit() or not actual.startswith("2008") or actual > ANCHOR:
            raise RuntimeError(f"{batch['id']} capture outside primary baseline: {actual}")
        rows.append({**public_row, "_source_path": source_path, "_public_path": public_path, "_source_binding": source_binding, "_public_binding": public_binding, "_destination": local_file})
    total = sum(int(row["length"]) for row in rows)
    if total != batch["expected_bytes"] or int(public.get("image_bytes", -1)) != total:
        raise RuntimeError(f"{batch['id']} byte total differs: {total}")
    return rows, source_binding, public_binding


def make_item(row: dict) -> dict:
    actual = str(row["actual_capture_timestamp"])
    return {
        "kind": "image",
        "logical_url": str(row["original"]),
        "original": str(row["original"]),
        "actual_timestamp": actual,
        "indexed_capture_timestamp": actual,
        "mime": str(row["mime"]),
        "dimensions": row.get("dimensions"),
        "decoded_frames": row.get("decoded_frames"),
        "length": int(row["length"]),
        "sha256": str(row["sha256"]).casefold(),
        "cdx_digest": str(row["cdx_digest"]).upper(),
        "local_path": rel(row["_destination"]),
        "temporal_class": "baseline_2008",
        "source_acceptance_path": rel(row["_source_path"]),
        "public_copy_acceptance_path": rel(row["_public_path"]),
        "public_copy_path": str(row["local_path"]),
        "source_relationship": "Root-accepted source/public-copy original bytes; v35 news delta overlay; no deployment implied.",
        "overlay_role": "primary_image_overlay",
    }


def route_sets(paths: tuple[Path, ...], exporter) -> tuple[set[str], set[str]]:
    routes: set[str] = set()
    static_paths: set[str] = set()
    for path in paths:
        payload = read_json(path, path.name)
        for index, item in enumerate(payload.get("items") or []):
            logical = str(item.get("logical_url") or item.get("original") or "")
            if not logical:
                raise RuntimeError(f"map item missing logical URL: {path}[{index}]")
            route = exporter.mirror.route_path(logical) if exporter.mirror.is_primary_origin(logical) else exporter.mirror.origin_route(logical)
            routes.add(route)
            static_paths.add(exporter.static_rel_for_route(route))
    return routes, static_paths


def source_bindings(paths: tuple[Path, ...]) -> list[dict]:
    return [binding(path) for path in paths]


def extract_native(items: list[dict]) -> dict:
    sys.path.insert(0, str(INTEGRATION)) if str(INTEGRATION) not in sys.path else None
    spec = importlib.util.spec_from_file_location("wow_recovery_v35_native", INTEGRATION / "extract_v35_native_inputs.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load native input extractor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.extract_items(items)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    if not (args.prepare and args.preflight):
        parser.error("v35 preparation requires both --prepare and --preflight; export is execute_v35.py only")
    for path, label in ((PRIMARY_MAP, "v35 primary map"), (SUPPLEMENT_MAP, "v35 supplement map"), (SOURCE_CLOSURE, "v35 source closure"), (NATIVE_INPUT, "v35 native input"), (PREPARATION, "v35 preparation"), (PREFLIGHT, "v35 preflight"), (PROPOSAL, "v35 proposal"), (RUNNER_NOTE, "v35 runner note")):
        if path.exists():
            raise RuntimeError(f"refusing existing {label}: {path}")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v35 preparation floor: {free_before}")
    if not SOURCE_SITE.is_dir():
        raise RuntimeError(f"missing frozen Source15 site: {SOURCE_SITE}")
    source15 = binding(SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256)
    original_manifest = binding(ORIGINAL_MANIFEST, EXPECTED_ORIGINAL_MANIFEST_SHA256)
    if sha256_file(EXPORTER) != EXPECTED_EXPORTER_SHA256 or sha256_file(HISTORICAL_EXHIBITS) != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError("current tool SHA differs from accepted v34 tool pins")
    exporter = load_exporter()
    old_primary, old_supplement = closure_maps()
    old_primary_routes, old_primary_paths = route_sets(old_primary, exporter)
    old_supplement_routes, old_supplement_paths = route_sets(old_supplement, exporter)
    old_items = [item for path in old_primary + old_supplement for item in (read_json(path, path.name).get("items") or [])]
    old_origin_keys = {exporter.mirror.origin_key(str(item.get("original") or item.get("logical_url") or "")) for item in old_items}
    all_rows: list[dict] = []
    batch_meta: list[dict] = []
    for batch in NEWS_BATCHES:
        rows, source_binding, public_binding = receipt_rows(batch)
        all_rows.extend(rows)
        batch_meta.append({"id": batch["id"], "role": batch["role"], "source_acceptance": source_binding, "public_copy_acceptance": public_binding, "count": len(rows), "bytes": sum(int(row["length"]) for row in rows)})
    new_items = [make_item(row) for row in all_rows]
    new_origin_keys = {exporter.mirror.origin_key(str(item["original"])) for item in new_items}
    if len(new_origin_keys) != len(new_items) or old_origin_keys & new_origin_keys:
        raise RuntimeError("v35 news originals duplicate frozen closure or each other")
    for item in new_items:
        route = exporter.mirror.route_path(str(item["logical_url"]))
        if route in old_primary_routes | old_supplement_routes or route.startswith("/__offline/"):
            raise RuntimeError(f"v35 route collides with frozen closure: {route}")
    primary_payload = {
        "schema_version": "wow-recovery.integration.v35.primary-source-map.v1",
        "kind": "wow_static_v35_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v35_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only the two root-accepted frontier news source/public-copy receipts are added; v34 maps and bytes remain unchanged.",
        "relative_to_v34": {"new_items": len(new_items), "new_bytes": sum(int(item["length"]) for item in new_items), "frozen_primary_overlays": len(old_primary_routes), "frozen_supplement_overlays": len(old_supplement_routes), "v34_primary_map": binding(V34_PRIMARY_MAP), "v34_supplement_map": binding(V34_SUPPLEMENT_MAP), "v34_provenance": binding(V34_PROVENANCE, EXPECTED_V34_PROVENANCE_SHA256)},
        "source_acceptance": [{"path": row["source_acceptance"]["path"], "sha256": row["source_acceptance"]["sha256"]} for row in batch_meta],
        "public_copy_acceptance": [{"path": row["public_copy_acceptance"]["path"], "sha256": row["public_copy_acceptance"]["sha256"]} for row in batch_meta],
        "items": new_items,
    }
    supplement_payload = {
        "schema_version": "wow-recovery.integration.v35.supplement-source-map.v1",
        "kind": "wow_static_v35_supplement_image_source_map",
        "role": "supplement_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v35_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "No new supplement rows; the v34 supplement closure remains unchanged.",
        "relative_to_v34": {"new_items": 0, "new_bytes": 0, "frozen_primary_overlays": len(old_primary_routes), "frozen_supplement_overlays": len(old_supplement_routes), "v34_primary_map": binding(V34_PRIMARY_MAP), "v34_supplement_map": binding(V34_SUPPLEMENT_MAP), "v34_provenance": binding(V34_PROVENANCE, EXPECTED_V34_PROVENANCE_SHA256)},
        "items": [],
    }
    primary_bytes = json_bytes(primary_payload)
    supplement_bytes = json_bytes(supplement_payload)
    write_once(PRIMARY_MAP, primary_bytes, "v35 primary map")
    write_once(SUPPLEMENT_MAP, supplement_bytes, "v35 supplement map")
    native_payload = extract_native(new_items)
    native_bytes = json_bytes(native_payload)
    write_once(NATIVE_INPUT, native_bytes, "v35 native input")
    # The frozen v34 maps are already an accepted closure.  Validate them
    # against an empty collision baseline, then validate only the new delta
    # against the frozen routes/static paths.  Passing the whole closure and
    # its own routes as ``frozen_*`` makes the loader reject its first legacy
    # row as an apparent override.
    frozen_routes = old_primary_routes | old_supplement_routes
    frozen_static_paths = old_primary_paths | old_supplement_paths
    old_primary_loader, old_primary_bytes_checked = exporter.load_image_overlays(
        old_primary,
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=set(),
        frozen_static_paths=set(),
    )
    new_primary_loader, new_primary_bytes_checked = exporter.load_image_overlays(
        (PRIMARY_MAP,),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_static_paths,
    )
    old_supplement_loader, old_supplement_bytes_checked = exporter.load_supplement_image_overlays(
        old_supplement,
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=set(),
        frozen_static_paths=set(),
        # The accepted v34 supplement closure intentionally contains later
        # historical captures (for example 2010).  Revalidate that closure
        # with the same compatibility policy used by the v34 runner.
        allow_later_image_supplements=True,
    )
    new_supplement_loader, new_supplement_bytes_checked = exporter.load_supplement_image_overlays(
        (SUPPLEMENT_MAP,),
        workspace_root=ROOT,
        anchor_timestamp=ANCHOR,
        frozen_routes=frozen_routes,
        frozen_static_paths=frozen_static_paths,
        allow_later_image_supplements=False,
    )
    if len(old_primary_loader) != len(old_primary_routes) or len(new_primary_loader) != len(new_items) or len(old_supplement_loader) != len(old_supplement_routes) or len(new_supplement_loader) != 0:
        raise RuntimeError(
            "v35 loader counts differ: "
            f"old-primary={len(old_primary_loader)}/{len(old_primary_routes)}, "
            f"new-primary={len(new_primary_loader)}/{len(new_items)}, "
            f"old-supplement={len(old_supplement_loader)}/{len(old_supplement_routes)}, "
            f"new-supplement={len(new_supplement_loader)}/0"
        )
    primary_loader = old_primary_loader + new_primary_loader
    supplement_loader = old_supplement_loader + new_supplement_loader
    primary_bytes_checked = old_primary_bytes_checked + new_primary_bytes_checked
    supplement_bytes_checked = old_supplement_bytes_checked + new_supplement_bytes_checked
    v34_stats = read_json(V34_PROVENANCE, "v34 provenance").get("stats") or {}
    if int(v34_stats.get("source_records", 0)) != 8357 or int(v34_stats.get("guide_image_collection_images", 0)) != 39 or int(v34_stats.get("guide_preview_count", 0)) != 22:
        raise RuntimeError("v34 baseline stats changed")
    closure_payload = {
        "schema": "wow-recovery.integration.v35-source-closure.v1",
        "status": "frozen_v34_closure_verified_with_root_accepted_news_delta",
        "source15_manifest": source15,
        "original_manifest": original_manifest,
        "v34_preparation": binding(V34_PREPARATION),
        "v34_preflight": binding(V34_PREFLIGHT),
        "v34_build_receipt": binding(V34_BUILD_RECEIPT, EXPECTED_V34_RECEIPT_SHA256),
        "v34_input_acceptance": binding(V34_INPUT_ACCEPTANCE, EXPECTED_V34_INPUT_ACCEPTANCE_SHA256),
        "v34_provenance": binding(V34_PROVENANCE, EXPECTED_V34_PROVENANCE_SHA256),
        "v34_browser_r2": binding(V34_R2_REPORT),
        "v34_winners_navigation_r3b": binding(V34_R3B_REPORT),
        "contest_tool_acceptance": binding(CONTEST_TOOL_ACCEPTANCE),
        "primary_maps": source_bindings(old_primary),
        "supplement_maps": source_bindings(old_supplement),
        "news_batches": batch_meta,
        "counts": {"source_records": 8357, "frozen_primary_overlays": len(old_primary_routes), "frozen_supplement_overlays": len(old_supplement_routes), "new_primary_overlays": len(new_items), "primary_overlays": len(primary_loader), "supplement_overlays": len(supplement_loader), "total_overlays": len(primary_loader) + len(supplement_loader), "guide_images": 39, "guide_previews": 22},
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
    }
    closure_bytes = json_bytes(closure_payload)
    write_once(SOURCE_CLOSURE, closure_bytes, "v35 source closure")
    prep = {
        "schema": "wow-recovery.integration.v35-input-preparation.v1",
        "status": "prepared_waiting_root_v35_input_acceptance",
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "runner": binding(RUNNER),
        "source_closure": binding(SOURCE_CLOSURE, sha256_bytes(closure_bytes)),
        "new_source_batches": batch_meta,
        "new_maps": {"primary": {"path": rel(PRIMARY_MAP), "sha256": sha256_bytes(primary_bytes), "items": len(new_items), "bytes": sum(int(item["length"]) for item in new_items)}, "supplement": {"path": rel(SUPPLEMENT_MAP), "sha256": sha256_bytes(supplement_bytes), "items": 0, "bytes": 0}},
        "native_ui_input": binding(NATIVE_INPUT, sha256_bytes(native_bytes)),
        "frozen_v34": {"primary_overlays": len(old_primary_routes), "supplement_overlays": len(old_supplement_routes), "total_overlays": len(old_primary_routes) + len(old_supplement_routes), "maps": source_bindings(old_primary + old_supplement), "provenance": binding(V34_PROVENANCE, EXPECTED_V34_PROVENANCE_SHA256)},
        "guide_maps": {"preview": binding(GUIDE_PREVIEW_MAP), "collection": binding(GUIDE_COLLECTION_MAP)},
        "tool_bindings": {"exporter": binding(EXPORTER, EXPECTED_EXPORTER_SHA256), "historical_exhibits": binding(HISTORICAL_EXHIBITS, EXPECTED_HISTORICAL_EXHIBITS_SHA256), "contest_tool_acceptance": binding(CONTEST_TOOL_ACCEPTANCE)},
        "expected_after_export": {"source_records": 8357, "primary_overlays": len(primary_loader), "supplement_overlays": len(supplement_loader), "total_overlays": len(primary_loader) + len(supplement_loader), "declared_files": 9041, "actual_files": 9042, "guide_images": 39, "guide_previews": 22, "runtime_allowed_changes": {"contest_navtree_fallback_repaired": 1, "new_primary_image_overlays": len(new_items)}},
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    preflight = {
        "schema": "wow-recovery.integration.v35-preflight.v1",
        "status": "preflight_passed_waiting_root_v35_input_acceptance",
        "checked_utc": prep["checked_utc"],
        "source_closure": prep["source_closure"],
        "new_image_count": len(new_items),
        "new_image_bytes": sum(int(item["length"]) for item in new_items),
        "new_primary_count": len(new_items),
        "new_supplement_count": 0,
        "map_validation": {"primary": {"records": len(primary_loader), "bytes": primary_bytes_checked}, "supplement": {"records": len(supplement_loader), "bytes": supplement_bytes_checked}},
        "loader_preflight": {"primary_overlay_records": len(primary_loader), "supplement_overlay_records": len(supplement_loader), "total_overlay_records": len(primary_loader) + len(supplement_loader), "new_primary_records": len(new_items), "new_supplement_records": 0, "guide_collection_groups": 3, "guide_collection_images": 39, "guide_previews": 22, "network_requests": 0, "export_executed": False, "old_image_payloads_rehashed": False},
        "native_ui_input": prep["native_ui_input"],
        "expected_after_export": prep["expected_after_export"],
        "root_input_acceptance_required": True,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    proposal = f"""# v35 input proposal

v35 is a preparation-only delta over the locally built and byte-audited v34
closure.  The accepted contest navigation compatibility repair remains bound
through the current exporter and root contest-tool receipt.  The frozen
closure is 459 primary plus 100 supplement overlays (559 total), 39 guide
images, and 22 guide previews.

Two root-accepted original-byte news batches add 24 primary images totaling
191943 bytes: frontier-news04 (4/41536) and frontier-news20a (20/150407).
The resulting target is 483 primary, 100 supplement, and 583 total overlays,
with 9041 declared and 9042 actual files.  All 24 captures are on the
canonical `www.worldofwarcraft.com` host in the 2008 baseline through anchor;
no pre-anchor or supplement policy is widened.

The map source is limited to the two accepted source/public-copy receipts and
their Git-visible `publication/accepted-images/` paths.  Native page evidence
is separately recorded in `v35-native-ui-inputs.json` from literal Source15
references and actual `news-expand`/`news-collapse` ids.  It is evidence for
the later browser gate, not a browser acceptance result.

`execute_v35.py --go --root-export-go` is the only export entry point.  It
requires a root acceptance gate with exact bindings and post-export
expectations, checks the D: free-space floor and 13:30Z start deadline, and
refuses an existing output, partial, or receipt.  No export, network request,
or publication is performed by this preparation.
"""
    runner_note = """# v35 runner preparation

`execute_v35.py` is a one-shot, export-only wrapper. It reads the frozen v35
maps/preflight and root-v35 input gate, verifies every map, source/public-copy
receipt, v34 closure, current exporter, and contest-tool acceptance SHA, then
calls `export_pages` exactly once with `max_bytes=None`, the D: free-space
floor, the frozen primary/supplement maps, and the v35 primary delta. It
requires `--go --root-export-go`, an accepted root gate, and a parent 900-second
watchdog. It never reads pending network folders, regenerates maps, or
publishes Pages.
"""
    write_once(PREPARATION, prep, "v35 preparation")
    write_once(PREFLIGHT, preflight, "v35 preflight")
    write_once(PROPOSAL, proposal, "v35 proposal")
    write_once(RUNNER_NOTE, runner_note, "v35 runner note")
    print(json.dumps({"status": preflight["status"], "new_images": len(new_items), "new_bytes": sum(int(item["length"]) for item in new_items), "primary": len(primary_loader), "supplement": len(supplement_loader), "total": len(primary_loader) + len(supplement_loader), "declared": 9041, "actual": 9042, "native_targets": len(native_payload["targets"]), "network_requests": 0, "export_executed": False, "disk_free_bytes": free_before}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
