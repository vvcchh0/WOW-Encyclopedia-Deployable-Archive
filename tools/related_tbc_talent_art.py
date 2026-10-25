"""Validated later-TBC talent art and derived inactive-state SVGs.

The production loader accepts the pinned 58-icon baseline and its reviewed
59-icon Shaman extension. PNGs are preserved byte-for-byte;
inactive-state SVGs embed those exact bytes and apply the source app's fixed
sRGB grayscale matrix. No original 2008 JPEG is claimed or synthesized.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import stat
import struct
import zipfile
import zlib
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


EXPECTED_MAP_SCHEMA = "wow-related-tbc-talent-art-map/v1"
EXPECTED_CATALOG_SCHEMA = "wow-related-tbc-talent-art-catalog/v1"
EXPECTED_SOURCE_REPOSITORY = "https://github.com/Vampyr7878/WoW-Talent-Caluclator-TBC"
EXPECTED_SOURCE_COMMIT = "2a5f39aadb1c88ded12ff6389f4f0bdc4470c2a4"
EXPECTED_SOURCE_CLASSIFICATION = "later_related_source"
EXPECTED_CANDIDATE_ACCEPTANCE_SHA256 = "c4921194ecea53fcf2cf9f6146199cda854bd528f366ecb3d5b159ffa6caf73c"
EXPECTED_CANDIDATE_AUDIT_SHA256 = "3371a6ee75f5672e618fdeabc899098faec79663ece103e915ca22a41e022e0b"
EXPECTED_SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
EXPECTED_MAP_SHA256 = "092e451fd9b558279408b27737aa81bc24b8113266466e128c81eec0e4a868bd"
EXPECTED_SOURCE_PINSET_SHA256 = "a74cfa0b874150095912e81c7210b78caf051358f57a3f13e5143aa3cbbc4485"
EXPECTED_TALENT_MAPPING_SHA256 = "c44e2f86200a64dd199fa2d6e0e66601c5d825563624e1864d82345388c857ba"
EXPECTED_ICON_COUNT = 58
EXPECTED_TALENT_COUNT = 65
EXPECTED_ROUTE_REUSE_COUNT = 130
EXPECTED_ZIP_FILENAME = "source-payloads.zip"
EXPECTED_CATALOG_RELATIVE = "__offline/related-tbc-talent-art/catalog.json"
OUTPUT_NAMESPACE = "__offline/related-tbc-talent-art"
MAX_SOURCE_ZIP_BYTES = 8 * 1024 * 1024
MAX_PNG_BYTES = 1024 * 1024
MAX_PNG_DIMENSION = 4096
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
CLASS_SLUG_RE = re.compile(r"^[a-z]+$")
ICON_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
GRAYSCALE_MATRIX = ".30 .59 .11 0 0 .30 .59 .11 0 0 .30 .59 .11 0 0 0 0 0 1 0"
NOTICE_HTML = (
    '<p id="related-tbc-talent-art-note" role="note">'
    'Additional icon art: <a href="'
    f'{EXPECTED_SOURCE_REPOSITORY}/tree/{EXPECTED_SOURCE_COMMIT}'
    '" rel="noopener noreferrer" style="color:#255075;text-decoration:underline">'
    'TBC calculator archive (2019)</a>.'
    "</p>"
)
MAPPING_FIELDS = (
    "class",
    "class_slug",
    "name",
    "specializations",
    "icon_id",
    "source_path",
    "active_route",
    "off_route",
)


class RelatedTbcTalentArtError(ValueError):
    """Raised when a TBC talent-art map or payload bundle fails validation."""


@dataclass(frozen=True)
class RelatedTbcTalentArtAsset:
    route: str
    relative: str
    data: bytes
    mime: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedTbcTalentArtBundle:
    assets: tuple[RelatedTbcTalentArtAsset, ...]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    route_reuses: Mapping[str, str]
    notice_html: str
    map_sha256: str
    payload_zip_sha256: str
    payload_zip_length: int
    icon_count: int
    talent_count: int


@dataclass(frozen=True)
class _Expectations:
    repository: str
    commit: str
    classification: str
    candidate_acceptance_sha256: str
    candidate_audit_sha256: str
    source_manifest_sha256: str
    source_pinset_sha256: str
    talent_mapping_sha256: str
    icon_count: int
    talent_count: int
    route_reuse_count: int
    map_sha256: str | None = None


_PRODUCTION_EXPECTATIONS = _Expectations(
    repository=EXPECTED_SOURCE_REPOSITORY,
    commit=EXPECTED_SOURCE_COMMIT,
    classification=EXPECTED_SOURCE_CLASSIFICATION,
    candidate_acceptance_sha256=EXPECTED_CANDIDATE_ACCEPTANCE_SHA256,
    candidate_audit_sha256=EXPECTED_CANDIDATE_AUDIT_SHA256,
    source_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256,
    source_pinset_sha256=EXPECTED_SOURCE_PINSET_SHA256,
    talent_mapping_sha256=EXPECTED_TALENT_MAPPING_SHA256,
    map_sha256=EXPECTED_MAP_SHA256,
    icon_count=EXPECTED_ICON_COUNT,
    talent_count=EXPECTED_TALENT_COUNT,
    route_reuse_count=EXPECTED_ROUTE_REUSE_COUNT,
)

# Keep the original profile and asset namespace intact. Only this additional
# immutable map is accepted; its renamed talent was checked rank by rank.
_SHAMAN_EXTENSION_EXPECTATIONS = replace(
    _PRODUCTION_EXPECTATIONS,
    candidate_acceptance_sha256="b88230b3665a1053841ccf98ce1bbf885850ac74c3e4859735cac9fce344bdf6",
    candidate_audit_sha256="1275bd1180718c952ed4fc3a85ffc191e7880de9133586c47a142a01a9527162",
    source_pinset_sha256="2b2e996a4a1246d0a16a76943525277ff4c11f76dff00dc2b564d6da82459299",
    talent_mapping_sha256="97d629d2af73c1491059dd84f57e60f022db16c7641c6d5724bbed279924b2f5",
    map_sha256="9a3f24a0ba4bae5ec91bbc5876d7c3282a74edfa2b81b4d1828daa603e06cc6e",
    icon_count=59,
    talent_count=66,
    route_reuse_count=132,
)
_ACCEPTED_PROFILES = {
    item.map_sha256: item
    for item in (_PRODUCTION_EXPECTATIONS, _SHAMAN_EXTENSION_EXPECTATIONS)
}


def _fail(message: str) -> RelatedTbcTalentArtError:
    return RelatedTbcTalentArtError(message)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _resolve_workspace_file(root: Path, value: str | Path, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        if candidate.is_symlink():
            raise _fail(f"{label} is a symlink")
        resolved = candidate.resolve()
    else:
        candidate = root / candidate
        if candidate.is_symlink():
            raise _fail(f"{label} is a symlink")
        resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise _fail(f"{label} escapes workspace_root") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise _fail(f"{label} is not a regular non-symlink file")
    return resolved


def _validate_repo_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise _fail(f"{label} is not a safe repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts) or ":" in value:
        raise _fail(f"{label} contains an unsafe path segment")
    if path.as_posix() != value:
        raise _fail(f"{label} is not normalized")
    return value


def _validate_route(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        raise _fail(f"{label} must be an absolute logical route")
    if any(token in value for token in ("?", "#", "\\", "\x00")):
        raise _fail(f"{label} contains a query, fragment, or unsafe character")
    parts = value[1:].split("/")
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise _fail(f"{label} contains an empty/dot/traversal segment")
    return value


def _normalize_source_pins(icons: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for item in icons:
        if not isinstance(item, Mapping):
            raise _fail("PNG metadata records must be objects")
        normalized.append(
            {
                "source_path": item.get("source_path"),
                "source_length": item.get("source_length"),
                "git_blob_sha1": item.get("git_blob_sha1"),
            }
        )
    return sorted(normalized, key=lambda item: str(item["source_path"]))


def _normalize_talent_mappings(talents: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for item in talents:
        if not isinstance(item, Mapping):
            raise _fail("talent mapping records must be objects")
        specs = item.get("specializations")
        if (
            not isinstance(specs, list)
            or not specs
            or any(not isinstance(spec, str) or not spec for spec in specs)
            or specs != sorted(set(specs))
        ):
            raise _fail("each talent specialization list must be non-empty, unique, and sorted")
        normalized.append({key: item.get(key) for key in MAPPING_FIELDS})
    return sorted(normalized, key=lambda item: (str(item["class_slug"]), str(item["active_route"])))


def _parse_static_png(data: bytes) -> tuple[int, int]:
    """Read a structurally valid, single-frame PNG and return IHDR dimensions."""

    if len(data) < 45 or len(data) > MAX_PNG_BYTES or not data.startswith(PNG_SIGNATURE):
        raise _fail("source payload is not a bounded PNG")
    offset = len(PNG_SIGNATURE)
    width = height = 0
    saw_ihdr = saw_idat = saw_iend = saw_plte = False
    allowed_critical = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise _fail("PNG chunk extends beyond the source payload")
        chunk_data = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        actual_crc = zlib.crc32(kind + chunk_data) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise _fail("PNG chunk CRC does not match")
        if kind in (b"acTL", b"fcTL", b"fdAT"):
            raise _fail("animated PNG payloads are not accepted")
        if kind == b"IHDR":
            if saw_ihdr or offset != len(PNG_SIGNATURE) or length != 13:
                raise _fail("PNG has a malformed or duplicate IHDR")
            width, height = struct.unpack_from(">II", chunk_data, 0)
            bit_depth, color_type, compression, filtering, interlace = chunk_data[8:13]
            valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if (
                width < 1 or height < 1 or width > MAX_PNG_DIMENSION or height > MAX_PNG_DIMENSION
                or color_type not in valid_depths or bit_depth not in valid_depths[color_type]
                or compression != 0 or filtering != 0 or interlace not in (0, 1)
            ):
                raise _fail("PNG IHDR fields are invalid or exceed the dimension bound")
            saw_ihdr = True
        elif not saw_ihdr:
            raise _fail("PNG data precedes IHDR")
        elif kind == b"PLTE":
            saw_plte = True
        elif kind == b"IDAT":
            saw_idat = True
        elif kind == b"IEND":
            if length != 0 or not saw_idat or (chunk_end != len(data)):
                raise _fail("PNG IEND or trailing data is invalid")
            saw_iend = True
            offset = chunk_end
            break
        elif kind[:1].isupper() and kind not in allowed_critical:
            raise _fail(f"PNG contains an unknown critical chunk: {kind!r}")
        offset = chunk_end
    if not (saw_ihdr and saw_idat and saw_iend):
        raise _fail("PNG is missing IHDR, IDAT, or IEND")
    if data[25] == 3 and not saw_plte:
        raise _fail("indexed PNG is missing PLTE")
    return width, height


def _make_off_state_svg(data: bytes, width: int, height: int) -> bytes:
    if width < 1 or height < 1:
        raise _fail("SVG dimensions must be positive")
    encoded = base64.b64encode(data).decode("ascii")
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<defs><filter id="off-state-gray" color-interpolation-filters="sRGB">'
        f'<feColorMatrix type="matrix" values="{GRAYSCALE_MATRIX}"/>'
        '</filter></defs>'
        f'<image width="{width}" height="{height}" preserveAspectRatio="none" '
        f'href="data:image/png;base64,{encoded}" filter="url(#off-state-gray)"/>'
        '</svg>'
    )
    return document.encode("utf-8")


def _zip_member_bytes(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    *,
    expected_length: int,
) -> bytes:
    if info.is_dir() or info.flag_bits & 0x1:
        raise _fail(f"ZIP member is a directory or encrypted: {info.filename!r}")
    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise _fail(f"ZIP member uses an unsupported compression method: {info.filename!r}")
    mode = info.external_attr >> 16
    if stat.S_ISLNK(mode):
        raise _fail(f"ZIP member is a symbolic link: {info.filename!r}")
    _validate_repo_path(info.filename, "ZIP member")
    if info.file_size != expected_length or info.file_size > MAX_PNG_BYTES:
        raise _fail(f"ZIP member length differs from the accepted source pin: {info.filename!r}")
    try:
        with archive.open(info, "r") as source:
            data = source.read(expected_length + 1)
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        raise _fail(f"could not read ZIP member {info.filename!r}: {exc}") from exc
    if len(data) != expected_length:
        raise _fail(f"ZIP member uncompressed length is invalid: {info.filename!r}")
    return data


def _validate_talent_rows(
    raw_talents: Any,
    icon_by_id: Mapping[str, Mapping[str, Any]],
    expectations: _Expectations,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if not isinstance(raw_talents, list) or len(raw_talents) != expectations.talent_count:
        raise _fail(f"talent map must contain exactly {expectations.talent_count} rows")
    normalized = _normalize_talent_mappings(raw_talents)
    if _sha256(_canonical_json_bytes(normalized)) != expectations.talent_mapping_sha256:
        raise _fail("talent name/route mapping does not match the reviewed 65-name audit")
    seen_names: set[tuple[str, str]] = set()
    route_reuses: dict[str, str] = {}
    for item in normalized:
        class_name = item["class"]
        class_slug = item["class_slug"]
        name = item["name"]
        icon_id = item["icon_id"]
        source_path = item["source_path"]
        if not all(isinstance(value, str) and value for value in (class_name, class_slug, name, icon_id, source_path)):
            raise _fail("talent mapping row has an empty identity field")
        if not CLASS_SLUG_RE.fullmatch(class_slug) or not ICON_ID_RE.fullmatch(icon_id):
            raise _fail("talent mapping row contains an invalid class slug or icon identifier")
        icon = icon_by_id.get(icon_id)
        if icon is None or source_path != icon["source_path"]:
            raise _fail(f"talent mapping does not resolve to its pinned source icon: {icon_id}")
        name_key = (class_slug, name)
        if name_key in seen_names:
            raise _fail(f"duplicate class/name talent mapping: {class_name}/{name}")
        seen_names.add(name_key)
        active = _validate_route(item["active_route"], "active target route")
        off = _validate_route(item["off_route"], "off target route")
        prefix = f"/shared/global/talents/{class_slug}/images/"
        if not active.startswith(prefix) or not off.startswith(prefix):
            raise _fail(f"talent state routes are outside the exact class image namespace: {name}")
        if not active.endswith(".jpg") or not off.endswith("-off.jpg") or off != active[:-4] + "-off.jpg":
            raise _fail(f"active/off routes are not a matching JPEG state pair: {name}")
        png_route = f"/{OUTPUT_NAMESPACE}/{icon_id}.png"
        off_svg_route = f"/{OUTPUT_NAMESPACE}/{icon_id}-off.svg"
        if active in route_reuses or off in route_reuses:
            raise _fail(f"duplicate target image route: {name}")
        route_reuses[active] = png_route
        route_reuses[off] = off_svg_route
    if len(route_reuses) != expectations.route_reuse_count:
        raise _fail(f"talent state mapping does not contain exactly {expectations.route_reuse_count} unique routes")
    referenced = {route.split("/")[-1].removesuffix("-off.svg").removesuffix(".png") for route in route_reuses.values()}
    if referenced != set(icon_by_id):
        raise _fail("talent mapping icon set differs from the 58 pinned source icons")
    return normalized, route_reuses


def _load_bundle_with_expectations(
    map_path: str | Path,
    workspace_root: str | Path,
    base_path: str,
    source_manifest_sha256: str,
    expectations: _Expectations,
) -> RelatedTbcTalentArtBundle:
    del base_path  # Routes are logical; the exporter applies its accepted base path.
    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail("workspace_root is not a directory")
    map_file = _resolve_workspace_file(root, map_path, "input map")
    try:
        map_bytes = map_file.read_bytes()
        map_data = json.loads(map_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"input map is unreadable or invalid JSON: {exc}") from exc
    if not isinstance(map_data, dict) or map_data.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("input map schema is not the accepted related TBC talent-art v1")
    map_sha256 = _sha256(map_bytes)
    if expectations.map_sha256 is not None and map_sha256 != expectations.map_sha256:
        raise _fail("input map SHA-256 differs from the accepted source map")

    source = map_data.get("source")
    if not isinstance(source, dict):
        raise _fail("input map is missing source identity metadata")
    source_expected = {
        "repository": expectations.repository,
        "commit": expectations.commit,
        "classification": expectations.classification,
        "candidate_acceptance_sha256": expectations.candidate_acceptance_sha256,
        "candidate_audit_sha256": expectations.candidate_audit_sha256,
    }
    for key, value in source_expected.items():
        if source.get(key) != value:
            raise _fail(f"input map source identity differs from reviewed pin: {key}")

    guard = map_data.get("source_guard")
    if not isinstance(guard, dict):
        raise _fail("input map is missing its Source16 manifest guard")
    if source_manifest_sha256 != expectations.source_manifest_sha256:
        raise _fail("actual source manifest SHA-256 is not the accepted Source16 manifest")
    if guard.get("source_manifest_sha256") != expectations.source_manifest_sha256:
        raise _fail("input map source manifest guard differs from the accepted Source16 manifest")

    raw_icons = map_data.get("icons")
    if not isinstance(raw_icons, list) or len(raw_icons) != expectations.icon_count:
        raise _fail(f"input map must contain exactly {expectations.icon_count} PNG records")
    if any(not isinstance(item, dict) for item in raw_icons):
        raise _fail("PNG metadata records must be objects")
    if _sha256(_canonical_json_bytes(_normalize_source_pins(raw_icons))) != expectations.source_pinset_sha256:
        raise _fail("source PNG path/length/Git blob pins differ from reviewed acceptance")
    if map_data.get("source_rows_sha256") != expectations.source_pinset_sha256:
        raise _fail("input map source rows digest is missing or incorrect")

    icon_by_id: dict[str, Mapping[str, Any]] = {}
    icon_by_source: dict[str, Mapping[str, Any]] = {}
    for item in raw_icons:
        if not isinstance(item, dict):
            raise _fail("PNG metadata records must be objects")
        source_path = _validate_repo_path(item.get("source_path"), "source PNG path")
        zip_member = _validate_repo_path(item.get("zip_member"), "source ZIP member")
        icon_id = item.get("icon_id")
        if not isinstance(icon_id, str) or not ICON_ID_RE.fullmatch(icon_id):
            raise _fail("source PNG record has an invalid icon_id")
        if PurePosixPath(source_path).suffix != ".png" or PurePosixPath(source_path).stem != icon_id:
            raise _fail(f"icon_id must equal the source PNG filename stem: {source_path}")
        expected_member = f"icons/{icon_id}.png"
        if zip_member != expected_member:
            raise _fail(f"ZIP member must use the accepted icons/<icon_id>.png path: {source_path}")
        length = item.get("source_length")
        blob_sha = item.get("git_blob_sha1")
        width, height = item.get("png_width"), item.get("png_height")
        if not isinstance(length, int) or isinstance(length, bool) or length < 1 or length > MAX_PNG_BYTES:
            raise _fail(f"source PNG length is invalid: {source_path}")
        if not isinstance(blob_sha, str) or not SHA1_RE.fullmatch(blob_sha):
            raise _fail(f"source Git blob SHA-1 is invalid: {source_path}")
        if (
            not isinstance(width, int) or isinstance(width, bool) or width < 1
            or not isinstance(height, int) or isinstance(height, bool) or height < 1
        ):
            raise _fail(f"source PNG dimensions are invalid: {source_path}")
        if width > MAX_PNG_DIMENSION or height > MAX_PNG_DIMENSION:
            raise _fail(f"source PNG dimensions exceed the bound: {source_path}")
        if icon_id in icon_by_id or source_path in icon_by_source:
            raise _fail(f"duplicate source icon record: {icon_id}")
        icon_by_id[icon_id] = item
        icon_by_source[source_path] = item

    raw_talents = map_data.get("talents")
    talents, route_reuses = _validate_talent_rows(raw_talents, icon_by_id, expectations)
    if map_data.get("talent_rows_sha256") != expectations.talent_mapping_sha256:
        raise _fail("input map talent rows digest is missing or incorrect")

    zip_record = map_data.get("source_zip")
    if not isinstance(zip_record, dict) or zip_record.get("filename") != EXPECTED_ZIP_FILENAME:
        raise _fail(f"input map must name sibling {EXPECTED_ZIP_FILENAME}")
    zip_path = map_file.parent / EXPECTED_ZIP_FILENAME
    if zip_path.is_symlink() or not zip_path.is_file():
        raise _fail("source payload ZIP must be a regular sibling file")
    try:
        zip_path.resolve().relative_to(root)
    except ValueError as exc:
        raise _fail("source payload ZIP escapes workspace_root") from exc
    zip_length = zip_path.stat().st_size
    if zip_length < 1 or zip_length > MAX_SOURCE_ZIP_BYTES:
        raise _fail("source payload ZIP length is outside its bound")
    zip_data = zip_path.read_bytes()
    zip_sha256 = _sha256(zip_data)
    if zip_record.get("length") != zip_length or zip_record.get("sha256") != zip_sha256:
        raise _fail("source payload ZIP hash or length differs from the input map")

    raw_member_names = [item["zip_member"] for item in raw_icons]
    if len(set(raw_member_names)) != expectations.icon_count:
        raise _fail("source ZIP member whitelist contains duplicates")
    source_bytes: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != expectations.icon_count or len(set(names)) != len(names):
                raise _fail(f"source ZIP must contain exactly {expectations.icon_count} unique non-directory members")
            if set(names) != set(raw_member_names):
                raise _fail(f"source ZIP member set differs from the accepted {expectations.icon_count}-file whitelist")
            if sum(info.file_size for info in infos) > MAX_SOURCE_ZIP_BYTES:
                raise _fail("source ZIP uncompressed size exceeds its bound")
            info_by_name = {info.filename: info for info in infos}
            for icon in raw_icons:
                member = icon["zip_member"]
                data = _zip_member_bytes(archive, info_by_name[member], expected_length=icon["source_length"])
                if _git_blob_sha1(data) != icon["git_blob_sha1"]:
                    raise _fail(f"Git blob SHA-1 differs from accepted source bytes: {member}")
                width, height = _parse_static_png(data)
                if (width, height) != (icon["png_width"], icon["png_height"]):
                    raise _fail(f"PNG dimensions differ from accepted metadata: {member}")
                source_bytes[icon["icon_id"]] = data
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise _fail(f"source payload ZIP cannot be read: {exc}") from exc

    source_metadata = {
        "repository": expectations.repository,
        "commit": expectations.commit,
        "classification": expectations.classification,
        "candidate_acceptance_sha256": expectations.candidate_acceptance_sha256,
        "candidate_audit_sha256": expectations.candidate_audit_sha256,
        "source_manifest_guard_sha256": expectations.source_manifest_sha256,
        "source_map_sha256": map_sha256,
        "source_zip_sha256": zip_sha256,
        "source_zip_length": zip_length,
        "raw_png_count": expectations.icon_count,
        "derived_off_svg_count": expectations.icon_count,
        "directly_named_talents": expectations.talent_count,
        "state_routes": expectations.route_reuse_count,
        "original_2008_talent_jpegs_recovered": 0,
    }

    assets: list[RelatedTbcTalentArtAsset] = []
    public_icons = []
    for icon_id in sorted(icon_by_id):
        item = icon_by_id[icon_id]
        data = source_bytes[icon_id]
        source_sha256 = _sha256(data)
        width, height = item["png_width"], item["png_height"]
        png_relative = f"{OUTPUT_NAMESPACE}/{icon_id}.png"
        off_relative = f"{OUTPUT_NAMESPACE}/{icon_id}-off.svg"
        source_reference = {
            "repository_path": item["source_path"],
            "git_blob_sha1": item["git_blob_sha1"],
            "source_length": len(data),
            "source_sha256": source_sha256,
            "png_width": width,
            "png_height": height,
        }
        assets.append(
            RelatedTbcTalentArtAsset(
                route="/" + png_relative,
                relative=png_relative,
                data=data,
                mime="image/png",
                metadata={"icon_id": icon_id, "state": "color_source_png", "transformed": False, **source_reference},
            )
        )
        off_svg = _make_off_state_svg(data, width, height)
        assets.append(
            RelatedTbcTalentArtAsset(
                route="/" + off_relative,
                relative=off_relative,
                data=off_svg,
                mime="image/svg+xml; charset=UTF-8",
                metadata={
                    "icon_id": icon_id,
                    "state": "derived_grayscale_off_svg",
                    "transformed": True,
                    "derivation": "embedded unchanged PNG data URI with fixed 0.30/0.59/0.11 sRGB matrix; alpha preserved",
                    **source_reference,
                },
            )
        )
        public_icons.append(
            {
                "icon_id": icon_id,
                "source_path": item["source_path"],
                "source_length": len(data),
                "git_blob_sha1": item["git_blob_sha1"],
                "source_sha256": source_sha256,
                "png_width": width,
                "png_height": height,
                "png_route": "/" + png_relative,
                "derived_off_svg_route": "/" + off_relative,
                "off_svg_sha256": _sha256(off_svg),
                "off_svg_length": len(off_svg),
            }
        )

    public_talents = [dict(item) for item in talents]
    catalog = {
        "schema": EXPECTED_CATALOG_SCHEMA,
        "source": dict(source_metadata),
        "icon_count": len(public_icons),
        "derived_off_svg_count": len(public_icons),
        "talent_count": len(public_talents),
        "state_route_count": len(route_reuses),
        "icons": public_icons,
        "talents": public_talents,
        "route_reuses": dict(sorted(route_reuses.items())),
        "off_state_derivation": {
            "kind": "derived_rendering",
            "source_is_unchanged_png_data_uri": True,
            "color_interpolation_filters": "sRGB",
            "matrix": GRAYSCALE_MATRIX,
            "alpha_preserved": True,
            "original_2008_image_recovered": False,
        },
    }
    catalog_bytes = _canonical_json_bytes(catalog) + b"\n"
    return RelatedTbcTalentArtBundle(
        assets=tuple(assets),
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=sum(len(asset.data) for asset in assets) + len(catalog_bytes),
        source_metadata=source_metadata,
        route_reuses=route_reuses,
        notice_html=NOTICE_HTML,
        map_sha256=map_sha256,
        payload_zip_sha256=zip_sha256,
        payload_zip_length=zip_length,
        icon_count=len(public_icons),
        talent_count=len(public_talents),
    )


def load_related_tbc_talent_art_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    base_path: str,
    *,
    source_manifest_sha256: str,
) -> RelatedTbcTalentArtBundle:
    """Load one immutable root-accepted profile for the Source16 manifest."""

    root = Path(workspace_root).resolve()
    map_file = _resolve_workspace_file(root, map_path, "input map")
    try:
        map_sha256 = _sha256(map_file.read_bytes())
    except OSError as exc:
        raise _fail(f"input map is unreadable: {exc}") from exc
    expectations = _ACCEPTED_PROFILES.get(map_sha256)
    if expectations is None:
        raise _fail("input map SHA-256 is not an accepted talent-art profile")

    return _load_bundle_with_expectations(
        map_file,
        root,
        base_path,
        source_manifest_sha256,
        expectations,
    )


def merge_talent_source_notice(existing_html: str, related_html: str | None) -> str:
    """Append a concise source note while preserving the old note byte-for-byte when absent."""

    if not related_html:
        return existing_html
    separator = "" if not existing_html else "\n"
    return existing_html + separator + related_html


__all__ = [
    "RelatedTbcTalentArtAsset",
    "RelatedTbcTalentArtBundle",
    "RelatedTbcTalentArtError",
    "load_related_tbc_talent_art_bundle",
    "merge_talent_source_notice",
]
