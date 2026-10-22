#!/usr/bin/env python3
"""Load pinned current ArchiveCraft guide-image supplements (v2 and v3).

The v2 bundle contains The Broken JPEG and its same-topic compatibility
thumbnail route. The v3 bundle retains that entry and adds the Profession
Updates PNG banner with its own static route. Both are current related
sources; neither asserts a historical 2008 capture.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import html
import io
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

EXPECTED_V3_MAP_SHA256 = "7558451ac2f2a97f558587dfb7eb9a5e21da4acea7dc239044df88cca4ebd8e5"
EXPECTED_V3_DECISION_SHA256 = "02f9cef4f70cf85959eddc90b6b935b8d9773eb539fe050f9059675282557e1c"
EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256 = "51e1a415c50d21006cec532749b653b689bae7dd391e5884f14c6274836f6976"
EXPECTED_V3_ROOT_INPUT_PINS_SHA256 = "945416af325d4b5657e1dd05866068433b1c2b41b9a05fc7d509536e2177a954"
EXPECTED_V3_MAP_SCHEMA = "wow-related-guide-image-map/v3"
EXPECTED_V3_DECISION_SCHEMA = "wow-related-guide-image-decision/v3"
EXPECTED_V3_ACCEPTANCE_SCHEMA = "wow-related-guide-image-source-acceptance/v3"
EXPECTED_V3_INPUT_MAP = "research/continuous-recovery-20261022/integration/related-guide-images-v53/input-map.json"
EXPECTED_V3_PINS_RELATIVE = "research/continuous-recovery-20261022/integration/related-guide-images-v53/root-input-pins.json"
EXPECTED_V3_ENTRY_COUNT = 2
EXPECTED_V3_NEW_PAYLOAD_BYTES = 18846
EXPECTED_V3_PUBLIC_ASSET_PATH = "research/continuous-recovery-20261022/integration/related-guide-images-v53/assets/professions-page-title.png"

EXPECTED_V3_ENTRY: Mapping[str, Any] = {
    "title": "Profession Updates",
    "page_route": "/burningcrusade/townhall/professions.html",
    "target_route": "/burningcrusade/townhall/images/professions/page-title.png",
    "route": "/__offline/related-guide-images/professions-page-title.png",
    "source_image_url": "https://archivecraft.com/wp-content/uploads/images/index/townhall/burning-crusade/professions/page-title.png",
    "source_page_url": "https://archivecraft.com/burningcrusade/townhall/professions/",
    "current_observed_utc": "2026-10-22T08:36:27.337365Z",
    "sha256": "33caa0898bfce8e5d6e92e3bfca2cd5505c3784316b36e800ed0a3069e8e2a8b",
    "length": 18846,
    "format": "PNG",
    "width": 324,
    "height": 72,
    "frames": 1,
    "classification": EXPECTED_CLASSIFICATION,
    "original_capture_timestamp": None,
    "source_processing_note": "Processing before retrieval is unknown.",
}

EXPECTED_V3_SOURCE_ACCEPTANCE_INPUTS = (
    {
        "path": "research/continuous-recovery-20261021/publication/root-archivecraft-broken-image-source-acceptance.json",
        "sha256": "97a0e8005573a77ee38d2bb1c758f48386067e6fe4b20c0d02c14ac9782bb64e",
        "schema": "wow-root-archivecraft-guide-image-source-acceptance/v1",
        "entry_title": "The Broken",
    },
    {
        "path": "research/continuous-recovery-20261022/root-professions-banner-source-acceptance.json",
        "sha256": "0c9d29f9896fbb3813835bedc218ab01238f9f5c16d07e4ab82291e89d634d01",
        "schema": "wow-root-professions-banner-source-acceptance/v1",
        "entry_title": "Profession Updates",
    },
)

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


def _validate_png(data: bytes, entry: Mapping[str, Any], route: str) -> tuple[int, int, int]:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required to validate {route}: {_PIL_IMPORT_ERROR}")
    if entry.get("format") != "PNG":
        raise _fail(f"{route} map format is not PNG")
    try:
        with Image.open(io.BytesIO(data)) as image:
            actual_format = image.format
            width, height = image.size
            frame_count = int(getattr(image, "n_frames", 1))
            if actual_format != "PNG":
                raise _fail(f"{route} payload decodes as {actual_format}, not PNG")
            if frame_count != 1:
                raise _fail(f"{route} has {frame_count} frames, expected one")
            for frame_index in range(frame_count):
                image.seek(frame_index)
                image.load()
                image.convert("RGBA").tobytes()
    except RelatedGuideImageError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable PNG: {exc}") from exc
    if (width, height) != (324, 72):
        raise _fail(f"{route} dimensions are {width}x{height}, expected 324x72")
    if entry.get("width") != width or entry.get("height") != height or entry.get("frames") != frame_count:
        raise _fail(f"{route} map dimensions/frames do not match the PNG payload")
    return width, height, frame_count


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


def _validate_v2_bindings(
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


def _expected_v3_entries() -> tuple[dict[str, Any], ...]:
    broken = {**dict(EXPECTED_ENTRY), "payload_path": "research/continuous-recovery-20261021/network/archivecraft-broken-image01/review/thebroken.jpg"}
    professions = {
        **dict(EXPECTED_V3_ENTRY),
        "payload_path": EXPECTED_V3_PUBLIC_ASSET_PATH,
    }
    return broken, professions


def _validate_v3_source_inputs(root: Path, acceptance: Mapping[str, Any]) -> None:
    expected_refs = [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in EXPECTED_V3_SOURCE_ACCEPTANCE_INPUTS
    ]
    refs = acceptance.get("source_acceptance_inputs")
    if refs != expected_refs:
        raise _fail("v3 source_acceptance_inputs do not match the accepted source roles")

    expected_by_title = {entry["title"]: entry for entry in _expected_v3_entries()}
    for source_input in EXPECTED_V3_SOURCE_ACCEPTANCE_INPUTS:
        source_path = _resolve_file(root, source_input["path"], "source acceptance input")
        source_record, _ = _read_pinned(
            source_path, source_input["sha256"], f"{source_input['entry_title']} source acceptance input"
        )
        if source_record.get("schema") != source_input["schema"]:
            raise _fail(f"{source_input['entry_title']} source acceptance input has the wrong role schema")
        if source_record.get("accepted_sources") is not True:
            raise _fail(f"{source_input['entry_title']} source acceptance input is not accepted")
        if source_record.get("images_reencoded") is not False:
            raise _fail(f"{source_input['entry_title']} source acceptance input does not bind original bytes")
        if source_record.get("historical_original_images_recovered") != 0:
            raise _fail(f"{source_input['entry_title']} source acceptance input claims historical recovery")
        if source_input["entry_title"] == "Profession Updates" and source_record.get("accepted_for_browser_supplement") is not True:
            raise _fail("Profession Updates source acceptance input is not accepted for browser supplement")
        expected_entry = _public_entry(expected_by_title[source_input["entry_title"]])
        if source_record.get("records") != [expected_entry]:
            raise _fail(f"{source_input['entry_title']} source acceptance input has a different image binding")


def _validate_v3_bindings(
    map_file: Path,
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    map_data, map_sha = _read_pinned(map_file, EXPECTED_V3_MAP_SHA256, "v3 input map")
    if map_data.get("schema") != EXPECTED_V3_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted guide-image map v3")
    try:
        map_relative = map_file.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise _fail("v3 input map is outside the workspace") from exc
    if map_relative != EXPECTED_V3_INPUT_MAP:
        raise _fail("v3 input map path is not the accepted pinned path")

    pins_path = _resolve_file(root, EXPECTED_V3_PINS_RELATIVE, "root input pins")
    pins, _ = _read_pinned(pins_path, EXPECTED_V3_ROOT_INPUT_PINS_SHA256, "root input pins")
    expected_pins = {
        "map_sha256": EXPECTED_V3_MAP_SHA256,
        "decision_sha256": EXPECTED_V3_DECISION_SHA256,
        "source_acceptance_sha256": EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256,
        "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "input_map": EXPECTED_V3_INPUT_MAP,
        "entry_count": EXPECTED_V3_ENTRY_COUNT,
        "new_payload_bytes": EXPECTED_V3_NEW_PAYLOAD_BYTES,
        "public_asset_path": EXPECTED_V3_PUBLIC_ASSET_PATH,
    }
    if pins != expected_pins:
        raise _fail("root input pins do not match the accepted v3 aggregate")
    if map_data.get("source_label") != "ArchiveCraft community archive":
        raise _fail("v3 input map source label is not accepted")
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("v3 input map source manifest is not the accepted Source16 manifest")

    decision_rel = _safe_relative(map_data.get("decision"), "decision path")
    acceptance_rel = _safe_relative(map_data.get("source_acceptance"), "source acceptance path")
    expected_decision_rel = "research/continuous-recovery-20261022/integration/related-guide-images-v53/decision.json"
    expected_acceptance_rel = "research/continuous-recovery-20261022/integration/related-guide-images-v53/source-acceptance.json"
    if decision_rel != expected_decision_rel or acceptance_rel != expected_acceptance_rel:
        raise _fail("v3 decision or source acceptance path is outside the accepted roles")
    decision_path = _resolve_file(root, decision_rel, "decision path")
    acceptance_path = _resolve_file(root, acceptance_rel, "source acceptance path")
    decision, decision_sha = _read_pinned(decision_path, EXPECTED_V3_DECISION_SHA256, "v3 decision record")
    acceptance, acceptance_sha = _read_pinned(
        acceptance_path, EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256, "v3 source acceptance record"
    )
    if map_data.get("decision_sha256") != decision_sha:
        raise _fail("v3 input map decision_sha256 does not match decision record")
    if map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("v3 input map source_acceptance_sha256 does not match source acceptance")
    if decision.get("schema") != EXPECTED_V3_DECISION_SCHEMA:
        raise _fail("v3 decision schema is not accepted")
    if acceptance.get("schema") != EXPECTED_V3_ACCEPTANCE_SCHEMA:
        raise _fail("v3 source acceptance schema is not accepted")
    if decision.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("v3 decision source manifest is not the accepted Source16 manifest")
    if decision.get("source_acceptance") != acceptance_rel or decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("v3 decision source acceptance binding does not match")
    if decision.get("accepted_for_browser_supplement") is not True:
        raise _fail("v3 decision is not accepted for browser supplement")
    if decision.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("v3 decision classification is not current_related_archive_source")
    if decision.get("original_2008_images_recovered") != 0:
        raise _fail("v3 decision claims recovered 2008 images")
    if acceptance.get("accepted_sources") is not True:
        raise _fail("v3 source acceptance is not accepted")
    if acceptance.get("images_reencoded") is not False:
        raise _fail("v3 source acceptance does not bind original bytes")
    if acceptance.get("historical_original_images_recovered") != 0:
        raise _fail("v3 source acceptance claims recovered historical images")
    if acceptance.get("new_current_related_images") != 1 or acceptance.get("retained_current_related_images") != 1:
        raise _fail("v3 source acceptance role counts do not match the two-entry aggregate")

    entries = map_data.get("entries")
    expected_entries = _expected_v3_entries()
    if not isinstance(entries, list) or len(entries) != EXPECTED_V3_ENTRY_COUNT:
        raise _fail("v3 input map does not contain the exact two-image scope")
    if entries != list(expected_entries):
        raise _fail("v3 input map entries do not match the accepted routes and source roles")
    if decision.get("targets") != [_public_entry(entry) for entry in expected_entries]:
        raise _fail("v3 decision targets do not exactly match the accepted map entries")
    if acceptance.get("records") != [_public_entry(entry) for entry in expected_entries]:
        raise _fail("v3 source acceptance records do not exactly match the accepted map entries")
    _assert_exact_compatibility(map_data.get("compatibility_reuses"), "v3 input map")
    _assert_exact_compatibility(decision.get("compatibility_reuses"), "v3 decision")
    if decision.get("compatibility_reuses") != map_data.get("compatibility_reuses"):
        raise _fail("v3 decision compatibility_reuses do not exactly match input map")
    _validate_v3_source_inputs(root, acceptance)
    _validated_utc(acceptance.get("checked_utc"), "v3 source acceptance checked_utc")
    for entry in expected_entries:
        _validated_utc(entry["current_observed_utc"], f"{entry['route']} current_observed_utc")
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


def _validate_bindings(
    map_file: Path,
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str, str]:
    try:
        raw = map_file.read_bytes()
        probe = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot inspect input map version: {map_file}: {exc}") from exc
    if not isinstance(probe, dict):
        raise _fail("input map must be a JSON object")
    schema = probe.get("schema")
    map_sha = _sha256(raw)
    if schema == EXPECTED_MAP_SCHEMA:
        if map_sha != EXPECTED_MAP_SHA256:
            raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
        return (*_validate_v2_bindings(map_file, root), "v2")
    if schema == EXPECTED_V3_MAP_SCHEMA:
        if map_sha != EXPECTED_V3_MAP_SHA256:
            raise _fail(f"v3 input map SHA mismatch: expected {EXPECTED_V3_MAP_SHA256}, got {map_sha}")
        return (*_validate_v3_bindings(map_file, root), "v3")
    raise _fail("input map schema is not an accepted guide-image map version")


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
    """Validate and load an accepted v2 one-image or v3 two-image bundle."""

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map(root, map_path)
    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha, version = _validate_bindings(map_file, root)
    assets: list[RelatedGuideImageAsset] = []
    route_reuses: dict[str, str] = {}
    seen_routes: set[str] = set()
    source_bytes = 0
    for entry in map_data["entries"]:
        route = str(entry["route"])
        relative = _safe_relative(route[1:] if route.startswith("/") else route, f"canonical route {route}")
        if route in seen_routes or relative in seen_routes:
            raise _fail(f"duplicate canonical route: {route}")
        seen_routes.add(route)
        payload_file = _resolve_file(root, entry["payload_path"], f"payload {route}")
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read payload for {route}: {exc}") from exc
        if not isinstance(entry.get("length"), int) or isinstance(entry.get("length"), bool) or len(data) != entry["length"]:
            raise _fail(f"{route} length mismatch")
        actual_sha = _sha256(data)
        if actual_sha != entry.get("sha256"):
            raise _fail(f"{route} SHA mismatch: expected {entry.get('sha256')}, got {actual_sha}")
        image_format = entry.get("format")
        if image_format == "JPEG":
            width, height, frames = _validate_jpeg(data, entry, route)
            mime = "image/jpeg"
        elif image_format == "PNG":
            width, height, frames = _validate_png(data, entry, route)
            mime = "image/png"
        else:
            raise _fail(f"{route} has an unsupported accepted image format: {image_format!r}")
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
            "format": image_format,
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
            mime=mime,
            metadata=metadata,
        )
        assets.append(asset)
        if asset.target_route in route_reuses:
            raise _fail(f"duplicate target route: {asset.target_route}")
        route_reuses[asset.target_route] = asset.route
        source_bytes += len(data)

    compatibility_reuses = [dict(item) for item in map_data.get("compatibility_reuses", [])]
    for reuse in compatibility_reuses:
        target_route = str(reuse["target_route"])
        if target_route in route_reuses:
            raise _fail(f"compatibility target duplicates a static target: {target_route}")
        route_reuses[target_route] = str(reuse["route"])

    source_metadata = {
        "source_label": map_data["source_label"],
        "classification": EXPECTED_CLASSIFICATION,
        "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "image_count": len(assets),
        "source_bytes": source_bytes,
        "source_checked_utc": acceptance.get("checked_utc"),
        "compatibility_reuses": compatibility_reuses,
    }
    if version == "v3":
        source_metadata["new_current_related_images"] = 1
        source_metadata["retained_current_related_images"] = 1
    notice_by_page = {
        str(entry["page_route"]): _make_notice(str(entry["source_page_url"]))
        for entry in map_data["entries"]
    }
    catalog_bytes = _make_catalog(base_path=normalized_base, assets=assets, source_metadata=source_metadata)
    return RelatedGuideImageBundle(
        assets=tuple(assets),
        route_reuses=route_reuses,
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=source_bytes + len(catalog_bytes),
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
    "EXPECTED_V3_ACCEPTANCE_SCHEMA",
    "EXPECTED_V3_DECISION_SCHEMA",
    "EXPECTED_V3_DECISION_SHA256",
    "EXPECTED_V3_ENTRY",
    "EXPECTED_V3_MAP_SCHEMA",
    "EXPECTED_V3_MAP_SHA256",
    "EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256",
    "RelatedGuideImageAsset",
    "RelatedGuideImageBundle",
    "RelatedGuideImageError",
    "load_related_guide_image_bundle",
]
