#!/usr/bin/env python3
"""Load the three accepted current ArchiveCraft encyclopedia illustrations.

The loader validates a pinned map, decision, source-acceptance record, and the
three local JPEG payloads.  It returns in-memory route reuses and a public
catalog; it never writes site files, imports ArchiveCraft pages, or treats the
images as recovered 2008 originals.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import html
import io
import json
import os
from pathlib import Path, PureWindowsPath
import stat
from typing import Any, Mapping

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - repository test runtime has Pillow
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class RelatedEncyclopediaImageError(ValueError):
    """Raised when the pinned three-image supplement is unsafe or drifted."""


EXPECTED_MAP_SHA256 = "2ca642c277733b345af25770ded42f6e5a949fbbab6ec872281f194cabddc3f4"
EXPECTED_DECISION_SHA256 = "118b85c721f8cb37e0caca92b48af28dd7b257731a301161549a3804bbb24dc8"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = "0af6e20a93d4915fcb19bc62dbd3b605592957bfcad0285ecff2266d99a54b3d"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_MAP_SCHEMA = "wow-related-encyclopedia-image-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-related-encyclopedia-image-decision/v1"
EXPECTED_ACCEPTANCE_SCHEMA = "wow-root-archivecraft-image-source-acceptance/v1"
EXPECTED_CLASSIFICATION = "current_related_archive_source"
EXPECTED_ENTRY_COUNT = 3
EXPECTED_CATALOG_RELATIVE = "__offline/related-encyclopedia-images.json"

EXPECTED_ENTRIES: tuple[Mapping[str, str], ...] = (
    {
        "page_route": "/info/encyclopedia/315.xml",
        "target_route": "/info/encyclopedia/images/articles/alleriawindrunner.jpg",
        "route": "/__offline/related-encyclopedia-images/alleriawindrunner.jpg",
    },
    {
        "page_route": "/info/encyclopedia/349.xml",
        "target_route": "/info/encyclopedia/images/articles/cenarioncircle.jpg",
        "route": "/__offline/related-encyclopedia-images/cenarioncircle.jpg",
    },
    {
        "page_route": "/info/encyclopedia/474.xml",
        "target_route": "/info/encyclopedia/images/articles/malfurionstormrage.jpg",
        "route": "/__offline/related-encyclopedia-images/malfurionstormrage.jpg",
    },
)


@dataclass(frozen=True)
class RelatedEncyclopediaAsset:
    """One exact JPEG payload and its old missing target route."""

    route: str
    relative: str
    target_route: str
    data: bytes
    mime: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedEncyclopediaImageBundle:
    """Validated image payloads, route reuses, notices, and public catalog."""

    assets: tuple[RelatedEncyclopediaAsset, ...]
    route_reuses: Mapping[str, str]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    notice_by_page: Mapping[str, str]
    map_sha256: str
    decision_sha256: str
    source_acceptance_sha256: str


def _fail(message: str) -> RelatedEncyclopediaImageError:
    return RelatedEncyclopediaImageError(message)


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
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a non-empty relative POSIX path")
    if "\x00" in value or "\\" in value or value.startswith("/") or PureWindowsPath(value).is_absolute():
        raise _fail(f"{label} must be a safe relative path")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts) or ":" in parts[0]:
        raise _fail(f"{label} contains traversal or drive syntax")
    return value


def _resolve_file(root: Path, value: Any, label: str) -> Path:
    relative = _safe_relative(value, label)
    current = root
    for part in relative.split("/"):
        current = current / part
        try:
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink")
        except OSError as exc:
            raise _fail(f"cannot inspect {label}: {exc}") from exc
    candidate = root.joinpath(*relative.split("/"))
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} is missing or escapes workspace") from exc
    try:
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise _fail(f"cannot stat {label}: {exc}") from exc
    if not stat.S_ISREG(mode) or resolved.is_symlink():
        raise _fail(f"{label} is not a regular non-symlink file")
    return resolved


def _resolve_map(root: Path, map_path: str | os.PathLike[str]) -> Path:
    candidate = Path(map_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise _fail("input map escapes workspace_root") from exc
        if candidate.is_symlink() or not resolved.is_file():
            raise _fail("input map is not a regular non-symlink file")
        return resolved
    return _resolve_file(root, candidate.as_posix(), "input map")


def _read_pinned(path: Path, expected: str, label: str) -> tuple[dict[str, Any], str]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read {label}: {exc}") from exc
    actual = _sha256(data)
    if actual != expected:
        raise _fail(f"{label} SHA mismatch: expected {expected}, got {actual}")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object")
    return value, actual


def _normalize_base_path(value: str) -> str:
    if not isinstance(value, str):
        raise _fail("base_path must be a string")
    if "?" in value or "#" in value or "\\" in value:
        raise _fail("base_path must not contain query, fragment, or backslash")
    if value in ("", "/"):
        return ""
    if not value.startswith("/"):
        raise _fail("base_path must start with '/'")
    parts = [part for part in value.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise _fail("base_path contains traversal")
    return "/" + "/".join(parts) + "/"


def _validated_utc(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _fail(f"{label} is missing")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail(f"{label} is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _fail(f"{label} must include a timezone")
    return value.strip()


def _validate_jpeg(data: bytes, entry: Mapping[str, Any], route: str) -> tuple[int, int, int]:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required to validate {route}: {_PIL_IMPORT_ERROR}")
    if entry.get("format") != "JPEG":
        raise _fail(f"{route} map format is not JPEG")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "JPEG":
                raise _fail(f"{route} payload is not JPEG")
            width, height = image.size
            frames = int(getattr(image, "n_frames", 1))
            if frames != 1:
                raise _fail(f"{route} has {frames} frames")
            image.load()
            image.convert("RGB").tobytes()
    except RelatedEncyclopediaImageError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable JPEG: {exc}") from exc
    if entry.get("width") != width or entry.get("height") != height or entry.get("frames") != frames:
        raise _fail(f"{route} map dimensions/frames do not match payload")
    return width, height, frames


def _entry_public(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key != "payload_path"}


def _validate_bindings(
    map_file: Path,
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    try:
        map_bytes = map_file.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read input map: {exc}") from exc
    map_sha = _sha256(map_bytes)
    if map_sha != EXPECTED_MAP_SHA256:
        raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
    try:
        map_data = json.loads(map_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail("input map is not valid UTF-8 JSON") from exc
    if not isinstance(map_data, dict) or map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted encyclopedia image map")
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
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("input map source manifest is not the accepted Source16 manifest")
    if decision.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision schema is not accepted")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA:
        raise _fail("source acceptance schema is not accepted")
    if decision.get("source_acceptance") != acceptance_rel or decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("decision source acceptance binding does not match")
    if not decision.get("accepted_for_browser_supplement"):
        raise _fail("decision is not accepted for browser supplement")
    if not acceptance.get("accepted_sources"):
        raise _fail("source acceptance is not accepted")
    if map_data.get("source_label") != "ArchiveCraft community archive":
        raise _fail("source label is not the accepted ArchiveCraft source")
    if decision.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("decision classification is not current_related_archive_source")
    if decision.get("original_2008_images_recovered") != 0 or acceptance.get("historical_original_images_recovered") != 0:
        raise _fail("source records claim recovered 2008 images")
    if not isinstance(map_data.get("entries"), list) or len(map_data["entries"]) != EXPECTED_ENTRY_COUNT:
        raise _fail("input map does not contain exactly three entries")
    if not isinstance(decision.get("targets"), list) or decision["targets"] != [
        _entry_public(entry) for entry in map_data["entries"]
    ]:
        raise _fail("decision targets do not exactly match map entries")
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


def _make_notice(source_page_url: str) -> str:
    source_url = html.escape(source_page_url, quote=True)
    return (
        '<aside id="__offline-related-encyclopedia-images" role="note" '
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
    assets: list[RelatedEncyclopediaAsset],
    source_metadata: Mapping[str, Any],
) -> bytes:
    payload = {
        "schema": "wow-related-encyclopedia-image-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "source": dict(source_metadata),
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
                "source_processing_note": asset.metadata["source_processing_note"],
            }
            for asset in assets
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_related_encyclopedia_image_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedEncyclopediaImageBundle:
    """Validate and load the exact three current related encyclopedia JPEGs."""

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map(root, map_path)
    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha = _validate_bindings(map_file, root)
    entries = map_data["entries"]
    entry_by_target = {entry.get("target_route"): entry for entry in entries}
    if set(entry_by_target) != {item["target_route"] for item in EXPECTED_ENTRIES}:
        raise _fail("map target routes are outside the exact three-image scope")
    if len(entry_by_target) != EXPECTED_ENTRY_COUNT:
        raise _fail("duplicate encyclopedia target route")

    acceptance_records = acceptance.get("records")
    if not isinstance(acceptance_records, list):
        raise _fail("source acceptance records are missing")
    records_by_url = {
        record.get("url"): record
        for record in acceptance_records
        if isinstance(record, dict) and record.get("url")
    }
    assets: list[RelatedEncyclopediaAsset] = []
    route_reuses: dict[str, str] = {}
    seen_routes: set[str] = set()
    source_bytes = 0
    for expected in EXPECTED_ENTRIES:
        entry = entry_by_target[expected["target_route"]]
        if any(entry.get(key) != value for key, value in expected.items()):
            raise _fail(f"entry does not match exact accepted route: {expected['target_route']}")
        if entry.get("classification") != EXPECTED_CLASSIFICATION:
            raise _fail(f"{expected['target_route']} classification is not accepted")
        if entry.get("original_capture_timestamp") is not None:
            raise _fail(f"{expected['target_route']} has an original capture timestamp")
        route = str(entry["route"])
        relative = _safe_relative(route[1:], f"canonical route {route}") if route.startswith("/") else _safe_relative(route, "canonical route")
        if route in seen_routes or relative in seen_routes:
            raise _fail(f"duplicate canonical route: {route}")
        seen_routes.add(route)
        payload_file = _resolve_file(root, entry.get("payload_path"), f"payload {route}")
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read payload for {route}: {exc}") from exc
        if not isinstance(entry.get("length"), int) or len(data) != entry["length"]:
            raise _fail(f"{route} length mismatch")
        actual_sha = _sha256(data)
        if actual_sha != entry.get("sha256"):
            raise _fail(f"{route} SHA mismatch: expected {entry.get('sha256')}, got {actual_sha}")
        width, height, frames = _validate_jpeg(data, entry, route)
        source_record = records_by_url.get(entry.get("source_image_url"))
        if not isinstance(source_record, dict):
            raise _fail(f"{route} has no source acceptance record")
        for key in ("source_image_url", "source_page_url", "current_observed_utc", "sha256", "length"):
            source_key = "url" if key == "source_image_url" else ("body_sha256" if key == "sha256" else ("body_bytes" if key == "length" and "body_bytes" in source_record else "content_length" if key == "length" else key))
            expected_value = entry.get(key)
            actual_value = source_record.get(source_key)
            if expected_value != actual_value:
                raise _fail(f"{route} source acceptance {key} does not match map")
        if source_record.get("valid") is not True or source_record.get("http_status") != 200:
            raise _fail(f"{route} source acceptance is not a valid HTTP image")
        if source_record.get("content_type") != "image/jpeg" or source_record.get("format") != "JPEG":
            raise _fail(f"{route} source acceptance is not JPEG")
        _validated_utc(entry.get("current_observed_utc"), f"{route} current_observed_utc")
        if source_record.get("current_response_is_not_historical_capture") is not True:
            raise _fail(f"{route} source is incorrectly presented as historical capture")
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
            "source_processing_note": entry.get("source_processing_note"),
        }
        asset = RelatedEncyclopediaAsset(
            route=route,
            relative=relative,
            target_route=entry["target_route"],
            data=data,
            mime="image/jpeg",
            metadata=metadata,
        )
        assets.append(asset)
        route_reuses[asset.target_route] = asset.route
        source_bytes += len(data)

    notice_by_page = {
        str(entry["page_route"]): _make_notice(str(entry["source_page_url"]))
        for entry in entries
    }
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
    }
    catalog_bytes = _make_catalog(base_path=normalized_base, assets=assets, source_metadata=source_metadata)
    return RelatedEncyclopediaImageBundle(
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
    "EXPECTED_DECISION_SCHEMA",
    "EXPECTED_DECISION_SHA256",
    "EXPECTED_ENTRIES",
    "EXPECTED_ENTRY_COUNT",
    "EXPECTED_MAP_SCHEMA",
    "EXPECTED_MAP_SHA256",
    "EXPECTED_SOURCE_ACCEPTANCE_SHA256",
    "EXPECTED_SOURCE_MANIFEST_SHA256",
    "RelatedEncyclopediaAsset",
    "RelatedEncyclopediaImageBundle",
    "RelatedEncyclopediaImageError",
    "load_related_encyclopedia_image_bundle",
]
