#!/usr/bin/env python3
"""Validate the accepted Source16 same-site layout reuses in memory.

This is deliberately a route-reuse loader.  It returns target-to-existing-route
records and public provenance only; it never copies or returns image bytes,
creates aliases, writes a manifest, or edits the Source16 site.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - repository test runtime has Pillow
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class LayoutCompatibilityError(ValueError):
    """Raised when the pinned layout map, manifest, or source asset drifts."""


EXPECTED_MAP_SHA256 = "85056e02afbd1a87005c99fab8be6adc68d771683c324c8f274b358c03081243"
EXPECTED_DECISION_SHA256 = "88de11e8efe23ae05e4bf3df4a3695e642318c249dcc26f92337416041f71350"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_MAP_SCHEMA = "wow-source16-layout-compatibility-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-root-source16-layout-reuse-decision/v1"
EXPECTED_CLASSIFICATION = "layout_compatibility_reuse"
EXPECTED_ENTRY_COUNT = 10
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_RE = re.compile(r"^[0-9]{14}$")
_ROOT_ORIGIN = "http://www.worldofwarcraft.com"
_TOOLTIP_FILES = (
    "ttip-tl.png", "ttip-tr.png", "ttip-t.png", "ttip-l.png", "ttip-r.png",
    "ttipbg.png", "ttip-bl.png", "ttip-br.png", "ttip-b.png",
)
_EXPECTED_ENTRIES = {
    f"/info/items/images/tinfoilhat/{name}": {
        "page_route": "/info/items/tinfoilhat.xml",
        "source_route": f"/wrath/images/layout/{name}",
    }
    for name in _TOOLTIP_FILES
}
_EXPECTED_ENTRIES["/moltencore/images/backarrow.gif"] = {
    "page_route": "/moltencore/index.html",
    "source_route": "/wrath/images/layout/backarrow.gif",
}


@dataclass(frozen=True)
class LayoutCompatibilityBundle:
    """Validated route reuses and public records, without source image bytes."""

    route_reuses: Mapping[str, str]
    public_records: tuple[Mapping[str, Any], ...]
    map_sha256: str
    decision_sha256: str
    source_manifest_sha256: str
    per_page_records: Mapping[str, tuple[Mapping[str, Any], ...]]


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


def _relative(value: Any, label: str) -> str:
    if isinstance(value, Path):
        value = value.as_posix()
    elif isinstance(value, os.PathLike):
        value = os.fspath(value)
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a non-empty relative POSIX path")
    if "\x00" in value or "\\" in value or value.startswith("/") or PureWindowsPath(value).is_absolute():
        raise _fail(f"{label} must be a safe relative POSIX path: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts) or ":" in parts[0]:
        raise _fail(f"{label} contains traversal or drive syntax: {value!r}")
    return value


def _inside_file(workspace_root: Path, value: Any, label: str) -> Path:
    """Resolve a relative or absolute path while rejecting symlink components."""

    root = workspace_root.resolve()
    candidate = Path(value)
    if candidate.is_absolute():
        raw = candidate
    else:
        rel = _relative(value, label)
        raw = root.joinpath(*rel.split("/"))
    try:
        raw_abs = raw.absolute()
        raw_abs.relative_to(root)
    except ValueError as exc:
        raise _fail(f"{label} escapes workspace: {value!r}") from exc
    current = root
    try:
        for part in raw_abs.relative_to(root).parts:
            current = current / part
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink: {value!r}")
        resolved = raw_abs.resolve(strict=True)
        resolved.relative_to(root)
        mode = resolved.stat().st_mode
    except LayoutCompatibilityError:
        raise
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} cannot resolve inside workspace: {value!r}: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise _fail(f"{label} is not a regular file: {value!r}")
    return resolved


def _inside_dir(workspace_root: Path, value: Any, label: str) -> Path:
    root = workspace_root.resolve()
    candidate = Path(value)
    raw = candidate if candidate.is_absolute() else root / _relative(value, label)
    try:
        raw_abs = raw.absolute()
        raw_abs.relative_to(root)
        current = root
        for part in raw_abs.relative_to(root).parts:
            current = current / part
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink: {value!r}")
        resolved = raw_abs.resolve(strict=True)
        resolved.relative_to(root)
        if not resolved.is_dir():
            raise _fail(f"{label} is not a directory: {value!r}")
        return resolved
    except LayoutCompatibilityError:
        raise
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} cannot resolve inside workspace: {value!r}: {exc}") from exc


def _assert_target_missing(site: Path, target_route: str) -> None:
    """Require the target route to be absent without following symlinked parents."""

    current = site
    try:
        for part in target_route.lstrip("/").split("/"):
            current = current / part
            if current.is_symlink():
                raise _fail(f"target route traverses a symlink: {target_route}")
        if current.exists():
            raise _fail(f"target route already exists and would be overwritten: {target_route}")
    except LayoutCompatibilityError:
        raise
    except OSError as exc:
        raise _fail(f"cannot inspect target route {target_route}: {exc}") from exc


def _route(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("/") or "\\" in value or "?" in value or "#" in value:
        raise _fail(f"{label} is not a clean absolute route: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts[1:]):
        raise _fail(f"{label} contains empty/traversal segments: {value!r}")
    return value


def _hash_checked(path: Path, expected: Any, expected_length: Any, label: str) -> tuple[bytes, str]:
    if not isinstance(expected, str) or not _SHA256_RE.fullmatch(expected):
        raise _fail(f"{label} SHA-256 is malformed")
    if not isinstance(expected_length, int) or expected_length < 0:
        raise _fail(f"{label} length is malformed")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    actual = _sha256(data)
    if actual != expected:
        raise _fail(f"{label} SHA mismatch: expected {expected}, got {actual}")
    if len(data) != expected_length:
        raise _fail(f"{label} length mismatch: expected {expected_length}, got {len(data)}")
    return data, actual


def _validate_image(data: bytes, entry: Mapping[str, Any], label: str) -> None:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required to validate {label}: {_PIL_IMPORT_ERROR}")
    expected_format = entry.get("format")
    expected_dimensions = entry.get("dimensions")
    expected_frames = entry.get("frames")
    if expected_format not in ("PNG", "GIF") or not isinstance(expected_dimensions, list) or len(expected_dimensions) != 2:
        raise _fail(f"{label} image metadata is malformed")
    if not all(isinstance(v, int) and v > 0 for v in expected_dimensions) or not isinstance(expected_frames, int) or expected_frames != 1:
        raise _fail(f"{label} image dimensions/frames are malformed")
    try:
        with Image.open(__import__("io").BytesIO(data)) as image:
            image.load()
            actual_format = image.format
            actual_size = list(image.size)
            actual_frames = getattr(image, "n_frames", 1)
    except Exception as exc:  # Pillow raises several format-specific errors
        raise _fail(f"{label} is not a decodable image: {exc}") from exc
    if actual_format != expected_format or actual_size != expected_dimensions or actual_frames != expected_frames:
        raise _fail(
            f"{label} image metadata mismatch: expected {expected_format} {expected_dimensions} frames={expected_frames}, "
            f"got {actual_format} {actual_size} frames={actual_frames}"
        )


def _public_record(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "page_route": entry["page_route"],
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


def load_layout_compatibility_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    source_site: str | Path,
    manifest_path: str | Path,
    manifest: Mapping[str, Any],
) -> LayoutCompatibilityBundle:
    """Validate the pinned ten-route reuse map and return public route records."""

    root = Path(workspace_root).resolve()
    map_file = _inside_file(root, map_path, "input map")
    map_data, map_bytes = _read_json(map_file, "input map")
    map_sha = _sha256(map_bytes)
    if map_sha != EXPECTED_MAP_SHA256:
        raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted Source16 layout map")
    if map_data.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("input map classification is not layout_compatibility_reuse")
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("input map source_manifest_sha256 is not the accepted Source16 manifest")
    entries = map_data.get("entries")
    if not isinstance(entries, list) or len(entries) != EXPECTED_ENTRY_COUNT:
        raise _fail(f"input map must contain exactly {EXPECTED_ENTRY_COUNT} entries")

    decision_rel = _relative(map_data.get("decision"), "decision path")
    decision_file = _inside_file(root, decision_rel, "decision path")
    decision_data, decision_bytes = _read_json(decision_file, "decision record")
    decision_sha = _sha256(decision_bytes)
    if decision_sha != EXPECTED_DECISION_SHA256 or map_data.get("decision_sha256") != decision_sha:
        raise _fail("decision SHA binding does not match the accepted decision")
    if decision_data.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision schema is not the accepted Source16 layout decision")
    if decision_data.get("accepted_for_compatibility_reuse") is not True:
        raise _fail("decision is not accepted for compatibility reuse")
    if decision_data.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("decision classification is not layout_compatibility_reuse")
    if decision_data.get("new_image_payloads") != 0 or decision_data.get("target_original_images_recovered") != 0:
        raise _fail("decision contains an unexpected new or original image payload")
    decision_targets = decision_data.get("targets")
    if decision_targets != entries:
        raise _fail("input map entries do not exactly match decision targets")

    manifest_file = _inside_file(root, manifest_path, "source manifest")
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
                binding_file = _inside_file(root, binding.get("path"), "decision manifest binding")
            except LayoutCompatibilityError:
                continue
            if binding_file == manifest_file:
                binding_ok = True
                break
    if not binding_ok:
        raise _fail("decision does not bind the accepted source manifest")

    site = _inside_dir(root, source_site, "source site")
    seen_targets: set[str] = set()
    seen_sources: set[str] = set()
    normalized_entries: list[dict[str, Any]] = []
    records_by_route = {
        row.get("route"): row for row in manifest_data.get("files", []) if isinstance(row, dict) and row.get("route")
    }
    if len(records_by_route) != len([row for row in manifest_data.get("files", []) if isinstance(row, dict) and row.get("route")]):
        raise _fail("source manifest contains duplicate route records")
    for raw in entries:
        if not isinstance(raw, dict):
            raise _fail("layout map entry must be an object")
        entry = dict(raw)
        target = _route(entry.get("target_route"), "target route")
        source = _route(entry.get("source_route"), "source route")
        expected = _EXPECTED_ENTRIES.get(target)
        if expected is None or entry.get("page_route") != expected["page_route"] or source != expected["source_route"]:
            raise _fail(f"entry is outside the exact accepted ten-route scope: {target}")
        if target in seen_targets or source in seen_sources:
            raise _fail("duplicate target or source route in layout map")
        seen_targets.add(target)
        seen_sources.add(source)
        if entry.get("classification") != EXPECTED_CLASSIFICATION:
            raise _fail(f"entry classification is not accepted: {target}")
        if entry.get("target_capture_timestamp") is not None:
            raise _fail(f"target capture timestamp must be null: {target}")
        if not isinstance(entry.get("source_capture_timestamp"), str) or not _TIMESTAMP_RE.fullmatch(entry["source_capture_timestamp"]):
            raise _fail(f"source capture timestamp is malformed: {target}")
        if entry.get("source_original_url") != _ROOT_ORIGIN + source:
            raise _fail(f"source original URL does not match source route: {target}")
        if entry.get("sha256") is None or not _SHA256_RE.fullmatch(str(entry.get("sha256"))):
            raise _fail(f"entry SHA is malformed: {target}")
        if not isinstance(entry.get("length"), int) or entry["length"] < 1:
            raise _fail(f"entry length is malformed: {target}")
        expected_format = entry.get("format")
        if expected_format not in ("PNG", "GIF"):
            raise _fail(f"entry format is not PNG/GIF: {target}")
        manifest_row = records_by_route.get(source)
        if not isinstance(manifest_row, dict):
            raise _fail(f"source route is missing from source manifest: {source}")
        for key, expected_value in (
            ("source_sha256", entry["sha256"]), ("derived_sha256", entry["sha256"]),
            ("source_length", entry["length"]), ("derived_length", entry["length"]),
            ("mime", f"image/{expected_format.lower()}"), ("source_mime", f"image/{expected_format.lower()}"),
            ("actual_timestamp", entry["source_capture_timestamp"]),
            ("source_base_url", entry["source_original_url"]),
        ):
            if manifest_row.get(key) != expected_value:
                raise _fail(f"manifest {key} drift for {source}")
        if manifest_row.get("transformed") is not False:
            raise _fail(f"source manifest marks {source} as transformed")
        _assert_target_missing(site, target)
        output_path = manifest_row.get("output_path")
        output_file = _inside_file(root, output_path, f"manifest output for {source}")
        expected_file = (site / source.lstrip("/")).resolve()
        if output_file != expected_file:
            raise _fail(f"manifest output does not match source site for {source}")
        source_file = _inside_file(site, source.lstrip("/"), f"source asset {source}")
        data, _ = _hash_checked(source_file, entry["sha256"], entry["length"], f"source asset {source}")
        _validate_image(data, entry, f"source asset {source}")
        dimensions = entry.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 2 or not all(isinstance(v, int) and v > 0 for v in dimensions):
            raise _fail(f"entry dimensions are malformed: {target}")
        normalized_entries.append(entry)

    if len(seen_targets) != EXPECTED_ENTRY_COUNT or seen_targets != set(_EXPECTED_ENTRIES):
        raise _fail("layout map does not cover the exact accepted target set")
    public = tuple(_public_record(entry) for entry in normalized_entries)
    by_page: dict[str, tuple[Mapping[str, Any], ...]] = {}
    for page in sorted({entry["page_route"] for entry in normalized_entries}):
        by_page[page] = tuple(record for record in public if record["page_route"] == page)
    return LayoutCompatibilityBundle(
        route_reuses={record["target_route"]: record["source_route"] for record in public},
        public_records=public,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_manifest_sha256=manifest_sha,
        per_page_records=by_page,
    )

