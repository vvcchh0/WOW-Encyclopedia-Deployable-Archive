#!/usr/bin/env python3
"""Load the accepted later-source talent UI images.

This module is deliberately a read-only loader.  It validates the pinned
input map, decision, source acceptance record, and private image payloads,
then returns in-memory records for the Pages exporter.  It does not write site
files, create aliases, execute calculator code, or infer any other talent
asset.  The v1 six-PNG contract remains available alongside the pinned v2
six-PNG/eighteen-GIF contract.
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
except ImportError as exc:  # pragma: no cover - guarded by repository setup
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class RelatedTalentUIError(ValueError):
    """Raised when the pinned UI map or a payload is unsafe or has drifted."""


EXPECTED_MAP_SHA256 = "44dc4433a19e369d3b58192597988c29e7c3da57b114594164aae50cfba05666"
EXPECTED_DECISION_SHA256 = "977e8b06d2891a877fad14abfb959f47cb5f6988ca7be0228738b770813571f6"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = (
    "4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465"
)

EXPECTED_REPOSITORY_URL = (
    "https://github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a"
)
EXPECTED_COMMIT_SHA = "4c8013cf40d0edf84625430eaf43b86d97880ae0"
EXPECTED_TREE_SHA = "e8916c038b41c2c29144f5411f8fc6ec5cd032d5"
EXPECTED_CLASSIFICATION = "later_related_source"
EXPECTED_UI_COUNT = 6
EXPECTED_TOTAL_BYTES = 5619
EXPECTED_CATALOG_RELATIVE = "__offline/related-talent-ui.json"
EXPECTED_MAP_SCHEMA = "wow-related-talent-ui-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-related-talent-ui-integration-decision/v1"
EXPECTED_ACCEPTANCE_SCHEMA = "wow-root-related-talent-source-acceptance/v1"

# v2 was independently reviewed for its exact 24 routes.  Keep these pins
# separate from the v1 constants above so the original public behavior remains
# byte-for-byte stable.
EXPECTED_V2_MAP_SHA256 = "f795ed587062553831afd24d682aaba516ac07bdc6360636119a28aca2bf8355"
EXPECTED_V2_DECISION_SHA256 = "958ae52a9bde6ff505522ba920257936971231650db0e3db1ef92241853fc304"
EXPECTED_V2_SOURCE_ACCEPTANCE_SHA256 = EXPECTED_SOURCE_ACCEPTANCE_SHA256
EXPECTED_V2_UI_COUNT = 24
EXPECTED_V2_TOTAL_BYTES = 26930
EXPECTED_V2_MAP_SCHEMA = "wow-related-talent-ui-map/v2"
EXPECTED_V2_DECISION_SCHEMA = "wow-related-talent-ui-integration-decision/v2"
EXPECTED_V2_MAP_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-ui-v54/input-map.json"
)
EXPECTED_V2_DECISION_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-ui-v54/decision.json"
)
EXPECTED_V2_PINS_RELATIVE = (
    "research/continuous-recovery-20261022/integration/related-talent-ui-v54/root-input-pins.json"
)
EXPECTED_V2_ACCEPTANCE_RELATIVE = (
    "research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json"
)
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

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")

# The target routes are the historical GIF URLs.  The source payloads are
# explicit PNGs, and the canonical output routes are intentionally separate
# from both the historical target and the private payload path.
UI_TARGETS: Mapping[str, Mapping[str, Any]] = {
    "/shared/global/talents/images/talents/icon-over-grey.gif": {
        "route": "/__offline/related-talent-ui/icon-over-grey.png",
        "repository_path": "shared/global/talents/images/talents/icon-over-grey.png",
        "sha256": "319d767bc96501a63decfe40b98314535c597a7574677e40f4b02c37c84367f9",
        "length": 258,
        "git_blob_sha1": "c897002ebacc10d5be12fec17f99419431b202dd",
        "width": 52,
        "height": 48,
    },
    "/shared/global/talents/images/talents/icon-over-green.gif": {
        "route": "/__offline/related-talent-ui/icon-over-green.png",
        "repository_path": "shared/global/talents/images/talents/icon-over-green.png",
        "sha256": "ded186cc380ed775408c59c3715a1ba129eed90bd9edcb80e1ed6e18e4dfc1bb",
        "length": 280,
        "git_blob_sha1": "ae5e67c14922ebfa690dea9b69dfc1ae4e7e6f42",
        "width": 52,
        "height": 48,
    },
    "/shared/global/talents/images/talents/icon-over-yellow.gif": {
        "route": "/__offline/related-talent-ui/icon-over-yellow.png",
        "repository_path": "shared/global/talents/images/talents/icon-over-yellow.png",
        "sha256": "c213b691fa534821bede1d238fcf841f8b658f4b84812a995a7ae2f103ab1808",
        "length": 280,
        "git_blob_sha1": "4e332c3a4af1a86211eb9630cca100971e0026e7",
        "width": 52,
        "height": 48,
    },
    "/shared/global/talents/includes/images/reset.gif": {
        "route": "/__offline/related-talent-ui/reset.png",
        "repository_path": "shared/global/talents/includes/images/reset.png",
        "sha256": "0838291593345f22c7366a027491f04cd93806b057f4546ec5f94b2486aa7c83",
        "length": 1203,
        "git_blob_sha1": "00d44895b6d216892faf90949a092ee29a0b6e5d",
        "width": 60,
        "height": 20,
    },
    "/shared/global/talents/includes/images/resetall.gif": {
        "route": "/__offline/related-talent-ui/resetall.png",
        "repository_path": "shared/global/talents/includes/images/resetall.png",
        "sha256": "30a0b85e9edd8c0abadea728b7797ea6312b1eaa6c556c2418a127385af5e3ac",
        "length": 1465,
        "git_blob_sha1": "dc08b3b602aaf3bbd7cf8892493d5b7b9c5c970e",
        "width": 80,
        "height": 20,
    },
    "/shared/global/talents/includes/images/printableversion.gif": {
        "route": "/__offline/related-talent-ui/printableversion.png",
        "repository_path": "shared/global/talents/includes/images/printableversion.png",
        "sha256": "f25423d27e95bf8af550dcbfe5905f85f2139730bcc536159563516c51dae2c5",
        "length": 2133,
        "git_blob_sha1": "18f04f93016ea1d7c8f23ab96bbd587b8d2d48e5",
        "width": 130,
        "height": 20,
    },
}

_ARROW_GEOMETRIES: Mapping[str, tuple[int, int]] = {
    "across-left": (25, 21),
    "across-right": (25, 21),
    "down-1": (21, 25),
    "down-2": (21, 80),
    "down-4": (21, 221),
    "down-right": (46, 46),
}
_ARROW_STATES = ("green", "grey", "yellow")
_V2_ARROW_TARGETS: dict[str, dict[str, Any]] = {}
for _geometry, (_width, _height) in _ARROW_GEOMETRIES.items():
    for _state in _ARROW_STATES:
        _filename = f"{_geometry}-{_state}.gif"
        _target = f"/shared/global/talents/images/talents/arrows/{_filename}"
        _V2_ARROW_TARGETS[_target] = {
            "route": f"/__offline/related-talent-ui/arrows/{_filename}",
            "repository_path": _target.lstrip("/"),
            "width": _width,
            "height": _height,
            "format": "GIF",
            "frames": 1,
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
V2_UI_TARGETS: Mapping[str, Mapping[str, Any]] = {
    **{
        target: {
            **dict(expected),
            "format": "PNG",
            "frames": 1,
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
        for target, expected in UI_TARGETS.items()
    },
    **_V2_ARROW_TARGETS,
}


@dataclass(frozen=True)
class RelatedTalentUIAsset:
    """One validated canonical PNG and its historical target route."""

    route: str
    relative: str
    target_route: str
    data: bytes
    mime: str
    source_refs: tuple[str, ...]
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedTalentUIBundle:
    """Validated UI assets plus a public catalog for an exporter."""

    assets: tuple[RelatedTalentUIAsset, ...]
    route_reuses: Mapping[str, str]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    notice_html: str
    map_sha256: str
    decision_sha256: str
    source_acceptance_sha256: str


def _fail(message: str) -> RelatedTalentUIError:
    return RelatedTalentUIError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
    current = root
    for part in rel.split("/"):
        current = current / part
        try:
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink: {relative!r}")
        except OSError as exc:
            raise _fail(f"cannot inspect {label}: {relative!r}: {exc}") from exc
    try:
        resolved = current.resolve(strict=True)
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


def _resolve_map_file(workspace_root: Path, map_path: str | os.PathLike[str]) -> Path:
    candidate = Path(map_path)
    if not candidate.is_absolute():
        return _resolve_workspace_file(workspace_root, candidate.as_posix(), "input map")
    if candidate.is_symlink():
        raise _fail("input map is a symlink")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(workspace_root.resolve())
    except (OSError, ValueError) as exc:
        raise _fail("input map escapes workspace_root or is unavailable") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise _fail("input map is not a regular non-symlink file")
    return resolved


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object: {path}")
    return value


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
    return "/" + "/".join(part for part in base_path.split("/") if part).rstrip("/")


def _validated_utc(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _fail("source downloaded_utc is missing")
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail("source downloaded_utc is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _fail("source downloaded_utc must include a timezone")
    return parsed.isoformat()


def _asset_url(base_path: str, route: str) -> str:
    return f"{base_path}{route}" if base_path else route


def _validate_common_source(
    source: Mapping[str, Any], label: str, *, require_classification: bool = True
) -> None:
    expected = {
        "repository_url": EXPECTED_REPOSITORY_URL,
        "commit_sha": EXPECTED_COMMIT_SHA,
        "tree_sha": EXPECTED_TREE_SHA,
    }
    if require_classification:
        expected["classification"] = EXPECTED_CLASSIFICATION
    for key, wanted in expected.items():
        if source.get(key) != wanted:
            raise _fail(f"{label} {key} is not pinned to the accepted source")
    if source.get("original_capture_timestamp") is not None:
        raise _fail(f"{label} has a non-null original capture timestamp")


def _binding_fields(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: entry.get(key)
        for key in (
            "target_route",
            "route",
            "repository_path",
            "sha256",
            "length",
            "git_blob_sha1",
            "format",
            "width",
            "height",
            "frames",
            "classification",
            "original_capture_timestamp",
        )
    }


def _validate_bindings(
    map_file: Path,
    workspace_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    try:
        map_bytes = map_file.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read input map: {map_file}: {exc}") from exc
    map_sha = _sha256(map_bytes)
    if map_sha != EXPECTED_MAP_SHA256:
        raise _fail(f"input map SHA mismatch: expected {EXPECTED_MAP_SHA256}, got {map_sha}")
    try:
        map_data = json.loads(map_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"input map is not valid UTF-8 JSON: {map_file}: {exc}") from exc
    if not isinstance(map_data, dict):
        raise _fail("input map must be a JSON object")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted talent UI map")

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
    del decision_bytes, acceptance_bytes

    if map_data.get("decision_sha256") != decision_sha:
        raise _fail("input map decision_sha256 does not match decision record")
    if map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("input map source_acceptance_sha256 does not match acceptance record")
    if decision.get("schema") != EXPECTED_DECISION_SCHEMA:
        raise _fail("decision record schema is not the accepted talent UI decision")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA:
        raise _fail("source acceptance schema is not the accepted source record")
    if decision.get("source_acceptance") != acceptance_rel:
        raise _fail("decision record points at a different source acceptance path")
    if decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("decision record source_acceptance_sha256 does not match acceptance record")
    if decision.get("accepted_for_browser_supplement") is not True:
        raise _fail("decision record is not accepted for browser supplement")
    if acceptance.get("accepted_source") is not True:
        raise _fail("source acceptance record is not accepted")

    source = map_data.get("source")
    if not isinstance(source, dict):
        raise _fail("input map source must be an object")
    _validate_common_source(source, "input map source")
    if not isinstance(source.get("downloaded_utc"), str):
        raise _fail("input map source downloaded_utc is missing")
    decision_source = decision.get("source")
    if not isinstance(decision_source, dict):
        raise _fail("decision source binding is missing")
    _validate_common_source(decision_source, "decision source", require_classification=True)
    _validate_common_source(acceptance, "source acceptance", require_classification=False)
    for label, record in (("source acceptance", acceptance), ("decision record", decision)):
        if record.get("original_2008_images_recovered") not in (None, 0):
            raise _fail(f"{label} claims recovered 2008 images")
    if acceptance.get("published_images") not in (None, 0):
        raise _fail("source acceptance unexpectedly marks images as published")

    if map_data.get("ui_count") != EXPECTED_UI_COUNT:
        raise _fail(f"input map ui_count is not {EXPECTED_UI_COUNT}")
    if decision.get("accepted_ui_count") != EXPECTED_UI_COUNT:
        raise _fail("decision accepted_ui_count does not match the pinned UI count")
    if decision.get("accepted_source_bytes") != EXPECTED_TOTAL_BYTES:
        raise _fail("decision accepted_source_bytes does not match the pinned UI bytes")
    entries = map_data.get("entries")
    targets = decision.get("targets")
    if not isinstance(entries, list) or len(entries) != EXPECTED_UI_COUNT:
        raise _fail("input map entries do not match the pinned UI count")
    if not isinstance(targets, list) or len(targets) != EXPECTED_UI_COUNT:
        raise _fail("decision targets do not match the pinned UI count")

    entry_by_target: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise _fail(f"UI map entry {index} is not an object")
        target = raw.get("target_route")
        if target in entry_by_target:
            raise _fail(f"duplicate UI target route: {target!r}")
        entry_by_target[target] = raw
    decision_by_target: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(targets):
        if not isinstance(raw, dict):
            raise _fail(f"decision target {index} is not an object")
        target = raw.get("target_route")
        if target in decision_by_target:
            raise _fail(f"duplicate decision target route: {target!r}")
        decision_by_target[target] = raw
    if set(entry_by_target) != set(UI_TARGETS) or set(decision_by_target) != set(UI_TARGETS):
        raise _fail("UI map or decision target set is outside the exact six-target scope")
    for target, expected in UI_TARGETS.items():
        entry = entry_by_target[target]
        decision_entry = decision_by_target[target]
        if _binding_fields(entry) != _binding_fields(decision_entry):
            raise _fail(f"decision target binding differs from input map: {target}")
        for key in ("route", "repository_path", "sha256", "length", "git_blob_sha1", "width", "height"):
            if entry.get(key) != expected[key]:
                raise _fail(f"{target} is not the accepted exact UI target binding")
        for key, expected_value in (
            ("format", "PNG"),
            ("frames", 1),
            ("classification", EXPECTED_CLASSIFICATION),
            ("original_capture_timestamp", None),
        ):
            if entry.get(key) != expected_value:
                raise _fail(f"{target} has an unexpected {key}")
        canonical = entry.get("route")
        if not isinstance(canonical, str) or not canonical.startswith("/__offline/related-talent-ui/"):
            raise _fail(f"{target} canonical route is outside the UI bundle")
        if "?" in canonical or "#" in canonical or "\\" in canonical:
            raise _fail(f"{target} canonical route is unsafe")

    source_bytes = sum(int(entry["length"]) for entry in entry_by_target.values())
    if source_bytes != EXPECTED_TOTAL_BYTES:
        raise _fail(f"input map payload length total is {source_bytes}, expected {EXPECTED_TOTAL_BYTES}")
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


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
    except RelatedTalentUIError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable PNG: {exc}") from exc
    if (width, height) != (entry.get("width"), entry.get("height")):
        raise _fail(
            f"{route} dimensions are {width}x{height}, expected "
            f"{entry.get('width')}x{entry.get('height')}"
        )
    if entry.get("frames") != 1:
        raise _fail(f"{route} map frames are not one")
    return width, height, frame_count


def _validate_v2_image(
    data: bytes, entry: Mapping[str, Any], route: str
) -> tuple[str, int, int, int]:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required to validate {route}: {_PIL_IMPORT_ERROR}")
    expected_format = entry.get("format")
    if expected_format not in ("PNG", "GIF"):
        raise _fail(f"{route} map format is not an accepted PNG or GIF")
    try:
        with Image.open(io.BytesIO(data)) as image:
            actual_format = image.format
            width, height = image.size
            frame_count = int(getattr(image, "n_frames", 1))
            if actual_format != expected_format:
                raise _fail(f"{route} payload decodes as {actual_format}, not {expected_format}")
            if frame_count < 1:
                raise _fail(f"{route} has no decodable frames")
            # Decode every frame before accepting or rejecting its declared
            # frame count; a one-frame field must never hide corrupt trailing
            # GIF frames.
            for frame_index in range(frame_count):
                image.seek(frame_index)
                image.load()
                if image.size != (width, height):
                    raise _fail(f"{route} frame {frame_index} has unexpected dimensions")
                image.convert("RGBA").tobytes()
    except RelatedTalentUIError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable {expected_format}: {exc}") from exc
    if frame_count != 1 or entry.get("frames") != 1:
        raise _fail(f"{route} has {frame_count} frames, expected one")
    if (width, height) != (entry.get("width"), entry.get("height")):
        raise _fail(
            f"{route} dimensions are {width}x{height}, expected "
            f"{entry.get('width')}x{entry.get('height')}"
        )
    return actual_format, width, height, frame_count


def _validate_v2_bindings(
    map_file: Path,
    workspace_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    try:
        map_relative = map_file.relative_to(workspace_root.resolve()).as_posix()
    except ValueError as exc:
        raise _fail("v2 input map escapes workspace_root") from exc
    if map_relative != EXPECTED_V2_MAP_RELATIVE:
        raise _fail("v2 input map is not the pinned v54 input-map.json")
    try:
        map_bytes = map_file.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read v2 input map: {map_file}: {exc}") from exc
    map_sha = _sha256(map_bytes)
    if map_sha != EXPECTED_V2_MAP_SHA256:
        raise _fail(f"v2 input map SHA mismatch: expected {EXPECTED_V2_MAP_SHA256}, got {map_sha}")
    try:
        map_data = json.loads(map_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"v2 input map is not valid UTF-8 JSON: {map_file}: {exc}") from exc
    if not isinstance(map_data, dict):
        raise _fail("v2 input map must be a JSON object")
    if map_data.get("schema") != EXPECTED_V2_MAP_SCHEMA:
        raise _fail("v2 input map schema is not the accepted talent UI v2 map")

    decision_rel = _normal_relative(map_data.get("decision"), "v2 decision path")
    acceptance_rel = _normal_relative(
        map_data.get("source_acceptance"), "v2 source acceptance path"
    )
    if decision_rel != EXPECTED_V2_DECISION_RELATIVE:
        raise _fail("v2 input map points at a different decision path")
    if acceptance_rel != EXPECTED_V2_ACCEPTANCE_RELATIVE:
        raise _fail("v2 input map points at a different source acceptance path")
    decision_path = _resolve_workspace_file(workspace_root, decision_rel, "v2 decision path")
    acceptance_path = _resolve_workspace_file(
        workspace_root, acceptance_rel, "v2 source acceptance path"
    )
    pins_path = _resolve_workspace_file(
        workspace_root, EXPECTED_V2_PINS_RELATIVE, "v2 root input pins"
    )
    decision_bytes, decision_sha = _read_hash_checked(
        decision_path, EXPECTED_V2_DECISION_SHA256, "v2 decision record"
    )
    acceptance_bytes, acceptance_sha = _read_hash_checked(
        acceptance_path,
        EXPECTED_V2_SOURCE_ACCEPTANCE_SHA256,
        "v2 source acceptance record",
    )
    decision = _read_json(decision_path, "v2 decision record")
    acceptance = _read_json(acceptance_path, "v2 source acceptance record")
    pins = _read_json(pins_path, "v2 root input pins")
    del decision_bytes, acceptance_bytes

    expected_pins = {
        "map_sha256": map_sha,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
        "map_schema": EXPECTED_V2_MAP_SCHEMA,
        "ui_count": EXPECTED_V2_UI_COUNT,
        "source_bytes": EXPECTED_V2_TOTAL_BYTES,
        "new_arrow_count": 18,
        "held_arrow_count": 3,
    }
    if pins != expected_pins:
        raise _fail("v2 root input pins do not bind the map, decision, acceptance, and aggregate")
    if map_data.get("decision_sha256") != decision_sha:
        raise _fail("v2 input map decision_sha256 does not match decision record")
    if map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("v2 input map source_acceptance_sha256 does not match acceptance record")
    if decision.get("schema") != EXPECTED_V2_DECISION_SCHEMA:
        raise _fail("v2 decision record schema is not the accepted talent UI decision")
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA:
        raise _fail("v2 source acceptance schema is not the accepted source record")
    if decision.get("source_acceptance") != acceptance_rel:
        raise _fail("v2 decision points at a different source acceptance path")
    if decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("v2 decision source_acceptance_sha256 does not match acceptance record")
    if decision.get("accepted_for_browser_supplement") is not True:
        raise _fail("v2 decision record is not accepted for browser supplement")
    if acceptance.get("accepted_source") is not True:
        raise _fail("v2 source acceptance record is not accepted")

    source = map_data.get("source")
    decision_source = decision.get("source")
    if not isinstance(source, dict) or source != EXPECTED_V2_SOURCE:
        raise _fail("v2 input map source is not the exact pinned later-source record")
    if not isinstance(decision_source, dict) or decision_source != EXPECTED_V2_SOURCE:
        raise _fail("v2 decision source is not the exact pinned later-source record")
    if source != decision_source:
        raise _fail("v2 decision source binding differs from input map")
    _validate_common_source(acceptance, "v2 source acceptance", require_classification=False)
    for key in ("zip_url", "zip_sha256"):
        if acceptance.get(key) != EXPECTED_V2_SOURCE[key]:
            raise _fail(f"v2 source acceptance {key} is not pinned to the accepted source")
    if acceptance.get("original_2008_images_recovered") not in (None, 0):
        raise _fail("v2 source acceptance claims recovered 2008 images")
    if acceptance.get("published_images") not in (None, 0):
        raise _fail("v2 source acceptance unexpectedly marks images as published")
    if source.get("original_capture_timestamp") is not None:
        raise _fail("v2 source has a non-null original capture timestamp")
    _validated_utc(source.get("downloaded_utc"))

    if map_data.get("ui_count") != EXPECTED_V2_UI_COUNT:
        raise _fail(f"v2 input map ui_count is not {EXPECTED_V2_UI_COUNT}")
    if decision.get("accepted_ui_count") != EXPECTED_V2_UI_COUNT:
        raise _fail("v2 decision accepted_ui_count does not match the pinned UI count")
    if decision.get("accepted_source_bytes") != EXPECTED_V2_TOTAL_BYTES:
        raise _fail("v2 decision accepted_source_bytes does not match the pinned UI bytes")
    if decision.get("classification") != EXPECTED_CLASSIFICATION:
        raise _fail("v2 decision classification is not the accepted later source")
    if decision.get("original_capture_timestamp") is not None:
        raise _fail("v2 decision has a non-null original capture timestamp")
    if decision.get("original_2008_images_recovered") != 0:
        raise _fail("v2 decision claims recovered 2008 images")
    if decision.get("retained_ui_count") != 6 or decision.get("new_cached_arrow_assets") != 18:
        raise _fail("v2 decision does not bind six retained images and eighteen arrows")
    if decision.get("new_downloaded_images") != 0:
        raise _fail("v2 decision claims new image downloads")

    entries = map_data.get("entries")
    targets = decision.get("targets")
    if not isinstance(entries, list) or len(entries) != EXPECTED_V2_UI_COUNT:
        raise _fail(f"v2 input map entries do not match the exact {EXPECTED_V2_UI_COUNT}-target scope")
    if not isinstance(targets, list) or len(targets) != EXPECTED_V2_UI_COUNT:
        raise _fail("v2 decision targets do not match the exact 24-target scope")
    entry_by_target: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise _fail(f"v2 map entry {index} is not an object")
        target = raw.get("target_route")
        if not isinstance(target, str) or target in entry_by_target:
            raise _fail(f"duplicate or invalid v2 UI target route: {target!r}")
        entry_by_target[target] = raw
    decision_by_target: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(targets):
        if not isinstance(raw, dict):
            raise _fail(f"v2 decision target {index} is not an object")
        target = raw.get("target_route")
        if not isinstance(target, str) or target in decision_by_target:
            raise _fail(f"duplicate or invalid v2 decision target route: {target!r}")
        decision_by_target[target] = raw
    if set(entry_by_target) != set(V2_UI_TARGETS) or set(decision_by_target) != set(V2_UI_TARGETS):
        raise _fail("v2 UI target set is outside the exact 24-target scope; down-3 is not accepted")

    source_bytes = 0
    payload_base = EXPECTED_V2_MAP_RELATIVE.rsplit("/", 1)[0] + "/assets/"
    for target, expected in V2_UI_TARGETS.items():
        entry = entry_by_target[target]
        decision_entry = decision_by_target[target]
        if _binding_fields(entry) != _binding_fields(decision_entry):
            raise _fail(f"v2 decision target binding differs from input map: {target}")
        for key, wanted in expected.items():
            if entry.get(key) != wanted:
                raise _fail(f"{target} is not the accepted exact v2 UI target binding ({key})")
        filename = Path(str(expected["repository_path"])).name
        if target in _V2_ARROW_TARGETS:
            expected_payload = payload_base + "arrows/" + filename
        else:
            expected_payload = payload_base + filename
        payload_rel = _normal_relative(entry.get("payload_path"), f"v2 payload {target}")
        if payload_rel != expected_payload:
            raise _fail(f"{target} payload path is not the pinned v54 asset location")
        length = entry.get("length")
        if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
            raise _fail(f"{target} has an invalid payload length")
        if not isinstance(entry.get("sha256"), str) or not _SHA256_RE.fullmatch(entry["sha256"]):
            raise _fail(f"{target} has a malformed SHA-256")
        if not isinstance(entry.get("git_blob_sha1"), str) or not _SHA1_RE.fullmatch(entry["git_blob_sha1"]):
            raise _fail(f"{target} has a malformed Git blob SHA-1")
        if "?" in str(entry.get("route")) or "#" in str(entry.get("route")) or "\\" in str(entry.get("route")):
            raise _fail(f"{target} canonical route is unsafe")
        source_bytes += length
    if source_bytes != EXPECTED_V2_TOTAL_BYTES:
        raise _fail(f"v2 input map payload total is {source_bytes}, expected {EXPECTED_V2_TOTAL_BYTES}")
    return map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha


def _load_v2_related_talent_ui_bundle(
    map_file: Path, workspace_root: Path, normalized_base: str
) -> RelatedTalentUIBundle:
    map_data, _decision, _acceptance, map_sha, decision_sha, acceptance_sha = (
        _validate_v2_bindings(map_file, workspace_root)
    )
    source = map_data["source"]
    entries = {entry["target_route"]: entry for entry in map_data["entries"]}
    assets: list[RelatedTalentUIAsset] = []
    route_reuses: dict[str, str] = {}
    canonical_routes: set[str] = set()
    source_bytes = 0
    source_refs = (
        str(source["repository_url"]),
        f"commit:{source['commit_sha']}",
        f"tree:{source['tree_sha']}",
    )
    for target, expected in V2_UI_TARGETS.items():
        entry = entries[target]
        canonical = entry["route"]
        if canonical in canonical_routes:
            raise _fail(f"duplicate v2 UI canonical route: {canonical!r}")
        canonical_routes.add(canonical)
        payload_file = _resolve_workspace_file(
            workspace_root, entry["payload_path"], f"v2 payload {target}"
        )
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read v2 payload for {target}: {exc}") from exc
        if len(data) != entry["length"]:
            raise _fail(f"{target} length mismatch: expected {entry['length']}, got {len(data)}")
        actual_sha = _sha256(data)
        if actual_sha != entry["sha256"]:
            raise _fail(f"{target} SHA mismatch: expected {entry['sha256']}, got {actual_sha}")
        actual_blob = _git_blob_sha1(data)
        if actual_blob != entry["git_blob_sha1"]:
            raise _fail(
                f"{target} Git blob SHA mismatch: expected {entry['git_blob_sha1']}, got {actual_blob}"
            )
        actual_format, width, height, frames = _validate_v2_image(data, entry, target)
        metadata = {
            "sha256": actual_sha,
            "length": len(data),
            "git_blob_sha1": actual_blob,
            "repository_path": entry["repository_path"],
            "width": width,
            "height": height,
            "frames": frames,
            "format": actual_format,
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
        assets.append(
            RelatedTalentUIAsset(
                route=canonical,
                relative=canonical[1:],
                target_route=target,
                data=data,
                mime="image/png" if actual_format == "PNG" else "image/gif",
                source_refs=source_refs,
                metadata=metadata,
            )
        )
        route_reuses[target] = canonical
        source_bytes += len(data)
    if source_bytes != EXPECTED_V2_TOTAL_BYTES:
        raise _fail(
            f"loaded v2 UI bytes do not match accepted total: {source_bytes}"
        )
    retrieved_utc = _validated_utc(source.get("downloaded_utc"))
    source_metadata: dict[str, Any] = {
        "repository_url": source["repository_url"],
        "commit_sha": source["commit_sha"],
        "tree_sha": source["tree_sha"],
        "classification": EXPECTED_CLASSIFICATION,
        "retrieved_utc": retrieved_utc,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "ui_count": len(assets),
        "retained_ui_count": 6,
        "new_cached_arrow_assets": 18,
        "accepted_source_bytes": source_bytes,
        "map_sha256": map_sha,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
    }
    notice_html = _make_notice(normalized_base)
    catalog_bytes = _make_catalog(
        base_path=normalized_base,
        assets=assets,
        source_metadata=source_metadata,
        notice_html=notice_html,
    )
    return RelatedTalentUIBundle(
        assets=tuple(assets),
        route_reuses=route_reuses,
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=source_bytes + len(catalog_bytes),
        source_metadata=source_metadata,
        notice_html=notice_html,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


def _make_notice(base_path: str) -> str:
    icon_catalog = html.escape(
        _asset_url(base_path, "/__offline/related-talent-icons.json"), quote=True
    )
    ui_catalog = html.escape(
        _asset_url(base_path, "/__offline/related-talent-ui.json"), quote=True
    )
    return (
        '<p id="related-talent-ui-notice" role="note">'
        "Talent data: 2008 archive. Some icons and interface images come from a later "
        "WotLK 3.3.5a calculator backup. "
        f'<a href="{icon_catalog}">Icon sources.</a> '
        f'<a href="{ui_catalog}">Interface sources.</a></p>'
    )


def _make_catalog(
    *,
    base_path: str,
    assets: list[RelatedTalentUIAsset],
    source_metadata: Mapping[str, Any],
    notice_html: str,
) -> bytes:
    # Public whitelist only: no private payload path, ZIP URL, or HTTP
    # transport metadata is exposed in the catalog.
    payload = {
        "schema": "wow-related-talent-ui-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "notice_html": notice_html,
        "source": dict(source_metadata),
        "ui_count": len(assets),
        "assets": [
            {
                "target_route": asset.target_route,
                "route": asset.route,
                "relative": asset.relative,
                "url": _asset_url(base_path, asset.route),
                "mime": asset.mime,
                "repository_path": asset.metadata["repository_path"],
                "sha256": asset.metadata["sha256"],
                "length": asset.metadata["length"],
                "width": asset.metadata["width"],
                "height": asset.metadata["height"],
                "frames": asset.metadata["frames"],
            }
            for asset in assets
        ],
    }
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _load_v1_related_talent_ui_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedTalentUIBundle:
    """Validate and load the v1 six-image UI supplement without changing it.

    ``map_path`` and every payload path must resolve to regular non-symlink
    files beneath ``workspace_root``.  The returned bytes are the original
    PNG bytes and no output file is written.
    """

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map_file(root, map_path)
    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, map_sha, decision_sha, acceptance_sha = _validate_bindings(
        map_file, root
    )
    source = map_data["source"]
    entries = {entry["target_route"]: entry for entry in map_data["entries"]}
    assets: list[RelatedTalentUIAsset] = []
    route_reuses: dict[str, str] = {}
    canonical_routes: set[str] = set()
    source_bytes = 0

    for target in UI_TARGETS:
        entry = entries[target]
        canonical = entry["route"]
        if canonical in canonical_routes:
            raise _fail(f"duplicate UI canonical route: {canonical!r}")
        canonical_routes.add(canonical)
        payload_file = _resolve_workspace_file(root, entry.get("payload_path"), f"payload {target}")
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read payload for {target}: {exc}") from exc
        if len(data) != entry["length"]:
            raise _fail(f"{target} length mismatch: expected {entry['length']}, got {len(data)}")
        actual_sha = _sha256(data)
        if actual_sha != entry["sha256"]:
            raise _fail(f"{target} SHA mismatch: expected {entry['sha256']}, got {actual_sha}")
        actual_blob = _git_blob_sha1(data)
        if actual_blob != entry["git_blob_sha1"]:
            raise _fail(
                f"{target} Git blob SHA mismatch: expected {entry['git_blob_sha1']}, got {actual_blob}"
            )
        width, height, frames = _validate_png(data, entry, target)
        metadata = {
            "sha256": actual_sha,
            "length": len(data),
            "git_blob_sha1": actual_blob,
            "repository_path": entry["repository_path"],
            "width": width,
            "height": height,
            "frames": frames,
            "format": "PNG",
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
        }
        assets.append(
            RelatedTalentUIAsset(
                route=canonical,
                relative=canonical[1:],
                target_route=target,
                data=data,
                mime="image/png",
                source_refs=(
                    str(source["repository_url"]),
                    f"commit:{source['commit_sha']}",
                    f"tree:{source['tree_sha']}",
                ),
                metadata=metadata,
            )
        )
        route_reuses[target] = canonical
        source_bytes += len(data)

    if source_bytes != EXPECTED_TOTAL_BYTES:
        raise _fail(f"loaded UI bytes do not match accepted total: {source_bytes}")
    retrieved_utc = _validated_utc(source.get("downloaded_utc"))
    source_metadata: dict[str, Any] = {
        "repository_url": source["repository_url"],
        "commit_sha": source["commit_sha"],
        "tree_sha": source["tree_sha"],
        "classification": EXPECTED_CLASSIFICATION,
        "retrieved_utc": retrieved_utc,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "ui_count": len(assets),
        "accepted_source_bytes": source_bytes,
        "map_sha256": map_sha,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": acceptance_sha,
    }
    notice_html = _make_notice(normalized_base)
    catalog_bytes = _make_catalog(
        base_path=normalized_base,
        assets=assets,
        source_metadata=source_metadata,
        notice_html=notice_html,
    )
    return RelatedTalentUIBundle(
        assets=tuple(assets),
        route_reuses=route_reuses,
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=source_bytes + len(catalog_bytes),
        source_metadata=source_metadata,
        notice_html=notice_html,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


def load_related_talent_ui_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedTalentUIBundle:
    """Validate and load the pinned v1 or v2 UI supplement.

    ``map_path`` and every payload path must resolve to regular non-symlink
    files beneath ``workspace_root``.  The returned bytes are the original
    payload bytes; this loader does not write output files.
    """

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map_file(root, map_path)
    try:
        probe = json.loads(map_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        # Keep the v1 parser's established diagnostics for malformed maps.
        return _load_v1_related_talent_ui_bundle(map_path, workspace_root, base_path)
    if isinstance(probe, dict) and probe.get("schema") == EXPECTED_V2_MAP_SCHEMA:
        normalized_base = _normalize_base_path(base_path)
        return _load_v2_related_talent_ui_bundle(map_file, root, normalized_base)
    return _load_v1_related_talent_ui_bundle(map_path, workspace_root, base_path)


__all__ = [
    "EXPECTED_CATALOG_RELATIVE",
    "EXPECTED_COMMIT_SHA",
    "EXPECTED_DECISION_SHA256",
    "EXPECTED_MAP_SHA256",
    "EXPECTED_REPOSITORY_URL",
    "EXPECTED_SOURCE_ACCEPTANCE_SHA256",
    "EXPECTED_TOTAL_BYTES",
    "EXPECTED_TREE_SHA",
    "EXPECTED_UI_COUNT",
    "RelatedTalentUIAsset",
    "RelatedTalentUIBundle",
    "RelatedTalentUIError",
    "UI_TARGETS",
    "load_related_talent_ui_bundle",
]
