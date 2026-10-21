#!/usr/bin/env python3
"""Validate the eight accepted talent point-box layout reuses.

The bundle is a narrow compatibility adapter for the existing
``source16_layout_compat.LayoutCompatibilityBundle`` shape.  It validates
only the eight approved target routes and returns route reuse plus public
provenance.  It never copies or returns image bytes, creates aliases, writes
manifests, or changes the Source16 site.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

import source16_layout_compat as _layout


LayoutCompatibilityBundle = _layout.LayoutCompatibilityBundle
LayoutCompatibilityError = _layout.LayoutCompatibilityError

EXPECTED_MAP_SHA256 = "1da1ceaceed5d5ca184de64e61ad72f0720515be5755fe532682e0707a46c08e"
EXPECTED_DECISION_SHA256 = "c6ab46441cc281ebc58fb83eebf77507ff8db12126ad93e8363d02674a5eacd0"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_MAP_SCHEMA = "wow-talent-box-layout-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-root-talent-box-layout-decision/v1"
EXPECTED_CLASSIFICATION = "layout_compatibility_reuse"
EXPECTED_ENTRY_COUNT = 8
EXPECTED_PAGE_ROUTES = (
    "/info/classes/druid/talents.html",
    "/info/classes/hunter/talents.html",
    "/info/classes/mage/talents.html",
    "/info/classes/paladin/talents.html",
    "/info/classes/priest/talents.html",
    "/info/classes/rogue/talents.html",
    "/info/classes/shaman/talents.html",
    "/info/classes/warlock/talents.html",
    "/info/classes/warrior/talents.html",
)

_ROOT_ORIGIN = "http://www.worldofwarcraft.com"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_RE = re.compile(r"^[0-9]{14}$")

_EXPECTED_ENTRIES: Mapping[str, Mapping[str, Any]] = {
    "/shared/global/talents/includes/images/bot-box/bot-left.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/bot-left.gif",
    },
    "/shared/global/talents/includes/images/bot-box/bot-right.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/bot-right.gif",
    },
    "/shared/global/talents/includes/images/bot-box/bot.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/bot.gif",
    },
    "/shared/global/talents/includes/images/bot-box/left.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/left.gif",
    },
    "/shared/global/talents/includes/images/bot-box/right.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/right.gif",
    },
    "/shared/global/talents/includes/images/bot-box/top-left.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/top-left.gif",
    },
    "/shared/global/talents/includes/images/bot-box/top-right.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/top-right.gif",
    },
    "/shared/global/talents/includes/images/bot-box/top.gif": {
        "source_route": "/info/classes/includes-new/images/bot-box/top.gif",
    },
}


def _fail(message: str) -> LayoutCompatibilityError:
    return LayoutCompatibilityError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object: {path}")
    return value, raw


def _public_record(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Return only public route/source metadata, never local source paths."""

    return {
        "page_routes": list(entry["page_routes"]),
        "target_route": entry["target_route"],
        "source_route": entry["source_route"],
        "source_original_url": entry["source_original_url"],
        "source_capture_timestamp": entry["source_capture_timestamp"],
        "source_memento_datetime": entry["source_memento_datetime"],
        "sha256": entry["sha256"],
        "length": entry["length"],
        "format": entry["format"],
        "dimensions": list(entry["dimensions"]),
        "frames": entry["frames"],
        "layout_role": entry["layout_role"],
        "classification": entry["classification"],
        "target_capture_timestamp": None,
    }


def _validate_entries(
    entries: list[Any],
    *,
    manifest_data: Mapping[str, Any],
    root: Path,
    site: Path,
) -> tuple[tuple[Mapping[str, Any], ...], dict[str, tuple[Mapping[str, Any], ...]]]:
    if len(entries) != EXPECTED_ENTRY_COUNT:
        raise _fail(f"input map must contain exactly {EXPECTED_ENTRY_COUNT} entries")
    records = [row for row in manifest_data.get("files", []) if isinstance(row, dict) and row.get("route")]
    records_by_route = {row["route"]: row for row in records}
    if len(records_by_route) != len(records):
        raise _fail("source manifest contains duplicate route records")

    seen_targets: set[str] = set()
    seen_sources: set[str] = set()
    public: list[Mapping[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, dict):
            raise _fail("talent-box map entry must be an object")
        entry = dict(raw)
        target = _layout._route(entry.get("target_route"), "target route")
        source = _layout._route(entry.get("source_route"), "source route")
        expected = _EXPECTED_ENTRIES.get(target)
        if expected is None or source != expected["source_route"]:
            raise _fail(f"entry is outside the exact accepted eight-route scope: {target}")
        if target in seen_targets or source in seen_sources:
            raise _fail("duplicate target or source route in talent-box map")
        seen_targets.add(target)
        seen_sources.add(source)
        if entry.get("page_routes") != list(EXPECTED_PAGE_ROUTES):
            raise _fail(f"entry page_routes are not the exact nine talent pages: {target}")
        if entry.get("classification") != EXPECTED_CLASSIFICATION:
            raise _fail(f"entry classification is not accepted: {target}")
        if entry.get("target_capture_timestamp") is not None:
            raise _fail(f"target capture timestamp must be null: {target}")
        capture = entry.get("source_capture_timestamp")
        if not isinstance(capture, str) or not _TIMESTAMP_RE.fullmatch(capture):
            raise _fail(f"source capture timestamp is malformed: {target}")
        if entry.get("source_original_url") != _ROOT_ORIGIN + source:
            raise _fail(f"source original URL does not match source route: {target}")
        if not isinstance(entry.get("source_memento_datetime"), str) or not entry["source_memento_datetime"].strip():
            raise _fail(f"source memento datetime is missing: {target}")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise _fail(f"entry SHA is malformed: {target}")
        if not isinstance(entry.get("length"), int) or entry["length"] < 1:
            raise _fail(f"entry length is malformed: {target}")
        if entry.get("format") != "GIF" or entry.get("frames") != 1:
            raise _fail(f"entry format/frames are not GIF/1: {target}")
        dimensions = entry.get("dimensions")
        if (
            not isinstance(dimensions, list)
            or len(dimensions) != 2
            or not all(isinstance(value, int) and value > 0 for value in dimensions)
        ):
            raise _fail(f"entry dimensions are malformed: {target}")

        manifest_row = records_by_route.get(source)
        if not isinstance(manifest_row, dict):
            raise _fail(f"source route is missing from source manifest: {source}")
        for key, expected_value in (
            ("source_sha256", digest),
            ("derived_sha256", digest),
            ("source_length", entry["length"]),
            ("derived_length", entry["length"]),
            ("mime", "image/gif"),
            ("source_mime", "image/gif"),
            ("actual_timestamp", capture),
            ("source_base_url", entry["source_original_url"]),
        ):
            if manifest_row.get(key) != expected_value:
                raise _fail(f"manifest {key} drift for {source}")
        if manifest_row.get("transformed") is not False:
            raise _fail(f"source manifest marks {source} as transformed")

        _layout._assert_target_missing(site, target)
        output_path = manifest_row.get("output_path")
        output_file = _layout._inside_file(root, output_path, f"manifest output for {source}")
        expected_file = (site / source.lstrip("/")).resolve()
        if output_file != expected_file:
            raise _fail(f"manifest output does not match source site for {source}")
        source_file = _layout._inside_file(site, source.lstrip("/"), f"source asset {source}")
        data, _ = _layout._hash_checked(source_file, digest, entry["length"], f"source asset {source}")
        _layout._validate_image(data, entry, f"source asset {source}")
        public.append(_public_record(entry))

    if seen_targets != set(_EXPECTED_ENTRIES) or len(seen_targets) != EXPECTED_ENTRY_COUNT:
        raise _fail("talent-box map does not cover the exact accepted eight target set")
    if seen_sources != {item["source_route"] for item in _EXPECTED_ENTRIES.values()}:
        raise _fail("talent-box map does not cover the exact accepted source set")
    public_records = tuple(public)
    per_page = {
        page: tuple(record for record in public_records if page in record["page_routes"])
        for page in EXPECTED_PAGE_ROUTES
    }
    if any(len(records_for_page) != EXPECTED_ENTRY_COUNT for records_for_page in per_page.values()):
        raise _fail("talent-box per-page references do not contain all eight entries")
    return public_records, per_page


def load_talent_box_layout_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    source_site: str | Path,
    manifest_path: str | Path,
    manifest: Mapping[str, Any],
) -> LayoutCompatibilityBundle:
    """Validate the accepted eight-route talent point-box reuse map."""

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _layout._inside_file(root, map_path, "input map")
    map_data, map_bytes = _read_json(map_file, "input map")
    map_sha = _sha256(map_bytes)
    if map_sha != EXPECTED_MAP_SHA256:
        raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted talent-box layout map")
    if map_data.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("input map classification is not layout_compatibility_reuse")
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("input map source_manifest_sha256 is not the accepted Source16 manifest")

    decision_rel = _layout._relative(map_data.get("decision"), "decision path")
    decision_file = _layout._inside_file(root, decision_rel, "decision path")
    decision_data, decision_bytes = _read_json(decision_file, "decision record")
    decision_sha = _sha256(decision_bytes)
    if decision_sha != EXPECTED_DECISION_SHA256 or map_data.get("decision_sha256") != decision_sha:
        raise _fail("decision SHA binding does not match the accepted talent-box decision")
    if decision_data.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision schema is not the accepted talent-box layout decision")
    if decision_data.get("accepted_for_compatibility_reuse") is not True:
        raise _fail("decision is not accepted for compatibility reuse")
    if decision_data.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("decision classification is not layout_compatibility_reuse")
    if decision_data.get("new_image_payloads") != 0 or decision_data.get("target_original_images_recovered") != 0:
        raise _fail("decision contains an unexpected new or original image payload")
    entries = map_data.get("entries")
    if not isinstance(entries, list) or len(entries) != EXPECTED_ENTRY_COUNT:
        raise _fail(f"input map must contain exactly {EXPECTED_ENTRY_COUNT} entries")
    if decision_data.get("targets") != entries:
        raise _fail("input map entries do not exactly match decision targets")

    manifest_file = _layout._inside_file(root, manifest_path, "source manifest")
    manifest_data, manifest_bytes = _read_json(manifest_file, "source manifest")
    manifest_sha = _sha256(manifest_bytes)
    if manifest_sha != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail(f"source manifest SHA mismatch: expected {EXPECTED_SOURCE_MANIFEST_SHA256}, got {manifest_sha}")
    if dict(manifest) != manifest_data:
        raise _fail("passed manifest does not match source manifest bytes")
    bindings = decision_data.get("bindings")
    binding_ok = False
    if isinstance(bindings, list):
        for binding in bindings:
            if not isinstance(binding, dict) or binding.get("sha256") != manifest_sha:
                continue
            try:
                binding_file = _layout._inside_file(root, binding.get("path"), "decision manifest binding")
            except LayoutCompatibilityError:
                continue
            if binding_file == manifest_file:
                binding_ok = True
                break
    if not binding_ok:
        raise _fail("decision does not bind the accepted source manifest")

    site = _layout._inside_dir(root, source_site, "source site")
    public_records, per_page_records = _validate_entries(
        entries, manifest_data=manifest_data, root=root, site=site
    )
    return LayoutCompatibilityBundle(
        route_reuses={record["target_route"]: record["source_route"] for record in public_records},
        public_records=public_records,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_manifest_sha256=manifest_sha,
        per_page_records=per_page_records,
    )


__all__ = [
    "EXPECTED_CLASSIFICATION",
    "EXPECTED_DECISION_SHA256",
    "EXPECTED_DECISION_SCHEMA",
    "EXPECTED_ENTRY_COUNT",
    "EXPECTED_MAP_SHA256",
    "EXPECTED_MAP_SCHEMA",
    "EXPECTED_PAGE_ROUTES",
    "EXPECTED_SOURCE_MANIFEST_SHA256",
    "LayoutCompatibilityBundle",
    "LayoutCompatibilityError",
    "_EXPECTED_ENTRIES",
    "load_talent_box_layout_bundle",
]
