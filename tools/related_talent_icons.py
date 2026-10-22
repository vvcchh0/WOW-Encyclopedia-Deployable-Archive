#!/usr/bin/env python3
"""Load the accepted same-class talent-icon supplements.

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

# Keep the original v1 contract above unchanged.  v2 layers twenty explicit
# same-class artwork mappings over that accepted 986-image bundle.
EXPECTED_V2_MAP_SHA256 = "dbf7e69a081d6769e243c7c8688b46181204102c58a9c933b6388c5197b67d9b"
EXPECTED_V2_DECISION_SHA256 = "eeb4706b46d4c5e71015e993bb7b79220d70d44d0201351f2dceb199861d7d24"
EXPECTED_V2_AUDIT_SHA256 = "fe8b6dfb6229e6c63eefafef778cffaa205b40fca9e8652389f823f64f98b520"
EXPECTED_V2_BASE_MAP_SHA256 = EXPECTED_MAP_SHA256
EXPECTED_V2_MAP_SCHEMA = "wow-related-talent-icon-map/v2"
EXPECTED_V2_DECISION_SCHEMA = "wow-related-talent-icon-decision/v2"
EXPECTED_V2_AUDIT_SCHEMA = "wow-talent-icon-reuse-audit/v1"
EXPECTED_V2_MAP_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v55/input-map.json"
)
EXPECTED_V2_DECISION_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v55/decision.json"
)
EXPECTED_V2_PINS_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v55/root-input-pins.json"
)
EXPECTED_V2_ACCEPTANCE_RELATIVE = (
    "research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json"
)
EXPECTED_V2_AUDIT_RELATIVE = (
    "research/continuous-recovery-20261022/talent-icon-reuse-audit/audit.json"
)
EXPECTED_V2_BASE_MAP_RELATIVE = (
    "research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json"
)
EXPECTED_V2_BASE_ICON_COUNT = 986
EXPECTED_V2_MAPPED_ICON_COUNT = 20
EXPECTED_V2_ICON_COUNT = 1006
EXPECTED_V2_MAPPED_SOURCE_BYTES = 21820
EXPECTED_V2_TOTAL_SOURCE_BYTES = EXPECTED_TOTAL_BYTES + EXPECTED_V2_MAPPED_SOURCE_BYTES
EXPECTED_V2_SOURCE = {
    "repository_url": EXPECTED_REPOSITORY_URL,
    "commit_sha": EXPECTED_COMMIT_SHA,
    "tree_sha": EXPECTED_TREE_SHA,
    "zip_url": (
        "https://codeload.github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a/zip/"
        "4c8013cf40d0edf84625430eaf43b86d97880ae0"
    ),
    "zip_sha256": "52cd20ed7509943d5a386c95888686f8ea043c051cb367d8efe779b2a191095f",
    "downloaded_utc": "2026-10-21T04:39:55.289652+00:00",
    "original_capture_timestamp": None,
    "classification": EXPECTED_CLASSIFICATION,
}
EXPECTED_V2_ROOT_PINS = {
    "map_sha256": EXPECTED_V2_MAP_SHA256,
    "decision_sha256": EXPECTED_V2_DECISION_SHA256,
    "base_map_sha256": EXPECTED_V2_BASE_MAP_SHA256,
    "semantic_audit_sha256": EXPECTED_V2_AUDIT_SHA256,
    "source_acceptance_sha256": EXPECTED_SOURCE_ACCEPTANCE_SHA256,
    "base_icon_count": EXPECTED_V2_BASE_ICON_COUNT,
    "mapped_icon_count": EXPECTED_V2_MAPPED_ICON_COUNT,
    "icon_count": EXPECTED_V2_ICON_COUNT,
    "mapped_source_bytes": EXPECTED_V2_MAPPED_SOURCE_BYTES,
    "new_network_requests": 0,
    "images_reencoded": False,
}

# v3 adds eighteen reviewed exact-title, same-class images on top of v2's
# 1,006 assets.  The raw Source16 data digest and the already-derived v55
# response digest are intentionally separate: the latter contains the
# pre-existing talentPath rewrite and is the expected browser response.
EXPECTED_V3_MAP_SHA256 = "ea6d4656a6bc35329fb400bf38c645172d43db0f34b11963787311341db2faa7"
EXPECTED_V3_DECISION_SHA256 = "0e22840852a79d52979f78535b00ae223547705a7ecec7f24bea299c0ce0b0d9"
EXPECTED_V3_ROOT_ACCEPTANCE_SHA256 = "b707e455f96da67a1426ecd2f6a12bbae93187f9bbfc8e0e9a67b93d38ab2e4d"
EXPECTED_V3_PREPARATION_SHA256 = "b5ebf6066d084f6dcda06cc78e4bc4e39114e1e0cfd3e29fb4c8ab38ad38826d"
EXPECTED_V3_AUDIT_SHA256 = "16629cb29bfc945a2843b9ee5dbbaf5765c28bfc2ce4afb0715992d922a571f3"
EXPECTED_V3_BASE_MAP_SHA256 = EXPECTED_V2_MAP_SHA256
EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256 = EXPECTED_SOURCE_ACCEPTANCE_SHA256
EXPECTED_V3_MAP_SCHEMA = "wow-related-talent-icon-map/v3"
EXPECTED_V3_DECISION_SCHEMA = "wow-root-related-talent-icons-v56-decision/v1"
EXPECTED_V3_ROOT_ACCEPTANCE_SCHEMA = "wow-root-talent-v56-source-acceptance/v1"
EXPECTED_V3_PREPARATION_SCHEMA = "wow-related-talent-icon-source-preparation/v1"
EXPECTED_V3_AUDIT_SCHEMA = "wow-talent-icon-remaining-audit/v1"
EXPECTED_V3_MAP_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v56/input-map.json"
)
EXPECTED_V3_DECISION_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v56/decision.json"
)
EXPECTED_V3_PINS_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v56/root-input-pins.json"
)
EXPECTED_V3_ROOT_ACCEPTANCE_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v56/root-source-acceptance.json"
)
EXPECTED_V3_PREPARATION_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-icons-v56/source-preparation.json"
)
EXPECTED_V3_AUDIT_RELATIVE = (
    "research/continuous-recovery-20261022/talent-icon-remaining-audit/audit.json"
)
EXPECTED_V3_SOURCE_ACCEPTANCE_RELATIVE = EXPECTED_V2_ACCEPTANCE_RELATIVE
EXPECTED_V3_BASE_MAP_RELATIVE = EXPECTED_V2_MAP_RELATIVE
EXPECTED_V3_BASE_ICON_COUNT = 1006
EXPECTED_V3_BASE_MAPPED_ICON_COUNT = 20
EXPECTED_V3_MAPPED_ICON_COUNT = 18
EXPECTED_V3_ICON_COUNT = 1024
EXPECTED_V3_MAPPED_SOURCE_BYTES = 19439
EXPECTED_V3_BASE_SOURCE_BYTES = EXPECTED_V2_TOTAL_SOURCE_BYTES
EXPECTED_V3_TOTAL_SOURCE_BYTES = EXPECTED_V3_BASE_SOURCE_BYTES + EXPECTED_V3_MAPPED_SOURCE_BYTES
EXPECTED_V3_SELECTED_IDS = (
    "mage-molten-shields",
    "paladin-guardian-s-favor",
    "rogue-dirty-tricks",
    "rogue-puncturing-wounds",
    "shaman-earth-s-grasp",
    "warrior-death-wish",
    "warrior-improved-disciplines",
    "warrior-improved-slam",
    "warrior-improved-thunder-clap",
)
EXPECTED_V3_CLASS_DELTAS = {
    "druid": 0,
    "hunter": 0,
    "mage": 2,
    "paladin": 2,
    "priest": 0,
    "rogue": 4,
    "shaman": 2,
    "warlock": 0,
    "warrior": 8,
}
EXPECTED_V3_ROOT_PINS = {
    "schema": "wow-related-talent-icons-v56-root-pins/v1",
    "map_sha256": EXPECTED_V3_MAP_SHA256,
    "decision_sha256": EXPECTED_V3_DECISION_SHA256,
    "root_source_acceptance_sha256": EXPECTED_V3_ROOT_ACCEPTANCE_SHA256,
    "source_preparation_sha256": EXPECTED_V3_PREPARATION_SHA256,
    "semantic_audit_sha256": EXPECTED_V3_AUDIT_SHA256,
    "source_acceptance_sha256": EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256,
    "base_map_sha256": EXPECTED_V3_BASE_MAP_SHA256,
    "base_icon_count": EXPECTED_V3_BASE_ICON_COUNT,
    "mapped_icon_count": EXPECTED_V3_MAPPED_ICON_COUNT,
    "icon_count": EXPECTED_V3_ICON_COUNT,
    "mapped_source_bytes": EXPECTED_V3_MAPPED_SOURCE_BYTES,
    "new_network_requests": 0,
    "images_reencoded": False,
}
EXPECTED_V3_SOURCE = EXPECTED_V2_SOURCE
EXPECTED_V3_V55_EXPORT_RELATIVE = (
    ".scratch/pages-resources-20261022-v55"
)

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


def _load_v1_related_talent_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedTalentBundle:
    """Validate and load the accepted v1 986-image talent icon bundle.

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


def _read_v2_bound_json(path: Path, expected_sha: str, label: str) -> tuple[dict[str, Any], str]:
    raw, actual = _read_hash_checked(path, expected_sha, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"{label} is not valid UTF-8 JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object: {path}")
    return value, actual


def _validate_v2_entry_semantics(
    entry: Mapping[str, Any],
    recommendation: Mapping[str, Any],
    state: str,
) -> tuple[str, str, str]:
    route = entry.get("route")
    repo_path = entry.get("repository_path")
    class_name = entry.get("class")
    if not isinstance(route, str) or any(token in route for token in ("?", "#", "\\", "\x00")):
        raise _fail(f"unsafe v2 target route: {route!r}")
    match = _ROUTE_RE.fullmatch(route)
    if match is None:
        raise _fail(f"v2 target route is outside the exact talent icon scope: {route!r}")
    if class_name != match.group("class"):
        raise _fail(f"v2 target route crosses talent classes: {route!r}")
    expected_target = recommendation["old_target"]
    if class_name != expected_target.get("class") or entry.get("talent") != expected_target.get("talent"):
        raise _fail(f"v2 semantic mapping does not match its old same-class talent: {route}")
    target_routes = expected_target.get("routes")
    if not isinstance(target_routes, list) or route not in target_routes:
        raise _fail(f"v2 route is not listed in its same-class audit target: {route}")
    if not isinstance(repo_path, str):
        raise _fail(f"v2 source repository path is missing: {route}")
    repo_path = _normal_relative(repo_path, f"v2 source repository path for {route}")
    expected_prefix = f"shared/global/talents/{class_name}/images/"
    if not repo_path.startswith(expected_prefix) or not repo_path.lower().endswith(".jpg"):
        raise _fail(f"v2 source path does not remain within the target class: {repo_path!r}")
    later_images = recommendation.get("later_images")
    if not isinstance(later_images, list):
        raise _fail(f"semantic audit lacks later image evidence for {route}")
    evidence_by_state = {
        str(image.get("state")): image.get("evidence_id")
        for image in later_images
        if isinstance(image, dict)
    }
    if evidence_by_state.get(state) != repo_path:
        raise _fail(f"v2 source path is not the exact same-class audit image for {route}")
    if entry.get("mapping_id") != recommendation.get("id"):
        raise _fail(f"v2 mapping_id does not match its semantic audit record: {route}")
    if entry.get("mapping_reason") != recommendation.get("reason"):
        raise _fail(f"v2 mapping reason differs from the accepted semantic audit: {route}")

    old_data = expected_target.get("old_data_evidence")
    later_talent = recommendation.get("later_talent")
    later_data = later_talent.get("data_evidence") if isinstance(later_talent, dict) else None
    if not isinstance(old_data, dict) or not isinstance(later_data, dict):
        raise _fail(f"v2 mapping lacks old/new talent data evidence: {route}")
    expected_old_route = f"/shared/global/talents/{class_name}/data.js"
    old_lines = old_data.get("talent_assignment_lines")
    new_lines = later_data.get("talent_assignment_lines")
    zip_member = later_data.get("zip_member")
    if not isinstance(zip_member, str) or "/talents/" not in zip_member:
        raise _fail(f"semantic audit later data member is malformed for {route}")
    later_data_path = "talents/" + zip_member.rsplit("/talents/", 1)[1]
    if (
        entry.get("old_data_route") != expected_old_route
        or entry.get("old_data_sha256") != old_data.get("v52_sha256")
        or entry.get("old_data_talent_lines") != old_lines
        or entry.get("later_data_repository_path") != later_data_path
        or entry.get("later_data_sha256") != later_data.get("sha256")
        or entry.get("later_data_talent_lines") != new_lines
    ):
        raise _fail(f"v2 old/new data references differ from the accepted audit: {route}")
    for label, lines in (("old", old_lines), ("later", new_lines)):
        if not isinstance(lines, list) or not lines or any(
            isinstance(line, bool) or not isinstance(line, int) or line <= 0 for line in lines
        ):
            raise _fail(f"v2 {label} talent data line references are malformed: {route}")
    if entry.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail(f"v2 entry classification is not a later related source: {route}")
    if entry.get("original_capture_timestamp") is not None:
        raise _fail(f"v2 entry claims an original capture timestamp: {route}")
    if entry.get("original_2008_pixel_identity") != "unknown":
        raise _fail(f"v2 entry overstates original 2008 pixel identity: {route}")
    return route, repo_path, class_name


def _validate_v2_bindings(
    map_file: Path,
    workspace_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str, str, str, str]:
    root = workspace_root.resolve()
    try:
        map_relative = map_file.relative_to(root).as_posix()
    except ValueError as exc:
        raise _fail("v2 input map escapes workspace_root") from exc
    if map_relative != EXPECTED_V2_MAP_RELATIVE:
        raise _fail("v2 input map is not the pinned v55 input-map.json")
    map_data, map_sha = _read_v2_bound_json(map_file, EXPECTED_V2_MAP_SHA256, "v2 input map")
    if map_data.get("schema") != EXPECTED_V2_MAP_SCHEMA:
        raise _fail("v2 input map schema is not the accepted related-talent map")

    expected_paths = {
        "decision": EXPECTED_V2_DECISION_RELATIVE,
        "source_acceptance": EXPECTED_V2_ACCEPTANCE_RELATIVE,
        "semantic_audit": EXPECTED_V2_AUDIT_RELATIVE,
        "base_map": EXPECTED_V2_BASE_MAP_RELATIVE,
    }
    bound_paths: dict[str, Path] = {}
    for key, expected in expected_paths.items():
        relative = _normal_relative(map_data.get(key), f"v2 {key} path")
        if relative != expected:
            raise _fail(f"v2 input map points at a different {key} path")
        bound_paths[key] = _resolve_workspace_file(root, relative, f"v2 {key} path")
    pins_path = _resolve_workspace_file(root, EXPECTED_V2_PINS_RELATIVE, "v2 root input pins")

    decision, decision_sha = _read_v2_bound_json(
        bound_paths["decision"], EXPECTED_V2_DECISION_SHA256, "v2 decision record"
    )
    acceptance, acceptance_sha = _read_v2_bound_json(
        bound_paths["source_acceptance"], EXPECTED_SOURCE_ACCEPTANCE_SHA256,
        "v2 source acceptance record",
    )
    audit, audit_sha = _read_v2_bound_json(
        bound_paths["semantic_audit"], EXPECTED_V2_AUDIT_SHA256, "v2 semantic audit"
    )
    pins = _read_json(pins_path, "v2 root input pins")
    base_map, base_map_sha = _read_v2_bound_json(
        bound_paths["base_map"], EXPECTED_V2_BASE_MAP_SHA256, "v2 base map"
    )
    expected_pins = dict(EXPECTED_V2_ROOT_PINS)
    if pins != expected_pins:
        raise _fail("v2 root input pins do not bind the accepted map and aggregate")

    for key, actual in (
        ("decision_sha256", decision_sha),
        ("source_acceptance_sha256", acceptance_sha),
        ("semantic_audit_sha256", audit_sha),
        ("base_map_sha256", base_map_sha),
    ):
        if map_data.get(key) != actual:
            raise _fail(f"v2 input map {key} does not match its bound record")
    if decision.get("schema") != EXPECTED_V2_DECISION_SCHEMA:
        raise _fail("v2 decision schema is not the accepted derived-trial decision")
    if decision.get("accepted_for_derived_trial") is not True:
        raise _fail("v2 decision is not accepted for derived trial")
    if decision.get("source_acceptance") != expected_paths["source_acceptance"]:
        raise _fail("v2 decision points at a different source acceptance record")
    if decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("v2 decision source acceptance binding differs")
    if decision.get("semantic_audit") != expected_paths["semantic_audit"]:
        raise _fail("v2 decision points at a different semantic audit")
    if decision.get("semantic_audit_sha256") != audit_sha:
        raise _fail("v2 decision semantic audit binding differs")
    if decision.get("base_map") != expected_paths["base_map"] or decision.get("base_map_sha256") != base_map_sha:
        raise _fail("v2 decision base map binding differs")

    if base_map.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("v2 base map is not the accepted v1 icon map")
    if base_map.get("icon_count") != EXPECTED_V2_BASE_ICON_COUNT:
        raise _fail("v2 base map does not contain the accepted 986 icons")
    base_entries = base_map.get("entries")
    if not isinstance(base_entries, list) or len(base_entries) != EXPECTED_V2_BASE_ICON_COUNT:
        raise _fail("v2 base map entries do not contain the accepted 986 icons")

    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA or acceptance.get("accepted_source") is not True:
        raise _fail("v2 source acceptance is not the accepted CraftedRO record")
    for key in ("repository_url", "commit_sha", "tree_sha", "zip_url", "zip_sha256"):
        if acceptance.get(key) != EXPECTED_V2_SOURCE[key]:
            raise _fail(f"v2 source acceptance {key} differs from the pinned source")
    if (
        acceptance.get("strict_36px_same_path_icon_candidates") != EXPECTED_V2_BASE_ICON_COUNT
        or acceptance.get("original_2008_images_recovered") != 0
        or acceptance.get("published_images") != 0
        or acceptance.get("raw_images_reencoded") is not False
    ):
        raise _fail("v2 source acceptance does not preserve the accepted source boundary")

    source = map_data.get("source")
    if source != EXPECTED_V2_SOURCE or decision.get("source") != EXPECTED_V2_SOURCE:
        raise _fail("v2 source metadata differs from the pinned later-source record")
    _validated_retrieved_utc(source.get("downloaded_utc"))
    if decision.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("v2 decision classification is not later_related_source")
    if decision.get("original_capture_timestamp") is not None or source.get("original_capture_timestamp") is not None:
        raise _fail("v2 source claims an original capture timestamp")
    if decision.get("original_2008_images_recovered") != 0 or decision.get("images_reencoded") is not False:
        raise _fail("v2 decision overstates original recovery or re-encodes source images")

    if audit.get("schema") != EXPECTED_V2_AUDIT_SCHEMA:
        raise _fail("v2 semantic audit schema is unexpected")
    conclusion = audit.get("conclusion")
    recommendations = audit.get("recommendations")
    if (
        not isinstance(conclusion, dict)
        or conclusion.get("strong_same_class_candidates") != 10
        or conclusion.get("confirmed_2008_image_recoveries") != 0
        or conclusion.get("automatic_aliases_created") != 0
        or not isinstance(recommendations, list)
        or len(recommendations) != 10
    ):
        raise _fail("v2 semantic audit does not bind the ten accepted same-class candidates")
    recommendation_by_id: dict[str, Mapping[str, Any]] = {}
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            raise _fail("v2 semantic audit recommendation is malformed")
        mapping_id = recommendation.get("id")
        if not isinstance(mapping_id, str) or mapping_id in recommendation_by_id:
            raise _fail("v2 semantic audit has a duplicate/invalid mapping id")
        recommendation_by_id[mapping_id] = recommendation

    if map_data.get("base_icon_count") != EXPECTED_V2_BASE_ICON_COUNT:
        raise _fail("v2 input map base_icon_count is not 986")
    if map_data.get("mapped_icon_count") != EXPECTED_V2_MAPPED_ICON_COUNT:
        raise _fail("v2 input map mapped_icon_count is not 20")
    if map_data.get("icon_count") != EXPECTED_V2_ICON_COUNT:
        raise _fail("v2 input map icon_count is not 1006")
    if map_data.get("mapped_source_bytes") != EXPECTED_V2_MAPPED_SOURCE_BYTES:
        raise _fail("v2 input map mapped_source_bytes is not 21820")
    for field, expected in (
        ("base_icon_count", EXPECTED_V2_BASE_ICON_COUNT),
        ("mapped_icon_count", EXPECTED_V2_MAPPED_ICON_COUNT),
        ("icon_count", EXPECTED_V2_ICON_COUNT),
        ("mapped_source_bytes", EXPECTED_V2_MAPPED_SOURCE_BYTES),
    ):
        if decision.get(field) != expected:
            raise _fail(f"v2 decision {field} differs from the accepted aggregate")

    entries = map_data.get("entries")
    decision_entries = decision.get("entries")
    if not isinstance(entries, list) or len(entries) != EXPECTED_V2_MAPPED_ICON_COUNT:
        raise _fail("v2 input map entries do not match the exact 20-image scope")
    if entries != decision_entries:
        raise _fail("v2 decision image entries differ from the input map")
    base_routes = {entry.get("route") for entry in base_entries if isinstance(entry, dict)}
    base_relatives = {entry.get("repository_path") for entry in base_entries if isinstance(entry, dict)}
    seen_routes: set[str] = set()
    seen_source_paths: set[str] = set()
    seen_payload_paths: set[str] = set()
    seen_states: dict[str, set[str]] = {}
    total_bytes = 0
    asset_dir = EXPECTED_V2_MAP_RELATIVE.rsplit("/", 1)[0] + "/assets/"
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise _fail(f"v2 image entry {index} is not an object")
        mapping_id = entry.get("mapping_id")
        recommendation = recommendation_by_id.get(mapping_id)
        if recommendation is None:
            raise _fail(f"v2 image entry has no accepted semantic mapping: {mapping_id!r}")
        state = entry.get("state")
        if state not in ("on", "off"):
            raise _fail(f"v2 image entry has an invalid state: {state!r}")
        route, repository_path, class_name = _validate_v2_entry_semantics(
            entry, recommendation, state
        )
        if route in seen_routes or route in base_routes:
            raise _fail(f"duplicate v2 target route or collision with v1 bundle: {route}")
        if repository_path in seen_source_paths or repository_path in base_relatives:
            raise _fail(f"duplicate v2 source repository path: {repository_path}")
        seen_routes.add(route)
        seen_source_paths.add(repository_path)
        seen_states.setdefault(str(mapping_id), set()).add(state)
        payload_path = _normal_relative(entry.get("payload_path"), f"v2 payload path for {route}")
        if not payload_path.startswith(asset_dir):
            raise _fail(f"v2 payload is outside the pinned public asset directory: {route}")
        if payload_path in seen_payload_paths:
            raise _fail(f"duplicate v2 payload path: {payload_path}")
        seen_payload_paths.add(payload_path)
        if entry.get("format") != "JPEG" or entry.get("width") != 36 or entry.get("height") != 36 or entry.get("frames") != 1:
            raise _fail(f"v2 map image metadata is not single-frame 36x36 JPEG: {route}")
        length = entry.get("length")
        if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
            raise _fail(f"v2 payload length is malformed: {route}")
        if not isinstance(entry.get("sha256"), str) or not _SHA256_RE.fullmatch(entry["sha256"]):
            raise _fail(f"v2 payload SHA-256 is malformed: {route}")
        if not isinstance(entry.get("git_blob_sha1"), str) or not _SHA1_RE.fullmatch(entry["git_blob_sha1"]):
            raise _fail(f"v2 payload Git blob SHA-1 is malformed: {route}")
        total_bytes += length
        del class_name
    if any(states != {"on", "off"} for states in seen_states.values()) or len(seen_states) != 10:
        raise _fail("v2 entries do not contain exactly on/off assets for ten mappings")
    if total_bytes != EXPECTED_V2_MAPPED_SOURCE_BYTES:
        raise _fail(f"v2 image payload total is {total_bytes}, expected {EXPECTED_V2_MAPPED_SOURCE_BYTES}")
    if set(recommendation_by_id) != set(seen_states):
        raise _fail("v2 image mappings do not cover exactly the ten accepted semantic candidates")
    return map_data, decision, acceptance, audit, map_sha, decision_sha, acceptance_sha, audit_sha


def _make_v2_catalog(
    *,
    base_path: str,
    assets: list[RelatedTalentAsset],
    source_metadata: Mapping[str, Any],
    per_class_counts: Mapping[str, int],
    notice_html: str,
) -> bytes:
    public_assets: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    for asset in assets:
        item: dict[str, Any] = {
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
        mapping_id = asset.metadata.get("mapping_id")
        if mapping_id is not None:
            item.update(
                {
                    "mapping_id": mapping_id,
                    "source_repository_path": asset.metadata["source_repository_path"],
                    "mapping_reason": asset.metadata["mapping_reason"],
                    "classification": asset.metadata["classification"],
                    "original_capture_timestamp": None,
                    "original_2008_pixel_identity": "unknown",
                }
            )
            mappings.append(
                {
                    "target_route": asset.route,
                    "target_url": _public_asset_url(base_path, asset.route),
                    "source_repository_path": asset.metadata["source_repository_path"],
                    "source_image_url": asset.metadata["source_image_url"],
                    "mapping_id": mapping_id,
                    "class": asset.metadata["class"],
                    "talent": asset.metadata["talent"],
                    "state": asset.metadata["state"],
                    "mapping_reason": asset.metadata["mapping_reason"],
                    "sha256": asset.metadata["sha256"],
                    "git_blob_sha1": asset.metadata["git_blob_sha1"],
                    "length": asset.metadata["length"],
                    "format": asset.metadata["format"],
                    "width": asset.metadata["width"],
                    "height": asset.metadata["height"],
                    "frames": asset.metadata["frames"],
                    "old_data_route": asset.metadata["old_data_route"],
                    "old_data_sha256": asset.metadata["old_data_sha256"],
                    "old_data_talent_lines": asset.metadata["old_data_talent_lines"],
                    "later_data_repository_path": asset.metadata["later_data_repository_path"],
                    "later_data_sha256": asset.metadata["later_data_sha256"],
                    "later_data_talent_lines": asset.metadata["later_data_talent_lines"],
                    "classification": asset.metadata["classification"],
                    "original_capture_timestamp": None,
                    "original_2008_pixel_identity": "unknown",
                }
            )
            old_source_data_sha = asset.metadata.get("old_source_data_sha256")
            if old_source_data_sha is not None:
                mappings[-1]["old_source_data_sha256"] = old_source_data_sha
        public_assets.append(item)
    payload = {
        "schema": "wow-related-talent-icon-catalog/v2",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "notice_html": notice_html,
        "source": dict(source_metadata),
        "icon_count": len(assets),
        "class_counts": dict(per_class_counts),
        "assets": public_assets,
        "mappings": mappings,
    }
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _load_v2_related_talent_bundle(
    map_file: Path,
    workspace_root: Path,
    normalized_base: str,
) -> RelatedTalentBundle:
    map_data, _decision, _acceptance, _audit, map_sha, decision_sha, acceptance_sha, audit_sha = (
        _validate_v2_bindings(map_file, workspace_root)
    )
    root = workspace_root.resolve()
    base_map_path = _resolve_workspace_file(
        root, map_data["base_map"], "v2 base map path"
    )
    base_bundle = _load_v1_related_talent_bundle(base_map_path, root, normalized_base)
    if base_bundle.map_sha256 != EXPECTED_V2_BASE_MAP_SHA256:
        raise _fail("loaded v2 base icon bundle is not the accepted v1 map")
    routes = {asset.route for asset in base_bundle.assets}
    relatives = {asset.relative for asset in base_bundle.assets}
    per_class_counts = dict(base_bundle.per_class_counts)
    mapped_assets: list[RelatedTalentAsset] = []
    source_bytes = 0
    source = map_data["source"]
    source_refs_base = (
        str(source["repository_url"]),
        f"commit:{source['commit_sha']}",
        f"tree:{source['tree_sha']}",
    )
    for entry in map_data["entries"]:
        route = str(entry["route"])
        relative = route[1:]
        if route in routes or relative in relatives:
            raise _fail(f"v2 target route collides with an existing icon: {route}")
        payload_file = _resolve_workspace_file(
            root, entry["payload_path"], f"v2 payload {route}"
        )
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read v2 payload for {route}: {exc}") from exc
        if len(data) != entry["length"]:
            raise _fail(f"{route} length mismatch: expected {entry['length']}, got {len(data)}")
        actual_sha = _sha256(data)
        if actual_sha != entry["sha256"]:
            raise _fail(f"{route} SHA mismatch: expected {entry['sha256']}, got {actual_sha}")
        actual_blob = _sha1_git_blob(data)
        if actual_blob != entry["git_blob_sha1"]:
            raise _fail(f"{route} Git blob SHA mismatch: expected {entry['git_blob_sha1']}, got {actual_blob}")
        width, height, frames = _validate_image(data, entry, route)
        source_repository_path = entry["repository_path"]
        source_image_url = (
            f"https://raw.githubusercontent.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a/"
            f"{EXPECTED_COMMIT_SHA}/{source_repository_path}"
        )
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
            "original_2008_pixel_identity": "unknown",
            "mapping_id": entry["mapping_id"],
            "source_repository_path": source_repository_path,
            "source_image_url": source_image_url,
            "mapping_reason": entry["mapping_reason"],
            "class": entry["class"],
            "talent": entry["talent"],
            "state": entry["state"],
            "old_data_route": entry["old_data_route"],
            "old_data_sha256": entry["old_data_sha256"],
            "old_data_talent_lines": entry["old_data_talent_lines"],
            "later_data_repository_path": entry["later_data_repository_path"],
            "later_data_sha256": entry["later_data_sha256"],
            "later_data_talent_lines": entry["later_data_talent_lines"],
        }
        mapped_assets.append(
            RelatedTalentAsset(
                route=route,
                relative=relative,
                data=data,
                mime="image/jpeg",
                source_refs=source_refs_base
                + (
                    f"path:{source_repository_path}",
                    f"mapping:{entry['mapping_id']}",
                    f"reason:{entry['mapping_reason']}",
                ),
                metadata=metadata,
            )
        )
        routes.add(route)
        relatives.add(relative)
        per_class_counts[entry["class"]] += 1
        source_bytes += len(data)
    if len(mapped_assets) != EXPECTED_V2_MAPPED_ICON_COUNT or source_bytes != EXPECTED_V2_MAPPED_SOURCE_BYTES:
        raise _fail("loaded v2 assets do not match the accepted count/byte aggregate")
    assets = list(base_bundle.assets) + mapped_assets
    if len(assets) != EXPECTED_V2_ICON_COUNT:
        raise _fail("combined v2 bundle does not contain exactly 1006 assets")

    source_metadata = dict(base_bundle.source_metadata)
    source_metadata.update(
        {
            "icon_count": len(assets),
            "base_icon_count": EXPECTED_V2_BASE_ICON_COUNT,
            "mapped_icon_count": len(mapped_assets),
            "source_bytes": EXPECTED_V2_TOTAL_SOURCE_BYTES,
            "mapped_source_bytes": source_bytes,
            "map_sha256": map_sha,
            "decision_sha256": decision_sha,
            "source_acceptance_sha256": acceptance_sha,
            "base_map_sha256": EXPECTED_V2_BASE_MAP_SHA256,
            "semantic_audit_sha256": audit_sha,
        }
    )
    notice_html = base_bundle.notice_html
    catalog_bytes = _make_v2_catalog(
        base_path=normalized_base,
        assets=assets,
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=notice_html,
    )
    return RelatedTalentBundle(
        assets=tuple(assets),
        catalog_relative=base_bundle.catalog_relative,
        catalog_bytes=catalog_bytes,
        estimated_bytes=EXPECTED_V2_TOTAL_SOURCE_BYTES + len(catalog_bytes),
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=notice_html,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


def _validate_v3_entry_semantics(
    entry: Mapping[str, Any],
    candidate: Mapping[str, Any],
    preparation_candidate: Mapping[str, Any],
    accepted_object: Mapping[str, Any],
) -> tuple[str, str, str]:
    route = entry.get("route")
    if not isinstance(route, str) or any(token in route for token in ("?", "#", "\\", "\x00")):
        raise _fail(f"unsafe v3 target route: {route!r}")
    match = _ROUTE_RE.fullmatch(route)
    if match is None:
        raise _fail(f"v3 target route is outside the exact talent icon scope: {route!r}")
    class_name = match.group("class")
    mapping_id = entry.get("mapping_id")
    if mapping_id not in EXPECTED_V3_SELECTED_IDS or mapping_id != candidate.get("candidate_id"):
        raise _fail(f"v3 entry is outside the nine selected canonical mappings: {mapping_id!r}")

    old = candidate.get("old_2008_target")
    later = candidate.get("later_same_class_candidate")
    if not isinstance(old, dict) or not isinstance(later, dict):
        raise _fail(f"v3 semantic audit lacks old/later data for {route}")
    title = old.get("canonical_talent_title")
    if (
        candidate.get("class") != class_name
        or old.get("canonical_talent_title") != later.get("canonical_talent_title")
        or entry.get("class") != class_name
        or entry.get("talent") != title
    ):
        raise _fail(f"v3 mapping is not an exact same-class canonical title match: {route}")
    if not str(candidate.get("finding_type", "")).startswith("exact_same_class_title"):
        raise _fail(f"v3 semantic audit does not classify {mapping_id} as an exact canonical title match")
    if entry.get("mapping_reason") != candidate.get("reason"):
        raise _fail(f"v3 mapping reason differs from semantic audit: {route}")

    state = entry.get("state")
    if state not in ("on", "off") or (route.lower().endswith("-off.jpg") != (state == "off")):
        raise _fail(f"v3 route state does not match its on/off designation: {route}")
    old_routes = old.get("routes")
    if not isinstance(old_routes, list) or route not in old_routes:
        raise _fail(f"v3 target route is absent from the exact old Source16 target: {route}")
    repo_path = entry.get("repository_path")
    repo_path = _normal_relative(repo_path, f"v3 source repository path for {route}")
    if not repo_path.startswith(f"shared/global/talents/{class_name}/images/") or not repo_path.lower().endswith(".jpg"):
        raise _fail(f"v3 source path leaves the same talent class: {repo_path!r}")
    image_by_state = {
        image.get("state"): image
        for image in later.get("images", [])
        if isinstance(image, dict)
    }
    source_image = image_by_state.get(state)
    if not isinstance(source_image, dict) or source_image.get("repository_path") != repo_path:
        raise _fail(f"v3 source path is not the exact accepted later image for {route}")
    if (
        entry.get("sha256") != source_image.get("sha256")
        or entry.get("git_blob_sha1") != source_image.get("git_blob_sha1")
        or entry.get("length") != source_image.get("length")
        or entry.get("format") != source_image.get("format")
        or [entry.get("width"), entry.get("height")] != source_image.get("dimensions")
        or entry.get("frames") != source_image.get("frames")
    ):
        raise _fail(f"v3 image metadata differs from the accepted ZIP inventory for {route}")

    old_raw_sha = old.get("source16_data_sha256")
    old_data_route = old.get("data_route")
    later_zip_member = later.get("data_zip_member")
    later_data_sha = later.get("data_sha256")
    if not isinstance(later_zip_member, str) or "/talents/" not in later_zip_member:
        raise _fail(f"v3 later data member is malformed for {route}")
    later_data_path = "talents/" + later_zip_member.rsplit("/talents/", 1)[1]
    old_lines = [old.get("talent_assignment_line")]
    later_lines = [later.get("talent_assignment_line")]
    old_derived_sha = entry.get("old_data_sha256")
    if (
        entry.get("old_data_route") != old_data_route
        or entry.get("old_source_data_sha256") != old_raw_sha
        or not isinstance(old_derived_sha, str)
        or not _SHA256_RE.fullmatch(old_derived_sha)
        or old_derived_sha == old_raw_sha
        or entry.get("old_data_talent_lines") != old_lines
        or entry.get("later_data_repository_path") != later_data_path
        or entry.get("later_data_sha256") != later_data_sha
        or entry.get("later_data_talent_lines") != later_lines
    ):
        raise _fail(f"v3 old raw/derived or later data binding differs from accepted evidence: {route}")
    for label, lines in (("old", old_lines), ("later", later_lines)):
        if any(isinstance(line, bool) or not isinstance(line, int) or line <= 0 for line in lines):
            raise _fail(f"v3 {label} talent line reference is malformed: {route}")

    prep_old = preparation_candidate.get("old_data")
    prep_dnl = preparation_candidate.get("old_donotlocalize")
    prep_later = preparation_candidate.get("later_data")
    if not all(isinstance(value, dict) for value in (prep_old, prep_dnl, prep_later)):
        raise _fail(f"v3 source preparation is missing old/new data evidence for {route}")
    if (
        prep_old.get("sha256") != old_raw_sha
        or prep_old.get("talent_assignment_line") != old.get("talent_assignment_line")
        or prep_old.get("image_label_assignment_line") != old.get("image_label_assignment_line")
        or prep_old.get("rank_array_line") != old.get("rank_array_line")
        or prep_dnl.get("sha256") != old.get("donotlocalize_source_sha256")
        or prep_dnl.get("assignment_index") != old.get("talent_assignment_index")
        or prep_dnl.get("assigned_label") != old.get("image_label")
        or prep_later.get("repository_path") != later_data_path
        or prep_later.get("sha256") != later_data_sha
        or prep_later.get("talent_assignment_line") != later.get("talent_assignment_line")
    ):
        raise _fail(f"v3 data references differ from the independently reviewed source preparation: {route}")
    if (
        entry.get("page_route") != f"/info/classes/{class_name}/talents.html"
        or entry.get("classification") != EXPECTED_CLASSIFICATION
        or entry.get("original_capture_timestamp") is not None
        or entry.get("original_2008_pixel_identity") != "unknown"
    ):
        raise _fail(f"v3 entry overstates original capture or pixel identity: {route}")
    if (
        accepted_object.get("route") != route
        or accepted_object.get("repository_path") != repo_path
        or accepted_object.get("sha256") != entry.get("sha256")
        or accepted_object.get("bytes") != entry.get("length")
        or accepted_object.get("class") != class_name
        or accepted_object.get("talent") != title
        or accepted_object.get("state") != state
    ):
        raise _fail(f"v3 source review does not approve this exact image object: {route}")
    return route, repo_path, class_name


def _validate_v3_bindings(
    map_file: Path,
    workspace_root: Path,
) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any],
    dict[str, Any], str, str, str, str, str,
]:
    root = workspace_root.resolve()
    try:
        map_relative = map_file.relative_to(root).as_posix()
    except ValueError as exc:
        raise _fail("v3 input map escapes workspace_root") from exc
    if map_relative != EXPECTED_V3_MAP_RELATIVE:
        raise _fail("v3 input map is not the pinned v56 input-map.json")
    map_data, map_sha = _read_v2_bound_json(map_file, EXPECTED_V3_MAP_SHA256, "v3 input map")
    if map_data.get("schema") != EXPECTED_V3_MAP_SCHEMA:
        raise _fail("v3 input map schema is not wow-related-talent-icon-map/v3")

    expected_paths = {
        "decision": EXPECTED_V3_DECISION_RELATIVE,
        "root_source_acceptance": EXPECTED_V3_ROOT_ACCEPTANCE_RELATIVE,
        "source_preparation": EXPECTED_V3_PREPARATION_RELATIVE,
        "semantic_audit": EXPECTED_V3_AUDIT_RELATIVE,
        "source_acceptance": EXPECTED_V3_SOURCE_ACCEPTANCE_RELATIVE,
        "base_map": EXPECTED_V3_BASE_MAP_RELATIVE,
    }
    paths: dict[str, Path] = {}
    for key, expected in expected_paths.items():
        relative = _normal_relative(map_data.get(key), f"v3 {key} path")
        if relative != expected:
            raise _fail(f"v3 input map points at a different {key} path")
        paths[key] = _resolve_workspace_file(root, relative, f"v3 {key} path")
    pins_path = _resolve_workspace_file(root, EXPECTED_V3_PINS_RELATIVE, "v3 root input pins")

    decision, decision_sha = _read_v2_bound_json(paths["decision"], EXPECTED_V3_DECISION_SHA256, "v3 decision")
    root_acceptance, root_acceptance_sha = _read_v2_bound_json(
        paths["root_source_acceptance"], EXPECTED_V3_ROOT_ACCEPTANCE_SHA256, "v3 root source acceptance"
    )
    source_preparation, preparation_sha = _read_v2_bound_json(
        paths["source_preparation"], EXPECTED_V3_PREPARATION_SHA256, "v3 source preparation"
    )
    audit, audit_sha = _read_v2_bound_json(paths["semantic_audit"], EXPECTED_V3_AUDIT_SHA256, "v3 semantic audit")
    acceptance, acceptance_sha = _read_v2_bound_json(
        paths["source_acceptance"], EXPECTED_V3_SOURCE_ACCEPTANCE_SHA256, "v3 source acceptance"
    )
    base_map, base_map_sha = _read_v2_bound_json(paths["base_map"], EXPECTED_V3_BASE_MAP_SHA256, "v3 v55 base map")
    pins = _read_json(pins_path, "v3 root input pins")
    if pins != EXPECTED_V3_ROOT_PINS:
        raise _fail("v3 root input pins do not bind the accepted map and source review")

    for key, actual in (
        ("decision_sha256", decision_sha),
        ("root_source_acceptance_sha256", root_acceptance_sha),
        ("source_preparation_sha256", preparation_sha),
        ("semantic_audit_sha256", audit_sha),
        ("source_acceptance_sha256", acceptance_sha),
        ("base_map_sha256", base_map_sha),
    ):
        if map_data.get(key) != actual:
            raise _fail(f"v3 input map {key} does not match its bound record")

    if decision.get("schema") != EXPECTED_V3_DECISION_SCHEMA or decision.get("accepted_for_derived_trial") is not True:
        raise _fail("v3 decision is not accepted for a derived trial")
    if decision.get("base_map") != expected_paths["base_map"] or decision.get("base_map_sha256") != base_map_sha:
        raise _fail("v3 decision base-map binding differs")
    for field, path_key, hash_key in (
        ("semantic_audit", "semantic_audit", "semantic_audit_sha256"),
        ("source_acceptance", "source_acceptance", "source_acceptance_sha256"),
        ("root_source_acceptance", "root_source_acceptance", "root_source_acceptance_sha256"),
    ):
        if decision.get(field) != expected_paths[path_key] or decision.get(hash_key) != map_data.get(hash_key):
            raise _fail(f"v3 decision {field} binding differs")
    if decision.get("source") != EXPECTED_V3_SOURCE or map_data.get("source") != EXPECTED_V3_SOURCE:
        raise _fail("v3 source metadata differs from the pinned later-source record")
    _validated_retrieved_utc(map_data["source"].get("downloaded_utc"))
    if decision.get("original_2008_images_recovered") != 0 or decision.get("images_reencoded") is not False:
        raise _fail("v3 decision overstates original recovery or re-encodes source images")

    if base_map.get("schema") != EXPECTED_V2_MAP_SCHEMA:
        raise _fail("v3 base map is not the accepted v2 map")
    if (
        base_map.get("icon_count") != EXPECTED_V3_BASE_ICON_COUNT
        or base_map.get("base_icon_count") != EXPECTED_V2_BASE_ICON_COUNT
        or base_map.get("mapped_icon_count") != EXPECTED_V2_MAPPED_ICON_COUNT
        or len(base_map.get("entries", [])) != EXPECTED_V2_MAPPED_ICON_COUNT
    ):
        raise _fail("v3 base map does not describe the accepted 1,006-icon v55 bundle")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA or acceptance.get("accepted_source") is not True:
        raise _fail("v3 original source acceptance is not accepted")
    for key in ("repository_url", "commit_sha", "tree_sha", "zip_url", "zip_sha256"):
        if acceptance.get(key) != EXPECTED_V3_SOURCE[key]:
            raise _fail(f"v3 original source acceptance {key} differs")
    if (
        acceptance.get("original_2008_images_recovered") != 0
        or acceptance.get("raw_images_reencoded") is not False
    ):
        raise _fail("v3 original source acceptance overstates recovery or changes image bytes")

    if root_acceptance.get("schema") != EXPECTED_V3_ROOT_ACCEPTANCE_SCHEMA:
        raise _fail("v3 root source review schema is unexpected")
    if (
        root_acceptance.get("accepted_sources") is not True
        or root_acceptance.get("source_preparation_sha256") != preparation_sha
        or root_acceptance.get("semantic_audit_sha256") != audit_sha
        or root_acceptance.get("source_zip_sha256") != EXPECTED_V3_SOURCE["zip_sha256"]
        or root_acceptance.get("images") != EXPECTED_V3_MAPPED_ICON_COUNT
        or root_acceptance.get("bytes") != EXPECTED_V3_MAPPED_SOURCE_BYTES
        or root_acceptance.get("original_2008_image_recoveries") != 0
        or root_acceptance.get("classification") != EXPECTED_CLASSIFICATION
        or root_acceptance.get("original_capture_timestamp") is not None
        or root_acceptance.get("pixel_identity_with_2008") != "unknown"
        or root_acceptance.get("all_zip_bytes_rehashed_and_frames_decoded") is not True
        or root_acceptance.get("old_and_new_data_rows_independently_checked") is not True
        or root_acceptance.get("old_image_label_rows_independently_checked") is not True
        or root_acceptance.get("old_2008_talent_rows_unchanged") is not True
        or root_acceptance.get("old_derived_data_unchanged") is not True
    ):
        raise _fail("v3 root source review does not accept the pinned 18 later-source images")

    if source_preparation.get("schema") != EXPECTED_V3_PREPARATION_SCHEMA:
        raise _fail("v3 source preparation schema is unexpected")
    preparation_ids = source_preparation.get("candidate_ids")
    if (
        source_preparation.get("preparation_status") != "prepared_for_independent_parent_review"
        or not isinstance(preparation_ids, list)
        or set(preparation_ids) != set(EXPECTED_V3_SELECTED_IDS)
        or len(preparation_ids) != len(EXPECTED_V3_SELECTED_IDS)
        or source_preparation.get("network_requests") != 0
        or source_preparation.get("not_an_acceptance_or_decision") is not True
    ):
        raise _fail("v3 source preparation is outside the pinned inputs-only preparation")

    if audit.get("schema") != EXPECTED_V3_AUDIT_SCHEMA:
        raise _fail("v3 semantic audit schema is unexpected")
    candidate_list = audit.get("new_same_class_candidates")
    if not isinstance(candidate_list, list):
        raise _fail("v3 semantic audit lacks the candidate list")
    candidate_by_id = {
        row.get("candidate_id"): row
        for row in candidate_list
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }
    preparation_list = source_preparation.get("selected_candidates")
    if not isinstance(preparation_list, list):
        raise _fail("v3 source preparation lacks candidate-level bindings")
    preparation_by_id = {
        row.get("candidate_id"): row
        for row in preparation_list
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }
    accepted_objects = root_acceptance.get("objects")
    if not isinstance(accepted_objects, list) or len(accepted_objects) != EXPECTED_V3_MAPPED_ICON_COUNT:
        raise _fail("v3 root source review object list is malformed")
    accepted_by_route = {row.get("route"): row for row in accepted_objects if isinstance(row, dict)}
    if len(accepted_by_route) != EXPECTED_V3_MAPPED_ICON_COUNT:
        raise _fail("v3 root source review has duplicate image targets")
    if set(decision.get("selected_canonical_ids", [])) != set(EXPECTED_V3_SELECTED_IDS):
        raise _fail("v3 decision selected canonical IDs differ from the nine reviewed IDs")

    for field, expected in (
        ("base_icon_count", EXPECTED_V3_BASE_ICON_COUNT),
        ("mapped_icon_count", EXPECTED_V3_MAPPED_ICON_COUNT),
        ("icon_count", EXPECTED_V3_ICON_COUNT),
        ("mapped_source_bytes", EXPECTED_V3_MAPPED_SOURCE_BYTES),
    ):
        if map_data.get(field) != expected or decision.get(field) != expected:
            raise _fail(f"v3 map/decision {field} differs from the pinned aggregate")
    entries = map_data.get("entries")
    if not isinstance(entries, list) or len(entries) != EXPECTED_V3_MAPPED_ICON_COUNT:
        raise _fail("v3 map must contain exactly eighteen entries")
    if entries != decision.get("entries"):
        raise _fail("v3 decision entries differ from the pinned map")
    if set(preparation_by_id) != set(EXPECTED_V3_SELECTED_IDS):
        raise _fail("v3 source preparation does not bind exactly the nine selected IDs")

    base_routes = {row.get("route") for row in base_map["entries"] if isinstance(row, dict)}
    base_source_paths = {row.get("repository_path") for row in base_map["entries"] if isinstance(row, dict)}
    seen_routes: set[str] = set()
    seen_sources: set[str] = set()
    seen_payloads: set[str] = set()
    seen_states: dict[str, set[str]] = {}
    data_by_class: dict[str, tuple[str, Path]] = {}
    total_bytes = 0
    asset_dir = EXPECTED_V3_MAP_RELATIVE.rsplit("/", 1)[0] + "/assets/"
    source_files_by_class = {
        row.get("class"): row for row in audit.get("source16_old_data_files", []) if isinstance(row, dict)
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise _fail(f"v3 image entry {index} is not an object")
        mapping_id = entry.get("mapping_id")
        candidate = candidate_by_id.get(mapping_id)
        prep_candidate = preparation_by_id.get(mapping_id)
        if candidate is None or prep_candidate is None:
            raise _fail(f"v3 entry lacks its exact semantic or preparation binding: {mapping_id!r}")
        route, repo_path, class_name = _validate_v3_entry_semantics(
            entry, candidate, prep_candidate, accepted_by_route.get(entry.get("route"), {})
        )
        if route in seen_routes or route in base_routes:
            raise _fail(f"duplicate v3 target route or collision with v2 bundle: {route}")
        if repo_path in seen_sources or repo_path in base_source_paths:
            raise _fail(f"duplicate v3 source path or collision with v2 bundle: {repo_path}")
        seen_routes.add(route)
        seen_sources.add(repo_path)
        seen_states.setdefault(str(mapping_id), set()).add(str(entry["state"]))
        payload_path = _normal_relative(entry.get("payload_path"), f"v3 payload for {route}")
        if not payload_path.startswith(asset_dir) or payload_path in seen_payloads:
            raise _fail(f"v3 payload is outside the pinned asset directory or is duplicated: {route}")
        seen_payloads.add(payload_path)
        payload_file = _resolve_workspace_file(root, payload_path, f"v3 payload for {route}")
        data, _ = _read_hash_checked(payload_file, entry.get("sha256"), f"v3 payload for {route}")
        length = entry.get("length")
        if isinstance(length, bool) or not isinstance(length, int) or length <= 0 or len(data) != length:
            raise _fail(f"v3 payload length mismatch: {route}")
        if _sha1_git_blob(data) != entry.get("git_blob_sha1"):
            raise _fail(f"v3 payload Git blob SHA mismatch: {route}")
        _validate_image(data, entry, route)
        total_bytes += len(data)

        old_target = candidate["old_2008_target"]
        source_file = source_files_by_class.get(class_name)
        if not isinstance(source_file, dict) or source_file.get("source_sha256") != entry.get("old_source_data_sha256"):
            raise _fail(f"v3 raw Source16 data digest is not bound to audit for {class_name}")
        v55_data_file = root / EXPECTED_V3_V55_EXPORT_RELATIVE / old_target["data_route"].lstrip("/")
        derived_data, _ = _read_hash_checked(
            _resolve_workspace_file(root, v55_data_file.relative_to(root).as_posix(), f"v3 v55 derived data for {class_name}"),
            entry.get("old_data_sha256"),
            f"v3 derived v55 data for {class_name}",
        )
        if class_name not in data_by_class:
            source16_path = source_file.get("derived_site_path")
            source16_file = _resolve_workspace_file(root, source16_path, f"v3 Source16 data for {class_name}")
            source16_data, _ = _read_hash_checked(source16_file, entry.get("old_source_data_sha256"), f"v3 raw Source16 data for {class_name}")
            source_lines = source16_data.splitlines()
            derived_lines = derived_data.splitlines()
            if len(source_lines) != len(derived_lines):
                raise _fail(f"v3 Source16/v55 data line count changed for {class_name}")
            changed_lines = [i for i, (before, after) in enumerate(zip(source_lines, derived_lines), 1) if before != after]
            if changed_lines != [5]:
                raise _fail(f"v3 v55 derived data changed lines other than the pinned talentPath line for {class_name}")
            data_by_class[class_name] = (entry["old_data_sha256"], v55_data_file)
        elif data_by_class[class_name][0] != entry.get("old_data_sha256"):
            raise _fail(f"v3 entries disagree on derived v55 data digest for {class_name}")
        del derived_data

    if set(seen_states) != set(EXPECTED_V3_SELECTED_IDS) or any(states != {"on", "off"} for states in seen_states.values()):
        raise _fail("v3 entries do not provide exactly on/off state images for all nine selected talents")
    if total_bytes != EXPECTED_V3_MAPPED_SOURCE_BYTES:
        raise _fail(f"v3 image payload total is {total_bytes}, expected {EXPECTED_V3_MAPPED_SOURCE_BYTES}")
    return (
        map_data, decision, root_acceptance, acceptance, audit, source_preparation,
        map_sha, decision_sha, acceptance_sha, audit_sha, root_acceptance_sha,
    )


def _load_v3_related_talent_bundle(
    map_file: Path,
    workspace_root: Path,
    normalized_base: str,
) -> RelatedTalentBundle:
    (
        map_data, decision, root_acceptance, _acceptance, _audit, _preparation,
        map_sha, decision_sha, acceptance_sha, audit_sha, root_acceptance_sha,
    ) = _validate_v3_bindings(map_file, workspace_root)
    root = workspace_root.resolve()
    base_map_path = _resolve_workspace_file(root, map_data["base_map"], "v3 base v55 map")
    base_bundle = _load_v2_related_talent_bundle(base_map_path, root, normalized_base)
    if base_bundle.map_sha256 != EXPECTED_V2_MAP_SHA256 or len(base_bundle.assets) != EXPECTED_V3_BASE_ICON_COUNT:
        raise _fail("loaded v3 base bundle is not the accepted 1,006-icon v55 bundle")

    routes = {asset.route for asset in base_bundle.assets}
    relatives = {asset.relative for asset in base_bundle.assets}
    per_class_counts = dict(base_bundle.per_class_counts)
    mapped_assets: list[RelatedTalentAsset] = []
    source_bytes = 0
    source = map_data["source"]
    source_refs_base = (
        str(source["repository_url"]),
        f"commit:{source['commit_sha']}",
        f"tree:{source['tree_sha']}",
    )
    for entry in map_data["entries"]:
        route = str(entry["route"])
        relative = route[1:]
        if route in routes or relative in relatives:
            raise _fail(f"v3 target route collides with existing v2 icon: {route}")
        payload_file = _resolve_workspace_file(root, entry["payload_path"], f"v3 payload {route}")
        data = payload_file.read_bytes()
        if len(data) != entry["length"]:
            raise _fail(f"{route} length mismatch: expected {entry['length']}, got {len(data)}")
        actual_sha = _sha256(data)
        if actual_sha != entry["sha256"]:
            raise _fail(f"{route} SHA mismatch: expected {entry['sha256']}, got {actual_sha}")
        actual_blob = _sha1_git_blob(data)
        if actual_blob != entry["git_blob_sha1"]:
            raise _fail(f"{route} Git blob SHA mismatch: expected {entry['git_blob_sha1']}, got {actual_blob}")
        width, height, frames = _validate_image(data, entry, route)
        source_repository_path = entry["repository_path"]
        source_image_url = (
            f"https://raw.githubusercontent.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a/"
            f"{EXPECTED_COMMIT_SHA}/{source_repository_path}"
        )
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
            "original_2008_pixel_identity": "unknown",
            "mapping_id": entry["mapping_id"],
            "source_repository_path": source_repository_path,
            "source_image_url": source_image_url,
            "mapping_reason": entry["mapping_reason"],
            "class": entry["class"],
            "talent": entry["talent"],
            "state": entry["state"],
            "old_data_route": entry["old_data_route"],
            "old_data_sha256": entry["old_data_sha256"],
            "old_source_data_sha256": entry["old_source_data_sha256"],
            "old_data_talent_lines": entry["old_data_talent_lines"],
            "later_data_repository_path": entry["later_data_repository_path"],
            "later_data_sha256": entry["later_data_sha256"],
            "later_data_talent_lines": entry["later_data_talent_lines"],
        }
        mapped_assets.append(
            RelatedTalentAsset(
                route=route,
                relative=relative,
                data=data,
                mime="image/jpeg",
                source_refs=source_refs_base + (
                    f"path:{source_repository_path}",
                    f"mapping:{entry['mapping_id']}",
                    f"reason:{entry['mapping_reason']}",
                    f"old-source-data-sha256:{entry['old_source_data_sha256']}",
                    f"old-derived-data-sha256:{entry['old_data_sha256']}",
                ),
                metadata=metadata,
            )
        )
        routes.add(route)
        relatives.add(relative)
        per_class_counts[entry["class"]] += 1
        source_bytes += len(data)
    assets = list(base_bundle.assets) + mapped_assets
    if len(mapped_assets) != EXPECTED_V3_MAPPED_ICON_COUNT or source_bytes != EXPECTED_V3_MAPPED_SOURCE_BYTES:
        raise _fail("loaded v3 assets do not match the accepted count/byte aggregate")
    if len(assets) != EXPECTED_V3_ICON_COUNT:
        raise _fail("combined v3 bundle does not contain exactly 1,024 assets")

    source_metadata = dict(base_bundle.source_metadata)
    source_metadata.update(
        {
            "icon_count": len(assets),
            "ordinary_icon_count": EXPECTED_ICON_COUNT,
            "base_icon_count": EXPECTED_ICON_COUNT,
            "mapped_icon_count": EXPECTED_V2_MAPPED_ICON_COUNT + EXPECTED_V3_MAPPED_ICON_COUNT,
            "v2_mapped_icon_count": EXPECTED_V2_MAPPED_ICON_COUNT,
            "v3_mapped_icon_count": EXPECTED_V3_MAPPED_ICON_COUNT,
            "source_bytes": EXPECTED_V3_TOTAL_SOURCE_BYTES,
            "mapped_source_bytes": EXPECTED_V2_MAPPED_SOURCE_BYTES + source_bytes,
            "v2_mapped_source_bytes": EXPECTED_V2_MAPPED_SOURCE_BYTES,
            "v3_mapped_source_bytes": source_bytes,
            "class_mapping_deltas": dict(EXPECTED_V3_CLASS_DELTAS),
            "map_sha256": map_sha,
            "decision_sha256": decision_sha,
            "base_map_sha256": EXPECTED_V3_BASE_MAP_SHA256,
            "v55_map_sha256": EXPECTED_V2_MAP_SHA256,
            "semantic_audit_sha256": audit_sha,
            "source_preparation_sha256": EXPECTED_V3_PREPARATION_SHA256,
            "root_source_acceptance_sha256": root_acceptance_sha,
            "v56_selected_canonical_ids": list(EXPECTED_V3_SELECTED_IDS),
        }
    )
    catalog_bytes = _make_v2_catalog(
        base_path=normalized_base,
        assets=assets,
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=base_bundle.notice_html,
    )
    return RelatedTalentBundle(
        assets=tuple(assets),
        catalog_relative=base_bundle.catalog_relative,
        catalog_bytes=catalog_bytes,
        estimated_bytes=EXPECTED_V3_TOTAL_SOURCE_BYTES + len(catalog_bytes),
        source_metadata=source_metadata,
        per_class_counts=per_class_counts,
        notice_html=base_bundle.notice_html,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


def load_related_talent_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedTalentBundle:
    """Load a pinned v1 bundle or one of its explicit same-class extensions."""

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
    try:
        map_file.relative_to(root)
    except ValueError as exc:
        raise _fail("input map escapes workspace_root") from exc
    if not map_file.is_file() or map_file.is_symlink():
        raise _fail("input map is not a regular non-symlink file")
    try:
        map_header = json.loads(map_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        # Preserve v1's established diagnostics for malformed/unreadable maps.
        return _load_v1_related_talent_bundle(map_file, root, base_path)
    if isinstance(map_header, dict):
        normalized_base = _normalize_base_path(base_path)
        if map_header.get("schema") == EXPECTED_V3_MAP_SCHEMA:
            return _load_v3_related_talent_bundle(map_file, root, normalized_base)
        if map_header.get("schema") == EXPECTED_V2_MAP_SCHEMA:
            return _load_v2_related_talent_bundle(map_file, root, normalized_base)
    return _load_v1_related_talent_bundle(map_file, root, base_path)


__all__ = [
    "ALLOWED_CLASSES",
    "EXPECTED_CATALOG_RELATIVE",
    "RelatedTalentAsset",
    "RelatedTalentBundle",
    "RelatedTalentIconError",
    "load_related_talent_bundle",
]
