#!/usr/bin/env python3
"""Load the pinned later-source faction reward icon supplement.

The original Source16 GIFs remain absent. This adapter exposes three exact
2015 repository JPEGs at separate canonical routes and records their use as a
later related source; it does not claim byte or pixel recovery of those GIFs.
"""

from __future__ import annotations

from dataclasses import dataclass
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
except ImportError as exc:  # pragma: no cover - repository tests provide Pillow
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class RelatedFactionIconError(ValueError):
    """Raised when fixed faction icon inputs are unsafe or have drifted."""


EXPECTED_MAP_SHA256 = "6f5741104a0d7bd0aaf75f54498fa534dfdc936cc5e99a407143d1de1eccd9b4"
EXPECTED_DECISION_SHA256 = "48bfe451f4c5ea7e08e4a63edc40f144b0c9572df9c38b2ec21690fd469d4ec5"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = "5d7dfa177f25fe324fbd215363782de2b4b5a6a6f7f0149ec2b794e40a6ed4c2"
EXPECTED_SEMANTIC_AUDIT_SHA256 = "5a78c3f5494a0e1551d2a1f5a56983af1ab7c3f647351271eaa4b3a018410702"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_ROOT_INPUT_PINS_SHA256 = "3417b2c6b7a12b35400c331dbdceaebea03c46eb5e986f94ac72cd0c123614ff"

EXPECTED_MAP_RELATIVE = "research/continuous-recovery-20261022/integration/related-faction-icons-v54/input-map.json"
EXPECTED_DECISION_RELATIVE = "research/continuous-recovery-20261022/integration/related-faction-icons-v54/decision.json"
EXPECTED_PINS_RELATIVE = "research/continuous-recovery-20261022/integration/related-faction-icons-v54/root-input-pins.json"
EXPECTED_ACCEPTANCE_RELATIVE = "research/continuous-recovery-20261022/root-coolwow2-item-source-acceptance.json"
EXPECTED_AUDIT_RELATIVE = "research/continuous-recovery-20261022/faction-related-candidates/semantic-usage-audit.json"
EXPECTED_SOURCE_MANIFEST_RELATIVE = ".scratch/offline-non-gallery-20261021-v16/build-manifest.json"

EXPECTED_MAP_SCHEMA = "wow-related-faction-icon-map/v1"
EXPECTED_DECISION_SCHEMA = "wow-related-faction-icon-decision/v1"
EXPECTED_ACCEPTANCE_SCHEMA = "wow-root-coolwow2-item-source-acceptance/v1"
EXPECTED_AUDIT_SCHEMA = "wow-faction-related-icon-semantic-audit/v1"
EXPECTED_CLASSIFICATION = "later_related_source"
EXPECTED_CATALOG_RELATIVE = "__offline/related-faction-icons.json"
EXPECTED_REPOSITORY_URL = "https://github.com/boom8866/coolwow2"
EXPECTED_COMMIT_SHA = "09c52b7673871b8048da92e5a13ed753fc08162f"
EXPECTED_TREE_SHA = "5b3f74d7522aee7d57f8f9b554570a272836e869"
EXPECTED_COMMIT_DATE = "2015-12-16T16:29:03Z"
EXPECTED_SOURCE_BYTES = 3587
EXPECTED_OCCURRENCES = 85
EXPECTED_NOTICE_TEXT = "Some reward icons use a later game database backup (2015). Sources."

EXPECTED_PAGES = (
    "/info/basics/factions/aldorscryers/aldor-scryers.xml",
    "/info/basics/factions/cenarionxp/cenarionxp.xml",
    "/info/basics/factions/consortium/consortium.xml",
    "/info/basics/factions/hellfire/hellfire.xml",
    "/info/basics/factions/keepers/keepers.xml",
    "/info/basics/factions/lowercity/lowercity.xml",
    "/info/basics/factions/nagrand/nagrand.xml",
    "/info/basics/factions/shatar/shatar.xml",
    "/info/basics/factions/sporeggar/sporeggar.xml",
    "/info/basics/factions/violeteye/violeteye.xml",
    "/info/basics/factions/zangarmarsh/zangarpvp.xml",
)

# Exact route and payload bindings are duplicated here so a newly pinned map
# cannot silently expand the output scope without a code review.
EXPECTED_ASSETS: tuple[Mapping[str, Any], ...] = (
    {
        "repository_path": "images/item_icons/INV_Scroll_03.jpg",
        "sha256": "df950c468d7cf158cd7eb42794657a2242c385a93d3240e29a3ae29068920bf5",
        "git_blob_sha1": "937b4f2d28526b5ab7ff8828af54095d204a970c",
        "length": 1090,
        "route": "/__offline/related-faction-icons/INV_Scroll_03.jpg",
        "target_route": "/info/basics/factions/images/icons/INV_Scroll_03.gif",
        "page_routes": EXPECTED_PAGES[:10],
        "source_occurrence_count": 58,
        "role": "Recipe and design reward icon",
    },
    {
        "repository_path": "images/item_icons/INV_Scroll_06.jpg",
        "sha256": "e78a6d19f3bd0f0b7faf494ccae2cc61ee787913d0a1f374e28b1088f9fa7e59",
        "git_blob_sha1": "ffa4f6e3dcb75d3ae0a0cb0f06380f29aaba4458",
        "length": 1262,
        "route": "/__offline/related-faction-icons/INV_Scroll_06.jpg",
        "target_route": "/info/basics/factions/images/icons/INV_Scroll_06.gif",
        "page_routes": EXPECTED_PAGES[:10],
        "source_occurrence_count": 25,
        "role": "Recipe and design reward icon",
    },
    {
        "repository_path": "images/item_icons/INV_Wand_11.jpg",
        "sha256": "4c0d765966a621cea89d34c841612420bfbb5aebe52c78d8ed7c15608259091d",
        "git_blob_sha1": "660cbee0f7d36d9bdc8d2c67640c16e4e21f7fd2",
        "length": 1235,
        "route": "/__offline/related-faction-icons/INV_Wand_11.jpg",
        "target_route": "/info/basics/factions/images/icons/INV_Wand_11.gif",
        "page_routes": EXPECTED_PAGES[10:],
        "source_occurrence_count": 2,
        "role": "Incendic Rod item icon",
    },
)


@dataclass(frozen=True)
class RelatedFactionIconAsset:
    """One exact JPEG and its later-source route mapping."""

    route: str
    relative: str
    target_route: str
    data: bytes
    mime: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedFactionIconBundle:
    """Validated payloads, route mappings, public catalog, and notices."""

    assets: tuple[RelatedFactionIconAsset, ...]
    route_reuses: Mapping[str, str]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    notice_by_page: Mapping[str, str]
    map_sha256: str
    decision_sha256: str
    source_acceptance_sha256: str


def _fail(message: str) -> RelatedFactionIconError:
    return RelatedFactionIconError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


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
        mode = resolved.stat().st_mode
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} is missing or escapes workspace") from exc
    if not stat.S_ISREG(mode) or resolved.is_symlink():
        raise _fail(f"{label} is not a regular non-symlink file")
    return resolved


def _resolve_map(root: Path, map_path: str | os.PathLike[str]) -> Path:
    candidate = Path(map_path)
    if candidate.is_absolute():
        try:
            lexical_relative = candidate.absolute().relative_to(root).as_posix()
            resolved = _resolve_file(root, lexical_relative, "input map")
        except (OSError, ValueError, RelatedFactionIconError) as exc:
            raise _fail("input map is outside the workspace or missing") from exc
        if resolved.relative_to(root).as_posix() != EXPECTED_MAP_RELATIVE:
            raise _fail("input map path is not the accepted pinned path")
        return resolved
    resolved = _resolve_file(root, candidate.as_posix(), "input map")
    if resolved.relative_to(root).as_posix() != EXPECTED_MAP_RELATIVE:
        raise _fail("input map path is not the accepted pinned path")
    return resolved


def _read_pinned(path: Path, expected: str, label: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read {label}: {exc}") from exc
    actual = _sha256(raw)
    if actual != expected:
        raise _fail(f"{label} SHA mismatch: expected {expected}, got {actual}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object")
    return value, actual


def _normalize_base_path(value: str) -> str:
    if not isinstance(value, str) or "?" in value or "#" in value or "\\" in value:
        raise _fail("base_path must be a path without query, fragment, or backslash")
    if value in ("", "/"):
        return ""
    if not value.startswith("/"):
        raise _fail("base_path must start with '/'")
    parts = [part for part in value.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise _fail("base_path contains traversal")
    return "/" + "/".join(parts) + "/"


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
    except RelatedFactionIconError:
        raise
    except Exception as exc:
        raise _fail(f"{route} is not a fully decodable JPEG: {exc}") from exc
    if (width, height, frames) != (entry.get("width"), entry.get("height"), entry.get("frames")):
        raise _fail(f"{route} map dimensions/frames do not match payload")
    return width, height, frames


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object")
    return value


def _verify_bindings(map_file: Path, root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str, str, str, str]:
    map_data, map_sha = _read_pinned(map_file, EXPECTED_MAP_SHA256, "input map")
    if map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not accepted")
    if map_file.relative_to(root).as_posix() != EXPECTED_MAP_RELATIVE:
        raise _fail("input map path is not accepted")

    pins_path = _resolve_file(root, EXPECTED_PINS_RELATIVE, "root input pins")
    pins, _ = _read_pinned(pins_path, EXPECTED_ROOT_INPUT_PINS_SHA256, "root input pins")
    expected_pins = {
        "map_sha256": EXPECTED_MAP_SHA256,
        "decision_sha256": EXPECTED_DECISION_SHA256,
        "source_acceptance_sha256": EXPECTED_SOURCE_ACCEPTANCE_SHA256,
        "semantic_audit_sha256": EXPECTED_SEMANTIC_AUDIT_SHA256,
        "entry_count": 3,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "affected_page_count": 11,
        "source_occurrences": EXPECTED_OCCURRENCES,
        "new_network_requests": 0,
    }
    if pins != expected_pins:
        raise _fail("root input pins do not match the accepted aggregate")

    if map_data.get("decision") != EXPECTED_DECISION_RELATIVE:
        raise _fail("decision path is outside the accepted role")
    if map_data.get("source_acceptance") != EXPECTED_ACCEPTANCE_RELATIVE:
        raise _fail("source acceptance path is outside the accepted role")
    if map_data.get("semantic_audit") != EXPECTED_AUDIT_RELATIVE:
        raise _fail("semantic audit path is outside the accepted role")

    decision_path = _resolve_file(root, EXPECTED_DECISION_RELATIVE, "decision record")
    acceptance_path = _resolve_file(root, EXPECTED_ACCEPTANCE_RELATIVE, "source acceptance")
    audit_path = _resolve_file(root, EXPECTED_AUDIT_RELATIVE, "semantic audit")
    decision, decision_sha = _read_pinned(decision_path, EXPECTED_DECISION_SHA256, "decision record")
    acceptance, acceptance_sha = _read_pinned(
        acceptance_path, EXPECTED_SOURCE_ACCEPTANCE_SHA256, "source acceptance"
    )
    audit, audit_sha = _read_pinned(audit_path, EXPECTED_SEMANTIC_AUDIT_SHA256, "semantic audit")

    if map_data.get("decision_sha256") != decision_sha or map_data.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("input map hashes do not match the decision and source acceptance")
    if map_data.get("semantic_audit_sha256") != audit_sha:
        raise _fail("input map semantic audit hash does not match")
    if map_data.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("input map source manifest is not the pinned Source16 manifest")

    source = map_data.get("source")
    expected_source = {
        "repository_url": EXPECTED_REPOSITORY_URL,
        "commit_sha": EXPECTED_COMMIT_SHA,
        "tree_sha": EXPECTED_TREE_SHA,
        "repository_commit_date_utc": EXPECTED_COMMIT_DATE,
        "original_capture_timestamp": None,
        "classification": EXPECTED_CLASSIFICATION,
    }
    if source != expected_source:
        raise _fail("input map repository identity or source classification is not accepted")
    if decision.get("schema") != EXPECTED_DECISION_SCHEMA or decision.get("accepted_for_derived_trial") is not True:
        raise _fail("decision is not accepted for the bounded derived trial")
    if decision.get("source_acceptance") != EXPECTED_ACCEPTANCE_RELATIVE:
        raise _fail("decision does not bind the pinned source acceptance")
    if decision.get("source_acceptance_sha256") != acceptance_sha:
        raise _fail("decision source acceptance hash does not match")
    if decision.get("semantic_audit") != EXPECTED_AUDIT_RELATIVE or decision.get("semantic_audit_sha256") != audit_sha:
        raise _fail("decision semantic audit binding does not match")
    if decision.get("source_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("decision does not bind the pinned Source16 manifest")
    if decision.get("classification") != EXPECTED_CLASSIFICATION or decision.get("historical_original_images_recovered") != 0:
        raise _fail("decision overstates the historical recovery")
    if decision.get("original_capture_timestamp") is not None or decision.get("images_reencoded") is not False:
        raise _fail("decision changes the accepted source or byte-preservation status")
    if decision.get("allowed_targets") != [item["target_route"] for item in EXPECTED_ASSETS]:
        raise _fail("decision target routes differ from the reviewed scope")
    if decision.get("allowed_page_routes") != list(EXPECTED_PAGES):
        raise _fail("decision affected pages differ from the reviewed scope")

    # Preserve the prior source acceptance boundary: it accepts the repository
    # bytes but explicitly does not grant browser supplement acceptance.
    if acceptance.get("schema") != EXPECTED_ACCEPTANCE_SCHEMA or acceptance.get("accepted_sources") is not True:
        raise _fail("source acceptance record is not accepted")
    if acceptance.get("accepted_for_browser_supplement") is not False:
        raise _fail("source acceptance browser status changed")
    if acceptance.get("historical_original_images_recovered") != 0 or acceptance.get("images_reencoded") is not False:
        raise _fail("source acceptance overstates original recovery or byte transformation")
    if (acceptance.get("repository_url"), acceptance.get("commit_sha"), acceptance.get("tree_sha")) != (
        EXPECTED_REPOSITORY_URL, EXPECTED_COMMIT_SHA, EXPECTED_TREE_SHA
    ):
        raise _fail("source acceptance repository identity changed")

    if audit.get("schema") != EXPECTED_AUDIT_SCHEMA or audit.get("network_requests") != 0:
        raise _fail("semantic audit schema or offline boundary changed")
    if audit.get("scope", {}).get("source16_build_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("semantic audit does not bind the pinned Source16 manifest")
    candidate = audit.get("scope", {}).get("candidate_source_identity", {})
    if (candidate.get("repository"), candidate.get("commit"), candidate.get("commit_date"), candidate.get("original_capture_date")) != (
        EXPECTED_REPOSITORY_URL, EXPECTED_COMMIT_SHA, EXPECTED_COMMIT_DATE, None
    ):
        raise _fail("semantic audit source identity changed")
    if audit.get("interpretation", {}).get("pixel_identity") != (
        "No byte/pixel comparison to Source16 is possible because the original GIF targets are absent; shared basename is not proof of identical artwork."
    ):
        raise _fail("semantic audit no longer preserves the original GIF identity boundary")

    source_manifest = _resolve_file(root, EXPECTED_SOURCE_MANIFEST_RELATIVE, "Source16 build manifest")
    try:
        manifest_hash = hashlib.sha256()
        with source_manifest.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                manifest_hash.update(chunk)
    except OSError as exc:
        raise _fail(f"cannot read Source16 build manifest: {exc}") from exc
    if manifest_hash.hexdigest() != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise _fail("Source16 build manifest SHA mismatch")

    entries = map_data.get("entries")
    if not isinstance(entries, list) or len(entries) != len(EXPECTED_ASSETS):
        raise _fail("input map must contain exactly the three reviewed assets")
    if decision.get("entry_count") != len(EXPECTED_ASSETS) or decision.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        raise _fail("decision aggregate does not match the three reviewed assets")
    if decision.get("allowed_targets") != [entry["target_route"] for entry in entries]:
        raise _fail("decision target set does not match input map")

    acceptance_records = acceptance.get("records")
    if not isinstance(acceptance_records, list) or len(acceptance_records) != len(EXPECTED_ASSETS):
        raise _fail("source acceptance does not contain exactly three repository records")
    acceptance_by_path = {record.get("repository_path"): record for record in acceptance_records if isinstance(record, dict)}
    audit_images = audit.get("source_images", {})
    for entry, expected in zip(entries, EXPECTED_ASSETS):
        if not isinstance(entry, dict):
            raise _fail("input map asset entry must be an object")
        if entry.get("repository_path") != expected["repository_path"]:
            raise _fail("input map repository paths differ from the reviewed scope")
        if entry.get("target_route") != expected["target_route"] or entry.get("route") != expected["route"]:
            raise _fail(f"{expected['repository_path']} route changed")
        if entry.get("page_routes") != list(expected["page_routes"]):
            raise _fail(f"{expected['repository_path']} affected pages changed")
        for field in ("sha256", "git_blob_sha1", "length", "source_occurrence_count", "role"):
            if entry.get(field) != expected[field]:
                raise _fail(f"{expected['repository_path']} {field} changed")
        if entry.get("format") != "JPEG" or (entry.get("width"), entry.get("height"), entry.get("frames")) != (36, 36, 1):
            raise _fail(f"{expected['repository_path']} is not the accepted 36x36 single-frame JPEG")
        if entry.get("classification") != EXPECTED_CLASSIFICATION or entry.get("original_capture_timestamp") is not None:
            raise _fail(f"{expected['repository_path']} source classification changed")
        if entry.get("original_gif_pixel_identity") != "unknown":
            raise _fail(f"{expected['repository_path']} overstates GIF pixel identity")
        payload_relative = _safe_relative(entry.get("payload_path"), f"{expected['repository_path']} payload")
        expected_payload = "research/continuous-recovery-20261022/integration/related-faction-icons-v54/assets/" + Path(expected["repository_path"]).name
        if payload_relative != expected_payload:
            raise _fail(f"{expected['repository_path']} payload path changed")

        accepted = acceptance_by_path.get(expected["repository_path"])
        if not isinstance(accepted, dict) or any(
            accepted.get(field) != entry.get(field)
            for field in ("sha256", "git_blob_sha1", "length", "format", "width", "height", "frames", "classification", "original_capture_timestamp")
        ):
            raise _fail(f"{expected['repository_path']} source acceptance binding changed")
        audited = audit_images.get(Path(expected["repository_path"]).name)
        if not isinstance(audited, dict) or (
            audited.get("private_local_payload_sha256"), audited.get("private_local_payload_bytes"),
            audited.get("git_blob_sha1"), audited.get("format"), audited.get("native_dimensions_px"), audited.get("frames"),
        ) != (expected["sha256"], expected["length"], expected["git_blob_sha1"], "JPEG", [36, 36], 1):
            raise _fail(f"{expected['repository_path']} semantic audit binding changed")
        target_basename = Path(expected["target_route"]).name
        missing = audit.get("target_presence", {}).get("source16", {}).get(target_basename, {})
        if missing.get("exists") is not False or missing.get("target_path") != expected["target_route"]:
            raise _fail(f"{expected['repository_path']} original target presence changed")

    if sum(int(entry["length"]) for entry in entries) != EXPECTED_SOURCE_BYTES:
        raise _fail("input map total payload bytes changed")
    if sum(int(entry["source_occurrence_count"]) for entry in entries) != EXPECTED_OCCURRENCES:
        raise _fail("input map total source occurrences changed")
    if set(page for entry in entries for page in entry["page_routes"]) != set(EXPECTED_PAGES):
        raise _fail("input map page set differs from the reviewed eleven pages")
    return map_data, decision, acceptance, audit, map_sha, decision_sha, acceptance_sha, audit_sha


def _make_notice(base_path: str) -> str:
    catalog_url = html.escape((base_path or "/") + EXPECTED_CATALOG_RELATIVE, quote=True)
    return (
        '<aside id="__offline-related-faction-icons" role="note" '
        'style="padding:6px 12px;background:#eadbb7;color:#302619;'
        'font:13px/1.5 Arial,sans-serif;text-align:center">'
        'Some reward icons use a later game database backup (2015). '
        f'<a href="{catalog_url}" style="color:#174f7d;text-decoration:underline">Sources</a>.'
        "</aside>"
    )


def _make_catalog(base_path: str, assets: list[RelatedFactionIconAsset], source_metadata: Mapping[str, Any]) -> bytes:
    images = []
    for asset in assets:
        item = dict(asset.metadata)
        item["route"] = asset.route
        item["target_route"] = asset.target_route
        item["url"] = (base_path + asset.relative) if base_path else "/" + asset.relative
        item["mime"] = asset.mime
        images.append(item)
    document = {
        "schema": "wow-related-faction-icon-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "source": dict(source_metadata),
        "image_count": len(assets),
        "source_bytes": sum(len(asset.data) for asset in assets),
        "images": images,
    }
    return (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _load_legacy_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedFactionIconBundle:
    """Validate fixed source inputs and return a read-only in-memory bundle."""

    try:
        root = Path(workspace_root).resolve(strict=True)
    except OSError as exc:
        raise _fail(f"workspace_root is missing: {exc}") from exc
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    map_file = _resolve_map(root, map_path)
    normalized_base = _normalize_base_path(base_path)
    map_data, decision, acceptance, audit, map_sha, decision_sha, acceptance_sha, audit_sha = _verify_bindings(map_file, root)

    assets: list[RelatedFactionIconAsset] = []
    route_reuses: dict[str, str] = {}
    seen_routes: set[str] = set()
    for entry, expected in zip(map_data["entries"], EXPECTED_ASSETS):
        route = str(entry["route"])
        relative = _safe_relative(route.lstrip("/"), f"canonical route {route}")
        if route in seen_routes or relative in seen_routes:
            raise _fail(f"duplicate canonical route: {route}")
        seen_routes.add(route)
        payload_file = _resolve_file(root, entry["payload_path"], f"payload for {route}")
        try:
            data = payload_file.read_bytes()
        except OSError as exc:
            raise _fail(f"cannot read payload for {route}: {exc}") from exc
        if len(data) != expected["length"] or len(data) != entry["length"]:
            raise _fail(f"{route} length mismatch")
        digest = _sha256(data)
        if digest != expected["sha256"] or digest != entry["sha256"]:
            raise _fail(f"{route} SHA mismatch")
        if _git_blob_sha1(data) != expected["git_blob_sha1"] or _git_blob_sha1(data) != entry["git_blob_sha1"]:
            raise _fail(f"{route} Git blob SHA mismatch")
        width, height, frames = _validate_jpeg(data, entry, route)
        metadata = {
            "repository_path": entry["repository_path"],
            "source_url": entry["source_url"],
            "repository_url": EXPECTED_REPOSITORY_URL,
            "commit_sha": EXPECTED_COMMIT_SHA,
            "tree_sha": EXPECTED_TREE_SHA,
            "repository_commit_date_utc": EXPECTED_COMMIT_DATE,
            "current_observed_utc": entry["current_observed_utc"],
            "sha256": digest,
            "git_blob_sha1": _git_blob_sha1(data),
            "length": len(data),
            "format": "JPEG",
            "width": width,
            "height": height,
            "frames": frames,
            "classification": EXPECTED_CLASSIFICATION,
            "original_capture_timestamp": None,
            "role": entry["role"],
            "source_occurrence_count": entry["source_occurrence_count"],
            "page_routes": list(entry["page_routes"]),
            "original_gif_pixel_identity": "unknown",
        }
        asset = RelatedFactionIconAsset(
            route=route,
            relative=relative,
            target_route=str(entry["target_route"]),
            data=data,
            mime="image/jpeg",
            metadata=metadata,
        )
        if asset.target_route in route_reuses:
            raise _fail(f"duplicate target route: {asset.target_route}")
        assets.append(asset)
        route_reuses[asset.target_route] = asset.route

    if sum(len(asset.data) for asset in assets) != EXPECTED_SOURCE_BYTES:
        raise _fail("loaded payload aggregate differs from the pinned source byte count")
    source_metadata = {
        "source_label": f"coolwow2 GitHub repository at commit {EXPECTED_COMMIT_SHA} (2015-12-16)",
        "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "repository_url": EXPECTED_REPOSITORY_URL,
        "commit_sha": EXPECTED_COMMIT_SHA,
        "tree_sha": EXPECTED_TREE_SHA,
        "repository_commit_date_utc": EXPECTED_COMMIT_DATE,
        "classification": EXPECTED_CLASSIFICATION,
        "original_capture_timestamp": None,
        "original_2008_images_recovered": 0,
        "historical_original_images_recovered": 0,
        "images_reencoded": False,
        "accepted_for_derived_trial": decision["accepted_for_derived_trial"],
        "initial_source_record_browser_acceptance": acceptance["accepted_for_browser_supplement"],
        "source_acceptance_sha256": acceptance_sha,
        "decision_sha256": decision_sha,
        "semantic_audit_sha256": audit_sha,
        "source_checked_utc": acceptance.get("checked_utc"),
        "image_count": len(assets),
        "source_bytes": sum(len(asset.data) for asset in assets),
    }
    notice = _make_notice(normalized_base)
    notice_by_page = {route: notice for route in EXPECTED_PAGES}
    catalog_bytes = _make_catalog(normalized_base, assets, source_metadata)
    return RelatedFactionIconBundle(
        assets=tuple(assets),
        route_reuses=route_reuses,
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=source_metadata["source_bytes"] + len(catalog_bytes),
        source_metadata=source_metadata,
        notice_by_page=notice_by_page,
        map_sha256=map_sha,
        decision_sha256=decision_sha,
        source_acceptance_sha256=acceptance_sha,
    )


def load_related_faction_icon_bundle(
    map_path: str | os.PathLike[str],
    workspace_root: str | os.PathLike[str],
    base_path: str,
) -> RelatedFactionIconBundle:
    """Select an immutable faction supplement profile."""
    root = Path(workspace_root).resolve()
    candidate = Path(map_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    extended_relative = "artifacts/related-faction-item-icons-20261025/input-map.json"
    canonical_relative = "artifacts/related-faction-canonical-art-20261025/input-map.json"
    more_relative = "artifacts/related-faction-canonical-more-20261025/input-map.json"
    third_relative = "artifacts/related-faction-canonical-third-20261025/input-map.json"
    if candidate.resolve() == (root / third_relative).resolve():
        import related_faction_canonical_extension
        baseline = load_related_faction_icon_bundle(more_relative, root, base_path)
        return related_faction_canonical_extension.extend_bundle(candidate, root, base_path, baseline)
    if candidate.resolve() == (root / more_relative).resolve():
        import related_faction_canonical_extension
        baseline = load_related_faction_icon_bundle(canonical_relative, root, base_path)
        return related_faction_canonical_extension.extend_bundle(candidate, root, base_path, baseline)
    if candidate.resolve() == (root / canonical_relative).resolve():
        import related_faction_canonical_extension
        baseline = load_related_faction_icon_bundle(extended_relative, root, base_path)
        return related_faction_canonical_extension.extend_bundle(candidate, root, base_path, baseline)
    if candidate.resolve() == (root / extended_relative).resolve():
        import related_faction_item_extension
        baseline = _load_legacy_bundle(EXPECTED_MAP_RELATIVE, root, base_path)
        return related_faction_item_extension.extend_bundle(candidate, root, base_path, baseline)
    return _load_legacy_bundle(map_path, workspace_root, base_path)


__all__ = [
    "EXPECTED_CATALOG_RELATIVE",
    "EXPECTED_DECISION_SHA256",
    "EXPECTED_MAP_SHA256",
    "EXPECTED_NOTICE_TEXT",
    "EXPECTED_PAGES",
    "EXPECTED_SEMANTIC_AUDIT_SHA256",
    "EXPECTED_SOURCE_ACCEPTANCE_SHA256",
    "EXPECTED_SOURCE_MANIFEST_SHA256",
    "RelatedFactionIconAsset",
    "RelatedFactionIconBundle",
    "RelatedFactionIconError",
    "load_related_faction_icon_bundle",
]
