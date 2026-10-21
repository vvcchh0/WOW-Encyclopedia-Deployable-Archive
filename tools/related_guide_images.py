#!/usr/bin/env python3
"""Load the accepted current ArchiveCraft guide-image supplement.

This adapter intentionally handles one pinned The Broken JPEG plus its one
same-topic dynamic thumbnail route.  It reuses the encyclopedia adapter's
path, JSON, timestamp, and JPEG checks while keeping guide-specific
dataclasses, routes, catalog, and source notice names.  The payload is a
current related source; no historical 2008 capture is asserted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import html
import json
import os
from pathlib import Path
from typing import Any, Mapping

try:
    from PIL import Image  # noqa: F401  # imported by the shared JPEG helper
except ImportError as exc:  # pragma: no cover - repository tests provide Pillow
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None

import related_encyclopedia_images as _encyclopedia


class RelatedGuideImageError(ValueError):
    """Raised when the pinned guide-image supplement is unsafe or drifted."""


EXPECTED_MAP_SHA256 = "b2ef90f1cdb17af02a534be71c26d4c8859bab1c87220fb9f7cb1b9e94c2c05b"
EXPECTED_DECISION_SHA256 = "c1fb85a441852463c3715d7f7e86bcdf6c34e7757e4c92817a97777a45465915"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = "97a0e8005573a77ee38d2bb1c758f48386067e6fe4b20c0d02c14ac9782bb64e"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_MAP_SCHEMA = "wow-related-guide-image-map/v2"
EXPECTED_DECISION_SCHEMA = "wow-related-guide-image-decision/v2"
EXPECTED_ACCEPTANCE_SCHEMA = "wow-root-archivecraft-guide-image-source-acceptance/v1"
EXPECTED_CLASSIFICATION = "current_related_archive_source"
EXPECTED_COMPATIBILITY_CLASSIFICATION = "current_related_display_mapping"
EXPECTED_ENTRY_COUNT = 1
EXPECTED_CATALOG_RELATIVE = "__offline/related-guide-images.json"

EXPECTED_ENTRY: Mapping[str, Any] = {
    "title": "The Broken",
    "page_route": "/burningcrusade/townhall/bestiary.html",
    "target_route": "/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg",
    "route": "/__offline/related-guide-images/thumb-thebroken.jpg",
    "source_image_url": "https://archivecraft.com/wp-content/uploads/images/index/townhall/burning-crusade/bestiary/thumb-thebroken.jpg",
    "source_page_url": "https://archivecraft.com/burningcrusade/townhall/bestiary/",
    "current_observed_utc": "2026-10-21T09:38:21.231103Z",
    "sha256": "07f86855600ec20dbd9712ad654df2aaafd5c4b48a3355582f8d5d216dadd1b9",
    "length": 17152,
    "format": "JPEG",
    "width": 237,
    "height": 184,
    "frames": 1,
    "classification": EXPECTED_CLASSIFICATION,
    "original_capture_timestamp": None,
    "source_processing_note": "Processing before retrieval is unknown.",
}

EXPECTED_COMPATIBILITY_REUSE: Mapping[str, Any] = {
    "target_route": "/burningcrusade/townhall/images/bestiary/thumb-broken.jpg",
    "route": "/__offline/related-guide-images/thumb-thebroken.jpg",
    "page_route": "/burningcrusade/townhall/bestiary.html",
    "creature_name": "broken",
    "classification": EXPECTED_COMPATIBILITY_CLASSIFICATION,
    "original_capture_timestamp": None,
    "page_source_sha256": "d661ab5331d5cda695b74b7eba791d1745c19d755c693d296f89b6501e79db0c",
    "script_source_sha256": "8c622c25920d0a2045f2537e4c56c6f5274e00c521c8783da2edacaef9fdb69a",
}


@dataclass(frozen=True)
class RelatedGuideImageAsset:
    """One exact JPEG payload and its same-topic missing target route."""

    route: str
    relative: str
    target_route: str
    data: bytes
    mime: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedGuideImageBundle:
    """Validated guide payload, route reuse, catalog, and notices."""

    assets: tuple[RelatedGuideImageAsset, ...]
    route_reuses: Mapping[str, str]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    notice_by_page: Mapping[str, str]
    map_sha256: str
    decision_sha256: str
    source_acceptance_sha256: str


def _fail(message: str) -> RelatedGuideImageError:
    return RelatedGuideImageError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object")
    return value


def _safe_relative(value: Any, label: str) -> str:
    try:
        return _encyclopedia._safe_relative(value, label)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _resolve_file(root: Path, value: Any, label: str) -> Path:
    try:
        return _encyclopedia._resolve_file(root, value, label)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _resolve_map(root: Path, map_path: str | os.PathLike[str]) -> Path:
    try:
        return _encyclopedia._resolve_map(root, map_path)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _read_pinned(path: Path, expected: str, label: str) -> tuple[dict[str, Any], str]:
    try:
        return _encyclopedia._read_pinned(path, expected, label)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _normalize_base_path(value: str) -> str:
    try:
        return _encyclopedia._normalize_base_path(value)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _validated_utc(value: Any, label: str) -> str:
    try:
        return _encyclopedia._validated_utc(value, label)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _validate_jpeg(data: bytes, entry: Mapping[str, Any], route: str) -> tuple[int, int, int]:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required to validate {route}: {_PIL_IMPORT_ERROR}")
    try:
        return _encyclopedia._validate_jpeg(data, entry, route)
    except Exception as exc:
        raise _fail(str(exc)) from exc


def _public_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key != "payload_path"}


def _assert_exact_entry(entry: Mapping[str, Any], label: str) -> None:
    # The pinned map SHA protects the exact production metadata.  These stable
    # identity fields are also checked for portable test maps; bytes, length,
    # dimensions, and capture time are validated against the bound records and
    # payload below so tests can use a small synthetic JPEG.
    stable_keys = (
        "title",
        "page_route",
        "target_route",
        "route",
        "source_image_url",
        "source_page_url",
        "classification",
        "original_capture_timestamp",
        "source_processing_note",
    )
    for key in stable_keys:
        expected = EXPECTED_ENTRY[key]
        if entry.get(key) != expected:
            raise _fail(f"{label} does not match accepted {key}")
    _safe_relative(entry.get("payload_path"), f"{label} payload_path")


def _assert_exact_compatibility(value: Any, label: str) -> None:
    if not isinstance(value, list) or value != [dict(EXPECTED_COMPATIBILITY_REUSE)]:
        raise _fail(f"{label} does not contain the exact accepted compatibility reuse")
    reuse = value[0]
    if reuse["classification"] != EXPECTED_COMPATIBILITY_CLASSIFICATION:
        raise _fail(f"{label} compatibility classification is not accepted")
    if reuse["original_capture_timestamp"] is not None:
        raise _fail(f"{label} compatibility mapping must not claim an original capture")


def _validate_bindings(
    map_file: Path,
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    map_data, map_sha = _read_pinned(map_file, EXPECTED_MAP_SHA256, "input map")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted guide-image map")
    if map_data.get("source_label") != "ArchiveCraft community archive":
        raise _fail("input map source label is not accepted")
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("input map source manifest is not the accepted manifest binding")

    decision_rel = _safe_relative(map_data.get("decision"), "decision path")
    acceptance_rel = _safe_relative(map_data.get("source_acceptance"), "source acceptance path")
    decision_path = _resolve_file(root, decision_rel, "decision path")
    acceptance_path = _resolve_file(root, acceptance_rel, "source acceptance path")
    decision, decision_sha = _read_pinned(decision_path, EXPECTED_DECISION_SHA256, "decision record")
    acceptance, acceptance_sha = _read_pinned(
        acceptance_path, EXPECTED_SOURCE_ACCEPTANCE_SHA256, "source acceptance record"
    )
    if map_data.get("decision_sha256") != decision_sha:
        raise _fail("input map decision_sha256 does not match decision record")
    if map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("input map source_acceptance_sha256 does not match source acceptance")
    if decision.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision schema is not accepted")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA:
        raise _fail("source acceptance schema is not accepted")
    if decision.get("source_acceptance") != acceptance_rel or decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("decision source acceptance binding does not match")
    if not decision.get("accepted_for_browser_supplement"):
        raise _fail("decision is not accepted for browser supplement")
    if decision.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("decision classification is not current_related_archive_source")
    if decision.get("original_2008_images_recovered") != 0:
        raise _fail("decision claims recovered 2008 images")
    _assert_exact_compatibility(map_data.get("compatibility_reuses"), "input map")
    _assert_exact_compatibility(decision.get("compatibility_reuses"), "decision")
    if decision.get("compatibility_reuses") != map_data.get("compatibility_reuses"):
        raise _fail("decision compatibility_reuses do not exactly match input map")
    if acceptance.get("accepted_sources") is not True:
        raise _fail("source acceptance is not accepted")
    if acceptance.get("historical_original_images_recovered") != 0:
        raise _fail("source acceptance claims recovered historical images")
    if acceptance.get("images_reencoded") is not False:
        raise _fail("source acceptance does not bind original bytes")

    entries = map_data.get("entries")
    targets = decision.get("targets")
    if not isinstance(entries, list) or len(entries) != EXPECTED_ENTRY_COUNT:
        raise _fail("input map does not contain the exact one-image scope")
    if not isinstance(targets, list) or targets != [_public_entry(entry) for entry in entries]:
        raise _fail("decision targets do not exactly match map entries")
    for entry in entries:
        if not isinstance(entry, dict):
            raise _fail("map entry must be an object")
        _assert_exact_entry(entry, "map entry")
    acceptance_records = acceptance.get("records")
    if not isinstance(acceptance_records, list) or len(acceptance_records) != EXPECTED_ENTRY_COUNT:
        raise _fail("source acceptance does not contain the exact one-image scope")
    if acceptance_records != [_public_entry(entries[0])]:
        raise _fail("source acceptance record does not exactly match map entry")
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


def _make_notice(source_page_url: str) -> str:
    source_url = html.escape(source_page_url, quote=True)
    return (
        '<aside id="__offline-related-guide-images" role="note" '
        'style="padding:6px 12px;background:#eadbb7;color:#302619;'
        'font:13px/1.5 Arial,sans-serif;text-align:center">'
        f'Illustration from <a href="{source_url}" '
        'style="color:#174f7d;text-decoration:underline" '
        'target="_blank" rel="noopener noreferrer">ArchiveCraft</a>.'
        "</aside>"
    )


def _make_catalog(
    *,
    base_path: str,
    assets: list[RelatedGuideImageAsset],
    source_metadata: Mapping[str, Any],
) -> bytes:
    payload = {
        "schema": "wow-related-guide-image-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "source": dict(source_metadata),
        "compatibility_reuses": list(source_metadata.get("compatibility_reuses", ())),
        "image_count": len(assets),
        "images": [
            {
                "title": asset.metadata["title"],
                "page_route": asset.metadata["page_route"],
                "target_route": asset.target_route,
                "route": asset.route,
                "url": f"{base_path}{asset.relative}" if base_path else "/" + asset.relative,
                "source_image_url": asset.metadata["source_image_url"],
                "source_page_url": asset.metadata["source_page_url"],
                "current_observed_utc": asset.metadata["current_observed_utc"],
                "sha256": asset.metadata["sha256"],
                "length": asset.metadata["length"],
                "mime": asset.mime,
                "width": asset.metadata["width"],
                "height": asset.metadata["height"],
                "frames": asset.metadata["frames"],
                "classification": asset.metadata["classification"],
                "original_capture_timestamp": None,
                "source_processing_note": asset.metadata["source_processing_note"],
            }
            for asset in assets
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_related_guide_image_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedGuideImageBundle:
    """Validate and load the exact current related guide JPEG."""

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map(root, map_path)
    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha = _validate_bindings(map_file, root)
    entry = map_data["entries"][0]
    route = str(entry["route"])
    relative = _safe_relative(route[1:] if route.startswith("/") else route, f"canonical route {route}")
    payload_file = _resolve_file(root, entry["payload_path"], f"payload {route}")
    try:
        data = payload_file.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read payload for {route}: {exc}") from exc
    if len(data) != entry["length"]:
        raise _fail(f"{route} length mismatch")
    actual_sha = _sha256(data)
    if actual_sha != entry["sha256"]:
        raise _fail(f"{route} SHA mismatch: expected {entry['sha256']}, got {actual_sha}")
    width, height, frames = _validate_jpeg(data, entry, route)
    _validated_utc(entry["current_observed_utc"], f"{route} current_observed_utc")
    metadata = {
        "title": entry["title"],
        "page_route": entry["page_route"],
        "target_route": entry["target_route"],
        "source_image_url": entry["source_image_url"],
        "source_page_url": entry["source_page_url"],
        "current_observed_utc": entry["current_observed_utc"],
        "sha256": actual_sha,
        "length": len(data),
        "format": "JPEG",
        "width": width,
        "height": height,
        "frames": frames,
        "classification": EXPECTED_CLASSIFICATION,
        "original_capture_timestamp": None,
        "source_processing_note": entry["source_processing_note"],
    }
    asset = RelatedGuideImageAsset(
        route=route,
        relative=relative,
        target_route=entry["target_route"],
        data=data,
        mime="image/jpeg",
        metadata=metadata,
    )
    source_metadata = {
        "source_label": map_data["source_label"],
        "classification": EXPECTED_CLASSIFICATION,
        "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "image_count": 1,
        "source_bytes": len(data),
        "source_checked_utc": acceptance.get("checked_utc"),
        "compatibility_reuses": [dict(EXPECTED_COMPATIBILITY_REUSE)],
    }
    notice_by_page = {entry["page_route"]: _make_notice(entry["source_page_url"])}
    catalog_bytes = _make_catalog(base_path=normalized_base, assets=[asset], source_metadata=source_metadata)
    compatibility_route = str(EXPECTED_COMPATIBILITY_REUSE["target_route"])
    if compatibility_route == str(entry["target_route"]):
        raise _fail("compatibility target must be distinct from the static target")
    return RelatedGuideImageBundle(
        assets=(asset,),
        route_reuses={asset.target_route: asset.route, compatibility_route: asset.route},
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=len(data) + len(catalog_bytes),
        source_metadata=source_metadata,
        notice_by_page=notice_by_page,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


__all__ = [
    "EXPECTED_ACCEPTANCE_SCHEMA",
    "EXPECTED_CATALOG_RELATIVE",
    "EXPECTED_CLASSIFICATION",
    "EXPECTED_COMPATIBILITY_CLASSIFICATION",
    "EXPECTED_COMPATIBILITY_REUSE",
    "EXPECTED_DECISION_SCHEMA",
    "EXPECTED_DECISION_SHA256",
    "EXPECTED_ENTRY",
    "EXPECTED_ENTRY_COUNT",
    "EXPECTED_MAP_SCHEMA",
    "EXPECTED_MAP_SHA256",
    "EXPECTED_SOURCE_ACCEPTANCE_SHA256",
    "EXPECTED_SOURCE_MANIFEST_SHA256",
    "RelatedGuideImageAsset",
    "RelatedGuideImageBundle",
    "RelatedGuideImageError",
    "load_related_guide_image_bundle",
]
