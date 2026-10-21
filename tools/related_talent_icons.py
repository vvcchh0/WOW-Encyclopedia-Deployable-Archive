#!/usr/bin/env python3
"""Load the accepted, same-path talent-icon supplement.

This module is intentionally a loader, rather than an exporter.  It validates
the pinned input map and its two acceptance records, reads only the private
payloads named by that map, and returns immutable-ish in-memory records for a
caller that already owns the Pages export policy.  It never writes site files,
executes the calculator, imports WotLK data files, or guesses an icon from a
different class/tree.
"""

from __future__ import annotations

import hashlib
import html
import io
import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - the repository test runtime has Pillow
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class RelatedTalentIconError(ValueError):
    """Raised when the pinned icon map or a private payload is unsafe/drifted."""


EXPECTED_MAP_SHA256 = "db2295c57b336be03b1fcccdb5a86373e4e95047b4be8e56647a1c2c95970092"
EXPECTED_DECISION_SHA256 = "a9c54b3552dba1d19415b3814b44fae65b667b7c81922d37835dc4aebd31daf6"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = "4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465"

EXPECTED_REPOSITORY_URL = "https://github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a"
EXPECTED_COMMIT_SHA = "4c8013cf40d0edf84625430eaf43b86d97880ae0"
EXPECTED_TREE_SHA = "e8916c038b41c2c29144f5411f8fc6ec5cd032d5"
EXPECTED_CLASSIFICATION = "later_related_source"
EXPECTED_ICON_COUNT = 986
EXPECTED_TOTAL_BYTES = 1_038_389
EXPECTED_CATALOG_RELATIVE = "__offline/related-talent-icons.json"
EXPECTED_MAP_SCHEMA = "wow-related-talent-icon-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-root-related-talent-icon-integration-decision/v1"
EXPECTED_ACCEPTANCE_SCHEMA = "wow-root-related-talent-source-acceptance/v1"

ALLOWED_CLASSES = (
    "druid",
    "hunter",
    "mage",
    "paladin",
    "priest",
    "rogue",
    "shaman",
    "warlock",
    "warrior",
)

_ROUTE_RE = re.compile(
    r"^/shared/global/talents/(?P<class>" + "|".join(ALLOWED_CLASSES) + r")/images/"
    r"(?P<tree>[^/]+)/(?P<filename>[^/]+\.jpg)$"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class RelatedTalentAsset:
    """One validated same-path JPEG and the public provenance needed by callers."""

    route: str
    relative: str
    data: bytes
    mime: str
    source_refs: tuple[str, ...]
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedTalentBundle:
    """Validated assets plus a public catalog, without private payload paths."""

    assets: tuple[RelatedTalentAsset, ...]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    per_class_counts: Mapping[str, int]
    notice_html: str
    map_sha256: str
    decision_sha256: str
    source_acceptance_sha256: str


def _fail(message: str) -> RelatedTalentIconError:
    return RelatedTalentIconError(message)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object: {path}")
    return value


def _normal_relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a non-empty relative POSIX path")
    if "\x00" in value or "\\" in value:
        raise _fail(f"{label} contains NUL or backslash: {value!r}")
    if value.startswith("/") or PureWindowsPath(value).is_absolute():
        raise _fail(f"{label} must be relative: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise _fail(f"{label} contains an empty/dot/traversal segment: {value!r}")
    if ":" in parts[0]:
        raise _fail(f"{label} contains a drive-like segment: {value!r}")
    return value


def _resolve_workspace_file(workspace_root: Path, relative: Any, label: str) -> Path:
    rel = _normal_relative(relative, label)
    root = workspace_root.resolve()
    raw = root.joinpath(*rel.split("/"))

    # Check every component before resolving so a symlink cannot silently turn
    # an apparently safe map path into a file outside the workspace.
    current = root
    for part in rel.split("/"):
        current = current / part
        try:
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink: {relative!r}")
        except OSError as exc:
            raise _fail(f"cannot inspect {label}: {relative!r}: {exc}") from exc

    try:
        resolved = raw.resolve(strict=True)
    except OSError as exc:
        raise _fail(f"{label} does not resolve inside workspace: {relative!r}: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise _fail(f"{label} escapes workspace: {relative!r}") from exc
    try:
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise _fail(f"cannot stat {label}: {relative!r}: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise _fail(f"{label} is not a regular file: {relative!r}")
    return resolved


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha1_git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _read_hash_checked(path: Path, expected: Any, label: str) -> tuple[bytes, str]:
    if not isinstance(expected, str) or not _SHA256_RE.fullmatch(expected):
        raise _fail(f"{label} expected SHA-256 is malformed")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    actual = _sha256(data)
    if actual != expected:
        raise _fail(f"{label} SHA mismatch: expected {expected}, got {actual}")
    return data, actual


def _normalize_base_path(base_path: str) -> str:
    if not isinstance(base_path, str):
        raise _fail("base_path must be a string")
    if "?" in base_path or "#" in base_path or "\\" in base_path:
        raise _fail("base_path must not contain query, fragment, or backslash")
    if base_path in ("", "/"):
        return ""
    if not base_path.startswith("/"):
        raise _fail("base_path must be empty or start with '/'")
    normalized = "/" + "/".join(part for part in base_path.split("/") if part)
    return normalized.rstrip("/")


def _validated_retrieved_utc(value: Any) -> str:
    """Return the pinned source download time only when it carries a timezone."""

    if not isinstance(value, str) or not value.strip():
        raise _fail("source downloaded_utc is missing")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail("source downloaded_utc is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _fail("source downloaded_utc must include a timezone")
    return parsed.isoformat()


def _public_asset_url(base_path: str, route: str) -> str:
    return f"{base_path}{route}" if base_path else route


def _validate_bindings(
    map_path: Path,
    workspace_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    try:
        map_data_bytes = map_path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read input map: {map_path}: {exc}") from exc
    map_sha = _sha256(map_data_bytes)
    if map_sha != EXPECTED_MAP_SHA256:
        raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
    try:
        map_data = json.loads(map_data_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"input map is not valid UTF-8 JSON: {map_path}: {exc}") from exc
    if not isinstance(map_data, dict):
        raise _fail("input map must be a JSON object")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted related-talent-icon map")

    decision_rel = _normal_relative(map_data.get("decision"), "decision path")
    acceptance_rel = _normal_relative(map_data.get("source_acceptance"), "source acceptance path")
    decision_path = _resolve_workspace_file(workspace_root, decision_rel, "decision path")
    acceptance_path = _resolve_workspace_file(workspace_root, acceptance_rel, "source acceptance path")
    decision_bytes, decision_sha = _read_hash_checked(
        decision_path, EXPECTED_DECISION_SHA256, "decision record"
    )
    acceptance_bytes, acceptance_sha = _read_hash_checked(
        acceptance_path, EXPECTED_SOURCE_ACCEPTANCE_SHA256, "source acceptance record"
    )
    decision = _read_json(decision_path, "decision record")
    acceptance = _read_json(acceptance_path, "source acceptance record")

    if map_data.get("decision_sha256") != decision_sha:
        raise _fail("input map decision_sha256 does not match decision record")
    if map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("input map source_acceptance_sha256 does not match acceptance record")
    if decision.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision record schema is not the accepted related-talent decision")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA:
        raise _fail("source acceptance schema is not the accepted related-talent record")
    if decision.get("source_acceptance") != acceptance_rel:
        raise _fail("decision record points at a different source acceptance path")
    if decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("decision record source_acceptance_sha256 does not match acceptance record")
    if not decision.get("accepted_for_browser_supplement"):
        raise _fail("decision record is not accepted for browser supplement")
    if not acceptance.get("accepted_source"):
        raise _fail("source acceptance record is not accepted")

    source = map_data.get("source")
    if not isinstance(source, dict):
        raise _fail("input map source must be an object")
    for label, actual in (
        ("repository_url", EXPECTED_REPOSITORY_URL),
        ("commit_sha", EXPECTED_COMMIT_SHA),
        ("tree_sha", EXPECTED_TREE_SHA),
    ):
        if source.get(label) != actual or acceptance.get(label) != actual:
            raise _fail(f"source {label} is not pinned to the accepted repository")
    if source.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("input map source classification is not later_related_source")
    if source.get("original_capture_timestamp") is not None:
        raise _fail("input map source has an unexpected original capture timestamp")
    if decision.get("original_capture_timestamp") is not None:
        raise _fail("decision record has an unexpected original capture timestamp")
    if acceptance.get("original_2008_images_recovered") != 0:
        raise _fail("source acceptance claims recovered 2008 images")
    if decision.get("original_2008_images_recovered") != 0:
        raise _fail("decision record claims recovered 2008 images")
    if acceptance.get("published_images") != 0:
        raise _fail("source acceptance unexpectedly marks images as published")

    expected_count = EXPECTED_ICON_COUNT
    if map_data.get("icon_count") != expected_count:
        raise _fail(f"input map icon_count is not {expected_count}")
    if decision.get("accepted_icon_count") != expected_count:
        raise _fail("decision accepted_icon_count does not match the pinned icon count")
    if acceptance.get("strict_36px_same_path_icon_candidates") != expected_count:
        raise _fail("source acceptance candidate count does not match the pinned icon count")
    if not isinstance(map_data.get("entries"), list) or len(map_data["entries"]) != expected_count:
        raise _fail("input map entries do not match the pinned icon count")

    # Keep these variables explicitly consumed so a future refactor cannot
    # accidentally omit the hash-checked bytes from the binding path.
    del decision_bytes, acceptance_bytes
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


def _validate_image(data: bytes, entry: Mapping[str, Any], route: str) -> tuple[int, int, int]:
    if Image is None:  # pragma: no cover - guarded by the environment setup
        raise _fail(f"Pillow is required to validate {route}: {_PIL_IMPORT_ERROR}")
    if entry.get("format") != "JPEG":
        raise _fail(f"{route} map format is not JPEG")
    try:
        with Image.open(io.BytesIO(data)) as image:
            actual_format = image.format
            width, height = image.size
            frame_count = int(getattr(image, "n_frames", 1))
            if actual_format != "JPEG":
                raise _fail(f"{route} payload decodes as {actual_format}, not JPEG")
            if frame_count != 1:
                raise _fail(f"{route} has {frame_count} frames, expected one")
            for frame_index in range(frame_count):
                image.seek(frame_index)
                image.load()
                image.convert("RGB").tobytes()
    except RelatedTalentIconError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable JPEG: {exc}") from exc
    if (width, height) != (36, 36):
        raise _fail(f"{route} dimensions are {width}x{height}, expected 36x36")
    if entry.get("width") != 36 or entry.get("height") != 36 or entry.get("frames") != 1:
        raise _fail(f"{route} map dimensions/frames are not 36x36/1")
    return width, height, frame_count


def _validate_route(entry: Mapping[str, Any]) -> tuple[str, str, str]:
    route = entry.get("route")
    repository_path = entry.get("repository_path")
    if not isinstance(route, str) or not route:
        raise _fail("each icon entry needs a route")
    if any(token in route for token in ("?", "#", "\\", "\x00")):
        raise _fail(f"unsafe icon route: {route!r}")
    route_parts = route[1:].split("/")
    if any(part in ("", ".", "..") for part in route_parts):
        raise _fail(f"icon route contains an empty/dot/traversal segment: {route!r}")
    match = _ROUTE_RE.fullmatch(route)
    if match is None:
        raise _fail(f"icon route is outside the exact same-path scope: {route!r}")
    if repository_path != route[1:]:
        raise _fail(f"repository_path does not exactly equal route without leading slash: {route!r}")
    filename = match.group("filename")
    if filename.lower() == "background.jpg":
        raise _fail(f"long tree background is excluded from the icon bundle: {route!r}")
    relative = route[1:]
    return route, relative, match.group("class")


def _make_notice(base_path: str) -> str:
    catalog_url = f"{base_path}/{EXPECTED_CATALOG_RELATIVE}" if base_path else f"/{EXPECTED_CATALOG_RELATIVE}"
    safe_url = html.escape(catalog_url, quote=True)
    return (
        '<p id="related-talent-icons-notice" role="note">'
        "Talent data: 2008 archive. Some icons are supplied by a later WotLK "
        "3.3.5a calculator backup. "
        f'<a href="{safe_url}">Source catalog.</a></p>'
    )


def _make_catalog(
    *,
    base_path: str,
    assets: list[RelatedTalentAsset],
    source_metadata: Mapping[str, Any],
    per_class_counts: Mapping[str, int],
    notice_html: str,
) -> bytes:
    # The catalog is deliberately a public whitelist.  In particular, it does
    # not contain payload_path, zip/HTTP metadata, private capture details, or
    # any source acceptance record paths.
    payload = {
        "schema": "wow-related-talent-icon-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "notice_html": notice_html,
        "source": dict(source_metadata),
        "icon_count": len(assets),
        "class_counts": dict(per_class_counts),
        "assets": [
            {
                "route": asset.route,
                "relative": asset.relative,
                "url": _public_asset_url(base_path, asset.route),
                "mime": asset.mime,
                "sha256": asset.metadata["sha256"],
                "length": asset.metadata["length"],
                "width": asset.metadata["width"],
                "height": asset.metadata["height"],
                "frames": asset.metadata["frames"],
            }
            for asset in assets
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def load_related_talent_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedTalentBundle:
    """Validate and load the accepted 986-image related talent icon bundle.

    ``map_path`` and all payload paths are resolved beneath ``workspace_root``.
    The returned ``relative`` values are site-relative paths without a leading
    slash; ``route`` values retain the exact original leading slash.  No files
    are written by this function.
    """

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    requested_map = Path(map_path)
    if requested_map.is_absolute():
        if requested_map.is_symlink():
            raise _fail("input map is a symlink")
        map_file = requested_map.resolve()
    else:
        map_file = _resolve_workspace_file(root, requested_map.as_posix(), "input map")
    # Absolute map paths are still required to be inside workspace_root.
    try:
        map_file.relative_to(root)
    except ValueError as exc:
        raise _fail("input map escapes workspace_root") from exc
    if not map_file.is_file() or map_file.is_symlink():
        raise _fail("input map is not a regular non-symlink file")

    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha = _validate_bindings(
        map_file, root
    )
    source = map_data["source"]
    assets: list[RelatedTalentAsset] = []
    routes: set[str] = set()
    relatives: set[str] = set()
    per_class_counts = {name: 0 for name in ALLOWED_CLASSES}
    source_bytes = 0

    for index, raw_entry in enumerate(map_data["entries"]):
        if not isinstance(raw_entry, dict):
            raise _fail(f"icon entry {index} is not an object")
        route, relative, class_name = _validate_route(raw_entry)
        if route in routes or relative in relatives:
            raise _fail(f"duplicate icon route/relative path: {route!r}")
        routes.add(route)
        relatives.add(relative)
        payload_file = _resolve_workspace_file(root, raw_entry.get("payload_path"), f"payload {route}")
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read payload for {route}: {exc}") from exc
        expected_length = raw_entry.get("length")
        if not isinstance(expected_length, int) or expected_length < 0:
            raise _fail(f"{route} map length is malformed")
        if len(data) != expected_length:
            raise _fail(f"{route} length mismatch: expected {expected_length}, got {len(data)}")
        expected_sha = raw_entry.get("sha256")
        if not isinstance(expected_sha, str) or not _SHA256_RE.fullmatch(expected_sha):
            raise _fail(f"{route} map SHA-256 is malformed")
        actual_sha = _sha256(data)
        if actual_sha != expected_sha:
            raise _fail(f"{route} SHA mismatch: expected {expected_sha}, got {actual_sha}")
        expected_blob = raw_entry.get("git_blob_sha1")
        if not isinstance(expected_blob, str) or not _SHA1_RE.fullmatch(expected_blob):
            raise _fail(f"{route} git blob SHA-1 is malformed")
        actual_blob = _sha1_git_blob(data)
        if actual_blob != expected_blob:
            raise _fail(f"{route} git blob SHA mismatch: expected {expected_blob}, got {actual_blob}")
        width, height, frames = _validate_image(data, raw_entry, route)
        metadata = {
            "sha256": actual_sha,
            "length": len(data),
            "git_blob_sha1": actual_blob,
            "width": width,
            "height": height,
            "frames": frames,
            "format": "JPEG",
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
        assets.append(
            RelatedTalentAsset(
                route=route,
                relative=relative,
                data=data,
                mime="image/jpeg",
                source_refs=(
                    str(source["repository_url"]),
                    f"commit:{source['commit_sha']}",
                    f"tree:{source['tree_sha']}",
                ),
                metadata=metadata,
            )
        )
        per_class_counts[class_name] += 1
        source_bytes += len(data)

    if source_bytes != EXPECTED_TOTAL_BYTES:
        raise _fail(
            f"loaded payload bytes do not match accepted total: expected {EXPECTED_TOTAL_BYTES}, got {source_bytes}"
        )

    retrieved_utc = _validated_retrieved_utc(source.get("downloaded_utc"))
    source_metadata: dict[str, Any] = {
        "repository_url": source["repository_url"],
        "commit_sha": source["commit_sha"],
        "tree_sha": source["tree_sha"],
        "classification": EXPECTED_CLASSIFICATION,
        "retrieved_utc": retrieved_utc,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "icon_count": len(assets),
        "map_sha256": map_sha,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
    }
    notice_html = _make_notice(normalized_base)
    catalog_bytes = _make_catalog(
        base_path=normalized_base,
        assets=assets,
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=notice_html,
    )
    estimated_bytes = source_bytes + len(catalog_bytes)
    return RelatedTalentBundle(
        assets=tuple(assets),
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=estimated_bytes,
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=notice_html,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


__all__ = [
    "ALLOWED_CLASSES",
    "EXPECTED_CATALOG_RELATIVE",
    "RelatedTalentAsset",
    "RelatedTalentBundle",
    "RelatedTalentIconError",
    "load_related_talent_bundle",
]
